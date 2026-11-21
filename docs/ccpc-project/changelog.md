# CCPC ERP Change Log

*Last updated: 2026-10-12*

This document records significant completed changes to the CCPC ERP
Deployment Framework, custom application, and operational environment.

Current verified state belongs in `ccpc-project-context.md`. Planned
work belongs in `roadmap.md`.

## 2026-10-12 — GitHub-first custom-app workflow adopted (documentation only)

- Owner decided GitHub should be the authoritative source of committed/pushed CCPC custom application code, with DEVELOPMENT pulling reviewed commits for testing and any DEV fixes returned to GitHub. PRODUCTION execution requires separate approval.
- Verified default app branch `version-16` at `cfcc193` lacks the billing implementation; real pushed feature branch is `feature/intercompany-material-billing` at `7ac238e`. Preliminary static review found potential concurrent approval / invoice duplication risk in pushed code; not reproduced.
- Operator reported eight uncommitted application/test/patch files in the DEV app working tree, plus untracked `AGENTS.md`; **not yet verified staged, committed or pushed**. First transition must preserve/review these changes safely.
- Created [workflow and handoff runbook](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) on draft docs PR #24. This is documentation, **not** a code change to the running servers. Windows VS Code clone retained; no cleanup required.
- Automatic reporting and paid API setup are not part of the new priority; GitHub code inspection through connected ChatGPT is available.

## 2026-10-10 — P19G controlled GitHub publishing completed; P20A begun

- Built and offline-tested a dedicated, restricted CCPC report publisher with
  report file policy, bounded GitHub HTTPS client, exclusive lock, persistent
  SQLite delivery ledger, reconciliation/duplicate protection, root-controlled
  report approval, and exact report SHA-256 checks.
