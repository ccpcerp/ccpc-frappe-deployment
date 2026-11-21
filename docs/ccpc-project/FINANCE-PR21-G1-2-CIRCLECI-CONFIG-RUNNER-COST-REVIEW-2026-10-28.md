# CCPC Finance PR #21 — G1.2 CircleCI configuration, runner isolation and cost review

**Date:** 2026-10-28 (Asia/Manila)  
**Authority:** Owner answered **"Approved"** to the next task offered after G1.1 full offline static validation: CircleCI CLI configuration validation, then runner-isolation/resource-cost review. Interpreted as **review and read-only/offline validation only**, NOT approval to run a CircleCI pipeline, create/migrate a Frappe site, approve a hold job, change CircleCI secrets/project settings, merge code, pull DEVELOPMENT or deploy PRODUCTION.  
**Result:** **SOURCE / POLICY REVIEW COMPLETED; CircleCI CLI VALIDATION BLOCKED BY LOCAL TOOL AVAILABILITY. G2 NO-GO.**

## 1. GitHub source of truth

- [GitHub-first project workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Finance G1 implementation checkpoint](FINANCE-PR21-CIRCLECI-HARNESS-G1-IMPLEMENTATION-CHECKPOINT-2026-10-28.md)
- [G0 CI isolation review](FINANCE-PR21-CIRCLECI-FEATURE-HARNESS-G0-SAFETY-REVIEW-2026-10-28.md)
- [Finance isolated database test plan](FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md)
- [Draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) remains OPEN / DRAFT / UNMERGED. Feature branch `feature/finance-mapping-lifecycle-2026-10-28` exact HEAD **`375de12e7bf79210fdb7ec54b6e7184d0b27ead6`**, PR base `review/circleci-isolated-erpnext-phase2-2026-10-26` at **`0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`**.
- GitHub's exact `.circleci/config.yml` blob **`0f23d7ce0f1a1e94cad0debbee865ac813ed1509`** was re-read. This documentation-only review did not alter app code, CI YAML, environment or branch.
- Owner-executed Ubuntu full source `compileall` and **34/34** Python static/security/config tests **PASS** at this exact feature HEAD. Prior assistant-run PyYAML 6.0.3 parsed the same blob and confirmed both expensive integration parameters default false plus the Finance manual-approval dependency. Neither is CircleCI CLI compilation or ERPNext/MariaDB integration.

## 2. CircleCI CLI verification status and reproducible safe check

**Attempted availability on isolated assistant container:** `command -v circleci` returned no CLI; `curl -I --max-time 7 https://circleci.com` failed with `Could not resolve host: circleci.com`. Installing CLI from the internet or invoking CircleCI's config-validation service from this container was not possible. **No `circleci config validate` command was executed; do not call the configuration CircleCI-CLI-validated.**

CircleCI CLI official reference (read 2026-10-28): https://cli.circleci.com/reference/ confirms **`circleci config validate [path] --json`** and `circleci config process <path>`; the CLI can validate configs without an API token for configs not relying on private orbs. **Config validation and expansion do not start a pipeline.** An exact-SHA checked temporary complete source checkout with trusted already-installed CLI can run:

```bash
set -euo pipefail
cd "$ISOLATED_REVIEW_CHECKOUT"  # independently created temp source clone; NOT any ERPNext bench
test "$(git rev-parse HEAD)" = "375de12e7bf79210fdb7ec54b6e7184d0b27ead6"
command -v circleci >/dev/null || { echo "CLI absent: STOP, do not install on production host"; exit 1; }
circleci --version
circleci config validate .circleci/config.yml --json
```

**Operator preflight:** The directory must be a disposable temporary clone of **ccpcerp/ccpcerp**, not a live DEVELOPMENT/PRODUCTION checkout, and `circleci` must already be a trusted installed executable. Do not run `circleci auth login`, `circleci project link`, `circleci pipeline trigger`, `circleci run`, or any hold-approval action under G1.2. Do not attempt an unreviewed `curl | sudo` installation on ccpcerpserver. A PASS output would verify only the reported CLI parser/config compiler, **not** Docker images/bench compatibility or the runtime authorization, and must be recorded verbatim along with `circleci --version` and source SHA. Check whether CLI requires outbound configuration-service access; failure to reach it is not proof YAML is valid/invalid.

## 3. Source-defined runner, isolation and permission review

