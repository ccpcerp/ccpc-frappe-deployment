# CCPC ERPNext — First Material Issue source-level naming, child-row and search side-effect trace

## Operator-reported isolated metadata read-only audit PASSED; relevant customizations FOUND — 2026-10-15

**Exact permission and provenance:** After explicit owner authorization to execute the **one** newly staged read-only metadata probe, operator supplied these eight sanitized output lines:

```text
ISOLATED DEV METADATA CONNECTION CONFIG: VERIFIED
ACTUAL ISOLATED DEV DATABASE: VERIFIED
DOCTYPE NAMING AND CHILD GLOBAL SEARCH METADATA: READ
STOCK ENTRY DETAIL SEARCH FIELDS: PRESENT
RELEVANT SITE CUSTOMIZATIONS: PRESENT - REQUIRE REVIEW
STOCK ENTRY NAMING SERIES COUNTER: COUNTED (VALUE NOT PRINTED)
NO FRAPPE INIT, SQL WRITES, STOCK/GL, BACKUP OR PRODUCTION ACCESS
ISOLATED METADATA READ-ONLY AUDIT: PASSED
```

**Audited source:** `scripts/development/operator/ccpc_material_issue_isolated_metadata_readonly_review_20261015.sh`, Git blob `3dd860d6e254ee361b8f61769fe72ac9dc6a3854`, SHA256 `d38a617a23a91bb008a1f794ac5f9f179097e9b98ea3b1f54fc4109cda56aa32` from branch `review/material-issue-first-commit-preparation-2026-10-15` at pre-staging pinned commit `4af5c269e20dbf490fb0390e9e109167147d6286`. Staging and source SHA256/syntax checks were previously reported PASSED before this separate explicitly approved invocation. Connected GitHub re-fetched the same audited source blob and review branch HEAD. **Runtime evidence is operator-reported**, not independently observed by ChatGPT.

**Narrow interpretation:**
- The probe's actual isolated MariaDB database identity matched `ccpc-integration2.localhost` site configuration, with expected `mariadb:3306` DEVELOPMENT endpoint and shared DEV database `db_name` distinct by configuration. No connection to shared DEVELOPMENT SQL or PRODUCTION SQL is in the script.
- All six checked `tabDocType` rows and the Stock Entry `naming_series` base DocField row were available, but the probe **did not print autoname or naming-series options**; it does not prove effective Stock Entry numbering or the next naming series counter value.
- At least one `tabDocField` in **Stock Entry Detail** has `in_global_search=1`. This makes the pinned `update_global_search` / `frappe.cache.lpush` source path relevant, but **does not prove** effective global search is enabled for this site, that a Redis event occurred, or whether child search fields were actually populated on the synthetic issue.
- `RELEVANT SITE CUSTOMIZATIONS: PRESENT` means **at least one** `tabProperty Setter` row for `Stock Entry`, `Stock Entry Detail`, `Withdrawal Slip` or `Withdrawal Slip Item` **OR** one `tabCustom Field` row for those DocTypes exists. It does **not** identify which DocType, which property, its value, or whether it alters stock/financial behavior. Reviewing the specific override *names/categories* without exposing sensitive business data is the next missing metadata step.
- The `tabSeries` query simply returned a `COUNT(*)` for a `MAT-STE-%` name pattern and deliberately **never printed its value**, so the output does **not** indicate whether matching counters exist, nor the selected prefix or next sequence number.
- Audit printed `NO FRAPPE INIT, SQL WRITES, STOCK/GL, BACKUP OR PRODUCTION ACCESS` and final PASS. Exact script opens `START TRANSACTION READ ONLY`, executes fixed SELECT queries, then rolls back/closes. No permanent Material Issue/Stock Entry/GL posting was performed by this audit, and it does not verify backup restore or transaction callback isolation.

**Decision / next gate:** **NO-GO remains** for the original commit-capable candidate and early-exit inert v2; do NOT loosen `tabSeries`/DELETE/Redis guards or make a trial COMMIT based on this result. Review site-specific *relevant customization metadata, naming selection, and global-search enabled/disabled state* through **new separately authorized isolated read-only-only analysis** before designing a **new** separately approved rollback-only integration trace. Do not run or modify the prior one-time probe repeatedly; treat its approved execution as used. PRODUCTION requires completely separate explicit authorization.

## Exact GitHub-blob offline metadata probe contract tests PASSED — 2026-10-15

After initial GitHub staging as a **source-only review artifact**, the newly created metadata probe and its test suite were reconstructed locally in a credential-free, isolated model test workspace, **then independently matched by `git hash-object` to the exact connected-GitHub blobs**:
- `scripts/development/operator/ccpc_material_issue_isolated_metadata_readonly_review_20261015.sh` — **`3dd860d6e254ee361b8f61769fe72ac9dc6a3854`**, 6,508 bytes.
- `tests/offline/test_material_issue_metadata_probe_contract.py` — **`6c396b5045b994d09128a837dfa92755839bc938`**, 3,117 bytes.

