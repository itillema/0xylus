# 0010. License and DCO

- **Status:** Proposed
- **Date:** 2026-10-10
- **Deciders:** Isaac Tillema (@itillema)

## Context

0xylus is open source and welcomes outside contributors. It needs a license that companies can adopt and that
includes a patent grant. It also needs a lightweight way to confirm that contributors have the right to submit their
changes.

## Decision

- **License.** The project is licensed under the **Apache License 2.0**. `LICENSE` is the unmodified text from
  apache.org.
- **Contributions.** Contributions are made under the same license.
- **Sign-off.** Contributors certify the [Developer Certificate of Origin](https://developercertificate.org/) instead
  of signing a CLA. Every commit carries a `Signed-off-by:` line that matches its author, added with `git commit -s`.
  The maintainer signs off their own commits too.
- **DCO check.** A self-contained workflow (`.github/workflows/dco.yml`) checks every non-merge commit in each pull
  request:
  - It skips bot accounts, such as Dependabot and release automation, which can't sign off.
  - It runs only on pull requests, so direct pushes aren't checked.
  - Once branch protection is set up on `main`, the check is required.
- **Third-party material.** Third-party files, such as test fixtures copied from other projects, keep their own
  licenses, which are recorded next to them. Algorithms that are reimplemented from research tools are credited to
  their authors.

## Consequences

- Each contributor must sign off every commit. A missed sign-off is fixed with `git rebase --signoff <base>`.
- No contributor agreement has to be collected or stored.

## Alternatives considered

- **A contributor license agreement:** more paperwork, and it deters casual contributors.
- **The DCO GitHub App:** it skips bots automatically, but it's a third-party app with access to the repository. A
  short workflow that can be audited does the same job.
- **MIT:** permissive like Apache 2.0, but without an explicit patent grant.
