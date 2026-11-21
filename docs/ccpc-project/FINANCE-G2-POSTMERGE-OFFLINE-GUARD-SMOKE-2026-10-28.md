# Finance G2 — Post-merge exact-script offline guard smoke; faster-delivery standing instruction

**Date:** 2026-10-28 evening (Asia/Manila)  
**Scope:** Owner requested more **offline CircleCI readiness testing** while away from the office and explicitly asked ChatGPT to stop requesting repeat permission for routine low-risk source/test/documentation work. **No CircleCI pipeline launched or approved, no CI project-variable update, no hosted credit spend, no app-code or approved feature-SHA change, no DEVELOPMENT/Integration2, no PRODUCTION action.**

## Current immovable runnable feature candidate

- `ccpcerp/ccpcerp` branch `feature/finance-mapping-lifecycle-2026-10-28` remains **`317ad24d603e3d78d13d13e35fe08aca6bd90193`**, created by reviewed Finance-only PR23 merge into the feature branch. [PR21](https://github.com/ccpcerp/ccpcerp/pull/21) remains draft/unmerged into its parent; PR22 remains draft and separate.
- Do **NOT** update this feature branch merely to add more static tests; the owner-approved one-run CI project variable must be pinned to the exact prepared SHA. The [one-run CircleCI procedure](FINANCE-G2-ONE-RUN-CIRCLECI-HANDOFF-2026-10-28.md) is still applicable. Do not repeat previous 24/24 Python suite merely because this new independent smoke was run.
- GitHub exact verified blobs: `.circleci/config.yml` `933d1945afb2eea34a65f9cb98bd98397d5dcd19`; `.circleci/finance_baseline_stage.sh` `1a17067fd57af7d65d11610726016e46794fd323`; `.circleci/finance_baseline_deadline.py` `5d4707f24bf9e33ac51df51d694f1e873a59aa17`; `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py` `87e1f98308d6f2094ab6a45458dcd9cb6e6e5513`; `ccpcerp/ccpc_erp/test_finance_lifecycle_disposable_integration.py` `4aeaa7c5b841637fe3c66a0e507f6b0f5db1448b`.

## Source-only audit performed

Connected GitHub source pinned at feature SHA `317ad24d`: **51/51** targeted JavaScript review assertions PASS for:
- both expensive pipeline parameters default `false`, manual Finance approval, dependency/filter graph, exactly one guarded stage per kind, only one sidecar wait,
- exact CircleCI org/repo/job/feature branch/site, checkout equals `CIRCLE_SHA1` equals external `CCPC_FINANCE_APPROVED_SHA`, Frappe site role/actor guard,
- guard before deadline and expensive commands; only services/install/tests timeboxed; no PR22 probe path in Stage A; pinned Frappe/ERPNext Git SHAs, eight reviewed Finance tests, unknown-stage rejection and timebox process-group termination.

**5/5 independently mutation-negative control assertions PASS**, deliberately modifying in-memory representations to emulate duplicate service wait, removed approval dependency, raw service wait outside deadline, wrong branch filters and missing authorized SHA check. All broken variants rejected by corresponding review checks. First harness had a **test-check expression precedence mistake** for the duplicate control; it was **corrected and the final 5/5 rerun passed**. These are *ephemeral reviewer JS assertions*, not committed CI Python methods or a provider parser.

## ACTUALLY EXECUTED shell guard negatives on exact GitHub blobs

Local isolated scratch path `/mnt/data/finance_preflight_exact`, **not a real GitHub repository checkout**. Copied the two exact source files from the connected GitHub `317ad24d` commit into scratch, independently ran `git hash-object`, and verified both exact GitHub blob hashes:
- `.circleci/finance_baseline_stage.sh` = `1a17067fd57af7d65d11610726016e46794fd323` — `bash -n` **PASS**.
- `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py` = `87e1f98308d6f2094ab6a45458dcd9cb6e6e5513` — `python -m compileall -q` **PASS**.

A fresh isolated **local** `git init` and harmless one-commit fixture was made *only inside scratch*, HEAD `39019458808b89429195f8c4e96300bd3696596d`, using no remote and no CCPC real Git checkout. The test harness uses this temporary 40-character HEAD as a **test-only approved SHA** so it can exercise the *actual exact stage guard script*. **Do NOT confuse this local fixture SHA with the real authorized CircleCI SHA `317ad24d...`.**

Actual invocation: `python offline_stage_guards.py`. It only launches `bash finance_baseline_stage.sh install/tests/services` for **intentionally invalid identities**, and invokes `unknown` for one valid-identity case to prove the identity guards pass before the **unknown stage is denied**. No valid-identity services/install/tests commands were executed, and all four executable operations `sudo`, `bench`, `mariadb`, `npm` were shadowed with local sentinel scripts for fail-safe detection.

**17/17 EXECUTABLE FAIL-CLOSED CHECKS PASS**:
1. Wrong branch; missing branch.
2. Wrong CI job; wrong site.
3. Missing approved SHA; wrong approved SHA; wrong pipeline SHA; missing pipeline SHA.
4. Missing CircleCI identity flag; wrong CircleCI org; wrong CircleCI repo.
5. Missing workflow ID; missing pipeline ID.
6. Wrong Finance enable flag.
7. Invalid branch fails before **`tests`** dispatch; invalid branch fails before **`services`** dispatch.
8. Valid local-identity fixture + **unknown action** -> expected exit 2, proving strict stage dispatch.
For 16 early denials, expected exit **1**. For the final invalid stage, expected exit **2**. The sentinel file was not created in any case: **no sudo/bench/MariaDB/npm executed**. Local text log: `/mnt/data/finance_preflight_exact/offline-stage-guard-results-2026-10-28.log`.

**Interpretation:** This improves confidence that real CircleCI Finance steps cannot reach expensive operations under common invalid identity or dispatch inputs. It **does not prove** the real CircleCI provider config compiler, GitHub App pipeline trigger/branch semantics, secrets/variable presence in the user's account, real Frappe/ERPNext/MariaDB setup, accuracy of fixtures, credit cap, or actual eight Finance lifecycle tests. The previously reported 24/24 source Python tests remain the strongest complete local module evidence and are **not added** to 17/17 or 51/51 to make an artificial mega-test count.

## Next fastest safe action

1. **At the office, perform the owner-authorized single CircleCI manual Finance run** on feature SHA `317ad24d603e3d78d13d13e35fe08aca6bd90193`: project variable `CCPC_FINANCE_APPROVED_SHA` exact SHA, `run_finance_lifecycle=true`, `run_integration=false`; verify remaining credits, branch and correct manual hold/job, then one monitored approval. Log exact compiler/job result and do not rerun failures automatically.
2. While waiting, continue GitHub source review for the next **end-to-end** Withdrawal → SLE/GL → intercompany → four reports candidate. Avoid additional redundant preflight loops.
3. **Standing owner preference recorded in** [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md): routine source-only GitHub/code/test/doc tasks within the current requested scope proceed without repeat approval; ask only for major business/financial, persistent environment, irreversible Git, credentials/security or CI spend/action changes not already precisely authorized. This avoids interruption without weakening release safety.

**Decision: one-run Finance CI READY FROM GITHUB, hosted job NOT RUN, release/PRODUCTION NO-GO.**
