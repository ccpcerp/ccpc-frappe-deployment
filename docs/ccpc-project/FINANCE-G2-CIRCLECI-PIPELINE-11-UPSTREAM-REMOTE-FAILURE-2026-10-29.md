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
