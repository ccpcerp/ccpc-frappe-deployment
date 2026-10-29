# PR #32 — CircleCI Build #52 integrated four-report MariaDB acceptance

**Recorded:** 2026-10-29. **Observed result:** **86/86 PASS** on the same synthetic disposable Frappe/ERPNext + MariaDB site; **64/64 report unit tests + 22/22 genuine native MariaDB integration tests**, including the new one-source cross-report case. **No persistent CCPC DEVELOPMENT or PRODUCTION test, app merge, or financial-statement certification is implied.**

## Authoritative tested GitHub identity

- [Draft/unmerged PR #32](https://github.com/ccpcerp/ccpcerp/pull/32) on `review/four-day-one-reports-integration-2026-10-29`, exact unchanged HEAD **`061e65710eb4b527fc8ac579aaab8ccad4dd131d`**, Finance base **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**.
- Owner uploaded three CircleCI **Build #52** step exports to this conversation, **not** committed as raw CI logs:
  - `build_52_step_103_container_0.txt` (1 line): `Combined four-report exact-SHA isolated CircleCI identity verified`. The identity check is a one-line summary: it **does not print all 40 SHA characters**, nor individually itemize the six static CI guard test method results.
  - `build_52_step_104_container_0.txt` (2,224 lines): same identity check, prepared the pinned disposable bench, `HEAD is now at 988e54f` (Frappe 16.33.1; line 1145), `HEAD is now at 4048fb7` (ERPNext 16.34.2; line 2149), checked out CCPC from combined review branch, installed ERPNext and ccpcerp, migrated disposable site `ci-four-reports.localhost`, ending `Combined four-report disposable Frappe site installed; no persistent CCPC site used` (line 2224).
  - `build_52_step_105_container_0.txt` (200 lines): same identity check (line 1), **all eight unit/native modules finish `OK`**, concluding `Combined four-report MariaDB acceptance finished; inspect each source/SLE/GL test log` (line 200).
- Independent GitHub commit status readback for the **same exact current PR32 SHA**:
  - [`ci/circleci: python-syntax`](https://app.circleci.com/workflow/8e7e9401-7a9d-450d-a497-507475f66c30/job/232590e9-2181-43bd-a893-c5d0170e928c): **success**.
  - [`ci/circleci: four-reports-manual-approval`](https://app.circleci.com/workflow/65d25a23-1764-45e3-a813-07594f9fc76f): **success**.
  - [`ci/circleci: four-reports-isolated-integration`](https://app.circleci.com/workflow/65d25a23-1764-45e3-a813-07594f9fc76f/job/ace7794f-da14-4665-b6b1-8feb16e06012): **success**.
- Thus the owner-supplied native test transcripts and provider statuses **agree**. The source-only six CI safeguard cases were authored and part of the starter/identity command, but their **individual outcomes are not separately itemized in the supplied step-103 output**, so **do not count them on top of 86**.

## Exact passing eight-suite matrix

| Tested installed-Frappe module | Source lines (step 105) | Result |
| --- | --- | --- |
| `ccpc_intercompany_withdrawal_billing_status.test_ccpc_intercompany_withdrawal_billing_status` | 2–30 | **17/17 PASS** in 0.095 s |
| `ccpc_department_material_consumption.test_ccpc_department_material_consumption` | 31–59 | **17/17 PASS** in 0.097 s |
| `ccpc_equipment_job_material_activity.test_ccpc_equipment_job_material_activity` | 60–86 | **15/15 PASS** in 0.089 s |
| `ccpc_company_stock_pnl_gl_reconciliation.test_ccpc_company_stock_pnl_gl_reconciliation` | 87–113 | **15/15 PASS** in 0.086 s |
| `ccpcerp.ccpc_erp.test_four_reports_28_disposable_integration` | 114–135 | **6/6 PASS** in 9.669 s |
| `ccpcerp.ccpc_erp.test_four_reports_29_disposable_integration` | 136–157 | **6/6 PASS** in 4.753 s |
| `ccpcerp.ccpc_erp.test_four_reports_30_disposable_integration` | 158–178 | **5/5 PASS** in 4.150 s |
| `ccpcerp.ccpc_erp.test_four_reports_31_disposable_integration` | 179–199 | **5/5 PASS** in 4.002 s |
| **Total eight executed suites** | **64 policy + 22 native** | **86/86 PASS** |

**What the new joint database test actually proves:** `test_report_f_same_signed_issue_all_four_read_only_reports` passed (step 105 line 129). On one genuinely signed/submitted, synthetic original Intercompany Withdrawal→Material Issue, the report adapters return the same original voucher/detail and consistent outbound original SLE gross issue value in four **independent** perspectives. No summing across reports, no invented Job Order material cost or billing amount, and no claim of GL consolidation across Companies. This is a concrete native cross-report integration result, **not four independent runs merely presented together**.

**Other real synthetic test categories:** submitted original issues, SLE/outgoing valuation, signed maker/checker Finance mappings, draft intercompany invoice pair and duplicate/forged link quality, protected beneficiary Department vs editable requesting Slips, Equipment snapshot provenance with unpriced Job activity, posted Expense GL vs stock voucher variance, missing SLE/GL as explicit null/exception, user/Company/date denials, multiple outbound SLE fragments and source/row caps. **Seven new permission/query tests** on combined PR28/PR29 now passed within the 64/64 unit suite. This is not evidence that every actual CCPC user-permission policy or all historical books were covered.

## Warnings, amount and constraints

- Installer `build_52_step_104` line 1568 recorded **pre-pin warning** when fetching moving ERPNext `version-16`: Frappe 16.33.1 did not satisfy the moving dependency `>=16.50.0,<17.0.0`. This happened **before** ERPNext pinned checkout at line 2149. Live GitHub read of pinned ERPNext SHA `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` `pyproject.toml` confirms `frappe >=16.21.0,<17.0.0`, **compatible** with Frappe 16.33.1. The pinned combination and native tests succeeded. Do not label the tested pinned pair incompatible.
- Native Frappe tests emitted a **nonfatal v17 `limit_page_length` deprecation warning** in four native suites (step 105 lines 121–124, 143–146, 165–168, 186–189). Yarn/Vite/build warnings in installation step did not prevent successful acceptance.
- Owner reports **27,555 CircleCI credits remaining** after Build #52, compared with previous reported **27,689**: a **134-credit balance decrease**, NOT a provider-itemized Build #52 bill. The separately approved **single** manually held execution was consumed; **no more paid run or retry is authorized**. The 90-minute subprocess deadline was a runtime guard, **not** a guaranteed credit-spend cap.
- This run did **not** test real CCPC transactions or live permissions in persistent DEVELOPMENT, returns/repost/refund netting, full financial-statement/GL tie-out, intercompany eliminations, production-grade query plans, stock adjustments across variable UOMs, immutable issue-time Requesting Section or Job Order costing, or posted intercompany invoices. In particular, PR28's intercompany paired SI/PI are verified as **draft**, PR29's original beneficiary Department is not issue-time requested Section, PR30 has no immutable stock-detail→Job Order link and Job activity remains **unpriced**, and PR31's original stock SLE vs P&L GL are distinct **non-additive** accounting perspectives.
- The four original individually tested PRs #28–31 and the integrated PR32 all remain **draft/unmerged**. Do not merge/deploy solely on synthetic CI green status. Changes to the Finance feature base and any needed downstream migrations are an **independent** integration/release concern.

## Next controlled DEVELOPMENT gate (not started)

**Recommended next stage: separate owner authorization for read-only DEVELOPMENT preflight, not a blind pull.** Operator inspects exact shared app Git checkout branch, remote/HEAD, uncommitted tracked/untracked files (`AGENTS.md` historically observed), both DEVELOPMENT site names/databases, current installed versions/patch state, existing protected backups and tested restore/rollback, and shared Docker/build resources with PRODUCTION. Stop if worktree is dirty or shared infrastructure could affect PRODUCTION. Do **not** checkout or apply PR32 to a real DEVELOPMENT site until after this preflight is reviewed and separately approved. Later controlled DEVELOPMENT acceptance needs real CCPC Company/Department/Equipment/Account mappings, real role/row permissions, original issue/SLE vs GL provenance, duplicate controls, performance, returns and exception handling. All real test fixes must go back to GitHub.

**Do not run the synthetic CI fixtures against persistent DEVELOPMENT or PRODUCTION**: the fixture source is deliberately guarded for exact CircleCI project/branch/job/disposable site. Separate actual acceptance should use safe read-only diagnostics or separately approved synthetic test environment.

**PRODUCTION NO-GO:** requires its own explicit user approval plus backup, recovery, rollback and financial signoff. No new production DB migrations, restarts, Docker recreations, deployment or data changes approved.

**Documentation branch:** `docs/ccpc-checkpoint-2026-10-10`; raw CI logs were owner-provided in chat and deliberately not stored in source control.
