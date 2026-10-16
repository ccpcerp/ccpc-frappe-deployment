# CCPC ERPNext — DEVELOPMENT Redis topology evidence contract (GitHub-only design)

**2026-10-16 | DESIGN ONLY — no executable probe, staging, Ubuntu inspection, runtime tests or production access | Material Issue Stock Entry/SLE/GL and write-then-rollback: NO-GO**

## 1. Authorization, source pins, and reason for a different approach

The owner explicitly approved **preparing a GitHub-only DEVELOPMENT Redis topology verification design**, after the [final endpoint-label usefulness review](MATERIAL-ISSUE-REDIS-ENDPOINT-LABEL-CANDIDATE-2026-10-16.md) concluded **DEFER STAGING**. This approval covers reading applicable GitHub sources and updating review/handoff documentation, **not** operator script creation/execution, Docker or host access, site-config reads, Redis/DNS/SQL operations, service changes, application pulls, PRODUCTION reads, live transaction tests or automation.

Starting GitHub refs independently rechecked:
- Deployment review branch `review/material-issue-first-commit-preparation-2026-10-15` at `c3aff0cb53844ec2a808de658faa1effbc4a55cc`.
- Rolling handoff docs branch `docs/ccpc-checkpoint-2026-10-10` at `81aef0ef0d4934474cb0243af42b6e55d86ecb88`.
- App `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`; unchanged.
- Pinned reviewed Frappe baseline `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76` is a source baseline, **not a live build/version attestation**.

Preserve the old original Redis boundary script's **unclassified STOP** and consumed authorization. The independently corrected JSON/Redis format v2 returned **3 JSON_OK + 2 FORMAT_OK and COMPLETED** in an operator-reported, once-only DEVELOPMENT run, **not** endpoint isolation. The distinct [43/43 offline-tested endpoint-label candidate](../../scripts/development/operator/ccpc_material_issue_redis_endpoint_labels_readonly_candidate_20261016.sh) at blob `ddd56afef0e8b5c6f61aedcc7975ce0a8ec0f8cc` remains **review-only and NOT STAGED**; DNS-label inputs usually produce `AMBIGUOUS_STOP`. Do not modify, replay, reauthorize or confuse any of those artifacts.

## 2. Verified source constraints, not live topology findings

| Source | Verified baseline | Consequence for this design |
| --- | --- | --- |
| [DEV/PROD architecture](DOCKER-DEV-PROD-ARCHITECTURE.md), Git blob `6007ebef0c2f36794d4a4607a2c47efcd42a47e2` | Separate Compose projects **share Ubuntu host and Docker daemon**; active DEV `.devcontainer/docker-compose.yml` is Git-ignored and its live deployment may differ from the tracked template | **Cannot prove no PRODUCTION overlap from a DEV-only probe.** Any PRODUCTION-facing Docker, network or process inspection requires a separate explicit production-scope consent. |
| [DEV Compose template](../../devcontainer-example/docker-compose.yml), blob `75f57aac53dd03246d4d7d355db2e8ce641aa78e` | Declares services `frappe`, `redis-cache`, `redis-queue` (among others) and a RW host workspace mount | A service label is an *expected role*, not a confirmed live process, Redis instance or isolation boundary. The only host container already verified in prior one-shot checks is `frappe_docker_devcontainer-frappe-1`; redis container names require fresh discovery and explicit allowlisting. |
| Tracked base [Compose](../../compose.yaml) blob `752b86e1ba4c1977a2636b1916f6015771f4c28c` and [Redis override](../../overrides/compose.redis.yaml) blob `64bc05ac2e955719822718e5118a62d0c9771e24` | Model distinct Redis cache/queue services and separate WebSocket/worker processes in the tracked deployment | **These are source templates, not evidence of current running PROD or DEV service identities.** No PROD resource names/IDs must be retrieved in the proposed DEV-only stage. |
| [Frappe config.py](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/config.py) blob `631a79d8283d2ae04f1fb4b95c2da4dba9f0450b` | Python effective Redis precedence: common config → site config → process Redis environment LAST; dynamic `extra_config` possible | A short-lived child process's environment is not a substitute for each existing long-lived web/RQ process; dynamic hooks and cached connections require explicit UNKNOWN states. |
| [Frappe node_utils.js](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/node_utils.js) blob `0fc5a37189e4e49ac64a1bb850669d1e3f100d5a` | Node `get_conf()` reads bench `config.json`, then common-site JSON and Node process environment; `get_redis_subscriber()` uses `redis_queue` | A synthetic Node/common/environment computation cannot prove the *running* WebSocket/subscriber's actual route. Never silently use the exec-child environment as the Node process environment. |
| [Frappe realtime/index.js](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/realtime/index.js) blob `f3337103829e956cdbe15d1c696c81dc796d1ffe` and [realtime.py](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/realtime.py) blob `7e8e31f1b0a8d4362d51ba108f26e3c795c2e21a` | Literal pub/sub channel `events`; Node subscribes; roomless event source may fan out to multiple site namespaces | Redis key namespacing or a site value in an event payload is **not subscriber transport isolation**. No trial events/publish permitted. |
| [Redis wrapper](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/utils/redis_wrapper.py) blob `8a48e16afc91c14e10644058fea950e0d41a4124` | Client cache invalidation uses literal `clear_persistent_cache` channel; in-process/persistent caches may be invalidated before COMMIT | DB rollback cannot undo those Redis effects. No Redis read/write/subscribe needed for the *design*. |
| [RQ/background jobs](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/utils/background_jobs.py) blob `a5f5b206d64d71a79dfb4ce81d899fe219299196` and [RedisQueue](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/utils/redis_queue.py) blob `7ee3bd0ab10962684f00a21f9317f3ad7671bf4f` | Redis clients may be cached in long-lived workers; worker queues use bench IDs | Declared service, container startup configuration and currently active client/socket endpoints are **different evidence layers**. |

