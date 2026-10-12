# CCPC ERP Operations Manual

*Last updated: 2026-10-12 (GitHub-first custom-app workflow)*

## Current custom-app development rule (2026-10-12)

The CCPC owner adopted a **GitHub-first workflow**; read the [authoritative runbook](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) before any new DEVELOPMENT code synchronization, especially in a fresh ChatGPT thread. Custom-app code lives in `ccpcerp/ccpcerp` (billing feature branch `feature/intercompany-material-billing`), **not** the deployment framework repository. The first transition is **not yet complete**: DEVELOPMENT currently has eight uncommitted app code/test/patch files and a separate untracked `AGENTS.md`. Inspect/preserve them on a reviewed checkpoint branch before pulling or replacing code.

After reconciliation: prepare/review code in GitHub → pull reviewed commits into DEVELOPMENT on a verified clean worktree → validate on DEV → commit any DEV test fixes back to GitHub. GitHub is source of truth for **pushed committed app code**, not Frappe site/database state. PRODUCTION remains independently controlled, with explicit operator approval and verified recovery preparation. No automated Codex reporting, new paid API key, or experimental Codex execution inside the DEV container.

## Purpose

This document defines the routine release, deployment, rollback, and
operational verification procedures for the CCPC ERP Deployment
Framework.

It consolidates the former deployment guide, release process, and
operations index into one operational reference.

Architecture and engineering principles belong in `framework.md`.
Backup, restore, and disaster recovery procedures belong in
`recovery.md`. Current verified environment state belongs in
`ccpc-project-context.md`.

## Operating principles

Every production release should be:

-   Reproducible
-   Versioned
-   Tested
-   Documented
-   Recoverable
-   Explicitly approved before production-impacting execution

A code merge does not authorize a deployment.

Production deployment, rollback, database migration, database
restoration, destructive Docker cleanup, and production container
recreation require explicit operator approval.

## CCPC Codex DEVELOPMENT report publishing — state as of 2026-10-10

This section is a status and safety reference, **not authorization to execute
publication**. Controlled one-off publishing was tested on 2026-10-10, but the
general runtime and automatic reviewer remain disabled.

**Destinations and separation**

- GitHub: private `ccpcerp/ccpc-frappe-deployment` Issue #22, previously
  tested with the existing `ccpcerp` account.
- DEV writer: `frappe` (host UID 1000), Docker container
  `frappe_docker_devcontainer-frappe-1`; host outbox
  `/home/gani/deployments/frappe_docker/development/.ccpc-codex-report-outbox`
  (DEV `/workspace/development/.ccpc-codex-report-outbox`), originally checked
  owner UID 1000 / GID 983 / mode `2750`. Reports require owner UID 1000,
  GID 983, mode `0640`, a regular single-link file and a conservative size cap.
- Publisher identity: `ccpc-reporter` (UID 995, GID 983), not privileged.
  Tested systemd isolation binds only the outbox read-only at
  `/run/ccpc-reporter/inbox`, hides the host home workspace, denies Docker
  socket access and lacks Docker/sudo/lxd groups.
- Database: `/var/lib/ccpc-reporter/deliveries.sqlite3`, mode `0600`;
  successful test is confirmed with comment ID `6094678841`.
- Publisher code: `/usr/local/libexec/ccpc-reporter/` (`validate_report.py`,
  `report_policy.py`, `automatic_report_policy.py`, `github_comment.py`,
  `github_transport.py`, `github_https_policy.py`, `github_client.py`,
  `publisher_core.py`, `publisher_coordinator.py`, `publisher_lock.py`,
  `publisher_database.py`, `publisher_runtime.py`, `publisher_approval.py`,
  `report_review.py`, `publisher_controlled_once.py`).
- Root-only manual approval source: `/etc/ccpc-reporter/approvals/` mode `0700`;
  the successful test's approval was consumed and removed.
- Token source `/etc/ccpc-reporter/github-token` was **removed** after the
  token was revoked. Do not assume a credential is installed or request it in
  chat; any new one needs separate explicit operator approval. Do not store
  tokens in Docker, Git, command-line arguments, or documentation.

**Mandatory operating boundaries**

1. A prior one-shot test is not permission to publish new reports. Detailed
   reports require operator review, an exact SHA-256-bound approval, and a
   deliberate single use. Keep general `LIVE_PUBLISHING_ENABLED = False`.
2. All automatic metadata-only reporting is **planned and disabled**. The
   P20A-1 library only converts fixed enumerated JSON into a development
   report; the 15/15 P20A-2 test was offline. No timer or network publisher
   was enabled.
