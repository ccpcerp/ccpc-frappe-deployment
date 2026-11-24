# CCPC ERPNext — Proposed Phase 1: Withdrawal to Departmental Cost Reporting

**Prepared:** 2026-11-17 Asia/Manila. **Decision status: PROPOSAL ONLY, pending owner confirmation of same-Company boundary and Finance accounting signoff. PRODUCTION NO-GO.**

## Executive decision proposal

The owner is considering **a partial PRODUCTION release** whose immediate business outcome is Withdrawal Slip → independently authorized stockroom issue → native posted Material Issue / SLE + approved Expense GL / Department and Cost Center → trustworthy departmental consumption and cost reporting. The complex **CCPC→Ricor intercompany material billing/Draft SI/PI correction can be deferred to Phase 2** if Phase 1 **restricts issuance to stock issued by, and consumed by a Department of, the same legal Company**. Do **not** conflate source-Company stock expense with a different Company's booked operating expense.

**The owner has NOT authorized any production deployment, production DB migration, branch merge, or change to real existing approved DEV batch/Draft invoices.** Owner agreement on release scope must be obtained before implementing exclusion, feature gates or release packaging.

## Phase 1 acceptance scope (proposed)

1. Department requester prepares Withdrawal Slip with valid Item, quantity, warehouse, requesting Company and source Company; documented Supervisor/Department approvals and immutable business intent.
2. A distinct authenticated Stockroom Personnel user processes the approved slip using the reviewed `issue_withdrawal_slip` route; exactly one native submitted ERPNext `Stock Entry` Material Issue, exact Stock Ledger Entry and proper General Ledger expense/stock effects. Prevent duplicates, excess/issues, forgery, race, rollback and replay.
3. Enforce independent real Finance maker/checker and signed **Company + frozen original leaf Item Group → Expense Account** and **Company + beneficiary Department → Cost Center** mapping decisions, valid from actual approval instant, plus Department Accounting Dimension. Missing/mismatched Company, unsigned, stale, forged, backdated or ambiguous financial evidence must reject before posting.
4. A usable **CCPC Department Material Consumption** report with actual issue-time Department, Item, stock UOM, original issue/Slip references, date, gross issued quantity/valuation, material-source quality/legacy flags, Company and currency; separate **verified GL expense / Cost Center reconciliation** to distinguish raw SLE issue valuation from booked Department expense. Do not silently certify a per-row GL allocation when native GL aggregates by voucher; design accountable drill-down or exception bucket.
5. Equipment/Job Order read-only source report and Company-wide stock-vs-P&L GL reconciliation can be included *only* with exact release-source integration, permission and consistency verification. A report is not yet certified net material/maintenance or all-P&L accounting. No duplicate valuation, UOM or cross-company totals.
6. Authenticated roles: named Supervisor, Stockroom issuer, independently authorized Finance mapping maker/checker, and appropriately scoped report readers. Existing Department script currently grants `System Manager` (with separate executive-report bypass), **not ordinary Department users**; any broader access requires carefully tested Company+Department data visibility and cannot be authorized through front-end hiding alone.
7. Real Company, Account, Department, UOM, Cost Center, Department dimension, role and warehouse masters validated; official Fiscal, period, reversal and return policy signed. Restrict Company/user scope to actual authenticated permissions, not synthetic fixture authorizations.

## Phase 1 explicit exclusions (proposed)

- Intercompany Material Billing Batch creation, SI/PI pair generation/correction/submission, reconciliation and corresponding intercompany financial reports, especially the unresolved original CCPC→Ricor approved batch and Draft SI `ACC-SINV-2026-00001` / PI `ACC-PINV-2026-00005`. These remain protected in MAIN DEVELOPMENT; no replay of one-shot markers.
- **Cross-Company withdrawals** where stock belongs to issuer Company but beneficiary is another Company's Department; block such new financial issues in Phase 1 unless Finance approves a separate, audited and fully tested treatment. Merely showing CCPC SLE valuation under Ricor is not proof of Ricor expense or payable.
- Posting historical Ricor invoices, purchase-side direct-consumption charge Item correction and synthetic signing of real past mapping evidence.
- Optional advanced maintenance/purchasing/Equipment financial features not needed to prove the actual Department material expense control, while keeping data integrity and normal ERPNext operations intact.

**Isolation requirement:** Before calling intercompany deferred, inspect app migration hooks, patches, roles, workspaces, whitelisted server routes, background jobs and schema. Merely hiding billing menu items is NOT sufficient to disable financial transactions; server-side permission/feature gating and replay/submit prevention are necessary. Installed inactive DocTypes may remain without being an authorized operational feature. Do not delete existing DEV records or write to either PRODUCTION.

## GitHub findings and confidence

