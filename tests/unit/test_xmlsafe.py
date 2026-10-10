import io
import re
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from zeroxylus.errors import (
    InputError,
    InputTooLargeError,
    MalformedInputError,
    UnsafeXMLError,
)
from zeroxylus.ingest.xmlsafe import JUNIT_ROOT_TAGS, load_junit_root, parse_junit_stream

SYNTHETIC = Path(__file__).resolve().parents[1] / "fixtures" / "junit" / "synthetic"

EXPECTED_ERRORS: dict[str, type[InputError]] = {
    "xxe-system-entity.xml": UnsafeXMLError,
    "xxe-parameter-entity.xml": UnsafeXMLError,
    "external-dtd.xml": UnsafeXMLError,
    "internal-dtd.xml": UnsafeXMLError,
    "billion-laughs.xml": UnsafeXMLError,
    "quadratic-blowup.xml": UnsafeXMLError,
    "invalid-utf8.xml": MalformedInputError,
    "encoding-mismatch.xml": MalformedInputError,
    "invalid-char-reference.xml": MalformedInputError,
    "truncated.xml": MalformedInputError,
    "empty.xml": MalformedInputError,
    "wrong-root.xml": MalformedInputError,
}


def _report_of_size(size: int) -> bytes:
    """A valid JUnit report padded with a comment to exactly `size` bytes."""
    head, tail = b"<testsuites><!--", b"--></testsuites>"
    return head + b"x" * (size - len(head) - len(tail)) + tail


def test_every_synthetic_sample_has_an_expected_error() -> None:
    assert sorted(path.name for path in SYNTHETIC.glob("*.xml")) == sorted(EXPECTED_ERRORS)


def test_every_synthetic_sample_is_documented_in_the_readme() -> None:
    readme = (SYNTHETIC / "README.md").read_text(encoding="utf-8")
    for name, error in EXPECTED_ERRORS.items():
        assert f"| `{name}` |" in readme
        assert f"| `{error.__name__}` |" in readme


@pytest.mark.parametrize(("name", "error"), sorted(EXPECTED_ERRORS.items()))
def test_synthetic_sample_is_rejected_with_a_typed_error(
    name: str, error: type[InputError]
) -> None:
    with pytest.raises(error):
        load_junit_root(SYNTHETIC / name)


@pytest.mark.parametrize(
    "document",
    [
        b'<?xml version="1.0" encoding="UTF-8"?>\n<testsuites name="pytest tests"/>\n',
        b'<testsuite name="bare" tests="1"><testcase classname="c" name="n"/></testsuite>',
        '<testsuites name="café \U0001f600"/>'.encode(),
    ],
)
def test_minimal_reports_load(tmp_path: Path, document: bytes) -> None:
    path = tmp_path / "report.xml"
    path.write_bytes(document)

    assert load_junit_root(path).tag in JUNIT_ROOT_TAGS


def test_file_over_the_cap_is_rejected_before_parsing(tmp_path: Path) -> None:
    path = tmp_path / "oversized.xml"
    path.write_bytes(_report_of_size(1025))

    with pytest.raises(InputTooLargeError):
        load_junit_root(path, max_bytes=1024)


def test_file_exactly_at_the_cap_loads(tmp_path: Path) -> None:
    path = tmp_path / "at-cap.xml"
    path.write_bytes(_report_of_size(1024))

    assert load_junit_root(path, max_bytes=1024).tag == "testsuites"


def test_stream_over_the_cap_is_rejected_while_reading() -> None:
    stream = io.BytesIO(_report_of_size(64 * 1024))

    with pytest.raises(InputTooLargeError):
        parse_junit_stream(stream, max_bytes=1024)


def test_errors_name_the_source() -> None:
    source = "results/run-7.xml"

    with pytest.raises(MalformedInputError, match=re.escape(source)):
        parse_junit_stream(io.BytesIO(b"<oops"), source=source)


@settings(deadline=None, max_examples=300)
@given(st.binary(max_size=4096))
def test_arbitrary_bytes_load_or_raise_an_input_error(data: bytes) -> None:
    try:
        root = parse_junit_stream(io.BytesIO(data), max_bytes=8192)
    except InputError:
        return
    assert root.tag in JUNIT_ROOT_TAGS


@settings(deadline=None, max_examples=300)
@given(st.text(max_size=300))
def test_arbitrary_text_inside_a_report_loads_or_raises_an_input_error(text: str) -> None:
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<testsuites><testsuite name="{text}"><testcase classname="c" name="n">{text}'
        "</testcase></testsuite></testsuites>"
    ).encode()
    try:
        root = parse_junit_stream(io.BytesIO(document), max_bytes=64 * 1024)
    except InputError:
        return
    assert root.tag == "testsuites"
