# CCPC ERPNext — Query-builder named SQL bind correction and first-issue evidence requirements

**2026-10-15 | GitHub-only pinned-source correction | NO-GO for live rehearsal, permanent Material Issue posting and PRODUCTION**

## Why this correction was required

Earlier `tests/offline/material_issue_capture_coverage.py` required all hypothetical SQL events to have a **tuple** of binds. That was overrestrictive for the **actual pinned Frappe query-builder code**. The earlier 16/16 tests passed as tests of that model, but the model's assumption did **not** reflect Frappe's query-builder named-parameter path. This correction is not a claim that earlier unit tests established production safety.

Inspected exact pinned source `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`:

- `frappe/query_builder/terms.py` blob **`a042d407784b7cd522e17ce165247188a667d228`**: `NamedParameterWrapper.get_sql()` constructs placeholder `%(paramN)s` and stores the associated value in `self.parameters`, a dictionary. `ParameterizedValueWrapper.get_sql()` may pass an SQL-rendered / quoted form for string values, so a reviewer **must not assume** a bind value is necessarily the original raw document string. The exact output still depends on pinned PyPika and runtime configuration.
- `frappe/query_builder/utils.py` blob **`0b3a2f315346f9813717f8d201b9546989da2761`**: `prepare_query(query)` returns generated SQL plus **`param_collector.parameters` (dict)**. `execute_query` sends those two to `frappe.local.db.sql(query, params)`.
- `frappe/database/database.py` blob **`a2ba78e2488f03810d58c43c768b4fbab624c3dc`**: `Database.sql` normalizes and may transform the SQL/binds before calling `Database.execute_query` and its underlying driver cursor. A high-level captured pair and the final cursor pair are **not automatically interchangeable**.
- `frappe/model/document.py` blob **`e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`**: `update_child_table` builds the parent/parenttype/parentfield query-builder DELETE and optional `name NOT IN` retained-child predicate. **Neither PyPika rendering nor MariaDB row count has been observed.**

### Fixed review-only coverage model

The existing historical review files were **corrected in place**, not superseded by another conflicting model:

- `tests/offline/material_issue_capture_coverage.py` (Git blob **`65aa9ab32eb3cc3166fea7eb710ac33990ea7841`**, commit **`f7842587387721ebd7888bd8de43c717b2bd5324`**) now accepts either simple immutable positional tuples or **`FrozenNamedBinds`**, an immutable tuple of unique named pairs representing an offline copy of a dictionary. It rejects raw mutable dictionaries, mutable nested values, invalid or duplicate bind names, and named-placeholder/key discrepancies. It continues to reject unknown effects and always returns `NO_GO_SOURCE_ONLY`.
- `tests/offline/test_material_issue_capture_coverage.py` (Git blob **`671608fa2d1a5fe5138070b70243c570636cc61b`**, final exact-byte commit **`26043ab3c73c4ad901aa950a6dafd3c280efa607`**) adds **nine** adversarial tests for named query-builder and `multisql` parameters, missing/extra placeholder keys, direct raw-dict rejection, duplicate/invalid keys, nested mutable values, mutable positional binds and frozen-object integrity. The updated suite has **25/25 tests PASS** in credential-free local Python 3.13.5 with strict warnings, compilation PASS, and exact local Git blob hashes independently confirmed by GitHub readback.

The named SQL examples are **illustrative synthetic fixtures**, not claims of exact PyPika SQL output. The small placeholder regular expression is **not a SQL parser**. Even 25/25 PASS does **not** prove full runtime capture, bind equivalence, row scope, Redis isolation, rollback, or authorization. The model has no Frappe/PyPika/database/Redis/network imports, scripts or execution effects.

## Required read-only evidence packet for a later separately approved DEVELOPMENT diagnostic

The future procedure must be independently reviewed **before** any on-site command and must gather identity and effects without changing DEV/PRODUCTION state.

1. **Identity and scope:** isolated site `ccpc-integration2.localhost`, actual installed Frappe/ERPNext/CCPC Git HEADs, Frappe/PyPika versions, active hooks and child-table metadata; confirm isolation from both shared DEVELOPMENT `development.localhost` and PRODUCTION. Reject any mismatch, uncommitted work, unresolved backup/rollback path or unknown redis topology.
2. **Exact child row target:** Stock Entry parent `name`, parenttype `Stock Entry`, parentfield `items`, child table/DocType `Stock Entry Detail`, and complete before-state child **primary-key set** for the exact parent scope, with an independently known empty new-parent prestate as appropriate. These are expected values, **not verified runtime facts**.
3. **SQL and binds at both observation layers:** the **prepared query-builder SQL string**, complete **named bind dictionary** (including quoting/encoding if present), then **final driver SQL** and complete driver values **after** `_transform_query`. Record bind *types* and matched parameter keys as well as exact parent/type/field values. Do not accept a broad string-match on DELETE, WHERE 1, prefix-only identifiers, redacted bind fields or a tuple-only assumption.
4. **Physical impact and concurrency:** establish affected-row count from the actual driver and complete scoped **before/after child PK sets** while controlling concurrent writes, proving **zero unrelated/unwanted deletions**. An attempted DELETE whose actual row count is zero is distinct from no statement. Any unknown row, missing baseline, changed parent identity or speculative counter result is immediate STOP.
5. **Related persistent state:** first-series `tabSeries` key and prior state, initial insert-versus-increment, SLE/GL/Bin/Version and related Withdrawal Slip status/Item updates. Protect against concurrent first counter insertion and duplicate stock/GL posting.
6. **Other effects and rollback:** explicitly verify external Redis cache/queue/pubsub, `clear_persistent_cache`, `events`, `global_search_queue`, enqueue, callbacks, filesystem, and unexpected SQL fallback. SQL rollback alone cannot compensate precommit Redis effects; savepoint rollback does not run all full-rollback watchers.
7. **Recovery and authorization:** independently restorable isolated-site backup, confirmed safe Git working tree and equipment/server boundaries, failure/uncertain-commit and repeat protection, strict one-shot manually reviewed procedure. Any runtime command, even read-only, needs **fresh scoped owner authorization**. Rollback-only writes and persistent first posting need separate owner decisions; no production changes implied.

**Current absence of evidence:** no installed-site runtime data were gathered this turn; no generated MariaDB SQL, actual SQL dictionary, driver rowcount, before/after rowset, Redis endpoint or callback invocation was observed. The original posting candidate and review-only v2 remain unchanged; v2 retains unconditional `exit 1`. **Material Issue permanent posting: NO-GO.**
