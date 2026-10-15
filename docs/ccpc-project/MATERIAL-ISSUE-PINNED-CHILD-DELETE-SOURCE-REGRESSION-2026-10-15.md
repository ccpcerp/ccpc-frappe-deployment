# CCPC ERPNext — Pinned Frappe child DELETE source regression gate

**2026-10-15 | GitHub-only offline source integrity milestone | no DEVELOPMENT or PRODUCTION execution**

## Narrow question answered

What does the **pinned** `frappe.model.document.Document.update_child_table` source actually instruct Frappe's query builder to do before the first Material Issue is considered?

Reviewed directly from `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`, file `frappe/model/document.py`, **whole-file Git blob `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`**. This milestone does not claim Frappe or PyPika packages are installed in the local Python test workspace; neither SQL rendering nor actual MariaDB execution occurred.

The source creates a child-table query with **all three predicates**:

- `tbl.parent == str(self.name)`: expected owning document name.
- `tbl.parenttype == self.doctype`: owning DocType.
- `tbl.parentfield == fieldname`: target child-table field.

It builds `existing_row_names` using child rows with an existing name that are not `is_new()`. **Only when that list is nonempty**, it adds `tbl.name.notin(existing_row_names)` to the query. A `.delete()` is performed and then `qry.run()` is called under a guard excluding virtual / ignored child doctypes; the method later `db_update()`s each in-memory child row.

**Important distinction:** The source can issue a SQL `DELETE` even when the database removes **zero** rows. A first, newly named Stock Entry's intended empty child-table footprint and expected zero affected rows must be verified with exact isolated-site parent identity, generated SQL/binds and actual affected-row observation, not assumed because the source has predicates.

## Files committed to the existing review branch

- `tests/offline/fixtures/frappe_document_update_child_table_988e54f3.py.txt` — source excerpt extracted **directly** from the pinned GitHub method, without importing Frappe or running any code. Local Git blob and independently re-fetched GitHub blob **`3529d2adde53fc8ebeb2e231b54b49f248b47a95`**. SHA256 **`4a971d4471dc82bdacd7232dc73454a5eff8fcefb30dc8b40a1bb9097f233d9f`**. Fixture commit **`2aa726cd63a8a3d6c03c8feb17dbf796e60f907a`**.
- `tests/offline/material_issue_child_delete_source_guard.py` — **non-executing** `ast.parse` plus SHA256 of the Python AST (not source import/execution), checked against the pinned exact AST fingerprint **`feff34221f70388a6f5802d55f167e6937cd1832aef329404b5ab9a8352d96a6`**. Validates expected three comparisons, retained-name `notin`, query-builder `delete()` and `qry.run()`. Exact Git blob **`c4ea07478850fc2828c1ed691d2aea31a4f57f7a`**; commit **`96c6763abdd54b87a5e77be01147cd1a3f767f97`**.
- `tests/offline/test_material_issue_child_delete_source_guard.py` — 21 independent unit tests, Git blob **`d127c6efba780ca5ec6ccf63d5431956a869cf89`**, commit **`cf8f69c963775820c7c1a751fbcbdfccb2e39883`**.

Local Python **3.13.5**, credential-free:

```shell
PYTHONPATH=tests/offline python -m unittest discover -s tests/offline -p 'test_material_issue_child_delete_source_guard.py' -v
python -m py_compile tests/offline/material_issue_child_delete_source_guard.py tests/offline/test_material_issue_child_delete_source_guard.py
```

**21/21 PASS**, compilation PASS, all three local `git hash-object` SHAs match independently fetched committed GitHub blobs. Source mutations exercised: missing parent/parenttype/parentfield, global WHERE-true substitution, wrong owner, missing or inverted retained-row exclusion, virtual/ignored child guard removal, query-builder DELETE replaced/removed, `qry.run()` moved outside guard, unreviewed COMMIT/SQL added, malformed/unknown input. Comments alone do not affect the AST fingerprint. **A change to the upstream method requires fresh pinning and review rather than a permissive whitelist adjustment.** The AST digest is Python AST representation sensitive; validate against the specified test interpreter, and do not assume cross-version stability.

## Gates still NOT verified

1. **Installed source identity:** actual DEVELOPMENT Frappe/ERPNext/app versions, site hooks and configured child DocType/table and metadata; pinned source cannot establish that deployed code is identical.
2. **Prepared SQL shape and binding:** actual MariaDB-dialect query-builder output; exact bound owner name, DocType, field name, optional retained child IDs and any extra filters; verify at final SQL-driver boundary. The unit tests do not exercise PyPika.
3. **Affected rows and scope:** exact pre/post child primary-key sets and rowcount, verifying **zero unwanted deletions**, not just a syntactically constrained WHERE. Capture any unknown or extra statements as immediate STOP, not permissive update/delete regex.
4. **Other first-posting effects:** initial `tabSeries` key/counter and concurrency; SLE/GL/Bin/Version and auxiliary writes, cache invalidation, global search Redis `lpush`, Redis pub/sub, background jobs, callbacks and rollback.
5. **Containment and recovery:** actual isolated SQL database, distinct or fully contained Redis cache/queue and workers, source-reviewed instrumentation completeness and an independently restorable backup; no silent SQL COMMIT or uncertain outcome.
6. **Authorization:** staging a new diagnostic, new one-off read-only probe or live rollback-only writing test needs **fresh explicit user approval**. Permanent first Material Issue COMMIT and any PRODUCTION operation are separate decisions.

The AST guard **always reports** `generated_sql_text_verified=false`, `bound_arguments_verified=false`, `actual_affected_row_count_verified=false`, `safe_to_stage=false`, `safe_to_rehearse=false`, and `safe_to_commit=false`. This is **source-integrity regression testing**, not a runnable isolation control or executable business transaction.

**Protected originals:** No change to the original posting candidate or review-only v2 with unconditional `exit 1`. No GitHub app code changes, Docker/SQL/Redis/site operations, DEVELOPMENT pull, or PRODUCTION modifications. **Permanent Material Issue: NO-GO.**
