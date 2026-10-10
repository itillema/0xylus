# Architecture decision records

Significant decisions are recorded here as short architecture decision records (ADRs), using
[the template](template.md).

## Process

- Copy the template to `NNNN-short-title.md`. Numbers 0001–0012 are reserved for decisions planned from the start;
  other decisions take the next free number from 0013 on.
- A new ADR starts as **Proposed**. The maintainer marks it **Accepted** or **Rejected**.
- To change an accepted decision, write a new ADR and mark the old one **Superseded by NNNN**. Changes to test
  identity also need a data migration.

## Index

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-name-and-github-owner.md) | Name and GitHub owner | Proposed |
| [0002](0002-stack.md) | Technology stack | Proposed |
| [0003](0003-storage-and-stores.md) | Storage and stores | Proposed |
| [0004](0004-test-identity.md) | Test identity | Proposed |
| 0005 | Clustering method and defaults | Planned |
| 0006 | Validation statistics | Planned |
| 0007 | First validation runner | Planned |
| 0008 | Mutation testing tool | Planned |
| 0009 | LLM provider abstraction and data policy | Planned |
| [0010](0010-license-and-dco.md) | License and DCO | Proposed |
| 0011 | pytest plugin injection for rerun mode | Planned |
| 0012 | Distribution of the GitHub Actions | Planned |
| [0013](0013-phase-0-adjustments.md) | Phase 0 adjustments | Proposed |
