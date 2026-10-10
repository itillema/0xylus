# 0002. Technology stack

- **Status:** Proposed
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

0xylus parses untrusted JUnit XML, stores CI history, and runs statistics: bootstrap intervals, hypergeometric and
permutation tests, and hierarchical clustering. It must run offline and deterministically, from a single install,
on Linux, macOS and Windows. The first users are expected to be Python teams on GitHub Actions, and one person
maintains it.

## Decision

We use the stack below. `pyproject.toml` sets `>=` floors at the versions current at kickoff (checked on PyPI on
2026-10-09 and 2026-10-10), and `uv.lock` pins exact versions. Dependabot proposes updates weekly, after a 7-day
cooldown.

| Area | Choice | Version at kickoff |
| --- | --- | --- |
| Language | Python ≥ 3.12; CI on 3.12, 3.13 and 3.14 | 3.12.15, 3.13.16, 3.14.8 |
| Packaging | uv, hatchling, `src/` layout, dependency groups | uv 0.13.0, hatchling 1.32.4 |
| CLI | Typer, with Rich only in the CLI layer | Typer 0.27.3, Rich 15.0.0 |
| Models and configuration | Pydantic v2, pydantic-settings | 2.14.0, 2.15.0 |
| XML | defusedxml (ElementTree API) | 0.7.1 |
| Storage | DuckDB, plus Parquet snapshots (ADR-0003) | 1.5.6 |
| Statistics | NumPy, SciPy | 2.5.3, 1.18.1 |
| GitHub API | httpx and tenacity | 0.28.1, 9.2.1 |
| Reports | Jinja2, with autoescaping for HTML | 3.1.6 |
| Code analysis (v0.3) | tree-sitter, with one grammar wheel per language as an extra | 0.26.0; grammars: Python 0.25.0, Java 0.23.5, JavaScript 0.25.0, TypeScript 0.23.2, Go 0.25.0, C# 0.23.5 |
| Test runners | pytest-randomly, pytest-repeat, pytest-xdist; Maven Surefire, iDFlakies, NonDex | 5.0.0, 0.9.4, 3.8.0 |
| Mutation testing (v0.3) | mutmut or cosmic-ray, chosen in ADR-0008 | 3.8.0, 8.7.0 |
| LLM (v0.4, optional extra) | Anthropic SDK | 1.13.0 |
| Tests | pytest, hypothesis, syrupy, respx, pytest-cov | 9.1.1, 6.168.5, 6.1.1, 0.23.1, 7.1.0 |
| Code quality | ruff; mypy in strict mode, with scipy-stubs and types-defusedxml; pre-commit | 0.17.0; 2.4.0, 1.18.1.1, 0.7.0.20260504; 4.6.2 |
| Supply chain | zizmor, pip-audit, Dependabot, OpenSSF Scorecard; Actions pinned by commit SHA | zizmor 1.30.1, pip-audit 2.10.1 |
| Task runner | just, installed from the `rust-just` wheel | 1.58.0 |

**Python versions.** NumPy 2.5 and SciPy 1.18 require Python 3.12 or newer, so that is the floor. CPython 3.15.0 was
released on 2026-10-09. We add it to CI once DuckDB and tree-sitter publish wheels for it; neither does yet. Local
development is pinned to 3.12 with `.python-version` (ADR-0013).

## Consequences

- **defusedxml** last released 0.7.1 in 2021, and the project looks inactive. It wraps the standard library's
  parsers, so Python changes reach it directly. On Python 3.15, an `iterparse` iterator that opened a file warns if
  it isn't closed, and `close()` only exists from 3.13. Our XML loader therefore always opens files itself. If
  defusedxml breaks, the fallback is lxml with a hardened parser, which would need its own ADR.
- **httpx**'s last stable release is 0.28.1, from December 2024. Since version 1.0, the Anthropic SDK depends on
  httpx2, Pydantic's continuation of httpx, so the `llm` extra installs both, and respx can't mock httpx2. We revisit
  this when building the GitHub client (Phase 1) and the LLM fixer (Phase 4).
- **Typer** vendors Click from 0.26 on. Ctrl-C exits with 130, and running with no arguments exits with 2.
- **rust-just** is a third-party repackaging of just (CC0 license, no PyPI attestations), listed in just's manual.
- **mutmut** needs `fork()`, so on Windows it only runs under WSL. ADR-0008 weighs this.

## Alternatives considered

- **Language:** Go has weaker statistics libraries, and TypeScript has weaker numerics.
- **Packaging:** Poetry and pip-tools are slower than uv and offer no `uvx`-style zero-install runs.
- **CLI:** Click and argparse are less typed and less discoverable.
- **Models:** attrs with cattrs doesn't generate a JSON Schema for the configuration reference.
- **Storage:** SQLite is a row store, and Postgres needs a server.
- **Statistics:** statsmodels is heavier than we need.
- **GitHub API:** PyGithub and githubkit hide too much of the request handling we need to control: redirects, ETags
  and rate limits.
- **Code analysis:** tree-sitter-language-pack downloads native code at runtime, and Semgrep is heavier.
- **Releases and updates:** python-semantic-release, Renovate, Make and nox each overlap a chosen tool, without a
  clear advantage.
