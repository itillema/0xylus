# 0004. Test identity

- **Status:** Proposed. This ADR will be completed with evidence from the real fixtures in `tests/fixtures/junit/`.
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

Detection and clustering compare the same test across runs, branches, operating systems and report formats. That
needs one canonical identity per test. Three facts constrain it:

- pytest's default JUnit XML family (`xunit2`) has no `file` attribute. Only the legacy `xunit1` family has it.
- Repeat and retry tools change how a test shows up in a report. pytest-repeat appends `[i-N]` to test names.
  Maven Surefire writes retried attempts as nested `flakyFailure`, `flakyError`, `rerunFailure` and `rerunError`
  elements.
- pytest-rerunfailures (versions 16.6 and 16.7 checked on 2026-10-09) doesn't write the failures of retried attempts
  to JUnit XML. pytest's XML writer ignores the plugin's `rerun` outcome. From 16.6.1, earlier attempts appear to come
  out as empty `<testcase>` entries that look like passes.

## Decision (proposed)

**Identity.** A test's identity is `test_id = framework::classname::name[params]`. It never depends on `file`, which
is kept as metadata when present. The storage key `test_key` is the first 16 hexadecimal characters of the SHA-256 of
`test_id`.

**Normalization** before building the identity:

- strip workspace prefixes, such as `/home/runner/work/<repo>/<repo>/`, and use POSIX path separators;
- remove volatile tokens from parameters with configurable patterns, such as memory addresses, temporary paths and
  random ports;
- strip pytest-repeat's `[i-N]` suffix, so that repeats of one test share one identity.

**Attempts.** Retries inside one report are attempts of one test, numbered `attempt_in_run` in document order. For
Surefire, `flakyFailure` and `flakyError` are failed attempts before a pass. `rerunFailure` and `rerunError` are
failed reruns after a first failure.

**pytest-rerunfailures.** A duplicate pytest `<testcase>` without a failure doesn't count as a passing attempt until
real fixtures show exactly what each plugin version writes. Hidden failures must never become apparent passes.

**Counting.** Parsers count `<testcase>` elements and never trust `<testsuite>` totals. Surefire changed what those
totals mean in version 3.5.5. Parsers don't validate against Surefire's XSD either, because real rerun output doesn't
follow that schema's element order.

| Producer | `classname` | `name` |
| --- | --- | --- |
| pytest | Dotted module path, plus the class if any | Function name, with parameters in `[...]` |
| Maven Surefire | Fully qualified class name | Method name or display name |

## Consequences

- The real fixtures, generated with pinned tool versions and listed with their provenance, will confirm or correct
  each rule above before this ADR is accepted.
- Changing the identity rules later needs a new ADR and a migration of stored test keys.

## Alternatives considered

- **Including `file` in the identity:** impossible for pytest's default output, which has no `file` attribute.
- **Treating each duplicate `<testcase>` as its own test:** this would split one test's history across several
  identities.
