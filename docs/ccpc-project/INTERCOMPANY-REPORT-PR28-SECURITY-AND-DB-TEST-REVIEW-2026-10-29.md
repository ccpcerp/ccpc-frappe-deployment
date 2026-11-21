# CCPC ERPNext — PR #28 intercompany source/billing-status report: review and SQL acceptance plan

**Checked 2026-10-29. GitHub-only source review; no hosted or persistent database execution.**
Review app [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28) stays **DRAFT/UNMERGED**. App review branch `review/intercompany-source-billing-report-2026-10-29` at **`b6842960fbd683acd3e3a2b84ff2c6814d20095d`**, based on Finance feature `feature/finance-mapping-lifecycle-2026-10-28` at **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**. GitHub compare found only five new files under `ccpcerp/ccpc_erp/report/ccpc_intercompany_withdrawal_billing_status/`; no existing accounting controller, DocType, CI config, migration, permission role or deployment change. GitHub source check **20/20 focused assertions PASS**; these assertions are structural and **not** real Python tests or MariaDB execution.

## Findings that were corrected within the review branch

1. **Cross-Company confidentiality:** Initial optional `requesting_company` meant an authorized issuer-company user could query other requesting companies without checking Company read restrictions. Server `_validate_filters` and JS now require both issuer and requester, verify both Company records' read permission, enforce different Companies, and SQL uses `ws.requesting_company = %(requesting_company)s` rather than `IS NULL OR` wildcard. Report metadata is `System Manager` only; DocType read rights are checked at runtime. Broader Accounting/Department role grants are out of scope.
2. **Forged billing origin:** Source row is exact original posted `Stock Entry Detail.name` joined by `billing_item.stock_entry_detail`, but the billed child may contain inconsistent parent `stock_entry` / `withdrawal_slip` references. Query now selects both and marks `BILLING_ORIGINAL_VOUCHER_MISMATCH` instead of silently treating the forged parent as valid.
3. **Cross-company invoice disclosure and pairing:** A linked SI can now only join where `si.company=se.company`; a linked PI only where `pi.company=ws.requesting_company`. Missing or mismatched refs are treated as exceptions; reciprocal `inter_company_invoice_reference` is read from both real invoices and mismatches explicitly flagged. This is not a substitute for owner-approved invoice submission/cancellation policy.
4. **No monetary conflation:** `source_sle` groups each noncancelled outbound SLE by `voucher_no`, `voucher_detail_no`, Company **before** any billing item join. Sources without outbound SLE remain marked missing, rather than zero. Source issue valuation and frozen billing amount are shown as distinct columns, both explicitly displayed using issuer currency. Report has **no sum/grand total row** and never adds invoice totals into SLE consumption.
5. **Bounded, no-write query:** Both Companies and from/to dates required; date-window delta at most 366 days. SQL filters are bound parameters and issuer SLE/posted source bounded to the same range; no write/insert/save/submit/commit. Multiple active billing claims per original source are rejected rather than silently deduplicated.

## Reviewed test code (not yet executed)

`test_ccpc_intercompany_withdrawal_billing_status.py` includes **13** authored test methods checking: exact-source SLE grouping, independent valuation measures, unbilled row retention, duplicate claim rejection, foreign invoice/company/source mismatch flags, System Manager guard, invoice statuses, issuer-currency column formatting, mandatory requesting-company filter, unauthorized Company access rejection, original voucher + reciprocal invoice link checks, and foreign Company invoice join rejection.

**Caveat:** These are Python source test methods only; no Python compile, real `unittest` execution, Frappe Report UI, MariaDB SQL execution, permissions against installed site, realistic query plan or benchmark has been run. The earlier CircleCI #34 **12/12** pass covers prior Finance and real paired *draft* SI/PI tests, not this new report.

## Required actual disposable MariaDB acceptance matrix (next gated work)

