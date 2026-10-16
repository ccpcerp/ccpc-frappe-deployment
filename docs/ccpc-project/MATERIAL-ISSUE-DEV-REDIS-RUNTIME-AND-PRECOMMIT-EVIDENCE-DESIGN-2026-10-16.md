# CCPC ERPNext — Alternative DEVELOPMENT Redis runtime and pre-COMMIT effects evidence design

**2026-10-16 | GITHUB-ONLY DESIGN | NOT AN EXECUTABLE DIAGNOSTIC | NO UBUNTU / DEV / PROD RUNTIME ACCESS | MATERIAL ISSUE WRITE-THEN-ROLLBACK AND COMMIT: NO-GO**

## 1. Decision, consent and authoritative source scope

After [Stage A v2 final review](MATERIAL-ISSUE-REDIS-DEV-TOPOLOGY-STAGE-A-V2-REVIEW-2026-10-16.md) concluded **DEFER STAGING**, the owner approved a **separate GitHub-only alternative evidence design** focused on actual Node/RQ Redis routing and pre-COMMIT cache/pub/sub behavior. The approval authorizes current GitHub source inspection, an evidence architecture, review documentation and rolling handoff only. It is **not** consent to develop/execute a host diagnostic, inspect a live process or config file, query Docker/Redis/DNS/SQL, modify an app, pull to DEVELOPMENT, restart workers, publish events, stage a script, run a transaction, or read PRODUCTION metadata.

**GitHub refs verified at design start:**
- `ccpcerp/ccpc-frappe-deployment@review/material-issue-first-commit-preparation-2026-10-15` commit `6782b25e0d20caea753ff1d9ec6a34788d120e85`.
- `ccpcerp/ccpc-frappe-deployment@docs/ccpc-checkpoint-2026-10-10` handoff commit `6f40d2e2e0660996980c8167a5256076181e0052`.
- `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` commit `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`.
- Baseline reviewed Frappe source ref `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`. **This does not attest to the exact framework build currently loaded in a running DEVELOPMENT process**.

The previous Redis endpoint-shape / label investigations, Stage A v1 and Stage A v2 remain historical evidence or review-only artifacts with their exact former permissions **consumed**. Do not replay, stage or broaden them. A passing 39/39 synthetic suite is not proof of live transport or transaction isolation. The DEV and PROD environments share an Ubuntu host and Docker daemon, so no DEV-only claim may be represented as physical or network separation from PRODUCTION.

## 2. Source-based hazard map for the actual Material Issue path