## 3. Stage A: proposed DEVELOPMENT-only, read-only Docker metadata contract

This is **an acceptance design, not a command or implementation**. The future independently reviewed candidate, if commissioned, should:
1. Require operator `gani` (nonroot), a **distinct new approval token**, exact DEVELOPMENT container `frappe_docker_devcontainer-frappe-1`, expected project/service Compose labels and running state, and a noninteractive manual one-shot wrapper with strict ownership, permissions, staged SHA256 and syntax checks; fail with no retries. Never reuse any consumed script or token.
2. Use only host Docker **read-only metadata** needed to assess the **DEVELOPMENT project's** expected `frappe`, `redis-cache`, `redis-queue` roles. An allowlist of expected Compose labels and service roles should bound discovery. Validate returned identities and cardinalities in memory; unexpected, stopped, absent, duplicate or ambiguous service roles produce a fixed STOP. A global unrestricted `docker ps` listing and arbitrary container-name matching are out of scope.
3. For only verified DEV candidates, evaluate **coarse** state and network attachment predicates (for example, whether named DEV roles expose known shared attachment risks, have a nonempty network attachment set, or use host network mode). Treat host/none/network-mode anomalies, multiple/foreign network ambiguity and changing state as STOP/UNKNOWN. Exact network names, IDs, aliases, IPs and subnet addresses may be held transiently in memory when strictly required, but must never be logged, echoed or committed.
4. **Do not inspect the full Docker network object or its peer/member list**, because it can identify PRODUCTION containers or other services. Do not inspect any non-DEV container even to compare network IDs, names, volumes or labels. Consequently any `NO_KNOWN_DEV_CROSS_ATTACHMENT`-style finding is **DEV-internal only**, not a statement of DEV/PROD separation; active shared-host network paths and host forwarding remain unknown.
5. No `docker compose config`, generic `docker inspect` dumps, environment field extraction, executable command dumps, mount-source paths, published ports, network names, Redis URLs, secrets, process arguments, raw JSON output, site configuration, DNS resolution, Redis PING/PUBSUB, Frappe/SQL connections or operator desktop history. The Docker API is sensitive even for reads because a Docker-privileged user could affect both projects; only reviewed fixed-format extraction is eligible for a later explicitly approved run.
6. Fail closed on parse failures, unexpected API shape, legacy/absent Compose labels, inconsistent network or service metadata, permission errors, time-of-check/time-of-use changes and untrusted source text. Do not attempt recovery by restarting a container, reloading a config, changing a network, resolving names or retrying with elevated privileges.