**Executed only offline on exact source:** `bash -n` PASSED, embedded Python `ast.parse` PASSED, and `python3 -m unittest discover -v -s tests/offline -p 'test_material_issue_metadata_probe_contract.py'` reported **5 tests, all PASS**. These check approval and exact DEV container preconditions, only fixed SELECT metadata calls, one read-only SQL transaction without a commit call, absence of Frappe/stock posting and Docker lifecycle operations. An **unarmed local** shell invocation with the approval variable absent exited **1** with `NOT AUTHORIZED: read-only metadata probe not approved` before accessing Docker.

**Boundary:** These are exact-source syntax/source-contract tests, **not** a live database readback, proof of effective site naming, runtime Docker inspection, or permission to execute. The script was **not staged or run on the user's Ubuntu server**; its real metadata output and actual site overrides remain UNKNOWN. Any authorized future run still requires one separate scoped owner approval and checksum-verified manual staging; the probe's environment variable by itself is not equivalent to authorization. No financial COMMIT or PRODUCTION action follows from this PASS.

**Date:** 2026-10-15  
**Scope:** GitHub source inspection and preparation of a separate, bounded **read-only** isolated-DEVELOPMENT metadata probe. No runnable posting candidate was changed or executed.  
**Disposition:** **NO-GO for one-unit committed posting.** An existing 12/12 offline test pass covers only isolated v2 guard/helper behavior, not live ERPNext/Frappe write paths.

## Immutable sources read directly through connected GitHub

