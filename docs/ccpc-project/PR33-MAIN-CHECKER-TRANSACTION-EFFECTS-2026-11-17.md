# CCPC ERPNext — PR #33 MAIN DEVELOPMENT Finance Checker transaction-effects review

## November 17, 2026 — V2 single-run MAIN rollback rehearsal EXPLICITLY APPROVED; execution PENDING

The project owner responded **APPROVED** to the separately requested V2 test: one **MAIN `development.localhost` DEVELOPMENT** rehearsal calling the real Finance Checker `approve_and_create_invoices()` controller in an outer SQL transaction and rolling it back, using existing synthetic users. This permission is **not** a permanent invoice approval, real-user permissions change, production deployment or a repeat of consumed V1. Original V1 marker stays intact.

Use only the new `scripts/development/operator/ccpc_pr33_main_checker_rollback_v2_review_20261117.sh` Git blob `b95a07bc15c9a70539864f5b36ab9ab034444093`, exact application commit `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, V2-specific operator gate and one-shot marker. Before a single invocation, verify GitHub docs commit and blob on the host, run `bash -n` and `ast.parse` of embedded Python without executing it. Test fails closed on unusual realtime events, mail/queues/requests/SMTP, and verifies post-rollback persisted batch/related invoices plus SI/PI/GL/SLE counts if baseline was captured. Any blocked API or postcheck mismatch means STOP, **no replay**. No host rehearsal has yet been reported; do not describe this as a successful financial integration test.

## November 17, 2026 — confirmed installed Frappe native notification path; safer V2 plan staged

Owner returned a read-only installed DEV `frappe/model/document.py` AST check:

```text
POST_SAVE_CALLS_NOTIFY= True
NOTIFY_CALLS_REALTIME= True
REALTIME_AFTER_COMMIT= True
FRAPPE_SOURCE_CHECK=COMPLETE
```

This independently confirms the **installed** `Document.run_post_save_methods() → notify_update() → publish_realtime(..., after_commit=True)` source path (upstream version-16 review further shows event names `doc_update`/`list_update`). A regular document-save notification can therefore naturally trigger the original rehearsal's generic realtime-blocking guard. The original log did not capture a per-API stack or source, so this remains a strong likely cause, **not definitive runtime attribution**. The separate post-failure MAIN DB integrity check already PASS and stays accepted.

**V2 GitHub-only preparation:** `scripts/development/operator/ccpc_pr33_main_checker_rollback_v2_review_20261117.sh` committed to docs PR37, a **distinct** proposed one-time rehearsal, pinned to app PR33 exact SHA and exact billing controller/authority blobs. It checks installed Frappe source, suppresses only `after_commit=True` `doc_update`/`list_update` UI notification events (no messages sent, counted), rejects non-allowlisted/nondeferred realtime events, and assigns distinctive guard codes to `frappe.enqueue`, `frappe.sendmail`, background-job enqueue, requests, SMTP/SSL. The original source/actor/Company/one-batch, role/DocPerm, SQL rollback, no-commit, invoice pair/ledger invariants remain. A newly added separate read-only post-rollback check compares baseline SI/PI/GL/SLE counts and the batch state/linked invoices **even if** the controller previously hit a guard or validation error, provided the baseline had been captured.

**NOT EXECUTED.** Existing V1 one-shot marker must remain. The prior authorization was consumed and **does not authorize** a V2 transient database write. A fresh explicit owner-approved scope, script static `bash -n`/`ast.parse` validation, and read-only identity/recovery guard must precede any one-time run. Outbound monkeypatches are not a true process/network sandbox of all possible third-party hooks; use disposable isolated test if untrusted hooks or network risk remains. No persistent invoices, GL/SLE posting, user grants, scheduler/service changes or production effects have been created in this preparation.

## November 17, 2026 — source-based likely cause of generic outbound guard error

Independent read-only inspection of official `frappe/frappe` `version-16` `frappe/model/document.py` (blob `4e7ead9ef1c09c0a4fb7dc37d9198a9b2f87531b`) shows `Document.run_post_save_methods()` normally calls `self.notify_update()` after a document INSERT/UPDATE and `notify_update()` calls `frappe.publish_realtime("doc_update", ..., after_commit=True)` and often `"list_update"`. The one-shot harness blocks `frappe.publish_realtime` with the same `FORBIDDEN_OUTBOUND_SIDE_EFFECT` error as its email, queue, HTTP and SMTP blockers. This is a **plausible explanation** of the failure at `CONTROLLER_APPROVE_AND_CREATE` and may reflect a **normal Frappe save notification**, not application financial logic error. Exact DEV version/call path was not independently inspected. No conclusion about actual external delivery follows.

A new **separately approved** rehearsal, if needed, should identify each guard by precise name, selectively suppress only verified `after_commit=True` `doc_update`/`list_update` notifications, block all other outbound side-effect attempts, and perform the persisted-state read-only postcheck whether the in-transaction assertions passed or an exception occurred. Original one-use marker and script are consumed: **do not rerun**. A disposable isolated site is preferable if network/hooks cannot be comprehensively constrained.

## November 17, 2026 — owner-confirmed post-abort MAIN database check PASS

Owner completed a *separate read-only transaction*, following the abort of the single approved one-shot rehearsal:

```text
MAIN_BATCH_COUNT= 1
MAIN_BATCH_UNDER_REVIEW= True
MAIN_RELATED_SALES_INVOICES= 0
MAIN_RELATED_PURCHASE_INVOICES= 0
POST_FAILURE_DB_CHECK= PASS
```

This confirms exactly one original CCPC→Ricor billing batch still `Under Review` (`docstatus=0`, no approval fields or invoice references, as required by the invoked check), and zero related Sales/Purchase Invoices with the **exact controller-generated** `remarks` marker. The test read only MAIN `development.localhost` and rolled back its read-only transaction. This **does not upgrade** the stopped checker rehearsal to PASS or demonstrate controller-generated Draft SI/PI persistence, unchanged GL/SLE row counts, absent arbitrary unrelated records, or no external hooks. No recovery restore, user permission modification or scheduler change was necessary. Keep the original one-shot marker and do not rerun it.

Before authorizing any fresh write-capable trial, identify the guarded outbound API through source inspection or separately approved instrumented isolated test, with per-API labels and a complete post-rollback check regardless of success/error.

## November 17, 2026 — executed rehearsal STOPPED safely at outbound guard, no invoice-pair acceptance

**Owner-run output** from the original one-shot script `scripts/development/operator/ccpc_pr33_main_checker_rollback_once_20261117.sh`:

```text
PINNED_DEV_APP_AND_WORKTREE=PASS
DB_COMMIT_AND_SQL_CONTROL_GUARDS=PASS
OUTBOUND_COMMON_API_GUARDS_ACTIVE=PASS
UNDER_REVIEW_SOURCE_AND_ACTORS=PASS
REHEARSAL_DB_TRANSACTION=ROLLED_BACK
REHEARSAL_FAILURE_PHASE=CONTROLLER_APPROVE_AND_CREATE
REHEARSAL_FAILURE_CLASS=RuntimeError
REHEARSAL_FAILURE_LABEL=FORBIDDEN_OUTBOUND_SIDE_EFFECT
PRODUCTION_NOT_TARGETED=PASS
REHEARSAL_RESULT=STOPPED_AND_ROLLED_BACK
DO_NOT_AUTOMATICALLY_RETRY=PASS
```

This is a **deliberate test guard exception** from one of six common outbound hook paths patched with a shared `FORBIDDEN_OUTBOUND_SIDE_EFFECT` error, not proof of which exact API was called and **not** evidence that the billing controller itself is wrong. The script reported successful outer SQL rollback; the positive pair/GL/SLE assertions **never ran to completion** and the separate post-rollback read-only verification block was skipped because it runs only after completed in-transaction assertions. **No Draft SI/PI success is claimed.** No persistent approval is authorized. One-shot host marker must remain; do not rerun with guard removed or mutate source.

Next **nonmutating** action: use a separate MAIN read-only transaction to verify the one CCPC→Ricor batch still `Under Review`, no approvals or linked SI/PI, and zero invoice rows with that batch's generated remarks; do not claim whole-schema no-change without initial committed count baselines. Then examine Frappe/ERPNext native insert hooks and distinguish harmless transient UI realtime events from external queues/mail/HTTP before proposing a safer isolated rerun under a **new** owner scope/approval.

## November 17, 2026 — one rollback-only rehearsal APPROVED, script PREPARED (NOT RUN)

The owner specifically approved a **single rollback-only MAIN DEVELOPMENT Checker rehearsal** of the existing CCPC→Ricor `Under Review` batch after reviewing expected changes. This is a **temporary SQL write** test with unconditional rollback; **not** permission to persist a Draft invoice pair or approve the batch, assign real-user roles, migrate, start services/scheduler, run PRODUCTION, or submit invoices.

A *new* one-time operator script was committed in docs PR #37 at `scripts/development/operator/ccpc_pr33_main_checker_rollback_once_20261117.sh`. It uses the exact `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` app SHA, verified billing controller/authority Git blobs, detached/clean DEV worktree with only protected `AGENTS.md`, original host/user/Compose identity, the historical (not fresh) protected MAIN NAS recovery set, and a private one-use host marker. It is not one of the consumed obsolete Nov 4 scripts.

The Python portion runs from DEV bench `sites`, connects **only** to `development.localhost`, begins an ordinary transaction, disallows `frappe.db.commit()` and raw SQL COMMIT/DDL/session transaction-control, blocks common outbound side-effect APIs (Frappe queue/email/realtime, requests, SMTP), and verifies synthetic actors, grants, one finalized source line, native `approve_and_create_invoices()` behavior, reciprocal `docstatus=0` SI/PI, Company/date/amount/party/source, `+1/+1` drafts and `+0/+0` ledger/stock in-transaction. A finalizer always calls `frappe.db.rollback()`; if all checks passed it initiates a separate **read-only** transaction and verifies original batch remains `Under Review`, neither invoice persisted and row counts are unchanged. On any unexpected error, it fails closed with a phase/class label; no automatic retry. The common API guards are not a complete sandbox for arbitrary installed third-party hooks; verify no unexpected external effects before interpreting PASS as production-grade acceptance.

**Execution status: PREPARED, NOT EXECUTED.** The script must be retrieved from an exact docs PR #37 commit, Git blob independently checked, `bash -n` plus Python heredoc `ast.parse` checked, and operator-invoked once. Only **operator-provided** output containing `REHEARSAL_RESULT=PASS_ALL_CHECKS_ROLLED_BACK`, `POST_ROLLBACK_BATCH_AND_COUNTS=PASS`, `NO_INVOICE_COMMIT_REQUESTED=PASS` plus no `STOP` establishes this bounded rehearsal PASS. There remains no persistent invoice-pair acceptance, real user permission certification, concurrent checker race, actual posting/GL/SLE reconciliation, or PROD readiness.

**Date:** 2026-11-17 Asia/Manila. **Status:** Source review and proposed next gate only. **No new Frappe transaction executed.** Owner approved review/preparation of the remaining PR33 financial integration work following previously completed executive reporting acceptance. This is **not** standing approval to create invoices, mutate Company/user permissions, submit invoices, restart workers or deploy to PRODUCTION.

## GitHub authority, DEVELOPMENT baseline, and evidence level

- App draft PR [#33](https://github.com/ccpcerp/ccpcerp/pull/33) head `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` on `review/billing-authorization-correction-2026-11-03`, independently re-fetched November 17. MAIN/Integration2-shared DEV source-only checkout at this SHA passed operator checks (`DEV_SOURCE_UPDATE=PASS`); only later changes since `1bde04bf...` are the executive gateway and its Frappe tests. No financial controller code changes in these last four commits.
- Code reviewed at the exact app head:
  - `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` (Git blob `a9a6e609759e77948d40d31bdbd342f727b208a9`).
  - `ccpcerp/ccpc_erp/intercompany_billing_authority.py` (blob `8de2d6ba2aa0f8995b727157491e236d2a0a8ae2`).
  - Batch schema `.../intercompany_material_billing_batch.json` (blob `461671fd6e33a8074ef2a80fe77bff94231cc03c`).
- Owner's Nov 17 consolidated read-only MAIN inventory previously reported exactly **one CCPC → Ricor batch Under Review**, zero SI/PI links and zero paired invoices; two enabled System Users counted for each Billing Preparer/Finance Controller role, and synthetic maker/checker role+Company grants separately checked. These are **historical observed counts**, not current-state authorization to commit. No new MAIN invoice-pair acceptance since this observation is claimed.
- DEVELOPMENT web/socketio healthy after a duplicate accidental `bench start`: one Honcho manager, port 9000 listening, `development.localhost` loopback HTTP 200, zero scheduler candidates observed. Honcho was explicitly launched with only `web socketio`; unrestricted `bench start` risks triggering known broken third-site scheduler enumeration. No restart needed for this review.
- Original Nov 4 *one-shot* checker commit and rollback diagnostic scripts are pinned to **obsolete** app SHA `9f174bb9...` and were previously consumed; **do not rerun or merely remove their hash guards**. No actual current-head checker action is authorized here.

## Precisely what a successful checker approval would write

The checked-in controller method is `IntercompanyMaterialBillingBatch.approve_and_create_invoices()` (approx. lines 1483–1584). If all guards pass, one transaction:

1. Locks issuing Company and batch row, reloads persisted state, validates a **different, enabled named Finance Controller** from persisted `finalized_by`, with exact Company User Permissions for *both* issuing/requesting Companies. `Administrator`, `Guest`, and `Stockroom Personnel` are rejected; actual DocPerm `write` is checked. The role check uses real `Has Role` membership, not just UI button visibility.
2. Requires batch `status=Under Review`, `docstatus=0`, both SI/PI links absent, finalization after period end with its author/time set, nonempty frozen source items, submitted matching Material Issue/Withdrawal Slip snapshot, and unclaimed source detail. No maker refresh/finalization rerun is required for an already finalized batch.
3. Validates one enabled internal **Customer representing Ricor** and one enabled internal **Supplier representing CCPC**, both Company's default currency equal, valid default non-group Cost Centers, and Company-owned ledger Accounts (`1312` intercompany receivable, `2121` intercompany payable, `5150` intercompany materials expense, `6050` intercompany material charges; resolved with actual Company abbreviations). No FX conversion is invented.
4. Creates one **Draft Sales Invoice** for the issuing Company, CCPC, and one **Draft Purchase Invoice** for the requesting Company, Ricor, using frozen item quantity/rate and billing period-end posting date (`set_posting_time=1`), without automatic taxes or stock updates (`update_stock=0`). Inserts use `ignore_permissions=True` *inside the already checked server-side role/Company guard*—a significant reason to protect the method and actor boundary.
5. Writes reciprocal `inter_company_invoice_reference` fields and validates **both persisted links**, Draft `docstatus=0`, no new taxes, posting dates equal batch period end and grand totals within PHP/amount tolerance 0.01 of batch total. Changes the batch **Under Review → Approved**, populating `approved_by`, `approved_on`, `sales_invoice` and `purchase_invoice`, retaining `finalized_by` and frozen source items.
6. On an exception, rolls back to a unique SQL savepoint, clears the in-memory approval fields and re-raises. The command does **not** call `submit()`, does not explicitly create Stock Entry/SLE/GL, and does **not** request native SI/PI posting. The controller is not an invoice-posting or accounting-completion certification. A successful HTTP method call, or an operator script explicitly calling `frappe.db.commit()`, **would persist** the two drafts and batch approval.
7. Expected in-transaction row deltas, to be actually **measured** at any approved rehearsal: Sales Invoice `+1`, Purchase Invoice `+1`, GL Entry `+0`, Stock Ledger Entry `+0`, with one reciprocal Draft pair and one Approved batch. Pre-existing GL/SLE balances and references are not to be inferred or modified.

**Failure/side-effect caveat:** SQL savepoint/outer rollback protects transactional MariaDB rows under normal isolation; cannot prove that every native ERPNext hook avoids emails, queues, external integrations, filesystem writes or implicit commits. Future rehearsal must explicitly review/block commits and outbound side effects and verify post-rollback counts. Do not promise persistent zero impact simply because a Python `finally` calls rollback.

## Mandatory checks before any new write-capable experiment

- **Source/site/worktree:** exact app SHA above, `HEAD` detached, tracked tree untouched, sole protected untracked `AGENTS.md`, named DEV container/Compose project, named MAIN `development.localhost`, no broken third-site DB connection, no PROD access.
- **Recovery:** historical NAS manifests were present and previously independently checksummed; **fresh recovery currency and restore have not been proven**. An irreversible committed billing operation needs a suitably fresh, isolated and recoverable MAIN snapshot plus verified non-destructive rollback/recovery plan. Avoid using old backup manifests as substitute.
- **Current batch data:** exactly one CCPC/Ricor `Under Review` candidate, no invoice refs or approvals, one frozen source line only if previously observed invariant still holds, correct Company/month, finalized_by the intended separate maker, no duplicate active source claims, no existing committed draft pairs/correction case, dates and totals consistent.
- **Actors:** existing *synthetic DEV* checker is **not** a real nominated accountant. Even if it carries `Finance Controller` plus `CCPC DEV Billing Master Reader` and both Company grants, a committed invoice approval attributed to this synthetic user is a separate explicit business/audit decision; do not silently assign it or new privileges to real users. Verify actual effective DocPerm/master reads without role escalation.
- **External hooks:** test for possible transactional email/notification/queue/integration effects and immutable audit fields. Check approval guarded against replays, concurrent two-checker attempts, failure between draft inserts, and nonunique correction review (the correction DocType lacks an identified DB unique batch index).

## Fastest safe next acceptance choice (requires distinct approval)

**Recommended first:** A *new* exact-SHA-pinned, one-time, guarded **rollback-only MAIN DEVELOPMENT checker rehearsal** using the existing synthetic maker/checker identities, invoking the **real controller**, verifying both Draft invoices, amount/currency, reciprocal links, approved batch and GL/SLE count invariants, blocking explicit DB commits, then rolling back and re-reading the batch/row counts in a fresh transaction. It involves **transient SQL writes** and possible native hook side effects, so this is NOT approved by the present source-review authorization. If the hook and rollback boundary cannot be established, prefer a disposable isolated Frappe/MariaDB CI fixture rather than live MAIN.

After a successful rehearsal and fresh recovery checks, request a **separate explicit single committed approval** identifying the site, batch, checker account, exact expected two Draft invoices and recovery point. Do not reuse the old `20261104` scripts or run them with disabled guards; do not auto-retry on a partial failure. If nominated actual Finance users/rights are not ready, treat synthetic *committed* invoice tests as audit policy-sensitive and require a separate decision. Subsequently verify invoice posting/cancellation, Company GL and stock/SLE reconciliations, concurrency and reports under separately approved gates.

**Not authorized:** `bench start`, `bench migrate`, scheduler, raw SQL account/User Permission writes, real-user role grants, invoice `submit()`/cancellation, PRODUCTION, PR merge, paid CI run, automatic Codex or background work.
