# Finance G2 — CircleCI pipeline #11: Bench remote-name failure and reviewed CI correction

**Date:** 2026-10-29 (Asia/Manila)  
**Scope:** disposable hosted CircleCI Finance baseline only. **PRODUCTION and DEVELOPMENT unchanged.**  
**Disposition:** first approved hosted run **FAILED during setup**; no eight-test Finance MariaDB evidence. **No rerun authorized.**

## Exact approved pipeline and observed failure

- CircleCI project: `CCPCerp_2026/ccpcerp`; pipeline **#11**, manually triggered and manually approved by the owner.
- Config and checkout branch: `feature/finance-mapping-lifecycle-2026-10-28`.
- Feature commit: `317ad24d603e3d78d13d13e35fe08aca6bd90193`.
- Parameters: `run_finance_lifecycle=true`, `run_integration=false`.
- Workflow: `starter-validation` passed, separate `opt-in-finance-lifecycle` approved. No legacy integration job run.
- Uploaded owner-provided job step log: `build_22_step_104_container_0.txt`, ending **exit code 128**. The disposable runner installed host packages, installed `frappe-bench`, cloned Frappe v16 with `--origin upstream`, installed Frappe's Python/Yarn dependencies, and reported successful Bench initialization. Immediately afterward, `git -C apps/frappe fetch --depth 1 origin "$FRAPPE_SHA"` failed with `fatal: 'origin' does not appear to be a git repository`.
- The failure occurred **before** ERPNext installation, site creation/migration and the eight `ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration` test methods. Do not classify Finance behavior as passed or failed.

## Verified cause and exact corrective change

Frappe Bench creates Git checkouts using the remote name `upstream` (`git clone ... --origin upstream`). The original Finance shell script incorrectly assumed the remotes for both `frappe` and `erpnext` were named `origin`.