- CCPC feature `ccpcerp/ccpcerp` branch `feature/withdrawal-material-issue-safety`, HEAD `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`; posting handler `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` blob `771d27781f8d933fd243415e8286976fbdd1a861`.
- Pinned Frappe `988e54f3c4c291e2077a83809663f123731abe76`: `frappe/model/document.py` blob `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`; `frappe/model/base_document.py` blob `65fa116d3e1725ee806ac469a9905122f25b586f`; `frappe/model/naming.py` blob `84e9ad01eb934d4ebaf60e608cf039eb15f1dbc4`; `frappe/query_builder/utils.py` blob `0b3a2f315346f9813717f8d201b9546989da2761`; `frappe/utils/global_search.py` blob `174ee0479160223aa69bc5df3adb924a6afb9b6a`.
- Pinned ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`: Stock Entry schema `erpnext/stock/doctype/stock_entry/stock_entry.json` blob `181def4fd4a9cd6a2c72ff9f6ccbfc5f55921fe7`; Stock Entry Detail schema blob `d30910461a6d0558dd209549a2432ab1374a27ab`; `erpnext/stock/doctype/stock_entry/stock_entry.py` blob `e699594f5ba7ec3021e74c4d7837c3f7c232b56c`; `erpnext/accounts/general_ledger.py` blob `a4018f50f61a375438c8702690112e14a474870a`; `erpnext/accounts/utils.py` blob `c5feb863f38bd63259d334cd6518b1aad0aa0821`.
- Local source metadata from GitHub, **not from running ERPNext on the actual site**: Stock Entry JSON `autoname = naming_series:`, `track_changes = 1`, naming-series field with upstream `MAT-STE-.YYYY.-` options; Stock Entry's `items` table is `Stock Entry Detail`, additional costs is `Landed Cost Taxes and Charges`. Stock Entry Detail has `in_global_search` for `item_code` and `item_name`; Withdrawal Slip JSON `autoname = naming_series:`, `track_changes = 1` and an `items` child table.

## Exact write-path review (all conditional on actual site metadata/fixtures)

| Step / source | Confirmed possible effect | Why current inert v2 remains NO-GO |
|---|---|---|
| Stock Entry naming: `frappe/model/naming.py` lines 185–198, 210–233, 408–423 | With naming-series selection and absent overriding custom rule, `getseries()` locks and `INSERT`s or `UPDATE`s `tabSeries`. | V2 intentionally denies all `tabSeries` DML. This is a genuine compatibility blocker; do **not** simply allow all counters. Need actual selected series/prefix and before/after counter invariant. |
| Withdrawal Slip `save()`: Frappe `document.py` lines 559–612 and 647–688 | `db_update()` of parent; each table-field sync builds a query-builder `DELETE` for absent child rows, then child `db_update()`. DELETE may affect zero rows but is still issued. | V2 denies every DELETE, so normal child synchronization may be rejected if the SQL proxy observes it; if not observed, interceptor coverage is incomplete. Do not loosen until generated SQL and exact row predicates are independently traced. |
| Query-builder `.run()`: `frappe/query_builder/utils.py` lines 133–152 | Calls `frappe.local.db.sql(query, params, ...)`. | Verify whether v2's patch of `frappe.db.sql` observes every actual query-builder and connection alias in the isolated Frappe runtime. Static source alone is not a complete interception guarantee. |
| Stock Entry `insert()`: Frappe `document.py` lines 473–514 | Calls `set_new_name`, then parent `db_insert` and every child `db_insert`; `base_document.py` lines 728–776 emit raw `INSERT INTO tab{doctype}`. | Child table and naming writes need exact post-rollback deltas; document-level monkeypatches cannot prove complete DML. |
| Stock Entry `submit()`: ERPNext `stock_entry.py` lines 580–610 | Conditional reservations, pick lists, Work Orders, SLE/Bin, GL, stock reposting, project, inspections and other effects. | Many branches may be inactive for clean synthetic fixture, but the source does not establish the exact active subset. |
| GL posting: `general_ledger.py` lines 29–60 and 426–443, `accounts/utils.py` lines 1991–2086 | GL submit and budget validation; `create_payment_ledger_entry` is called for non-cancelled GL and filters receivable/payable GL accounts for actual Payment Ledger records. | Synthetic adjustment/inventory accounts are not expected to be receivable/payable, so a Payment Ledger write is **not demonstrated**, but the branch must be audited rather than assumed absent. |
| Document after-save: Frappe `document.py` lines 1445–1475, 1493–1513 | `notify_update` queues doc/list realtime events after COMMIT; `save_version` may create `tabVersion` when change tracking applies. | Suppression of selected realtime events is not a general non-SQL side-effect control; Version changes require exact document/ref allowlist and delta checks. |
| **Global search:** Frappe `document.py` line 1470, `global_search.py` lines 242–286, 425–432 | When global search is enabled and searchable data exists, `update_global_search` calls `sync_value_in_queue`, which performs `frappe.cache.lpush('global_search_queue', ...)` in Redis **before SQL COMMIT**. On Redis ConnectionError, `sync_value` can instead write `__global_search` SQL (lines 435–467). | **New concrete B3 blocker.** V2's `frappe.publish_realtime`/enqueue shim does not intercept global-search `frappe.cache.lpush`. SQL rollback cannot undo an already queued Redis event. Stock Entry Detail has searchable item fields, increasing relevance; actual site `disable_global_search` and doc contents must be checked before any rehearsal. |
| Conditional follow-created-documents: Frappe `document.py` lines 524–526 | May invoke `_follow_document` depending on acting user's preference. | Needs real test User configuration inspection and scoped side-effect tracing; source alone does not prove active. |

### Important evidence limits

These are **source-supported potential behaviors**, not proof each occurred on the isolated site's previous rollback-only diagnostic. No live COMMIT and no source changes to `ccpcerp/ccpcerp` occurred. The installed site can have Property Setters/Custom Fields, naming rule overrides, settings and stock-module conditions different from the pinned DocType JSON. A read-only metadata pass can tell us base stored values and whether overrides exist; it **cannot** establish every effective runtime hook or SQL/Redis operation.

## New isolated SQL read-only metadata probe — created, NOT RUN

- Operator candidate (deployment review branch): `scripts/development/operator/ccpc_material_issue_isolated_metadata_readonly_review_20261015.sh`, Git blob `3dd860d6e254ee361b8f61769fe72ac9dc6a3854` (6,508 bytes), created at commit `6289324d2142d74ce5f42d27d101a3127c878db4`.
- Offline source-only safety-contract suite: `tests/offline/test_material_issue_metadata_probe_contract.py`, Git blob `6c396b5045b994d09128a837dfa92755839bc938` (3,117 bytes), created at commit `f6754961451749dbb65356b5a8ed4fc59a290c91`.
- The operator probe requires an explicit scoped approval value **in addition to owner's actual approval**, checks only the one expected DEVELOPMENT Compose Frappe container, reads isolated and shared DEVELOPMENT site config `db_name` keys but **no shared-development SQL records**, refuses non-`mariadb:3306` endpoints, opens `START TRANSACTION READ ONLY` against isolated `ccpc-integration2.localhost`, performs only seven fixed SELECT-based metadata queries, prints sanitized categories/count-status (not DB names, counter names, passwords, document values, SQL rows, or custom-field details), and rolls back/closes. It does not import Frappe, post stock or GL, touch PRODUCTION, modify backups, change Docker or perform a SQL COMMIT. Count/field results are *indicative*, not complete effective metadata resolution.
- **Status:** GitHub blob/source structure read back and nonmutating source predicates checked; **exact GitHub script has not been syntax-checked by `bash -n` or AST-parsed on Ubuntu, the new test suite has not been executed, and the metadata probe has never run**. Do not claim it has passed a live audit. Stage/syntax-check in a separately reviewed operator procedure, then request explicit one-run user approval before any read-only execution. No permission for any commit-capable script.

## Next gates

1. Validate exact pinned metadata-probe Bash/Python syntax and run its five offline contract tests **without executing the probe**; correct any source defects through the GitHub review branch and re-pin bytes.
2. Once a separate owner approval is granted, stage-only from immutable reviewed branch and SHA256, then execute one read-only isolated metadata query with its own separate approval.
3. Use the result to design a **new, separately authorized rollback-only** write/callback trace. Check all table deltas including `tabSeries`, `tabVersion`, child rows, Bin, SLE, GL, `__global_search` and active Redis/cache operations. Do not replay consumed rollback diagnostic.
4. Keep permanent one-unit stock/GL posting **NO-GO** until end-to-end transaction/recovery review and a new explicit posting authorization. PRODUCTION remains untouchable without separate approval.
