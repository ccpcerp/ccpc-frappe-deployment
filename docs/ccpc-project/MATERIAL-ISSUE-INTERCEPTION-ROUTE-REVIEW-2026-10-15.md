# CCPC ERPNext — First Material Issue interception route review

**2026-10-15 | GitHub-only source review and offline tests | NO-GO for a live rollback or persistent posting**

## Pinned and independently inspected GitHub source

- Frappe commit: 988e54f3c4c291e2077a83809663f123731abe76.
- frappe/model/document.py, Git blob e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a: update_child_table, run_post_save_methods, clear_cache and notify_update.
- frappe/query_builder/utils.py, Git blob 0b3a2f315346f9813717f8d201b9546989da2761: execute_query and prepare_query.
- frappe/database/database.py, Git blob a2ba78e2488f03810d58c43c768b4fbab624c3dc: sql, execute_query, multisql, commit, rollback and savepoint.
- frappe/utils/global_search.py, Git blob 174ee0479160223aa69bc5df3adb924a6afb9b6a: update_global_search, sync_value_in_queue and sync_value.
- frappe/utils/redis_wrapper.py, Git blob 8a48e16afc91c14e10644058fea950e0d41a4124: make_key, delete_value and lpush.
- Custom app feature/withdrawal-material-issue-safety remains pinned to 2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6; app source was not modified.

All results below are **static source paths**, not evidence any particular installed-site branch actually executed.

## Source-based interception findings

1. **Child-table DELETE:** Document.update_child_table builds a query-builder DELETE with parent, parenttype, parentfield, and possibly an existing-child-name exclusion. Query-builder execute_query forwards rendered SQL plus binds to frappe.local.db.sql. Database.sql calls Database.execute_query, which calls self._cursor.execute(query, values). Query-builder-only capture is insufficient for non-query-builder SQL, while a high-level SQL wrapper would not on its own establish coverage of unknown direct driver calls. Actual rendered child SQL, binds, and row deltas remain **unobserved**.
2. **Naming-series:** Pinned getseries performs a tabSeries INSERT/UPDATE depending on state, so a query-builder-only hook cannot suffice. The exact site key, first-row behavior and concurrency invariants remain **unverified at transaction time**.
3. **Global-search Redis:** Document.run_post_save_methods calls update_global_search. Conditional searchable content can cause sync_value_in_queue to call frappe.cache.lpush('global_search_queue', ...) **before SQL COMMIT**. RedisWrapper.lpush uses make_key, which normally prefixes keys with the configured database name. **Key prefixing alone is not an isolated Redis endpoint, comprehensive interception proof, or rollback protection**.
4. **Redis failure SQL fallback:** A Redis ConnectionError in sync_value_in_queue calls sync_value, which uses frappe.db.multisql with a MariaDB INSERT INTO __global_search ... ON DUPLICATE KEY UPDATE path. This is a distinct SQL mutation route. Simulating a Redis failure to avoid queued work would instead activate this fallback and is not an isolation solution.
5. **Cache, realtime and hooks:** Document post-save also clears document cache, calls notify_update and executes on_change. RedisWrapper.delete_value can unlink keys and change the local cache, but the concrete installed-site cache chain is not yet completely traced. notify_update uses publish_realtime with after_commit=True for its notifications; that parameter does not establish that all other effects are deferred.
6. **Callbacks and savepoint:** Database.commit executes before_commit callbacks before COMMIT and after_commit callbacks afterwards. Full rollback executes rollback watchers, but rollback(save_point=...) issues SQL rollback-to-savepoint without full rollback watcher execution. The pinned method warns about filesystem effects across savepoints. SQL rollback cannot undo prior external effects.
7. **Driver and transaction controls:** Database.sql also exposes auto_commit behavior, so interception must separately account for unexpected transaction-control paths, unknown lower-level calls, and unreviewed installed hooks.

## New offline artifacts and actual local test result

- [Inert route model](../../tests/offline/material_issue_effect_routes.py): commit 287a0f6895e08c1b7a9c6fbcca35ccc987acad23, exact Git blob **77a3ec5fec3b0610f5ca9fffd5240668af507562**, SHA256 **9d98d13439292b7f0fa698dc0c841602290fa1141a4aa226cf51331260af9cc6**.
- [Seventeen adversarial tests](../../tests/offline/test_material_issue_effect_routes.py): commit 934bf4409d438fe2ce59a789d8e34b539ca60456, exact Git blob **6185893a6f908bc4146999eb6136852a6ab386ff**, SHA256 **6d58c0b7f6c2b2be32a219c956d6b995b04e7f21dbad297f46ae4c0b200078f3**.
- An isolated, credential-free local Python workspace ran unittest discovery for the new module: **17/17 PASS**. Python compilation PASS. Local git hash-object matches GitHub re-fetched blobs.
- The earlier 16/16 capture-coverage suite, 14/14 naming witness and 19/19 blocker characterization are **separate previous results, not rerun here**.

The new model contains **12 synthetic risk paths**. Paths marked pinned_source reflect only the cited call sequence; requires_source_review paths are unverified/hypothetical and explicitly not proven installed-site behavior. The tests show missing theoretical hook coverage with a query-builder-only, db.sql-only, cache.lpush-only or rollback-callback-only claim. Even when all named candidate hooks are claimed, the model always returns safe_to_rehearse=false, safe_to_commit=false, and source_graph_exhaustive=false. It contains no runtime adapter, database/Redis imports, SQL executor or runnable diagnostic.

## Remaining decision gates

- Independently verify actual installed code, dynamic call targets, site configuration, custom hooks, final SQL driver and Redis client interception boundaries. **Twelve modeled routes are not an exhaustive graph**.
- Source-review actual query-builder DELETE SQL and binds, exact Withdrawal Slip Item key/parent and zero-row child deletion invariant, initial series counter concurrency, and all stock/GL/Bin/Version/payment-ledger auxiliary writes.
- Design actual separate-process/endpoint isolation or source-reviewed complete process-local interception of SQL, Redis, cache invalidation, search queue, realtime, background jobs and callbacks. Never mutate or flush shared DEVELOPMENT or PRODUCTION Redis.
- Review COMMIT, auto-commit, rollback savepoint and unknown-driver behaviors. Prove external effects and SQL state are fully contained before attempting a rollback-only exercise.
- Verify backups and safe recoverability, and obtain **fresh separate owner approval** for staging and any one-off DEVELOPMENT diagnostic. A new approval would be needed for permanent posting; PRODUCTION has a separate explicit-release gate.

The original commit-capable candidate and review-only v2 were not changed or staged. V2 retains its hard early exit. **NO-GO for first permanent Material Issue. No DEVELOPMENT or PRODUCTION server operation performed.**