| Verified pinned source | Observed behavior in GitHub | Consequence for evidence / risk |
| --- | --- | --- |
| [CCPC withdrawal posting](https://github.com/ccpcerp/ccpcerp/blob/2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6/ccpcerp/ccpc_erp/withdrawal_slip_stock.py), Git blob `771d27781f8d933fd243415e8286976fbdd1a861` | `issue_withdrawal_slip` locks/checks the slip, creates and inserts a draft Stock Entry, calls `submit()` (ordinary Stock Entry validation/ledger/GL hooks), returns without an explicit local commit. `sync_withdrawal_slip_issue_status_for_name` writes issue/status fields and calls `frappe.clear_cache(doctype="Withdrawal Slip")`. | Database atomicity intent is present, but the submission call graph includes cache effects. No proof that all side effects remain reversible until SQL COMMIT. |
| [CCPC hooks](https://github.com/ccpcerp/ccpcerp/blob/2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6/ccpcerp/hooks.py), blob `023dc7b04b8f4fa019654c074124bd03f3b82489` | Stock Entry `validate`/`before_submit` check CCPC safeguards, and `on_submit` calls the slip synchronization above. | Include both CCPC and framework/ERPNext Stock Entry hooks in any future complete side-effect audit; unit tests mocking Stock Entry do not exercise full posting callbacks. |
| [Frappe cache manager](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/cache_manager.py), blob `fc4cb7e0d15c893fd0baf4d289de1e3deb70950d` | `clear_cache(doctype=...)` calls `clear_doctype_cache`, which immediately erases local/client caches and invokes `_clear_doctype_cache_from_redis`, **then** adds an after-COMMIT callback and an after-ROLLBACK callback for Redis cache clearing. | The immediate invalidation is not undone by SQL rollback. After-ROLLBACK cache invalidation is intentionally possible. Distinguish reversible database state, cache invalidation (usually reconstructible but externally visible), and irreversible/fanout side effects; avoid claiming "clean rollback" solely from SQL. |
| [Frappe database transaction manager](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/database/database.py), blob `a2ba78e2488f03810d58c43c768b4fbab624c3dc` | `commit()` runs before/after-COMMIT callbacks; full `rollback()` runs after-ROLLBACK callbacks. Savepoint rollback does **not** run those transaction watchers. | Explicitly distinguish full rollback from savepoint rollback. Watchers are not an isolation boundary for already-emitted Redis writes/events. |
| [Frappe realtime](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/realtime.py), blob `7e8e31f1b0a8d4362d51ba108f26e3c795c2e21a` | `publish_realtime(after_commit=False)` emits immediately on literal Redis channel `events`; `after_commit=True` buffers with transaction callbacks, except certain task-progress cases force `after_commit=False`. | Any actual hook invoking immediate realtime can publish before a subsequent SQL rollback. No test message may be emitted merely to identify a channel. |
| [Frappe Node subscriber](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/realtime/index.js), blob `f3337103829e956cdbe15d1c696c81dc796d1ffe`; [Node config](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/node_utils.js), blob `0fc5a37189e4e49ac64a1bb850669d1e3f100d5a` | Node subscriber uses `get_redis_subscriber()` default `redis_queue`, loads bench config and common config then Node process env overrides, and subscribes to literal `events`. Message namespace is used for Socket.IO routing **after** subscription; missing room can fan out. | Logical namespace in event payload does not establish Redis transport separation. A freshly started Node child reading files does not attest to a long-lived subscriber's actual connection. |
| [Frappe RQ worker/queue](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/utils/background_jobs.py), blob `a5f5b206d64d71a79dfb4ce81d899fe219299196`; [Redis wrapper](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/utils/redis_wrapper.py), blob `8a48e16afc91c14e10644058fea950e0d41a4124` | Long-running RQ starts from a Redis connection; the queue connection may be cached in `_redis_queue_conn`. Redis cache wrapper may maintain local cache and Redis client tracking; namespaced key strings are **not** proof of server independence. | A configuration-file comparison and mock tests do not identify existing cached Redis clients, sockets, in-flight jobs, or real worker route. |
| [Frappe config](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/config.py), blob `631a79d8283d2ae04f1fb4b95c2da4dba9f0450b` | Redis configuration combines common/site values, optional dynamic `extra_config`, and environment overrides; some config views are cached. | Static labels are only **declared routing intent**, not proof of effective long-lived Node/Python process settings. |

**Source limitations:** The above is a bounded source-path review, not proof of every transitive ERPNext stock/GL hook, custom app hook, notification, worker or middleware side effect. Installed ERPNext/Frappe versions, running supervisors, active DEVELOPMENT Compose config, per-process Redis clients and network connections have **not** been freshly attested. No Stock Entry or SLE/GL was created in this review.

## 3. Evidence tiers and their honest conclusions

| Tier | Future evidence artifact | May conclude | Must NOT conclude |
| --- | --- | --- | --- |
| **E0 — GitHub static path inventory (first preference)** | Pinned call graph of CCPC hooks + installed-version Frappe/ERPNext source; classify each external effect as immediate, after commit, after rollback, background, conditional or unknown | Source-level *potential* for pre-COMMIT effects, and whether a reviewed code path attempts to defer them | Actual runtime no-event/no-worker property; Redis server or DEV/PROD isolation |
| **E1 — offline deterministic instrumentation (separate implementation approval)** | Credential-free mocks of Redis clients, enqueue, realtime, cache, callbacks, and simulated commit/rollback, recording only synthetic event types and order | Code-path ordering and callback registration in tested mocked conditions | Complete live ERPNext/SQL integration or actual subscriber/worker routing |
| **E2 — explicitly DEV-bounded runtime process attestation (separate design + operator authorization)** | A narrowly authorized *running-process-specific* attestation channel/observer that can prove it is attached to a designated DEV process and reveal only fixed nonsecret relation flags, not endpoints or secrets | A particular *identified* DEV Node/RQ process's loaded config and, if safely accessible, existing Redis client/connection classification **at observation time** | Transport isolation from PRODUCTION, absence of other listeners/jobs, or complete running-process population absent independent census |
| **E3 — real route and side-effect boundary proof (currently blocked)** | Independently proven route ownership / separation and no externally observable pre-COMMIT effects, possibly needing credentials/network/PROD-sensitive evidence | Only facts directly supported by a separately reviewed, scoped procedure | Never infer physical isolation from E0–E2, labels, IP spellings, site names or rollback success |

**Architecture decision:** Do not attempt E2/E3 through the shared Docker daemon, Docker network inspect, daemon-wide container/process enumeration, Redis `CLIENT LIST`, Pub/Sub `SUBSCRIBE`, test `PUBLISH`, DNS/network probing, `/proc/*/environ`, Node process arguments, Redis URL dump, raw site config, or generated user traffic under the present authorization. An instrumented DEV-only observer **might** be proposed later, but adding code into live processes or restarting services is a separate app/infrastructure change with rollback and cross-environment review. If such an observer cannot unambiguously bind to DEV without peeking at PROD, E2 is **UNAVAILABLE/STOP**, not a reason to weaken isolation restrictions.

## 4. Safe next engineering unit: source-level pre-COMMIT effect audit

This is **a future design contract, not code currently written**.

1. Pin the actual CCPC app commit plus all pertinent ERPNext/Frappe framework source commits and active hook registrations in GitHub; for *runtime* equivalence later, separately attest the loaded DEV build without secrets or changes. Existing Frappe pin is a reference baseline only.
2. Begin at `issue_withdrawal_slip` → `Stock Entry.insert` → `Stock Entry.submit` → core ERPNext stock/valuation/SLE/GL and CCPC `on_submit` → `sync_withdrawal_slip_issue_status_for_name` → `frappe.clear_cache`; inspect transitive hooks and exception paths, including duplicate submit, issuer authorization and concurrency protections. Identify which calls may publish, cache-invalidate, enqueue, send notifications, write files, or call third-party services **before, during, and after** the SQL transaction.
3. Build a **side-effect classification matrix**: trigger/caller, site/process context, effect, transaction timing, rollback behavior, namespace/recipient scope, whether the call is conditional or uncertain, confidence and exact source SHA/line. For each effect, distinguish *reversible DB-only*, *cache invalidation/repopulation*, *queued transaction callback*, *independently delivered pub/sub*, *asynchronous job*, *unknown*. Do **not** declare immediate cache invalidation automatically catastrophic, but do not declare it rolled back.
4. Design **offline negative tests** with all network/Redis/SQL interfaces mocked. Include exception before Stock Entry insert, failure after insert/before submit, failure within submit hooks, multiple/failing after-commit and after-rollback callbacks, duplicated issuance attempts, and immediate versus deferred realtime. Assert that no actual Redis/pubsub or business-data operation occurs. These tests would detect only the code paths included in the fixture, not runtime side effects.
5. If the matrix reveals an unacceptable immediate effect, separately review a **GitHub-only code-change proposal** to move *eligible* custom side effects to after-COMMIT or adopt an appropriate read-safe invalidation strategy. Do not change framework cache semantics or suppress required rollback invalidation speculatively. Application changes and DEV integration still need distinct approvals.

A static analysis finding **does not grant** permission to run a write-then-rollback trial. A low-risk cache clearing may still be visible to a shared Redis service; evaluate effect impact separately from transaction irreversibility.

## 5. Process-specific Node and Python/RQ route evidence: design, not an executable probe

A route-evidence request must answer the following *without* borrowing the environment of a short-lived `docker exec` child:

- **Node/WebSocket:** Which exact DEV-resident *currently running long-lived Node subscriber* instantiated `get_redis_subscriber()`? Did it read `config.json` and common config at startup? Was `FRAPPE_REDIS_QUEUE` overridden in **that process**? Does its **existing** Redis client prove anything about an established connection, not merely a parsed URL? Is more than one Node subscriber active?
- **Python/RQ:** Which exact DEV-resident *currently running worker processes* execute RQ? From which startup config, site/bench context, environment override, and cached `_redis_queue_conn` did each active connection originate? Did the configuration change after process start? Are there worker pools/forks and clients with distinct routes?
- **Boundaries:** Who independently attests that observer, process, bench and site are genuinely DEV without shared-daemon/PRODUCTION inspection? Can secrets, endpoint strings, credentials, user/job/session data, PID/command-line disclosures and raw environment be excluded **before acquisition**, not merely scrubbed afterward? Can it show actual connection ownership without creating or switching a connection?
- **Evidence output:** Permit only fixed pass/fail/unknown statuses and a high-level category count after scope is proven; never print raw process identifiers, network addresses, DNS names, Redis URLs, paths, queue names, tokens, site config, credential material, worker payloads or the source data from which they were derived.

Until there is a separately reviewed *process-native, existing-client, read-only* mechanism and a genuinely verified DEV identity boundary, mark:
`DEV_PROCESS_PROVENANCE_UNVERIFIED`,
`NODE_ROUTE_UNVERIFIED`,
`WORKER_ROUTE_UNVERIFIED`,
`REDIS_INSTANCE_IDENTITY_UNVERIFIED`,
`DEV_PROD_SEPARATION_UNVERIFIED`.
Do not print `NODE_ROUTE_OK` or `WORKER_ROUTE_OK` on the basis of a config-file match, static code, mock fixture or Compose role. An observer might require operational changes; **there is no currently approved way to install or start it**.

## 6. Threat model and explicit STOP conditions

Hard STOP on inability to establish DEV-only observer process identity independently of untrusted Compose labels; service/process count ambiguity; cached clients not introspectable without new traffic; dynamic config hooks/environment unknown; mismatching installed-version source; credentials or addresses needed in raw output; any cross-env socket/network/prod lookup required; any suggested event publish/subscribe or cache modification; a stale or changing process during observation; live test requiring stock/GL or rollback-only mutations; and any attempt to reuse previous one-shot tokens.

Even a purely DEV process connection address cannot by itself prove what physical Redis server or other subscribers it reaches. Shared-host and DNS alias risk persists. No PRODUCTION reads or tests may be "included for completeness" without **new and precise owner approval**, and PRODUCTION writes/deployments are wholly separate.

Proposed sanitized acceptance record vocabulary (examples only, **not** achieved statuses):

| Dimension | Permissible design label | Mandatory caveat |
| --- | --- | --- |
| GitHub source effect map | `SOURCE_EFFECT_MAP_COMPLETE` / `SOURCE_EFFECT_MAP_INCOMPLETE_STOP` | Complete only relative to explicitly enumerated pinned files/hooks |
| Mocked callback sequencing | `OFFLINE_ORDERING_PASS` / `OFFLINE_ORDERING_STOP` | Synthetic and credential-free, never live |
| Process scope | `DEV_PROCESS_PROVENANCE_UNVERIFIED` | No live attestation yet |
| Node, RQ clients | `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED` | Do not infer from files or new child process |
| Physical transport | `REDIS_INSTANCE_IDENTITY_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED` | Always in currently approved DEV-only/GitHub-only scope |
| Posting | `POSTING_NO_GO` | Unconditional until independently approved business/transaction gates |

## 7. Decision path, approval gates and completion criteria

- **G0 — COMPLETED BY THIS DESIGN ONLY:** GitHub source review; hazard map and plan documented on deployment review branch; current rolling handoff updated. No runnable code produced, no test run claimed.
- **G1 — separately authorized GitHub-only E0/E1 implementation:** Prepare a narrowly scoped side-effect call-graph inventory and synthetic ordering tests with source-version pins. Validate with fresh offline tests; commit and readback. No Frappe DB/Redis calls or mutations even if the tests import mock targets.
- **G2 — separately authorized process-native runtime design/implementation:** Only if a credible independent DEV-only process binding exists and can yield more than file-config labels; design security review first, then separately authorize implementation and any staging. No restart or worker/process impact without explicit approval.
- **G3 — separately scoped DEV runtime run:** Stage an exact script/build only after explicit staging consent and SHA256/branch verification. Distinct one-shot execution consent, exact target, stable nonroot identity and fail-closed output. Any service restart or app deployment is a *different* approval, not implicit in a read-only diagnostic.
- **G4 — separate Material Issue acceptance:** Evaluate user-facing behavior, concurrency, duplicate prevention, permissions, SLE/GL account integrity, backups/recovery and independently justified side-effect isolation before any new rollback-only or persistent Stock Entry/ledger write. **No permission now**.

**Recommended next action:** pursue **G1 only**—a pinned static pre-COMMIT effect inventory plus credential-free offline callback ordering assertions. It directly addresses a confirmed `frappe.clear_cache` side-effect path and avoids the shared Docker daemon entirely. Do **not** request staging for Stage A v1/v2. If G1 cannot account for all relevant runtime hooks, explicitly keep the source effect map partial and POSTING_NO_GO.

**End state:** Design-only GitHub milestone. DEVELOPMENT runtime and PRODUCTION unchanged; no Docker, Node, RQ, Redis, SQL, or business transaction touched. **Material Issue write-then-rollback and committed Stock Entry/SLE/GL posting: NO-GO.**
