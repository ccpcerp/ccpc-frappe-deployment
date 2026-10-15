# CCPC ERPNext — CURRENT HANDOFF

**Last verified update:** 2026-10-15 (GitHub connector and operator terminal reports).  
**Purpose:** This is the **single rolling GitHub handoff** for CCPC ERPNext. Maintain **this same path** at meaningful milestones, during longer conversations before a thread limit is reached, and when the operator requests a handoff. Do not create a new dated Project Source attachment every time.

> **Read first in every new project conversation:** [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), then this handoff, then verify relevant live GitHub branches and commits with the GitHub connection. The permanent ChatGPT Project Instructions define policy; older Project Sources and dated handoffs supply historical context only. If information conflicts, the most recently verified GitHub state takes precedence. If GitHub is inaccessible, report the inability to verify rather than treating old snapshots as current.

## Owner-approved corrected SLE/GL-allowlisted rollback-only test prepared; NOT YET RUN — 2026-10-15

**Authorization:** Owner replied **"aPPROVED"** to the narrowly scoped offer to **prepare and execute one corrected rollback-only diagnostic on `ccpc-integration2.localhost`**, following the prior diagnostic's confirmed harness-only `STOP: Unexpected document submission: Stock Ledger Entry` error. This authorization covers **one** new transient isolated posting-path rehearsal, unconditional SQL rollback and independent post-rollback read-only verification; it **does not authorize** a committed Material Issue, repeat/replay of earlier one-shot scripts, database repair or restore, PRODUCTION or shared DEVELOPMENT changes.

**GitHub read-only re-verification:** App feature `feature/withdrawal-material-issue-safety` pinned SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`; shared DEVELOPMENT review `review/intercompany-approval-failure-tests` SHA `806fa23516490ec7beefcff03a1baa09d722120e`; draft app PR #7 open/unmerged. Installed ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` source confirmed `erpnext/stock/stock_ledger.py:make_entry` performs `Stock Ledger Entry.submit()`, and `erpnext/accounts/general_ledger.py:make_entry` performs `GL Entry.submit()`. Both are legitimate effects of normal Material Issue `Stock Entry.submit()` and were incorrectly blocked by the prior test harness (not shown to be a CCPC app defect).

**New operator-only artifact, prepared locally; user execution NOT YET REPORTED:** `ccpc_material_issue_corrected_rollback_diagnostic.sh`, SHA256 **`098ef7e45d2b6915dd8c820192cbbfbb757ba5bf6f96d44cafb9504f961d1f01`**. Derived from but **does not overwrite or replay** first rollback-only diagnostic `ccpc_material_issue_rollback_only_diagnostic.sh`. It retains exact Git/site/isolated DB/12 checkpoint sets and 48 artifact fingerprints, baseline one unsubmitted `WS-2026-00001` with empty `received_by`, fictitious Users and roles, zero Stock Entry, one existing SLE and two GL, 10 Nos/PHP1,000 Bin, accounting defaults and installed live CCPC Stock Entry hooks. Under Stockroom B in one SQL transaction temporarily saves a fictional `Received By`, calls the actual pinned handler `issue_withdrawal_slip(SLIP)` **exactly once**, then **unconditionally rolls back even if all checks pass**. It has **no explicit COMMIT** and patches `frappe.db.commit` to STOP if any internal commit is attempted; retains outgoing email/enqueue and unrelated document insertion/submission prohibitions. Source is loaded from pinned isolated feature checkout, not switched/pulled into shared checkout. Site-init may have Redis/cache effects that SQL rollback cannot reverse; cannot claim zero non-SQL effects.

**Narrow correction:** Capture exactly one permitted pre-submission **draft Stock Entry.insert** and the same stock document's `submit`. Bind a maximum of **one `Stock Ledger Entry.submit/insert`** to its exact stock voucher, synthetic `CCPC-INT-TEST-CONSUMABLE-001`, issuer Company, `Stores - TISS`, and `-1 Nos`. Bind at most **two `GL Entry.submit/insert`** to the same voucher, issuer Company and exactly `Stock Adjustment - TISS` debit (~PHP100, `Main - TISS`) and `Stock In Hand - TISS` credit (~PHP100). Reject duplicate/wrong voucher/item/quantity or unrelated submissions. Only accept an in-transaction successful handler if actual SQL shows exactly one submitted linked Material Issue, one new SLE, two balanced GL rows, correct Slip `Fully Issued` state, expected Bin 9 Nos/approx PHP900; **then still ROLLBACK, not COMMIT**. Fresh independent direct MySQLdb READ ONLY post-rollback audit must confirm unchanged original business/stock/GL and Email Queue, and verify original 48 backup-file fingerprints, site config and Git source unchanged. Sanitized STOP reason and path/line traceback are retained if any downstream guard fails.

**Local-only validation:** `bash -n`, embedded Python `ast.parse`, static one-handler/no-commit contract and simulated allowlist exercises all PASS: exact one Stock Entry draft insert/submit, one SLE submit/insert, two GL submit/inserts accepted; duplicate SLE, duplicate Stock Entry, wrong GL voucher, wrong SLE quantity and unrelated Journal Entry rejected. **These are not real ERPNext integration results.** The prior 12th recovery set `20261015_085718-ccpc-integration2_localhost` stays protected; historical snapshots unmodified in this conversation. Existing real persisted baseline last independently verified is Slip `WS-2026-00001` in Stockroom Review, Received By empty, 0 Stock Entries, 1 SLE, 2 GL and 10 Nos/PHP1000.

**Operator gate:** Send checksum-pinned script once from Windows Downloads to `gani@192.168.50.166` and execute once with `bash`. **Never rerun this script or the prior scripts**, including after a STOP; report its sanitized terminal output. Expected successful completion requires both `INDEPENDENT POST-ROLLBACK SQL BASELINE: PASSED` and `CORRECTED ROLLBACK-ONLY MATERIAL ISSUE TEST: COMPLETED`; even a successful transient stock/GL pathway is **not** permission to commit and does not prove HTTP POST/CSRF, concurrency or production readiness.


## Rollback-only diagnostic pinpointed harness-only Stock Ledger Entry submit guard — 2026-10-15

**Operator successfully ran once** the separately owner-approved `ccpc_material_issue_rollback_only_diagnostic.sh` SHA256 `f74f00e23f6b2532eeefe3bdcb98c18023de7b33cf5ef388f05e7e2d237f0f5c`, expressly limited to an **unconditionally rolled-back diagnostic**, not a committed posting. Exact terminal output: `PINNED SOURCE, ISOLATED SITE, AND 12 RECOVERY CHECKPOINTS: VERIFIED`; `PINNED MATERIAL ISSUE HANDLERS: VERIFIED`; `ONE UNPOSTED SLIP, STOCK AND ACCOUNTING BASELINE: VERIFIED`; `FICTIONAL RECEIVED BY: TEMPORARILY SAVED (UNCOMMITTED)`; **`ROLLBACK-ONLY DIAGNOSTIC SQL: ROLLED BACK`**, **`INDEPENDENT POST-ROLLBACK SQL BASELINE: PASSED`**, `BACKUPS, CONFIGURATION AND SOURCE: UNCHANGED`, `OBSERVED FAILURE CLASS: RuntimeError`, `OBSERVED FAILURE STAGE: diagnostic: invoke pinned one-unit issue handler as Stockroom B`, **`SANITIZED FAILURE REASON: STOP: Unexpected document submission: Stock Ledger Entry`**, `DIAGNOSTIC OUTCOME: EXCEPTION CAPTURED; NO STOCK POSTED`, **`ROLLBACK-ONLY MATERIAL ISSUE DIAGNOSTIC: COMPLETED`**, `THIS DIAGNOSTIC MUST NOT BE RERUN`. Safe traceback ended `apps/erpnext/erpnext/stock/doctype/stock_entry/stock_entry.py:590:on_submit → :2226:update_stock_ledger`, `apps/erpnext/erpnext/controllers/stock_controller.py:1443:make_sl_entries`, `apps/erpnext/erpnext/stock/stock_ledger.py:125:make_sl_entries → :234:make_entry`, then `GUARDED_DIAGNOSTIC:380:limited_submit`, `GUARDED_DIAGNOSTIC:50:stop`. No successful persisted stock or accounting posting occurred; independent direct-SQL audit verified business baseline unchanged. Existing 12 site-local checkpoints/48 private files preserved.

**Root cause CONFIRMED in the TEST HARNESS, not a demonstrated feature-code defect:** The exact checksum-verified diagnostic shell/Python patched `frappe.model.document.Document.submit` and only allowed a linked `doc.doctype='Stock Entry'` to submit; it raised a deliberate `RuntimeError('STOP: Unexpected document submission: Stock Ledger Entry')` when ERPNext naturally reached its stock-ledger submission. Inspected installed ERPNext exact SHA `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` source `erpnext/stock/stock_ledger.py:make_entry`, which legitimately creates `Stock Ledger Entry` and executes `sle.submit()` as part of `Stock Entry.on_submit`. Separately `erpnext/accounts/general_ledger.py:make_entry` legitimately executes **`gle.submit()`** for each `GL Entry` when perpetual inventory accounting posts; the original guard would also block these later even though the first failure prevented reaching that point. Do **not** treat these ERPNext ledger operations as unrelated business transactions; they are necessary for accounting safety and must be allowed **strictly bound to the one authorized Material Issue**.

**Proposed narrow fix, NOT APPLIED or EXECUTED:** Modify only the *external operator test harness*, not CCPC app or ERPNext: capture the single authorized Stock Entry name on entry to its allowed `Document.submit`; allow **at most one** `Stock Ledger Entry.submit` only with matching `voucher_type='Stock Entry'`, `voucher_no=<captured name>`, `item_code=CCPC-INT-TEST-CONSUMABLE-001`, `warehouse=Stores - TISS`, issuer Company, `actual_qty=-1`, uncancelled; allow **at most two** `GL Entry.submit` only if `voucher_type='Stock Entry'`, same voucher, same issuer Company, and accounts among `Stock Adjustment - TISS` (debit, expected 100 PHP) and `Stock In Hand - TISS` (credit, expected 100 PHP) with proper cost center. Retain previous prohibition of all unrelated document submits, unrelated invoices, internal COMMIT, outgoing mail/background jobs, cross-site changes; existing before-commit SQL check must still require exactly one new SLE, two balanced new GL and bin 10→9 Nos with original business baseline/source/backups unchanged. Diagnostic error reporting should include sanitized guard reason and location to avoid another opaque `RuntimeError`. **Do not simply remove the Document.submit guard.**

**Next authorization boundary:** This approved one-shot diagnostic has been consumed; do not rerun either script. Request new explicit owner approval for the next **one** narrowly scoped retry/rollback-only validation on `ccpc-integration2.localhost` after the minimal corrected guard has been reviewed, checksum-pinned and staged. No actual posting, GitHub app code changes, new batch/GL, PRODUCTION or shared DEVELOPMENT changes are currently authorized; preserved baseline remains Slip `WS-2026-00001`, Stockroom Review, empty Received By, 0 Stock Entry, 1 original SLE, 2 original GL, Bin 10 Nos/PHP1,000. A follow-up rollback-only rehearsal before committing is the conservative preferred next validation because the downstream GL path has not yet been live-tested.


## Approved rollback-only Material Issue diagnostic PREPARED, not executed — 2026-10-15

**Owner approval:** After the first one-unit Material Issue attempt reported `RuntimeError` and independent SQL rollback readback confirmed no persisted changes, the owner explicitly replied **"Approved"** to **preparing and executing one rollback-only diagnostic** against `ccpc-integration2.localhost`, with **no intended permanent stock, ledger or GL writes**. This approval is for **one** controlled source-level diagnostic invocation and unconditional rollback only; **not** for committing/posting, retrying the original one-shot script, restoring backups, fault/concurrency tests, changing settings, persistent DEVELOPMENT or PRODUCTION operations.

**Prepared (not executed by operator yet):** `ccpc_material_issue_rollback_only_diagnostic.sh`, **SHA256 `f74f00e23f6b2532eeefe3bdcb98c18023de7b33cf5ef388f05e7e2d237f0f5c`**, new one-shot 486-line shell+embedded Python artifact. Built from locally checksum-verified original 2026-10-15 posting runner (SHA256 `aa80e6e87b0734377f7a3b90568f735af6b4893caffe8e50394cad1e759f04f3`); original remains untouched. Exact guard preconditions include shared/review and detached feature SHA/status, installed Frappe/ERPNext SHA, separate test/persistent DB identities, 12 checkpoint sets/48 SHA256-fingerprinted private archive artifacts, previously committed `WS-2026-00001` parent and 1-unit child in Stockroom Review with `received_by` empty, zero Stock Entries, original one SLE/two GL/one opening reconciliation, Bin 10 Nos/PHP1000, test users/roles and expected stock/expense settings. Loads pinned `ccpcerp` feature source in **single non-serving Docker Frappe-user process**; checks installed Stock Entry hook mappings.

**Diagnostic execution only after checksum/operator run:** within one SQL transaction authenticated as fictional Stockroom B, temporarily saves fictional `Received By`, invokes the pinned **actual** `issue_withdrawal_slip` handler **once**, checks transient issue rows if the handler unexpectedly returns, and **unconditionally `frappe.db.rollback()` even if posting path succeeds**. Patches `frappe.db.commit` to hard-stop unexpected framework/internal commits; blocks outbound mail/background enqueue and unrelated business document inserts/submissions. Rollback is invoked after the temporary patch context exits, matching the first failed runner's successful rollback behavior. Captures exception **class**, approved fixed `STOP: ...` guard **reason** if safely printable, and **last 12 module-relative traceback function:line locations only** (no source excerpts, argument values, credentials or exception messages outside pinned guards). Fresh independent MySQLdb `START TRANSACTION READ ONLY` then verifies original business/stock/GL/user baseline, zero linked Stock Entry and unchanged Email Queue count; Git source, checkpoint content hashes and site configs rechecked. No SQL COMMIT call appears in this new script; Bash `bash -n`, Python AST and static no-commit/one-handler checks passed **locally**. Expected terminal ending `ROLLBACK-ONLY MATERIAL ISSUE DIAGNOSTIC: COMPLETED` only after **`INDEPENDENT POST-ROLLBACK SQL BASELINE: PASSED`**. If a guard fails or an exception is reported, diagnostic is still a failure investigation, not a stock-posting PASS. If after rollback independent audit fails, STOP, preserve all state and investigate.

**Scope / limits:** The test may temporarily run Frappe hooks, locks and Redis/cache operations; SQL rollback does **not** in itself prove zero non-DB side effects. Do **not** rerun either original posting script or this new diagnostic; a second invocation requires separate approval. Current actual persisted state remains: `WS-2026-00001` unposted, Received By empty, 0 Stock Entries, 1 SLE, 2 GL, Bin 10 Nos/PHP1000. **No new diagnostic has been executed or result returned yet.**


## Independent SQL rollback readback PASSED after failed Material Issue attempt — 2026-10-15

**Operator independently verified the persisted business state after the approved-but-aborted Material Issue attempt** with checksum-pinned `ccpc_material_issue_rollback_readonly_audit.sh` (SHA256 `573d7ac320bc3855b295bf9181214f664780f6e55af21f81d0813aa50e59fe22`). Terminal output: `PROTECTED SOURCE CHECKOUTS: VERIFIED`, `TWELFTH RECOVERY CHECKPOINT: PRESENT; FOUR ARCHIVES READABLE`, `ISOLATED DATABASE READ-ONLY TRANSACTION: VERIFIED`, `tabWithdrawal Slip: 1`, `tabStock Entry: 0`, `tabIntercompany Material Billing Batch: 0`, `tabStock Ledger Entry: 1`, `tabGL Entry: 2`, `tabStock Reconciliation: 1`, `SAVED SLIP: WS-2026-00001 | STATUS: Stockroom Review | RECEIVED BY: EMPTY | ISSUED BY: EMPTY`, `SLIP ITEM: 1 Nos REQUESTED, 1 Nos REVIEWED, 0 ISSUED`, `STOCK BIN: 10 Nos / PHP 1000 / PHP 100 PER NOS — UNCHANGED`, `THREE TEST USERS AND PERMISSIONS: UNCHANGED`, `MATERIAL ISSUE SQL ROLLBACK READBACK: PASSED`, `DATABASE WRITES: NONE`, `DO NOT RERUN THE FAILED POSTING SCRIPT`. **This directly confirms that the SQL rollback left no persisted Stock Entry, inventory deduction, new ledger posting or Received By value.** Existing recovery checkpoint #12 remains readable. The audit does *not* prove that no Redis/cache or other out-of-DB effects occurred, nor is it a restore drill.

**Static failure triage only — original RuntimeError remains UNDIAGNOSED.** Reinspected the original file `/mnt/data/ccpc_isolated_one_unit_material_issue_guarded.sh` and independently confirmed its SHA256 `aa80e6e87b0734377f7a3b90568f735af6b4893caffe8e50394cad1e759f04f3`. Exception handler prints only `type(exc).__name__` and not the source location or redacted message. During issue handler it patches `frappe.db.commit`, `frappe.enqueue`, `frappe.sendmail`, `background_jobs.enqueue`, and Document insertion/submission guards, all of which can raise a user-defined `RuntimeError('STOP: ...')`; Frappe/ERPNext runtime can also raise that class. Connected GitHub source `frappe/erpnext` at **installed** SHA `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` contains potential internal SQL commit paths for **item valuation reposting only** (`erpnext/stock/stock_ledger.py` near lines 330 and 776); these are **not proof** that the failed simple Material Issue reached such a path. The submitting handler returned no result line; exact failing guard cannot be inferred from this output. Do not weaken all failure guards or guess away a deliberate safety failure.

**Next proposed gated action:** continue non-mutating source and backup analysis, then if needed prepare a separate checksum-pinned *transactional diagnostic* designed to report a sanitized `RuntimeError` message and traceback location with strict no-commit/rollback and no ledger persistence. **Even rollback-only execution may transiently invoke document hooks and out-of-SQL operations, so requires a fresh explicit owner authorization.** Do not execute the original one-shot again, post stock or manipulate backups in the meantime. No persistent DEVELOPMENT/PRODUCTION changes approved.


## First approved isolated one-unit Material Issue attempt STOPPED; SQL rollback reported — 2026-10-15

**Operator terminal evidence; NO successful Material Issue claimed.** Owner ran checksum-pinned one-shot `ccpc_isolated_one_unit_material_issue_guarded.sh` SHA256 `aa80e6e87b0734377f7a3b90568f735af6b4893caffe8e50394cad1e759f04f3`. Output: `PINNED SOURCE, ISOLATED SITE, AND 12 RECOVERY CHECKPOINTS: VERIFIED`, `PINNED MATERIAL ISSUE HANDLERS: VERIFIED`, `ONE UNPOSTED SLIP, TEST USERS, STOCK AND ACCOUNTING BASELINE: VERIFIED`, `FICTIONAL RECEIVED BY: SET UNDER STOCKROOM B IN TRANSACTION`, **`POSTING TEST TRANSACTION: ROLLED BACK (SQL)`**, `ISOLATED MATERIAL ISSUE TEST: STOPPED`, `STAGE: one authorized issue transaction: set Received By and submit as Stockroom B`, `ERROR CLASS: RuntimeError`, `PRESERVE ALL BACKUPS AND EXISTING SLIP — DO NOT CLEANUP OR RERUN`. There was **NO** `STOCKROOM B MATERIAL ISSUE SUBMISSION: COMPLETED IN TRANSACTION`, `ONE LINKED MATERIAL ISSUE: COMMITTED`, or `INDEPENDENT POST-COMMIT SQL READBACK: PASSED` output. The explicit commit path in the reviewed script was not reached. A transient `received_by='CCPC Fictional Integration Test Receiver'` was saved within the SQL transaction, then the Python exception handler called `frappe.db.rollback()` successfully as reported. An independent fresh SQL check **has not yet been run**; do not assert committed row counts solely from the rollback statement. Redis/cache/non-DB side effects might remain, unverified.

