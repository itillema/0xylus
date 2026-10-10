# The flaky zoo

The zoo generates small pytest suites with planted, controlled flakiness. Detection, clustering and later cause
analysis are measured against this ground truth.

Each configuration, Z1 to Z7, plants one root cause. Its member tests form one planted cluster. Twelve control tests
complete the suite.

| Key | Cause | Members | Planted failure | Passive signal | Matching stressor (Phase 3) |
| --- | --- | --- | --- | --- | --- |
| Z1 | Test order and shared state | 3 victims, plus a polluter that always passes | `AssertionError: module cache polluted by an earlier test: ...` | The polluter runs first in runs where the victims fail, and last otherwise | `order` |
| Z2 | Async waits and timeouts | 3 | `TimeoutError: event not set within 0.15s` | Failing runs wait out the timeout, so durations sit near it; the members share a slow module fixture | `cpu` |
| Z3 | Resource contention | 2 | `OSError: [Errno 98] Address already in use: ('127.0.0.1', 47001)` | Failing runs are mostly on small runners with 4 workers (`runner`, `workers` in the manifest) | `parallel` |
| Z4 | Time and clock | 2 | `AssertionError: date changed between calls: <day> != <day before>` | Failing runs start 0.5–2 s before midnight UTC (`started_at` in the manifest) | `time` |
| Z5 | Network and external dependencies | 4 | `ConnectionResetError` or `TimeoutError` naming `stub.zoo.invalid:8080` | The external host appears in the messages | `network` |
| Z6 | Unordered collections | 2 | `assert ['beta', 'alpha', 'gamma'] == ['alpha', 'beta', 'gamma']` | Same elements, different order | `hashseed` |
| Z7 | Unseeded randomness | 1 | `ZeroDivisionError: division by zero` | None (found by static scanning later) | none |
| Controls | — | 10 always pass, 2 always fail | `AssertionError: control test that always fails` | — | — |

## Knobs

Each configuration has three knobs:
- **`rate`** is the per-run failure probability. The default is 0.20: at 30 runs, that gives a 99.9% chance of at
  least one failure, and a 96% chance of the 3 shared failures clustering needs.
- **`shared_fault`** is on by default. One draw per run decides whether the shared resource fails, and then every
  member fails in that run. Off, each member fails independently at `rate`, which makes a null control for
  clustering.
- **`size`** is the number of member tests.

## Determinism

Seeded mode is the only mode in Phase 0. A real mode, which runs the actual mechanisms, comes in Phase 3.

**The guarantees:**
- The same seed and run count always produce a byte-identical `manifest.json`, so the same seed gives the same
  outcomes.
- Every draw comes from its own random stream, keyed by the seed, the run index, the configuration and the purpose.
  So changing one configuration, or the number of runs, never changes another configuration's draws or earlier
  runs.

**How the code keeps them:**
- It only calls `random.Random.random()`. For an integer seed, CPython guarantees that sequence across versions.
- Shuffles use our own Fisher–Yates loop.
- No global random state or clock is involved.

## The manifest

`manifest.json` is the ground truth, written next to the generated suite. Its top-level keys:

| Key | Contents |
| --- | --- |
| `schema_version`, `generator`, `mode`, `seed`, `runs` | Identification |
| `configs` | Each configuration's knobs, module, member node ids and extra tests (Z1's polluter) |
| `controls` | The always-pass and always-fail node ids |
| `tests` | Every test's pytest node id, plus the JUnit XML `classname` and `name` pytest writes for it |
| `plan` | One entry per run, described below |

Each run entry contains:
- `faults` for each configuration;
- the sorted `failing` node ids;
- the test `order`;
- the synthetic run metadata: `started_at`, `runner` and `workers`.

pytest writes the real wall-clock time and hostname into each report, so the planted time and runner signals live in
the manifest. The benchmark harness supplies them as run metadata when it ingests the reports.

## Running it

From the repository root:

```bash
uv run python -m benchmarks.zoo --seed 1 --runs 30
```

This writes the suite to `benchmarks/zoo/out/seed-1/suite/` and one report per run to
`benchmarks/zoo/out/seed-1/junit/run-0000.xml` and onward. The `out/` directory is ignored by git, ruff and mypy.
Thirty runs take about 17 seconds on a laptop.

| Option | Effect |
| --- | --- |
| `--seed N` | Suite seed (default 1) |
| `--runs N` | Number of runs (default 30) |
| `--out DIR` | Output directory (default `benchmarks/zoo/out/seed-<seed>`) |
| `--rate R` | Failure rate for every configuration (default 0.20) |
| `--set KEY.FIELD=VALUE` | Override one configuration, for example `Z3.rate=0.3`, `Z3.size=4` or `Z5.shared_fault=false`; repeatable |
| `--no-run` | Only generate the suite |

Each run is a fresh pytest process with:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, so installed plugins can't change the runs;
- `PYTHONHASHSEED=0`;
- `PYTEST_ADDOPTS` and `PYTEST_PLUGINS` removed from the environment.

pytest exits with 1 because the controls fail. Any other exit code except 0 stops the run with an error.

## The generated suite

The generated files are:
- `pytest.ini`;
- a `conftest.py` that reads the manifest, applies the run's order, and gives each test a `planned_failure` fixture;
- one module per configuration, plus `test_controls.py`;
- `manifest.json`.

The `ZOO_RUN` environment variable selects the run. In code, `benchmarks.zoo.plan.build_plan` makes a plan,
`benchmarks.zoo.render.write_suite` writes its suite, and `benchmarks.zoo.run.run_suite` runs it.
