# CCPC ERPNext — CURRENT HANDOFF 2

**Active, concise GitHub-first checkpoint.** Last verified 2026-10-29. **Start here after [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).** This file supersedes the giant [CURRENT-HANDOFF.md](CURRENT-HANDOFF.md) **for current progress and next actions only**; the original remains an immutable-intent historical/reference record, not deleted or overwritten. New threads should read this compact file, verify live GitHub branch SHA and PRs, and consult historical records only for needed details.

## Document maintenance (fix for oversized former handoff)

1. Keep this file **small, current, and authoritative as the navigation/continuity checkpoint**, with a verified SHA, test evidence, outstanding gates and 1–3 current priorities. Target <15 KB. Do **not** paste full logs, huge diffs, repetitive milestone transcripts or secrets here.
2. Record detailed investigations, exact test logs, design rationale and reviews in **separately named versioned technical records**, then link them from this handoff.
3. After a meaningful milestone, **edit this file in place on the verified docs branch** using its current blob SHA, preserving current sections. Update the last-verified date/SHAs/evidence. If a future handoff grows too large, **create CURRENT-HANDOFF-3.md and update [README.md](README.md) to point to it**, rather than appending indefinitely or overwriting an unverified full file.
4. [README.md](README.md) defines which compact handoff is active. The old `CURRENT-HANDOFF.md` (~1.3 MB) is **historical and intentionally preserved**; do not retry full-file updates unless the owner specifically requests restructuring. [Build #34 acceptance handoff](CURRENT-HANDOFF-CI34-ACCEPTANCE-2026-10-29.md) and [integrated engineering record](INTEGRATED-WITHDRAWAL-LEDGER-BILLING-REVIEW-2026-10-29.md) contain the last detailed acceptance proof.
5. GitHub files are the authoritative progress records, not ChatGPT Project Source attachments. All changes are made during active approved conversations and independently reread/verified.

## Authoritative repositories and workflow

- **Custom app:** [ccpcerp/ccpcerp](https://github.com/ccpcerp/ccpcerp). Current active Finance feature `feature/finance-mapping-lifecycle-2026-10-28`, independently verified HEAD **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**. PR #27 merged at that SHA after fixing the synthetic ERPNext root/child Account fixture. The release/default app `version-16` was last verified at `cfcc19394a6646548f2b7050db040c8cf5ebafde`; it does **not** have these newer Finance feature tests.
- **Docs, Docker, procedures:** [ccpcerp/ccpc-frappe-deployment](https://github.com/ccpcerp/ccpc-frappe-deployment), verified docs branch `docs/ccpc-checkpoint-2026-10-10`. Always read the [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) before editing.
- **Practice:** inspect GitHub code/requirements, create isolated reviewed feature branch, implement authorized changes in GitHub, review changes and tests, seek separate authorization for billable CircleCI and DEVELOPMENT pull/testing, push verified DEVELOPMENT fixes back to GitHub, and update this checkpoint. **Never assume default app branch is latest.**
- **DEV/PRODUCTION:** DEVELOPMENT and PRODUCTION are different Docker environments but may share infrastructure. Never overwrite uncommitted DEV work, switch its branch blindly, or deploy/migrate/restart/recreate/restore PRODUCTION without a distinct explicit approval, tested backups and rollback procedure. **PRODUCTION NO-GO.** No autonomous reporting, paid API agents or background Codex publishing.

## Latest verified milestone — CircleCI build #34, 12/12 PASS (2026-10-29)

Actual owner-supplied runner logs, disposable `ci-finance-lifecycle.localhost`, job `finance-lifecycle-isolated-integration` shown **green** in CircleCI UI screenshot:

- `build_34_step_105_container_0.txt`: `test_finance_lifecycle_disposable_integration`, **8 individual tests A–H PASS**, `Ran 8 tests in 2.365s`, `OK`.
- `build_34_step_106_container_0.txt`: `test_finance_withdrawal_billing_bridge_disposable`, **4 individual tests A–D PASS**, `Ran 4 tests in 8.984s`, `OK`. The V17 Frappe `limit_page_length` warning is nonfatal.
- **Combined evidence 12/12 PASS**: authenticated independent Maker/Checker Finance mapping lifecycle, forge/replay/unauthorized/rollback rejection, real submitted original Withdrawal Material Issue, Stock Ledger Entries + expense GL source reconciliation, precise billing preview and unsigned denial, persisted month-end batch finalization under **test-only** simulated elapsed month-end, real native ERPNext **DRAFT** Sales/Purchase Invoices cross-linked with expected source/amount/Company/party, no draft invoice stock or GL, replay denial, real savepoint rollback of orphan Sales draft after injected Purchase failure and one successful retry. Earlier build #31 test fixture error was resolved by [app PR #27](https://github.com/ccpcerp/ccpcerp/pull/27).
- The snippets show the exact test outcomes but **do not print a full CI checkout SHA**. The feature branch SHA above was verified in GitHub and matches the approved operator test context; do not overstate independent CI runner SHA attestation.
- This is a **disposable SQL integration test milestone, not full site, finance, or production acceptance**. Invoice submission, AR/AP/GL after submission, reversal/returns, HTTP+CSRF and concurrent request isolation, actual CCPC accounting signature/business masters, four agreed reports and persistent DEVELOPMENT validation are outstanding.

## Current owner-approved development — four day-one reporting families

The owner approved continuation of **GitHub-first reporting development** after the CI #34 milestone, **not** deployment or unrestricted CI spending. Preserve reporting/accounting integrity:

1. **Department material consumption:** original posted issue source, immutable issue-time requesting/work-for Department/Section, Company, dates and stock valuation; report unknown/legacy attribution separately.
2. **Equipment / Job Order consumption:** the existing [CCPC Equipment Maintenance Baseline](https://github.com/ccpcerp/ccpcerp/tree/feature/finance-mapping-lifecycle-2026-10-28/ccpcerp/ccpc_erp/report/ccpc_equipment_maintenance_baseline) (app repository) is already a gross SLE-based read-only source report, **not** a complete cost report. Verify that original issue row Equipment snapshot, source quality and exact SLE association are preserved; do not relabel unattributed rows or count unpriced job activity as financial consumption. Reference [snapshot report design](EQUIPMENT-SNAPSHOT-REPORT-CUTOVER-AND-FORGED-VOUCHER-2026-10-18.md).
3. **Intercompany Withdrawal & billing (with invoice status):** exact original Withdrawal→Stock Entry Detail→billing child row→finalized batch→draft/posted SI and PI links; display batch/invoice status separately, avoid duplicating issue valuation by billing amounts.
4. **Company-wide consumption vs all-Company P&L expense:** reconcile posted issue SLE to relevant expense GL through original voucher and voucher detail where possible; keep each Company's currency and stock UOM separate, distinguish source valuation, GL posting, intercompany invoice amounts and incomplete/exception attribution; **no cross-currency/unit sum or double-counted intercompany expense**.

**Engineering gate before code:** Reinspect existing app Script Reports, Stock Entry/Withdrawal/Invoice DocType fields and current permissions. Design explicit filter security and no-group leakage, detail/aggregate rules, safe parameterized queries, cancel/repost/returns and source-quality buckets. Build one tightly scoped reviewed branch and test offline/static first, then separate owner-approved disposable MariaDB CI. Reporting logic/permissions and results **not yet verified** by build #34.

## Unresolved accounting and release gates

- Formal owner approval for actual Company, Department, account and internal Customer/Supplier masters and Finance approvers; do not infer from CI synthetic fixtures.
- Submitted SI/PI pair validation and GL/AR/AP, month-end closing/reopening, tax/policy/FX treatment, returns and reversal, idempotency and concurrent approval guards.
- Four reports' independently reconciled outputs, legacy/unknown Equipment/Department attribution, multi-company/UOM/currency isolation, audit trail, and per-Company permission checks.
- Persistent DEVELOPMENT pull only after safe status/branch/commit review, signed-off backups, controlled migration plan if required, genuine site integration, and fixes pushed back to GitHub.
- PRODUCTION separate explicit authorization, backups/recovery/rollback and actual Company controls. **Do not change PRODUCTION based on this handoff.**

## Latest GitHub-only reporting progress — 2026-10-29

- **Reporting program documented:** [Four day-one reports source/GL reconciliation plan](FOUR-DAY-ONE-REPORTS-GITHUB-FIRST-PLAN-2026-10-29.md), detailed evidence and owner gates; documentation commit `594a72ae32295d562e8991cdcdef456cbf5dbeb9`.
- **First report code candidate, not yet merged:** [draft app PR #28](https://github.com/ccpcerp/ccpcerp/pull/28), `review/intercompany-source-billing-report-2026-10-29` review HEAD **`a1a9535c2e59f935565808a5f25e0c9c1bd4ff48`**, exact base Finance feature `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. Adds five new `CCPC Intercompany Withdrawal Billing Status` Script Report files, no runtime business/CI code modifications. Original posted source→grouped outbound SLE→active billing claim→SI/PI Draft/Submitted/Cancelled/Missing status and unbilled rows; signed issuer money and frozen billing amount independent; fail on duplicate active claims; Company-date-scoped System Manager read-only access; nine source unit test methods created, including explicit issuer-currency display validation.
- **Validation status:** GitHub source-only preflight **15/15 initial and 11/11 latest focused structural checks PASS**; report Python tests and real Frappe/MariaDB report execution **NOT RUN**. Existing previously hosted build #34 **12/12** does **not** exercise this new report. Do not merge PR #28 or trigger paid CI/DEVELOPMENT without separate approvals. Department report, Equipment/Job cost completion and Company-wide GL reconciliation are next family-specific milestones (not completed).
- **Status of oversized handoff fix:** This file is the active, small rolling handoff; [README](README.md) points here. Old [CURRENT-HANDOFF.md](CURRENT-HANDOFF.md) stays archived for historical specifics. Update *this* file at verified milestones rather than appending to the 1.3 MB old handoff.

## Latest references

- [CircleCI #34 acceptance summary](CURRENT-HANDOFF-CI34-ACCEPTANCE-2026-10-29.md)
- [Finance→Withdrawal→Ledger→Billing engineering record](INTEGRATED-WITHDRAWAL-LEDGER-BILLING-REVIEW-2026-10-29.md)
- [Equipment source-quality design](EQUIPMENT-SNAPSHOT-REPORT-CUTOVER-AND-FORGED-VOUCHER-2026-10-18.md)
- [Operating architecture](DOCKER-DEV-PROD-ARCHITECTURE.md)
- [DEVELOPMENT controlled integration plan](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md)