**Failure not yet diagnosed.** I inspected the exact checksum-matched local script after the operator's failure. Its `stop(reason)` deliberately raises `RuntimeError('STOP: '+reason)`; it patches `frappe.db.commit` to reject unexpected internal commits, `frappe.sendmail`, `frappe.enqueue` and background `enqueue` to reject unexpected async side effects, and `Document.insert`/`submit` to reject unrelated documents. Actual Frappe/ERPNext code can also raise `RuntimeError`. Critically, the original exception reporter printed only `type(exc).__name__`, not a safe message, call site or traceback. Therefore **exact failure guard / root cause is UNKNOWN**. Stage remained the transaction stage; failure occurred *after* `Received By` was saved and *before* the outcome was printed, plausibly in handler/Stock Entry hooks, but cannot be narrowed without further read-only analysis. **Never rerun v1** to extract a traceback; do not mutate Slip or recover/delete backups.

**Prepared (not executed) independent zero-write follow-up:** `ccpc_material_issue_rollback_readonly_audit.sh` SHA256 **`573d7ac320bc3855b295bf9181214f664780f6e55af21f81d0813aa50e59fe22`**, Bash and embedded Python AST syntax verified. One Docker `frappe`-user Python process without `frappe.init`; checks four exact pinned Git SHAs/shared `?? AGENTS.md`, 12 existing snapshot sets/48 archive files and current checkpoint gzip/TAR readability, direct MySQLdb connection to separately identified `ccpc-integration2.localhost` using `START TRANSACTION READ ONLY`, original 1 Slip/0 Stock Entry/0 billing/1 SLE/2 GL/1 opening Reconciliation counts, Slip owner/parent `status='Stockroom Review'` and `received_by`/issuer EMPTY, one unchanged child with 0 issued, original 10 Nos/PHP1,000 Bin, original three test User role sets and no persisted linked Stock Entry; explicit rollback/close; **no source/DB mutations**. It should stop and report any unexpected persistence, preserve backup and not auto-fix. Its passing output would independently confirm SQL rollback did not persist those business changes, **not** resolve `RuntimeError` trigger.

**Authorization boundary:** Owner's approval was for one 1-Nos actual issue, and the first script attempted the authorized transaction and stopped. **Do not retry automatically**; first obtain zero-write audit evidence and identify the failed guard from static/source analysis or separately approved diagnostic before asking for a new tightly scoped retry authorization. No PRODUCTION, shared DEVELOPMENT, migrations, concurrency, restoration or unapproved financial transaction.


## Owner approved one isolated 1-Nos Material Issue; guarded one-shot script PREPARED — 2026-10-15

**Explicit approval:** Owner replied **"Approved"** to the immediately preceding precisely scoped proposal: prepare and execute **exactly one** synthetic **1 Nos** Material Issue linked to existing `WS-2026-00001` on **`ccpc-integration2.localhost` only**, including entering one fictional `Received By`, using independent `ccpc-int-stockroom-b@example.test` as issuer and validating stock/GL changes. This approval covers the **one real isolated-site posting only**, not a second issue, repeat/duplicate attempt, concurrency/failure injection, cancellation/restore, extra fixture edits, persistent DEVELOPMENT/PRODUCTION, migrations, branch changes or merges.

**GitHub/source:** Connector reverified `feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`; persistent DEVELOPMENT `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e`; draft app PR #7 open/unmerged. Inspected pinned feature's actual POST-whitelisted `issue_withdrawal_slip` (independent Stockroom check, Slip row `FOR UPDATE`, duplicate Stock Entry checks, scoped new Stock Entry `insert(ignore_permissions=True)` + `submit()`; hooks on validate/before_submit/on_submit) and Slip Stockroom-only `received_by` mutation logic. Installed Frappe and ERPNext SHAs were previously independently verified, and full preposting checkpoint #12 (48 artifacts) just archive-verified.

**Prepared artifact, NOT yet run on user's server:** `ccpc_isolated_one_unit_material_issue_guarded.sh`, **SHA256 `aa80e6e87b0734377f7a3b90568f735af6b4893caffe8e50394cad1e759f04f3`**, Bash and embedded Python AST syntax checked, guarded 420-line one-time operator script. It runs a fresh non-serving `docker exec -i --user frappe` Python process with `FRAPPE_STREAM_LOGGING=1` and `PYTHONDONTWRITEBYTECODE=1`. Verifies exact four installed/pinned Git SHAs, active shared checkout and protected untracked `AGENTS.md`, detached feature cleanliness, separate target/persistent database identities, **12 recovery sets/48 SHA256-fingerprinted files** including newly validated prefix `20261015_085718-ccpc-integration2_localhost`, 1 saved unposted Slip and one child requested/reviewed 1 Nos, exactly three fictional Users/role sets, zero Stock Entry, zero intercompany batches, 1 opening SLE/2 opening GL and synthetic Bin 10 Nos/PHP1000 at PHP100/No, issuer account/Stock Settings and installed-site hook mapping. **No process source or Git switch.**

**Authorized transaction design:** Set Frappe session to Stockroom B, save only `WS-2026-00001.received_by='CCPC Fictional Integration Test Receiver'` using real Slip `save()` validation; **inside the same explicit SQL transaction**, call the real pinned whitelisted `issue_withdrawal_slip(SLIP)` implementation **directly as authenticated Frappe session B**. It exercises the actual handler/security/Stock Entry submit/ledger/hooks, **not HTTP POST transport/CSRF authentication**. Prevent any internal `frappe.db.commit()`, new unrelated business document submission/inserts, outgoing email or enqueued jobs. Before the **one** explicit commit require one submitted Stock Entry owned/issued by B and linked by parent+child provenance to the exact item/Slip, parent Slip `Fully Issued`, issued_qty=1, Bin Qty 9 and value about PHP900, one new SLE delta -1 Nos/about -PHP100, precisely two new balanced GL rows debit `Stock Adjustment - TISS` PHP100/ `Main - TISS` and credit `Stock In Hand - TISS` PHP100, accounting baseline and backup/source fingerprints unchanged. Financial tolerance in the guard is PHP0.05; unexpected valuations/extra entries force **precommit rollback** rather than accepting an unexplained posting. On successful commit, fresh independent MySQLdb `START TRANSACTION READ ONLY` re-verifies the persisted stock and GL results. Distinguishes a failed precommit rollback from an attempted/confirmed SQL commit; in either case **never run this script again**. Normal Frappe Redis/cache effects may outlive SQL rollback; if any anomaly, investigate separately.

**Status:** SCRIPT PREPARED AND SYNTAX VALIDATED ONLY. **No Material Issue has been run/posted as of this handoff update.** A successful operator run must show `ONE LINKED MATERIAL ISSUE: COMMITTED`, `INDEPENDENT POST-COMMIT SQL READBACK: PASSED`, `ISOLATED SINGLE MATERIAL ISSUE TEST: PASSED`; until terminal evidence arrives do not claim stock is 9 or GL changed. Operator should download `ccpc_isolated_one_unit_material_issue_guarded.sh`, checksum-pin to `aa80e6e87b0734377f7a3b90568f735af6b4893caffe8e50394cad1e759f04f3`, run exactly once from `gani@192.168.50.166`, paste complete output, and **stop** on any failure with no cleanup/retry. A full restoration drill, idempotency/repeated POST, concurrency and production deployment are still unapproved/untested.


## Twelfth protected isolated recovery checkpoint created and archive-verified — 2026-10-15

**Operator terminal output verified backup-only success:** The user ran the previously downloaded checksum-pinned `ccpc_isolated_post_slip_backup_guarded.sh` (SHA256 `385169bfb6460b3209902daf8d27d23756881ebf21b7bbbd95eb331f34189506`) on the DEVELOPMENT host. The console reported `PROTECTED SOURCE AND SITE IDENTITY: VERIFIED`, `PREVIOUS RECOVERY SETS: 11 / 44 FILES FINGERPRINTED`, `EXISTING TEST SLIP, USERS, STOCK AND LEDGERS: VERIFIED`, `NEW ISOLATED RECOVERY DIRECTORY: CREATED EMPTY`, `FRAPPE BACKUP RETENTION: REDIRECTED TO NEW EMPTY DIRECTORY`, `ONE FULL ISOLATED-SITE BACKUP: CREATED`, `FOUR NEW PRIVATE BACKUP ARTIFACTS: ARCHIVE-VERIFIED`, `EXISTING 44 BACKUP FILES: SHA256 UNCHANGED`, `ISOLATED DATABASE, BIN AND LEDGERS: UNCHANGED`, `SHARED DEVELOPMENT AND PINNED FEATURE: UNCHANGED`, `RECOVERY CHECKPOINTS: 12 SETS / 48 ARCHIVE-VERIFIED FILES`, `RESTORE DRILL: NOT PERFORMED`, and **`ISOLATED POST-SLIP BACKUP: PASSED`**.

**Exact new protected destination, isolated site-local filesystem only:**
`sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-verified-withdrawal-slip-pre-material-issue-20261015`.

**Four artifacts as printed (no confidential contents published):**
- `20261015_085718-ccpc-integration2_localhost-database.sql.gz` — 1,008,563 bytes.
- `20261015_085718-ccpc-integration2_localhost-files.tar` — 10,240 bytes.
- `20261015_085718-ccpc-integration2_localhost-private-files.tar` — 10,240 bytes.
- `20261015_085718-ccpc-integration2_localhost-site_config_backup.json` — 212 bytes.

The guarded script's output supports that this checkpoint includes the isolated test state with the existing committed `WS-2026-00001` (Stockroom Review), three fictional Users and synthetic Bin at 10 Nos/PHP1,000, with zero Stock Entries, one preexisting SLE and two opening GL entries; business data, prior 44 backups, Git checkout and site config remained unchanged. **Archive/hash verification is not a successful restore test**, and this is a **site-local recovery copy, not an independently verified NAS/off-host copy**. Never publish the site_config or any dump because it can contain sensitive site data/config. GitHub stores only names/sizes/procedure, **not backups or secrets**. Site persistence is confirmed by operator script output; no separate new Frappe posting/integration test occurred.

**Authority gate:** The backup-only owner approval has been fulfilled. Do not rerun this one-shot script. No PRODUCTION action, persistent DEVELOPMENT modification, stock issue/GL transaction, `received_by` change, user-role change, database migration or restore is approved. The next possible milestone is a separately **explicitly authorized** one-unit Material Issue test on `ccpc-integration2.localhost` using independent Stockroom B and existing `WS-2026-00001`, only after reviewing and checksum-pinning the guarded transaction/rollback/independent-ledger-audit procedure. Expected account pair under the verified current isolated config: **debit Stock Adjustment - TISS, credit Stock In Hand - TISS**; forecast stock 10→9 Nos and nominal 100 PHP expense/stock transfer (not a verified posting). Preserve the now-protected pre-posting checkpoint.


## Owner-approved isolated post-Slip backup: guarded operator script prepared — 2026-10-15

**Explicit owner consent:** The owner responded **"aPPROVED"** to the narrowly scoped request to create **one new full recovery backup of `ccpc-integration2.localhost` only**, after the independently verified saved fictional Slip `WS-2026-00001` and three fictional users. This consent covers **only** a site-private backup (MariaDB dump, public files, private files, site_config), archive/hash integrity validation and preservation of existing snapshots. **No restoration/drill, cleanup/retention deletion, migration, user or Slip change, stock/GL posting, persistent DEVELOPMENT modification, Docker recreation or PRODUCTION operation is authorized.**

**Review/source safety:** Connected GitHub reverified app feature `feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` and persistent shared DEV base `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e`. Installed `frappe` source `988e54f3c4c291e2077a83809663f123731abe76` was inspected in GitHub: `frappe/utils/backups.py:new_backup()` **unconditionally** invokes `delete_temp_backups()` **even with an explicit backup_path**, so a naive bench backup could delete historical files under `private/backups`. The approved isolated process must temporarily override **in-memory** `frappe.conf.backup_path` to a new empty site-private directory, validate `get_backup_path()`, then call `scheduled_backup(ignore_files=False, backup_path=<same new directory>, ignore_conf=True, force=True)` exactly once. `ignore_conf=True` ignores backup include/exclude restrictions, but still writes the backed-up site configuration. Installed logging previously required `FRAPPE_STREAM_LOGGING=1` to avoid a missing parent logs directory; it is enabled only in the short-lived process.

**Prepared — NOT RUN on operator server:** Guarded local artifact `ccpc_isolated_post_slip_backup_guarded.sh`, SHA256 **`385169bfb6460b3209902daf8d27d23756881ebf21b7bbbd95eb331f34189506`**. Bash and embedded Python AST syntax checks and static guard checks passed locally. Uses `docker exec -i --user frappe frappe_docker_devcontainer-frappe-1`, never switches source branch, checks exact Frappe/ERPNext/CCPC SHAs and protected `?? AGENTS.md`, distinct isolated vs `development.localhost` DB names, one unposted `WS-2026-00001`, test User role assignments, 0 Stock Entry, 1 SLE, 2 GL, 1 opening Stock Reconciliation, 0 intercompany billing batches, Bin 10 Nos/PHP1,000; fingerprints **all 44 original checkpoint files** across 11 sets before backup. Verifies >1 GiB free, and creates **one new, previously nonexistent** 0700 destination `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-verified-withdrawal-slip-pre-material-issue-20261015/`. Runs one full Frappe backup after safely redirecting its retention cleanup into the empty destination; requires 4 regular private (no-group/world-access) files, exact timestamp/site slug/name pattern, complete gzip stream with saved test Slip and test-user strings, readable/safe public+private TARs, and backed-up site config byte hash/DB identity. Afterwards hashes all 44 old archives again, confirms site config and Git checkouts unchanged, independently re-reads DB baseline. **Never removes partial backup files or existing backups; no automatic retry.** The script intentionally prints only safe filenames, sizes, and stage on error, not secrets.

**State: BACKUP EXECUTION PENDING OPERATOR.** If the script runs successfully expect `ISOLATED POST-SLIP BACKUP: PASSED` and 12 site-private checkpoint sets/48 archive-verified files; these counts are prospective, not achieved yet. A file checksum/archive scan **is not a restore drill**. Do not retry automatically if a stage stops, even with an empty/partial destination; report full output first. Real Material Issue, any `received_by` edit or stock/GL accounting postings remain gated by separate explicit owner approval.


## Account-path audit PASS; expense/account resolution and installed ERPNext source verified — 2026-10-15

**Operator-provided full output from checksum-pinned read-only diagnostic `ccpc_material_issue_account_path_readonly.sh` SHA256 `204a1bed155bcb5cb35a3c5f86fc01ea069d3a3cb0076515f67a10c4f176044a`:** `ISOLATED DATABASE READ-ONLY TRANSACTION: VERIFIED`; existing one unsubmitted `WS-2026-00001` and business baseline passed; Bin remained 10 Nos / PHP 1000 / PHP 100 per Nos; `DATABASE WRITES: NONE`; **`ACCOUNT PATH AND STOCK SETTINGS READ-ONLY AUDIT: PASSED`**. Real installed code SHAs as reported by operator: `apps/erpnext=4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`, `apps/frappe=988e54f3c4c291e2077a83809663f123731abe76`. The actual *installed* ERPNext Stock Entry `get_item_details`, ledger `on_submit`, `StockController.make_gl_entries/get_gl_entries`, and warehouse account fallback were independently inspected on connected GitHub at exact ERPNext commit `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`. This resolves uncertainty from earlier reliance on newer upstream version-16 HEAD: installed source contains the same Material Issue account default behavior.

**Actual isolated test settings from operator:** `Item Default` expense account and buying cost center both None. `Consumable` Item Group issuer-company expense account and buying cost center both None. `Integration Test Issuer` stock adjustment account `Stock Adjustment - TISS`; inventory account `Stock In Hand - TISS`; cost center `Main - TISS`; perpetual inventory on. `Stock Settings` from `tabSingles`: Moving Average, allow negative stock 0, no freeze date (freeze days 0), no special stock authorization role. `Stores - TISS` and parent `All Warehouses - TISS` both have null explicit account; resolved asset fallback `Stock In Hand - TISS`, verified active non-group Asset/Stock account. Expense fallback `Stock Adjustment - TISS`, verified active non-group Expense/Stock Adjustment account. Cost center `Main - TISS` valid. **Verified expected account pair for current synthetic fixture: debit Stock Adjustment - TISS, credit Stock In Hand - TISS** for one-unit Material Issue. Under current Bin Moving Average of PHP100/No and no intervening transaction, approximate expected debit and credit PHP100, stock 10→9 Nos and value PHP1000→PHP900; **actual rates, postings, GL balancing and quantity must be read from real committed ERPNext result**. Stock Adjustment is technically the configured fallback, not proof it is CCPC's preferred business expense categorization. Do not silently edit Item/Item Group/Company accounting masters to force COGS.

**Next safe gate:** decide whether `Stock Adjustment - TISS` is the intended test debit (versus deliberately configuring ordinary consumption expense in a separately approved change). Arrange **fresh isolated-site-only post-Slip database+private-files recovery checkpoint** (historical checkpoint predates the 3 fictitious users and Slip); verify integrity and protected environment boundaries; backup is not a restoration drill and none has yet been created this turn. Only then separately approve setting `received_by` and invoking exactly one restricted Material Issue posting as Stockroom B. No such write or PRODUCTION action is presently approved.


## Account-path follow-up SQL diagnostic prepared; NOT EXECUTED — 2026-10-15

**Operator-only artifact:** `ccpc_material_issue_account_path_readonly.sh` SHA256 `204a1bed155bcb5cb35a3c5f86fc01ea069d3a3cb0076515f67a10c4f176044a` passed Bash `bash -n` and embedded Python AST parse locally. No user-side execution yet. It creates no records and uses separate isolated DB `START TRANSACTION READ ONLY` / rollback, does not call `frappe.init`, and prints installed ERPNext/Frappe Git SHAs, Item Group `Consumable` expense/cost center defaults, Stock Settings from `tabSingles`, Warehouse parent account inheritance and resolved asset/expense Account status. Fail closed on changed one-Slip/zero-Stock-Entry/one-SLE/two-GL baseline or 10 Nos/PHP1,000 Bin. **Passing output is account-path prerequisite evidence, not an authorization for stock or GL posting.**


## Read-only pre-posting accounting audit PASSED; Material Issue account fallback requires Item Group check — 2026-10-15

**Operator supplied complete terminal output** from previously prepared SHA256-pinned `ccpc_material_issue_accounting_readonly_audit.sh`, `17aca52d156d596607a67483d39f6e33d78e16b2239b4671dd8d5cfd4e9abca6`. Output passed protected Git source checkouts, existence of earlier recovery checkpoints (**not** a restore drill), isolated DB read-only transaction, and the existing single test Slip, roles, stock and GL baseline. It ended **`PRE-POSTING ACCOUNTING READ-ONLY REVIEW: COMPLETED — AWAITING CONFIGURATION REVIEW`**, **`DATABASE WRITES: NONE`**, protected checkouts unchanged. The audit does not authorize a posting or prove eventual GL booking.

**Site values independently read by operator:** issuing Company `Integration Test Issuer`/`TISS` currency PHP; `enable_perpetual_inventory=1`, `stock_adjustment_account=Stock Adjustment - TISS`, `default_expense_account=Cost of Goods Sold - TISS`, `cost_center=Main - TISS`, `default_inventory_account=Stock In Hand - TISS`, `stock_received_but_not_billed=Stock Received But Not Billed - TISS`. Active stock Item `CCPC-INT-TEST-CONSUMABLE-001` in Item Group `Consumable`, UOM Nos, serial=0, batch=0, item-level `valuation_method` blank (global setting not yet read), company-specific Item Default `expense_account=None` and buying/selling cost centers None. `Stores - TISS` is enabled, leaf, belongs to issuer, `Warehouse.account=None` (but parent Warehouse may specify an override). `tabBin` actual 10 Nos/value PHP1,000/rate PHP100, reserved=0/projected=10. `Cost of Goods Sold - TISS` is enabled leaf Expense / Cost of Goods Sold; `Stock Adjustment - TISS` is enabled leaf Expense / Stock Adjustment; `Main - TISS` valid enabled leaf issuer Cost Center. Stock Entry/Detail provenance columns verified. Prior `WS-2026-00001` remains unposted; no SLE/GL change was reported.

