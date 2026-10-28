# CCPC Finance — PR #22 isolated HTTP/CSRF and Company-lock probe source review

**Date:** 2026-10-28 (Asia/Manila).  
**Authority:** Owner replied **"Approved"** to GitHub-first preparation of targeted authenticated HTTP/CSRF and concurrency test code for Finance PR #21, with review and separately authorized execution. This is authorization to **develop and review source in GitHub**, not an approval to execute a paid CircleCI job, provision credentials or users, modify DEVELOPMENT/Integration2, migrate a persistent site, merge into the Finance feature or deploy to PRODUCTION.

## Current source and review isolation

- Finance application [draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) remained OPEN/DRAFT at original exact HEAD `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.
- Created a separate application review branch `review/finance-http-concurrency-tests-2026-10-28` from that exact SHA and [draft PR #22](https://github.com/ccpcerp/ccpcerp/pull/22), targeting `feature/finance-mapping-lifecycle-2026-10-28`.
- Final verified PR #22 HEAD **`e1cfd3e63cfcac54a6b4b16ebdeb1be8212bf15d`**, five commits ahead / zero behind the Finance feature starting commit, exactly **three added files** and no changed existing source/config files. It has **NOT been merged** into PR #21 or any default branch.
- Code files added:
  - `.circleci/finance_http_session_probe.py` — a **manual** loopback-only HTTP probe, guarded by exact disposable CircleCI site/org/branch/job, approved SHA, independent opt-in flag, strict hostname resolution, disabled proxy and redirect refusal. Requires an explicitly provisioned fictional checker and a running local isolated Frappe web process. Logs in via a cookie session and verifies exact user identity, GET rejection on POST-only review endpoint, and CSRF rejection on an authenticated POST **to a read-only review method with a nonexistent revision**. It deliberately does not call mapping approval, issue, invoice or stock/GL posting endpoints; session login itself can create ephemeral session state.
  - `ccpcerp/ccpc_erp/ci_finance_company_lock_probe.py` — **manual** two-connection MariaDB `SELECT ... FOR UPDATE` / `NOWAIT` Company-lock contention probe against an **already committed** fictional `_Test Company`, with strict disposable-site/CI identity and SHA checks, independent opt-in flag, no mapping/financial writes and `rollback()` in cleanup for both DB connections. Demonstrates a database locking primitive only, **not simultaneous business approval or retirement idempotency**.
  - `.circleci/test_finance_probe_source_policy.py` — pure stdlib AST/source-policy checks to be run separately offline. The active CircleCI `.circleci/config.yml` was **not edited**; neither probe is auto-wired into a pipeline.

**Credential safety:** No actual user password, real account identity, session cookie, GitHub token, private SSH material, business record or production data was committed. The HTTP probe requires a **synthetic disposable-only** password supplied only during a separately approved run. Both source probes restrict their Git SHA verification subprocess to a PATH-only environment to avoid passing session-password environment variables to git.

## What was and was not verified

- **Verified from connected GitHub:** Exact app feature baseline and PR #22 head, branch comparison (5 ahead, 0 behind; three new files), the three new blobs, untouched `.circleci/config.yml`, and PR #22 OPEN/DRAFT/UNMERGED.
- **Read-only lightweight source checks:** 17/17 JavaScript-driven source-policy string/relationship checks passed against final GitHub files (preflight-before-use ordering, opt-in, SHA, loopback/proxy/redirect restrictions, checker identity, GET/CSRF expectations, second DB connection and NOWAIT, rollback, and absent auto-wiring).
- **NOT executed:** The newly added Python unittest source-policy module, Python `compileall` on the final review HEAD, the actual Frappe v16 HTTP server, authenticated login, CSRF response, second-connection MariaDB test, any simultaneous approval/retirement endpoints, CircleCI pipeline or persistent DEVELOPMENT integration.
- Existing separately documented G1.2 **34/34 PASS** and CircleCI CLI validation belong to the earlier **Finance PR #21 SHA `d154886`**, **not** to PR #22 and not to these new probes.

## Next safe offline validation

Only after independently establishing a **clean, isolated complete temporary checkout** at PR #22 HEAD `e1cfd3e63cfcac54a6b4b16ebdeb1be8212bf15d` (NOT a live bench / production repository), run read-only/offline commands:

```bash
git rev-parse HEAD
python3 -m compileall -q .circleci/finance_http_session_probe.py \
  .circleci/test_finance_probe_source_policy.py \
  ccpcerp/ccpc_erp/ci_finance_company_lock_probe.py
