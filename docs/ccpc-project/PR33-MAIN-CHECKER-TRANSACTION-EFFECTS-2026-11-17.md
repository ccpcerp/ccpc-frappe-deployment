# CCPC ERPNext — PR #33 MAIN DEVELOPMENT Finance Checker transaction-effects review

## November 17, 2026 — native SI/PI GL and reconciliation readiness review authorized, no posting

Owner said **"Approved, continue"** in response to the successful independent postcommit read-only Draft-pair audit. This advances the **posting-readiness analysis and planning** only. The exact currently committed Draft CCPC SI `ACC-SINV-2026-00001` and Draft Ricor PI `ACC-PINV-2026-00005` must **remain unsubmitted** until their full native ERPNext accounting effects, Company and Account/Cost Center mappings, chosen posting actor's native `submit` permission, fiscal freeze/period constraints, and recoverability are independently reviewed and an explicit write-capable test is approved.

New dedicated source review and accounting plan: `docs/ccpc-project/PR33-NATIVE-INVOICE-POSTING-READINESS-2026-11-17.md`. New prepared, **not yet host-executed**, read-only operator `scripts/development/operator/ccpc_pr33_main_draft_pair_readonly_posting_preflight_20261117.sh`, blob `d18feaba3c4dea7c7345bb703b296dcb5c6bec16`, inspects exact Draft invoice/account/Company/currency/cost center and current Finance Controller native invoice submit rights under `START TRANSACTION READ ONLY`. It never submits, saves, grants or commits. Public upstream ERPNext version-16 `SalesInvoice.on_submit` and `PurchaseInvoice.on_submit` source shows native GL creation plus potential other hooks; the derived expected per-company debits/credits are not booked journal entries. The existing backup predates these persistent Draft records: take new post-Draft local+offsite SHA256-reverified backup before any eventual persistent submission, avoiding any destructive restore of the earlier snapshot.

## November 17, 2026 — INDEPENDENT POSTCOMMIT READ-ONLY MAIN DEVELOPMENT DRAFT SI/PI ACCEPTANCE PASS

After the owner-operated one-time permanent Draft CCPC SI `ACC-SINV-2026-00001` and Ricor PI `ACC-PINV-2026-00005` creation/SQL commit PASS, the owner separately executed the **newly supplied independent read-only Frappe/MariaDB audit** from bench `sites` on `development.localhost`. Complete operator output:

```text
INDEPENDENT_APPROVED_BATCH=PASS
INDEPENDENT_DRAFT_PAIR=PASS
NO_RELATED_GL_OR_STOCK_POSTINGS=PASS
INDEPENDENT_PERSISTED_AUDIT=PASS
READ_ONLY_NO_COMMIT=PASS
```

**Scope of independently corroborated database state:** The one CCPC → Ricor batch exists as `Approved`, `docstatus=0`, `approved_by=finance_controller@ccpc.com`, with original approval timestamp, and its two invoice reference fields equal the exact SI/PI IDs. Independently fetched invoices are both **Draft** (`docstatus=0`), with correct Companies and reciprocal intercompany references, no stock update or tax rows, exactly one matching frozen original billing line (item code, quantity, rate), matching month-end posting date and amount within 0.01, exact batch-identifying remarks and **one** matching-remarks record of each invoice type. The distinct audit checked zero `GL Entry` and `Stock Ledger Entry` rows **per exact invoice voucher type/name pair**. Its transaction was `START TRANSACTION READ ONLY` and closed with rollback in `finally`; **no new writes/approval/submission**. This confirms the committed state outside the original committing process. It does not prove wider GL/SLE database-wide changes are zero or that any posted accounting reconciliation has passed.

