# CCPC ERPNext — Dedicated PRODUCTION Operations and Deployment Record

**Created:** 2026-11-06  
**Scope:** Dedicated Ubuntu server `ccpcerp-prod`, **not yet live**.  
**Status:** Preparation/documentation approved; no authorization for container creation, deployment, database restoration/migration, cutover, or old-host changes.  
**Purpose:** Preserve current verified facts and the shortest safe continuation path so subsequent conversations do not repeat completed read-only inventory.

## How to use this file

1. **Read this production record first** for dedicated-host facts, current decisions, checks, and deployment gates. Read [the GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [active app/development handoff](CURRENT-HANDOFF-3.md) for overall engineering state.
2. GitHub controls committed deployment code and documentation; **live host output controls actual running state**. Date every new host observation. Do not silently upgrade a historical observation into current proof.
3. Update this file after meaningful host verification, approved deployment/restore, or recovery milestones. Keep a concise **latest checkpoint at the top**; archive lengthy test transcripts separately. Never store passwords, private keys, complete `.env`, credentials, sensitive configuration, database content, or unredacted logs.
4. Preserve DEV/PROD physical separation and the **old** production server. GitHub merges or preparatory approval do not authorize production runtime changes.

## Latest checkpoint — 2026-11-06 (owner-reported read-only terminal output)

**Host:** New dedicated `ccpcerp-prod`, LAN `192.168.50.186`, account `ccpcadmin`. Historic host provisioning documented in [PRODUCTION-HOST-SETUP-HANDOFF.md](PRODUCTION-HOST-SETUP-HANDOFF.md). Windows SSH uses an owner-held Ed25519 key; do not request or copy private key material. Earlier reported `hostnamectl --static` = `ccpcerp-prod`, Docker context = `default`; this conversation's inspected Docker endpoint was `unix:///var/run/docker.sock` per prior guarded-run status, not independent proof of immutable daemon identity.

**Docker and permissions:** Docker Compose reports `5.6.1`; `sudo systemctl is-active docker` returned `active`. Socket `/var/run/docker.sock` was `root:docker` with mode `srw-rw----`; `ccpcadmin` is in `adm cdrom sudo dip plugdev lxd`, **not** `docker`. Unprivileged inventory failed with `permission denied`; later *explicit owner-performed* read-only `sudo docker ps`, `sudo docker ps -a`, and `sudo docker system df -v` succeeded and showed **zero running/stopped containers, zero Docker images, zero Docker local volumes, and 0 B build cache**. This is **consistent with the brand-new host**, not evidence of deleted ERPNext data. Docker network inventory, actual firewall behavior and effective Compose model have **not** been verified in this checkpoint. Do not change Docker socket mode/groups/ACLs merely for convenience; Docker access is effectively root-level.

**Host Git checkouts (owner-reported):**

| Location | Branch | HEAD (short) | Git state | Remote |
|---|---|---|---|---|
| `/home/ccpcadmin/ccpc-frappe-deployment` | `security/dedicated-production-pre-tls-2026-10-23` | `0bf8c6a` | clean (`git status --short` empty) | `git@github.com:ccpcerp/ccpc-frappe-deployment.git` |
| `/home/ccpcadmin/ccpc-pr29-review` | `security/dedicated-prod-external-env-2026-10-23` | `bd92ade` | clean (`git status --short` empty) | same |

Both checked-out commits matched the GitHub PR branch tips on 2026-11-06. The first checkout tracks `compose.yaml`, `overrides/compose.dedicated-pre-tls.yaml`, `images/production/Containerfile`, and the dedicated port-profile document. The second additionally tracks `docs/04-operations/dedicated-production-external-credentials.md`. **Preserve both checkouts; no blind pull, switch, clean, reset or overwrite.**

**Connected GitHub PR status (2026-11-06):** [PR #27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27) pre-TLS `0bf8c6a`, [PR #29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29) external credentials `bd92ade`, [PR #30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) backup safety `fd751ab` are **OPEN/DRAFT/UNMERGED**, stacked in that order. These are **review candidates**, not approved deployed releases. Later dedicated Compose identity/environment reviews also exist; see [Step 144 inventory record](DEDICATED-PROD-STEP144-READONLY-HOST-INVENTORY-2026-10-25.md) and verify the right final reviewed source revision before use. The app's feature/review branches must also be reverified at release selection; never assume `version-16` includes all reviewed functionality.

## GitHub-only source review — 2026-11-06 (no host execution)

**Owner approval:** Continue non-live preparation and preserve a dedicated production record. Review executed through connected GitHub only; no PR merge, SSH session, credential provision, Compose execution, image build, container start, database operation or production modification.

**Verified review ancestry:** GitHub compare shows PR #29 is 10 commits ahead/0 behind PR #27; PR #30 is 27 ahead/0 behind PR #29; `review/dedicated-host-readonly-inventory-2026-10-25` (`c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` at this review) is 20 ahead/0 behind PR #30. The latter contains later Compose project/credential-selector guards and the read-only host inventory helper, **but is still a review branch and not a final approved production release**. The existing on-host directories are behind these later draft protections; preserve them rather than pulling automatically.

**Candidate source inspection:** On the later review branch, `scripts/config.sh` blob `32614da1044c768bd67dcb9b9491e7c48ff2653a` defines five Compose inputs for `dedicated-pre-tls`, adding `overrides/compose.dedicated-pre-tls.yaml` last. The override blob `14fd89a3c2371104f464964137483de9f4a35861` replaces frontend publication with `127.0.0.1:8080:8080/tcp`, requires nonempty `DB_PASSWORD`, and declares explicit backend sites/logs mounts. The revised Docker module blob `a99bcdb2077f55f5ded118159ad72a90d0a9fd7e` requires the dedicated env file (external, 0600, owner-only parent 0700, one `DB_PASSWORD` key), rejects ambient Compose project/file/profile selection, verifies local default Docker context/socket, and passes the **candidate-only** `--project-name ccpc_prod_erpnext`. These are **source-level findings, not a real `docker compose config` validation**.

**Material pinning gap:** `scripts/config.sh` still pins `CCPC_REF=release-2026-09-16` with `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`; later October/November business application review work exists. **Do not equate this pinned older app revision with the current proposed day-one financial/billing release** or automatically change it to the moving `version-16` tip. Independently select and approve exact app source, Frappe/ERPNext compatibility, image provenance, unresolved permissions/SoD issues, and migrations before any release build.

**No-runtime-render gap:** All five-file Compose inputs still need an exact-source, secret-safe `docker compose config --quiet` validation in an authorized environment, followed by sanitized verification of service/port/mount metadata, Compose project identity, expected volumes and unknown environment-selector behavior. Avoid full config dumps that interpolate credentials. Docker zero-resource inventory reduces name-collision uncertainty only at the time observed; it is not authorization to allocate volumes or start services.

**Next decisive action:** Review the specific app candidate release SHA and unresolved blockers alongside the stacked dedicated Compose review branch; produce a single pinned candidate and a safely executable, credential-free or synthetic Compose-validation plan. The on-host checkouts and old PRODUCTION remain untouched. Real secret provisioning, host checkout updates, image build, starting containers, backups/restores, migration and cutover each retain their respective explicit approval gates.

## Permanent data and release boundaries

- **Migration authority:** Owner approved the **existing old PRODUCTION site/database** on `ccpcerpserver` (internal site `ccpcerp.local`) as the starting source of business records. That approval selects a source; it does **not** permit live data export/transfer/restore or site migration.
- **No DEV substitution:** `development.localhost` and disposable integration sites are test environments, not business migration sources. Do not initialize new live business data independently and later overwrite or splice it into the old source.
- **Protect old operations:** Keep old production serving users unchanged until a separately authorized, backed-up, tested cutover. During final authorized cutover, fence old writes before final sync to prevent split-brain; verify transaction reconciliation and rollback plans.
- **Backup and recovery:** Future migration requires a complete, consistent **database, site configuration, public files, and private files** set; safe handling of secrets; verified integrity and isolated restore; version/schema compatibility; Company, COA, inventory, GL, users/roles, documents and attachments validation. The dedicated NAS share `ccpcerp-prod_backups` has historical SMB smoke-test evidence, **not** evidence of a successful four-artifact production backup or restore.
- **Production safety:** No restart, Compose `up/down`, database migration/restore, material changes, DNS/TLS cutover, backup deletion/retention change or Docker cleanup without separately scoped explicit approval. No accidental use of legacy deployment environment or secrets.

## Reviewed candidate design (not current running state)

- The pre-TLS profile is intended to publish frontend HTTP on **`127.0.0.1:8080` only**, with no MariaDB/Redis host ports; employee-facing `https://ccpcerp.com` on LAN TCP 443 requires a separate validated gateway, certificate trust, WebSocket/Host headers and firewall rules. Refer to [dedicated port profile](../04-operations/dedicated-production-port-profile.md) on the relevant branch.
- The external-credentials draft proposes a **0600**, user-owned, non-symlink env file outside Git checkout, in a **0700** owner-only directory, passed via `CCPC_DEDICATED_ENV_FILE`; never use checkout `.env` for dedicated database secrets. Do not print interpolated `docker compose config` in chat or logs.
- Candidate dedicated Compose project `ccpc_prod_erpnext` and volume names are **unapproved proposals**, not an observed deployed namespace; check selector/env guards and name collisions before any deployment.
- The dedicated backup-safety PR is still a draft. Signed release/source pin, backup identity, recovery, and approval controls require review and execution evidence rather than relying on offline mock tests alone.

## Approved work versus gated work

**Approved on 2026-11-06:** Prepare the dedicated **non-live release candidate**, including GitHub documentation, inspection/review of exact candidate source, and planning the separate credential provisioning and configuration validation. This approval **does not** cover provisioning actual passwords without a controlled procedure, changing SSH/Docker access rights, starting containers, old production backup execution, restoring or migrating any database, switching DNS/TLS traffic, merging draft PRs, or go-live.

**Immediate engineering next action:** Compare the stacked dedicated release candidate (PRs #27/#29/#30 plus later reviewed Compose/identity guards) against the available on-host checkout revisions, identify a single **source-pinned non-live configuration** and a no-secrets `docker compose config --quiet` validation plan. Do GitHub-only source review first; use a separately reviewed checkout or exact pinned commit rather than mutating the two existing checkouts. For any host-side change or real credential setup, present the exact command and seek the necessary scoped approval once.

**Release gates, in order:**

1. Freeze reviewed app + deployment source SHAs, Compose project/overrides, dependencies, and image provenance; resolve draft PR dependencies and unresolved security defects.
2. Independently validate effective Compose project/services/ports/volumes, no remote daemon and no namespace collision in a safe environment; keep 8080 loopback-only prior to HTTPS gateway.
3. Explicitly approve and provision segregated production credentials **outside Git**, with secret backup/rotation and failure recovery; never copy from DEVELOPMENT.
4. Approve and instantiate a **non-live** isolated stack only after volumes, image/version and rollback are reviewed. Validate service and data recovery behavior without live employee transactions.
5. Separately approve source production backup/export, transfer and isolated new-host restoration of the **old production** four-artifact backup. Prove files, data, schema, permissions and reconciled reports.
6. Verify independent NAS backup, restore rehearsal, TLS trust/redirect/WebSocket, LAN segmentation, role/SoD and accounting acceptance, maintenance-window and rollback/runbook.
7. Obtain explicit go-live/cutover approval; fence old writes, make final consistent copy, reconcile, switch access deliberately, observe and retain old recovery assets until separately approved retirement.

## Next-conversation quick start

**Do not repeat** Docker installation, empty-container diagnostics, home directory discovery, or Git checkout identification unless host state actually changed. Start by reading this record, the current workflow and the latest active handoff; compare GitHub draft PR heads/current reviews, then continue the immediate engineering next action above. If the host changes, record exact date, operator-run read-only evidence, affected host, result and new next action. Clearly label historical facts, new observations and unverified assumptions.

**No production deployment or migration occurred in this documentation milestone.**
