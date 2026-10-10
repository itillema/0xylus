# Synthetic JUnit XML samples

**Every file in this directory is synthetic.** None is output from a test tool: each was written for this project's
tests by [`make_samples.py`](make_samples.py) on 2026-10-10, and is licensed like the rest of the repository
(Apache-2.0). They exist to prove that hostile or malformed input is rejected with a typed error, not a crash. Real
tool output lives in the sibling `pytest/` and `surefire/` directories.

| File | What it contains | Expected error |
| --- | --- | --- |
| `xxe-system-entity.xml` | An external entity that would read `/etc/passwd` | `UnsafeXMLError` |
| `xxe-parameter-entity.xml` | A parameter entity that would fetch a remote DTD | `UnsafeXMLError` |
| `external-dtd.xml` | A reference to an external DTD | `UnsafeXMLError` |
| `internal-dtd.xml` | An internal DTD with no entities | `UnsafeXMLError` |
| `billion-laughs.xml` | Nested entities that would expand to 10^9 copies of "lol" | `UnsafeXMLError` |
| `quadratic-blowup.xml` | One large entity referenced many times (scaled down) | `UnsafeXMLError` |
| `invalid-utf8.xml` | A byte sequence that isn't valid UTF-8 (`C3 28`) | `MalformedInputError` |
| `encoding-mismatch.xml` | A declaration that says UTF-16, on ASCII content | `MalformedInputError` |
| `invalid-char-reference.xml` | A character reference to NUL (`&#0;`) | `MalformedInputError` |
| `truncated.xml` | A report cut off mid-element | `MalformedInputError` |
| `empty.xml` | An empty file | `MalformedInputError` |
| `wrong-root.xml` | Well-formed XML whose root isn't `<testsuites>` or `<testsuite>` | `MalformedInputError` |

The oversized sample isn't committed. `tests/unit/test_xmlsafe.py` generates it in a temporary directory, against a
1 KiB cap.
