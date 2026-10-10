# Contributing to 0xylus

Thanks for your interest. 0xylus is pre-alpha and has one maintainer, so small, focused pull requests are the easiest
to review. For anything larger, please open an issue first so we can agree on the approach.

## Ways to help

These contributions are small, self-contained and driven by fixtures, so they make good first contributions:

- **A JUnit XML dialect** beyond pytest and Maven Surefire, such as Gradle, Jest, Vitest, Playwright, Go or .NET. It
  needs a real report as a fixture, with its provenance, plus the adapter.
- **A stack-trace parser** for another language.
- **A failure-signature normalizer**, for example for a new kind of volatile token in messages.
- Later: cause detectors and test-runner adapters.

Bug reports with a minimal reproduction are just as valuable.

## Development setup

You need [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
uv sync --all-extras          # create .venv with every extra and the dev tools
uv run pre-commit install     # optional: run the checks on every commit
uv run just check             # lint, format check, type check and unit tests
uv run just integration       # integration tests
```

The [development guide](docs/guide/development.md) lists every command.

## Pull requests

- Keep each pull request to one change, and make sure `uv run just check` passes.
- Every behavior change comes with tests. Algorithms get property-based tests for their invariants, and report formats
  get snapshot tests, including hostile test names.
- Update the docs: a guide page, or an architecture decision record in `docs/adr/` for a significant decision.
- Write commit messages and the pull request title as [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `build:`, `refactor:` or `chore:`, with `!` for a breaking change.

## Sign your commits (DCO)

Every commit must be signed off under the [Developer Certificate of Origin](https://developercertificate.org/). The
sign-off certifies that you wrote the change or otherwise have the right to submit it under the project's license.
Add it with:

```bash
git commit -s
```

This appends a line such as `Signed-off-by: Your Name <you@example.com>`, which must match the commit's author. To sign
off commits you've already made, run `git rebase --signoff <base>`. A check on every pull request verifies the
sign-offs.

## Rules the code follows

These rules keep 0xylus safe to run on untrusted CI data, and keep its results reproducible:

- **Input is hostile.** JUnit XML, logs and artifacts are parsed only with `defusedxml`, with size limits, and are
  never passed to `eval` or a shell.
- **Output is escaped.** Test names, paths and messages are escaped for every report format: HTML, Markdown and
  workflow annotations.
- **The core is deterministic and offline.** Library code doesn't read the clock or use a global random number
  generator, and only a few modules may use the network or start processes. The linter enforces this.
- **No write actions by default.** Nothing comments, pushes or merges unless the user turns it on.
- **Statistics are not loosened to make a test pass.** If a threshold or rule looks wrong, open an issue and explain
  why.
- **Each test has one identity:** its framework, class name, name and parameters. Changing the identity rules needs an
  architecture decision record.

## Test fixtures

- Fixtures are real tool output. Each fixture directory has a README that records, for every file, the source URL or
  the command that generated it, the tool version or commit, the license and the retrieval date.
- Hand-written samples, such as malformed or hostile XML, are allowed only when they are labeled synthetic.
- Don't commit large files. Generate them inside the test that needs them.
- Fixtures are byte-exact, so don't reformat them or change their line endings.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By taking part, you agree to uphold it.

## Security

Please don't report vulnerabilities in public issues; see [SECURITY.md](SECURITY.md).

## License

Contributions are licensed under the project's license, the [Apache License 2.0](LICENSE).
