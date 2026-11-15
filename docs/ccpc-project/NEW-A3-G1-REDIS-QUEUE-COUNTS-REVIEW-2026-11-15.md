# NEW A3 G1 — Read-only Redis queue counts: GitHub-only review

**Date:** 2026-11-15 Asia/Manila. **Scope:** New source and offline synthetic tests only. **No deployment, NEW-host staging, execution, container/Redis operation, or G1 activation authorized by this commit.** Draft [PR #35](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/35) remains unmerged. `G1_ACTIVATION_REVIEWED=False`; employee production cutover **NO-GO**.

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

**No live result exists for this script.** Its checks are observational; empty or absent canonical queue keys cannot establish empty custom queues, an empty retry/delayed-work system, worker isolation, deployed app code-to-image mapping, or OLD/NEW single-writer safety.

## Next controlled step

Complete code review and, **only with specific separate one-shot NEW read-only runtime approval**, deliver the exact pinned script using the existing Windows-to-NEW SCP workflow (the attempted NEW-to-private-GitHub SSH fetch failed public-key authentication previously). Verify the full SHA256 on Windows **and NEW** before execution. No use of raw Redis output, passwords, secrets, key names, job IDs or raw `docker inspect` in chat. Stop on any mismatch; do not repeat automatically.

The next business-safety tasks remain deployed image/source mapping, external queue-consumer ownership, and OLD/NEW single-writer/duplicate GL-stock-purchasing prevention. Even a clean Redis counts report **does not authorize** enabling `unless-stopped`, G1 service/boot recovery, reboot, startup migrations, employee cutover or unreviewed PROD writes.