**Important source review correction:** connected GitHub confirms ERPNext upstream is `frappe/erpnext` (`version-16` retrieved at commit `fd97695de7bfeb1d7728a7370c3e128d0cc1509e`, *not yet pinned to installed container ERPNext SHA*). In `erpnext/stock/doctype/stock_entry/stock_entry.py` `StockEntry.get_item_details` (approx. line 2943–2983), **Material Issue row expense-account selection is `Item Default.expense_account` → company-specific `Item Group.item_group_defaults.expense_account` → `Company.stock_adjustment_account`**. The present item override is empty, so unless the Consumable Item Group has a company-specific expense account, posting would debit **`Stock Adjustment - TISS`**, **not** automatically use `Company.default_expense_account=Cost of Goods Sold - TISS`. Cost center similarly checks project/item/group defaults then Company cost center. Warehouse inventory account with warehouse.account absent is resolved from parent Warehouse account or Company default inventory account, per `erpnext/stock/__init__.py`. Ledger entries for a Material Issue under perpetual inventory debit selected difference/expense and credit inventory based on actual stock value difference; account, values and counts must be audited after posting, not assumed before. `Stock Settings` is **Single DocType** (confirmed `erpnext/stock/doctype/stock_settings/stock_settings.json`, `issingle=1`); `STOCK SETTINGS: TABLE OR RELEVANT COLUMNS UNAVAILABLE` is not proof of a configuration defect—read `tabSingles` for `valuation_method`, `allow_negative_stock` and stock freeze settings.

**Next SAFE action (no new write approval):** fresh read-only isolated SQL check of Item Group `Consumable` company-specific expense/cost-center default (and optional parent group ancestry), `Stock Settings` `tabSingles`, parent Warehouse account chain, `Stock In Hand - TISS` Account asset/Stock status, unchanged `WS-2026-00001` and Bin, and the installed ERPNext checkout commit (read-only). Do not configure/change item group defaults automatically based on the desired accounting outcome. A new *isolated-only* recovery checkpoint after the saved Slip, a clear intended debit-account policy, and explicit separate owner approval are still needed before editing `received_by` or submitting a one-unit Material Issue. PRODUCTION remains outside the scope.


## One-unit Material Issue reviewed; accounting preflight prepared WITHOUT posting — 2026-10-15

**Scope / owner consent:** User said **"Proceed"** immediately after being offered **review and preparation** of the next controlled one-unit Material Issue test. This authorizes code review and non-mutating preparation, **NOT** invoking `issue_withdrawal_slip`, setting `received_by`, submitting any Stock Entry, posting SLE/GL, inventory deduction, additional database fixture writes, backups/restores or modifying persistent DEVELOPMENT/PRODUCTION. Do not interpret this turn as posting approval.

**GitHub source verification:** App feature branch `feature/withdrawal-material-issue-safety` still at SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, draft unmerged PR #7; persistent DEV review base `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e`. Inspected exact feature `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` and `ccpcerp/hooks.py`; this is **static code review**, not a new live posting test:
- `issue_withdrawal_slip` is POST-whitelisted; checks Stockroom role, acquires parent `tabWithdrawal Slip` `FOR UPDATE`, verifies current status, `received_by`, real peer issuer different from saved creator/Prepared By, Slip write permission; rejects both previously submitted and existing draft linked Stock Entries. It builds one new Material Issue, flags `ignore_permissions` **only** on its new Stock Entry, inserts then submits it; deliberately contains no `frappe.db.commit` or exception catch. Frappe HTTP request rollback-on-error semantics must be tested, not presumed for manually invoked scripts.
- `Stock Entry.validate` and `before_submit` CCPC hooks validate Slip/item provenance, parent/current-row source warehouse/item/quantity, reject a pre-existing submitted issue; `before_submit` reacquires parent lock, rechecks independent issuer, current warehouse availability, and stamps `withdrawal_slip_issued_by`. `on_submit` updates Slip issue quantities and status; no duplicate idempotent return on re-POST is promised (expected second request should fail with no additional posting). Actual concurrency, server-level hooks under real submit, SLE/GL and fault rollback **still untested**.
- `_build_material_issue` supplies item, quantity, UOM, source Warehouse and Slip provenance but does **not** directly set `expense_account` or `cost_center` on Stock Entry Detail. ERPNext will select values via Item/Item Group/Company and Warehouse/accounting configuration; exact selection and whether perpetual inventory generates the expected balanced GL must be verified **before and after** posting. Official ERPNext documentation describes Material Issue stock deduction and dependent perpetual-inventory GL. Synthetic Company historical notes identify `Stock Adjustment - TISS`, `Cost of Goods Sold - TISS`, `Main - TISS`, but exact posting account selection is not yet proven. Expected stock quantity delta after a successful one-unit issue is 10→9 Nos, **do not assume** PHP900 closing stock value or exact GL row count without site accounting validation.
- Last known isolated snapshot prefix `20261014_125043-ccpc-integration2_localhost` **predates creation of the three Users and `WS-2026-00001`**. It exists but has not had a restore drill; before any irreversible inventory/accounting trial, require review of a fresh safe recoverable checkpoint scoped only to isolated site and separate owner approval. Never restore or alter PRODUCTION.

**Created read-only accounting preflight artifact (not executed against server):** `ccpc_material_issue_accounting_readonly_audit.sh` SHA256 `17aca52d156d596607a67483d39f6e33d78e16b2239b4671dd8d5cfd4e9abca6`. Bash syntax and embedded Python AST parse verified. Separate container Python process uses MySQLdb `START TRANSACTION READ ONLY` and explicit rollback, does **not** call `frappe.init`, and protects both exact Git checkouts, four existing snapshot files and separate `ccpc-integration2.localhost` DB identity. Fail-closed asserts one existing `WS-2026-00001` owner/Prepared By Stockroom A, status Stockroom Review, 1 requested/issue and 0 issued/returned, `received_by` and issuer fields still empty, no Stock Entry/billing, existing one SLE/two GL, 10 Nos/PHP1000 Bin, exact test roles and Company/Warehouse/Department links. READ-ONLY prints optional Company inventory/expense/cost-center settings, Stock Settings, Item+Item Default, Warehouse, Bin, existing synthetic Account/Cost Center metadata; guards required physical provenance columns and Git state. The final message is **`PRE-POSTING ACCOUNTING READ-ONLY REVIEW: COMPLETED — AWAITING CONFIGURATION REVIEW`**, **not** accounting approval or posting permission. Operator should run once with pinned SHA, return output for comparison; if STOP, investigate without any repair/rerun.

**Next boundary:** After preflight output verify actual expense and stock GL settings, account/cost center validity, item valuation method and serial/batch flags, conditional rollback/recovery behavior, then propose a separate *explicitly approved* scoped operation for `received_by` and exactly one linked Material Issue. No write/test posting script has been authorized or executed.


## Independent read-only post-commit audit verifies WS-2026-00001 and unchanged stock/GL — 2026-10-15

**Operator returned full output from the prior checksum-pinned `ccpc_isolated_slip_postcommit_audit.sh` direct SQL audit (SHA256 `d1f704b8deb3b55526000d325a129cf4cdf3e815c367066299dbd4b9bc8289f7`).** It reports `PROTECTED SOURCE CHECKOUTS: VERIFIED`, `EXISTING RECOVERY CHECKPOINT: VERIFIED`, `ISOLATED DATABASE READ-ONLY TRANSACTION: VERIFIED`, `tabWithdrawal Slip: 1`, `tabStock Entry: 0`, `tabIntercompany Material Billing Batch: 0`, `tabStock Ledger Entry: 1`, `tabGL Entry: 2`, `COMMITTED UNPOSTED SLIP: VERIFIED WS-2026-00001 OWNER: ccpc-int-stockroom-a@example.test STATUS: Stockroom Review`, `ONE REQUESTED/REVIEWED UNIT: VERIFIED CCPC-INT-TEST-CONSUMABLE-001`, `INVENTORY BASELINE: 10 Nos / PHP 1000 — UNCHANGED`, `PROTECTED CHECKOUTS: UNCHANGED`, `DATABASE WRITES: NONE`, and **`INDEPENDENT POST-COMMIT SLIP AUDIT: PASSED`**. Direct SQL check used a fresh `START TRANSACTION READ ONLY`, rolled back and closed; separately independently confirms the earlier operator-reported Frappe workflow commit. SLE 1 and GL 2 are the unchanged isolated opening entries, **not new postings**.

**Workflow milestone now independently verified:** exactly one unsubmitted test Withdrawal Slip `WS-2026-00001`, `status=Stockroom Review`, owner Stockroom A, child requested and reviewed 1 unit of synthetic item, no associated Stock Entry/Material Issue and no stock or accounting changes. GitHub connector reverified current app feature `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, shared base `806fa23516490ec7beefcff03a1baa09d722120e`; draft PR #7 remains open/unmerged. Original 3 fictitious User fixtures remain, and no application deployment or PRODUCTION action occurred.

**Next authorization boundary:** Do not rerun User creation or Slip workflow scripts. Any attempt to set `received_by`, invoke an actual `issue_withdrawal_slip` endpoint, create/submit a linked Stock Entry, reduce Bin, change SLE/GL, conduct concurrency/rollback tests or modify the shared DEVELOPMENT/PRODUCTION environment requires separate explicit scope and approval. For the next planned step, review the feature's posting code, ledger and account selection, idempotence, permission enforcement, recovery checkpoints and controlled 1-unit expected deltas; do not call site ready for production or infer accounting correctness from the current unposted Slip.


## One isolated unsubmitted Withdrawal Slip committed; real workflow and owner permissions PASSED — 2026-10-15

**Owner-approved operator execution SUCCESS (operator terminal evidence, not yet an independent post-commit SQL audit).** The checksum-verified `ccpc_isolated_slip_workflow_guarded_v2.sh` SHA256 `65ac3ccc0564fc8918d96933d13c5861c81fdfd0a9d65e910e183d1718061bc8` reported: `PINNED FEATURE SOURCE: VERIFIED`, `ISOLATED FRAPPE SITE AND FEATURE HOOKS: VERIFIED`, `WORKFLOW, TEST USERS, AND STOCK BASELINE: VERIFIED`, `ONE TEST SLIP CREATED IN TRANSACTION: WS-2026-00001`, `DOCUMENT OWNERSHIP AND PEER PERMISSIONS: VERIFIED`, `WORKFLOW TRANSITION: Draft -> Approved (Stockroom A)`, `WORKFLOW TRANSITION: Approved -> Stockroom Review (Stockroom B)`, `INDEPENDENT ISSUER GUARD: B ACCEPTED, SELF-ISSUER A REJECTED`, `PRE-COMMIT BUSINESS AND SOURCE CHECKS: PASSED`, **`ONE UNPOSTED TEST WITHDRAWAL SLIP: COMMITTED WS-2026-00001`**, `NO MATERIAL ISSUE, STOCK LEDGER, OR GL POSTING: VERIFIED`, `SHARED DEVELOPMENT AND PINNED FEATURE: UNCHANGED`, and **`ISOLATED WORKFLOW TEST STAGE: PASSED`**. No exceptions reported. Exactly one user-approved Slip is now expected in site `ccpc-integration2.localhost`; **do not run v1 or v2 creation/workflow scripts again.**

**What the reviewed exact v2 source verified:** Separate non-serving Frappe Python process loaded detached feature from Git SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` and checked installed site's Stock Entry hook mappings and module origins; shared base checkout at `806fa23516490ec7beefcff03a1baa09d722120e` with pre-existing `?? AGENTS.md` untouched. It authenticated as existing fictional `ccpc-int-stockroom-a@example.test` to insert one Slip for `CCPC-INT-TEST-CONSUMABLE-001`, `requested_qty=1`, Company `Integration Test Issuer`, requester Company `Integration Test Requester`, warehouse `Stores - TISS`, Department `Operations - TREQ`, with owner and immutable Prepared By equal A; tested actual per-document permissions (unrelated Requestor cannot write, owner A can read, peer B can write), applied ordinary Frappe workflow actions `Approve & Send to Stockroom` as A then `Start Review` as B, ending `status='Stockroom Review'`, `docstatus=0`, `issue_qty=1`, `received_by` and issue identity fields empty. Directly invoked **only the pure `_assert_independent_issuer` policy helper**, where B passed and A raised `frappe.PermissionError`; **did not call stock-issuing HTTP/Python endpoint or create/post a Stock Entry**. A single explicit transaction commit followed before/after guards; postcommit check counted one Slip, no Stock Entry, one SLE and two GL and unchanged Git source. Before commit it also verified test Bin at 10 Nos/PHP1,000 and Email Queue unchanged. Workflow generated ordinary comments/metadata as allowed.

**Unverified future work:** Independent fresh SQL `START TRANSACTION READ ONLY` post-commit audit must confirm persisted parent/child, exactly one Slip, no Stock Entry/Intercompany Batch or SLE/GL changes and 10 Nos/PHP1,000 Bin before any further changes. Then separate owner approval is necessary for any genuine Material Issue creation/submission, any inventory deduction, accounting ledger validation, concurrency or rollback/fault-injection test. **No PRODUCTION deployment, migrations, shared DEV switch or master/user mutations authorized.**


## Read-only Company-name diagnostic PASSED; workflow script v2 corrected — 2026-10-15

**Operator provided direct isolated MariaDB `START TRANSACTION READ ONLY` output**: `ISOLATED DATABASE: VERIFIED`, two literal Company rows `name='Integration Test Issuer', abbr='TISS'` and `name='Integration Test Requester', abbr='TREQ'`, Warehouse `Stores - TISS` belongs to `Integration Test Issuer`, Department `Operations - TREQ` belongs to `Integration Test Requester`; `tabWithdrawal Slip=0`, `tabStock Entry=0`, `tabStock Ledger Entry=1`, `tabGL Entry=2`, synthetic Bin 10 Nos / PHP 1,000; `INVENTORY BASELINE: UNCHANGED`; **`READ-ONLY COMPANY DIAGNOSTIC: PASSED`**. The first workflow script stopped before the write transaction because it mistakenly appended parenthesized abbreviations to two Company names. No new Company master records or Slip records should be created as a workaround.

**Minimal script correction prepared, NOT executed on server:** `ccpc_isolated_slip_workflow_guarded_v2.sh` SHA256 **`65ac3ccc0564fc8918d96933d13c5861c81fdfd0a9d65e910e183d1718061bc8`**. Verified original v1 SHA256 `eac81258ed5fa6627c857f13ac203ef0bd5622cc66b24f30155e26d1b7a5061f`; exact diff is **only** `ISSUER = 'Integration Test Issuer (TISS)'` → `'Integration Test Issuer'` and `REQUESTER = 'Integration Test Requester (TREQ)'` → `'Integration Test Requester'`. Bash `bash -n` and embedded Python AST parse passed. All existing safety gates, immutable prior source/roles/masters/stock/GL baselines, single intended Frappe workflow Slip, no Stock Entry or GL posting, explicit transactional rollback on error, and postcommit stop condition remain unchanged. Prior owner approval remains specifically limited to one fictional unsubmitted Slip and its two workflow transitions in `ccpc-integration2.localhost`; no business stock posting or PRODUCTION modification. Operator should checksum-verify v2 before run, **never rerun v1**, and paste full output. **Execution/result still PENDING.**


## First authorized one-Slip workflow attempt stopped at Company-name guard — 2026-10-15

**Operator-provided output** from checksum-verified `ccpc_isolated_slip_workflow_guarded.sh` SHA256 `eac81258ed5fa6627c857f13ac203ef0bd5622cc66b24f30155e26d1b7a5061f`: `PINNED FEATURE SOURCE: VERIFIED`, `ISOLATED FRAPPE SITE AND FEATURE HOOKS: VERIFIED`, `WORKFLOW TEST TRANSACTION: ROLLED BACK`, **`ERROR: RuntimeError STOP: Fictional companies unavailable`**. The exact locally mounted script was inspected: it uses `frappe.db.get_value('Company', 'Integration Test Issuer (TISS)', 'name')` and `frappe.db.get_value('Company', 'Integration Test Requester (TREQ)', 'name')`, and fails closed if either lookup does not return the exact hard-coded value. This error is raised *before* `frappe.db.begin()`, `frappe.get_doc('Withdrawal Slip', ...).insert()`, workflow transitions or attempted stock posting, so no test Slip or stock posting was attempted by this script. The rollback message is the exception handler; it does not independently verify full Redis/cache state after `frappe.init()`.

**Root cause not yet proven:** earlier independent fixture notes alternately describe requester as `Integration Test Requester (TREQ)` and `Integration Test Requester`; an exact-name mismatch is likely, but actual `tabCompany.name` values must be read from the isolated database. **No master data changes or reruns are approved.** Next action is a new, direct `START TRANSACTION READ ONLY` SQL audit of isolated `tabCompany` names/abbreviations and the Company references on `Stores - TISS` Warehouse and `Operations - TREQ` Department, maintaining DB identity and original stock/GL baseline. Only after exact identities are returned should a minimal checksum-pinned script fix be reviewed and one controlled retry considered. The previous authorization remains limited to exactly one unsubmitted fictional Withdrawal Slip and Draft→Approved→Stockroom Review transitions; no Stock Entry, stock or GL postings, shared checkout changes or PRODUCTION.


## Owner approves one isolated, unsubmitted Withdrawal Slip workflow test — 2026-10-15

The owner replied **"Approved"** to the assistant's specifically scoped proposal to **create one fictional Withdrawal Slip on `ccpc-integration2.localhost`, request 1 Nos of `CCPC-INT-TEST-CONSUMABLE-001`, and exercise the actual `Draft → Approved → Stockroom Review` Frappe Workflow** using distinct existing nonprivileged fictitious Stockroom System Users. This approval is limited to **one test Slip** (plus ordinary workflow metadata/comments), no Stock Entry or Material Issue, inventory stock ledger, general ledger or intercompany posting, no fixture master or role changes, no shared DEVELOPMENT branch/file/worker change, and **no PRODUCTION operations**. The already committed users and recovery checkpoints must remain intact.

GitHub source independently reverified before preparing the procedure: `feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`; base `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e`; draft PR #7 still open and unmerged. Frappe v16 `frappe.model.workflow.apply_workflow` calls the normal Document permission and workflow validation/save paths and produces workflow comments; all configured workflow states must remain `doc_status=0` for this test. GitHub Slip controller sets `approving_supervisor` to creator and automatically sets `issue_qty` on entering Stockroom Review. A read-only source import check previously passed, but a **live initialized Frappe site using the detached feature source has not yet been run**.

**Prepared operator script, not executed:** `ccpc_isolated_slip_workflow_guarded.sh` SHA256 `eac81258ed5fa6627c857f13ac203ef0bd5622cc66b24f30155e26d1b7a5061f` (local user-download artifact). Static bash syntax and embedded Python AST checks succeeded. It runs a fresh non-serving Docker Python process; checks Git SHAs/clean feature/only protected untracked `AGENTS.md` in shared checkout, existing snapshot files, distinct isolated/persistent DB names, feature module provenance/hook signatures, initialized isolated Frappe site/hook binding, exactly 3 test-user assigned-role sets and no ordinary Stock Entry rights, zero current Slips/Entries and 10 Nos/PHP1,000 Bin, exact fictional Company `Integration Test Issuer (TISS)` and requester `Integration Test Requester (TREQ)`, warehouse `Stores - TISS`, Department `Operations - TREQ`, and one active four-transition workflow. It only starts a DB write transaction **after passing all gates**. Within an explicit transaction it creates one Slip as `ccpc-int-stockroom-a@example.test`, checks Prepared By and owner equal A, verifies unrelated Requestor cannot write it and independent Stockroom B can, uses real workflow actions to `Approved` as A and `Stockroom Review` as B, checks `issue_qty=1`, keeps `received_by` unset, directly checks only pure independent-issuer policy helper B-allowed/A-denied, and asserts no Stock Entry/SLE/GL/billing/email queue change and no Bin change before one explicit commit. It blocks outgoing email, enqueued jobs, document submission, accidental financial/inventory Document inserts and unexpected internal commits; re-verifies source checkouts. On exception precommit: rollback, report failure. On any postcommit failure: warn **do not rerun**. No site migration, production action, routine serving-worker monkeypatch or source switch.

**State: operator execution and live workflow results PENDING.** If the procedure fails or stops, report the complete output and investigate without rerunning or cleanup. A transaction rollback is not proof all Redis/cache effects disappear. Stock posting, negative endpoint tests involving actual Stock Entries, concurrent issuance, GL and recovery drills need separately scoped approvals.


## Pinned isolated feature import/hook and unchanged site baseline PASSED — 2026-10-15

