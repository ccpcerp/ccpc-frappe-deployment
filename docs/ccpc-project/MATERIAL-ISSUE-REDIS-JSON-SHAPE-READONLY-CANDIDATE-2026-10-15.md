# CCPC ERPNext — Redis JSON shape and URL-format diagnostic (review-only)

**2026-10-15 | New GitHub-only candidate; NOT STAGED OR RUN on Ubuntu or DEVELOPMENT.**

## Purpose and verified source basis

The prior one-shot Redis configuration-boundary preflight is **consumed** and produced only the operator-reported final `ONE-SHOT READ-ONLY PREFLIGHT: STOPPED OR FAILED`. Its preceding output was not recovered. Later host checks independently reported script SHA256/syntax/ownership, DEVELOPMENT container identity, Python launch and stdin, and non-symlink readable metadata for the common, isolated test and shared development site config files. None establishes why the prior preflight stopped or that Redis instances are physically isolated.

A **separate** diagnostic is prepared to narrow the potential failure to one of three bounded JSON-read stages or two effective Redis URL-format stages, without repeating the original endpoint equality/overlap classifier. It prints **only fixed category labels**. No configuration file or endpoint value appears in output. It opens only the three documented DEVELOPMENT JSON files and reads only `FRAPPE_REDIS_QUEUE` and `FRAPPE_REDIS_CACHE` from the new short-lived exec child environment.

**Pinned Frappe source correction:** `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`, `frappe/config.py` Git blob `631a79d8283d2ae04f1fb4b95c2da4dba9f0450b`. `_get_common_site_config` applies environment overrides, then `_get_site_config` overlays a specific site's config and calls `_apply_common_env_overrides` again. Therefore the **effective final Redis precedence is common -> site -> current environment last** (followed by any Frappe `extra_config` dynamic hook at runtime). The **old consumed Redis boundary candidate** had modeled common -> environment -> site for Redis URL labels. That is a source-level mismatch, not evidence for any particular prior runtime STOP. **Do not repair or rerun the consumed script on the host**; keep it preserved as diagnostic history. The new format-only candidate tests the Frappe final environment precedence and expressly does not model dynamic hooks or live worker process state.

## Exact current review-only artifacts

Repository `ccpcerp/ccpc-frappe-deployment`, branch `review/material-issue-first-commit-preparation-2026-10-15`:

- [New guarded JSON/Redis format diagnostic](../../scripts/development/operator/ccpc_material_issue_redis_json_shape_readonly_candidate_20261015.sh), creation commit **`d709b0ee851558bdea9ccbc43d1e4d8cba80e779`**, exact Git blob **`fc5617117806b8cd19586ae3c7bf530dab21d632`**, SHA256 **`b88dadc10cac64c5b6f48a695fbf506b046613cbe4db192da440227934b212b0`**.
- [25 adversarial offline regression tests](../../tests/offline/test_material_issue_redis_json_shape_candidate.py), creation commit **`65011733e6fd67494fc44cad709e761492647089`**, exact Git blob **`53bddbb28c778ed604c8b0f06d70aacecf1ca280`**, SHA256 **`51f06704233a9f73c435229f1952428887400b7e8fa9ac46edfba16d218b0297`**.
- Local Bash syntax and embedded Python AST checks: **PASS**. Offline Python unittest suite: **25/25 PASS**, run in a credential-free local workspace on 2026-10-15 with `PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover -s tests/offline -p 'test_material_issue_redis_json_shape_candidate.py' -v` (using that local workspace as cwd). Tests used synthetic temporary files, including malformed/non-UTF-8/oversized JSON, symlinks, a FIFO, invalid URL shapes, Sentinel flags, injected environment-overrides, secret-bearing fake URLs and safe output assertions. Bash unapproved-execution smoke test stops before Docker; no Docker/network/API/site test ran.

## Safety architecture and output classification

- This script has a **new distinct approval gate** `CCPC_REDIS_SHAPE_READONLY_APPROVED` requiring the exact one-operation value `ccpc-redis-json-shape-one-shot`. Neither existing Redis preflight approval nor any prior one-shot permission authorizes it.
- Requires nonroot operator, Docker availability, exact running Compose project `frappe_docker_devcontainer`, service `frappe`, and container `frappe_docker_devcontainer-frappe-1`; single `docker exec -i --user frappe` only after identity confirmation. No user-provided target, environment dump or PRODUCTION context.
- Embedded Python uses `-I -B -S` and `PYTHONDONTWRITEBYTECODE=1`. It imports only standard-library `ipaddress`, `json`, `os`, `stat`, `sys`, `pathlib`, and `urllib.parse`. It never imports Frappe, Redis, SQL or networking modules, does not initialize Frappe, and performs no Redis DNS resolution, connection, ping, publish, key access, SQL or file write.
- Reads exactly three fixed-path JSON configs with read-only, nonblocking, nofollow flags where available and `fstat` regular-file/size checks (maximum **65,536 bytes per file**). Fixed parent-directory symlink checks and a nonfollow flag protect against ordinary symlink redirects; these are **not an atomic race-proof directory capability**. Any unexpected state STOPs.
- Stage-specific sanitized labels: `COMMON: JSON_OK/JSON_STOP`, `ISOLATED: JSON_OK/JSON_STOP`, `SHARED: JSON_OK/JSON_STOP`, `ISOLATED_REDIS: FORMAT_OK/FORMAT_STOP`, `SHARED_REDIS: FORMAT_OK/FORMAT_STOP`. The parser only checks `redis://` and `rediss://` URL format, explicit host/valid port, rejects unsuitable unspecified/multicast IPs and truthy Sentinel mode; it applies Frappe-like fallbacks and only the exec-child Redis environment overrides. **No raw config, user, password, host, port, path, URL, Frappe exception, hostname resolution or database name is displayed**. Docker exec stderr is suppressed to prevent incidental disclosure.
- Even a completed `FORMAT_OK` result is **NOT** proof of successful Redis connection, absence of endpoint overlap, distinct physical Redis servers, physical PRODUCTION isolation, worker / Socket.IO / pubsub isolation, SQL rollback recoverability, or posting safety. `FORMAT_STOP` may reflect a safe unsupported configuration, not necessarily a system malfunction.

## Consent gates, deployment limits and next action

1. **Current scope:** GitHub-only source review, offline synthetic tests, design/security documentation and handoff. No DEVELOPMENT or PRODUCTION inspection or execution is approved by a generic “Continue.”
2. **If the owner later explicitly approves staging only:** Reverify review-branch HEAD, exact script blob and SHA256; use the documented private `$HOME/ccpc-reviewed-scripts` pinned GitHub-to-Ubuntu workflow outside the protected checkout. This is a NEW filename; do not replace/reexecute the earlier staged preflight.
3. **If staging independently succeeds:** Require **another distinct specific one-shot approval for execution** on the confirmed DEVELOPMENT container. Review operation one at a time, print only sanitized labels; STOP on unexpected output and do not auto-retry. Operator must paste the full sanitized transcript, not secrets or raw JSON.
4. **No subsequent writing:** Any read-only format result only guides another review. The first permanent Material Issue Stock Entry/SLE/GL COMMIT, rollback-only writing, database migrations, service restart, Redis configuration change, and PRODUCTION changes remain **NO-GO** without separate reviewed authorization.

**No assertion of production-readiness or real DEVELOPMENT Redis isolation is justified by these offline tests.**
