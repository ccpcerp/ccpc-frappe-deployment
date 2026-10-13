# CCPC ERPNext — CURRENT HANDOFF

**Last verified update:** 2026-10-13 (GitHub connector, test output attachment, and operator terminal reports).  
**Purpose:** This is the **single rolling GitHub handoff** for CCPC ERPNext. Maintain **this same path** at meaningful milestones, during longer conversations before a thread limit is reached, and when the operator requests a handoff. Do not create a new dated Project Source attachment every time.

> **Read first in every new project conversation:** [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), then this handoff, then verify relevant live GitHub branches and commits with the GitHub connection. The permanent ChatGPT Project Instructions define policy; older Project Sources and dated handoffs supply historical context only. If information conflicts, the most recently verified GitHub state takes precedence. If GitHub is inaccessible, report the inability to verify rather than treating old snapshots as current.

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
