# CCPC ERPNext — First Material Issue transaction-effect boundary design (source-only)

## New inert exact-SQL effect witness and 14 offline tests PASSED — 2026-10-15

**Owner scope:** “Approved Continue” was interpreted as **GitHub-only** design, source audit and offline tests, *not* permission for an isolated DEVELOPMENT rollback-only script or any PRODUCTION operation. The prior live read-only audits were one-run consents already used. The original v2 retains its unconditional `exit 1`.

**Committed offline-only Python module:** [`tests/offline/material_issue_effect_witness.py`](../../tests/offline/material_issue_effect_witness.py), created review commit `047bdc8326f3ae2ba883433489bd46c5cba32618`, blob **`ba56262cc1adf0f9d995687de288cf8b3845df54`**, SHA256 **`5e4aa02ba642824e8e8aa287bfb6082c5c3d04038f70914577e5371451fe3706`**. It implements a **model**, NOT an SQL interceptor/executor: an immutable hypothetical site/key/counter baseline, exact SQL text + bound-param equality against the two pinned Frappe `getseries()` DML spellings, one-statement-only rejection, and unconditional refusal of any declared Redis/cache/realtime/background effect. It **never** returns `safe_to_execute` or `safe_to_commit` true, even when the expected series SQL matches.

**Exact tested companion:** [`tests/offline/test_material_issue_effect_witness.py`](../../tests/offline/test_material_issue_effect_witness.py), review commit `9e9ec6f323ec5ccfda448f5a398759bfd760a58b`, blob **`ea9640270bbc189c40a564fe53e37a942cf79cc9`**, SHA256 **`99cb905f041cc98eaec17de4126ab332f5b4c9fe1cf6637bedf2b2ec0349a38e`**. Both GitHub re-fetched blob SHAs matched exact local files via `git hash-object`; source/test Python compile PASS and **14/14 unittest methods PASS** in the credential-free isolated local workspace. Tests reject wrong site/year/key, malformed baselines, broad `WHERE 1` updates, any child DELETE, unexpected/multiple series statements, mixed/comment SQL, list/extra parameters and all external-effect labels. A matching synthetic insert or increment is **not** permission to actually execute it. The prior 19 offline NO-GO tests were a separate earlier milestone; this 14-test count is new and must not be confused with DB integration.

**Hard limitations and next engineering steps:** This module does not connect to or instrument Frappe, MySQLdb, query builder, Redis, cache, filesystem or Docker; it does not observe real production/development SQL or inspect actual DB contents. The `MAT-STE-2026-` in unit tests is **synthetic**, not the current runtime naming key or series allocation. The `current=None` model assumption is a reviewer-provided fixture, not a recent transactional counter readback; existing-counter races remain unresolved. Real query-builder child SQL and actual bind parameters are not captured; **all child DELETEs remain rejected**. No global-search/cache side-effect suppression is implemented or validated; the model merely refuses an explicitly reported external effect and could miss effects not observed. SQL formatting from a framework update may differ and is correctly treated as unreviewed. Unknown business-document, ledger, Version, Bin and callback paths are unmodeled.

**Future gate:** First design *capture coverage* for all Frappe SQL driver/query-builder paths and non-SQL global-search/cache/queue callbacks, and a full transaction-local invariant plan that guarantees no shared-state side effects before considering any live rollback-only diagnostic. Do not attach this offline witness to a live code path, remove v2's early `exit 1`, stage/run either candidate or widen its SQL allowlist without a separate reviewed design, explicit owner permission and recovery readiness. **Permanent 1 Nos Material Issue COMMIT remains NO-GO.**

**2026-10-15 | Review branch:** `review/material-issue-first-commit-preparation-2026-10-15`  
**Scope:** GitHub-only verified framework/application source tracing, isolated offline tests, acceptance criteria for a *future separately approved* rollback-only DEVELOPMENT rehearsal. **This document is not an executable change, a release sign-off, or owner approval for a live transaction.**  
**State:** **NO-GO** for persistent first Material Issue; **NO-GO** for any new live write-then-rollback test until the effect isolation and recovery plan is explicitly reviewed and approved. Original commit-capable runner and inert v2 unchanged.