3. A read-only preview or format/syntax PASS is not approval to publish and
   does not prove confidentiality; Codex may access sensitive paths through
   existing DEV container mounts. Never auto-publish raw transcripts or code.
4. Timeouts/errors on submission can leave an `uncertain` SQLite delivery
   record. **Do not blindly retry.** Reconcile remotely under controlled
   procedure before deciding whether to continue.
5. The optional GitHub Actions AI reviewer in PR #23 remains a *draft*;
   review workflow permissions, author/issue markers, comment feedback loops,
   API cost and key handling before considering merge or activation.
6. No automatic migrations, code merges, production operations, or container
   recreation are implied by engineering report text or AI recommendations.

**Controlled proof of delivery:**
[GitHub comment 6094678841](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22#issuecomment-6094678841).
The posted synthetic outbox file was removed; the immutable audit record and
GitHub comment remain. A distinct production-backup/recovery audit still uses
`recovery.md`; do not confuse the publisher's SQLite ledger with ERPNext
production business-data backup.

**Next:** P20A-3 offline Codex completion metadata producer/atomic handoff,
then P20B integration under disabled service and no credentials. See
`P20-HANDOFF-2026-10-10.md` for the next-chat starting point.

## Source of truth

Use the current Git repository as the authority for tracked scripts,
Compose configuration, and implementation details.

Use `ccpc-project-context.md` for the latest verified
environment-specific state.

Do not rely on an old Project Source script snapshot when it conflicts
with newer verified Git state.

The intended production ERP access URL is currently:

`http://ccpcerp.com`

The internal Frappe site name is:

`ccpcerp.local`

## Release lifecycle

``` text
Development
    |
    v
Validation
    |
    v
Git Commit / Pull Request
    |
    v
Merge to Main
    |
    v
Build Release Image
    |
    v
Review Release
    |
    v
Explicit Deployment Approval
    |
    v
Deploy
    |
    v
Verify
    |
    v
Release Complete
```

Rollback is a separate explicitly approved production operation when
required.

## Pre-release requirements

Before preparing a release, verify:

-   Development work is complete.
-   Required changes are committed.
-   The intended branch is correct.
-   The relevant working tree is clean except for deliberately protected
    local state.
-   Required validation has passed.
-   Pull-request/CI requirements have been satisfied.
-   Documentation has been updated when behavior changed.
-   A recovery path is understood.

`compose.yaml.backup` is protected local production state and must not
be staged, committed, deleted, reset, cleaned, or overwritten.

## Validation baseline

The known-good repository-wide pre-commit command is:

``` bash
uvx --python 3.12 pre-commit run --all-files
```

Additional validation commonly includes:

``` bash
git diff --check
```

and, for changed shell files:

``` bash
bash -n <script>
```

Validation should be appropriate to the change. Do not perform a
production deployment merely as a substitute for missing non-production
validation.

## Build procedure

Building creates a release image but does not deploy it.

From the deployment repository root:

``` bash
./scripts/build.sh
```

The build workflow should verify the project/repository state, determine
the release version according to the current implementation, build the
Docker image, and verify that the resulting image exists.

After the build, review the generated image tag and retain it for the
deployment decision.

Do not assume example version numbers in historical documentation are
current.

## Production deployment

Production deployment requires explicit approval.

The normal deployment entry point is:

``` bash
./scripts/deploy.sh <image-tag>
```

Example form only:

``` bash
./scripts/deploy.sh v16.X.Y
```

The exact image tag must be an existing verified release image.

The current framework design is expected to:

1.  Verify the requested image.
2.  Preserve deployment configuration as appropriate.
3.  Apply the requested release tag/configuration.
4.  Deploy the containers using the CCPC Compose configuration.
5.  Wait for services.
6.  Verify running containers.
7.  Run the required site migration.
8.  Perform the application health check.
9.  Report the deployed release and intended access URL.

Because migration is production-impacting, deployment execution must
remain separately approved even when the deployment code itself has
already been reviewed and merged.

## Deployment verification

After an approved deployment, verify at minimum:

-   Required production containers are running.
-   The migration completed successfully.
-   The intended Frappe site responds through the intended host-routing
    path.
-   `http://ccpcerp.com` is reachable from an appropriate LAN client.
-   The application presents the expected ERPNext/Frappe interface.
-   Representative login/application behavior works.
-   No unexpected production service is exposed through host-published
    ports.
-   Logs do not show an obvious deployment failure.

Where the change affects routing or application behavior, also verify
the relevant browser, WebSocket, redirect, cookie, CSRF, or integration
behavior.

## Rollback procedure

Rollback requires explicit approval.

First identify the previous known-good application image.

Then use:

``` bash
./scripts/rollback.sh <previous-image-tag>
```

Example form only:

``` bash
./scripts/rollback.sh v16.X.Y
```

After rollback, verify the same core conditions as a deployment:

-   Required containers are running.
-   The intended application endpoint responds.
-   ERPNext is accessible.
-   Representative application behavior works.
-   Logs do not show an obvious failure.

### Database boundary

Application/image rollback and database rollback are not the same
operation.

Do not assume that deploying an older image reverses database
migrations.

If a failed release introduced a database/schema issue, follow an
explicitly approved recovery decision and the procedures in
`recovery.md`.

## Failed deployment handling

If a deployment fails:

1.  Stop and preserve useful failure output/logs.
2.  Determine whether the failure occurred before or after database
    migration.
3.  Avoid repeated uncontrolled deployment attempts.
4.  Identify the last known-good image/configuration.
5.  Decide whether application rollback is appropriate.
6.  Treat any database recovery as a separate production decision.
7.  Execute rollback only after explicit approval.
8.  Verify the recovered application.
9.  Document the failure and corrective action.

## Release checklist

Before declaring a production release complete:

-   [ ] Intended code is merged to the approved branch.
-   [ ] Required CI/validation passed.
-   [ ] Working state was reviewed.
-   [ ] Release image built successfully.
-   [ ] Image tag was reviewed and recorded.
-   [ ] Recovery/rollback path was identified.
-   [ ] Explicit production deployment approval was obtained.
-   [ ] Deployment completed successfully.
-   [ ] Database migration completed successfully, if part of the
    approved deployment.
-   [ ] Containers were verified.
-   [ ] Application health check passed.
-   [ ] Intended LAN URL was verified.
-   [ ] Representative ERPNext behavior was checked.
-   [ ] Documentation/changelog was updated where required.

## Git workflow

Tracked framework changes should normally follow:

``` text
Create feature/fix branch
        |
        v
Implement focused change
        |
        v
Validate
        |
        v
Commit
        |
        v
Push to CCPC remote
        |
        v
Open Pull Request
        |
        v
Review CI
        |
        v
Merge to main
        |
        v
Synchronize local main
```

Keep the upstream Frappe `origin` remote intact.

Use the CCPC deployment remote for CCPC-specific framework changes.

Do not force-push or destructively manipulate `main` as normal practice.

## Routine operational verification

Operational reviews may include:

-   Git state and synchronization
-   Production container state
-   Application health
-   Host-published ports
-   LAN routing
-   Backup/NAS status
-   Backup logs
-   Disk capacity
-   Docker disk consumption
-   CI health
-   Pending security or dependency updates

Read-only verification does not authorize production changes discovered
during the review.

If corrective work is required, separate investigation, code changes,
merge, and production execution into controlled steps.

## Backup and recovery

Detailed backup, NAS, restore, and disaster-recovery procedures are
maintained in:

`recovery.md`

Current backup highlights are intentionally not duplicated here because
the recovery guide is authoritative for those procedures.

The current project context may be consulted for the latest verification
status.

## Documentation map

The consolidated Project Source documentation model is:

-   `ccpc-project-context.md` --- current verified environment/project
    state
-   `framework.md` --- architecture and engineering principles
-   `operations.md` --- release, deployment, rollback, and routine
    operations
-   `recovery.md` --- backup, restore, and disaster recovery
-   `roadmap.md` --- planned framework work
-   `changelog.md` --- historical framework changes

This document replaces the separate Project Source roles previously
served by:

-   `deployment-guide.md`
-   `release-process.md`
-   `index.md`

## Change recording

Significant framework releases and operational changes should be
recorded in `changelog.md`.

The changelog is historical; it should not be used as the authority for
current runtime configuration.

## Future operational improvements

Potential improvements include:

-   Deployment history
-   Structured deployment logging
-   Improved failure reporting
-   Safe image lifecycle cleanup
-   Backup-failure alerting
-   Periodic restore testing
-   CI/CD integration
-   Multiple environments
-   Carefully designed automatic rollback with explicit database
    boundaries
-   Internal HTTPS where justified

Future automation must preserve operator visibility, recoverability, and
explicit control over production-impacting actions.

## Safety summary

Never expose passwords, tokens, NAS credentials, private keys, recovery
codes, or other secrets.

Do not stage, commit, delete, reset, clean, or overwrite protected local
production state such as `compose.yaml.backup`.

Do not deploy, rollback, migrate, restore a production database, perform
destructive Docker cleanup, recreate production containers, alter backup
retention, or delete backup data without explicit approval.

When current documentation and implementation disagree, verify the live
Git repository and current project context before taking operational
action.