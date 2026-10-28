# Finance G2 — source-only CircleCI and disposable-site preflight readiness review

**Date:** 2026-10-28, Asia/Manila  
**Authorization boundary:** Owner approved a **source-only readiness review** following Finance PR22's committed offline 23/23 PASS. No live CircleCI pipeline creation, manual approval, spend, fixture/master commit, real Frappe/MariaDB/HTTP operation, DEVELOPMENT/Integration2, application merge, or PRODUCTION operation was authorized or performed.

## GitHub truth verified

- [Finance draft PR22](https://github.com/ccpcerp/ccpcerp/pull/22): OPEN/DRAFT/UNMERGED `review/finance-http-concurrency-tests-2026-10-28` @ `175207c798fe63b49f22a940d0510f667b798c52`; base `feature/finance-mapping-lifecycle-2026-10-28` @ `d154886ab45c51878a87a4ecf42e45602d8d9ccb`. PR22 is **26 commits ahead**, zero behind its base, with **eight added files**, and **does not modify** `.circleci/config.yml`.
- [Finance draft PR21](https://github.com/ccpcerp/ccpcerp/pull/21): OPEN/DRAFT/UNMERGED; head is the same `d154886ab45c51878a87a4ecf42e45602d8d9ccb`, base `review/circleci-isolated-erpnext-phase2-2026-10-26`.
- Active app `.circleci/config.yml` at PR22 SHA has verified GitHub blob `9aa8c676dfa7b22e7b7035d70a0b461af773908d`. `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py` has verified blob `87e1f98308d6f2094ab6a45458dcd9cb6e6e5513`. Both baseline integration test module `test_finance_lifecycle_disposable_integration.py` (8 test methods) and config/guard tests are present at feature and PR22 refs, with identical blobs.

## Source-only findings

| Check | Result and required interpretation |
| --- | --- |
| Finance pipeline parameter | **PASS source:** `run_finance_lifecycle` defaults to `false`. Original `run_integration` also defaults to `false`. |
| Manual approval | **PASS source:** Finance workflow includes `finance-lifecycle-manual-approval`; integration job requires that hold. |
| Branch filtering / guard | **BLOCKER for PR22:** Workflow filter, early shell checks, and Python disposable-site guard all require `feature/finance-mapping-lifecycle-2026-10-28`; PR22 head is on `review/finance-http-concurrency-tests-2026-10-28`. Do not spoof CircleCI branch variables or bypass exact-SHA controls. To test PR22 code in hosted CI would require separately reviewed code-branch integration plus authorization; existing G2 configuration tests only the feature-branch baseline. |
| Exact SHA | **PASS source, NOT live verified:** `CIRCLE_SHA1`, checkout `git rev-parse HEAD`, and externally administered `CCPC_FINANCE_APPROVED_SHA` must agree. The approved SHA is not hardcoded in YAML; whether it is provisioned correctly in the CircleCI project was **not** checked. |
| CI site identity | **PASS source, NOT runtime isolation proof:** Exact `ci-finance-lifecycle.localhost`, job/project/branch IDs and `CCPC_ALLOW_FINANCE_LIFECYCLE_TESTS=isolated-only` required. Sidecars: MariaDB 11.8 plus two Redis 7 services, created within CircleCI's Docker executor. The guard checks environment identity; independent real-world runner isolation and credentials were not verified. |
| Pinned external code | **PASS source:** Frappe pinned `988e54f3c4c291e2077a83809663f123731abe76`; ERPNext pinned `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`; app checkout gated to approved SHA. No actual bench installation or pinned runtime compatibility test performed. |
| Test scope | **BLOCKER for PR22 probes:** The integration job runs the original eight ERPNextTestSuite lifecycle tests only. The PR22 two-connection lock probe, real Maker/Checker race, HTTP/CSRF probe, master bootstrap and fixture builder are **not called**, deliberately dormant and independently gated. Passing the original tests would **not** establish PR22's new HTTP/race objectives. |
| Physical DB/schema evidence | **NOT VERIFIED:** Real Company/CoA bootstrap generation, Item Group, synthetic actors, actual migrated MariaDB unique indexes, optimistic-lock and commit interactions, thread-local hooks, network/email side effects, and rollback/recovery controls are still untested on an authorized disposable site. |
| CI template syntax | **LIMITED PASS:** GitHub-exact YAML parsed locally with PyYAML as v2.1. All four Finance `run.command` shell blocks passed local `bash -n` **after replacing** `\\<<` with `<<` as CircleCI's documented heredoc escape is intended to render. The raw `\\<<` source fails shell syntax check; CircleCI docs instruct this escape in config v2.1. **Actual CircleCI compiler rendering/validation was not performed:** CircleCI CLI was not available, no hosted pipeline/config process attempted. |
| Executed Python tests | **PREVIOUSLY VERIFIED ONLY:** The exact-file offline 23/23 committed source/mock tests PASS at `175207c`. No real DB, HTTP, CircleCI or ERPNext runtime test this review. |
| Additional starter job | **COST/CONTROL RISK:** `starter-validation` is unconditional and includes a `python-syntax` Docker `small` job. Starting an opt-in Finance pipeline also starts this job, regardless of Finance manual hold status. An opt-in pipeline is therefore **not a zero-cost preflight**. |
| Timeouts / cost | **BLOCKER:** Finance job has `no_output_timeout` of 20 minutes on two long steps; this is **an idle-output timeout, not a 20-minute total cap**. No approved global wall-clock/credit ceiling or automated cutoff is present. Plan/account billing & current credit balance were not checked. |

## Current CircleCI cost planning (not approval)

CircleCI's **2026-10-08** x86 Docker Gen1 price list quotes `large` at **20 credits/min**, `small` at **5 credits/min** (sources: <https://circleci.com/pricing/price-list/> and <https://circleci.com/docs/guides/plans-pricing/credits/>). The raw configuration specifies `large`, not `large.gen2`. A hypothetical 90-minute Finance job at 20 credits/min implies **~1,800 compute credits**, plus starter job compute and any billable extras; **2,500 credits** corresponds to 125 Finance-job minutes at the nominal large-class rate **before** other charges. Previously mentioned **90-minute/2,500-credit** limits were proposals, not owner approvals or hard enforced controls. Account resource availability, billing and actual execution cost cannot be inferred from public pricing.

CircleCI documentation confirms `no_output_timeout` tracks duration *without output*, not total run time. An actual bounded run would need an approved enforcement method across all steps and a verifiable cancellation/rollback policy, not reliance on step idle timeouts alone. See: <https://circleci.zendesk.com/hc/en-us/articles/360007188574-Build-has-Hit-Timeout-Limit>.

CircleCI's 2026 documentation recommends escaping shell heredoc `<<` as `\\<<` in v2.1 source: <https://discuss.circleci.com/t/breaking-changes-config-compilation-updates-september-21-2026/54719>. The compiler output must still be checked by an approved safe offline/CLI-only method before any hosted run.

## Required before any hosted G2 launch

1. Decide the **exact test target**: feature-branch **eight baseline lifecycle tests**, or **PR22 review-branch HTTP/race probes**. Do not describe the former as proving the latter. If PR22 probes are desired, design the needed independently authorized fixture setup and reviewed branch integration; do not bypass branch/SHA guards.
2. Validate compiled CircleCI v2.1 config and hermetic shell commands without launching a pipeline; verify actual CircleCI organization/project identity, plan resource availability, current credit balance, and externally controlled approved SHA (do not disclose or commit secrets).
3. Establish a separately **approved and enforced** job wall-clock and consumption boundary, accounting for the unconditional starter job, eligible retries/reruns and sidecar overhead; establish who monitors/stops runs and whether automatic refill would permit overrun.
4. Verify site/DB/Redis are disposable and contain no persistent DEV/PRODUCTION data, examine pinned Company controller's master creation and side effects, confirm physical unique indexes and test preconditions, then approve any synthetic master or fixture **COMMIT** separately.
5. Obtain explicit separate owner authorization for any CircleCI pipeline start and approval hold, along with the exact reviewed commit, named tests, maximum spend and rollback/disposal procedure. **No approval is inferred from this source review.**

**Disposition: G2 FINANCE CI — NO-GO, source-only review complete.** No application code changed. No CircleCI pipeline, CI approval hold, test master creation, SQL write, DEVELOPMENT/Integration2 or PRODUCTION operation was performed.
