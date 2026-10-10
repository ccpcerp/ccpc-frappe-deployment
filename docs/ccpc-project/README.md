# CCPC ERPNext project documentation

This directory preserves CCPC-specific ERPNext deployment and DEVELOPMENT engineering records. The checkpoint reflects **observations through 2026-10-10**; it is not authority to change code, restart services, deploy, or modify PRODUCTION.

## Start here

- [P20 conversation handoff](P20-HANDOFF-2026-10-10.md) — current milestone and next safe step (P20A-3).
- [Project context](ccpc-project-context.md) — architecture, boundaries, and known issues.
- [Docker DEVELOPMENT / PRODUCTION architecture](DOCKER-DEV-PROD-ARCHITECTURE.md) — verified separation, volumes, ports, backup dependencies, and safe change boundaries.
- [Roadmap](roadmap.md) — planned DEVELOPMENT reporting and AI review work.
- [Changelog](changelog.md) — milestone history.
- [Operations manual](operations.md) — operational runbooks and safeguards.
- [Deployment framework](framework.md) and [Recovery guide](recovery.md) — retained unchanged from the previous approved snapshots.

GitHub [Issue #22](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22) contains the first verified controlled engineering-report submission. Automated GitHub publishing and AI review remained **disabled** at this checkpoint; the temporary token was revoked and removed.

## Updating these files

Update after significant verified milestones, distinguishing observations from plans. Never commit credentials, production data, private business records, or raw logs.

These Git-tracked files **do not automatically replace** ChatGPT Project Source attachments. Synchronize those separately if needed and verify.
