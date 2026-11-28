# CCPC ERP Project Context

_Last updated: 2026-10-12 (GitHub-first decision; older sections are historical)_

## CURRENT RULE — 2026-10-12: GitHub-first CCPC custom-app development

This block **supersedes older P20 Codex automation priorities and DEV-first editing habits**. Full source of truth: [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).

- **Default:** GitHub change/review first, controlled pull of reviewed commit into persistent DEVELOPMENT for testing, then push any test fixes back to GitHub. A merged code change does not authorize PRODUCTION deployment; PRODUCTION requires separate explicit approval and backup/recovery review.
- App repo: `ccpcerp/ccpcerp`. **Correct active billing feature branch** `feature/intercompany-material-billing` at confirmed pushed commit `7ac238e`, not default `version-16` at `cfcc193`. The Windows clone remains clean at the latter commit and **should be kept for now**; deleting it is unnecessary.
- At last operator check, DEVELOPMENT app `/workspace/development/frappe-bench/apps/ccpcerp` tracked the feature branch at `7ac238e` with **eight uncommitted app/patch/test changes, plus untracked `AGENTS.md`**. **Before any new pull, branch switch, reset or GitHub-first implementation, inspect and preserve this DEV-only work** on a reviewed separate checkpoint branch. No staging/commit/push of those changes has been verified.
- ChatGPT can inspect code via the connected GitHub tools; **Codex is optional**, not required for GitHub inspection. No additional paid OpenAI API key or revival of unattended reporting. Avoid Codex inside existing DEV container because its SSH material is mounted/readable and its nested sandbox was previously unreliable.
- Priority feature: Withdrawal Slip → Material Issue → Intercompany Billing, especially transaction locking and duplicate invoice protection. Pushed code's concurrent approval safety is **not proven**; DEV-only diffs may include the fix. No automatic migrations, transaction testing, PROD operations, or destructive Git commands without review.
- Documentation remains on a **draft documentation branch PR #24**, not merged to main or automatically synced into ChatGPT Project Sources. Fresh chats should open this workflow link explicitly.

## 2026-10-10 continuity update — Codex DEVELOPMENT reporting (P19G complete; P20A in progress)

**Scope and evidence:** This block records results observed in the 2026-10-10
operator-assisted Ubuntu terminal session and a subsequent read-only GitHub
verification. It supplements the older sections below; it is **not** proof
that all earlier infrastructure and backup facts were rechecked on this date.

### Latest verified state

