# Withdrawal Slip original issue — Decision A + D joint integration draft review

**Date:** 2026-10-18 (Asia/Manila). **Status:** GITHUB-ONLY DRAFT PR; EQUIPMENT MOCKED CI **12/12 PASS**, TWO GENUINE DISPOSABLE CI SUITES RUNNING AT LAST CHECK, NOT VERIFIED COMPLETE. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**

## GitHub authoritative sources and exact branches

- Decision A beneficiary Department enforcement: [app draft PR #14](https://github.com/ccpcerp/ccpcerp/pull/14), branch `review/withdrawal-issue-accounting-ci-2026-10-17`, verified source head `ebeec379f623e8596c1d178ad7b45d0f8859c2e5`. Earlier independent CI `39097918235` passed 72 mocked and 13 genuine disposable MariaDB/ERPNext/GL tests.
- Decision D Equipment-at-issue snapshots, source locks and gross-issue report: [app draft PR #15](https://github.com/ccpcerp/ccpcerp/pull/15), branch `review/equipment-maintenance-baseline-2026-10-18`, source head `7ef5299c368a0fe4ad8f458a9771eade5d52861f`. Its earlier independent review passed 12 mocked and 13 real disposable tests.
- **New joint review:** [app draft PR #16](https://github.com/ccpcerp/ccpcerp/pull/16), `review/withdrawal-beneficiary-equipment-integration-2026-10-18`, created from the **exact PR #15 head** above, targeting the original common base `review/withdrawal-cancellation-ledger-ci-2026-10-16`. PR #14 and #15 were **not edited, merged or closed**. Current integration review source checkpoint: `827993e45ae9321e7a936f48f7fc3b17bf842099` (verify head before any further edits).

## What the combined source now does (read and review, not approved release)

1. Preserves PR #15 `Stock Entry Detail.ccpc_equipment_at_issue` (Link) and `ccpc_equipment_code_at_issue` (independent original-number Data), linked-issue builder population, before-submit comparison against locked Slip Equipment, submitted-history guard, Equipment rename prevention and read-only baseline report.
2. Ports PR #14 `withdrawal_issue_beneficiary.py` without changing its Decision A semantics: explicit `work_for_department`, Equipment Department fallback only if explicit missing, reject conflict/missing/wrong Company/inactive/group beneficiary; require active native Department GL Accounting Dimension and presence on Stock Entry, item and GL Entry. Apply header/item beneficiary at issue build and revalidate on `before_submit`.
3. Reconciles overlapping `withdrawal_slip_stock.py` to acquire `equipment` **and** `work_for_department` in the same SQL `FOR UPDATE` Slip lock and to check both fields in the post-lock stale-document comparisons. Preserve existing double-issue, quantity, permission, cancellation, provenance and ledger protections.
4. Carries PR #14 mocked/real tests and concurrent worker into the PR #15 branch; retains PR #15 mocked/real report tests. The report's real integration method `test_real_new_issue_snapshot_pair_is_provisioned` now asserts **on the same genuinely submitted original Material Issue** the original Equipment pair, the actual beneficiary Department on header/item, native active Department GL dimension, and the expense GL debit's Department and item Cost Center.
5. Adjusts **only** the separate disposable GitHub CI review workflows and real-test environment guards for the new exact same-repo branch. No secrets, self-hosted runners, scheduled jobs, PROD or DEVELOPMENT connections were added. These workflows only initialize temporary Frappe v16 / ERPNext v16 MariaDB sites or use pure mocked report tests.

## Verified CI status at latest review

- [PR #16 mocked Equipment report Actions run 39100967202](https://github.com/ccpcerp/ccpcerp/actions/runs/39100967202): **COMPLETED SUCCESS, 12/12 mocked tests passed** (verified workflow job conclusion and log `Ran 12 tests ... OK`).
- [PR #16 real Accounting attribution run 39100967156](https://github.com/ccpcerp/ccpcerp/actions/runs/39100967156): **IN PROGRESS** at last check; no claimed real ledger pass yet.
- [PR #16 real Equipment report run 39100967357](https://github.com/ccpcerp/ccpcerp/actions/runs/39100967357): **IN PROGRESS** at last check; no claimed genuine snapshot+Department GL assertion pass yet.
- All three runs originated from the integration source head `827993e45ae9321e7a936f48f7fc3b17bf842099`. Verify latest run/head again before release.

## Review and acceptance gates

- **Required CI pass on this specific branch/head:** accounting mocked tests, accounting genuine real GL/transaction/concurrency tests, report mocked tests and report real SQL/SLE/GL/permission tests. Prior PR results are not combined acceptance evidence. Inspect Actions steps and test counts; failing CI means **blocked**.
- If either CI suite needs fixture updates because the other approved safeguard now runs, preserve both fail-closed validators and both source identifiers. Do **not** bypass Department GL dimension checks or Equipment snapshot guards to make CI pass; update synthetic isolated fixtures and add a joint ledger assertion.
- Review submitted issue and direct-voucher forgery, source changes under lock, stale saved drafts, legacy blank Equipment snapshots, update-after-submit immutability, cancellation, permission boundaries, stock/GL balance and exact equipment/Department read-only reporting. Distinguish tests with mocked objects from real ERPNext SQL/GL tests.
- **Decision B & C posting blockers remain**: no verified Accounting-approved Company/category→Expense Account mapping, no Company/beneficiary Department→Cost Center crosswalk, exception authority or storage design. Real CI defaults are synthetic and **cannot** stand in for CCPC masters.
- Physical Return Option A remains separate and is **not implemented** in this review. The report is gross original SLE issue valuation, **not net maintenance costs**.
- Before any DEVELOPMENT action, independently verify the exact target, origin, branch/HEAD, Git cleanliness, backups and containment. Shared PRODUCTION infrastructure is never automatically affected. PRODUCTION requires its own explicit approval, recovery/rollback gate and mapping signoff.

No Google Drive or personal notes were searched or used for this review. Only verified GitHub project code, workflow, Decisions A–D and handoff were used.
