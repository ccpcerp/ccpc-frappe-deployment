# CCPC ERPNext — Second isolated DEVELOPMENT metadata probe: review-only preparation

**Date:** 2026-10-15  
**Authorization:** Owner requested **GitHub-only preparation** after the first owner-approved isolated read-only metadata audit passed and indicated relevant site customizations and Stock Entry Detail searchable fields. **No staging, Docker/SQL access, rollback-only posting, financial COMMIT, PRODUCTION operation or repeat of the first audit was approved.**  
**Current decision:** New probe **SOURCE-PREPARED; NOT STAGED; NOT EXECUTED; syntax/unittest execution pending**. Permanent Material Issue still **NO-GO**.

## Project context and source of truth

- Deployment review branch `review/material-issue-first-commit-preparation-2026-10-15`, prior verified HEAD `b99af73ff9950bbfb5f0126ea738be6249248dde`.
- Pinned application branch `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety`, HEAD `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`.
- First read-only metadata audit, source `ccpc_material_issue_isolated_metadata_readonly_review_20261015.sh`, blob `3dd860d6e254ee361b8f61769fe72ac9dc6a3854`, had one **operator-reported PASS** on the actual isolated DEVELOPMENT MariaDB service. It found **one or more Property Setter / Custom Field rows** among Stock Entry, Stock Entry Detail, Withdrawal Slip and Withdrawal Slip Item; Stock Entry Detail searchable fields present. It did **not** identify which field/property was altered, confirm effective series or runtime Redis state. First audit was consumed and must not be replayed.
- Pinned Frappe `988e54f3c4c291e2077a83809663f123731abe76`:
  - `frappe/config.py` blob `631a79d8283d2ae04f1fb4b95c2da4dba9f0450b` merges `common_site_config.json` first then isolated `site_config.json` (lines 14–46).
  - `frappe/utils/global_search.py` blob `174ee0479160223aa69bc5df3adb924a6afb9b6a` checks `frappe.local.conf.get('disable_global_search')` in `update_global_search`; `frappe.cache.lpush` is a possible pre-COMMIT Redis side effect if content exists.
  - Property Setter schema `frappe/custom/doctype/property_setter/property_setter.json` blob `54a025298ba7e74fe13b3cb6bc3e2b4af8440dc3` verifies `doc_type`, `field_name`, `property`, `property_type`, `value`.
  - Custom Field schema `frappe/custom/doctype/custom_field/custom_field.json` blob `f46773903801b1f106e5df17c58ad588444b3635`, and DocField schema `frappe/core/doctype/docfield/docfield.json` blob `08f80b005a0380598cf1e5f5a203ca4b992ad46d` both expose `in_global_search`.
  - Frappe `frappe/model/naming.py` blob `84e9ad01eb934d4ebaf60e608cf039eb15f1dbc4` implements naming-series allocation and possible `tabSeries` INSERT/UPDATE. Stock Entry pinned ERPNext JSON `181def4fd4a9cd6a2c72ff9f6ccbfc5f55921fe7` uses `autoname: naming_series:` and Stock Entry `naming_series` options `MAT-STE-.YYYY.-`.

## New source artifacts committed to GitHub, NOT executable without fresh owner approval

**New operator probe:**
`scripts/development/operator/ccpc_material_issue_isolated_customizations_readonly_review_20261015.sh` created commit `a0d1a9be4fbb63606169c8d907f70c5303b0d3c4`; corrected empty/NULL DocType Property Setter override keys at commit `7729282a04a8680505dc35f4962be8a451d1b4b8`; resulting Git blob **`d13f605876eb669b404179a52e6e084c4031f191`** (10,263 bytes). Its **distinct** `CCPC_METADATA_DETAILS_APPROVED=ccpc-isolated-metadata-details-once` script-level gate is *not* equivalent to owner approval. Do not stage or execute yet.

**Offline source-contract suite:** `tests/offline/test_material_issue_customizations_probe_contract.py`, created commit `2e8bc4cbd455254973fc8a49c0fa1501fa912f32`, Git blob **`60ae76a2570a473bba441546a07a0c2b95a6922e`** (6,243 bytes). Contains eight `unittest` methods for Bash/Python syntax, gate/DEV container, static SQL-only, sanitized identifier/pattern output, three-way config-file flag, and no PROD/financial action. **Not yet executed** against exact source, so no test PASS claimed.

## Read-only design and restricted output

- Fails closed if not explicitly approved, root user, missing or unexpected DEV Compose Frappe container, absent/untrusted site config, config mismatch or non-`mariadb:3306` endpoint. Uses `ccpc-integration2.localhost` for the only SQL connection and reads `development.localhost` config **solely** to ensure a distinct database name.
- Connects via `MySQLdb` without Frappe initialization and opens `START TRANSACTION READ ONLY`; verifies `SELECT DATABASE()` equals the expected isolated configured name. Permits only fixed, parameterized `SELECT` statements, then rolls back/closes. Does not run SQL COMMIT, write config/backup, post stock/GL, initialize Frappe, publish Redis, manipulate Docker lifecycle or touch PRODUCTION.
- Restricted output: Property Setter **DocType, field-name, property-name, property-type**; Custom Field **DocType, fieldname, fieldtype**; only safely escaped/whitelisted identifier characters, each record count bounded at 80. Does **not print arbitrary Property Setter values, business data, SQL rows, site credentials, database names, document IDs or counter values.**
- Targeted Stock Entry naming source: reads base `tabDocType.autoname`, base `tabDocField.naming_series` options/default and `tabProperty Setter.value` **only** for `Stock Entry` DocType autoname or `naming_series` options/default overrides, redacting nonstandard patterns. Handles both NULL and empty `field_name` on DocType-level overrides. Reports whether `MAT-STE-%` naming-counter row(s) exist, **not** the count/current value/key.
- Global-search file flag: reads `disable_global_search` from a common-then-isolated JSON merge and reports disabled/not-disabled/unknown-format status. Lists base and custom searchable Stock Entry Detail field **names**, but does not initialize Frappe or examine Redis. This is **config-file evidence only**, not definitive proof of active runtime hooks, queue operations, customized effective Meta, or whether a future transaction produces searchable content.

## Static checks, execution status, and next gate

Connected GitHub refetch confirmed the new script and test blobs. Source-structure predicate checks PASSED for owner-approval gate before Docker, expected DEV-only Compose labels, exact isolated database/host checks, read-only transaction without SQL COMMIT/Frappe, safe-value output controls, site-over-common config merge, NULL/empty setter handling, original first audit unchanged, and the first-commit **inert** v2 candidate's `exit 1` intact. The eight tests contain no DB/Frappe import or executable shell run and were reviewed as source only.

**Evidence limit:** Static predicates are **not** `bash -n`, embedded `ast.parse`, executed unit tests, live metadata results, effective naming selection, network isolation, or recovery/transaction validation. Before any future operator staging, execute `bash -n`, Python AST parse, and the exact committed source-contract suite in an isolated credential-free environment; correct any failures via reviewed GitHub commits, re-pin SHA256 and provide a new stage-only procedure **only after separate owner consent**. Execution of the distinct probe then requires **another** explicit user authorization. Keep both commit-capable posting candidates NO-GO. Never use first audit's one-time approval again; no PRODUCTION activity.