- CCPC GitHub report inbox: private `ccpcerp/ccpc-frappe-deployment`, Issue
  [#22](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22).
- First controlled live DEVELOPMENT report was published **once**, and the
  GitHub comment was independently located as
  [comment 6094678841](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22#issuecomment-6094678841),
  author `ccpcerp`. Corresponding SQLite delivery status `confirmed` and comment
  ID `6094678841` were subsequently verified read-only.
- Tested report: `p19f-controlled-live-test.md`, content SHA-256
  `ea253ac6183328b69bebdd362f1186286f48ad2d59dd7349228d75fc6fd66333`.
  Delivery marker SHA-256 (a **different** identifier):
  `70602198f63202860dc9347c38fd92aba4776d2d2a7b87652c288b24cb46a61b`.
- The temporary fine-grained `ccpcerp` GitHub token was deleted in GitHub by
  the operator and its `/etc/ccpc-reporter/github-token` source file removed;
  an absence check passed. Do not assume any token remains available.
- `/etc/ccpc-reporter/approvals` was verified root-owned mode `0700` and
  **empty**. The approved one-shot manifest was retired.
- DEVELOPMENT `.ccpc-codex-report-outbox` was verified **empty** after the
  synthetic report was removed with a SHA-256 check.
- The general runtime source still sets `LIVE_PUBLISHING_ENABLED = False`;
  known publisher systemd service/timer names were checked **inactive**.
  This is not a comprehensive check of all possible scheduler names.
- Automatic GitHub publishing is **not active**; draft optional AI reviewer
  in deployment-repository PR #23 is **not activated or merged** as observed
  in the reporting work. Recheck live GitHub status before changing it.
- The `ccpc-reporter` account is a dedicated unprivileged identity (UID 995,
  GID 983); it has no Docker/sudo/lxd membership. DEV Codex/`frappe` UID 1000
  writes report files to the DEVELOPMENT-only outbox; under tested systemd
  isolation the reporter receives that outbox read-only at
  `/run/ccpc-reporter/inbox` and cannot traverse the wider host workspace.
- Durable SQLite ledger: `/var/lib/ccpc-reporter/deliveries.sqlite3`,
  owned by `ccpc-reporter`, mode `0600`. Its integrity and the matching
  confirmed comment record passed read-only verification.

### P20A current progress

- **P20A-1 PASSED:** `/usr/local/libexec/ccpc-reporter/automatic_report_policy.py`
  installed as root:root, mode `0644`, without modifying the existing
  coordinator or enabling any service.
- **P20A-2 PASSED:** 15/15 offline safety tests. The renderer accepts a strict
  1,024-byte maximum JSON object with **only** nine enumerated fields:
  `version`, `environment`, `work_type`, `status`, `change_scope`,
  `test_status`, `finding`, `risk`, `approval`. It generates a fixed-format
  DEVELOPMENT-only Markdown report. Unknown/free-text fields, duplicate keys,
  invalid environment/types/categories/timestamps, and oversized input fail.
  No reports were written to disk or sent to GitHub in these tests.
- The automatic summary contains **Codex-reported categories**, not independently
  verified findings; it cannot support a full AI code audit without separate
  evidence collection and review.
- Next: **P20A-3** — design/test Codex's structured completion-metadata handoff
  (single atomic write, immutable/stable task identity, filename/ownership
  limits, completeness gate, no secrets). Then P20B offline producer/publisher
  integration; P20C review and test PR #23 AI reviewer including API cost and
  permissions; P20D authorized end-to-end activation. **No activation yet.**

### Safety and continuity constraints

- Two Docker Compose projects share the Ubuntu host. The DEV container is
  `frappe_docker_devcontainer-frappe-1`, its workspace is
  `/workspace/development/frappe-bench/apps/ccpcerp`, and site is
  `development.localhost` (not disposable). Do not touch production Compose,
  production ERPNext data, migrations, Docker lifecycle, or backups without
  explicit separate approval.
- DEV Codex's nested sandbox previously failed in this Docker setup; older
  documentation below records a historical `danger-full-access` alias. **That
  historical alias is not a standing approval to use it.** Treat the DEV
  container's bind-mounted workspace and SSH material as sensitive.
- Manual detailed reports still require explicit review and a SHA-256 approval
  record; metadata-only automatic reporting remains a planned, disabled feature.
- Regex filters and fixed categories reduce exposure but do not guarantee
  confidentiality, correctness, or absence of misleading agent claims.
- No PR merge, new token, service/timer enablement, GitHub workflow activation,
  automatic AI API spending, or production action is authorized by P20A testing.

For next-chat continuity use `P20-HANDOFF-2026-10-10.md` alongside these
project documents; `changelog.md` records the milestone and `roadmap.md`
records the outstanding work.

## Project identity

CCPC ERP is a Frappe/ERPNext deployment project built on the upstream `frappe/frappe_docker` repository, with CCPC-specific deployment automation, operational documentation, and a custom `ccpcerp` application.

Primary GitHub repositories:

- Deployment framework: `ccpcerp/ccpc-frappe-deployment` (private)
- Custom application: `ccpcerp/ccpcerp` (private)

Repository remotes for `/workspace`:

- `ccpc` — CCPC deployment repository
- `origin` — upstream `frappe/frappe_docker`; keep this upstream remote intact

Custom app remote at `development/frappe-bench/apps/ccpcerp`:

- `origin` — `ccpcerp/ccpcerp`

Local Git identity for the CCPC repositories is `CCPC ERP <ccpcerp@gmail.com>`.

## Deployment framework

The CCPC ERP Deployment Framework is a modular Bash deployment framework. Its primary entry points are:

- `scripts/build.sh`
- `scripts/deploy.sh`
- `scripts/rollback.sh`

Workflow logic is coordinated through `scripts/deployment.sh`. Operational modules include Docker, database, environment, Git, health, and version handling.

Important configuration includes:

- Application branch: `version-16`
- Release prefix: `v16`
- App path: `development/frappe-bench/apps/ccpcerp`
- Image name: `ccpcerp`
- Containerfile: `images/custom/Containerfile`
- Internal Frappe site name: `ccpcerp.local`

Engineering principles include simplicity, single responsibility, reusable modules, testing, documentation, and reversible production changes.

## Governance and Codex

`AGENTS.md` is the repository-level engineering and AI-agent policy. It covers architecture, Bash standards, Git safety, secrets, Docker/database/deployment safety, validation, documentation, and Codex workflow.

Codex is an engineering assistant, not an unrestricted production operator. Production deployment, rollback, database changes, destructive Docker actions, and other production-impacting operations require explicit user approval.

Codex CLI is installed in the dev container. Because the normal Codex sandbox cannot create its nested namespace in this container environment, the project uses the controlled alias:

`ccpc-codex='codex --sandbox danger-full-access --ask-for-approval on-request --no-alt-screen'`

The dev container remains an external isolation boundary, but `/workspace` is bind-mounted and Docker access can affect the environment. `--dangerously-bypass-approvals-and-sandbox` is not normal project practice.

Repository governance includes:

- `.github/CODEOWNERS` with `@ccpcerp` ownership
- `SECURITY.md` using `ccpcerp@gmail.com` for private vulnerability reports
- Updated issue and pull-request templates
- Existing upstream CI and Dependabot machinery preserved

## Validation baseline

The repository has a clean pre-commit baseline. The baseline cleanup was merged before the governance work.

Because the local default Python 3.14 environment is incompatible with the current `pyupgrade` pre-commit hook, the known-good local validation command is:

`uvx --python 3.12 pre-commit run --all-files`

Additional checks include `git diff --check` and `bash -n` for changed shell files.

## ERPNext custom application --- Phase 2 Equipment Asset Integration

Phase 2 Equipment Asset Integration is merged into the custom application
`version-16` branch through PR #4.

Current verified custom-app Git state:

- Feature commit: `0971a00` --- `feat: add equipment asset assignment integration`
- Merge commit: `464d28e` --- `Merge pull request #4 from ccpcerp/feature/equipment-asset-integration`
- Local `version-16`, `origin/version-16`, and `origin/HEAD` were verified at `464d28e` after merge.
- The merged feature branch was deleted locally and from `origin`.

Verified Phase 2 behavior:

- Equipment remains the permanent functional/plant position. ERPNext Asset is
  the physical/accounting asset occupying that position.
- `Equipment Asset Assignment` records the historical relationship between
  Equipment and Asset using half-open assignment intervals.
- New assignments enforce Active Equipment, submitted same-company Assets,
  blocked terminal Asset states, overlap prevention, immutable assignment
  identity/install fields, one-way closure, and protected deletion rules.
- Work Request and Job Order include read-only assignment/Asset provenance
  snapshots. Linked Job Orders inherit the Work Request snapshot exactly;
  standalone Equipment Job Orders snapshot the current assignment when one
  exists. Existing records are not backfilled.
- Maintenance accounting continues to use the Equipment Accounting Dimension;
  Phase 2 does not add custom Asset GL/accounting behavior.
- Concurrent new assignments are serialized with deterministic Equipment then
  Asset locking and locking overlap reads. The MariaDB errno `1020`
  `ER_CHECKREAD` case from the locking overlap read is converted to a retry
  ValidationError; unrelated deadlock errors are not masked.

DEVELOPMENT validation status:

- Site migration completed successfully on `development.localhost`.
- 108 Python tests passed with 0 failures.
- Work Request, Job Order, and equipment-costing JavaScript regressions passed.
- Python compile, DocType JSON validation, JS syntax, and `git diff --check` passed.
- Real two-process concurrency testing proved one assignment can commit while
  the competing assignment is rejected cleanly without creating a duplicate.
- DEVELOPMENT-only support/test records created during Phase 2 validation remain
  present intentionally unless a separate cleanup is approved.

Release boundary:

- Phase 2 is merged and DEVELOPMENT-validated.
- Production has not been deployed, migrated, or otherwise changed for Phase 2.
- Production release preparation, backup/recovery verification, image build/tag
  selection, deployment, and migration remain separate controlled steps that
  require explicit approval.

## Protected local production state

`compose.yaml.backup` is a local, untracked production backup. It must not be staged, committed, deleted, reset, or cleaned.

Independent backups also exist outside the repository under `~/ccpc-local-backup/`.

The former uncommitted base-Compose edit that changed `8080:8080` to `80:8080` has been replaced by the tracked LAN-production override design described below. The base Compose file is no longer dependent on that local port edit.

## LAN production access

LAN production access was implemented through PR #7 and is now merged into `main`.

Merge commit:

`27cb5ca` — `Merge pull request #7 from ccpcerp/infra/lan-production-access`

The feature branch `infra/lan-production-access` has been deleted both locally and from the `ccpc` remote after verifying the merge.

The intended access path is:

`LAN client -> ccpcerp.com -> ERP server TCP 80 -> Docker host 80/container 8080 -> frontend Nginx -> Frappe site ccpcerp.local`

Key implementation details:

- `overrides/compose.lan-production.yaml` publishes `${HTTP_PUBLISH_PORT:-80}:8080`.
- The LAN override supplies the CCPC default `FRAPPE_SITE_NAME_HEADER` of `ccpcerp.local`.
- Base `compose.yaml` preserves upstream-compatible dynamic routing with `${FRAPPE_SITE_NAME_HEADER:-$$host}`.
- `scripts/config.sh` exports the intended CCPC site header and HTTP publish port.
- User-facing ERP URL is `http://ccpcerp.com`.
- Local health checks use the host-published port and explicitly route the intended Frappe site.
- Deployment/database Docker Compose operations use the CCPC Compose helper so the LAN override is consistently included.
- Deployment and rollback summaries now report the intended ERP access URL instead of hardcoded `localhost:8080`.
- `docs/04-operations/lan-production-access.md` documents the design and operational assumptions.

The corrective commit `caa820c` restored dynamic Frappe site routing in base Compose while keeping the CCPC-specific default in the LAN override. This fixed the initial CI endpoint-routing regression.

Merging this code did **not** deploy, restart, migrate, or otherwise change the running production environment.

## LAN/network verification — verified

The LAN production design from PR #7 has now been verified against the running environment. This verification was read-only except for the separate devcontainer hardening work described below; it did not deploy, restart, migrate, or otherwise change the production stack.

Verified LAN and host behavior:

- LAN DNS resolves `ccpcerp.com` to the ERP server's intended private LAN address.
- The ERP server's LAN address is backed by an enabled DHCP reservation.
- A separate Windows LAN client successfully reached `http://ccpcerp.com` on TCP port 80 and received the Frappe login response.
- Server-local requests to `http://ccpcerp.com` also returned the Frappe login response.
- A direct request to host port 80 with `Host: ccpcerp.local` returned the same login page, confirming internal Frappe site routing.
- The running production frontend has `FRAPPE_SITE_NAME_HEADER=ccpcerp.local`, `BACKEND=backend:8000`, and `SOCKETIO=websocket:9000`.
- Frontend-to-backend TCP connectivity on port 8000 was verified inside the production Docker network.
- Frontend-to-WebSocket TCP connectivity on port 9000 was verified inside the production Docker network.
- Production Docker networking was inspected. The frontend is the only production container with a host-published application port. Backend, WebSocket, database, Redis, queues, and scheduler have no host-published ports.
- Docker publishes production frontend host port 80 to frontend container port 8080.
- UFW is inactive. The effective Docker/iptables-nft rules were inspected directly; Docker DNAT/filter rules, rather than UFW, govern the observed container port publication.
- The server has no globally scoped IPv6 address, so there is currently no direct globally routed IPv6 path to the host listeners.

Verified router and WAN behavior:

- Router One-to-One NAT configuration was checked and contained no mapping exposing the ERP server.
- Router Virtual Server/port-forward configuration was checked and contained no inbound mapping exposing the ERP server.
- Router DMZ configuration was checked and contained no mapping exposing the ERP server.
- UPnP was disabled and no UPnP mappings were present.
- Public DNS lookup for `ccpcerp.com` returned NXDOMAIN; the hostname currently exists through LAN DNS rather than public DNS.
- An independent cellular-network test to the router's public IPv4 address could not reach the ERP HTTP service. The public address itself is intentionally omitted from this context.

Together, these checks provide good evidence that the current production HTTP service is reachable through the intended LAN path and is not currently reachable from the public Internet through the tested IPv4/IPv6 paths.

### Remaining application/network follow-ups

Basic LAN, Docker, router, public-DNS, IPv4 WAN, and IPv6 verification is complete. Remaining checks are narrower application- and segmentation-level reviews:

- Verify canonical application URL behavior in a normal browser.
- Verify redirects and host/scheme normalization.
- Verify absolute links, OAuth callbacks, and email-generated links where applicable.
- Review cookie scope/security attributes and CSRF behavior through normal authenticated browser workflows.
- Verify browser WebSocket connection/upgrade behavior end-to-end.
- Review the observed HSTS header being emitted while the current LAN service is accessed over plain HTTP.
- Verify intended LAN/VLAN segmentation, including guest/IoT or other network segments where applicable.
- Consider internal HTTPS later as a separate hardening improvement.

The current LAN design intentionally uses HTTP and retains the internal Frappe site name `ccpcerp.local`.

## Devcontainer port exposure and hardening — resolved in PR #9

During LAN verification, the running development container was found to have Docker host mappings for:

- `8000-8005`
- `9000-9005`

The mappings were bound on all host interfaces. Windows LAN connection tests to ports 8000 and 9000 failed, and inspection inside the development container confirmed that no process was listening on the mapped development ranges at verification time. Therefore this was not an active application exposure during testing, but it was a latent exposure: if a development service later listened on one of those ports, Docker's existing host mapping could make it reachable through host network interfaces.

The source of the mappings was traced to `.devcontainer/docker-compose.yml`. The `.devcontainer` directory is intentionally ignored by Git. The tracked template `devcontainer-example/docker-compose.yml` contained the same upstream-style mappings, and `docs/05-development/04-alternate-setup.md` contained a related alternate-port example.

PR #9 hardened the tracked development configuration by binding the development ranges to IPv4 loopback:

- `127.0.0.1:8000-8005:8000-8005`
- `127.0.0.1:9000-9005:9000-9005`

The alternate development setup documentation was updated to preserve the loopback prefix when alternate port ranges are used. This keeps host-local development access while preventing direct LAN access through those Docker-published ports after the devcontainer is recreated. Container-to-container Docker networking is unaffected.

PR #9 details:

- Branch: `security/restrict-devcontainer-ports`
- Feature commit: `fe08077` — `security: restrict devcontainer ports to loopback`
- Merge commit: `5af1bda` — `Merge pull request #9 from ccpcerp/security/restrict-devcontainer-ports`
- CI/checks passed before merge.
- The local and remote feature branches were deleted after merge.

Safe validation included `git diff --check` and applicable pre-commit hooks. Compose semantic validation was not available inside the dev container because the Docker/Compose CLI was not installed there; no runtime-changing validation was substituted.

The ignored active `.devcontainer/docker-compose.yml` was updated locally to match the loopback-only template. However, the currently running devcontainer has **not** been restarted or recreated. Docker applies published-port changes at container creation/recreation, so the running container still has its existing host port mappings until a future deliberate recreation. No container recreation, production deployment, migration, or Docker cleanup was performed as part of PR #9.

## CI runner disk-headroom issue — resolved in PR #8

PR #7 exposed two different CI issues. The first was a real site-routing problem and was fixed by `caa820c`. After that fix, the v16 test suite reached Frappe and passed endpoint, ping, file, database, and cache checks before failing while Docker pulled MinIO with:

`docker: failed to register layer: write /usr/bin/minio: no space left on device`

The failure reproduced and was isolated as a GitHub-hosted runner disk-headroom problem, not a LAN-production regression. A dedicated branch/PR, `ci/runner-disk-headroom` / PR #8, added diagnostics around the image-build/test transition. Immediately before pytest on the failing AMD64 runner, diagnostics showed:

- `/dev/root`: 72 GB total, 68 GB used, 3.9 GB available, 95% used.
- Docker images: 2.147 GB total, 1.88 GB reclaimable.
- Local volumes: 8.228 GB in use.
- Buildx cache: 7.928 GB total and 7.928 GB reclaimable.

Based on that evidence, PR #8 added a targeted cleanup after the image build and before Python/test setup:

`docker buildx prune --all --force`

A broad `docker system prune` was deliberately avoided. The subsequent CI run passed all checks, confirming the targeted Buildx cleanup restored enough runner disk headroom for the MinIO-backed tests.

PR #8 details:

- Diagnostic commit: `e9d4cf9 ci: add runner disk usage diagnostics`
- Mitigation commit: `efc5717 ci: free buildx cache before tests`
- Merge commit: `19118dc`
- Remote branch `ccpc/ci/runner-disk-headroom` was deleted after merge.

MinIO version/digest pinning remains a separate reproducibility improvement and was not required to resolve this disk-capacity failure.

## Current Git state after PR #9

After PR #9 merged, local `main` was fast-forwarded to the merge commit and verified against `ccpc/main`.

Current verified state:

- `HEAD -> main` and `ccpc/main` are synchronized at `5af1bda`.
- `compose.yaml.backup` remains untracked, protected, and untouched.
- The merged feature branch `security/restrict-devcontainer-ports` was deleted locally and from the `ccpc` remote.
- The Frappe upstream `origin` remote was untouched.
- No production runtime, container, database, deployment, or Docker-cleanup operation was performed during PR #9 merge and branch cleanup.

## Production backup and recovery state

The ERPNext production backup path was reviewed and repaired on 2026-09-02.

The production site backed up by the host backup workflow is:

`ccpcerp.local`

### NAS backup storage

The Synology NAS backup share is mounted on the ERP server at:

`/mnt/erpnext_backups`

The expected CIFS source is:

`//192.168.50.132/erpnext_backups`

The NAS address was updated after the network migration because the previous address on the former subnet was no longer reachable.

The `/etc/fstab` configuration was updated to use the current NAS address while preserving the existing CIFS credential-file mechanism and mount options.

The mount was verified using the live mount table:

- target: `/mnt/erpnext_backups`
- filesystem: CIFS
- source: `//192.168.50.132/erpnext_backups`
- access: read/write

Credentials and credential-file contents must never be copied into project documentation, source control, logs, ChatGPT project context, or troubleshooting output.

### Historical local fallback condition

Before the NAS mount was repaired, `/mnt/erpnext_backups` was an ordinary directory on the ERP server's local NVMe filesystem rather than the intended CIFS mount.

The previous backup script created its destination directory before proving that the NAS was mounted. As a result, scheduled backups could appear successful while being written to local server storage.

The local fallback backup set was preserved before remounting the NAS.

A recovery copy exists at:

`/home/gani/erpnext-backup-recovery-2026-09-02`

It contained 29 timestamped backup directories with 116 files. The original and recovery-copy file counts and total byte counts matched before NAS recovery work continued.

The recovery set was transferred to the Synology NAS using `rsync --ignore-existing`. A subsequent checksum dry-run using `rsync -rcn` reported no differences between the recovery copy and the corresponding NAS content.

The recovery copy should remain in place until the hardened scheduled backup workflow has completed an unattended run and the operator deliberately approves cleanup.

There is a known historical backup-date gap for:

`2026-08-04`

No backup for that date was found either in the recovered local fallback set or in the NAS backup set. This should be treated as a documented historical gap, not reconstructed or assumed to exist.

### Hardened backup script

The active production backup script is:

`/usr/local/bin/erpnext_backup.sh`

A pre-change safety copy was retained as:

`/usr/local/bin/erpnext_backup.sh.backup-2026-09-02`

The hardened script now follows a fail-safe sequence:

1. Create a fresh Frappe backup locally inside the production backend container using `bench --site ccpcerp.local backup --with-files`.
2. Determine the newly created backup set.
3. Require all four expected artifacts to exist and be non-empty:
   - compressed MariaDB database backup
   - site configuration backup
   - public files archive
   - private files archive
4. Retain local Frappe backup files according to the configured local retention period.
5. Verify `/mnt/erpnext_backups` is an actual mounted filesystem.
6. Verify the mounted filesystem type is `cifs`.
7. Verify the mount source exactly matches `//192.168.50.132/erpnext_backups`.
8. Verify the NAS mount is writable.
9. Copy all four artifacts to a temporary `.partial-*` directory on the NAS.
10. Require each copied artifact to be non-empty.
11. Rename the completed temporary directory to the final timestamped NAS backup directory only after all copies succeed.
12. Apply NAS retention only to directories matching the expected timestamp naming pattern.
13. Report successful completion only after the complete workflow succeeds.

This prevents an unavailable NAS from silently degrading into local NVMe storage.

The previous behavior that ignored failed public/private-file copies with `|| true` has been removed. All four artifacts are now required for a successful NAS backup.

Temporary `.partial-*` directories are used so an interrupted transfer is not presented as a completed timestamped backup.

### Backup retention

Current retention policy:

- Local Frappe backup files: 7 days
- NAS timestamped backup directories: 30 days

NAS cleanup is restricted to timestamp-formatted directories matching the backup naming convention rather than deleting arbitrary directories at the NAS root. This protects unrelated NAS-managed locations such as Synology's `#recycle`.

Retention changes and manual cleanup of backup data are destructive operations and require explicit approval.

### Backup validation performed on 2026-09-02

A controlled production backup test was run after the script was hardened.

The test exited successfully with exit code `0`.

The script confirmed:

- all four Frappe artifacts existed and were non-empty
- the NAS mount was the expected CIFS source
- all four artifacts were copied successfully
- the temporary NAS directory was promoted to the final directory
- NAS retention completed
- the backup workflow reported successful completion

The resulting NAS backup directory was:

`/mnt/erpnext_backups/2026-09-02_09-48`

It contained exactly four expected files:

- `20260902_094850-ccpcerp_local-database.sql.gz`
- `20260902_094850-ccpcerp_local-files.tar`
- `20260902_094850-ccpcerp_local-private-files.tar`
- `20260902_094850-ccpcerp_local-site_config_backup.json`

All four files were non-empty.

A search after the test found no leftover `.partial-*` backup directory.

This verifies the hardened backup workflow end-to-end when manually executed.

### Backup scheduling

The production backup schedule is owned by root's crontab:

`0 2 * * * /usr/local/bin/erpnext_backup.sh >> /var/log/erpnext_backup.log 2>&1`

The ERP server timezone is:

`Asia/Manila`

The system reports the abbreviation `PST` for Philippine Standard Time with UTC offset `+0800`.

The backup therefore runs daily at:

`02:00 Asia/Manila`

A duplicate backup entry that had existed under user `gani` was removed. That user could not write the root-owned `/var/log/erpnext_backup.log`, while root can execute the root-owned script and write the log.

There should now be exactly one scheduled ERPNext backup job: the root crontab entry.

The first natural unattended execution of the newly hardened script is still pending verification. Until that run is inspected, manual end-to-end backup validation is complete but unattended scheduler validation should be considered pending.

### Remaining backup/recovery follow-ups

Remaining backup and recovery work is narrower than the repaired mount/script issue:

- Verify the first unattended hardened backup after its natural 02:00 run.
- Consider adding periodic restore testing rather than relying only on successful backup creation.
- Consider adding backup-failure alerting or monitoring.
- Decide later, with explicit approval, when to remove `/home/gani/erpnext-backup-recovery-2026-09-02`.
- The old local fallback backup directories underneath `/mnt/erpnext_backups` remain hidden while the CIFS filesystem is mounted. They should not be removed without deliberately unmounting the NAS and explicitly approving the destructive cleanup.
- Preserve the known `2026-08-04` historical backup gap in operational records.

The repaired backup path is sufficient to proceed with normal ERPNext configuration work while these follow-ups are completed separately.

## GitHub hardening — current limitation

Branch protection/ruleset hardening was investigated for `main`, but GitHub displayed that rulesets and classic branch-protection rules will not be enforced on this private repository under the current account/plan. GitHub indicated that enforcement requires moving to a GitHub Team or Enterprise organization account.

No unenforced ruleset or classic protection rule was created. Until the account/plan changes, repository governance relies on the established voluntary workflow:

- Work on feature/fix branches rather than directly on `main`.
- Open pull requests into `main`.
- Run and review CI before merging.
- Keep force pushes and branch deletion of `main` out of the normal workflow.
- Resolve review conversations where practical.
- Do not require an external approving reviewer in the current single-maintainer workflow.

The v16 full-build CI disk-headroom issue has now been resolved by PR #8, so it is no longer considered an unstable check because of that known capacity problem. Dependabot PRs should still not be merged blindly; validate them against the clean lint baseline and current CI behavior.

## Roadmap

Framework v1.1 priorities include:

- Automatic rollback semantics with explicit database recovery boundaries
- Deployment history/logging
- Image cleanup
- Improved error reporting

Automatic rollback must preserve reversibility: capture the previous release/tag, restore configuration and containers safely, do not automatically reverse database migrations, document database recovery explicitly, and test failure paths with mocks before production use.

ERPNext business configuration can now proceed in parallel with remaining infrastructure hardening.

Recommended business-configuration sequence:

1. Company and accounting foundation
2. Warehouses
3. Item Groups and Units of Measure
4. Item master data
5. Suppliers and customers
6. Opening stock
7. Purchasing and receiving
8. Stock transfers, issues, and adjustments
9. Selling and delivery
10. Roles, permissions, and approval workflows
11. Operational reports and end-to-end testing

Opening inventory and other material production transactions should not be entered until the warehouse structure, UOM design, item coding rules, valuation approach, and related accounting configuration have been reviewed.

## Working practices

Work incrementally and verify command output before proceeding.

Keep upstream `origin` intact and use `ccpc` for the CCPC deployment repository.

Use feature branches and pull requests for tracked repository changes.

Never expose passwords, tokens, NAS credentials, 2FA/recovery codes, SSH private keys, or other secrets.

Do not stage, commit, delete, reset, clean, or overwrite `compose.yaml.backup`.

Production-impacting actions are always separate from code merge/branch cleanup and require explicit approval.

Destructive backup-retention changes, backup deletion, database changes, Docker cleanup, deployment, rollback, migration, and production container recreation require explicit approval.

Project Sources should contain the consolidated documentation set rather than tracked code snapshots. Git remains authoritative for tracked repository code and configuration.

Project context should distinguish between:

- verified state
- pending validation
- known historical gaps
- planned improvements

Do not represent an unverified assumption as completed infrastructure state.