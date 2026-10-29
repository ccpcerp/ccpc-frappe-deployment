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


## 2026-10-29 — Owner-approved PR #25 merge verified (new CircleCI bridge run not authorized)

**Owner approval and GitHub action:** The owner explicitly approved merging PR #25 **into the Finance feature branch only**. GitHub connector marked draft PR ready for review and performed a merge with exact expected review head `bd9c3d1e1e68a99d216a736f4f044bcf17841162`. GitHub returned `merged=true` and merge commit **`39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`**. PR #25 is **CLOSED / MERGED** with `merged_at=2026-10-29T01:14:42Z`.

**Independent post-merge verification** via connected GitHub:
- `feature/finance-mapping-lifecycle-2026-10-28` current HEAD **`39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`**; old Finance baseline parent SHA `0564e94f5eea5eaa3c07f16a4fdacb84871eafdc` was the base, **9 commits ahead / 0 behind**, exactly **four changed files**: `.circleci/config.yml`, `.circleci/finance_baseline_stage.sh`, `.circleci/test_finance_bridge_config_static.py`, `ccpcerp/ccpc_erp/test_finance_withdrawal_billing_bridge_disposable.py`.
- Merged blob hashes respectively: `8f64c1c0968934305e3dcb2f5720b93f15a719ec`, `98560f6e28f92ff90951c8273179f68350d0c0c3`, `f8b41e8736e2f143e0dc23b5bebbd5a00c8aa131`, `90a113e95d5dfee36e44dc45ab993a49c0b2bebe`.
- New CI parameter `run_finance_bridge` remains **false by default** with its own manual hold; existing Finance deadline/SHA guard remains. No app business-code, posting logic, DocType/schema, permission, report or release branch files changed.
- App default `version-16` independently remains `cfcc19394a6646548f2b7050db040c8cf5ebafde`.

**Critical verification boundary:** The previous CircleCI pipeline #12 **Finance G2 8/8 PASS** belongs to the **old** `0564e94...` source, not to this merged test harness. **No CircleCI pipeline or expensive job has been triggered for new SHA `39290e93...`; official CircleCI config compile, four static bridge preflight tests, Frappe fixture import and two real MariaDB bridge tests remain unverified.** Do not represent this PR as functional billing acceptance or release-ready.

**Next independent consent:** Request specific approval for **one** additional opt-in, manually held, disposable CircleCI pipeline at new SHA. If approved, operator separately updates CircleCI project variable `CCPC_FINANCE_APPROVED_SHA` (last set to old `0564e94...`) to full **`39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`**, checks plan/credits and paid auto-refill, uses *both* Config and Checkout Sources `feature/finance-mapping-lifecycle-2026-10-28`, parameters `run_integration=false`, `run_finance_lifecycle=false`, `run_finance_bridge=true`. Verify the hold and full commit before authorizing the expensive job; **no automatic retry**. Separate DEVELOPMENT/PRODUCTION approval remains required.


## 2026-10-29 — Hosted bridge execution: 2/2 real Frappe/MariaDB PASS (baseline 8/8 PASS)

**Evidence source:** The owner uploaded original CircleCI job-step logs from **build #28**, step #105 (`build_28_step_105_container_0.txt`) and step #106 (`build_28_step_106_container_0.txt`), both against disposable Frappe site `ci-finance-lifecycle.localhost`. These were examined as actual runner text, not inferred from a pipeline-green screenshot.

**Step #105 — existing Finance G2 regression on the newly merged bridge run:** `ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`. **8/8 PASS**, no failures/errors or skips reported; exact `Ran 8 tests in 2.588s`, `OK`, and `Finance disposable database tests finished; reconcile results before further stages`. The eight methods cover schema/permissions, draft rejection/audit, single-use signed approval/forgery denial, audit rollback, retirement/replay, unauthorized identities, Company/Department scope, and rejection-audit rollback. This is **new execution evidence** from build #28, not merely historical pipeline #12.

