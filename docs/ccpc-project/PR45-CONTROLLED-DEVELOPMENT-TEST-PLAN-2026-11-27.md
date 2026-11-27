# CCPC ERPNext — PR #45 controlled DEVELOPMENT test plan

**Plan prepared 2026-11-27; status: reviewed preparation, NOT deployment authorization.** Read [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [CURRENT-HANDOFF-5.md](CURRENT-HANDOFF-5.md) before execution. The owner said "Approved" to preparing the next PR45 controlled DEVELOPMENT testing milestone; this is **not** interpreted as blanket authorization for `bench migrate`, app checkout changes, service restarts, new live Finance mapping decisions, stock posting, or PRODUCTION.

## Source-of-truth pins and completed evidence

- Application: [DRAFT PR #45](https://github.com/ccpcerp/ccpcerp/pull/45), branch `review/stockroom-center-proposer-2026-11-27`, exact tested HEAD **`afcc7b48ff8c664b0b0c781f89864995b9a59691`**, open/draft/unmerged at plan review.
- DEVELOPMENT last operator-verified application HEAD **`e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5`**, detached, clean, expected origin, exact DEV host `ccpcerpserver`, container `frappe_docker_devcontainer-frappe-1`, bench `/workspace/development/frappe-bench`, site `development.localhost`. **Re-check immediately before each write.**
- Direct GitHub compare `e5c6f4...afcc7b4`: **24 ahead, 0 behind**, 16 changed files. Changes include Finance proposal runtime/page, protected Finance DocType deny hooks and migrate cleanup, tests and isolated GitHub Actions workflows; no schema field JSON changes found in the PR patch.
- Two successful hosted runs on that exact HEAD: [isolated unit/UI #45940149294](https://github.com/ccpcerp/ccpcerp/actions/runs/45940149294) (16 Python; 5 Playwright) and [disposable Frappe/MariaDB #45940149308](https://github.com/ccpcerp/ccpcerp/actions/runs/45940149308) (10 security; 1 real DB acceptance); do not confuse these with testing against persistent CCPC DEVELOPMENT.
- Actual DEVELOPMENT read-only baseline already verified: nine Finance private DocTypes PRESENT with **0 standard and 0 custom DocPerm rows each**; `Main - CCPC` exact enabled CCPC leaf Cost Center; named `stockroom@personnel1.com` enabled, `Stockroom Personnel=1`, `CCPC Mapping Preparer=1`, `Accounting Approver=0`, `System Manager=0`, **exactly one** Company grant for CCPC, `apply_to_all_doctypes=1`, empty `applicable_for`, `is_default=0`, `hide_descendants=1`. The v2 permission change is **DONE** and **neither v1 nor v2 permission operator script must rerun**.
- Two enabled Controller-labeled users have the checker role and CCPC grants, but which human will sign any real Finance decision still requires a separately recorded authorization. A synthetic `.invalid` user must not act as operational signer.

## Significant migration risk — DO NOT skip this review

New PR45 code adds `finance_doctype_security.py`, document/list permission hooks for **nine pinned private Finance DocTypes**, and a guarded cleanup at the beginning of `ccpcerp.setup.after_migrate`. The helper scans all nine standard and custom DocPerms before deleting only the exact Frappe v16 default `System Manager` grants. It **fails closed** on unexpected or custom rows; current DEVELOPMENT inspection found zero grant rows, but re-check after any Frappe DocType sync and before migration as practical.

**The existing full `ccpcerp.setup.after_migrate()` is not a Finance-only migration.** It also invokes these persistent site routines: Department/Section seeding, Equipment Section and Personnel Company backfills, Maintenance/Supervisor role and permission setup, module profiles and desktop layout resets, MRS/procurement/purchasing/approval workflow setup, Stockroom permissions, Stock Entry/Withdrawal Slip custom fields and workflows, and Withdrawal Slip Issue Qty backfill. These are intended to be idempotent but may create/update/delete real configuration or master records. For example, `ensure_stockroom_personnel_permissions()` deletes selected legacy `Custom DocPerm` records and `reset_maintenance_supervisor_desktop_layouts()` deletes saved desk layout records. **Do not claim `bench migrate` is limited to the new nine-DocType cleanup.** Review the actual current site deltas, backup, and affected users/workflows before authorizing this broader mutation. A source checkout without migrate does not itself prove the required hooks/assets/effective runtime are loaded.

## Controlled sequence with separate gates

### Gate A — Preparation and immutable baseline (approved preparation / read-only)

1. Re-check DEVELOPMENT host, exact separate Docker container, site, installed app SHA, clean tracked **and untracked** Git status, trusted origin, detached HEAD, and Synology mounted CIFS target. Stop on any unexpected value. Never reset, clean, switch, or stash away user changes.
2. Obtain a **fresh** `development.localhost` with-files backup before any source update or migration. The 2026-11-25 `ccpc-dev-preupdate-20261125_143912` NAS backup had four nonempty files, previously passed archive checks and 4/4 source/NAS SHA256 checks, but predates the new stockroom Company grant and has **no verified restore**. Treat it as historical recovery evidence, not a current pre-migration restore point.
3. Validate a fresh backup **without exposing the site configuration or dump contents**: site-scoped command success, nonempty SQL gzip, both file tar archives, nonempty config backup, `gzip -t`, `tar -tf`, exclusive named NAS copy, individual SHA256 equivalence. Preserve original backups and observe available NAS space. A restore rehearsal in an isolated disposable environment is preferable before accepting wide migrations; never restore over live DEVELOPMENT by default.
4. Independently snapshot sanitized read-only baseline: nine private Finance DocTypes standard/custom DocPerm counts, CCPC `Main - CCPC` Cost Center master, Stockroom exact Company grant and role counts, permitted real Checker role/grants, representative MRS/Withdrawal Slip state (especially `WS-2026-00008` staying Draft), and audit targets for migration-altered role/workflow/config. Avoid copying confidential lists or raw data into GitHub.
5. Review `setup.after_migrate` and named routines against site baseline. Identify any unexpected changes, including legacy Custom DocPerm deletions, User/Role assignments, Workflow/desktop layout updates and Master backfills; stop and request a specific plan if anything is unsafe.

### Gate B — Explicitly authorized source update only (NOT approved by this plan)

After Gate A passes and the owner approves **this exact DEVELOPMENT source-update operation**, a reviewed operator-owned command may:
- Verify protected checkout and expected old HEAD `e5c6f4...`, clean tree and trusted origin; fetch only PR45 branch from canonical GitHub with strict SSH host verification.
- Verify fetched `FETCH_HEAD` equals exact reviewed HEAD `afcc7b48...`, that old HEAD is an ancestor, that diff check passes, and that no user changes appeared in between.
- Switch to a detached exact commit through a safe, non-force procedure **only after all guards**, report resulting HEAD/clean tree, and stop. No `git pull` against unknown default, `reset --hard`, destructive cleanup, service restart, or PRODUCTION action.
- Treat this as a code checkout milestone, NOT a verified live Frappe feature or database migration. Rollback of code to an old SHA cannot reverse a database migration.

### Gate C — Explicitly authorized persistent DEVELOPMENT migration (NOT approved by this plan)

After fresh backup/recoverability and documented risk review, separately approve the **exact** `bench --site development.localhost migrate` operation and any required scoped cache/build/restart. Verify that such commands target only the pinned DEVELOPMENT container/site. Plan for potential failure/partial writes and Frappe migration's wider `setup.after_migrate` effects. Do not invoke `harden_finance_mapping_doctype_permissions` manually outside install/migrate. Do not install or update framework versions in this step. Stop on any failure and independently audit actual DB/checkout state before proposing rollback; no unreviewed live database restore.

### Gate D — Independent DEVELOPMENT functional and security acceptance

- Confirm exact new app SHA and installed app framework versions, completed migration, hook registration, and all nine protected Finance DocTypes effectively deny normal document and list/report rights to unauthorized users, including System Manager, with zero non-default DocPerm/Custom DocPerm rows.
- Verify real Stockroom + Preparer account (CCPC-only Company grant) can see **Center-only** context, no Expense candidate access and no Finance signature authority; only exact existing `Main - CCPC` Center candidate is offered. A real named independent Finance Controller has checker authority only. Confirm `Administrator`/test users do not substitute for actual Finance approvals.
- First exercise read-only context, role/permission and master search endpoints; avoid creating a real mapping Draft or Accounting Decision until separately approved as actual business data. If approved later, verify single draft, independent signer, provenance, no replay/duplicate approval and no unintended accounts/SLE/GL.
- Re-audit existing operational roles and legacy workflows to detect drift from broad `after_migrate`, plus `WS-2026-00008` unchanged in Draft status. Never issue stock/GL during this phase.
- Record exactly what is **GitHub CI-tested**, **persistent DEV-tested**, and **still unverified**. If failures require code changes, commit them to a reviewed GitHub branch and repeat bounded disposable tests before another DEV update.

## Safety and authorization summary

**Allowed now:** GitHub plan/source review, non-mutating preparation, and a guarded read-only DEVELOPMENT preflight. No new on-server code, schema or business-record changes authorized solely by this planning approval. This plan may be committed to GitHub as documentation.

**Requires separate explicit authorization:** fresh site backup execution where it writes archival files, actual DEVELOPMENT Git checkout update, `bench migrate`, build/cache/restart, user roles/permissions, real mapping Draft/signature, stock entry or accounting entries. The exact user-approved Company User Permission change was separately completed and verified already.

**Never without explicit production deployment approval:** connect to, restore, restart, migrate or change PRODUCTION. No autonomous paid Codex reporting/cron actions or unreviewed credentials.

**Fast path:** Validate fresh full backup + tight baseline, apply reviewed exact PR45 source commit, migrate only after impact approval, then run real-role read-only acceptance against DEVELOPMENT. Hosted disposable CI already passed and need not be repeated unless the source changes.