- Completed manual live test: published one previously approved DEVELOPMENT
  synthetic report to private deployment GitHub Issue #22, subsequently
  independently confirmed comment
  [6094678841](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22#issuecomment-6094678841)
  by `ccpcerp` and read-only SQLite `confirmed` state.
- Revoked temporary fine-grained token via GitHub UI and removed local
  `/etc/ccpc-reporter/github-token`; removed the consumed approval record and
  synthetic outbox report; all cleanup checks passed. The GitHub comment and
  ledger audit record were preserved.
- Verified general publisher code `LIVE_PUBLISHING_ENABLED = False` and known
  publisher units inactive. No automatic service, timer, PR merge, or AI review
  was enabled.
- P20A-1: Installed root-owned metadata-only `automatic_report_policy.py`
  with strict enum schema and fixed Markdown renderer; no publisher integration
  or activation.
- P20A-2: **15/15** offline tests passed for strict JSON schema,
  duplicate/missing/extra fields, invalid content, UTC timestamps, and
  compatibility with existing GitHub report format. No live GitHub requests or
  report-file writes occurred during the tests.
- Remaining P20 work: structured Codex completion handoff, safe immutable
  metadata/task identifier, controlled automatic delivery, GitHub AI reviewer
  draft PR #23 review, API secret/cost authorization, explicit final activation.
- Confirmed that P20 metadata-only reports are self-reported triage categories,
  **not** proof of successful code or integration tests.

## 2026-09-15 --- ERPNext Equipment Asset Integration Phase 2 (PR #4)

-   Implemented Phase 2 Equipment Asset Integration in the custom
    `ccpcerp` application while preserving Equipment as the permanent
    functional/plant identity and ERPNext Asset as the physical/accounting
    asset occupying that position.
-   Added the `Equipment Asset Assignment` DocType with historical
    assignment intervals, same-company and submitted-Asset eligibility,
    Active-Equipment requirement for new assignments, overlap protection,
    immutable identity/install fields, one-way closure, and protected
    deletion behavior.
-   Added read-only Asset provenance snapshots to Work Request and Job
    Order. Linked Job Orders inherit the source Work Request snapshot
    exactly; standalone Equipment Job Orders snapshot the current assignment
    when one exists. Existing Work Requests and Job Orders are not backfilled.
-   Preserved the existing Equipment Accounting Dimension as the maintenance
    cost identity; Phase 2 adds no custom Asset GL/accounting logic.
-   Added concurrency protection using deterministic Equipment-to-Asset row
    locking plus locking overlap reads for new assignments. MariaDB
    `ER_CHECKREAD` / errno `1020` from that locking read is converted to a
    clear retry ValidationError without an in-transaction retry or re-query.
-   DEVELOPMENT validation completed successfully, including 108 Python
    tests with 0 failures, Work Request/Job Order/equipment-costing JavaScript
    regressions, compile/JSON/diff checks, and real two-process concurrency
    validation.
-   Feature commit: `0971a00` ---
    `feat: add equipment asset assignment integration`.
-   Merged PR #4 into `version-16` with merge commit `464d28e`.
-   Verified local `version-16` and `origin/version-16` synchronized at
    `464d28e`, then deleted the merged feature branch locally and remotely.
-   Production was not deployed or migrated as part of this merge. Production
    release remains a separate explicitly approved operation.

## 2026-09-02 --- Backup and recovery hardening

### Backup storage

-   Repaired the Synology NAS backup mount after the network migration.
-   Updated the expected backup source to
    `//192.168.50.132/erpnext_backups`.
-   Verified `/mnt/erpnext_backups` as a read/write CIFS mount from the
    expected source.
-   Preserved the existing credential-file mechanism without documenting
    credential contents.

### Historical backup recovery

-   Preserved the accidental local fallback backup set at
    `/home/gani/erpnext-backup-recovery-2026-09-02`.
-   Verified the preserved recovery copy matched the original local set
    by file count and total bytes before continuing.
-   Recovered 29 timestamped backup directories containing 116 files to
    the NAS without overwriting existing NAS backups.
-   Verified the recovered NAS content against the recovery copy with a
    checksum dry-run.
-   Recorded `2026-08-04` as a known historical backup gap.

### Backup script hardening

-   Hardened `/usr/local/bin/erpnext_backup.sh`.
-   Required all four Frappe backup artifacts: database, site
    configuration, public files, and private files.
-   Added explicit mountpoint, CIFS filesystem, exact NAS source, and
    writability validation.
-   Added `.partial-*` staging followed by final rename only after
    successful copy verification.
-   Removed behavior that could hide public/private file copy failures.
-   Restricted NAS retention cleanup to timestamp-formatted backup
    directories.
-   Set current retention to 7 days for local Frappe backups and 30 days
    for NAS timestamped backup directories.

### Backup validation and scheduling

-   Completed a controlled manual end-to-end backup test successfully.
-   Verified backup `/mnt/erpnext_backups/2026-09-02_09-48` contained
    all four required non-empty artifacts.
-   Verified no `.partial-*` directory remained after the test.
-   Removed the duplicate `gani` backup cron entry.
-   Retained root's daily 02:00 Asia/Manila backup schedule as the sole
    scheduled ERPNext backup job.
-   Left first unattended hardened cron execution explicitly pending
    verification.

## 2026-09-02 --- Project Source documentation consolidation

-   Established Git as the authoritative source for tracked
    deployment-framework code.
-   Consolidated architecture and engineering guidance into
    `framework.md`.
-   Consolidated release, deployment, rollback, and routine operational
    guidance into `operations.md`.
-   Updated `recovery.md` for the verified NAS/backup state and recovery
    procedures.
-   Updated `roadmap.md` to distinguish completed, partially completed,
    and planned work.
-   Retained `ccpc-project-context.md` as the concise current-state and
    safety-boundary reference.
-   Reduced duplicated documentation roles previously served by separate
    deployment guide, release process, operations index, architecture,
    and engineering documents.

## 2026-09-02 --- Development port hardening (PR #9)

-   Hardened tracked devcontainer port mappings to bind development
    ranges to IPv4 loopback:
    -   `127.0.0.1:8000-8005:8000-8005`
    -   `127.0.0.1:9000-9005:9000-9005`
-   Updated alternate development setup documentation to preserve
    loopback binding.
-   Merged PR #9 with merge commit `5af1bda`.
-   Deleted the merged feature branch locally and from the CCPC remote.
-   Updated the ignored active `.devcontainer/docker-compose.yml`
    locally to match the hardened template.
-   Did not recreate the running devcontainer; runtime verification of
    the new mappings remains pending a deliberate recreation.

## CI runner disk-headroom mitigation (PR #8)

-   Diagnosed the v16 full-build CI failure as GitHub-hosted runner disk
    exhaustion while pulling MinIO.
-   Added disk diagnostics to establish the failure condition.
-   Added targeted `docker buildx prune --all --force` cleanup after
    image build and before tests.
-   Avoided broad `docker system prune`.
-   Verified the subsequent CI run passed.
-   Merged PR #8 with merge commit `19118dc`.

## LAN production access (PR #7)

-   Added the tracked LAN-production Compose override.
-   Published the production frontend on host TCP port 80.
-   Preserved upstream-compatible dynamic Frappe routing in base
    Compose.
-   Set the CCPC LAN override default site header to `ccpcerp.local`.
-   Added the intended user-facing URL `http://ccpcerp.com`.
-   Updated deployment/database Compose operations to use the CCPC
    Compose configuration.
-   Updated local health checks and deployment/rollback summaries for
    the intended LAN routing design.
-   Added LAN production access operational documentation.
-   Corrected the initial site-routing regression with commit `caa820c`.
-   Merged PR #7 with merge commit `27cb5ca`.

### LAN/WAN verification

-   Verified LAN DNS and client access to `http://ccpcerp.com`.
-   Verified host port 80 routes to the intended Frappe site.
-   Verified frontend-to-backend and frontend-to-WebSocket connectivity
    inside the production Docker network.
-   Verified the frontend is the only production application container
    with a host-published port.
-   Verified no router One-to-One NAT, Virtual Server, DMZ, or UPnP
    mapping exposes the ERP server.
-   Verified public DNS for `ccpcerp.com` is not published.
-   Verified an independent cellular IPv4 test could not reach the ERP
    HTTP service.
-   Verified the server has no globally scoped IPv6 address.

## Governance and validation hardening

-   Added/maintained repository-level `AGENTS.md` engineering and
    AI-agent policy.
-   Added `.github/CODEOWNERS` ownership for `@ccpcerp`.
-   Added `SECURITY.md` with private vulnerability reporting guidance.
-   Updated issue and pull-request templates while preserving upstream
    CI and Dependabot machinery.
-   Established `uvx --python 3.12 pre-commit run --all-files` as the
    known-good local repository-wide validation command.
-   Investigated GitHub branch-protection/ruleset enforcement and
    documented the current private-repository account/plan limitation.
-   Retained the voluntary feature-branch, pull-request, and
    CI-before-merge workflow.

## Framework v1.0.0

Release date: `2026-07-27`

### New features

-   Modular deployment framework
-   Modular build framework
-   Rollback framework
-   Shared deployment workflow
-   Docker module
-   Database module
-   Health module
-   Environment module
-   Git module
-   Version module

### Documentation

-   Framework documentation
-   Recovery guide
-   Deployment guide
-   Release process

### Infrastructure

-   GitHub repository
-   Git tag
-   Framework release

## Notes

Operational hardening completed after v1.0.0 does not by itself imply
that a new framework version has been formally released.

Production deployment, rollback, database migration/restoration,
destructive Docker cleanup, production container recreation, backup
deletion, and retention changes remain separately controlled operations
requiring explicit approval.