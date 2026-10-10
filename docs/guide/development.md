# Development

## Setup

Install [uv](https://docs.astral.sh/uv/), then run this from the repository root:

```bash
uv sync --all-extras
```

This creates `.venv` with the package installed in editable mode, every optional extra, and the `dev` dependency
group. `.python-version` pins local development to Python 3.12, the oldest supported version; CI also tests 3.13 and
3.14. If 3.12 isn't installed, run `uv python install 3.12`.

To run the checks on every commit, install the pre-commit hooks once:

```bash
uv run pre-commit install
```

The hooks are local and run the tools pinned in `uv.lock`.

## Commands

Run tasks through `uv run` so that the project's tools are on `PATH`:

| Command | What it does |
| --- | --- |
| `uv run just check` | Lint (ruff), check formatting, type-check (mypy, strict) and run the unit tests |
| `uv run just integration` | Integration tests, which run the installed commands and other subprocesses |
| `uv run just fmt` | Format the code and apply safe lint fixes |
| `uv run just` | List all recipes |
| `uv run 0xylus --version` | Print the version; `--help` lists the options |

pytest collects only `tests/`. `uv run just test` is the same as `uv run pytest -q -m "not integration"`.

## Rules the linter enforces

Library code under `src/` must not:

- read the system clock or use the global random number generator (inject a clock or a seeded generator instead);
- parse XML with anything but `defusedxml`;
- start subprocesses or open network connections, except in the modules built for that.

Tests and benchmarks are exempt.

## Names

The command is `0xylus`. The PyPI distribution and the import package are both `zeroxylus`, for two reasons:
`0xylus` is not a valid Python identifier, and PyPI rejects it as too similar to an existing project. The `zeroxylus`
command is an alias for `0xylus`, so `uvx zeroxylus` works.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success, including a validation PASS |
| 1 | Policy failure: a validation FAIL or a guard BLOCK |
| 2 | Usage or configuration error |
| 3 | Internal error (a bug) |
| 4 | Inconclusive: validation couldn't decide |
| 130 | Interrupted with Ctrl-C |
