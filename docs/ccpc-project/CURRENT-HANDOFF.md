# CCPC ERPNext — CURRENT HANDOFF

**Last verified update:** 2026-10-14 (GitHub connector and operator terminal reports).  
**Purpose:** This is the **single rolling GitHub handoff** for CCPC ERPNext. Maintain **this same path** at meaningful milestones, during longer conversations before a thread limit is reached, and when the operator requests a handoff. Do not create a new dated Project Source attachment every time.

> **Read first in every new project conversation:** [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), then this handoff, then verify relevant live GitHub branches and commits with the GitHub connection. The permanent ChatGPT Project Instructions define policy; older Project Sources and dated handoffs supply historical context only. If information conflicts, the most recently verified GitHub state takes precedence. If GitHub is inaccessible, report the inability to verify rather than treating old snapshots as current.

## Corrected detached checkout prepared for second 12-test run — 2026-10-14

**Operator terminal confirmation:** Within frappe_docker_devcontainer-frappe-1, fetched origin/feature/withdrawal-material-issue-safety from SHA 55f13fb to corrected test commit 85d129e193b32cc229de2e30145359bb3979c257; verified pinned FETCH_HEAD before advancing only detached worktree /tmp/ccpc-material-issue-tests-55f13fb with git switch --detach. Final detached status clean at 85d129e; active shared DEVELOPMENT app still on review/intercompany-approval-failure-tests HEAD 806fa23516490ec7beefcff03a1baa09d722120e, only untracked AGENTS.md. Printed CORRECTED TEST CHECKOUT: READY. **No rerun yet**. No database, PRODUCTION, migration, package install, role, or active app changes.

**Next exact limited step:** Rerun existing 12-case mocked unittest using fresh process with explicit sys.path prioritizing detached checkout, both detached and active HEAD guards, clean detached status, PYTHONDONTWRITEBYTECODE=1, NoDatabase fake assigned to frappe.local.db, and blocked frappe.init/frappe.connect. Expected detached SHA 85d129e193b32cc229de2e30145359bb3979c257. New TestCase.setUp patches module-level translation function so expected rejection test branches no longer contact Redis translations/logger. Do not assume tests pass until output verified; no site/inventory posting.

## Detached 12-test mock security run exposed uninitialized translations; GitHub test-only repair pending rerun — 2026-10-14

**Operator provided complete terminal output** of 12 focused mocked unittest tests, executed as `frappe` from the separate detached worktree `/tmp/ccpc-material-issue-tests-55f13fb` at GitHub commit `55f13fba2a7e68d2c606f1d8b97b14ad0e9130a8` using a guarded harness. Preflight printed `DETACHED APPLICATION SOURCE: VERIFIED`, `REAL DATABASE ACCESS: BLOCKED`, `FRAPPE SITE INITIALIZATION: BLOCKED`, `TEST CASES DISCOVERED: 12`. **Actual result:** `Ran 12 tests in 0.018s`, `FAILED (errors=5)`, `MOCKED SECURITY TESTS: FAILED` (seven cases reported `ok`).

**All five errors are test-environment translation/logging errors, not assertions of failed business invariants:** Cases `test_already_submitted_guard_is_a_locking_read`, `test_draft_endpoint_does_not_elevate_stock_entry_rights`, `test_multiple_existing_drafts_fail_closed`, `test_single_preexisting_draft_is_never_privilege_submitted`, and `test_stale_slip_snapshot_is_rejected_after_lock` call the module's localized `_(...)` text on expected rejection paths. With `frappe.init` and cache connection intentionally disabled, `frappe.cache` was `None` and translation lookup raised `AttributeError: 'NoneType' object has no attribute 'hget'`; its logging error path then raised `FileNotFoundError /workspace/development/logs/frappe.log` due known logger relative working directory. This masks intended error-path assertions; it does **not** establish production bugs or successful tests. The seven passing mock checks indicate unaffected cases executed. No site/database transactions or user/permissions changes were requested/executed.

**GitHub-only focused fix committed:** On `feature/withdrawal-material-issue-safety`, added a `TestWithdrawalIssueSafety.setUp()` fixture that uses `unittest.mock.patch` to replace the imported module-level `ccpcerp.ccpc_erp.withdrawal_slip_stock._` translation function with an identity function and registers `addCleanup`. This keeps the 12 test methods and intended exception-path assertions intact, without initializing Frappe, Redis, database, or logger. New feature commit `85d129e193b32cc229de2e30145359bb3979c257`, test file updated only. **Tests have not yet been rerun on this new commit.**

**Next safe operator action:** First update only the detached /tmp worktree to pinned `85d129e...`, using guarded Git fetch and clean-status/expected-HEAD checks; leave shared app checkout at `806fa235...` and untracked `AGENTS.md` alone. Then rerun the same guarded unittest harness with its pinned SHA adjusted to `85d129e...`, and report complete counts/errors. No background CI, active app checkout changes, bench migrate, Frappe site init, test users, stock posting, restoration or production operations.

## Detached feature worktree created with original DEVELOPMENT checkout preserved — 2026-10-14

**Actual operator command and output:** Inside `frappe_docker_devcontainer-frappe-1` as `frappe`, safely fetched `origin/feature/withdrawal-material-issue-safety` with git hooks disabled, verified `FETCH_HEAD` equaled pinned GitHub commit `55f13fba2a7e68d2c606f1d8b97b14ad0e9130a8`, and created a **detached separate worktree** at `/tmp/ccpc-material-issue-tests-55f13fb`. Checkout reported `## HEAD (no branch)`, same pinned commit, with no changed/untracked test checkout files. The active shared app remained `/workspace/development/frappe-bench/apps/ccpcerp`, branch `review/intercompany-approval-failure-tests`, HEAD `806fa23516490ec7beefcff03a1baa09d722120e`, and only `?? AGENTS.md` untracked. Printed `SEPARATE TEST CHECKOUT: PREPARED`. No branch checkout or overwrite in active app, database writes, site initialization, service restarts, bench migration, role or user changes.

**Current testing checkpoint:** Python 3.14.2 has `unittest` but not pytest. Detached checkout is a Git worktree referencing the original repo metadata but is **not** installed as the active Frappe app. For tests use an explicit `sys.path.insert(0, '/tmp/ccpc-material-issue-tests-55f13fb')` in a fresh bench Python process and assert imported CCPC app file resolves under that directory. Import Frappe without running `frappe.init`/`connect`; prebind a fail-closed fake `frappe.local.db` so `@patch(...frappe.db.sql)` works but unexpected DB operations raise; prohibit Frappe site initialization and DB connections during the mocked test session. `PYTHONDONTWRITEBYTECODE=1` prevents .pyc writes. Execute only the 12 focused mock unit tests (not broad app discovery). This may uncover import/mocking problems; do not claim runtime integration coverage or deploy. GitHub feature PR #7 was last verified draft at the same SHA.

## Separate unit-test checkout readiness verified — 2026-10-14

Operator ran a read-only module availability check inside the existing DEVELOPMENT container using bench Python with PYTHONDONTWRITEBYTECODE=1. Output: unittest AVAILABLE, pytest NOT FOUND, pip AVAILABLE, frappe AVAILABLE, erpnext AVAILABLE, ccpcerp AVAILABLE; READ-ONLY TEST RUNNER CHECK: COMPLETED. Python was previously reported 3.14.2. This proves unittest importability, **not execution of any tests**. No packages installed, no app files changed, and no database touched. GitHub feature branch feature/withdrawal-material-issue-safety and draft PR #7 HEAD reverified at 55f13fba2a7e68d2c606f1d8b97b14ad0e9130a8.

Next safe operator step is a pinned-SHA fetch plus detached Git worktree at an unused directory outside /workspace/development/frappe-bench (e.g. /tmp/ccpc-material-issue-tests-55f13fb), with hooks disabled, no live branch switch, and preservation of untracked AGENTS.md. This prepares independent source checkout only, **not deployment nor test execution**. Stop if target exists or fetched SHA differs. After creating checkout, verify its HEAD and both worktree statuses; then plan unittest invocation ensuring PYTHONPATH prioritizes the detached copy while avoiding site initialization or business DB writes. A detached worktree still shares the original repo's Git metadata but not app working files; no new Python environment is needed.

## Safe test-runner preflight and additional issue privilege hardening — 2026-10-14

**Operator read-only environment inspection:** Within `frappe_docker_devcontainer-frappe-1`, the command `git -C apps/ccpcerp worktree list --porcelain` reported exactly **one** worktree: `/workspace/development/frappe-bench/apps/ccpcerp`, HEAD `806fa23516490ec7beefcff03a1baa09d722120e`, branch `review/intercompany-approval-failure-tests`; Python version `3.14.2`; `./env/bin/python -m pip show pytest` piped through grep produced **no Name/Version lines** (pip and stderr were masked, so this does **not** independently establish whether pytest is importable). No separate feature test checkout exists or was created; active shared DEVELOPMENT app checkout and untracked `AGENTS.md` were left unchanged.

**Security hardening under previously authorized GitHub-only scope:** Further review of draft PR #7 found that `issue_withdrawal_slip` previously called `stock_entry.submit()` with `flags.ignore_permissions=True` even when reusing an *existing, potentially edited* Stock Entry draft. This could inadvertently elevate posting-related draft contents (e.g., expense/costing fields) that the restricted stockroom caller did not construct. Corrected **fail closed**: the privileged one-call endpoint now rejects any pre-existing draft under the same Slip; an appropriately authorized Stock Entry user must review/discard the draft through an independently controlled process. Only a new server-built Stock Entry can be inserted and submitted with document-scoped `ignore_permissions` by this endpoint. Legacy draft API remains gated by native Stock Entry create permissions. Updated the mocked regression test to assert a single pre-existing draft cannot be privileged-submitted. **No site/bench/database changes**, GitHub only.

