# CCPC ERPNext — Current DEVELOPMENT handoff (continuation 4)

**Checkpoint: 2026-11-02, Asia/Manila.** This is the latest concise status after the oversized `CURRENT-HANDOFF-3.md`. Read that file for historical milestones; do not interpret its old final "next action" as current. Operational policy remains `GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md`.

## Immutable scope / source

- Source of truth: `ccpcerp/ccpcerp` PR **#32**, review branch `review/four-day-one-reports-integration-2026-10-29`, **draft/open/unmerged** at exact head `532a28d99bd0548241854495156a61f94eb1ac6b` (reconfirmed through connected GitHub on Nov 2).
- Installed code in **DEVELOPMENT only**: Docker container `frappe_docker_devcontainer-frappe-1`, bench `/workspace/development/frappe-bench`, app `apps/ccpcerp`, detached HEAD pinned to that SHA; only `?? AGENTS.md` untracked and protected. Avoid checkout or cleanup.
- DEVELOPMENT sites: synthetic `ccpc-integration2.localhost` and MAIN `development.localhost`, distinct databases. **PRODUCTION has not been touched** and requires separate explicit approval for any change.
- Protected Nov 2 four-part snapshots (do not clean up) at `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/`: `ccpc-integration2.localhost-20261102T001358Z-00771ef0fbcf` and `development.localhost-20261102T002314Z-7dc759b9afc9`. Verified SHA256 copies on Synology `/mnt/erpnext_backups/ccpc-development-pr32-20261102T003434Z-237495dd9a3d4061`. No full isolated restore test.
- DEV Honcho/web/workers/scheduler were gracefully stopped for migrations and remain **not restarted** as of this checkpoint; earlier process sweep found 4 idle shells that must remain untouched. No broad Docker/host restarts.

## Owner-run verified outcomes

1. Source switch to exact pinned PR32 SHA, with worktree guard and untouched `AGENTS.md`: **PASS**.
2. Both **sequential** owner-approved DEVELOPMENT migrations (`bench --site ccpc-integration2.localhost migrate`, then `bench --site development.localhost migrate`): **PASS**, exit 0. Schema/data/backfill migration was an approved DB write; no PRODUCTION migration.
3. Postmigration metadata validation on **both sites**: Role `CCPC Group Executive Reporting`, standard Page `ccpc-group-executive-reporting` with exclusive Role, four standard native Script Reports each restricted to `System Manager`, reference DocTypes, and **0 users assigned** the new executive role: **PASS**.
4. Synthetic Integration2 lacks `tabStock Entry.department` and `tabStock Entry Detail.department`; **MAIN has both**. Department source SQL on synthetic Integration2 is not compatible and must not be represented as tested; do not manually add columns.
5. MAIN six raw underlying report SQL statements on October 1–31, 2026, explicit read-only transaction and bounded rows: **6/6 PASS**. Counts: Dept material 2, equipment material 2, equipment job 0, intercompany CCPC/RMC 1, stock source 2, P&L GL 2. Zero equipment jobs means Job Order row presentation still lacks coverage.
6. Initial standalone full-report test failed at `frappe.connect()` with `FileNotFoundError: database.log` because Python was launched from bench root while Frappe expected the sites working directory. Exact mistaken target: `/workspace/development/logs/database.log` (missing parent). Correct real bench logger: `/workspace/development/frappe-bench/logs/database.log` (present and writable). **Resolved by changing diagnostic working directory**, not by creating new directories or modifying code/database.
7. **Most recent owner-run corrected MAIN real Frappe runtime test PASS, exit 0**: run from `/workspace/development/frappe-bench/sites` with `frappe.init(site="development.localhost", sites_path=".")`, `frappe.connect()`, `START TRANSACTION READ ONLY`, Administrator diagnostic identity. Four full report `execute()` functions succeeded: Department **19 columns / 2 rows**, Equipment Material & Job **24 / 2**, Intercompany Billing **22 / 1**, Stock & P&L GL **17 / 4**. Guest and Administrator invoking `run_group_report` were **both denied** by `frappe.PermissionError`. Transaction explicitly rolled back, destroyed Frappe session, no business records/roles changed. DEVELOPMENT services **NOT RESTARTED**, PRODUCTION **NOT TOUCHED**.

## Pending / limitations

