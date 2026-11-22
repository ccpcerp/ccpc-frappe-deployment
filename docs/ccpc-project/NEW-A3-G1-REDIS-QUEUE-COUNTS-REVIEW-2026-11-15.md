# NEW A3 G1 — Read-only Redis queue counts: GitHub-only review

**Date:** 2026-11-15 Asia/Manila. **Scope:** GitHub-reviewed source and isolated synthetic tests, followed by **one authorized, operator-reported NEW-host read-only Redis DB0 inspection**. This is not independent host verification or proof of queue/system quiescence. Draft [PR #35](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/35) remains unmerged. `G1_ACTIVATION_REVIEWED=False`; employee production cutover **NO-GO**.

## Baseline

- Operator-reported one-time pinned NEW backend process inspection: 19/19 container identities and six candidate process tables PASS, backend process count **3**, recognized worker/scheduler signatures **0**, startup worker/scheduler signatures **NO**. A zero signature count **does not** prove no async consumers or business writes.
- Generic review-branch `compose.yaml` has distinct `queue-short`, `queue-long` and `scheduler` definitions, but these are **not** evidence that they are running in NEW. The current R0 manifest pins 19 observed identities and the candidate backend image. Their state and identity must remain unchanged.
- Redis RQ conventions for queue lists and job registries are used for **fixed-key probes**, not enumeration or certified comprehensive discovery. Different installed RQ versions, custom queues, databases, registry naming and application work handlers may remain unknown.

## Reviewed source

- Python script: [`scripts/ccpc_new_a3_g1_redis_counts_readonly.py`](../../scripts/ccpc_new_a3_g1_redis_counts_readonly.py). SHA256 of exact reviewed UTF-8 bytes: `47e0320dff5857e861a9af217363194b9d2afaa60681dab9e98d479d6307d74c`. Verified Git blob: `f97b66f90926dfd741b626dc1fc32f41d5c53e14`.
- Synthetic 19-test suite: [`tests/test_ccpc_new_a3_g1_redis_counts_readonly.py`](../../tests/test_ccpc_new_a3_g1_redis_counts_readonly.py). SHA256 `85eddbd4fc460e7fda41bd71c426a503a2120a0e4b63243e3e66110131247a53`. Verified Git blob `34314c729b6cb7f16347602e7a4dcd5e815d36a1`.
- Offline validation: **19/19 PASS** in isolated Python unittest mocks, without Docker, Redis, host networks, NEW/OLD/DEV containers or real queues. This is a distinct suite from earlier 48/48 G1 mocks and 15/15 backend process tests; **no combined integration run was performed**.

## Bounded inspection contract

1. Requires root via `sudo` from `ccpcadmin` on `ccpcerp-prod`; rejects Docker context/host environment overrides. Reads original protected root-owned 0700/0600 R0 manifest **without changing or printing it**. Requires all 19 exact names, pinned full container IDs, expected running/stopped status, all `RestartPolicy=no`, backend image ID, and one matching pinned Docker network. Repeats the identity/policy snapshot after reading Redis.
2. Uses only `docker --host unix:///var/run/docker.sock ps -a --format ...` and `docker ... container inspect`. No Docker exec, Compose up, process signals, service changes, host writes, database imports, backup/restore, key scans or worker start.
3. Derives the Redis **queue** candidate bridge IPv4 from its pinned inspect record. Requires a private IPv4, a single expected Docker network, and the same Docker network ID as the backend. Attempts one bounded (5-second timeout) direct TCP Redis **DB 0** session on port 6379. No Redis AUTH credential acquisition or configuration reads; authentication rejection or inaccessible bridge endpoint leads to a sanitized STOP, **not** a workaround.
4. Sends only `DBSIZE`, `INFO clients`, `TYPE`, `LLEN`, `ZCARD`, and `SCARD`. Reads key counts and a connected-client count; only fixed conventional `default`, `short`, `long` RQ list and failed/deferred/scheduled/started registry names are probed. The registered-queue set is counted, **never enumerated**. No `GET`, `KEYS`, `SCAN`, `LRANGE`, `ZRANGE`, job IDs/payloads, arbitrary key names, personal data, secrets, or redis writes. Standard registered-queue/registry probes may not match the deployed version.
5. Reports only fixed names and decimal integer counts or `ABSENT` (rather than claiming missing keys have zero jobs). Output explicitly says other databases and unknown queues were not inspected; external consumers are unidentified; and the sample is **not atomic**. No safe-recovery/no-writes verdict is ever emitted. All protocol errors, malformed replies, data drift and identity failure yield only `CCPC_NEW_A3_G1_REDIS_STOP_REVIEW_REQUIRED` and exit nonzero.
6. A TCP connection and read commands can update Redis *internal connection and command statistics* transiently even though they do not change job/queue data; this is **not** a literally side-effect-free host action. No server password changes, firewall changes or retries to overcome access failure are approved.

## Offline fixtures

Nineteen unit tests cover positive queue/failed counts, registered-queue count greater than three (unknown queues), missing keys vs zero, wrong Redis key types, Redis NOAUTH/error redaction, INFO raw secret non-leakage, malformed protocol, socket refusal, operator/host/override mismatch, Docker identity and restart-policy drift, unexpected containers, private bridge IPv4 requirement, network ID mismatch, accidentally running drill backend, duplicate manifest IDs and absence of a false no-writes/recovery assertion.

**One owner-authorized NEW-host result is now reported by the operator (details below).** Its checks are observational; zero DB0 keys does not establish zero keys in other Redis databases/instances, absence of future work, worker isolation, deployed app code-to-image mapping, or OLD/NEW single-writer safety.

## Next controlled step

The one approved read-only NEW run is now complete; **do not rerun automatically**. Windows-to-NEW SCP using the existing operator SSH key succeeded, and the operator reported on-NEW SHA256 verification PASS before execution. No Redis server reconfiguration or worker start was reported. Next focus on GitHub-only deployed-image/source mapping and external-consumer/single-writer safety review, with separate authorization for any subsequent NEW inspection.

The next business-safety tasks remain deployed image/source mapping, external queue-consumer ownership, and OLD/NEW single-writer/duplicate GL-stock-purchasing prevention. Even a clean Redis counts report **does not authorize** enabling `unless-stopped`, G1 service/boot recovery, reboot, startup migrations, employee cutover or unreviewed PROD writes.


## 2026-11-15 — Operator-reported one-time NEW Redis inspection

- Source pin: reviewed PR #35 script Git blob `f97b66f90926dfd741b626dc1fc32f41d5c53e14`, full UTF-8 SHA256 `47e0320dff5857e861a9af217363194b9d2afaa60681dab9e98d479d6307d74c`. Operator's Windows PowerShell SCP reported **9,355 bytes** sent to `ccpcadmin@ccpcerp-prod`, followed by NEW output `CCPC_NEW_A3_G1_REDIS_SCRIPT_VERIFIED_PASS` and `CCPC_NEW_A3_G1_REDIS_SCRIPT_NOT_EXECUTED` before the subsequently authorized one-time execution.
- **Operator-reported stdout, not independently connected host evidence:** `REDIS_IDENTITIES_19_PASS`; `REDIS_PINNED_DB0_METADATA_PASS`; `REDIS_DB0_TOTAL_KEYS=0`; `REDIS_CONNECTED_CLIENTS_INCLUDING_AUDIT=4`; `REDIS_RQ_REGISTERED_QUEUE_NAMES_COUNT=ABSENT`. For **each** queue `DEFAULT`, `SHORT`, `LONG`, the `PENDING_LIST`, `FAILED_REGISTRY`, `DEFERRED_REGISTRY`, `SCHEDULED_REGISTRY`, `STARTED_WIP_REGISTRY` and `STARTED_ALT_REGISTRY` fields all reported `ABSENT`. Terminal marker: `CCPC_NEW_A3_G1_REDIS_READONLY_COUNTS_COMPLETE`.
- Inspector also explicitly returned `CCPC_NEW_A3_G1_REDIS_UNKNOWN_QUEUES_NOT_INSPECTED=YES`, `CCPC_NEW_A3_G1_REDIS_OTHER_DATABASES_NOT_INSPECTED=YES`, `CCPC_NEW_A3_G1_REDIS_EXTERNAL_CONSUMERS_NOT_IDENTIFIED=YES`, `CCPC_NEW_A3_G1_REDIS_SNAPSHOT_ATOMIC=NO`.
- **Interpretation:** at observation time, the pinned NEW redis-queue container's **DB0** held zero keys; canonical RQ queue and registry keys were absent (not present with zero length). The four Redis clients include the inspector and **were not identified**. No arbitrary queue data or payloads were read. **No assertion** about other databases, Redis instances, external consumers, future enqueues, automatic workers, pending side effects in other systems, or OLD/NEW business single-writer safety can be drawn. This does not change G1's BLOCKED gate.
- **No further live execution authorized or planned from this observation.** Do not repeat the diagnostic or enable auto-restart, G1 unit, Caddy/boot recovery, reboot, migrate or cut over employees without a new scoped decision. Continue with source/image mapping and OLD/NEW business write isolation gates.
