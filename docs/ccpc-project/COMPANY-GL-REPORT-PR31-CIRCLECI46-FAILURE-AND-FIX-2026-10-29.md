# PR #31 — CircleCI Build #46 source-policy assertion failure and one-line fix

**Subsequent result (2026-10-29):** The single owner-approved Build #49 re-execution **PASSED 15/15 unit + 5/5 native MariaDB tests** at corrected SHA `5016ad711c8940258850cc602e9c9c58ec41c30b`. See [Build #49 acceptance](COMPANY-GL-REPORT-PR31-CIRCLECI49-REAL-MARIADB-ACCEPTANCE-2026-10-29.md). This file preserves Build #46's actual failure at its old SHA and the one-line GitHub repair, not the latest outcome. PR remains draft/unmerged; DEV/PROD untouched.

**Recorded:** 2026-10-29. **State:** Build #46 integration FAILURE at old exact app SHA; one-line test-only correction subsequently committed. No paid rerun or native MariaDB acceptance yet.

## Identity and observed results

- [Draft app PR #31](https://github.com/ccpcerp/ccpcerp/pull/31) remains unmerged on `review/company-source-pnl-gl-reconciliation-2026-10-29`; Finance base `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd` unchanged.
- Owner provided `build_46_step_105_container_0.txt` (43 log lines) and reported **27,799 CircleCI credits remaining** (previous owner-reported 27,876, **77 lower**, not an independently itemized Build #46 bill).
- Step 105 line 1: `PR31 exact-SHA isolated CircleCI identity verified`. Attempted site `ci-company-gl-report31.localhost`. Unit suite `ccpcerp.ccpc_erp.report.ccpc_company_stock_pnl_gl_reconciliation.test_ccpc_company_stock_pnl_gl_reconciliation` executed **15** source/presentation/permission tests; **14 passed, 1 failed**; `Ran 15 tests in 0.087s`, `FAILED (failures=1)`; process exited with code 1.
- Failing `test_sql_only_original_submitted_material_issue_with_grouped_sle` expects the literal substring **`AND ledger.company = se.company`**; actual SQL contains **`ON ledger.company = se.company`**, then `AND ledger.voucher_no = se.name` and `AND ledger.voucher_detail_no = sed.name`. The actual company/voucher/detail join condition is present and correct; the **test string** was stale/wrong. The incident log contains **no execution of the separate five-case native MariaDB suite**; do not count those as passing or failing.
- GitHub independent status query **at exact tested old SHA `c27487c60f867be752417088b57186f83ee5997a`**:
  - `ci/circleci: python-syntax` **success**.
  - `ci/circleci: company31-manual-approval` **success**.
  - [`ci/circleci: company-gl-report31-isolated-integration`](https://app.circleci.com/workflow/77ae0545-4985-406f-a6fd-dd6b580e623e/job/b6ff052c-cbef-4c31-b1af-74305c4f1780) **failure**.
- Because the test stage exited before the second suite, no published PR31 real MariaDB reconciliation acceptance exists. The one-run authorization has been consumed, and no automatic retry was approved.

## Exact corrective change — verified committed to GitHub

- App branch `review/company-source-pnl-gl-reconciliation-2026-10-29` has new HEAD **`5016ad711c8940258850cc602e9c9c58ec41c30b`**.
- **Only one line** changed in `ccpcerp/ccpc_erp/report/ccpc_company_stock_pnl_gl_reconciliation/test_ccpc_company_stock_pnl_gl_reconciliation.py`:
  - Before: `"AND ledger.company = se.company",`
  - After: `"ON ledger.company = se.company",`
- Connected GitHub old-SHA vs new-SHA compare independently confirmed **1 modified test file, +1/-1 lines, 1 commit ahead, zero behind**, with SQL source, accounting logic, fixture, CI job, access controls and migration files **unchanged**. New HEAD readback confirms the corrected assertion.
- **No completed CircleCI statuses are currently reported for the new SHA**; the corrected test itself has **not** rerun. Do not label 15/15 or native 5/5 as passing at the new commit. Test result cannot transfer from old SHA to new SHA without fresh execution.

## Next safe acceptance gate

1. Before any rerun, owner explicitly approves **one new bounded hosted CircleCI execution**; no implicit reuse of Build #46's approval or unlimited retries. 90-minute cumulative subprocess safeguard is not a hard credit-spend ceiling.
2. Operator changes **only** the existing CircleCI Project Setting `CCPC_COMPANY31_APPROVED_SHA` to the **new** exact reviewed head `5016ad711c8940258850cc602e9c9c58ec41c30b`; the old `c27487c60f867be752417088b57186f83ee5997a` must not remain as the configured approval value. Preserve all other Finance/PR28/PR29/PR30 environment variables.
3. Trigger the `ccpcerp-integration-tests` config and checkout on `review/company-source-pnl-gl-reconciliation-2026-10-29`, set **only** `run_company_gl_report31=true` and the remaining optional integration parameters false. Verify head SHA and `company31-manual-approval` before granting one paid held integration job.
4. Review all test logs and real MariaDB results before marking PR31 accepted; separately review voucher-grain accounting and source GL exclusions, returns, timing, permissions and performance before DEVELOPMENT. Any failure requires a new GitHub-first correction and a new approval to spend further credits.

**Status:** PR31 draft and unmerged; no DEVELOPMENT or PRODUCTION actions; **PRODUCTION NO-GO**. Build #46 proves neither a real accounting-code defect nor full PR31 acceptance, only the reported stale test-literal assertion failure.
