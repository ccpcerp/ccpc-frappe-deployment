# CCPC ERPNext — Four day-one reports: source and accounting reconciliation plan

**Date:** 2026-10-29. **Status:** GitHub-only scoped engineering plan + first draft report. No CI/DEVELOPMENT/PRODUCTION action and no new reporting acceptance claim.

## Evidence and source-of-truth

- App Finance feature `feature/finance-mapping-lifecycle-2026-10-28` last verified at `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. Owner-uploaded CircleCI #34 Finance G2 8/8 and genuine original Withdrawal→SLE/GL→persisted final month-end→draft SI/PI SQL bridge 4/4 PASS (combined 12/12). The test snippets themselves omit the full checkout SHA; see [integration record](INTEGRATED-WITHDRAWAL-LEDGER-BILLING-REVIEW-2026-10-29.md).
- Current GitHub app already has the read-only `CCPC Equipment Maintenance Baseline` report under `ccpcerp/ccpc_erp/report/ccpc_equipment_maintenance_baseline`; it reports gross outbound SLE value by original Equipment issue-time snapshots and explicitly separates missing/conflicting snapshot attribution. It **is not a complete maintenance-cost or GL report**.
- `Intercompany Material Billing Batch` and `Intercompany Material Billing Item` store original `stock_entry_detail` and source `stock_entry`, `withdrawal_slip`, frozen quantity/rate/amount, the batch status, and header `sales_invoice`/`purchase_invoice`. Billing controller produces **draft invoices**, not submitted accounting entries. Some attribution in child row is copied from Withdrawal Slip at rebuild; do **not** automatically treat it as independently immutable issue-time evidence in historical reports.
- The report path and roll-forward pointer are maintained in [active handoff 2](CURRENT-HANDOFF-2.md); the former `CURRENT-HANDOFF.md` is archival.

## Foundational report rules

1. **Financial provenance:** Count **original submitted Material Issue** `Stock Ledger Entry` by exact `voucher_type='Stock Entry'`, `voucher_no`, `voucher_detail_no = Stock Entry Detail.name`, Company, and `is_cancelled=0`. Aggregate multiple outbound SLE fragments per source detail before joins. Never join SLE fragments to billing children and then sum without aggregation.
2. **Separate financial measures:** Distinguish SLE issue valuation (issued-Company stock movement), frozen intercompany billing amount, Sales/Purchase Invoice totals (if later posted), and General Ledger expense or receivable/payable amounts. **Never add them together** as consumption. Ensure company and currency labeling for *each* amount.
3. **UOM:** Group quantities by `stock_uom`, never sum unlike UOMs; prefer original `transfer_qty` plus reconciled outbound SLE `actual_qty`. Show discrepancy buckets, not silently replace quantities.
4. **Historical attribution:** Use frozen original source row snapshots where actually present. Do not rewrite legacy submitted documents or guess Department/Equipment from the present-day Withdrawal Slip/Job Order/Equipment master. Flag missing/conflicting/renamed master data separately and preserve source. Billing child `requesting_department` is a snapshot **at billing refresh**, not necessarily original issue-time truth.
5. **Returns/reversal:** Do not net physical returns or cancelled invoices until signed return/accounting policy and actual source links are tested. Show gross original and recorded return/adjustment separately, with a visible pending reconciliation flag.
6. **Safe access:** Report `System Manager` only as conservative initial role, explicit DocType read and Company permission checks, mandatory Company/date filters with bounded date range, static SQL with bound parameters, no DB writes. Any Finance Controller or Department report-grant needs separate owner role/mapping review. Never show other Company rows merely because UI filter is optional.
7. **Idempotence, quality:** Reject duplicate active billing claims for same `stock_entry_detail`; expose SLE/membership/Company/invoice inconsistencies as exceptions. No silent dedup that hides financial mismatches. All new reports start **unmerged and untested** until actual SQL fixture confirmation.

## Four report families and gates

### 1. Department material consumption — NOT IMPLEMENTED

Target: stock item, stock UOM, Company, original posted date, original issue row, original Department/Section or Work-for Department at **issue-time evidence**, gross signed SLE issue value, currency and source-quality exception. The current snapshot/GL dimensions must be inspected before deciding whether a Department field is authentically frozen on Stock Entry Detail or signed GL. If provenance cannot be established, output **UNATTRIBUTED / LEGACY / DISCREPANCY** and withhold any certified per-Department expense sum. Enforce user Company and permitted Department visibility. Review accounting authority and original/beneficiary attribution distinctions.

### 2. Equipment and Job Order material consumption — PARTIAL EXISTING BASELINE ONLY

Current [Equipment Maintenance Baseline design](EQUIPMENT-SNAPSHOT-REPORT-CUTOVER-AND-FORGED-VOUCHER-2026-10-18.md) keeps gross SLE issue value and recorded unpriced Job Order activity separate. Verify tests and live original snapshot fields `ccpc_equipment_at_issue` / `ccpc_equipment_code_at_issue`, Equipment Registry Company link, and legacy anomaly buckets. Further work: agreed per-Equipment material report vs cost accounting, approved actual partial return netting, Section/Job Order joins, GL reconciliation and unknown attribution. Do not treat unpriced work hours as expenses or infer machine attribution from mutable current Slip/Equipment.

### 3. Intercompany Withdrawal/billing with invoice status — DRAFT PR #28, UNMERGED

New app [draft PR #28](https://github.com/ccpcerp/ccpcerp/pull/28), review branch `review/intercompany-source-billing-report-2026-10-29`, source base `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`, current reviewed source tip `b6842960fbd683acd3e3a2b84ff2c6814d20095d` (GitHub readback verified). Five newly created paths all in `ccpcerp/ccpc_erp/report/ccpc_intercompany_withdrawal_billing_status/`: Python Script Report, JS filters, Report metadata, init, source-focused unit tests.

Reports original posted intercompany source and exact grouped original outbound SLE, left-joins only active billing claims, retains **unbilled** rows, flags multiple conflicting active claims rather than double counting, shows frozen billing amount distinctly from SLE issue cost, invoice refs and **Draft / Submitted / Cancelled / Missing** status, separate Company/currency, source-quality exceptions. System Manager-only, **both Companies mandatory and individually permission-checked**, bounded posting dates, read-only; report-wide totals intentionally off. **Do not claim real DB report execution, complete billing acceptance, or full accounting/P&L reconciliation**. Need syntax + Frappe unit testing, disposable MariaDB with unbilled/cancelled/replay/missing-SLE/multi-SLE/foreign-company and invoice cases, then user signoff before merge.

### 4. Company-wide stock consumption vs all-company P&L — NOT IMPLEMENTED

Design a dual-perspective reconciliation **not** a single additive figure: one original signed SLE issue valuation view and a separate independently posted GL expense (by voucher/account/Company/period), plus separate intercompany invoice AR/AP/revenue/expense view. Never assume a 1:1 GL Entry link to every Stock Entry Detail when actual GL can aggregate per voucher; reconcile at exact supported voucher/grouping grain, disclose unallocated differences and original Work-for attribution. Include non-Stock-Entry P&L entries only in an independently labeled all-P&L view. Keep each Company, currency and UOM separate; show cross-company eliminations as an explicit later Accounting decision, not automatic deductions. Filter by Company/date, post/cancel and account role, with unit/integration variance cases.

## Development and acceptance sequencing

1. Review draft report #3 source for SQL safety, duplicate joins and Company access, then run offline Python syntax + source-focused tests. Create/amend review branch only, **do not merge automatically**.
2. Build focused disposable MariaDB integration tests for report #3, using original signed source from previously verified bridge fixtures but no production Company records; separately approve any new billable CI run.
3. Author/review Department original attribution and adapt existing Equipment baseline using frozen issue-time snapshots and exception handling.
4. Design/implement reconciled Company-wide report at GL voucher grain with department, intercompany and return exception tests.
5. Only after independently approved tests and real CCPC accounting policy review, authorize a safe checked DEVELOPMENT pull/test. PRODUCTION requires separate owner approval, backup/recovery/rollback review, Company permissions and reconciliation signoff.

**Current protection:** No automated CI schedule, no DEVELOPMENT/PRODUCTION writes, no unapproved invoice submission or migrations. **PRODUCTION NO-GO.**


**Review follow-up 2026-10-29:** The two money columns now explicitly reference `issuing_currency` as their Currency display option (no default-user-currency display); a ninth source-focused unit test verifies the currency binding. GitHub compare remains five new report-only paths and zero-behind feature base; 11/11 latest focused structural checks PASS; actual Python/Frappe/MariaDB tests still NOT RUN.


**PR #28 source security and accounting review:** The current review hardens the original draft against requester Company wildcard disclosure, cross-company invoice joins and mismatched billing original vouchers, and checks reciprocal SI/PI references. Two monetary columns explicitly use issuer currency, with no currency/UOM mixed totals. **13 authored Python tests (NOT EXECUTED), 20/20 latest GitHub structural checks PASS**. See [PR28 SQL security review and acceptance matrix](INTERCOMPANY-REPORT-PR28-SECURITY-AND-DB-TEST-REVIEW-2026-10-29.md). Further Frappe syntax/unit and genuine MariaDB report execution require a separately approved test procedure, not an automatic rerun.
