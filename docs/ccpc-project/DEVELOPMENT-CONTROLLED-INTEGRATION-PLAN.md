# CCPC ERPNext — Controlled DEVELOPMENT app integration and acceptance plan

**Prepared:** 2026-10-27 (Asia/Manila)  
**Status, updated 2026-10-27:** Both DEVELOPMENT migrations and independent 4/2/5 Finance schema checks PASS at pinned detached app HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. **Owner executed guarded DEVELOPMENT-only Honcho restart** and reported `DEVELOPMENT RESTART GUARDS: PASS`, `DEVELOPMENT HONCHO STARTED: PID=380905`; the subsequent guarded D5 HTTP probe returned `HTTP PING PASS` with **200 for both** `development.localhost` and `ccpc-integration2.localhost` and `BOTH DEV WEB PINGS: PASS`. This establishes web response on both sites after migration. **Owner's next read-only process inspection found Honcho PID `380905` still running after `27:22` with 25 live descendants and all five expected Procfile service labels configured**; this does not identify each actual service or prove queue/scheduler health. **Both valid DEVELOPMENT sites completed `bench doctor` with one shared registered worker, no scheduler-disabled/paused/inactive/maintenance warnings, and no queued job methods listed.** These are initial health checks only, not proof of scheduler execution or successful background jobs. Authenticated UI and financial transaction acceptance remain unverified. Read-only scheduler history now confirms all 4 enabled `All` jobs on each site have prior starts; historical `Complete` counts are 3,628 main and 3,718 integration2, with 1 historical Oct 25 failure each. However, main latest start `2026-10-27 10:30:03` / Complete `10:02:14` is older than integration2 latest start `13:00:08` / Complete `13:00:13` despite SQL database `NOW()` around `05:03` on both, consistent with but not yet proof of UTC database vs Asia/Manila application timestamps. Further read-only site-clock checks confirmed both sites' four frequent scheduler jobs started ~50 seconds before their own site-local clocks: main `development.localhost` is configured `Asia/Kolkata` (UTC+5:30), whereas `ccpc-integration2.localhost` is `Asia/Manila` (UTC+8). Thus the apparent 2h30 difference is accounted for by site timezone, not stalled scheduler ticks. **Owner approved and executed** the guarded one-site Frappe ORM save: `development.localhost` changed from `Asia/Kolkata` to `Asia/Manila`; `ccpc-integration2.localhost` stayed `Asia/Manila`. Terminal reported `PRECHANGE GUARDS: PASS`, `MAIN DEV TIMEZONE SAVE COMPLETED`, and `DEVELOPMENT TIMEZONE ALIGNMENT: PASS` after independent re-reads. Next verify two-site scheduler timestamps after setting change. No service restarts or PRODUCTION actions. PRODUCTION excluded. Both protected October 27 four-part snapshots and October 13 historical copies remain preserved locally; independent restore/off-host verification untested.

## 1. Objective and current verified inputs

Move the reviewed custom application toward persistent DEVELOPMENT acceptance while preserving both site databases, protecting untracked operator material, and retaining recoverable checkpoints. Finish the Withdrawal Slip → Material Issue → Finance mappings → intercompany billing → reporting milestone; do not restart previously agreed business design.

