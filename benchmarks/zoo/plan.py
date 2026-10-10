"""The ground truth for one zoo suite: which tests fail in which run, decided by seeded draws.

Every draw comes from its own stream, keyed by (seed, run, purpose), so the same seed always gives
the same plan, and changing one configuration or the number of runs never moves another's draws.
Only `random.Random.random()` is used: for an integer seed, CPython guarantees that sequence
across versions. Shuffles use our own Fisher-Yates loop for the same reason.
"""

import hashlib
import json
import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from benchmarks.zoo.configs import (
    CONTROL_FAILURES,
    CONTROL_MODULE,
    CONTROL_PASSES,
    LAYOUT,
    ZooConfig,
)

SCHEMA_VERSION = 1
FIRST_RUN_DAY = datetime(2026, 1, 1, tzinfo=UTC)
"""Run r is dated r days after this, so every run has its own synthetic date."""

type JSONValue = str | int | float | bool | list[JSONValue] | dict[str, JSONValue] | None


def stream(seed: int, *labels: str | int) -> random.Random:
    """An independent random stream for one (seed, labels) key."""
    key = ":".join(["zoo", str(seed), *(str(label) for label in labels)])
    digest = hashlib.sha256(key.encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def shuffled[T](items: Sequence[T], rng: random.Random) -> list[T]:
    """A Fisher-Yates shuffle that only calls `rng.random()`."""
    result = list(items)
    for i in range(len(result) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        result[i], result[j] = result[j], result[i]
    return result


@dataclass(frozen=True)
class PlannedTest:
    """One test in the generated suite, by pytest node id."""

    nodeid: str

    @property
    def module(self) -> str:
        return self.nodeid.split("::", 1)[0]

    @property
    def classname(self) -> str:
        """The JUnit XML `classname` pytest writes for this test."""
        return self.module.removesuffix(".py").replace("/", ".")

    @property
    def name(self) -> str:
        """The JUnit XML `name` pytest writes for this test."""
        return self.nodeid.split("::", 1)[1]


@dataclass(frozen=True)
class RunPlan:
    """What happens in one run of the suite."""

    run: int
    faults: dict[str, bool]
    """Per configuration: whether its shared fault fired, or (without one) any member failed."""
    failing: tuple[str, ...]
    """Node ids of every test that fails in this run, sorted."""
    order: tuple[str, ...]
    """Node ids in the order pytest runs them."""
    started_at: str
    """Synthetic start time (ISO 8601, UTC). Runs where Z4 fails start just before midnight."""
    runner: str
    """Synthetic runner size, "small" or "large". Runs where Z3 fails are mostly small."""
    workers: int
    """Synthetic number of parallel workers, 1 or 4. Runs where Z3 fails mostly use 4."""


@dataclass(frozen=True)
class Plan:
    """The ground truth for one generated suite."""

    seed: int
    configs: tuple[ZooConfig, ...]
    tests: tuple[PlannedTest, ...]
    members: dict[str, tuple[str, ...]]
    extras: dict[str, tuple[str, ...]]
    control_pass: tuple[str, ...]
    control_fail: tuple[str, ...]
    runs: tuple[RunPlan, ...]

    def to_manifest(self) -> dict[str, JSONValue]:
        """The plan as JSON-ready data, with a fixed key order."""
        return {
            "schema_version": SCHEMA_VERSION,
            "generator": "benchmarks.zoo",
            "mode": "seeded",
            "seed": self.seed,
            "runs": len(self.runs),
            "configs": [
                {
                    "key": config.key,
                    "cause": config.cause,
                    "stressor": config.stressor,
                    "size": config.size,
                    "rate": config.rate,
                    "shared_fault": config.shared_fault,
                    "module": LAYOUT[config.key].module,
                    "members": list(self.members[config.key]),
                    "extras": list(self.extras[config.key]),
                }
                for config in self.configs
            ],
            "controls": {
                "module": CONTROL_MODULE,
                "always_pass": list(self.control_pass),
                "always_fail": list(self.control_fail),
            },
            "tests": [
                {"nodeid": test.nodeid, "classname": test.classname, "name": test.name}
                for test in self.tests
            ],
            "plan": [
                {
                    "run": run.run,
                    "faults": dict(run.faults),
                    "failing": list(run.failing),
                    "order": list(run.order),
                    "started_at": run.started_at,
                    "runner": run.runner,
                    "workers": run.workers,
                }
                for run in self.runs
            ],
        }


def manifest_json(plan: Plan) -> str:
    """The manifest file's exact text: identical for identical plans."""
    return json.dumps(plan.to_manifest(), indent=2, ensure_ascii=False) + "\n"


def build_plan(seed: int, runs: int, configs: Sequence[ZooConfig]) -> Plan:
    """Plan `runs` runs of a suite with the given configurations and the control tests."""
    if runs < 1:
        raise ValueError(f"runs must be at least 1, not {runs}")
    keys = [config.key for config in configs]
    if len(set(keys)) != len(keys):
        raise ValueError(f"each configuration may appear once: {keys}")

    tests: list[PlannedTest] = []
    members: dict[str, tuple[str, ...]] = {}
    extras: dict[str, tuple[str, ...]] = {}
    for config in configs:
        layout = LAYOUT[config.key]
        extras[config.key] = tuple(f"{layout.module}::{name}" for name in layout.extras)
        members[config.key] = tuple(
            f"{layout.module}::{layout.member_stem}_{i}" for i in range(1, config.size + 1)
        )
        tests.extend(PlannedTest(nodeid) for nodeid in extras[config.key] + members[config.key])
    control_pass = tuple(
        f"{CONTROL_MODULE}::test_control_pass_{i}" for i in range(1, CONTROL_PASSES + 1)
    )
    control_fail = tuple(
        f"{CONTROL_MODULE}::test_control_fail_{i}" for i in range(1, CONTROL_FAILURES + 1)
    )
    tests.extend(PlannedTest(nodeid) for nodeid in control_pass + control_fail)

    run_plans = tuple(
        _plan_run(seed, run, tuple(configs), members, extras, control_fail, tests)
        for run in range(runs)
    )
    return Plan(
        seed=seed,
        configs=tuple(configs),
        tests=tuple(tests),
        members=members,
        extras=extras,
        control_pass=control_pass,
        control_fail=control_fail,
        runs=run_plans,
    )


def _plan_run(
    seed: int,
    run: int,
    configs: tuple[ZooConfig, ...],
    members: dict[str, tuple[str, ...]],
    extras: dict[str, tuple[str, ...]],
    control_fail: tuple[str, ...],
    tests: Sequence[PlannedTest],
) -> RunPlan:
    faults: dict[str, bool] = {}
    failing = set(control_fail)
    for config in configs:
        if config.shared_fault:
            fault = stream(seed, run, config.key, "fault").random() < config.rate
            hits = list(members[config.key]) if fault else []
        else:
            hits = [
                nodeid
                for i, nodeid in enumerate(members[config.key], start=1)
                if stream(seed, run, config.key, "member", i).random() < config.rate
            ]
        faults[config.key] = bool(hits)
        failing.update(hits)

    started_at = _started_at(seed, run, near_midnight=faults.get("Z4", False))
    runner, workers = _runner(seed, run, contended=faults.get("Z3", False))
    return RunPlan(
        run=run,
        faults=faults,
        failing=tuple(sorted(failing)),
        order=tuple(_order(seed, run, tests, faults, extras)),
        started_at=started_at,
        runner=runner,
        workers=workers,
    )


def _order(
    seed: int,
    run: int,
    tests: Sequence[PlannedTest],
    faults: dict[str, bool],
    extras: dict[str, tuple[str, ...]],
) -> list[str]:
    """Shuffle modules, then tests within each module, like pytest-randomly.

    In Z1's module, the polluter runs first when the victims fail and last otherwise, so the order
    in the report carries the order signal.
    """
    by_module: dict[str, list[str]] = {}
    for test in tests:
        by_module.setdefault(test.module, []).append(test.nodeid)
    rng = stream(seed, run, "order")
    polluters = set(extras.get("Z1", ()))
    order: list[str] = []
    for module in shuffled(list(by_module), rng):
        block = shuffled(by_module[module], rng)
        if polluters & set(block):
            rest = [nodeid for nodeid in block if nodeid not in polluters]
            first = sorted(polluters) if faults.get("Z1", False) else []
            last = [] if faults.get("Z1", False) else sorted(polluters)
            block = first + rest + last
        order.extend(block)
    return order


def _started_at(seed: int, run: int, *, near_midnight: bool) -> str:
    """Synthetic start: 0.5 to 2 s before midnight UTC if Z4 fails, otherwise 01:00 to 23:00."""
    rng = stream(seed, run, "started_at")
    day = FIRST_RUN_DAY + timedelta(days=run)
    if near_midnight:
        offset = 86_400 - (0.5 + 1.5 * rng.random())
    else:
        offset = 3_600 + 22 * 3_600 * rng.random()
    start = day + timedelta(seconds=offset)
    return start.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _runner(seed: int, run: int, *, contended: bool) -> tuple[str, int]:
    """Synthetic runner size and parallelism, enriched for small, parallel runners when Z3 fails."""
    p_small = 0.8 if contended else 0.3
    small = stream(seed, run, "runner").random() < p_small
    parallel = stream(seed, run, "workers").random() < p_small
    return ("small" if small else "large", 4 if parallel else 1)
