# CCPC ERPNext — Redis configuration boundary read-only preflight CANDIDATE

**2026-10-15 | GitHub-only prepared artifact; not staged or executed on DEVELOPMENT | NO-GO for posting.**

## Verified source and limitation

GitHub verified the custom app branch `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` (unchanged). This work uses pinned Frappe `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`:

- `frappe/config.py`, Git blob `631a79d8283d2ae04f1fb4b95c2da4dba9f0450b`: `_get_common_site_config` applies `FRAPPE_REDIS_QUEUE` and `FRAPPE_REDIS_CACHE` environment overrides to the common config, then `_get_site_config` overlays the site's `site_config.json`. A read-only review of **only** `common_site_config.json` cannot establish effective Redis settings.
- `frappe/utils/redis_wrapper.py`, blob `8a48e16afc91c14e10644058fea950e0d41a4124`: `setup_cache()` uses the configured Redis cache URL or Sentinel master.
- `frappe/utils/redis_queue.py`, blob `7ee3bd0ab10962684f00a21f9317f3ad7671bf4f`: `RedisQueue.get_connection()` uses configured queue Redis URL or Sentinel.
- `frappe/realtime.py`, blob `7e8e31f1b0a8d4362d51ba108f26e3c795c2e21a`: realtime `events` publishes on a queue Redis connection. `ClientCache.erase_persistent_caches` also publishes cache-side `clear_persistent_cache` (unprefixed pub/sub channel).
- The versioned deployment `compose.yaml`, blob `752b86e1ba4c1977a2636b1916f6015771f4c28c`, configures `REDIS_CACHE` and `REDIS_QUEUE` independently; `overrides/compose.redis.yaml`, blob `64bc05ac2e955719822718e5118a62d0c9771e24`, **defines two Redis services** named `redis-cache` and `redis-queue`. These are *templates*, not an authoritative observation of the running `frappe_docker_devcontainer` DEVELOPMENT environment, active worker environments, or any PRODUCTION endpoint.

Existing [database isolation read-only candidate](../../scripts/development/operator/ccpc_material_issue_db_isolation_readonly_20261015.sh) and [site baseline read-only candidate](../../scripts/development/operator/ccpc_material_issue_isolated_baseline_readonly_20261015.sh) already cover different questions. **Do not rerun those or any consumed one-shot probes.** This new candidate covers only an unresolved Redis **configuration** comparison.

## New exact GitHub files

- [Guarded read-only Redis boundary candidate](../../scripts/development/operator/ccpc_material_issue_redis_boundary_readonly_candidate_20261015.sh): creation commit `19dcec054fbc5dd655a60249631bf43b88449813`, Git blob `5a37dae1391bac0a2bb1be979a6aaf036f9f4c6d`, SHA256 `4fbac349cddb43d40994ef53182c225069341c8fbac393a33c9f7db5c47f7b05`.
- [19 offline negative tests](../../tests/offline/test_material_issue_redis_boundary_candidate.py): creation commit `aa31a0b56ea72b54354d3bfec271f1ed4d957eb1`, Git blob `bac736443d77b595d401d982cad11130d6a15b22`, SHA256 `95d27f1c82db175901da1635086bd55451d4b30b40eff001a658d7683fc08960`.

Local Python 3.13.5 and Bash checks (credential-free): `bash -n` PASS; embedded Python `ast.parse` PASS; `PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover -s tests/offline -p 'test_material_issue_redis_boundary_candidate.py' -v` **19/19 PASS** after fixing an initial **test-only** `ast.ImportFrom` root-name mistake. Local `git hash-object` matched both independent GitHub readback blobs. Unapproved local execution exited 1 **before any Docker inspection**. The pure classifier was exercised only with fake endpoint labels and local temporary JSON fixtures; no network was used.

## Strict intended one-operation scope (future approval needed)

The candidate is *inert unless a separately authorized one-shot environment flag is explicitly set*. Even with such approval it will:
1. Require normal non-root operator and check exactly the documented **DEVELOPMENT** Docker container `frappe_docker_devcontainer-frappe-1` for Compose project `frappe_docker_devcontainer`, service `frappe`, running state.
2. Open **only** that DEVELOPMENT container for an embedded Python script with no `frappe`, `redis`, `MySQLdb`, `docker` or network imports. Read bounded regular, non-symlink `sites/common_site_config.json`, `sites/ccpc-integration2.localhost/site_config.json`, and `sites/development.localhost/site_config.json` using read-only file handles. Examine only two allowlisted environment variables.
3. Apply common config + observed exec-process env overrides + site overrides. Compare only internal opaque `(hostname, port)` endpoint tuples for isolated cache, isolated queue, shared-site cache and shared-site queue. Ignore Redis database numbers, username/password and TLS for conservative same-host/port matching. Reject Sentinel/unknown/malformed settings rather than assuming isolation.
4. **STOP** if isolated cache and isolated queue are configured on the same host/port or any test Redis role exactly overlaps any shared-development Redis role. Otherwise print **CONFIG ONLY** and explicitly that actual DNS, physical Redis, workers and pub/sub isolation are **UNVERIFIED**.
5. Never print raw URLs, credentials, hostnames, ports, database names, site configuration or stack traces. No SQL, Redis ping/publish/write, Frappe initialization, shared-development business-data access, PRODUCTION container access, worker restart, Docker lifecycle changes, backup mutation or Git checkout modifications.

## Interpretation and next approval gates

A `REDIS CONFIGURATION ENDPOINT OVERLAP: DETECTED; STOP` outcome would be **expected and safety-relevant**, not a failure that should be worked around automatically. Do **not** change Redis service settings, detach shared caches, drop keys, or retry the script without an independently reviewed plan.

A `NO EXACT OVERLAP` outcome still cannot prove physical isolation: DNS aliases, service proxies, container networks, Sentinel, differing worker environment variables, cached Frappe configs, pub/sub subscribers and host-level shared infrastructure require separate validation. The `docker exec` child process environment is not proof of current backend/worker/socketio process environment. This candidate intentionally performs **no** live Redis service, DNS or worker probes.

**Status:** Committed for review only. User's generic “Approved and Continue” is **not** treated as authorization to stage or run this new script. A separate explicit consent is required for **one pinned SHA256-verified staging operation**, then a further separate explicit manual **read-only execution** on the isolated DEVELOPMENT environment. Any read-only result can inform a subsequent distinct plan; write-then-rollback diagnostics and permanent Stock Entry/SLE/GL COMMIT still need different approvals plus recoverable isolation and effect containment. PRODUCTION expressly excluded. Original commit-capable candidate and inert v2 with unconditional early `exit 1` remain unchanged.

**Permanent first Material Issue COMMIT: NO-GO.**
