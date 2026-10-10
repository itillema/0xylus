# 0013. Phase 0 adjustments

- **Status:** Proposed
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

The kickoff checks for the foundation phase turned up facts that changed how the work is done: the package name,
tool releases from the week of kickoff, and Windows defaults. This ADR records the resulting adjustments.

## Decision

1. **First push.** The repository's first push happens after the fixture corpus and the test-suite generator are
   done, so the initial history can be reviewed as a whole. CI on all three operating systems runs after that push.
   Before it, the checks run locally on Windows and in Linux containers with Python 3.12 and 3.14.
2. **LICENSE and README with the scaffold.** Both arrive together with the package scaffold, because the package
   metadata refers to them.
3. **A `main()` wrapper.** Both commands point at `zeroxylus.cli:main`, a wrapper around the Typer app. With the app as
   the entry point, an unexpected exception would exit with 1, which means "policy failure" here; the wrapper makes
   it exit with 3, "internal error".
4. **The XML loader comes with the fixtures.** A size-capped, defusedxml-only XML loader with typed errors arrives
   with the fixture corpus, because hostile samples must already be rejected with typed errors. The full streaming
   JUnit parser builds on it later.
5. **ADR-0004 waits for the fixtures.** ADR-0004 (test identity) is proposed with the other first ADRs, and completed
   once the real fixtures exist.
6. **pip-audit.** A pip-audit workflow audits every locked dependency weekly and whenever dependencies change.
   pip-audit lives in its own `audit` dependency group. We don't use `uv audit`, which is still a preview feature.
7. **A self-contained DCO check.** The DCO check is a short workflow that skips bot authors, with no third-party app
   or action (ADR-0010).
8. **`.gitattributes`.** Git for Windows defaults to `core.autocrlf=true`. A `.gitattributes` file keeps LF line
   endings everywhere and keeps fixture files byte-exact.
9. **`.python-version`.** Local development is pinned to Python 3.12. Since 0.13, uv downloads Python 3.15 when no
   suitable interpreter is installed, and DuckDB has no 3.15 wheels yet.
10. **Ruff skips Markdown.** Ruff's file list excludes Markdown. Ruff 0.17 formats code blocks in `.md` files, and
    we don't want the formatter rewriting documentation.

## Consequences

- macOS and Windows on Python 3.13 and 3.14 are first tested in CI after the first push, so any failures specific to
  those platforms surface then.
- The exit codes are 0, 1, 2, 3 and 4, plus 130 for Ctrl-C.

## Alternatives considered

- **Pushing earlier, after the CI workflows exist:** faster feedback on macOS, but the initial history would be
  published before the foundation was reviewed as a whole.
- **Writing the full parser first:** that work belongs to the next phase. The small loader is the part it builds on.
