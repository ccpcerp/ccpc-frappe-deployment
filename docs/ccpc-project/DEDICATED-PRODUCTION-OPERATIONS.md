# CCPC ERPNext — Dedicated PRODUCTION Operations and Deployment Record

## CURRENT DECISION — 2026-11-06: migrate **only existing live PRODUCTION**, unchanged in functionality

**Owner-directed scope change (supersedes the earlier candidate app PR #33 release path and this document's prior 'accounting acceptance first' recommendation):** Relocate the **already running live production** from the shared legacy Ubuntu host `ccpcerpserver` to the new physically dedicated `ccpcerp-prod`, without promoting unfinished DEVELOPMENT features. The application, version, database and business configuration source of truth is the **actual active legacy PRODUCTION deployment**, not DEVELOPMENT Git state and not a future release candidate. The old host's DEVELOPMENT installation remains untouched and continues independently.

**Decision is approved as migration direction and planning scope; production-impacting execution remains separately gated.** Do not interpret the owner's proposal as blanket approval for new-host container creation, exporting/copying the live database, taking new production backups, secrets handling, restoration, migrations, DNS cutover, stopping legacy services or retiring the old production instance. Obtain exact scoped approval for each consequential phase after presenting a verified plan.

**What must be included:** same live ERPNext/Frappe/installed CCPC application code and metadata (verify running image identity, app revisions, patches and versions), all existing PRODUCTION Companies, Chart of Accounts, inventory/Stock Ledger, GL, users/roles/User Permissions, business documents and configuration; **all four Frappe backup artifacts** — database, site configuration, public files and private files — plus independently handled environment secrets, integration config and recovery prerequisites. Keep the Frappe site identity `ccpcerp.local` unless a later separately approved compatibility plan requires otherwise.

**What must NOT be included:** any changes existing only in `development.localhost`, disposable CI/integration sites, unmerged review/feature branches, PR #33's unfinished billing roles/policies, DEV test records, DEV database or DEV credentials. The custom app Git `version-16` HEAD or `release-2026-09-16` pin alone is **not proof** of what currently runs on old production; exact live image/application version must be observed and preserved or reproducibly matched. Do not introduce a newer app release, unapproved DocTypes, database patches, workflows, role grants, or business rules as part of this infrastructure migration.

**Infrastructure compatibility is separate from changing business functionality:** The new host still requires independently protected credentials, Docker/Compose networking, appropriate image availability, volumes, NAS backup, TLS/firewall and restore testing. Those safe host-specific changes may be needed to run the same application, but must be reviewed for unwanted app or data/schema changes. An accidental version mismatch or automatic `bench migrate` could change schema/business behavior; exclude it until independently justified and approved.

### Migration sequence / safety gates

1. **Read-only old-host baseline first:** verify `ccpcerpserver` host identity; current legacy production containers, Compose project, image tags/IDs, installed app and Frappe/ERPNext versions and Git SHAs (including dirty changes), database/site identity, declared volumes, existing backup job and NAS path — without printing secrets or modifying any container. Separate production facts from development data. On the new host, already-verified empty Docker inventory and two clean historical checkouts need not be repeated unless changed.
2. **Freeze exact production-source identity:** choose an immutable, verifiable copy of the *live* app image or a byte-equivalent reproducible build from precisely matched commits and tracked overlays, supported by backups and checksums. Do not use the candidate `1bde04b` billing app or `c12d46f` dedicated review stack as a substitute for live-app identity; the latter may supply **reviewed infrastructure safeguards only** after checking for compatibility.
3. **Approved full recovery point:** produce a new, consistent legacy production four-artifact backup; independently verify files and off-host NAS, preserve an unaffected recovery point, and capture an approved operational settings/credential re-provisioning inventory. Confirm that backup creation alone is not restore proof.
4. **Isolated new-host rehearsal:** on a separately authorized non-live stack, restore old production data and verify documents/attachments, company books, stock/GL totals, permissions, version compatibility and migration behavior. During testing, prevent duplicate scheduled jobs, background workers, email, external integrations, payment/accounting writes and network access to employees; do not let a restored copy and old production both process business events. Do not make the new copy live before validation.
5. **Separate planned cutover:** approved downtime/maintenance window; quiesce/fence writes and background processing on old PRODUCTION; make a **fresh final consistent backup/sync** (not the earlier rehearsal copy); verify checksums, restore and reconciliation; separately approve and configure LAN DNS/TLS/endpoints and start only the new production instance. Ensure no split-brain/simultaneous write access.
6. **Post-cutover:** validate representative real production records, GL/SLE balances, attachments, login, workers, scheduler, integrations and new NAS scheduled backups; retain old production isolated and recoverable until explicit approval of retirement. Define rollback triggers and data reconciliation before any cutover.

**Immediate next operator step (read-only on OLD host only, not on new `ccpcerp-prod`):** Once in the trusted `gani@ccpcerpserver` session, execute:

```bash
hostnamectl --static
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

If hostname differs from `ccpcerpserver`, stop. Output lists container metadata only; **no secrets, volume contents or Frappe data**. This establishes exactly which production image/tag and relevant containers currently run before requesting any backup or restoration actions. Record the date, source host and operator output. Do not stop/restart any container.

**Historical sections below remain as review evidence only:** Previous proposals to deploy PR #33 and resolve its incomplete Finance billing functionality **before** migrating are **superseded for this live-only move**, though still valid for a later independent DEVELOPMENT-to-PRODUCTION release after successful migration. Ignore old 'next step' wording where it conflicts with this current decision.

---

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

## Source-pinned candidate selection and Compose validation plan — 2026-11-06

**Outcome:** Identified a **provisional application candidate and provisional deployment-review baseline**, not a buildable/approved release pair. All findings are from connected GitHub; zero server or Compose execution.

### Candidate sources verified

| Part | Provisional source reference | Verified state | Disposition |
|---|---|---|---|
| Application baseline | `ccpcerp/ccpcerp` `version-16` @ `cfcc19394a6646548f2b7050db040c8cf5ebafde` | Older base; 585 commits behind the billing review head (GitHub compare) | **Not sufficient for latest day-one billing behavior** |
| Application candidate | `ccpcerp/ccpcerp` `review/billing-authorization-correction-2026-11-03` @ `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` | PR #33 OPEN/DRAFT/unmerged; GitHub combined commit status SUCCESS with `python-syntax`, `billing-controls-manual-approval`, `billing-controls-isolated-integration` | **Pin for review only**; not live-accepted or production approved |
| Deployment baseline | `ccpcerp/ccpc-frappe-deployment` `review/dedicated-host-readonly-inventory-2026-10-25` @ `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` | Descends from PRs #27/#29/#30; includes reviewed project-name and local Docker checks | **Pin for source review only**; not merged or production approved |
| Frappe / ERPNext | `FRAPPE_REF=v16.33.1` and `ERPNEXT_REF=v16.34.2` in deployment `scripts/config.sh` | Corresponding SHAs and ERPNext patch/overlay hashes are frozen in that file | **Compatibility and image build still unverified** |

**Critical alignment issue:** The pinned deployment `scripts/config.sh` and `apps.json` still reference `CCPC_REF=release-2026-09-16`, `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`, and `apps.json` branch `release-2026-09-16`. The image Containerfile explicitly checks the cloned application's actual `HEAD` against `EXPECTED_CCPC_SHA`; therefore **changing only the expected SHA fails unless the Git fetch ref also retrieves that exact revision**. An approved release must introduce an immutable reachable app ref (or deliberate supported exact-SHA checkout design), update `CCPC_REF`, `CCPC_SHA` and `apps.json` coherently on a **new reviewed deployment branch**, then validate private Git fetch, image build, framework/ERPNext version compatibility, and installed app behavior. Do **not** change the existing two server checkouts, copy draft code straight into live production, or substitute a moving branch/ref as an immutable release pin.

**Business and acceptance blockers:** The three GitHub CI statuses establish bounded automated results, **not** persistent DEVELOPMENT named-Checker acceptance, solved Purchase Invoice Submit separation of duties, full authenticated HTTP/concurrency regression coverage, signed image release, or disaster recovery. Consult `CURRENT-HANDOFF-3.md` before asserting these gaps have closed. PR #33 remains draft and requires business/security review before release approval.

### Source-pinned safe Compose validation — plan only

1. Start with an **isolated scratch/lab checkout** of the exact reviewed deployment commit `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`; preserve existing production host checkouts. Check blob fingerprints and verify all five Compose files in this exact order: `compose.yaml`, `overrides/compose.mariadb.yaml`, `overrides/compose.redis.yaml`, `overrides/compose.lan-production.yaml`, `overrides/compose.dedicated-pre-tls.yaml`.
2. First use credential-free static/offline tests and Bash syntax checks. The final override must replace `frontend.ports` to `127.0.0.1:8080:8080/tcp`; there should be no published MariaDB/Redis host ports. Review YAML `!override` semantics with real Compose 5.6.1 or an approved known-compatible Compose v2 lab CLI, not a generic YAML parser alone.
3. For a later **explicitly authorized isolated Compose render**, supply **synthetic test-only** `DB_PASSWORD` via an ephemeral protected 0600 external file in an owner-controlled 0700 directory, **not** via checkout `.env` or real production secrets. Use `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` and reviewed explicit image name/tag. Run only non-deploying `docker compose ... config --quiet` with the pinned five-file configuration and project selector in the authorized lab. Do **not** print full `config` output, because it can expose interpolated secrets. Preserve the security wrapper's environment guards; do not misrepresent a raw `docker compose` invocation as equivalent to the protected wrapper.
4. Validate sanitized expected service set (`configurator`, `backend`, `frontend`, `websocket`, `queue-short`, `queue-long`, `scheduler`, `db`, `redis-cache`, `redis-queue`), candidate Compose project identity `ccpc_prod_erpnext`, loopback-only frontend port, named `sites`/`db-data`/`logs` volumes, and no unexpected external/bind mounts or ambient Compose selectors. Any mismatch is a **stop**.
5. Only after a successful isolated render, obtain separate approval for on-host checkout preparation and any real credential creation, then for image build/containers. Before a restore or employee cutover, separately verify old-production consistent backup, isolated restore, schema, security, ledger, TLS, and rollback.

**Next implementation decision:** Complete focused code and acceptance review for app PR #33 and the inherited deployment guards; specify the exact app immutable release ref and a coherent `apps.json` / `config.sh` change on a fresh **review branch**. Do not merge PRs, create host secrets or run `compose up` based on this plan. The user approved GitHub-only preparation; business-policy changes, merges, persistent DEV actions and any production-impacting operation still require separate scoped approval.

## Owner-delegated next-step selection — 2026-11-06

**Decision:** Prioritize the **existing app PR #33 accounting authorization acceptance gate** ahead of image-source alignment, production image build or Compose execution. This is not a new authorization to change Company permissions, role assignments, DEVELOPMENT records, or any production resources.

**GitHub verified again on 2026-11-06:** app PR #33 remains OPEN/DRAFT at `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` against `feature/finance-mapping-lifecycle-2026-10-28`; current commit's combined status SUCCESS with `python-syntax`, `billing-controls-manual-approval` and `billing-controls-isolated-integration`. The reviewed `intercompany_billing_authority.py` explicitly denies Administrator/Guest, disabled users, Stockroom Personnel, absent literal role, and missing Company User Permission for either Company. It requires two different named Maker/Checker users. The controller also has row locking and protected billing state transitions, but no new live tests were executed here.

**Important unresolved distinction:** Application-level `require_billing_actor()` does not establish that ordinary **native Purchase Invoice Submit** permission is denied to every conflicted shared purchasing employee. GitHub's active handoff identifies this separation-of-duties overlap and persistent DEVELOPMENT named-Checker acceptance as unresolved. A CI pass is not proof that real site DocPerm/role memberships cannot bypass the workflow. Do not auto-assign the new roles, revoke other users, alter native PI DocPerm, or change business policy without a separate business/security decision.

**Chosen delivery sequence:** (1) Safely inspect protected DEVELOPMENT branch/status and obtain fresh post-Maker off-host backup under separate approval; (2) run targeted read-only role/Company scope/native PI Submit permission mapping and present the smallest effective policy choice; (3) perform explicitly authorized named Maker/Checker end-to-end acceptance on DEVELOPMENT, with rollback boundaries and test records documented; (4) only after resolution, create a coherent immutable app ref + `apps.json`/`config.sh` pin update on a fresh GitHub review branch, validate actual image and synthetic/isolated Compose render; (5) separately authorize non-live new-host instantiation, migration backup/restore, TLS, and finally cutover. Preserve existing old PRODUCTION unchanged throughout.

**Immediate external dependency:** A safeguarded DEVELOPMENT preflight and later actual acceptance require separate scoped authorization and operator-side access; the GitHub connector does not provide live SSH. No such host operation was performed by this documentation decision.

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