- Current app review branch `review/billing-authorization-correction-2026-11-03` has `withdrawal_slip_stock.issue_withdrawal_slip`: Stockroom role, distinct issuer, locked Slip and submitted-issue denial, `_build_material_issue`, `apply_issue_beneficiary`, `assign_original_issue_b_c`, native Stock Entry submit. The issuance source examined contains **no billing batch API dependency**, so original stock issue is **architecturally separable**, subject to a complete source/route/schema and transaction test.
- The same app review branch **already contains three relevant reports**, including `ccpc_department_material_consumption` (currently only gross original issue SLE value and verified at-issue Department, intentionally NOT certified per-Department expense GL), `ccpc_equipment_job_material_activity`, and `ccpc_company_stock_pnl_gl_reconciliation` (stock valuation and GL separate views). Each is read-only and requires restricted access. Current Department report metadata grants System Manager.
- Prior combined [PR32 CircleCI Build #52 acceptance](FOUR-REPORTS-PR32-CIRCLECI52-REAL-MARIADB-ACCEPTANCE-2026-10-29.md) documents 64/64 installed-Frappe report policy and 22/22 native MariaDB tests **86/86 PASS** on earlier app SHA `061e65710eb4b527fc8ac579aaab8ccad4dd131d`; source is **not identical** to PR33 review for the three main report Python files (Git blob comparisons inspected on Nov 17). These are valuable *historical* tests, **not current-source regression signoff**.
- Current PR33 and stacked PR34 remain draft/unmerged; the current 3-method dedicated Ricor native PI CI test job has **not** run. Under a Phase 1 same-Company release, the intercompany-specific CI gate is **not the critical Phase 1 release blocker**; existing CircleCI `CCPC_RICOR_APPROVED_SHA` variable alone creates no pipeline and does not need to be removed or exposed. Do not launch the Ricor job merely because the variable is saved.
- No proof yet of a complete, current-source same-Company business posting+Department report+GL reconciliation+permissions test in disposable MariaDB or final accepted persistent DEVELOPMENT. Prior true subsets and standalone report suites are partial evidence.
- Existing dedicated PRODUCTION host/Compose, LAN HTTPS, secrets, backup/restore and rollback remain **separate mandatory blockers even for Phase 1**; don't call Phase 1 released without these.

## Proposed order (do not jump)

**Gate 0 — lock the legal-Company scope.** Owner confirms Phase 1 **same-Company stock issues and beneficiaries only**, defers all new cross-company financial issues. Separate approved Finance decision if cross-company consumption is essential now.

**Gate 1 — exact GitHub release isolation review.** Build narrowly scoped **Phase 1 review branch** after owner confirms scope, preserving tested issue/roles/reports and preventing intercompany server actions; audit imports, patches and migrations/permissions. Do not rewrite/retire the original DEV Draft invoices.

**Gate 2 — one integrated disposable v16/MariaDB proof.** Authenticated independent mapper+checker → eligible Withdraw Slip → separately authorized Stockroom issue → exact signed expense account and beneficiary Cost Center/Department dimension → posted Stock Entry/SLE/GL → same-Company Department report + GL reconciliation. Cover cancellation/return, wrong Company, missing mappings, stale approvals, duplicate issue, concurrency, unauthorized report access, unknown historic attribution, aggregation and mixed UOM. Validate new combined source, not only previous test SHA.

**Gate 3 — controlled real DEVELOPMENT acceptance.** Before migration/persistent writes verify exact Git branch/worktree, guarded post-Draft local and Synology recovery point, rollback drill and explicit DEV operation authorization. Named real users/roles/maps and site-specific representative data; run authorized UAT and update GitHub with evidence. No destructive cleanup, replay or rewriting the original invoices.

**Gate 4 — dedicated production infrastructure and explicit release approval.** Final exact GitHub candidate, safe clean release integration, real Compose semantic render, TLS/LAN login, credentials, backup/NAS isolated restore, rollback drill, user training, staged operational acceptance and separate **explicit owner signoff**. PRODUCTION never changes just from GitHub or DEV acceptance.

## Estimate tracking

- The broad original-scope `PRODUCTION-READINESS-SCORECARD.md` remains **40% ±10 points**, **NO-GO**, until re-scored from new results.
- **Proposed narrower Phase 1 estimate: roughly 50–60% (wide uncertainty ±15 points), not a verified KPI.** Prior genuine SQL stock/GL + four-report subsets favor the revised scope, but current source, actual Company finance/permissions/Dept GL signoff and production restore are unproven. Different denominator: do **not** claim total project progressed 40→55% merely by deferring features.
- Rough planning, not commitment: ~2–5 additional months toward a protected Phase 1 production release if owner confirms same-Company scope promptly and real accounting/host approvals go smoothly; historical full-scope estimate 4–8 months is superseded only for the narrower release goal. One blocker can invalidate the range.
- Update a *separate Phase 1* scorecard after Gate 0 is formally agreed and genuine Gate 2+ evidence has been reviewed; state scoped exclusions prominently.

**References:** `CURRENT-HANDOFF-4.md`, `CURRENT-HANDOFF-2.md`, `PRODUCTION-READINESS-CRITICAL-PATH-2026-10-28.md`, app source `withdrawal_slip_stock.py`, `withdrawal_issue_beneficiary.py`, `bc_issue_runtime.py`, original three report modules and user-approved CI acceptance records. 