- App repo: `ccpcerp/ccpcerp`. Running shared DEVELOPMENT checkout (last operator inspection): `/workspace/development/frappe-bench/apps/ccpcerp`, branch `review/intercompany-approval-failure-tests`, commit `806fa23516490ec7beefcff03a1baa09d722120e`; untracked `AGENTS.md`. Recheck directly before any operation.
- Reviewed app candidate: `review/circleci-isolated-erpnext-phase2-2026-10-26`, exact GitHub head `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. This tip is a documentation-only update after CircleCI-passing **source** `c32f3f20bc3f0b5fa88f651d6dddee774b6cb2cb`. Operator-confirmed CircleCI pipeline #10 passed both opt-in isolated ERPNext and starter validation; **persistent DEVELOPMENT acceptance is NOT established**.
- The guarded fetch of the incoming ref already succeeded. GitHub compare from installed `806fa235...` to reviewed `0c223d7...`: **204 commits ahead, zero behind, 60 changed paths**; reviewed branch is a descendant. No incoming tracked root `AGENTS.md` in the changed paths. These facts do NOT imply automatic checkout/migration safety.
- Intended DEVELOPMENT sites: `development.localhost` and `ccpc-integration2.localhost`; both report Frappe 16.33.1, ERPNext 16.34.2 and CCPC 0.0.1 in prior operator checks. Integration2 `bench list-apps` was re-confirmed Oct 27 while still on the old shared checkout. Each site has a different configured MariaDB database name on host `mariadb`. They nevertheless share **one app code checkout, bench, Redis/services and host**. `ccpc-integration.localhost` has a known incomplete failed creation and must NOT be used.
- The host filesystem at `/workspace` reported 686 GiB available / 22% used (Oct 27). Each intended DEVELOPMENT site has one visible four-artifact local backup set dated October 13 (database, public files, private files, site configuration). Nonzero file presence does not establish restore viability or freshness. The legacy Synology CIFS mount was separately confirmed at `/mnt/erpnext_backups`; GitHub does NOT demonstrate that these two DEVELOPMENT backups reside on NAS or that NAS retention protects them.
- Existing PRODUCTION on the shared old Ubuntu host and separate dedicated `ccpcerp-prod` build remain **outside this procedure**. Do not operate legacy production containers `frappe_docker-*` or use the production backup script/site.

## 2. Incoming changes with site-migration implications (verified from GitHub)

**Schema and accounting controls:**

- Four **new** Finance mapping DocTypes: `CCPC Expense Mapping Scope`, `CCPC Expense Mapping Revision`, `CCPC Center Mapping Scope`, `CCPC Center Mapping Revision`. Their scope/revision key fields are unique; revisions hold proposed/approved values and provenance. DocType JSON has no general grant to users.
- `ccpcerp/setup.py` adds `ensure_bc_finance_mapping_roles()` to the existing `after_migrate` hook. It **creates** `CCPC Mapping Preparer` and `CCPC Accounting Mapping Approver` role definitions and expressly **does not assign roles to users**. Independent Company-specific Accounting signoff/permissions remain a distinct gate.
- Additional `Stock Entry Detail` custom fields capture source Equipment/Item Group and signed mapping revision identifiers. `ccpcerp/hooks.py` adds `Stock Entry.before_update_after_submit` snapshot validation. Other code paths for Withdrawal, Stock Entry and intercompany invoicing changed.
- `ccpcerp/patches.txt` is **identical** at old and incoming refs: it already lists equipment, role, intercompany Account/Customer/Supplier and non-unique index patches. An unchanged patch list does **not** prove these patches have already executed on both site databases. Patch Log and required actual master data must be checked before migration. Several patches enforce exact Companies, Account hierarchy/numbers and party configuration, and can fail against a site with missing/incompatible master data.
- `after_migrate()` also already contains substantial existing role/permission/workflow changes, custom-field creation, personnel/section setup, and issue-quantity backfills. It must be treated as a site-data-changing operation even where the only *new* after-migrate steps are narrow.

**Do not** assert that a green disposable CI run proves site-specific MariaDB schema compatibility, roles, real Company/account/cost-center mappings, full rollback, or PRODUCTION readiness.

## 3. Execution gates — strict sequence

### Gate A — current read-only checkout and site preflight (no migration)

1. Reverify app checkout location, current branch and full HEAD, staged/unstaged/untracked status, remote pinned SHA, and absence of incoming `AGENTS.md` path collision. **Stop on any deviation**, especially unknown uncommitted work. Do not stash, discard, clean, reset or unconditionally pull.
2. Reconfirm both *intended* sites' app installation and effective logical database separation without exposing passwords/configuration secrets. Verify the failed `ccpc-integration.localhost` is excluded from the test plan.
3. Read-only inspect the intended site's `tabPatch Log` status for the listed existing patches; check prerequisite Company/Account/party metadata without altering masters and without printing sensitive business data. Missing exact masters or conflicting structure is a **NO-GO** until evaluated separately.
**Patch Log CLI diagnostic, October 27:** A one-off script launched from `/workspace/development/frappe-bench` with `frappe.init(sites_path="sites")` failed before SQL execution: Frappe's default rotating file logger resolved `../logs/database.log` relative to the current directory, landing on the nonexistent `/workspace/development/logs/database.log`. This was a **working-directory/logging-path error**, not a demonstrated MariaDB failure or a patch result. Do not create the extra parent log directory or change service settings to work around this. Run ad hoc site scripts from `frappe-bench/sites` with `sites_path="."` and optionally enable per-process `FRAPPE_STREAM_LOGGING=1` to keep output off disk. The corrected read-only inventory command is:

```bash
docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
set -euo pipefail
cd /workspace/development/frappe-bench/sites
FRAPPE_STREAM_LOGGING=1 ../env/bin/python -' <<'PY'
from pathlib import Path
import frappe

patches = [
    item.strip() for item in Path("../apps/ccpcerp/ccpcerp/patches.txt").read_text().splitlines()
    if item.strip().startswith("ccpcerp.patches.")
]
for site in ("development.localhost", "ccpc-integration2.localhost"):
    print(f"\\nPATCH STATUS: {site}")
    frappe.init(site=site, sites_path=".")
    try:
        frappe.connect()
        recorded = {row[0] for row in frappe.db.sql(
            "SELECT patch FROM `tabPatch Log`", as_list=True
        )}
        for patch in patches:
            print(f"{patch.rsplit('.', 1)[-1]}: {'RECORDED' if patch in recorded else 'NOT RECORDED'}")
    finally:
        frappe.destroy()
