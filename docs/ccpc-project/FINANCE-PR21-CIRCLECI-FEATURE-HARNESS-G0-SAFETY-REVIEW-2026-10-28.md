# CCPC Finance PR #21 — G0 CircleCI feature-harness safety review

**Date:** 2026-10-28 (Asia/Manila)  
**Approval:** Owner replied "Approved" to a **GitHub-only CI harness safety review**, explicitly **without starting a pipeline or modifying any ERPNext environment**.  
**Status:** REVIEW COMPLETE — RECOMMENDED DESIGN ONLY, NO CI/TEST CODE CHANGE AUTHORIZED, NO JOB EXECUTED.

## 1. Verified GitHub inputs

Use [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), [Finance PR21 disposable MariaDB plan](FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md), [Finance authentication handoff](INTEGRATION2-FINANCE-AUTHENTICATION-CHECKPOINT-2026-10-27.md), and [draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21).

At review, GitHub reported:

| Item | Exact current GitHub ref / blob |
| --- | --- |
| App feature branch | \`feature/finance-mapping-lifecycle-2026-10-28\` at **\`76973699a085d3eb4efd6412d21a773ec1499e19\`** |
| App PR base/review | \`review/circleci-isolated-erpnext-phase2-2026-10-26\` at **\`0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41\`** |
| PR | **#21 OPEN / DRAFT / UNMERGED** |
| \`.circleci/config.yml\` | Blob \`5a9f023c0105bad333ddedfe1976939049447151\`, identical at feature and base tips |
| \`ccpcerp/ccpc_erp/ci_disposable_site_guard.py\` | Blob \`e20c7822186729bd793e3934a9af46f57c38742b\` |
| \`.circleci/test_ci_disposable_site_guard.py\` | Blob \`fa1f950901df0434fb9d0ad86dd0cd2419cebcc4\` |
| \`ccpcerp/ccpc_erp/ci_synthetic_finance_fixture.py\` | Blob \`c13498d0c7669ca29b48b58daa28d8a4551f9008\` |

Previous operator-run Python source/static policy tests **24/24 PASS** at the feature SHA, but no PR21 real MariaDB/HTTP test has been executed. Do not confuse these facts with CI harness readiness. Recheck all refs immediately before any later implementation or run.

## 2. Existing CircleCI safety behavior — static source findings

- \`.circleci/config.yml\` has an inexpensive \`python-syntax\` job and an expensive \`isolated-erpnext-integration\` job. The latter exists only under \`run_integration\`, **default false**. The source says the prior PR \`run-ci\` label runs only starter-validation; it is **not** blanket approval for an integration run. No CI schedules or auto approval jobs should be introduced.
- The integration job is a CircleCI Docker environment with a fresh bench, local MariaDB 11.8 and Redis sidecars, site \`ci-circleci.localhost\`, and local CI-only credentials. Its shell preflight checks the actual CircleCI organization, repository, job, pipeline/workflow/build identity, **CIRCLE_BRANCH equal to the original review branch**, and \`git rev-parse HEAD == CIRCLE_SHA1\`. It then creates/migrates a new Frappe v16 and ERPNext v16 site; its Frappe/ERPNext selectors currently track **floating version-16 branches**, not exact Git commit pins.
- \`is_reviewed_circleci_disposable_site\` also requires the original review branch, exact site, CircleCI identity, \`CIRCLE_JOB=isolated-erpnext-integration\`, several build IDs and \`CCPC_ALLOW_COMMIT_PROBE=isolated-only\`. This is referenced by existing B/C and Withdrawal/Intercompany synthetic fixtures; \`ci_synthetic_finance_fixture.py\` creates synthetic Approved-looking rows with a **special non-Accounting token**, which must NEVER be interpreted as a genuine internal signed Accounting Decision.
- Existing pure-stdlib negative tests explicitly deny missing/mismatched CircleCI identity, wrong branch/job and non-disposable site. These tests are a proven **source-defined** boundary, not a certification that runner network isolation was audited.
- Existing integration job executes legacy Withdrawal/GL and Intercompany test modules. **It does not list a PR21-specific lifecycle test module**, and the currently committed PR21 tests are only static/pure-policy. Thus modifying a branch condition alone would not exercise actual signed Decision, one-time Use, terminal reject, retirement requests/acceptance or their SQL/HTTP/Version failure cases.
- The old job is guarded for original review SHA/branch. Running it directly from the PR21 feature branch should **STOP by design**. Neither the shell guards nor legacy fixture allowlist should be casually widened; an environment variable spoof or force-move of a branch is forbidden.

## 3. G0 selected technical recommendation — separate fail-closed Finance CI path

**Recommend creating a distinct, explicitly opt-in, disposable Finance lifecycle CI job and guard in a later separately authorized app commit.** Do NOT edit the old \`isolated-erpnext-integration\` job, its original \`is_reviewed_circleci_disposable_site\`, its existing fixture tests, or other site guards just to make this feature pass.

**Proposed interfaces (not installed):**

1. New isolated job with distinct exact name such as \`finance-lifecycle-isolated-integration\`, distinct site such as \`ci-finance-lifecycle.localhost\`, independent transient test database and Redis connections, separate CI-only synthetic credentials, no production contexts or persistent Docker volume mounts. Its source preflight must confirm actual CircleCI org/repo/branch/job identity, nonempty pipeline/workflow/build IDs and exact checked-out commit. **Block if branch is not \`feature/finance-mapping-lifecycle-2026-10-28\`** or if current \`CIRCLE_SHA1\` does not match checked-out Git HEAD.
2. An independent \`is_reviewed_finance_lifecycle_disposable_site(site)\` that rejects every other site/branch/job and all missing/altered identity conditions. Include exact new job/site identity, actual runner commit and a newly reviewed immutable source authorization. Never make the old guard accept this site or branch, and never let the new guard authorize generic withdrawal/intercompany fixture helpers.
3. **Commit pinning / authorization:** Initial test source is PR21 feature SHA \`76973699...\` **only as the pre-harness baseline**. A harness commit necessarily changes SHA. At the next review, freeze the **new post-implementation SHA** in a reviewer-controlled allowlist or independently authorized run manifest, then verify CircleCI checkout \`HEAD == CIRCLE_SHA1 == approved SHA\` in the job before bench setup. Merely trusting a caller-provided pipeline SHA or branch name is not release approval. Any later source change invalidates that authorization pending explicit review.
4. New CI workflow selector distinct from the original \`run_integration\`, default false, manual/owner-authorized trigger only, never enabled by a PR label or schedule. Limit one approved disposable job, capped resource class/runtime/attempts and reviewed compute cost. Verify feature-branch CircleCI workflow trigger semantics (actual \`CIRCLE_BRANCH\` on PR builds, fork trust, branch filters) *before* an expensive run; do not spoof environmental values to pass.
5. Pin Frappe v16 and ERPNext v16 to exact reviewed commit SHAs (do not silently float version-16 tip) with recorded Python, Node, MariaDB, Redis and bench versions. The exact known compatible versions from earlier DEVELOPMENT are context, not automatically validated on CI. Dependency install source integrity/availability and supply-chain risks should be reviewed separately.
6. Add a **new real Frappe v16/MariaDB Finance lifecycle integration module** to the feature branch (currently missing), not just schema-file tests. Include a true authenticated Maker/Checker HTTP+CSRF loop and **test-only** isolated site data for B and C; isolated schema installation, signed internal decision, one-use consumption, rejected Draft, pending/declined/accepted retirement, before_submit cutoff, historical as-of verification, wrong-Company/self-approval, locked races, forced Version rollback, migration compatibility and independent rowcount audits. Use the previously reviewed 24-case acceptance matrix from the test plan. Do not reuse TISS persistent synthetic records or promote the special CI fixture token into real Accounting evidence.
7. The independent job must be denied access to existing CCPC DEVELOPMENT/PRODUCTION site configs, SSH keys, NAS mounts, Docker host sockets, production database networks and connected live app credentials. Check service endpoints and deny unexpected egress before any data writes. Source-based branch guards alone do not prove physical isolation; if the runner cannot be safely attested, STOP and prefer a separately approved VM.

**Why an independent path?** It isolates feature-specific test authorization, prevents legacy fixture exceptions from spreading, preserves old CI behavior and blocks accidental invocation from persistent sites. It also lets Finance test modules remain separately reviewable without broad existing Withdrawal/Intercompany regression runs.

## 4. Non-negotiable negative-test and code-review contract

Before *any* runtime execution, the proposed CI harness change must include and **execute locally/static-only** source/guard tests for:

| Class | Must be denied/verified |
| --- | --- |
| Identity | Non-CircleCI runner; missing org/repo/job/build/workflow/pipeline ID; wrong branch; mismatched checked-out SHA or reviewer-pinned SHA |
| Site | \`development.localhost\`, \`ccpc-integration2.localhost\`, \`ccpcerp.local\`, \`production.localhost\`, legacy \`ci-circleci.localhost\`, empty/nonstring/site spoof |
| Cross-authority | Old \`is_reviewed_circleci_disposable_site\` denies new Finance branch/site; new guard never authorizes old CI fixtures/Intercompany runners |
| Pipeline activation | No unrequested integration job from PR labels/default parameters; default false; branch filter; one explicit approved manual run only |
| Data and secrets | No DEV/PROD remote URL/secrets/mounts, no stock/GL master import; synthetic test identities only, no business record attachments in logs |
| App code | Exact feature SHA/PR base and Git status; no broad source change, no merge/rebase or force-push; no relaxation of legacy approval guards |
| Database/rollback | New disposable DB/site only; abort on unexpected existing tables/records, unverified MariaDB uniqueness or partial audit writes; independent readback |
| Logs/cost | Sanitized failure output, proof of resource expiry and bounded cost; do not rerun ambiguous failed stage without inspection |

**Review hard-stops:** Any change to the original guard that accepts feature branch, any fallback to generic \`CI=true\`, CI environment spoofing, unpinned source, automatic expensive PR runs, use of persistent site, unreviewed runner context, shared Docker daemon or secrets, or missing test-only lifecycle module. Do not claim the new job is ready merely because YAML parses or a source guard unit test passes.

## 5. Next authorization gates and handoff

- **G0 safety review: COMPLETED HERE.** This document is a review conclusion and recommended design; no GitHub application/CI file was edited or executed under this scope.
- **G1 — Separate owner approval for GitHub implementation** of an isolated, feature-only CI job + guard + negative tests + genuine lifecycle database integration tests. Name the feature branch/review baseline, allow no CI run/merge, and require a new pinned post-implementation SHA and code review.
- **G2 — Separate owner approval for a specific opt-in paid CircleCI test run** (or named isolated VM), after inspecting exact runner identity, isolation, cost bounds, source pins, secrets/network and validated negative tests. Define precisely which 24-case stages and whether test-only stock/GL and SQL failure injection are permitted.
- **G3 — After recorded CI results, separately approve or reject persistent DEVELOPMENT adoption** with backups/site isolation and verified Git status. No production deployment is implied by a green disposable run.
- **G4 — PRODUCTION: independent explicit release approval** with genuine Accounting business signatories/crosswalk, audited data recovery and rollback review.

**Status at conclusion:** PR21 OPEN/DRAFT/UNMERGED, feature HEAD \`76973699a085d3eb4efd6412d21a773ec1499e19\`. Static Python 24/24 PASS; CI runner/feature lifecycle database testing **NOT EXECUTED**; current CI hard guard **NOT MODIFIED**; existing Integration2 Draft \`fieef2e44j\` **last verified Draft**. No app source/CI job change, pipeline, migration, financial posting, DEVELOPMENT or PRODUCTION interaction authorized or performed by this review.
