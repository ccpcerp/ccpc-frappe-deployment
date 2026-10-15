# CCPC ERPNext — Synthetic containment manifest and Redis connection boundaries

**2026-10-15 — GitHub-only source review and credential-free offline test milestone.**
**Decision: NO-GO for Ubuntu staging, DEVELOPMENT writing rehearsal, permanent Material Issue COMMIT and PRODUCTION operations.**

## Scope and pinned source

The custom application remains `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`, unchanged. Frappe source used is pinned at `988e54f3c4c291e2077a83809663f123731abe76`.

Exact reviewed source:
- `frappe/utils/background_jobs.py` blob `a5f5b206d64d71a79dfb4ce81d899fe219299196`: `enqueue` optionally runs synchronously via `now=True` or `is_async=False`, queues immediately by default, or registers an after-commit callback when `enqueue_after_commit=True`; `get_redis_connection_without_auth` holds a process-global Redis queue connection.
- `frappe/utils/redis_queue.py` blob `7ee3bd0ab10962684f00a21f9317f3ad7671bf4f`: `RedisQueue.get_connection` selects queue Redis from the site configuration (`redis_queue`) or Sentinel; actual runtime endpoint and sharing are **not known**.
- `frappe/utils/redis_wrapper.py` blob `8a48e16afc91c14e10644058fea950e0d41a4124`: `setup_cache` uses `redis_cache` or configured Sentinel and `ClientCache.erase_persistent_caches` publishes `clear_persistent_cache` immediately. The `RedisWrapper.make_key` site database-name prefix does not apply to every pub/sub channel.
- `frappe/realtime.py` blob `7e8e31f1b0a8d4362d51ba108f26e3c795c2e21a`: `emit_via_redis` publishes `events` using the queue Redis connection; `publish_realtime(after_commit=True)` can defer and task-ID paths can change the timing.
- `frappe/model/document.py` blob `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a`, `frappe/cache_manager.py` blob `fc4cb7e0d15c893fd0baf4d289de1e3deb70950d`, and custom `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` blob `771d27781f8d933fd243415e8286976fbdd1a861`: first-issue-related Slip synchronization can update records and call immediate `clear_cache(doctype="Withdrawal Slip")`, which may cause non-SQL cache and pub/sub effects prior to COMMIT.

**Critical distinction:** Static GitHub source identifies *candidate* boundaries. It cannot reveal actual installed site Redis URLs, whether the queue and cache share physical infrastructure, effective hooks, worker subscriptions, credentials, network topology or whether a specific branch executes on a real site. Do not collect or commit secrets to prove any of these.

## Fourteen independent manifest surfaces

| Category | Review surfaces | Gate |
| --- | --- | --- |
| Database | `sql.driver`, `sql.transaction`, `sql.child_delete`, `sql.series` | Final driver interception, no implicit COMMIT/DDL, exact child predicates/binds and deleted-row delta, first-series counter and concurrency |
| Redis & workers | `redis.cache_keys`, `redis.cache_pubsub`, `redis.queue_pubsub`, `redis.background_jobs`, `redis.search_queue` | Independent sink coverage for keys, pub/sub, jobs, and global-search queue; no presumed shared-Redis safety or silent bypass |
| Process and app hooks | `process.cache`, `document.hooks`, `transaction.callbacks`, `filesystem.external` | Cache invalidation before rollback, custom hook order, callback execution vs registration, unknown external writes |
| Recovery | `backup.recovery` | Independently verified backup, recoverability, and uncertain-outcome handling, without touching shared deployments |

## New exact tested inert artifacts

- `tests/offline/material_issue_containment_manifest.py`: commit `20c9b99f06287b21a0808736bb58d5b8a5c22890`, exact Git blob `4a03ce27e051df8350e750a011b34a83f80037c1`, SHA256 `4dab31d3310750c87c6fd49c663f4655d60517311da86139cc829ef760d0d70f`.
- `tests/offline/test_material_issue_containment_manifest.py`: commit `a4497687ca46db6fcb04cf980070be05ec28b8c9`, exact Git blob `4dcbcbad62250ffd75d0218f28b6d62473484345`, SHA256 `58e6662ab7e6ec055b4b9ce25472cea8e2e3306857f4112207b4554395e0d01a`.
- Local command `python3 -m unittest discover -s tests/offline -p 'test_material_issue_containment_manifest.py' -v`: **25/25 PASS**. `python3 -m py_compile` both: **PASS**. `git hash-object` for both byte-identical files matches independently fetched GitHub blobs.
- This is a new standalone offline suite. Earlier 19/19 effect-timeline, 17/17 route, 16/16 capture, 14/14 series, 19/19 blocker suites were not rerun.

The pure Python module **does not import Frappe, Redis, SQL, Docker, subprocess or network code**, and neither instruments nor writes any service. Its immutable `BoundaryClaim` entries accept only 14 known surfaces, an exact isolated-site symbol and a small finite set of untrusted claim modes and evidence labels. It reports omissions, duplicate claims, shared/unknown categories and *declared* overlapping Redis endpoint aliases. Importantly:
- All 14 categories claimed = **still NO-GO**.
- Separate alias labels = **not proof** of separate Redis endpoints or network/worker isolation.
- Source-only, synthetic or self-asserted runtime evidence = **not independently verified instrumentation**.
- Positive-looking declarations cannot activate a live operator script or post Stock Entry/SLE/GL.

The model **always** returns false for `safe_to_stage`, `safe_to_rehearse`, `safe_to_commit`, real SQL/Redis isolation, recovery verification, hook binding, and owner approval. This is a negative evidence model, not a deployable security control or a mechanism that makes a writing rehearsal safe.

## Further work and approval boundaries

Next GitHub-only work should review exact installed-hook *source* as far as GitHub allows, map direct driver/Redis/cache/queue escape paths and distinguish real physical isolation from proposed interception. Before any separately approved diagnostic, independently verify the live isolated site's branch/configuration without exposing secrets, full resource ownership, recoverable backups, exact first-series and child DELETE behavior, unknown hooks, cleanup/rollback side effects, and no PRODUCTION/shared DEVELOPMENT mutation.

Do not equate SQL ROLLBACK with rollback of Redis pub/sub, queued jobs, cache invalidation, or filesystem side effects. The original commit-capable candidate and the inert review-only v2 remain unchanged; v2 must retain its unconditional early `exit 1`. No remote execution, Ubuntu staging, Docker, database, Redis, production operation, or new on-site read-only probes were performed in this milestone.