| Item | Verified config/source fact | Assessment / required evidence before G2 |
| --- | --- | --- |
| Trigger | `run_finance_lifecycle` Boolean pipeline parameter defaults **false**. Original `run_integration` remains default false. | Good source gate. **Not proof** of project trigger configuration; review live CircleCI trigger/settings without changing them. |
| Approval | The Finance workflow has `finance-lifecycle-manual-approval` `type: approval` and the expensive Finance job `requires` it. Both jobs filtered to exact feature branch. | Confirm who has push access and can approve. Per CircleCI docs, push-access repo users may approve a hold job; this is **not exclusively owner signoff**. Explicit CCPC owner approval for G2 remains mandatory. |
| Commit attestation | Source requires `CIRCLE_SHA1 == git rev-parse HEAD == CCPC_FINANCE_APPROVED_SHA` plus org/repo/branch/job/site identities. | Good fail-closed check. Project setting `CCPC_FINANCE_APPROVED_SHA` absent/unverified by this review, **must not be configured without G2 authorization**. Confirm trusted administrative provenance of variable. |
| Execution class | CircleCI Cloud Docker, primary image `cimg/python:3.14-node`; MariaDB 11.8 and two Redis 7-alpine service containers; `resource_class: large`. | Expected isolated container networking and localhost sidecars by CircleCI Docker docs, **not independently attested** access to DEV/PROD networks, contexts, runner types or variables. Must verify project settings and network restrictions before any run. |
| Volumes and credentials | New job source declares no named CCPC DEV/PROD volume, no SSH-key injection, no `context:` and no `docker.sock` mount. Hard-coded credentials are test-only sidecar values. | No visible direct production credential/mount in YAML. However project-level env vars, injected checkout keys/contexts, policy settings, outbound routing and secret redaction are **unknown**; demand a reviewed project-settings inventory. |
| Site | `TEST_SITE=ci-finance-lifecycle.localhost`, independently guarded Finance site, `bench new-site` and migrate in the job. | Intended disposable site; never reuse live `development.localhost`/`ccpc-integration2.localhost`. Real site/DB identity must be logged and independently checked **before** test writes. |
| Dependencies | Pin Frappe commit `988e54f3c4c291e2077a83809663f123731abe76` and ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` after initial v16 branch installation. | Source pins verified, but image availability, Python 3.14 compatibility, Frappe bench setup, app installation and CLI semantic compilation **not tested**. A failed first run must STOP rather than weaken guard. |
| Test scope | `bench ... run-tests --module ccpcerp.ccpc_erp.test_finance_lifecycle_disposable_integration`. | Eight direct-Frappe service tests are coded but **not run**; this is not authenticated HTTP/CSRF, two-connection SQL concurrency, GL/SLE or stock posting certification. |

**Important separation:** GitHub code inspection cannot establish actual CircleCI organization role membership, trusted approved-SHA project variable, pricing plan entitlements/balance, runner network isolation or outbound access. Do not claim that self-hosted DEVELOPMENT/PRODUCTION infrastructure is protected merely because a Docker executor is selected. An independent G2 reviewer must check the actual CircleCI project/runner settings using least-privileged read-only views before any execution.

## 4. Credit rate and cost review, without spending

**Verified external official pricing as of 2026-10-28:** CircleCI's [Cloud pricing price list](https://circleci.com/pricing/price-list/) last updated **2026-10-08** lists standard x86 Docker **`large` (4 CPUs / 8 GB)** at **20 credits per minute**. Some executor generations/classes differ; actual plan eligibility and other charges must be checked. The exact project pricing plan and available balance are **NOT** known. The job's MariaDB/Redis sidecars run alongside the primary Docker container and share the selected job's capacity/network model; source alone does not certify available memory or final billing.

| Illustrative run duration | Base compute credits at 20/min |
| --- | ---: |
| 15 minutes | 300 |
| 30 minutes | 600 |
| 60 minutes | 1,200 |
| 120 minutes | 2,400 |

**Cost controls missing from current source:** `no_output_timeout: 20m` applies to **silence on an individual run step**, *not* a full-job spending cap or a promised 20-minute total. The job performs apt, npm, pip, git, bench/site/migrate work and may run long. CircleCI [configuration reference](https://circleci.com/docs/reference/configuration-reference/) indicates plan-level job maxima can be as long as **1 hour Free, 3 hours Performance, 5 hours Scale**; at 20 credits/min that corresponds to base compute exposure of approximately **1,200 / 3,600 / 6,000 credits** before other charges, unless explicitly limited/cancelled. Do not assume which plan CCPC has or that any example is the actual bill.

**Required before G2:** Owner signs a maximum acceptable one-run credit/time budget; confirm live plan, credits remaining and spend alert; set an enforceable or actively supervised cancellation boundary with a named operator; prevent unapproved retries; avoid automatic reruns, unnecessary large executor and heavy package installs. A change to job resource class or duration policy would be a **new reviewed GitHub code change** with a new feature SHA, and prior G1.1 verification must be reassessed as relevant.

## 5. G2 gate recommendation and exact outstanding risks

**G1.2 decision:** **NO-GO for CircleCI execution at this checkpoint**, until:
1. CircleCI CLI configuration validation runs successfully against the exact HEAD `375de12...` and result/version recorded; if compiler reports an error, fix it in GitHub first and repeat relevant static tests.
2. Review live CircleCI project triggers, org/user roles, approval rights, runner type, network access, project variables/context restrictions and any injected secrets without changing settings. Document clear exclusion of real database addresses/SSH/NAS mounts or production Docker hosts.
3. Confirm the user's actual CircleCI plan, permission for `large`, available credits, a single-run maximum spend/cancellation procedure, and approvals before any billable run. Do not infer a total cost solely from `no_output_timeout`.
4. Choose exactly one approved post-harness commit/CI job, set the protected SHA only under separate G2 owner consent, authorize a single opt-in pipeline and separate manual approval, and explicitly limit synthetic MariaDB tests. No actual financial signatory/ledger/stock posting and no persistent site accesses.
5. Resolve any newly exposed app/Frappe compatibility, historical Finance/SQL transaction and rollback blockers through reviewed GitHub commits rather than bypassing guards.

**No CI run, pipeline trigger, setting change, schema migration, DEVELOPMENT or PRODUCTION interaction** occurred during this approval. Draft PR #21 remains unchanged/open; the last verified persistent Integration2 TISS Expense Scope `fie8da5c59` and revision `fieef2e44j` were **Draft**, not re-read live. CircleCI semantic validation is **PENDING, not PASS**; the only executed new-head tests remain the owner-run Python `34/34 PASS`, full compileall pass, and previous SHA-verified local PyYAML parse.

## 6. Owner-reported opt-in CircleCI compiler failure — 2026-10-28

**Owner-generated test evidence, not a ChatGPT-run CI job:** On ccpcerpserver, the owner retrieved CircleCI CLI v1.11.0 from the official GitHub Linux AMD64 tarball, verified SHA-256 `70c3a935e0c2d71d42ba65f0005696eb17fd65fb625c678f45311b826d56de47`, extracted it into a temporary /tmp directory, and confirmed `circleci 1.11.0 (cee106974671)`. They independently confirmed the temporary repository's app HEAD `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`.

**Default configuration:** CircleCI CLI `config validate .circleci/config.yml --json` returned `valid: true` and a compiled configuration containing **starter-validation only**, with the Finance parameter defaulted to false. This did **not** compile the Finance opt-in workflow.

**Finance opt-in configuration:** CircleCI CLI `config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: true'` returned **exit 7**, reporting `Error calling workflow: 'opt-in-finance-lifecycle'`, `Error calling job: 'finance-lifecycle-isolated-integration'`, `Unclosed '<<' tag` with the error pointing to `python - <<'PY'`. The error explicitly instructs escaping the shell heredoc tag with a backslash in config 2.1+.

