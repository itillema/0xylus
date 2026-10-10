"""Properties of the zoo's ground-truth plans."""

import hashlib
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from math import exp, lgamma, log, log1p

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from benchmarks.zoo.configs import (
    CONTROL_FAILURES,
    CONTROL_PASSES,
    DEFAULT_CONFIGS,
    ZooConfig,
    default_configs,
)
from benchmarks.zoo.plan import build_plan, manifest_json, shuffled, stream

SEEDS = st.integers(min_value=0, max_value=2**32 - 1)
RUN_COUNTS = st.integers(min_value=1, max_value=40)
# The manifest for seed 1, 30 runs and the default configurations. It must be identical on every
# Python version and OS; if the generator changes on purpose, update it and say so in the change.
GOLDEN_MANIFEST_SHA256 = "8e67da5755d0a6fc110bb0526971ac1730881752a957e51bfb01c5929ea87364"


def _two_sided_binomial_p(k: int, n: int, p: float) -> float:
    """Exact two-sided binomial test: the probability of an outcome no more likely than k."""
    log_pmf = [
        lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log1p(-p)
        for i in range(n + 1)
    ]
    observed = log_pmf[k]
    return min(1.0, sum(exp(x) for x in log_pmf if x <= observed + 1e-9))


def test_stream_values_are_pinned() -> None:
    # CPython guarantees random() for an integer seed across versions; this pins it for our keys.
    assert stream(1, 0, "Z1", "fault").random() == 0.3849440626928162


def test_golden_manifest_is_reproduced() -> None:
    text = manifest_json(build_plan(1, 30, DEFAULT_CONFIGS))
    assert hashlib.sha256(text.encode()).hexdigest() == GOLDEN_MANIFEST_SHA256


@settings(deadline=None, max_examples=50)
@given(seed=SEEDS, runs=RUN_COUNTS)
def test_the_same_seed_gives_a_byte_identical_manifest(seed: int, runs: int) -> None:
    first = manifest_json(build_plan(seed, runs, DEFAULT_CONFIGS))
    second = manifest_json(build_plan(seed, runs, DEFAULT_CONFIGS))

    assert first == second


def test_different_seeds_give_different_plans() -> None:
    first = manifest_json(build_plan(1, 30, DEFAULT_CONFIGS))
    second = manifest_json(build_plan(2, 30, DEFAULT_CONFIGS))

    assert first != second


@settings(deadline=None, max_examples=50)
@given(seed=SEEDS, runs=RUN_COUNTS)
def test_members_of_a_shared_fault_cluster_fail_together(seed: int, runs: int) -> None:
    plan = build_plan(seed, runs, DEFAULT_CONFIGS)

    for run in plan.runs:
        failing = set(run.failing)
        for config in plan.configs:
            members = set(plan.members[config.key])
            assert members <= failing or not members & failing
            assert run.faults[config.key] == (members <= failing)


@settings(deadline=None, max_examples=50)
@given(seed=SEEDS, runs=RUN_COUNTS)
def test_controls_and_the_polluter_never_vary(seed: int, runs: int) -> None:
    plan = build_plan(seed, runs, DEFAULT_CONFIGS)

    assert len(plan.control_pass) == CONTROL_PASSES
    assert len(plan.control_fail) == CONTROL_FAILURES
    for run in plan.runs:
        failing = set(run.failing)
        assert set(plan.control_fail) <= failing
        assert not set(plan.control_pass) & failing
        assert not set(plan.extras["Z1"]) & failing


@settings(deadline=None, max_examples=50)
@given(seed=SEEDS, runs=RUN_COUNTS)
def test_each_run_orders_every_test_once_and_follows_the_z1_rule(seed: int, runs: int) -> None:
    plan = build_plan(seed, runs, DEFAULT_CONFIGS)
    all_tests = sorted(test.nodeid for test in plan.tests)
    [polluter] = plan.extras["Z1"]

    for run in plan.runs:
        assert sorted(run.order) == all_tests
        position = {nodeid: i for i, nodeid in enumerate(run.order)}
        victims = [position[nodeid] for nodeid in plan.members["Z1"]]
        if run.faults["Z1"]:
            assert position[polluter] < min(victims)
        else:
            assert position[polluter] > max(victims)