## Verified source and live metadata basis

Authoritative GitHub app feature `ccpcerp/ccpcerp` at `feature/withdrawal-material-issue-safety`, head `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`. Pinned `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` blob `771d27781f8d933fd243415e8286976fbdd1a861`, especially lines 102–144, 177–202 and 321–370. Handler builds a new Stock Entry, does **not explicitly assign `naming_series`**, and performs `stock_entry.insert(ignore_permissions=True)` then `stock_entry.submit()` with ordinary ERPNext hooks. It links Stock Entry and its rows to a Withdrawal Slip and updates Slip/child issue status via normal data paths. No owner-approved stock/GL posting has occurred.

Two previously authorized, one-time, isolated DEV read-only metadata audits were reported PASS by the operator; **both consents are consumed**. The second audited source `scripts/development/operator/ccpc_material_issue_isolated_customizations_readonly_review_20261015.sh` Git blob `d13f605876eb669b404179a52e6e084c4031f191`, SHA256 `9a026738074f31e790186fc9156ab5755baab06c351b22ad9db399a006db72d0`. It found four `hidden` (type `Check`) Property Setter **names**, but did *not* read their boolean values, three Withdrawal Slip traceability Custom Fields, Stock Entry base naming series `MAT-STE-.YYYY.-` with no naming override, no `MAT-STE-%` rows in `tabSeries`, Stock Entry Detail searchable `item_code,item_name`, and `disable_global_search` **NOT_DISABLED_BY_CONFIG**. These are operator-reported metadata results, **not** proof of active Redis writes or transaction path.

**Relevant pinned Frappe commit:** `988e54f3c4c291e2077a83809663f123731abe76`:
- `frappe/model/naming.py` blob `84e9ad01eb934d4ebaf60e608cf039eb15f1dbc4`, lines 260–268, 326–387, 408–423, 481–489.
- `frappe/model/document.py` blob `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`, lines 473–514, 647–688, 1445–1480, 1588–1611.
- `frappe/query_builder/utils.py` blob `0b3a2f315346f9813717f8d201b9546989da2761`, lines 133–140 (query builder calls `frappe.local.db.sql`).
- `frappe/utils/global_search.py` blob `174ee0479160223aa69bc5df3adb924a6afb9b6a`, lines 242–286, 425–467.
- `frappe/database/database.py` blob `a2ba78e2488f03810d58c43c768b4fbab624c3dc`: before/after commit callback registration around lines 129–130; commit/rollback around 1176–1203.
- Pinned ERPNext Stock Entry DocType JSON blob `181def4fd4a9cd6a2c72ff9f6ccbfc5f55921fe7`: autoname `naming_series:`, option `MAT-STE-.YYYY.-`.

## B2 — Missing naming counter: fail-closed write constraints needed

**Observed:** isolated site's `tabSeries` contains no row whose `name LIKE 'MAT-STE-%'` at audit time. Naming source `set_name_by_naming_series` uses first truthy meta option when unset; `parse_naming_series` generates an effective prefix from the site-local calendar year; `getseries()` performs `SELECT ... FOR UPDATE`, then `INSERT INTO tabSeries (name,current) VALUES (%s,1)` if absent (or `UPDATE` existing row).

**Derived only under the assumed 2026 default path:** The model-generated prefix is `MAT-STE-2026-` and an initial 5-digit value may appear; **do not assume the actually selected prefix, date, prior counter absence at commit time, or actual next name without current readback and runtime hook checks.** Alternate naming rules, fixture dates, hook overrides and concurrent issues could change behavior.

**Future separately authorized rollback-only trace must ensure all of the following**, not merely permit an INSERT table name:

