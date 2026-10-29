# PR #30 — Equipment original material and separate unpriced Job activity

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