**Operator provided complete terminal output** of the hash-pinned `ccpc_pinned_feature_import_readonly.sh` (SHA256 `1f7e93d3c57ac144e71a51aebbca8149bb34853800faed4563b6aab534cbfdf3`). It reports `PROTECTED SOURCE CHECKOUTS: VERIFIED`, all six `PINNED MODULE VERIFIED` lines (`ccpcerp`, `ccpcerp.hooks`, `ccpcerp.setup`, `ccpcerp.ccpc_erp.doctype.withdrawal_slip.withdrawal_slip`, `ccpcerp.ccpc_erp.withdrawal_slip_stock`, `ccpcerp.ccpc_erp.equipment_costing`), `PINNED FEATURE HOOKS AND HANDLERS: VERIFIED`, `ISOLATED SITE AND IDENTITY BASELINE: VERIFIED`, `SITE INITIALIZATION: NOT PERFORMED`, `DATABASE WRITES AND BUSINESS TRANSACTIONS: NONE`, `PROTECTED CHECKOUTS: UNCHANGED`, and **`ISOLATED FEATURE IMPORT READ-ONLY GATE: PASSED`**.

The reviewed script pinned both Git SHAs, prepended the detached feature directory in a fresh short-lived Python process, checked the `__file__` path of every imported `ccpcerp.*` module to exclude source mixing, examined `ccpcerp.hooks.doc_events` for Stock Entry `validate`, `before_submit`, `on_submit`, `on_cancel` handlers, verified `User.before_save` role synchronization and peer-issuance callables, and independently read the isolated MariaDB baseline via `START TRANSACTION READ ONLY` then rollback. No `frappe.init()`, `frappe.connect()`, real site hook dispatch, installed-site app-hook cache, write workflow, permission ownership, concurrency, Stock Entry or SLE/GL tests were attempted. Operator's passing output is evidence of process-only source-import feasibility **not** running-site integration or deployment. GitHub connector separately rechecked feature SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` and base SHA `806fa23516490ec7beefcff03a1baa09d722120e`; draft PR #7 remains open/unmerged.

**Next scoped proposal, not yet approved:** design and operator-review a **single controlled, unsubmitted Withdrawal Slip** on `ccpc-integration2.localhost`, with stockroom fixture A as authenticated creator/Prepared By and independent B as reviewer, using the existing synthetic `CCPC-INT-TEST-CONSUMABLE-001` requested quantity 1 Nos but with **no Stock Entry or inventory posting**. Follow site-approved `Draft → Approved → Stockroom Review` workflow through true user sessions, then test document ownership/authorization and same-person nonissue **without posting**. Verify source/hook bindings when initializing only the isolated site in a fresh worker, potential Redis/cache side effects and rollback/cleanup semantics, and preserve original 10 Nos / PHP 1,000 Bin. Request distinct **explicit user authorization** before any Slip/document workflow writes; inventory posting and concurrency/ledger tests are separate future gates. The reviewed GitHub JSON confirms mandatory `requestor`, `approving_supervisor` (automatically set from user), `required_by`, `source_warehouse`, `company`, `department`, `physical_location`, `purpose`, `requesting_company`, plus child `item_code`, `requested_qty`. Plan must use site-verified synthetic Company TISS, Department Operations - TREQ, warehouse Stores - TISS, without changing masters or the serving checkout. No PRODUCTION changes.


## Independent post-commit identity database audit PASSED — 2026-10-15

**Operator supplied full terminal output** of approved read-only `ccpc_identity_readonly_audit.sh` with prior expected SHA256 `c0869a38d4abeffbe13fcd35059a114bccc2c8f7a739e6227113fa5bbd31fba5`: `PROTECTED GIT CHECKOUTS: VERIFIED`; `ISOLATED DATABASE: VERIFIED`; each of the three committed users independently read back with exact assigned roles; `BUSINESS AND INVENTORY BASELINE: UNCHANGED`; `DATABASE WRITES: NONE`; `SHARED DEVELOPMENT AND FEATURE CHECKOUTS: UNCHANGED`; **`INDEPENDENT READ-ONLY IDENTITY AUDIT: PASSED`**. The script used a fresh direct MySQLdb connection to distinct `ccpc-integration2.localhost` DB, a `START TRANSACTION READ ONLY` session, rolled back and closed. Checks: `tabUser` includes exactly the three expected email-named enabled System Users with `send_welcome_email=0`; direct `tabHas Role` returns `Withdrawal Slip Requestor` only for `ccpc-int-requestor@example.test`, and both `Stockroom Personnel` plus `Withdrawal Slip Requestor` for each `ccpc-int-stockroom-a@example.test` and `ccpc-int-stockroom-b@example.test`. `tabWithdrawal Slip=0`, `tabStock Entry=0`, `tabIntercompany Material Billing Batch=0`, `tabStock Ledger Entry=1`, `tabGL Entry=2`; synthetic Bin `CCPC-INT-TEST-CONSUMABLE-001`/`Stores - TISS` unchanged at **10 Nos, PHP1,000**. Shared protected checkout and pinned detached feature checkout again passed guards before and after; no app files changed. This independent post-commit read removes the uncertainty of relying solely on the creation command's commit output.

**Next gate:** read-only pinned-feature source plus Frappe isolated-site import/hook isolation checks in a **short-lived non-serving process**, never changing the shared checkout, workers, DB content or PRODUCTION. Feature `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` remains draft/unmerged PR #7; `development.localhost` is separately served from base SHA `806fa23516490ec7beefcff03a1baa09d722120e`. Do not attempt live workflow/Withdrawal Slip writes, Stock Entry posting, concurrency, migrations or restores without separate scope and approval. A site-free import proof alone is not a live runtime hook or ledger validation.


## Three isolated fictional test Users COMMITTED; permission tests PASSED — 2026-10-14

**Operator returned stdout from the approved checksum-verified v2 guarded script**, `ccpc_isolated_user_creation_guarded_v2.sh`, SHA256 `889f68a25d09bfecc35bb8124d4d7ba1a5d7e6db5ce11005ae71084ca5d4d328`. Output includes `GIT AND RECOVERY GUARDS: PASSED`, `TARGET USER ABSENCE: VERIFIED`, `ISOLATED SITE AND BASELINE: VERIFIED`, `ROLE AND HOOK AVAILABILITY: VERIFIED`, all three `CREATED IN TRANSACTION:` lines, `ALL THREE USER FIXTURES AND PERMISSIONS: VALIDATED`, **`ISOLATED USER CREATION: COMMITTED`**, `SUPPRESSED WELCOME EMAILS AND CONTACT JOBS: VERIFIED`, `SHARED DEVELOPMENT AND FEATURE SOURCE: UNCHANGED`, `NO WITHDRAWAL SLIPS OR STOCK/GL POSTINGS: VERIFIED`, and **`ISOLATED IDENTITY TEST STAGE: PASSED`**. No exception was reported. This confirms a successful *operator-reported persistent User transaction*, unlike the earlier rolled-back v1 attempt.

**Committed test accounts and verified assigned-role sets on `ccpc-integration2.localhost` only:**
- `ccpc-int-requestor@example.test`: exactly `Withdrawal Slip Requestor`.
- `ccpc-int-stockroom-a@example.test`: exactly `Stockroom Personnel` and auto-granted `Withdrawal Slip Requestor`.
- `ccpc-int-stockroom-b@example.test`: exactly `Stockroom Personnel` and auto-granted `Withdrawal Slip Requestor`.

Printed `frappe.get_roles` includes framework-derived `All`, `Desk User`, `Guest` in addition to assigned roles. These entries are effective roles, **not** an Administrator login or extra assigned System Manager role. The guarded script independently compared each User document's actual assigned-role set against the exact expected roles, denied unexpected privileged `System Manager`, `Stock Manager`, `Stock User`, `Accounts Manager`, `Accounts User`, and called installed `frappe.has_permission(doctype, ptype, user=address)` to verify Withdrawal Slip `create` for all, Withdrawal Slip `write` for Stockroom A/B, and **no general Stock Entry `create`, `submit` or `cancel` for any**. It verified `enabled=1`, `user_type=System User`, `send_welcome_email=0`; suppressed three specific User Contact enqueue jobs; patched email-sending APIs to fail closed; checked the Email Queue count unchanged. Actual User creation runs the shared app's role-sync hook, which is GitHub-verified unchanged on base and feature branches; feature source was not deployed. Normal User creation may create notification/share metadata and cache effects; do not claim only three raw database rows were inserted.

**Integrity and remaining gates:** This stage did not create or submit Withdrawal Slips, Stock Entries, SLE/GL, intercompany documents, or inventory adjustments; existing business baseline remained unchanged as tested before commit. The script's site identity guard checked the isolated DB differs from persistent `development.localhost`; shared checkout remained at base SHA `806fa23516490ec7beefcff03a1baa09d722120e` with protected `AGENTS.md`, non-serving feature worktree at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`. Current GitHub draft PR #7 remains unmerged. **Do not run either account-creation script again.** Separately read back committed users under a fresh read-only transaction if independent post-commit verification is desired. Tests proved role/doctype-level checks, **not** real per-document `if_owner` restrictions, workflow transitions, independent-person posting denial, concurrency, SLE/GL, or rollback safety. Before creating a real Withdrawal Slip, decide test-site source isolation/import of pinned feature, fixture fields and write scope and obtain **separate explicit owner approval**. Do not post inventory, change shared DEVELOPMENT or touch PRODUCTION.


## Authorized three-User creation attempt ROLLED BACK on Frappe API mismatch — 2026-10-14

**Operator-supplied stdout from the approved guarded Docker script** (`ccpc_isolated_user_creation_guarded.sh`, SHA256 `2045e1ca68683d42be239373690d649cf3849c8f6f6f1adc5197a8395fba2259`) reports `GIT AND RECOVERY GUARDS: PASSED`, `ISOLATED SITE AND BASELINE: VERIFIED`, `ROLE AND HOOK AVAILABILITY: VERIFIED`, and three `CREATED IN TRANSACTION:` lines for `ccpc-int-requestor@example.test`, `ccpc-int-stockroom-a@example.test`, `ccpc-int-stockroom-b@example.test`. The script next attempted permission checking and raised **`TypeError has_permission() got an unexpected keyword argument 'print_logs'`**. Its exception handler reported **`USER CREATION TRANSACTION: ROLLED BACK`** and returned nonzero. The success/commit lines were **not** printed. Therefore **User creation and permission verification are NOT confirmed complete**; no claim that durable records exist or do not exist until a subsequent site verification. No Slip/Stock Entry/SLE/GL postings were in the operation.

**Root cause verified against the exact uploaded shell script:** the `permitted()` helper called `frappe.has_permission(doctype, ptype, user=address, print_logs=False)`, but the installed application's exposed `frappe.has_permission` does not accept `print_logs` (regardless of upstream documented versions). Only this optional keyword needs removal, retaining real user-scoped permission checks.

**Reviewed remediation script (local artifact, not server-executed):** `ccpc_isolated_user_creation_guarded_v2.sh` SHA256 `889f68a25d09bfecc35bb8124d4d7ba1a5d7e6db5ce11005ae71084ca5d4d328`. Exact diff: remove only `print_logs=False` from permission check and print `TARGET USER ABSENCE: VERIFIED` after fail-closed presence audit. Shell syntax and embedded Python compile checks passed; runtime result is **PENDING**. Preserve all pre-existing Git/site/backup guards, explicit transactional rollback, welcome-email/Contact-job prevention, no business transaction creation. Do not rerun v1. If v2 finds any of the three Users already present, it stops before inserting; investigate instead of overwriting. Verify output before marking identity phase completed. Frappe cache side effects can occur independently of SQL rollback; no deletion or repair automatically authorized.


## Owner authorizes exactly three isolated fictional test Users — 2026-10-14

Owner explicitly replied **"I authorized"** to create exactly the three previously named fictional Frappe System Users **in the isolated DEVELOPMENT site `ccpc-integration2.localhost` only** and verify roles/permissions, with no welcome emails, real employee data, Withdrawal Slips, Stock Entries, SLE/GL or any other business transactions. Names and initial roles: `ccpc-int-requestor@example.test` -> `Withdrawal Slip Requestor`; `ccpc-int-stockroom-a@example.test` -> `Stockroom Personnel`; `ccpc-int-stockroom-b@example.test` -> `Stockroom Personnel`. Existing `User.before_save` hook is expected (but not yet proven under live User insertion) to grant the two Stockroom accounts `Withdrawal Slip Requestor` where present. Actual effective `Stock Entry` create/submit must remain denied. This **does authorize narrowly scoped User/role-related database writes** in that single test site; it does **not** authorize feature deployment/switch, other DEV site writes, fixture masters, workflow transitions, inventory/accounting posting, migration, merge, restores/cleanup, or PRODUCTION changes.

**Reviewed Frappe v16 creation behavior:** `User.after_insert` creates notification settings; `User.on_update` can enqueue Contact creation and send welcome mail through `send_password_notification`; a guarded operator-run plan must set `send_welcome_email=0`, per-document `no_welcome_mail`, block direct mail and suppress only the identified Contact-creation enqueue (reject unanticipated jobs). Frappe's normal role/permission validation and CCPC `User.before_save` hook must execute; no extra roles should be created or assigned. Before any insert, verify isolated vs persistent DB identity, protected Git commits/status, four recovery checkpoint files, exact baseline counts and 10 Nos / PHP1000 Bin, role availability, and all three User names absent. Use an explicit DB transaction, rollback on any exception, and commit only if three target users and effective role/permission assertions pass. Code review is not execution evidence: **user-creation result pending operator output**. A DB commit can create legitimate ancillary User/notification metadata and Redis cache effects; avoid claiming only three DB rows change or that rollback reverses all out-of-DB side effects.

**Authoritative app feature** still GitHub commit `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, draft unmerged PR #7; shared review base `806fa23516490ec7beefcff03a1baa09d722120e`; prior site-free 65/65 and read-only preflight both passed. Once User stage output is verified, report actual roles/DocPerm and whether any limits surfaced; request separate scope before saving Withdrawal Slips or posting real stock.


## Isolated DEVELOPMENT readiness preflight PASSED (read-only) — 2026-10-14

**Owner-provided guarded Ubuntu/Docker stdout** for the authorized read-only integration readiness check reports: `GIT CHECKOUTS: VERIFIED`; `ISOLATED DATABASE IDENTITY: VERIFIED`; `RECOVERY CHECKPOINT: 4 NONEMPTY ARTIFACTS`; checkpoint filesystem **686.44 GiB available**; `READ-ONLY DATABASE BASELINE: VERIFIED`; `SHARED DEVELOPMENT: UNCHANGED`; `ISOLATED FEATURE: UNCHANGED`; `DATABASE WRITES: NONE`; `READ-ONLY INTEGRATION PREFLIGHT: PASSED`. The guarded command used a `START TRANSACTION READ ONLY` MariaDB connection to site `ccpc-integration2.localhost`, verified its DB name differed from persistent `development.localhost`, then rolled back/closed the connection. Git verified shared `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e` with only protected `?? AGENTS.md`, and detached non-serving checkout at feature `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, both unchanged.

**Verified operator-reported isolated DB baseline**: `tabWithdrawal Slip=0`, `tabStock Entry=0`, `tabIntercompany Material Billing Batch=0`, `tabStock Ledger Entry=1`, `tabGL Entry=2`; synthetic `CCPC-INT-TEST-CONSUMABLE-001` at `Stores - TISS` has **10 Nos, PHP 1,000 stock value**. Four nonempty timestamped recovery checkpoint artifacts were found, but **not restored or independently hash-revalidated in this run**; existence/nonzero bytes do not prove recovery. The above is reported terminal evidence and verified GitHub code/branch state, **not** an actual live accounting/inventory integration result.

**GitHub source and permission review for next gate**: existing `User.before_save` role-sync helper conditionally auto-adds `Withdrawal Slip Requestor` to `Stockroom Personnel` System Users when the Role exists; the prior isolated read-only role audit found it exists and two other conditional requestor roles absent. Peer-issue guard requires a different authenticated Stockroom issuer (not Guest/Administrator) and matches saved `owner` and `approving_supervisor`; actual effective permissions remain unverified.

**Proposed next phase — NOT YET AUTHORIZED**: create precisely three synthetic, non-deliverable `.test` System User identities **only in `ccpc-integration2.localhost`**, namely one Requestor/preparer with `Withdrawal Slip Requestor`, plus independent Stockroom A and Stockroom B initially assigned `Stockroom Personnel` and expected to acquire `Withdrawal Slip Requestor` via reviewed hook. Verify actual resulting roles/permissions, ownership restrictions, independent-person rule, and absence of general Stock Entry create/submit rights. No welcome emails, real staff or customer data, privileged Stock Manager/System Manager roles, stock postings, database migrations, or worktree switches. Exact user creation/permission test procedure and explicit separate operator approval are required first. No persistent test-user records have been created; no real Frappe permission or transaction tests have run. A future one-unit Issue and concurrency/rollback tests remain separate further gates.


## Owner approves read-only isolated integration readiness review — 2026-10-14

Owner replied **"Approved"** immediately after the assistant proposed proceeding toward controlled DEVELOPMENT integration testing, beginning with **review of isolated site and recovery safeguards**, and explicitly stated that **creating users, database changes, or posting actual Material Issues would require separate approval**. Interpret the current approval as authorization for the **read-only readiness/preflight phase**, not blanket consent to later persistent site write operations. The source remains feature SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, draft PR #7; 65/65 mock regression cases passed on isolated source. Readiness output and real integration results are **pending**.

Next action: one guarded operator-run, read-only snapshot/git/site-configuration and isolated MySQL `START TRANSACTION READ ONLY` baseline audit on `ccpc-integration2.localhost`, without importing site modules, editing shared DEVELOPMENT, creating users, posting inventory or changing PRODUCTION. If fixture/baseline/backup or source checks differ, **STOP**, preserve state and investigate. After audit, present exact synthetic accounts, role assignments, transactions and recovery boundary for **separate owner approval** before any site writing or ledger integration tests. Do not equate a backup's existence with successful restore testing.


## Site-free peer-issuance regression retry PASSED: 65/65 — 2026-10-14

