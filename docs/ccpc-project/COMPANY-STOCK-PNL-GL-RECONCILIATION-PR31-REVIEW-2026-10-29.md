# PR #31 — Company-wide original stock vs posted P&L GL reconciliation

**2026-10-29. Status:** Source-only GitHub draft, no executable Frappe/MariaDB tests yet, unmerged and not deployable.

## Source-of-truth and design

- Approved [four report families and accounting-source rules](FOUR-DAY-ONE-REPORTS-GITHUB-FIRST-PLAN-2026-10-29.md); active [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).
- Base app Finance feature `feature/finance-mapping-lifecycle-2026-10-28` at verified SHA `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`; distinct [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28) Intercompany (CircleCI #37 18/18 PASS), [PR #29](https://github.com/ccpcerp/ccpcerp/pull/29) Department (CircleCI #40 20/20 PASS) and [PR #30](https://github.com/ccpcerp/ccpcerp/pull/30) Equipment/Job activity (source-only) remain unmerged and **are not part of PR #31's source/test evidence**.
- [Draft PR #31](https://github.com/ccpcerp/ccpcerp/pull/31) on branch `review/company-source-pnl-gl-reconciliation-2026-10-29`; initial verified app head `238e7e073e97e0fad40b00fda20de108dec9c74d`. Five new paths only under `ccpcerp/ccpc_erp/report/ccpc_company_stock_pnl_gl_reconciliation/`: `__init__.py`, Python Script Report, JSON and JS filters, 15 authored Frappe unit tests. No existing app/CI/controller/schema/permission/deployment file changes, zero commits behind Finance base.

## What the report shows

**Two separate perspectives which must never be added together:**

1. `STOCK_ISSUE_VOUCHER_COMPARISON` includes *all* submitted same-Company Stock Entry **Material Issue** vouchers in the selected date range, including non-CCPC-Withdrawal material issues. It first groups only outbound and noncancelled SLE by Company/voucher/detail to avoid multiplying source value across split ledger fragments. It then rolls to Stock Entry voucher grain, exposing original material row count, rows with outbound SLE, gross SLE issued stock value and Company currency. It intentionally **does not sum quantities across different stock UOMs** and does not net physical returns or use billing amount as expense.
2. `ALL_PNL_GL_VOUCHER_ACCOUNT` independently selects same-Company posted noncancelled GL Entries, with P&L Account `root_type` Income/Expense, grouped by posting date, voucher type/no and Account. It shows signed debit-minus-credit in the same Company currency as an **independent P&L value**, includes non-Stock Entry vouchers and is **not additive** to source value.

Comparison only on supported `Stock Entry` voucher grain: independently posted **P&L Expense** GL entries summed by voucher (not detail). Report shows `stock_source - eligible_voucher_expense_GL` when both exist; no GL or no SLE yields NULL comparison, never fabricated zero. Flags source missing SLE, partial Stock Entry Detail coverage, unexpected negative SLE amount, non-Withdrawal source, no expense GL, and voucher discrepancy. It does not certify per-Item, per-Department, per-Equipment or Job Order P&L, invoices or AR/AP/Revenue, posted returns, intercompany elimination, foreign exchange, valuation repost timing or full financial-statement reconciliation. No direct financial posting or mutation.

**Security and scale:** System Manager-only, required DocType read checks Company/Stock Entry/Stock Ledger Entry/GL Entry/Account, explicit Company document read and per-source Stock Entry/Account read, mandatory Company and posting dates limited to 367 days inclusive, cap 400 original material vouchers and 800 P&L grouped account rows (throws instead of truncating), bound SQL, `apply_user_permissions=1` and no totals.

## Verification and pending gates

- **20/20 targeted source structural checks passed** through GitHub connector readback: exact Finance base, five new paths, Company binding, submitted original stock, split SLE grouping, P&L Expense/Income account filter, date boundaries, independent monetary columns, no write/additive totals, 15 test methods.
- **15 Frappe tests authored but NOT EXECUTED.** No native Frappe/MariaDB test, schema/SQL `EXPLAIN`, real permission, sample CCPC Company account mapping or historical GL voucher reconciliation has passed for PR #31. Neither CircleCI #37 nor #40 is evidence for this new report.
- A separately authorized, exact-SHA, manually held disposable CircleCI test should exercise real signed Withdrawal→submitted Stock Entry→SLE/GL as well as non-stock P&L, missing/cancelled stock and GL, multiple accounts per voucher, cross-Company access, issue returns/reposting and account classification.
- Accounting review before release: whether special stock vouchers post P&L expense at all, fiscal closing rules, account groups vs leaf, GL date differences, cancellation behavior, foreign currency, intercompany elimination, historical source attribution, performance/index review and actual CCPC DEVELOPMENT data.
- No new paid CircleCI run, merge, DEVELOPMENT pull/migrate, PRODUCTION change, autonomous job or paid API arrangement was authorized by this source-only milestone. **PRODUCTION NO-GO**.

**Next shortest path:** prepare independently isolated, branch/SHA-gated real MariaDB acceptance for PR #30 and #31, then request approval for bounded hosted runs; use results to correct GitHub and only after separate approval validate in DEVELOPMENT.