**GitHub diagnosis:** Independently re-read feature `.circleci/config.yml` blob `0f23d7ce0f1a1e94cad0debbee865ac813ed1509`. It contains one shell heredoc at line 194 and two legitimate workflow template tags. CircleCI's official 2026 compiler guidance confirms the required fix for the shell heredoc: add **one backslash before the literal double less-than** (in source, `python - \\<<'PY'` when displayed as escaped string, or shell source with backslash preceding `<<`). Do not escape workflow template expressions. See https://discuss.circleci.com/t/breaking-changes-config-compilation-updates-september-21-2026/54719 and https://circleci.zendesk.com/hc/en-us/articles/36469244864539-How-to-solve-the-escaping-character-error .

**Controlled path:** First use a separate temporary **YAML COPY** of the exact source config to test the one-line escaped heredoc and compile Finance opt-in. Original GitHub commit and operator source checkout remain unchanged. The diagnostic result by itself does not authorize GitHub source changes; seek separate explicit authorization before any app feature-branch fix commit. The tested patch, if committed, changes HEAD and requires renewed exact-SHA verification. **NO CircleCI pipeline or MariaDB/DEV/PROD activity authorized; G2 remains NO-GO.**

## 7. Owner-verified copy-only Finance opt-in compiler PASS (2026-10-28)

**Operator-reported result of the exact copy-only command from this discussion:**

