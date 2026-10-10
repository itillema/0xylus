"""Generate a zoo suite and run it, from the repository root:

python -m benchmarks.zoo --seed 1 --runs 30
"""

import argparse
import sys
import time
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from benchmarks.zoo.configs import DEFAULT_RATE, ZooConfig, default_configs
from benchmarks.zoo.plan import build_plan
from benchmarks.zoo.render import write_suite
from benchmarks.zoo.run import ZooRunError, run_suite

DEFAULT_OUT = Path("benchmarks") / "zoo" / "out"


def _parse_bool(text: str) -> bool:
    lowered = text.strip().lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    raise ValueError(f"expected true or false, not {text!r}")


def apply_override(configs: Sequence[ZooConfig], text: str) -> tuple[ZooConfig, ...]:
    """Apply one KEY.FIELD=VALUE override, such as Z3.rate=0.3 or Z3.shared_fault=false."""
    target, equals, raw = text.partition("=")
    key, dot, field = target.partition(".")
    if not equals or not dot:
        raise ValueError(f"expected KEY.FIELD=VALUE, not {text!r}")
    key = key.strip().upper()
    if key not in {config.key for config in configs}:
        raise ValueError(f"unknown configuration {key!r} in {text!r}")
    updated = []
    for config in configs:
        if config.key != key:
            updated.append(config)
        elif field == "rate":
            updated.append(replace(config, rate=float(raw)))
        elif field == "size":
            updated.append(replace(config, size=int(raw)))
        elif field == "shared_fault":
            updated.append(replace(config, shared_fault=_parse_bool(raw)))
        else:
            raise ValueError(f"unknown field {field!r} in {text!r}: use rate, size or shared_fault")
    return tuple(updated)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m benchmarks.zoo",
        description="Generate a flaky-zoo suite and run it, writing one JUnit XML report per run.",
    )
    parser.add_argument("--seed", type=int, default=1, help="suite seed (default: 1)")
    parser.add_argument("--runs", type=int, default=30, help="number of runs (default: 30)")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory (default: benchmarks/zoo/out/seed-<seed>)",
    )
    parser.add_argument(
        "--rate", type=float, default=DEFAULT_RATE, help="failure rate for every configuration"
    )
    parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY.FIELD=VALUE",
        help="override one configuration, e.g. Z3.rate=0.3, Z3.size=4 or Z3.shared_fault=false",
    )
    parser.add_argument("--no-run", action="store_true", help="only generate the suite")
    args = parser.parse_args(argv)

    try:
        configs = default_configs(rate=args.rate)
        for text in args.overrides:
            configs = apply_override(configs, text)
        plan = build_plan(args.seed, args.runs, configs)
    except ValueError as exc:
        parser.error(str(exc))

    out: Path = args.out or DEFAULT_OUT / f"seed-{args.seed}"
    if args.no_run:
        write_suite(plan, out / "suite")
        print(f"suite written to {out / 'suite'} (seed {plan.seed}, {len(plan.runs)} runs planned)")
        return 0

    started = time.perf_counter()
    try:
        result = run_suite(plan, out)
    except ZooRunError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    elapsed = time.perf_counter() - started

    counts = {
        config.key: sum(run.faults[config.key] for run in plan.runs) for config in plan.configs
    }
    faults = ", ".join(f"{key} {count}" for key, count in counts.items())
    print(f"suite:   {result.suite} (seed {plan.seed})")
    print(f"reports: {len(result.reports)} JUnit XML files in {result.reports[0].parent}")
    print(f"faults:  {faults} (runs where each configuration failed)")
    print(f"elapsed: {elapsed:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
