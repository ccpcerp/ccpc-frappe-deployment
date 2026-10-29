# PR #30 — CircleCI Build #43 genuine Equipment / Job Activity MariaDB acceptance

**Reviewed:** 2026-10-29, via owner-provided unmodified step logs. **Result: 20/20 installed-Frappe report tests PASS.** Scope: synthetic, isolated disposable MariaDB; **not** full Equipment/Job Cost, persistent DEVELOPMENT acceptance, merge or PRODUCTION authorization.

## GitHub/CI identity

- [Draft app PR #30](https://github.com/ccpcerp/ccpcerp/pull/30), branch `review/equipment-job-source-cost-report-2026-10-29`, exact verified HEAD **`872d56b4b908a571daf581df20e4b56661531c6e`**, based on Finance feature SHA **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**. DRAFT and UNMERGED at verification.
- Owner uploaded three CircleCI **Build #43** text exports to this chat, not committed as raw logs:
  - `build_43_step_103_container_0.txt`: `PR30 exact-SHA isolated CircleCI identity verified`. This one-line identity summary **does not itemize the six pure-Python static CI safeguard test method outcomes**.
  - `build_43_step_104_container_0.txt`: `PR30 exact-SHA isolated CircleCI identity verified` before creation of the disposable bench; confirms Frappe/ERPNext/CCPC installation and migration on **`ci-equipment-report30.localhost`**, ending `PR30 disposable Frappe site installed; no persistent CCPC site used`.
  - `build_43_step_105_container_0.txt`: same CI identity check, **15 report unit tests `OK`** and **5 real Frappe/MariaDB integration tests `OK`**, ending `PR30 real Equipment acceptance finished; review each test and SQL log`.
- Independent GitHub exact-commit combined-status query confirmed three successful statuses:
  - [`ci/circleci: python-syntax`](https://app.circleci.com/workflow/7d67c22d-0e0c-4e01-b095-af886fde5e4d/job/71e4d7dc-7754-4e3b-bc60-fda077632cfb): **success**
  - [`ci/circleci: equipment30-manual-approval`](https://app.circleci.com/workflow/862cc580-c593-4237-994c-3d4fba1a7f0a): **success**
  - [`ci/circleci: equipment-report30-isolated-integration`](https://app.circleci.com/workflow/862cc580-c593-4237-994c-3d4fba1a7f0a/job/b8887073-a41f-4780-af51-c12f60f0fdf0): **success**
- The uploaded text says the exact-SHA identity guard succeeded, but does not print the entire checked-out app SHA. The exact PR SHA and green provider check identities were verified independently in GitHub; do not overstate a full-SHA printout in the text log.

## 15 + 5 = **20/20 PASS**

| Installed Frappe suite (step 105) | Outcome |
| --- | --- |
| `ccpcerp.ccpc_erp.report.ccpc_equipment_job_material_activity.test_ccpc_equipment_job_material_activity` | **15/15 PASS**, `Ran 15 tests in 0.092s`, `OK`; step-105 lines 2–27 |
| `ccpcerp.ccpc_erp.test_equipment_report30_disposable_integration` | **5/5 PASS**, `Ran 5 tests in 3.580s`, `OK`; step-105 lines 29–49 |

The five genuine MariaDB test methods named in the step 105 log:
1. `test_a_real_signed_source_and_exact_outbound_sle` — signed Finance maker/checker mapping, authenticated issuance of a submitted material Stock Entry, original Equipment snapshot, exact outbound Stock Ledger source quantity/value and issuing Company currency.
2. `test_b_mutable_slip_equipment_does_not_relabel_posted_snapshot` — changing current Withdrawal Slip Equipment does not change the original Equipment attribution or gross SLE source amount; discrepancy remains visible.
3. `test_c_invalid_snapshot_and_source_membership_surface_exceptions` — corrupted original Equipment snapshot pair and invalid Withdrawal Slip Item membership remain flagged and preserve source value without relabeling.
4. `test_d_real_job_order_activity_is_unpriced_and_not_source_link` — a real Job Order linked to Equipment appears as **separate operational/unpriced activity**, not a material-to-Job Order accounting link. Material issue has no assumed Job Order cost attribution.
5. `test_e_actual_role_filter_company_and_date_rejections` — genuine non-Manager and invalid Company/date filters rejected; correctly scoped source still readable to authorized synthetic fixture.

The 15 source/report unit tests in installed Frappe cover metadata currency/no totals, row-level permission checks, source-detail duplicate denial, equipment-filter warning, Company/date and Company-specific Equipment scope, independent Job query, exact voucher/detail SLE grain, missing/foreign legacy snapshot and slip membership exceptions, current Slip edit conflict, source/job cost separation, role denial, row-cap, SLE anomalies and unpriced labor hours.

**Do not count these 20 cases together with earlier Finance/PR28/PR29 tests as one end-to-end production certification.** The six separate CI safeguard method outputs were not itemized in the provided identity step; no explicit 6/6 claim on that basis.

## Bench versions and nonfatal warnings

- Frappe **16.33.1**, Git SHA `988e54f3c4c291e2077a83809663f123731abe76`; ERPNext **16.34.2**, Git SHA `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`. CCPC app installed from the isolated PR30 branch; site completed `bench migrate`.
- Installer emitted a **temporary/pre-pin warning** when fetching moving ERPNext `version-16`: Frappe 16.33.1 did not satisfy a moving requirement `>=16.50.0,<17.0.0` (step-104 log line 1568). **After** that warning, ERPNext was checked out to the pinned commit (line 2148). Live connected GitHub readback of `frappe/erpnext` `pyproject.toml` **at the pinned SHA** confirms `frappe = ">=16.21.0,<17.0.0"`, compatible with pinned Frappe 16.33.1. Do **not** report the tested pinned pair as incompatible.
- Test step 105 issued a **nonfatal Frappe v17 deprecation warning** about `limit_page_length` in `qb_query.py`. Other npm peer and Vite build warnings were nonfatal.

## Accounting and operational limits

- The report is a **read-only original posted Material Issue outbound SLE gross Equipment value register**, not net stock consumption after return/repost, GL-certified Expense P&L, service/vendor/labor cost, downtime or total equipment maintenance cost.
- Original issue-time Equipment Link + Equipment Code must agree and map to same-Company Equipment Registry; unknown, missing or corrupted links must remain unattributed. Current editable Withdrawal Slip Equipment is **not** historical source for a posted issue.
- **No original frozen Job Order link** from posted Stock Entry Detail exists in reviewed app path. The Job Order branch shows separate, **unpriced** operational activity only. A per-Job Order material-cost financial figure would require a separate approved immutable issue-time source-capture design/migration, not retrospective joining on current Slip fields.
- Further acceptance gates: true Company/user-permission isolation beyond synthetic role, multiple-UOM and mixed-item rows, large-range query plans/`EXPLAIN` and row caps, returns/valuation reposting/time boundaries, cross-company Equipment registration, actual CCPC master/data semantics, persistent DEVELOPMENT safely pulled after explicit owner approval; real source→P&L GL reconciliation is distinct PR #31.
- Build #43 was the single manually approved PR30 integration run already executed. **Do not launch another or retry automatically.** Current CircleCI balance was **not supplied with this upload**; do not invent a new balance or an itemized cost. No PR merge, DEVELOPMENT pull, PRODUCTION migration or deployment was authorized. **PRODUCTION NO-GO.**

## Controlled next step

Review the passing but scoped PR30 result, preserve the unchanged verified PR30 SHA, and continue **separately** with the owner-held PR31 Company-wide SLE/P&L GL integration, only after confirming its exact current SHA, CircleCI project variable and a distinct scoped one-run authorization. No automatic workflow or production-side integration.

**Documentation branch:** `docs/ccpc-checkpoint-2026-10-10`. Full raw CI logs and synthetic records are not committed.
