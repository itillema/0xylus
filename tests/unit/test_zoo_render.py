"""The generated zoo suite matches its plan."""

import ast
from dataclasses import replace
from pathlib import Path

from benchmarks.zoo.configs import DEFAULT_CONFIGS
from benchmarks.zoo.plan import build_plan, manifest_json
from benchmarks.zoo.render import suite_files, write_suite


def _defined_tests(source: str, filename: str) -> set[str]:
    tree = ast.parse(source, filename=filename)
    compile(tree, filename, "exec")
    return {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }


def test_generated_modules_define_exactly_the_planned_tests() -> None:
    plan = build_plan(1, 5, DEFAULT_CONFIGS)
    files = suite_files(plan)
    planned: dict[str, set[str]] = {}
    for test in plan.tests:
        planned.setdefault(test.module, set()).add(test.name)

    modules = {name for name in files if name.startswith("test_") and name.endswith(".py")}
    assert modules == set(planned)
    for module in modules:
        assert _defined_tests(files[module], module) == planned[module]


def test_generated_conftest_compiles() -> None:
    files = suite_files(build_plan(1, 2, DEFAULT_CONFIGS))

    compile(files["conftest.py"], "conftest.py", "exec")
    assert "junit_family = xunit2" in files["pytest.ini"]


def test_write_suite_writes_every_file_byte_for_byte(tmp_path: Path) -> None:
    plan = build_plan(3, 4, DEFAULT_CONFIGS)
    expected = suite_files(plan)

    written = write_suite(plan, tmp_path / "suite")

    assert {path.name for path in written} == set(expected)
    for path in written:
        assert path.read_bytes() == expected[path.name].encode("utf-8")
    assert (tmp_path / "suite" / "manifest.json").read_text(encoding="utf-8") == manifest_json(plan)


def test_size_sets_the_number_of_generated_members() -> None:
    configs = tuple(
        replace(config, size=5) if config.key == "Z5" else config for config in DEFAULT_CONFIGS
    )
    files = suite_files(build_plan(1, 2, configs))

    assert files["test_z5_network.py"].count("def test_z5_api_") == 5
    assert "ConnectionResetError" in files["test_z5_network.py"]
    assert "TimeoutError" in files["test_z5_network.py"]