**Accepted milestone:** Main DEVELOPMENT first persistent **Draft-only** invoice-pair acceptance **PASS, including independent postcommit read-only audit**. Application draft PR33 remains open/unmerged; not production-ready. Preserve all one-time markers, new invoices, and local/off-host SHA256 backup sets (backup restore NOT independently tested). No native invoice submission, GL/SLE posting, cancellation, repeat approval, real authenticated web Finance approval, concurrency stress, or PRODUCTION deployment authorized. The existing operator-driven `frappe.set_user()` attribution and synthetic DEV maker remain audit caveats. Next review only: plan ERPNext native SI/PI submission and ledger accounting reconciliation, separate authorization for any financial posting, plus concurrency/replay and recovery acceptance.

## November 17, 2026 — FIRST MAIN DEVELOPMENT PERSISTENT DRAFT SI/PI PAIR COMMIT + SCRIPT POSTCOMMIT CHECK PASS

After explicit owner authorization for one DEV-only persistent pair and nomination of `finance_controller@ccpc.com`, the owner executed the previously exact-source static-validated one-time script `scripts/development/operator/ccpc_pr33_main_checker_persist_draft_pair_once_20261117.sh` from docs PR37 (Git blob `b20edd9762fb3497eb5d866e51100bb337eff25b`). App PR33 pinned at `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`. The precommit off-host backup rehash, source/permissions/source-item guards, single controller/commit, exact one Draft pair, zero GL/SLE delta, and new READ ONLY persisted-state postcheck all returned PASS. Full operator stdout:

```text
FINAL_EXECUTION_SOURCE_CHECK=PASS
PINNED_FRESH_MAIN_OFF_HOST_RECOVERY_SHA256_4_OF_4=PASS
[sudo: authenticate] Password:
PINNED_DEV_APP_AND_WORKTREE=PASS
INSTALLED_FRAPPE_UI_NOTIFICATION_PREFLIGHT=PASS
SINGLE_COMMIT_AND_SQL_CONTROL_GUARDS=PASS
SELECTIVE_REALTIME_AND_OUTBOUND_API_GUARDS_ACTIVE=PASS
UNDER_REVIEW_SOURCE_AND_ACTORS=PASS
NAMED_CHECKER_NATIVE_BATCH_PERMISSIONS=PASS
CROSS_LINKED_DRAFT_SI_PI_IN_TRANSACTION=PASS
ONLY_TWO_DRAFT_INVOICES_CREATED=PASS
GL_AND_STOCK_ROW_COUNTS_UNCHANGED=PASS
DEFERRED_UI_NOTIFICATIONS_SUPPRESSED_COUNT=12
PRECOMMIT_DRAFT_PAIR_AND_ZERO_GL_SLE=PASS
SINGLE_EXPLICIT_DB_COMMIT=PASS
ACTIVE_TRANSACTION_CLEANUP=PASS
PERSISTED_DRAFT_PAIR_AND_COUNTS_POSTCHECK=PASS
PERSISTED_SALES_INVOICE_NAME=ACC-SINV-2026-00001
PERSISTED_PURCHASE_INVOICE_NAME=ACC-PINV-2026-00005
COMMIT_SQL_COMPLETED=True
COMMIT_CALL_COMPLETED=True
POSTCOMMIT_READ_ONLY_VALIDATED=True
PRODUCTION_NOT_TARGETED=PASS
PERSISTENT_DRAFT_PAIR_APPROVAL=PASS
INVOICE_SUBMISSION_NOT_REQUESTED=PASS
DO_NOT_REPEAT_THIS_ONE_SHOT=PASS
```

