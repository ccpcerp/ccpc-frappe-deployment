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
