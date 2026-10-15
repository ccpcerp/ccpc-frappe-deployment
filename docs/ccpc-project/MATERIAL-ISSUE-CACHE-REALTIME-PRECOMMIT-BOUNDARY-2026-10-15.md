# CCPC ERPNext — Material Issue cache, realtime, and pre-COMMIT effects boundary

**2026-10-15 | Verified pinned GitHub source + credential-free offline characterization | permanent posting NO-GO**

## Exact source baseline

- CCPC custom app: `ccpcerp/ccpcerp` branch `feature/withdrawal-material-issue-safety`, SHA `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`. `ccpcerp/hooks.py` blob `023dc7b04b8f4fa019654c074124bd03f3b82489`, `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` blob `771d27781f8d933fd243415e8286976fbdd1a861`.
- Pinned Frappe: `988e54f3c4c291e2077a83809663f123731abe76`. Document `frappe/model/document.py` blob `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`; cache manager `frappe/cache_manager.py` blob `fc4cb7e0d15c893fd0baf4d289de1e3deb70950d`; redis wrapper `frappe/utils/redis_wrapper.py` blob `8a48e16afc91c14e10644058fea950e0d41a4124`; realtime `frappe/realtime.py` blob `7e8e31f1b0a8d4362d51ba108f26e3c795c2e21a`; global search `frappe/utils/global_search.py` blob `174ee0479160223aa69bc5df3adb924a6afb9b6a`; DB `frappe/database/database.py` blob `a2ba78e2488f03810d58c43c768b4fbab624c3dc`.

This review studies exact source call paths. It does **not** claim to have observed actual installed-site Redis traffic, SQL effects, hooks, cache configurations, or backup recoverability.

## Newly narrowed effects — source evidence versus runtime status

| Path | Pinned code sequence | Why rollback cannot by itself establish containment |
| --- | --- | --- |
| Stock Entry submit | Custom `hooks.py` registers Stock Entry `on_submit` => `withdrawal_slip_stock.sync_withdrawal_slip_issue_status` | When `withdrawal_slip` is populated, the handler calls the named Slip synchronizer |
| Slip status synchronization | `sync_withdrawal_slip_issue_status_for_name` calculates quantities, updates `Withdrawal Slip Item` and `Withdrawal Slip` by `frappe.db.set_value`, then calls `frappe.clear_cache(doctype="Withdrawal Slip")` | SQL field changes and cache actions belong to different effect boundaries |
| DocType cache clear | `frappe.cache_manager.clear_cache(doctype=...)` -> `clear_doctype_cache` -> `frappe.client_cache.erase_persistent_caches` and `_clear_doctype_cache_from_redis` **immediately**, also registering after-COMMIT and after-ROLLBACK cache-clear callbacks | A cache invalidation and publish can already occur before SQL commit; additional callbacks may repeat it |
| Cross-worker invalidation | `ClientCache.erase_persistent_caches` calls `self.redis.publish("clear_persistent_cache", json.dumps({doctype,site}))` | The channel is literal, with the site in the payload. Key prefixing does not establish separate Redis transport, subscribers, or transactional compensation |
| Individual document cache | `frappe.model.document.clear_document_cache` calls `frappe.cache.delete_value` / `delete_keys` **immediately**, then adds after-COMMIT and after-ROLLBACK invalidation callbacks | `RedisWrapper.delete_value` changes process cache and calls Redis `unlink`; rollback cannot undo a previously published/unlinked effect |
| Global-search content | `update_global_search` -> `sync_value_in_queue` -> `frappe.cache.lpush("global_search_queue", ...)` when conditions hold | Redis push may precede SQL commit; Redis failure triggers a separate `__global_search` SQL fallback and is not an approved workaround |
| Realtime | `publish_realtime(after_commit=True)` records a process-local log and registers flush/clear callbacks; other paths can call `emit_via_redis` immediately. An associated task ID can force `after_commit=False` in pinned code | `emit_via_redis` opens `get_redis_connection_without_auth()` and publishes on the literal Redis `events` channel, with namespace in the message. Suppressing only `publish_realtime` does not prove complete external-effect control |
| SQL/savepoints | `Database.rollback(save_point=...)` uses rollback-to-savepoint without executing the full rollback watchers; `commit()` runs before- and after-commit callbacks | Savepoints only address SQL state; callback and non-SQL effects are separate |

