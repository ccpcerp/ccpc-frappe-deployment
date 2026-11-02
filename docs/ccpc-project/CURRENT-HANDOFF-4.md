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