python3 -m unittest discover -s .circleci -p 'test_finance_probe_source_policy.py' -v
```

Record exact checkout SHA, Python version, output and failures. These commands **do not** import Frappe or start a job/site. A PASS would establish Python syntax and static policy only.

## Further gates — separate owner approval

Actual HTTP and MariaDB execution remains blocked until the owner separately approves a **specific exact review SHA**, the ephemeral CircleCI job and budget, attested cloud runner/network isolation, safe local HTTP listener, fictional checker credential provisioning without logs, committed fictional Company test fixture, rollback/disposal and a human cancellation operator. The approved SHA project variable was absent in the prior CircleCI UI inventory and must not be created without separate authorization. `run_finance_lifecycle` remains default false.

**Open test gaps after these probes:** successful CSRF-bearing authenticated checker POST and maker-vs-checker HTTP scope enforcement; two independent concurrent **business approval/retirement** requests with exact decision-use, stale-state/duplicate protection and rollback assertions; stock/GL/SLE tests; DEVELOPMENT acceptance. These cannot be reported as passed based on a row-lock probe. Do not run probes on `development.localhost`, `ccpc-integration2.localhost` or PRODUCTION. No service restart, migration, source merge, user creation or financial posting authorized by this code checkpoint.


## Offline exact-blob syntax and Python source-policy validation — 2026-10-28

**Approval:** Owner replied **"Approved"** to the prior checkpoint's *offline-only Python syntax and source-policy tests* on the PR #22 review code. This approval did **not** extend to running the manually gated HTTP/CSRF or database probes, CircleCI jobs, changing credentials, merging the PR, or accessing persistent DEVELOPMENT/PRODUCTION.

**Source provenance and snapshot fidelity:** The execution environment cannot resolve/clone the private GitHub repository (attempted unauthenticated `git ls-remote` returned `Could not resolve host: github.com`), so the assistant assembled **only the four exact relevant files** into a separate throwaway local directory; this was **not a full Git checkout**, and no source files were fetched by unauthenticated direct web access. Connected GitHub `fetch_file` and the previously verified exact PR head supplied authoritative file contents. Git blob SHA-1 recomputation over `blob <size>\\0<bytes>` independently matched **all 4 GitHub blobs**:

| File | Matched exact Git blob |
| --- | --- |
| `.circleci/finance_http_session_probe.py` | `fb2d6b8bea90fd6989d293b58d3117f64b51a5e0` |
| `ccpcerp/ccpc_erp/ci_finance_company_lock_probe.py` | `9c890ac5245af7fa837e422d37d09d99593d2705` |
| `.circleci/test_finance_probe_source_policy.py` | `013926bb6ab44664ce3992efacce2d1feda1c1a6` |
| `.circleci/config.yml` (unchanged PR #21 baseline) | `9aa8c676dfa7b22e7b7035d70a0b461af773908d` |

**Executed command category (Python 3.13.5):** `python3 -m compileall -q` on the **three PR22 Python files**, and `python3 -m unittest discover -s .circleci -p 'test_finance_probe_source_policy.py' -v` within the exact-blob snapshot.

**Results:** All three Python files compiled successfully, exit status 0; **four Python unittest methods ran, 4 PASS, zero failures/errors, 0.002s**:
- `test_both_probes_parse_without_importing_frappe`
- `test_http_probe_requires_isolated_identity_and_cookie_csrf`
- `test_lock_probe_requires_distinct_transactions_and_rollback`
- `test_neither_probe_is_wired_to_active_circleci_jobs`

This source-policy PASS is **not** a CircleCI config compiler pass at the review SHA, a full repo test-suite run or any Frappe/MariaDB runtime test. Python 3.13.5 was used locally; CI's declared Python image is 3.14. The exact final PR22 HEAD remains `e1cfd3e63cfcac54a6b4b16ebdeb1be8212bf15d`, OPEN/DRAFT/UNMERGED. **No application/CI source changes were made by this validation.**

**Remaining validation and safety gates:** The manual probes are **not wired to CI**. A later disposable synthetic checker login/CSRF assessment and MariaDB NOWAIT lock check require separately approved exact-SHA isolated runtime prerequisites, credential handling, budget/cancel oversight, and explicit authorization. Two-request Finance approval/retirement race tests and authenticated positive CSRF paths still need design and implementation. The G2 Finance paid job remains **NO-GO**; DEVELOPMENT/Integration2/PRODUCTION untouched.


## Pinned Frappe HTTP semantics and real Finance business-race probe — 2026-10-28

**Approval scope:** Owner explicitly approved reviewing the pinned Frappe v16 HTTP/CSRF implementation and extending Finance concurrency coverage from a Company row lock to actual Finance approval and retirement methods. This authorizes **source-only changes in GitHub** on PR #22, **not** CI or MariaDB execution, test fixture/credential creation, merging, migrations, DEVELOPMENT work or PRODUCTION deployment.

**Authoritative upstream review:** The pinned Frappe commit `988e54f3c4c291e2077a83809663f123731abe76` provides:
- `frappe/handler.py` `is_valid_http_method()` checks `frappe.allowed_http_methods_for_whitelisted_func` and calls `frappe.throw_permission_error()` for GET against a POST-only endpoint; Frappe `PermissionError.http_status_code = 403`. The previous manual HTTP probe incorrectly expected 405; corrected to **403**.
- `frappe/auth.py` `HTTPRequest.validate_csrf_token()` checks unsafe HTTP methods, site `ignore_csrf`, saved session token, `X-Frappe-CSRF-Token`/form token and allowed referrer/origin. It raises `CSRFTokenError.http_status_code = 400` if guard fails. Previous manual HTTP probe incorrectly expected 403; corrected to **400**.
- `frappe/sessions.py` `Session.start()` does not itself visibly initialize a CSRF token. The manual HTTP probe now visits the **synthetic `/app` Desk boot** after confirming an exact fictional checker cookie login and before submitting an unprotected POST. This is a **source-level attempt** to ensure a CSRF-bearing session, not a live proof that Desk boot set the token. A later runtime test must verify actual session token initialization, exception type and site `ignore_csrf` settings before treating an HTTP 400 as a definitive positive CSRF security result. An authenticated successful CSRF-token-bearing Finance HTTP request is still not implemented.
- The Finance code under review declares `@frappe.whitelist(methods=["POST"])` on its server methods. No live HTTP requests were made.

**New dormant manual concurrency probe:** `ccpcerp/ccpc_erp/ci_finance_business_race_probe.py` adds `verify_finance_business_race(action, target, expected_modified, decision_id)`, limited to `action="Approve"` or `action="Retire"`. It requires exact disposable Finance site/org/repo/branch/job/SHA guard and a separate `CCPC_ALLOW_FINANCE_RACE_PROBE=isolated-only` opt-in, test-only Company `_Test Company`, a synthetic Checker, exact committed revision/request, signed and unconsumed Accounting decision, then starts **two separate thread-local Frappe/MariaDB connections** with a barrier. Each invokes real `approve_mapping` or `decide_mapping_retirement`, committing on success or rolling back on business rejection. Assertions require exactly **one successful commit, one business denial, one Decision Use**, and for retirement exactly one cutoff event while the original Approved revision remains historically unchanged. A lock timeout, unexpected exception, broken barrier, duplicate success or missing audit fact is **not** accepted as a passing result. The function intentionally commits synthetic changes only if separately run against a verified ephemeral site; do not run on any persistent site.

**Constraints and gap boundary:** No setup fixtures were generated or committed by this milestone. Existing eight direct Finance test methods generate fixtures in rolled-back test transactions, so this new concurrent worker test requires a separately reviewed procedure to create and **commit fictional fixtures in the disposable CI site** before launch. CI config on PR22 remains exact GitHub blob `9aa8c676dfa7b22e7b7035d70a0b461af773908d`; the new probe is **not wired to a workflow or scheduled job**. Its source-level identity guard currently expects the Finance feature branch, while PR22 is a distinct review branch, so a separately reviewed merge and then a new approved SHA would be required before any execution. No source change here is approved for persistent DEVELOPMENT or PRODUCTION.

**GitHub verified source:** Draft app [PR #22](https://github.com/ccpcerp/ccpcerp/pull/22) now at **`e842aa62cb42531752299503206e6eb1cba395d0`**, compares exactly **four added files**, ten commits ahead and zero behind Finance feature baseline `d154886ab45c51878a87a4ecf42e45602d8d9ccb`, draft/unmerged. The updated `.circleci/test_finance_probe_source_policy.py` includes a fifth pure-stdlib source test for real business method concurrency, and tightened HTTP response assertions. **22/22 independent read-only GitHub source-policy inspection checks PASS**, not Python AST/compile execution, not actual HTTP, MariaDB or CI. The previously executed **4/4 Python source tests** applied only to the earlier PR22 head `e1cfd3e`, **not** the current files. No credentials, application secrets or production data were committed.

**Next safe step:** In a clean isolated temporary checkout of the **current PR22 SHA**, run `compileall` and `python3 -m unittest discover -s .circleci -p 'test_finance_probe_source_policy.py' -v`; source-only validation does not require MariaDB/CircleCI. Separately review the executor and synthetic fixture setup plus positive CSRF and full two-request concurrency semantics before considering exact-SHA CI execution; **G2 remains NO-GO** and paid jobs/hold approvals/variables/network/credits require separate user approval.


## Exact-blob offline Python validation at expanded PR #22 head — PASS (2026-10-28)

**User approval:** The owner explicitly approved **offline Python syntax and source-policy tests** at `e842aa62cb42531752299503206e6eb1cba395d0`. No hosted CircleCI pipeline, MariaDB, HTTP server, credentials or DEVELOPMENT/PRODUCTION operation was approved.

**Provenance and limits:** A prior temporary exact-file snapshot existed locally for the old PR22 SHA. Because the private GitHub repo cannot be cloned from this runtime (`Could not resolve host: github.com`), the assistant reconstructed the changed/new source from the connected GitHub read results into a **separate** directory `/mnt/data/ccpc_pr22_e842aa6_offline_snapshot` and verified canonical Git blob SHA-1 across **all five** source inputs for the **current PR22 head**. This is a pinned-source **exact-file offline snapshot**, not a complete repository clone. GitHub branch/PR head was independently reverified as OPEN/DRAFT, exact SHA `e842aa62cb42531752299503206e6eb1cba395d0`.

| Source at PR #22 head | Exact matched Git blob |
|---|---|
| `.circleci/finance_http_session_probe.py` | `f93e81cb01c19ce4e97671a7417ebc9352a0e780` |
| `.circleci/test_finance_probe_source_policy.py` | `b817b767ab82ac21f737ae8097b84056cc50bc4a` |
| `ccpcerp/ccpc_erp/ci_finance_company_lock_probe.py` | `9c890ac5245af7fa837e422d37d09d99593d2705` |
| `ccpcerp/ccpc_erp/ci_finance_business_race_probe.py` | `5555d0a64ed491f76ef68a96b192ba93e5300404` |
| `.circleci/config.yml` (unchanged Finance baseline) | `9aa8c676dfa7b22e7b7035d70a0b461af773908d` |

**Executed with Python 3.13.5:** `python3 -m compileall -q` on the **four PR22 Python files**: **PASS** (exit 0); `python3 -m unittest discover -s .circleci -p 'test_finance_probe_source_policy.py' -v`: **5 tests run, all PASS, 0 errors/failures, 0.004s**. This adds one source-policy test to the previously executed 4/4 snapshot for the older PR22 head.

**Tests performed:** AST parse of three manual probes; static assertions covering isolated HTTP cookie/CSRF and pinned Frappe HTTP status expectations (GET method disallow: 403; missing CSRF when enforced: 400); two-DB-connection lock and rollback; new business-method two-worker concurrency guard and one-use/one-retirement-event source checks; and absence of automatic CircleCI pipeline wiring. These are only **source contracts**. They do **not** test actual Frappe HTTP response codes, session CSRF generation, MariaDB lock behavior, concurrent approval/retirement persistence, live integration, or ERPNext accounting/stock ledger correctness.

**Prior CircleCI work distinguished:** Earlier Finance PR21 checkpoint documented operator-executed **CircleCI CLI 1.11.0** `config validate` (default) and `config process ... run_finance_lifecycle: true` **PASS** at Finance baseline `d154886`, plus **34/34 Python offline static tests PASS**. These **local CLI/config and Python runs are not proof that the paid CircleCI Cloud MariaDB Finance job ran**. G2 review still records NO-GO for launching that job; no ChatGPT CircleCI API authenticated session or current hosted result is independently available.

**Next gate:** Review the exact changes as a draft PR and identify safe fixture setup for actual HTTP session/CSRF and concurrent Finance approval/retirement integration. Keep **G2 Finance MariaDB CI execution NO-GO** pending separate exact-sha owner authorization and cost, runner, secret and DEV/PROD network boundaries. No merge or operational changes occurred in this offline validation.
