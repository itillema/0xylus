# 0004. Test identity

- **Status:** Proposed. Backed by the real fixtures in `tests/fixtures/junit/` (pytest and Maven Surefire), whose
  observed format is pinned by `tests/unit/test_fixture_corpus.py`.
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

Detection and clustering compare the same test across runs, branches, operating systems and report formats. That
needs one canonical identity per test. Three facts constrain it:

- pytest's default JUnit XML family (`xunit2`) has no `file` attribute. Only the legacy `xunit1` family has it.
- Repeat and retry tools change how a test shows up in a report. pytest-repeat appends `[i-N]` to test names, or
  `[param-i-N]` for parametrized tests. Maven Surefire writes retried attempts as nested `flakyFailure`,
  `flakyError`, `rerunFailure` and `rerunError` elements.
- pytest-rerunfailures doesn't write the failures of retried attempts to JUnit XML, because pytest's XML writer
  ignores the plugin's `rerun` outcome. The real fixtures in `tests/fixtures/junit/pytest/` show:
  - **Version 16.6** writes one `<testcase>` per test, with the final outcome only.
  - **Version 16.7** writes one `<testcase>` per attempt. The failed attempts are empty elements that look exactly
    like passes.
- pytest writes two `<testcase>` entries for one execution when a test fails and then errors in teardown: a
  `<failure>`, then an `<error message="failed on teardown with ...">`. Under pytest-xdist, entries appear in arrival
  order, so the two can be far apart.

## Decision (proposed)

**Identity.** A test's identity is `test_id = framework::classname::name[params]`. It never depends on `file`, which
is kept as metadata when present. The storage key `test_key` is the first 16 hexadecimal characters of the SHA-256 of
`test_id`.

**Normalization** before building the identity:

- strip workspace prefixes, such as `/home/runner/work/<repo>/<repo>/`, and use POSIX path separators;
- remove volatile tokens from parameters with configurable patterns, such as memory addresses, temporary paths and
  random ports;
- strip pytest-repeat's repeat index (`[i-N]` becomes nothing, and `[param-i-N]` becomes `[param]`), so that repeats
  of one test share one identity.

**Attempts.** Retries inside one report are attempts of one test, numbered `attempt_in_run` in document order:
- **Surefire:** `flakyFailure` and `flakyError` are failed attempts before a pass. `rerunFailure` and `rerunError` are
  failed reruns after a first failure.
- **pytest, teardown errors:** an `<error>` whose message starts with `failed on teardown with` belongs to the same
  execution as the test's other entry, wherever it appears in the file. It doesn't start a new attempt.
- **pytest-rerunfailures 16.6.1 and later:** reruns only follow failures, so when a test has several entries, each
  entry but the last is a failed attempt, and the last carries the final outcome. pytest-xdist's `--dist each` also
  produces duplicate entries, and those really passed, so this rule applies only when ingest knows that
  pytest-rerunfailures produced the report. Until then, empty duplicate entries count as neither passes nor failures.
  Phase 1 decides how ingest learns this, for example from the `record` Action's metadata or a setting.
- **pytest-rerunfailures 16.6 and older:** failed attempts can't be recovered from the report.

Hidden failures must never become apparent passes.

**Counting.** Parsers count `<testcase>` elements and never trust `<testsuite>` totals. For the same five tests, the
fixtures show `tests="5"` (Surefire 3.6.0, plus a `flakes` attribute), `tests="2"` (3.5.4 with JUnit 5) and
`tests="11"` (3.5.4 with JUnit 4, which counts every rerun). Parsers don't validate against Surefire's XSD either,
because real reports write `system-out` and `system-err` before the `rerun*` elements, which isn't the schema's
order.

| Producer | `classname` | `name` |
| --- | --- | --- |
| pytest | Dotted module path, plus the class if any | Function name, with parameters in `[...]` |
| Surefire with JUnit Jupiter | Fully qualified class name; a `@Nested` class is `Outer$Nested`, in the outer class's file | Method name, never the display name; parameterized invocations are `method(Type)[index]` |
| Surefire with JUnit 4 | Fully qualified class name | Method name; the Parameterized runner's pattern, such as `rejectsTwo[1: value 2]` |

## Consequences

- The real fixtures were generated with pinned tool versions and are listed with their provenance. They back each
  rule above, and the corpus tests fail if a regenerated fixture contradicts one.
- Under Surefire with JUnit Jupiter, a parameterized invocation is identified by its position, `[index]`.
  Reordering the arguments changes which identity each invocation gets, so its history shifts.
- Changing the identity rules later needs a new ADR and a migration of stored test keys.

## Alternatives considered

- **Including `file` in the identity:** impossible for pytest's default output, which has no `file` attribute.
- **Treating each duplicate `<testcase>` as its own test:** this would split one test's history across several
  identities.
