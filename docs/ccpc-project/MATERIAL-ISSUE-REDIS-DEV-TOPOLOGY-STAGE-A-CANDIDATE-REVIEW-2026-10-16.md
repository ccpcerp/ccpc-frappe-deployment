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


---

## Final independent GitHub-only security and usefulness review — 2026-10-16

**Decision: DEFER STAGING.** Owner approved **review only**, not Ubuntu staging, runtime execution, DEVELOPMENT/PRODUCTION Docker inspection, or code/test modification. This final assessment is based on static GitHub inspection of the candidate, 39-case synthetic suite, design, and tracked DEV Compose template. The prior **39/39 synthetic PASS** is not a live Docker result and was **not rerun** in this review.

**Exact source reviewed:** script blob `d610b749eb212163ee08a99b314c143dad25453f`; offline tests blob `94727d1e727cbee18831bb72638d376c740b3f55`. The script and tests remain unchanged.

### Findings by priority

1. **BLOCKER — post-discovery metadata checks cannot enforce a no-foreign-object inspection boundary.** The script discovers IDs from `docker container ls` filtered on claimed Compose project/service labels, then invokes `docker inspect` on those IDs **before** checking the expected container name and metadata. Docker labels are not independently authenticated proof of origin. A mislabelled/substituted foreign container could be inspected before an eventual STOP. Therefore the script cannot substantiate an unconditional promise to inspect *only* actual DEV objects or never inspect a PRODUCTION object. A later implementation must establish a defensible pre-inspection DEV identity boundary or explicitly reduce the claimed guarantee; no broader Docker/PROD discovery is approved.
2. **BLOCKER — unbounded child-output buffering.** `subprocess.run(..., stdout=subprocess.PIPE)` buffers all stdout in memory; `len(result.stdout) > 4096` is checked **after** the subprocess has finished. The 4 KB threshold is a *validation check*, **not** a capture-time memory bound. Existing mock tests supply oversized completed results, not a bounded streaming or adversarial high-volume subprocess test. Fix before exposing the shared Ubuntu host to a future diagnostic.
3. **MATERIAL — Docker template/runtime shape unverified.** The success fixtures exactly reproduce the candidate's assumed `docker inspect --format` output: six JSON fields plus one network-attachment line. The tests do not execute real Docker Go-template parsing or verify actual host Docker version, `--no-trunc`, `HostConfig.NetworkMode`, newline behavior, or network attachment output. A format mismatch may safely STOP but give negligible diagnostic evidence.
4. **MATERIAL — strict network/container-name assumptions may STOP on valid DEV.** Exact container names `frappe_docker_devcontainer-{frappe,redis-cache,redis-queue}-1`, sole attachment to `frappe_docker_devcontainer_default`, and an identical NetworkMode are assumptions from tracked template conventions, **not observed running REDIS service identities**. Do not relax/fallback to broad Docker discovery without a separately approved design.
5. **MATERIAL — operator executable provenance is not bounded.** The script resolves `id`, `docker`, and `python3` through inherited `PATH`; the existing mocked PATH tests demonstrate substitution is possible, **not** that an operator host PATH/binaries are trustworthy. A future delivery and execution review must check those assumptions as well as file ownership/SHA256, without accessing PROD.

### What remains positive but limited

The new approval guard rejects old tokens; selected Docker commands use narrow project/service label filters, exact-field formats, strict JSON/cardinality checks, two snapshot reads, suppressed raw errors and fixed output vocabulary. No SQL, Redis, site config, Node/RQ process, network-peer enumeration, pub/sub publication, Docker mutation or ERPNext transaction call is present in the reviewed source. Every outcome retains `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED`, and `POSTING_NO_GO`.

**Usefulness:** At best, this tool could confirm three Compose-labelled running objects and certain DEV network metadata predicates at an instant. It does not prove Redis instance identity, actual worker/WebSocket transport, inter-project isolation, or reversible pre-COMMIT Redis/cache/pubsub effects. The present incremental value does **not** justify a staging cycle while blockers remain.

**Next separate authorization gate:** Request a focused **GitHub-only revision and adversarial tests** addressing pre-inspection DEV scope and bounded subprocess output first. Also decide whether a truly useful DEV-only topology check can be made without observing non-DEV objects; verify Docker formatting/provenance from trusted sources before any future staging proposal. If absolute no-foreign inspection cannot be established, do not claim it. Revised code, its offline checks, and security review must precede any separately requested **staging-only** permission, followed by a distinct **one-shot DEV read-only execution** permission.

**NO-GO:** Current Stage A script is **REVIEW-ONLY, NOT STAGED, NOT EXECUTED**. Material Issue write-then-rollback and permanent Stock Entry/SLE/GL remain **NO-GO**. No PRODUCTION interaction.
