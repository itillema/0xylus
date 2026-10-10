# 0xylus

[![CI](https://github.com/itillema/0xylus/actions/workflows/ci.yml/badge.svg)](https://github.com/itillema/0xylus/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/itillema/0xylus/badge)](https://scorecard.dev/viewer/?uri=github.com/itillema/0xylus)

0xylus finds flaky tests in CI history, groups tests that fail together, ranks likely root causes, and checks with
statistics whether a fix worked.

> **Status: pre-alpha.** Nothing is usable yet. The first release (v0.1) will read CI history and report clusters of
> flaky tests.

## Why

- A flaky test passes and fails on the same code. Retries turn red builds green and hide the cost, and quarantine
  hides the test. Neither finds the cause.
- Flakiness clusters. In a study of 24 Java projects, 75% of 810 flaky tests belonged to groups of tests that fail
  together ([Parry et al., 2025](https://arxiv.org/abs/2504.16777)). One fix can clear a whole group, yet most tools
  rank tests one at a time.
- 0xylus reports evidence, not verdicts. Every claim links to the runs, counts or diffs behind it, with intervals where
  they apply.

## Roadmap

| Version | Goal |
| --- | --- |
| v0.1 | Read JUnit XML from GitHub Actions history or local reruns, find flaky tests, cluster the tests that fail together, and rank clusters by the CI time they cost |
| v0.2 | Suggest likely causes (test order, timing, network, shared state and more), each with the evidence behind it |
| v0.3 | Reproduce a cluster under stress and check whether a fix holds up, with guards against fixes that only silence tests |
| v0.4 | Optionally draft a fix with an LLM that gets no tools, then validate it the same way |

## Names

The command is `0xylus`. The Python package is published and imported as `zeroxylus`, so once it's released you'll be
able to run it with `uvx zeroxylus`.

## Contributing

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). To set up a development environment with
[uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras
uv run just check
```

The [development guide](docs/guide/development.md) has the details.

## Security

Please report vulnerabilities privately; see [SECURITY.md](SECURITY.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