@settings(deadline=None, max_examples=50)
@given(
    seed=SEEDS,
    runs=RUN_COUNTS,
    rate=st.floats(min_value=0.0, max_value=1.0),
    size=st.integers(min_value=1, max_value=6),
)
def test_changing_one_configuration_does_not_move_the_others(
    seed: int, runs: int, rate: float, size: int
) -> None:
    changed_configs = tuple(
        replace(config, rate=rate, size=size) if config.key == "Z3" else config
        for config in DEFAULT_CONFIGS
    )
    before = build_plan(seed, runs, DEFAULT_CONFIGS)
    after = build_plan(seed, runs, changed_configs)

    for old, new in zip(before.runs, after.runs, strict=True):
        for key in ("Z1", "Z2", "Z4", "Z5", "Z6", "Z7"):
            assert old.faults[key] == new.faults[key]


@settings(deadline=None, max_examples=30)
@given(seed=SEEDS, runs=st.integers(min_value=2, max_value=40))
def test_adding_runs_does_not_change_earlier_runs(seed: int, runs: int) -> None:
    shorter = build_plan(seed, runs - 1, DEFAULT_CONFIGS)
    longer = build_plan(seed, runs, DEFAULT_CONFIGS)

    assert longer.runs[: runs - 1] == shorter.runs


@settings(deadline=None, max_examples=50)
@given(seed=SEEDS, runs=RUN_COUNTS)
def test_z4_failures_start_just_before_midnight(seed: int, runs: int) -> None:
    plan = build_plan(seed, runs, DEFAULT_CONFIGS)

    for run in plan.runs:
        start = datetime.fromisoformat(run.started_at)
        day = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=run.run)
        seconds = (start - day).total_seconds()
        if run.faults["Z4"]:
            assert 86_398.0 <= seconds <= 86_399.5
        else:
            assert 3_600.0 <= seconds < 23 * 3_600.0


@settings(deadline=None, max_examples=50)
@given(items=st.lists(st.integers(), max_size=30), seed=SEEDS)
def test_shuffle_is_a_deterministic_permutation(items: list[int], seed: int) -> None:
    first = shuffled(items, stream(seed, "shuffle"))
    second = shuffled(items, stream(seed, "shuffle"))

    assert first == second
    assert sorted(first) == sorted(items)


@pytest.mark.parametrize("rate", [0.05, 0.2, 0.5])
def test_shared_faults_fire_at_the_configured_rate(rate: float) -> None:
    runs = 2000
    plan = build_plan(1, runs, default_configs(rate=rate))
    fired = sum(run.faults[config.key] for run in plan.runs for config in plan.configs)

    assert _two_sided_binomial_p(fired, runs * len(plan.configs), rate) >= 0.001


def test_independent_members_fail_independently_at_the_configured_rate() -> None:
    runs = 2000
    configs = tuple(replace(config, shared_fault=False) for config in DEFAULT_CONFIGS)
    plan = build_plan(11, runs, configs)
    member_count = sum(config.size for config in configs)
    failures = sum(
        len(set(run.failing) & set(plan.members[config.key]))
        for run in plan.runs
        for config in configs
    )
    z5 = set(plan.members["Z5"])
    all_four_together = sum(z5 <= set(run.failing) for run in plan.runs)

    assert _two_sided_binomial_p(failures, runs * member_count, 0.2) >= 0.001
    assert all_four_together < 0.01 * runs  # expected 0.2**4 * 2000 = 3.2


def test_z3_failures_are_enriched_on_small_parallel_runners() -> None:
    plan = build_plan(7, 2000, DEFAULT_CONFIGS)
    faulty = [run for run in plan.runs if run.faults["Z3"]]
    clean = [run for run in plan.runs if not run.faults["Z3"]]

    assert sum(run.runner == "small" for run in faulty) / len(faulty) > 0.7
    assert sum(run.runner == "small" for run in clean) / len(clean) < 0.4
    assert sum(run.workers == 4 for run in faulty) / len(faulty) > 0.7
    assert sum(run.workers == 4 for run in clean) / len(clean) < 0.4


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"key": "Z9"}, "unknown zoo configuration"),
        ({"size": 0}, "size must be at least 1"),
        ({"rate": 1.5}, "rate must be between 0 and 1"),
    ],
)
def test_invalid_configurations_are_refused(changes: dict[str, object], message: str) -> None:
    fields: dict[str, object] = {"key": "Z1", "cause": "test-order", "stressor": None, "size": 3}
    fields.update(changes)

    with pytest.raises(ValueError, match=message):
        ZooConfig(**fields)  # type: ignore[arg-type]


def test_invalid_plans_are_refused() -> None:
    with pytest.raises(ValueError, match="runs must be at least 1"):
        build_plan(1, 0, DEFAULT_CONFIGS)
    with pytest.raises(ValueError, match="each configuration may appear once"):
        build_plan(1, 3, (DEFAULT_CONFIGS[0], DEFAULT_CONFIGS[0]))