The connected GitHub app created the separate review branch [`review/finance-g2-upstream-remote-fix-2026-10-29`](https://github.com/ccpcerp/ccpcerp/tree/review/finance-g2-upstream-remote-fix-2026-10-29) from the unchanged feature tip, then committed only:

1. `.circleci/finance_baseline_stage.sh`: change **two** pinned fetches from `origin` to `upstream`. Keep pinned Frappe SHA `988e54f3c4c291e2077a83809663f123731abe76` and ERPNext SHA `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`, with their exact HEAD equality checks.
2. `.circleci/test_finance_ci_config_static.py`: add a regression test requiring both upstream fetches, retained pinned HEAD checks and forbidding the bad origin fetch.

Commits: `e2b4a01e2c8e854fb3901b3cad44274fc11a1381`, `6a17a6426d78b9bccb8ab6428e4137142d56edd0`, `9ccc815ed5904af2bbd816fdce93bf7e02bce126` (current review head). Draft [app PR #24](https://github.com/ccpcerp/ccpcerp/pull/24) targets **only** the Finance feature branch. No PR merge, original-branch write, CI variable change, job rerun, DEV site work or PROD action.

## Validation actually performed

- GitHub compare against original Finance feature SHA: **3 commits ahead, 0 behind, exactly two modified CI files** (two fetch-line replacements and 18 new test lines).
- **9/9** focused source invariants passed via independent GitHub read-back, including exact SHA preservation, identity guard preservation and no unintended stage changes.
- Independent offline Git fixture `git clone --origin upstream` reproduced the `origin` remote failure and verified `upstream` fetch plus checked-out commit equality for analogous Frappe and ERPNext repositories.
- An independently reconstructed copy of the **exact GitHub updated shell source**, verified by `git hash-object` blob `bc837147f543ff60155525be496e992927886011`, passed `bash -n`.
- Independently reconstructed **exact GitHub static test source**, verified by blob `2994901cf9dd79ec21a3388e5ba01a99520e074b`, passed Python compile; its **one new upstream regression test** executed **1/1 PASS** against the verified shell source. The other tests did not run here because the scratch import used placeholders for unrelated files. No claim of full 25-test suite.
- **Not run:** official CircleCI config compiler/rebuild, Frappe/ERPNext installation after fix, Finance real DB tests, HTTP/races, stock/GL, full suite.

## Safe continuation

1. Review draft app PR #24 and obtain **explicit scoped approval** before merging this fix into `feature/finance-mapping-lifecycle-2026-10-28`. The CI identity code intentionally forbids running the review branch.
2. After merge verify the **new full feature HEAD** and CI config/file hashes.
3. Since project environment variable `CCPC_FINANCE_APPROVED_SHA` is still pinned to `317ad24...`, update it in CircleCI project settings **only after approval and verification**. Never reuse old SHA or rerun the old pipeline.
4. Verify current free credits and account auto-refill/provider spending boundary. A source 90-minute timeout is not a hard monetary cap.
5. Ask for explicit approval of **exactly one new** manually held disposable Finance pipeline (new SHA). Confirm config and checkout branch, `run_finance_lifecycle=true`, `run_integration=false`, exact SHA in compiled pipeline, and finance approval hold before allowing paid job. No automatic retries.
6. Review full job output and eight real MariaDB results. Failure leaves Finance G2 pending; it does not approve business master/financial transactions, Integration2/DEVELOPMENT/PRODUCTION changes, app release or further CI workflows.

**Current status:** CI setup defect diagnosed; narrow corrected GitHub PR opened and locally regression-checked; **hosted integration remains pending**.


## 2026-10-29 — Owner-approved PR #24 merge completed (GitHub verified)

The owner explicitly approved **merging PR #24 into the Finance feature branch only**. The GitHub connector marked the PR ready for review and merged with exact head-lease `9ccc815ed5904af2bbd816fdce93bf7e02bce126`. GitHub returned `merged=true`, merge commit **`0564e94f5eea5eaa3c07f16a4fdacb84871eafdc`**.

Independent post-merge read-back:
- [PR #24](https://github.com/ccpcerp/ccpcerp/pull/24) CLOSED/MERGED with this exact SHA.
- `feature/finance-mapping-lifecycle-2026-10-28` HEAD now **`0564e94f5eea5eaa3c07f16a4fdacb84871eafdc`**.
- Comparison to previous feature tip `317ad24d603e3d78d13d13e35fe08aca6bd90193`: exactly **two changed CI-only files**, 2 fetch-line substitutions, 18 added test lines; no business code touched.
- Merged `.circleci/finance_baseline_stage.sh` blob **`bc837147f543ff60155525be496e992927886011`** includes both `upstream` remote fetches.
- Merged `.circleci/test_finance_ci_config_static.py` blob **`2994901cf9dd79ec21a3388e5ba01a99520e074b`** includes the new regression.
- Default `version-16` HEAD was separately read back at `cfcc19394a6646548f2b7050db040c8cf5ebafde`; not merged into default.
- **No new hosted CircleCI pipeline, job approval, environment-variable change, DEVELOPMENT test/migration, or PRODUCTION action** was performed as part of the merge.

**New run requires separate approval and a new SHA pin.** The previously configured CircleCI project variable `CCPC_FINANCE_APPROVED_SHA` was set for the old commit `317ad24...`; it does not authorize `0564e94...`. Do not rerun pipeline #11. Operator should first reconfirm the exact new SHA, credit balance/paid auto-refill boundaries, then separately approve a **single new manually held disposable** Finance pipeline with both config/checkout branches `feature/finance-mapping-lifecycle-2026-10-28`, `run_finance_lifecycle=true`, `run_integration=false`. Test and provider compilation remain unverified on the new commit until an actual run.

## 2026-10-29 — CircleCI pipeline #12: green workflow, test log pending

The owner explicitly authorized **one further** manually held disposable Finance CircleCI run at the post-PR24 feature SHA `0564e94f5eea5eaa3c07f16a4fdacb84871eafdc`. CircleCI project variable `CCPC_FINANCE_APPROVED_SHA` was changed in the app UI and displayed a masked suffix `afdc`; the operator reported **29,017 remaining credits** before triggering. Screenshots independently show both config and checkout branches `feature/finance-mapping-lifecycle-2026-10-28`, parameters `run_finance_lifecycle=true`, `run_integration=false`.

The owner's CircleCI screenshot of **pipeline #12** shows a **green/successful pipeline**, `starter-validation` green (18s), `opt-in-finance-lifecycle` green (6m 8s), displayed checkout SHA prefix `0564e94`, and title `Merge PR #24: fix Finance CircleCI pinned upstream remote fetches`. This is user-visible provider workflow-state evidence, not a captured step log. **Eight Finance MariaDB test assertions, explicit final `Ran 8 tests ... OK`, skipped tests, and backend/fixture details have not yet been individually verified.** Operator was asked to open `finance-lifecycle-isolated-integration` → `Finance lifecycle MariaDB service tests, no HTTP server or ledger posting` and share the full step log before promoting Finance G2 from pipeline-green to validated integration evidence.

**No third pipeline, rerun, CI variable change, GitHub app code change, DEVELOPMENT or PRODUCTION action authorized.** Any further DB/HTTP/stock/GL tests remain separate release gates.


## 2026-10-29 — Pipeline #12 Finance G2 real MariaDB test log: 8/8 PASS

**Evidence:** Operator-uploaded original CircleCI step text log `build_25_step_105_container_0.txt` from the successful, one-time pipeline #12, job step **Finance lifecycle MariaDB service tests, no HTTP server or ledger posting**. This is direct runner output, not only a green workflow screenshot.

- Test site: `ci-finance-lifecycle.localhost` (disposable CircleCI-only site).
- Bench module: `ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`.
- Log reports `Running 8 unspecified-category tests for ccpcerp` and individually shows a green check for **all eight** `TestFinanceLifecycleDisposableIntegration` methods:
  1. `test_a_schema_has_required_lifecycle_fields_and_no_general_permissions`
  2. `test_b_draft_rejection_is_terminal_and_audited`
  3. `test_c_signed_approval_is_once_only_and_denies_forged_reference`
  4. `test_d_signing_version_failure_rolls_back_decision`
  5. `test_e_retirement_request_replay_decline_and_accept_are_audited`
  6. `test_f_unauthorized_guest_and_administrator_fail_closed`
  7. `test_g_center_approval_uses_exact_company_department`
  8. `test_h_rejection_audit_failure_rolls_back_event_and_state`
- Final output: **`Ran 8 tests in 2.096s`**, **`OK`**, **`Finance disposable database tests finished; reconcile results before further stages`**.
- **8/8 PASS, 0 failures, 0 errors, and no skipped tests indicated by the provided step output.** Screenshot had already shown `starter-validation` and `opt-in-finance-lifecycle` successful at source SHA prefix `0564e94`; independent GitHub branch read-back confirms full feature SHA **`0564e94f5eea5eaa3c07f16a4fdacb84871eafdc`**. Original CI setting was pinned to this SHA for the approved second run.
- The prior #11 `origin` failure is resolved for this observed pipeline; the dedicated Frappe/MariaDB install and Finance step reached completion, though the full setup log for #12 was not separately uploaded in this session.

**Acceptance boundary:** The **Finance G2 disposable eight-test SQL/service baseline is validated at the recorded source**, not production certification. It does **not** verify authenticated browser/HTTP/CSRF flows, independent multi-connection concurrency, all Stock Ledger/GL postings, end-to-end Withdrawal→intercompany invoices and reports, full persistent DEVELOPMENT acceptance, real Accounting signatory/Company grants, or dedicated PRODUCTION backup/restore/cutover.

**Next:** Focus on the actual integrated withdrawal→material issue→stock/expense ledger→intercompany invoices and the four frozen day-one reports, with a reviewed exact-source acceptance plan. Separate owners' approvals for any future billable CI, persistent DEVELOPMENT or PRODUCTION modifications, and Finance signatories still apply. Do **not** automatically rerun pipeline #12.
