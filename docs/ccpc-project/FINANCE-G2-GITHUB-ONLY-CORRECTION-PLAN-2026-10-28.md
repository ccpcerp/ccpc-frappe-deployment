# Finance G2 — GitHub-only correction plan for reviewed test selection and bounded CI

**Date:** 2026-10-28 (Asia/Manila)  
**Status:** **PLAN FOR REVIEW / NOT CODE AUTHORIZATION / NO-GO for hosted G2.** The owner approved preparing this narrowly scoped GitHub-only plan after the [source-only CI readiness review](FINANCE-G2-SOURCE-ONLY-CI-READINESS-REVIEW-2026-10-28.md), **not** implementing or running any CircleCI pipeline, installing a bench, creating/committing masters, touching DEVELOPMENT/Integration2/PRODUCTION, merging code, enabling paid API access or authorizing spending.

## 1. Current verified baseline — preserve these facts

- [Finance PR21](https://github.com/ccpcerp/ccpcerp/pull/21) is **OPEN/DRAFT/UNMERGED**, feature `feature/finance-mapping-lifecycle-2026-10-28` @ **`d154886ab45c51878a87a4ecf42e45602d8d9ccb`**.
- [Finance PR22](https://github.com/ccpcerp/ccpcerp/pull/22) is **OPEN/DRAFT/UNMERGED**, review `review/finance-http-concurrency-tests-2026-10-28` @ **`175207c798fe63b49f22a940d0510f667b798c52`**, **26 commits ahead and zero behind** feature. It adds eight probe/fixture/mock-test files and **does not edit** the active `.circleci/config.yml`.
- Existing CircleCI config blob **`9aa8c676dfa7b22e7b7035d70a0b461af773908d`**; disposable Finance site guard blob **`87e1f98308d6f2094ab6a45458dcd9cb6e6e5513`**. Its Finance job, workflow branch filter, guard and SHA gate require the **feature** branch, **not** PR22 review branch. The Finance job executes only the eight original methods of `ccpcerp/ccpc_erp/test_finance_lifecycle_disposable_integration.py` (blob `4aeaa7c5b841637fe3c66a0e507f6b0f5db1448b`).
- **Important test side-effect boundary:** the eight-test baseline's `setUp()` calls `self.load_test_records("Stock Entry")` after a disposable-site check; a live baseline run may create Company/account/user/item fixtures **in its test DB**, and requires separate runtime authorization even though the test is rollback-oriented. It is not safe to describe it as a database-read-only check or a PR22 HTTP/race test.
- PR22's exact committed offline Python **23/23 PASS**, **15 mock-DB behavior + 8 static source-policy**, was previously verified at the review SHA. It does **not** prove actual Company/CoA creation, database index uniqueness, authenticated CSRF, or two-transaction operation.
- No live CircleCI project variables, account plan/credit balance, actual configuration compilation, or external job execution have been checked.

## 2. Decision: split the work into two independent review stages

### Stage A — *baseline G2, eight lifecycle tests* (first proposed execution target; still NOT authorized)

**Objective:** Safely validate the existing Finance feature-branch integration suite **without** merging PR22 or running the new probes. This keeps test scope and branch truth aligned and avoids changing the established Finance guard merely to make a PR pass.

**Minimal prospective GitHub code patch, subject to a new, separate approval:**

1. On an **appropriate review branch created from/targeting the Finance feature source**, leave the exact feature-branch identity and externally approved commit gate intact. Do **not** retarget PR22, relax its guard, spoof `CIRCLE_BRANCH`, move to default, or merge PR21/PR22 as a shortcut. Review the actual branch/commit before any write.
2. Modify only the **Finance-specific** pieces of `.circleci/config.yml`, a small optionally separate Finance deadline helper, and Finance config/guard offline tests. Preserve legacy Withdrawal/GL CI workflows, parameter defaults, branch guards and approval holds.
3. Keep `run_finance_lifecycle: false` default, a separate manual approval hold, and exact `CIRCLECI` org/project/job/site identity, checkout SHA and externally administered approved SHA.
4. Explicitly pin the sole baseline test command to `bench --site "$TEST_SITE" run-tests --module ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`. Assert **the eight known test-method identifiers** in source/offline tests. No unconditional test discovery, user-provided module string, PR22 `ci_finance_*_probe` call, master bootstrap, race fixture creation, or HTTP login.
5. Minimize unconditional starter cost only after checking current CircleCI trigger semantics. Current `starter-validation` always runs `python-syntax` even when Finance is held; this must be explicitly included in the approved compute budget, or changed through a separately reviewed condition that **does not suppress normal starter CI** on ordinary pushes. Any source push might itself trigger starter checks depending on project settings; verify first.

**Acceptance:** Offline fixture/source/guard tests cover both allowed and denied identities, pin and branch mismatches, default-false/no-auto-trigger, and exact baseline module selection. CircleCI compiled configuration must pass CLI validation without creating a pipeline. Live test execution remains separately gated.

### Stage B — *PR22 HTTP / genuine concurrent race probes* (later, separate approval and PR)

**Objective:** Establish PR22-specific evidence separately; **do not claim the baseline G2 run tests these paths**.

- Introduce an **independent**, default-false, manual approval and exact review-branch/SHA job **only in a separately approved PR**, not by widening the existing feature-branch Finance guard. If new branch support is needed, design a separately named fail-closed probe guard with precise `job`, `site`, `branch`, `CIRCLE_SHA1`, approved SHA and distinct owner-approved flags. Update each PR22 probe/fixture import intentionally; never treat both branches as generally interchangeable.
- Define fixed, enumerated opt-in sub-stages: (a) read-only preflight/CoA/physical unique-index audit; (b) authenticated HTTP/CSRF check against a preprovisioned fictional checker; (c) two-connection Company lock check; (d) independently authorized signed Maker/Checker fixture **COMMIT**; and (e) once-only Approval/Retirement competition with real writes in a disposable DB. One stage cannot imply permission for later stages. Each stage must fail closed without its own explicit owner authorization.
- Maintain no real business emails/passwords and no DEV/PROD data. The temporary site must be demonstrably disposable with rollback/disposal, and the fixture builder must prove Frappe state-restoration and non-DB side effects before persistent synthetic commits.
- Keep stage B **dormant** until Stage A's reviewed evidence and a distinct owner's approval. No branch bypass, blanket `ignore_permissions` relaxation, rollback shortcut, or default-on toggle.

## 3. CircleCI syntax and config verification — source-only gate

CircleCI currently documents **`circleci config validate`** and **`circleci config process ... --pipeline-parameters ...`** (official reference: https://cli.circleci.com/reference/). These can validate/compile config **without triggering a pipeline**; a real CircleCI CLI validation was **not executed** in this planning turn, and the CLI is not installed in the available local runtime.

After a separately approved source patch, validate the exact GitHub blob on both the default/opt-in parameter permutations. Provisional offline commands (do not use `circleci local execute`, `trigger`, `pipeline run`, hosted approval, or any networked CI execution):

```sh
circleci config validate .circleci/config.yml
circleci config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: false'
circleci config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: true'
```

Save the compiled outputs and checksum **locally, redacting any sensitive project metadata**. Inspect the actual compiled job graph for default-false behavior, manual approval dependencies, exact branch filters and starter job behavior. Extract `run.command` blocks from the **compiled** output, then `bash -n` those shells. The raw config's `\\<<` heredoc escape cannot be evaluated as the literal final shell script: simulate `\\<<` → `<<` only as a preliminary local check, **not as CircleCI compiler evidence**. Also test the wrong branch/SHA/job/site, missing approved SHA, and unknown test target against isolated source-only guard tests. CircleCI official docs on parameters and workflow filtering: https://circleci.com/docs/guides/orchestrate/pipeline-variables/ and https://circleci.com/docs/guides/orchestrate/using-branch-filters/.

## 4. Enforceable wall-clock control and credit accounting — design, not a promise

**No numeric limit is approved by this plan.** The previously discussed **90-minute/2,500-credit** proposal is only a *candidate for a later decision*, not authorization or a guaranteed cap.

- **Job-local duration:** design a cumulative deadline from the start of the first Finance shell step (for example, an absolute UTC epoch persisted to every subsequent step), and require every long-running Finance command to run through a tested, fail-closed `timeout --signal=TERM --kill-after=...` wrapper using the **remaining** time. A deadline set separately for each step **would not bound the whole job**. Define handling for checkout, startup delays, MariaDB sidecar failures, processes spawned by `bench`, errors during cleanup, and aborted jobs. Preserve the no-output timeout as a secondary safety, not as a wall clock cap. Add offline tests using simulated near-expiry, expired and cleanup/failure paths.
- **Limits of in-job timeout:** CircleCI job startup/checkout precedes the first deadline; sidecars, agent delays and external billing may also matter. A shell `timeout` **does not hard-cap pipeline credit use**. CircleCI plan-specific job maximums are not a substitute for an approved shorter cap (official configuration reference: https://circleci.com/docs/reference/configuration-reference/).
- **Operational outer cutoff required before launch:** owner/approved operator must confirm actual CircleCI subscription, credits, auto-refill and rerun controls, starter job cost, compute class and sidecar charges; define a **single-use approval**, no automatic/manual reruns without reapproval, real-time monitoring and separate **CircleCI cancel** procedure before a specified wall-clock/credit threshold. If an enforced organization-level spending cap cannot be verified, **do not promise a strict 2,500-credit ceiling**: classify the spend bound as an estimate and retain **NO-GO** for runs requiring a hard monetary cap.
- **Planning rates, not authorization:** CircleCI's [October 8, 2026 price list](https://circleci.com/pricing/price-list/) lists Docker x86 `large` at **20 credits/minute** and `small` at **5 credits/minute**. Illustrative **90 min × 20 = 1,800 credits** for the Finance job alone, **plus** starter `small` compute and eligible add-ons; a **2,500-credit** proposed cap is **not guaranteed** by checking job time. CircleCI documents automatic reruns may consume extra credits (https://circleci.com/docs/guides/orchestrate/automatic-reruns/). Current project billing, credit availability and actual runtime remain unknown.

**Proposed explicit authorization record for any future hosted run:** checked-out 40-character SHA, target branch, exact named test suite/stage, disposable site name, CircleCI project/org identity, approved maximum total duration and credit spend, no-rerun instruction, operator who can cancel, rollback/disposal path, and separate fixture-COMMIT permission if applicable.

## 5. Implementation order and review gates

| Phase | Change | Required evidence | Authorization |
| --- | --- | --- | --- |
| 0 — **now** | Commit this **source-only plan** to the docs branch and update rolling handoff | GitHub document/handoff commit SHAs; current PR branches verified | Covered by owner's plan approval |
| 1 — next | Review and separately authorize the **Stage A Finance-only config/deadline tests patch** on the correct review branch | Changed-path audit; no legacy CI regression; synthetic timeout/fail-closed tests; PR reviewed | **New explicit owner approval needed** |
| 2 | Offline CircleCI CLI validation and compiled-shell audit of exact approved source SHA | Validated/compiled YAML, false/true workflow graphs, `bash -n` of compiled shell, negative guard checks | Offline-only permission; **no pipeline** |
| 3 | Review original eight-test suite's Company/CoA/Stock Entry test fixture dependencies, cost/stop policy, physical DB index preconditions and ephemeral site disposal | Owner-signed G2 readiness/rollback checklist; current actual CircleCI plan and available credits | **Separate permission before any DB test or hosted spend** |
| 4 | Single approved baseline Finance G2 run, then document results in GitHub | Actual Frappe/MariaDB test results, cost, commit and recoverability review | **Separate explicit operator authorization** |
| 5 — later | Stage B PR22-specific probe wiring/fixtures/HTTP/race integration review | Per-stage identity, fixture commit safeguards, data and webhook/email side effects, independent once-only SQL evidence | **Separate PR and separate authorizations** |

**Stop conditions:** unknown source SHA/branch; inability to compile config offline; missing manual hold/approved SHA; unknown CircleCI billing/auto-refill or unsupported resource class; no enforceable time/cost path; non-disposable site; incomplete physical DB uniqueness/recovery preflight; unsafe financial master side effects. Any one blocker remains **NO-GO**.

**Disposition:** correction **plan documented only**. No app code edits, PR merge, CircleCI CLI execution, CircleCI project environment modification, pipeline creation/approval, persisted master/test fixture commit, DEVELOPMENT/Integration2 or PRODUCTION action.
