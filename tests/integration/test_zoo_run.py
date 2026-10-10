"""The zoo end to end: generated suites run under pytest exactly as planned."""

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from xml.etree.ElementTree import Element

import pytest

from benchmarks.zoo.configs import DEFAULT_CONFIGS
from benchmarks.zoo.plan import build_plan
from benchmarks.zoo.run import run_suite
from zeroxylus.ingest.xmlsafe import load_junit_root

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]


def _nodeid(case: Element) -> str:
    return f"{case.get('classname')}.py::{case.get('name')}"


def _failed(case: Element) -> bool:
    return case.find("failure") is not None or case.find("error") is not None


def _outcomes(report: Path) -> tuple[list[str], list[str]]:
    """The failing node ids (sorted) and every node id in report order."""
    cases = list(load_junit_root(report).iter("testcase"))
    return sorted(_nodeid(case) for case in cases if _failed(case)), [_nodeid(c) for c in cases]


def test_thirty_seeded_runs_finish_in_time_and_match_the_plan(tmp_path: Path) -> None:
    plan = build_plan(1, 30, DEFAULT_CONFIGS)

    started = time.perf_counter()
    result = run_suite(plan, tmp_path)
    elapsed = time.perf_counter() - started

    assert elapsed < 120, f"30 runs took {elapsed:.1f} s"
    assert len(result.reports) == 30
    z2_members = set(plan.members["Z2"])
    failing_z2: list[float] = []
    passing_z2: list[float] = []
    for run, report in zip(plan.runs, result.reports, strict=True):
        failing, order = _outcomes(report)
        assert failing == list(run.failing), f"run {run.run}"
        assert order == list(run.order), f"run {run.run}"
        for case in load_junit_root(report).iter("testcase"):
            if _nodeid(case) in z2_members:
                duration = float(case.get("time") or 0)
                (failing_z2 if _failed(case) else passing_z2).append(duration)

    assert failing_z2, "seed 1 should plant Z2 failures"
    assert min(failing_z2) >= 0.12  # failing members wait out the 0.15 s timeout
    assert statistics.median(passing_z2) < 0.1


def test_the_same_seed_gives_the_same_outcomes(tmp_path: Path) -> None:
    first = run_suite(build_plan(5, 5, DEFAULT_CONFIGS), tmp_path / "first")
    second = run_suite(build_plan(5, 5, DEFAULT_CONFIGS), tmp_path / "second")

    assert first.manifest.read_bytes() == second.manifest.read_bytes()
    assert [_outcomes(r) for r in first.reports] == [_outcomes(r) for r in second.reports]


def test_cli_generates_and_runs_a_suite(tmp_path: Path) -> None:
    out = tmp_path / "zoo"
    command = [sys.executable, "-m", "benchmarks.zoo", "--seed", "3", "--runs", "2"]
    command += ["--out", str(out), "--set", "Z3.rate=1"]

    result = subprocess.run(
        command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=300, check=False
    )

    assert result.returncode == 0, result.stderr
    reports = sorted((out / "junit").glob("run-*.xml"))
    assert [path.name for path in reports] == ["run-0000.xml", "run-0001.xml"]
    manifest = json.loads((out / "suite" / "manifest.json").read_text(encoding="utf-8"))
    z3 = next(config for config in manifest["configs"] if config["key"] == "Z3")
    assert z3["rate"] == 1.0
    for report in reports:
        failing, _ = _outcomes(report)
        assert set(z3["members"]) <= set(failing)  # rate 1 fails Z3 in every run