**Key new blocker:** An apparently legitimate, same-site first Material Issue can trigger CCPC's explicit `frappe.clear_cache(doctype="Withdrawal Slip")` when the custom submit hook takes the linked-Slip path. This branch is present in GitHub source, but its execution in a particular isolated transaction has not been observed.

## No-safe-shortcut containment plan

1. Identify actual installed-site hooks, naming settings, transaction and Redis/cache endpoint routing **before** any write-capable diagnostic. The project checkout and pinned source are not runtime proof.
2. For a future, separately authorized synthetic isolated test, require independently isolated Redis cache **and pub/sub**, queues/workers, document hooks and any external dependencies; *or* construct a separately reviewed, process-scoped interception architecture covering final physical sinks **with explicit failure on any untracked path**. Neither option is presently implemented or proven. Do not disable or flush shared Redis.
3. Include precommit cache deletion/unlink, `clear_persistent_cache` pub/sub, `events` pub/sub, global-search queue, fallback SQL and callback register/invoke sequences. Each must be classified by exact phase and verified effects, not just by presence of a claimed hook.
4. Do not assume site-prefixed Redis keys isolate unprefixed pub/sub channels. Check actual target connections, consumers, payload routing and effective configurations. Never emit a trial event into shared cache, realtime or workers simply to test coverage without separate explicit approval.
5. Prove exact Withdrawal Slip Item row identity, SQL child DELETE predicates/binds and zero removed rows; the initial `tabSeries` counter/series key/concurrency; SLE/GL/Bin/Version/payment ledger and all other auxiliary writes, even when noncache effects are contained.
6. Review all transaction controls including SQL `auto_commit`, callback ordering, nested savepoints, uncertain outcomes, and a tested recovery path. A SQL ROLLBACK success message alone is not acceptable.
7. Get **separate permission** for creating/staging any new operator script and for each one-shot DEVELOPMENT execution; a permanent one-unit Stock Entry/SLE/GL COMMIT and any PRODUCTION operation require separately explicit authorization.

## New offline files and validation

- `tests/offline/material_issue_effect_timeline.py`: Git blob `35ef3b265c6b3478eeaa49548c140ee5da5d7d1e`, SHA256 `b568696a76b8c240d0fc34533893b98ec8ba0b1dc1ed6cac62a3df21eeea84e4`, creation commit `ddeed952f7ebb47ddf934135f7863586f9759c5e`.
- `tests/offline/test_material_issue_effect_timeline.py`: Git blob `feda6fd1993be91e25634808d249f1ca769862b8`, SHA256 `6316c69cc7fd21ef701ce7a47235b1c6746639271903a67495600e986b926da8`, creation commit `8f75950a4d0acdb743fc27aba5d7c3b006eae1ed`.
- **19/19 offline unit tests PASS**, Python compilation PASS, and `git hash-object` matches both verified GitHub file blobs. Tests are source-only and credential-free, using immutable hypothetical effects; they intentionally return `safe_to_stage=false`, `safe_to_rehearse=false`, `safe_to_commit=false`, and no assertion of real runtime capture or Redis isolation.
- Earlier offline suites (17/17 route model, 16/16 coverage, 14/14 series witness and 19/19 blocker characterization) are separate past results and were **not rerun** in this milestone.

**Unchanged safety decision:** Original commit-capable candidate unchanged. Review-only v2 stays Git blob `0a17d53cc0badac1de05745ef9edfb60d342ed89` with unconditional early `exit 1`. No DEVELOPMENT or PRODUCTION server operations, SQL/Redis execution, live posting, container lifecycle changes, backups, or database migration occurred. **Permanent first Material Issue COMMIT: NO-GO.**
