# CCPC ERPNext — Redis endpoint-label read-only candidate (separate reviewed v1)

**2026-10-16 | GITHUB-ONLY DEVELOPMENT + OFFLINE SYNTHETIC TESTS | NOT STAGED, NOT EXECUTED ON UBUNTU | PERMANENT MATERIAL ISSUE POSTING: NO-GO**

## Authorization and verified sources

After the successful, consumed, separately approved v2 **URL format-only** DEVELOPMENT diagnostic, the owner explicitly approved **GitHub-only preparation and offline testing** of a **new** configured Redis endpoint-label comparison. No Ubuntu/DEVELOPMENT/PRODUCTION command, remote staging, Docker entry, Redis or SQL connection, Frappe initialization, restore, Stock Entry/SLE/GL posting, app checkout change or automation is included in this approval.

Starting verified branch tips were:

- `ccpcerp/ccpc-frappe-deployment@review/material-issue-first-commit-preparation-2026-10-15`: **`0af5284e7701a67a43db60d14e75d5a73bbed547`**.
- `ccpcerp/ccpc-frappe-deployment@docs/ccpc-checkpoint-2026-10-10`: **`f4f0165f955bb5a3005a5beebb9f4dc40346b0c7`**.
- `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety`: **`2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`**.
- Reviewed framework source is pinned to `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`: `frappe/config.py` blob `631a79d8283d2ae04f1fb4b95c2da4dba9f0450b` and `node_utils.js` blob `0fc5a37189e4e49ac64a1bb850669d1e3f100d5a`. These are **pinned source baselines, not asserted running process versions**.

See [GitHub-only isolation source review](MATERIAL-ISSUE-REDIS-ISOLATION-SOURCE-REVIEW-2026-10-16.md) for DNS, Node, workers, pub/sub and transaction blockers. The previously consumed original Redis endpoint preflight (Git blob `85123cd4d487110d01cdc375ad7e6969035bdc34`) ended in an unclassified STOP. The earlier consumed JSON/format v2 completed successfully but did **not** compare endpoints. Neither script was altered or replayed.

## New distinct, inert-until-authorized GitHub files

Repository `ccpcerp/ccpc-frappe-deployment`, branch `review/material-issue-first-commit-preparation-2026-10-15`:

- [New configuration-label candidate](../../scripts/development/operator/ccpc_material_issue_redis_endpoint_labels_readonly_candidate_20261016.sh) — exact Git blob **`ddd56afef0e8b5c6f61aedcc7975ce0a8ec0f8cc`**, SHA256 **`568a7554b0a7c7e8d9182842cb57de1d9ae6231a472a503228d0194d95392c9f`**. Initial create commit `44d110d50f49244f8b9aed5533b94bdb6df6363c`; final source safety update commit **`073f0c1493ba3e47f741439ccb522cecf42621d5`**. The new environment approval gate `CCPC_REDIS_LABELS_V1_APPROVED=ccpc-redis-labels-v1-one-shot` is distinct from the two previously consumed Redis scripts; when unset or set to an old flag, it **exits before Docker**.
- [New synthetic offline regression tests](../../tests/offline/test_material_issue_redis_endpoint_labels_readonly_candidate_20261016.py) — exact Git blob **`84a0ecf7606c903bdc0e3f0e80dcb5afd5112cd4`**, SHA256 **`c31fa6ce9a131ba63d3b8eb4d7a5f38d630333599a30044c8260259791eb889c`**. Initial create commit `cc76808b50c99bb6e405c8163d44fc730e0d4ae0`; final test amendment commit **`c9bc5077dc184dee203f0c3e91a92a58ff93ed15`**.

The final GitHub script and test blobs were independently **read back and confirmed to equal the exact locally tested Git blobs**, not merely presumed to match names. There are no credentials, configurations or business records in the committed artifacts.

## What the reviewed candidate would do — only after future separate approvals