**Operator-supplied direct DEVELOPMENT terminal output (2026-10-14)** confirms the guarded synthetic-Frappe-context retry of the *same 65 mock-based tests* on detached isolated checkout `/workspace/development/frappe-bench/.ccpc-peer-issuance-tests-2f846a75` at pinned application feature SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`: `TESTS DISCOVERED: 65`; `Ran 65 tests in 0.053s`; `OK`; `TESTS RUN: 65`; `FAILURES: 0`; `ERRORS: 0`; `SKIPPED: 0`; `SITE-FREE REGRESSION RESULT: PASSED`. The earlier run's 31 errors were harness context-binding errors, not test assertion failures. The retry populated synthetic `frappe.local.session`, `db`, `flags`, `conf`, and `lang`; the synthetic database object denied unmocked method calls, while `frappe.init` and `frappe.connect` were forbidden by the guarded runner.

**Integrity and boundaries:** Output explicitly stated `SHARED DEVELOPMENT: PROTECTED`, `ISOLATED FEATURE: VERIFIED`, `SHARED DEVELOPMENT: UNCHANGED`, `ISOLATED FEATURE: UNCHANGED`, and `SITE INITIALIZATION: NOT PERFORMED`. All three modules came from the pinned isolated checkout. Existing Frappe logs reported `Unable to load translations` because `frappe.cache` was absent in the site-free process; these messages did not cause a unittest error or failure. The output is operator-reported runtime evidence, not proof of persistent site audit. The GitHub connector separately verified the feature branch and draft unmerged PR #7 still at `2f846a75...` and PR base `806fa235...` when recording this milestone.

**Scope of result:** **Mocked/site-free regressions passed; real integration remains UNTESTED.** These tests do not prove actual effective user roles/DocPerm, live MariaDB row locking/concurrent issue prevention, Stock Entry/SLE/GL posting, rollback semantics, or inventory reconciliation. No shared DEVELOPMENT source switch/pull, site/DB operations, test user creation, stock/GL posting, migration, merge, or PRODUCTION operation is authorized by this result. The detached source is not deployed code.

**Next development gate:** Perform a review of the remaining integration and permission/transaction test plan against the verified feature source; request **separate explicit operator authorization** before any persistent DEVELOPMENT site initialization/database fixtures, real users, controlled posting, or concurrency tests. Protect the shared checkout, `AGENTS.md`, site records, recovery snapshots, and PRODUCTION. Preserve the feature branch/draft PR until those checks and release review complete.


## First site-free 65-test run failed: unbound Frappe local proxies, no site/DB operations — 2026-10-14

**Owner supplied actual operator stdout/stderr via big-paste attachment (976 lines), 2026-10-14, after executing approved guarded site-free test runner** on detached checkout `/workspace/development/frappe-bench/.ccpc-peer-issuance-tests-2f846a75`, feature commit `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`. Output: `SHARED DEVELOPMENT APP: PROTECTED`; `ISOLATED FEATURE COMMIT: VERIFIED`; all three test modules imported from isolated source; `TESTS DISCOVERED: 65`; `Ran 65 tests in 0.053s`; `FAILED (errors=31)`; `FAILURES: 0`; `ERRORS: 31`; `SKIPPED: 0`; `SHARED DEVELOPMENT APP: UNCHANGED`; `ISOLATED FEATURE CHECKOUT: UNCHANGED`; `SITE INITIALIZATION: NOT PERFORMED`; `SITE-FREE REGRESSION RESULT: FAILED`. Thus **34 tests reported ok** and 31 tests errored without testing their assertions; this is **NOT** a passing regression run and does not establish the new rule's behavior. Output also contained translation log noise `Unable to load translations`, due to no site/cache, while some affected tests still reported `ok`.

**Root cause supported by tracebacks:** Every new peer-issuer test errored at `test_withdrawal_peer_issuance.py:setUp` `patch(f"{MODULE}.frappe.session", create=True).start()`, with `RuntimeError: object is not bound` from `frappe.utils.local.LocalProxy._get_current_object`; several existing tests errored patching `frappe.db.sql`, `frappe.session` or similar unbound context-local objects in the site-free process. Frappe v16's installed `frappe.local` uses `ContextVar` and `LocalProxy` that require a backing binding even when real site initialization is forbidden. Source confirmed against upstream `frappe/frappe` `version-16:frappe/utils/local.py` and `frappe/__init__.py` (the developer's actual source may differ; verify next operator run). Nothing in this output yet proves a security-code regression; further test failures may emerge once mocking is corrected.

**Next safe operator step (within already-approved site-free testing scope):** Repeat the **same 65 tests** in a fresh short-lived Python process only after establishing **synthetic** context-local bindings: `frappe.local.session = frappe._dict(user="Guest")`, `frappe.local.db = MagicMock(...)` with all SQL/transaction methods hard-denied unless the tests mock them, and `frappe.local.flags = frappe._dict()` (and simple `lang/conf` defaults if needed); assert `frappe.local.initialised` false and never call `frappe.init()`, `frappe.connect()` or a bench site command. Preserve exact shared checkout/feature worktree SHA/status pre- and post-run; do not edit isolated source or protected shared app, create test users, connect to DB, write transactions, cleanup worktrees, or change PRODUCTION. Report test totals and first new failures if any. This is a **test harness-only retry**, not permission for database integration, schema changes or migrations. Test outcome pending operator command.

## Isolated site-free source checkout created; 65 test cases to run — 2026-10-14

**Operator-confirmed execution after separate authorization:** User ran the previously prepared guarded Docker command and returned: `SHARED DEVELOPMENT APP: PROTECTED`, `GITHUB ORIGIN: VERIFIED`, `ISOLATED DESTINATION: AVAILABLE`, `PINNED FEATURE COMMIT: VERIFIED`, `ISOLATED FEATURE CHECKOUT: CREATED`, `ISOLATED COMMIT: 2f846a7`, `SHARED APPLICATION: UNCHANGED`, `SITE INITIALIZATION: NOT PERFORMED`, `DATABASE ACCESS: NOT PERFORMED`, `CHECKOUT PREPARATION: PASSED`. Exact non-serving checkout path `/workspace/development/frappe-bench/.ccpc-peer-issuance-tests-2f846a75`. The guarded command independently checked the shared app remains on `review/intercompany-approval-failure-tests` SHA `806fa23516490ec7beefcff03a1baa09d722120e` with only preserved `?? AGENTS.md`; verified `origin` is `github.com/ccpcerp/ccpcerp`; fetched feature branch exact SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` and added a clean detached Git worktree outside `bench/apps`. No changes to persistent site, database, warehouse, Git branch in shared worktree or PRODUCTION. Git worktree administrative metadata and new isolated files were created under owner's specific checkout permission; this does not imply that tests have passed.

**Current next authorized action:** Run **site-free, mock-only Frappe Python/unittest** from the new detached checkout and stop if its pinned Git SHA/source path or protected shared worktree differs. Target three GitHub-verified modules: `ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_peer_issuance` (**18 tests**, blob `46e502df203ad87cfe8bab37c37813f45ec8d66a`), `ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_issue_safety` (**12 tests**, blob `56a41b644368b7b8d852658355ca59fc1b1e3305`), and `ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_slip` (**35 tests**, blob `3295d90c6134653a0bf589c530a4b0f51c6224e2`): **65** test methods total. Enforce fresh-process origin checks for every test and feature source module, no `frappe.init` or `frappe.connect`, no site or DB, `PYTHONDONTWRITEBYTECODE=1`, `FRAPPE_STREAM_LOGGING=1`. Do not mistake mock tests for effective user/ledger/concurrency integration. Developer host has no direct connected terminal; operator runs one guarded Docker command and pastes output. If tests fail, inspect and change reviewed code in GitHub first; do not mutate the shared checkout.

## Owner authorizes isolated non-serving checkout for site-free regressions — 2026-10-14