1. Start with a pinned readback of **actual selected series**, full relevant `tabSeries` key set and counter state in the same isolated transaction, with a one-unit fictional fixture and no matching existing submitted/draft issue.
2. If a counter row truly does not exist, permit **at most one** exact expected-key `tabSeries` INSERT with **`current=1`** and no other name-series mutation. If a row exists, require an exact expected-key increment with baseline/after comparison. Never globally allow `tabSeries` writes, dynamic key prefixes or retry after ambiguous COMMIT.
3. Verify new Stock Entry `name` equals the expected resolved prefix+formatted counter and links to exactly the target synthetic Withdrawal Slip. Reject any unexpected series writes, other DocTypes, or cross-site keys; concurrency/idempotency and missing-row collision behavior must be reviewed independently.
4. For a rollback-only rehearsal, check SQL state and any non-SQL effects **before and after rollback**; no increment, Stock Entry, stock ledger, GL, child/status, or queued external side effect may survive. Reject even if SQL rollback succeeds but cache/queue mutations remain uncontained.

Current v2 `review_dml_scope` rejects `tabSeries` INSERT/UPDATE; do **not** remove its unconditional `exit 1` or expand allowlists based on this design.

## B2 — Child synchronization DELETE and row-predicate integrity

`Document.update_children()` calls `update_child_table()` for each table field. Pinned code builds a query-builder DELETE with **`parent == self.name`**, **`parenttype == self.doctype`**, **`parentfield == fieldname`** and, for existing child rows, **`name NOT IN existing_row_names`** (Document lines 647–688). Thus a normal Slip `save()` *can issue a DELETE even when it deletes zero rows*. Child docs then `db_update()`.

Required future source/runtime evidence before allowing any one DELETE:
- Capture the **generated parameterized SQL and arguments**, not just a regex on the table name. Confirm target is exactly `tabWithdrawal Slip Item` for the locked Slip (or another explicitly traced child table for this one fixture), with matching parent, parenttype and parentfield, and **no child names removed**; reject parentless, wrong-site, broad, or destructive SQL.
- Compare child primary-key sets, parent field, quantities, version/modification flags before/after. For this fictional full-item issue, an unchanged child name set is expected; any removal requires STOP and new explicit owner review, not auto-allow.
- Stock Entry child creation is via document `db_insert`; do not conflate that with subsequent Slip child synchronization. Review all other child tables, `tabVersion`, and any auxiliary DocType writes based on the actual flow.
- V2 presently rejects **every DELETE**, so a clean source-path acceptance criterion cannot be satisfied by v2. Its `UPDATE ... WHERE 1` passes the current regex even without row identity, proving the v2 check is **not row-scoped protection**. Replace with independently validated statements/parameter predicates or verified pre/post invariants in a *new* explicitly reviewed diagnostic; do not claim the regex is complete.

## B3 — Global search is a pre-COMMIT external side-effect boundary

Pinned `Document.run_post_save_methods` invokes `clear_cache`, `notify_update`, `update_global_search`, `save_version`, `on_change`. `update_global_search(doc)` checks `disable_global_search`; when searchable parent or child content exists, `sync_value_in_queue` calls **`frappe.cache.lpush('global_search_queue', json.dumps(value))`** immediately. On Redis `ConnectionError`, the fallback `sync_value` attempts **`__global_search` SQL INSERT ... ON DUPLICATE KEY UPDATE**. Neither a normal database ROLLBACK nor suppressing just `frappe.publish_realtime` guarantees no Redis mutation. Cache clearing itself may affect shared keys before COMMIT.

**Mandatory before any live write-then-rollback rehearsal:**
- Independently verify process-local effective `disable_global_search`, document/search-content activation, Redis/cache targets, all Frappe hooks and monkeypatch targets. A file-config `NOT_DISABLED_BY_CONFIG` result is not proof of a particular runtime `frappe.local.conf`; avoid assuming disabled.
- **Do not turn off global search persistently on shared DEVELOPMENT or PRODUCTION, flush Redis, clear shared caches, or redirect live production infrastructure.** Design either a fully isolated throwaway cache/queue endpoint and verify exact routing, or a source-reviewed fail-closed, process-local interception of *all* global-search/cache mutations and SQL fallback. A simple `publish_realtime`/enqueue suppression is insufficient.
- Require a zero-external-side-effect observation (or exact safely isolated reversible effect) before/after the rollback, including `global_search_queue`, cache invalidation, realtime callbacks and queued background jobs. If coverage is incomplete or effects are discovered, STOP; no assumption that ROLLBACK reverted them.
- Trace Frappe commit/rollback callbacks and any document hook file/system effects separately. No live test is authorized solely from this description.