**Step #106 — new real source bridge:** `ccpcerp.ccpc_erp.test_finance_withdrawal_billing_bridge_disposable`. **2/2 PASS**, no failures/errors or skips reported:
1. `test_a_signed_issue_reaches_real_ledger_and_billing_source` — green; integration test's asserted path covers synthetic independently signed Finance Expense/Center mappings, real submitted Withdrawal Slip Material Issue, real Stock Ledger qty/valuation outflow, beneficiary-mapped Expense GL, equality of stock value outflow and GL debit, real Intercompany Material Billing Batch preview row linked to source Stock Entry Detail, duplicate/replay protection.
2. `test_b_unsigned_issue_cannot_enter_billing_preview` — green; absence of Finance signed mapping fails issue and leaves pre-existing receipt Bin/SLE unchanged, no submitted issue and no billable preview row.

Exact step tail: `Ran 2 tests in 2.580s`, `OK`, `Finance-Withdrawal-billing bridge test completed; verify per-test SQL/GL log`. Step #106 also printed a **nonfatal `V17FrappeDeprecationWarning`** from Frappe `qb_query.py:163` that `limit_page_length` is deprecated in favor of `limit`; no test failure and not yet attributed to a specific CCPC source call.

**Combined observed test result for the two provided steps:** **10/10 tests PASS**, zero reported failures, errors, or skips. This is meaningful **disposable Frappe v16/ERPNext v16/MariaDB Finance→Withdrawal→SLE/GL→intercompany source *preview* acceptance**. GitHub branch readback on this date still reports feature `feature/finance-mapping-lifecycle-2026-10-28` HEAD **`39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`**, with the test module unchanged from merged PR #25 blob `90a113e95d5dfee36e44dc45ab993a49c0b2bebe`. **The two uploaded test-step texts do not themselves display the full checkout SHA or pipeline metadata**, so exact runner SHA attribution is supported by the prior reviewed CircleCI setup and current GitHub, not by these excerpts alone. No official provider pipeline-wide status, final credit consumption, or full preparatory-step trace was included in these files.

**Acceptance boundary (NOT YET proven):** This bridge **does not finalize month-end** or create/approve/submit an actual paired Sales Invoice/Purchase Invoice from a truly source-linked finalized batch. No invoice GL, cancellation/returns accounting, real Company mappings, production-grade Finance user signoff, HTTP/CSRF/concurrent writer validation, four day-one reconciliation reports, persistent DEVELOPMENT acceptance, or PRODUCTION recovery/cutover. The prior PR #20 standalone real draft-invoice tests rely on a mocked finalized batch; their results cannot substitute for a complete source-to-draft-invoice chain.

**Next practical development milestone:** On a *new isolated review branch* based on verified feature HEAD, implement one true SQL-source billing-month finalization→atomic real draft SI/PI pair acceptance with source/Company/Department/replay/rollback checks and synthetic same-currency intercompany masters, using existing production methods and no change to persistent sites. Then validate the four owner-frozen reports (Department, Equipment/Job, intercompany withdrawal/billing, and distinct overall material/P&L with SLE/GL reconciliation) before proposing any PRODUCTION approval. No CI rerun or additional spend authorized from this log alone.


## 2026-10-29 — Draft PR #26: unmocked finalized source-linked SI/PI draft-pair test candidate

**Owner authorized GitHub-only continuation** after receipt of two independent CircleCI #28 step logs showing eight Finance lifecycle and two signed Withdrawal→SLE/GL→intercompany source-preview MariaDB tests PASS. This authorization does NOT approve a hosted CI run, release branch merge or any DEVELOPMENT/PRODUCTION operation.

### Exact GitHub code milestone