**New explicit owner authorization:** In reply to a direct request on 2026-10-14, user stated **"I authorized"** creating a **temporary isolated source checkout in DEVELOPMENT** solely for **site-free Python/Frappe regression tests** at the verified feature commit. This **does not** authorize user creation, site initialization/database access, stock/GL posting, shared live app checkout branch changes, shared `AGENTS.md` alteration, migrations, restarts or PRODUCTION. GitHub reverified app branch `feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, review base `806fa23516490ec7beefcff03a1baa09d722120e`, PR #7 draft unmerged; new peer test module exists with 18 mocked test definitions.

**Execution access:** Current ChatGPT tool connections support GitHub source operations but **not direct Docker/SSH terminal execution in the remote DEVELOPMENT host**. Owner must run a guarded Docker terminal command and return its output. Next operator step is to verify active shared app still on review/base SHA with only protected untracked `AGENTS.md`, remote Git URL matches official app, and target worktree path is absent. If so, fetch the named feature branch into Git object storage (verify fetched commit equals exact authorized SHA) and create a **detached, non-serving worktree outside bench/apps**, e.g. `/workspace/development/frappe-bench/.ccpc-peer-issuance-tests-2f846a75`. Verify new worktree HEAD/clean tracked state and unchanged shared checkout, without importing Frappe yet. No removal, cleanup or reset in this step. Next operator interaction after verified creation: execute short-lived Python with `PYTHONDONTWRITEBYTECODE=1`, source package pinned via `PYTHONPATH`/sys.path and explicit module-origin check, then focused `unittest` mocked tests **without** `frappe.init`, `frappe.connect` or any bench site command. Stop on failures and inspect output; do not change shared DEV. GitHub documentation records authorization, **not evidence worktree creation or test passing**.

## Peer-issuer guard is now committed to GitHub feature branch; no site testing or deployment — 2026-10-14

**Authorization from owner:** The owner explicitly replied **"Approved, Continue"** to the final peer-issuer offline V3 candidate on 2026-10-14, authorizing reviewed code/test commits in GitHub while retaining explicit **NO DEVELOPMENT/PRODUCTION modification, user creation, Material Issue posting, database migrations, or production deploy** restrictions. A fresh GitHub check showed previous app head `85d129e193b32cc229de2e30145359bb3979c257` and draft PR #7, review base `review/intercompany-approval-failure-tests`. Prior GitHub application write restrictions no longer blocked this turn: **connected GitHub `update_file` / `create_file` actions successfully committed exact reviewed code/test edits**, without a workaround or operations on DEVELOPMENT. The old detached checkout (last proven at SHA `85d129e`) was not updated and must not be mistaken as the new tested code.

**New authoritative feature head: `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`** on `ccpcerp/ccpcerp:feature/withdrawal-material-issue-safety`, draft unmerged PR [#7](https://github.com/ccpcerp/ccpcerp/pull/7), base `review/intercompany-approval-failure-tests`. Six **verified app GitHub commits** in chronological order:

- `359d0bb3d0f57c61a010191f3b26901e17637f86`: extend parent locking read to `owner, approving_supervisor`, shared `_assert_independent_issuer` guard, authenticated independent Stockroom role; reject Guest and Administrator; locked identity stale-check and `Stock Entry.before_submit` backstop; both POST endpoints pass common guarded `_get_issuable_slip`.
- `54ef3d42ced990f0045b59b19a820eb7313afe5d`: Withdrawal Slip controller rejects saved owner identity edits alongside existing Prepared By immutability.
- `ac2bba65d34f18cc3b4cf4161ef7c18f1ff092e8`: adapt stock-safety mocked lock query and pre-submit test.
- `c1f21dbac83f8fda18cb95cf0c2ff55f86737247`: adapt two existing Withdrawal Slip mocked pre-submit cases.
- `451b78aba11d7e126015c368eb3cf6b6cc4f28e0`: create site-free mock test module `test_withdrawal_peer_issuance.py` with 15 tests.
- `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`: add three more positive peer-through-endpoint/before-submit mocked test paths, making **18 tests** total.

**Verified affected files by GitHub compare from former head to new head (six commits, exactly five paths):** `ccpcerp/ccpc_erp/withdrawal_slip_stock.py`, `ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.py`, `ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_issue_safety.py`, `ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_slip.py`, `ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_peer_issuance.py`. Verified draft PR head equals new feature tip and unmerged. The offline V3 patch was **not applied to GitHub**; it is now superseded by authoritative GitHub commits. Its hunk numbering did not apply cleanly against the complete original source in two places; the committed exact-source updates were checked separately. No schema/custom-field changes, stock records or role/permission mutations.

**Test honesty:** Source, commit, comparison, hooked guard and 18 test definitions verified statically; **new mocked tests were NOT executed on real Frappe**. The previous 47/47 site-free mock result pertains to the old baseline, not new commit. GitHub returned **zero workflow runs**, so there is no CI pass or Frappe runtime result. No live user-effective DocPerm, MariaDB concurrency, inventory Bin/SLE/GL posting, rollback, or restore drill since change. Local ChatGPT sandbox has no Frappe runtime and shell GitHub network is unavailable. **Not production-ready.**

**Documentation updates in same milestone:** [WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md](WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md) reflects committed feature and gates, docs commit `660fae9f8f3a6c406dedde5e0d75d33b6562764f`; [WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md](WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md) reflects committed-but-untested feature at docs commit `9a0cc1458ddd79ea88ab430c74d208583fc7a508`. The 11 protected isolated site recovery snapshot sets / 44 verified backup files remain the last known untouched baseline; no restore drill.

**Next step, read-only operator gate:** Independently recheck shared DEVELOPMENT checkout branch/commit/status (`review/intercompany-approval-failure-tests`, `806fa235...`, protected `?? AGENTS.md`), detached old worktree at old `85d129e`, isolated site untouched, before asking **separate owner authorization** to create/fetch a new *isolated, non-serving* source checkout at `2f846a75...` for actual site-free Frappe Python mock testing. Do **not** switch/pull the shared DEVELOPMENT checkout, alter live DEVELOPMENT, create test users, material issue, change PROD or mislabel mock tests as ledger integration tests. If isolated source tests later pass, further permission is needed for DB fixtures and issue/GL verification. Owner approved GitHub code commits only in this step.

## Peer-issuer patch v3 supersedes v2: explicitly bar Administrator; offline only — 2026-10-14

**Additional review under owner's existing GitHub-only code authorization:** Since `frappe.get_roles("Administrator")` can represent broad effective roles in some Frappe contexts, v2's sole check for `Stockroom Personnel` may not independently exclude the built-in Administrator account. V3 offline review candidate `ccpc-peer-issuer-review-v3.patch` explicitly denies `Administrator` and `Guest`, also denies System Manager **without** Stockroom role, and requires the issuer to be different from both consistent authenticated Slip creator/Prepared By identities. No general Administrator bypass to linked Slip issuance is approved. A different real Stockroom peer may issue. Direct unlinked Stock Entry privileges are outside the scoped guard, and real administrator permission semantics require live verification before release.

**V3 patch details:** Local sandbox `/mnt/data/ccpc-peer-issuer-review-v3.patch`, **13,214 bytes**, SHA256 `de0ccbc8288bfed3ec738de56a3781223e89f9e74f22326f6bc43aef64e31725`. Five files, 15 new mocked test definitions, `git apply --numstat` and `--stat` valid. Synthetic old-side hunk fragment `git apply --check` and `git apply` both passed; AST syntax parse of inserted helper and test module passed; **12 isolated executable stubbed guard behavior assertions passed**. This is not a full repository checkout application, actual Frappe unit-test execution, database, stock/GL ledger, concurrency or rollback testing. V3 **supersedes V1/V2** for future manual review, with all versions still **uncommitted**. The patch artifact is available in current conversation only, not automatically in GitHub.

**Current GitHub:** code branch `feature/withdrawal-material-issue-safety` reverified at `85d129e193b32cc229de2e30145359bb3979c257`, PR #7 still draft/unmerged, source blob `73598fae5873c393af08e3ae9d10f2775114bc79`. Previous app source `update_file` attempts were blocked by safety checks; do not bypass that block or claim code was published. Docs only: design note updated at `ea11990c7a03d895533d8467ebc0f57d8dd9f6c1`. No test user creation, DB/migrations, shared DEVELOPMENT checkout changes, material issues, stock postings or PRODUCTION modifications. Next implementation gate: a **permitted** GitHub source update followed by full Frappe mocked regression tests; next site gate needs separate owner approval.

## Peer-issuer patch v2 offline review: require Stockroom role; GitHub app blocked — 2026-10-14

**User requested continued progress**, without authorizing DEVELOPMENT/PRODUCTION changes. GitHub reverified application feature `feature/withdrawal-material-issue-safety` still at `85d129e193b32cc229de2e30145359bb3979c257`, draft unmerged PR #7, app file `withdrawal_slip_stock.py` unchanged blob `73598fae5873c393af08e3ae9d10f2775114bc79`, prior mocked test file unchanged blob `89c162cd2a5985b0cb5874f76e3de982fe40210c`; connected workflow `GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md` reviewed. Temporary container could not reach github.com via shell DNS; no full repository clone or Frappe Python package in local sandbox. Connected GitHub reads remain available. Previous connected GitHub **application source write was blocked**; no attempt to bypass that safety restriction with an alternate write tool and **no application code commit**.

**New code-review finding:** current `_require_stockroom_user()` explicitly allows Administrator and System Manager as well as Stockroom Personnel. Previous peer guard checked only that caller differs from document's preparer; a distinct privileged non-Stockroom account could pass it. Revised offline candidate `ccpc-peer-issuer-review-v2.patch` adds `"Stockroom Personnel" in frappe.get_roles(issuer)` to its shared peer issuer helper, preserving same-preparer denial. Offline review patch v2 has **5 paths**, 14 proposed new mocked tests, is **12,950 bytes**, SHA256 `2a78de7233985638fc5f9dc4db87f16c38197992189e66aba518c337f13c35cf`; patch generated from previous local v1, provided to user in conversation, **not** committed. It is not a permission to apply to shared checkout.

**Local verification:** `git apply --numstat` succeeded; `git apply --check` and `git apply` succeeded against synthesized exact old-side **hunk fragments**, not complete authoritative repository files. Added helper and test module passed Python AST syntax parsing. **11 executable isolated helper checks passed** (peer permitted, same originator denied, supervisor-proxy path allowed, missing/mismatched identities denied, Guest, unset user, System Manager without Stockroom role, and Administrator with no matching Stockroom role rejected). These mocked/stub checks are **not** the Frappe unit-test suite, nor integration, permission, ledger, rollback or concurrency verification; the original mocked suite has **not been rerun**.

**Remaining security review:** Depending on Frappe's Administrator effective role semantics, simply querying `frappe.get_roles("Administrator")` may reveal all roles; a future implementation may need an **explicit Administrator disallow** except a separately documented emergency process. Review real effective role behavior and any System Manager accounts additionally assigned Stockroom Personnel. General unlinked Stock Entries by highly privileged users remain outside Slip-bound peer guard; do not overstate it as global stock-posting separation. The source remains **NOT IMPLEMENTED**, feature PR unchanged, no test users or stock/GL postings and no DEVELOPMENT/PRODUCTION modifications. The authoritative peer-issuer policy documentation was updated on docs branch at commit `deff3ea0fd6d430243e88142661081f25463c48c` to capture role-scope finding. Obtain supported authorized app GitHub commit and real Frappe tests before recommending any deployment.

## Offline peer-issuer code diff and mock regression candidate prepared; no GitHub app commit — 2026-10-14

**User continuation** after the safety-blocked connector app write: completed a **local-only draft diff** in the conversation sandbox, named `ccpc-peer-issuer-review.patch`, 12,197 bytes, final SHA256 `84fcc695d975040f34d5ae9c488899811f80194c8d4f9988493d78744a74903d`. **This is NOT committed to GitHub** and is **NOT accessible automatically in future conversations**; the user can access its attachment in the current conversation or reattach it later. This draft **must not be applied to the shared DEVELOPMENT bench**. Do not treat a download link as a GitHub code commit or release artifact.

**Patch content (candidate, review required):** five paths: existing `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` extends locked Slip SELECT by `owner, approving_supervisor`, adds a shared account-ID peer issuer guard (reject owner/Prepared By missing/mismatch, current issuer matching preparer, and unauthenticated session), compares added locked fields to loaded Slip to fail on stale reads, enforces in common issuing Slip endpoint (covering both POST issue and legacy POST draft) and in `Stock Entry.before_submit`; existing Withdrawal Slip controller adds standard `owner` immutability check alongside existing Prepared By immutability; two existing unit-test files get focused mock adaptations; a new `test_withdrawal_peer_issuance.py` adds **13 site-free mocked test cases** spanning self-denial, peer and supervisor-proxy permitted checks, forged typed fields, ambiguous or missing originator, Guest/Admin, legacy draft, before-submit and stale-read guards. Existing statuses, role gates, existing duplicate/ledger checks are intended to remain intact. The actual `requestor` and `received_by` names remain untrusted text; no new DB field.

**Offline verification completed (not live test):** valid unified patch with `git apply --numstat`; **`git apply --check` and `git apply` on synthesized fragment files representing the patch's exact old-side hunks passed**, plus Python AST syntax parse on new tests and guard function, and **7 pure mocked/stubbed guard behavior smoke checks passed**. This checks diff structure and guard logic only: **NOT** verified against a full current application checkout, and **NOT** a successful `unittest` run under Frappe. Existing tests have **not** been rerun; no live database/stock ledger/GL/rollback/concurrency tests run. Require exact GitHub base ref and test suite verification before app commit or deployment. All work was in ephemeral local `/mnt/data`; no site initialization or DB connection.

**GitHub safety and boundaries:** Previous tool calls to update the application source on `feature/withdrawal-material-issue-safety` were blocked by safety checks. **No attempt to circumvent the block**; no application GitHub code write or application commit. Latest reverified feature head and draft PR #7 remain `85d129e193b32cc229de2e30145359bb3979c257`, unchanged. Only this handoff document update in the docs repo is permitted. Owner has approved code work in GitHub but **not** creation of site users, stock/GL posting, shared DEVELOPMENT changes, migrations, merge, or PRODUCTION deployment. Next phase requires an allowed, explicitly authorized GitHub code-write route plus proper unit tests and code review; after success, separately request owner approval for any isolated DEVELOPMENT integration testing and protect the shared checkout and `AGENTS.md`.

## Peer-issuer GitHub implementation approved but connector code write blocked — 2026-10-14

**Owner authorization:** Owner answered **"Approved"** on 2026-10-14 immediately after a proposal to implement the reviewed server-side peer-issuer safeguard and regression tests **in GitHub**. Interpret as authorization for narrow application source/test changes on `feature/withdrawal-material-issue-safety` only; prior explicit restrictions remain: **no user creation, stock or GL posting, shared DEVELOPMENT checkout changes, migrations, TEST-site record changes, deploy, merge, or PRODUCTION changes**.

**Fresh GitHub re-verification before attempted write:** Feature head `85d129e193b32cc229de2e30145359bb3979c257`, base `review/intercompany-approval-failure-tests` `806fa23516490ec7beefcff03a1baa09d722120e`, draft PR #7 still unmerged. Reviewed full `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` blob `73598fae5873c393af08e3ae9d10f2775114bc79`, focused mocked test blob `89c162cd2a5985b0cb5874f76e3de982fe40210c`, Withdrawal Slip controller blob `8675e5413cf5efea6a17eb1088b1d08f36defe27`. Verified source has parent `SELECT ... FOR UPDATE` covering `status, received_by, company, source_warehouse` only; scoped POST issuer and legacy POST draft endpoints, plus `Stock Entry.validate` and `before_submit`; no same-preparer issuer guard. `owner` is Frappe standard creator identity; `approving_supervisor` is User Link labeled **Prepared By**, set to session user when Slip first validated. `requestor` and `received_by` are unverified display text.

**Implementation review scoped, **NOT EXECUTED****: (1) extend locked parent SELECT to include `owner, approving_supervisor`; (2) shared assertion rejects missing/inconsistent creator/preparer accounts or session issuer matching creator, with no unconditional Administrator override; (3) recheck locked identity against Slip stale snapshot; (4) enforce in common `_get_issuable_slip` for both POST endpoints and `Stock Entry.before_submit` for alternative submit paths; (5) protect saved Slip `owner` and Prepared By immutability; (6) add mocked regression cases: own Slip denied (both endpoints and before_submit) without privileged insertion; peer permitted, supervisor-on-behalf permitted, spoofed typed fields ineffective, missing/mismatched/stale IDs fail closed, and existing duplicate/rollback checks still work. Do not add new User field/schema or trust typed names. This design is in [WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md](WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md) and [WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md](WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md).

**Blocker:** Two calls to the **connected GitHub `update_file` action targeting the feature application source** were blocked with `This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.` The first attempted a consolidated guarded change but did **not** complete; the second attempted a single narrow SELECT-column addition and was also blocked. Treat **all application edits as uncommitted, not implemented**; stop rather than use an alternate route around the refusal. **No code commit/test evidence exists.** No tests rerun. Do not report the safeguarding behavior as live or verified. The documentation-only record and any later owner-directed safe implementation/review path may proceed; preserve the source/head until a supported authorized code-write route is available.

## Confirmed CCPC supervisor-on-behalf practice removes need for new User field in peer-issuer guard — 2026-10-14

**New owner clarification (binding operating assumption for review):** Stockroom workers **never create Withdrawal Slips on behalf of employees in other departments**. All approximately five Stockroom workers **have their own individual ERPNext accounts**. For their own supply consumption they must create their own Withdrawal Slip. **Most ordinary CCPC employees do not have ERPNext accounts**; their **supervisor creates the Withdrawal Slip on their behalf**, recording the actual employee in the existing free-text `requestor` field. The supervisor's authenticated User ID is the Slip's creator/Prepared By, **not** necessarily the person consuming. Any different authorized Stockroom user can issue a supervisor-prepared Slip. On a Stockroom self-request, an **independent Stockroom peer** must issue. Routine manager approval is not required. Shared logins and having supervisors submit Stockroom staff's personal requests as a workaround must be prohibited operationally.

**Design simplification based on this fact, still review-only:** For **preparer-versus-issuer** separation, the existing standard `Withdrawal Slip.owner` and current immutable User Link field `approving_supervisor` (labeled **Prepared By**, assigned on first validation) supply authenticated preparer identity. A new `requestor_user` field, table alteration or migration is **not necessary for this specific control**. Proposed server code should fail closed if either originator ID missing/mismatched/stale, and should reject `frappe.session.user` if equal to saved owner **or** Prepared By, under a single parent-row `FOR UPDATE` read; cover `issue_withdrawal_slip`, legacy `make_material_issue` and `Stock Entry.before_submit` to prevent ordinary alternative submissions. Ensure Frappe server-side originator immutability, direct API protection, normal per-transaction rollbacks and issuer audit field. Do not treat free-text `requestor` or `received_by` as authenticated identities. Supervisor on behalf remains fully allowed. Note that different **preparer** does not prove the typed human requester is a different person; recipient-name verification remains an operational control.

**GitHub-only changes in response:** Revised [WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md](WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md) at docs commit `697718809bae931e5ef2ccb2074d338f4347d15c`; revised [WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md](WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md) at docs commit `d9352cb8e8c7e38dee086573d849216db1de2bc5`. Planned integration fixture now anticipates **two independent Stockroom users** plus Requestor/Supervisor (not yet created). Feature draft PR #7 still unchanged at last-verified `85d129e193b32cc229de2e30145359bb3979c257`. This is **planning/review only** under owner's explicit scope; absolutely no app code, test users, site migrations, stock/GL transactions, shared DEVELOPMENT or PRODUCTION modifications authorized. 11 site backup sets / 44 integrity-checked artifacts remain baseline; no restore drill. Next gate if owner elects to proceed later: separately authorize a reviewed GitHub feature-code change with mock tests before any isolated DEVELOPMENT testing.

## Owner selected Option A peer issuance; design reviewed, app not modified — 2026-10-14

**Approved business policy, not yet implemented:** The owner explicitly selected **Option A** on 2026-10-14: Stockroom personnel (around five people) may request and consume their own office supplies and other operational items, but a **different Stockroom employee** must physically verify/release and post the linked Material Issue. No routine manager approval (manager is frequently unavailable). Same-person requester/issuer must be denied at server side; ordinary requests by employees from other departments continue to be issued by authorized Stockroom personnel. Owner explicitly authorized **GitHub-first planning/review only**, and prohibited any user creation, stock posting, or DEVELOPMENT/PRODUCTION modifications. Do not interpret policy selection as implementation approval.

**New authoritative design document, documentation-only commit:** [WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md](WITHDRAWAL-SLIP-PEER-ISSUANCE-POLICY-AND-DESIGN.md), created on `docs/ccpc-checkpoint-2026-10-10` at commit `879d5621b15379e5da1ae20e713cf3443a1400f2`. Existing [WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md](WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md) cross-linked/updated on docs branch at `f61216c5871d7c2b10b96da3362fb6a890df14b9`.

**Code review, feature draft PR #7 at unchanged `85d129e193b32cc229de2e30145359bb3979c257`:** `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` currently includes two POST endpoints (`issue_withdrawal_slip`, legacy `make_material_issue`), a Withdrawal Slip parent `SELECT ... FOR UPDATE`, and `Stock Entry` validate/before_submit/on_submit/on_cancel hooks; existing code checks Stockroom role, Slip write, state/received-by, duplicate and quantity controls, but has **no current actor != original requester** validation. Workflow allows Requestor's `Draft→Approved` self-approval and Stockroom's `Approved→Stockroom Review`; these remain deliberately available without manager per Option A. Stockroom auto-grants existing `Withdrawal Slip Requestor` role; site lacks `MRS Requestor` and `CCPC Stock Inquiry User` role records.

**Critical identity-model design issue:** `Withdrawal Slip.requestor` is a user-editable `Autocomplete` plain-text field; `received_by` is a `Data` plain-text field. `approving_supervisor` is a User Link actually labeled **Prepared By** and defaults to creator, **not verified separate approver**; standard `owner` identifies doc creator but not necessarily employee consuming when one person prepared a request on behalf of another. Reliable same-person issuer policy requires an authenticated, immutable requestor identity (e.g. reviewed new User Link field or equivalent audit-backed mapping) and a recheck under parent row lock. **Simple owner != issuer** alone is a conservative restriction but can reject legitimate on-behalf requests and does not by itself identify the actual requester. `issued_by` is a server-set User link from Stock Entry's `withdrawal_slip_issued_by`. Future reviewed implementation must enforce peer check in *both* POST issue/draft endpoint and Stock Entry `before_submit`, prohibit identity tampering/alternate APIs, preserve transaction safety and provide regression + real isolated MariaDB/SLE/GL tests. Prohibit automatic legacy backfill from names and any schema change before separate authorization.

**Current verification:** Site-free feature Python imports and hook registrations passed, isolated SQL verified two fictional companies TISS/TREQ, 13 eligible Departments, stock `10 Nos/PHP1000`, 1 issuer leaf Cost Center and expense/adjustment accounts, workflow and DocPerm role inventory; 11 protected site recovery checkpoint sets / 44 intact archives (no restore drill); 47/47 earlier mocked tests passed, **no live user/stock/GL/rollback/concurrency tests**. Shared active DEV checkout remains at most recently verified `review/intercompany-approval-failure-tests` SHA `806fa23516490ec7beefcff03a1baa09d722120e` with untracked `AGENTS.md` preserved. No app code, schema, users, records, GitHub feature branch, PR, DEVELOPMENT, or PRODUCTION changed for this policy decision.

**Next owner decision, not required this turn:** Whether Stockroom clerks regularly *create Slips on behalf of other employees*, because a conservative creator-vs-issuer control would prohibit issuing those too and because identity field design must reflect the actual consumer. The owner has only authorized design review and can decide separately before code development. Do not run server commands or apply source changes without appropriate explicit scope approval.

## Isolated Workflow confirms combined Requestor/Stockroom self-issue risk; owner policy decision next — 2026-10-14

**Operator read-only isolated database Workflow audit PASSED:** `ISOLATED DATABASE: VERIFIED`; `ACTIVE WORKFLOW: CCPC Withdrawal Slip Workflow`; `READ-ONLY WORKFLOW AUDIT: COMPLETED`. Eight states, **all docstatus 0**: Draft (edit Withdrawal Slip Requestor); Approved, Stockroom Review, Fully Issued, Issued with Shortage (edit Stockroom Personnel); Returned for Correction (edit Withdrawal Slip Requestor); Cancelled/Closed (edit System Manager). Four transitions all `allow_self_approval=1`: Draft→Approved via `Approve & Send to Stockroom` by Withdrawal Slip Requestor, **no condition**; Approved→Stockroom Review via `Start Review` by Stockroom Personnel, **no condition**; Stockroom Review→Returned for Correction via `Return for Correction` by Stockroom Personnel, **no condition**; Returned for Correction→Approved via `Re-Approve` by Withdrawal Slip Requestor with `frappe.session.user == doc.approving_supervisor`. Native `tabDocPerm`: Stockroom Personnel (read=1 write=1 create=0 submit=0 if_owner=0); Withdrawal Slip Requestor (read=1 write=1 create=1 submit=0 if_owner=1), both permlevel 0. `tabCustom DocPerm` no matching rows.

**Cross-check with preceding source + role inventory:** On isolated site, Stockroom Personnel and Withdrawal Slip Requestor roles exist; MRS Requestor and CCPC Stock Inquiry User do not. The identical `User.before_save` code on feature and base automatically adds Withdrawal Slip Requestor for a new System User with Stockroom Personnel. The issue endpoint requires Stockroom role, Slip write, Stockroom Review and valid records but has no explicit different-user check. Therefore the configuration and source show a **plausible create→self-approve→Start Review→Material Issue path for the same Stockroom account**; this is a separation-of-duties control risk, **not yet a tested ability or actual exploit** because no enabled non-Administrator test user has been created. All four workflow transitions permit self approval; creator being saved as `approving_supervisor` does not establish independent actual approval. No stock posting, users/roles, development checkout or PRODUCTION changed.

**Owner decision gate next:** Recommend a **strict same-document requester/issuer separation**: Stockroom must not issue a Slip they originated/approved; separately review the automatic role grant. Preserve user's existing Requestor-only Draft→Approved self-approval process unless they approve changing it. Obtain explicit business policy choice before authorizing GitHub security change, fictional users, or posting tests. The detailed integration plan now captures exact Workflow, DocPerm, role/hook intersection (updated docs commit `dfc1b587465fd05ffa1b0fdbdfcbe5f20f151a6c`). 11 snapshots / 44 archives integrity verified, no restore drill, shared DEVELOPMENT checkout & AGENTS.md protected, feature draft PR #7 unmerged. No new server command required for this decision.

## Read-only combined-role audit: stockroom auto-adds existing Requestor role; SoD policy pending — 2026-10-14

**Owner/operator supplied completed site-isolated read-only SQL audit:** `ISOLATED DATABASE: VERIFIED`, `READ-ONLY COMBINED-ROLE AUDIT: COMPLETED`. Existing Role names of four tested: **Stockroom Personnel PRESENT**, **Withdrawal Slip Requestor PRESENT**, **MRS Requestor MISSING**, **CCPC Stock Inquiry User MISSING**. From `tabDocPerm`, Withdrawal Slip / Stockroom Personnel has `read,write`, and Withdrawal Slip / Withdrawal Slip Requestor has `read,write,create`. No matching `tabDocPerm` for Stock Entry, Stock Ledger Entry or GL Entry for these roles; `tabCustom DocPerm` **NO MATCHING PERMISSIONS**. Given exact current `User.before_save` hook from both base and feature GitHub branches, a newly created Stockroom System User would also receive **Withdrawal Slip Requestor** because it exists, but cannot receive the two missing requested role records from that hook. This is conditional source/config behavior; **no enabled fictional user, actual role assignment or effective user permission tested yet**.

**Additional verified requester/issuer masters:** `Operations - TREQ: ELIGIBLE` (company `Integration Test Requester`, enabled non-group); issuer's sole leaf Cost Center `Main - TISS`; issuer's `Cost of Goods Sold - TISS` and `Stock Adjustment - TISS` accounts present with root type Expense and `is_group = 0`. Previous prior baseline 10 Nos / PHP1000, two companies and warehouse verified; not new writes. Account presence is not proof of GL mapping.

**Security decision before any fixture/user creation or positive stock posting:** The combined Requestor/Stockroom rights plus self-approval Workflow **may** permit an individual to create, approve, begin Stockroom Review and issue their own request, violating typical separation-of-duties expectations. It is not a confirmed exploit or tested permission path; site Workflow detail and `if_owner` should be checked read-only. Do not create users, suppress existing hook, change permission role matrices, submit documents, switch the shared app, restart services, touch PRODUCTION or claim site connected feature tests. Feature draft PR #7 at SHA `85d129e193b32cc229de2e30145359bb3979c257` remains unmerged. 11 recovery checkpoints / 44 integrity-verifed files preserved; no restore drill. The integration test plan was updated by docs commit `6d029512a48333d5baaae1212df0ac053dc97494` on branch `docs/ccpc-checkpoint-2026-10-10`. Next operator step only: read-only verify the actual isolated Withdrawal Slip workflow transitions, per-role DocPerm ownership restrictions and resulting role-action intersection. Then request explicit owner decision on requestor/issuer self-processing policy and separate consent before any User writes.

## Fictional fixture preflight passed; discovered Stockroom auto-granted requestor roles — 2026-10-14

**Operator-provided isolated DB read-only preflight passed:** `ISOLATED DATABASE: VERIFIED`; companies `Integration Test Issuer` (TISS) and `Integration Test Requester` (TREQ); 13 requester Department records and all 13 enabled leaf eligible; `Operations - TREQ` is a suitable candidate; no active CCPC Section for any requester Department. `Stores - TISS` verified as issuer's active leaf warehouse; `CCPC-INT-TEST-CONSUMABLE-001` verified active stock Item / Nos; Bin `10.000000000` actual_qty and `PHP 1000.000000000` stock value. Issuer has 30 leaf Expense Accounts and 1 leaf Cost Center; configured `default_expense_account = Cost of Goods Sold - TISS`, `stock_adjustment_account = Stock Adjustment - TISS`; `tabCompany.default_cost_center` column not present, so Cost Center assignment cannot be inferred from Company. Script `READ-ONLY FIXTURE PREFLIGHT: COMPLETED`; no DB writes. Account/cost center resolution on actual Material Issue still untested.

**New GitHub source security/fixture finding:** On active review/base branch and feature branch, the `User.before_save` hook uses the **identical** `ccpcerp.setup.ensure_operational_requestor_roles_on_user` implementation. `Stockroom Personnel` is in `OPERATIONAL_REQUESTOR_SOURCE_ROLES`, so a Stockroom System User automatically gets `MRS Requestor`, `Withdrawal Slip Requestor` and `CCPC Stock Inquiry User` when these role records exist. This is **intentional current-code behavior** but invalidates the previous draft fixture phrase "only Stockroom Personnel". The read-only DocPerm audit had examined two roles, not the extra grants. Since Workflow permits Requestor self-approval (Draft→Approved) and Stockroom can Start Review, the effective combined roles **may allow same individual to request, approve and issue**; treat as a potential separation-of-duties gap pending actual permission/owner policy review. No policy change, source patch, role write or posting is authorized.

**Next safe gate:** Read-only SQL audit of existence of three auto-added roles and effective relevant DocPerm rows (at least Withdrawal Slip and Stock Entry; include standard/custom sources) and confirm `Operations - TREQ` and available issuer Cost Center plus account records. Continue to preserve shared DEVELOPMENT Git, the detached import source, 11 protected snapshots / 44 archives (no restore drill) and PRODUCTION. After combined-role audit, seek explicit user decision on stockroom dual-role/self-issue policy and scoped approval for any fictional test User creation. Integration plan updated at docs commit `be483d651a29d5dadc707ae0b3926f3d91949a26`; this handoff remains source of truth for continuity.

## Pinned feature imports and Stock Entry hook registrations passed site-free — 2026-10-14

**Operator-supplied actual short-lived Python module-import test output:** `FEATURE MODULE VERIFIED:` `ccpcerp`, `ccpcerp.hooks`, `ccpcerp.ccpc_erp.doctype.withdrawal_slip.withdrawal_slip`, `ccpcerp.ccpc_erp.withdrawal_slip_stock`; `FEATURE HOOK REGISTRATIONS: VERIFIED`; `FEATURE ENDPOINT IMPORT: VERIFIED`; `SHARED APPLICATION: UNCHANGED`; `SITE INITIALIZATION: NOT PERFORMED`; `DATABASE ACCESS: NOT PERFORMED`; `SITE-FREE FEATURE IMPORT CHECK: PASSED`. Test reasserted shared checkout at `806fa23516490ec7beefcff03a1baa09d722120e` with only untracked `?? AGENTS.md`, detached feature at `85d129e193b32cc229de2e30145359bb3979c257`, no tracked changes, resolved every imported module's `__file__` inside exact detached checkout, verified `Stock Entry` `validate`/`before_submit` handler, `on_submit`/`on_cancel` handler strings and callable endpoint, and confirmed Frappe `local.initialised` was false. No site/DB connection or writes.

**Implication:** The exact feature source is importable in a **separate ephemeral process** without modifying the active app worktree or initializing any site. This does **not** establish feature hooks dispatching under a live initialized Frappe site, user permissions, HTTP POST behavior, SLE/GL correctness, concurrency locking, or transaction rollback. Next safe step: read-only direct SQL prerequisite audit of synthetic `Integration Test Issuer` (TISS), `Integration Test Requester` (TREQ), eligible requester Department and active CCPC Section if required, item `CCPC-INT-TEST-CONSUMABLE-001`, `Stores - TISS` warehouse, plus configured company costing/account defaults and stored stock. Do not write or initialize site. Specific workflow/user/Material Issue writes require separate owner authorization. Integration plan updated on docs branch in commit `5b5edbddf403fffb2904f6cea2e864729c584632`. Backup baseline remains 11 verified snapshots / 44 archived files; no restore drill.

## Detached feature checkout and source-resolution gate passed read-only — 2026-10-14

**Operator-reported site-free Docker test (read-only):** `ACTIVE SHARED APP: PROTECTED`; `PINNED FEATURE WORKTREES FOUND: 1`; `DETACHED FEATURE CHECKOUT: VERIFIED`; `PYTHON PACKAGE RESOLUTION: FEATURE SOURCE`; `ISSUE ENDPOINT AND HOOK SOURCE: VERIFIED`; `DATABASE ACCESS: NOT PERFORMED`; `SITE INITIALIZATION: NOT PERFORMED`; `READ-ONLY FEATURE ISOLATION: COMPLETED`. Command reverified live app `review/intercompany-approval-failure-tests` SHA `806fa23516490ec7beefcff03a1baa09d722120e` with only protected `?? AGENTS.md`; uniquely identified a separate detached Git worktree at exact feature SHA `85d129e193b32cc229de2e30145359bb3979c257` and no tracked modifications; `importlib.util.find_spec("ccpcerp")` resolved `ccpcerp/__init__.py` from that detached tree; required endpoint and hook symbol strings were present in detached source.

**Important limit:** `find_spec` and reading source do **not** establish that importing the complete `ccpcerp` package, Withdrawal Slip/Stock Entry hook modules and hook handlers succeeds at runtime, nor that Frappe site initialization, module map, background workers and request transactions would load those modules from detached source. No feature endpoint was invoked, no Frappe site was initialized, no roles/users or database writes. The next permitted check is a **fresh short-lived site-free Python process** with `FRAPPE_STREAM_LOGGING=1`, prefix its `sys.path` with the pinned detached tree, `importlib.import_module` the exact hooks and Withdrawal Slip issue/controller modules, verify each `__file__` and hook registration targets match the pinned feature, and assert `frappe.local.initialised` remains false. This is not yet a DB integration test. If an import fails or points to the shared checkout, stop; design a stronger separate-bench isolation plan before any writes.

**Broader scope:** All 11 recovery checkpoints and 44 backup files verified (no restore drill); 47/47 mocked regressions passed; no ordinary users exist on site, roles/doc permissions were audited but effective role checks still pending. User said "Continue" to proceed with planning/review; this is **not** permission for creating identities, performing stock/GL transactions, merging/deploying feature, migrating, altering shared DEVELOPMENT, or modifying PRODUCTION. Integration plan remains [WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md](WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md).

## Proposed isolated Material Issue integration-test design saved; no fixture writes — 2026-10-14

**New reviewed GitHub design document:** [WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md](WITHDRAWAL-MATERIAL-ISSUE-INTEGRATION-TEST-PLAN.md) created on docs branch `docs/ccpc-checkpoint-2026-10-10` at commit `c12647b92898ce9da32d4d1ceb1d5f10622d9808`. This is **design only**, under owner's "Continue" request following the successfully verified 11th backup, not approval for users, permission changes, feature code deployment, financial records or posting tests. GitHub app branch feature/withdrawal-material-issue-safety remains at `85d129e193b32cc229de2e30145359bb3979c257` and draft PR #7 is unmerged; shared app is still expected at `806fa23516490ec7beefcff03a1baa09d722120e` with protected untracked AGENTS.md. Backup recovery baseline: 11 sets / 44 archive-verified files (but no restore drill).

**Design reviewed from GitHub source:** POST-only `issue_withdrawal_slip` should enforce Stockroom role + Slip write permission, parent FOR UPDATE lock, workflow state `Stockroom Review`, `received_by`, no submitted/draft issue, validated item quantity, scoped insert/submit and normal document hooks. Site's Workflow has 8 states/4 transitions; setup source defines Requestor `Draft → Approved` then Stockroom `Approved → Stockroom Review`. Slip DocType requires source warehouse, both Companies, requester department, requestor, date, physical location, purpose and item row; controller checks department-company consistency. Two fictional test users with minimal Requestor and Stockroom roles are **proposed only**. No privileged stock roles. Before any writes, verify requester Department and cost center/expense settings read-only.

**Key blocker/next safe read-only action:** The shared DEVELOPMENT app tree serves both isolated and persistent sites. Never use `git switch`, `pull`, `bench migrate`, restart or write feature code into that active worktree. First inspect detached Git worktrees read-only and prove a pinned feature checkout still exists at `85d129e...` and Python import resolution can select its `ccpcerp` package in a separate test process; check hook/module origins before permitting runtime invocation. If the detached checkout is missing or Python resolves the old shared code, STOP and redesign isolation. Also inspect effective role/Department prerequisites before any fixture. Later stages require **separate scoped owner authorization** for user/role writes and for live Withdrawal Slip/Material Issue posting, concurrency and rollback tests; do not infer permissions from "Continue." Planned one-unit stock issue expectation nominally changes 10 Nos/PHP1000 to 9 Nos with valuation/GL separately audited; no synthetic transaction has been created or authorized.

## Eleventh isolated full backup verified: 44 protected artifacts; pre-Material-Issue baseline — 2026-10-14

**Owner-authorized backup-only task COMPLETED, independently operator-verified from printed terminal output.** The corrected one-shot backup ran in DEVELOPMENT's Frappe container against **only** `ccpc-integration2.localhost` and ended `ISOLATED BACKUP: PASSED`. Operator output: `SAFETY PREFLIGHT: PASSED`; `STREAM LOGGING: ENABLED FOR THIS PROCESS`; `EXISTING EMPTY DESTINATION: VERIFIED`; `RETENTION CLEANUP REDIRECTED: VERIFIED`. New recovery checkpoint: `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-stock-entry-fields-pre-material-issue-20261014/`, four files timestamped `20261014_125043`:
- `20261014_125043-ccpc-integration2_localhost-database.sql.gz` — **995981 bytes**
- `20261014_125043-ccpc-integration2_localhost-files.tar` — **10240 bytes**
- `20261014_125043-ccpc-integration2_localhost-private-files.tar` — **10240 bytes**
- `20261014_125043-ccpc-integration2_localhost-site_config_backup.json` — **212 bytes**

**Exact verification:** Script validated the four new files are nonempty regular files with 0600-style no-group/world-access mode, exact expected names, full gzip stream readability and TAR member readability, site-config JSON parse and db_name match to the isolated target, without printing secrets. It separately re-hashed all **40 original historical backup files** before and after and output `ORIGINAL 40 FILES: SHA256 UNCHANGED`; site_config SHA256 was unchanged (`SITE CONFIGURATION: UNCHANGED`); and post-run independent MySQLdb `START TRANSACTION READ ONLY` audit matched the pre-run isolated DB baseline (`DATABASE BASELINE: UNCHANGED`): 0 Withdrawal Slips, 0 Stock Entries, 1 SLE, 2 GL, 0 intercompany billing batches, a synthetic Bin with 10 Nos / PHP1,000, one submitted opening Stock Reconciliation. Overall counts **11 recovery checkpoints / 44 full-site backup artifacts**. Previously 10/40 had been archive validated; new 4 were archive validated on this run. **NO FULL RESTORE DRILL HAS BEEN PERFORMED**, and backup artifact integrity is not recovery-test proof.

**Issue resolution:** Previous first backup attempt failed after preflight due to FileNotFoundError before retention redirection, creating only an empty target directory; root error pathname was not captured. Read-only diagnostic confirmed missing `/workspace/development/logs` plus installed Frappe v16 logger's file-handler default. The corrected attempt set `FRAPPE_STREAM_LOGGING=1` in its single process, safely reused the empty site-private target without deleting it, temporarily changed only in-memory `frappe.conf.backup_path` so Frappe's built-in `delete_temp_backups()` operated on the empty new directory rather than standard `private/backups/` (which contains the original pre-index checkpoint). No saved site config or permanent logging config changed.

**Scope and next gate:** This was **backup only**. No user/role, Withdrawal Slip or Material Issue creation, inventory/GL posting, database migrations, feature checkout/pull/merge/deployment, restores, or PRODUCTION actions were authorized/executed. Application feature branch and draft PR #7 remain at `85d129e193b32cc229de2e30145359bb3979c257` (GitHub verified 2026-10-14); active shared DEV checkout most recently independently verified at `review/intercompany-approval-failure-tests` commit `806fa23516490ec7beefcff03a1baa09d722120e` with untracked `AGENTS.md` preserved. Two detached mock-only suites passed 12/12 and 35/35 (47 total); live Stockroom-user, MariaDB row lock/race, inventory and GL posting/rollback remain untested. **New separate user authorization required** before any user identity/role writes, business transactions or feature-code invocation on the isolated site. Next safe task: design strictly isolated process/source testing method preserving shared bench and PRODUCTION, plus synthetic user and one-unit test plan; do not treat fresh backup alone as approval to execute integration tests.

## Installed Frappe logging/backup code confirmed; corrected single backup retry planned — 2026-10-14

**Operator-provided read-only Python source inspection:** `INSTALLED FRAPPE SOURCE: VERIFIED`, `FILE-BASED LOG HANDLER: PRESENT`, `STREAM LOGGING SUPPORT: PRESENT`, `PARENT LOG DIRECTORY: ABSENT`, `STREAM LOGGING ENVIRONMENT: UNSET`, `BACKUP CLEANUP ROUTINE: PRESENT`, `BACKUP PATH OVERRIDE: PRESENT`, `READ-ONLY LOGGING DIAGNOSIS: COMPLETED`. On the previous read-only filesystem triage, new destination `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-stock-entry-fields-pre-material-issue-20261014` is an empty directory; original 40 checkpoint files remained present/nonempty; active shared checkout `review/intercompany-approval-failure-tests` SHA `806fa23516490ec7beefcff03a1baa09d722120e` with `?? AGENTS.md` unchanged.

**Cause assessment:** Public and installed v16 Frappe logger source both support file-based `RotatingFileHandler` and the `FRAPPE_STREAM_LOGGING` environment switch. Under Python working directory `/workspace/development/frappe-bench`, upstream `../logs` resolves to absent `/workspace/development/logs`. Missing logger directory is the likely explanation for FileNotFoundError during initial Frappe init/connect; **exact missing pathname is not proven** because original guarded script printed only exception class. The supported runtime-only `FRAPPE_STREAM_LOGGING=1` should bypass file-backed handler. Separately, source inspection shows Frappe backup's implicit `delete_temp_backups()` cleanup must remain pointed to the new empty destination in an in-memory `frappe.conf.backup_path` override, otherwise the original first checkpoint in `private/backups/` could be pruned.

**Authorized corrected execution plan (still pending):** Reuse the existing empty target (check no symlinks/no entries); do not delete or rename it. Preflight site DB identity, baseline Bin and ledger counts, git branch/status, >=1 GiB free disk, new target mode, config hash and SHA-256 of all 40 old checkpoint files; invoke Python with `FRAPPE_STREAM_LOGGING=1` before importing Frappe; initialize only the isolated site and redirect runtime backup path to target; verify resolved cleanup path equals target; run supported `backups.scheduled_backup(ignore_files=False, backup_path=<absolute target>, ignore_conf=True, force=True)` **once**; validate new four full archives, gzip/TAR/database-config identity, file permissions, unchanged originals/config, and unchanged DB baseline. Include safe explicit operation stage in failure output instead of leaking credentials or complete traceback; on any failure **stop with no automatic retry/cleanup**. Not yet executed. No additional user authorization beyond the earlier one full isolated-site backup is required because the first attempt produced no files and the approval scope remains the same; if meaningful anomalies arise obtain new approval before further writes. No user/role/Stock Entry/PRODUCTION actions authorized.

## Failed backup filesystem triage: empty new destination; original 40 present; bench-parent log dir absent — 2026-10-14

**Operator-provided read-only failure-diagnosis output:** Active shared application remains `review/intercompany-approval-failure-tests` commit `806fa23516490ec7beefcff03a1baa09d722120e`, with protected untracked `?? AGENTS.md`. New backup target `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-stock-entry-fields-pre-material-issue-20261014` is **a real directory with zero entries**. All **40 preexisting backup files remain present and nonempty**, across nine old checkpoint subdirectories and four first-checkpoint artifacts in `private/backups`. After the failed attempt, those old files were **not re-hashed**; the latest read-only test verified presence/nonzero size, not equal SHA256 against the pre-run hashes. Directory `/workspace/development/logs` is ABSENT; `/workspace/development/frappe-bench/logs` is PRESENT; `/workspace/development/frappe-bench/sites/logs` is ABSENT. Command ended `READ-ONLY FAILURE DIAGNOSIS: COMPLETED`. No new archive file verified; **ten existing checkpoints remain the only verified backups**.

**Likely technical cause, pending installed-source confirmation:** Frappe v16 upstream `frappe/utils/logger.py` `create_handler` sets bench logfile path to `os.path.join("..", "logs", f"{module}.log")` and constructs `RotatingFileHandler` when `FRAPPE_STREAM_LOGGING` is unset. With the command run from `/workspace/development/frappe-bench`, that relative path is under **the absent `/workspace/development/logs` directory**; this could cause `FileNotFoundError` during `frappe.init`, Frappe caching or logging before `BACKUP RETENTION SAFELY REDIRECTED` prints. **Exact missing pathname is not proven because original script suppressed exception details.** Upstream logger source uses environment `FRAPPE_STREAM_LOGGING` to enable stderr streaming instead of file handlers; a per-process setting is a candidate fix without directory creation or persistent configuration. Before proceeding, use **read-only static inspection of installed logger and backups.py source**, confirming handling and expected paths; do not re-execute the failing backup yet or remove its empty target.

**Safety boundary:** Approved scope remains exactly one new site-specific backup; since the attempt did not produce files, it is still **PENDING**, not completed. Do not delete the empty directory (unsafe shortcut), alter `private/backups`, modify `site_config.json`, switch shared app, create test users/documents, execute a restore or touch PRODUCTION. Plan a revised guarded single backup invocation only after confirming installed logger and retention semantics; if needed, adopt the existing empty destination and protect 40 old file fingerprints. No application code changes made. GitHub remains source of truth for notes, not the failed test run.

## Approved isolated full-backup attempt stopped after preflight; FileNotFoundError — 2026-10-14

**Operator terminal output for owner-approved one-time backup-only command:** Full operator command was the guarded inline Python script targeting only `ccpc-integration2.localhost`, new destination `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-stock-entry-fields-pre-material-issue-20261014`. Its preflight fingerprinted all **40 historical backup files**, verified git HEAD/branch with protected untracked AGENTS.md, isolated DB identity and business counts/Bin, site configuration fingerprint and >=1 GiB free disk, and printed `SAFETY PREFLIGHT: PASSED`. Then command printed `STOP: Guarded backup did not complete verification; no automatic retry or cleanup.` and `ERROR CLASS: FileNotFoundError`; **no** `BACKUP RETENTION SAFELY REDIRECTED (PROCESS ONLY)`, new file verification or `ISOLATED BACKUP: PASSED` printed.

**Failure location unknown:** Script enters its writing phase immediately after the successful preflight by invoking `target.mkdir(mode=0o700)`; it then imports Frappe, initializes/connects site, verifies existing backup retention path and source, and overrides only in-memory Frappe backup path before calling `backups.scheduled_backup`. Because `BACKUP RETENTION SAFELY REDIRECTED` never printed, failure occurred before that print; the failed command only printed exception class, **not missing filename or traceback**. Consequently, one new empty/incomplete destination directory **may** have been created, but no verified new recovery checkpoint exists. Original 40 were fingerprinted before failure; **no after-failure read-only inventory yet**. Never assume that original backups or site settings are definitely unchanged until independently rechecked. Do not automatically retry, clean, remove, move, or restore files.

**Immediate next step:** A **read-only** guard command to (a) list only the new target directory's existence, type and zero/known file count/sizes without opening secrets; (b) verify all original 40 expected exact backup file paths remain accessible and nonempty, including four in `private/backups/`, with nine old snapshot folders excluding the new target; (c) verify active shared app branch/HEAD/AGENTS.md; (d) inspect existence (not write) of candidate Frappe log directories including `/workspace/development/logs` and `/workspace/development/frappe-bench/logs`. This is a diagnostic **not permission to create another backup**. If old files have changed, stop. Next diagnose the exact missing path via a guarded, redacted exception report before deciding on a replacement backup attempt under the limited approval; do not run Frappe init/connect speculatively or expose secret configs. No users/stock GL postings, migrations, app checkout changes, service restarts or PRODUCTION operations authorized. Feature draft PR #7 and 47 mocked tests unaffected.

## Owner approved exactly one new isolated-site full backup; execution pending — 2026-10-14

**Explicit user approval:** In response to "Do you approve creating one new protected full backup of ccpc-integration2.localhost only, preserving all ten existing recovery checkpoints?", owner answered **"Approved"**. This authorizes **one new full backup only**, not users, permissions, Withdrawal Slips, Stock Entries, accounting/GL posting, migrations, feature deployment, active branch changes, production operations, cleanup or backup restoration.

**Validated recovery preflight:** Isolated site has 1 active Withdrawal Slip Workflow, 8 states / 4 transitions; stock Bin CCPC-INT-TEST-CONSUMABLE-001 / Stores - TISS at 10 Nos, PHP1,000; 1 submitted opening Stock Reconciliation; 0 Withdrawal Slips, 0 Stock Entries, 1 SLE, 2 GL entries, 0 billing batches, 0 enabled nonstandard users and 0 Stockroom Personnel assignments. Both Stockroom Personnel and Withdrawal Slip Requestor roles exist, with Stockroom read/write 1/1 and zero native Stock Entry permissions in inspected DocPerm tables. Previously 47/47 mocked tests green; ten checkpoints/40 files separately integrity validated with no restore drill. GitHub draft PR #7 remains on feature/withdrawal-material-issue-safety at 85d129e193b32cc229de2e30145359bb3979c257. Active shared app stays at review/intercompany-approval-failure-tests SHA 806fa23516490ec7beefcff03a1baa09d722120e and untracked AGENTS.md preserved.

**Crucial observed Frappe v16 source behavior before next backup:** Public upstream frappe/frappe version-16 frappe/utils/backups.py new_backup() calls delete_temp_backups() unconditionally before BackupGenerator, **even when backup_path is explicitly provided**. delete_temp_backups() removes files older than configured hours under get_backup_path() (usually private/backups), thus might delete the original pre-index first backup (20261013_102539) during a naive bench --site ... backup --backup-path invocation. Its per-process get_backup_path() resolves frappe.conf.backup_path. A guarded isolated-only Python procedure should set a temporary in-memory frappe.conf.backup_path to a new empty protected site-private backup directory AND pass the same absolute directory to supported scheduled_backup(ignore_files=False, ignore_conf=True, force=True), asserting get_backup_path() resolves to that new directory before starting. Do not persist this override to site_config.json, do not touch private/backups or other checkpoint sets. Guard unchanged active app branch/AGENTS.md, target-vs-persistent database identity, 40 preexisting file fingerprints, site-only ledger baseline, sufficient free disk, no existing new target path, and backup encryption compatibility. After one backup, verify four files (gzip/TAR/JSON identity and permissions), all 40 old fingerprints unchanged and no site-config changes; output only safe names/counts. This is a planned procedure based on upstream source and prior successfully used site-only backup API; actual installed code behavior is still subject to local safety checks.

**Status: ONE BACKUP APPROVED BUT NOT YET EXECUTED OR VERIFIED.** Next reply should supply one guarded Ubuntu server command for owner to run as frappe within DEVELOPMENT container. After operator reports result, independently reconcile outcome and update this same rolling handoff. No assumption about successful backup or test integration until observed.

## Isolated role/DocPerm audit verifies limited Stockroom access — 2026-10-14

**Owner/operator provided read-only MySQLdb permissions audit, isolated `ccpc-integration2.localhost` only:** Output `ISOLATED DATABASE: VERIFIED`; both `Stockroom Personnel` and `Withdrawal Slip Requestor` Role records are present. At permission level 0 in `tabDocPerm`, Withdrawal Slip / Stockroom Personnel rights `read=1, write=1, create=0, submit=0, cancel=0`; Withdrawal Slip / Withdrawal Slip Requestor rights `read=1, write=1, create=1, submit=0, cancel=0`. No matching `tabDocPerm` rows for Stock Entry with either of those roles. In `tabCustom DocPerm`, no matching rows for either role on Withdrawal Slip or Stock Entry. The script ended `READ-ONLY PERMISSION AUDIT: COMPLETED`; used `START TRANSACTION READ ONLY` and rollback/close. No user/role or DB writes.

**Interpretation/limitations:** Configured permission rows support the least-privilege design: the Stockroom role may read/write an existing Withdrawal Slip but has **no native Stock Entry permission from the two queried tables**, including create or submit; the Requestor may create Withdrawal Slips but may not submit them natively. No nonstandard enabled user or Stockroom role assignment exists yet, so **effective session/role/record permissions and live Stock Entry submission are NOT TESTED**. Other roles, ownership conditions, user permissions and hooks may affect effective rights; the query was limited to exactly the two roles and doctypes. GitHub feature branch at `85d129e193b32cc229de2e30145359bb3979c257` uses a POST-only, role-gated issue endpoint with document-specific bypass for newly constructed Stock Entry, not a grant of the standard Stock User/Manager role. The active bench at `806fa235...` remains separate from feature branch.

**GitHub workflow and next authorization gate:** Confirmed `setup.py` workflow defines Draft -> Approved through a Withdrawal Slip Requestor self-approval transition; Approved -> Stockroom Review through Stockroom Personnel; stock issue is endpoint-triggered from Stockroom Review. Read-only audits show site has 8 states/4 transitions, correct three integration fields, one Bin (10 Nos/PHP1000), 1 opening Stock Reconciliation, no Withdrawal Slip/Stock Entry, one SLE/two GL, zero nonstandard users. Previously 47/47 mocked tests passed and all 40 backup archives passed integrity/DB identity checks, but no restore drill. **Do not change the live shared app worktree**: both `development.localhost` and `ccpc-integration2.localhost` load it. Proposed staged isolated integration verification requires explicit user authorization for (1) new site-only post-fields/pre-integration checkpoint, (2) minimal fictional test users and only required rights on isolated site, (3) a process-isolated pinned feature import (must independently verify hooks/source and not switch active app), and (4) separately approved synthetic Withdrawal Slip and 1-unit Material Issue posting, duplicate/race/error rollback assertions, independent SLE/GL/Bin verification. Until approval, only read-only compatibility/source checks. Preserve `AGENTS.md`, existing checkpoints, databases and PRODUCTION; no broad roles, bench migrate, restart or unapproved posting.

## Isolated Workflow, roles, and stock readiness audited read-only — 2026-10-14

**Operator supplied read-only MySQLdb integration preflight result:** Output `ISOLATED DATABASE: VERIFIED` (connection to `ccpc-integration2.localhost` database distinct from persistent `development.localhost`, within `START TRANSACTION READ ONLY`, rolled back and closed); one active Withdrawal Slip Workflow, **8 workflow states**, **4 transitions**; **0 enabled nonstandard User accounts** (other than Administrator and Guest); **0 user assignments to Stockroom Personnel**; exactly **1** Bin for `CCPC-INT-TEST-CONSUMABLE-001` at `Stores - TISS` with `actual_qty = 10.000000000`, `stock_value = PHP 1000.000000000`; **1 submitted Stock Reconciliation**. Script ended `READ-ONLY INTEGRATION PREFLIGHT: COMPLETED`. This reaffirms the isolated synthetic-stock baseline and confirms no real Stockroom-user permissions could have been runtime-tested so far.

**Current test/recovery status:** Two detached site-free suites passed 12/12 newly mocked issue-safety tests and 35/35 existing mocked Withdrawal Slip regressions (47 across two runs) at feature commit `85d129e193b32cc229de2e30145359bb3979c257`; draft PR #7 remains unmerged. All ten checkpoint sets and 40 artifacts across `private/backups` and `private/ccpc-test-snapshots` were re-read and passed gzip/TAR/JSON and DB-name identity validation, but **no restore drill**. Earlier independent DB read-only audit: 3/3 Stock Entry custom provenance fields and SQL columns exist; Withdrawal Slips 0, Stock Entries 0, SLE 1, GL 2, billing batches 0.

**Important control:** This isolated site shares the active Frappe application worktree with persistent `development.localhost`. That worktree remains `review/intercompany-approval-failure-tests` SHA `806fa23516490ec7beefcff03a1baa09d722120e` with untracked `AGENTS.md` preserved at last check. Only the detached /tmp worktree contains the new feature. **No permission changes, user creation, workflow actions, Stock Entry posting, database mutation, migrations, service restart, branch change or PRODUCTION work have been approved.** Live role/DocPerm behavior, issue concurrency, rollback, GL/SLE correctness remain untested. Continue with a read-only role/permission metadata audit and detached test-process isolation design. Before any synthetic user/Slip or financial posting, obtain separate explicit owner approval of the site-scoped fixtures, isolation, backups, expected ledger movements and rollback procedure; never switch the shared app branch just to run tests.

## Isolated Material Issue database readiness audit passed — 2026-10-14

**Operator-provided independent read-only MySQLdb audit:** Connected to the isolated `ccpc-integration2.localhost` site database using its site-local config and shared read-only endpoint settings; verified `site_config.json` `db_name` differs from persistent `development.localhost`; executed `START TRANSACTION READ ONLY`, checked `SELECT DATABASE()` matched expected isolated DB name. Confirmed both `tabCustom Field` record and matching physical SQL column for each of `Stock Entry.withdrawal_slip`, `Stock Entry.withdrawal_slip_issued_by`, and `Stock Entry Detail.withdrawal_slip_item`, exactly one each. Business baseline counts were `tabWithdrawal Slip = 0`, `tabStock Entry = 0`, `tabStock Ledger Entry = 1`, `tabGL Entry = 2`, `tabIntercompany Material Billing Batch = 0`. Command output finished `READ-ONLY DATABASE READINESS: COMPLETED`; the Python finally block rolled back and closed the read-only connection. No writes, records, branch switch, Frappe site initialization, or service changes performed.

**Interpretation:** Zero Withdrawal Slips, Stock Entries and billing batches is a clean pre-issue baseline; one SLE and two GL entries are consistent with the previously independently verified 10 Nos / PHP1,000 synthetic opening-stock reconciliation, though this particular query counted rows rather than independently revalidating their economic amounts/links. This audit checks presence of Custom Field rows and physical columns, not their full required metadata properties or actual document behavior. The previously verified ten checkpoints and 40 archives passed gzip/TAR/JSON/database-identity integrity checks (but NO restore drill). GitHub feature branch `feature/withdrawal-material-issue-safety` and draft PR #7 remain pinned at `85d129e193b32cc229de2e30145359bb3979c257` and 47 of 47 mocked tests passed in separate runs. Active shared DEV app stayed at `806fa23516490ec7beefcff03a1baa09d722120e` with untracked `AGENTS.md` at last operator status.

**Critical next gate:** Real MariaDB concurrency, live Stockroom DocPerm enforcement, Material Issue insert/submit, SLE+GL effects, and transaction failure/rollback are NOT YET TESTED. The accepted GitHub-only coding scope does not authorize placing new feature code in the shared application checkout, modifying persistent DEVELOPMENT or PRODUCTION, creating test identities/stock transactions, or triggering DB migrations. Next limited action: independent read-only audit of relevant isolated-site Workflow, test-user/role readiness and synthetic Bin/reconciliation context, then devise a precise *separate-process source import/isolation and transaction recovery plan*, and seek explicit operator authorization for any live test writes. Do not merge/deploy PR #7 or change the active application just to test it.

## All ten isolated-site recovery checkpoints archive-verified read-only — 2026-10-14

**Operator-provided result of complete 40-artifact read-only integrity script:** Reported ten `VERIFIED` lines (pre-index first, followed by all nine separate site-private snapshot folders). Summary printed `CHECKPOINTS VERIFIED: 10`, `BACKUP FILES VERIFIED: 40`, `READ-ONLY ARCHIVE INTEGRITY: PASSED`. The script checked presence, regular-file type (rejecting symlinks), nonzero size and exact expected four suffixes per checkpoint; streamed the full database `database.sql.gz` through gzip decompression (checking gzip integrity), read each regular member of public/private TAR archives, parsed `site_config_backup.json` and matched its `db_name` to the isolated test site's `site_config.json` without displaying credentials. The first pre-index checkpoint resides in `sites/ccpc-integration2.localhost/private/backups/`; the remaining nine are in `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/`. Therefore the prior 36-vs-40 location/count discrepancy is resolved and all **40 expected archived files were read successfully** on this run.

**Limits:** This was an archive integrity/database-name check, **not a full site restore**, recovery-time verification, independent SHA-256 comparison or actual MySQL import trial. Backup retention in the standard first-backup directory remains a possible future risk. Do not delete, move, restore or print backup/config contents. No source changes, site initialization, DB operations/transactions, role or user changes, migration, service restarts, or DEVELOPMENT/PRODUCTION deployment occurred during the operator's script.

**Overall feature readiness:** Branch `feature/withdrawal-material-issue-safety` remains at GitHub commit `85d129e193b32cc229de2e30145359bb3979c257`; draft PR #7 is NOT merged, active shared DEVELOPMENT application stays at `review/intercompany-approval-failure-tests` commit `806fa23516490ec7beefcff03a1baa09d722120e` with protected untracked `AGENTS.md`. The two separately executed site-free mocked suites remain green: 12 security checks and 35 legacy regressions (47/47). **Live MariaDB row locking, permissions, Stock Entry/Stock Ledger/General Ledger posting, commit/rollback and concurrent duplicate prevention are still UNTESTED**. The prior owner authorization covered GitHub code and mocked tests **without deploying**, and does not approve inserting synthetic business transactions or changing the shared app directory. Before any database-backed tests, use a separate approved isolation plan that cannot silently affect persistent development.localhost or PRODUCTION, read-only inspect the isolated site's current schema/business baseline, and obtain explicit follow-on approval for any setup, deployment or transactional writes.

## Ten snapshot checkpoints / 40 expected artifacts now accounted for across two directories — 2026-10-14

**Operator supplied read-only first-checkpoint verification:** Under `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/backups/`, all four exact regular files exist (the command tested `-f` and rejected symbolic links), with prefix `20261013_102539-ccpc-integration2_localhost`: `database.sql.gz` **899266 bytes**, `files.tar` **10240 bytes**, `private-files.tar` **10240 bytes**, `site_config_backup.json` **212 bytes**. The command output ended `READ-ONLY PRE-INDEX CHECK: COMPLETED`.

A prior same-day read-only `find` counted **nine** checkpoint directories with exactly four files each under `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/`, totaling **36** and including all four `20261013_181534` tenth/latest artifacts. Combined with the separately located pre-index checkpoint's four verified present files, the historical **ten sets / 40 expected backup file paths and byte sizes** are now accounted for. Earlier `find` saw **zero symbolic links** within the nine snapshot directories. This resolves the apparent 36-versus-40 inventory discrepancy: original first backup is at standard `private/backups/`, not inside the snapshot subdirectory.

**Critical limitation:** Same-day existence/size checks **do not yet verify gzip CRC, TAR readability, JSON validity, database identity or SHA256 hashes**, and none of the checkpoints has been restored in a drill. Do not equate file presence with recovery readiness or describe full restoration as tested. Next guard is one read-only, site-scoped audit of all 40 expected archives, checking gzip/TAR structure, JSON syntactic validity and backup DB identity against the isolated site config without printing credentials or contents. The first backup under standard retention-managed `private/backups/` should be preserved; do not copy, move, delete, restore or modify any backup without distinct approval. No site/database/branch/service/PRODUCTION changes authorized.

**Development/testing state unchanged:** Feature branch draft PR #7 at `85d129e193b32cc229de2e30145359bb3979c257`; 12/12 focused mocked security tests and 35/35 legacy mocked regression tests passed separately. Active shared app remains at `806fa23516490ec7beefcff03a1baa09d722120e`, with untracked `AGENTS.md` preserved. Real MariaDB/Stock Entry/GL posting and concurrency integration tests remain pending separate approved isolation/deployment procedure.

## Backup-location reconciliation: first four files historically outside snapshot directory — 2026-10-14

**Operator read-only snapshot tree inventory:** Inside `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/` there are **nine** subdirectories, each with exactly four files, totaling 36. The latest `post-withdrawal-workflow-pre-stock-entry-fields-20261013` is present with four exact files using prefix `20261013_181534-ccpc-integration2_localhost`, sizes 984402, 10240, 10240 and 212 bytes; zero symbolic links. No files deleted or restored. The active application remains review/intercompany-approval-failure-tests SHA 806fa23516490ec7beefcff03a1baa09d722120e and untracked AGENTS.md remains.

**Documented location resolves the apparent 36 versus 40 *directory counting* mismatch:** The original **first/pre-index** checkpoint was created in **a separate directory**, `sites/ccpc-integration2.localhost/private/backups/`, under the prefix `20261013_102539-ccpc-integration2_localhost`. Prior verified artifact names/sizes in older sections of this same handoff: `database.sql.gz` 899266 bytes, `files.tar` 10240 bytes, `private-files.tar` 10240 bytes, `site_config_backup.json` 212 bytes. The nine later checkpoint sets are in `private/ccpc-test-snapshots/` and their 36 files are consistent. If the first four still reside in `private/backups/`, total becomes ten checkpoint sets and 40 files. **Their present-day existence/integrity is NOT YET VERIFIED**; retention may affect standard backups, so do not describe all 40 as currently preserved until a read-only direct file check.

**Next one-step guard:** List only the exact four named pre-index files in `private/backups/` by presence, regular-file type and byte count; never print or transmit archived content or site configuration secrets. If all four remain, separately assess archive integrity, then plan controlled isolated-site DB testing under distinct authorization. If missing, do not restore/recreate/cleanup or claim ten intact backups; assess coverage of remaining nine and recovery options before any database writes. PRODUCTION and shared DEVELOPMENT stay unchanged.

## Isolated site snapshot count discrepancy: 36 observed versus 40 historically verified — 2026-10-14

**Read-only operator preflight (Docker DEVELOPMENT container):** Verified active application checkout `review/intercompany-approval-failure-tests` at exact SHA `806fa23516490ec7beefcff03a1baa09d722120e` with unchanged `?? AGENTS.md` untracked; isolated site `sites/ccpc-integration2.localhost` exists; private checkpoint directory `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots` exists. However, `find "$SNAP" -type f | wc -l` printed **36**, rather than historically verified **40 protected artifacts from ten sets of four** (see tenth checkpoint post-withdrawal-workflow-pre-stock-entry-fields-20261013 with prefix 20261013_181534-ccpc-integration2_localhost-). This is a genuine **unreconciled discrepancy**; a total count alone cannot identify which specific backup files are absent or whether they were moved/represented differently. Do NOT claim all ten checkpoints still intact based on current output. Backup restoration has never been exercised.

**Safety gate:** STOP before database-backed tests, production/development actions, snapshot cleanup, restoration, new site snapshots, or transactions. First run read-only grouped inventory and metadata/type checks on checkpoint subdirectories and on expected tenth directory; do not print backup contents or any site_config secrets. Determine which specific four files, if any, are actually missing and whether other known directories contain them. Document results and evaluate protected backup integrity/rollback before seeking separate approval for live isolated-site testing. Current prior approval was GitHub code and mocked tests only; no deployment authorized.

## Detached Withdrawal Slip tests green: 12 new security + 35 existing regression — 2026-10-14

**Operator provided the complete successful rerun of the existing 35 mocked Withdrawal Slip regression tests**, under the same detached checkout and verified source rules. Preflight printed `DETACHED APPLICATION SOURCE: VERIFIED`, `DATABASE ACCESS: BLOCKED`, `SITE INITIALIZATION: BLOCKED`, `REGRESSION TESTS DISCOVERED: 35`; all 35 named test methods printed `ok`; summary `Ran 35 tests in 0.030s`, `OK`, `WITHDRAWAL SLIP REGRESSION TESTS: PASSED`. The previous five failures were test-harness mocking defects: the fail-closed NoDatabase fake was updated **in the invocation only** to expose `exists`, `set_value`, and `get_value` blocking placeholders so `unittest.mock.patch` can replace them. No repository application change was required. Alongside the previously independently recorded **12/12** focused security mock test pass on the same feature commit, **47/47 mocked tests across two separate runs passed** with no errors or failures on the corrected runs. They were not one combined invocation.

**Scope and boundaries:** These are **mocked unit/regression tests, not live Frappe integration results**. They do not validate actual Stock Entry posting, Stock Ledger Entries, GL Entries, effective role/DocPerm authorization in the real site, concurrent MariaDB transaction behavior, or rollback of failures. Source and tested detached worktree remain at `85d129e193b32cc229de2e30145359bb3979c257`, active shared DEVELOPMENT worktree remains at `806fa23516490ec7beefcff03a1baa09d722120e` with protected untracked `AGENTS.md`, per most recent guarded test script preflight. No Frappe site initialization, database operation, schema modification, user/permission mutation, deployment, service restart, migration, or production action was requested/performed. GitHub-connected review verified app branch/PR #7 remains draft at `85d129e...`.

**Next milestone is gated separately:** Before database-backed testing, review the isolated site's current readiness and preserved ten snapshot checkpoints with read-only queries only; design minimal authorized synthetic identities/transactions and a two-session duplicate-posting test plus failure/rollback verification. Because both sites share a Frappe app checkout, do **not** change the active app or initiate transactions without an explicit approved scope and a verified method to preserve persistent DEVELOPMENT and PRODUCTION. No mock test result justifies merging/deploying draft PR #7 yet.

## Existing 35 Withdrawal Slip regression tests: 30 passed, five harness mock-setup failures — 2026-10-14

**Operator-provided full second-suite terminal log:** From detached test checkout /tmp/ccpc-material-issue-tests-55f13fb at verified feature SHA 85d129e193b32cc229de2e30145359bb3979c257, guarded Python test harness printed DETACHED APPLICATION SOURCE: VERIFIED, DATABASE ACCESS: BLOCKED, SITE INITIALIZATION: BLOCKED, and EXISTING REGRESSION TESTS DISCOVERED: 35. Existing module ccpcerp.ccpc_erp.doctype.withdrawal_slip.test_withdrawal_slip ran 35 tests in 0.031s; 30 printed ok; five printed FAIL; summary FAILED (failures=5) and WITHDRAWAL SLIP REGRESSION TESTS: FAILED. **This run is NOT a passing regression suite.** No Frappe site or database connection was permitted.

**Five specific fixture-setup failures, not demonstrated application assertions:** test_configured_department_requires_section_on_new_slip; test_full_issue_marks_withdrawal_slip_fully_issued; test_reduced_issue_marks_withdrawal_slip_issued_with_shortage; test_form_defaults_keep_issuer_but_use_personnel_requester; test_new_slip_defaults_requesting_context_from_preparer_personnel. Each failed inside unittest.mock.patch before executing the test body while trying to replace a standard mocked DB attribute on the test runner's NoDatabase object. Missing attributes: exists, set_value, get_value. Python's patch() first tries getattr(frappe.db, attribute), NoDatabase.__getattr__ throws AssertionError ("Unexpected database access"), which prevents patch fixture setup. No evidence yet of actual business assertions failing; success of all 35 is PENDING.

**Next safe action:** Rerun same 35-test site-free harness, changing ONLY the runner's NoDatabase fake to explicitly define blocking placeholders for exists(), set_value(), and get_value(), each raising AssertionError when called without a mock. That allows unittest.mock.patch() to replace and restore them without permitting real DB operations. Retain strict blocking fallback __getattr__, no connection/init, pinned detached SHA 85d129e and live SHA 806fa235, clean detached checkout and active untracked AGENTS.md. No GitHub application code change is needed for this harness-only correction; maintain draft PR #7. GitHub feature and PR remain at 85d129e as reverified through connector.

## All 12 scoped Stockroom Material Issue mocked security tests passed — 2026-10-14

**Operator-provided second focused test run result:** Using only detached test checkout /tmp/ccpc-material-issue-tests-55f13fb at feature commit 85d129e193b32cc229de2e30145359bb3979c257 (fresh Python process with detached import path priority, clean test checkout, expected active base SHA and fake failing DB connection), guarded output printed DETACHED APPLICATION SOURCE: VERIFIED, REAL DATABASE ACCESS: BLOCKED, FRAPPE SITE INITIALIZATION: BLOCKED, TEST CASES DISCOVERED: 12. Every one of the 12 individually named tests in ccpcerp/ccpc_erp/doctype/withdrawal_slip/test_withdrawal_issue_safety.py printed ok, then Ran 12 tests in 0.007s, OK, MOCKED SECURITY TESTS: PASSED. The former five translation-cache/logging errors did not recur after commit 85d129e provided test-only translation mocking. No actual site initialization or database access was allowed by the harness.

**Scope:** These are successful *mocked unit checks* for role/access guard routing, parent-row and submitted/draft SQL FOR UPDATE invocation, pre-existing draft refusal, scoped construction/insert/submit call sequence, stale-slip rejection, and submit exception propagation. They DO NOT verify real multi-session MariaDB serialization, actual Stock Entry submit permissions under active Frappe/ERPNext, transaction rollback, stock ledger/GL, account/cost center requirements, or cancellation/reissue. The older Withdrawal Slip test module was not included in this run. No PR merge, deployment, active shared bench branch change, schema edit, test user, transaction, role change, restore, or PRODUCTION action was performed.

**GitHub verification:** Authoritative feature review branch feature/withdrawal-material-issue-safety and draft PR #7 remain at 85d129e193b32cc229de2e30145359bb3979c257 (connector-confirmed). Continue with a separately guarded run of relevant pre-existing mocked Withdrawal Slip tests from the same detached checkout before proposing DB-backed isolated tests. Protect active app checkout at 806fa23516490ec7beefcff03a1baa09d722120e and untracked AGENTS.md. For next unittest harness, ensure Frappe cache-dependent localization is patched at module boundaries and NoDatabase fails closed; do not claim a success until output checked.

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
