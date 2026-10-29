# CCPC ERPNext — Integrated Withdrawal → SLE/GL → Billing Acceptance Candidate

**Date:** 2026-10-29 Asia/Manila  
**Status:** GitHub-only reviewed test candidate, **NOT executed**, no release approval.

## Why this is the next critical step

The owner has confirmed the Finance G2 hosted disposable SQL baseline **8/8 PASS** on CircleCI pipeline #12 at app feature SHA `0564e94f5eea5eaa3c07f16a4fdacb84871eafdc`. That baseline validates signed Finance decision lifecycle but **does not prove source-to-intercompany billing**. Existing earlier real Withdrawal B/C SQL/GL tests on draft PR #19 predate newer Finance G2 signed-decision requirements. Earlier draft PR #20 uses a synthetic finalized batch to prove real draft invoices, but not their real Withdrawal/Stock Entry eligibility. Consequently the complete chain remains an acceptance gap.

## New GitHub code

Draft [app PR #25](https://github.com/ccpcerp/ccpcerp/pull/25) targets `feature/finance-mapping-lifecycle-2026-10-28`, based exactly at `0564e94f5eea5eaa3c07f16a4fdacb84871eafdc`. Branch: `review/integrated-withdrawal-ledger-billing-acceptance-2026-10-29`, HEAD `97ddb12a4206eca0710bf7571d6963932fc74bee` (feature untouched).

Only one **new test-only module**: `ccpcerp/ccpc_erp/test_finance_withdrawal_billing_bridge_disposable.py`. No business/accounting runtime, DocType, permission, patch, hook, report or CI configuration changes.

Two real-Frappe/MariaDB test candidates:

1. Signed Finance maker/checker decision and one-use consumption for Expense and Center; submitted original Withdrawal Slip Material Issue with preserved source/item, real SLE, approved Expense GL with beneficiary Department and Cost Center. A distinct synthetic requesting Company makes the Stock Entry eligible for Intercompany Material Billing Batch; `refresh_preview()` is called against the real submitted source and must capture precisely its Stock Entry Detail and Slip Item. A second preview and issue attempt must not create duplicate Stock Entry or GL.
2. Without approved signed Finance mapping, issue is rejected; quantity and existing fixture SLE are unchanged, no submitted issue/GL created, and the real billing preview has no source row.

Strict initial `assert_finance_disposable_site` requires the existing approved CircleCI Finance job identity, exact new SHA and ephemeral `ci-finance-lifecycle.localhost`. Tests use synthetic `_Test Company` and `_Test Company 5`, test-only maker/checker and ERPNext test receipts; not genuine CCPC accounting authorization. The helper updates only a synthetic, unsubmitted Slip's requesting company within test transaction, to exercise the intercompany selector. No invoice is created, approved or posted by these two tests.

## Verified and not verified

- Connected GitHub branch compare: **one added test file**, zero behind base and **13/13 read-back source assertions PASS** for first-contact guard, real methods referenced, SQL source/GL queries, negative denial, no invoice posting or CI/production code changes.
- New module commit `0298392a44a83f78957607a5de0f662df7d030c6`; corrected SLE receipt baseline commit `97ddb12a4206eca0710bf7571d6963932fc74bee` (current branch head).
- **Not executed:** Python syntax/import in actual checked-out source, Frappe fixture preparation, genuine MariaDB two-test module, month-end finalization, real invoice pair from source, cross-company invoice reconciliation, concurrency or CI provider validation. These are candidate tests, **not 2/2 PASS**. CircleCI pipeline #12's earlier 8/8 PASS is an independent historical milestone.

## Next quickest safe delivery gate

**Fastest practical:** review PR #25's full test source, perform exact-source Python compile/preflight; with a distinct scoped approval prepare a strictly opt-in, manually held CircleCI test job/commit for the new two-test bridge using a fresh approved SHA and controlled credits. **Do not run on the PR's review branch with bypassed CI identity**. Follow the existing Finance exact-source SHA gate and require provider approval before any billable execution; do not change existing project secrets or automatic scheduling.

Upon real SQL results, fix any failing fixtures or code **in GitHub** and move from billing **preview** to actual post-month-end finalized source billing and real draft Sales/Purchase Invoice pairing, with approved account/party fixtures and rollback/replay tests. Then implement/validate the four owner-frozen reports:
- Department material consumption;
- Equipment/Job Order material consumption;
- Intercompany withdrawal and billing (including invoice state);
- Overall material consumption and all Company P&L expense **separately**, reconciled to SLE/GL and not double-counting intercompany.

**Release boundaries:** PR #25 draft/unmerged. App `version-16`, persistent DEVELOPMENT/Integration2, PRODUCTION and real Accounting signatories untouched; no new CircleCI pipeline or paid action authorized by this GitHub source-only work. Production remains NO-GO.
