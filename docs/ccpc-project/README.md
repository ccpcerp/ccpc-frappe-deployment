# CCPC ERPNext project documentation

This directory preserves CCPC-specific ERPNext deployment and DEVELOPMENT engineering records. **The current workflow decision was updated 2026-10-12; older P20 automation plans below are historical, not the current priority.** This documentation is not authority to change code, restart services, deploy, or modify PRODUCTION.

## Start here

- **[GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) — permanent development rules.** Start every new thread here; keep PRODUCTION separate.
- **[CURRENT-HANDOFF-3.md](CURRENT-HANDOFF-3.md) — ACTIVE compact rolling GitHub checkpoint (2026-10-30).** Read after the workflow for exact current app/DEV/backup state, encrypted CircleCI restore design, owner approval limits and next priorities.
- [CURRENT-HANDOFF-2.md](CURRENT-HANDOFF-2.md) — preserved previous checkpoint, now historical. It became oversized; do not keep appending milestone logs there.
- [CURRENT-HANDOFF.md](CURRENT-HANDOFF.md) — historical comprehensive handoff (~1.3 MB), **preserved as archive/reference**, not the active file to append to. Consult only for historical details.
- [Build #34 12/12 acceptance evidence](CURRENT-HANDOFF-CI34-ACCEPTANCE-2026-10-29.md) — tested Finance→Withdrawal→paired *draft* SI/PI source, no production acceptance.
- [P20 conversation handoff](P20-HANDOFF-2026-10-10.md) — historical continuity log; newer GitHub-first section supersedes its P20A next-step proposals.
- [Project context](ccpc-project-context.md) — architecture, boundaries, and known issues.
- [Docker DEVELOPMENT / PRODUCTION architecture](DOCKER-DEV-PROD-ARCHITECTURE.md) — verified separation, volumes, ports, backup dependencies, and safe change boundaries.
- [Roadmap](roadmap.md) — historical plans and current priority overrides; cancelled Codex automation is not active.
- [Changelog](changelog.md) — milestone history.
- [Operations manual](operations.md) — operational runbooks and safeguards.
- [Deployment framework](framework.md) and [Recovery guide](recovery.md) — retained unchanged from the previous approved snapshots.

GitHub [Issue #22](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22) contains the first verified controlled engineering-report submission. Automated GitHub publishing and AI review remained **disabled** at this checkpoint; the temporary token was revoked and removed.

## Updating these files

Update after significant verified milestones, distinguishing observations from plans. Never commit credentials, production data, private business records, or raw logs.

These Git-tracked files **do not automatically replace** ChatGPT Project Source attachments. Synchronize those separately if needed and verify.