```text
Temporary configuration prepared.
FINANCE CONFIGURATION: PASS
137:  opt-in-finance-lifecycle:
138-    jobs:
139-    - finance-lifecycle-manual-approval:
140-        filters:
141-          branches:
142-            only: feature/finance-mapping-lifecycle-2026-10-28
143-        type: approval
144-    - finance-lifecycle-isolated-integration:
145-        filters:
146-          branches:
147-            only: feature/finance-mapping-lifecycle-2026-10-28
148-        requires:
149-        - finance-lifecycle-manual-approval
```

**Scope and meaning:** The operator executed CircleCI CLI v1.11.0 `config process` with `run_finance_lifecycle: true` against a **temporary YAML COPY**, after the command confirmed the working Git HEAD exactly equals `375de12e7bf79210fdb7ec54b6e7184d0b27ead6` and the unchanged original `.circleci/config.yml` Git blob exactly equals `0f23d7ce0f1a1e94cad0debbee865ac813ed1509`. The Python copy step asserted exactly one shell heredoc `python - <<'PY'` and changed only that copy to `python - \\<<'PY'` (a single backslash character before the two angle brackets in the YAML source). The CLI compiler returned success and the compiled workflow visibly includes an approval job and the Finance job depending on it. **The reported opt-in CLI compilation error has been resolved in the temporary patched YAML**, not in current GitHub source.

**Exact next action / approval boundary:** Ask for specific **GitHub-only one-line feature-branch code fix authorization** before changing `.circleci/config.yml` on [draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21). Proposed single-line change: `python - <<'PY'` → `python - \\<<'PY'` in the Finance job's shell heredoc only; leave the two real CircleCI workflow parameter tags, older integration job/guard, source branch and other functions unchanged. Include a static regression guard preventing this opt-in compiler error from reappearing if later expressly authorized. After new commit, verify new GitHub SHA and re-run exact-SHA Python/CircleCI default and opt-in config compilation against the **committed file**, not just a temporary copy. A successful compiler PASS is not a permission to dispatch CircleCI jobs.

**G2 still NO-GO:** CircleCI runner/project settings, actual network isolation, approved externally controlled SHA, spend cap/credit balance, finance MariaDB integration and DEVELOPMENT/PRODUCTION release gates remain entirely separate. This documentation change touches no application source, CI project settings, CircleCI execution, or site.

## 8. GitHub-only one-line CircleCI compiler fix committed — owner approved 2026-10-28

**Approval boundary:** After the owner demonstrated `FINANCE CONFIGURATION: PASS` on the exact-blob temporary YAML copy, the owner explicitly approved committing **only** the one-line CircleCI heredoc escape to the existing PR #21 feature branch and following up with static validation. No pipeline, project setting, CI held-job approval, database migration, DEVELOPMENT/PRODUCTION modification or merge is authorized.

**GitHub implementation verified:** App `ccpcerp/ccpcerp` feature branch `feature/finance-mapping-lifecycle-2026-10-28` advanced from `375de12e7bf79210fdb7ec54b6e7184d0b27ead6` to **`d154886ab45c51878a87a4ecf42e45602d8d9ccb`**; commit message `fix(ci): escape Finance Python heredoc for CircleCI opt-in compiler`. The **only** changed file was `.circleci/config.yml`, one line added and one deleted, at line 194. Specifically: the Finance shell heredoc is now `python - \\<<'PY'` in the YAML source (single literal backslash before the double less-than operator); **no other code/content changed**. The GitHub post-change config blob is **`9aa8c676dfa7b22e7b7035d70a0b461af773908d`**, previously `0f23d7ce0f1a1e94cad0debbee865ac813ed1509`. Both intended CircleCI workflow templates remain unescaped.

**GitHub readback/source assertions:** The new branch HEAD equals draft PR #21 head; PR remains OPEN/DRAFT/UNMERGED with same review base. Exact one-line string replacement, identical original integration job text compared against `review/circleci-isolated-erpnext-phase2-2026-10-26`, original workflows unchanged, default-off `run_finance_lifecycle` and `run_integration`, manual approval `requires` relationship, exact approved-SHA and site guards, source pins, existing original CI guard blob, independent Finance CI guard blob and the Finance Frappe service-test module blobs have all been inspected and found unchanged as intended. These checks are **GitHub source assertions, not a Python unittest execution**.