Created [app draft PR #26](https://github.com/ccpcerp/ccpcerp/pull/26), source branch `review/source-linked-intercompany-draft-pair-2026-10-29` based on tested `feature/finance-mapping-lifecycle-2026-10-28` SHA `39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`. Current candidate commit **`2940b405f917792642f50f980f13bd4a3e2a0a61`**. Connected GitHub compare confirms **exactly two test-only modified files**; no changed production Controller/business function, DocType, finance mapping policy, role, schema, fixture migration, workflow/schedule or release branch.

1. `ccpcerp/ccpc_erp/test_finance_withdrawal_billing_bridge_disposable.py`: keep the exact original source-preview `test_a_...` and denial `test_b_...` methods that passed in build #28. Add **test C** `test_c_real_source_finalizes_to_actual_paired_invoice_drafts`: independent authenticated synthetic Finance Expense+Center mapping approvals, real original Withdrawal stock issue→SLE/GL→actual billing preview row, explicit real denial when month not over, then *billing Controller-only time simulation* for the first following-month date, real persisted `finalize_month()` + `approve_and_create_invoices()`, native ERPNext Sales/Purchase Invoice `insert/save`, exact source/quantity/value links, correct Company/party/cross-references, both drafts (docstatus 0), no stock updates, taxes, invoice GL, or duplicate approval. **No invoice submission.**
2. Same module **test D** `test_d_second_draft_insert_failure_rolls_back_real_first_invoice`: on real source-linked finalized batch inject only Purchase Invoice builder failure after real first Sales Invoice insert, verify actual SQL savepoint removes orphaned first invoice and leaves batch Under Review, then retry and assert one linked draft SI/PI pair (no duplicate). Only controlled month-end clock and one deliberate exception are mocked; both invoice persistence and rollback use MariaDB.
3. `.circleci/test_finance_bridge_config_static.py`: remove stale preview-only assertion that all `approve_and_create_invoices` calls are forbidden, replacing it with assertions that the bridge uses real draft generation yet **must not submit** Sales/Purchase invoices; static AST must show **exactly A/B/C/D** methods. The original CI manual hold, default-off `run_finance_bridge`, exact feature branch/approved SHA guard, cumulative 90min deadline and disposable site are unchanged.

**Source-only verification** performed through connected GitHub: base and feature unchanged, two intended files only, **14/14 focused structural assertions PASS**, including same first-contact disposable CI site guard, real billing method use, premonth denial, rollback injection, draft-only checks and preservation of A/B. This is NOT an executed Python compile, no unittest execution, no official CircleCI compiler validation and **C/D real SQL outcomes NOT KNOWN**. Potential fixture risks include synthetic accounts' exact expected names/numbers, internal Customer/Supplier and ERPNext future posting-date validators under simulated month-end; resolve based on actual disposable test outcomes, never by weakening source/Company/business restrictions.

**Next gates:** inspect/review PR #26; request owner approval to merge **into Finance feature only** if acceptable. A separate bounded manually held **one-time** CircleCI run on the resulting **new merge SHA** must be explicitly approved; operator updates `CCPC_FINANCE_APPROVED_SHA` from previous `39290e93...` to that exact new approved commit, verifies remaining credits and paid auto-refill control and `run_finance_bridge=true`, `run_finance_lifecycle=false`, `run_integration=false`. Do not rerun pipeline #28 or bypass SHA guard. Invoice submission/reversal, four owner-frozen reports, genuine Accounting/Company authority, DEVELOPMENT and PRODUCTION remain independent gates. **PRODUCTION NO-GO.**


## 2026-10-29 — Owner-approved PR #26 MERGED; source-linked month-end invoice SQL tests still NOT RUN

**Exact owner authorization:** Owner explicitly approved **merge PR #26 to `feature/finance-mapping-lifecycle-2026-10-28` only**. GitHub pre-merge checks reverified the correct head, target, branch ancestry (zero behind), exactly two previously reviewed test files, and mergeability; normalized connected GitHub PR metadata confirmed `base_sha=39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`, `head_sha=2940b405f917792642f50f980f13bd4a3e2a0a61`. GitHub marked draft PR ready, then merged with **`expected_head_sha=2940b405f917792642f50f980f13bd4a3e2a0a61`** and standard merge method. GitHub returned **`merged=true`** and new merge SHA **`724d008ccc91043975f47a3a11fa7e8030f31f4d`**.

**Independent post-merge readback:** [App PR #26](https://github.com/ccpcerp/ccpcerp/pull/26) **CLOSED/MERGED** at `2026-10-29T02:02:10Z`; the Finance feature branch HEAD is now exactly `724d008ccc91043975f47a3a11fa7e8030f31f4d`. Compare against former base `39290e93d6a3e5f231eb63e7110f7ad3c6ceabbd`: **5 commits ahead, zero behind, exactly two changed test files**:
- `ccpcerp/ccpc_erp/test_finance_withdrawal_billing_bridge_disposable.py` — updated merged blob `44674b00bf3f1e3055060eca76332ced08f920cb`, **four test methods** (previously hosted passing A/B plus new not-yet-executed C/D).
- `.circleci/test_finance_bridge_config_static.py` — updated merged blob `e2d9a148f0bf5f45ba86faf8576698d27b5968f5`; allows real paired **draft** Invoice creation but requires no invoice submission, asserts the four methods.
- `.circleci/config.yml` unchanged from prior tested source (blob `8f64c1c0968934305e3dcb2f5720b93f15a719ec`), retains `run_finance_bridge: false` default and separate manual approval; stage file unchanged `98560f6e28f92ff90951c8273179f68350d0c0c3`, retains exact SHA, site, branch and deadline guard.
- Release/default branch `version-16` remained `cfcc19394a6646548f2b7050db040c8cf5ebafde`.

**Verification boundary:** The prior CircleCI build #28 **10/10 PASS** was from the former Finance source commit and included only eight Finance and bridge A/B methods. **No hosted execution on merged source `724d008...`, no actual two new C/D SQL results, no updated CircleCI project approval variable, no CircleCI runner, no DEVELOPMENT/Integration2 or PRODUCTION operations.** The new time-simulated month-end invoice pair/rollback tests require a **separately approved one-time, held, exact-SHA disposable CI execution**. No automatic rerun, no paid CI authorization implied by this merge.

**Next operator gate:** If a separately scoped CI run is approved, set CircleCI `CCPC_FINANCE_APPROVED_SHA` to exact full **`724d008ccc91043975f47a3a11fa7e8030f31f4d`**; verify credits and paid auto-refill controls, both Config and Checkout Source branches `feature/finance-mapping-lifecycle-2026-10-28`, `run_finance_bridge=true`, `run_finance_lifecycle=false`, `run_integration=false`; verify manual `finance-bridge-manual-approval` hold and exact checkout SHA before authorizing hosted job. Capture all Finance and four bridge test outputs and distinguish fixture failures from financial logic failures. Following independently validated results, tackle the four frozen day-one reports, genuine Accounting signatory and persistent DEVELOPMENT acceptance. **PRODUCTION NO-GO.**


## 2026-10-29 — CircleCI build #31: A/B pass; C/D blocked by nested test Company Account fixture

**Owner-uploaded actual failure evidence:** Original `build_31_step_106_container_0.txt`, source `ccpcerp.ccpc_erp.test_finance_withdrawal_billing_bridge_disposable`, disposable `ci-finance-lifecycle.localhost`: **`Ran 4 tests in 4.819s` / `FAILED (errors=2)` / exit 1**. Individual **A** `test_a_signed_issue_reaches_real_ledger_and_billing_source` and **B** `test_b_unsigned_issue_cannot_enter_billing_preview` **PASS**; new **C** `test_c_real_source_finalizes_to_actual_paired_invoice_drafts` and **D** `test_d_second_draft_insert_failure_rolls_back_real_first_invoice` each **ERROR**.

**Same reproducible failure in both C/D:** At `_prepare_disposable_invoice_masters` → `_ensure_disposable_account` → actual ERPNext `Account.insert(ignore_permissions=True)` of `1312 - Intercompany Receivable - _TC5`, source Company `_Test Company 5`, parent Account `Temporary Accounts - _TC5`. Actual exception: **`frappe.exceptions.ValidationError: Please add the account to root level Company - _Test Company 3`**. The failing source was the new merged Finance feature **`724d008ccc91043975f47a3a11fa7e8030f31f4d`** (independently verified in GitHub); step excerpt does not print entire checkout SHA. No evidence of a failed finalization, invoice insertion, savepoint rollback or replay: **C/D never reached those stages**.

**Root cause verified against pinned ERPNext v16 source `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`:** `Account.validate_root_company_and_sync_account_to_children()` disallows adding a new Account directly to descendant Company without the name first existing on its root Company. Official ERPNext synthetic Company fixtures define `_Test Company 3` (root, group) → `_Test Company 4` → `_Test Company 5` (child). This is an expected integrity guard, **not reason to weaken accounting validation or update Company permissions**.

**GitHub-only correction candidate:** New [draft app PR #27](https://github.com/ccpcerp/ccpcerp/pull/27), branch `review/ci31-root-company-account-fixture-2026-10-29`, HEAD **`5a877bac7e46df00e9d674bc55133025804d3c0e`** from exact Finance parent `724d008ccc91043975f47a3a11fa7e8030f31f4d`. **Two test-only changes:** `ccpcerp/ccpc_erp/test_finance_withdrawal_billing_bridge_disposable.py` now uses ERPNext's native `get_root_company`, requires a matching root COA parent group, creates the exact synthetic Account at root FIRST, permits native child synchronization and only then validates/creates the expected descendant ledger Account; rejects conflicting names/numbers and validates account company, type and non-group status. The `.circleci/test_finance_bridge_config_static.py` adds a regression requiring that root-before-child order and disallows `ignore_root_company_validation`, `allow_account_creation_against_child_company`, and explicit commits. **No bypass of ERPNext Company policy**, no production Account patch, no runtime business code or CI workflow changes. GitHub compare **2 files only, 16/16 focused structural checks PASS**; not runnable Python tests.

**Risk and next gates:** Native ERPNext auto propagation may expose other fixture COA parent-group gaps; that would require further test-only correction, never silently disabling constraints. New draft PR #27 remains **unmerged and its fix UNTESTED in real MariaDB**; user separately approves branch merge and any *new* paid/manual held CircleCI. No automatic retry of build #31. No new CI variable modification; previous approved SHA refers to `724d008...`. Existing Finance G2 step #105 results for build #31 were not provided, so do not claim 12 combined tests passed. No DEVELOPMENT/Integration2/PRODUCTION modification. **PRODUCTION NO-GO.**


## 2026-10-29 — Owner-approved PR #27 merged (real invoice C/D retest NOT RUN)

**Owner approval and exact GitHub operation:** Owner explicitly approved merging [PR #27](https://github.com/ccpcerp/ccpcerp/pull/27) **into Finance feature only**. Connected GitHub rechecked PR state, original head SHA `5a877bac7e46df00e9d674bc55133025804d3c0e`, target `feature/finance-mapping-lifecycle-2026-10-28` at `724d008ccc91043975f47a3a11fa7e8030f31f4d`, zero-behind merge ancestry, PR mergeability and two test-only changes. 14/14 premerge source/permission/CI checks passed. Marked PR ready, then merged using `expected_head_sha=5a877bac7e46df00e9d674bc55133025804d3c0e`. GitHub returned **`merged=true`** and new commit **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**.

**Independent post-merge verification:** PR #27 CLOSED/MERGED, `merged_at=2026-10-29T02:33:49Z`, full merge SHA above. App Finance feature HEAD **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**; compare vs previous feature `724d008ccc91043975f47a3a11fa7e8030f31f4d` shows **three commits ahead, zero behind, exactly TWO modified test-only paths**:
- `ccpcerp/ccpc_erp/test_finance_withdrawal_billing_bridge_disposable.py` blob `530cc3bf197b186ebe08a5a22c2fa25998378fd4` — synthetic child Account setup now creates the matching root Company Account before child and preserves native hierarchy validation.
- `.circleci/test_finance_bridge_config_static.py` blob `78baf652ae0d47122e44dbe9a4b33a5a0033fe5b` — static guard requires root-first fixture and prohibits root-Company validation bypass.
- `.circleci/config.yml` still original blob `8f64c1c0968934305e3dcb2f5720b93f15a719ec`: **default-off `run_finance_bridge=false`, separate manual approval**; no job/schedule/production authorization change.
- App release/default `version-16` stays `cfcc19394a6646548f2b7050db040c8cf5ebafde`.

**Evidence boundary:** CircleCI build #31 A/B PASS, C/D ERROR is **prior source `724d008...`** and does not validate new merge. Although fixture cause is grounded in pinned ERPNext v16 root-Company validation and GitHub source assertions, **the fix has NOT been exercised in genuine SQL tests**, and the month-end paired draft SI/PI, rollback and retry remain **UNVERIFIED**. Do not report 12/12 passed. A further unrelated synthetic COA/party/date validation error could appear. No new CI run, approval-variable edit, persistent DEVELOPMENT/Integration2 action or PRODUCTION action taken.

**Next separate decision:** Owner may authorize **one bounded, manually held, disposable CircleCI Finance bridge test** at exact new merge SHA `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`. The operator must check remaining credits and paid auto-refill, replace `CCPC_FINANCE_APPROVED_SHA` with the new full SHA (previous value was approved for `724d008...`), set Config and Checkout Source to Finance feature, `run_finance_bridge=true`, `run_finance_lifecycle=false`, `run_integration=false`, inspect manual approval hold and exact checkout before approving job. No automatic reruns or DEV/PROD changes. Production remains NO-GO.


## 2026-10-29 — CircleCI build #34 verified: real source-linked month-end invoice draft pair and SQL rollback 4/4 PASS

**Owner-supplied direct CI runner evidence:** File `build_34_step_106_container_0.txt`, for `site=ci-finance-lifecycle.localhost`, exact module `ccpcerp.ccpc_erp.test_finance_withdrawal_billing_bridge_disposable`: starts `Running 4 unspecified-category tests for ccpcerp`, then shows four individual green checks:
- **A PASS** `test_a_signed_issue_reaches_real_ledger_and_billing_source` — signed Finance mapping→original Withdrawal Material Issue→real SLE/expense GL→one billing preview source.
- **B PASS** `test_b_unsigned_issue_cannot_enter_billing_preview` — fail-closed unsigned-source exclusion.
- **C PASS** `test_c_real_source_finalizes_to_actual_paired_invoice_drafts` (3.57s) — real source-linked finalized month-end batch, actual native ERPNext **Draft** Sales/Purchase invoices, cross-reference, amount/Company/party checks, no invoice GL or new Stock Entry, duplicate approval denial. Test-only simulated elapsed billing-Controller month-end clock.
- **D PASS** `test_d_second_draft_insert_failure_rolls_back_real_first_invoice` (3.19s) — intentionally fail second-invoice builder after actual first-invoice DB insert, verify MariaDB savepoint removes orphan draft and retains batch/source, retry creates one paired draft set.

**Exact end of uploaded job step:** `Ran 4 tests in 8.984s`, `OK`, `Finance-Withdrawal-billing bridge test completed; verify per-test SQL/GL log`. **No failures/errors or skipped tests reported in this step.** Same nonfatal `V17FrappeDeprecationWarning` from Frappe `frappe/model/qb_query.py:163` about `limit_page_length` deprecated in favor of `limit` persists; not a failure. This execution resolves the earlier **build #31 C/D blocking synthetic Account fixture error** for this runner. It does not mean the test passed on every possible Company hierarchy/Account variant.

**GitHub source readback alongside evidence:** Finance feature `feature/finance-mapping-lifecycle-2026-10-28` still has exactly **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**; [PR #27](https://github.com/ccpcerp/ccpcerp/pull/27) merged at that commit. The bridge test blob is `530cc3bf197b186ebe08a5a22c2fa25998378fd4` and contains exactly the A/B/C/D methods. CI config retains default-off `run_finance_bridge`, manual approval, blob `8f64c1c0968934305e3dcb2f5720b93f15a719ec`. **The supplied step #106 does not include the full checkout SHA or provider-wide pipeline status**; commit identification is supported by current GitHub, prior approved operator SHA sequence, and matching module/test names, not proven by that excerpt alone.

**Acceptance boundary:** Promote **disposable SQL finance→Withdrawal→ledger→intercompany preview→actual paired DRAFT SI/PI + savepoint rollback/retry test 4/4 PASS**. **Do not call this full CircleCI 12/12:** build #34 Finance G2 eight-test baseline `step #105` was NOT supplied with this message. Historical #28 baseline 8/8 PASS belongs to the older source and cannot substitute for a new execution at `7cc85cf5...`. No official provider build-level success/credits, invoice SUBMISSION/cancellation/returns GL or full HTTP/CSRF/concurrency, final business mappings, four owner-approved consumption/reconciliation reports, persistent DEVELOPMENT or PRODUCTION readiness was established. Real business signoff, source-to-invoice reconciliation and guard checks remain release gates.

**Next operator action:** Obtain the **build #34 step #105 Finance lifecycle test log**, and if possible its final provider job/pipeline status with full checkout SHA, to reconcile the full 8+4 suite **without starting another run**. Then continue GitHub-first reports and security/transaction review under separately scoped change approval; no further billable CI, DEV, Integration2 or PRODUCTION operation implied by these results. **PRODUCTION NO-GO.**


## 2026-10-29 — CircleCI build #34 confirmed 12/12 PASS across Finance G2 and actual invoice bridge

**Owner-supplied second independent runner log:** `build_34_step_105_container_0.txt` from `ci-finance-lifecycle.localhost` executes `ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`. Eight individually green tests:
1. `test_a_schema_has_required_lifecycle_fields_and_no_general_permissions`
2. `test_b_draft_rejection_is_terminal_and_audited`
3. `test_c_signed_approval_is_once_only_and_denies_forged_reference`
4. `test_d_signing_version_failure_rolls_back_decision`
5. `test_e_retirement_request_replay_decline_and_accept_are_audited`
6. `test_f_unauthorized_guest_and_administrator_fail_closed`
7. `test_g_center_approval_uses_exact_company_department`
8. `test_h_rejection_audit_failure_rolls_back_event_and_state`

**Exact end of step #105:** `Ran 8 tests in 2.365s`, `OK`, `Finance disposable database tests finished; reconcile results before further stages`. No errors, failures or skips reported in this step.

**Same build #34 step #106** (separately uploaded and recorded in previous section): `ccpcerp.ccpc_erp.test_finance_withdrawal_billing_bridge_disposable`, **A/B/C/D all green**, `Ran 4 tests in 8.984s`, `OK`, no failures/errors/skips reported. Thus **same CircleCI build #34, same disposable site: 8/8 Finance G2 + 4/4 real Withdrawal/billing bridge = 12/12 PASS** for the combined two direct test logs. The owner also supplied CircleCI UI screenshot showing the whole `finance-lifecycle-isolated-integration` job green, with the MariaDB service and signed Withdrawal/ledger bridge steps green; do not infer the status of unrelated pipelines from that job screenshot.

**Acceptance promoted:** Hosted real MariaDB/Frappe test coverage now proves signed Finance Maker/Checker mapping lifecycle; unauthorized/forged/replay/rollback rejection; original submitted Withdrawal Material Issue→actual SLE/expense GL→source-eligible intercompany billing; real persisted billing Controller month-end finalization with test-only simulated elapsed month-end; real native ERPNext **Draft** Sales/Purchase invoices correctly cross-linked, source and totals matched, no invoice GL/stock from unsubmitted drafts, duplicate approval rejected; injected second-invoice builder failure after real first Sales draft insert ensures SQL savepoint removes orphan and retry creates only one pair. Previous build #31 C/D error was from nested synthetic COA fixture; build #34 passing C/D is actual confirmation that PR #27 root-first fixture correction works in this hosted test environment.

**Verified GitHub version context:** `feature/finance-mapping-lifecycle-2026-10-28` remained `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd` when checked on this day; PR #27 merged at same SHA; bridge test blob `530cc3bf197b186ebe08a5a22c2fa25998378fd4` shows A/B/C/D. The excerpts themselves do **not print the runner's full checkout SHA**; the UI screenshot shows job success, not an independently legible checkout SHA. Describe SHA association as operator-authorized branch and verified GitHub source, not as a separately observed CI checkout hash.

**Important remaining release gates:** No validation of **submitted** Sales or Purchase Invoices and resulting intercompany GL/AR/AP, invoice reversal/cancellation/returns, fully asynchronous/concurrent requests, HTTP/CSRF edge cases, owner-frozen real business mappings/signatories, four production-aimed reports (Department, Equipment/Job Order, intercompany invoice status, company-wide materials vs P&L expense with SLE/GL reconciliation), or persistent DEVELOPMENT acceptance. **Not PRODUCTION-ready.** No further CircleCI run or DEVELOPMENT/PRODUCTION deployment authorized solely by this successful evidence.

**Next engineering milestone:** Develop and review owner-frozen day-one reporting with explicit valuation UOM/currency and no intercompany double recognition; separately review invoice submission and rollback/reversal with Accounting before any production release. Run further CI/DEVELOPMENT/PRODUCTION only on separately approved gates. **PRODUCTION NO-GO.**
