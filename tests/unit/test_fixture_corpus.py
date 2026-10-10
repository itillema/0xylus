"""Real JUnit XML fixtures: each loads safely, is documented, and shows the facts we rely on."""

import hashlib
from collections import Counter
from pathlib import Path
from xml.etree.ElementTree import Element

import pytest

from zeroxylus.errors import MalformedInputError
from zeroxylus.ingest.xmlsafe import load_junit_root

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "junit"
PYTEST = FIXTURES / "pytest"
SUREFIRE = FIXTURES / "surefire"
REAL_DIALECTS = [PYTEST, SUREFIRE]
TRUNCATED_WILD_REPORT = (
    SUREFIRE
    / "wild"
    / "camunda"
    / "truncated"
    / "TEST-io.zeebe.broker.it.clustering.BrokerLeaderChangeTest-it-testrun.xml"
)
GENERATED_SUREFIRE = [
    "surefire-3.6.0/junit6",
    "surefire-3.6.0/junit4",
    "surefire-3.5.4/junit5",
    "surefire-3.5.4/junit4",
]


def _documented_files() -> list[Path]:
    """Every fixture file except the generators' sources and the READMEs themselves."""
    return sorted(
        path
        for dialect in REAL_DIALECTS
        for path in dialect.rglob("*")
        if path.is_file()
        and path.name != "README.md"
        and "source" not in path.relative_to(dialect).parts
    )


def _real_fixtures() -> list[Path]:
    return [
        path
        for path in _documented_files()
        if path.suffix == ".xml" and path != TRUNCATED_WILD_REPORT
    ]


def _testcases(path: Path) -> list[Element]:
    return list(load_junit_root(path).iter("testcase"))


def _children(case: Element) -> list[str]:
    return [child.tag for child in case]


@pytest.mark.parametrize("path", _real_fixtures(), ids=lambda p: p.name)
def test_real_fixture_loads(path: Path) -> None:
    assert load_junit_root(path).tag in {"testsuites", "testsuite"}


@pytest.mark.parametrize("path", _documented_files(), ids=lambda p: p.name)
def test_fixture_file_is_listed_in_its_readme_with_its_hash(path: Path) -> None:
    dialect = next(d for d in REAL_DIALECTS if d in path.parents)
    relative = path.relative_to(dialect).as_posix()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = [
        line
        for line in (dialect / "README.md").read_text(encoding="utf-8").splitlines()
        if f"`{relative}`" in line
    ]
    assert rows, f"{relative} is not listed in {dialect.name}/README.md"
    assert any(digest in row for row in rows), f"{relative}: README hash doesn't match {digest}"


def test_xunit1_records_file_and_line_but_xunit2_does_not() -> None:
    xunit1 = _testcases(PYTEST / "xunit1-outcomes.xml")
    xunit2 = _testcases(PYTEST / "xunit2-outcomes.xml")

    assert all(case.get("file") and case.get("line") is not None for case in xunit1)
    assert not any(case.get("file") or case.get("line") for case in xunit2)


def test_pytest_9_names_the_testsuites_root_and_pytest_7_does_not() -> None:
    assert load_junit_root(PYTEST / "xunit2-outcomes.xml").get("name") == "pytest tests"
    assert load_junit_root(PYTEST / "xunit2-outcomes-pytest7.4.4.xml").get("name") is None


@pytest.mark.parametrize("name", ["xunit2-outcomes.xml", "xunit2-xdist.xml"])
def test_failure_then_teardown_error_is_two_entries_for_one_execution(name: str) -> None:
    entries = [
        case
        for case in _testcases(PYTEST / name)
        if case.get("name") == "test_fails_and_errors_in_teardown"
    ]

    assert [_children(case)[0] for case in entries] == ["failure", "error"]
    error = entries[1].find("error")
    assert error is not None
    assert (error.get("message") or "").startswith("failed on teardown with")


def test_xdist_reports_in_arrival_order() -> None:
    names = [case.get("name") for case in _testcases(PYTEST / "xunit2-xdist.xml")]
    positions = [i for i, n in enumerate(names) if n == "test_fails_and_errors_in_teardown"]

    assert len(positions) == 2
    assert positions[1] - positions[0] > 1  # the two entries for one execution aren't adjacent


def test_pytest_repeat_appends_the_repeat_index_after_any_parameters() -> None:
    names = sorted(str(case.get("name")) for case in _testcases(PYTEST / "xunit2-repeat.xml"))

    assert names[:3] == ["test_repeated[1-3]", "test_repeated[2-3]", "test_repeated[3-3]"]
    assert "test_repeated_with_params[2-1-3]" in names


def test_collection_error_is_one_entry_with_an_empty_classname() -> None:
    [case] = _testcases(PYTEST / "xunit2-collection-error.xml")

    assert case.get("classname") == ""
    assert case.get("name") == "broken.test_broken_import"
    error = case.find("error")
    assert error is not None
    assert error.get("message") == "collection failure"


def test_rerunfailures_16_6_keeps_only_final_outcomes() -> None:
    cases = _testcases(PYTEST / "xunit2-rerunfailures-16.6.xml")

    assert Counter(case.get("name") for case in cases) == dict.fromkeys(
        [
            "test_passes",
            "test_fails_once_then_passes",
            "test_fails_twice_then_passes",
            "test_always_fails",
            "test_setup_error_once",
        ],
        1,
    )
    flaky = [case for case in cases if case.get("name") != "test_always_fails"]
    assert all(_children(case) == [] for case in flaky)  # failed attempts leave no trace