**No Stage A output can prove PRODUCTION isolation**. At most it could independently support that named DEV service-role objects were present, running, project-labelled as expected, and met specific DEV-only metadata predicates at that instant.

## 4. Stage B: separate process-routing and active subscriber evidence (NOT part of Stage A)

Before writing any Stage B probe, review whether the service process runs (a) in one or several DEV containers, (b) under supervisor or bench processes, or (c) not at all, and whether observed process identities are stable. Metadata-only Stage A may not identify active Python/RQ or Node processes.

A future *distinct* DEV-only read-only design could consider:
- **Node WebSocket**: derive effective Node route **only** after identifying the actual running DEV Node process and establishing the source of its own `config.json` + common JSON + **that process's** `FRAPPE_REDIS_QUEUE` override. Do not open raw `/proc/*/environ`, Docker `.Config.Env`, command lines or arbitrary site files; these can reveal secrets. If the process-specific override cannot be safely recovered using a proven fixed-field method, report `NODE_ROUTE_UNVERIFIED`.
- **Python web and RQ workers**: verify live service presence/role and Redis configuration version without importing Frappe or executing any job. Installed source/bench config does not attest that a long-lived worker has reloaded it; cached connections can predate file state. Report `WORKER_ROUTE_UNVERIFIED` absent a narrowly defined, provably nonsecret process-specific readback. Do not query Redis CLIENT LIST or enumerate jobs/subscribers; those may reveal user/session data and constitute new access.
- **Service identity / DNS**: Container service labels and Docker attachment are not evidence that a hostname resolves to one Redis process; no DNS queries or redis/TCP connections are in scope now. A later proposed connection test must be a separately reviewed and explicitly approved operation with site- and PRODUCTION-impact review, not something folded into Stage A.
- **Pub/sub**: No synthetic `events` or `clear_persistent_cache` messages, Redis subscriptions, key reads, flush/clear, queue mutations, socket handshakes or user sessions. Static channel and subscriber source mapping is the only currently authorized layer.

This stage is **unimplemented** and no source/test claims should be made for it.

## 5. Sanitized evidence taxonomy and sample *design labels* (not runtime output)

All output labels are proposals, not an approved executable command. Use a fixed-size, fixed-vocabulary transcript. Example independent categories:

| Evidence dimension | Allowed illustrative statuses | Explicit limitation |
| --- | --- | --- |
| DEV target identity | `DEV_IDENTITY_OK` / `DEV_IDENTITY_STOP` | Compose-label match only; not physical separation |
| DEV role inventory | `DEV_REDIS_ROLES_PRESENT` / `DEV_ROLE_MISSING_STOP` / `DEV_ROLE_AMBIGUOUS_STOP` | Cardinality of DEV service roles only; no PRODUCTION peer enumeration |
| DEV networking | `DEV_NETWORK_METADATA_CHECKED` / `DEV_NETWORK_RISK_STOP` / `DEV_NETWORK_UNKNOWN_STOP` | Never output IDs/aliases/IPs; checked metadata does not prove no external reachability |
| Live Node subscriber | `NODE_ROUTE_UNVERIFIED` by default; no PASS without distinct later design | Node actual environment/process/connection not read |
| Live RQ workers | `WORKER_ROUTE_UNVERIFIED` by default; no PASS without distinct later design | Runtime cached clients not read |
| Cross-environment | `DEV_PROD_SEPARATION_UNVERIFIED` **always in DEV-only scope** | Only a separate production-scope review can change this |
| Release gate | `POSTING_NO_GO` **always** | Does not release Stock Entry/SLE/GL or rollback-only write |

Avoid status codes that invite false confidence (`ISOLATED`, `SAFE_TO_POST`, `NETWORK_CLEAN`, `PRODUCTION_NOT_REACHABLE`). Any unexpected data, missing role, stale snapshot, unavailable API or unauthorized scope must stop **without revealing raw fields or attempting more intrusive fallbacks**. The categories should distinguish *missing*, *duplicate*, *unknown* and *risk* rather than conflating all failures as a generic ambiguous STOP. Even `DEV_NETWORK_METADATA_CHECKED` must carry the explicit `DEV_PROD_SEPARATION_UNVERIFIED` line.