## B1/B4/B5/B6/B7 — Transaction, endpoint, backup and duplicate-post safeguards

The prior v2 helper tests cover narrow mock/isolated guards, not a fully proven integration transaction. Before any write-capable diagnostic:

1. Verify the exact DEVELOPMENT site/DB/Compose service and guard against all shared-DEV/PRODUCTION access even when Docker environments share infrastructure. Preserve Git working status and pending changes.
2. Account for `tabStock Entry`, `tabStock Entry Detail`, `tabWithdrawal Slip`, `tabWithdrawal Slip Item`, `tabSeries`, `tabStock Ledger Entry`, `tabGL Entry`, `tabBin`, conditional `tabVersion`, conditional Payment Ledger and all other actual auxiliary tables.
3. Review permissions, item valuation, stock balances, GL debit/credit equality, immutable ledger, transaction rollback behavior and intercompany impact; current expected synthetic one-SLE/two-GL footprint is **historical, unverified for newly traced branch conditions**.
4. Verify independent backup/restorability and non-shared-state recovery. Backup file hashes alone do not prove restoration; no production restore/deployment is authorized.
5. Define stop/inspection/recovery actions for signal loss and uncertain COMMIT outcome. Do not retry transactions automatically, edit series counters to repair a rehearsal, or restore over user data.
6. Separate owner approval for a **rollback-only isolated DEVELOPMENT** diagnostic from any much later **permanent** one-unit COMMIT. Production requires its own backup/rollback plan and explicit permission.

## New exact-source OFFLINE blocker-characterization test evidence

- Inert V2 source: `scripts/development/operator/ccpc_material_issue_first_commit_review_only_v2_20261015.sh`, exact Git blob **`0a17d53cc0badac1de05745ef9edfb60d342ed89`**, hard unconditional `exit 1` before Docker.
- New suite: `tests/offline/test_material_issue_first_commit_blockers_contract.py`, exact Git blob **`27ec2374d14d93cf471e1661ae2d88ea56a2037a`**, SHA256 **`64c86d3d6a4ca8b997b611d0d356b74f01b600c450566435f2446ff99aeff063`**. Created then corrected backtick-escaping to byte-match the exact local tested file at GitHub commit **`014cbb981c94d84ff219611ec7575358e23b8954`**.
- Credential-free local offline commands with both SHA-matched files: `bash -n` and embedded Python `ast.parse` **PASS**; previous **12/12** v2 offline tests PASS; **7/7** new NO-GO-characterization tests PASS (19 total). New checks verify absent `tabSeries` allowed targets, child DELETE denial, unknown table denial, early STOP, absence of a precommit `cache.lpush` interceptor, and importantly **demonstrate that `UPDATE tabBin ... WHERE 1` and `UPDATE tabGL Entry ... WHERE 1` still pass the provisional regex**.
- **These tests PASS because known NO-GO gaps are detected; they do NOT indicate first-commit posting safety.** No server, Docker, SQL, Redis, Frappe, stock or GL transaction executed.

## Next source-only development gate

Design a **new, isolated, separately owner-reviewed rollback-only diagnostic** that can capture/validate exact parent/child and naming-series SQL with true row/parameter scoping and can guarantee zero unreviewed external effects. Do not stage/run it or change v2's unconditional stop until new owner approval. Continue independent pinned-source analysis of cache clearing, notification/callback manager, naming concurrency and ledger auxiliary paths. The first actual one-unit stock/GL COMMIT remains **NO-GO**; PRODUCTION must never be modified by a GitHub review commit.