- Positive authorized executive gateway test **not performed**: new Role assigned to zero named users, and do not assign roles or create fake accounts merely for testing without approval. Further named nonexec denial, cross-company and role/DocPerm isolation, source-quality flags, row-level permissions, and web/browser UX remain pending. Historical pre-migration test found some named System Managers lacked all underlying source DocType read permissions, so do not broaden those grants automatically.
- Report outputs successfully render in Administrator diagnostic context; that does **not** certify financial totals, posted accounting balances, original source quality, or production release readiness. Original SLE, P&L GL and billing values must not be incorrectly aggregated as one cost.
- Review guarded DEV-only service restoration procedure and current stopped process status before starting services; verify exact Docker container, bench Procfile and ensure no duplicate Honcho or shared-infrastructure impact. **Do not blindly run `docker restart`, `bench start` in the background, or signal unrelated processes.** If owner authorizes the narrow service start, restore only DEVELOPMENT processes and confirm both sites and reporting browser paths. No PRODUCTION activity. No PR merge/release yet.

## Immediate next safe action

Perform a **read-only DEVELOPMENT service-start readiness audit**: inspect Procfile, process/listener inventory, process manager and exact launch mechanism from deployment docs/current environment, without starting/stopping anything. Separately decide whether to perform remaining security tests before/after DEV service restoration. Preserve protected recovery snapshots and untracked `AGENTS.md`. Update this handoff with verified results during active conversation.

## Key pointers

- Prior history: `docs/ccpc-project/CURRENT-HANDOFF-3.md`.
- Workflow: `docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md`.
- Code PR: https://github.com/ccpcerp/ccpcerp/pull/32 .


## 2026-11-02 — DEVELOPMENT-only service restart readiness PASS (owner output)

**Owner-reported read-only service-start audit after both DEV site migrations and successful four native report executions:**
```text
PINNED SOURCE AND AGENTS.md: PASS
PROCFILE SERVICES: web, socketio, watch, schedule, worker
PROCFILE FIVE SERVICES: PASS
DEVELOPMENT SITE CONFIGURATIONS: PASS
BENCH LOG DIRECTORY: PASS
LIVE SERVICE CANDIDATES: 0
ZOMBIE PROCESSES IGNORED: 48
DEVELOPMENT SERVICE LISTENERS: []
SERVICE RESTART READINESS: PASS
NO PROCESSES SIGNALED
NO SERVICES STARTED
NO DATABASE CHANGES
READINESS_AUDIT_EXIT_CODE=0
```
**Interpretation:** exact pinned detached PR32 source `532a28d99bd0548241854495156a61f94eb1ac6b` and protected `?? AGENTS.md` intact. The named DEV container has exactly the expected five bench Procfile labels; both DEV site configs and bench log directory present. No matching active service processes or listeners were found. **48 zombies are dead process entries, not services to signal or delete**. No files, Docker state, site DB, application code, scheduled queue state, or PRODUCTION changed by this audit. Connected GitHub reconfirms PR #32 draft/open/unmerged and head unchanged.

**Previously owner-approved next controlled action:** re-guard source, backups, exact DEV container, Procfile labels, absence of active managers/workers/web/scheduler/watch/socketio/listeners; then launch exactly one detached DEV-only Honcho `/home/frappe/.local/bin/honcho start` from `/workspace/development/frappe-bench`, using a private non-clobber log there. Verify one live Honcho manager and pinned SHA after launch. Do not restart containers, affect shared host/PRODUCTION, clear zombie entries, rerun migrations, alter roles, merge PR or automatically retry a failed launch. Manager PASS alone does not establish site HTTP readiness; separately test both sites and queue/worker/scheduler on next operator step. Retain all local+Synology snapshots and original `AGENTS.md`.


## 2026-11-02 — Honcho restart blocked by overrestrictive socketio Procfile preflight; no launch