**Verification:** GitHub feature HEAD `55f13fba2a7e68d2c606f1d8b97b14ad0e9130a8`, branch `feature/withdrawal-material-issue-safety`; [draft PR #7](https://github.com/ccpcerp/ccpcerp/pull/7) points to same HEAD and targets `review/intercompany-approval-failure-tests`. Verified GitHub comparison of base `806fa235...55f13fb` shows **8 feature commits and exactly the original 4 intended changed files**, including 12 new mocked tests. **Tests have not yet run.** Next safe check is read-only inspection of test-runner module availability (`unittest`, `pytest`, `pip`, `frappe`, `erpnext`), then plan and separately review an out-of-bench detached test checkout before any execution. Do not switch the live worktree, grant roles, create business documents, migrate, restore or touch PRODUCTION.

## DEVELOPMENT working-tree preflight for draft Material Issue PR — 2026-10-14

**Operator-provided read-only Docker Git status:** In `frappe_docker_devcontainer-frappe-1`, user `frappe`, `/workspace/development/frappe-bench/apps/ccpcerp`, command `git status --short --branch; git rev-parse HEAD; git branch --show-current` yielded:

```text
## review/intercompany-approval-failure-tests...origin/review/intercompany-approval-failure-tests
?? AGENTS.md
806fa23516490ec7beefcff03a1baa09d722120e
review/intercompany-approval-failure-tests
```

Thus no tracked local code modifications appeared in this inspection; **untracked AGENTS.md exists and must be preserved / never blindly staged or overwritten**. Installed application matches the base review commit from which PR #7 was branched. GitHub independently verified draft PR #7's feature branch remains at `9570ddcd4eccff5110b2c25e8baac24e51e23f1a`. Nothing was fetched/pulled/checked out/deployed.

**Deployment boundary:** The app directory belongs to a shared DEVELOPMENT Frappe bench hosting the persistent `development.localhost` site as well as isolated `ccpc-integration2.localhost`. Switching or pulling the app worktree may affect Python code served by both sites even without database writes; the prior owner's approval was **GitHub code + tests only, explicitly without deployment**. Do not switch the shared app branch, pull, migrate, restart services, apply permission changes, or create stock transactions under that approval. Before tests, plan an independent/non-live test checkout and identify how it will run without touching the shared bench or protected snapshots; obtain explicit authorization before staging any code in the live app or running test code that modifies site state.

## Approved scoped Stockroom Material Issue safeguard developed on GitHub, draft PR — 2026-10-14

**Owner explicitly authorized GitHub code and focused test changes only, without deployment.** Work performed directly through connected GitHub on new feature branch feature/withdrawal-material-issue-safety from verified app review branch review/intercompany-approval-failure-tests at base 806fa23516490ec7beefcff03a1baa09d722120e. **HEAD 9570ddcd4eccff5110b2c25e8baac24e51e23f1a**; draft pull request [ccpcerp/ccpcerp#7](https://github.com/ccpcerp/ccpcerp/pull/7), targeting the existing review branch; NOT merged or deployed. Connected GitHub compare verified six new commits and exactly four changed files.

**Implemented files and behavior:**
- ccpcerp/ccpc_erp/withdrawal_slip_stock.py: adds POST-only issue_withdrawal_slip server endpoint with Stockroom/System Manager/Administrator role gate, Withdrawal Slip write permission, Stockroom Review and Received By preconditions, parent row SELECT ... FOR UPDATE lock, current/locking reads for draft and any submitted issue, fail-closed multiple-draft check, and tightly scoped per-document ignore_permissions only for the source-constructed or linked existing Stock Entry, which then follows standard Frappe insert/submit and ERPNext hooks. Submission hook independently rechecks the submitted issue under the same parent lock; no manual explicit commit and errors propagate. Legacy draft creation is restricted to users with ordinary Stock Entry create permission.
- ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.js: change client button to a confirmed Issue Materials action that invokes one-call posting instead of opening a Stock Entry draft inaccessible to Stockroom Personnel.
- ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_issue_safety.py: twelve new **mocked** tests for role and slip access, locking/current reads, submitted issue guards, draft reuse/fail-closed multiple drafts, scoped permission bypass, failed submit propagation and hook locking.
- ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_slip.py: adjust pre-existing mocked tests for helper/locking calls.

**Review and verification boundary:** Connected GitHub compare verified intended four files. Public Frappe v16 implementation was inspected for Document.insert(ignore_permissions=True), document-scoped flags.ignore_permissions during save/submit, and HTTP POST-only whitelisting support. **No tests have run**; there are no GitHub Actions workflow files in the reviewed app tree. Static review and committed mocked tests do not prove live Frappe permissions, database row-lock behavior, concurrency race prevention, inventory/GL posting correctness, rollback on failure, or cancellation/reissue. Draft PR must not be merged or described as production-ready yet.

**Next safe step:** Before any DEVELOPMENT update, inspect branch, HEAD, tracked/untracked changes and installed app code (preserve any local work). Plan isolated-site runtime validation with the ten preserved recovery checkpoints and separately approved backup/restore review, synthetic users and transactions only under explicit follow-on authorization, and two-session database race/failure tests. Record actual DEV results and fixes in GitHub. No site database, permission grants, deployments, services, or PRODUCTION touched by current approved GitHub work. Avoid new API fees, Codex reporting, and background automation.

## GitHub-first Withdrawal Slip → Material Issue static security review — 2026-10-14

**Scope completed:** Read-only GitHub source inspection of authoritative custom app branch `review/intercompany-approval-failure-tests` at verified HEAD `806fa23516490ec7beefcff03a1baa09d722120e` (not default branch), plus Workflow/handoff from docs branch `docs/ccpc-checkpoint-2026-10-10` at previous HEAD `ab7fb59fb65b97109fb1ac0eef14248380e0b911`. Relevant code: `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` blob `04171d661de748414b26a1f1cf24deb95005297f` (353 lines); `ccpcerp/hooks.py` blob `023dc7b04b8f4fa019654c074124bd03f3b82489`; `ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_slip.py` blob `c661d1cede97dbc26959a9d59639d2ecd3b68427`; `withdrawal_slip.py` blob `8675e5413cf5efea6a17eb1088b1d08f36defe27`; Withdrawal Slip DocType JSON blob `63fd9ad0eb89f1ab66e92b4b9a673dbda8099f24`. This review performed **no code/DB mutations and ran no tests**.

**Established existing implementation:** `make_material_issue` is a whitelisted helper gated by Stockroom Personnel/System Manager/Administrator role and Withdrawal Slip write permission, `Stockroom Review` status, and `received_by`. It reuses newest matching draft by `frappe.get_all`; otherwise checks already submitted line quantities and creates a draft `Stock Entry` of purpose `Material Issue` with company, warehouse, slip and slip-item pointers, quantity/reduced-issue validation, and `stock_entry.insert()` under ordinary user permissions. Hooked `Stock Entry.validate` and `before_submit` additionally check authority, workflow state, company, purpose, warehouse, row provenance, planned quantity and available stock; before_submit captures `withdrawal_slip_issued_by`. `on_submit`/`on_cancel` sync issued/shortage counts, slip status, and issuer fields. Client form offers Create Material Issue only in Stockroom Review to eligible roles. Unit tests cover positive / negative stock, provenance, issue quantity, shortage, status, issuer; these are **mock-based unit tests**, not proof of live DB concurrency, user DocPerm, stock ledger posting or GL integrity.

**Risk 1 (blocking for normal Stockroom Personnel):** Historical isolated DB DocPerm/Custom DocPerm read-only audit on 2026-10-13 established that Stockroom Personnel has Withdrawal Slip read/write but **no Stock Entry create/submit**, while `stock_entry.insert()` does not specify `ignore_permissions`. Standard Stock User/Stock Manager roles do have broader create/submit; do not grant these broadly as a shortcut. No runtime test user yet; do not claim current capability has been demonstrated.

**Risk 2 (high priority before financial/inventory posting):** Existing draft lookup (`get_all` then `insert`) and submitted-quantity check (`_get_submitted_qty_by_slip_item`) have no explicit row lock or uniqueness constraint visible in inspected integration file. Concurrent requests may both observe no draft/no submitted quantities and attempt duplicate documents/posting. This is a **plausible transaction race**, not a reproduced production defect. Generic Stock Entry submit path also needs compatible atomic duplicate checks, not only a whitelisted creation endpoint.

**Other review boundaries:** Application validates quantities and stock availability at submit, but its live behavior under stock revaluation, stock ledger concurrency, errors during submit/status sync and return/cancel permissions is **not yet integration-tested**. The code currently rejects creating an additional issue if any submitted quantity exists; partial-issue policy seems one Material Issue with shortage, not incremental subsequent issue. Confirm desired cancellation/reissue policy before choosing unique constraints. `frappe.db.set_value` sync modifies Withdrawal Slip and child rows, so transaction/failure recovery should be tested with real DB rollback. Existing `test_withdrawal_slip.py` mocked tests cannot settle these questions.

**Next recommended GitHub coding step — separate scoped approval before implementation:** Design and review a narrowly privileged, server-side issuance pathway for Stockroom Personnel only, coupled with a consistent row-lock/atomic single-issue guard across draft creation and Stock Entry submission (including cancellation/retry policy), strict slip role/warehouse/company/qty/provenance checks, no uncontrolled privilege elevation, and errors that roll back inventory/GL/status as one transaction. Add deterministic negative permission and mocked concurrency-path tests in GitHub, then design actual isolated-site two-session DB integration tests. Inspect installed Frappe v16 permission semantics before choosing `ignore_permissions` or submit mechanics. After review, determine specific branch/commit and verify app code in GitHub; check DEVELOPMENT git status before pulling. **No code changes, permission grants, user creation, site posting, bench migration, restore, production operations or new recovery artifacts have been executed/authorized by this static review.**

## Isolated Stock Entry provenance fields independently database-verified — 2026-10-14

**Milestone COMPLETE within approved limited scope:** On `ccpc-integration2.localhost`, the operator executed SHA-256-verified v3 guarded installer (`/home/gani/ccpc_stock_entry_fields_setup_v3.py`, SHA-256 `309fe219cc3f806b475de9f2b004af7f22cb8d75d6f3c33f04dad32922d8698c`), and the script reported all three approved Custom Fields persisted/committed and all ten protected existing checkpoints (40 files) intact. The operator then ran a **separate, direct `MySQLdb` read-only audit** using `START TRANSACTION READ ONLY` and provided the complete success summary:

```text
ISOLATED DATABASE: VERIFIED
Stock Entry.withdrawal_slip: METADATA AND SQL COLUMN VERIFIED
Stock Entry.withdrawal_slip_issued_by: METADATA AND SQL COLUMN VERIFIED
Stock Entry Detail.withdrawal_slip_item: METADATA AND SQL COLUMN VERIFIED
ACTIVE WORKFLOW AND SELF-APPROVAL: VERIFIED
OPENING STOCK: 10 NOS / PHP 1,000 VERIFIED
STOCK LEDGER AND BALANCED GL: VERIFIED
UNRELATED BUSINESS DOCUMENTS / USERS: NONE
THREE STOCK ENTRY INTEGRATION FIELDS: INDEPENDENTLY VERIFIED
READ-ONLY DATABASE AUDIT: PASSED
```

**Scope and checks:** The independent audit directly compared isolated database identity with `development.localhost` (different DB), confirmed precisely one `tabCustom Field` row and one corresponding physical `information_schema.COLUMNS` record for each of the three fields, and asserted metadata labels, field types, options, insert positions, `read_only`, `hidden`, `no_copy` match reviewed `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()`: `Stock Entry.withdrawal_slip` Link → Withdrawal Slip after purchase_order (read-only, no_copy), `Stock Entry.withdrawal_slip_issued_by` Link → User after withdrawal_slip (read-only, hidden, no_copy), and `Stock Entry Detail.withdrawal_slip_item` Data after material_request_item (read-only, hidden, no_copy). It asserted active Workflow with eight states/four transitions and expected Draft→Approved self-approval action; Bin at 10 Nos/PHP1,000; one submitted opening Stock Reconciliation, one Stock Ledger Entry and two balanced GL Entries of PHP1,000 debit/credit; zero Withdrawal Slips, Stock Entries, Sales Invoices, Purchase Invoices, Intercompany Material Billing Batches and non-Administrator/Guest users. Read-only transaction rolled back/connection closed. The exact audit command was provided in chat before operator reported success. **No further installation is needed.**

**Verification boundaries:** This proves persisted fields and the enumerated database invariants, **not** end-to-end withdrawal issuing, role-based posting access, concurrency/duplicate-issue controls, posting or billing integration, recovery restore drill, or an independent second archive checksum pass after installation. The installer itself reported pre-/post-install recovery checkpoint preservation; no backups were restored. Persistent DEVELOPMENT and PRODUCTION have not been changed as part of this milestone. Do not rerun v3, `bench migrate`, create test users/Stock Entries, adjust permissions, post inventory/GL, or deploy without separate reviewed scope/authorization.

**Next milestone to plan separately (not yet authorized for mutation):** GitHub-first review of the existing Withdrawal Slip → Stock Entry Material Issue integration logic and planned limited isolated-site test cases. Identify the separate Stockroom Personnel Create/Submit permissions gap, duplicate-operation prevention, audit trail, concurrency, failure/rollback, and initial integration steps. Safeguard isolation and protected checkpoints, seek explicit approval before executing any additional schema/roles/users/business-document changes. Record test outputs in GitHub; PRODUCTION deployment always needs separate approval.

## Approved three Stock Entry provenance fields installed and committed on isolated site; independent audit pending — 2026-10-14

**Actual operator-provided terminal execution, after SHA-256 guard:** `/home/gani/ccpc_stock_entry_fields_setup_v3.py` checksum matched `309fe219cc3f806b475de9f2b004af7f22cb8d75d6f3c33f04dad32922d8698c`. Command ran once as user `frappe` inside existing `frappe_docker_devcontainer-frappe-1` from `/workspace/development/frappe-bench`, with input redirected to Python via stdin. The script reported `ISOLATED SITE: VERIFIED`, `ALL TEN EXISTING CHECKPOINTS: VERIFIED (40 FILES)`, `REVIEWED SETUP CODE: VERIFIED`, active Withdrawal Slip Workflow/self-approval and 10 Nos / PHP1,000 opening stock/balanced GL verified, and no users, Stock Entries or unrelated transactions. It printed `Installing exactly three approved provenance Custom Fields...`, `ALL THREE FIELD DEFINITIONS: VERIFIED IN FRAPPE`, `FIELD INSTALLATION: FUNCTION RETURNED AND COMMITTED`, each target field `VERIFIED`, `Metadata and physical SQL columns: VERIFIED`, ten checkpoints preserved and Workflow/stock/GL/users/permissions/business documents unchanged. Terminal finished `STOCK ENTRY INTEGRATION FIELDS: PERSISTED AND VERIFIED` with no traceback.

**Exactly scoped installed fields (operator/script in-session verification; independent check pending):** `Stock Entry.withdrawal_slip` (Link → Withdrawal Slip), `Stock Entry.withdrawal_slip_issued_by` (Link → User), `Stock Entry Detail.withdrawal_slip_item` (Data), defined in `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()` on app review branch `review/intercompany-approval-failure-tests` at verified `806fa23516490ec7beefcff03a1baa09d722120e` (`setup.py` blob `915e0109a508d503384b227de864ef318fa6ed8c`). No broad `bench migrate` or `after_migrate`.

**Crucial verification boundary:** This is successful **operator-reported install and in-script post-commit verification**, not yet an **independent read-only audit** of persisted state. Do not call the milestone independently verified until a separate MySQLdb `START TRANSACTION READ ONLY` audit checks target DB is distinct from persistent `development.localhost`, all 3 `tabCustom Field` metadata rows and 3 `information_schema.COLUMNS` entries, expected field type/options/insert_after/read_only/hidden/no_copy, active 8-state/4-transition Withdrawal Slip Workflow, 10 Nos/PHP1,000 Bin with reconciled GL, zero unintended stock/invoice/billing transactions, and ideally target roles/permissions plus protected snapshot inventory. Snapshot hashes were checked by the script (40 artifacts) but are not a substitute for a restore drill. **Do not rerun installer** after success. No test users, Stock Entries, invoice/billing transactions, changes to persistent DEVELOPMENT or PRODUCTION, migrations, cleanup or restores authorized. The next action is independent read-only persistence verification; then record observed result here.

## V3 stock-entry provenance installer prepared and operator-verified, execution pending — 2026-10-14

**Operator terminal evidence, preparation only:** Source v2 was rechecked against SHA-256 `e27386879c02f3f98c76ed4489474255e882b3f0664a84c6ec70c578f6477660`; v3 passed `compile(..., "exec")`. The operator displayed the **exact v2→v3 unified diff** consisting of: (1) add `import os`; (2) change `SITES = Path('sites')` to `SITES = Path('sites').resolve()`; (3) insert `os.chdir(SITES)` immediately before existing `frappe.init(site=SITE, sites_path=str(SITES))`. The script's guarded checks, three-field setup call and commit/rollback logic were not intentionally changed. Saved separate host script `/home/gani/ccpc_stock_entry_fields_setup_v3.py` with operator-reported SHA-256 `309fe219cc3f806b475de9f2b004af7f22cb8d75d6f3c33f04dad32922d8698c`. **Not executed**, no fresh schema or database writes at preparation step.

**Rationale:** Installed Frappe v16 logger uses `../logs/database.log` relative to process cwd. Executing the Python script from the bench then `os.chdir(SITES)` after all direct-DB preflight makes Frappe's relative logger path resolve to the existing writable bench `logs` directory. Resolving `SITES` to an absolute path before changing cwd retains prior isolated-site and checkpoint references. This is a narrowly reviewed script execution-context fix; success of Frappe connection / custom-field persistence is **not yet tested**.

**Next permitted guarded operation:** In the Ubuntu **host** terminal, recheck v3 SHA-256 and only if it passes execute v3 once inside existing `frappe_docker_devcontainer-frappe-1` as `frappe`, starting from `/workspace/development/frappe-bench`, using the same container Python stdin method as v2. Target only `ccpc-integration2.localhost`, call only `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()` to create the previously authorized three fields; verify all ten protected checkpoints and stock/workflow/GL preflight. On any failure STOP (DDL may be partially committed), **no blind rerun/restoration**; independent direct MySQLdb read-only audit before deciding next action. On apparent success, independent read-only post-commit audit of Custom Field metadata, physical columns, Workflow, Bin/GL, business transactions and preservation of snapshots **before** calling milestone complete. No full `bench migrate`, test-user/permission/financial transactions, persistent DEVELOPMENT or PRODUCTION operations authorized.

## Installed logger and v2 script inspection confirms narrow v3 preparation plan — 2026-10-14

**Operator read-only installed-source output:** `frappe.utils.logger.create_handler` uses `os.path.join("..", "logs", logfile)` and `RotatingFileHandler(log_filename, ...)`; cwd `/workspace/development/frappe-bench` therefore resolves `../logs/database.log` to nonexistent `/workspace/development/logs/database.log`. From cwd `/workspace/development/frappe-bench/sites`, the same relative logger path resolves to existing bench `logs/database.log`. Isolated site log directory exists. The bad relative logger path is **confirmed in installed code**, not merely inferred from upstream source.

**Operator SHA-verified inspection of** `/home/gani/ccpc_stock_entry_fields_setup_v2.py` (`e27386879c02f3f98c76ed4489474255e882b3f0664a84c6ec70c578f6477660`): `SITES = Path('sites')` at line 14; `PRIVATE = SITES / SITE / 'private'` at line 15; `frappe.init(site=SITE, sites_path=str(SITES))` at line 229; `frappe.connect()` 231; only intended `setup.ensure_withdrawal_slip_stock_entry_fields()` at 250; `frappe.db.commit()` 267; rollback 270. The guarded script prints its initial validations before `frappe.init`, so Frappe initialization and connect occur before the approved field-install call. No post-error persistent field schema was found by the prior independent MySQLdb audit.

**Proposed local operator-script v3 (NOT executed):** Preserve original v2. With exact v2 checksum guard, convert `SITES = Path('sites')` to `SITES = Path('sites').resolve()` **before changing cwd**; import `os` and insert `os.chdir(SITES)` immediately before unchanged `frappe.init(site=SITE, sites_path=str(SITES))`. This allows the installed logger's `../logs` path to target bench logs while keeping the script's `SITES` and `PRIVATE` references absolute and retaining isolated site context. Create a separately named v3 file without overwriting, syntax-check, record its new SHA-256 and inspect its exact unified diff before any run. This correction is focused on raw-script execution context, **not a CCPC application-code change**. Do not execute until the new script is independently checked; any further failure requires STOP/read-only audit, not automatic retry.

**Safety scope:** Only three previously approved fields on `ccpc-integration2.localhost`, and the ten existing checkpoints (40 artifacts) preserved. The audit proved fields absent, active Withdrawal Slip Workflow and PHP1,000 opening-stock/GL unchanged. No persistent DEVELOPMENT or PRODUCTION operations, bench migration, user/role changes, or business transactions authorized.

## Frappe logging path diagnosis: correct bench directory but relative logger destination — 2026-10-14

**Operator read-only Docker inspection:** `os.getcwd()` and `frappe.utils.get_bench_path()` both returned `/workspace/development/frappe-bench`; `FRAPPE_BENCH_ROOT` was unset. `/workspace/development/frappe-bench/logs` exists and is writable; `/workspace/development/logs` does **not** exist. This explains the reported attempted file target but does not alone identify the exact line in the installed logger or prove the failed installation reached any schema operation.

**Installed Frappe logger behavior now independently verified by the operator (read-only source inspection):** `frappe.utils.logger.create_handler` contains `log_filename = os.path.join("..", "logs", logfile)` and `handler = RotatingFileHandler(log_filename, ...)`, plus `sitelog_filename = os.path.join(site, "logs", logfile)` and `site_handler = RotatingFileHandler(sitelog_filename, ...)`. Under raw Python cwd `/workspace/development/frappe-bench`, `../logs/database.log` resolves to the absent `/workspace/development/logs/database.log`; from cwd `/workspace/development/frappe-bench/sites`, the same expression resolves to the existing writable `/workspace/development/frappe-bench/logs/database.log`. The isolated site's own `sites/ccpc-integration2.localhost/logs` exists. **This establishes the incorrect logger path resolution, not a finished installer fix.** Avoid creating `/workspace/development/logs` as a workaround.

**Next safe one-step action:** Read-only inspect the guarded v2 script's `SITES` path constants and the source context around `frappe.init`, `frappe.connect`, and `setup.ensure_withdrawal_slip_stock_entry_fields()` (without printing credentials). Do not create `/workspace/development/logs`, change permissions, execute the setup script again, restore or perform DDL. Develop an exact reviewed path correction once the actual code has been examined. The separate SQL audit remains authoritative: all three intended Custom Field records and physical SQL columns absent; active Workflow, 10 Nos/PHP1,000 and balanced GL preserved. Target remains isolated `ccpc-integration2.localhost` only; persistent DEVELOPMENT/PRODUCTION untouched.

## Corrected Stock Entry field installation halted on bench database-log path; independent audit clean — 2026-10-14

**Operator-reported execution:** The SHA-256-verified `/home/gani/ccpc_stock_entry_fields_setup_v2.py` (`e27386879c02f3f98c76ed4489474255e882b3f0664a84c6ec70c578f6477660`) ran via `docker exec -i --user frappe frappe_docker_devcontainer-frappe-1` from `/workspace/development/frappe-bench`, with intended site `ccpc-integration2.localhost`. Guarded preflight passed site isolation, all ten existing recovery checkpoints (40 artifacts), reviewed setup code, active Workflow / self-approval, opening stock 10 Nos/PHP1,000, balanced GL and no user/Stock Entry/unrelated transactions. The process then stopped:

```text
STOP: FileNotFoundError [Errno 2] No such file or directory: '/workspace/development/logs/database.log'
Database DDL might have committed partial schema changes even if rollback was requested.
DO NOT rerun or restore. Run an independent read-only audit first.
```

**Independent audit completed and reported by operator:** Direct `MySQLdb` connection in `START TRANSACTION READ ONLY` verified target DB identity distinct from `development.localhost`; `tabCustom Field` rows and `information_schema.COLUMNS` for each of `Stock Entry.withdrawal_slip`, `Stock Entry.withdrawal_slip_issued_by`, and `Stock Entry Detail.withdrawal_slip_item` all **0**. Withdrawal Slip Workflow verified (active with eight states/four transitions in the audit's assertions); opening stock Bin **10 Nos / PHP1,000**, two GL entries balanced **PHP1,000 each**, and **zero** Withdrawal Slips, Stock Entries, Sales Invoices, Purchase Invoices and Intercompany Material Billing Batches. Output ended `THREE FIELDS: NO PERSISTED SCHEMA CHANGES` and `INDEPENDENT READ-ONLY AUDIT: COMPLETED`. No restoration or new transactions performed. The independent audit did not re-hash backup archives, but the failing installer preflight reported all ten checkpoints verified.

**Status:** Targeted Custom Field installation still **NOT completed**; nothing to claim as persisted, migrated or integration tested. The `/workspace/development/logs/database.log` exception is a **new unresolved Frappe logging/bench-path problem**; the exact cause and point of failure relative to the guarded install function need inspection. Avoid assuming the missing directory merely needs creating. **Next safe one-step action:** read-only inspect within the existing DEV container of `os.getcwd()`, Frappe's computed bench path, the *nonsecret* `FRAPPE_BENCH_ROOT` path setting, and existence/permissions of `/workspace/development/logs` versus `/workspace/development/frappe-bench/logs`. Do not call `frappe.init`, `frappe.connect`, `bench migrate`, run installer again, make new directories or permission changes, or restore backups until inspected. Review and checksum any focused correction before a subsequent already-scoped attempt; perform independent postcommit SQL audit after actual installation. Authorization remains exactly the same three Custom Fields on `ccpc-integration2.localhost` only. Persistent DEVELOPMENT and PRODUCTION untouched.

## Approved three-field install stopped before Frappe connection: incorrect sites_path — 2026-10-14

Owner ran first narrowly approved Stock Entry provenance Custom Field install on isolated `ccpc-integration2.localhost` via `/home/gani/ccpc_stock_entry_fields_setup.py`, with SHA-256 `1c9b2a55cd3126781c247167802ff8569789bd39072a7959d2779e8706716ed5`; script integrity passed. Output:

```text
ISOLATED SITE: VERIFIED
ALL TEN EXISTING CHECKPOINTS: VERIFIED (40 FILES)
REVIEWED SETUP CODE: VERIFIED
WORKFLOW / SELF-APPROVAL / OPENING STOCK / BALANCED GL: VERIFIED
NO USERS, STOCK ENTRIES OR UNRELATED TRANSACTIONS: VERIFIED
STOP: IncorrectSitePath 404 Not Found: ccpc-integration2.localhost does not exist.
Database DDL might have committed partial schema changes even if rollback was requested.
DO NOT rerun or restore. Run an independent read-only audit first.
```

**Defect confirmed by inspection of submitted script:** command runs `cd /workspace/development/frappe-bench`, the script uses `SITES = Path('sites')` for successful direct MySQLdb preflight, but calls `frappe.init(site=SITE)` without `sites_path='sites'`. Frappe v16.33.1's `frappe.init(site, sites_path='.')` defaults to current working directory, so it looked for `/workspace/development/frappe-bench/ccpc-integration2.localhost` instead of `.../frappe-bench/sites/ccpc-integration2.localhost`. Failure arose at **`frappe.init` before `frappe.connect()` and before `setup.ensure_withdrawal_slip_stock_entry_fields()`** (the 'Installing exactly three approved...' banner was not printed), and thus **no DDL was attempted by this script**. The generic failure message about DDL was unconditional and should not be interpreted as proof of partial schema mutation. Still conduct a separate **read-only MySQLdb audit** of the isolated DB, confirm all three `tabCustom Field` rows and corresponding `information_schema.COLUMNS` absent, Workflow intact, same 10 Nos/PHP1000 opening-stock ledger and balanced GL, zero Stock Entry/Withdrawal Slip/invoices, tenth backed-up DB identity. Do not rerun or restore before independent audit.

**If audit passes**, fix solely Frappe initialization to `frappe.init(site=SITE, sites_path='sites')` while keeping exact same bench cwd, and reverify preflight and all 40 protected backup hashes; no extra scope. Consider preparing corrected script and checksum, then continue the already-approved field-only operation. Frappe's `create_custom_fields` may perform DDL/implicit commits once actually invoked; ensure independent postcommit verification. No `bench migrate`, no entire `after_migrate`, no user/role changes, Stock Entry postings, persistent DEVELOPMENT or PRODUCTION operations.

## First approved Stock Entry field attempt stopped at Frappe site-path setup; independent audit clean — 2026-10-14

**Owner/operator reports first guarded attempt installing the three approved Withdrawal Slip–Stock Entry Custom Fields** on isolated `ccpc-integration2.localhost` stopped after passing the script file SHA-256 verification, database isolation, ten protected checkpoints (40 files), reviewed application code, active Withdrawal Slip Workflow with self-approval, Opening Stock 10 Nos / PHP1000 and balanced GL, zero non-admin test users and transactions. Error: **`STOP: IncorrectSitePath 404 Not Found: ccpc-integration2.localhost does not exist.`**. The script printed no "Installing exactly three..." message.

Owner then executed a **separate read-only database audit** and reported `ISOLATED SITE: VERIFIED`, `TENTH CHECKPOINT IDENTITY: VERIFIED`; all three Custom Field records **0** and physical SQL columns **0**; active Workflow 8 states/4 transitions, Opening Stock 10 Nos / PHP1000, balanced GL, zero unrelated transactions. Final output **`FAILED FIELD INSTALLATION: NO SCHEMA CHANGES PERSISTED`** and `READ-ONLY AUDIT: PASSED`. No restore was required.

**Exact cause verified from source**: `/mnt/data/ccpc_stock_entry_fields_setup.py` executes within working directory `/workspace/development/frappe-bench` and used `frappe.init(site=SITE)`. Frappe v16.33.1's `frappe.init(site, sites_path=".")` defaults sites path to current working directory, hence looks for `/workspace/development/frappe-bench/ccpc-integration2.localhost`, not the existing `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost`. **Minimal patch**: replace only `frappe.init(site=SITE)` with `frappe.init(site=SITE, sites_path=str(SITES))`, where `SITES=Path('sites')`. The review compared original/revised files with one-line-only diff, verified Python syntax; old SHA-256 `1c9b2a55cd3126781c247167802ff8569789bd39072a7959d2779e8706716ed5`; revised file `ccpc_stock_entry_fields_setup_v2.py` SHA-256 `e27386879c02f3f98c76ed4489474255e882b3f0664a84c6ec70c578f6477660`. No production or persistent-development site should be touched.

**Status:** schema remains unchanged; the owner previously approved only these same three field installations on isolated site; after independent rollback audit confirmed no persisted change, correcting the invocation path is within the earlier approval. Next step transfer revision from Windows to `/home/gani/` using `scp`, verify SHA-256 before execution, run guarded script once, and independently perform post-commit read-only audit before closing milestone. DDL/implicit-commit risk remains even with correct path: any failure means STOP and inspect; never blindly rerun or restore. No test users, roles, business transactions, other setup functions, broad `bench migrate`, changes to persistent DEVELOPMENT or PRODUCTION are authorized. Tenth recovery prefix remains `20261013_181534-ccpc-integration2_localhost-*`; nine predecessors preserved.

## Isolated Stock Entry provenance field installation explicitly approved — 2026-10-13

The owner **explicitly approved installation of only three Withdrawal Slip–Stock Entry provenance Custom Fields** on isolated `ccpc-integration2.localhost`: `Stock Entry.withdrawal_slip` (Link → Withdrawal Slip), `Stock Entry.withdrawal_slip_issued_by` (Link → User), and `Stock Entry Detail.withdrawal_slip_item` (Data). These are already defined by `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()` in app review branch `review/intercompany-approval-failure-tests`, last verified HEAD `806fa23516490ec7beefcff03a1baa09d722120e` (`setup.py` Git blob `915e0109a508d503384b227de864ef318fa6ed8c`). No application-code change is needed for this narrowly approved step.

**Protected recovery baseline:** tenth backup-only snapshot `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-withdrawal-workflow-pre-stock-entry-fields-20261013/20261013_181534-ccpc-integration2_localhost-*` created 2026-10-13 18:15:34 Asia/Manila; format and backed-up database identity verified, nine earlier sets retained (40 artifacts total). Active owner-approved requestor self-approval Workflow (8 states / 4 transitions); single submitted opening stock 10 Nos @ PHP100, PHP1000 inventory, balanced two opening GL entries; no test users, Withdrawal Slips, Stock Entries, invoices or billing batches. No restore drill performed.

**Narrow isolated implementation plan:** guarded Python script to run inside exact DEVELOPMENT Docker bench while pointing Frappe exclusively at `ccpc-integration2.localhost`; preflight confirms distinct DB identity from persistent `development.localhost`, all 40 protected artifacts and tenth snapshot identity/file sizes, reviewed `setup.py` Git blob, installed Frappe/ERPNext versions, target workflow and GL/Bin baseline, absent three fields in metadata and physical SQL columns, correct insertion anchors in core DocTypes, zero business documents. Call **only** `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()`. Verify each created Custom Field fieldtype/options/insert_after/read_only/hidden/no_copy and Frappe metadata, commit, then independently re-query SQL columns and persisted rows; require exactly +3 Custom Fields and no unexpected changes to watched records, ledger, users, permissions, workflow, or backup hashes. **Schema alterations may implicitly commit despite rollback**; failure requires stop, independent read-only inspection and recovery review, NEVER blind rerun or automatic restore. Post-commit independent audit required; report actual successful output to GitHub only after observed.

**Authorization scope excludes:** `bench migrate`, whole `after_migrate`, broad permission grants (Stockroom Personnel still lacks Stock Entry create/submit), test-user creation, Withdrawal Slip/Stock Entry/financial posting, changes to persistent DEVELOPMENT, and ANY PRODUCTION changes. This note records **approval and plan**, not a claim that fields have been installed.

## Tenth post-Workflow recovery checkpoint completed and verified — 2026-10-13

Owner ran the explicitly authorized **backup-only** command on **isolated `ccpc-integration2.localhost`** and reported a successful and independently checked in-command tenth site-private backup. Exact operator output includes:

```text
/home/gani/ccpc_tenth_backup_check.py: OK
ISOLATED SITE: VERIFIED
NINE EARLIER CHECKPOINTS: VERIFIED (36 FILES)
ACTIVE WITHDRAWAL SLIP WORKFLOW: VERIFIED
REQUESTOR SELF-APPROVAL: VERIFIED
OPENING STOCK 10 NOS / PHP 1,000 AND BALANCED GL: VERIFIED
NO UNRELATED TRANSACTIONS: VERIFIED
Backup Summary for ccpc-integration2.localhost at 2026-10-13 18:15:34.980785
Tenth snapshot prefix: 20261013_181534
All nine earlier checkpoints: PRESERVED
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
Post-backup Workflow, Opening Stock and GL baseline: VERIFIED
TENTH RECOVERY CHECKPOINT: VERIFIED AND SECURED
```

**Path:** `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-withdrawal-workflow-pre-stock-entry-fields-20261013/`. **Artifact prefix:** `20261013_181534-ccpc-integration2_localhost-`. **Verified file sizes:** `database.sql.gz` 984402 bytes, `files.tar` 10240 bytes, `private-files.tar` 10240 bytes, `site_config_backup.json` 212 bytes. The operator command checked database gzip and tar archive structures, backed-up site database identity, all 36 predecessor checkpoint file hashes preserved, and reaudited stock/GL and active Withdrawal Slip Workflow. Ten distinct site-private recovery sets are now preserved. **Archive-integrity and identity verification are not a restore drill; restoration remains untested.** All earlier checkpoints remain retained; no deletion/restoration.

**Preserved isolated baseline:** submitted synthetic Opening Stock `MAT-RECO-2026-00001`, stock Bin 10 Nos at PHP100 = PHP1000, one Stock Ledger Entry, two balanced GL Entries; active `CCPC Withdrawal Slip Workflow` with eight states/four transitions and the owner-approved requestor self-approval; no new business transactions, users or roles. All three Withdrawal Slip–Stock Entry provenance Custom Fields remain **not installed**. Stockroom Personnel still lacks independent Stock Entry create/submit permission, a separate security/code item for GitHub-first review.

**Next gated milestone:** design/inspect only the three Stock Entry/Detail provenance custom fields in `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()`, then seek **new explicit site-specific authorization** before any Frappe custom-field/schema operation. In MariaDB, schema DDL can implicitly commit, so guard site isolation and backed-up state, prepare recovery plan, and independently audit after. No full `bench migrate` or `after_migrate`; no persistent DEVELOPMENT or PRODUCTION operations. No test-user/role, Withdrawal Slip/Stock Entry, invoicing or billing write is authorized by tenth-backup approval. Current app review branch `review/intercompany-approval-failure-tests` verified HEAD `806fa23516490ec7beefcff03a1baa09d722120e`.

## Tenth protected isolated recovery checkpoint explicitly approved — 2026-10-13

Project owner **explicitly approved creation of a tenth recovery checkpoint only** on the isolated site `ccpc-integration2.localhost` after independent post-commit validation of the active self-approval `CCPC Withdrawal Slip Workflow`. This approval **does not authorize** schema changes, creating/editing users or roles, new Withdrawal Slips/Stock Entries/invoices/billing, any change to persistent `development.localhost` or PRODUCTION, `bench migrate`, full `after_migrate`, or restoring/deleting previous backups.

**Recovery target:** a new site-private, mode 0700 directory `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-withdrawal-workflow-pre-stock-entry-fields-20261013/`, containing the four uniquely timestamped `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path <new-directory>` files; minimum permissions 0600, gzip and tar archive integrity checks, site config database identity check. Preserve original nine checkpoints including ninth prefix `20261013_171109-ccpc-integration2_localhost` in `post-opening-stock-pre-withdrawal-slip-20261013`; compare SHA-256 of all 36 predecessor artifacts before and after. No restore drill has been performed.

**Guarded preconditions:** DB isolation from `development.localhost`, no symlink/occupied target, sufficient disk capacity; synthetic submitted reconciliation `MAT-RECO-2026-00001` with 10 Nos `CCPC-INT-TEST-CONSUMABLE-001` @ PHP100 in `Stores - TISS`, one Stock Ledger Entry, two balanced opening GL entries; exactly one active Withdrawal Slip Workflow (`status`, eight child states, four transitions, eight required state master records, four actions; owner-approved requestor self-approval); zero non-Administrator users and target role assignments, zero Withdrawal Slips, Stock Entries, Sales/Purchase Invoices, Intercompany Billing Batches and target Stock Entry provenance Custom Fields. After backup re-audit exact DB baseline and compare nine predecessors' SHA-256. **On any failure do not delete a partial checkpoint or rerun blindly; stop and inspect.**

**Status:** backup is **approved but NOT YET executed or verified**. Once operator shares terminal output, update this same GitHub handoff with actual timestamp/prefix/sizes, verification and commit, then plan next separately authorized Stock Entry schema-field operation. App review branch currently inspected `review/intercompany-approval-failure-tests` HEAD `806fa23516490ec7beefcff03a1baa09d722120e`.

## Withdrawal Slip Workflow independently verified after commit — 2026-10-13

The owner completed the separate **read-only MySQLdb post-commit audit** on isolated `ccpc-integration2.localhost` after the narrowly scoped workflow provisioning. Final output: **`WITHDRAWAL SLIP WORKFLOW POST-COMMIT AUDIT: VERIFIED`**, **`NO DATABASE CHANGES MADE`**. Database isolation and ninth protected recovery checkpoint verified.

**Persisted workflow:** exactly one active `CCPC Withdrawal Slip Workflow` for Withdrawal Slip with state field `status`; 8 Workflow Document State children and 4 Workflow Transition children, matching the GitHub `ccpcerp.setup.WORKFLOW_STATES` and `WORKFLOW_TRANSITIONS`; all state and action master records present. The owner-approved **requestor self-approval** is independently confirmed: `Draft → Approved` via **Approve & Send to Stockroom** allowed `Withdrawal Slip Requestor`; `Approved → Stockroom Review` via **Start Review** allowed `Stockroom Personnel`; `Stockroom Review → Returned for Correction` via **Return for Correction** allowed `Stockroom Personnel`; `Returned for Correction → Approved` via **Re-Approve** allowed `Withdrawal Slip Requestor`, limited to creator `approving_supervisor` condition. No unrelated MRS or Purchase Order workflow created.

**Isolation and accounting preserved:** no non-Administrator test users, no workflow role assignments, no Stock Entry/Stock Entry Detail provenance Custom Fields, no Withdrawal Slip, Stock Entry, Sales Invoice, Purchase Invoice, or Intercompany Material Billing Batch. Opening Stock `MAT-RECO-2026-00001` still submitted, one Bin of `CCPC-INT-TEST-CONSUMABLE-001` in `Stores - TISS` **10 Nos @ PHP100 = PHP1000**, one correct SLE, exactly two balanced opening GL entries. This milestone is **independently database-verified**, distinct from the pre-commit checks and owner-reported commit.

**Pending / next gated work:** workflow is configured, but no runtime user-authorization or material issue end-to-end test has happened. All 9 earlier backups preserved; ninth snapshot prefix `20261013_171109-ccpc-integration2_localhost` is **pre-workflow**, so consider a new uniquely named tenth site-private backup **before schema changes**, only after explicit owner approval. Review and separately authorize provisioning 3 provenance Custom Fields via only `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()`, with DB DDL/implicit-commit risk, exact site isolation and independent postcommit validation. Then separate permissions/API design for narrowly authorized Stockroom Material Issue (currently role Stockroom Personnel lacks Stock Entry create/submit), fictional test users and later business transaction tests, each separately gated. **No broad `bench migrate` / full `after_migrate()`, persistent DEVELOPMENT, or PRODUCTION action authorized.** Current reviewed app branch `review/intercompany-approval-failure-tests`, last verified HEAD `806fa23516490ec7beefcff03a1baa09d722120e`.

## Targeted Withdrawal Slip Workflow successfully committed; independent DB audit pending — 2026-10-13

Owner executed the corrected, previously authorized workflow-only Frappe setup command on isolated `ccpc-integration2.localhost`. Operator reported site/backup/code verified, opening-stock and GL baseline verified, existing Workflow baseline verified, and requestor self-approval policy verified. It called only `ccpcerp.setup.ensure_withdrawal_slip_workflow()` and printed:

```text
WORKFLOW: CCPC Withdrawal Slip Workflow
Workflow status: ACTIVE
Workflow states: 8
Workflow transitions: 4
Requestor self-approval: VERIFIED
Users and role assignments: UNCHANGED
Stock Entry integration fields: UNCHANGED
Opening Stock and GL: UNCHANGED
WORKFLOW PRE-COMMIT CHECKS: PASSED
WITHDRAWAL SLIP WORKFLOW: COMMITTED AND VERIFIED
```

**Status:** owner-reported successful committed transaction with in-session pre-commit validation; **separate independent post-commit database audit still pending**. Current reviewed app branch remains `review/intercompany-approval-failure-tests`, at inspected HEAD `806fa23516490ec7beefcff03a1baa09d722120e` (verified `setup.py` Git blob `915e0109a508d503384b227de864ef318fa6ed8c`). The earlier first attempt failed before setup due to `frappe.db.sql()` tuple/list mismatch; independent DB audit verified no changes from that attempt. Corrected script normalized SQL rows and passed.

**Next authorized read-only step:** separately query isolated persisted DB using `MySQLdb` in `START TRANSACTION READ ONLY`, revalidate target vs persistent DEVELOPMENT DB identity and ninth snapshot path, verify exactly one active Withdrawal Slip Workflow, eight child states and four child transitions matching approved self-approval policy, all eight expected Workflow State masters/four Action Masters, untouched user/role and Stock Entry custom fields, and persisted single opening reconciliation, 10 Nos at PHP100 in Bin, SLE and two balanced GL entries, no Withdrawal Slip, Stock Entry, invoice or billing transactions. Update GitHub with exact independent audit result. Do **not** rerun the now-committed workflow creation command. No authorization exists to provision stock-entry schema fields, users, additional permissions, business transactions or other site operations. Full `bench migrate`, `after_migrate()`, persistent `development.localhost`, and PRODUCTION remain out of scope.

## Independent rollback audit confirms SQL comparison defect — 2026-10-13

Owner ran the separate read-only verification after the first narrow Workflow setup command stopped before invoking its setup function. Audit reported `WORKFLOW ATTEMPT ROLLBACK: VERIFIED`, `OPENING STOCK AND GL: PRESERVED`, `NO DATABASE CHANGES MADE`. The exact Stock Reconciliation row `MAT-RECO-2026-00001` is correct; Frappe SQL returned a tuple of tuples. Comparison against a list of tuples incorrectly failed (`Old list comparison: False`; `Normalized comparison: True`). This confirms the error was in the verification script, not the persisted Opening Stock.

The isolated site retains one submitted Stock Reconciliation, one Bin (10 Nos, PHP100 rate and PHP1000 stock value), one Stock Ledger Entry with quantity after 10, balanced two GL entries at PHP1000 each, zero Withdrawal Slips/Stock Entries/invoices/billing batches; no Withdrawal Slip Workflow, only pre-existing Approved state, none of the four Workflow Action Masters. Ninth checkpoint remains verified. No setup function was run, no workflow transaction committed.

Correct *all* row-container comparisons before retry; do not change the stock baseline. The previously approved workflow-only operation on `ccpc-integration2.localhost` remains authorized. The guarded retry should run only `ccpcerp.setup.ensure_withdrawal_slip_workflow()` after proving site isolation and unchanged records, check one active workflow, eight Workflow Document State rows, four transitions, seven new Workflow State master records, four new action masters, no other database changes, then single commit. Independently audit postcommit. No broader migration, user/role/configuration/schema or business transaction changes, and no persistent DEVELOPMENT or PRODUCTION modifications.

## First scoped Workflow setup attempt stopped at Python SQL row-container mismatch — 2026-10-13

The owner ran the previously approved, guarded, isolated-site-only `ccpcerp.setup.ensure_withdrawal_slip_workflow()` command and pasted terminal output. The preflight printed:
```text
ISOLATED SITE: VERIFIED
NINTH RECOVERY CHECKPOINT: VERIFIED
GITHUB-REVIEWED SETUP CODE: VERIFIED
WORKFLOW SETUP STOPPED: RuntimeError Opening Stock document baseline changed.
Database rollback requested.
Independently inspect persisted state before any retry.
```

The failure occurred **BEFORE** the code path invoking `setup.ensure_withdrawal_slip_workflow()`, at `require(db.sql("SELECT ... FROM tabStock Reconciliation") == [(expected_row)], "Opening Stock document baseline changed.")`. The baseline was independently verified in the preceding milestone and no alteration to the reconciliation has been shown. **Most likely root cause is verification code using list-of-tuples equality for Frappe `frappe.db.sql()` default output, which is normally a tuple of tuples** (the previous succeeding preflight explicitly applied `tuple(db.sql(...))`). Frappe `v16.33.1` `frappe/database/database.py::Database.sql` returns its cursor's `fetchall()` output unchanged by default (unless `as_list` or `as_dict` requested); a tuple of tuples never equals `[(...)]`, even if values are correct. Other later comparisons in this same script have the same bug; correct ALL SQL row comparisons before retry. There was no `WORKFLOW: ...` or `WORKFLOW ... COMMITTED` output; the exception handler invoked `frappe.db.rollback()`. **Do not claim independent rollback/database state verified until a separate read-only audit is run.** No rollback or restore action is authorized.

**Next action: read-only isolated DB audit** with DB identity check against `development.localhost` and ninth backed-up config identity, show the exact `Stock Reconciliation` row and `frappe.db.sql()` returned Python row-container type, assert expected stock reconciliation, Bin 10/100/1000, SLE, balanced two-row GL, and **zero Workflow document for Withdrawal Slip, no new Workflow State/Action Master rows, zero Withdrawal Slip/Stock Entry and absent provenance custom fields**. If confirmed no writes persisted, repair the script's row-container comparisons (use `tuple(db.sql(...)) == (expected_row,)` or `as_dict=True`) and review whether `db.sql(FOR UPDATE)` comparisons require same correction. Only then run the previously authorized narrow workflow setup; post-commit independently audit. Never run `after_migrate` or `bench migrate`. Ninth checkpoint `20261013_171109-ccpc-integration2_localhost-*` must remain protected, and no transaction/user/role/other-schema write authorized.

## Owner authorizes only targeted isolated Withdrawal Slip Workflow provisioning — 2026-10-13

The owner **explicitly approved only** provisioning the existing `CCPC Withdrawal Slip Workflow` on isolated `ccpc-integration2.localhost`; permission scope excludes broad migrations, user creation, stock-entry permissions or custom schema fields, Withdrawal Slips, Stock Entries, invoices, billing, changes to persistent `development.localhost` and any PRODUCTION changes. Current policy **requestor self-approval permitted** per existing reviewed `ccpcerp.setup.WORKFLOW_TRANSITIONS` (Draft → Approved by Withdrawal Slip Requestor; Approved → Stockroom Review by Stockroom Personnel). No custom app code changes requested.

Prior isolated site diagnostics found installed `ccpcerp/setup.py` and `ccpcerp/hooks.py` match GitHub review branch `review/intercompany-approval-failure-tests` (`setup.py` blob SHA `915e0109a508d503384b227de864ef318fa6ed8c`), but **no Workflow for Withdrawal Slip**, only existing Workflow State `Approved`, no four workflow action masters, no three Stock Entry custom provenance fields. Ninth protected site-private recovery checkpoint is verified at `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-opening-stock-pre-withdrawal-slip-20261013/`, prefix `20261013_171109-ccpc-integration2_localhost`, and all earlier eight snapshots preserved. Submitted `MAT-RECO-2026-00001` with 10 Nos @ PHP100 (Bin PHP1000) and two balanced GL entries verified; no new inventory transactions.

**Narrow next operation, NOT YET EXECUTED:** verify isolated target database name distinct from persistent DEVELOPMENT, existing ninth backup identity/files, exact installed setup source blob, expected baseline and no Workflow for Withdrawal Slip, all four role definitions and status field metadata. Call **only** `ccpcerp.setup.ensure_withdrawal_slip_workflow()` using the isolated site's Frappe context and administrator permissions (not `ccpcerp.setup.after_migrate()` and not `bench migrate`). Expected insert: **one** `CCPC Withdrawal Slip Workflow`, **seven** new Workflow State records (since Approved already exists) and **four** Workflow Action Master records, with **eight** attached workflow states and **four** transitions. Its Frappe v16.33.1 `Workflow.on_update()` can create a Custom Field only when workflow state field is absent; `Withdrawal Slip.status` already exists as a read-only Select so this branch should not create schema changes. Guard zero preexisting Withdrawal Slips; workflow may initialize empty status values, but none exist. Check that Custom Field and user counts remain unchanged, and no Stock Entry fields or business ledger mutations occurred. Commit only after inspection; rollback on failure and independently inspect before rerun. After user reports output, conduct independent postcommit read-only audit and update GitHub handoff with actual confirmed results. This approval does **not** authorize workflow setup on other sites, or test users/transactions.

## Isolated Stock Entry permissions audit: stockroom has no create/submit rights — 2026-10-13

Owner posted the read-only permission audit from isolated `ccpc-integration2.localhost`, with ninth protected backup DB identity verified and **NO DATABASE CHANGES MADE**. The audit enumerated `tabDocPerm` and `tabCustom DocPerm` for Withdrawal Slip, Stock Entry and selected reference DocTypes. **No matching `tabCustom DocPerm` rows** in this selection. Key `tabDocPerm` rows:
- `Withdrawal Slip`: `Withdrawal Slip Requestor` read/write/create=1, submit=0, if_owner=1; `Stockroom Personnel` read/write=1, create/submit=0; `Maintenance Supervisor` and `System Manager` read/write/create=1.
- `Stock Entry`: `Stock User` and `Stock Manager` each read/write/create/submit=1; **no Stock Entry create/submit permission for `Stockroom Personnel`, `Withdrawal Slip Requestor`, or `Maintenance Supervisor`** in inspected DocPerm/Custom DocPerm.
- Stockroom role reference DocType permissions were not materialized through `tabCustom DocPerm`; `ccpcerp.setup.ensure_stockroom_personnel_permissions()` would provision other reference rights but **does not itself give Stock Entry** creation/submit.
- Stock Entry/Detail Withdrawal Slip integration Custom Fields still absent.
- Record counts unchanged from post-opening-stock baseline: 1 submitted Stock Reconciliation, 1 Bin, 1 Stock Ledger Entry, 2 GL Entries; 0 Withdrawal Slips, 0 Stock Entries.

**GitHub code review on app review branch `review/intercompany-approval-failure-tests` at HEAD `806fa23516490ec7beefcff03a1baa09d722120e`:** `ccpcerp/ccpc_erp/withdrawal_slip_stock.py::make_material_issue` checks `_require_stockroom_user()` and `slip.check_permission("write")`, requires `Stockroom Review` and `received_by`, enforces item provenance, qty/shortage, creates a `Stock Entry` `purpose=Material Issue`, and calls `stock_entry.insert()` with normal logged-in permissions (no `ignore_permissions`). Dedicated Stockroom Personnel **cannot create** via this endpoint if they lack an additional Stock Entry role. Stock Entry submission also requires appropriate separate authorization. Simply assigning `Stock User` or `Stock Manager` introduces broader inventory privileges and should **not** be the default workaround. Security-sensitive remedy should be designed, reviewed, and implemented in GitHub first before isolated site deployment: narrow server-side stockroom issuance API confined to the linked approved Withdrawal Slip, strict role and slip access checks, one-time/atomic stock posting and duplicate prevention under concurrency, warehouse/company/item/qty validation, reliable rollback and audit. Consider approval for code change separately. No application code was changed during this audit.

**Project-owner policy remains confirmed**: requestor self-approval is allowed; no distinct supervisor approval is mandatory. Workflow/master/action and Stock Entry provenance fields are still missing; no non-Administrator test users exist. Existing reviewed setup functions `ccpcerp.setup.ensure_withdrawal_slip_workflow()` and `ensure_withdrawal_slip_stock_entry_fields()` are candidates for narrowly scoped isolated setup, **subject to separate owner authorization**, not full `bench migrate` or `after_migrate()`. Custom Field schema updates may involve non-transactional DDL; preserve ninth checkpoint and check exact target site identity. Keep business transaction creation separately authorized. Neither persistent DEVELOPMENT nor PRODUCTION was modified.

## Owner confirms Withdrawal Slip requestor self-approval; isolated setup plan — 2026-10-13

**Confirmed project-owner decision:** CCPC Withdrawal Slip **requestor self-approval is permitted**, as currently designed on app review branch `review/intercompany-approval-failure-tests` HEAD `806fa23516490ec7beefcff03a1baa09d722120e`. The owner requested an **isolated test environment workflow setup plan**, not a PRODUCTION deployment or broad site migration. No approval-policy code change is necessary.

**Approved policy/actual flow:** `ccpcerp/setup.py` `WORKFLOW_TRANSITIONS` assigns `Draft → Approved` ("Approve & Send to Stockroom") to **Withdrawal Slip Requestor** with `allow_self_approval=1`; `Approved → Stockroom Review` ("Start Review") to **Stockroom Personnel**. Stockroom can return a review for correction, and the requestor can re-approve under the code's permitted conditions. `Withdrawal Slip.approving_supervisor` is actually labeled **Prepared By**, auto-filled with current session user on initial save; it is **not** a distinct supervisor sign-off. Stock issuance via `withdrawal_slip_stock.py` separately requires **Stockroom Review**, `received_by`, stockroom role/authorization and a valid material issue. Avoid describing the approved process as independent supervisor approval. Distinct role-permission testing is still required even though self-approval is allowed.

**Current isolated test-site technical facts:** both `ccpcerp/setup.py` and `ccpcerp/hooks.py` installed file hashes match GitHub, but `tabWorkflow` has no Withdrawal Slip workflow (or MRS or Purchase Order workflow), only state `Approved` exists of expected states, none of four Withdrawal Slip Workflow Action Master records exist, and all three Stock Entry/Detail custom provenance fields are missing. `Withdrawal Slip.status` is a read-only Select. 0 non-Administrator users, 0 role assignments for Workflow Requestor / Maintenance Supervisor / Stockroom Personnel, 0 active CCPC Personnel, 0 `Operations - TREQ` sections. Existing fixture Bin has **10 Nos / PHP100 / PHP1000** plus independently verified submitted Opening Stock `MAT-RECO-2026-00001` and balanced GL. Ninth fully archived pre-Withdrawal Slip recovery checkpoint `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-opening-stock-pre-withdrawal-slip-20261013/20261013_171109-ccpc-integration2_localhost-*` and prior eight preserved (format checked, no restore drill).

**Proposed narrow isolated setup sequence, subject to separately authorized writes:**
1. Read-only inspection of *effective* Stock Entry create/submit and reference-DocType permissions for Stockroom Personnel vs Withdrawal Slip Requestor (`tabDocPerm`, `tabCustom DocPerm`, role-profiles / system role inheritance), plus installed and DB schema checks. The setup's `ensure_stockroom_personnel_permissions` intentionally does **not** list Stock Entry rights, while `withdrawal_slip_stock.make_material_issue()` uses `stock_entry.insert()` under active user; this could block real stockroom issuance unless another controlled role authorizes it. Confirm before proposing permission writes. Also confirm no existing Workflow or conflicting Custom Fields/Property Setters.
2. With separate explicit site-specific approval, preserve ninth backup; provision only `CCPC Withdrawal Slip Workflow` via `ccpcerp.setup.ensure_withdrawal_slip_workflow()` and necessary Workflow State/Action master records. This is an isolated database change. Do **not** run full `bench migrate` or full `ccpcerp.setup.after_migrate()`; they modify many other modules.
3. In a separate gated step, provision only the three required Stock Entry/Detail provenance Custom Fields via `ccpcerp.setup.ensure_withdrawal_slip_stock_entry_fields()` and verify SQL schema and Frappe metadata. **MariaDB DDL can implicitly commit**, so do not promise that creating Custom Fields/ALTER TABLE is fully reversible with a transaction rollback; prefer checkpoint-based recoverability, no automatic restore.
4. After verifying Workflow and fields, with a further approval, create at most two synthetic test Users on isolated site (requestor and stockroom), no external emails or real credentials; assign only necessary approved roles and test permissions under those identities. Note `ccpcerp.setup.ensure_operational_requestor_roles_on_user` may auto-append `Withdrawal Slip Requestor` when granting `Stockroom Personnel`; inspect role inheritance/effective permissions and do not assert roles are strictly separate.
5. With separately authorized business writes, create **one** fictional Draft Withdrawal Slip for requester company TREQ / department `Operations - TREQ`, issuer company TISS / `Stores - TISS`, one Item `CCPC-INT-TEST-CONSUMABLE-001` for a limited quantity <= 10, with fictional requestor/purpose/location, and exercise permitted self-approval and Stockroom Review transitions; check unauthorized user behavior. **Do not** post a Material Issue, Stock Entry, invoice or billing batch without distinct authorization and another checkpoint appropriate to the next milestone. Audit after each persisted mutation and record actual results back into GitHub.

**Authorization distinction:** owner approved **policy and planning** here. No workflow, Stock Entry schema, roles, test Users or Withdrawal Slip mutations executed or independently authorized by this planning step. No persistent `development.localhost` or PRODUCTION operations.

## Isolated Withdrawal Slip workflow setup incomplete despite matching setup code — 2026-10-13

Owner completed independent READ-ONLY diagnostic on `ccpc-integration2.localhost`, after ninth backup, with no database writes. Output:

```text
ISOLATED SITE: VERIFIED
INSTALLED WORKFLOW SETUP CODE
apps/ccpcerp/ccpcerp/setup.py MATCH
apps/ccpcerp/ccpcerp/hooks.py MATCH
CONFIGURED WORKFLOWS
[none for Withdrawal Slip, MRS, Purchase Order]
WITHDRAWAL SLIP WORKFLOW STATES
('Approved',)
WITHDRAWAL SLIP WORKFLOW ACTIONS
[none]
STOCK ENTRY INTEGRATION FIELDS
[none]
WITHDRAWAL SLIP STATUS METADATA
('status', 'Select', 1)
WORKFLOW SETUP DIAGNOSTIC: COMPLETED
NO DATABASE CHANGES MADE
```

**Conclusion:** installed setup and hooks files match GitHub review branch `review/intercompany-approval-failure-tests` HEAD `806fa23516490ec7beefcff03a1baa09d722120e`, but their intended setup effects are **absent in test-site database**. In `ccpcerp/setup.py`, `ensure_withdrawal_slip_workflow()` (called by `after_migrate()`) creates Workflow master, Workflow State, Workflow Action Master rows and transitions. `ensure_withdrawal_slip_stock_entry_fields()` creates `Stock Entry.withdrawal_slip`, `Stock Entry.withdrawal_slip_issued_by` and `Stock Entry Detail.withdrawal_slip_item` fields. All three fields missing. Current `Withdrawal Slip.status` is a read-only Select, so absence of active workflow blocks intended UI state transitions. No Workflow for MRS or Purchase Order either, so likely broader partial setup; reason not yet proven. Full `bench migrate` or entire `after_migrate()` is **not** authorized and can produce many unrelated writes.

Prior audit also found 0 non-Administrator Users, 0 role assignments for Withdrawal Slip Requestor, Maintenance Supervisor, Stockroom Personnel, 0 CCPC Personnel, 0 sections under Operations - TREQ; four role definitions enabled. Ninth protected pre-Withdrawal Slip backup archived with prefix `20261013_171109-ccpc-integration2_localhost` and earlier eight preserved. Posted stock baseline 10 Nos × PHP100 with one opening reconciliation and two balanced GL entries remains protected.

**Owner decision required before targeted workflow provisioning or user creation:** existing GitHub `WORKFLOW_TRANSITIONS` permits requestor self-approval on Draft → Approved (`allow_self_approval=1`, `allowed=Withdrawal Slip Requestor`), with Stockroom Personnel completing Approved → Stockroom Review. `approving_supervisor` is labeled `Prepared By` and automatically set to creating session user, not independent supervisor approval. Should intended CCPC controls permit requestor self-approval or require a **different supervisor**? Once policy is clarified, review/modify authorized GitHub code first if necessary, and separately obtain explicit approval for narrowly scoped isolated setup writes (workflow, integration fields, test users/roles). No changes to persistent DEVELOPMENT or PRODUCTION, no Stock Entry/Withdrawal Slip/financial transaction yet.

## Withdrawal Slip role preflight: no test users and missing expected Workflow — 2026-10-13

The operator completed read-only isolated test site role and workflow audit, `WITHDRAWAL SLIP ROLE READINESS: AUDIT COMPLETED` and `NO DATABASE CHANGES MADE`. Site `ccpc-integration2.localhost` and ninth post-opening-stock checkpoint verified. All four roles exist and are enabled (`Withdrawal Slip Requestor`, `Maintenance Supervisor`, `Stockroom Personnel`, `System Manager`). Role assignments: **0, 0, 0, 1** respectively. There are **zero non-Administrator users**, zero active `CCPC Personnel`, zero enabled `CCPC Section` for `Operations - TREQ`, and **no `tabWorkflow` document for Withdrawal Slip**. `tabDocPerm` provides Withdrawal Slip Requestor/Maintenance Supervisor/System Manager read/write/create, Stockroom Personnel read/write only. The Bin remains 10 Nos / PHP 100 / PHP 1000 and Withdrawal Slip, Stock Entry, Purchase/Sales Invoice and Billing Batch counts remain zero.

**Critical GitHub source discrepancy discovered:** review branch `review/intercompany-approval-failure-tests` app `ccpcerp/setup.py` defines `WITHDRAWAL_SLIP_WORKFLOW = "CCPC Withdrawal Slip Workflow"`, `WORKFLOW_STATES` and `WORKFLOW_TRANSITIONS` and `ensure_withdrawal_slip_workflow()`, which is called by `ccpcerp.setup.after_migrate()` from `ccpcerp/hooks.py`. However target site's read-only DB returns **no Workflow record** for Withdrawal Slip. Before any write, check **actual installed** `setup.py` and `hooks.py` blobs and metadata against this review branch, plus whether Workflow State/Action master records and the Stock Entry custom link fields are present. Do not assume all `after_migrate` operations ran and do **not** run a broad `bench migrate` or `after_migrate()` to repair a single fixture; it performs many unrelated writes.

**Workflow policy choice:** GitHub `WORKFLOW_TRANSITIONS` currently allows `Withdrawal Slip Requestor` to transition `Draft → Approved` via "Approve & Send to Stockroom" with `allow_self_approval=1`, then Stockroom Personnel `Approved → Stockroom Review`. Return for correction is handled by Stockroom Personnel. The `approving_supervisor` database field is labeled **Prepared By** and `WithdrawalSlip.before_validate()` automatically sets it to the creating session user. Consequently, creating a separate `Maintenance Supervisor` test account does **not** by itself enforce independent approval. Do not describe the existing workflow as a three-person approval chain or mark segregation-of-duties tested; ask owner to choose intended approval policy before changing workflow or roles. `Withdrawal Slip.status` is a read-only Select field in reviewed DocType, so absence of the configured Frappe Workflow is significant.

**Scope/next step:** READ ONLY diagnostic of installed `setup.py` and `hooks.py` Git blobs and absence/presence of Workflow, Workflow State and Workflow Action Master references, after site DB isolation guard. Preserve ninth checkpoint and all eight predecessors. No authorization to create users, role assignments, CCPC Personnel, workflow, Withdrawal Slips, Stock Entries, invoices or intercompany billing; persistent DEVELOPMENT/PRODUCTION untouched.

## Read-only Withdrawal Slip preflight: code matches, required test roles unassigned — 2026-10-13

Owner ran the requested read-only test-site inspection after ninth protected backup. Output on **isolated ccpc-integration2.localhost**:

```text
ISOLATED SITE: VERIFIED
NINTH RECOVERY CHECKPOINT: VERIFIED
CUSTOM APPLICATION CODE COMPARISON
doctype/withdrawal_slip/withdrawal_slip.py : MATCH
withdrawal_slip_stock.py : MATCH
WITHDRAWAL SLIP METADATA
('Withdrawal Slip', 0)
('Withdrawal Slip Item', 0)
REQUEST CONTEXT
Requesting Department: (('Operations - TREQ', 'Integration Test Requester', 0, 0),)
Issuing Warehouse: (('Stores - TISS', 'Integration Test Issuer', 0, 0),)
REQUIRED WITHDRAWAL SLIP FIELDS
('requestor', 1)
('required_by', 1)
('approving_supervisor', 1)
('company', 1)
('source_warehouse', 1)
('requesting_company', 1)
('department', 1)
('physical_location', 1)
('purpose', 1)
('items', 1)
USER ROLE ASSIGNMENT COUNTS
[no rows]
INVENTORY AVAILABLE FOR FUTURE TEST
('CCPC-INT-TEST-CONSUMABLE-001', 'Stores - TISS', 10, 100, 1000)
EXISTING WORKFLOW DOCUMENT COUNTS
tabWithdrawal Slip 0
tabStock Entry 0
tabIntercompany Material Billing Batch 0
tabSales Invoice 0
tabPurchase Invoice 0
INSTALLED APPLICATION MATCH: YES
WITHDRAWAL SLIP READ-ONLY PREFLIGHT: COMPLETED
```

Files were compared by installed Git blob hashes with app review branch `review/intercompany-approval-failure-tests` commit `806fa23516490ec7beefcff03a1baa09d722120e`, and **both match**. `Withdrawal Slip` and `Withdrawal Slip Item` installed as non-custom doctypes, correct issuing/requesting company reference fixtures. Empty role-assignment result means **no `tabHas Role` User assignment for `Withdrawal Slip Requestor`, `Maintenance Supervisor`, or `Stockroom Personnel`**, not proof the `tabRole` definitions are absent. Inventory still 10 Nos and no new transactional documents.

Github source inspection: `WithdrawalSlip.before_validate` sets `approving_supervisor` from current session user upon new request and defaults request context as appropriate. Document required fields include requester, supervisor, required-by, company, source warehouse, requesting company, department, physical location, purpose, items. `_validate_section_requirement` requires section only when active CCPC Sections exist under the department. `_validate_requested_quantities` rejects total draft requested quantity greater than current Bin availability. `withdrawal_slip_stock.make_material_issue` accepts only `Stockroom Review` and requires `received_by` plus stockroom role (or privileged Administrator/System Manager); separately authorized stock issuance needed. Creating using Administrator would bypass a meaningful permission test.

**Next step only READ-ONLY:** inspect presence of Role definitions, enabled non-Administrator user counts and assignments, Supervisor/Requestor/Stockroom DocPerm rows, active CCPC Personnel and CCPC Sections, Workflow records/transition availability, and current snapshot/item count without outputting user identities or credentials. Then agree on controlled isolated test-user/role fixture and draft Withdrawal Slip scope and obtain separate owner approval before any mutation. Ninth archive-verified snapshot `post-opening-stock-pre-withdrawal-slip-20261013/20261013_171109-ccpc-integration2_localhost-*` preserved; no restore drill. No authorization to create users, roles, Withdrawal Slip, Stock Entry, invoice, or change persistent DEVELOPMENT/PRODUCTION.

## Ninth isolated post-opening-stock checkpoint completed and verified — 2026-10-13

Operator completed the **owner-authorized ninth backup-only checkpoint** for isolated `ccpc-integration2.localhost`. Output confirms preflight: `Isolated test site: VERIFIED`, `Eight previous recovery checkpoints: VERIFIED`, TISS/TREQ Moving Average, submitted first Opening Stock `MAT-RECO-2026-00001`, stock Bin **10 Nos / PHP 1,000**, one Stock Ledger, and balanced opening GL, with no unrelated transactions. All eight predecessors were SHA-256 hashed and verified unchanged again after the backup.

**Ninth backup timestamp:** 2026-10-13 **17:11:10.715288** Asia/Manila. **Site-only directory:** `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-opening-stock-pre-withdrawal-slip-20261013/`; **artifact prefix:** `20261013_171109-ccpc-integration2_localhost`. Operator-verified file sizes: `database.sql.gz` **983175 bytes**; `files.tar` **10240 bytes**; `private-files.tar` **10240 bytes**; `site_config_backup.json` **212 bytes**. `gzip -t`, both `tar -tf` checks and backed-up DB identity matched; output ended **`NINTH RECOVERY CHECKPOINT: VERIFIED AND SECURED`**. The posted stock and balanced GL baseline was reaudited after backup. **Nine archived checkpoints exist and prior eight preserved; full recovery restoration is still untested.** Ninth created no inventory or GL transactions, no Withdrawal Slip or invoice, and affected no other site.

**Next phase is NOT authorized to create new business transactions yet.** GitHub active app review branch `review/intercompany-approval-failure-tests` at inspected HEAD `806fa23516490ec7beefcff03a1baa09d722120e`. Inspection of `ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.py`, Withdrawal Slip/item DocType JSON and `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` confirms required requester, supervisor, required-by, company, requesting company, source warehouse, requesting department, physical location, purpose and item rows, with a section required when configured; the stock issue helper accepts only state `Stockroom Review` and requires stockroom role and `received_by`. The next **read-only** activity may check installed app commit, actual metadata/roles and fixture reference records on the isolated test site to design a minimal synthetic Withdrawal Slip test, after which obtain explicit authorization for any write. No Stock Entry/Material Issue or billing authorized, no persistent DEVELOPMENT or PRODUCTION modifications.

## Ninth test-site backup approved after independent opening-stock audit — 2026-10-13

The owner explicitly approved the **ninth recovery checkpoint only** on `ccpc-integration2.localhost`. It must capture the post-opening-stock baseline independently verified earlier (submitted `MAT-RECO-2026-00001`, 10 Nos of `CCPC-INT-TEST-CONSUMABLE-001` in `Stores - TISS` at PHP 100 each, inventory value PHP 1,000, one Stock Ledger Entry at qty after 10 and two opening GL rows balancing PHP 1,000 each). The Item still inherits Moving Average, and prior audit found no unrelated transactions.

Next: use site-only guarded backup after independent baseline checks and eight predecessor artifact checks; save four files in `private/ccpc-test-snapshots/post-opening-stock-pre-withdrawal-slip-20261013/`; verify archives and correct test database identity; keep all prior backups. Owner has **not** authorized new stock or billing documents, persistent DEVELOPMENT or PRODUCTION changes. Ninth backup not yet executed or confirmed.

## Opening Stock integration milestone independently verified after commit — 2026-10-13

Operator completed the separate read-only MySQLdb post-commit audit of **isolated ccpc-integration2.localhost**, verified DB identity distinct from persistent `development.localhost`, following successful standard Frappe insert/submit of the sole authorized synthetic opening-stock reconciliation. Final operator result: `OPENING STOCK POST-COMMIT AUDIT: VERIFIED`.

**Persisted records independently verified**:
- `Stock Reconciliation` **MAT-RECO-2026-00001**, `docstatus=1`, purpose `Opening Stock`, company `Integration Test Issuer`, posting date **2026-10-13**, posting time **16:59:56**, difference account `Temporary Opening - TISS`, cost center `Main - TISS`.
- Exactly one `Stock Reconciliation Item` child, name `vjpl3g6kjf`, item `CCPC-INT-TEST-CONSUMABLE-001`, warehouse `Stores - TISS`, quantity **10 Nos**, valuation rate **PHP 100**.
- Exactly one `Bin`: `Stores - TISS`, item, `actual_qty=10`, `valuation_rate=100`, `stock_value=1000`.
- Exactly one active `Stock Ledger Entry` for this voucher/child item, `actual_qty=0` (normal ERPNext 16.34.2 reconciliation behavior), `qty_after_transaction=10`, `valuation_rate=100`, `stock_value=1000`, `stock_value_difference=1000`, `is_cancelled=0`.
- Exactly two uncancelled `GL Entry` rows with `is_opening=Yes`, company TISS, cost center Main - TISS: **Debit `Stock In Hand - TISS` PHP 1,000** and **Credit `Temporary Opening - TISS` PHP 1,000**. Total debit equals total credit, PHP 1,000 each.
- Test Companies `Integration Test Issuer` and `Integration Test Requester`, plus global Stock Settings, persist **Moving Average**; synthetic Item valuation override blank.
- Master count invariants: 2 Companies, 198 Accounts, 1 Customer, 1 Supplier, 1 Item, 2 Party Accounts, 2 Allowed To Transact With.
- **Zero unrelated transactions**: Item Price, Stock Entry, Repost Item Valuation, Withdrawal Slip, Sales Invoice, Purchase Invoice, Intercompany Material Billing Batch. No duplicate reconciliation / SLE / GL records.

**Milestone status:** The synthetic opening-stock inventory-plus-perpetual-GL scenario is **independently database-integration verified**, NOT a full approval/material issue/intercompany billing test nor a PRODUCTION-readiness claim. Both prior failed attempts were correctly isolated and separately verified rolled back before this successful posting. ERPNext/Frappe installed versions last verified ERPNext **16.34.2**, Frappe **16.33.1**. The eighth protected recovery checkpoint `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-moving-average-pre-opening-stock-20261013/20261013_163228-ccpc-integration2_localhost-*` remains a **pre-stock** checkpoint; the prior seven archives are also preserved. Archive structure/database identity verified for all eight, **no restoration drill**, and **no post-stock checkpoint yet**.

**Next recommended gated work:** seek explicit owner approval to create a ninth *site-private post-opening-stock/pre-Withdrawal Slip* recovery checkpoint, preserve eight earlier sets, validate site isolation, existing single submitted reconciliation, Bin 10, one SLE, balanced two-entry GL, no subsequent transaction. Before a synthetic Withdrawal Slip test review current custom app review-branch code, installed app alignment, permission gates, department/requestor/supervisor fields, cross-company state transitions, stockroom role; use safe isolated test only, approvals and subsequent Stock Entry/Billing Batch each remain separately gated. Do not alter persistent `development.localhost` or PRODUCTION. No new code changes were made.

## First opening stock posted successfully; separate persistence audit pending — 2026-10-13

Owner executed the corrected guarded ERPNext Stock Reconciliation posting command on isolated `ccpc-integration2.localhost` after independently verifying rollback of an earlier assertion-only failure, and verified the eighth private pre-stock backup. The script validated identical Company/Item/warehouse/accounts, `Moving Average` for TISS and TREQ, and zero initial stock/financial entries, then inserted and submitted **exactly one** synthetic `Opening Stock` document through standard Frappe APIs.

**Operator-reported successful result (in-session checks before one database commit):**
```text
Posting date: 2026-10-13
Posting time: 16:59:56
Reconciliation: MAT-RECO-2026-00001
Document Status: SUBMITTED
Bin: CCPC-INT-TEST-CONSUMABLE-001 / Stores - TISS / actual_qty 10 / valuation_rate 100 / stock_value 1000
SLE: company Integration Test Issuer; voucher_detail_no vjpl3g6kjf; actual_qty 0; qty_after_transaction 10; valuation_rate 100; stock_value 1000; stock_value_difference 1000; is_cancelled 0
GL: Stock In Hand - TISS (Main - TISS) debit 1000 credit 0 is_opening Yes is_cancelled 0
GL: Temporary Opening - TISS (Main - TISS) debit 0 credit 1000 is_opening Yes is_cancelled 0
GL Balance: VERIFIED
Unrelated documents: NONE
ALL PRE-COMMIT CHECKS: PASSED
OPENING STOCK: COMMITTED AND VERIFIED
```

The operator output reports **successful `frappe.db.commit()`**, with 10 Nos × PHP 100 = PHP 1,000 synthetic inventory. Distinguish this from **independent persistence audit, still pending**. Crucial ERPNext 16.34.2 reconciliation behavior: SLE `actual_qty=0` is expected while `qty_after_transaction=10` reflects the updated balance; previous script incorrectly checked `actual_qty==10` and rolled back.

**Next safe step:** independent read-only MySQLdb session with target DB-identity guard vs persistent `development.localhost`, check the one submitted `MAT-RECO-2026-00001` and exact Item row, one Bin at 10/100/1000, one active SLE at 0/10/100/1000/1000, exactly two active opening GL entries for only that voucher and exact 1000 inventory debit/temporary credit, all master counts unchanged, TISS/TREQ/global Moving Average, item override blank, no unrelated Stock Entry/Withdrawal Slip/invoices/batch/repost. Do not recreate or rerun the opening reconciliation now that the script reports committed. After independently confirmed persistence, update the same GitHub handoff with actual audit outcome and next milestone. All eight private checkpoints were archive-verified, last one captured **pre-stock**; no restoration drill and no post-stock checkpoint. PRODUCTION and persistent DEVELOPMENT untouched.

## Opening-stock rollback independently verified; retry remains within approval — 2026-10-13

Owner ran the independent, read-only post-failure audit of isolated ccpc-integration2.localhost and reported **ROLLBACK VERIFIED: NO STOCK POSTING PERSISTED**. TISS and TREQ persisted Moving Average; global Stock Settings Moving Average; synthetic Item CCPC-INT-TEST-CONSUMABLE-001 override blank, is_stock_item=1 and disabled=0. Master counts remain two Companies, 198 Accounts, one Customer, one Supplier, one Item, two Party Accounts and two Allowed To Transact With rows. All inspected transactions persisted zero: Bin, Item Price, Stock Reconciliation, Stock Reconciliation Item, Stock Entry, Stock Ledger Entry, GL Entry, Repost Item Valuation, Withdrawal Slip, Sales Invoice, Purchase Invoice, Intercompany Material Billing Batch. There is no need to restore the eighth private recovery checkpoint.

The first opening-stock attempt failed in a script assertion, and its database rollback is independently confirmed. ERPNext v16.34.2 stock_reconciliation.py get_sle_for_items initializes Stock Reconciliation SLE actual_qty=0 and separately sets qty_after_transaction to the reconciled quantity; for this one synthetic item, expect actual_qty 0 and qty_after_transaction 10. A previous script expected actual_qty 10, which was incorrect. Remaining ledger values and GL checks have NOT passed yet, so must verify on retry before committing.

Owner's existing explicit approval still covers exactly one synthetic Opening Stock reconciliation on isolated ccpc-integration2.localhost, issuing Company Integration Test Issuer, Warehouse Stores - TISS, Item CCPC-INT-TEST-CONSUMABLE-001, 10 Nos at PHP 100 each = PHP 1,000, expense/difference account Temporary Opening - TISS, cost center Main - TISS, Moving Average. Retry must verify eighth pre-stock backup and isolation, unchanged baseline and empty transactions, insert and submit via ERPNext, require exactly one Bin 10/100/1000, the Stock Reconciliation SLE fields including actual_qty 0 and qty_after_transaction 10, 100 valuation rate and 1000 stock value and stock value difference; require two balanced GL rows, stock account debit 1000, opening account credit 1000, opening flags, no unrelated documents; single commit only after all assertions. If any check fails, rollback and independently inspect before retry. Do not modify persistent DEVELOPMENT or PRODUCTION.

## First approved opening-stock attempt stopped at incorrect Stock Ledger actual_qty assertion — 2026-10-13

The owner pasted the entire terminal transcript of their first **already approved** `Stock Reconciliation` attempt on isolated `ccpc-integration2.localhost` (see user-provided `Pasted text.txt` in conversation). The guarded script's preflight printed `Isolated site: VERIFIED`, `Eighth recovery checkpoint: VERIFIED`, `Moving Average valuation: VERIFIED`, `Opening accounts: VERIFIED`, and `No previous stock or accounting entries: VERIFIED`; posting time `2026-10-13 16:43:10`. It created and submitted the single reconciliation **within the uncommitted transaction**, and passed the script's reconciliation header/item and Bin validation, then failed during the Stock Ledger assertion before checking GL or executing `db.commit()`:

```text
Posting date: 2026-10-13
Posting time: 16:43:10
Creating one approved opening-stock reconciliation...

OPENING STOCK STOPPED: RuntimeError Stock Ledger quantity or value mismatch.
Database rollback requested.
Inspect persisted state before any retry.
```

**Root cause supported by exact ERPNext v16.34.2 upstream source:** in `erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py::StockReconciliation.get_sle_for_items`, for a standard non-serial/non-batch row with no inventory dimensions the Stock Ledger Entry is **initialized with `actual_qty=0`**, and separately sets **`qty_after_transaction=row.qty`** (expected 10 Nos). The verification script **incorrectly required `entry.actual_qty==10`**, making the SLE assertion invalid for this entry type. This is a **verification bug**, not yet evidence of a wrong ERPNext posting. The script's exception handler called `frappe.db.rollback()`; no commit success line. **Do not declare rollback independently verified until separately checking persisted test DB.** The exact SLE value of other fields (value, rate, difference) was never printed and must be verified on retry, not assumed. The first attempt's GL checks were **not reached**; do not claim they passed.

**Next one safe action:** independent read-only MySQLdb connection to exact isolated target after checking DB identity != persistent `development.localhost`. Inspect and assert two Companies' Moving Average methods, global Stock Settings method, one Item blank valuation override, exact master counts, and zero persisted Bin, Stock Reconciliation/Item, Stock Entry, SLE, GL, Withdrawal Slip, invoices, billing batch and Repost Item Valuation. Report all results and don't rerun until operator supplies verified rollback output. Preserve all eight protected site-private backups (latest pre-opening-stock prefix `20261013_163228-ccpc-integration2_localhost`, archive-verified but not restore tested).

**Subsequent retry only after verified rollback:** construct guarded standard insert/submit in same approved scope (TISS, Stores - TISS, 10 Nos × PHP 100 = PHP 1,000, Temporary Opening - TISS, Main - TISS, Moving Average), but correct the SLE check: `actual_qty=0` is normal for a non-serialized reconciliation, `qty_after_transaction=10`, `valuation_rate=100`, `stock_value=1000`, `stock_value_difference=1000` subject to real results, exactly one Bin 10/100/1000, two posted balanced GL entries against exact approved accounts/amounts. Single `db.commit()` after all checks, then independent postcommit SQL audit. No permission for other transactions, persistent DEVELOPMENT, or PRODUCTION.

## Installed ERPNext 16.34.2 Opening Stock posting preflight passed — 2026-10-13

Operator completed separately requested **read-only** Frappe runtime stock-posting readiness inspection on isolated `ccpc-integration2.localhost` before the one **already-approved** PHP 1,000 Opening Stock reconciliation. The eighth private, verified backup with prefix `20261013_163228-ccpc-integration2_localhost` and distinct target/persistent-development database identity were checked.

Operator output:
```text
ISOLATED SITE: VERIFIED
EIGHTH RECOVERY CHECKPOINT: VERIFIED
INSTALLED SOFTWARE
Frappe: 16.33.1
ERPNext: 16.34.2
Site date: 2026-10-13
Site time: 16:35:52.396060
VALUATION METHODS
Integration Test Issuer : Moving Average
Integration Test Requester : Moving Average
OPENING STOCK CONFIGURATION
Company Integration Test Issuer {'default_currency': 'PHP', 'default_inventory_account': 'Stock In Hand - TISS', 'stock_adjustment_account': 'Stock Adjustment - TISS', 'cost_center': 'Main - TISS'}
Warehouse Stores - TISS {'company': 'Integration Test Issuer', 'is_group': 0, 'disabled': 0, 'account': None}
Account Temporary Opening - TISS {'company': 'Integration Test Issuer', 'report_type': 'Balance Sheet', 'is_group': 0, 'disabled': 0}
Account Stock In Hand - TISS {'company': 'Integration Test Issuer', 'report_type': 'Balance Sheet', 'is_group': 0, 'disabled': 0}
Cost Center Main - TISS {'company': 'Integration Test Issuer', 'is_group': 0, 'disabled': 0}
INSTALLED RECONCILIATION FIELDS
Header: company Link required: 1
Header: purpose Select required: 1
Header: posting_date Date required: 1
Header: posting_time Time required: 1
Header: expense_account Link required: 0
Header: cost_center Link required: 0
Header: items Table required: 1
Item: item_code Link required: 1
Item: warehouse Link required: 1
Item: qty Float required: 0
Item: valuation_rate Currency required: 0
INSTALLED POSTING CONTROLLER
validate: True
on_submit: True
validate_expense_account: True
update_stock_ledger: True
make_gl_entries: True
OPENING ACCOUNT VALIDATION SOURCE
validate_expense_account: perennial perpetual inventory opening-stock difference account must not be Profit and Loss
CURRENT TRANSACTION BASELINE
Bin 0
Stock Reconciliation 0
Stock Entry 0
Stock Ledger Entry 0
GL Entry 0
Withdrawal Slip 0
Sales Invoice 0
Purchase Invoice 0
Intercompany Material Billing Batch 0
INSTALLED STOCK POSTING READINESS: VERIFIED
```

Also consulted exact upstream **ERPNext `v16.34.2` tag** via GitHub, consistent with observed installed version, rather than newer `version-16`. `StockReconciliation.validate` retains explicitly supplied `expense_account`, `on_submit` invokes `update_stock_ledger()` then `make_gl_entries()` then repost assessment, and `validate_expense_account` rejects P&L differences on `Opening Stock`. `StockController.get_voucher_details` marks resulting GL `is_opening=Yes` when reconciliation purpose is `Opening Stock`. `StockController.get_gl_entries` accounts each stock value difference through inventory account versus supplied difference account. `erpnext.stock.utils.get_valuation_method(item, company)` exists in v16.34.2; previously unavailable `clear_valuation_method_cache` exists in newer branches only. `Stock Reconciliation` has `set_posting_time` to respect explicit posting date/time.

**Next authorized action, NOT yet executed:** One safe, guarded `Stock Reconciliation` `purpose=Opening Stock` (only `Integration Test Issuer`, `Stores - TISS`, single nonserial `CCPC-INT-TEST-CONSUMABLE-001`, 10 Nos × PHP 100 = PHP 1,000, Moving Average, cost center `Main - TISS`, explicit `expense_account=Temporary Opening - TISS`, current site-local posting date/time). Assert verified eighth backup, exact site-vs-persistent-development DB isolation, Company/Item/Stock Settings method, existing master/Party Accounts and stock zero baseline before write; create through normal `frappe.get_doc(...).insert(ignore_permissions=True)` followed by `submit()`; assert document submitted, exactly one current Bin 10/100/1000, one submitted SLE 10/100/1000 and two balanced GL entries (Dr `Stock In Hand - TISS` PHP 1,000; Cr `Temporary Opening - TISS` PHP 1,000, opening flags), no other Stock Entry/Withdrawal Slip/Invoice/Billing Batch. Commit **once** only after all checks; rollback on error and operator must independently check persistence before any retry. After confirmed success independently re-audit committed DB records in a new read-only session. No permission for other stock flows or PRODUCTION/persistent DEVELOPMENT modification. Eight checkpoints archive-verified, not restore-tested.

## Eighth archive-verified isolated pre-opening-stock recovery checkpoint — 2026-10-13

Operator completed the **owner-approved eighth** site-private recovery checkpoint on **only** isolated `ccpc-integration2.localhost`, following independently verified `Moving Average` method configuration and **before** any inventory or accounting transactions. Command preflight verified: target DB isolation, TISS/TREQ both Moving Average, global Stock Settings Moving Average, synthetic stock Item `CCPC-INT-TEST-CONSUMABLE-001` enabled with blank method override, `Stores - TISS`, `Stock In Hand - TISS`, `Temporary Opening - TISS`, `Main - TISS`, unchanged two-company master and party/account mapping counts, zero prior stock/GL/invoice/billing records; **seven previous protected checkpoint archives preserved**.

Eighth successful full `bench backup --with-files --ignore-backup-conf --backup-path` output from operator at **2026-10-13 16:32:28 Asia/Manila**:
```text
Backup Summary for ccpc-integration2.localhost at 2026-10-13 16:32:28.947256
Backup for Site ccpc-integration2.localhost has been successfully completed with files
Verifying eighth recovery checkpoint...
database.sql.gz | 982189 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
EIGHTH RECOVERY CHECKPOINT: VERIFIED AND SECURED
```
The site-private directory is `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-moving-average-pre-opening-stock-20261013/`, prefix `20261013_163228-ccpc-integration2_localhost`. **All eight** protected archive sets preserve distinct tested milestones and passed archive format/DB-identity checks; still **no actual restore drill**.

**Next authorized write, NOT YET EXECUTED:** exactly one synthetic Opening Stock `Stock Reconciliation` on that site, Company TISS, item `CCPC-INT-TEST-CONSUMABLE-001`, warehouse `Stores - TISS`, **10 Nos × PHP 100 = PHP 1,000**, `expense_account=Temporary Opening - TISS`, `cost_center=Main - TISS`, effective Moving Average. Because a previous isolated settings script failed due to API mismatch between upstream source and **installed** ERPNext, first do **read-only inspection using the actual installed ERPNext controller/DocType and runtime**, including actual site-local clock/posting field behavior, current Company accounts, account/warehouse validation, version, and empty transaction baseline, before constructing the posting script. Single guarded commit should follow only after submitted reconciliation has coherent Bin, SLE, and balanced GL 1,000 debit to Stock In Hand and credit to Temporary Opening; independently verify persisted state in new SQL session. Never use direct SQL to modify ledgers; rollback on errors and inspect before rerun. Approval does **not** extend to Withdrawal Slip, Material Issue, invoices, intercompany billing, other master changes, persistent DEVELOPMENT `development.localhost`, or PRODUCTION.

## Owner approved eighth isolated recovery checkpoint and one PHP 1,000 opening-stock posting — 2026-10-13

Owner explicitly replied **Approved** to the proposal: create an **eighth** protected full checkpoint of isolated `ccpc-integration2.localhost` **after** independently verified Moving Average alignment, then exactly **one** controlled ERPNext `Stock Reconciliation`, purpose `Opening Stock`, Company `Integration Test Issuer` (TISS), Warehouse `Stores - TISS`, Item `CCPC-INT-TEST-CONSUMABLE-001`, **10 Nos at PHP 100/each = PHP 1,000**, difference/expense account **`Temporary Opening - TISS`**, cost center **`Main - TISS`** and effective **Moving Average** valuation. Expected posted GL is inventory asset debit (`Stock In Hand - TISS`) and temporary opening account credit, PHP 1,000 each, **subject to real ERPNext postcommit verification**, together with Stock Ledger and Bin balance. This authorization is site-specific and transaction-limited.

**One operator command at a time:** first run guarded **backup-only** command, create `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-moving-average-pre-opening-stock-20261013`; preserve all seven prior archives, verify isolated database identity, two Company valuation methods/global `Moving Average`, one Item blank override, 198 accounts and internal master baseline, zero stock/GL/invoices and other transactions before backup, require safe retention and free space, run `bench backup --with-files --ignore-backup-conf --backup-path`, verify four artifact archives and backup configuration database identity. Wait for **operator's verified eighth-backup result** before any stock posting.

**Before subsequent approved stock write:** inspect **installed** ERPNext Stock Reconciliation controller/DocType (upstream version-16 did not exactly match installed API; previously missing `clear_valuation_method_cache` caused script failure, which was independently rolled back). Verify posting date/time and relevant company default inventory, opening account and cost-center validations in isolated DB; ensure current time in site timezone. Use standard `Stock Reconciliation.insert/submit` and only one commit after guards and verified posted SLE/Bin/GL debit=credit amount, avoiding direct SLE/GL SQL edits or duplicate posting. Roll back and inspect on error, never blindly rerun. Check independently in new read-only session after successful commit. Approved opening reconciliation only; no Withdrawal Slips, Material Issues, invoices, Billing Batches, other master changes, persistent `development.localhost` or PRODUCTION actions. No eighth backup or stock write has occurred as of this report. Seven earlier checkpoints archive-verified, none restore-tested.

## Independent post-commit audit confirms Moving Average inheritance baseline — 2026-10-13

Operator performed the separate **read-only MySQLdb post-commit audit** after changing exactly two isolated Companies' valuation methods plus one isolated Stock Settings value using the authorized, corrected narrow Frappe DB API script. Output independently persisted in **ccpc-integration2.localhost** with target database identity guarded against persistent `development.localhost`:

```text
ISOLATED SITE: VERIFIED

PERSISTED COMPANY VALUATION METHODS
('Integration Test Issuer', 'Moving Average')
('Integration Test Requester', 'Moving Average')

GLOBAL STOCK SETTINGS
(('Moving Average',),)

SYNTHETIC ITEM VALUATION
(('CCPC-INT-TEST-CONSUMABLE-001', '', 1, 0),)

MASTER DATA COUNTS
tabCompany 2
tabAccount 198
tabCustomer 1
tabSupplier 1
tabItem 1
tabParty Account 2
tabAllowed To Transact With 2

STOCK AND FINANCIAL TRANSACTIONS
tabBin 0
tabItem Price 0
tabStock Reconciliation 0
tabStock Entry 0
tabStock Ledger Entry 0
tabGL Entry 0
tabWithdrawal Slip 0
tabSales Invoice 0
tabPurchase Invoice 0
tabIntercompany Material Billing Batch 0

MOVING AVERAGE POST-COMMIT CHECK: VERIFIED
```

**Milestone independently verified**: Company TISS and TREQ `valuation_method=Moving Average` and Stock Settings global method `Moving Average` are now committed and persisted. The one synthetic stock Item remains enabled, `valuation_method` override blank, hence according to ERPNext's documented valuation-precedence code it inherits Company method. Exact counts of companies, 198 accounts, internal Customer/Supplier mappings by count and single Item are preserved. No Bin or Item Price or any inventory or accounting postings. The installed ERPNext's runtime `get_valuation_method()` has **not** been separately called since a prior optional helper import proved absent; don't equate code inspection with live function execution. Earlier failed attempt was proven rolled back before the successful retry.

Seven archive-verified snapshots exist (latest seventh pre-valuation update `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-item-pre-moving-average-20261013/` with prefix `20261013_161234-ccpc-integration2_localhost`); none is a **post-Moving Average** recovery checkpoint yet; none restore-tested.

**Next approval gate:** recommend an eighth protected full site snapshot **post-Moving Average/pre-opening-stock**, preserving all seven prior snapshots, archive-verifying the new one with DB identity guards. After separately authorized snapshot, one supported ERPNext `Stock Reconciliation` `purpose=Opening Stock` on isolated site only, issuer `Integration Test Issuer`, `Stores - TISS`, synthetic Item `CCPC-INT-TEST-CONSUMABLE-001`, proposal 10 Nos at PHP 100/each = PHP 1,000, explicit `expense_account=Temporary Opening - TISS` (eligible Balance Sheet/Temporary), `cost_center=Main - TISS`, positive valuation, company Moving Average. Review exact installed ERPNext validations/version, posting time and GL treatment before actual insert/submit. Validate one Bin with 10 actual quantity, SLE, and expected balanced GL (inventory asset debit versus opening account credit) through the supported workflow and a separate independent read-only postcommit check. **No approval yet to create stock, GL postings or any inventory transaction; the previously approved step only authorized the valuation configuration correction.** Do not create Withdrawal Slips, Stock Entries, intercompany billing, invoices, or touch persistent DEVELOPMENT/PRODUCTION.

## Isolated Moving Average update committed; independent SQL audit pending — 2026-10-13

Under the previously granted **three-field valuation settings authorization** on isolated `ccpc-integration2.localhost`, operator successfully executed the revised guarded Frappe DB API script, after a separate direct-SQL read-only audit verified the earlier failed update fully rolled back. The seventh private archive-verified pre-change recovery checkpoint (`20261013_161234-ccpc-integration2_localhost`) was verified before writes. Input site was confirmed distinct from persistent `development.localhost`. Revised script specifically avoided importing the helper `clear_valuation_method_cache` that does not exist in installed ERPNext, and tested exact values using direct SQL within its own transaction before one commit. Operator supplied successful output:

```text
Isolated test site: VERIFIED
Seventh recovery checkpoint: VERIFIED
Original FIFO settings: VERIFIED
Synthetic Item override blank: VERIFIED
No stock or accounting transactions: VERIFIED
Applying three approved valuation changes...
Three valuation fields: VERIFIED BEFORE COMMIT
Item override: UNCHANGED
Stock and accounting records: UNCHANGED

Integration Test Issuer: Moving Average
Integration Test Requester: Moving Average
Global Stock Settings: Moving Average
Item valuation override: BLANK
Stock and financial transactions: NONE

MOVING AVERAGE SETTINGS: COMMITTED
```

**State of evidence:** operator's just-executed script reports successful `frappe.db.commit()` after checking TISS/TREQ `Company.valuation_method` and isolated global `Stock Settings.valuation_method` were all Moving Average, and single Item override remained blank. It verified no Bin, Item Price, Stock Reconciliation/Entry/Ledger, GL, Withdrawal Slip, invoices or Billing Batch in that session. **Independent persisted read-only SQL audit in a separate process is pending**, so do not yet claim externally persisted values verified. Standard Item/Company valuation method inheritance will then be tested against the actual installed API if possible; avoid reliance on upstream-only helper names. Previous FIFO update failed due to installed-version import incompatibility and was separately proven rolled back, not an unverified in-flight failure. No inventory quantity, opening-stock transaction or GL posting authorized; seven protected snapshots archive-verified but no restoration drill. Persistent DEVELOPMENT and PRODUCTION must not be modified.

**Next one safe operator step:** read-only independent MySQLdb transaction on `ccpc-integration2.localhost`, guard database name against `development.localhost`, assert two Company valuation values `Moving Average`, global `tabSingles` value `Moving Average`, Item `valuation_method` blank, exact two Companies and one Item/master counts unchanged, and zero Bin/Stock Reconciliation/Stock Entry/Stock Ledger/GL/Withdrawal Slip/invoices/Billing Batch. If audit succeeds record verified result in handoff; propose further seventh/post-change backup strategy and obtain **separate** owner approval for a synthetic `Opening Stock` reconciliation (tentative 10 Nos at PHP 100 each, 1,000 PHP, `Stores - TISS`, `Temporary Opening - TISS`, `Main - TISS`) only after checks.

## Isolated valuation update rollback independently verified; safe retry authorized — 2026-10-13

Operator independently checked actual persisted DB values **after** the prior failed Moving Average update (ImportError from missing installed ERPNext `erpnext.stock.utils.clear_valuation_method_cache`). The independent MySQLdb read-only SQL check explicitly verified target `ccpc-integration2.localhost` versus separate persistent `development.localhost` DB identity. Exact operator output:

```text
ISOLATED SITE: VERIFIED

PERSISTED COMPANY VALUATION METHODS
('Integration Test Issuer', 'FIFO')
('Integration Test Requester', 'FIFO')

PERSISTED GLOBAL STOCK SETTINGS
(('FIFO',),)

PERSISTED ITEM VALUATION OVERRIDE
(('CCPC-INT-TEST-CONSUMABLE-001', ''),)

STOCK AND FINANCIAL TRANSACTION COUNTS
tabBin 0
tabStock Reconciliation 0
tabStock Entry 0
tabStock Ledger Entry 0
tabGL Entry 0
tabWithdrawal Slip 0
tabSales Invoice 0
tabPurchase Invoice 0
tabIntercompany Material Billing Batch 0

ROLLBACK VERIFIED: ORIGINAL FIFO STATE PRESERVED
```

**Conclusion:** the failed attempt's `frappe.db.rollback()` worked; all three valuation methods persisted as FIFO, item override blank, zero stock/accounting documents. No restoration necessary; seventh protected full site backup remains archive-verified, site-private and pre-change (`private/ccpc-test-snapshots/post-item-pre-moving-average-20261013/20261013_161234-ccpc-integration2_localhost-*`). Prior six checkpoints remain preserved, none restore-tested.

**Next action is permitted under existing explicit owner approval**: retry changing exactly two isolated test `Company.valuation_method` and `Stock Settings.valuation_method` using targeted Frappe DB APIs; **do not import optional helper `clear_valuation_method_cache`** from installed app (confirmed unavailable), and avoid relying on assumptions about upstream release helper names. After verifying preflight/backup and original FIFO, make three writes, check the updated fields with **direct SQL in the same transaction** (avoids stale Frappe caches), ensure Item override remains blank, other masters/financial/stock counts unchanged, then commit once; rollback on any error. Independently verify persisted SQL **in a new separate session after commit** and effective Item method from installed API after version compatibility is inspected. Do not rerun previous failed script or blindly retry on a mismatch. Opening-stock reconciliation and all material/financial postings remain unapproved, as do changes to persistent DEVELOPMENT or PRODUCTION.

## Moving Average update interrupted by installed ERPNext helper import — 2026-10-13

Operator executed the **already authorized** three-field Moving Average change script on the isolated `ccpc-integration2.localhost` site, following the verified seventh pre-change protected backup (prefix `20261013_161234-ccpc-integration2_localhost`). Operator pasted:
```text
Isolated site: VERIFIED
Seventh recovery checkpoint: VERIFIED
FIFO valuation baseline: VERIFIED
No stock or financial transactions: VERIFIED
Changing three valuation settings...
VALUATION UPDATE STOPPED: ImportError cannot import name 'clear_valuation_method_cache' from 'erpnext.stock.utils' (/workspace/development/frappe-bench/apps/erpnext/erpnext/stock/utils.py)
Do not rerun until database state is inspected.
```
**Why:** script wrote two `Company.valuation_method` fields and isolated `Stock Settings.valuation_method` using targeted Frappe DB APIs but then imported `clear_valuation_method_cache` which is not available in the **installed ERPNext** `erpnext.stock.utils`. The originally consulted upstream `version-16` GitHub helper differs from installed site code. Import error occurred **before** any `frappe.db.commit()` and was caught by the script, which called `frappe.db.rollback()`; likely all three changes were reverted, but **persisted database state has NOT yet been independently verified**. Import error is a script compatibility issue, not proof a transaction posted or that valuation setting changes persisted. Do NOT rerun unchanged failed script and do NOT restore backup without verifying state.

**Next step (read-only only):** direct SQL with independent connection and distinct target/development DB check: select both test Companies' `valuation_method`, global `tabSingles` Stock Settings method, single Item `valuation_method` and master record counts, zero stock/GL/financial document counts. Print observed values even if they show partial changes and classify them; no SQL writes or Frappe mutating API calls. Then adapt script to the **installed ERPNext** API, avoiding missing helper and verifying via a fresh Frappe process / DB reads after commit (no assumed upstream-only functions), under **existing narrowly scoped owner approval** if the read-only check proves normal rolled-back baseline. Any unexpected partial state requires further investigation before another write. Seventh private archive remains preserved, six predecessors preserved and no restoration test. Opening-stock posting, financial transactions, persistent DEVELOPMENT and PRODUCTION are still outside authorization.

## Seventh isolated full checkpoint verified before Moving Average switch — 2026-10-13

The owner completed the authorized seventh protected full backup on **only** isolated `ccpc-integration2.localhost`, before changing three valuation settings. Guarded SQL preflight independently confirmed two Companies both `FIFO`, isolated `Stock Settings.valuation_method=FIFO`, one synthetic Item `CCPC-INT-TEST-CONSUMABLE-001` with blank method override, 198 Accounts, internal parties and mappings unchanged, zero Bin/Stock Reconciliation/Stock Entry/Stock Ledger/GL/Withdrawal Slip/Invoices/Billing Batch, and six existing protected checkpoints preserved.

Backup successfully completed at **2026-10-13 16:12:35 Asia/Manila** in `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-item-pre-moving-average-20261013/`, prefix `20261013_161234-ccpc-integration2_localhost`. Operator-verified artifacts:
```text
database.sql.gz | 982177 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
SEVENTH RECOVERY CHECKPOINT: VERIFIED AND SECURED
```
Seven recovery checkpoints are archive-verified and preserved, not full restoration-tested. No stock or GL postings and no valuation setting changes yet by this milestone.

**Next already-authorized action:** update `Company.valuation_method` for exact `Integration Test Issuer` and `Integration Test Requester` from `FIFO` to `Moving Average` and isolated `Stock Settings.valuation_method` from `FIFO` to `Moving Average`, while leaving Item valuation override blank and all stock, GL and transactions at zero. Enforce test/persistent-development DB distinction, exact prior baseline and seventh backup identity; avoid unintended global Stock Settings save side effects: ERPNext v16 Stock Settings controller `validate()` can change unrelated defaults and Property Setters even when modifying only valuation_method. Prefer **targeted supported Frappe DB setting APIs** to change exactly the three authorized valuation fields only, after reproducing the key documented `cant_change_valuation_method` restriction (no stock ledger entries with Item override blank) and pre/post change checks. Single DB commit only after all assertions; rollback on any exception and do not blindly rerun. Clear cached docs and use live `erpnext.stock.utils.get_valuation_method` to verify method inherited for the synthetic Item under both Companies plus global case. Independently verify persisted state after commit via a second read-only SQL audit.

No new approval for stock quantity or valuation entries; proposed PHP 1,000 Opening Stock reconciliation remains **on hold**. No operations on `development.localhost` or PRODUCTION.

## Seventh snapshot and Moving Average settings: owner approval — 2026-10-13

The owner explicitly approved a seventh site-private full checkpoint on isolated `ccpc-integration2.localhost`, followed by exactly three valuation settings changes: `Integration Test Issuer` Company FIFO -> Moving Average, `Integration Test Requester` Company FIFO -> Moving Average, and isolated-site global Stock Settings FIFO -> Moving Average. Keep Item `CCPC-INT-TEST-CONSUMABLE-001` valuation override blank. This approval does not include Stock Reconciliation, opening stock, Stock Entry, GL, Withdrawal Slip, invoice, batch, migrations, persistent DEVELOPMENT or PRODUCTION changes.

The last independent audit confirmed both Company valuations FIFO, Stock Settings FIFO, Item valuation override empty, and zero Stock Reconciliation/Entry/Ledger/GL records. Do the approved protected full site backup first; verify preservation of all six earlier checkpoints and recovery artifact integrity. Only after operator confirms it, perform Frappe document-based valuation updates with test DB isolation guards, then an independent read-only audit of persisted fields and effective valuation method. The proposed 10 Nos at PHP 100 opening-stock transaction remains unapproved.

## Valuation inheritance independently audited: all isolated defaults FIFO, no Item override — 2026-10-13

Operator returned **read-only test-site MySQLdb** result for `ccpc-integration2.localhost` (target DB identity checked against persistent `development.localhost`):
```text
COMPANY VALUATION METHODS
('Integration Test Issuer', 'FIFO')
('Integration Test Requester', 'FIFO')
ITEM VALUATION METHOD
('CCPC-INT-TEST-CONSUMABLE-001', '')
GLOBAL STOCK VALUATION METHOD
(('FIFO',),)
STOCK TRANSACTION COUNTS
tabStock Reconciliation 0
tabStock Entry 0
tabStock Ledger Entry 0
tabGL Entry 0
VALUATION CONFIGURATION AUDIT: COMPLETED
```

**Verified fact:** BOTH isolated test Companies have `valuation_method=FIFO`; global Stock Settings is `FIFO`; the one Item has an **empty valuation_method override**, so ERPNext v16 `get_valuation_method(item_code, company)` currently inherits the relevant company `FIFO` for TISS/TREQ stock transactions. Verified that function again from upstream `erpnext/stock/utils.py` version-16 in GitHub. Owner's intended actual CCPC method is **Moving Average** (owner statement; no read of PRODUCTION needed). This is a test-fidelity problem, not merely a cosmetic setting.

No previous authorization to alter valuation settings or post opening stock. Suggested separate scoped authorization for (1) **seventh private post-Item/pre-change site backup** with six prior snapshots preserved and archive/DB-identity integrity checks; (2) standard supported Frappe API update to valuation method **Moving Average** for exact two isolated synthetic Companies TISS/TREQ and isolated `Stock Settings` global default; leave Item override blank to inherit Company value (no need to set explicit Item override) after checking no stock/GL/Stock Reconciliation, no changed Company baseline, item unaffected; (3) independent postcommit read-only verification of all three defaults plus `get_valuation_method` for the single Item under both Companies. Before the first new stock posting, take separately scoped **post-valuation / pre-stock** snapshot if necessary. Do not touch persistent `development.localhost` or PRODUCTION. Do not yet create Stock Reconciliation, Stock Entry, GL, Withdrawal Slip, Billing Batch or invoices. Opening stock 10 Nos at PHP 100 is a **proposal on hold** and requires separate authorization after alignment.

## Moving Average alignment required before first synthetic inventory posting — 2026-10-13

**Owner raised an important mismatch**: CCPC's **actual intended inventory valuation method is Moving Average**, while the isolated TISS test site's last verified `Company.valuation_method` and `Stock Settings.valuation_method` both read **FIFO**. Production method is **user-reported**, not independently audited on PRODUCTION (and no PRODUCTION access/change is authorized). The owner asked whether proceeding with FIFO is appropriate.

**Decision/recommendation:** Do **not** submit the previously proposed seventh backup/first Opening Stock reconciliation until the isolated test site's effective stock valuation method is aligned to **Moving Average** and independently confirmed. Six previous private archived checkpoints are preserved; there are still zero `Stock Ledger Entry`, `Stock Reconciliation`, `Bin` and `GL Entry` records, so now is the safe opportunity to align the test baseline. A first 10 Nos × PHP 100 entry will have the same initial value under either method, but subsequent mixed-rate receipts and withdrawals will cost differently, affecting inventory and intercompany billing verification. No approved stock-posting action yet.

Verified **upstream ERPNext v16** `erpnext/stock/utils.py:get_valuation_method(item_code, company)`: explicitly configured **Item.valuation_method** takes precedence; if blank, a company-aware stock transaction uses **Company.valuation_method**; `Stock Settings.valuation_method` is used when no company is supplied. `erpnext/stock/doctype/item/item.json` includes an optional `valuation_method` Select with **Moving Average**. The user-approved Item-creation script did not explicitly set this field; **its actual persisted value has not yet been inspected**. Therefore verify read-only both TISS/TREQ Company methods, Stock Settings, and specific test Item override, and compute the effective result using the installed app's `get_valuation_method` before preparing any change. Do not assume that changing only global Stock Settings changes company-aware TISS valuation.

**Next gated action (not yet authorized)**: after read-only baseline audit, ask owner's explicit approval before adjusting isolated test master settings (prefer test Company TISS, possibly TREQ and global Stock Settings for consistency, Item override if needed), using standard DocType APIs and full rollback/postcommit checks. Changing valuation configuration on persistent `development.localhost` or PRODUCTION remains prohibited without separate approval. Also re-evaluate whether to take the seventh backup before or after changing the valuation defaults. The previously floated PHP 1,000 fictional opening Stock Reconciliation remains **on hold** and requires separate approval after effective method verified.

## Isolated TISS opening-stock account, valuation, and warehouse readiness verified — 2026-10-13

Operator ran previously requested read-only MySQLdb accounting-readiness audit on isolated `ccpc-integration2.localhost`, proving DB identity distinct from persistent `development.localhost` and exact TISS/TREQ Company pair. The output:

```text
ISOLATED SITE: VERIFIED
ISSUER COMPANY SETTINGS
name : Integration Test Issuer
default_currency : PHP
enable_perpetual_inventory : 1
valuation_method : FIFO
stock_adjustment_account : Stock Adjustment - TISS
default_inventory_account : Stock In Hand - TISS
default_expense_account : Cost of Goods Sold - TISS
cost_center : Main - TISS

ISSUER WAREHOUSE
('Stores - TISS', 'Integration Test Issuer', 0, 0, account=None)

OPENING / STOCK ACCOUNT CANDIDATES
Capital Stock - TISS | Equity | Balance Sheet | Equity | leaf, enabled
Cost of Goods Sold - TISS | Expense | Profit and Loss | COGS | leaf, enabled
Opening Balance Equity - TISS | Equity | Balance Sheet | Equity | leaf, enabled
Stock Adjustment - TISS | Expense | Profit and Loss | Stock Adjustment | leaf, enabled
Stock Assets - TISS | Asset | Balance Sheet | Stock | group
Stock Expenses - TISS | Expense | Profit and Loss | [blank] | group
Stock In Hand - TISS | Asset | Balance Sheet | Stock | leaf, enabled
Stock Liabilities - TISS | Liability | Balance Sheet | [blank] | group
Stock Received But Not Billed - TISS | Liability | Balance Sheet | Stock Received But Not Billed | leaf, enabled
Temporary Opening - TISS | Asset | Balance Sheet | Temporary | leaf, enabled

ISSUER COST CENTERS
Integration Test Issuer - TISS | group, enabled
Main - TISS | leaf, enabled

STOCK SETTINGS
allow_negative_stock = 0
default_warehouse = Stores - TISS
valuation_method = FIFO

SYNTHETIC ITEM
CCPC-INT-TEST-CONSUMABLE-001 | Consumable | Nos | stock item, enabled

TRANSACTION BASELINE
tabBin 0
tabStock Reconciliation 0
tabStock Entry 0
tabStock Ledger Entry 0
tabGL Entry 0
tabWithdrawal Slip 0
tabSales Invoice 0
tabPurchase Invoice 0
tabIntercompany Material Billing Batch 0

STOCK ACCOUNTING READINESS AUDIT: COMPLETED
```

Assessment: `Temporary Opening - TISS` is an appropriate **candidate** difference account for `Stock Reconciliation` with `purpose="Opening Stock"`, unlike the P&L `Stock Adjustment - TISS`. `Stock In Hand - TISS` is the issuer Company's asset account and `Stores - TISS` is its enabled leaf Warehouse (no direct warehouse account override). `Main - TISS` is valid leaf cost center; FIFO, PHP and perpetual inventory enabled; no prior stock/GL entries.

Inspected upstream **ERPNext v16** `erpnext/stock/doctype/stock_reconciliation/stock_reconciliation.py` and JSON: `validate()` defaults difference account to Company `stock_adjustment_account`, so **explicitly override it with `Temporary Opening - TISS`** for an opening entry. `validate_expense_account` rejects P&L difference accounts for `Opening Stock` or first stock ledger entry. `on_submit` creates Stock Ledger Entries and GL Entries through supported ERPNext methods. Reconciliation Item requires warehouse, item, quantity and positive valuation rate (normal nonzero stock valuation); `update_stock_ledger` rejects nonzero quantity without valuation rate unless special zero-valuation allowance. Positive valuation must be specified even though Item's stored valuation_rate=0. Test Item nonserial/nonbatch. ERPNext v16 `Stock Reconciliation` DocType supports `Opening Stock` purpose and cost center, and `Stock Reconciliation Item` supports `qty` and `valuation_rate`.

**No new data was written by audit.** Current verified state is **one Item, zero stock, zero GL**. Six protected archives survive; sixth captured pre-Item state, not restoration-tested.

**Next approval gate (not yet obtained)**: recommend seventh guarded protected full test-site snapshot after Item and before posting inventory. Then one synthetic `Stock Reconciliation` `purpose=Opening Stock`, only company `Integration Test Issuer`, only Item `CCPC-INT-TEST-CONSUMABLE-001`, only warehouse `Stores - TISS`, explicit difference account `Temporary Opening - TISS`, cost center `Main - TISS`, and an agreed small qty/rate (suggest **10 Nos at PHP 100 each**, stock value PHP 1,000). Confirm explicit posting date/time before execution and inspect installed ERPNext release/code and real site safety preconditions. Use standard `insert()` + `submit()`, perform guarded SLE and GL checks including expected inventory debit and opening account credit, and single commit only after valid results; on errors rollback/inspect. This is a **real inventory and accounting posting** even with fictional data, and warrants separate owner authorization. No Stock Entry/Withdrawal Slip/Billing Batch/invoices or any persistent DEVELOPMENT/PRODUCTION change under this authorization.

## Independent committed synthetic Item and zero-stock/GL baseline confirmed — 2026-10-13

Operator ran a **separate read-only post-commit MySQLdb audit** against isolated `ccpc-integration2.localhost` after the one previously authorized Item insertion. The audit checked site DB identity distinct from persistent `development.localhost`, selected the **only** Item row and asserted exact identity/configuration, asserted opening stock, valuation rate and standard rate all zero, and asserted no Bin or stock/accounting/billing documents. Complete supplied output:

```text
ISOLATED SITE: VERIFIED

SYNTHETIC ITEM
('CCPC-INT-TEST-CONSUMABLE-001', 'CCPC-INT-TEST-CONSUMABLE-001', 'Synthetic Integration Test Consumable', 'Consumable', 'Nos', 1, 0, 0, 0, Decimal('0E-9'), Decimal('0E-9'), Decimal('0E-9'))

STOCK AND ACCOUNTING BASELINE
tabBin 0
tabItem Price 0
tabStock Reconciliation 0
tabStock Entry 0
tabStock Ledger Entry 0
tabGL Entry 0
tabWithdrawal Slip 0
tabSales Invoice 0
tabPurchase Invoice 0
tabIntercompany Material Billing Batch 0

MASTER DATA COUNTS
tabCompany 2
tabAccount 198
tabCustomer 1
tabSupplier 1
tabItem 1
tabParty Account 2
tabAllowed To Transact With 2

SYNTHETIC ITEM POST-COMMIT CHECK: VERIFIED
```

**Verified:** one committed synthetic stocked and enabled `CCPC-INT-TEST-CONSUMABLE-001` Item, `Consumable` group, `Nos` UOM, no serial/batch tracking, zero opening stock/standard selling rate/valuation, no Item Price/Bin/Stock Reconciliation/Stock Entry/Stock Ledger/GL/Withdrawal Slip/Invoices/Billing Batch, and baseline two Companies/198 Accounts/internal trading parties unchanged. Sixth full private checkpoint `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-parties-pre-item-20261013/20261013_154329-ccpc-integration2_localhost-*` was taken **before Item insert**; six archives checked but no restore trial.

**Next action is read-only stock-accounting readiness investigation**: inspect TISS stock/reconciliation Company defaults (`stock_adjustment_account`, `cost_center`, perpetual flag/PHP), candidate enabled leaf expense or temporary equity account as appropriate, required Warehouse and item/group defaults, existing ledger and zero-quantity checks. Consult matching installed ERPNext version Stock Reconciliation validations before choosing quantity, PHP valuation rate, posting date, expense account, cost center. Do **not** create stock quantity, Stock Reconciliation/Stock Entry/GL, Withdrawal Slip or invoices under existing Item authorization. Obtain separate explicit approval and recommend protected post-item/pre-stock seventh snapshot. Any genuine stock valuation operation must use standard ERPNext document posting and verify SLE/GL balance and rollback/test environment confinement. Persistent `development.localhost` and PRODUCTION out of scope.

## One zero-opening-stock synthetic Item created and verified in isolated site — 2026-10-13

Operator ran the **previously authorized** guarded Frappe Item insertion on **only** isolated `ccpc-integration2.localhost` after verifying the sixth site-private backup artifacts with prefix `20261013_154329-ccpc-integration2_localhost` and matching target database identity distinct from persistent `development.localhost`. Initial preflight checks passed: exact TISS and TREQ pair, 99 Account rows each, correct internal Customer/Supplier and company allowlists/Party Accounts, eligible `Operations - TREQ` and `Stores - TISS`, available `Consumable` group and `Nos` UOM, PHP/perpetual inventory Company settings, zero Item rows and zero transaction/price/bin documents.

The script used normal `frappe.get_doc({"doctype":"Item",...}).insert(ignore_permissions=True)` with `opening_stock=0` and `standard_rate=0` (prevents ERPNext `Item.after_insert` auto-opening reconciliation and auto Item Price), then verified saved Item fields, exactly one Item, unchanged Company/Account/Customer/Supplier master counts, empty `Item Price`, `Bin`, `Withdrawal Slip`, `Stock Reconciliation`, `Stock Entry`, `Stock Ledger Entry`, `Sales Invoice`, `Purchase Invoice`, `GL Entry` and `Intercompany Material Billing Batch`; **one `frappe.db.commit()` after all checks**. Operator pasted:

```text
Isolated site: VERIFIED
Sixth recovery checkpoint: VERIFIED
Two-company accounting baseline: VERIFIED
Internal Customer/Supplier mappings: VERIFIED
Item Group and UOM: VERIFIED
Warehouse and Department: VERIFIED
No Items or transactions: VERIFIED
Creating one fictional stock Item...

Item Code: CCPC-INT-TEST-CONSUMABLE-001
Item Name: Synthetic Integration Test Consumable
Item Group: Consumable
Stock UOM: Nos
Maintain Stock: 1
Opening Stock: 0.0
Standard Rate: 0.0
Total Items: 1
Stock and financial transactions: NONE

SYNTHETIC STOCK ITEM: CREATED AND VERIFIED
```

The single test Item now exists: `CCPC-INT-TEST-CONSUMABLE-001`, name `Synthetic Integration Test Consumable`, `item_group=Consumable`, `stock_uom=Nos`, `is_stock_item=1`, `disabled=0`, `has_serial_no=0`, `has_batch_no=0`, `opening_stock=0`, `standard_rate=0`; also `valuation_rate=0` requested by script. **No inventory quantity, valuation, Stock Reconciliation, Stock Entry, GL Entry, invoice, Withdrawal Slip or Billing Batch has been authorized or created by this action**. Six archive-verified snapshots survive; sixth was created **before Item** and no restore drill yet.

**Next step:** run a separate read-only post-commit SQL audit of the Item master, no Item Price, no Bin, no Stock Reconciliation/Entry/Ledger/GL transactions, and persistence of exact party mappings, enforcing target-vs-persistent-Development DB isolation; do not rerun the successful insert. After confirmation, research safe Stock Reconciliation opening inventory setup and accounting safeguards (stock adjustment account, cost center, valuation, posting date and inventory/GL reconciliation) and request **separate explicit operator approval** for any opening quantity/valuation or stock transaction; consider a seventh snapshot post-Item/pre-stock. This test does not prove billing flow integration or restoration behavior.

## Sixth recovery checkpoint archive-verified, before synthetic Item master — 2026-10-13

Operator completed the separately authorized **sixth** full snapshot on isolated `ccpc-integration2.localhost`, with **no Item insert yet**. Guard preflight output confirmed test site isolation, exact two fictional Companies and **198 Accounts**, correct internal-party mappings, warehouse/department/Item Group/UOM master readiness, zero existing Items and transactional records, and all **five earlier** protected checkpoints preserved.

Full `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"` succeeded at 2026-10-13 15:43:30 Asia/Manila, writing prefix `20261013_154329-ccpc-integration2_localhost` inside `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-parties-pre-item-20261013/`. Operator supplied checksum/integrity-stage readout:
```text
Isolated site: VERIFIED
Two companies and 198 accounts: VERIFIED
Internal party mappings: VERIFIED
Item prerequisites: VERIFIED
No existing items or transactions: VERIFIED
Five earlier recovery checkpoints: PRESERVED
Creating sixth recovery checkpoint...
Backup for Site ccpc-integration2.localhost has been successfully completed with files
Verifying sixth recovery checkpoint...
database.sql.gz | 980906 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
SIXTH RECOVERY CHECKPOINT: VERIFIED AND SECURED
```

All six checkpoints are archive-verified, **not fully restore-tested**. They remain site-private; database credentials must not be printed or committed.

**Next already-approved action** (one guarded test-site-only command): create exactly one `Item` document `CCPC-INT-TEST-CONSUMABLE-001`, name `Synthetic Integration Test Consumable`, group `Consumable`, UOM `Nos`, `is_stock_item=1`, enabled, with explicitly **zero `opening_stock` and zero `standard_rate`** and no serial/batch handling. Use standard `Item.insert()`, do not use real-company-specific patches, check named snapshot and DB identity, party/account baseline, Item uniqueness and absence of ledger/stock transaction records before write, and post-verify exact Item fields/stock and no Item Price/Stock Reconciliation/Stock Entry/GL before single `frappe.db.commit()`. ERPNext v16 `Item.after_insert` only generates Item Prices on nonzero `standard_rate` or opening reconciliation on nonzero `opening_stock`, so leaving both at explicit zero is important. If error, roll back and inspect rather than blindly rerun. No Item has been created so far by this report.

Opening stock quantity and valuation, Stock Reconciliation/Entry/Ledger postings, Withdrawal Slip, Billing Batch, invoices, accounting entries, broader DEVELOPMENT or PRODUCTION actions all **remain outside the user's current authorization**.

## Owner authorized sixth isolated backup and one zero-stock synthetic Item — 2026-10-13

Operator explicitly answered **Approved** to creating a sixth **post-internal-parties/pre-item** full recovery snapshot and then **one fictional stocked Item** on isolated `ccpc-integration2.localhost` only. The planned Item has `item_code=CCPC-INT-TEST-CONSUMABLE-001`, `item_name=Synthetic Integration Test Consumable`, `item_group=Consumable`, `stock_uom=Nos`, `is_stock_item=1`, `disabled=0`, `opening_stock=0`, no item price/valuation/serial/batch fixture or warehouse account override. The user **did not approve creating actual stock quantity**, Stock Reconciliation/Entry/Ledger/GL postings, Withdrawal Slip, invoices, billing batches, migrations, or changes to persistent `development.localhost` or PRODUCTION.

Prior operator read-only prerequisite audit verified: `Operations - TREQ` is enabled non-group Department belonging to requester, `Stores - TISS` enabled non-group warehouse belonging to issuer, `Nos` and `Unit` UOMs exist, `Consumable` Item Group leaf, TISS `enable_perpetual_inventory=1`, PHP currency, Stock Reconciliation count zero. Previous SQL audits confirmed zero `Item`/`Bin`, transactional tables zero and persisted internal Customer/Supplier with exact Party Account/allowlist mappings. GitHub app reviewed at `review/intercompany-approval-failure-tests` commit `806fa23516490ec7beefcff03a1baa09d722120e`.

**Next safe step (before any Item inserts):** one guarded backup command against isolated site with fixed new protected directory `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-parties-pre-item-20261013`; verify DB isolation, five prior snapshot artifacts including fifth `20261013_151050`, no existing Item/stock/GL/Withdrawal Slip records, two Companies, 198 Accounts, two Intercompany groups, Customer/Supplier and child mappings; guard Frappe housekeeping of standard backup folder before calling absolute `bench backup --with-files --ignore-backup-conf --backup-path`; verify gzip, public/private tar, JSON/db identity and secure file permissions. Archive-verification does not equal full restore-tested.

After operator confirms sixth backup, create Item via normal `frappe.get_doc({"doctype":"Item",...}).insert()` with **both `opening_stock=0` and `standard_rate=0`** explicitly (ERPNext v16 `item.py` after_insert triggers Item Price on nonzero standard_rate or Stock Reconciliation on nonzero opening_stock). Precheck Item uniqueness and relevant master settings; check item data and absence of Stock Reconciliation/Bin/GL/Stock Entries/Item Price if baseline zero and commit once; stop on exception, don't blindly rerun. Item creation has not been attempted yet.

## Synthetic TISS-to-TREQ stock item prerequisite validation — 2026-10-13

Operator completed the **requested read-only** test-site SQL prerequisites check on isolated `ccpc-integration2.localhost`. Output:
```text
REQUESTING DEPARTMENT: (('Operations - TREQ', 'Integration Test Requester', 0, 0),)
ISSUING WAREHOUSE: (('Stores - TISS', 'Integration Test Issuer', 0, 0),)
STOCK UOM: (('Nos',), ('Unit',))
ITEM GROUP: (('Consumable', 0),)
ISSUER INVENTORY SETTINGS: (('Integration Test Issuer', 1, 'PHP'),)
EXISTING STOCK RECONCILIATIONS: ((0,),)
ITEM AND DEPARTMENT READINESS AUDIT: COMPLETED
```
This confirms `Operations - TREQ` is enabled/non-group and belongs to requester, `Stores - TISS` is enabled/non-group and belongs to issuer, `Nos` and `Unit` UOMs exist, `Consumable` is a leaf group, TISS has perpetual inventory enabled and PHP currency, with no Stock Reconciliation documents. Previous inventory audit: zero `Item`, `Bin`, `Stock Entry`, `Stock Ledger Entry`, `GL Entry`, `Withdrawal Slip`, `Sales Invoice`, `Purchase Invoice` and billing batch. All read-only; **no synthetic item or stock quantity has yet been created**.

Current `ccpcerp` source on verified `review/intercompany-approval-failure-tests` branch requires stocked Item with `requested_qty <= actual_qty` from issuer `Stores - TISS` and eligible TREQ Department before saving a Withdrawal Slip. No `CCPC Section` exists, so section is not currently mandatory. ERPNext v16 `erpnext/stock/doctype/item/item.json` specifies `item_code` as autoname, required `item_group`/`stock_uom`, default `is_stock_item=1` and `opening_stock` optional; its Item controller performs additional stock UOM/item default validations.

**Next authorization request (not yet given):** create a **sixth** guarded full site snapshot **after parties but before item**, with preserved five previous archive-verified checkpoints and matching site DB identity, then create **one** explicitly synthetic stock Item using the standard Frappe `Item.insert()` API. Suggested fixture identity `CCPC-INT-TEST-CONSUMABLE-001`, name `Synthetic Integration Test Consumable`, `item_group=Consumable`, `stock_uom=Nos`, `is_stock_item=1`, `disabled=0`, **opening_stock=0**, no serial/batch rules, no price, item warehouse defaults or valuation transaction. Before writes verify no duplicate Item and party/account/transaction baseline; postverify and commit single transaction. **Do not create opening stock, Stock Reconciliation, Stock Entry, Withdrawal Slip, Billing Batch, invoices or GL/Stock Ledger records under this approval**; these must be reviewed and separately approved with backups because perpetual inventory posting has financial consequences. Persistent DEVELOPMENT `development.localhost` and PRODUCTION excluded. No new backup or item insert has happened yet.

## Isolated inventory master/readiness SQL audit; stock prerequisites absent — 2026-10-13

Operator ran isolated-site read-only SQL inventory prerequisites audit on `ccpc-integration2.localhost` (site-specific DB identity separately checked against persistent `development.localhost`; exact TISS/TREQ company pair verified). Output confirms exactly 5 warehouses per company: root `All Warehouses - TISS/TREQ` (group), leaf `Finished Goods`, `Goods In Transit`, `Stores`, and `Work In Progress` in each, all enabled. Key possible issue location: `Stores - TISS` is a verified enabled leaf warehouse owned by issuer. Each Company has 13 standard leaf Departments including `Operations - TREQ`; audit did **not** include Department `disabled` flag. Zero `CCPC Section` records. Exactly 6 item groups `All Item Groups` (group), `Consumable`, `Products`, `Raw Material`, `Services`, `Sub Assemblies` (leaf). **No `Item` records, no `Bin` records.** `tabWithdrawal Slip`, `tabStock Entry`, `tabStock Ledger Entry`, `tabSales Invoice`, `tabPurchase Invoice`, `tabGL Entry`, `tabIntercompany Material Billing Batch` all zero at this read-only checkpoint. `INVENTORY PREREQUISITES AUDIT: COMPLETED`.

Reviewed verified app review branch `review/intercompany-approval-failure-tests` source:
- `ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.py`: explicitly supplied `source_warehouse` must be an enabled leaf owned by `slip.company`; automatic default only searches a specially named `Warehouse 1` (absent from verified setup), **so use explicit `Stores - TISS`, not implicit default**. `company=TISS`, `requesting_company=TREQ`; requesting `department` must be eligible enabled leaf owned by TREQ via `validate_department_company(..., require_eligible=True)` in `equipment_costing.py`. `section` required only if enabled CCPC Section records exist for the chosen Department; no sections found now, so optional unless changed. Withdrawal Slip requires requestor, approving supervisor, required date, department, physical location, purpose, and at least one stocked item with requested quantity <= warehouse actual Bin quantity. If equipment/job order are omitted, corresponding optional validation does not require them.
- `ccpcerp/ccpc_erp/withdrawal_slip_stock.py`: `make_material_issue` requires approved operational status `Stockroom Review`, `received_by`, eligible Stockroom/System Manager authorization or Administrator, no previous submitted issue, and generates a `Material Issue` Stock Entry with a per-row `withdrawal_slip_item` pointer. Stock Entry validation checks issue quantities, provenance, company/warehouse, and availability on submission; direct manual synthetic stock-ledger inserts must not bypass hooks.
- `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py`: billing-source query requires submitted `Stock Entry` `purpose=Material Issue`, `se.company=ws.company=TISS`, `ws.requesting_company=TREQ`, posting date in billing month, and Stock Entry Detail with `withdrawal_slip_item` nonblank. Finalization/approval must occur after billing month end, and required roles, locks, and invoice mapping validations apply.

**Proposed safe next gate, NOT yet authorized:** one read-only query checking candidate TREQ department `Operations - TREQ` enabled status, `Stores - TISS` leaf properties, `Nos` UOM availability, `Consumable` item group, stock settings/Company inventory setup and absence of `Stock Reconciliation`/other stock transactions; then seek separate operator approval for a **sixth protected post-party/pre-item backup** and creation of one explicitly synthetic stocked Item by normal Frappe API. Opening quantity/valuation via supported Stock Reconciliation is **a separate material inventory/GL transaction** needing further explicit approval and backup/rollback review. Do not create stock, slips or invoices merely because user pasted audit. No production or persistent DEVELOPMENT work. Five distinct protected archive-verified backups exist through pre-party; no post-party backup or restore test yet.

## Internal-party persisted SQL mappings independently verified — 2026-10-13

Operator supplied **separate read-only MySQLdb post-commit** result against isolated `ccpc-integration2.localhost`, with command configured to STOP if test site `db_name` matched persistent `development.localhost`. Unlike previous precommit doc checks, this verifies committed DB rows directly:
```text
CUSTOMER
(('Integration Test Requester', 'Integration Test Requester', 'Intercompany', 'Philippines', 1, 'Integration Test Requester', 0),)

SUPPLIER
(('Integration Test Issuer', 'Integration Test Issuer', 'Intercompany', 1, 'Integration Test Issuer', 0),)

ALLOWED COMPANIES
('Customer', 'Integration Test Requester', 'companies', 'Integration Test Issuer')
('Supplier', 'Integration Test Issuer', 'companies', 'Integration Test Requester')

PARTY ACCOUNTS
('Customer', 'Integration Test Requester', 'accounts', 'Integration Test Issuer', '1312 - Intercompany Receivable - TISS')
('Supplier', 'Integration Test Issuer', 'accounts', 'Integration Test Requester', '2121 - Intercompany Payable - TREQ')

INTERCOMPANY GROUPS
Customer Group ('All Customer Groups', 0)
Supplier Group ('All Supplier Groups', 0)

TRANSACTION BASELINE
tabStock Entry 0
tabStock Ledger Entry 0
tabSales Invoice 0
tabPurchase Invoice 0
tabGL Entry 0
tabIntercompany Material Billing Batch 0

INTERNAL PARTY POST-COMMIT CHECK: VERIFIED
```
The **one-direction TISS->TREQ customer/supplier prerequisite configuration is independently confirmed persisted**. These checks did not create Stock Entries, invoices, Billing Batches or accounting records. Account values and names were independently verified in preceding eight-account postcommit audit; most recent party audit confirms the relevant mapping text. The fifth backup is archive integrity-checked but was taken before these parties were created; no new post-party snapshot exists and **no restoration drill** done.

Next: review on verified GitHub application review branch `review/intercompany-approval-failure-tests` the live `Withdrawal Slip`, `Stock Entry` hooks, Item/stock prerequisites, and Billing Batch source-row conditions before a synthetic stock-flow plan. Any proposed material/stock transaction write requires **separate explicit approval**, a new protected post-party baseline backup recommended, and safeguards for site isolation, rollback and transaction integrity. Keep persistent DEVELOPMENT and PRODUCTION out of scope.

## Fifth-checkpoint protected; TISS-to-TREQ internal parties created and verified — 2026-10-13

Operator ran the **already approved** single guarded insert command on isolated DEVELOPMENT site `ccpc-integration2.localhost` only, after confirming the fifth recovery snapshot at `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-accounts-pre-parties-20261013` with artifact prefix `20261013_151050-ccpc-integration2_localhost` and matching database identity. Script preflight confirmed two company accounting configurations, eight correct intercompany accounts, parent party groups and Philippines Territory, no existing party/transaction records, then used normal `frappe.get_doc(...).insert(ignore_permissions=True)` APIs to create **exactly four** parent/party master records (plus corresponding child rows), verified everything before a single `frappe.db.commit()`, and printed:

```text
Isolated site: VERIFIED
Fifth recovery checkpoint: VERIFIED
Two-company accounting configuration: VERIFIED
Party groups and Territory: VERIFIED
No existing party records or transactions: VERIFIED
Creating approved internal trading parties...

Customer Group: Intercompany VERIFIED
Supplier Group: Intercompany VERIFIED

Internal Customer: Integration Test Requester
Represents: Integration Test Requester
Allowed company: Integration Test Issuer
Receivable account: 1312 - Intercompany Receivable - TISS

Internal Supplier: Integration Test Issuer
Represents: Integration Test Issuer
Allowed company: Integration Test Requester
Payable account: 2121 - Intercompany Payable - TREQ

Customer count: 1
Supplier count: 1
Party Account rows: 2
Allowed company rows: 2
Financial transaction baseline: EMPTY

INTERNAL TRADING PARTIES: CREATED AND VERIFIED
```

Specific new records:
- `Customer Group` **Intercompany** (leaf under `All Customer Groups`).
- `Supplier Group` **Intercompany** (leaf under `All Supplier Groups`).
- Internal `Customer` name **Integration Test Requester**, `customer_name=Integration Test Requester`, `customer_type=Company`, `customer_group=Intercompany`, `territory=Philippines`, `is_internal_customer=1`, `represents_company=Integration Test Requester`, `disabled=0`, sole `Allowed To Transact With` **Integration Test Issuer**, sole `Party Account` **1312 - Intercompany Receivable - TISS** owned by issuer.
- Internal `Supplier` name **Integration Test Issuer**, `supplier_name=Integration Test Issuer`, `supplier_type=Company`, `supplier_group=Intercompany`, `is_internal_supplier=1`, `represents_company=Integration Test Issuer`, `disabled=0`, sole allowed company **Integration Test Requester**, sole `Party Account` **2121 - Intercompany Payable - TREQ** owned by requester.
- Explicit non-self-company mappings; `tabCustomer` 1, `tabSupplier` 1, `tabParty Account` 2, `tabAllowed To Transact With` 2. Company count 2, account count 198. Empty `Stock Entry`, `Stock Ledger Entry`, `Sales Invoice`, `Purchase Invoice`, `GL Entry`, `Intercompany Material Billing Batch` checked before and immediately prior to commit.

**Verification status:** Results from operator-pasted terminal output, including normal Frappe DocType reads immediately before commit. Separate **post-commit independent read-only SQL validation is still outstanding**. Backup archive integrity checked, **not** full restoration. These parties support **TISS issuing to TREQ only**, not reverse direction. No material-issue Stock Entries, withdrawal slip records, submitted transaction, billing batch, finance-approval, or actual DB integration tests yet. Persistent `development.localhost` and PRODUCTION untouched by authorized procedure.

**Next step:** one read-only independent SQL inspection of the persisted Customer/Supplier parent fields, both exact `Allowed To Transact With` child rows and `Party Account` child rows, the two Intercompany groups, and all transaction tables. Confirm separate site database identity before connecting. If verified, plan the next synthetic document fixtures by reviewing GitHub current CCPC withdrawal slip, stock issue and billing code/DocTypes, requirements and account correctness. **Request fresh explicit approval before any synthetic Stock Entry, withdrawal slip, invoice, billing batch or other substantive data writes**. Do not rerun already-successful party creation or historical real-company patches.

## Fifth recovery checkpoint independently archive-verified before synthetic internal parties — 2026-10-13

After explicit owner approval, operator ran the **guarded fifth full site backup only** on `ccpc-integration2.localhost` and provided command output. Pre-backup read-only preconditions passed: isolation from persistent `development.localhost`, exactly two test companies with 198 accounts total and eight exact intercompany ledger accounts, intended customer/supplier group parents, leaf `Philippines` Territory, zero internal Customer/Supplier/Party Account/Stock Entry/Stock Ledger Entry/Sales Invoice/Purchase Invoice/GL Entry/Billing Batch records, and four earlier full snapshot artifacts preserved. No synthetic party writes were performed by this backup command.

Official `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"` wrote into the protected **absolute directory** `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-accounts-pre-parties-20261013` with prefix `20261013_151050-ccpc-integration2_localhost`. Operator's verification:
```text
Isolated site: VERIFIED
Both companies and 198 accounts: VERIFIED
Eight dedicated intercompany accounts: VERIFIED
Customer/Supplier group prerequisites: VERIFIED
Territory: VERIFIED
Party and transaction baseline: VERIFIED
Four earlier recovery checkpoints: PRESERVED
Creating fifth recovery checkpoint...
Backup for Site ccpc-integration2.localhost has been successfully completed with files
Verifying fifth recovery checkpoint...
database.sql.gz | 980410 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
FIFTH RECOVERY CHECKPOINT: VERIFIED AND SECURED
```
This confirms **five distinct archive-verified recovery checkpoints**. The new files contain site configuration secrets, remain restricted to protected private directory, and must never be committed to GitHub. No recovery restore test has been performed.

Reviewed current authoritative `ccpcerp` application branch `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e`, especially batch `_get_internal_party` and historical real-CCPC-only party patch. Reviewed ERPNext v16 `Customer`, `Supplier`, `Customer Group`, `Supplier Group` controllers and `erpnext.accounts.party.validate_party_accounts`: Customer/Supplier identity may be by name or naming series; each document supports child tables `companies` (Allowed To Transact With) and `accounts` (Party Account), which validates account belongs to expected company. Customer/Supplier group parent records `All Customer Groups`/`All Supplier Groups` are groups; `Intercompany` should be leaf. `Customer` should represent TREQ and only be allowed under TISS with TISS `1312` receivable; `Supplier` should represent TISS and only allowed under TREQ with TREQ `2121` payable. The other direction is not yet being tested.

**Next authorized action:** one guarded, test-site-only standard-ERPNext document insert of exactly two `Intercompany` group masters plus one internal Customer and one internal Supplier with a single allowed-company row and a single Party Account row apiece; check fifth snapshot identity first, absence of all parties, intact eight dedicated accounts and empty transaction baseline, verify all created fields and counts before a single commit, on error rollback and do **not** blindly rerun. No invoice, billing batch, GL, stock, migration or PRODUCTION scope. Current documentation records verified backup only, **not** that internal party creation succeeded.

## Owner approved fifth snapshot and minimal TISS-to-TREQ internal parties — 2026-10-13

Operator explicitly replied **Approved** to a scoped plan for (1) a new **post-eight-accounts, pre-internal-parties** full recovery snapshot and (2) only the test-site `Intercompany` Customer Group and Supplier Group, internal Customer representing `Integration Test Requester (TREQ)` allowed to transact only with `Integration Test Issuer (TISS)` and linked to issuer receivable `1312 - Intercompany Receivable - TISS`, and internal Supplier representing `Integration Test Issuer (TISS)` allowed only with `Integration Test Requester (TREQ)` and linked to requester payable `2121 - Intercompany Payable - TREQ`.

Authority is **exclusively isolated DEVELOPMENT site `ccpc-integration2.localhost`**. The fifth recovery snapshot should use protected directory `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-accounts-pre-parties-20261013` and site-specific, absolute backup path; must check correct DB identity distinct from persistent `development.localhost`, verify prior four snapshots remain, eight dedicated ledger records retained/each test company has 99 accounts, Customer and Supplier groups absent, one leaf Philippines Territory, and zero Customer, Supplier, Party Account, billing, GL, stock and sales/purchase invoice data. Account/group/root/party details must be reconfirmed read-only before any write; Frappe backup housekeeping can delete standard-backup files older than configured hours, so guard default retention before running `bench backup` with absolute `--backup-path`. Validate resulting database gzip, public/private tar, site_config JSON/db identity and secure permissions. **Do not create internal parties until fifth snapshot is confirmed successful.** All preexisting snapshots must remain.

Internal-party writes later (after snapshot confirmation) must use standard ERPNext document APIs, company and account allowlists, exact reciprocal per-direction Party Account mappings, group validation, and postinsert checks before single DB commit. Customer and Supplier DocType names may be naming series, so validate their actual `customer_name`, `supplier_name` and `represents_company`, not assume primary keys. Existing real-company-only CCPC historical patches are out of scope and must not run. No reverse-direction parties, stock entries, invoices, billing batches, migrations, or persistent DEVELOPMENT/PRODUCTION changes were authorized. No snapshot or party writes have been reported yet in response to this approval.

## Post-commit synthetic ledger and internal-party prerequisites audit verified — 2026-10-13

Operator ran a **read-only post-commit** MySQL audit on isolated `ccpc-integration2.localhost` after the fourth snapshot and eight account insertions. Readout confirms eight exact-account records persisted:
```text
Integration Test Issuer | 1312 | 1312 - Intercompany Receivable - TISS | Receivable
Integration Test Issuer | 2121 | 2121 - Intercompany Payable - TISS | Payable
Integration Test Issuer | 5150 | 5150 - Intercompany Materials Expense - TISS | [blank]
Integration Test Issuer | 6050 | 6050 - Intercompany Material Charges - TISS | [blank]
Integration Test Requester | 1312 | 1312 - Intercompany Receivable - TREQ | Receivable
Integration Test Requester | 2121 | 2121 - Intercompany Payable - TREQ | Payable
Integration Test Requester | 5150 | 5150 - Intercompany Materials Expense - TREQ | [blank]
Integration Test Requester | 6050 | 6050 - Intercompany Material Charges - TREQ | [blank]
Dedicated account count: 8
```
Customer Group master has `All Customer Groups` (is_group=1) and non-group `Commercial`, `Government`, `Individual`, `Non Profit` (no `Intercompany`). Supplier Group has `All Supplier Groups` (is_group=1) and non-group `Distributor`, `Electrical`, `Hardware`, `Local`, `Pharmaceutical`, `Raw Material`, `Services` (no `Intercompany`). Territory `Philippines` (leaf) exists under `All Territories`. `tabCustomer`, `tabSupplier`, `tabParty Account`, `tabStock Entry`, `tabSales Invoice`, `tabPurchase Invoice`, `tabIntercompany Material Billing Batch` all remain count 0 at audit.

Further reviewed `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` on verified `review/intercompany-approval-failure-tests` app branch: `approve_and_create_invoices` obtains exactly one enabled **Customer representing requesting company** and exactly one enabled **Supplier representing issuing company**. For **one-direction integration test only**, minimum synthetic party design (not yet authorized/executed):
1. `Customer Group` `Intercompany` as leaf under `All Customer Groups`; `Supplier Group` `Intercompany` leaf under `All Supplier Groups`.
2. One Customer named in `customer_name` field `Integration Test Requester` (actual document identifier may follow naming series), `customer_type=Company`, `territory=Philippines`, `is_internal_customer=1`, `represents_company=Integration Test Requester`, `disabled=0`, with sole `Allowed To Transact With` company `Integration Test Issuer` and one Party Account row for issuer `1312 - Intercompany Receivable - TISS`.
3. One Supplier named in `supplier_name` field `Integration Test Issuer` (actual document identifier may use naming series), `supplier_type=Company`, `is_internal_supplier=1`, `represents_company=Integration Test Issuer`, `disabled=0`, sole allowed company `Integration Test Requester` and Party Account row for requester `2121 - Intercompany Payable - TREQ`.
4. No self-trading links or own-company Party Account rows. Company and account scope must be validated. This minimal two-party configuration only supports `TISS` -> `TREQ` billing; reverse direction would require two additional parties later.
5. ERPNext version-16 Customer/Supplier controllers run `validate_party_accounts` plus internal uniqueness checks and may generate naming series IDs. Use supported document inserts, preflight table schema/defaults and naming, followed by postcommit read-only validation. Existing `ccpcerp/patches/v1_0/create_intercompany_parties.py` is **not applicable** because it targets actual CCPC-company names.

**Next approval gate**: obtain explicit operator authorization for taking a **new post-account/pre-party recovery snapshot** and creating only two `Intercompany` group records + exactly one internal Customer, one internal Supplier, each with one allowed-companies row and one Party Account row. Preserve prior four snapshots; archive verification != tested restore. No additional data was written by the audit, and no party fixtures have yet been created. Invoice submission, stock movements, GL entries, persistent `development.localhost`, or PRODUCTION are outside scope.

## Eight isolated intercompany ledger accounts created and verified — 2026-10-13

Operator ran the previously approved single-shot Frappe/ERPNext Account fixture insertion **only on isolated `ccpc-integration2.localhost`**. Before writes, script rechecked target-vs-persistent-`development.localhost` database isolation; fourth snapshot `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-requester-pre-accounts-20261013/20261013_135316-ccpc-integration2_localhost-*` (four nonempty files, matching DB identity, archive checks documented separately); exactly two test companies `Integration Test Issuer (TISS)` and `Integration Test Requester (TREQ)`; complete Frappe/ERPNext setup; valid PHP/Philippines Company settings and enabled non-group Cost Centers; 95 Standard CoA accounts per company; eight suitable enabled parent groups; no name/number conflicts, and no Stock Entries, Sales Invoices, Purchase Invoices, Billing Batches, GL Entries, Customers, Suppliers or Party Account rows.

Using `frappe.get_doc({"doctype":"Account", ...}).insert()` (no SQL INSERT, no historical real-company patches), it created and checked **exactly four non-group PHP ledger accounts for each company**:

| Account number | Account name | Parent group | Root / account type |
|---|---|---|---|
| `1312` | `Intercompany Receivable` | `Accounts Receivable - <abbr>` | Asset / Receivable |
| `2121` | `Intercompany Payable` | `Accounts Payable - <abbr>` | Liability / Payable |
| `5150` | `Intercompany Materials Expense` | `Indirect Expenses - <abbr>` | Expense / blank |
| `6050` | `Intercompany Material Charges` | `Indirect Income - <abbr>` | Income / blank |

Full account names are `<number> - <account_name> - TISS` and `<number> - <account_name> - TREQ`, matching `ccpcerp` billing-code string requirements. The command postchecked each account's saved `company`, number, account name, expected parent, root type, account type, ledger/non-group, enabled status and PHP currency; exactly 99 Account rows per company; exactly two Companies; unchanged empty transaction and party baseline. It performed **one `frappe.db.commit()` only after these checks**. User-reported terminal end:
```text
Isolated site: VERIFIED
Fourth recovery checkpoint: VERIFIED
Both company configurations: VERIFIED
All eight parent accounts: VERIFIED
No account name/number conflicts: VERIFIED
Transaction and party baseline: VERIFIED
Creating eight dedicated accounts...

COMPANY: Integration Test Issuer (TISS)
VERIFIED: 1312 - Intercompany Receivable - TISS
VERIFIED: 2121 - Intercompany Payable - TISS
VERIFIED: 5150 - Intercompany Materials Expense - TISS
VERIFIED: 6050 - Intercompany Material Charges - TISS
Total company accounts: 99

COMPANY: Integration Test Requester (TREQ)
VERIFIED: 1312 - Intercompany Receivable - TREQ
VERIFIED: 2121 - Intercompany Payable - TREQ
VERIFIED: 5150 - Intercompany Materials Expense - TREQ
VERIFIED: 6050 - Intercompany Material Charges - TREQ
Total company accounts: 99

Total companies: 2
EIGHT INTERCOMPANY ACCOUNTS: CREATED AND VERIFIED
```
**Completion boundary:** Account fixtures and pre-account archive verified, but no separate post-commit SQL confirmation yet, no restoration drill, no real database integration/rollback/concurrency tests, no internal Customer/Supplier or Party Account fixtures, and **no inventory or financial transactions**. Existing historical patches hardcode real CCPC business companies and must not be run on TISS/TREQ.

**Next:** read-only checks on Customer Group/Supplier Group/Territory defaults, Company ledger Cost Centers, exact eight account records and current empty-party/transaction baseline, then plan scoped internal test Customer representing TREQ for TISS and internal test Supplier representing TISS for TREQ, with company allowlist and dedicated Party Account mapping. Obtain explicit separate operator permission before creating party fixtures; present prior archive-verified snapshot situation and consider a new post-account/pre-party snapshot. Do not change persistent `development.localhost` or PRODUCTION.

## Fourth isolated recovery snapshot verified before intercompany-account inserts — 2026-10-13

Operator executed the **approved** pre-account site-scoped backup on isolated `ccpc-integration2.localhost` after synthetic `TISS` and `TREQ` Companies were created. Read-only safety checks passed: target DB isolated from `development.localhost`, exact two-company names and abbreviations, 95 existing Standard CoA accounts in each Company, verified company-specific enabled parent Account groups `Accounts Receivable`, `Accounts Payable`, `Indirect Expenses`, `Indirect Income`, no dedicated account numbers 1312/2121/5150/6050, no Stock Entries, Sales/Purchase Invoices, billing batches, Customers or Suppliers; prior three backup checkpoints preserved.

Backup command used **absolute path** `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-requester-pre-accounts-20261013` with `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"`. Operator output:
```text
Site isolation: VERIFIED
Two-company baseline: VERIFIED
Standard account parent groups: VERIFIED
No dedicated intercompany accounts: VERIFIED
Transaction and internal party baseline: VERIFIED
Three earlier recovery snapshots: PRESERVED
Backup for Site ccpc-integration2.localhost has been successfully completed with files
database.sql.gz | 979004 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
POST-TREQ BACKUP: VERIFIED AND SECURED
```
New snapshot filename prefix `20261013_135316-ccpc-integration2_localhost`. **This is the fourth** archive-verified recovery checkpoint (no full restore drill yet). No intercompany accounts have been inserted yet.

As explicitly approved, next authorized step is **one guarded creation of exactly eight standard-ERPNext Account ledger records**, four numbers `1312`, `2121`, `5150`, `6050` in each of `TISS` and `TREQ`, with exact names and valid parent groups matching the Standard CoA. Use Frappe `Account.insert()` and a single `frappe.db.commit()` only after verifying all eight account records; stop and inspect rather than rerun if exceptions occur. ERPNext v16 source confirms `get_autoname_with_number` returns `<number> - <account_name> - <company_abbr>`, enforces nonduplicate number/company and parent groups, derives account currency from Company, and runs nested-set update on save. Do not execute real-company-specific historical patches. Current operator approval does not include internal Customers/Suppliers, Stock Entries, invoices, or other sites/production. GitHub documentation update is not evidence that those eight accounts have been created.

## Approved isolated post-TREQ backup and eight intercompany ledger fixtures — 2026-10-13

Operator explicitly **approved** creating another full, site-scoped backup and adding the **eight** test-only `Account` ledger rows (four each, two fictional test companies) on isolated `ccpc-integration2.localhost`: `1312 - Intercompany Receivable` (Asset/Receivable, under existing Accounts Receivable group), `2121 - Intercompany Payable` (Liability/Payable, under existing Accounts Payable group), `5150 - Intercompany Materials Expense` (Expense, under existing Indirect Expenses group), `6050 - Intercompany Material Charges` (Income, under existing Indirect Income group), each suffixed by `TISS` or `TREQ`. Scope **excludes** internal party creation, Stock Entries, Sales/Purchase Invoices, broad site migrate, persistent `development.localhost`, PRODUCTION, and historical real-business company patches. Request remains one verified step at a time.

Before account writes: take a fourth recovery snapshot named `post-requester-pre-accounts-20261013` using **absolute** `bench backup --backup-path` (avoid old `sites/sites/` mistake), `--with-files --ignore-backup-conf`. Confirm source target-db isolation, exact two company records, 95 standard accounts each, no existing dedicated 1312/2121/5150/6050 accounts, zero transaction counts, preserved earlier backups, and safe standard-backup retention; validate new database archive with `gzip -t`, public/private TAR listings, JSON and DB identity, and restrict permissions. Previously archived backups, including post-wizard/pre-TREQ `20261013_133756`, are archive checked but **not restore tested**. The backup must be reported as operator-verified before moving to Account inserts; no silent site execution by GitHub tool. Frappe v16 `new_backup` calls `delete_temp_backups` in default backup location even when absolute `--backup-path` is provided, so preflight must guard against any stale standard-directory files that it might delete.

After backup is confirmed, Account document APIs should preflight and verify exact names, unique numbers, valid company-specific enabled parent group/root, company cost center and transaction baseline, create all eight in one guarded transaction, post-verify and commit once. No account fixture changes yet reported as executed.

## Read-only TISS/TREQ intercompany account and party fixture audit — 2026-10-13

Operator's read-only SQL audit completed on isolated `ccpc-integration2.localhost` (explicit target-vs-persistent-DEVELOPMENT database name comparison in command); no write occurred. `Integration Test Issuer` (`TISS`), `Integration Test Requester` (`TREQ`) each have **95 Standard Chart of Accounts records** distributed as Asset=29, Equity=6, Expense=33, Income=7, Liability=20, with default cost centers `Main - TISS` / `Main - TREQ`, and inventory account `Stock In Hand - TISS` / `Stock In Hand - TREQ`. Each has **zero Account records with numbers 1312, 2121, 5150, or 6050**. Global `tabCustomer` count 0 (internal 0), `tabSupplier` count 0 (internal 0), and `tabParty Account` 0. This is a synthetic test fixture gap, not an error in Company insertion.

The TISS chart contains verified parent groups `Accounts Receivable - TISS` (Asset), `Accounts Payable - TISS` (Liability), `Indirect Expenses - TISS` (Expense), `Indirect Income - TISS` (Income). TREQ was created from same Standard template, but **its specific parent group names/properties must be verified** before any new account writes. In `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` reviewed on branch `review/intercompany-approval-failure-tests`, exact invoice defaults per Company abbreviation are `1312 - Intercompany Receivable` (Asset/Receivable), `2121 - Intercompany Payable` (Liability/Payable), `5150 - Intercompany Materials Expense` (Expense), and `6050 - Intercompany Material Charges` (Income); they must be enabled, valid leaf accounts. `_get_internal_party` requires **exactly one enabled internal Customer representing the requester** and **one enabled internal Supplier representing the issuer**. ERPNext v16 `Account` controller `autoname` uses `get_autoname_with_number` and enforces unique account number per company, proper group parent and root. Historical real-company-specific CCPC patches expect a different parent account numbering and must **not** be run here.

**Proposed fixture design (not executed or approved):** create four exact additional ledger accounts per fictional company under existing verified Standard-chart parent groups, e.g. receivable in Accounts Receivable, payable in Accounts Payable, expense in Indirect Expenses, income in Indirect Income. Validate names, numbers, company, root, type, is_group=0, enabled, and parent groups, no duplicate account number/name; use Frappe `Account.insert()` in one guarded test-site-only transaction, no SQL inserts. Verify both company charts preserve baseline. In a later separately approved stage, create appropriate `Intercompany` Customer/Supplier groups as needed and internal Customer/Supplier with company restrictions and Party Accounts, after inspecting group/territory defaults. Before account fixture changes, consider taking a new post-second-company/pre-accounts checkpoint; third verified backup is pre-second-company. No permission to create accounting fixtures yet; request explicit approval. No actual Stock Entry, Sales/Purchase Invoice or real-DB rollback/concurrency test was run.

## Isolated DEVELOPMENT second synthetic company created and verified — 2026-10-13

Operator completed the **explicitly approved** single Frappe/ERPNext Company document insert on isolated `ccpc-integration2.localhost`, after verifying the full `20261013_133756` post-wizard/pre-requester recovery snapshot, correct 2026 fiscal year, both composite indexes and zero transaction baseline. Operator terminal output:
```text
Isolated site: VERIFIED
Post-setup recovery snapshot: VERIFIED
Company, fiscal year, indexes, and transaction baseline: VERIFIED
Creating Integration Test Requester (TREQ)
Requester: Integration Test Requester
Abbreviation: TREQ
Country: Philippines
Currency: PHP
Default cost center: Main - TREQ
Requester accounts: 95
Requester warehouses: 5
Total companies: 2
SECOND TEST COMPANY: CREATED AND VERIFIED
```
The script used `frappe.get_doc({"doctype":"Company", "company_name":"Integration Test Requester", "abbr":"TREQ", "country":"Philippines", "default_currency":"PHP", "enable_perpetual_inventory":1, "create_chart_of_accounts_based_on":"Standard Template", "chart_of_accounts":"Standard"}).insert()` and committed after verifying the returned Company fields, non-group enabled requester Cost Center belonging to TREQ, nonzero chart and warehouses, and exactly two companies. Previously verified issuer is `Integration Test Issuer` (`TISS`, PHP, Philippines, `Main - TISS`). No stock entries, sales invoices, purchase invoices, or billing batches were created by the submitted company-create script; transaction counts were checked before the insert, not rechecked afterward. **No real DB billing workflow, rollback, or concurrency tests executed.**

**GitHub code review**: `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` requires exact ledger accounts `1312 - Intercompany Receivable - {abbr}`, `2121 - Intercompany Payable - {abbr}`, `5150 - Intercompany Materials Expense - {abbr}`, `6050 - Intercompany Material Charges - {abbr}` and enabled leaf Cost Centers, plus internal Customer representing requester and internal Supplier representing issuer for invoice creation. `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` expects parent accounts tailored to real CCPC chart (`1310`, `2001`, `5100`, `6000`); `create_intercompany_parties.py` targets four actual CCPC-group companies. Neither patch should run blindly on fictional TISS/TREQ standard charts. Do not assume dedicated accounts/parties exist.

**Next safely authorized action:** read-only inspection of TISS/TREQ default accounts, available account parent hierarchies, existing internal Customers/Suppliers/Party Account rows and current transaction baseline. Then design a scoped synthetic account/party fixture plan in GitHub and request explicit permission for master-data writes (current approval covered second Company only). All backup archives remain private with pre-index, pre-wizard and post-wizard/pre-requester snapshots; archive checks are not full restore tests. No modifications to `development.localhost` or PRODUCTION.

## Isolated DEVELOPMENT post-setup/pre-requester backup verified — 2026-10-13

User explicitly **approved creating a new post-setup backup and second fictional test Company** `Integration Test Requester` (`TREQ`, Philippines/PHP, ERPNext Standard CoA), exclusively on `ccpc-integration2.localhost`, after `Integration Test Issuer` (`TISS`) completed its wizard. No authorization for stock moves, invoice creation, historical real-company patches, persistent `development.localhost`, or PRODUCTION.

Operator ran guarded full-site `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"`, using an **absolute** path to avoid the earlier accidental `sites/sites` duplication. All post-setup/pre-requester baseline checks and archive integrity succeeded:
```text
Isolated site: VERIFIED
Initial ERPNext setup: VERIFIED
Previous recovery backups: PRESERVED
Pre-requester transaction baseline: VERIFIED
Backup for Site ccpc-integration2.localhost has been successfully completed with files
database.sql.gz | 973014 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database gzip integrity: PASSED
Public and private archives: PASSED
Database identity: VERIFIED
POST-SETUP BACKUP: VERIFIED AND SECURED
```
Protected backup location within bench:
`sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-setup-pre-requester-20261013/`
Four files have common filename prefix `20261013_133756-ccpc-integration2_localhost`. This is the **third** preserved checkpoint, after the pre-index and pre-wizard backups. Gzip/TAR/JSON verification and live DB name identity checks passed; **no full restore test** performed. No second Company has yet been created, no transaction records created.

Source-reviewed `erpnext/version-16/erpnext/setup/doctype/company/company.py`: new `frappe.get_doc({"doctype":"Company",...}).insert()` invokes standard `on_update` routines creating chart of accounts, default warehouses, default cost center, and company departments. Use ERPNext standard chart name `Standard`; do not rerun setup wizard nor run `bench migrate`. Require a one-site preflight showing `TISS` only, valid post-setup snapshot, isolated DB, zero transactional records, existing 2026 fiscal year, company abbreviations, and previously verified indexes before the **one-time** insertion. Then verify TREQ’s exactly matching Company fields, default leaf cost center, nonzero chart of accounts and warehouses, and issuer preservation; stop and inspect on any failure. Frappe Company hooks may make broader fixture/config changes; do not blindly retry. Do not run old CCPC account/customer/supplier patches hardcoded for real group entities, and dedicated billing accounts/parties are not yet created.

## Post-wizard isolated integration baseline independently checked — 2026-10-13

User pasted read-only `MySQLdb` result for `ccpc-integration2.localhost`, confirming site database remains different from persistent `development.localhost` (command would stop otherwise). Verified exact values:
```text
Companies: (('Integration Test Issuer', 'TISS', 'PHP', 'Philippines', 'Main - TISS'),)
Fiscal years: (('2026', datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)),)
Billing indexes:
idx_icmb_scope VERIFIED
idx_icmbi_source_parent VERIFIED
Transaction baseline:
tabStock Entry: 0
tabSales Invoice: 0
tabPurchase Invoice: 0
tabIntercompany Material Billing Batch: 0
POST-SETUP READ-ONLY CHECK: COMPLETED
```
Both composite indexes retain full ordered nonunique BTREE definitions without prefixes after wizard, and the four tested transaction DocTypes remain empty. **No Purchase or Sales Invoices, Stock Entries, or Billing Batches have been created.** One Company is present, with issuer default enabled-leaf Cost Center not independently checked yet. No tests of actual accounting/inventory operations, deadlocks or transaction rollback yet.

Reviewed relevant source on verified `ccpcerp/ccpcerp` branch `review/intercompany-approval-failure-tests`: `_validate_companies` in batch DocType only rejects identical issuing/requesting company (it does not restrict to the four actual-group-name constants of historical seed patches). `_get_company_invoice_defaults` requires exact non-group receivable/payable/expense/income accounts `1312`, `2121`, `5150`, `6050` with names suffixed by test-company abbreviations, plus valid Cost Centers. In ERPNext v16 `Company` document insertion can create default COA, cost centers and warehouses; new test requester should use standard Frappe document API, not direct SQL or re-run setup wizard.

**Next approval gate:** take distinct **post-wizard pre-second-company** site-scoped full backup in a unique protected location, verify archives and preserve older snapshots; then create one additional fictional `Integration Test Requester` (suggest abbreviation `TREQ`, country Philippines, PHP, Standard COA) on `ccpc-integration2.localhost` only. User's prior approval covered the first issuer company setup, not the second company or synthetic financial transactions. Seek their separate approval for backup + second Company before any write. Use site-scoped permissions and preflight. Do not invoke historic real-company party/account patches automatically; plan separate test-fixture account/party and synthetic transaction steps. No PRODUCTION action.

## Isolated DEVELOPMENT ERPNext initial setup verified — 2026-10-13

Operator completed previously approved **one-time Frappe/ERPNext version-16 initial setup** exclusively on isolated `ccpc-integration2.localhost`, using the official `frappe.desk.page.setup_wizard.setup_wizard.setup_complete(args)` entrypoint called once from the site context rather than `bench execute`. Inputs were `Integration Test Issuer` (abbreviation `TISS`), `Philippines`, `PHP`, `Asia/Manila`, `2026-01-01` through `2026-12-31`, chart template `Standard`, `setup_demo=0`, `enable_telemetry=0`. Preflight confirmed distinct target DB versus persistent `development.localhost`, four archive-verified pre-setup snapshot files in `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/pre-setup-20261013` and an initially uninitialized/empty master-data baseline.

Operator terminal output (reported, not independently queried by connector):
```text
Site isolation: VERIFIED
Pre-setup recovery snapshot: VERIFIED
Initial setup preconditions: VERIFIED
Initializing Integration Test Issuer (TISS)
Updating Dashboard for frappe
Updating Dashboard for erpnext
Updating Dashboard for ccpcerp
Setup wizard returned: SUCCESS
frappe setup_complete = 1
erpnext setup_complete = 1
ccpcerp setup_complete = 0
Test company abbreviation: TISS
Fiscal Year: 1 records
Account: 95 records
Cost Center: 2 records
Warehouse: 5 records
UOM: 239 records
Item Group: 6 records
INITIAL ERPNEXT SETUP: VERIFIED
```
Python produced nonfatal warnings because interpreter was invoked with `../env/bin/python` while inside `sites`; command completed successfully. The CCPC flag remains 0 as app has no active wizard setup-complete hook; Frappe and ERPNext 1 signify base wizard completion. Only one fictional Company was created, **not** the second `Integration Test Requester`. Do **not** infer default chart is compatible with the custom billing code's exact accounts `1312`, `2121`, `5150`, `6050`; source review found these must be provisioned intentionally for each test Company. Do not run real-group-only historical intercompany account/party patches with fictional firms. Existing two composite intercompany billing indexes were separately verified before wizard, but **should be checked read-only afterward**. No Stock Entries, Sales/Purchase Invoices or real DB integration/rollback/concurrency tests performed. Do not touch persistent `development.localhost` or PRODUCTION. Pre-setup backup is archive verified, not restoration tested.

**Next:** read-only post-wizard verification of `Company`, `Global Defaults`/`System Settings`, `Fiscal Year`, `Account` / `Cost Center` / `Warehouse` essentials, and retained billing index definitions. Then plan a post-setup checkpoint and request separate user approval for creating the second fictional Company and scoped test fixtures; do not make unintended transactions.

## Isolated DEVELOPMENT pre-setup snapshot verified and relocated — 2026-10-13

User approved taking a fresh pre-wizard snapshot of **`ccpc-integration2.localhost`** and running initial ERPNext setup for fictional issuer `Integration Test Issuer (TISS)`, Philippines/PHP, 2026-01-01 through 2026-12-31, ERPNext Standard chart, no demo data. During the first backup command Frappe's `--backup-path` interpreted a relative `sites/...` beneath the bench `sites` directory, creating a `sites/sites/...` path and causing the wrapper's immediate verification to fail (not a reported backup failure). Subsequent guarded command validated backup database identity and `gzip -t` / `tar -tf` / JSON, preserved older `20261013_102539` backup, and moved only the new snapshot to the intended site directory. Operator output:
```text
Backup database identity: VERIFIED
Previous backup: PRESERVED
Backup archive integrity: PASSED
20261013_104420-ccpc-integration2_localhost-database.sql.gz | 899304 bytes
20261013_104420-ccpc-integration2_localhost-files.tar | 10240 bytes
20261013_104420-ccpc-integration2_localhost-private-files.tar | 10240 bytes
20261013_104420-ccpc-integration2_localhost-site_config_backup.json | 212 bytes
Backup relocated to: /workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/pre-setup-20261013
PRE-SETUP BACKUP: VERIFIED AND SECURED
```
Archive validation is **not** a full test restore. No ERPNext wizard or synthetic company/data writes yet reported. Preserve both snapshots and never commit their contents. User authorization covers site-scoped initial ERPNext wizard setup and backup only; **not** stock entries, purchase/sales invoices, persistent `development.localhost`, or PRODUCTION.

Source review `frappe/version-16` and `erpnext/version-16` shows authoritative wizard function `frappe.desk.page.setup_wizard.setup_wizard.setup_complete(args)` dispatches ERPNext stages. ERPNext `stage_fixtures`, `setup_company` and `setup_defaults` provision baseline records. The ERPNext Standard chart argument is `"Standard"`; no demo data when `setup_demo=0`. CCPC hooks branch contains no active `setup_wizard_stages` or `setup_wizard_complete` hook; therefore after success **Frappe and ERPNext flags** should be 1 while CCPC may remain 0. Initial setup also changes site system settings and may enable the site scheduler. Next step: run guarded one-site official setup entrypoint (never broad `bench migrate`), report postconditions and any exceptions without rerun, and document actual result.

## Isolated DEVELOPMENT Setup Wizard completion flags verified — 2026-10-13

Operator ran a read-only parameterized `MySQLdb` query of `tabInstalled Application` on **`ccpc-integration2.localhost`**. Results: `ccpcerp setup_complete = 0`, `erpnext setup_complete = 0`, `frappe setup_complete = 0`. This is consistent with no initial setup wizard yet completed and the documented zero UOM / Item Group / Fiscal Year / Account / Cost Center / parties / Warehouse / Company records. Frappe, ERPNext and CCPC apps remain installed, two billing composite indexes independently verified, and pre-index archive-verified backup preserved.

GitHub `ccpcerp/hooks.py` on reviewed app branch shows no active `setup_wizard_stages` or `setup_wizard_complete` declarations; a separate `after_migrate = "ccpcerp.setup.after_migrate"` hook exists but must **not** invoke general `bench migrate` to initialize this test site. Review of Frappe/ERPNext v16 setup source confirms initial setup provisions normal master data through supported setup APIs, including fixtures and a first Company; full setup will write many configuration/master-data rows and should be run **only after explicit approval for isolated site**. Existing historical CCPC accounts/parties patches use actual group company names, and must not be run indiscriminately with fictional companies. No wizard invocation, test master-data writes, or production actions performed yet.

**Next proposed decision:** seek approval to perform supported initial ERPNext setup using entirely fictional issuer company, `Philippines`, `PHP`, fiscal year 2026, without demo/company business data copied from live sites; document complete steps and verify postconditions. Then separately plan a second fictional requester company and accounts/parties/warehouses for real DB integration tests, with backup checkpoints. Do not mark any synthetic transaction as a tested result until executed in this DB.

## Isolated DEVELOPMENT ERPNext setup/master-data readiness confirmed — 2026-10-13

Operator ran read-only table existence and `COUNT(*)` checks **only on `ccpc-integration2.localhost`** after the index milestone. Results: `tabCurrency=149`; `tabUOM=0`, `tabItem Group=0`, `tabFiscal Year=0`, `tabAccount=0`, `tabCost Center=0`, `tabCustomer Group=0`, `tabSupplier Group=0`, and `tabTerritory=0`. Prior checks likewise found zero Company/Warehouse/Item/Stock Entry/Sales Invoice/Purchase Invoice/Billing Batch/Billing Item rows. Installation has created DocTypes but core operational master data is not provisioned, so end-to-end inventory/billing database integration tests cannot yet run. No records created by this check.

**Frappe/ERPNext version-16 source review (GitHub):** `erpnext/setup/setup_wizard/setup_wizard.py` sequences fixtures, company, defaults; `erpnext/setup/setup_wizard/operations/install_fixtures.py` creates UOMs, Item Groups, Territory, Customer/Supplier Groups, fiscal year, first Company and defaults; `frappe/__init__.py:is_setup_complete()` checks `tabInstalled Application.is_setup_complete` for Frappe and ERPNext. Fresh-site configuration is not the same as a completed setup wizard. Review readiness and wizard flags read-only before proposing any write. Avoid direct SQL inserts; use supported Frappe/ERPNext APIs with synthetic company names on the isolated site, after separate authorization, and plan code/fixture prerequisites on GitHub first. Real-business-name-only CCPC account/party historical patches must not be used blindly with fictional test companies. The user has not yet authorized creating fixture or financial records.

## Isolated DEVELOPMENT integration fixture baseline confirmed empty — 2026-10-13

Operator ran read-only `MySQLdb` queries against `ccpc-integration2.localhost` after two required index definitions were created/verified. All eight tables exist and each contained **0 rows**: `tabCompany`, `tabWarehouse`, `tabItem`, `tabStock Entry`, `tabSales Invoice`, `tabPurchase Invoice`, `tabIntercompany Material Billing Batch`, and `tabIntercompany Material Billing Item`. These results do not assert other ERPNext configuration tables are empty. The site is an empty baseline for isolated synthetic data; **there is no current real-DB end-to-end coverage** of stock, billing, rollback, permissions, or concurrency.

**GitHub source review:** `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py` replaces Frappe DB with `MagicMock`, and `test_intercompany_billing_approval_failures.py` explicitly documents mocked failure-path checks, not true MariaDB rollback. Billing invoice defaults in `intercompany_material_billing_batch.py` require both companies with enabled non-group cost centers and dedicated account names by abbreviation `1312` receivable, `2121` payable, `5150` expense, `6050` income. The historical account and internal-party seed patches `create_intercompany_material_accounts.py` and `create_intercompany_parties.py` are hardcoded for four actual business-name companies (CCPC/RMC/GSL/WFC) and expect chart-of-accounts parents; do not execute these patches on arbitrary fictional companies or assume fresh `install-app` executed their bodies. Suitable synthetic tests should use **new fictional company names and abbreviations with explicitly test-scoped prerequisite accounts and parties**, or have separately reviewed fixtures; do not copy any real DEVELOPMENT/PRODUCTION data.

**Next:** plan/version test fixtures in GitHub-first review process, inspect necessary Frappe/ERPNext master-data requirements and then request distinct approval before creating fixtures/financial records on `ccpc-integration2.localhost`. Leave persistent `development.localhost`, PRODUCTION, historical patch log and untracked `AGENTS.md` untouched. Existing site backup is a pre-index recovery point only and restoration has not been tested.

## Isolated DEVELOPMENT billing indexes created and independently verified — 2026-10-13

**Operator-approved schema operation completed successfully** on `ccpc-integration2.localhost` only. Operator submitted terminal output for guarded command executed inside `frappe_docker_devcontainer-frappe-1` as `frappe` user. Preconditions checked `review/intercompany-approval-failure-tests` at exact commit `806fa23516490ec7beefcff03a1baa09d722120e` with no tracked modifications, four pre-change backup artifacts existed, and new site had a different DB name from persistent `development.localhost`. The command used `bench --site ccpc-integration2.localhost execute ccpcerp.patches.v1_0.add_intercompany_material_billing_indexes.execute` (not `bench migrate` or Patch Log change). Output:
```text
Isolated DEVELOPMENT database: VERIFIED
Executing approved index patch on ccpc-integration2.localhost only
Index patch command completed.
idx_icmb_scope: VERIFIED
idx_icmbi_source_parent: VERIFIED
BOTH INDEX DEFINITIONS VERIFIED
```
Independent parameterized `information_schema.STATISTICS` queries on the new site's own DB credentials confirmed the full ordered columns, NON_UNIQUE=1, BTREE index type, no prefix lengths for:
- `idx_icmb_scope` on `tabIntercompany Material Billing Batch` (`issuing_company`, `requesting_company`, `billing_month`)
- `idx_icmbi_source_parent` on `tabIntercompany Material Billing Item` (`stock_entry_detail`, `parent`)

**Status now: indexes are present and verified**; historical notes below that say 'missing' reflect earlier pre-correction observations, not the current state. Pre-change backup dated `20261013_102539` passed gzip/TAR/JSON archive checks; a restoration test was NOT performed. No evidence of changes to persistent `development.localhost` or PRODUCTION, and no general migration was invoked. **Not yet tested:** database integration, financial correctness, idempotency, rollback, concurrency, permissions and actual end-to-end transaction behavior. Proceed with a **read-only** test-fixture readiness check, then separately authorize synthetic test data/transactions (isolation, clean rollback/cleanup strategy, and snapshots) before writes. Do not assume production readiness.

## Isolated DEVELOPMENT pre-index backup archive integrity verified — 2026-10-13

Operator ran read-only archive/config checks on the four full-site backup files under `sites/ccpc-integration2.localhost/private/backups/`, prefix `20261013_102539-ccpc-integration2_localhost`. Reported:
```text
Database gzip integrity: PASSED
Public files archive: PASSED
Private files archive: PASSED
Site configuration JSON: PASSED
BACKUP ARCHIVE CHECKS: PASSED
```
Site config JSON was parsed without displaying secrets. Four nonempty files and basic archive integrity have been verified, **but no restoration test** has been performed. Both requested non-unique composite billing indexes are still absent. Next gate is **distinct user approval** for index DDL on this isolated site only, after backups and checks, using reviewed code and postconditions. DDL has implicit commit/metadata-lock risks. No broad migration, patch-log edit, persistent DEVELOPMENT modification, or PRODUCTION action.

## Isolated DEVELOPMENT full-site backup completed — 2026-10-13

Operator reported successful **site-scoped** `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path ...` run at server timestamp `2026-10-13 10:25:40` in the DEVELOPMENT Frappe container, exit success, followed by a four-file non-empty verification printed `BACKUP FILE VERIFICATION: PASSED`. Artifacts under `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/backups/`:

- `20261013_102539-ccpc-integration2_localhost-database.sql.gz` — 899266 bytes
- `20261013_102539-ccpc-integration2_localhost-files.tar` — 10240 bytes
- `20261013_102539-ccpc-integration2_localhost-private-files.tar` — 10240 bytes
- `20261013_102539-ccpc-integration2_localhost-site_config_backup.json` — 212 bytes

Preflight stopped if site config missing, backup path symlink, custom backup destination, existing files in backup directory, or low host free space; `umask 077`, directory permissions `700`, and backup output verified four nonempty artifacts. Backup is **not yet archive-integrity-tested or restore-tested**. The site config backup includes secrets; never copy backup files, database contents, or config JSON to GitHub. Next: read-only integrity verification `gzip -t`, `tar -tf`, JSON parse without printing sensitive content. After that, obtain distinct explicit authorization before any DDL to create two known missing composite indexes exclusively on the isolated site. No `bench migrate`, patch-log edit, existing `development.localhost` changes or PRODUCTION operations authorized.

## Isolated DEVELOPMENT billing index column preflight verified — 2026-10-13

Operator read-only `information_schema.COLUMNS` query against `ccpc-integration2.localhost` confirmed all five requested index columns: `tabIntercompany Material Billing Batch` has `issuing_company varchar(140)`, `requesting_company varchar(140)`, and `billing_month date`; `tabIntercompany Material Billing Item` has `stock_entry_detail varchar(140)` and `parent varchar(140)`. Earlier check established both tables exist, neither requested named index exists, and no equivalent matching non-unique BTREE composite index is present. This satisfies basic column-presence/type preflight; it does not mean indexes have been created or tested under concurrency.

**Next controlled step:** obtain separate authorization and complete a verified backup of only the isolated site (including database/configuration and files), preserving the output securely; then request explicit approval for DDL creating the two narrowly scoped indexes. Any index creation should use the reviewed CCPC patch logic and verify `information_schema.STATISTICS` postconditions. Do not edit `tabPatch Log`, broadly `bench migrate`, touch persistent `development.localhost`, or operate on PRODUCTION. Fresh install may have pre-marked patch as complete.

## Isolated DEVELOPMENT equivalent-index inspection — 2026-10-13

The operator ran a read-only metadata query using MySQLdb on `ccpc-integration2.localhost`. The **only reported secondary indexes** are `creation` on `tabIntercompany Material Billing Batch` and `parent` on `tabIntercompany Material Billing Item`; **no equivalent composite indexes** for either CCPC-defined target were found. Missing named targets `idx_icmb_scope` and `idx_icmbi_source_parent` were separately confirmed earlier. Both tables exist. This is an expected possible fresh-install discrepancy because Frappe v16 `install_app(..., set_as_patched=True)` marks historical patches as completed by inserting Patch Log rows, not calling their `execute()` functions. No conclusion of DB corruption or confirmed runtime error should be made.

GitHub review branch `review/intercompany-approval-failure-tests` still points to `806fa23516490ec7beefcff03a1baa09d722120e`. Its index patch defines two NON-UNIQUE BTREE composite indexes, checks for equivalent/conflicting definitions, and creates indexes using `frappe.db.add_index`; it does not provide database-level uniqueness. No index DDL or patch re-execution has been approved or performed yet. **Next:** read-only check target columns' availability/types and table sizes, then independently approved backup and isolated-site-only index creation with exact schema/postcondition checks; no broad `bench migrate`, no Patch Log editing, no PRODUCTION actions.

## Isolated DEVELOPMENT billing tables confirmed; new-install patch-log semantics reviewed — 2026-10-13

Operator read-only MySQLdb `information_schema.TABLES` checks against `ccpc-integration2.localhost` reported **both** `tabIntercompany Material Billing Batch: PRESENT` and `tabIntercompany Material Billing Item: PRESENT`. Earlier checks found `idx_icmb_scope` and `idx_icmbi_source_parent` absent but the named index patch logged in `tabPatch Log`.

**New source finding:** In GitHub Frappe `version-16` `frappe/installer.py`, `install_app(name, ..., set_as_patched=True)` defaults to marking app patches completed; `set_all_patches_as_completed(app)` inserts Patch Log entries without invoking the patch `execute()`. `frappe/commands/site.py` routes `bench install-app` through that installer. This behavior **plausibly explains** a patch logged on fresh install while two custom indexes remain absent; installed Frappe 16.33.1's exact local source for this function has not yet been read to confirm identical behavior. Avoid describing these logged patches as successfully executed or declaring database corruption.

**Next safe operator action:** read-only inspect `information_schema.STATISTICS` of the two new-site tables for equivalent composite non-unique BTREE indexes under different names, then decide separately whether a backed-up, explicitly approved site-scoped index patch is warranted. No `bench migrate`, patch-log edits, DDL, financial test transactions, or PRODUCTION changes were performed.

## DEVELOPMENT billing index patch inconsistency — 2026-10-13

Operator's read-only MySQLdb queries against **only** `ccpc-integration2.localhost` showed `idx_icmb_scope: MISSING` and `idx_icmbi_source_parent: MISSING`, while a subsequent parameterized query showed `Patch Log table: PRESENT` and `Index patch recorded as executed: True` for `ccpcerp.patches.v1_0.add_intercompany_material_billing_indexes`. The query does not yet prove why patch log and index state differ. Do not treat patch-log presence as evidence that DDL ran, especially on a newly installed site. No migration, patch re-execution, or table/index mutation authorized. Previous standalone `frappe.init` attempt failed due to incorrect sites path, followed by logging path failure; neither reached index query. Direct MySQLdb checks are read-only and succeeded.

**Next:** verify the billing tables actually exist and inspect matching/equivalent index metadata read-only; review installer patch-marking semantics before any site-scoped migration or DDL. Keep DEVELOPMENT persistent site and PRODUCTION untouched.

## Isolated DEVELOPMENT full application registration verified — 2026-10-13

Operator executed read-only `bench --site ccpc-integration2.localhost list-apps` following the successful site and app installation. Output:
```text
frappe  16.33.1 version-16
erpnext 16.34.2 version-16
ccpcerp 0.0.1   review/intercompany-approval-failure-tests
```
All three applications are registered on the isolated site. This does **not** prove the intercompany billing schema indexes/patches, hooks, transaction integrity, permissions, or concurrent operations function correctly. No data-changing integration tests or PRODUCTION actions performed. Next step is read-only checks of applicable index and patch state, then plan synthetic tests with explicit approval and preserved backups.

## Isolated DEVELOPMENT CCPC app installation completed — 2026-10-13

Operator reported `bench --site ccpc-integration2.localhost install-app ccpcerp` completed with `Updating DocTypes for ccpcerp: 100%` and `CCPC installation exit code: 0`. Previous terminal verification established the new site's separate functioning MariaDB schema, Frappe 16.33.1 and ERPNext 16.34.2 installed. Prior to installation, DEVELOPMENT custom-app checkout was `review/intercompany-approval-failure-tests` at `806fa23` with untracked `AGENTS.md` deliberately preserved; the guarded installation command checked the exact full commit `806fa23516490ec7beefcff03a1baa09d722120e` and would stop if mismatched. Installer success is operator-provided output; post-install `list-apps`, schema/migration status, live hooks and integration tests have **not** yet been verified. No financial workflow tests or PRODUCTION operations reported.

**Next safe step:** read-only `bench --site ccpc-integration2.localhost list-apps` and basic installed-app check; then plan isolated, synthetic DEVELOPMENT database tests, migration/index review and backups separately. Do not run real billing transactions, cleanup, `bench migrate`, or PRODUCTION changes without specific approval.

## Isolated DEVELOPMENT integration site created and database verified — 2026-10-13

Operator ran guarded non-interactive `bench new-site ccpc-integration2.localhost --db-root-username=root --db-host=mariadb --db-type=mariadb` in `frappe_docker_devcontainer-frappe-1`, using `pexpect` and an existing verified DEV MariaDB root credential conveyed through an in-memory Docker pipe (not printed). A separate site Administrator password was entered privately. Reported `Installer exit status: 0`, `Installer signal status: None`. Next, a read-only Python/MySQLdb check reported: `New site configuration: PRESENT`, `Separate database name: True`, `New site database connection: SUCCESS`, `Database contains tables: True`. These establish successful Frappe site/database creation. ERPNext and CCPC application installation on the new site **remain unverified/not reported**.

The original failed `ccpc-integration.localhost` directory remains preserved; its configured DB/user were verified absent earlier. Persistent `development.localhost` was not intentionally targeted; no PRODUCTION operation was authorized. The new site is logically database-separated on shared DEV host, not physically isolated. **Next safe action:** read-only inspect installed apps for `ccpc-integration2.localhost`, confirm installed bench apps and current custom-app review branch before a separately staged `bench --site ccpc-integration2.localhost install-app erpnext` followed by CCPC app. No financial test transactions, migrations on existing DEV site, forced cleanup, or PRODUCTION actions.

## DEVELOPMENT partial integration-site database and user confirmed absent — 2026-10-13

**Operator terminal evidence:** Following a successful DEV MariaDB local-root authentication using the container's configured `MYSQL_ROOT_PASSWORD` and a successful read-only `SHOW DATABASES`, the operator ran a piped Python/SQL query. The Frappe container read `db_name` and `db_user` from the partial `ccpc-integration.localhost/site_config.json` without printing the identifiers, and the separate **DEVELOPMENT** MariaDB container queried `information_schema.SCHEMATA` and `mysql.user`. Actual reported results:

```text
Partial database exists: False
Partial database user exists: False
```

These checks establish absence of the **configured identifiers** in the DEV MariaDB server at the time of the query; they do not prove there are no unrelated orphan objects. The prior TCP root authentication failure (1045) did not prevent local socket authentication with the configured container root password. The partial site directory remains on disk. No database write, user creation, site deletion, restart, retry, or PRODUCTION operation occurred.

**Next safe decision:** Preserve the partial directory while planning controlled new-site recovery. Do not run `bench new-site --force`, remove files, or overwrite the existing DEVELOPMENT site. Consider choosing a *new, unique* test-site name and new DB identifiers rather than deleting the partial site, after a read-only collision check. Any actual new-site command requires a reviewed, prompt-safe credential procedure; ensure the administrator secret used is accepted from the DEV Frappe network, not merely through the local MariaDB socket. No financial integration tests or PRODUCTION changes authorized.

## DEVELOPMENT MariaDB root login from Frappe container rejected — 2026-10-13

**Operator-reported read-only authentication test:** The operator executed the approved interactive Python `MySQLdb.connect(host="mariadb", user="root", passwd=getpass.getpass(...))` from the **DEVELOPMENT Frappe** container. It returned `Database connection failed. Error code: 1045` (MariaDB access denied), before either `information_schema.SCHEMATA` or `mysql.user` SELECT could run. **Partial test database/user existence remains unverified**. The root password was not shown in the terminal transcript and must not be requested, printed, logged or committed. A 1045 can reflect wrong credentials **or** a root-account host/login restriction, so do not assume the operator entered the wrong secret.

**Next one read-only diagnostic:** On the Ubuntu host, check if the **DEVELOPMENT MariaDB container's local Unix socket** permits OS root to connect as MariaDB root without supplying or printing a password. Use only `frappe_docker_devcontainer-mariadb-1` and a harmless `SELECT 1`, suppressing any auth/error details:

```bash
docker exec --user root frappe_docker_devcontainer-mariadb-1 sh -lc '
if mariadb --protocol=socket --user=root --batch --skip-column-names --execute="SELECT 1" >/dev/null 2>&1; then
  echo "DEV MariaDB local socket root login: available"
else
  echo "DEV MariaDB local socket root login: unavailable"
fi
'
```

This does not modify databases or use production containers; if unavailable, stop and verify the **DEV-only** MariaDB administrator credential source and host-access policy through sanitized inspection, never dumping env vars/secret contents. No new-site retry, `--force`, deletion, password reset, rollback, migrations or real financial integration tests approved. Partial `ccpc-integration.localhost` site directory and config remain present, distinct configured DB name/user from `development.localhost`; no successful MariaDB object creation verified. Earlier approved DEV four-part backup format checked, not restore-tested. If the mistakenly entered superuser name was a real password, treat as exposed and plan controlled rotation after proper credential ownership identification, without repeating it.

## DEVELOPMENT partial site DB identifiers checked without disclosure — 2026-10-13

**Operator-provided read-only results:** Within the DEVELOPMENT Frappe container, read (but did **not** print) `db_name` and `db_user` fields in the partial `sites/ccpc-integration.localhost/site_config.json`; compared its database name to persistent `development.localhost`. Results:

```text
1. Partial site has DB name: True
2. Different from existing DEVELOPMENT DB: True
3. Partial site has DB user: True
```

The partial site has its own *configured* DB name/user, distinct from the persistent site's DB name; **none of these booleans proves that a database or user was actually created**. The original creation failed on MariaDB authentication during Frappe's `create_user -> get_current_host`, before the ordinary database-creation step, making absence plausible but not yet independently verified. Neither partial files nor existing site data were deleted or modified by this check; PRODUCTION untouched.

**Next read-only preflight proposal:** Query **only** the DEVELOPMENT MariaDB service `mariadb` via an interactive Python helper in `frappe_docker_devcontainer-frappe-1`, reading partial config names privately, prompting with `getpass` for MariaDB DEV root password (never in command/history/chat), and querying `information_schema.SCHEMATA` for the partial DB's existence without printing any schema names. If authenticated, optionally query `mysql.user` for the partial DB user's existence; both are SELECT only. Stop on auth error; no password logging, privilege changes, forced site recreation, rollback, or cleanup. This will enable a separately authorized safe partial-site recovery plan. If earlier user-entered SQL-username value was a real password, treat as disclosed and plan rotation separately, not in GitHub.

## DEVELOPMENT partial integration-site directory observed — 2026-10-13

**Operator-reported results after failed approved site creation:** The terminal returned `Aborted!` and prompt `gani@ccpcerpserver` after declining Frappe's rollback, then a read-only `find` of `sites/ccpc-integration.localhost` inside `frappe_docker_devcontainer-frappe-1` reported that the site path **exists** and contains **`logs`, `locks`, `private`, `site_config.json`, `public`**. Do not print/read that JSON raw because it can contain credentials; no secrets are reproduced in this handoff. Successful site creation, separate DB creation, or app installation **NOT verified**. Preserve any partial files; **no `rm`, rollback, `--force`, re-run of `new-site`, migrations, or PROD changes** are authorized at this moment.

**Source check:** Frappe version-16 GitHub `frappe/installer.py` first creates site directories and calls `make_conf` before `setup_database`. MariaDB `setup_database` calls `create_user` before `create_database`. The actual traceback occurred in `DbManager.create_user -> get_current_host -> self.db.sql("select user()")` at MySQL authentication. This strongly suggests **the database creation step was not reached**; it is nevertheless unsafe to assert there are no partial DB artifacts without an independent check.

**Next safe one-step read-only inspection** for operator on Ubuntu host: compare only whether `db_name` is configured for partial site and whether it matches the existing site, without printing names or passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
./env/bin/python -c "
import json
from pathlib import Path
root = Path(\"sites\")
old = json.loads((root / \"development.localhost\" / \"site_config.json\").read_text())
partial = json.loads((root / \"ccpc-integration.localhost\" / \"site_config.json\").read_text())
name = partial.get(\"db_name\")
print(\"Partial site has DB name:\", bool(name))
print(\"DB name differs from existing DEVELOPMENT:\", bool(name) and name != old.get(\"db_name\"))
print(\"Partial site has DB user:\", bool(partial.get(\"db_user\")))
"
'
```

Only boolean results are displayed. If the partial DB name unexpectedly matches the persistent site, STOP; if it differs, proceed with separately planned **read-only existence check** of MariaDB objects in the DEVELOPMENT DB service. Never include passwords in shell history/chat. Determine a safe, exact plan for either restoring a known empty test-site creation or renaming to a new unique test site; any partial artifact deletion needs specific review/authorization. If credential entered as DB username was a real secret, treat it as exposed and arrange safe rotation, preferably not during testing setup.

## DEVELOPMENT integration site creation halted on MariaDB authentication — 2026-10-13

**Operator-reported failed interactive setup** using the previously approved new-site command **only in DEVELOPMENT**: `docker exec -it --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '... bench new-site ccpc-integration.localhost --db-host mariadb --db-type mariadb'`. The Frappe CLI prompted `Enter mysql super user [root]:`. **A value other than `root` was entered at the username prompt**. **Do not copy that value here or into GitHub**, as it resembles a credential and was included in user-shared terminal output. Subsequent password prompt and trace reported `MySQLdb.OperationalError: (1045, "Access denied for user [REDACTED] from DEV-container network")`. Frappe then displayed the interactive prompt `Site creation failed, do you want to rollback the site? [y/N]:`.

**Immediate safety response:** Instruct operator to press **Enter** to choose the default **No**, avoiding automatic rollback/cleanup before inspecting possible partial site artifacts. Do **not** retry or run `--force`; do not assume the failed attempt left nothing. The normal MariaDB administrator username is `root`, with its password entered separately and privately. If the accidentally entered username was a real password, it is exposed in chat transcript and requires **carefully planned credential rotation**, without printing it again.

**Current status:** New site and its DB/app installation **NOT verified as successful**. No further database changes, site rollback, cleanup or real integration tests authorized pending operator report of prompt completion, read-only inspection of `sites/ccpc-integration.localhost` artifacts, and cautious handling of possible partial DB objects. The last successful preflight was an October 13 four-file DEV backup with format checks; `development.localhost` and all PRODUCTION data must be preserved. Approval to create a new DEV site did not grant approval to delete ambiguous partial artifacts or change production.

**Next operator step after returning to shell:** run a read-only presence check **within the DEV Frappe container**, showing only directory existence and filenames, not any site-config contents or passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
if [ -e sites/ccpc-integration.localhost ] || [ -L sites/ccpc-integration.localhost ]; then
  echo "Integration site path exists (partial setup possible)"
  find sites/ccpc-integration.localhost -maxdepth 1 -mindepth 1 -printf "%f\n"
else
  echo "Integration site path absent"
fi
'
```

Then review Frappe installer state/rollback semantics before issuing any recovery or repeat creation command. Site creation may have generated a configuration file containing secrets; never print it. **PRODUCTION untouched in reported operation.**

## Operator approved isolated DEVELOPMENT integration site setup — 2026-10-13

**Explicit operator approval:** User replied **"Approved"** after being asked: "Do you approve creating `ccpc-integration.localhost`, with its own new DEVELOPMENT database and Frappe, ERPNext, and CCPC applications?" This approval covers **test-site/database creation and installing these applications in the existing DEVELOPMENT bench only**. It **does not authorize** financial transaction tests, modifying the persistent `development.localhost`, a `bench migrate` on that existing site, deletion/cleanup of existing sites or data, Docker restarts, copying production records, or **any PRODUCTION changes**.

**Preflight verified in active conversation:** DEV Frappe DB configured host `mariadb`; alias belongs to `frappe_docker_devcontainer-mariadb-1` on network `frappe_docker_devcontainer_default`, whereas PROD DB `frappe_docker-db-1` is on `frappe_docker_default`. MariaDB volumes separate. Only persistent existing DEV site is `development.localhost`. Fresh four-part DEV backup from October 13 passed gzip/tar/JSON format checks but is not restore-proven. Application review branch tip `806fa23516490ec7beefcff03a1baa09d722120e`; 155/155 combined mocked unit tests passed on DEV. Live Frappe `bench new-site --help` confirmed `--db-host`, `--db-type`, `--install-app` and credential prompt options.

**Safe staged procedure:** From host run guarded creation in **DEVELOPMENT Frappe container** `frappe_docker_devcontainer-frappe-1` as `frappe` user, from `/workspace/development/frappe-bench`: check `sites/ccpc-integration.localhost` does not exist (including symlink); run `bench new-site ccpc-integration.localhost --db-host mariadb --db-type mariadb` **without** `--force`, `--db-name`, inline admin/root passwords, or `--install-app` (stage app installations separately). Frappe chooses a new database name and prompts for passwords. Operator should enter prompts privately and **not paste secrets in chat**. Inspect terminal output and successful site creation before installing ERPNext then CCPC into **the new test site only** with explicit `--site ccpc-integration.localhost`. Stop if database provisioning fails, Frappe mentions an existing site/database, or an unexpected environment appears.

**Status:** Approval granted; creation **not yet observed**. Only actual operator terminal output can confirm site/database creation. No real transaction tests authorized. This approach provides logical site/database isolation on shared DEV infrastructure, not physical isolation.

## DEVELOPMENT Frappe new-site CLI options inspected — 2026-10-13

**Operator-provided read-only CLI help output:** On the Ubuntu host the operator executed `bench new-site --help` inside `frappe_docker_devcontainer-frappe-1` at `/workspace/development/frappe-bench` and filtered the help for database/admin/install flags. Verified flags include `--db-name`, `--db-password`, `--db-type [mariadb|postgres|sqlite]` (MariaDB default), `--db-host`, `--db-port`, `--db-root-username` / `--mariadb-root-username`, `--db-root-password` / `--mariadb-root-password`, `--admin-password`, `--install-app`, `--setup-db / --no-setup-db`, `--db-user`, and `--force`. Do **not** use `--force` or pass secret/password arguments in shell commands or history.

**Proposed operation (explicit operator authorization still required):** Prepare dedicated test site `ccpc-integration.localhost` and a distinct new MariaDB schema/user on the **DEVELOPMENT** service `mariadb`, with Frappe/ERPNext/CCPC installed using currently reviewed app checkout `review/intercompany-approval-failure-tests` at last verified commit `806fa23`. Do not copy production or existing persistent DEV business data, do not change default bench site, and use synthetic fixtures for later integration testing. Site creation/app installation writes to the DEV database server and filesystem, can consume CPU/RAM/I/O on the physical host shared with production, and is **not approved by the earlier DEVELOPMENT backup-only authorization**. Explicitly check for site/database naming collisions and password-prompt behavior; avoid displaying/root credentials. Installing apps and executing any test-suite writes must be staged, observed and separately approved when necessary.

**Verified prerequisites:** Only `development.localhost` was enumerated in DEV bench; effective `db_host` was `mariadb`; the DEV Frappe/MariaDB containers share network `frappe_docker_devcontainer_default` with matching `mariadb` alias; PROD MariaDB is on `frappe_docker_default`. DEV/PROD named DB storage volumes are different. Fresh DEV four-part backup `20261013_083457-development_localhost` was created following explicit backup approval and passed nonempty, gzip, tar, JSON syntax checks (not restore-tested). 155/155 mocked unit tests passed together on app review branch `806fa23`. No site creation, data-altering tests or PRODUCTION changes yet.

**Next action:** Ask operator to explicitly approve or reject the creation and app installation of the proposed DEVELOPMENT-only test site/database. If approved, prepare a safe, prompt-driven, collision-checked command sequence **one step at a time**, avoiding plaintext credentials in CLI history; proceed to real transactional/concurrency test plan only after another risk review, backup and explicit approval.

## Live DEVELOPMENT/PRODUCTION Docker network boundaries verified — 2026-10-13

**Operator-provided Docker host read-only inspection** of network names and aliases (no environment variables or secrets):

```text
/frappe_docker_devcontainer-frappe-1
  network=frappe_docker_devcontainer_default aliases=[frappe_docker_devcontainer-frappe-1 frappe]
/frappe_docker_devcontainer-mariadb-1
  network=frappe_docker_devcontainer_default aliases=[frappe_docker_devcontainer-mariadb-1 mariadb]
/frappe_docker-db-1
  network=frappe_docker_default aliases=[frappe_docker-db-1 db]
```

**Confirmed:** The DEVELOPMENT Frappe container and its MariaDB share `frappe_docker_devcontainer_default`, with the MariaDB alias `mariadb` matching effective `development.localhost` DB host. The checked PRODUCTION MariaDB container is on separate `frappe_docker_default`, without an observed connection to the DEV network. Separate live MariaDB storage volumes were previously verified (`frappe_docker_devcontainer_mariadb-data` vs `frappe_docker_db-data`). This **does not guarantee full host-level, credential, or network segmentation**: Docker host/kernel/storage are shared and privileged processes can affect both stacks.

**Readiness:** Persistent `development.localhost` was the only configured site found in the DEV bench. Fresh, explicitly approved DEVELOPMENT four-part backup `20261013_083457-development_localhost` was completed and passed four-file nonzero, gzip, tar and JSON format checks; **no restore rehearsal** has occurred. Combined 155/155 mocked Python tests passed on application review branch `review/intercompany-approval-failure-tests` at `806fa23`. No real MariaDB invoice rollback, transaction, concurrency or schema integration test has run.

**Proposed test isolation plan — not approved/executed:** Create a distinctly named **DEVELOPMENT-only disposable test site** (e.g. `ccpc-integration.localhost`) with **its own new MariaDB database**, reusing only the DEVELOPMENT Frappe bench and MariaDB service. Do not copy persistent DEV or PRODUCTION business data, do not change bench default site or existing `development.localhost` DB, and do not perform migrations on the persistent site. Use synthetic fixtures. Review permissions, storage overhead, Frappe installation/bootstrap requirements, test runner behavior, cleanup, and restoration/recovery strategy. A site within the same DEV bench/database server is **logical isolation only**, not a separate physical server or dedicated MariaDB daemon; broader isolation would require a separate Docker project and DB volume. Request explicit owner approval for new-site/DB creation and separately review/approve any database-changing integration tests, with stop-on-error and no destructive cleanup.

**Next safe read-only step to verify command flags before a site creation proposal:** Run `bench new-site --help` **only** in the DEVELOPMENT container, filtering output for database and administrative options; do not provide or print passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
bench new-site --help | grep -Ei -- "db-|database|mariadb|admin|install" | head -n 35
'
```

After reviewing available options, propose the precise site-creation command and seek separate approval. Do not create site/DB now or touch PRODUCTION.

## Read-only DEVELOPMENT effective database endpoint — 2026-10-13

**Operator-provided output** from a read-only merge of `sites/common_site_config.json` with `sites/development.localhost/site_config.json` inside `frappe_docker_devcontainer-frappe-1`. Command printed ONLY endpoint metadata, no config secrets:

```text
DEVELOPMENT DB host: mariadb
DEVELOPMENT DB port: [default]
```

This is consistent with Docker DNS/service-name lookup to a MariaDB service on the DEVELOPMENT container's network. The default MariaDB/MySQL TCP port is generally 3306, but that was **not explicitly configured** in the files checked. **Database network identity/isolation has not yet been independently confirmed** by live Docker networking inspection. Previously verified DEV and PROD containers have separate named MariaDB data volumes; they still share the Ubuntu host and Docker daemon. Persistent DEV `development.localhost` is the only configured site found, and its fresh Oct 13 backup passed nonempty/gzip/tar/JSON format checks but has not been restore-tested. 155/155 mock tests passed together on review commit `806fa23`.

**Next one-step read-only operator action:** On Ubuntu host, inspect just network names/aliases for the DEVELOPMENT Frappe app container, DEVELOPMENT MariaDB and PRODUCTION MariaDB, **without opening environment variables, site configs or credentials**:

```bash
docker inspect --format '{{.Name}}{{range $name, $net := .NetworkSettings.Networks}}{{printf "\n  network=%s aliases=%v" $name $net.Aliases}}{{end}}' \
  frappe_docker_devcontainer-frappe-1 \
  frappe_docker_devcontainer-mariadb-1 \
  frappe_docker-db-1
```

Confirm DEV Frappe and DEV MariaDB share the relevant network and `mariadb` alias, while PROD MariaDB is on a separate network. Distinct networks and volumes lower risk but are **not complete protection** against host-level effects or privileged access. Do **not** yet create a new site/database, run database-changing integration tests, migrate, restore or touch production. An isolated site-and-database test plan requires explicit approval after further review.

## DEVELOPMENT site inventory — only persistent site exists (2026-10-13)

**Operator-provided read-only output:** A command in `frappe_docker_devcontainer-frappe-1` enumerated site directories containing `site_config.json` in `/workspace/development/frappe-bench/sites`. Its **only result** was:

```text
development.localhost/
```

This confirms there is **no preexisting second Frappe site in this DEVELOPMENT bench** based on the on-disk site directory check. `development.localhost` contains persistent DEV data and **must not be regarded as disposable**. To validate actual MariaDB invoice rollback and concurrency safely, first design a dedicated **new isolated integration-test site and distinct DEV test database**, review connectivity, fixtures and cleanup/rollback procedures, and request explicit user approval before creating any site/database or running tests. Do not use production databases or copies of production data. The fresh four-part October 13 DEV backup successfully passed gzip/tar/JSON syntax checks but is not restore-proven.

**Next one-step read-only preflight:** Review the **effective DEVELOPMENT site DB host/port only**, merging common and site JSON configuration, without printing database name, passwords or other configuration. Execute on the Ubuntu host:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
./env/bin/python -c "
import json
from pathlib import Path
base = Path(\"sites\")
common = json.loads((base / \"common_site_config.json\").read_text())
site = json.loads((base / \"development.localhost\" / \"site_config.json\").read_text())
effective = {**common, **site}
print(\"DEVELOPMENT DB host:\", effective.get(\"db_host\", \"[not set]\"))
print(\"DEVELOPMENT DB port:\", effective.get(\"db_port\", \"[default]\"))
"
'
```

A successful result identifies the configured endpoint only, **not guaranteed isolation**; separately check the Docker networks before site creation. This operation reads two DEV JSON files and prints only non-secret endpoint metadata. No DB or PROD modifications authorized. App review branch remains at verified commit `806fa23516490ec7beefcff03a1baa09d722120e` with 155 combined mocked unit tests passing.

## Fresh DEVELOPMENT backup files verified — 2026-10-13

**Operator-reported validation run** from the Ubuntu host against the approved October 13 **DEVELOPMENT-only** site backup `20261013_083457-development_localhost`, via `docker exec --user frappe frappe_docker_devcontainer-frappe-1`. The shell command checked that each of four expected files is nonempty, then ran `gzip -t` on `-database.sql.gz`, `tar -tf` on **uncompressed** `-files.tar` and `-private-files.tar`, and `python -m json.tool` on `-site_config_backup.json`; it did not print secrets or extract files. The observed output was:

```text
DEVELOPMENT fresh backup format checks: PASS
```

**Verified scope:** existence/nonzero size, gzip integrity, tar archive readability, JSON syntax for all four artifacts in the fresh DEV backup set. This does **not** prove a valid full SQL restoration, database transactional consistency, off-host availability or recovery viability. The backup is on the shared physical server. No PRODUCTION change, migrations, Docker recreation, or database-changing integration tests were executed.

**Current milestone:** Application review branch `review/intercompany-approval-failure-tests`, commit `806fa23`, previously passed **155/155 mocked Python unit tests in one combined run**. DEV and PROD MariaDB volumes were independently distinguished by read-only live Docker inspect. Before any **real** Frappe/MariaDB transactional/concurrency tests, plan and authorize a **separate test site/database** and independent fixtures/rollback; do not run `bench run-tests` directly against persistent `development.localhost` or use production business data.

**Next low-risk read-only operator step:** Enumerate the existing site directories in the DEVELOPMENT bench **without reading site config contents**, so a unique isolation plan can be designed without colliding with existing sites:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit
for d in sites/*/; do
  [ -f "${d}site_config.json" ] && printf "%s\n" "${d#sites/}"
done
'
```

The results list site names only (no database passwords). Decide whether any site is available for isolated testing from explicit ownership/usage evidence; **do not assume a site is disposable**. Then document/review the new test site's database connection, backups, fixtures, migration and rollback procedure and request explicit operator approval before creating or modifying anything.

## Approved fresh DEVELOPMENT backup completed — 2026-10-13

**Explicit operator approval** was obtained in chat to create a fresh backup **only** for the persistent DEVELOPMENT Frappe site `development.localhost`. The operator ran on Ubuntu:

```bash
docker exec -it --user frappe \
  frappe_docker_devcontainer-frappe-1 \
  bash -lc 'cd /workspace/development/frappe-bench && bench --site development.localhost backup --with-files'
```

**Operator-provided successful output**, reporting backup summary at `2026-10-13 08:34:58.481811` and final `Backup for Site development.localhost has been successfully completed with files`:

- `sites/development.localhost/private/backups/20261013_083457-development_localhost-site_config_backup.json` — **234 B**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-database.sql.gz` — **1.6 MiB**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-files.tar` — **10.0 KiB**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-private-files.tar` — **20.0 KiB**

Unlike the October 9 `.tgz` file archives, this fresh October 13 backup has **uncompressed `.tar` public/private file archives**; therefore validate with `tar -tf` (no gzip flag). **Actual existence, compression/readability, complete database contents, and restore usability have not yet been independently verified after the completed backup command**. Backup is in local DEV site backup directory on host-shared storage, not demonstrated off-host. No database-changing tests, migrations, restore operations, or PROD actions were requested or reported.

**Next one safe, read-only operator action** on the Ubuntu host: validate all four new DEV backup artifacts inside the DEVELOPMENT Frappe container, checking nonzero files, gzip CRC, tar listings and config JSON syntax without printing config:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit
B=sites/development.localhost/private/backups/20261013_083457-development_localhost
for suffix in database.sql.gz files.tar private-files.tar site_config_backup.json; do
  test -s "${B}-${suffix}" || exit 1
done
gzip -t "${B}-database.sql.gz" &&
tar -tf "${B}-files.tar" >/dev/null &&
tar -tf "${B}-private-files.tar" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEVELOPMENT fresh backup format checks: PASS"
'
```

Even when these checks pass, do **not** represent them as a tested restore or database transaction-consistency verification. Before real concurrent billing approval/rollback experiments, review isolated test data and recovery/isolation plan, confirm that backup can be restored to an isolated environment, and obtain separate explicit operator approval. The last verified application review branch tip was `806fa23516490ec7beefcff03a1baa09d722120e`, with 155/155 combined mocked Python unit tests passing in DEVELOPMENT.

## DEVELOPMENT backup-destination capacity preflight — 2026-10-13

**Operator-reported read-only Docker container filesystem check** on Ubuntu host:

```bash
docker exec frappe_docker_devcontainer-frappe-1 \
  bash -lc 'df -h /workspace/development/frappe-bench/sites && df -i /workspace/development/frappe-bench/sites'
```

Result for filesystem `/dev/nvme0n1p2` mounted at `/workspace`: **915G total, 182G used, 687G available, 21% utilization**. Inodes: **60,981,248 total; 7,574,738 used; 53,406,510 free; 13% usage**. Capacity is ample relative to the known October 9 DEV archive sizes, but this is host-shared storage and free space alone does not prove successful backup or guarantee no host resource contention.

**Backup readiness checkpoint:** Site `development.localhost` listed Frappe 16.33.1, ERPNext 16.34.2 and CCPC 0.0.1; 155 combined isolated Python mock tests passed; DEV and PROD use separate named MariaDB Docker volumes; Oct 9 four-part DEV backup archives passed gzip/tar/JSON syntax checks but were not restore-tested and are four days old. Live DEV backup freshness, successful restoration, DB transactional/concurrency correctness and independent off-host recovery remain **unverified**.

**Next operator decision (do not execute without approval):** Obtain explicit agreement to create a **new DEVELOPMENT-only four-part site backup** from within `frappe_docker_devcontainer-frappe-1`, bench directory `/workspace/development/frappe-bench`, targeting **only** `development.localhost` using `bench --site development.localhost backup --with-files`. This reads the DEV database and writes new backup artifacts to the DEV site's local backups directory; it may consume shared host disk and I/O but does not intentionally mutate business records. Do not use `--site ccpcerp.local` or any production container. After approval, run safely and verify four new matching-prefix files, syntax and integrity, and consider separate recovery or off-host strategy before database-changing tests. No `bench migrate`, `run-tests`, ERPNext transactions, database restore or PRODUCTION operations authorized.

## Verified distinct live DEV and PROD MariaDB storage volumes — 2026-10-13

**Operator-provided read-only host Docker inspection:** On `gani@ccpcerpserver`, inspecting the `/var/lib/mysql` mounts for both running database containers returned:

```text
/frappe_docker_devcontainer-mariadb-1: volume frappe_docker_devcontainer_mariadb-data /var/lib/docker/volumes/frappe_docker_devcontainer_mariadb-data/_data -> /var/lib/mysql
/frappe_docker-db-1: volume frappe_docker_db-data /var/lib/docker/volumes/frappe_docker_db-data/_data -> /var/lib/mysql
```

**Conclusion:** Verified **separate named Docker volumes and separate host source paths** for DEV and PROD MariaDB data directories, matching the intended Compose project separation. This establishes database *storage directory* separation, **not independent physical servers**, full network/credential segregation, database/schema completeness or restore viability. The environments share the physical Ubuntu host and Docker daemon; direct Docker privileges can affect both. No production mutation occurred from this read-only inspect.

**Safety status:** 155/155 mocked Python tests passed in one combined DEVELOPMENT run at app review commit `806fa23`. The October 9 four-part DEV backup passed gzip/tar/JSON syntax checks but is stale for Oct 13 and has not been restored. Actual MariaDB rollback/durability, locking/concurrency, Frappe integration and indexed schema tests remain pending; no migrations or database-changing tests approved.

**Next safe operator action:** Check the filesystem's available space/inodes for the *DEV site backup destination only*, from the Ubuntu host without opening credentials or touching production:

```bash
docker exec frappe_docker_devcontainer-frappe-1 bash -lc 'df -h /workspace/development/frappe-bench/sites && df -i /workspace/development/frappe-bench/sites'
```

Use the output to plan a new complete `development.localhost` backup and eventual separated restoration rehearsal/rollback review. Do **not** execute a fresh backup, database-integrated test, `bench migrate`, restore, or prod action until its precise scope/safety plan is agreed with the operator.

## Live DEVELOPMENT and PRODUCTION database container discovery — 2026-10-13

**Operator-provided read-only Docker host output** from `gani@ccpcerpserver`:

```text
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -Ei 'NAMES|mariadb|db-'
NAMES                                      STATUS
frappe_docker_devcontainer-mariadb-1       Up 23 hours
frappe_docker-db-1                         Up 24 hours (healthy)
```

Confirms two **distinct running MariaDB containers**, first under the DEVELOPMENT Compose project and second under the PRODUCTION project. **It does not yet establish separate Docker database volume mounts or independent physical storage**; both share the Ubuntu host and Docker daemon. Do not infer "healthy" status for DEV, as its output only says Up.

**Next one-step read-only Docker mount verification** to run on the Ubuntu **host**, with no environment/config secrets printed:

```bash
docker inspect --format '{{.Name}}:{{range .Mounts}}{{if eq .Destination "/var/lib/mysql"}} {{.Type}} {{.Name}} {{.Source}} -> {{.Destination}}{{end}}{{end}}' \
  frappe_docker_devcontainer-mariadb-1 \
  frappe_docker-db-1
```

Compare DEV vs PROD mounts. No DB integration tests, fresh backup, schema changes, restore or PRODUCTION actions have been authorized. October 9 DEV four-file archive validation passed only compression/JSON syntax checks, not restore. The 155 combined mocked unit tests passed on app review commit `806fa23`.

## DEVELOPMENT Oct 9 backup archive syntax verification — 2026-10-13

**Operator-provided terminal output:** From `/workspace/development/frappe-bench` inside DEVELOPMENT, the operator ran read-only validation against the four `sites/development.localhost/private/backups/20261009_061614-development_localhost-*` backup artifacts:

```bash
B=sites/development.localhost/private/backups/20261009_061614-development_localhost
gzip -t "${B}-database.sql.gz" &&
tar -tzf "${B}-private-files.tgz" >/dev/null &&
tar -tzf "${B}-files.tgz" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEV backup files: compression and JSON syntax checks passed"
```

Actual reported output: **`DEV backup files: compression and JSON syntax checks passed`**. This establishes that all four listed files have readable compression/archive syntax or valid JSON structure; it **does NOT** verify SQL consistency/completeness, archive contents against the Frappe site, restoration, or current-day data coverage. These are October 9 artifacts being checked on October 13. No files extracted; no DB connection or write; no PRODUCTION action.

**Next safe operator action, one step at a time:** On the **Ubuntu Docker host** (exit the DEV container shell first), run the following **read-only** database-container discovery, without printing credentials/config:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -Ei 'NAMES|mariadb|db-'
```

Review the returned live DB container names, then use a separately designed **read-only** Docker mount inspection to confirm DEV and PRODUCTION database data mounts/volumes are distinct, without printing secrets. They are separate Compose projects but share host and Docker daemon. Only after verifying boundaries, backup freshness and recovery plans should the operator be asked to authorize a fresh DEVELOPMENT backup and database-integrated transaction tests. Do not run `bench run-tests` or `bench migrate` or backup restore now.

## Read-only DEVELOPMENT backup inventory — 2026-10-13

**Operator-provided listing, not archive integrity or restore verification.** From the DEVELOPMENT container in `/workspace/development/frappe-bench`, listing `sites/development.localhost/private/backups` showed the following four file artifacts with filesystem mtime **2026-10-09 00:46**:

- `20261009_061614-development_localhost-database.sql.gz` — **1,646,365 bytes**
- `20261009_061614-development_localhost-private-files.tgz` — **9,599 bytes**
- `20261009_061614-development_localhost-site_config_backup.json` — **234 bytes**
- `20261009_061614-development_localhost-files.tgz` — **141 bytes**

The file-name timestamp and mtime display differ; do not assume the time zone without checking. There is one four-part matching-prefix backup set in the 20-entry output. Presence of files **does not establish gzip/tar integrity, DB completeness, database origin, restore usability or recovery time**. On 2026-10-13 this backup is roughly four days old and may not contain recent DEVELOPMENT changes. Never expose site-config JSON contents; it can contain passwords and other sensitive values. Do not use production backups for DEV integration tests.

**Next one-step operator preflight (read-only, no extraction or DB access):** Validate archive compression and site_config JSON structure without printing contents, from the DEVELOPMENT bench:

```bash
cd /workspace/development/frappe-bench
B=sites/development.localhost/private/backups/20261009_061614-development_localhost
gzip -t "${B}-database.sql.gz" &&
tar -tzf "${B}-private-files.tgz" >/dev/null &&
tar -tzf "${B}-files.tgz" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEV backup files: compression and JSON syntax checks passed"
```

This checks readable archive structure only, **not** restored database correctness or recovery viability. Subsequently verify DEV/PROD database boundaries and free space; require a new, complete DEV backup and explicit authorization/safe rollback plan before any database-changing integration tests. Preserve DEV persistent state and all production services; no migration, restore, deletion or production access authorized.

## Read-only DEVELOPMENT site installed-app preflight — 2026-10-13

**Operator-provided DEVELOPMENT terminal output:** At `/workspace/development/frappe-bench`, the operator ran `bench --site development.localhost list-apps`; it completed successfully and reported:

```text
frappe  16.33.1 version-16
erpnext 16.34.2 version-16
ccpcerp 0.0.1   feature/intercompany-material-billing
```

This verifies that the named DEVELOPMENT site can provide its installed-application listing, supporting (but not independently proving) site/DB availability. The `ccpcerp` branch field in `list-apps` is app/version metadata and **must not be treated as the active Git branch**; the operator separately confirmed the DEVELOPMENT Git checkout on `review/intercompany-approval-failure-tests`, commit `806fa23`, and the connected GitHub branch was independently confirmed at `806fa23516490ec7beefcff03a1baa09d722120e`.

**Still unverified:** DEV backup freshness/completeness, DEV MariaDB identity/independence, schema/indexes, controlled rollback safety and MariaDB concurrency. DEV site has persistent data; no `bench run-tests`, `bench migrate`, invoice creation, backup restore, or schema changes have been approved. PRODUCTION untouched.

**Next one-step read-only preflight:** From DEVELOPMENT container's `/workspace/development/frappe-bench`, list filenames/timestamps/sizes of DEV site backups if directory exists; do not expose site config contents or passwords:

```bash
cd /workspace/development/frappe-bench
if [ -d sites/development.localhost/private/backups ]; then
  find sites/development.localhost/private/backups -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM  %12s bytes  %f\n' | sort -r | head -n 20
else
  echo 'DEVELOPMENT site backups directory not found at standard path'
fi
```

A directory listing or backup filename alone does not prove a valid/completed/restorable backup. Evaluate freshness, backup artifact sets and separate production boundaries before seeking authorization for persistent-DEV integration tests.

## Combined 155/155 DEVELOPMENT unit tests passed — 2026-10-13

**Operator-provided DEVELOPMENT terminal transcript** (not a CI run or connector-executed command): after prior verified DEV fast-forward to app review branch `review/intercompany-approval-failure-tests`, commit `806fa23`, ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest -q \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes
```

**Observed result: `Ran 155 tests in 0.379s`; `OK`.** All four mocked modules passed *together* in one Python interpreter, providing evidence their test setup and cleanup coexist and removing the earlier need to rely solely on separate runs. GitHub connector independently verified app branch tip `806fa23516490ec7beefcff03a1baa09d722120e`. No new application code change, DB migration, Docker restart or PRODUCTION modification occurred during this milestone.

**Remaining validation:** No actual Frappe/MariaDB multi-connection concurrency, invoice rollback/durability, installed index/schema, workflow hook integration or recovery test has been performed in this testing sequence. DEV site `development.localhost` is **persistent**, and DEV/PRODUCTION share host and Docker daemon even though their Compose projects/DB volumes are distinct. Do not execute `bench --site development.localhost run-tests`, `bench migrate`, invoice creation, schema changes, or any database-changing integration test until DEV backup/isolation and rollback plan are explicitly reviewed and operator-approved; never touch production.

**Next safe one-step preflight:** from the DEVELOPMENT container at `/workspace/development/frappe-bench`, run **read-only** `bench --site development.localhost list-apps`. This checks whether the Frappe site can connect to its site database and reports installed apps/versions without exposing credentials or performing planned writes. Collect output, then separately verify DEV database identity, backup availability and isolated test strategy without exposing secrets. Current known untracked `AGENTS.md` must remain excluded.

## DEVELOPMENT index patch mocks passed — 2026-10-13

**Operator-reported DEVELOPMENT test output:** At the DEVELOPMENT bench after the previously verified safe fast-forward to review branch `review/intercompany-approval-failure-tests`, commit **`806fa23`**, the operator ran:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes \
  -q
```

Terminal result: **`Ran 8 tests in 0.004s` — `OK`**. The patch's logic was exercised with mocked database access; **no actual index creation or migration has been run or proven**. Cumulative separate test-run reports now total **155 passing mocked test executions**: 124 core billing batch, 4 approval failure paths, 19 deletion protection, and 8 index-patch tests. This does not constitute a combined suite run, a CI result, actual MariaDB transaction-rollback/concurrency proof, schema verification, or a production-ready release. App review branch `806fa23516490ec7beefcff03a1baa09d722120e` independently checked through the GitHub connector.

**Recommended next safe operator action:** Run all four mocked test modules in **one standalone `unittest` invocation** at the current DEVELOPMENT commit to verify inter-test isolation, global `frappe.db` mock cleanup and reproducibility across the exact same revision, without database-integrated testing:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest -q \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes
```

Expected count based on separate runs: 155, but **combined execution not yet verified**. If clean, plan a separate read-only DEV site/backup/schema preflight before seeking authorization for any database-integrated tests. Preserve untracked `AGENTS.md`, DEV data and PROD; no migrations, restarts or destructive operations authorized.

## DEVELOPMENT deletion-protection mocked tests passed — 2026-10-13

**Operator-provided DEVELOPMENT terminal output:** With application checkout on `review/intercompany-approval-failure-tests` at **`806fa23`**, the operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  -q
```

Result: **`Ran 19 tests in 0.008s` — `OK`**, with no errors or failures. Together with separately reported 124 passing core Intercompany Billing mocked unit tests and 4 passing invoice failure-propagation mocked tests, **147 mocked test executions passed across three separate runs**. This is not a single combined run, nor evidence of real MariaDB rollback/concurrency behavior. The application review branch tip **`806fa23516490ec7beefcff03a1baa09d722120e`** was independently reverified via connected GitHub tools.

**Next safe action:** Run the existing index patch **mocked** unit tests from the DEVELOPMENT bench, without executing the actual patch or `bench migrate`:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes -q
```

The index mock suite in GitHub initializes/restores a mocked `frappe.db`; no further code change is planned unless tests fail. Keep untracked `AGENTS.md` excluded. Any future actual database tests, migrations, concurrent approval simulations or production release require separate safety review and authorization. **No PRODUCTION changes.**

## DEVELOPMENT mocked billing suite passed — 2026-10-13

**Operator-reported DEVELOPMENT test transcript:** After fast-forwarding `review/intercompany-approval-failure-tests` to **`f49e2e8`**, the operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  -q
```

Result **`Ran 124 tests in 0.345s` — `OK`** (no reported errors/failures). Previously the four mocked invoice failure-propagation tests on the same review line passed **`Ran 4 tests in 0.011s` — `OK`**. These are **128 passing mocked test executions across two independent commands**, not a combined all-suites run, real DB proof, or CI. The previous 45 LocalProxy test-harness errors were eliminated by the `f49e2e8` mocked-`frappe.db` setup.

**Proactive GitHub-only test-harness follow-up:** Source inspection found `ccpcerp/ccpc_erp/test_transaction_deletion_protection.py` uses the same `patch(...frappe.db.sql/get_value)` pattern without a bound database in standalone `unittest`. It was corrected to temporarily replace `frappe.__dict__["db"]` with `MagicMock()` and restore it via cleanup; no runtime code was modified. GitHub connector verified updated app review branch at **`806fa23516490ec7beefcff03a1baa09d722120e`**, one commit / one test file ahead of `f49e2e8`. This follow-up was **not yet pulled into DEVELOPMENT nor executed**, and the index-patch mock tests also remain unrun in the current work session.

**Next safe step:** With DEVELOPMENT still expected on `review/intercompany-approval-failure-tests` at `f49e2e8`, verify local branch and absence of modified *tracked* files, then `git pull --ff-only origin review/intercompany-approval-failure-tests` (preserve untracked `AGENTS.md`). Verify `806fa23`; then run the isolated mocked **Transaction Deletion Record protection** and **index patch** tests, recording actual outputs. Do not run `bench migrate`, Frappe integrated test runner, financial invoices or database concurrency experiments until separate DEV safety/backup approval. PRODUCTION untouched.

## DEVELOPMENT billing mock-suite failure and GitHub test-harness correction — 2026-10-13

**Operator-provided test output:** On DEVELOPMENT at `/workspace/development/frappe-bench` on review branch `review/intercompany-approval-failure-tests` (at the previously verified local commit `12e24c9`), ran:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  -q
```

The uploaded terminal output reported **`Ran 124 tests in 0.344s`, `FAILED (errors=45)`**. Representative/all visible failures were during `unittest.mock.patch` of `frappe.db.sql` or `frappe.db.get_value`, terminating at Frappe's `local.py` with **`RuntimeError: object is not bound`**. This is a **standalone unittest database LocalProxy/mock setup problem**, not a verified billing transaction failure. Tests encountering setup errors **did not validate their asserted billing behavior**.

**GitHub-first correction committed and verified:** App review branch [`review/intercompany-approval-failure-tests`](https://github.com/ccpcerp/ccpcerp/tree/review/intercompany-approval-failure-tests) advanced to **`f49e2e869e6f1c6c64da7f662042b6e0fee80aee`**. Exactly **one file** changed compared with `12e24c9`: `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py`. `TestIntercompanyMaterialBillingBatch.setUp` now temporarily substitutes `frappe.__dict__["db"]` with `MagicMock()` and registers cleanup to restore the original proxy. This mirrors the existing isolated index-patch test setup. **No application runtime code modified.**

**Verification status:** Commit and changed-file list independently verified on GitHub. **The revised 124-test suite has NOT yet been re-run on DEVELOPMENT**, so do not say it passes or assign release readiness based on this change. No CI test result, DB transaction, migration, PROD change, or branch merge.

**One next safe step:** In the DEVELOPMENT app directory, make sure the local branch remains `review/intercompany-approval-failure-tests` and tracked changes are clean; then fast-forward pull from the **same tracked remote branch** (no force, no switch, no destructive cleanup), retaining untracked `AGENTS.md`. Re-run the same `python -m unittest ...test_intercompany_material_billing_batch -q` and report the result. If new failures arise, resolve them in GitHub first. Actual MariaDB rollback and concurrency tests remain separate pending release gates.

## DEVELOPMENT mock unit-test milestone — 2026-10-13

**Operator-reported successful test execution (terminal transcript supplied in chat).** The user had entered the DEVELOPMENT Docker container and confirmed Git branch `review/intercompany-approval-failure-tests` tracking `origin/review/intercompany-approval-failure-tests`, at commit `12e24c9`, with only `?? AGENTS.md` untracked. The branch tip was independently reverified via GitHub connector as **`12e24c99daf020ba488940411379a6c517aa1c20`**.

The operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  -v
```

Captured transcript shows **4 tests passed**, `Ran 4 tests in 0.011s`, `OK`. All four mocked invoice failure-propagation paths passed: Sales Invoice insert exception, Purchase Invoice insert exception, SI cross-link save exception and final batch save exception. This is **operator-provided terminal evidence, not a remotely executed test via GitHub connector**.

**Strict scope:** This validates isolated Python mock interactions only. It **does not prove** MariaDB rollback, persisted invoice atomicity, two-connection concurrency correctness, hook behavior in a live Frappe request, or migrations. No database-integrated tests, `bench migrate`, application merges, or PRODUCTION modifications were authorized/performed in this step. The existing `AGENTS.md` stays untracked/excluded.

**Next safe action:** Run the **existing mocked billing batch Python unit-test module** on the same verified DEV branch using `./env/bin/python -m unittest ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch -q`. Inspect the result before expanding to the deletion-protection and patch unit tests. Only after a complete mock-suite baseline should a separate, explicitly reviewed DEVELOPMENT database-integration/backup/isolation procedure be considered.

## Prior development milestone — failure-path tests prepared (2026-10-12)

**GitHub code change complete, execution pending.** ChatGPT created application branch [`review/intercompany-approval-failure-tests`](https://github.com/ccpcerp/ccpcerp/tree/review/intercompany-approval-failure-tests) from preserved DEV checkpoint `f665cf3`. The GitHub connector verified tip **`12e24c99daf020ba488940411379a6c517aa1c20`** (2 commits ahead, zero behind checkpoint), adding **only one new Python test file**: [`test_intercompany_billing_approval_failures.py`](https://github.com/ccpcerp/ccpcerp/blob/review/intercompany-approval-failure-tests/ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_billing_approval_failures.py). No existing application code was altered; no pull/merge/migration/service/PRODUCTION action occurred.

**Four *mocked* failure-propagation test methods prepared** for: Sales Invoice insert failure; Purchase Invoice insert failure after Sales Invoice insert; Sales Invoice cross-link save failure after both inserts; and final billing batch save failure after both invoice inserts. These check exceptions propagate and later actions are skipped when appropriate. **No execution/lint/CI result has yet been verified** for these new tests. In-memory fields changed before final save do **not** establish database durability or rollback. These tests are not an alternative to real Frappe/MariaDB transactional tests.

**First next safe action:** request an operator **read-only DEVELOPMENT Git status/HEAD** before any pull or branch switch:

```bash
git -C /workspace/development/frappe-bench/apps/ccpcerp status --short --branch
git -C /workspace/development/frappe-bench/apps/ccpcerp rev-parse --short HEAD
```

Expect old review checkpoint `f665cf3` and untracked `AGENTS.md` based on earlier operator evidence, **but do not assume it without new output**. Do not overwrite local files or automatically stage `AGENTS.md`. If safe, separately plan bringing the new **GitHub test branch** into DEVELOPMENT with a verified procedure, then execute its test module only with operator approval and awareness Frappe's test runner may mutate the persistent DEV database. Backups/fixture isolation required for database mutation. Prioritize safe read-only assessment of MariaDB version/isolation, real two-connection locking tests, failure rollback, and non-unique-index review. No `bench migrate` without explicit review/authorization.

## Current decisions (standing)

- **GitHub-first:** implement specifically authorized CCPC custom-app changes in GitHub on reviewed feature/review branches, then DEVELOPMENT pulls reviewed commits for testing; push any DEV fixes back to GitHub. **Always verify the resulting GitHub commits** and maintain this handoff after milestones.
- **No automatic Codex reports to GitHub.** The user cancelled this effort; they may paste Codex reports manually. No recurring publisher, new paid OpenAI API integration or autonomous GitHub-reporting task.
- ChatGPT may inspect and update GitHub during **active conversations**; there is **no unattended or automatic handoff update** while no conversation is active. The user cannot know exactly when a thread will reach its limit, so update this handoff **proactively** at milestone boundaries rather than waiting for an explicit thread-transfer request.
- **PRODUCTION is off limits** without separate, explicit approval and backup/recovery/rollback review. DEVELOPMENT and PRODUCTION are separate Compose projects on the same host; database/data and credentials are not equivalent to GitHub code.

## Repositories and latest verified code

| Repository / role | Verified reference | Status |
| --- | --- | --- |
| [CCPC custom app](https://github.com/ccpcerp/ccpcerp) | `review/intercompany-dev-checkpoint-2026-10-12` → [`f665cf3805ba799e5182600286f40e027e3c3120`](https://github.com/ccpcerp/ccpcerp/commit/f665cf3805ba799e5182600286f40e027e3c3120) | **Eight DEV-only files safely committed and pushed, verified via GitHub** |
| Original billing feature branch | `feature/intercompany-material-billing` → `7ac238ee25101207216e601532d545297989b4ee` (last verified) | Earlier committed billing code; **review checkpoint not merged into it** |
| Application default branch | `version-16` → `cfcc193` (last verified) | Older, **does not contain billing/Withdrawal Slip feature** |
| [Deployment and project docs](https://github.com/ccpcerp/ccpc-frappe-deployment) | `docs/ccpc-checkpoint-2026-10-10`, draft [PR #24](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/24) | GitHub-first workflow and this handoff live in a **draft documentation branch; not merged to main** |

**Do not assume these SHAs remain current forever.** Reverify the branch tips when resuming.

### Recovered DEVELOPMENT checkpoint

Operator terminal verified the DEVELOPMENT application folder:

`/workspace/development/frappe-bench/apps/ccpcerp`

The operator staged exactly these eight files (four modified and four added), committed them as `f665cf3`, then pushed to `origin/review/intercompany-dev-checkpoint-2026-10-12`. The GitHub connector independently verified the remote branch tip and eight-file commit:

1. `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py`
2. `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py`
3. `ccpcerp/ccpc_erp/transaction_deletion_protection.py`
4. `ccpcerp/ccpc_erp/test_transaction_deletion_protection.py`
5. `ccpcerp/hooks.py`
6. `ccpcerp/patches.txt`
7. `ccpcerp/patches/v1_0/add_intercompany_material_billing_indexes.py`
8. `ccpcerp/patches/v1_0/test_add_intercompany_material_billing_indexes.py`

`AGENTS.md` was **untracked and deliberately excluded**; it still requires separate content review before any inclusion in GitHub. Do not treat it as operational instructions, automatically stage it, delete it, or run unreviewed agent directions.

At last operator check, DEVELOPMENT was on the local checkpoint branch. The exact **post-push working tree/status has not been rechecked**; do not assume it is completely clean. Never reset, clean, branch-switch or pull over pending work without checking.

A local Windows VS Code clone at `E:\CCPC Files 2025\Plant Wide\ERPnext\ccpcerp` was clean at `version-16`/`cfcc193` and remains optional. The user was told **not to delete it**; it is not required for ChatGPT GitHub inspection.

## Preliminary static code review of `f665cf3`

**Completed:** Verified eight files on GitHub and reviewed their source. Code includes Company and billing-batch `FOR UPDATE` locking, reload/stale-state checks, source-claim locking, guarded Finance approval transitioning to draft Sales/Purchase Invoices, approval/refresh immutability, Transaction Deletion Record protection, and two **non-unique** database indexes registered as a Frappe patch.

**Not completed or not proven:** No newly verified CI/test run, no MariaDB two-connection concurrency experiment, no live Frappe document integration test, no demonstrated atomic rollback if the second invoice insert fails, no migration execution, and no production release validation. Non-unique indexes do **not** guarantee uniqueness; actual isolation and lock ordering must be verified. The checkpoint is **work in progress**, not production-ready.

## Production-readiness assessment — 2026-10-12

**Scope:** Withdrawal Slip → Stock Entry / Material Issue → monthly Intercompany Material Billing only, **not** the entire ERPNext production instance. This is a **GitHub static-review assessment**, not a live DEVELOPMENT integration result. No deployment approval.

**Evidence checked with connected GitHub tools:** app review branch tip remains `f665cf3805ba799e5182600286f40e027e3c3120`, original feature branch tip remains `7ac238ee25101207216e601532d545297989b4ee`. Compare is one commit / eight files ahead; the original feature branch has **not** absorbed the checkpoint. Only a separate older Withdrawal Slip draft app PR #6 appeared in the inspected PR list; no reviewed billing release PR was verified. The billing batch Python test module contains **124 `test_...` methods**, mostly mocked. GitHub Actions query for PR runs associated with `f665cf3` returned **zero runs** (this does not prove no other CI ever ran). No newly verified fresh live DEV tests.

**Implementation appears substantially present:** Withdrawal Slip/Material Issue path, frozen source billing snapshots, Finance-approved paired draft SI/PI, locking and stale-state guards, audit-field immutability, source claim checks, deletion safeguards, and the two index patch definitions.

**Hard release gates still open:**

1. **Test current checkpoint in DEVELOPMENT**, collecting actual repeatable results rather than relying on the 124 test declarations or historical claimed pass counts; include Frappe v16 `extend_doctype_class` hook behavior and permissions.
2. **Two-connection concurrency verification on an approved safe DEVELOPMENT setup:** simultaneous batch creation/claims, preview/finalize/approve races; prove exactly one pair of invoices and clear retry behavior; inspect MariaDB transaction isolation and actual lock behavior. Code's `FOR UPDATE` and Company serialization is a mitigation, **not yet a demonstrated guarantee**.
3. **Failure atomicity/idempotency:** inject a failure after creation of the first draft invoice, prove transaction rollback leaves no orphan invoice and no incorrect Approved batch; test repeated approval calls, deletion/Transaction Deletion Record bypass attempts and accounting/stock consistency.
4. **Database/patch review:** `idx_icmb_scope` and `idx_icmbi_source_parent` are **NON-UNIQUE** and not proven applied. Review DDL and performance/lock effects separately, back up persistent DEV state where appropriate, seek explicit authorization before `bench migrate` or other DDL, test idempotence and clean failure handling.
5. **Review and release preparation:** ensure code review/CI coverage, resolve defects via GitHub-first branches, merge approved code, verify PRODUCTION's exact baseline, backups, restoration/rollback plan, migration scope and business acceptance. Production remains untouched until distinct explicit approval.

**How far:** Implementation is significantly advanced, but production readiness **cannot be assigned a credible percentage or go-live date** until real DEV DB integration tests pass. More verification work than feature scaffolding appears to remain. Treat it as **release blocked, not production-ready**, with at least these five groups of gates. Next practical milestone is a **safe DEVELOPMENT validation plan** that can first run non-mutating tests / review setup, then explicitly approves any fixture creation, DB changes, concurrency experiments and cleanup. No production testing.

## Immediate next priority

**Withdrawal Slip → Material Issue → Intercompany Billing**. Proceed from GitHub review checkpoint `f665cf3` and validate in DEVELOPMENT safely.

1. Inspect existing tests and identify highest-risk concurrency, idempotency, invoice failure rollback, audit-trail and transaction deletion paths. Document any code issues or missing tests **in GitHub**, using a reviewed branch for fixes.
2. Propose a controlled DEVELOPMENT-only validation plan, with transaction isolation and two simultaneous approval requests. **Do not invent results, execute financial transactions against production, or assume mock tests prove real MariaDB concurrency.**
3. Evaluate the new index patch separately before any DEV migration/DDL. Preserve DEV database/configuration and prepare appropriate backup/recovery steps if testing may modify persistent state.
4. After verified tests, push any corrections to GitHub, identify branch/commit, and update **this file** with outcomes, blockers and exact next safe step.

## Operating boundaries and handoff maintenance

- Read current app code and project documents using the connected GitHub tools before making code or workflow claims. Verify relevant branches, especially since the default app branch lacks recent work.
- Keep a clear distinction between **pushed code**, **uncommitted DEV changes**, **mocked tests**, **actual database tests**, **pending changes**, and **approved versus unapproved actions**.
- Protect SSH keys, tokens, business data and operational secrets. Existing DEV container historically exposed mounted SSH materials; **do not run uncontrolled agentic Codex inside it**.
- After **each meaningful code or test milestone**, before a high-risk context switch, and periodically in a long thread, update this *single current GitHub handoff* (and affected design/runbooks where needed); include UTC/date, verified refs, what changed, what was tested, outstanding risks, and the **one next safe step**. Do not churn files if nothing materially changed.
- When a chat reaches a length limit or an unexpected interruption, the **last successfully committed GitHub handoff** is the recovery checkpoint. No claim that ChatGPT can predict an exact thread limit or publish while a thread is inactive.

## Next-conversation starter

> Continue CCPC ERPNext **GitHub-first**. Use the connected GitHub tools to read `docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md` and `docs/ccpc-project/CURRENT-HANDOFF.md` on the deployment documentation branch (or their newest authoritative locations). Verify the live app review branch/commit before continuing. Do not use old ChatGPT Project Source handoffs as current state. No automatic Codex GitHub reporting, no additional API billing, no production operations. Proceed with the handoff's next safe development step.
