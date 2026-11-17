# CCPC ERPNext — 30-day first-release execution tracker

**Started:** 2026-11-17 (Asia/Manila). **Target decision / limited go-live: by 2026-12-17** if all technical, accounting and operational gates PASS. **Owner-approved product scope:** use the already-tested custom CCPC Withdrawal Slip, independent Stockroom Material Issue, genuine native SLE/GL, Department material cost register and native ERPNext accounting. **Same legal Company only.** CCPC↔Ricor billing deferred. Do not re-scope back to manual native Material Request as the main release workflow.

**Status:** Source preparation IN PROGRESS, **not** approved to ship. Release candidate draft app [PR #35](https://github.com/ccpcerp/ccpcerp/pull/35) created on `release/withdrawal-department-phase1-2026-11-17` from tested Finance feature SHA `a2f0e89f12afbc28ac10dab71b6af47a455fdc95`. Latest initial head `25b14e58f724e1bb787856b0a3e7ee1f4fd45ac1` (reverify before pull/tests). Five changed files, no DocType schema patch in PR35. Existing draft PR33/34 and persistent CCPC↔Ricor MAIN DEV batch/invoice pair untouched.

## Exactly what the first release must do

1. A named user submits approved **CCPC Withdrawal Slip** with correct *same* issuing/requesting Company, actual beneficiary Department, original Item/UOM/warehouse, requested and issued quantities.
2. Distinct authenticated **Stockroom Personnel** issues exactly once; native `Stock Entry` Material Issue is submitted; verify stock balance decrease and original Stock Ledger Entry by voucher/detail; negative role/duplicate/race/rollback paths reject.
3. Historical-at-approval **real** Finance maker and checker mapping evidence selects exact Company+frozen original leaf Item Group→Expense Account and Company+actual beneficiary Department→Cost Center. Department dimension and original SLE/GL Expense entry reconcile at supported voucher grain, with Account, Center and Company source visible. Missing/stale mappings, mismatched beneficiary, wrong Company and backdated requests reject before posting.
4. **CCPC Department Material Consumption** report shows original issue date, Item, Department, quantity by actual stock UOM, gross original SLE value and source quality. The existing Script Report is specifically **gross SLE**, not certified net Department P&L: cross-check separately against actual posted ERPNext GL/Cost Center. Do not sum SLE + GL or mix Companies, currencies or UOM.
5. Legacy cross-Company withdrawals and new intercompany batch/SI/PI API action **not available** in this release. Staff use standard ERPNext for routine functions beyond this small CCPC customization.

## Weekly acceptance path — deadline-driven but safety-gated

| Window | Deliverable / exact test evidence | Current status |
| --- | --- | --- |
| **Nov 17–23** — scope and release isolation | Draft PR35 source review, all pure policy and Frappe route regression, safe Company scope and billing-denial audit, inspect inbound migrations/hooks and past test evidence, **one current read-only production service+NAS+security check** to decide old-host pilot. Confirm named real Finance/Stockroom actors and exact mapping availability. | **PARTIAL:** branch and draft PR created; five pure Python policy tests **5/5 PASS** in an isolated temporary environment, source/test SHA1 byte matched GitHub; three new installed-Frappe tests **NOT RUN**, real ledger current-source acceptance **NOT RUN**; current production status **NOT RECHECKED**. |
| **Nov 24–30** — integrated correctness & DEVELOPMENT | One *authorized* disposable actual Frappe/ERPNext/MariaDB regression on exact release SHA (same Company positive + cross Company denial, Stock Entry→SLE/Expense GL, original Department report), actual permissions, then protect MAIN DEV untracked work and create **fresh post-Draft local + NAS** backup before any persistent DEV change; complete operator-scoped DEV pull/migrate/UAT and fix/record issues in GitHub. | **PENDING:** source testing and protection gates. |
| **Dec 1–7** — production readiness and staff walkthrough | Decide old shared-host legacy PROD vs separate new host based on current security and rollback evidence; confirm database/Item/Account/Center/Department masters, role grants and fiscal start; genuine separate recoverable four-part local/off-host backup/restore rehearsal, controlled tested rollout and rollback procedure; staff training and operational runbook. | **PENDING:** old LAN PROD historically served HTTP login; its **current** state, security and restore not verified. New dedicated host only partly built. |
| **Dec 8–17** — release decision, pilot and stabilization | Reviewed exact GitHub release code/merged state, latest DEV real data and ledger/report signoff, Company/users/training, rollback timebox and owner authorization. Controlled small-user PRODUCTION deployment **only after separate explicit approval**, one supervised same-Company posted test, verify GL/SLE/Department report, operate/monitor, then plan R1 small follow-ups. | **NO-GO** until all gates pass. |

**If a mandatory gate fails, defer that production write, not the safety standard.** Target date is an operating deadline, not a promise or justification for backdated or synthetic Finance signoff. Avoid repeating unrelated infrastructure audits or old green CI suites.

## Immediate GitHub changes and test truth

- **PR35 source**: `ccpcerp/ccpc_erp/phase1_release_scope.py`, `withdrawal_slip_stock.py` (both Stockroom and direct linked Stock Entry pathways, including `requesting_company` locked-state comparison), `doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` (fail-closed billing mutators/whitelisted methods), `test_phase1_release_scope.py`, `test_phase1_release_routes.py`.
- Pure tests locally executed: **5 test methods PASS** in a temporary `ccpcerp` package without Frappe; Git SHA1 for reconstructed policy `699802c12aba2c316e48cfbabb6b58d59ebcca23` and policy test `8071928c01b73b9d0f7d59968325d4ecd42fae3a` equal verified GitHub content blob IDs. **Do not claim genuine Frappe/MariaDB PASS**.
- Three more Frappe route mock tests were committed but **NOT RUN**; can be executed in a disposable installed-Frappe test environment, not persistent MAIN or PRODUCTION.
- Earlier Finance+Withdrawal native tests: Build #34 **12/12 PASS**, Department Build #40 **20/20 PASS**, four reports Build #52 **86/86 PASS**, current feature base PR33 body cites Build #131 **15/15** (provider log not independently read during this milestone). This evidence justifies reuse, not blindly shipping an altered candidate.
- Critical open review: custom intercompany controller disabled **for user-level mutations**, but verify other external entry points, native invoice DocPerm and migration patches. Calling an API disabled because its button is hidden is not sufficient.
- No CI provider run, DEV/PROD command, migration, posting, restore, role grant, backup change or release was carried out by source-only updates.

## One next action — old-host production status READ ONLY

Owner may run the command below on the **existing** `ccpcerpserver`, returning only summaries of service state and expected NAS mount. It performs no Docker/container/site writes:

```bash
docker ps --filter 'label=com.docker.compose.project=frappe_docker' \
  --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
findmnt -n -o TARGET,FSTYPE,SOURCE /mnt/erpnext_backups
```

After checking this output, make the **single next** current host read-only safety check (actual ERPNext version, recent backup restore evidence, HTTPS/access). Don't broaden into a long re-inventory if existing evidence is already trusted. Never run `docker compose up`, `bench migrate`, `bench update`, `bench restore`, `git reset/clean`, `bench start`, native `submit`, or direct PRODUCTION changes as a diagnostic.

**Release lead boundary:** GitHub → approved source review → safe DEVELOPMENT pull and signoff → separate owner-approved PRODUCTION plan. Original approved MAIN DEV intercompany source/Draft invoices must never be replayed or altered for R0. No automatic paid OpenAI/API/CircleCI runs.
