# PR #29 — CircleCI Build #40 genuine Frappe/MariaDB Department Report acceptance

**Reviewed:** 2026-10-29. **Scope:** Synthetic disposable report integration only. **Result: PASS, 20/20 installed-Frappe tests.** **Not a merge or deployment authorization.**

## Provenance, source and identity

The project owner shared three unmodified text exports from the completed CircleCI Build #40 job during this conversation:
- `build_40_step_103_container_0.txt`: `PR29 exact-SHA isolated CircleCI identity verified` (only one line visible in this uploaded step; this is **not** a separately itemized proof of the six CI static-policy test method results).
- `build_40_step_104_container_0.txt`: rechecks PR29 exact-SHA CI identity; performs disposable Frappe bench/ERPNext installation and migration on `ci-department-report29.localhost`; ends `PR29 disposable Frappe site installed; no persistent CCPC site used`.
- `build_40_step_105_container_0.txt`: rechecks identity, executes two installed-Frappe test suites against the disposable MariaDB site, and ends `PR29 real Department acceptance finished; review each test and SQL log`.

The source SHA gate script verifies project, checkout branch, job, site, pipeline/workflow identifiers, `CIRCLE_SHA1`, exact `CCPC_DEPT29_APPROVED_SHA` and actual Git checkout; the uploaded step text does not print the full checked-out SHA itself. Independent connected GitHub check status on **exact PR HEAD `dd1375343d84a9b48de8063eb530786d463a4989`** shows **success** on all three recorded CircleCI checks:
- [`ci/circleci: python-syntax`](https://app.circleci.com/workflow/99119f3b-6b72-404b-97b3-70035f5b5cc1/job/c720a531-a111-41a0-8208-5e2037c27444)
- [`ci/circleci: department29-manual-approval`](https://app.circleci.com/workflow/2674a088-6368-4b13-837c-be3473f80f13)
- [`ci/circleci: department-report29-isolated-integration`](https://app.circleci.com/workflow/2674a088-6368-4b13-837c-be3473f80f13/job/22156e7a-b563-4a40-a8a8-727e28323c15)

[App PR #29](https://github.com/ccpcerp/ccpcerp/pull/29) remains **DRAFT, UNMERGED** at SHA `dd1375343d84a9b48de8063eb530786d463a4989` on branch `review/department-original-material-consumption-2026-10-29`, based on unchanged Finance feature `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. PR #28 Intercompany report is separate and also unmerged. All changes were hosted in CircleCI disposable infrastructure, not DEVELOPMENT or PRODUCTION.

## Evidence: 14 + 6 = **20/20 PASS**

| Suite from step 105 | Result | Evidence |
| --- | --- | --- |
| `ccpcerp.ccpc_erp.report.ccpc_department_material_consumption.test_ccpc_department_material_consumption` | **14/14 PASS**, `Ran 14 tests in 0.098s`, `OK` | Step 105, lines 2–27 |
| `ccpcerp.ccpc_erp.test_department_report29_disposable_integration` | **6/6 PASS**, `Ran 6 tests in 5.395s`, `OK` | Step 105, lines 28–50 |

The six named genuine MariaDB tests, all checked green in the uploaded step 105:
1. `test_a_actual_sle_and_expense_gl_reconcile_with_original_report_row`: signed synthetic Withdrawal → posted Stock Entry → actual outbound SLE and GL valuation/Department, and report's issue-time beneficiary and source value.
2. `test_b_mutable_slip_requesting_department_is_not_historical_beneficiary`: modifying editable Withdrawal Slip Department does not reattribute the original posted issue.
3. `test_c_corrupt_row_header_department_and_source_membership_are_flagged`: mismatched source header/row Department and broken Slip-Item source links remain quality exceptions instead of inferred beneficiary.
4. `test_d_missing_ledger_and_mismatched_outbound_qty_are_explicit`: the report flags inconsistent SLE quantity and missing outbound ledger rather than converting missing value to zero.
5. `test_e_real_permission_and_invalid_company_or_date_scope_denied`: nonmanager role and invalid Company/date filters are denied by actual Frappe.
6. `test_f_multiple_real_sle_fragments_count_once_at_original_issue_grain`: two split outbound SLE fragments for the same original item remain **one** issue line and preserve total SLE quantity/value.

These are **scoped** tests. Tests of changed/forged source records run inside disposable site transactions and do not authorize changes to real business records. Existing Finance build #34 **12/12** and Intercompany build #37 **18/18** remain separate evidence; counts must not be merged into a single product certification.

## Installed software and warnings

Step 104 pinned Frappe commit **`988e54f3c4c291e2077a83809663f123731abe76`**, version **16.33.1**, and ERPNext commit **`4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`**, version **16.34.2**. CCPC app was installed from the PR29 review branch, exact-SHA gate passed, and the disposable site completed `bench migrate`.

- **Transient pre-pin dependency warning:** step 104 line 1572 reports Frappe 16.33.1 is below a moving `version-16` ERPNext branch's `>=16.50.0,<17.0.0` requirement. This occurs **before** checkout of pinned ERPNext SHA at line 2152. Direct GitHub verification of `frappe/erpnext` `pyproject.toml` **at pinned SHA** confirms `frappe = ">=16.21.0,<17.0.0"`, which is satisfied by Frappe 16.33.1. Therefore the message does **not** establish an incompatibility in the actually tested pinned pair. Keep pins; in a future reviewed CI cleanup, pin before dependency checks to prevent the misleading warning.
- **Nonfatal Frappe V17 deprecation** in step 105: `limit_page_length` will be removed in v17; observed with all six native tests `OK`. Other npm peer-dependency and Vite warnings were nonfatal in installation output.

Owner-reported CircleCI remaining balance: **27,980 credits**, compared to previously reported **28,115** (difference **135**). This delta is **not** a provider-itemized cost of Build #40. The single PR29 run approval was consumed; no paid retry or further run is authorized by these logs.

## Unverified business and release acceptance boundaries

- This confirms the **original-issue, gross SLE/verified beneficiary Department register** in an isolated synthetic sample. It is **not** certified Department P&L or net material consumption after stock returns, GL reversals/reposts, adjustments or cross-currency differences.
- Actual Requesting/Work-for Section and requesting Department are **not independently frozen** on original Stock Entry Detail in inspected code; the report intentionally signals `NO_ORIGINAL_SECTION_SNAPSHOT` rather than inferring historical Section from current editable Withdrawal Slip.
- Additional tests still needed before release: real Company-specific System Manager user-permission isolation, genuine missing/renamed Department masters, row cap and long-range performance/`EXPLAIN`, posting/repost date edge cases, cancelled returns, concurrent ledger behavior, multiple UOM scenarios, full ledger/accounting reconciliation and representative CCPC DEVELOPMENT business data.
- Only the owner can authorize any PR merge, DEVELOPMENT pull/migrate/test, or PRODUCTION deployment. Preserve backups and rollback safety before environment changes. **PRODUCTION NO-GO.**

## Next controlled steps

1. Review PR #29 accounting scope/security after the passing SQL evidence and decide whether to address material gaps (especially issue-time Section capture) as a separate business-design change. No automatic schema/migration change.
2. Continue the two outstanding day-one report families on separate GitHub-first branches: Equipment/Job Order cost, then Company-wide inventory consumption versus P&L GL reconciliation. Use only the owner-approved scope and new explicit approval for any paid CI.
3. Keep PRs #28/#29 draft until the owner explicitly approves merge and controlled DEVELOPMENT acceptance. Never infer a production release from passing synthetic CI.

**Evidence document branch:** `docs/ccpc-checkpoint-2026-10-10`. No credentials, source business data, raw runner logs, or ephemeral databases were committed.