| Case | Minimal disposable setup | Required assertion |
|---|---|---|
| Real, signed, eligible source | Two synthetic Companies, signed Maker/Checker Finance mapping, original submitted Withdrawal Material Issue | Exact original voucher/detail and SLE-derived qty/value, issuer currency and UOM, unbilled status before billing |
| Multiple outbound SLE fragments | Two noncancelled outbound SLE lines for one original detail (if fixture valid) | One report line; values aggregated once before billing join |
| Real paired draft invoice | Finalized one-month batch with genuine original source → real draft SI/PI | Exactly one source row, correct frozen billing value and both draft statuses, reciprocal SI/PI, no new SLE/GL from drafts |
| Repeated active claim | Deliberately corrupt two active batch claims in isolated DB; revert via test rollback | Report explicitly rejects duplicate detail rather than doubling valuation |
| Cancelled batch + unbilled | Historical canceled batch claim and no active claim | Source still shows unbilled; canceled claim does not obscure it |
| Forged origin or invoice refs | Billing child with different `stock_entry`/Slip or invoice pair not reciprocal | Explicit source-quality exception; no false fully reconciled status |
| Foreign-company invoice ref | Link to invoice that belongs to a third Company | No foreign invoice row payload via SQL join, marked invalid/missing |
| Unauthorized issuer/requester | Authenticated user with System Manager but targeted Company read not granted, or no System Manager | Permission rejected before sensitive report rows leave query |
| Date scope & blank requester | No requester/date, inverted date range, >366-day span | Fail closed; no unrestricted cross-Company query |
| Return/reposting/missing ledger | Existing true return/correction and original SLE missing or cancelled | Original gross value disclosed separately or flagged, never net invisibly |
| Mixed currency/UOM | Distinct issuer Companies/currencies and mixed stock UOM | No cross-company value or unlike-UOM aggregate; issuer currency only |
| Operational viability | Approved 1-year fixture size, report execution-plan review | No unsafe unbounded full-ledger scan or excessive report memory/latency |

**Important known limitation:** Invoice statuses are observational only. No report should claim intercompany AR/AP, revenue/expense reconciliation, submitted SI/PI validity, or return netting until those separate accounting workflows and bank/GL evidence are owner-approved and independently tested. The overall Company-wide P&L reconciliation report remains separate.

## Gate and next step

The reviewed PR is **not yet merge-ready** for the real CCPC site. Before merge, run Python syntax/import and 13 report unit tests in a proper Frappe environment, then a **separately owner-approved** manually held exact-SHA disposable MariaDB suite for source/Company/ledger/invoice cases. Review any SQL or fixture failure and repair on PR #28, document actual results. No automatic CircleCI rerun/charge, DEVELOPMENT pull, PRODUCTION migration or deployment follows this document. **PRODUCTION NO-GO.**


## Offline executable follow-up — 2026-10-29

The previously unexecuted Python source-focused tests have now been exercised against the **byte-for-byte GitHub source** using a local minimal Frappe stub. The first attempt **12/13 PASS** found that `test_exact_original_sle_is_grouped_before_billing_join` incorrectly searched for `AND se.docstatus = 1` while the real SQL correctly uses `WHERE se.docstatus = 1`. This was only a test assertion mistake: no production SQL, permission, DocType or business Controller changed. App PR #28 HEAD now **`dfb63d975de009ea0168ddd5c9e09a60c26ad4c6`**.

After the reviewed one-line test fix, **13/13 offline stubbed tests PASS**, **Python compile PASS**, and separately **12/12 synthetic in-memory SQLite SQL scenarios PASS**, with independent source/test Git blob hashes checked. This does **not** discharge the real Frappe/MariaDB, permission/HTTP or multi-company business acceptance gates. Full method, results, limitations and the exact next authorization in [offline execution record](INTERCOMPANY-REPORT-PR28-OFFLINE-EXECUTABLE-VALIDATION-2026-10-29.md). No further billable CircleCI, DEVELOPMENT or PRODUCTION action was initiated. **PR remains draft/unmerged; PRODUCTION NO-GO.**