PY
```

Do not infer that the corrected query succeeded until the operator supplies output. No database patch/migration may run as part of this inventory.

4. Record observed running DEVELOPMENT processes/queues and any background jobs that may import the shared app. A site-specific `bench migrate` does **not** isolate source changes from the other site.
5. Sample guarded Git preflight to run **only** immediately before a separately approved checkout, in the DEVELOPMENT container as `frappe`:

```bash
set -euo pipefail
cd /workspace/development/frappe-bench/apps/ccpcerp
test "$(git branch --show-current)" = "review/intercompany-approval-failure-tests"
test "$(git rev-parse HEAD)" = "806fa23516490ec7beefcff03a1baa09d722120e"
test "$(git status --porcelain=v1)" = "?? AGENTS.md"
test "$(git rev-parse refs/remotes/origin/review/circleci-isolated-erpnext-phase2-2026-10-26)" = "0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41"
test -z "$(git ls-tree -r --name-only 0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41 -- AGENTS.md)"
git diff --check
echo "PINNED APP CHECKOUT PREFLIGHT: PASS — NO FILE SWITCH EXECUTED"
```

This command is **read-only preflight**; no checkout, migration or service restart. If the earlier working-tree state changes, do not amend the guard to bypass unexpected differences.

### Gate B — new, verified DEVELOPMENT recovery points (requires separate operator authorization)

1. Preserve the October 13 original four-file sets from both sites in access-restricted locations **outside** Frappe's standard auto-cleanup directory before invoking fresh `bench backup`; verify copies with byte comparison or SHA256. Do not expose site config, SQL or private attachments in output, and do not overwrite/delete existing assets.
2. Obtain fresh four-artifact `--with-files` backup sets for **both sites** with an explicitly reviewed invocation and retention behavior. Remember normal Frappe backup commands may prune older default-location backups. Stage copies at a verified destination beyond that pruning; use an off-host copy only if the exact NAS target, access and protection are independently confirmed. Never reuse the existing legacy PRODUCTION scheduled backup workflow for DEV.
3. Validate filenames, nonzero sizes, gzip integrity, TAR readability and JSON syntax silently; verify checksums after copying. A true independent restore rehearsal to another isolated test database/site is the stronger release gate. Record restore status honestly; format checks alone are not restore tests.
4. Define rollback decision boundaries: source-code rollback alone does not reverse DocType schema, patch log, workflows, roles or backfilled rows. A necessary DB restore must target the exact DEVELOPMENT site and use the matched DB/public/private/config set after explicit approval. Keep both sites' snapshots and audit logs intact.

**No source checkout or site migration before Gate B.** A NAS mount confirmation and old PRODUCTION backup history do not satisfy this DEV gate.

### C0 — Owner-approved DEVELOPMENT-only Honcho shutdown (first runtime action)

**Authorization recorded 2026-10-27:** owner expressly approved a temporary DEVELOPMENT-only maintenance window, including interruption of the shared bench as part of the controlled integration process; no production actions permitted. Both sites may be unavailable while the five managed processes are down. Do not stop Redis/MariaDB containers or unrelated host processes. This phase **does not** include source checkout or database migration; perform those as subsequent separately verified steps rather than hiding them in one script.

**Process identity confirmed by owner from within DEVELOPMENT container:** Honcho PID `193`, parent shell PID `14`, session `14`, process group `193`, TTY `pts/0`, command `/home/frappe/.pyenv/versions/3.14.2/bin/python3.14 /home/frappe/.local/bin/honcho start`. The `Procfile` defines `web`, `socketio`, `watch`, `schedule`, `worker`. Startup terminal `pts/0` is historical; do not assume operator's current shell controls it.

Before performing shutdown, operator ensures no DEV users are transacting and no critical background job is intentionally running. Script **fail-closed checks exact Honcho identity** and sends `SIGINT` to *that process only* (not `kill -9`, not an unscoped `pkill`, not Docker restart). Honcho's process manager handles SIGINT by terminating its managed processes. The command waits for exit but never escalates to force-kill, and always requires operator to report if an unexpected condition occurs.

At Ubuntu **host** shell (`gani@ccpcerpserver`), *not* inside the devcontainer:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
set -euo pipefail
pid=193
expected="/home/frappe/.pyenv/versions/3.14.2/bin/python3.14 /home/frappe/.local/bin/honcho start"
actual=$(ps -o args= -p "$pid" | sed "s/^[[:space:]]*//")
[ "$actual" = "$expected" ] || { echo "STOP: Honcho identity changed"; exit 1; }
[ "$(ps -o ppid= -p "$pid" | tr -d " ")" = 14 ] || { echo "STOP: Honcho parent changed"; exit 1; }
[ "$(ps -o pgid= -p "$pid" | tr -d " ")" = 193 ] || { echo "STOP: Honcho process group changed"; exit 1; }
[ "$(ps -o tty= -p "$pid" | tr -d " ")" = "pts/0" ] || { echo "STOP: Honcho terminal changed"; exit 1; }
kill -s INT "$pid"
for i in $(seq 1 20); do
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "DEVELOPMENT HONCHO STOPPED: PASS"
        exit 0
    fi
    sleep 1
done
echo "STOP: Honcho did not exit within 20 checks; do not force-kill"
exit 1
'
```

**Postcondition required for Phase C1:** `DEVELOPMENT HONCHO STOPPED: PASS` *and* a separate targeted process check confirming managed web/socketio/watch/scheduler/worker children stopped. Do not switch source on the same command invocation. If no PASS or children remain, keep shared-code unchanged and investigate that actual blocker. Docker-managed DEVELOPMENT MariaDB and Redis remain running; do not interact with legacy `frappe_docker-*` PRODUCTION services.

**C1 next action when stopped:** re-run pinned Git/backup guards, then explicitly stage a source switch to the reviewed `0c223d7...` HEAD using the verified local fetch, preserving `AGENTS.md`. All valid site schemas must be migrated in a controlled period **before resuming ordinary use**, and the failed `ccpc-integration.localhost` is excluded. Stop on schema/master errors; Git rollback alone does not reverse a site migration. After successful app/site acceptance, restore DEVELOPMENT-only Honcho processes via a vetted start command and smoke-test both valid sites.

### Gate C — controlled shared-bench code change (separate operator approval required)

1. Prefer a reviewed isolated bench/container if available for no-downtime acceptance. If keeping the *existing shared bench*, schedule an explicit **DEVELOPMENT-only maintenance window** and verify operational isolation before stopping any DEVELOPMENT app workers/scheduler/web processes. Avoid generic Docker Compose commands which might affect legacy PRODUCTION on the same physical server.
2. Re-run Gate A and confirm Gate B recovery points. Prepare the pinned `0c223d7...` source in a separately identified staging checkout/worktree if feasible; verify the reviewed Git tree and Python/dependency compatibility without modifying the running app. Protect `AGENTS.md`; do not add it to Git.
3. Only after a reviewed, approved cutover mechanism is selected, move the **shared** app checkout to the **pinned** tested-code descendant (the `0c223d7...` review head), never to a floating default branch. Verify exact `HEAD`, branch/detached state, files and unchanged `AGENTS.md`.
4. Keep DEVELOPMENT services paused throughout the period where the shared code version does not match all intended site schemas. Do not resume ordinary main-site usage merely because the integration2 database migrates successfully; **both sites load the same Python source**. If preflight, checkout or migration fails, stop; do not attempt blind `git reset --hard` or automatic database reversal.

### D0 — Exact first integration2 migration after verified code switch

