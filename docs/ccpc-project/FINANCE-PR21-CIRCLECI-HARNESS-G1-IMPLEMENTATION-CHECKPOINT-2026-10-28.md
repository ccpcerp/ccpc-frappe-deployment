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

## 5. Owner-approved G1.1 offline verification — 10/10 NEW TESTS PASS (2026-10-28)

Owner approved the proposed **G1.1 offline static-test step** only. Current app source branch/PR head independently rechecked in GitHub: `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`, PR #21 OPEN/DRAFT/UNMERGED, base `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. The assistant attempted an isolated Git clone, but this local container had no GitHub DNS access (`Could not resolve host: github.com`). It used the **connected GitHub connector** to fetch the current files and reconstructed them in an independent `/tmp/ccpc-offline-static-...` workspace. `git hash-object` verified **all five** local files exactly matched these GitHub blobs before use:

| Exact file | Verified Git blob |
| --- | --- |
| `.circleci/config.yml` | `0f23d7ce0f1a1e94cad0debbee865ac813ed1509` |
| `.circleci/test_finance_lifecycle_ci_guard.py` | `8913fe6d914e9f5367640c664b2c8bc5a4e69ae4` |
| `.circleci/test_finance_ci_config_static.py` | `4295b8eb8761ff0a7f227e1f7ad76503488bd109` |
| `ccpcerp/ccpc_erp/ci_finance_lifecycle_site_guard.py` | `87e1f98308d6f2094ab6a45458dcd9cb6e6e5513` |
| `ccpcerp/ccpc_erp/ci_disposable_site_guard.py` | `e20c7822186729bd793e3934a9af46f57c38742b` |

**Executed results (not merely structural review):**
- `python3 -m unittest discover -s .circleci -p 'test_finance_lifecycle_ci_guard.py' -v`: **6/6 PASS**, no errors/failures.
- `python3 -m unittest discover -s .circleci -p 'test_finance_ci_config_static.py' -v`: **4/4 PASS**, no errors/failures.
- `python3 -m compileall -q` for the four exact Python files above: **PASS**.
- `PyYAML 6.0.3 yaml.safe_load` of GitHub-blob-verified CircleCI config: **PASS**, with explicit checks that original and Finance expensive pipeline parameters default **false**, and Finance integration requires its manual approval job. **Not** a CircleCI CLI config-compiler pass.

**Prior 24/24 Finance Python static tests:** The owner ran them at original feature commit `76973699...` and supplied full `OK` output. Fresh GitHub two-ref blob comparison verified the three original test files and seven relevant app service/policy/revision schema files are byte-identical at current feature commit `375de12...`. Those 24 tests were **NOT re-executed** at the new HEAD; evidence is carried forward only as unchanged code/test provenance, not claimed as a fresh full suite.

**G1.1 scope limitation:** This was a verified **subset of source**, not a full repo clone; full `compileall` and re-running the previous 24 tests at the latest head remain pending. No CircleCI CLI config validation, no CircleCI run, no schema migration, no Frappe v16/MariaDB service test, no HTTP/CSRF/concurrency/ledger test, no DEVELOPMENT/Integration2/PRODUCTION access or financial write. The current CI runner identity and external `CCPC_FINANCE_APPROVED_SHA` are *not* authorized/configured by this step.

**Next recommended isolated source check:** Use a safe complete temporary clone on the owner's Ubuntu host (preserve the original DEVELOPMENT checkout) to run full Python `compileall`, the original 24 static tests, the new 10 tests, and CircleCI CLI config validation if available. Post results for GitHub review. A **separate owner-authorized G2 run** with trusted SHA setting, CI runner/cost and permitted disposable DB actions remains mandatory; no pipeline is authorized now. PR #21 remains DRAFT.

## 6. Operator-executed full G1.1 source verification — 34/34 PASS (2026-10-28)

