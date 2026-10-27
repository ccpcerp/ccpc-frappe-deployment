# CCPC ERPNext — Controlled DEVELOPMENT app integration and acceptance plan

**Prepared:** 2026-10-27 (Asia/Manila)  
**Status, updated 2026-10-27:** Owner-executed DEVELOPMENT-only maintenance reached the reviewed **pinned app checkout**. Old Honcho was gracefully stopped and a guarded session check showed only an exited zombie (PID 197, `Z`); a second guarded live-process check returned `OLD HONCHO LIVE PROCESSES: NONE`. Owner-executed Git switch to detached `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` returned `GIT SAFETY GUARDS: PASS` and `DEVELOPMENT CODE SWITCH: PASS`; untracked `AGENTS.md` remains. Both DEVELOPMENT backups are preserved/format-verified. **Migrations have NOT run; five Honcho-managed DEVELOPMENT services remain stopped.** PRODUCTION excluded.

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

**Next concrete operator action:** deliberately authorize and execute the D0 single-site `ccpc-integration2.localhost` guarded migration command, **only if accepting that site-specific DB change**, while Honcho remains stopped. On PASS, validate integration2 then prepare the main site's distinct migration; on error, STOP.