def test_rerunfailures_16_7_writes_failed_attempts_as_empty_entries() -> None:
    root = load_junit_root(PYTEST / "xunit2-rerunfailures-16.7.xml")
    cases = list(root.iter("testcase"))
    entries: dict[str, list[Element]] = {}
    for case in cases:
        entries.setdefault(str(case.get("name")), []).append(case)

    assert {name: len(found) for name, found in entries.items()} == {
        "test_passes": 1,
        "test_fails_once_then_passes": 2,
        "test_fails_twice_then_passes": 3,
        "test_always_fails": 3,
        "test_setup_error_once": 2,
    }
    for found in entries.values():
        assert all(_children(case) == [] for case in found[:-1])  # failed attempts look like passes
    assert _children(entries["test_always_fails"][-1]) == ["failure"]
    suite = root.find("testsuite")
    assert suite is not None
    assert suite.get("tests") == "5"  # final outcomes only


def test_hostile_ids_and_messages_survive_parsing() -> None:
    cases = _testcases(PYTEST / "xunit2-outcomes.xml")
    names = " ".join(str(case.get("name")) for case in cases)

    hostile = ["<script>alert(1)</script>", "pipe | in | a table", "@maintainer", "back`ticks`"]
    for fragment in hostile:
        assert fragment in names
    assert "\\u202e" in names  # pytest escapes non-ASCII characters in ids
    failure = next(
        case.find("failure")
        for case in cases
        if case.get("name") == "test_fails_with_hostile_message"
    )
    assert failure is not None
    assert "\u202e" in (failure.get("message") or "")  # messages keep raw characters


def test_truncated_wild_report_is_rejected_with_a_typed_error() -> None:
    with pytest.raises(MalformedInputError, match="unclosed CDATA section"):
        load_junit_root(TRUNCATED_WILD_REPORT)


def test_surefire_reports_are_bare_testsuites() -> None:
    surefire = [path for path in _real_fixtures() if SUREFIRE in path.parents]

    assert surefire
    assert {load_junit_root(path).tag for path in surefire} == {"testsuite"}


def test_every_rerun_element_appears_in_the_surefire_corpus() -> None:
    tags = {
        child.tag
        for path in _real_fixtures()
        if SUREFIRE in path.parents
        for case in _testcases(path)
        for child in case
    }

    assert {"flakyFailure", "flakyError", "rerunFailure", "rerunError"} <= tags


@pytest.mark.parametrize("directory", GENERATED_SUREFIRE)
def test_surefire_writes_retries_as_nested_elements(directory: str) -> None:
    cases = {
        str(case.get("name")): case
        for case in _testcases(SUREFIRE / directory / "TEST-com.example.fixtures.FlakyTest.xml")
    }

    assert {name: _children(case) for name, case in cases.items()} == {
        "passes": [],
        "failsOnceThenPasses": ["flakyFailure"],
        "errorsOnceThenPasses": ["flakyError"],
        "alwaysFails": ["failure", "rerunFailure", "rerunFailure"],
        "alwaysErrors": ["error", "rerunError", "rerunError"],
    }
    for case in cases.values():
        for child in case:
            if child.tag.startswith(("flaky", "rerun")):
                assert child.find("stackTrace") is not None


@pytest.mark.parametrize(
    ("directory", "tests", "flakes"),
    [
        ("surefire-3.6.0/junit6", "5", "2"),
        ("surefire-3.6.0/junit4", "5", "2"),
        ("surefire-3.5.4/junit5", "2", None),
        ("surefire-3.5.4/junit4", "11", None),
    ],
)
def test_surefire_testsuite_totals_depend_on_the_version(
    directory: str, tests: str, flakes: str | None
) -> None:
    suite = load_junit_root(SUREFIRE / directory / "TEST-com.example.fixtures.FlakyTest.xml")

    assert len(list(suite.iter("testcase"))) == 5  # the same five tests every time
    assert suite.get("tests") == tests
    assert suite.get("flakes") == flakes


def test_jupiter_nested_class_is_reported_in_the_outer_class_file() -> None:
    path = SUREFIRE / "surefire-3.6.0/junit6/TEST-com.example.fixtures.OutcomesTest.xml"

    assert "com.example.fixtures.OutcomesTest$WhenNested" in {
        case.get("classname") for case in _testcases(path)
    }


@pytest.mark.parametrize("directory", ["surefire-3.6.0/junit6", "surefire-3.5.4/junit5"])
def test_jupiter_names_are_method_names_with_types_and_index(directory: str) -> None:
    path = SUREFIRE / directory / "TEST-com.example.fixtures.OutcomesTest.xml"
    names = {str(case.get("name")) for case in _testcases(path)}

    assert {"customDisplayName", "parameterized(int)[2]", "hostileArguments(String)[1]"} <= names
    assert not any("<script>" in name or "display name" in name for name in names)


@pytest.mark.parametrize("directory", ["surefire-3.6.0/junit4", "surefire-3.5.4/junit4"])
def test_junit4_parameterized_names_follow_the_runner_pattern(directory: str) -> None:
    path = SUREFIRE / directory / "TEST-com.example.fixtures.ParameterizedValuesTest.xml"

    assert {case.get("name") for case in _testcases(path)} == {
        "rejectsTwo[0: value 1]",
        "rejectsTwo[1: value 2]",
        "rejectsTwo[2: value 3]",
    }


def test_wild_reports_write_output_before_rerun_elements() -> None:
    [always_fail] = _testcases(
        SUREFIRE / "wild/junit-plugin-gh-237/TEST-io.olamy.AlwaysFailTest.xml"
    )
    [failing] = _testcases(
        SUREFIRE / "wild/camunda/TEST-com.github.pihme.jenkinstestbed.module1.FailingTest.xml"
    )

    assert _children(always_fail) == ["failure", "system-out", "system-err"] + ["rerunFailure"] * 3
    assert _children(failing) == ["failure", "system-out"] + ["rerunFailure"] * 15