**Owner-reported output from step 23, the guarded DEVELOPMENT-only postmigration Honcho startup attempt:**
```text
PROTECTED SYNOLOGY BACKUPS: PASS
PINNED SOURCE AND LOCAL BACKUPS: PASS
STOP: Review Procfile command socketio
DEVELOPMENT_START_EXIT_CODE=1
STOP: Do not automatically retry startup
```
The script exited during **read-only Procfile validation**, before reaching its `docker exec -d` Honcho launch. Thus this attempt **did not start** a new DEVELOPMENT Honcho manager, run a migration, change code, or touch PRODUCTION. The preflight used the predicate `'socketio.js' in command` and rejected any `;\`, `&&`, `||`, `|`, or backtick; actual Socket.IO Procfile line was not printed, so it is **unknown whether the problem was the expected path fragment, a forbidden operator, or both**. Earlier read-only readiness audit found exactly five labels `web, socketio, watch, schedule, worker`, zero live service candidates, no DEV listeners, and 48 zombie process entries (defunct, do not signal). Nov2 NAS and local backup manifests and exact pinned source guards passed in the attempted restart. Full Frappe MAIN four-report execution and Guest/Admin gateway denial previously PASS; no positive executive user test. PR #32 remains draft/open/unmerged at pinned SHA `532a28d99bd0548241854495156a61f94eb1ac6b`.

**Next one safe diagnostic:** read only the `socketio` entry in exact DEV bench `Procfile`; print its literal command after redacting any env-like secrets, and individual pass/fail booleans for `socketio.js` path fragment and each forbidden shell operator. Guard exact app SHA, detached status and protected sole `?? AGENTS.md`. No service launch or file modification. Then revise *the temporary startup guard*, not the app Procfile, based on its actual safe command; re-run full guarded DEV-only startup once after review, with no automatic retries. MAIN/Integration2 and PRODUCTION remain unchanged.


## 2026-11-02 — Socket.IO Procfile confirmed `bench socketio`; adjust only temporary Honcho guard

**Owner-run read-only exact DEVELOPMENT Procfile inspection after preflight-only startup block:**
```text
PINNED SOURCE: PASS
PROCFILE SERVICE LABELS: PASS
SOCKETIO COMMAND: bench socketio
CONTAINS socketio.js: False
CONTAINS realtime: False
CONTAINS SHELL MARKER ';': False
CONTAINS SHELL MARKER '&&': False
CONTAINS SHELL MARKER '||': False
CONTAINS SHELL MARKER '|': False
CONTAINS SHELL MARKER '`': False
SOCKETIO PROCFILE INSPECTION: COMPLETED
NO FILES MODIFIED
NO SERVICES STARTED
SOCKETIO_INSPECTION_EXIT_CODE=0
```
**Established:** the prior startup preflight incorrectly hardcoded an old Socket.IO launch fragment (`socketio.js`). The actual valid current Procfile line is **`socketio: bench socketio`** without forbidden shell operators, and exactly the five labels `web, socketio, watch, schedule, worker` remain. Do **not** modify the Procfile, app or site databases to satisfy the previous test. Source stays detached pinned at `532a28d99bd0548241854495156a61f94eb1ac6b` with only protected untracked `AGENTS.md`. Previous startup attempt stopped **before launch**. No services started, no production change. All four MAIN complete report executions and Guest/Admin gateway-denial tests already PASS; positive named executive viewer not tested because role has 0 assignments. Connected GitHub PR32 rechecked still draft/open/unmerged with exact SHA.

**Next authorized one action:** after repeating strict backup and process guards, modify only startup validation to accept `bench socketio` (exact command), and launch exactly one DEV-only Honcho process with non-clobber private bench log; verify single live manager and unchanged Git source. Fail closed on unexpected other Procfile commands, existing service processes/listeners or ambiguous launch state. No automatic retry, broad container restart, migrations, user-role edits, PR merge or PRODUCTION activity. If successful, next separate HTTP site and worker/scheduler health checks.


## 2026-11-02 — Corrected DEV startup preflight stops at worker command; no Honcho launch

**Owner report from second guarded startup attempt:**
```text
PROTECTED SYNOLOGY BACKUPS: PASS
PINNED SOURCE AND LOCAL BACKUPS: PASS
STOP: Review Procfile worker
DEVELOPMENT_START_EXIT_CODE=1
STOP: Do not automatically retry startup
```
This exited at read-only Procfile validation, **before** the one detached Honcho launch instruction. The previous Socket.IO mismatch was fixed in the temporary script: actual Procfile entry `socketio: bench socketio`. The worker failed because the script requires `shlex.split(command)[:2] == ['bench','worker']` and disallows certain shell metacharacters, but the actual worker command and precise failed predicate were not printed. It is **not** evidence that the worker is misconfigured. Earlier Procfile inspection verified five entries: web, socketio, watch, schedule, worker. The pinned source/AGENTS and NAS/local backup presence guards passed on attempted launch. Both DEV migrations, MAIN 6/6 raw SQL, four real report `execute()` functions and Guest/Admin gateway denial PASS. No service launch, code/schema/data change or PRODUCTION modification from this attempt. PR32 remains draft/open/unmerged at `532a28d99bd0548241854495156a61f94eb1ac6b` per connected GitHub.

**Next one read-only action:** inspect all five exact DEV `Procfile` commands, their tokenized command heads, and whether the current start-script validation would reject each, redacting sensitive assignments. Avoid repeating blind startup attempts. Then revise **only the temporary validation logic**, not the Procfile, to match reviewed safe commands; recheck live processes/listeners before any authorized DEV-only single-Honcho launch. No automatic retry, migrations, Docker restart, role edits, PR merge or PRODUCTION action.


## 2026-11-02 — All five DEVELOPMENT Procfile commands inventoried; worker redirects explain startup preflight stop

**Owner-reported read-only full Procfile diagnostic (`PROCFILE_DIAGNOSTIC_EXIT_CODE=0`)** verified pinned source and all five labels and commands:
```text
web:      bench serve  --port 8000
socketio: bench socketio
watch:    bench watch
schedule: bench schedule
worker:   bench worker 1>> logs/worker.log 2>> logs/worker.error.log
```
All five tokenize correctly; service heads match expected `bench serve/socketio/watch/schedule/worker`. The only shell marker across these commands is the expected worker log append redirection `>`; the previous temporary launch script rejected that marker globally, resulting in `STOP: Review Procfile worker` **before Honcho startup**. Worker redirection syntax is normal for this bench Procfile and is not proof of misconfiguration. The operator confirmed `NO FILES MODIFIED`, `NO SERVICES STARTED`, `NO DATABASE CHANGES`, `PRODUCTION: NOT TOUCHED` from diagnostic. App still pinned exact detached PR32 SHA `532a28d99bd0548241854495156a61f94eb1ac6b` with sole protected untracked `AGENTS.md`. GitHub PR32 remains draft/open/unmerged. Earlier successful MAIN postmigration metadata, 6/6 SQL, four real Frappe execute reports and Guest/Admin gateway denials remain valid.

**NEXT operator action under previously approved DEV maintenance:** launch **one** DEV-only Honcho manager after rechecking NAS+local snapshot manifests, correct app pinned source + sole AGENTS, no existing active DEV managers/services or listeners and Procfile **exact known five definitions**. Use corrected validator which allows **only** exact `worker: bench worker 1>> logs/worker.log 2>> logs/worker.error.log`, not arbitrary shell redirection or other unreviewed commands; preserve existing Procfile. Use a new unique non-clobber bench log and `docker exec -d` inside the single named DEV container; postcheck one live manager; if anything fails, **never blindly retry**, inspect resulting state first. No broad Docker restarts, Git checkout, data mutations, process signals, PR merge or PRODUCTION action. Following startup, verify both DEV sites HTTP health and workers/scheduler in separate step.


## 2026-11-02 — Third DEV Honcho startup preflight stops at strict exact-two site inventory

**Owner's result from re-guarded DEVELOPMENT-only startup attempt with five exact verified Procfile commands:**
```text
SYNOLOGY RECOVERY MANIFESTS: PASS
PINNED SOURCE AND LOCAL BACKUPS: PASS
VERIFIED FIVE PROCFILE COMMANDS: PASS
WORKER LOG REDIRECTIONS: PASS
STOP: Unexpected DEVELOPMENT bench sites
DEVELOPMENT_START_EXIT_CODE=1
STOP: Inspect state before any further startup attempt
```
**Scope and interpretation:** The temporary startup script's Python preflight compared every directory under the DEV bench `sites/*/site_config.json` to an **exact** set containing only `development.localhost` and `ccpc-integration2.localhost`. The strict set-equality failed. This can indicate additional legitimate site configs, a missing named config, or another filesystem issue; do not infer any particular third site without an inventory. Earlier audits confirmed both named DEV site configs exist, so additional site(s) are plausible. The script exited **before** the `docker exec -d` Honcho launch, with no startup/migration/code or production operation from this attempt. NAS/local recovery manifest and pinned source+AGENTS, five Procfile commands and worker append redirection guards passed. No PR merge; GitHub confirms PR32 draft/open/unmerged at `532a28d99bd0548241854495156a61f94eb1ac6b`.

**NEXT safe step:** read-only exact DEVELOPMENT bench site_config inventory from the named DEV container, guard pinned app SHA and protected AGENTS, print site directory names and classify expected/extra, detect symlinks and anonymous distinct DB checks without printing credentials, DB names or contents; do not mutate files. **Before starting Honcho**, review whether any extra site is potentially PRODUCTION or otherwise a workload not authorized to restart, since a bench-wide scheduler/worker can operate on all configured sites and DEV and PROD may share host infrastructure. Do not merely relax the set to allow arbitrary sites, and do not rerun startup until scope is understood. If all extras are verified DEV-only, change the startup guard to check both approved sites are present and no production/unknown sites would be acted on. All previous migrations and MAIN reporting tests remain PASS; web/workers/scheduler still down as of last verified inspection.


## 2026-11-02 — Three DEV bench site configs found; third known broken integration site excluded from rollout

**Owner's read-only exact DEV bench inventory after third guarded Honcho preflight stop:**
```text
PINNED SOURCE: PASS
SITE CONFIGURATION COUNT: 3
EXPECTED SITES PRESENT: True
ADDITIONAL SITE COUNT: 1
SITE: ccpc-integration.localhost
CLASSIFICATION: ADDITIONAL - REVIEW REQUIRED
SITE DIRECTORY SYMLINK: False
CONFIGURATION SYMLINK: False
SITE: ccpc-integration2.localhost
CLASSIFICATION: EXPECTED DEVELOPMENT
SITE DIRECTORY SYMLINK: False
CONFIGURATION SYMLINK: False
SITE: development.localhost
CLASSIFICATION: EXPECTED DEVELOPMENT
SITE DIRECTORY SYMLINK: False
CONFIGURATION SYMLINK: False
SITE INVENTORY: COMPLETED
NO CONFIGURATION CONTENTS DISPLAYED
NO FILES OR DATABASES MODIFIED
NO SERVICES STARTED
PRODUCTION: NOT TOUCHED
SITE_INVENTORY_EXIT_CODE=0
```
**Important GitHub reconciliation:** Earlier authoritative `CURRENT-HANDOFF-3.md`, `DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md` and `PR32-DEVELOPMENT-READ-ONLY-PREFLIGHT-2026-10-29.md` explicitly call `ccpc-integration.localhost` a **known incomplete/failed/broken integration site excluded from the approved two-site migration/recovery scope**. Thus the third site is **not an unknown PRODUCTION site on existing documentary evidence**, but it is explicitly **not part of the tested/migrated rollout**, and its lingering `site_config.json` might still be enumerated by bench-wide scheduler/web workers on a Honcho start. Do not simply relax the startup guard and treat all three as valid; do not remove, rename, migrate, restore or alter the broken site without separate review/authorization. The strict exact-two check correctly stopped before launch and exposed this latent topology risk. HEAD still pinned `532a28d99bd0548241854495156a61f94eb1ac6b`, only protected `?? AGENTS.md`; NAS/local backups and five exact Procfile commands passed previously. Both approved DEV migrations, MAIN metadata, 6/6 raw SQL, all four native report `execute()`, and Guest/Admin gateway-denials PASS. DEVELOPMENT services remain down at last observed audit. PRODUCTION untouched; PR32 draft/open/unmerged.

**NEXT safe owner action:** one read-only targeted three-site configuration/scheduler-scope check inside named DEV container: compare database names for 3/3 distinctness **without printing names, secrets, or hostname**, inspect site-level `disable_scheduler` and `maintenance_mode` flags, and report whether the known broken site's config is complete or points to any approved DEV DB. Avoid contacting/writing the broken site DB, changing any files or starting services. Depending on evidence, review Frappe's actual bench-wide scheduler site-selection behavior before the next DEV Honcho start. Full launch requires explicit scoped decision to keep broken site inactive or otherwise safely isolate it; no unapproved changes to site configs or PRODUCTION.


## 2026-11-02 — Three DEV site configs distinct; broken excluded site's scheduler not disabled; hold Honcho startup

**Owner's read-only three-site config/scheduler-scope check output:**
```text
PINNED SOURCE: PASS
SITE CONFIGURATIONS: 3/3 PRESENT
ALL DATABASE NAMES CONFIGURED: True
ALL THREE DATABASE NAMES DISTINCT: True
TWO APPROVED DATABASES DISTINCT: True
COMMON DISABLE_SCHEDULER: NOT SET
SITE: development.localhost
DB CONFIGURED: True
DB HOST CONFIGURED: True
SITE DISABLE_SCHEDULER: NOT SET
SITE MAINTENANCE_MODE: NOT SET
SITE: ccpc-integration2.localhost
DB CONFIGURED: True
DB HOST CONFIGURED: True
SITE DISABLE_SCHEDULER: NOT SET
SITE MAINTENANCE_MODE: NOT SET
SITE: ccpc-integration.localhost
DB CONFIGURED: True
DB HOST CONFIGURED: True
SITE DISABLE_SCHEDULER: NOT SET
SITE MAINTENANCE_MODE: NOT SET
CONFIGURATION INSPECTION: COMPLETED
DATABASE CONNECTIONS: NONE
NO FILES OR DATABASES MODIFIED
NO SERVICES STARTED
PRODUCTION: NOT TOUCHED
SITE_SCOPE_CHECK_EXIT_CODE=0
```
**Interpretation:** all three site configs have separate configured database names and database hosts and no explicit site-level scheduler disable or maintenance settings, with no common disable_scheduler flag. The third `ccpc-integration.localhost` is a known incomplete/broken **DEVELOPMENT** site explicitly excluded from owner-approved two-site backup/migration/release testing per `CURRENT-HANDOFF-3.md` and controlled DEV plan. Distinct names rule out *configured aliasing between these three DB names*, not host-level or credentials isolation; they do not guarantee no scheduler activity. No Frappe DB was connected in this check; cannot infer enabled site scheduler from config alone, since database-held scheduler/maintenance state and installed framework code may affect behavior. Starting full bench-wide Honcho without identifying installed scheduler site enumeration could attempt work on broken third site. **Hold DEV startup until verified or explicit safe isolation decision.** Latest operator command was read-only, no server processes launched or PRODUCTION touched. Pinned PR32 `532a28d99bd0548241854495156a61f94eb1ac6b` remains draft/open/unmerged as independently rechecked on connected GitHub. Successful two-site migrations, MAIN metadata, 6/6 raw SQL, four native report `execute()`, Guest/Admin gateway denials unchanged.

**NEXT safe read-only operator action:** inspect the **installed** `apps/frappe` scheduler source around site enumeration, `bench schedule`, and disabled-site checks with bounded excerpts only, using exact DEV container/app source guard; inspect no credentials/DB contents, run no scheduler, Frappe session, migrations or startup. Determine whether shared `bench schedule` will include the broken third site by default. Review site isolation options before any configuration-write authorization; do not rename/delete site, set flags, change Procfile, or start Honcho without appropriate scope.


## 2026-11-02 — Installed Frappe scheduler discovery includes broken third integration site; full Honcho startup held

**Owner-run read-only source inspection of installed DEVELOPMENT Frappe code (exit=0):** `get_sites` traverses `os.listdir(sites_path)`, accepts directory not symlink and containing `site_config.json`, and appends each site. `enqueue_events_for_all_sites` calls `get_sites()`, loops over returned sites and calls `enqueue_events_for_site(site=site)`; that function performs `frappe.init(site)`, **`frappe.connect()`**, then `is_scheduler_inactive()` before enqueueing. `is_scheduler_inactive()` checks `maintenance_mode`, `pause_scheduler` and `is_scheduler_disabled()`; disable check reads `frappe.conf.disable_scheduler` and `System Settings.enable_scheduler`. All requested function and pattern checks found (source inspection: completed, no DB connections, no scheduler/Honcho start, no modifications, PRODUCTION not touched). The earlier three-site inventory found `ccpc-integration.localhost` as a **real non-symlink directory with site_config.json**; prior GitHub docs classify it as a known broken/incomplete integration site **excluded** from approved migrations. Three site configs reference distinct database names and no disable or maintenance flags are set. **Inference from installed source:** bench-wide `bench schedule` may try initial DB connection on excluded site even if scheduler is subsequently found inactive, so blindly starting full Honcho risks unintended interaction with broken site. Explicitly HOLD full DEV Honcho startup and do not delete/rename site or change config without separate review/approval. The two migrated intended DEV sites and all four MAIN reports remain PASS; PR32 pinned exact `532a28d99bd0548241854495156a61f94eb1ac6b`, draft/open/unmerged.

**Next read-only operator step:** inspect the installed CLI declaration of `bench schedule` (path `apps/frappe/frappe/commands/scheduler.py`) and the scheduler's site-specific options plus runtime `start_scheduler` loop (path `apps/frappe/frappe/utils/scheduler.py`) using small AST/source excerpts; do not start scheduler, connect to DB, change site files/Procfile or execute CLI with write effects. Determine if any actual `--site` selector truly constrains `get_sites()` for background scheduling. Public Frappe CLI documents `schedule` as **bench-wide**, while other scheduler management commands have per-site options; do not assume a generic `bench --site X` context constrains this scheduler. Based on evidence, propose DEV-only minimal safe isolation, or deliberate no-start pending scope confirmation. PRODUCTION untouched.
