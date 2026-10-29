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