After the earlier **10/10 local subset** static tests and byte-verified CircleCI YAML parse, the project owner executed the previously supplied *full* temporary-checkout test script on Ubuntu and pasted test-by-test output. The provided command uses `set -euo pipefail`, a fresh `mktemp -d /tmp/ccpc-finance-g11-...` clone, and an exact preflight `git rev-parse HEAD == 375de12e7bf79210fdb7ec54b6e7184d0b27ead6`. Because the final marker `G1.1 FULL STATIC VERIFICATION COMPLETED` appeared, the command's `python3 -m compileall -q ccpcerp .circleci` passed before all five test suites.

| Python suite | Operator-reported test count | Outcome |
| --- | ---: | --- |
| `test_bc_finance_governance_static.py` | 6 | OK, 0.007s |
| `test_ccpc_mapping_schema_static.py` | 3 | OK, 0.003s |
| `test_bc_mapping_policy_static.py` | 15 | OK, 0.000s |
| `test_finance_lifecycle_ci_guard.py` | 6 | OK, 0.005s |
| `test_finance_ci_config_static.py` | 4 | OK, 0.000s |
| **Total** | **34** | **PASS, 0 failures, 0 errors** |

**Evidence provenance:** This is an owner-supplied Ubuntu terminal transcript, not a test run initiated by ChatGPT or GitHub Actions/CircleCI. The exact SHA preflight is part of the previously supplied script; terminal output shows the final marker. Verified PR #21 HEAD remains `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`; GitHub PR description updated with matching result. The tests validate static schema/policy and CI guard/config source, **not Frappe v16/MariaDB runtime**.

**Status change:** Previous §5 pending full `compileall` and reexecution of 24 baseline static tests **now satisfied** at current feature SHA, based on the owner-run command. **Still pending**: CircleCI CLI *semantic* configuration validation (not satisfied by prior PyYAML parser check), runner network/identity/cost assessment, separate explicit **G2** approval to configure trusted `CCPC_FINANCE_APPROVED_SHA` and opt-in to a specific disposable CI run, full Frappe/ERPNext/MariaDB integration and concurrency/rollback testing. PR #21 stays DRAFT and unmerged. Existing Integration2 TISS Expense revision `fieef2e44j` last verified Draft; no known DEV/PROD action from these static commands.

## 7. G1.2 CLI availability and runner cost review — 2026-10-28

The owner authorized read-only CircleCI configuration validation and cost/isolation review after the **34/34 PASS** G1.1 static milestone. See the [G1.2 CircleCI configuration, runner isolation and cost review](FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md), created/verified at GitHub commit `a0b9066887756da2b70ef288e8d1023e97e9c2db`. Source feature PR #21 remains draft at `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`.

**Explicit outcome:** CircleCI CLI was **not available** in the isolated assistant container (`command -v circleci` returned nothing; outbound DNS to CircleCI failed). Therefore **`circleci config validate` NOT RUN / CLI status PENDING**. Previously executed Python static 34/34 and PyYAML parsing remain valid but do not prove CircleCI configuration compilation. Official CircleCI CLI documents `circleci config validate .circleci/config.yml --json`; safe exact-SHA temp-clone command and warnings are in the G1.2 review. No pipeline was triggered.

**Runner/cost:** New Finance job is default-off with a separate human approval, an externally administered SHA gate, Docker `resource_class: large`, primary Python plus MariaDB/Redis sidecars and a disposable Finance site. Project CI settings, real network isolation, who can approve the hold and available credits **not independently checked**. CircleCI official 2026-10-08 price list shows standard x86 Docker large **20 credits/min** (4 CPU, 8 GB), excluding extras. `no_output_timeout: 20m` is a *no-output* limit, not a per-job ceiling. Plan-level maximum job durations can be 1/3/5h depending on account plan; approved spend/cancellation limit is mandatory before G2.

**Gate retained:** **NO-GO for paid CircleCI execution** until CircleCI CLI result, trusted current runner/settings read-only audit, exact signed-off SHA, separate owner budget/permission and G2 approval. No setting/CI app code, database, DEVELOPMENT/Integration2 or PRODUCTION change occurred under G1.2.
