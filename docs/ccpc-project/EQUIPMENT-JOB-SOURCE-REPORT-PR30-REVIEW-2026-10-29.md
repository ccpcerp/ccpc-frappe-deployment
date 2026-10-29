# PR #30 — Equipment original material and separate unpriced Job activity

**Superseding acceptance (Build #43):** Owner-provided CI logs and GitHub checks verify **15/15 Frappe report unit + 5/5 genuine MariaDB integration PASS** at unchanged PR30 SHA `872d56b4b908a571daf581df20e4b56661531c6e`. See [Build #43 acceptance/limitations](EQUIPMENT-REPORT-PR30-CIRCLECI43-REAL-MARIADB-ACCEPTANCE-2026-10-29.md). Prior **NOT EXECUTED** notes below describe historical preparation, **not current test status**. PR is still draft/unmerged, DEV/PROD untouched.

**Date:** 2026-10-29. **State:** GitHub-only draft; authored tests not executed, no CI, no merge, no DEVELOPMENT, no PRODUCTION.

## Verified starting point

- [Current development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [four approved reporting families](FOUR-DAY-ONE-REPORTS-GITHUB-FIRST-PLAN-2026-10-29.md).
- App Finance branch `feature/finance-mapping-lifecycle-2026-10-28`, exact HEAD `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28) Intercompany and [PR #29](https://github.com/ccpcerp/ccpcerp/pull/29) Department are distinct DRAFT/unmerged; their successful CircleCI #37 and #40 tests **do not** test PR #30.
- Existing `CCPC Equipment Maintenance Baseline` report remains in app base, and [its 2026-10-18 evidence](EQUIPMENT-SNAPSHOT-REPORT-CUTOVER-AND-FORGED-VOUCHER-2026-10-18.md) established prior *separate* 13/13 genuine MariaDB snapshot source integration on older commit. The baseline provides gross SLE Equipment aggregation and unpriced Job Order summaries, **not** complete maintenance cost. We did not change it.
- `withdrawal_slip_stock.py` copies Withdrawal Slip `equipment` to original `Stock Entry Detail.ccpc_equipment_at_issue` and `ccpc_equipment_code_at_issue` and protects those on later submit edits, per inspected application source. The inspected original Stock Entry Detail does **not independently freeze `Withdrawal Slip.job_order`**. Current Job Order Equipment, and today's Slip Job link, cannot be certified as the historical linkage for a posted Material Issue.

## New report design and review

[Draft PR #30](https://github.com/ccpcerp/ccpcerp/pull/30) branch `review/equipment-job-source-cost-report-2026-10-29` at verified original HEAD **`0243c5d8feaae3622149316b1ad2d7cbb92d8467`** from Finance base above. GitHub compare: **five newly added files only**, no existing application/CI/report files edited, zero behind base.

New Script Report `CCPC Equipment Job Material Activity` under `ccpcerp/ccpc_erp/report/ccpc_equipment_job_material_activity/`:
- `__init__.py`
- `ccpc_equipment_job_material_activity.py`
- `ccpc_equipment_job_material_activity.json`
- `ccpc_equipment_job_material_activity.js`
- `test_ccpc_equipment_job_material_activity.py`: **15 Frappe unit methods authored, not executed**.

**Source rules:**
1. `ORIGINAL_MATERIAL_ISSUE` each original submitted Material Issue + exact Stock Entry Detail + Company-matched Withdrawal Slip and Item membership. Aggregate noncancelled **outbound** SLE first at `company + voucher_no + voucher_detail_no` grain, Company and posting-window bound, then join; one report line per original issue detail. Gross signed source-value in issuer Company currency, quantity in original stock UOM. Do **not** net return SLE, sum unlike UOMs, or call value posted GL.
2. Equipment = original immutable-pipeline `ccpc_equipment_at_issue` Link/`ccpc_equipment_code_at_issue` Data **only if both present and agree**, plus a Company-matched Equipment Registry. Missing/foreign/mismatch source stays unattributed but preserves original Stock Ledger value. Current Slip Equipment conflict is a separate quality flag, never historical reclassification. Broken Slip Item, missing/mismatched SLE and unusual negative valuation remain visible exceptions.
3. `UNPRICED_JOB_ORDER_ACTIVITY` from standalone same-Company Job Order dated operational rows, status and positive recorded labor hours only; money and currency **NULL**. No join to original material details. Original material rows have `job_order=NULL`, `NO_FROZEN_JOB_LINK_ON_ORIGINAL_ISSUE` warning. Current Job Order Equipment is operational reference only. No labor rates, third-party service, downtime, actual net costing, Job Order bill, ROI/replacement recommendation, or P&L conclusion.
4. Mandatory Company/posting from/to, optional Equipment; System Manager-only, required source DocType permission checks, Company and Equipment read and Company-match validation, and per-result Stock Entry/Slip/Equipment/Job document permission checks before returning data. Date window max 367 inclusive days, caps 800 material issue and 200 job rows, explicit fail-close on overflow and duplicate original source. Filter carries explicit warning that other unattributed Company issues are excluded. Report totals disabled.
5. The work does not alter existing user permissions, original issue schema, stock/GL/invoice controllers, or any deployment.

**Source-review preflight:** 19/20 initial GitHub structural checks passed; the apparent failure was an overly broad scan matching the explanatory comment `No read of ws.job_order`. A subsequent connector readback explicitly examined only the returned original-source SQL string and verified **no `ws.job_order`, `ws.department` or GL join**; thus the corrected code-aware static review was **20/20 PASS**. This is still source-only inspection, **not** an executable Frappe test or genuine SQL validation.

## Remaining acceptance

- Python syntax and actual 15 Frappe unit tests, MariaDB SQL schema validation, synthetic posted Equipment-linked Withdrawal→SLE, split SLE one-source-row check, stale/cross-Company Equipment, missing legacy snapshots, Job activity and restrictions, and SQL `EXPLAIN` performance, all on a separately approved disposable site.
- Full source attribution from job to issue requires **distinct owner-approved original issue-time capture policy** and possibly schema migration; no retrospective backfill from today's Slip or Job Order.
- No paid CI run is authorized by this source-only milestone; no merge or persistent DEVELOPMENT / PRODUCTION operations. **PRODUCTION NO-GO.**

**Next report-family dependency:** Company-wide Stock/SLE vs P&L GL independent-perspectives reconciliation, based on original voucher grain and explicit unreconciled variance flags.

## Current gate (2026-10-29): dedicated real Frappe/MariaDB CI harness prepared, NOT RUN

- Current [draft PR #30](https://github.com/ccpcerp/ccpcerp/pull/30) head verified at **`872d56b4b908a571daf581df20e4b56661531c6e`** on `review/equipment-job-source-cost-report-2026-10-29`, unchanged Finance base `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. GitHub compare: **10 changed paths**, five new source/report files, four new CI/fixture files, only existing file changed is `.circleci/config.yml`; zero behind base.
- Owner requested to continue real acceptance. The CI harness itself is now prepared **without** a paid hosted execution, modifying only the PR review branch. Separate exact-SHA guard `ci_equipment30_site_guard.py` checks CircleCI identity, current PR review branch, `equipment-report30-isolated-integration`, `ci-equipment-report30.localhost`, `CIRCLE_SHA1`, exact `CCPC_EQUIP30_APPROVED_SHA` from project settings (unconfigured by ChatGPT), and `CCPC_ALLOW_EQUIP30_TESTS=isolated-only`.
- `.circleci/config.yml` has `run_equipment_report30=false` by default, a separate branch-filtered `equipment30-manual-approval` followed only by `equipment-report30-isolated-integration`. Older Finance workflows are preserved; no automation, PR-label trigger to costly work, provider context or stored SHA was added.
- `.circleci/equipment30_stage.sh`: pre-install exact-SHA guard and six new pure-Python source CI checks in `.circleci/test_equipment30_ci_config_static.py`; 90-minute cumulative subprocess deadline, disposable MariaDB/Redis, pinned previously green Frappe `988e54f3c4c291e2077a83809663f123731abe76` / ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`; then 15 authored Frappe report unit cases plus **five new native synthetic MariaDB cases** in `ccpcerp.ccpc_erp.test_equipment_report30_disposable_integration`. Native cases reuse authenticated Finance maker/checker and submitted original withdrawal/SLE/GL fixture without inheriting other Finance test methods. The 90-minute runner deadline is **not** a hard credit-spend cap.
- **Structural review: 17/17 focused GitHub readback conditions PASS.** The actual six static CI cases, 15 Frappe unit cases, five native MariaDB cases, CircleCI parser, SQL performance/`EXPLAIN`, real Company permission and fixture-specific runtime behavior **have not been executed**. Do not describe them as green or production-ready. Actual CircleCI success status is not yet known.
- **Next bounded approval/operator gate:** independently approve one exact reviewed-SHA, manually held CircleCI run for PR #30, no automatic retries; add a new CircleCI Project Settings variable `CCPC_EQUIP30_APPROVED_SHA` with this full SHA **without deleting prior Finance/PR28/PR29 values**. Trigger config and checkout from `review/equipment-job-source-cost-report-2026-10-29` with only `run_equipment_report30=true`, inspect `equipment30-manual-approval` before clicking Approve, and retain step outputs for source/GL accounting review. No merge or DEVELOPMENT/PRODUCTION changes. **PRODUCTION NO-GO.**
