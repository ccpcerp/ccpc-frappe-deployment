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


## 2026-10-29 — Manual CircleCI bridge prepared on PR #25 (no hosted run)

**Owner authorized continuation of GitHub test preflight/preparation, not an unbounded provider run or release merge.**

Connected GitHub review HEAD after work: **`bd9c3d1e1e68a99d216a736f4f044bcf17841162`** on `review/integrated-withdrawal-ledger-billing-acceptance-2026-10-29`; draft [app PR #25](https://github.com/ccpcerp/ccpcerp/pull/25), target `feature/finance-mapping-lifecycle-2026-10-28` still unmerged.

**Changes now in candidate:**
- `test_finance_withdrawal_billing_bridge_disposable.py` fixes the earlier fixture shortcut: creates the cross-company request **correctly at Draft insert**, with requesting Department in synthetic buyer `_Test Company 5` and separate issuer-beneficiary Department in `_Test Company`; sets Stockroom Review only using the existing disposable fixture's workflow shortcut. No request-intent change after Stockroom Review. Asserts real SLE stock-value outflow is equal to genuine signed Expense GL debit, plus original source snapshot, preview replay, and unsigned denial.
- `.circleci/config.yml` adds **`run_finance_bridge` boolean, default `false`**, plus `opt-in-finance-bridge` with `finance-bridge-manual-approval`; reuses existing Finance job with job-local **`run_bridge=false`** (legacy Finance run unchanged unless explicitly opted into bridge). Same manual filter `feature/finance-mapping-lifecycle-2026-10-28`.
- `.circleci/finance_baseline_stage.sh` adds `bridge)` command, inheriting the **exact CircleCI org/project/job/feature-branch/SHA, disposable site and same cumulative deadline**. Runs existing Finance 8 test module first, then two bridge methods only if job-local opt-in `run_bridge=true` is selected. No automatic schedule/PR trigger.
- `.circleci/test_finance_bridge_config_static.py` adds **four** static source tests and is referenced in the initial Finance job identity/preflight command. Existing `test_finance_ci_config_static.py` tests remain intact.

**Verification:** GitHub post-write compare against base `0564e94f5eea5eaa3c07f16a4fdacb84871eafdc` confirms **exactly four review-path changes**: two newly added test modules and two CI source modifications (no business runtime/doctype/report/role/schema files). **21/21 read-only structural/source invariants passed** via connected GitHub readback (default-off/mutual separate workflows/holds, same guard and deadline, no deploy, no submitted invoice, correct request-company fixture, positive/negative test methods). This is source inspection **not executed Python unittest/compile, CircleCI config compiler or Frappe/MariaDB**. Offline exact GitHub files cannot currently be materialized through this isolated scratch network; do not mislabel the structural checks as runnable Python tests.

**Required next gates:** owner explicitly approves scoped **merge of PR #25 only into Finance feature**, after human code review and provider config preflight; verify new *full* feature SHA; separately approves **one** bounded manual bridge CircleCI run with config/checkout branch `feature/finance-mapping-lifecycle-2026-10-28`, `run_finance_bridge=true`, `run_finance_lifecycle=false`, `run_integration=false`, current project balance/cost controls; user then replaces project `CCPC_FINANCE_APPROVED_SHA` from old `0564e94...` with new merge SHA. Wait for manual `finance-bridge-manual-approval` hold and verify SHA before approving expensive job. Never run review branch bypassing guard; no reruns without separate approval.

**Current status:** accepted prior Finance G2 SQL 8/8 PASS; **new signed Withdrawal→SLE/GL→intercompany preview tests NOT RUN**, draft review branch only. No new CI spend; DEV, Integration2, PRODUCTION, real business masters and default app branch unchanged.
