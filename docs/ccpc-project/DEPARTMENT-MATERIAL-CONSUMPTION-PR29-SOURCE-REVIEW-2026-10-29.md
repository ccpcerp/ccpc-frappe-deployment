# CCPC Department Material Consumption — PR #29 source review

**Date:** 2026-10-29. **Status:** GitHub-only five-file first implementation, draft/unmerged, not Frappe or MariaDB tested.

## Source-of-truth and existing accounting behavior

- Review app code on Finance feature `feature/finance-mapping-lifecycle-2026-10-28` at `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`, and the [four day-one reporting plan](FOUR-DAY-ONE-REPORTS-GITHUB-FIRST-PLAN-2026-10-29.md).
- In `withdrawal_issue_beneficiary.py`, `resolve_beneficiary_department` explicitly selects Work-for Department or valid Equipment Department only when no explicit source exists; it rejects conflicts and does **not** default to the Requesting Department. `apply_issue_beneficiary` writes the accounting beneficiary into **both** original Stock Entry header `department` and each Stock Entry Detail `department`.
- `withdrawal_slip_stock.py` validates original voucher, item membership and posting, invokes `validate_issue_beneficiary` before posting, and protects submitted issue `company`, header `department`, posting date/time and item `department` through the application update-after-submit hooks. These are controller guarantees in ordinary authenticated ERPNext flows, **not** independently fraud-proof against direct SQL or malicious database changes.
- The Withdrawal Slip currently has `department`, `section`, `work_for_department`, `work_for_section`, but the inspected original issue creation code does **not** independently freeze Requesting Department/Section or Work-for Section in the posted Stock Entry Detail. Billing child Department/Section snapshots are captured later at billing preview, which is **not** historical issue-time provenance. Do not backfill from current Slip or advertise as certified Section costs.

## Implemented draft

[App draft PR #29](https://github.com/ccpcerp/ccpcerp/pull/29) uses branch `review/department-original-material-consumption-2026-10-29`, created from exact verified Finance base `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`; current app PR head at initial review **`1757e42d866c3a75da16a9a80e0942c675606d57`**.

Five **new** files, and no existing business, CI, permission, migration, or deployment file changes:

1. `ccpcerp/ccpc_erp/report/ccpc_department_material_consumption/ccpc_department_material_consumption.py` — conservative read-only Script Report.
2. `.../ccpc_department_material_consumption.json` — System Manager role, `apply_user_permissions=1`, no total row.
3. `.../ccpc_department_material_consumption.js` — required issuing Company/from/to dates, optional beneficiary Department filtered by Company.
4. `.../__init__.py` — Python module package.
5. `.../test_ccpc_department_material_consumption.py` — 14 authored source, security, quality and row-cap unit scenarios, **not yet executed**.

The report:
- Queries exact submitted `Stock Entry` with `purpose='Material Issue'` and valid issuing-Company-matched Withdrawal Slip; links each original Stock Entry Detail to its matching Withdrawal Slip Item.
- Collapses **only noncancelled outbound** Stock Ledger Entry fragments by `voucher_no`, `voucher_detail_no`, and Company before joining to the original row. Uses Company-bound dates and static parameterized queries. Exposes `issued_qty` and `sle_issued_qty` separately, source signed gross issue value in **issuer currency**. Gross stock valuation is **not** posted expense GL, return-adjusted net, billed intercompany amount or equipment/labor cost.
- Marks `beneficiary_department_at_issue` only if item Department and header Department match and resolve to a Department master belonging to issuing Company. Else shows NULL in verified column, the raw source Department references, and quality flags. No Group/summarized totals to mask exceptions/mix unlike UOMs or currencies.
- Exposes missing outbound SLE vs zero stock cost, quantity mismatches, negative valuation signs, broken Withdrawal Slip Item link, source Item mismatch, missing/other-company Department master and header/row Department conflicts.
- Section provenance is **explicitly `NO_ORIGINAL_SECTION_SNAPSHOT`** for all current original issues; neither requesting Department nor Work-for Section is presented as a verified original snapshot.
- Limits output to 1000 original source rows and dates to at most 367 inclusive days; throws rather than silently truncating. Requires System Manager, six source DocType read rights, Company document read, optional Department read and Company match, and read permission for each Department identity appearing on the resulting source rows. Conflicting source row under a Department filter is retained if either header or row matches.

## Verification and remaining gates

- Connector readback confirmed **20/20 focused structural checks PASS**, source shape, SQL safety, Company/Department permissions, frozen-source policy, row cap, explicit currency, no GL/billing aggregation, no write operations, report metadata, and 14 authored tests. GitHub compare: **5 new paths**, 0 behind Finance base, no existing files modified.
- **NOT YET PASSING ANY EXECUTABLE SUITE:** Python compile, the 14 unit test cases in Frappe, native MariaDB, real permission behavior, SLE fragmentation/posting/repost, end-to-end Department ledger and `EXPLAIN` performance. The owner's 18/18 Build #37 result belongs to **Intercompany PR #28** exclusively.
- Risks to verify: real ERPNext Department Accounting Dimension schema on disposable site, System Manager Stock Ledger Entry DocType permission, historical missing Department and disabled/renamed master, date scoping of reposted SLE and accepted returns, cross-company/user permission scope, quantity group by distinct UOM. Exact source row financial value deliberately remains independent of GL until Company-wide reconciliation report.

## Next fastest safe path

A single manually held, default-off, exact-commit-SHA disposable Frappe/ERPNext/MariaDB job reusing the proven Finance fixture would validate this report. Its CircleCI config/project-variable/credit exposure and any paid run require a distinct scoped authorization. Do **not** reuse the consumed PR #28 single-run approval to run PR #29. A slower fallback is more offline unit/SQLite mocks. Development and production sites must not be touched without separate approval.

**PRODUCTION NO-GO.** No merge or deployment is implied by this source milestone.