## 6. Adversarial OFFLINE fixture/test requirements for future code

Do not represent these as existing passing tests. A separate GitHub-only source/test approval is needed before implementation; the following is a contract to test later using **synthetic Docker responses** only.

- Missing, duplicated, stopped, mismatched-label DEV `frappe`/`redis-cache`/`redis-queue`; spoofed `com.docker.compose.*` fields; swapped service roles; empty or repeated container IDs; malformed/non-object Docker response and unexpected array/dict shapes.
- Empty networks, host/none/container modes, multiple attachments, unrecognized network aliases, changed container state between observations, network sharing uncertainty, and network metadata that includes foreign-project peer references. Never follow a foreign reference; STOP.
- Malicious untrusted strings containing terminal escape sequences, JSON fragments, newline injection, secrets, URLs, mounted paths, Unicode control characters; assert **only fixed status labels** reach stdout/stderr and that no field values, credentials, network IDs or secret-bearing exception text appear.
- Ensure the script refuses no flag, malformed flag and every **consumed prior** Redis approval token **before Docker**. Exact expected operator, mode/ownership/hash gating and exit-code handling must be exercised, including explicit success, detected-risk, ambiguity, exception, timeout and interrupted-input failures. Never use `try: sys.exit(main())` with `except BaseException`; subprocess-test the full exit path.
- Mock Docker CLI output and enforce an exact command/target allowlist. Assert no Docker exec, network-inspect peer enumeration, production container inspection, `/proc/*/environ`, Docker secrets/env/command dumping, Redis/DNS/SQL/bench connections, publish, config writes, volume modifications, restarts or cleanup.
- Snapshot consistency and partial-result tests: all required DEV roles checked or the entire run is STOP; no false all-PASS when one role/query fails.
- Feature/runtime presence and worker metadata must remain `UNVERIFIED` under Stage A; no synthetic fixture can establish cross-project or physical Redis separation without a later explicitly scoped evidence path.

Do not put real Docker or site records into test fixtures or GitHub. Never assert a passing offline suite establishes live Redis isolation.

## 7. Separate approvals, decision criteria, and unresolved blockers

**Current checkpoint:** Design-only artifact and handoff. No new executable script, test suite, staging artifact, hash pin for staging, server runtime read, Redis process snapshot, or Node/worker evidence produced.

**Gate D1 (future, separately authorized GitHub-only):** Review and implement a **new, isolated, read-only Stage A DEV Docker metadata candidate** with offline adversarial tests, bounded command allowlist, fixed output, no silent widening. Only pursue it if exact limited evidence is materially useful. GitHub versioned script and tests must be reviewed, hash verified, and still labeled NOT STAGED.
**Gate D2 (distinct owner approval):** Manually stage exactly that reviewed *new filename* from a pinned GitHub branch/commit and script SHA256 into an owner-only location outside the active worktree. Staging must not execute.
**Gate D3 (distinct one-shot owner approval):** Execute read-only DEV metadata diagnostic once with explicit one-operation authorization, fail-closed and no retry; collect only sanitized categories. No PRODUCTION metadata read.
**Gate D4 (new scope, not implied by any DEV-only result):** Determine whether worker/Node process-specific, physical Redis connection, cross-network, or **PRODUCTION** metadata inspection is truly needed. A production read or any cross-environment inspection **requires a separate explicit PRODUCTION-scope approval**, after assessing sensitive metadata and shared-host effects.
**Gate D5:** Independently review SQL child/series/bin/SLE/GL capture, cache/queue/pubsub pre-COMMIT effects, callback paths, idempotency/unknown-COMMIT failure, concurrency and recoverability; only then consider a separately authorized isolated rollback-only rehearsal, and much later a distinct persistent posting authorization.

**Current decision: NO-GO for write-then-rollback and first permanent Material Issue Stock Entry/SLE/GL. PRODUCTION untouched.** Docker Compose separation and successful REDIS URL format checks do not lift that decision.