**Testing status and next action:** The owner-run original source at previous SHA `375de12...` passed **34/34 full Python static tests** and `compileall`. CircleCI CLI v1.11.0 **Finance opt-in** compiled successfully on an *identical patch in a temporary config copy*. However **neither Python tests nor CircleCI CLI compiler has yet been rerun on a fresh checkout at the committed new SHA `d154886...`**; a successful copy-only compile is evidence for the exact fix, not proof new HEAD was CLI-tested. The assistant container still lacks CircleCI CLI/GitHub direct network for a full post-commit run. Recommend a new `mktemp -d` isolated clone pinned to new SHA, repeat `python3 -m compileall`, original 24 and new 10 static tests, and BOTH CircleCI compilation modes (default `config validate --json` and Finance opt-in `config process --pipeline-parameters 'run_finance_lifecycle: true'`) with the verified official temporary CLI executable. Capture full output and document results before any G2 approval.

**G2 remains NO-GO.** Paid CircleCI execution, reviewed resource/cost cap, trusted `CCPC_FINANCE_APPROVED_SHA`, project/network isolation, real MariaDB service tests and any DEVELOPMENT/PRODUCTION changes are outside this authorization.

## 9. Post-fix committed-SHA static and CircleCI CLI verification — PASS (2026-10-28)

**Evidence provenance:** The owner pasted terminal output from running the previously supplied **isolated fresh-clone** Ubuntu verification script; the result was not obtained by running CircleCI Cloud or an ERPNext bench. The script created `/tmp/ccpc-finance-postfix-...` and cloned `feature/finance-mapping-lifecycle-2026-10-28`, then required exact `git rev-parse HEAD == d154886ab45c51878a87a4ecf42e45602d8d9ccb`. It executed within a `set -euo pipefail` subshell and ended with the literal message **`POST-FIX STATIC AND CIRCLECI VALIDATION: PASS`**. Therefore the exact-SHA check, full `python3 -m compileall -q ccpcerp .circleci`, all five test suites, and both CLI compiler operations returned success as ordered by the command. The assistant also independently re-read GitHub and confirmed draft PR #21 still points to the exact tested feature commit, with `.circleci/config.yml` blob **`9aa8c676dfa7b22e7b7035d70a0b461af773908d`** containing the escaped Finance heredoc.

| Operation at committed feature HEAD `d154886...` | Owner-supplied result |
| --- | --- |
| `python3 -m compileall -q ccpcerp .circleci` | **PASS** (fail-fast script reached final marker) |
| `test_bc_finance_governance_static.py` | **6/6 PASS**, 0.007s |
| `test_ccpc_mapping_schema_static.py` | **3/3 PASS**, 0.003s |
| `test_bc_mapping_policy_static.py` | **15/15 PASS**, 0.000s |
| `test_finance_lifecycle_ci_guard.py` | **6/6 PASS**, 0.005s |
| `test_finance_ci_config_static.py` | **4/4 PASS**, 0.000s |
| **Total Python static tests** | **34/34 PASS, 0 failures/errors** |
| Official standalone CircleCI CLI v1.11.0 `config validate .circleci/config.yml --json` | **`"valid": true`**, compiled *default* `starter-validation` / `python-syntax` only |
| CircleCI CLI `config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: true'` | **PASS**, compiled `opt-in-finance-lifecycle` containing `finance-lifecycle-manual-approval` (`type: approval`) and `finance-lifecycle-isolated-integration` (`requires: finance-lifecycle-manual-approval`). Also displayed an `upstream` key generated by CircleCI compilation; no runtime job was started. |

**Status change:** The previously pending **post-fix at-committed-SHA** source/static and both CircleCI configuration compiler checks are now **COMPLETE / PASS**, based on the operator transcript and exact-SHA fail-fast script. This is stronger than prior temporary-YAML-copy proof and eliminates the known unescaped-heredoc CI compilation blocker. It does **not** validate the job's Docker engine, image/bench setup, CircleCI approval/control-plane access, CI parameters injected at runtime, Frappe/ERPNext installation, schema, Finance signed-decision services, concurrent MariaDB transactions, authenticated HTTP/CSRF or financial posting.

**G2 remains NO-GO:** Before any paid opt-in run, independently verify live CircleCI project/org approval rights, resource class/plan/credits, trusted SHA project-variable provenance, network isolation from DEVELOPMENT and PRODUCTION, and a one-run credit/time budget with cancellation procedure; seek **separate explicit owner approval** to configure `CCPC_FINANCE_APPROVED_SHA`, start a specific pipeline and approve its hold. The 34/34 tests and two CLI compiler successes are **offline**, not MariaDB integration. Keep PR #21 OPEN/DRAFT/UNMERGED. No database migration or persistent DEVELOPMENT/Integration2/PRODUCTION operation is authorized by this result.
