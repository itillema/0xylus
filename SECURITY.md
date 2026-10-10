# Security policy

## Supported versions

0xylus is pre-alpha and has no releases yet, so security fixes go to the `main` branch. Once releases begin, only the
latest release will receive fixes.

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub:
[report a vulnerability](https://github.com/itillema/0xylus/security/advisories/new). If you can't use GitHub, email
isaactillema@isaactillema.com. Please don't open a public issue.

Include what you found, how to reproduce it, and the impact you expect. You'll get an acknowledgement within 7 days.
0xylus has one maintainer, so a fix can take longer; the disclosure date is agreed with you, normally within 90 days of
the report.

## Scope

0xylus reads data that attackers can control: JUnit XML, CI logs and artifacts, including those from pull requests
from forks. These reports are especially welcome:

- **Parsing:** XML external entities, entity expansion, or unbounded memory or time on crafted input.
- **Injection through reports:** unescaped test names or messages in HTML, Markdown, pull request comments or workflow
  annotations, including unwanted @mentions.
- **This repository's GitHub Actions:** token misuse, script injection, or running untrusted pull request code.
- **Unrequested actions:** anything that lets input data trigger network access, subprocesses or writes that the user
  didn't ask for.

Please report vulnerabilities in dependencies to their maintainers, unless the way 0xylus uses a dependency makes the
problem worse.
