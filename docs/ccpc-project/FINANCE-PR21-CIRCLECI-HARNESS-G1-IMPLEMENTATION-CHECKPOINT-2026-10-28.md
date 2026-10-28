# Finance PR21 — G1 separate CircleCI harness implementation checkpoint

**Date:** 2026-10-28 (Asia/Manila). **Status:** GitHub CODE COMMITTED / SOURCE REVIEWED; no new static Python or runtime test executed at latest feature HEAD. **Authority:** Owner explicitly approved implementation of the dedicated CircleCI Finance test harness and its security tests **in GitHub**, with **no pipeline, migration, DEVELOPMENT/Integration2 or PRODUCTION changes**. This document does not authorize executing any CI job, setting CI project secrets/variables, real financial approval or merging PR #21.

Read [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), [G0 feature-harness review](FINANCE-PR21-CIRCLECI-FEATURE-HARNESS-G0-SAFETY-REVIEW-2026-10-28.md), [isolated MariaDB test plan](FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md), [Finance role/evidence decision](FINANCE-MAPPING-ACCOUNTING-AUTHORITY-DECISION-2026-10-28.md), and [Integration2 handoff](INTEGRATION2-FINANCE-AUTHENTICATION-CHECKPOINT-2026-10-27.md).

## 1. Exact GitHub state and changes

At final code review, [ccpcerp/ccpcerp draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) remained **OPEN / DRAFT / UNMERGED**, from `feature/finance-mapping-lifecycle-2026-10-28` at verified HEAD **`375de12e7bf79210fdb7ec54b6e7184d0b27ead6`**, into `review/circleci-isolated-erpnext-phase2-2026-10-26` at `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. Original Finance source static result **24/24 Python PASS** belongs to earlier app commit `76973699a085d3eb4efd6412d21a773ec1499e19`; it does NOT verify this newly amended HEAD.

**Authorized G1 app commits:**
- `1d814b0` — new independent `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py`, requiring exact CircleCI organization, repository, feature branch, distinct CI job, disposable site, build IDs, 40-char checkout SHA matched to separately authorized SHA and isolated-only flag.
- `b77b968` — six pure-stdlib negative/positive guard tests under `.circleci/test_finance_lifecycle_ci_guard.py`.
- `1281689` — adds `run_finance_lifecycle` parameter **default false**, independent manually approved `finance-lifecycle-isolated-integration` job and new disposable MariaDB/Redis/Frappe site to `.circleci/config.yml`. Original job/guard and original workflows retained; no new schedule, PR-label trigger or automatic expensive workflow. Job is further blocked by absent externally administered `CCPC_FINANCE_APPROVED_SHA`.
- `259b2ae` — four static YAML-policy negative/assertion tests `.circleci/test_finance_ci_config_static.py`.
- `aa0b3ac` — new `ccpcerp/ccpc_erp/test_finance_lifecycle_disposable_integration.py`, Frappe/MariaDB-only synthetic Finance lifecycle service tests under site guard.
- `a725727` — fix Frappe `frappe.db.table_exists` check to receive DocType name.
- `9aa4a7e` — add Center mapping, effective retirement cutoff and rejection rollback probe coverage (8 total database test methods).
- `375de12` — explicitly deny `None` site in CI guard negative suite.

**Exact source version pins checked in GitHub:** Frappe `988e54f3c4c291e2077a83809663f123731abe76` (v16.33.1), ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` (v16.34.2). These are *candidate test pins*, not proof a bench builds successfully. Existing CircleCI test job uses floating v16 branches; the new job fetches and checks out these exact commits before its disposable site is built.

## 2. Identity and isolation invariants

