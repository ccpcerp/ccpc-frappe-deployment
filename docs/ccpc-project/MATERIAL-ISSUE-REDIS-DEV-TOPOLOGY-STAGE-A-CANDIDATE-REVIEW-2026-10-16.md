# CCPC ERPNext — DEV Redis topology Stage A metadata candidate review

**2026-10-16 | GitHub-only implementation and synthetic offline tests | NOT STAGED, NOT EXECUTED on Ubuntu | NO Material Issue posting**

## Authorization and scope

Owner explicitly approved Stage A **GitHub-only implementation**, synthetic adversarial offline tests, and documentation after reviewing the design [MATERIAL-ISSUE-REDIS-DEV-TOPOLOGY-EVIDENCE-DESIGN-2026-10-16.md](MATERIAL-ISSUE-REDIS-DEV-TOPOLOGY-EVIDENCE-DESIGN-2026-10-16.md). This approval does **not** cover staging, live DEVELOPMENT Docker/Redis/SQL/Node/worker inspection, configuration reads, PRODUCTION metadata or operations, rollback rehearsal, or Material Issue writes. All earlier one-shot approvals remain consumed.

### GitHub artifacts (review branch only)

Repository: `ccpcerp/ccpc-frappe-deployment`  
Branch: `review/material-issue-first-commit-preparation-2026-10-15`

- Candidate: [ccpc_material_issue_redis_dev_topology_stage_a_candidate_20261016.sh](../../scripts/development/operator/ccpc_material_issue_redis_dev_topology_stage_a_candidate_20261016.sh) — Git blob `d610b749eb212163ee08a99b314c143dad25453f`; SHA256 `fb0c2179ba69a51d8e251ead3304a727361bcf95d997edc8383037ffafc2576a`.
- Synthetic tests: [test_material_issue_redis_dev_topology_stage_a_candidate_20261016.py](../../tests/offline/test_material_issue_redis_dev_topology_stage_a_candidate_20261016.py) — Git blob `94727d1e727cbee18831bb72638d376c740b3f55`; SHA256 `076658614ba3b9856df9b240dc421208417de5ba3e5f7937bee6c0282d79e65c`.
- New file creation and test cleanup commits: `8acfc3290c9b351bac8a1dceeb1f222f62bed2eb`, `8d4b3993b12eb558171bf543dee1abdce7c03247`, `3ae49064bbbef72b15f273ab4d17547eebf037cc`. GitHub readback blob SHAs independently matched local tested source; no app source was changed.

## What Stage A does and does not measure

The reviewed script has a distinct single-use flag `CCPC_DEV_REDIS_TOPOLOGY_A_APPROVED`; absent/wrong/old flags refuse **before** Docker. It also restricts execution to nonroot user `gani`. These guards are **not** permission to use the flag now; they are defense-in-depth for a separately authorized future run.

The only prospective Docker commands are local Unix-socket `docker container ls -a --no-trunc` with **both exact DEVELOPMENT Compose project and individual service-role label filters**, and targeted `docker inspect --type container --format <fixed extraction>` of the three discovered IDs, twice. Required role set: `frappe`, `redis-cache`, `redis-queue`. The inspection extracts only the exact role identity, running state, network mode, and the named DEV network attachment ID. No raw inspected objects are printed. The code requires one stable exact container per role, names matching the expected Compose naming convention, a single expected `frappe_docker_devcontainer_default` attachment per role and matching network IDs; otherwise it STOPs. There is **no** `docker exec`, broad `docker ps`, Docker network peer listing, production inspection, env/command/mount dump, /proc read, site_config read, DNS/Redis/TCP connection, SQL/Frappe access, pub/sub publish, service mutation or transaction write.

The fixed output vocabulary distinguishes authorization/operator/prerequisite STOP, missing/duplicate/stopped/mismatched service roles, malformed metadata, network risk and changed snapshots. Even a synthetic **successful** Stage A case emits `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED` and `POSTING_NO_GO`.

**Limits:** The active DEV Compose file is Git-ignored and live Redis container names, attachment sets, Docker context and network mode are **not verified**. The candidate intentionally assumes narrow expected Compose container names and `frappe_docker_devcontainer_default`; a legitimate differently named/attached DEV may STOP until a separate scope/design review, not trigger relaxed fallback. A Docker label is not authenticated identity. Repeat inspection is not an atomic snapshot. Even a passing DEV-only metadata check cannot reveal non-DEV peers, prove DEV/PROD network separation, verify a Redis server/process/alias, attest the Node subscriber or RQ worker environment/cached clients, or undo pre-COMMIT Redis and pub/sub effects. Docker socket access is sensitive on a shared host even for read-only queries; any runtime approval must be reviewed separately.

## Offline verification

Executed in a disposable credential-free local workspace against **exact script/test bytes independently matched to GitHub blobs**:

```bash
bash -n scripts/development/operator/ccpc_material_issue_redis_dev_topology_stage_a_candidate_20261016.sh
PYTHONDONTWRITEBYTECODE=1 python3 -W error -m unittest discover -s tests/offline -p 'test_material_issue_redis_dev_topology_stage_a_candidate_20261016.py' -q
```

Result: **Ran 39 tests — OK (39/39 passing)**. Coverage includes default/consumed-token refusals, operator gate, exact Docker command shapes, synthetic successful full-shell run using fake `docker`/`id`, missing/duplicate/foreign/stopped roles, mismatched/suspicious names and project labels, host/none/foreign/multiple networks, network ID anomalies, malformed JSON/IDs, malicious strings/control sequences, changed two-pass snapshots, subprocess failure/KeyboardInterrupt and fixed-output/exact exit behavior. Synthetic fixtures use invented IDs only; **no live Docker socket, Ubuntu/DEVELOPMENT/PRODUCTION connection, Redis or database operation** was performed. This is *not* end-to-end runtime verification.

## Next separate consent gates

1. **Independent usefulness and security review before staging.** Assess whether strict name/network predicates and lack of atomicity justify a single narrow live DEV metadata run. If unsuitable, keep it as review-only and revise via GitHub with new review; do not deploy blindly.
2. Only after **specific new staging-only approval**, pin branch HEAD/full script SHA256 and use the approved private GitHub-to-Ubuntu delivery mechanism, under a fresh filename outside protected worktrees, without execution.
3. Only after **another distinct one-shot read-only DEV execution approval**, verify ownership, hash, nonroot context, fixed output, and STOP behavior before manual execution. Never reuse prior consumed permissions or auto-retry.
4. Node/WebSocket live process routing, Python/RQ worker Redis routes, physical Redis and cross-environment separation remain **separate unapproved gates**. Any PRODUCTION read—even metadata-only—requires its own explicit scope. Material Issue SQL/callback/cache/recoverability review remains independent.

**Status:** NEW STAGE A GITHUB-ONLY CANDIDATE + TESTS COMPLETE. **NOT STAGED. NOT EXECUTED.** No Material Issue write-then-rollback or permanent Stock Entry/SLE/GL posting permitted. PRODUCTION untouched.