1. Require a normal nonroot Ubuntu operator, an exact running container `frappe_docker_devcontainer-frappe-1` with Compose project/service `frappe_docker_devcontainer|frappe`, and a new, exact one-shot environment approval gate. **No staging/execution approval exists today.**
2. Open only the bounded, nonsymlink, regular-development configuration JSON files: `sites/common_site_config.json`, `sites/ccpc-integration2.localhost/site_config.json` and `sites/development.localhost/site_config.json`. Each has a 65,536-byte maximum. Read only `FRAPPE_REDIS_QUEUE` and `FRAPPE_REDIS_CACHE` from the **exec-child** environment; no shell process-environment dump. Suppress container/Python stderr, never print raw JSON, hostname, port, endpoint hash, URLs, credentials, stack traces or Redis data.
3. Model pinned Python configuration as **common → site → environment last**. Fail closed if `extra_config` dynamic hooks or Redis Sentinel are declared (scope deliberately unsupported), JSON is invalid, endpoint URL malformed, or file identity is unsafe. For Node's **bench-level** Redis queue, model only common+exec-environment when an explicit value is available; **do not claim** to model the unexamined Node `config.json` or a live WebSocket worker's environment. No Redis, Node or Frappe process is initialized.
4. Normalize opaque Redis **host+port** identities conservatively, collapsing `localhost`, IPv4/IPv6 loopback, IPv4-mapped IPv6 and obvious hostname case/trailing-dot aliases. Ignore DB number, username/password and TLS when testing for physical collision (those do not create separate Redis instances). Treat unknown DNS names, different DNS aliases, Sentinel and unsupported dynamic routing as ambiguous, **not safe**. Compare within isolated-site cache/queue; compare isolated roles against all shared-site cache/queue roles; flag when the bench-level Node queue equals either site's cache endpoint label. Return only fixed labels:
   - `CONFIGURED ENDPOINT LABELS: OVERLAP_STOP; POSTING: NO-GO` with nonzero status for a known normalized collision.
   - `CONFIGURED ENDPOINT LABELS: AMBIGUOUS_STOP; POSTING: NO-GO` with nonzero status when DNS identity or input modelling is insufficient.
   - `CONFIGURED ENDPOINT LABELS: NO_EXACT_LABEL_OVERLAP; ISOLATION: UNVERIFIED` and `NODE/WORKER/PUBSUB/PHYSICAL: UNVERIFIED; POSTING: NO-GO` for only a synthetic/config-label disjointness finding, not for physical isolation. Shell termination echoes only `REDIS LABEL REVIEW V1: COMPLETED/STOPPED; POSTING: NO-GO`.
5. Explicitly **no DNS queries**, Redis PING/GET/PUBSUB/publish, SQL, live Frappe hooks, service inspection outside the one DEVELOPMENT identity, PRODUCTION container reads, event emission or writes. It cannot verify active worker/Socket.IO environment, Redis service instance identity, cross-Compose network reachability, bus subscriptions or rollback safety.

**Important conservative trade-off:** Tracked Compose commonly uses DNS service labels like `redis-cache` and `redis-queue`. The candidate will intentionally report `AMBIGUOUS_STOP` for disjoint unresolved DNS names, even when their spelling differs. That is **not** evidence of configured overlap, only that label comparison cannot prove distinct physical services. A `NO_EXACT_LABEL_OVERLAP` finding is equally **not** permission for rollback tests or financial posting.

## Exact-source offline test evidence

Credential-free, local-only workspace contained the reviewed script and the 43-case test file with exactly the Git blob SHAs above, verified independently against GitHub. The final suite command was:

```bash
cd /mnt/data/ccpc_redis_label_v1_review
PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover \
  -s tests/offline -p 'test_material_issue_redis_endpoint_labels_readonly_candidate_20261016.py' -q
```

**Result: `Ran 43 tests in 0.384s — OK` (43/43 PASS).** This is **not a DEVELOPMENT database or Docker integration test**. Tests covered Bash `-n`, Python syntax, entry-point subprocess success/failure/exception redaction, one-shot gate refusal (including old v2 gate), Docker identity ordering and absence of mutating/network calls, full real Python `main()` on synthetic local files, known host/IP/loopback normalization, Redis/TLS/password/DB-number aliasing, within-site and cross-site collision STOP, Node queue-to-cache collision STOP, mismatched Node/worker routing remaining unverified, alternate DNS/Node ambiguity, malformed/oversize/symlink/FIFO config, missing node common/exec queue, dynamic `extra_config`/Sentinel and fixed-only output checks. No live site file, Redis, Docker or PRODUCTION service was read or contacted.

**Meaningful remaining limitations:** Tests are synthetic and include static source assertions, not proofs against all Python runtime capabilities; no real Docker instance or Redis network was exercised. A future code-review pass must still judge `config.json`/worker env ambiguity, unsafe alias equivalences, and whether even a read-only runtime diagnostic is worth performing given likely DNS `AMBIGUOUS_STOP` outcomes. Do not interpret test PASS as a physical isolation or first Material Issue go-live gate.

## Next decision / approval boundaries

**Current status: review-only GitHub artifact, NOT STAGED; NOT EXECUTED on Ubuntu.** Owner's GitHub-only approval is consumed. If the owner wants a future DEVELOPMENT diagnostic, first reverify latest GitHub branch and byte-identity, assess whether a DNS-name comparison offers sufficient information given active config, then obtain **separate explicit staging-only consent** for this exact new filename and verified SHA256. Staging cannot execute. After operator reports successful staging, obtain **a distinct explicit one-shot read-only execution approval**; never use any consumed script/gate or auto-retry. Still more independent review and separately approved evidence will be necessary for physical Redis/worker/pubsub isolation; any PRODUCTION metadata operation—even read-only—requires its own scoped explicit permission. Permanent Material Issue Stock Entry/SLE/GL posting and even a new live write-then-rollback rehearsal remain **NO-GO**.
