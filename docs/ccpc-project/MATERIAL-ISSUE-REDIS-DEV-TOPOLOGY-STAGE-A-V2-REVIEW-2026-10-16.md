# CCPC ERPNext — Stage A v2 bounded DEV-labelled Redis topology candidate

**2026-10-16 | GitHub-only implementation; NO Ubuntu staging/execution or PRODUCTION access | NO Material Issue posting**

## Scope and immutable source

Owner approved **GitHub-only corrections and adversarial offline tests** after the Stage A final security review deferred staging. It did **not** approve using the new execution token, staging on Ubuntu, Docker access, database/Redis operations, PRODUCTION metadata, app changes, or any write-then-rollback or permanent Material Issue posting.

Repository: `ccpcerp/ccpc-frappe-deployment`, branch `review/material-issue-first-commit-preparation-2026-10-15`.

- [New, separate Stage A v2 script](../../scripts/development/operator/ccpc_material_issue_redis_dev_topology_stage_a_v2_reviewonly_20261016.sh); verified Git blob `e8af1dd3c7f15f066d9572fbd5cc5b4119737d47`; exact UTF-8 SHA256 `d3c227ae219de448ee7ef96626924c23c06619f42db264767cb2aa2326c4b68d`. Created by `cd100d2bb08542a784e833c033b8197727616f92`.
- [New 39-case credential-free v2 offline tests](../../tests/offline/test_material_issue_redis_dev_topology_stage_a_v2_reviewonly_20261016.py); verified Git blob `86963b7149d4055e5e11d3c5b336db30d572716b`; exact UTF-8 SHA256 `827ba8fd51a718dfdc304399eb2c2f03380c38867f0bd26a1dbc23b22c4031f9`. Created in `d100352f401251161138133f42fa9ac72377f263`, then corrected an escaped invalid-UTF8 test fixture in `0f5a94666f9eeed5dad1aa564f221aca925716c1`; GitHub readback of **final bytes** independently matched the local tested file.
- **Original Stage A v1 script and its 39-test suite remain unchanged, un-staged and un-executed.** No automatic replay or use of a consumed approval token.

## What changed and what the 4 KB bound means

The earlier `subprocess.run(...stdout=PIPE)` read **all bytes before checking size**. It was NOT a memory cap, and 4,096 was a project-chosen threshold, **not a default Docker/Python/Ubuntu/ERPNext limit**. The v2 `bounded_docker_read` uses `Popen` + `selectors` + fixed-size `os.read`: it reads **no more than 4,097 output bytes per Docker CLI invocation**, rejects over 4,096, kills the child on excess or timeout, and discards stderr rather than printing raw Docker bytes. A hard six-second deadline applies per invocation. This is a **stdout capture bound**, not a whole-process memory, kernel pipe, Docker daemon resource, or host-wide RAM guarantee.

For reduced inspection scope, v2 makes **only** filtered `docker container ls -a --no-trunc` requests, exactly three named DEV-labelled roles (`frappe`, `redis-cache`, `redis-queue`), each requested in two snapshots. It does **not** follow discovered IDs with `docker inspect`, inspect networks/peers, enumerate all containers, read environment/commands/mounts, run Docker exec, contact Redis, SQL, Node, RQ, site config or perform any write. Docker output is limited to `.ID`, `.Names`, `.State`, `.Networks`, and two exact Compose label values via the documented Docker `container ls --format` placeholders. <https://docs.docker.com/reference/cli/docker/container/ls/>

The script uses separate unconsumed **v2-only** approval flag (which is **not authorized for runtime use** merely because it is in source), checks nonroot operator `gani`, and resolves `/usr/bin/id`, `/usr/bin/docker`, `/usr/bin/python3` by explicit absolute paths instead of inherited PATH. The subprocess environment is reduced to local Docker socket-related defaults, with no credentials/config loaded from the caller's environment; missing binaries/permissions STOP rather than prompting or falling back to root.

## Offline tests and observed limits

Exact-source credential-free local checks:

```bash
bash -n scripts/development/operator/ccpc_material_issue_redis_dev_topology_stage_a_v2_reviewonly_20261016.sh
PYTHONDONTWRITEBYTECODE=1 python -W error -m unittest discover -s tests/offline -p 'test_material_issue_redis_dev_topology_stage_a_v2_reviewonly_20261016.py' -q
```

**Ran 39 tests in 10.089s — OK, 39/39 PASS** after fixing a test-harness stub error. Coverage: consumed approval token refusal, shell parsing, no per-ID inspection, exact Docker argument allowlist, duplicate/missing/stopped/foreign labels, malicious strings, changed snapshots, fixed output, byte thresholds **0/4095/4096/4097**, large stdout flood termination, silent child deadline, nonzero exit, invalid UTF-8, stderr suppression and absolute executable paths. Tests exercised Python child subprocesses and mocked Docker results **only**; no Docker daemon, Ubuntu host, Redis, DEVELOPMENT container, or PRODUCTION API was contacted. GitHub blob verification established byte identity between the final test files and the local passing workspace.

### What remains unresolved

**Identity boundary is narrowed, not proved.** A Docker filtered container listing still operates on the **shared daemon** and can return a foreign/mislabelled container under expected labels/name. Compose labels/names are not cryptographic provenance, so it remains impossible to claim strict genuine-DEV-only metadata exposure or PRODUCTION physical separation. There is now **no individually targeted `docker inspect`**, but a single filtered listing is not an assurance that daemon operations are physically isolated. Therefore v2 always prints `DEV_OBJECT_PROVENANCE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED`, `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, and `POSTING_NO_GO`.

**Docker CLI / runtime unverified:** Go template placeholders are supported by Docker documentation, but no actual host CLI or active DEV Compose/name/network snapshot was read. Assumed `frappe_docker_devcontainer_default`, exact Redis names and only one network attachment per role may be too restrictive; expected behavior is conservative STOP, not silent fallback. `/usr/bin/docker` might not exist on the actual host (STOP). No Redis instance/alias/subscription/worker route verified; publishing `events` or `clear_persistent_cache` is forbidden. Snapshot comparison is not atomic.

**Disposition: KEEP V2 REVIEW-ONLY. NOT STAGED; NOT EXECUTED.** The bounded reader issue is addressed in the new source and tests, but the absolute no-PRODUCTION-inspection claim remains unprovable from the DEV-labelled Docker API. Consider a separate **GitHub-only final usefulness/security review of v2** before any staging request. Even later DEV metadata success would not authorize Material Issue write-then-rollback or permanent Stock Entry/SLE/GL. PRODUCTION untouched.
