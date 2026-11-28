# PR #31 — CircleCI Build #49 native MariaDB SLE vs P&L GL acceptance

**Recorded:** 2026-10-29. **Result:** **20/20 PASS** in pinned, disposable Frappe/ERPNext + MariaDB: **15/15 installed-Frappe report unit tests + 5/5 genuine synthetic database integration tests**. This is bounded source/voucher-level reporting acceptance, **not** complete P&L certification, DEVELOPMENT integration, merge or PRODUCTION release.

## GitHub identity and evidence

- [Draft app PR #31](https://github.com/ccpcerp/ccpcerp/pull/31), branch `review/company-source-pnl-gl-reconciliation-2026-10-29`, unchanged exact head **`5016ad711c8940258850cc602e9c9c58ec41c30b`**, shared Finance base `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. Verified DRAFT and UNMERGED.
- Owner uploaded three Build #49 raw text logs to this conversation; keep raw logs out of GitHub to avoid giant installation artifacts. `build_49_step_103_container_0.txt` contains `PR31 exact-SHA isolated CircleCI identity verified`. This **one-line summary does not individually report six pure-Python CI-guard method outcomes**, nor print the complete SHA; do not separately claim 6/6 by inference.
- `build_49_step_104_container_0.txt` confirms the identity check, pinned framework installation, ERPNext/CCPC installation and successful migration of **`ci-company-gl-report31.localhost`**, concluding `PR31 disposable Frappe site installed; no persistent CCPC site used`. Step 104 log includes `HEAD is now at 988e54f` (Frappe 16.33.1) and `HEAD is now at 4048fb7` (ERPNext 16.34.2), and independent setup checks in the reviewed job enforce full pin hashes.
- `build_49_step_105_container_0.txt`: same CI identity; report policy unit `Ran 15 tests in 0.088s`, `OK`; native database `Ran 5 tests in 4.601s`, `OK`; `PR31 real Company GL acceptance finished; review each test and SQL log`. An unrelated nonfatal Frappe v17 `limit_page_length` deprecation warning appears.
- Independent GitHub exact-commit status check at `5016ad711c8940258850cc602e9c9c58ec41c30b` confirms:
  - [`ci/circleci: python-syntax`](https://app.circleci.com/workflow/f8486b5d-1faa-4087-b6d4-ff134c99161c/job/f7b6703d-b199-4d0f-ae11-728f1abccca5) — **success**
  - [`ci/circleci: company31-manual-approval`](https://app.circleci.com/workflow/6f3cfe40-dc83-4560-9dfb-f4b9c0cbd9d1) — **success**
  - [`ci/circleci: company-gl-report31-isolated-integration`](https://app.circleci.com/workflow/6f3cfe40-dc83-4560-9dfb-f4b9c0cbd9d1/job/4bd8c926-3767-4992-90b5-2f82018d037d) — **success**

## Scope of all twenty tests

**15/15 policy/source presentation unit tests in installed Frappe:** Company and date permission/filter validation; duplicate original-stock or GL-group denial; all material issues including those without CCPC Withdrawal Slip; source vs posted P&L Expense GL match and variance shape; missing GL/SLE displayed as **NULL not zero**; separate Income and non-Stock Entry vouchers; partial SLE/negative valuation flags; per-record Stock Entry and Account read; Income not misinterpreted as Expense; P&L Account classification, cancellation and submitted GL SQL guards; row caps and issuer currency; sum multiple expense Accounts *at voucher grain* exactly once; original signed source SQL matching the actual `ON ledger.company = se.company` join; System Manager/source permissions.

**5/5 real MariaDB native tests using signed synthetic Finance maker/checker + submitted original material issue:**
1. `test_a_real_submitted_stock_sle_and_posted_expense_gl_match`: authentic submitted Stock Entry, outbound original SLE and posted P&L Expense GL values agree in the fixture; two separately labeled report perspectives; issuer Company currency; SLE value not duplicated onto P&L GL rows.
2. `test_b_changed_expense_gl_is_flagged_not_silently_net_matched`: disposable fixture-only GL debit alteration yields a correctly flagged voucher variance, retaining unchanged original stock SLE value. **Not a sanctioned manual GL adjustment for real books.**
3. `test_c_missing_expense_gl_is_explicit_missing_not_zero`: fixture-only cancellation flags on eligible Expense GL produce explicit missing GL, with **NULL** GL-side value and variance rather than fake zero.
4. `test_d_missing_or_split_outbound_sle_retains_original_voucher`: fixture-only cancelled outbound SLE yields missing-source exception and NULL original stock value; original voucher remains visible; re-enabling those records restores one original issue row. **This test does not manufacture additional split SLE fragments**, despite its method name.
5. `test_e_real_access_and_company_date_scopes_fail_closed`: actual role denial (non-System-Manager) and invalid Company/date filters on disposable test site; authorized source remains accessible.

The test suite does not prove GL Account completeness/reconciliation across all CCPC transactions, cross-company intercompany eliminations, financial statement tie-out, returns/reposts, account classification for real Company masters, user-permission combinations in persistent sites, large-range performance/index plans, issue-time Section or Job Order accounting links or finalized invoices.

## Prior failure and framework warning

- **Previous Build #46 at old SHA `c27487c60f867be752417088b57186f83ee5997a` FAILED**: 14/15 source-unit cases passed, one wrong string expectation `AND ledger.company = se.company` vs correct SQL `ON ledger.company = se.company`; native suite did not run. [Historical failure/correction record](COMPANY-GL-REPORT-PR31-CIRCLECI46-FAILURE-AND-FIX-2026-10-29.md) remains preserved.
- One-line test-only correction at **`5016ad711c8940258850cc602e9c9c58ec41c30b`** was verified through GitHub old/new compare, with unchanged report SQL. **Build #49 supersedes only the untested status at this new SHA; do not retroactively mark Build #46 as successful.**
- The Build #49 installer logs a **temporary dependency warning** while fetching moving ERPNext `version-16` (`frappe>=16.50.0,<17.0.0`) before checking out pinned ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`. The pinned version's independently checked `pyproject.toml` requires `frappe>=16.21.0,<17.0.0`, compatible with pinned Frappe 16.33.1 (`988e54f3c4c291e2077a83809663f123731abe76`). **Do not call the tested pin pair incompatible.** Asset build peer warnings and the v17 deprecation warning are nonfatal in this scoped run.

## Owner approvals, credits, and deployment boundary

- The owner separately authorized **one manually held Build #49 re-execution** after Build #46 failure. The run has succeeded; **no further run, auto retry, or paid workflow is authorized**.
- Owner-reported **27,689 CircleCI credits remaining** after Build #49 vs **27,799 before**: balance change **110**, **not** an itemized provider per-job bill. Prior Build #46 consumed its own manual authorization.
- All four owner-approved day-one read-only report PRs now have separately passing scoped synthetic Frappe/MariaDB acceptance: [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28) **18/18**, [PR #29](https://github.com/ccpcerp/ccpcerp/pull/29) **20/20**, [PR #30](https://github.com/ccpcerp/ccpcerp/pull/30) **20/20**, PR #31 **20/20**. **These are independent scoped reports, not a fully merged or DEVELOPMENT-integrated four-report accounting suite.**
- **All four PRs remain drafts/unmerged.** Different PR branches share the same Finance base, so combining them requires a separately reviewed merge/integration order, regression review and owner authorization. No persistent DEVELOPMENT or PRODUCTION changes are justified by these CI results.
- Subsequent gate: obtain owner's authorization for reviewed integration sequence and safe DEVELOPMENT pull. Check current branch/commit/working tree/status, preserve outstanding work and backups before any application, prove genuine CCPC permissions, master mappings, source vs GL totals, returns/reversals and rollback. **PRODUCTION NO-GO** until its own explicit backup/recovery/rollback/cutover approval.

**Documentation branch:** `docs/ccpc-checkpoint-2026-10-10`. This record reports observed test logs and independently verified GitHub status; no secrets, raw fixture records or full pipeline logs committed.