- Only CircleCI feature branch `feature/finance-mapping-lifecycle-2026-10-28`, job `finance-lifecycle-isolated-integration`, site `ci-finance-lifecycle.localhost`, recognized repo/org, nonempty pipeline/workflow/build IDs, allowed flag, and SHA equal to a **separately administered and owner-approved** `CCPC_FINANCE_APPROVED_SHA` pass the new Python guard. CI shell independently checks actual Git checkout HEAD == CircleCI SHA. A pending manual CircleCI approval job is a second guard; it does not itself confer Accounting signatory authority.
- The original `ci_disposable_site_guard.py` file was re-read at identical blob `e20c7822186729bd793e3934a9af46f57c38742b`; original `.circleci/config.yml` job text and workflows were compared and remain unchanged (the new job follows a blank separator). Old synthetic Approved-looking fixture and legacy Withdrawal/Intercompany tests are **not** run in the new job. A new guard does **not** authorize existing fixture bypasses.
- The new guarded database test suite has **eight** direct Frappe service/migration candidates: DocType installation, Expense draft rejection, signed approval/unique use, signing audit rollback, retirement request replay/decline/accept, prospective cutoff, denied Guest/Admin/Maker, Center approval and rejection audit rollback. These execute **real MariaDB** only *if an authorized future CircleCI job is run*; they are NOT actual authenticated HTTP/CSRF, independent-connection race/deadlock, or stock/GL posting tests. Do not describe them as such.
- The new CircleCI job creates its own bench and site on an ephemeral CI runner, without mounting CCPC DEV/PROD site configs, credentials, NAS shares, host Docker socket or production network connections in the reviewed source. **This is an intended boundary, not independent attestation of runner/network isolation.** Inspect runner contexts, project settings, IP routing and capacity before run. Code uses publicly visible disposable-only SQL/admin passwords within ephemeral sidecars; never substitute real credentials.
- A source SHA in an environment variable is not a cryptographic signature; the owner must separately confirm that its value is set only through a trusted CircleCI project-level control and corresponds to the exact GitHub review commit. Do not put it in untrusted pipeline parameters or the app source. Recheck after any code change; old approvals do not automatically authorize a new HEAD.

## 3. Source review vs executed test evidence

**Verified by connected GitHub reads and comparison:** PR base/head and open draft status, unique feature commits, code files and 30 changed paths, original CI job command text unchanged, original guard byte-identical, opt-in Finance job default false + manual dependency + SHA gate, distinct site, new guard negative tests (6), config tests (4), disposable Frappe/MariaDB module (8). Corrected Frappe API use after consulting pinned upstream source. Updated PR #21 body with these facts. These are **static code/review findings**, not executed tests.

**NOT yet verified:** Python syntax/AST/stdlib tests of the new files; CircleCI config compilation with approved parser; exact CircleCI branch-parameter/manual-approval behavior; Frappe v16/ERPNext v16 installation; v16 DocType validation; transaction results/Version rollbacks, Center/Expense approval and retirement; real HTTP/CSRF, stock/GL/SLE integration, concurrent workers, old approval migration/CI fixture compatibility, runner isolation or network boundaries. No CircleCI pipeline was intentionally started under this authorization. The new CI job is NOT an approved test run.

**Potential failure/release gate:** New database test module directly invokes Frappe workflow services after `frappe.set_user`; it tests real role/Company/SQL behavior if run, but is not a substitute for actual authenticated HTTP session+CSRF checks. It may expose implementation defects or schema mismatch. On any failure: STOP, preserve sanitized CI logs, correct GitHub source, repeat static review, and ask permission again for any new paid run. Do not weaken guards or bypass failing tests to get green.

## 4. Recommended next steps, all separate authorizations

**G1.1 — safe offline static verification:** Owner may approve a temporary, separate source checkout (outside live DEVELOPMENT worktree) to run Python compileall, original 24 static tests and the **10 new guard/config tests**, plus a no-execution YAML parser/check. Check exact SHA and no modifications to existing bench. Record results in PR/handoff.

**G2 — exact opt-in CI execution:** After passing G1.1 and independent review of current PR21 diff, owner must separately approve a **specific**, potentially paid Finance CircleCI run, exact new HEAD, approved project-variable SHA, actual runner/site isolation, resource class/time/cost, job approval, and allowed synthetic database actions. No real Accounting signature or live Company mapping is authorized. Explicitly disallow any real site. Any new code HEAD requires fresh reapproval.

**G3 — further test coverage and DEVELOPMENT adoption:** Actual HTTPS/CSRF and concurrent real DB connection/stock-GL test development and execution require further bounded approval. Persistent DEVELOPMENT checkout/migration must separately protect untracked work, databases, snapshots and shared infrastructure. No current approval for pulling or migrating `development.localhost` or `ccpc-integration2.localhost`.

**G4 — PRODUCTION:** Explicit separate approval, real Accounting signatories and business crosswalk, backup restoration/rollback evidence and production release gates. Never infer PRODUCTION readiness from green disposable CI.

**Preserved Integration2 state:** Last independently verified TISS Expense Scope `fie8da5c59`, Revision `fieef2e44j` remains **Draft**; no activation or financial posting. No CircleCI pipeline run, database migration or DEVELOPMENT/PRODUCTION operation occurred during G1 code authoring.
