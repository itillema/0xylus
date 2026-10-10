# 0001. Name and GitHub owner

- **Status:** Proposed
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

The project's name is **0xylus**. Kickoff checks on 2026-10-09 found that the name can't be used everywhere:

- **PyPI rejects it.** Before registering a new project, PyPI normalizes the name: it lowercases it, removes `.`, `-`
  and `_`, and maps `o` to `0` and `l` and `i` to `1`. It rejects the name as "too similar" if an existing project
  normalizes to the same string. `oxylus` is registered (with no releases yet), and both names normalize to
  `0xy1us`. Sources: the `ultranormalize_name` function and `ProjectService.check_project_name` in
  [pypi/warehouse](https://github.com/pypi/warehouse), and PyPI's help page
  ["Why isn't my desired project name available?"](https://pypi.org/help/#project-name).
- **It isn't a Python identifier.** Identifiers can't start with a digit, so `import 0xylus` is a syntax error. The
  [entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/) requires every
  part of an object reference such as `0xylus.cli:app` to be an identifier, and mypy refuses to check a package
  directory named `0xylus`.
- **It can't start an environment variable name.** POSIX shell names and GitHub Actions configuration variable names
  can't start with a digit, so a `0XYLUS_` prefix wouldn't work.
- **Some uses are fine.** A command name, a file name (`0xylus.toml`), a TOML table (`[tool.0xylus]`), labels and
  artifact names can all start with a digit.
- **The alternative package name is free.** No project on PyPI normalizes to the same string as `zeroxylus` (a scan
  of all of PyPI's roughly 909,000 project names). No GitHub user or organization uses it.
- **GitHub.** An organization named `0xylus` already exists (created in 2021, with no public repositories). The
  project doesn't use it.
- **Other uses of the name.** A quick web search found other uses of "Oxylus": a C++ game engine, a Django and Vue
  framework (probably the holder of the PyPI name), a wildlife technology company, and a figure in Greek mythology.
  The only USPTO record found is a design-only mark, with no words, held by Oxylus Energy P.B.C. for energy goods and
  services (serial 99315398). This was not a legal trademark clearance.

## Decision

- The brand, the repository and the command are **`0xylus`**. So are the configuration file (`0xylus.toml`), the
  `pyproject.toml` table (`[tool.0xylus]`), labels (`0xylus:*`) and artifact names (`0xylus-*`).
- The PyPI distribution and the import package are **`zeroxylus`**. The package installs two commands, `0xylus` and
  `zeroxylus`, both pointing at `zeroxylus.cli:main`, so `uvx zeroxylus` works.
- Environment variables use the prefix **`ZEROXYLUS_`**.
- The repository is **`itillema/0xylus`**, under the maintainer's personal GitHub account. The Actions are referenced
  as `itillema/0xylus/action/<name>@<sha>`.

## Consequences

- Install instructions always use `zeroxylus` (`pip install zeroxylus`, `uvx zeroxylus`). `pip install oxylus`
  installs an unrelated project, and nobody can register `0xylus` while `oxylus` exists.
- Users meet two names. The README and the development guide explain why.
- If `oxylus` ever disappears from PyPI, someone else could register `0xylus`. The docs never tell users to install
  `0xylus`, so that wouldn't mislead them.

## Alternatives considered

- **Rename everything to a name that works everywhere**, such as "flakeroot", which is free on PyPI and GitHub.
  Rejected to keep the 0xylus brand.
- **Ask PyPI for the `oxylus` name under [PEP 541](https://peps.python.org/pep-0541/).** Slow and uncertain, because
  its likely owner is active, and the import package would still need another name.
- **Use `0xylus-cli` as the distribution.** `uvx 0xylus-cli` is clumsier, and it still differs from the import name.
