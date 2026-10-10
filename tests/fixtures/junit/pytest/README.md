# pytest JUnit XML fixtures

These files are real pytest output, generated on 2026-10-10 from the sample project in [`source/`](source/). Don't
edit them by hand. To change them, regenerate them as described below and update this README, including the hashes.

## Provenance

| Item | Value |
| --- | --- |
| Generated | 2026-10-10, in Docker, with the container hostname `fixturegen` and the project copied to `/work/sample` |
| Sample project | [`source/`](source/), written for these fixtures. Its tests fail on purpose and are never collected by this repository's test run |
| Generator | [`source/generate.sh`](source/generate.sh), which runs every pytest command listed below |
| License | Apache-2.0, like this repository. The reports are pytest's output for this project's own sample tests |

| Environment | Image | Python | Packages (from `pip freeze`) |
| --- | --- | --- | --- |
| current | `python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170` | 3.14.8 | pytest 9.1.1, pytest-repeat 0.9.4, pytest-xdist 3.8.0, execnet 2.1.2, pytest-rerunfailures 16.7 (then 16.6), iniconfig 2.3.1, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0 |
| legacy | `python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1` | 3.12.15 | pytest 7.4.4, iniconfig 2.3.1, packaging 26.3, pluggy 1.6.0 |

To regenerate, run these from the repository root (POSIX shell syntax), then update the hashes below:

```bash
docker run --rm --hostname fixturegen \
  -v "$PWD/tests/fixtures/junit/pytest/source:/work/source:ro" \
  -v "$PWD/tests/fixtures/junit/pytest:/work/out" \
  python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170 \
  sh /work/source/generate.sh current
docker run --rm --hostname fixturegen \
  -v "$PWD/tests/fixtures/junit/pytest/source:/work/source:ro" \
  -v "$PWD/tests/fixtures/junit/pytest:/work/out" \
  python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1 \
  sh /work/source/generate.sh legacy
```

Timestamps and durations change on every run, so regenerated files never match these hashes byte for byte.

## Files

Each command ran in `/work/sample` as `python -m pytest <options> --junitxml=<file> <directory>`.

| File | Environment | Options and directory | SHA-256 |
| --- | --- | --- | --- |
| `xunit1-outcomes.xml` | current | `-o junit_family=xunit1 -o junit_logging=all tests` | `1d9a04420145eeba87f448abe46e9898e152c69dbec909c8daae14f374024e3a` |
| `xunit2-outcomes.xml` | current | `-o junit_family=xunit2 -o junit_logging=all tests` | `f105cdb83c38f176cf41bccd36362492087917768d1c2bb80a544e38ec378b5d` |
| `xunit2-xdist.xml` | current | `-n 2 tests` | `88b751dc58d913bf0155d15eb31476f6280684a56494dceb785fdbffab657d4e` |
| `xunit2-repeat.xml` | current | `--count 3 repeat` | `6b9723389803f727c895be509b0451bee006c63a9d4b167c58203e6ab0d4e536` |
| `xunit2-collection-error.xml` | current | `broken` | `6c7a07843781d67990b4a483096d8a6ea0563095ecc12432d92cd1e22249c384` |
| `xunit2-rerunfailures-16.7.xml` | current | `--reruns 2 reruns` (pytest-rerunfailures 16.7) | `b0624023e45104352ae695b113c960e0ac0adada3477e09687cb1302fe66f5d6` |
| `xunit2-rerunfailures-16.6.xml` | current | `--reruns 2 reruns` (pytest-rerunfailures 16.6) | `72ebf641104dee4c4ead40983b0eadfcda5f28940f5b8e50098c570fb73ea206` |
| `xunit2-outcomes-pytest7.4.4.xml` | legacy | `-o junit_family=xunit2 -o junit_logging=all tests` | `48fd44120dc2345da56101d5b80b1d667572d7333bab616fdde5c8d4ba51c9dc` |

## What the files show

`tests/unit/test_fixture_corpus.py` pins each of these facts.

**Report structure:**
- **Families:** `xunit1` adds `file` and `line` (0-based) to each `<testcase>`; `xunit2` has neither.
- **Root:** pytest 9.1.1 writes `<testsuites name="pytest tests">`; pytest 7.4.4 writes `<testsuites>` with no name.
- **Timestamps:** pytest 9.1.1 writes them with a UTC offset; pytest 7.4.4 writes a naive local time.

**Outcomes:**
- **Errors:** setup errors are written as `<error message="failed on setup with ...">`.
- **Skips and xfails:** skips are `<skipped type="pytest.skip">`, and xfails are `<skipped type="pytest.xfail">`.
- **Xpasses:** a strict xpass is a `<failure>`; a non-strict xpass looks like a pass.
- **One execution, two entries:** a test that fails and then errors in teardown gets two `<testcase>` entries: a
  `<failure>`, then an `<error message="failed on teardown with ...">`.
- **xdist:** entries appear in arrival order, so those two entries can be far apart.

**Names and parameters:**
- **Parameters:** parameter ids stay in `name`.
- **Escaping:** pytest escapes non-ASCII characters in ids (`\u202e` appears as text), but failure messages keep the
  raw characters.
- **pytest-repeat:** it appends `[i-N]`, or `[param-i-N]` for parametrized tests.
- **Collection errors:** a collection error is one `<testcase classname="" name="<module path>">` with
  `<error message="collection failure">`.

**pytest-rerunfailures:**
- **16.6:** writes one `<testcase>` per test with only the final outcome, so failed attempts leave no trace.
- **16.7:** writes one `<testcase>` per attempt, and the failed attempts are empty elements that look like passes.
  Every entry for a test except the last is an attempt that failed, because reruns only follow failures.
- **Counts:** in both versions, `<testsuite tests="5">` counts final outcomes only.