**Verified point-in-time operator output (2026-10-27):**
```text
OLD HONCHO LIVE PROCESSES: NONE
GIT SAFETY GUARDS: PASS
HEAD is now at 0c223d7 docs: record green CircleCI pipeline 10 for genuine Finance integration
DEVELOPMENT CODE SWITCH: PASS
0c223d7 docs: record green CircleCI pipeline 10 for genuine Finance integration
```
App checkout is now in detached HEAD, still with its single untracked `AGENTS.md`. Both independently verified site-local Oct27 four-artifact backups are protected outside auto-cleanup. CI passed isolated tests, **not** actual persistent site migration.

**First site migration has an additional site-specific DB/schema/data scope.** Owner may authorize this by deliberately executing the clearly marked guarded migration command below; the previous maintenance approval does not imply silent server execution by ChatGPT. Run once only, from Ubuntu host after confirming operator accepts integration2 database/roles/workflow/backfill changes. Keep shared Honcho-managed services stopped. No financial posting, restoration, Docker or PRODUCTION actions.

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
set -euo pipefail
cd /workspace/development/frappe-bench
test "$(git -C apps/ccpcerp rev-parse HEAD)" = "0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41" || { echo "STOP: App checkout differs"; exit 1; }
test -z "$(git -C apps/ccpcerp branch --show-current)" || { echo "STOP: App not detached at pinned revision"; exit 1; }
test "$(git -C apps/ccpcerp status --porcelain=v1)" = "?? AGENTS.md" || { echo "STOP: Working-tree state differs"; exit 1; }
for site in development.localhost ccpc-integration2.localhost; do
  test -s "sites/$site/site_config.json" || { echo "STOP: Site config missing: $site"; exit 1; }
  case "$site" in
    development.localhost) stem=20261027_075421-development_localhost;;
    ccpc-integration2.localhost) stem=20261027_104801-ccpc-integration2_localhost;;
  esac
  for suffix in database.sql.gz site_config_backup.json files.tar private-files.tar; do
    test -s "sites/$site/private/ccpc-preintegration-2026-10-27/fresh-backup/$stem-$suffix" || { echo "STOP: Protected set incomplete: $site"; exit 1; }
  done
done
if ps -eo pid=,pgid=,sid=,stat=,comm= | awk '"'"'($4 !~ /^Z/) && (($3==14 && $1!=14) || $2==193 || $5=="honcho") {bad=1} END {exit !bad}'"'"'; then
  echo "STOP: Live old Honcho process found"
  exit 1
fi
echo "GUARDS PASS — MIGRATING ONLY ccpc-integration2.localhost"
bench --site ccpc-integration2.localhost migrate
echo "INTEGRATION2 MIGRATION: PASS"
'
```

This **changes only integration2's site database** but may affect shared Redis/cache and assets; keep other site's access blocked until its own compatible schema is established. `bench migrate` may run pre/post patches, sync DocTypes/custom fields, make roles, modify workflows and backfill existing data. If an error occurs, do not run other site migration, switch checkout back, restore anything, kill services or force commands; retain the exact error for controlled diagnosis. If successful, verify migrated DocTypes/roles, pending patches and that the active code remains pinned, then plan the main site's own migration and both-site smoke tests before restart. Actual data restore remains untested and would need explicit recovery approval.

### D1 — Integration2 migration executed: PASS; focused schema/role verification next

**Operator transcript, 2026-10-27 (within approved DEVELOPMENT-only maintenance; GitHub verified target):**
```text
SAFETY GUARDS: PASS
MIGRATING: ccpc-integration2.localhost
Migrating ccpc-integration2.localhost
Updating DocTypes for frappe        : [========================================] 100%
Updating DocTypes for erpnext       : [========================================] 100%
Updating DocTypes for ccpcerp       : [========================================] 100%
Syncing jobs...
Syncing fixtures...
Syncing dashboards...
Updating Dashboard for frappe
Updating Dashboard for erpnext
Updating Dashboard for ccpcerp
Syncing customizations...
Syncing languages...
Flushing deferred inserts...
Removing orphan doctypes...
Removing orphan Workspaces
Removing orphan Dashboards
Removing orphan Pages
Removing orphan Reports
Removing orphan Notifications
Removing orphan Workspace Sidebars
Removing orphan Desktop Icons
Deleting icon Frappe Framework
Syncing portal menu...
Updating installed applications...
Executing `after_migrate` hooks...
Queued rebuilding of search index for ccpc-integration2.localhost
INTEGRATION2 MIGRATION: PASS
```

**Verified interpretation:** site migration command exited successfully, including DB-changing migration phases and `after_migrate`; no evidence of a finished search index rebuild, real Company/Account mapping validity, Maker/Checker signoff, transaction/posting tests, or another site migration. No claim that the second site is safe for live traffic before both sites are compatible and Honcho restarted. All protected pre-migration recovery files must stay intact.

**Immediate next read-only verification:** in *integration2's database only*, query `tabDocType` for four Finance Scope/Revision DocTypes, `tabRole` for `CCPC Mapping Preparer` and `CCPC Accounting Mapping Approver`, and `tabCustom Field` for the five new `Stock Entry Detail` provenance/revision fields. Validate exact expected counts (4,2,5) and stop on any mismatch. Then use a second, guarded owner-approved `bench --site development.localhost migrate` command with the same pinned source/backup/no-worker guards; do **not** re-migrate integration2 or run a combined multi-site migration blind. Continue with post-migration smoke tests and guarded DEV-only Honcho restart. Financial postings remain separately scoped.

### D2 — Integration2 Finance schema verified 4/4, 2/2, 5/5; main DEVELOPMENT migration next

**Owner-executed read-only MariaDB verification after successful `ccpc-integration2.localhost` migration:** following the three-part query against `tabDocType`, `tabRole`, and `tabCustom Field`, output was:
```text
check_name                      found  result
Finance mapping DocTypes           4   PASS
Finance mapping roles              2   PASS
Stock Entry provenance fields      5   PASS
```
The installed Finance mapping DocTypes are the Expense/Center **Scope** and **Revision** pairs; roles are `CCPC Mapping Preparer` and `CCPC Accounting Mapping Approver`; the five `Stock Entry Detail` provenance fields are `ccpc_equipment_at_issue`, `ccpc_equipment_code_at_issue`, `ccpc_item_group_at_issue`, `ccpc_expense_mapping_revision`, `ccpc_center_mapping_revision`. This is **schema presence**, not an actual authorized finance transaction test, migration-free rollback proof, user-role assignment verification, or full acceptance.

**Next explicitly chosen database write:** in the continuing approved DEVELOPMENT-only maintenance window, operator may elect to authorize the separate **main `development.localhost` site migration only** by deliberately running the following guarded command. It is a distinct scope from the completed integration2 database migration. Do not resume any shared Honcho-managed services beforehand.

```bash
docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 bash -lc 'bash -s' <<'SH'
set -euo pipefail
cd /workspace/development/frappe-bench
target="0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41"
test "$(git -C apps/ccpcerp rev-parse HEAD)" = "$target" || { echo "STOP: App HEAD mismatch"; exit 1; }
test -z "$(git -C apps/ccpcerp branch --show-current)" || { echo "STOP: Not detached on reviewed SHA"; exit 1; }
test "$(git -C apps/ccpcerp status --porcelain=v1)" = "?? AGENTS.md" || { echo "STOP: Unexpected Git changes"; exit 1; }
for site in development.localhost ccpc-integration2.localhost; do
  test -s "sites/$site/site_config.json" || { echo "STOP: Missing site config: $site"; exit 1; }
  case "$site" in
    development.localhost) stem="20261027_075421-development_localhost";;
    ccpc-integration2.localhost) stem="20261027_104801-ccpc-integration2_localhost";;
  esac
  base="sites/$site/private/ccpc-preintegration-2026-10-27/fresh-backup/$stem"
  for suffix in database.sql.gz site_config_backup.json files.tar private-files.tar; do
    test -s "$base-$suffix" || { echo "STOP: Missing recovery component: $site"; exit 1; }
  done
