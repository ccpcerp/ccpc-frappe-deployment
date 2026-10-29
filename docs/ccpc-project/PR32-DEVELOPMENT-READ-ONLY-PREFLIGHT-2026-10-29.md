# PR32 — DEVELOPMENT read-only preflight, operator evidence (2026-10-29)

**Status:** Seven read-only checks **PASS** as reported by the owner at `gani@ccpcerpserver`. **No Git checkout/pull, migration, new backup, backup restore, service restart, database writes, PR merge, PRODUCTION operation or paid CI run were authorized or executed in this preflight.** User-provided terminal outputs in the active conversation are the evidence, not machine access by ChatGPT. Continue one safe verified step at a time.

## Authority / target

- The owner explicitly approved **read-only DEVELOPMENT preflight only** after [draft PR32](https://github.com/ccpcerp/ccpcerp/pull/32) completed CircleCI Build #52 86/86 PASS on synthetic disposable MariaDB site.
- Intended incoming **GitHub** app branch: `review/four-day-one-reports-integration-2026-10-29`, tested full SHA **`061e65710eb4b527fc8ac579aaab8ccad4dd131d`**, **DRAFT/UNMERGED**, based on Finance commit `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`.
- Shared **actual DEVELOPMENT checkout**, last verified by operator: `/workspace/development/frappe-bench/apps/ccpcerp`; **detached HEAD**, full commit **`0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`**; `git status --porcelain=v1 --untracked-files=all` reports **only `?? AGENTS.md`** (no modified tracked files). **Preserve this untracked file; do not clean, stash, reset or overwrite.**
- Both intended DEVELOPMENT site config files exist: `development.localhost` and `ccpc-integration2.localhost`; each refers to a different configured database name, without printing names or passwords. Site-file separation **does not prove host-level resource isolation**. Known incomplete site `ccpc-integration.localhost` is excluded.

## Seven operator-confirmed read-only checks

| Gate | Direct owner output / interpretation |
|---|---|
| 1. Git checkout/worktree | Path above; blank current branch means detached HEAD; exact `0c223d7...`; only untracked `AGENTS.md`. **PASS**, but cannot assume incoming PR already installed. |
| 2. Site configs | Both config files found and database names distinct. **PASS**. |
| 3. Protected backup inventory | Both site's expected **October 27 four-component sets** found and nonzero. **PASS**. |
| 4. Live installed-app enumeration | Both sites reported `frappe 16.33.1 version-16`, `erpnext 16.34.2 version-16`, `ccpcerp 0.0.1 HEAD`. **PASS**; shared detached application HEAD remains `0c223d7...`. |
| 5. Recorded CCPC patches | On each site, **8 declared / 8 Patch Log records / 0 declared unrecorded**. **PASS** for recorded status, not independent patch result integrity. |
| 6. Finance schema | On each site, **four/four mapping DocTypes, two/two mapping Roles, five/five Stock Entry Detail provenance custom fields**. **PASS** for existence, not business configuration, users, accounting postings or role-level access. |
| 7. Backup archive integrity | On both sites, `gzip -t` database, `tar -tf` public/private files and `python3 -m json.tool` site config all **PASS**. **Archive readability only**; NOT full recovery, consistency or freshness. |

### Protected October 27 recovery file metadata from operator

| Site | Original database gzip | Site config backup | Public archive | Private archive |
|---|---:|---:|---:|---:|
| `development.localhost` | 1,652,142 bytes | 234 bytes | 10,240 bytes | 20,480 bytes |
| `ccpc-integration2.localhost` | 1,079,342 bytes | 212 bytes | 10,240 bytes | 10,240 bytes |

- All four of **main site's** files modified **2026-10-27 02:24:22 UTC**; all four of **integration2 site's** files modified **2026-10-27 02:48:02 UTC**. More current changes may exist. No current recovery point or off-host backup verification yet. Archive read checks were safe and left original backups in place.
- The initial patch log inspection emitted two **nonfatal `sys.prefix` / `sys.exec_prefix` path normalization warnings** because the invocation used `sites/../env/bin/python`; both database checks completed with 8/8/0 output. Subsequent commands should use canonical absolute venv interpreter path.

## Pending gates, strict boundaries

1. **NEXT READ-ONLY operator check:** validate the **four exact Companies and 5 intercompany Account structures per Company** against verified GitHub file `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` at PR32. Inspect actual Company abbreviation, Account number/name/company/parent/root/account type/is_group/disabled. Must print summary counts and field-name discrepancies only, no passwords/business values. A previously applied patch is insufficient proof that masters remain valid.
2. Then separately check internal Customer/Supplier party mappings and actual Company/Department/Cost Center/warehouse readiness and end-user data-access/role signoff, using bounded read-only reports without exposing private business records.
3. **Recoverability remains NO-GO** without verifying a current checkpoint, suitable off-host copy and an independent restore in a disposable, production-disconnected environment. Any creation/restoration, even on DEV, requires fresh scoped approval.
4. Shared DEVELOPMENT bench and host may also serve other sites and coexist with legacy production containers. Review actual `docker ps` / process and host resource scope read-only before any deployment.
5. A **controlled checkout/pull/migration and full real DEVELOPMENT acceptance are not authorized** by this preflight. App PR32 and original PRs remain DRAFT/UNMERGED. Never run CircleCI disposable test fixtures on persistent DEVELOPMENT, as their guards deliberately reject it.
6. **PRODUCTION NO-GO** absent explicit distinct approval, tested recovery, rollback and release signoff. No blanket deployment, additional CircleCI charges or automatic retries.

## References

- [Active handoff](CURRENT-HANDOFF-2.md)
- [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Prior DEVELOPMENT controlled integration plan](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md)
- [PR32 real MariaDB CI acceptance](FOUR-REPORTS-PR32-CIRCLECI52-REAL-MARIADB-ACCEPTANCE-2026-10-29.md)

## Step 8 — Company/account check: main PASS; synthetic Integration2 comparator was inapplicable

**Owner terminal output, 2026-10-29:** The Step 8 GitHub-derived patch checker `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` verified **4/4 actual Companies and 20/20 intercompany accounts** on `development.localhost`, including expected Company abbreviations and account parent/ledger attributes. **Main DEVELOPMENT: PASS**.

The **same check** on `ccpc-integration2.localhost` reported **0/4** expected real group-Company abbreviation matches and **0/20** accounts, followed by `RuntimeError: Master configuration requires review: ccpc-integration2.localhost`. **Interpretation correction:** The checker `continue`s before account lookups whenever a Company doesn't match, so `0/20` is **NOT evidence that the accounts are absent or invalid**; they were **not evaluated**. The check incorrectly assumed that this historically isolated test site used the four real CCPC group Companies.

**Existing GitHub design resolves the likely explanation without changing any database:** [DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md), milestones D13–D15 and D19, records Integration2 as **synthetic two-Company Finance test fixture**: `Integration Test Issuer` (`TISS`) and `Integration Test Requester` (`TREQ`), with **two** Companies historically confirmed at D14; TISS had 30 eligible Expense Accounts, one eligible Cost Center, 13 eligible leaf Departments and five leaf Item Groups. It also records completed dedicated maker/checker authorization tests. Thus **the production-like four-Company / 20-intercompany-account check is inappropriate for Integration2 and must not be used as an acceptance gate for that site's synthetic fixtures.**

**NEXT single read-only operator action:** On Integration2 only, count `tabCompany` rows, and verify the exact named/abbreviated TISS and TREQ records with bound SQL. Do not list unrelated Company names, secrets, accounts or financial entries. If both identities exist, classify Step 8 by site purpose: **main 4/4 + 20/20 PASS; Integration2 synthetic TISS/TREQ 2/2 PASS (separate criteria)**. If missing or changed, STOP and investigate; do not automatically create/rename Companies or rerun patches. Do not presume historical two-Company status is current without operator readback.

The user authorized **read-only preflight only**, not deployment or remediation. Existing October 27 protected backups remain non-restoration-tested and potentially stale. GitHub app PR32 stays DRAFT/UNMERGED; **no checkout/pull/migration/DB write, CircleCI repeat or PRODUCTION actions**.

## Step 9 — Synthetic Integration2 Company identity independently confirmed

**User terminal readback, 2026-10-29:** On `ccpc-integration2.localhost`, `SELECT COUNT(*) FROM tabCompany` = **2**; `Integration Test Issuer` correctly had abbreviation **TISS**; `Integration Test Requester` correctly had abbreviation **TREQ**. Terminal ended **`INTEGRATION2 SYNTHETIC COMPANIES: 2/2 PASS`**. No DB writes. This **resolves the previous Step 8 apparent mismatch by design**, without creating/renaming four real CCPC Companies on Integration2. Main `development.localhost` retains **4/4 real Companies and 20/20 real intercompany Accounts PASS**. These are different valid Company check criteria for different site purposes.

**Next separate read-only gate:** Check **main DEVELOPMENT only** for four real intercompany `Customer` and four real internal `Supplier` identities and correct represented Company, non-disabled internal party, group/type/territory against `ccpcerp/patches/v1_0/create_intercompany_parties.py`. The patch content at installed DEVELOPMENT commit `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and at tested PR32 `061e65710eb4b527fc8ac579aaab8ccad4dd131d` is **the exact same GitHub blob SHA `96990516b4270709bc991e4b32fa9e8311fa6bea`**, so no ambiguity about definitions. This first check can verify party headers; separate following gate should verify **party allowed-companies rows and per-counterparty receivable/payable account mapping**, duplicates and no self-transaction. This is not a reason to require 4 group-Company parties on synthetic Integration2.

**No deployment yet:** Retain read-only scope, protected untracked `AGENTS.md`, shared DEVELOPMENT bench and October 27 backups. Restore/off-host and current checkpoint not yet proven. PR32 draft/unmerged. PRODUCTION NO-GO.

## Step 10 — Main DEVELOPMENT internal Customer and Supplier identity PASS

**User-reported actual read-only terminal result, 2026-10-29:** For **main `development.localhost` only**, the GitHub-defined four real Companies each passed individual **Customer and Supplier** internal party header validation: `Customer CCPC PASS; Supplier CCPC PASS; Customer RMC PASS; Supplier RMC PASS; Customer GSL PASS; Supplier GSL PASS; Customer WFC PASS; Supplier WFC PASS`. Summary **`Internal Customers: 4/4`** and **`Internal Suppliers: 4/4`** with `MAIN DEVELOPMENT INTERCOMPANY PARTY IDENTITIES: PASS`. The test queried bounded identity records and checked exact represented Company, internal-party flag, enabled/non-disabled flag, Company type, Intercompany group and Philippine territory for Customers. It did **not** enumerate the party's `companies` allowed-to-transact child entries or `accounts` per-transacting-company Account records, so no conclusion yet about those eight parties' **24 expected allowed-company rows and 24 expected account mapping rows**.

**Important site boundary:** Synthetic Integration2 keeps TISS/TREQ 2/2 PASS; do **not** require real CCPC group Company/party records on that test site. Main DEV still has 4/4 real Companies and 20/20 account master validation PASS.

**NEXT (read-only):** Main DEV only, for each of 4 represented Companies' internal Customer and Supplier, verify each has the **three other** represented Companies as allowed transacting companies (no duplicates, missing/extra or own Company), and exactly three account mappings (one for each other transacting Company) to the expected `1312 - Intercompany Receivable - <transacting abbr>` (Customer) or `2121 - Intercompany Payable - <transacting abbr>` (Supplier), with actual Account Company/Type/leaf/disabled metadata validated. The incoming and installed code use the **same blob** of `ccpcerp/patches/v1_0/create_intercompany_parties.py` from verified GitHub `96990516b4270709bc991e4b32fa9e8311fa6bea`. Strict 'exactly three' is a safety review and may flag extra existing rows that the original patch did not remove; never auto-clean or write to resolve. No password/data dumps, no SQL updates, no migrations, no release authorization.

**Other open gates:** independent restore, current pre-deployment backup/off-host protection, host sharing, live role and financial postings. PRODUCTION remains NO-GO.

## Step 11 — Exact four-Company intercompany allowed-company and account child rows PASS

**2026-10-29, owner-run read-only terminal evidence, main `development.localhost` only:** The command first guarded the exact installed app Git HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and expected working tree `?? AGENTS.md` before reading party child rows. For each of the four represented group Companies, both internal Customer and Supplier passed:

- Customer CCPC, Supplier CCPC: allowed 3/3 and accounts 3/3 each — PASS.
- Customer RMC, Supplier RMC: allowed 3/3 and accounts 3/3 each — PASS.
- Customer GSL, Supplier GSL: allowed 3/3 and accounts 3/3 each — PASS.
- Customer WFC, Supplier WFC: allowed 3/3 and accounts 3/3 each — PASS.

**Aggregate operator output:** `Party configurations: 8/8`; `Allowed-company coverage: 24/24`; `Valid account mappings: 24/24`; **`INTERCOMPANY PARTY CHILD MAPPINGS: PASS`**. This enforced for each party exactly three unique allowed *other* Companies (no self, missing, duplicates, extras) and exactly three Company-unique matching account rows; account identifiers, owning Company, receivable/payable Account Type, enabled state and ledger vs group status were validated against the known patch.

**Scope:** This confirms **structural read-only accounting master data** for the **main DEVELOPMENT site**, not real intercompany invoice posting, SLE/GL integrity, real user permission or returns/reversal. The Integration2 test site is deliberately synthetic `TISS/TREQ`; no real-group intercompany party criteria should be imposed there. No DB or Git changes, migration, new backup, service restart or production actions were executed.

**Next practical blocker toward reviewed PR32 integration:** Reinspect current **shared host Docker/Compose service scope read-only**, distinguishing DEV containers, legacy PRODUCTION containers and common services/ports; do not stop/recreate, inspect secrets or change Compose. Assess the **October 27 backup freshness and independent restore/off-host recovery** before separately proposing a current, scoped DEV-only backup or checkout. No deployment, backup creation or restore authorized by read-only preflight. The PR32 branch remains draft/unmerged; all 86/86 CircleCI disposable tests green but not real persistent DEVELOPMENT user/Company acceptance. **PRODUCTION NO-GO.**

## Step 12 — Operator's current Docker Compose/container inventory: two projects coexist on one host (2026-10-29)

**User read-only terminal evidence, host `ccpcerpserver`, Docker context `default`:**

- Compose project `frappe_docker`: `exited(1), running(9)`. Production config files under `/home/gani/deployments/frappe_docker/` include the main Compose YAML, LAN production, MariaDB, Redis, noproxy overrides. Nine running `frappe_docker-*` containers: `frontend`, `backend`, `queue-short`, `queue-long`, `websocket`, `scheduler`, `redis-cache`, `redis-queue`, `db`. DB reported **healthy**. `frontend` publishes host TCP **0.0.0.0:80 / [::]:80 → container 8080**. One additional exited Compose container was **not named by this command**; earlier documentation expected one-time configurator, but do not infer current identity/health without `docker ps -a`.
- Compose project `frappe_docker_devcontainer`: **running(4)**, config via `/home/gani/deployments/frappe_docker/.devcontainer/docker-compose.yml` plus two generated `/tmp/devcontainercli-gani/...` feature override files. Four running `frappe_docker_devcontainer-*` containers: `frappe`, `redis-cache`, `redis-queue`, `mariadb`. DEV Frappe publishes **127.0.0.1:8000-8005 and 127.0.0.1:9000-9005**, not a wildcard host bind. Redis ports and MariaDB 3306 shown as container-private. All reported **Up 2 weeks**.
- The operator ran `hostname -s`, `docker context show`, `docker compose ls --all`, and `docker ps --format ...`. **No mutation** occurred. Current evidence confirms separate Compose **namespaces**, distinct container naming and apparent service sets, **not yet** distinct Docker network membership, bind mounts/volumes, host processes, underlying host risk, restored backups or resource isolation. Both projects coexist on **the same physical host**, so careless Compose `down`, restart, network/volume prune, or host-level operations are unsafe.
- The one exited production project container does **not** establish production failure; it must be inspected read-only only if relevant; documentation historically identified a one-time `configurator` container that exits normally.

**Next single read-only preflight:** Enumerate Docker mount sources and network names for containers in these **two exact Compose projects**, detect any **identical mount source** or **shared Docker network** across projects; print only relevant mount/network metadata and no `Config.Env`, secrets, passwords or database contents. If overlaps exist, inspect scope before approving any change. Otherwise continue toward a **separately authorized current DEVELOPMENT-only backup with off-host and restore-readiness plan**, then separately authorize controlled PR32 integration and genuine site acceptance. All October 27 protected snapshots remain untouched; archive checks did NOT prove restoration. The current read-only preflight approval does not authorize backup creation, pull, checkout, migration, restart, merge or deployment; **PRODUCTION NO-GO**.

## GitHub history rechecked — avoid repeated full Docker investigation (2026-10-29)

**Owner raised duplication concern after Step 12**: "Can you check it in GitHub I think we did this kind of investigation several times already". GitHub review confirmed earlier repeated documentation, so **do NOT request another full host Docker exploration as a default next step.** Sources:

- [DOCKER-DEV-PROD-ARCHITECTURE.md](DOCKER-DEV-PROD-ARCHITECTURE.md) explicitly records shared Ubuntu host+Docker daemon, distinct DEV and legacy PRODUCTION Compose projects, DEV RW `/workspace` source bind and separate MariaDB/Redis, PROD named `sites`, `db-data`, `redis-queue-data` volumes in tracked Compose; DEV ports `127.0.0.1` were previously directly audited. Old P20 audit found an **actually readable SSH-directory bind mount** in the existing DEV container, and the unused auto-Codex publisher remains disabled. See [P20-HANDOFF-2026-10-10.md](P20-HANDOFF-2026-10-10.md).
- Tracked `devcontainer-example/docker-compose.yml` declares `mariadb-data` and host workspace RW bind, but **active `.devcontainer/docker-compose.yml` is ignored** and actual running mounts can differ. PROD tracked `compose.yaml`, `overrides/compose.mariadb.yaml`, `overrides/compose.redis.yaml` declare independent named-volume keys. Compose naming conventions **do not prove zero live cross-project mount/network overlap**.
- The owner provided **fresh Step 12** `docker compose ls --all` / `docker ps` output showing both distinct projects, 9 running/1 exited PROD and 4 running DEV, distinct DB/Redis containers, PROD wildcard host TCP 80 and DEV host loopback ports. Thus project/service/port inventory is recently verified, not merely historical.
- **Open, bounded runtime fact:** An exhaustive current `docker inspect` mount/network cross-project comparison is NOT evidenced in the reviewed GitHub records. Avoid claiming full physical/storage/network isolation. This **can be deferred while merely planning**; if a proposed operation touches Docker, volumes, networks, host paths or container recreation, perform only the relevant narrow metadata verification in the *immediate execution preflight*, not a repetitive full audit. In contrast, a safe app-code-only operation in the shared DEV bind path may not require full resource enumeration, but does require exact worktree and site impact controls. No new commands were executed for this GitHub-side review.

**Decision:** Cancel the previously suggested blanket "Step 13" Docker network/mount inspection as the immediate next user request. Focus on **current DEV four-part recovery points** (October 27 copies are readable but may be stale), demonstrable off-host safety/isolated restore plan, preserved `AGENTS.md`, and a reviewed **exact-SHA, app-only** PR32 integration procedure with separate permission to implement. Neither backup creation nor code switch, site migration/restart, or PRODUCTION change is approved. Do not auto-run further CircleCI. After scoped backup/restore readiness, move toward genuine authenticated site-level four-report acceptance rather than another generic investigation loop.

## Next owner approval — guarded fresh DEVELOPMENT backup stage only (2026-10-29)

**Owner message:** "Approved" in reply to the proposed next sequence: establish current recoverable DEVELOPMENT backups, plan exact-SHA PR32 integration, then obtain **separate approval** for the actual DEVELOPMENT code update. Interpret this approval as **DEV recovery preparation/creation stage**, **not** a checkout, pull, DB migration, Honcho restart, merge, synthetic business-data write, fresh CircleCI run or PRODUCTION action.

**GitHub and Frappe source re-reviewed:** current installed DEV HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`, `?? AGENTS.md` protected; PR32 remains draft/unmerged HEAD `061e65710eb4b527fc8ac579aaab8ccad4dd131d` (86/86 disposable CI tests PASS). Frappe v16.33.1 pinned upstream `frappe/utils/backups.py` and `frappe/commands/site.py` were checked at commit `988e54f`. Although public Frappe documentation supports `bench --site X backup --with-files --backup-path PATH`, its CLI calls `scheduled_backup` → `new_backup` → **`delete_temp_backups()`**, which may **delete older files** from Frappe's standard per-site backup directory even when a custom target path is given. Avoid this silent retention side effect during preservation-oriented work.

**Reviewed safer approach for one operator-executed action at a time:** Use Frappe's pinned `BackupGenerator` directly (not `new_backup` / `scheduled_backup`), with `ignore_conf=True` for a **full unfiltered database backup**, `force=True`, `ignore_files=False`, site `ccpc-integration2.localhost` first as the synthetic, smaller DEV fixture; then the real four-Company `development.localhost` in a separately checked operator step. This avoids invoking default-backup-directory cleanup, and writes only four backup artifacts in a new `0700` directory **outside `sites/`**, under the DEV bench's separate `.ccpc-pr32-snapshots` folder. Guard exact Git HEAD, tracked/untracked worktree, site existence, historical four-part October 27 recovery files and available filesystem space. Do not print site config, SQL, attachments, credentials, connection arguments or backups in chat. Validate output file count, gzip/TAR/JSON integrity and hashes. A failed run must STOP without deleting prior snapshots. Confirm the Frappe site has no active backup encryption requirement before creating unencrypted files; if one exists, **STOP** for a security-safe design.

**Limits:** These are **same-host local snapshots**, not independently restored or off-host copies. Running Frappe site DB/files remain live, so dump/file capture is not guaranteed single-instant atomic for concurrent user writes. Before any actual checkout/migration, separately address suitable off-host retention, tested restoration / recovery plan, current two-site checkpoint (both sites), and distinct DEV deployment approval. No Docker lifecycle commands, no PRODUCTION changes.

## Backup Stage — Integration2 first fresh local recovery set: PASS (operator output 2026-10-29)

The owner executed the separately approved **Integration2-only** source-guarded `BackupGenerator` operation from the DEV `frappe_docker_devcontainer-frappe-1` container, with source checkout at `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and the preserved untracked `AGENTS.md`. **Actual owner-reported terminal output:**

```text
DEVELOPMENT SOURCE AND SPACE GUARDS: PASS
DATABASE BACKUP: PASS
SITE CONFIG BACKUP: PASS
PUBLIC FILES BACKUP: PASS
PRIVATE FILES BACKUP: PASS
BACKUP DIRECTORY: /workspace/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e
INTEGRATION2 FRESH BACKUP: PASS
```

**Proven scope:** New private local 0700 snapshot under the DEVELOPMENT bench **outside `sites/`**, targeting the fictional Integration2 site only, with four nonempty backup artifacts successfully opened/stream-read as gzip, JSON and TAR. Source/space guards passed, and encryption guard would have aborted if Frappe reported backup encryption enabled. The generator bypassed Frappe CLI's automatic `delete_temp_backups()` path. These are **reported execution results**, not independent container access. No evidence of a separate SHA256 checksum, off-host copy or successfully exercised independent restore yet; avoid overclaiming. The matched October 27 historical backups are still protected and were not intentionally touched, but their continued existence was not independently re-read in this run. Live database/files may change during backup.

**NEXT single operator action under existing approved recovery-only stage:** Create a separate four-artifact backup of **main `development.localhost`**, in a freshly named 0700 subdirectory alongside the completed Integration2 set (do not overwrite it). Guard exact Git HEAD and `?? AGENTS.md` plus presence of protected older snapshots and just-completed Integration2 directory; verify free space and full-unfiltered backup, open/stream-read all generated components without printing business data or credentials. Stop and investigate on any guard or integrity failure. Then assess off-host safety and independent restore method before proposing a separate reviewed PR32 DEVELOPMENT code pull/checkout/migration. No PRODUCTION changes, no code switch, no merge, no paid CI run.

## Backup Stage — Main DEVELOPMENT fresh local recovery set PASS; both protected (2026-10-29)

**Owner-reported exact terminal results:**
```text
SOURCE AND EXISTING BACKUP GUARDS: PASS
DATABASE BACKUP: PASS
SITE CONFIG BACKUP: PASS
PUBLIC FILES BACKUP: PASS
PRIVATE FILES BACKUP: PASS
BACKUP DIRECTORY: /workspace/development/frappe-bench/.ccpc-pr32-snapshots/development.localhost-20261029T134505Z-f9d195ea
MAIN DEVELOPMENT FRESH BACKUP: PASS
```

**Meaning:** The separate approved main `development.localhost` backup has four nonempty, readable components (complete gzip-stream, JSON parse, public/private TAR stream) under a new private snapshot directory; previous historical October 27 file sets and Integration2 snapshot presence passed guards. Both current protected backups are now locally present at distinct paths:

- Synthetic Integration2: `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e` (13:23:29 UTC).
- Main group Companies: `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/development.localhost-20261029T134505Z-f9d195ea` (13:45:05 UTC).

Each contains database, site-config, public and private files; both site backup encryption guards succeeded. This is a **same-host local 4-component backup**, not a verified transactionally consistent multi-component point-in-time snapshot, SHA256 manifests, off-host copy, or independent restored environment. No production changes, code switch, worker restart or DB migration executed in the owner-provided commands. App Git source/AGENTS.md still guarded at initial execution; must recheck before any future code action.

**NEXT:** No more repeat Docker separation investigations. To prepare an **off-host DEV-only protected copy** without touching the PRODUCTION backup workflow, verify the currently mounted legacy Synology share read-only before using it: `findmnt -rn -M /mnt/erpnext_backups -o SOURCE,FSTYPE` must return precisely the documented **`//192.168.50.132/erpnext_backups cifs`** and verify mountpoint, permissions/free space without reading share content. This is *current mount identity* verification, NOT generic infra re-audit. If incorrect/absent, stop (directory existence is insufficient). Design private DEV-only subfolder, permission/sensitive-data controls, separate approval for off-host data transfer if needed, checksum validation and later independent restore plan. Do not invoke legacy production backup script or alter existing NAS backups. PR32 remains draft/unmerged `061e65710eb4b527fc8ac579aaab8ccad4dd131d`; no app pull/checkout/migrate/merge, further CI or PRODUCTION action authorized.

## Off-host destination readiness — NAS mount identity and both source paths PASS (2026-10-29)

**User reported exactly**:
```text
NAS MOUNT IDENTITY: PASS
NAS ACCESS PERMISSIONS: PASS (no write attempted)
BOTH HOST-VISIBLE DEVELOPMENT SNAPSHOTS: PASS
NAS AVAILABLE SPACE:  1.5T
OFF-HOST BACKUP DESTINATION PREFLIGHT: PASS
```

**Interpretation:** On `ccpcerpserver`, `findmnt -rn -M /mnt/erpnext_backups -o SOURCE,FSTYPE` was guarded against exact expected `//192.168.50.132/erpnext_backups cifs`, verified mountpoint and host read/write access (not a write test); host can see the two expected fresh **October 29** source backup directories under `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots`. The NAS reported **1.5 TiB-ish available** via `df -h` display `1.5T`. **No copy yet**; this is a narrow current mount check rather than a Docker/infrastructure re-audit.

**NEXT operator action within owner's approved DEVELOPMENT backup stage:** Perform an **exclusive, non-overwriting DEV-only off-host copy** of the two *exact* local four-part snapshot directories into a new, randomly identified, hidden temporary directory under the verified NAS mount; verify source file exact counts/suffixes and nonzero sizes, source and destination SHA256 for all eight components, and best-effort restrictive on-mount directory/file modes **before exposing data**; create a `SHA256SUMS` manifest, then rename the staging directory to a unique `ccpc-development-pr32-...` directory. Never copy into/modify the legacy PRODUCTION backup tree, never delete local backups, never invoke the legacy production scheduled backup script or retention. If CIFS does not actually honor restrictive modes, **STOP before copy** and review Synology server-side SMB share and ACL protection. Linux `0700` metadata alone **does not independently establish server-side SMB ACL privacy**; treat that as a separate owner/administrator confirmation before sensitive backup content is considered secured. The destination is a NAS backup copy, *not* an isolated restore acceptance. No PR32 checkout, pull, migration, restart, release merge, additional CI or PRODUCTION action is approved.

## Off-host copy STOPPED safely at CIFS permission check — no backup content staged (2026-10-29)

**Owner terminal evidence following attempted DEV-only Synology transfer:**

- `find -mindepth 1 -maxdepth 1` listed **only** `.partial-ccpc-development-pr32-7895c72462f41cae`, and no completed `ccpc-development-pr32-*` final folder.
- Read-only metadata of that one staging directory: **POSIX mode `0o755`**, **0 top-level entries**, permission probe **ABSENT**, synthetic Integration2 folder **NOT STAGED**, main DEVELOPMENT folder **NOT STAGED**, `SHA256SUMS` **ABSENT**.
- This precisely matches the guarded copy script aborting **immediately after initial directory creation**: `partial.mkdir(mode=0o700)` had a CIFS-visible mode of `0755`, so `private(partial)` was false and `SystemExit` was raised before any permission test file or backup copy. No evidence that *any* secret-bearing snapshot data or manifest reached the NAS; only the empty uniquely named partial directory was created.
- Local site backups (Integration2 `...132329Z-99d6786e` and main `...134505Z-f9d195ea`) remain the accepted four-file **local** recovery sets; avoid describing either as off-host or restored. No Git checkout, DB write or production service operation executed.

**Decision: SECURITY STOP** on *any retry* or bypassing/chmodding the mode guard. The CIFS-mounted Linux `0755` view might be a synthetic client mapping and does **not prove** that actual Synology server-side SMB share/subfolder ACLs are public. Conversely, CLI mode or a `chmod` check alone cannot prove privacy. Next action is **Synology DSM administrator read-only permissions review** (shared-folder effective privileges for the NAS account, guest/everyone, existing backup admins, and applicability of ACL inheritance; if applicable a restricted DEV-only destination/share design), without copying business/credential files or changing PRODUCTION backup share permissions. No sharing account secrets or identities to chat. If permissions need alteration, seek separate explicit approval and review legacy PROD backup impacts. An alternative is a properly designed authenticated client-side encrypted off-host set with safely independent key custody and a restore test, also requiring reviewed design; never invent/manage a key in public GitHub or paste it into chat. Preserve empty partial directory until specific cleanup approval; no broad deletion of NAS files.

**NEXT:** single user action: in Synology DSM inspect `erpnext_backups` Shared Folder permissions and report **whether access is restricted to intended backup admin accounts and excludes Guest/Everyone**, without sharing confidential names, passwords or credentials. Only after that decision design the scoped transfer. PR32 remains draft/unmerged; **PRODUCTION NO-GO**.

## Legacy Synology access-control evidence rechecked in GitHub — distinct from dedicated new-host share (2026-10-29)

**Owner asked whether Synology access control was documented already, to avoid repeating prior reviews.** Reviewed current docs branch, complete 305-path tree, project recovery/architecture/context, and dedicated-host NAS design. **Finding: YES, scoped access was previously documented for the different `ccpcerp-prod_backups` share; NO conclusive current server-side SMB ACL/effective permissions for legacy `erpnext_backups` are recorded.**

- [DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md](DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md), §1: owner-reported Synology DSM SMB permission review for **new** share `//192.168.50.132/ccpcerp-prod_backups`; the dedicated account `ccpcerp_prod_backup` had user-only access to that intended share and explicit **No Access** to legacy `erpnext_backups` (and `docker`). This only proves that **one different account** was restricted from the legacy share; it does NOT prove blanket legacy-share guest/Everyone/general-user denial. Some `homes` permission on new account was shown as Default.
- [recovery.md](recovery.md) and [ccpc-project-context.md](ccpc-project-context.md): legacy `//192.168.50.132/erpnext_backups` is mounted via CIFS at `/mnt/erpnext_backups` with a root-owned local credentials file, previously verified source/type and read/write data operations. These records do **not** contain authoritative DSM shared-folder and subfolder ACL screenshots/results for legacy user/group access. Current user-confirmed host `findmnt` and NAS 1.5T also do not provide server-side ACL evidence.
- Live user diagnosis of empty `.partial-ccpc-development-pr32-7895c72462f41cae` showed **0755 client-visible directory mode**, no files copied. CIFS synthetic mode presentation neither establishes actual Synology effective permissions nor guarantees them.

**Narrow remaining check only, not a new general NAS investigation:** Review *existing* legacy `erpnext_backups` Synology DSM **Shared Folder permissions/effective read access** for Guest/Everyone/ordinary users versus intended backup administrators, including inheritance or per-folder restrictions if planning a dedicated DEV-only subfolder. Prefer existing documented DSM evidence if the owner can identify it; otherwise one read-only DSM review, without sharing account names or credentials, is necessary before retrying any unencrypted sensitive DEV off-host copy. Do NOT change share ACLs, reboot/reconfigure the NAS, rerun the transfer, delete partials, or affect legacy PRODUCTION backup scheduling without separate approval.

## Synology DSM legacy-share local-user permission screenshots reviewed (2026-10-30)

**Owner supplied four Synology DSM UI screenshots** from `Control Panel → Shared Folder → Edit erpnext_backups → Permissions`, selector **Local users**, scrolled across the displayed **39 items**. This is direct UI evidence for *legacy* `erpnext_backups`, correcting the earlier GitHub-only uncertainty (the previously documented *dedicated new-host* `ccpcerp-prod_backups` share is distinct).

**Observed effective "Preview" access in the screenshots:** `guest` = **No Access**; most displayed local users = **No Access**. **Four visible local-user entries** = **Read/Write** in Preview: two administrative-looking accounts, one named individual, and the backup-service account. The three non-backup rows show **Group Permission: Read/Write** (their explicit Read/Write checkbox is not ticked); the backup-service account shows an explicitly checked **Read/Write** user grant. Individual names are not reproduced in documentation to avoid unnecessary account disclosure. UI view proves what DSM reported on this screen; it does **not** establish all group memberships, whether other accounts or permissions are hidden, or a tested SMB session's effective file access.

**Current security decision:** Guest denial for the displayed local-users view is evidenced, but **legacy share cannot yet be classified as accessible exclusively to approved backup administrators**, because at least one individual receives group-derived Read/Write and the relevant Local groups/Everyone permissions have not been reviewed. `0755` on the CIFS client remains a separate presentation issue, not sufficient to infer NAS-side access. Do not automatically repeat or weaken the stopped copy command, apply chmod to production share, click DSM Save, alter group access, delete empty `.partial-ccpc-development-pr32-7895c72462f41cae`, or overwrite/probe business files.

**Next single, narrow read-only operator task:** With the same `erpnext_backups` DSM Edit Shared Folder dialog open, switch the **Permissions selector from Local users to Local groups** and review the effective Preview column, particularly **administrators/users/Everyone/guest-capable groups** and any group granting broad Read/Write. Do not change checkboxes or save. Share a screenshot or counts/categories; no need to share personally identifying user list or credentials. Then select a DEV-specific restricted NAS destination or an independently encrypted copy policy with separately approved ACL changes if needed; continue toward restore readiness and separately approved PR32 DEVELOPMENT acceptance. **PRODUCTION NO-GO**.

## Synology DSM legacy-share local-group permissions: shared-folder ACL scope resolved (2026-10-30)

**Owner supplied an additional Synology DSM `Edit Shared Folder erpnext_backups → Permissions → Local groups` screenshot** and confirmed the three individual `Read/Write` local-user entries inherited from the administrator group are **all controlled by the same project owner/administrator**, not other business personnel. The screenshot displays four local groups: **administrators = Read/Write** (explicit checked Read/Write); **http, Maintenance, users = No Access**. Previous four screenshots showed 39 local-user entries, including `guest = No Access`, exactly four `Read/Write` previews: three now owner-identified administrator accounts (group inherited) and one designated backup-service account (explicit user grant). All remaining displayed local-user entries showed `No Access`.

**Decision:** At the **Synology DSM shared-folder local-user and local-group permission** level, the legacy `erpnext_backups` share is acceptably restricted for the owner-approved **guarded DEVELOPMENT-only off-host copy** into a uniquely named directory. There is no evidence that the default `users` group, Guest, http, or Maintenance has access. This is not a penetration test, full domain group audit, per-subfolder advanced ACL inspection, or proof of restore. Do not repeat these same DSM screenshots again unless permissions change. The `0755` mode seen from the Linux CIFS client even after `mkdir(mode=0700)` is an **inconclusive client POSIX-mode presentation** and does not override the DSM server-side shared-folder restrictions; conversely it does not prove server-side security by itself. Do NOT modify mount flags, chmod the legacy share, or broaden Synology grants just to make CIFS appear 0700.

**Reviewed next operator action (same previously approved DEVELOPMENT recovery stage):** Run a **revised transfer** that relies on the owner-verified DSM share permissions rather than the misleading Linux CIFS mode check. Reconfirm the exact expected `//192.168.50.132/erpnext_backups cifs` mount, the two local protected snapshots and all eight expected files, sufficient NAS capacity; allocate an **exclusive fresh**, collision-resistant hidden `.partial-ccpc-development-pr32-...` destination at NAS root; copy eight files via exclusive file creation and compare source/destination SHA256 and bytes, write and verify a checksum manifest, then rename to unique final `ccpc-development-pr32-...`; report only status/directory name. **Do not touch the first EMPTY partial `.partial-ccpc-development-pr32-7895c72462f41cae`**, any legacy production timestamped backup, retention/cron, Docker services, app code or database; no automatic cleanup/retry. If unexpected error or mismatched hashes, STOP with an incomplete new partial untouched. Inherited Synology ACL/privacy for newly written subpaths should be verified during subsequent independent recovery/security review, as should full restore and any future cross-host ransomware/immutability threat model. No new PR32 checkout/migration/restart/merge/PRODUCTION authorization.

## Two DEVELOPMENT backups checksum-verified on Synology: OFF-HOST COPY PASS (2026-10-30)

**Owner provided completed operator terminal output** for the reviewed, owner-approved fresh exclusive NAS transfer:
```text
NAS MOUNT: PASS
LOCAL BACKUPS: 2/2 PASS
NEW NAS STAGING DIRECTORY: CREATED
ccpc-integration2.localhost: 4/4 SHA256 PASS
development.localhost: 4/4 SHA256 PASS
NAS BACKUP CHECKSUMS: 8/8 PASS
FINAL NAS DIRECTORY: /mnt/erpnext_backups/ccpc-development-pr32-20261029T234223Z-f38259861f97ed80
BOTH DEVELOPMENT OFF-HOST BACKUPS: PASS
```

**Verified by reported command execution:** Source snapshot directories were local `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots/{ccpc-integration2.localhost-20261029T132329Z-99d6786e,development.localhost-20261029T134505Z-f9d195ea}`. The script revalidated the **exact** mounted `//192.168.50.132/erpnext_backups cifs` NAS source, checked each site folder for the four expected nonempty artifacts (database gzip, site config JSON, public TAR, private TAR) and remaining space, created a uniquely named NAS staging location, copied all eight components via exclusive open, `fsync`'d destination files, compared source/destination SHA-256 plus byte sizes, wrote/re-read `SHA256SUMS`, and successfully renamed the staging directory to the published **final** path above. Reported published time: **2026-10-29 23:42:23 UTC = 2026-10-30 07:42:23 Asia/Manila**. This is **off-host NAS copy PASS**; not geographically offsite, immutable, independently re-read on a different session, or restore-verified. The earlier empty `.partial-ccpc-development-pr32-7895c72462f41cae` was explicitly not touched, as were legacy PRODUCTION timestamped backup directories.

**Restore readiness remains unverified:** Byte identity and gzip/TAR/JSON stream checks do not prove a live, internally consistent database-and-attachment snapshot nor that a clean isolated restore boots, applies exact schema and passes site login/attachment/representative business validation. Backup source was live when archived; synchronization across DB/files was not guaranteed atomic. Both backups share a Synology NAS in the same general site/LAN (not independent disaster domain). No DEV site restore, unapproved database writes/migrations, checkout/pull, worker restart, PR merge, or PRODUCTION action was performed as part of this transfer.

### Fresh GitHub exact-commit integration delta review

A GitHub compare read `ccpcerp/ccpcerp:0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41...061e65710eb4b527fc8ac579aaab8ccad4dd131d` returned **ahead 77, behind 0, changed files 62**. This is an *ancestry delta between the installed DEV source* and the combined PR32 review branch, not merely the four-report isolated PR diff against Finance base `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. In addition to all four `ccpc_erp/report/...` folders and CI tests, the intervening commits introduce Finance lifecycle Python modules, edit existing Finance/runtime helpers and DocType JSON, and add **five Finance lifecycle DocTypes** (Accounting Mapping Decision, Mapping Decision Use, Mapping Rejection Event, Mapping Retirement Event, Mapping Retirement Request). No files under `patches/` appeared in this GitHub file comparison, **but DocType schema and fixture/report sync need controlled migration/verification**. The synthetic Integration2 site and main Development site both share a bench code path, even though they have distinct databases. Do not treat PR32 as a zero-schema/report-only checkout compared against the currently installed source.

**Practical next decision:** Under the earlier approval, the **backup creation and off-host transfer stage is complete**; DO NOT run more generic host/Docker/Synology audits. Prepare a narrow **read-only source/schema/rollback readiness and isolated restore plan**, using the already verified 8/8 backups and pinned GitHub changes. Obtain **new, explicit owner approval** for an isolated synthetic site restore and any DEVELOPMENT code checkout / site migration / service interruption or financial test transactions, as applicable. No restore has yet been performed; PRODUCTION remains **NO-GO**, even though off-host backup transfer passed.

## PR32 DEVELOPMENT five-DocType read-only schema inventory: 0/5 on both sites (owner output 2026-10-30)

**Owner executed the exact read-only operator command previously supplied**, with guard that shared app `HEAD=0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and worktree `?? AGENTS.md` were unchanged. Output:

```text
<frozen site>:101: RuntimeWarning: Unexpected value in sys.prefix, expected /workspace/development/frappe-bench/env, got /workspace/development/frappe-bench/sites/../env
<frozen site>:101: RuntimeWarning: Unexpected value in sys.exec_prefix, expected /workspace/development/frappe-bench/env, got /workspace/development/frappe-bench/sites/../env
ccpc-integration2.localhost
Finance lifecycle DocTypes present: 0 / 5
FINANCE SCHEMA INVENTORY: PASS
development.localhost
Finance lifecycle DocTypes present: 0 / 5
FINANCE SCHEMA INVENTORY: PASS
```

**Interpretation:** The script/query completed on both separate existing DEVELOPMENT databases. `PASS` means the **inventory operation ran**, not that the five proposed target DocTypes are already installed. **All five proposed Finance lifecycle DocTypes are ABSENT in each site's currently deployed schema**, consistent with the current old code and a forthcoming `bench migrate` requirement. No site master/transaction changes were performed by this query. The `sys.prefix` and `sys.exec_prefix` warnings are due to launching virtualenv Python through `sites/../env/bin/python`; next commands should invoke the exact absolute `/workspace/development/frappe-bench/env/bin/python`, retaining cwd `sites` and `sites_path='.'`, avoiding the cosmetic warning. No evidence of Python runtime failure.

**Fresh GitHub source comparison, installed DEV `0c223d7...` → PR32 `061e657...`:** `ccpcerp/hooks.py`, `ccpcerp/setup.py`, `ccpcerp/patches.txt` are **byte-identical** at these two exact commits. The target adds five distinct new Finance lifecycle DocTypes:
1. CCPC Accounting Mapping Decision.
2. CCPC Mapping Decision Use.
3. CCPC Mapping Rejection Event.
4. CCPC Mapping Retirement Event.
5. CCPC Mapping Retirement Request.

It also modifies existing `CCPC Expense Mapping Revision` and `CCPC Center Mapping Revision` schema: **four optional rejection-provenance fields** (`rejected_by`, `rejected_at`, `rejection_reason`, `rejection_event`) and an additional `Rejected` approval_state option each. Existing role permission arrays in those two JSON files are unchanged. These schema additions are not proof of runtime compatibility: both existing sites must be migrated in a scheduled coordinated shared-bench window. Existing `after_migrate` still contains data-/permission-changing setup, even though its source is unchanged; the `patches.txt` list itself is unchanged. The previously verified 86/86 disposable CI tests do not substitute for persistent site acceptance.

**Next execution plan / authorization boundary:** Fresh local and off-host DEV four-part backup sets and 8/8 SHA256 NAS copies are verified, but **no independent restore rehearsal**. Existing authorization covers recovery-stage copying and GitHub review/documentation only; it does NOT approve changing shared app source, running site migrations, stopping/restarting DEV Honcho, performing real business writes or touching PRODUCTION. For the quickest bounded route to PR32 persistent DEV acceptance, first decide a separately scoped **non-production restore validation/rollback standard**, then obtain the owner's explicit approval for an exact-SHA shared-bench DEV maintenance window: (a) guard source checkout and two protected backups and snapshot age, (b) pause **DEV Honcho only** with verified exact process identity, (c) safe exact-SHA source update preserving `AGENTS.md`, (d) migrate synthetic Integration2 and verify five DocTypes and two extended revisions, (e) migrate main DEV after reviewing actual first-site results, (f) restore DEV-only Honcho and HTTP/queue/scheduler smoke, (g) authenticated per-company four-report checks plus rollback decision. Any restoration is a separate, data-destructive action needing its own precise approval; Git source reset alone cannot reverse site schema changes. **PRODUCTION NO-GO**. Do not issue another generic infrastructure audit or an unapproved code-switch command.
