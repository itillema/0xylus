"""Load untrusted JUnit XML safely: defusedxml only, with a size cap and typed errors.

DTDs, entity declarations and external references are refused outright. The size cap is checked
before parsing and again while reading, so streams without a known size are capped too.
"""

from pathlib import Path
from typing import Protocol
from xml.etree.ElementTree import Element

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import ParseError, parse

from zeroxylus.errors import InputTooLargeError, MalformedInputError, UnsafeXMLError

DEFAULT_MAX_BYTES = 200 * 1024 * 1024
"""Default size limit for one input file: 200 MiB."""

JUNIT_ROOT_TAGS = frozenset({"testsuites", "testsuite"})


class BinaryReadable(Protocol):
    """A binary stream, such as an open file or a member of a zip archive."""

    def read(self, size: int = -1, /) -> bytes: ...


class _CappedReader:
    """Pass reads through to a stream, failing once more than `limit` bytes have been read."""

    def __init__(self, stream: BinaryReadable, limit: int, source: str) -> None:
        self._stream = stream
        self._limit = limit
        self._source = source
        self._seen = 0

    def read(self, size: int = -1, /) -> bytes:
        if size < 0:
            size = self._limit + 1 - self._seen
        chunk = self._stream.read(size)
        self._seen += len(chunk)
        if self._seen > self._limit:
            raise InputTooLargeError(f"{self._source}: larger than the {self._limit}-byte limit")
        return chunk


def load_junit_root(path: Path, *, max_bytes: int = DEFAULT_MAX_BYTES) -> Element:
    """Parse the JUnit XML report at `path` and return its root element.

    Raises:
        InputTooLargeError: the file is larger than `max_bytes`.
        UnsafeXMLError: the document contains a DTD, entity declarations or external references.
        MalformedInputError: the document isn't well-formed XML, or its root isn't
            `<testsuites>` or `<testsuite>`.
    """
    size = path.stat().st_size
    if size > max_bytes:
        raise InputTooLargeError(f"{path}: {size} bytes, over the {max_bytes}-byte limit")
    # Open the file here rather than passing the path to the parser, so the parser never owns
    # the handle (an unclosed parser-owned handle warns on Python 3.15).
    with path.open("rb") as stream:
        return parse_junit_stream(stream, max_bytes=max_bytes, source=str(path))


def parse_junit_stream(
    stream: BinaryReadable, *, max_bytes: int = DEFAULT_MAX_BYTES, source: str = "<stream>"
) -> Element:
    """Parse a JUnit XML report from a binary stream and return its root element.

    `source` names the stream in error messages. Raises the same errors as `load_junit_root`.
    """
    reader = _CappedReader(stream, max_bytes, source)
    try:
        tree = parse(reader, forbid_dtd=True, forbid_entities=True, forbid_external=True)
    except DefusedXmlException as exc:
        raise UnsafeXMLError(f"{source}: refused to parse: {exc!r}") from exc
    except ParseError as exc:
        raise MalformedInputError(f"{source}: not well-formed XML: {exc}") from exc
    root = tree.getroot()
    if root is None or root.tag not in JUNIT_ROOT_TAGS:
        found = "nothing" if root is None else f"<{root.tag}>"
        raise MalformedInputError(f"{source}: expected <testsuites> or <testsuite>, found {found}")
    return root
