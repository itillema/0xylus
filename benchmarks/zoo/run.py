"""Run a generated zoo suite once per planned run, writing one JUnit XML report per run."""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from benchmarks.zoo.plan import Plan
from benchmarks.zoo.render import write_suite

RUN_TIMEOUT_SECONDS = 120
_ISOLATING_ENV = {
    # No installed plugins: runs stay independent of the environment and start faster.
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONIOENCODING": "utf-8",
}
_DROPPED_ENV = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")


class ZooRunError(RuntimeError):
    """A run ended in a way the plan doesn't explain, such as a pytest usage error."""


@dataclass(frozen=True)
class SuiteRun:
    """Where a run of the zoo put its files."""

    suite: Path
    manifest: Path
    reports: tuple[Path, ...]
    """One JUnit XML report per planned run, in run order."""


def report_path(junit_dir: Path, run: int) -> Path:
    return junit_dir / f"run-{run:04d}.xml"


def run_suite(plan: Plan, out: Path, *, python: str = sys.executable) -> SuiteRun:
    """Write the suite to `out/suite` and run it once per planned run into `out/junit`.

    Each run is a fresh pytest process. The controls always fail, so pytest exits with 1; any
    other exit code except 0 means something went wrong and raises `ZooRunError`.
    """
    suite = out / "suite"
    junit = out / "junit"
    write_suite(plan, suite)
    junit.mkdir(parents=True, exist_ok=True)
    for stale in junit.glob("run-*.xml"):
        stale.unlink()
    manifest = (suite / "manifest.json").resolve()
    env = {key: value for key, value in os.environ.items() if key not in _DROPPED_ENV}
    env |= _ISOLATING_ENV | {"ZOO_MANIFEST": str(manifest)}

    reports = []
    for run in plan.runs:
        report = report_path(junit, run.run)
        command = [
            python,
            "-m",
            "pytest",
            str(suite),
            "-c",
            str(suite / "pytest.ini"),
            "--rootdir",
            str(suite),
            "-q",
            f"--junitxml={report}",
        ]
        result = subprocess.run(
            command,
            env=env | {"ZOO_RUN": str(run.run)},
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=RUN_TIMEOUT_SECONDS,
            check=False,
        )
        if result.returncode not in (0, 1) or not report.is_file():
            raise ZooRunError(
                f"run {run.run}: pytest exited with {result.returncode}\n"
                f"{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
            )
        reports.append(report)
    return SuiteRun(suite=suite, manifest=manifest, reports=tuple(reports))
