# Security Policy

## Supported Versions

Security fixes are prioritized for:

- the current `main` branch
- the currently deployed production release
- the latest supported CCPC ERP release

Older releases may require upgrading before a security fix can be applied.

## Reporting a Vulnerability

Do not report suspected security vulnerabilities in a public issue.

Use GitHub's private vulnerability reporting or Security Advisory functionality when it is available for this repository.

If private vulnerability reporting is not available, contact the repository owner privately before publishing vulnerability details.

A useful report should include:

- the affected component
- the affected version or commit
- the security impact
- steps required to reproduce the problem
- any known workaround
- any suggested remediation

Do not include real production credentials, passwords, API keys, access tokens, private keys, database credentials, recovery codes, or other secrets in reports.

## Sensitive Operational Information

Treat the following as sensitive:

- production `.env` contents
- database credentials and backups
- administrator credentials
- API keys and access tokens
- SSH private keys
- GitHub credentials and recovery codes
- internal infrastructure details that could enable unauthorized access

Secrets must not be committed to Git.

If a secret is accidentally committed, removing it from the latest file is not sufficient. Treat the credential as compromised, rotate or revoke it, and determine whether repository history must be remediated.

## Production Safety

Security-related changes that affect production should follow the normal CCPC ERP deployment process.

Before deployment:

1. Review the proposed change.
2. Validate the repository state.
3. Confirm the target release or image.
4. Confirm that a usable backup exists.
5. Confirm the rollback path.
6. Validate required database migrations.
7. Perform appropriate staging verification when practical.

Destructive or production-impacting actions require explicit approval.

## Disclosure

Avoid public disclosure of unresolved vulnerabilities until an appropriate fix or mitigation is available.