**State after operation (from script's fresh read-only postcommit transaction):** One **persisted** `Approved` CCPC→Ricor one-line billing batch with `approved_by=finance_controller@ccpc.com` and exact links to `ACC-SINV-2026-00001` (CCPC Sales Invoice) and `ACC-PINV-2026-00005` (Ricor Purchase Invoice), both `docstatus=0` Draft, reciprocally linked, correct expected invoice fields, no tax/stock update, and precisely one related invoice of each type with exact batch remarks. New row count delta `SI +1, PI +1, GL +0, SLE +0`. The single explicit SQL commit returned and a separate read-only transaction verified those fields. There is no rollback of this successful commit; original V2 rollback-only result remains a separate earlier test. `frappe.publish_realtime` allowlisted deferred UI events were suppressed 12 times in the operator process. No invoice `submit()` or financial ledger posting requested. The execution used operator `frappe.set_user('finance_controller@ccpc.com')` in a CLI session: it is an approved DEVELOPMENT test attribution, **not independent proof of interactive authentication by the named account holder**. Original finalized_by remains the synthetic DEV preparer.

**Mandatory preservation:** The one-shot marker `~/.ccpc-pr33-main-persist-draft-pair-once-20261117` is now **consumed — DO NOT delete/reset/re-run**. Exact local backup: `development.localhost-20261117T043152Z-1582f342f870`; exact fresh Synology SHA256-verified copy: `ccpc-development-pr33-main-precommit-20261117T044035Z-591a9f7e2b035cae`. Integrity checked 4/4, but restore rehearsal not yet validated. No backup restore, migration, service restart, user grant, production modification or PR merge.

**Next acceptance:** Independently inspect persisted MAIN batch/invoice pair with a distinct **read-only** script/connection to corroborate state outside the original committing process. Then review separate native invoice submit/GL & Stock Ledger/reconciliation, permissions, HTTP/CSRF, correction/cancellation, concurrent approvals and recovery/rollback. No separate authorization yet exists for invoice submission or GL posting; PRODUCTION remains NO-GO. PR33/PR37 both still draft.

## November 17, 2026 — one-time permanent DEV Draft-pair script static source and syntax checks PASS; not executed

Owner ran the host static-only verification of the exact committed `ccpc_pr33_main_checker_persist_draft_pair_once_20261117.sh` source (Git blob `b20edd9762fb3497eb5d866e51100bb337eff25b`) against the previously pinned docs commit `7662d6ae9ccc61c9f16728e6e3cd5ef6efb75a00`. Full operator output:

```text
PERSISTENT_SCRIPT_SOURCE_AND_SYNTAX=PASS
ONE_CONTROLLER_AND_ONE_COMMIT_CALL=PASS
FINANCIAL_OPERATION_NOT_EXECUTED=PASS
```

This establishes exact Git file and host static checks (`bash -n`, embedded `ast.parse`, single literal `batch.approve_and_create_invoices()` and single `original_commit()`) without invoking code or consuming the persistent one-shot marker. The current docs PR37 was advanced by **documentation only**; script blob and app PR33 head remain unchanged.

**Operation still pending:** The owner previously approved *one* permanent Draft CCPC SI + Ricor PI pair on MAIN DEV and explicitly nominated existing `finance_controller@ccpc.com` as the permanent `approved_by`. On the eventual one-time command, if either the explicit commit or postcommit read-only audit reports an error, do **not** rerun, restore, submit/cancel invoices, or infer SQL rollback undid an already committed pair. Inspect persisted batch/SI/PI/GL/SLE via a fresh read-only connection first. Only the known, scoped Draft creation is authorized; no direct login-authenticated Finance click is proven by `frappe.set_user()`, and no production migration/deployment is approved. Local and NAS SHA256 verified backup set remains preserved and not restore-tested.

## November 17, 2026 — owner CONFIRMED named `approved_by`; one-shot persistent MAIN DEV operator prepared in GitHub, NOT RUN

Owner explicitly **confirmed** `finance_controller@ccpc.com` as the intended `approved_by` account for one persistent **Draft** CCPC Sales Invoice + Ricor Purchase Invoice pair on `development.localhost`. This follows separate owner approval of that persistent DEVELOPMENT acceptance milestone, a successful real-controller V2 **rollback-only** test, read-only named Finance Controller role/Company grants and native batch `read`/`write` permission PASS, and fresh exact-source MAIN local + Synology NAS 4/4 SHA256 backup integrity PASS. The original batch was previously finalized by the **synthetic DEV preparer** `ccpc-billing-preparer-dev@testing.invalid`; this is a DEVELOPMENT test fixture, not a claim of real human preparer authentication.

New **PREPARED / NOT EXECUTED** operator script on docs draft PR37: `scripts/development/operator/ccpc_pr33_main_checker_persist_draft_pair_once_20261117.sh`. It pins app PR33 SHA `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, controller blob `a9a6e609759e77948d40d31bdbd342f727b208a9`, authority blob `8de2d6ba2aa0f8995b727157491e236d2a0a8ae2`, exact MAIN site/host/Compose/worktree, prior maker and named Finance Checker role + Company grants, expected one single-source `Under Review` unapproved batch and zero related invoice pair, and exclusive one-shot host marker `~/.ccpc-pr33-main-persist-draft-pair-once-20261117`. Before writing, the host rehashes both manifests of the **exact Nov17 fresh offsite** folder `ccpc-development-pr33-main-precommit-20261117T044035Z-591a9f7e2b035cae` against original `development.localhost-20261117T043152Z-1582f342f870`. The script calls the actual controller exactly once under a `frappe.set_user("finance_controller@ccpc.com")` **operator-executed Frappe CLI session**, not an actual authenticated web click by that user; preserve this limitation transparently in financial audit review. It checks exactly `+1 Draft SI/+1 Draft PI/+0 GL/+0 SLE`, date/Company/party/frozen source/totals/reciprocal links, prevents implicit native commits/DDL, suppresses only allowlisted deferred UI document-update notifications, blocks common email/job/requests/SMTP API calls, and invokes one explicit `frappe.db.commit()` implementation only after the in-transaction checks. It then verifies persisted batch `Approved` with named `approved_by`, pair and row counts in a **new read-only transaction**. Any exception/possible post-commit side effect or postcheck failure means **STOP / NO RETRY** even if SQL commit may already have happened.

**Scope and limitations:** GitHub script preparation only; **no invoice has yet been committed**. The SQL and Python hook guards are not OS-level network isolation nor comprehensive interception of custom hooks. A pre-existing snapshot/hash PASS is not a verified restore. Real-user web session authentication, HTTP CSRF, concurrency, repeated attempts, native invoice submit/cancel, actual GL/SLE posting and PRODUCTION are not tested or authorized. Do not give the operation a label stronger than bounded operator-driven persistent DEV Draft-pair acceptance. The script must be retrieved by exact docs Git commit and its Git blob, undergo `bash -n` plus embedded `ast.parse` preflight before one host invocation; any STOP is terminal for that script marker and requires read-only state review, not deletion/replay. No user roles, migration, scheduler or PRODUCTION changes.

## November 17, 2026 — existing named Finance Controller native batch DocPerm PASS; awaiting exact approved_by identity selection

Owner ran the separately bounded, no-write MAIN DEVELOPMENT actual DocType/document permission check as `finance_controller@ccpc.com`:

```text
NATIVE_BATCH_READ_PERMISSION=PASS
NATIVE_BATCH_WRITE_PERMISSION=PASS
FINANCE_CHECKER= finance_controller@ccpc.com
READ_ONLY_PERMISSION_CHECK=PASS
```

The test pinned PR33 app code `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, used correct `frappe-bench/sites` CWD, checked exactly one original CCPC→Ricor `Under Review` unapproved batch with no invoice links, called `frappe.set_user("finance_controller@ccpc.com")`, then native `batch.check_permission("read")` and `batch.check_permission("write")` inside `START TRANSACTION READ ONLY`; rollback in `finally`. This is a successful site-level effective document read/write authorization check, supplementing the earlier role/Company/maker-separation census. It does not prove the account has been personally nominated as an accountable Finance Controller for a lasting `approved_by` entry. **No accounting/invoice mutation or persistent Finance approval was executed**.

The one-time persisted Draft pair authorization is conditional: before constructing/invoking the committed controller, the owner must identify this specific real account as the intended audit actor, and the guarded one-time code must reverify recoverability, exact actor/batch/source state and once-only postcommit invariants. Historical local and Synology four-part SHA256 PASS backups remain protected, not restore-tested. No automatic use of synthetic checker, no user grants, invoice submit, GL/SLE posting, PRODUCTION or scheduler operations.

## November 17, 2026 — one eligible nonsynthetic checker from MAIN read-only role/Company census; native DocPerm pending

The corrected owner-operated MAIN `START TRANSACTION READ ONLY` census ran from bench `sites` without the previous logger/cwd error:

```text
ENABLED_FINANCE_CONTROLLERS= 2
ELIGIBLE_NAMED_CHECKER= finance_controller@ccpc.com
ELIGIBLE_NAMED_CHECKER_COUNT= 1
READ_ONLY_CHECK=COMPLETE
```

The one eligible checker `finance_controller@ccpc.com` meets the queried **persisted named role**, enabled `System User`, both issuing/requesting Company `User Permission` grants with global scope, not forbidden Stockroom role, not same as batch `finalized_by`, and non-`@testing.invalid` identity requirements. Counts: two enabled Finance Controller users, one matches all filters. This is **not** a policy nomination by the owner and **not** an actual approval. App controller additionally uses `IntercompanyMaterialBillingBatch._require_finance_approver()` → `batch.check_permission("write")` before its enforced actor/Company/maker checks. The checked-in DocType JSON grants Finance Controller native `read`/`write`, but **effective instance-level permission for this user still requires read-only validation on MAIN**. Proposed next one step: with correct bench `sites` cwd, `frappe.init(...)`, connect, `START TRANSACTION READ ONLY`, query exactly one still-Under Review CCPC→Ricor batch, `frappe.set_user("finance_controller@ccpc.com")`, `batch.check_permission("write")`, report PASS, rollback and destroy. No native controller approval call, no invoice inserts or commit, and do not change user permissions. Separately confirm this real checker is the intended permanent `approved_by` audit identity before using the earlier conditional owner approval for one persistent Draft pair. Local+Synology backup integrity gate PASS, not restore-tested. PRODUCTION excluded.

## November 17, 2026 — MAIN fresh precommit Synology NAS 4/4 SHA256 verified; identity gate outstanding

Operator executed the separately reviewed NAS-transfer `scripts/development/operator/ccpc_pr33_precommit_main_nas_copy_20261117.sh` using the exact fresh local backup `development.localhost-20261117T043152Z-1582f342f870`. Output:

```text
NAS_COPY_SCRIPT_VERIFIED=PASS
NEW_MAIN_BACKUP_AGE_WINDOW=PASS
NAS MOUNT: PASS
FRESH_MAIN_SOURCE_MANIFEST: 4/4 PASS
NEW NAS STAGING DIRECTORY: CREATED
development.localhost: 4/4 SHA256 PASS
NAS BACKUP CHECKSUMS: 4/4 PASS
FINAL NAS DIRECTORY: /mnt/erpnext_backups/ccpc-development-pr33-main-precommit-20261117T044035Z-591a9f7e2b035cae
FRESH_PRECOMMIT_MAIN_DEV_OFF_HOST_BACKUP: PASS
```

**Recovery gate:** Local four-artifact backup and matching NAS offsite copy now both checked to four SHA256 hashes under the exact required mounted Synology source, with private immutable new directories. Do not reuse the consumed NAS or local backup one-shot markers; do not remove snapshots. This is **integrity verified, NOT restore tested** or a complete online database consistency proof. No invoice approvals or Frappe changes were performed by the backup scripts. An explicit persistent-billing approval is still conditional on selecting an existing legitimate named Finance Controller and validating exact Company grants and native DocPerm, fresh batch/period/source eligibility and safe one-time commit/recovery guard; synthetic `@testing.invalid` Checker was used in rollback-only V2, not implicitly authorized as the permanent `approved_by`. Next step: read-only census and owner nomination of an eligible existing real named Finance Controller, no user rights changes.

## November 17, 2026 — new MAIN local precommit backup verified by operator; NAS protection pending

Owner successfully ran new current-head exact-source MAIN backup `scripts/development/operator/ccpc_pr33_precommit_main_backup_20261117.sh`, creating **four new local backup artifacts** (database, site config, public/private archives) and private SHA256 manifest. Original host/output:

```text
DEVELOPMENT SNAPSHOT PRECHECK: PASS
MAIN_UNDER_REVIEW_BATCH_AND_ZERO_DRAFT_PAIRS: PASS
DATABASE BACKUP: PASS
SITE CONFIG BACKUP: PASS
PUBLIC FILES BACKUP: PASS
PRIVATE FILES BACKUP: PASS
SHA256 MANIFEST: PASS
BACKUP DIRECTORY: /workspace/development/frappe-bench/.ccpc-pr32-snapshots/development.localhost-20261117T043152Z-1582f342f870
FRESH_PRECOMMIT_MAIN_DEV_BACKUP: PASS
NO_INVOICE_ACTIONS_OR_COMMIT: PASS
```

The immutable new local snapshot's basename is `development.localhost-20261117T043152Z-1582f342f870`. The exact original `Under Review` financial batch remained unapproved with no linked or same-remark invoices as tested at preflight; no invoice action or commit occurred. This is a **local backup plus integrity check**, not yet a verified off-host recovery copy or restore test. Do not reuse its one-shot marker or overwrite previous backup archives. One-time current-head NAS copy script at `scripts/development/operator/ccpc_pr33_precommit_main_nas_copy_20261117.sh`, exact Git blob `19925587a894aef10fbd4df99776b612120c907d`, must copy **this exact basename** and verify all four copied hashes on Synology before the persistent finance write gate. No persistent checker approval until both fresh off-host backup status and accountable named Checker rights are revalidated.

## November 17, 2026 — OWNER APPROVED first persistent MAIN DEV Draft SI/PI pair, contingent on verified backup and actor

Owner explicitly approved progressing beyond the successful rollback-only rehearsal to **exactly one persistent linked Draft invoice pair** (CCPC SI + Ricor PI) via the checked-in Finance Controller `approve_and_create_invoices()` method on MAIN DEVELOPMENT. This permission is **conditional**, not a request to skip previously stated requirements: fresh scoped recoverable backup, intended named Finance Controller/Company permissions, unchanged `Under Review` finalized single-line batch with no invoice links, precise one-shot transaction and post-commit audit. **No persistent controller action has executed under this approval.** Use of the existing synthetic `ccpc-billing-checker-dev@testing.invalid` for an auditable committed invoice is **not presumed approved**; explicit checker identity and native permissions must be decided without automatically assigning rights. No `submit`, `cancel`, GL posting, PRODUCTION, migration, service restart or old test marker reuse.

The existing November 4 one-time backup/copy files were reviewed but cannot be reused, since they pin outdated source/initial `Draft` status. New script paths on docs PR37 (current review branch): `scripts/development/operator/ccpc_pr33_precommit_main_backup_20261117.sh` (new exact app SHA `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`, four local artifacts and SHA256 manifest) and `scripts/development/operator/ccpc_pr33_precommit_main_nas_copy_20261117.sh` (transfer exactly that new random-name MAIN snapshot, verify four offsite checksums). Both create only uniquely named snapshots and preserve older recovery, with one-time host gate/marker, no app edits and no invoice actions. **Neither script has been operator-executed yet.** Next one step: run checked/pinned local fresh backup and share PASS + basename, followed by separate verified NAS transfer; independently verify recovery before the eventually committed one-shot operation. Normal Frappe outbound UI notifications may occur on a future real commit; suppressing `after_commit` notifications for a rollback-only test is not necessarily valid in a persistent operational approval, so review messaging side effects separately.

## November 17, 2026 — PR33 V2 MAIN live rollback-only checker acceptance PASS (one-line draft SI/PI)

The owner executed the single separately approved V2 script at docs PR37 blob `b95a07bc15c9a70539864f5b36ab9ab034444093`, against the protected DEVELOPMENT app checkout exactly pinned to PR33 head `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87`. **Actual owner-supplied terminal result**:

```text
PINNED_DEV_APP_AND_WORKTREE=PASS
INSTALLED_FRAPPE_UI_NOTIFICATION_PREFLIGHT=PASS
DB_COMMIT_AND_SQL_CONTROL_GUARDS=PASS
SELECTIVE_REALTIME_AND_OUTBOUND_API_GUARDS_ACTIVE=PASS
UNDER_REVIEW_SOURCE_AND_ACTORS=PASS
CROSS_LINKED_DRAFT_SI_PI_IN_TRANSACTION=PASS
ONLY_TWO_DRAFT_INVOICES_CREATED=PASS
GL_AND_STOCK_ROW_COUNTS_UNCHANGED=PASS
DEFERRED_UI_NOTIFICATIONS_SUPPRESSED_COUNT=12
ROLLBACK_ONLY_IN_TRANSACTION_CHECKS=PASS
REHEARSAL_DB_TRANSACTION=ROLLED_BACK
POST_ROLLBACK_BATCH_AND_COUNTS=PASS
PRODUCTION_NOT_TARGETED=PASS
REHEARSAL_RESULT=PASS_ALL_CHECKS_ROLLED_BACK
NO_INVOICE_COMMIT_REQUESTED=PASS
```

**Acceptance interpretation:** This is a PASS for the bounded **real MAIN DEVELOPMENT Frappe/MariaDB controller integration** using the already-scoped **synthetic Finance Checker**, not merely mocked Python tests. In the uncommitted transaction the original one-line finalized CCPC→Ricor batch successfully generated exactly one linked **Draft** CCPC SI and one linked **Draft** Ricor PI; verified both companies, native internal parties, billing month-end date, amounts, frozen item and qty/rate, no tax or stock update; persisted in-session batch had `Approved` status and audit/checker/reciprocal links; SI/PI rows increased by one each while GL/SLE row counts remained unchanged. The V2 API interceptor suppressed **12** allowed *deferred UI realtime notifications* (`doc_update`/`list_update`), which is consistent with normal save notifications causing the V1 false safety abort. No other blocked outbound API was called in this execution. The controller transaction was explicitly rolled back, and a **fresh read-only transaction** verified batch reverted to `Under Review` without approved actor/invoice links or same-remark invoice rows and original SI/PI/GL/SLE counts. No lasting SI/PI pair or GL/SLE postings were requested.

**Limits and follow-up:** This proves exactly one guarded one-line success+rollback, not concurrent approvers, secondary retries/replay, native `submit`/cancel, actual GL/stock reconciliation, real named accounting user rights, HTTP/CSRF, multi-line, external mail/network risk from arbitrary hooks, fresh restore-tested backups, or PRODUCTION readiness. The host's V1 and V2 private one-use markers are both consumed; never clear/reuse. The previous historical NAS manifests are **not** a fresh pre-committed approval backup.

**Next gate:** separately approve and prepare one **persisted** Draft SI/PI checker approval on MAIN DEVELOPMENT only after a **fresh independently verified scoped backup**, exact named human Finance Controller decision (or explicit policy acceptance of synthetic test actor), strict Company User Permissions, source/role/account master data reconfirmation, and review of automatic hooks. One commit should create precisely one Draft pair and mark batch Approved; no immediate invoice `submit()` or GL posting, no production deployment. Then run native lifecycle and reconciliation under separate authorization. Do not turn this rehearsal PASS into permission for an actual financial commit.

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