done
if ps -eo pid=,ppid=,pgid=,sid=,stat=,comm= | awk '($5 !~ /^Z/) && (($4==14 && $1!=14) || $3==193 || $6=="honcho") {bad=1} END {exit !bad}'; then
  echo "STOP: Live original Honcho process remains"
  exit 1
fi
echo "SAFETY GUARDS: PASS"
echo "MIGRATING: development.localhost"
bench --site development.localhost migrate
echo "MAIN DEVELOPMENT MIGRATION: PASS"
SH
```

This can alter *main DEVELOPMENT site's* schema, role definitions, workflows, custom fields and data/backfills via `after_migrate`, and may perform cache/asset operations affecting the shared bench. **If it fails, STOP:** do not run automatic rollback, `bench migrate` again, restart Honcho or touch PRODUCTION; retain exact error. On PASS, check identical four Finance DocTypes, two roles, five provenance fields in `development.localhost`, then evaluate/authorize a supervised DEVELOPMENT-only Honcho restart and both-site smoke tests. **Do not claim integration complete merely from migration PASS.**

### D3 — Main DEVELOPMENT migration executed: PASS; schema verification then controlled restart

**Operator-executed and reported from `gani@ccpcerpserver`:** the reviewed individually guarded `bench --site development.localhost migrate` returned:
```text
SAFETY GUARDS: PASS
MIGRATING: development.localhost
Migrating development.localhost
Updating DocTypes for frappe        : [========================================] 100%
Updating DocTypes for erpnext       : [========================================] 100%
Updating DocTypes for ccpcerp       : [========================================] 100%
Syncing jobs...
Syncing fixtures...
Syncing dashboards...
Updating Dashboard for frappe
Updating Dashboard for erpnext
Updating Dashboard for ccpcerp
Syncing customizations...
Syncing languages...
Flushing deferred inserts...
Removing orphan doctypes...
Removing orphan Workspaces
Removing orphan Dashboards
Removing orphan Pages
Removing orphan Reports
Removing orphan Notifications
Removing orphan Workspace Sidebars
Removing orphan Desktop Icons
Syncing portal menu...
Updating installed applications...
Executing `after_migrate` hooks...
Queued rebuilding of search index for development.localhost
MAIN DEVELOPMENT MIGRATION: PASS
```

**Interpretation:** second/last intended site's database migration was reported successful; schema changes and `after_migrate` ran. Separate integration2 Finance mapping DocTypes, roles and provenance fields check passed 4/4, 2/2, 5/5. Search-index rebuild is queued, not confirmed finished; no genuine Finance transaction, site-to-site billing, returns, reconciliation, permissions, or report acceptance proven. The shared DEVELOPMENT Honcho processes must stay stopped until main schema postcheck is complete and restart pathway is approved.

**Next operator action, read-only:** `bench --site development.localhost mariadb` on DEVELOPMENT container, query `tabDocType` for four mapping Scope/Revision DocTypes (expected 4), `tabRole` for two mapping roles (expected 2), and `tabCustom Field` for the five Stock Entry Detail issue-provenance/revision fields (expected 5). Report three PASS rows, stop if any mismatch. This does not perform further migration or reveal business data.

**Next after 3 PASS rows:** plan a DEVELOPMENT-only controlled Honcho restart: verify pinned app HEAD, `AGENTS.md`, current process absence, and start Honcho exactly once under a durable service session without touching shared host PRODUCTION. Validate web/session access to **both** valid sites, queues, roles/access, master/account configuration and later approved synthetic intercompany workflows. Do not treat a bench start as successful until process/HTTP checks pass.

### D4 — Both sites schema PASS; guarded DEVELOPMENT-only Honcho restart

**Owner's main-site postmigration MariaDB read-only query** yielded:
```text
check_name                      found  result
Finance mapping DocTypes           4   PASS
Finance mapping roles              2   PASS
Stock Entry provenance fields      5   PASS
```
It matches the previously verified **integration2** 4/2/5 PASS. Therefore both DEVELOPMENT databases now have the four Finance Scope/Revision DocTypes, two mapping role definitions and five issue-provenance/mapping revision custom fields. This does **not** demonstrate assigned user permissions, authorized real mapping approvals or financially safe stock/invoice postings.

**Restart scope:** during already approved DEVELOPMENT maintenance window, start only the five Procfile services through the **single Frappe DEVELOPMENT container** `frappe_docker_devcontainer-frappe-1`. Never use Docker Compose or affect MariaDB/Redis/legacy PRODUCTION. A `docker exec -d --user frappe` Honcho process can outlive the temporary host invocation and preserve logs, but it is not a formally managed OS service, can disappear on container recreation, and log rotation for its dedicated log needs future operations review. This is a DEV-only continuity mechanism matching the previously interactive Honcho process, not a PRODUCTION process supervisor.

At Ubuntu host prompt, execute a fail-closed preguard on exact app pinned SHA, empty detached branch name, sole `AGENTS.md` untracked file, expected `Procfile`, and absence of any running Honcho process; then a **single detached Honcho** launch, and finally report the new PID. Actual web/socketio/scheduler/worker readiness requires the next smoke-check; PID alone is not full startup proof. The launch uses the previously verified executable `/home/frappe/.local/bin/honcho`, a private bench log, and `umask 077` for newly created output.

```bash
set -euo pipefail
dev=frappe_docker_devcontainer-frappe-1
docker exec --user frappe "$dev" bash -lc '
set -euo pipefail
cd /workspace/development/frappe-bench
test "$(git -C apps/ccpcerp rev-parse HEAD)" = "0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41" || { echo "STOP: App HEAD changed"; exit 1; }
test -z "$(git -C apps/ccpcerp branch --show-current)" || { echo "STOP: Unexpected app branch"; exit 1; }
test "$(git -C apps/ccpcerp status --porcelain=v1)" = "?? AGENTS.md" || { echo "STOP: Git working tree changed"; exit 1; }
test -s Procfile && test -d logs || { echo "STOP: Bench run files unavailable"; exit 1; }
if pgrep -x honcho >/dev/null; then echo "STOP: Honcho is already running"; exit 1; fi
echo "DEVELOPMENT RESTART GUARDS: PASS"
'
docker exec -d --user frappe "$dev" bash -lc '
set -euo pipefail
umask 077
cd /workspace/development/frappe-bench
exec /home/frappe/.local/bin/honcho start >> logs/ccpc-dev-honcho-20261027.log 2>&1
'
sleep 5
docker exec --user frappe "$dev" bash -lc '
set -euo pipefail
pid=$(pgrep -x honcho | head -n 1 || true)
test -n "$pid" || { echo "STOP: Honcho was not found after launch. Review private bench log."; exit 1; }
echo "DEVELOPMENT HONCHO STARTED: PID=$pid"
ps -o pid,ppid,stat,etime,args -p "$pid"
'
```

**Operator note:** if startup guard fails, stop and report; do not repeatedly launch or restart Docker. If Honcho is present but child apps fail, inspect **DEV-only** `logs/ccpc-dev-honcho-20261027.log` with bounded safe output (sanitize secrets), then repair separately. Next step after successful start is two-site HTTP response/scheduler/worker smoke test, process identity and configured origin checks; avoid writing financial business data. Keep integration acceptance distinct from migration schema success.

### D5 — Honcho restart launched: PID 380905; both-site HTTP ping next

**Owner-executed D4 command output**:
```text
DEVELOPMENT RESTART GUARDS: PASS
DEVELOPMENT HONCHO STARTED: PID=380905
PID    PPID STAT ELAPSED COMMAND
380905 0    Ss   00:05   /home/frappe/.pyenv/versions/3.14.2/bin/python3.14 /home/frappe/.local/bin/honcho start
```
The command launched `honcho start` detached in DEVELOPMENT container `frappe_docker_devcontainer-frappe-1` with log `logs/ccpc-dev-honcho-20261027.log`. Container namespace PID may change on process death/relaunch. The PID+five-second uptime is **not proof that Frappe HTTP works for both sites or that scheduler and queue workers are healthy**.

**Next focused read-only operator test**, executed from Ubuntu host and scoped strictly to the DEVELOPMENT Frappe container, sends a local HTTP request to `/api/method/ping` via web listener port 8000 with both Host and X-Frappe-Site-Name explicitly selected. No accounts, business records or database writes are created.
```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
set -euo pipefail
cd /workspace/development/frappe-bench
test "$(git -C apps/ccpcerp rev-parse HEAD)" = "0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41" || { echo "STOP: App checkout moved"; exit 1; }
if ! kill -0 380905 2>/dev/null; then echo "STOP: Started Honcho PID 380905 is not running"; exit 1; fi
for site in development.localhost ccpc-integration2.localhost; do
  code=$(curl --silent --show-error --output /dev/null --write-out "%{http_code}" --connect-timeout 3 --max-time 15 -H "Host: $site" -H "X-Frappe-Site-Name: $site" http://127.0.0.1:8000/api/method/ping) || { echo "STOP: HTTP probe failed for $site"; exit 1; }
  if [ "$code" = 200 ]; then echo "HTTP PING PASS: $site (200)"; else echo "STOP: HTTP $code for $site"; exit 1; fi
done
echo "BOTH DEV WEB PINGS: PASS"
'
```
If a request fails, keep exact output and inspect **only** the named DEVELOPMENT Honcho log with bounded/sanitized reads; do not re-run migrations, auto-restart, or touch shared host services. If both pass, proceed to supervised worker/scheduler readiness and both-site functional UI/API smoke testing; approval for financial postings remains distinct.

**D5 result (owner terminal, 2026-10-27):** Both intended DEVELOPMENT HTTP pings returned `200` and the script printed `BOTH DEV WEB PINGS: PASS`. The guard checked exact CCPC app SHA and Honcho PID before the requests. The next immediate operator action is a **read-only process inventory** for Honcho-managed `web`, `socketio`, `watch`, `schedule` and `worker`; actual background scheduler/queue function still needs separate verification. No new migration, restart, financial posting, backup work or PRODUCTION action is authorized by D5.

### Gate D — site-scoped migrations and persistent acceptance (separate explicit approval)

1. Reconfirm site-specific DB name/host, snapshot, prerequisites and pending patches. Run approved migration for **`ccpc-integration2.localhost` first**. Monitor patch/DocType/workflow outcomes and fail on errors.
2. Test the intended new DocTypes, safe Finance mapping maker/checker role separation, original issue provenance, Withdrawal lifecycle, intercompany invoice transaction atomicity, cancellation/return behavior, duplicate-prevention and stock/GL reconciliation. Use synthetic approved test masters, never live financial mappings inferred from labels. Test postings require their own approved fixture and cleanup/rollback scope.
3. Before resuming normal shared-bench operation, review and approve migration/verification for `development.localhost` using its **independent** fresh snapshot. If any site must remain on an old schema, an isolated separate bench is needed; do not run two schema generations indiscriminately against one checkout.
4. Record precise commands, errors, DB/migration evidence, regression test totals, code SHA, expected/unexpected row and permission changes, and recovery actions. Failed migration is not resolved by switching Git source back: schema/data recovery is a separate decision.
5. Resume only verified DEVELOPMENT services and run smoke tests on **both** intended sites; ensure no legacy PRODUCTION container/mount/config/port was affected. Recheck `AGENTS.md` and working-tree integrity.

### Gate E — report completion, review and release boundaries

- The four owner-approved day-one operational reports are **not yet implemented** on the reviewed app branch: Department consumption; Equipment/Job Order consumption; intercompany Withdrawal/billing with invoice state; consolidated material consumption versus distinct P&L/GL expense with unit-safe SLE/GL reconciliation. Implement/test on a **GitHub review branch** without re-scoping requirements.
- True end-to-end returns, cancellations and invoice submission remain to be validated. A persistent DEVELOPMENT PASS cannot be claimed solely from pipeline #10 or a migration command exiting zero.
- Require actual Company + leaf Item Group → Expense Account and Company + beneficiary Department → Cost Center mapping approvals, separate authorized maker/checker accounts and Company-scoped permissions before business posting.
- Keep dedicated PRODUCTION infrastructure review separate (draft PRs #27/#29/#30 at previous verified checkpoint). No PRODUCTION deployment, migration, restart, data restoration or cutover without independent authorization, tested recovery and DEVELOPMENT acceptance.

## 4. Stop conditions and authority

**STOP** on any branch/SHA/status mismatch, untracked path collision, missing or stale recovery point, incomplete restore requirements, site DB ambiguity, unexpected Patch Log contents, unsatisfied Company/Account prerequisites, unexpected running shared worker, migration errors, or inability to preserve the other site's service/schema state.

**Authorized as of October 27:** GitHub inspection, the completed DEVELOPMENT-only two-site backup preservation/creation and verification, and the owner-approved temporary DEVELOPMENT maintenance window including a guarded graceful Honcho shutdown.  
**Not independently authorized:** unreviewed application checkout/DB migration beyond the controlled subsequent steps, financial posting, broad Docker stop/restart, any PRODUCTION operation, unapproved restore or automated reporting. Stop on preflight mismatches.

**Historical D5 status (superseded by D6 result):** D5 two-site HTTP pings are 200/PASS; Honcho PID `380905` survived 27:22 with 25 descendants. The two site-specific `bench doctor` commands completed successfully, each reporting `Workers online: 1` (one shared-bench worker), no scheduler-disabled/paused/inactive/maintenance warning and no listed jobs. The operator's read-only historical scheduler query now confirms 4/4 frequent-job types with recorded starts on both sites and thousands of historical Complete logs; however, main site's newest start is `10:30:03`, newest Complete log `10:02:14`, versus integration2's newest start/Complete `13:00:08`/`13:00:13` on October 27. A corrected main-site SQL check now confirms `NOW()=UTC_TIMESTAMP()=2026-10-27 05:23:51` with `@@session.time_zone=SYSTEM` (effective UTC; equivalent to 13:23:51 in Asia/Manila). The preceding read-only syntax error was due to the `utc_time` alias. **Follow-up read-only site timezone and four-job checks PASSED:** main site `Asia/Kolkata` recorded four frequent starts at `10:58:02` (~50 seconds before its corresponding Kolkata 10:58:52 clock); Integration2 `Asia/Manila` recorded four frequent starts at `13:28:00–01` (~51–52 seconds before 13:28:53). The apparent 2h30 discrepancy is exactly the timezone-offset difference, not evidence of a lagging main scheduler. Do not infer completed job success from start timestamps alone. Next owner decision: retain intentional Kolkata setting or separately authorize DEVELOPMENT-only main-site timezone change to `Asia/Manila`, with targeted timestamp/calendar validation; do not change global DB/host settings, enqueue jobs, or touch PRODUCTION. Running/registered processes alone do not establish successful job execution. Do not re-run backups/migrations, force scheduler jobs or restart services; no PRODUCTION changes.

### D6 — Approved single-site DEVELOPMENT timezone alignment (operator execution pending)

**Owner authorization, 2026-10-27:** Change only `development.localhost` System Settings `time_zone` from `Asia/Kolkata` to `Asia/Manila`. Keep `ccpc-integration2.localhost` already at `Asia/Manila`. This approval is DEV-site-specific and excludes production, host/DB timezone, service restart, schema migrations, backup repetition, financial postings or other business settings.

Use a fail-closed pinned-app and clean-tree preflight, verify exact old and other-site timezone, then invoke Frappe v16 `bench --site development.localhost execute` to call the **System Settings Document.save() ORM path**, which validates and triggers `on_update` cache/default updates. Read and compare time_zone of both sites after, then follow-up scheduler tick and UI display. Do not substitute raw SQL or bypass document hooks. Owner executed the single-main-site guarded ORM save after explicit approval and independently verified both site values `Asia/Manila` (**PASS**). GitHub documentation now records the result; no other DEV settings or PRODUCTION state were changed. Read-only fresh postchange scheduler check PASSED on both sites: each now uses `Asia/Manila`, all four frequent jobs had start timestamps around `13:48`, and the Manila reference clock was `13:50:52` on October 27. This confirms fresh frequent-job starts, not individual execution success.

### D7 — Verified approved timezone alignment; site scheduler postchange health pending

**Owner terminal:** `BEFORE: main=Asia/Kolkata; integration2=Asia/Manila`; `PRECHANGE GUARDS: PASS`; `MAIN DEV TIMEZONE SAVE COMPLETED`; `AFTER: main=Asia/Manila; integration2=Asia/Manila`; `DEVELOPMENT TIMEZONE ALIGNMENT: PASS`. Only main DEV System Settings was changed via Frappe ORM; pinned reviewed app and protected `AGENTS.md` preguards passed. PRODUCTION untouched.

**D7 owner-provided result:** At Manila reference clock `2026-10-27 13:50:52`, `development.localhost` now reports timezone `Asia/Manila`, 4 enabled frequent scheduled jobs, oldest start `13:48:04.433605`, newest start `13:48:08.344874`. `ccpc-integration2.localhost` reports timezone `Asia/Manila`, 4 enabled frequent scheduled jobs, oldest start `13:48:01.066748`, newest start `13:48:03.351225`. Both had fresh natural starts within approximately 2m44–52s of verification; script completed with `POSTCHANGE SCHEDULER CHECK: COMPLETED`. **D7 postchange scheduler start-time check: PASS.** Job start timestamps do not guarantee successful job completion. **Next:** read-only per-site HTTP ping postchange, then separately scoped authenticated UI and Finance maker/checker permissions smoke checks; do not run financial postings without approved fixtures.


### D8 — Both DEV web pings PASS after timezone change; Finance authority inventory next

**Owner output:** `development.localhost: HTTP 200`, `ccpc-integration2.localhost: HTTP 200`, `POSTCHANGE TWO-SITE WEB CHECK: PASS`. Both sites remain set to `Asia/Manila` and have fresh four-job scheduler starts after the approved DEV-main Frappe settings change. Schema 4/2/5 checks, Honcho/web/worker/doctor/scheduler checks and Oct 27 protected recovery copies are verified as above; no rework required. This is a **runtime smoke PASS**, not authenticated app acceptance or job-success proof.

**Next operator action:** With the pinned app SHA guard, perform **read-only per-site aggregate Finance authority inventory** for the two required roles (`CCPC Mapping Preparer`, `CCPC Accounting Mapping Approver`). Code inspection of reviewed `bc_issue_runtime._real_authority` confirms actor must be a real enabled non-Administrator/non-Guest User with explicit `tabHas Role` assignment, a valid `tabUser Permission` grant for a Company (`allow='Company'`, `apply_to_all_doctypes=1`, `applicable_for` empty), and **no** `Stockroom Personnel` role. Report role-user and qualifying Company-grant counts only; do not reveal identities, write grants, or create finance mappings. Role existence 2/2 does not imply actual users are authorized; maker/checker distinctness and matched Company must be tested separately before authenticated workflow. Avoid transactions/posting until owner approves isolated synthetic fixtures.

### D9 — Finance authorization inventory BLOCKED: zero eligible maker/checker users on both sites

**Owner's read-only aggregate SQL result, both DEVELOPMENT sites:** For both `CCPC Mapping Preparer` and `CCPC Accounting Mapping Approver`, `enabled_nonstockroom_users=0`, `users_with_company_grants=0`, and `companies_with_eligible_users=0`. Script returned `BOTH DEV FINANCE ROLE INVENTORIES: COMPLETED`. These results confirm **no currently eligible Finance mapping actors** on either site; they do not determine whether no role memberships exist or only ineligible accounts carry them. Role definitions are migrated (2/2), but authorization/grants are a separate acceptance gate.

`bc_issue_runtime._real_authority` in the reviewed app requires a real enabled named User (not Administrator/Guest), assigned the exact Finance role, granted exact Company through `tabUser Permission` with `allow='Company'`, `apply_to_all_doctypes=1`, empty `applicable_for`, and not assigned `Stockroom Personnel`. `bc_mapping_workflow` additionally requires separate real maker/checker identities and reviewed eligible Company/master mappings. No migration, role grant, mapping proposal, approval, stock/GL transaction or PRODUCTION action is implied or authorized by this gate.

**Next read-only action:** Per-site role assignment counts for the two roles, distinguishing assigned vs enabled named vs disabled/admin vs Stockroom-excluded, plus total Company count; no username or Company data output. If no eligible roles exist, obtain owner-approved two distinct DEV users/role grants for an explicitly chosen Company before attempting Finance mapping workflow. **Do not silently create or assign Finance roles, company permissions or synthetic business masters**. Review and obtain separate authority and rollback plan for any user/grant changes.
