# 0003. Storage and stores

- **Status:** Proposed
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

Analysis needs months of CI history, but GitHub doesn't keep it that long. Artifacts and logs are kept for 90 days by
default, and public repositories can set 1–90 days. The `record` Action uploads its results with 7-day retention. The
data must be analyzable on a laptop, with no server: up to a million result rows in under a minute. It must also
persist between CI runs, ideally without write permissions.

## Decision

**Database.** We use embedded DuckDB. Numbered SQL migrations and a `schema_version` table version the schema.

| Version | Tables |
| --- | --- |
| v0.1 | `runs`, `tests`, `results`, `signatures`, `analyses`, `flaky_tests`, `clusters` and `cluster_members` |
| v0.2 | `hypotheses` |
| v0.3 | `experiments`, `trials` and `verdicts` |

Every derived row points to the analysis that produced it.

**Snapshots.** Snapshots export each table to Parquet. `results/` is partitioned by `date=YYYY-MM-DD`, and the other
tables are single files. `export parquet` and `import parquet` move history between stores.

**Stores.** History can live in four kinds of store:

| Store | How | When |
| --- | --- | --- |
| `local` | A DuckDB file | Development and laptops |
| `artifact` (default) | Each `collect` run downloads the previous snapshot artifact, appends to it, compacts it and uploads a new one | A quick start with no write permissions. History lasts only while `collect` keeps running |
| `branch:<name>` | Parquet committed to an orphan data branch | Long history: durable and versioned. Needs `contents: write`, in the collect workflow only |
| `s3://`, `gs://`, `az://` | Parquet through DuckDB's extensions | Teams that already have buckets |

**Keeping history alive.** `collect` runs daily, more often than the 7-day `record` retention. It uses a
`concurrency:` group, so two runs never write the same store at once. `report` warns when the newest ingested run is
more than 7 days old, because older `record` artifacts may already be gone.

## Consequences

- With the `artifact` store, history is lost if `collect` stops for longer than the artifact retention. The docs
  recommend the branch store for long history.
- GitHub disables scheduled workflows in public repositories after 60 days without repository activity. The docs
  explain how quiet repositories can re-enable `collect`.
- DuckDB doesn't publish wheels for Python 3.15 yet, so 3.15 stays out of CI until it does (ADR-0002).

## Alternatives considered

- **SQLite:** a row store, so it's slower for column-heavy analytics.
- **Postgres:** needs a server, which conflicts with self-hosted runs from a single install.
- **Parquet files without a database:** we would have to reimplement the queries and migrations ourselves.
