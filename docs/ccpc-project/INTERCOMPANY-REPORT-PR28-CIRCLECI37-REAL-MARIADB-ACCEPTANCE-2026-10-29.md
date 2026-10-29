# PR #28 — CircleCI build #37 real Frappe/MariaDB report acceptance (2026-10-29)

## Evidence provenance and scope

Owner supplied three raw CircleCI job step text exports in the active ChatGPT conversation:
`build_37_step_103_container_0.txt` (CI identity), `build_37_step_104_container_0.txt` (disposable installation), and `build_37_step_105_container_0.txt` (actual installed-Frappe test results). These logs were reviewed on 2026-10-29. This document is the concise versioned evidence record; no raw logs, credentials, synthetic database records or owner private data are committed.

- Application repository: [ccpcerp/ccpcerp](https://github.com/ccpcerp/ccpcerp), [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28), review branch `review/intercompany-source-billing-report-2026-10-29`.
- **Exact approved and verified GitHub PR head:** `444d1dcb795e79a97b0db7be487e529fa7a2fba2`. Finance base remains `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. Draft PR #28 remained **open, unmerged** at verification.
- Exact-SHA identity from step 103: `PR28 exact-SHA isolated CircleCI identity verified`. Same message appeared at start of installation and test steps. The reviewed stage code checks CircleCI identity, branch, site, job, project-variable approved SHA, CircleCI source SHA and actual checked-out Git SHA; the raw log does not itself print the full checked-out SHA.
- The connected GitHub status checks **independently showed success** for `ci/circleci: python-syntax`, `ci/circleci: report28-manual-approval`, and `ci/circleci: intercompany-report28-isolated-integration` on that exact commit. [Report integration job](https://app.circleci.com/workflow/b7ed03f0-4454-49f4-86df-1cec7dfdad77/job/7d1722f1-a551-4c15-9c9a-e1b7af42511a), [starter Python job](https://app.circleci.com/workflow/23c8d4c0-5d8a-4e9e-b589-459a1cb9555a/job/7eb781d3-3108-4300-8b08-5b1f1d0dcd8e).
- Test site `ci-intercompany-report28.localhost` was created/migrated on disposable CircleCI sidecar MariaDB and Redis; Frappe and ERPNext installed. No DEVELOPMENT/PRODUCTION connection, migration, release, cleanup, merge, master-data operation or persistent business-data change was performed by ChatGPT. Hosted pipeline was manually triggered and approved by the owner.

## Results: **18/18 PASS** on CircleCI #37

Step 105 real Frappe test-run evidence:

| Installed-Frappe suite | Result | Source line |
| --- | --- | --- |
| `ccpcerp.ccpc_erp.report.ccpc_intercompany_withdrawal_billing_status.test_ccpc_intercompany_withdrawal_billing_status` | **13/13 PASS**, `Ran 13 tests in 0.080s`, `OK` | step 105, lines 2–24 |
| `ccpcerp.ccpc_erp.test_intercompany_report28_disposable_integration` | **5/5 PASS**, `Ran 5 tests in 7.738s`, `OK` | step 105, lines 27–48 |

All five native MariaDB cases in step 105 passed:

1. `test_report_a_submitted_source_unbilled_then_draft_claim` — posted synthetic original issue, actual SLE and expense GL, visible unbilled row, then a real Draft billing claim.
2. `test_report_b_finalized_real_invoice_pair_stays_draft` — actual source and test-clock month-end, native paired SI/PI **Draft** status, reciprocal references and independent frozen billing amount.
3. `test_report_c_two_active_claims_fail_closed` — duplicate active billing claim caused a fail-closed report error rather than doubled financial value; corrupt setup is test-only within disposable transaction.
4. `test_report_d_scope_and_non_manager_are_rejected` — nonmanager access denied and invalid date/Company filters refused using real Frappe execution.
5. `test_report_e_forged_source_and_invoice_links_raise_quality_flags` — report flagged deliberately forged billing source, nonreciprocal invoice reference and missing foreign source while retaining original issue valuation.

Step 104 confirms pinning Frappe to commit `988e54f3c4c291e2077a83809663f123731abe76` (Frappe 16.33.1) and ERPNext to `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` (ERPNext 16.34.2), with app installed at the owner-approved review source. The site installer completed successfully. **No other source/report family was covered by these 18 tests.**

## Warnings, limitations and accounting/release decisions

- **Transient pre-pin branch compatibility warning, resolved by reading the pinned ERPNext manifest:** step 104 warned `Installed frappe-dependency 'frappe' version '16.33.1' does not satisfy required version '>=16.50.0,<17.0.0'` while `bench get-app --branch version-16` was fetching the *moving branch*. This is **before** the script checked out immutable ERPNext commit `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`. Direct GitHub verification of `frappe/erpnext` `pyproject.toml` at that **pinned SHA** confirms `[tool.bench.frappe-dependencies] frappe = ">=16.21.0,<17.0.0"`; pinned Frappe **16.33.1 satisfies this**. Hence this log warning does not show a version incompatibility in the actually tested pair. In any future CI harness cleanup, checkout the reviewed ERPNext SHA before dependency validation to avoid confusing transient-branch warnings. Preserve both pins and this accepted run; do not conflate successful report tests with full ERPNext functional certification.
- **Nonfatal deprecation:** step 105 emitted a V17FrappeDeprecationWarning for `limit_page_length`; all five native report cases still passed.
- Credit snapshot: owner reported **28,215** credits before triggering and **28,115** after sharing results (difference **100**). This is a balance comparison, **not** an independently verified per-job bill or a future budget authorization.
- The report was exercised with synthetic Companies and inventory on a disposable isolated database, not real CCPC Company accounting masters or persistent DEVELOPMENT. It does **not** test invoice submission, posted SI/PI AR/AP/GL, returns/reversals or stock reposting, cross-currency cases, heavy load/`EXPLAIN`, concurrency, true per-Company System Manager denials, historical legacy source attribution or all report dimensions.
- The separate Finance build #34 12/12 remains its own prior accepted source→ledger→billing-bridge evidence. It is **not** part of the new 18/18 report count. The original report offline 13/13 + SQLite 12/12 are separate preflight results.
- Build #37 is **PASS for the scoped PR #28 report integration gate**. PR #28 stays draft/unmerged until source review, additional acceptance/risk decisions and explicit owner authorization. No automatic CI rerun or new charged tests are authorized by this single-run result. **PRODUCTION NO-GO.**

## Recommended shortest next actions

1. Record/retain this CI evidence (done), review PR #28's reporting-only implementation and external approval gates. Pinned manifest compatibility was verified; when changing CI next, eliminate the transient pre-pin warning without invalidating the exact-SHA evidence.
2. Continue **already-approved four day-one reporting families**: build Department material consumption from original posted SLE, immutable requesting/work-for dimensions, then Equipment/Job costing and Company-wide GL reconciliation, each on reviewed GitHub branches and with security/source-quality tests.
3. Request distinct owner approval for any PR merge, paid CircleCI run, DEVELOPMENT pull/migrate/test, or PRODUCTION release. Preserve source valuation vs invoice amounts, Company/currency/UOM boundaries and fail-closed duplicate/forgery behavior.

**Verified GitHub branch:** `docs/ccpc-checkpoint-2026-10-10`. This document is an evidence record, not a deployment authorization.
