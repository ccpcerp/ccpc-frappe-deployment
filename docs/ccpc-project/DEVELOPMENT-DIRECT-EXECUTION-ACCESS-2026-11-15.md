# CCPC ERPNext — controlled DEVELOPMENT execution access

## 2026-11-17 — offline Codex worker Stage A PASS (owner-reported)

The operator ran the exact guarded setup from this PR's reviewed source and reported:

```text
ISOLATED_PROBE_CONFIG=PASS
WARNING: proceeding, even though we could not create PATH aliases: Read-only file system (os error 30)
ISOLATED_CODEX_CLI_VERSION=0.161.0
OFFLINE_WORKER_STAGE=PASS
PROBE_STOPPED=YES
NETWORK=NONE
NO_MODEL_AUTH_OR_AGENT_RUN=PASS
CURRENT_DEV_AND_PRODUCTION_UNCHANGED_BY_THIS_SETUP=YES
```

**Evidence classification:** owner-reported *successful host execution* of the Stage A one-use script, not direct ChatGPT Docker access or an independent adversarial isolation test. The script guards check nonroot identity, no volumes, no network, capability drop, read-only root, no-new-privileges, version and stopped probe. The CLI's PATH-alias warning is consistent with a read-only filesystem; it did **not** prevent the exact CLI version smoke PASS. Do not loosen read-only flags, copy existing SSH/Codex credentials or rerun/recreate the one-use setup just to eliminate this nonfatal warning.

**New local artifacts:** a clean `ccpc-codex-isolated:0.161.0-offline` image and a stopped `ccpc-codex-isolated-offline-probe-20261116` are reported as successfully created; neither serves a model session. Existing DEV/OLD PRODUCTION resources and credentials were not modified by the reviewed operator script. The build's public base/npm package retrieval was an explicit approved part of Stage A. No PRODUCTION change, database write, scheduler restart, CI provider invocation, GitHub runner, external API billing or automatic Codex report flow was authorized or performed.

**Stage B, not yet operational or approved to change infrastructure:** An actual Codex agent requires a writable *ephemeral* authenticated home and selectively allowed outbound model/auth connectivity. `--network none` precludes both remote model traffic and ordinary OAuth connectivity. A default Docker bridge, host network or generic unrestricted HTTP proxy would **not** safely constrain a shared host with OLD and NEW PROD networks. Design and separately review a fail-closed egress control that blocks RFC1918/link-local/host/Docker gateway/production routes and permits only verified Codex service/auth endpoints, with no DNS bypass and no unrestricted CONNECT. Avoid credentials copied from old `/home/frappe/.ssh`, host `~/.codex`, or service accounts; prefer a fresh owner-initiated interactive login inside a dedicated isolated boundary, with tokens protected from application source and operator logs. No runtime secrets stored in GitHub. Only a sanitized approved GitHub source snapshot and aggregate-only DEV diagnostic results may be presented; no production Docker, live DB, NAS, SSH or host filesystem mounts. Do not enable self-hosted auto-runners or publish reports automatically.

**Shortest safe interim DEVELOPMENT deliverable:** run the already-reviewed [consolidated two-site read-only diagnostic](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/pr33-dev-acceptance-2026-11-16/scripts/development/operator/ccpc_pr33_consolidated_readonly_dev_inventory_20261116.sh) once, retain only summary flags/counts, and combine that with the completed Codex Cloud source report. This advances real acceptance while Stage B network/auth security is designed. The offline probe can remain stopped; no repeat setup necessary.

## 2026-11-16 — owner-approved Codex worker setup, Stage A prepared in GitHub

Owner explicitly approved setting up a **new isolated DEVELOPMENT-only Codex worker** after confirming `codex-cli 0.161.0` in existing `frappe_docker_devcontainer-frappe-1` and observing that normal host `gani` has `sudo`, `docker`, `lxd` groups. This authorization is limited to the *new worker*, not to running agents in the existing SSH-exposed container or giving root/host access to Codex.

**New guarded artifacts on this review branch:**
- [`scripts/development/codex-isolated/Dockerfile`](../../scripts/development/codex-isolated/Dockerfile) — clean `node:24-bookworm-slim` image, exact `@openai/codex@0.161.0`, fixed nonroot UID; no credential or CCPC file copies.
- [`scripts/development/codex-isolated/ccpc_codex_stage_offline_worker_20261116.sh`](../../scripts/development/codex-isolated/ccpc_codex_stage_offline_worker_20261116.sh) — exact host/OLD project/DEV guard, new image build + network-none immutable/no-mount/no-capabilities new Docker probe; CLI version only, left stopped.
- [`tests/test_ccpc_codex_isolated_offline_worker_static.py`](../../tests/test_ccpc_codex_isolated_offline_worker_static.py) — Bash syntax + source boundary checks.
- [`scripts/development/codex-isolated/README.md`](../../scripts/development/codex-isolated/README.md) — scope/limitations and staged execution.

**Status at GitHub commit creation:** files committed and refetch/owner delivery checks pending; **NO host execution, image pull/build, image/container creation, Codex authentication, model task, network/firewall changes, DEV/PROD write or CI run has occurred in ChatGPT.** This is an offline worker stage; `--network none` makes it impossible to contact OpenAI model endpoints. A separate reviewed outbound-only egress/auth route and sanitized source/report workspace are necessary before it becomes an interactive agent. Existing creds from `frappe` or `gani` cannot be copied. Stage A may download public Node/npm packages at build time, without token/API expenses; keep resource/supply-chain limits explicit.

**Next operator milestone:** fetch this exact GitHub review branch with pinned commit/blob verification, run `bash -n` + static tests, then run only the approved Stage-A script as `gani`; report `OFFLINE_WORKER_STAGE=PASS` or STOP. No retries/cleanup on error. The owner retains control of host execution. The review branch is not merged.



**Date:** 2026-11-15 (Asia/Manila). **Status:** GitHub-only review implementation. **User authorization:** broaden DEV investigation/test access and set up an auditable, restricted DEV connection; **not** permission to access NEW PRODUCTION, restart any shared host, remove credentials, run unattended Codex, change DNS/firewall, or publish/rotate secrets. No host access has been configured or tested in this milestone.

## Exact-source offline test evidence

On 2026-11-15 the source and test files were reconstructed into a disposable local Python tree and **Git blob IDs verified** against GitHub before interpreting the tests: script `6aed1b7e6989c0896296127fb38d1ac26d00160b`; test `74aef289fabe38ac378f266f7ab73669a58febef`. The exact unit-test command was:

```bash
python3 -B -m unittest discover -s tests -p 'test_ccpc_dev_execution_boundary_readonly.py' -v
```

**11/11 mocked Python tests PASS**; scenario coverage includes OLD PROD running, readable SSH mounts, Docker socket mount, privileged container, stopped DEV, wrong Docker Compose identity, bad Docker access, host and context rejection, sanitized output, and no source mutation verbs. **This was not a legacy-host Docker inspection, remote connection, CI runner execution or approval to install the worker.** The review-only script has not been copied to or executed on `ccpcerpserver`.

## Current state and known hazards

- Dedicated NEW host: `ccpcerp-prod`. This project does **not** authorize changes to it.
- Legacy host: `ccpcerpserver`, operator `gani`. Owner reports OLD PRODUCTION site has now been **cut off**. This is owner-reported operational status, **not yet verified** to imply stopped containers, disabled writers/schedulers/webhooks, removed host mounts, or purged data.
- Historical GitHub architecture: legacy host ran both `frappe_docker` (OLD PROD) and `frappe_docker_devcontainer` (DEV). The running DEV container `frappe_docker_devcontainer-frappe-1` had a bind mount at `/home/frappe/.ssh`, with readable files as the `frappe` user. That is **unsafe for unrestricted agent execution**. The earlier automatic Codex publisher was cancelled; its reporting token was revoked. Do **not** reuse this publisher or expose the SSH files.
- Existing app CI in `ccpcerp/ccpcerp` uses opt-in disposable CircleCI ERPNext/MariaDB tests. Preserve manual opt-in controls and cost checks; don't enable automatic paid/broad jobs or CI triggers merely because direct access is approved.
- This review branch is separate from open NEW G1 production readiness PR #35. Production G1 activation locks remain unchanged.

## Effective scope after verified isolation

**Allowed within named DEV-only disposable target:** source/log/health inspection, non-sensitive metadata, Python compile/tests, Frappe/MariaDB integration on an explicitly designated synthetic test site, repeatable test fixture setup/cleanup, and reviewed code deployment with worktree/commit/backup checks. Mutating procedures must be auditable and limited to DEV-target paths, identities and databases. GitHub remains authoritative for committed code; no overwriting uncommitted changes.

**Still individually controlled:** operations that touch non-synthetic persistent DEVELOPMENT data, migration, high-risk cleanup, service restarts affecting other containers, configuration of firewall/Docker daemon/host networking, credential changes, new CI paid runs, and integration with external production systems. User has not authorized a blanket shell root account. No NEW PROD access, OLD preserved data deletion, Docker socket mount to the agent, host-wide sudo, SSH material in agent workspaces, production DB credentials, NAS credentials, autonomous Codex publishing, or extra paid API access.

## Owner-reported legacy-host Docker status — 2026-11-15

The owner executed a **read-only** `docker ps -a` Compose-label inventory on the original legacy host and shared the sanitized states:

- OLD PRODUCTION project `frappe_docker`: `frontend`, `backend`, `websocket`, `queue-short`, `queue-long`, `scheduler`, `configurator` are **exited** (7). `db`, `redis-cache`, and `redis-queue` remain **running** (3).
- DEVELOPMENT project `frappe_docker_devcontainer`: `frappe`, `mariadb`, `redis-cache`, and `redis-queue` are **running** (4).
- This **supports the owner's claim that the normal OLD web/backend/worker/scheduler application services were shut down**, but does **not** certify no other OLD external writer or retained production credentials. It also does not justify destroying the OLD MariaDB/Redis containers. No mutations were performed by this inspection.
- The **first** boundary-script revision required `OLD_PRODUCTION_COMPOSE_ACTIVE=0` and would have stopped solely because the retained data services were running. This was an overrestrictive design, **corrected in the review branch** under the access-blocker priority update below. Do not stop the OLD DB/Redis containers or weaken the check for OLD app workers.
- Next one safe operator observation is a bounded **DEV container privilege/SSH/Docker-socket mount presence check only**, without printing mount source paths or secrets. Even if this narrow check is negative, it does not replace a complete credential isolation and external writer audit.

## Access-blocker priority and revised cutoff-aware audit

**Priority change — requested by owner:** Enable broader *controlled* DEVELOPMENT tests as the immediate engineering priority, without changing NEW PRODUCTION or destroying OLD retained recovery data.

The first draft auditor accidentally treated all three retained OLD MariaDB/Redis containers as an application-writer failure. This conflated **running data services** with **running OLD app/worker/scheduler services**. On the same PR #36 review branch, commit `c24618a4c2364c201c52d319ae6a37dbe2bbb583` revises the auditor to pin the ten expected OLD Compose identities and separately report `OLD_PRODUCTION_APP_ACTIVE` versus `OLD_PRODUCTION_RETAINED_DATA_ACTIVE`. The guard now stops on **any** active OLD app/worker/scheduler, missing/unexpected service, or old identity drift; the three preserved OLD data containers need not be stopped. Commit `85372ff34efd417f1694e23e282407adcc872edd` updated mocked tests to cover this distinction and unexpected OLD service drift. **The revised full test suite has not been executed in this milestone**; these are source changes, not a host clearance. The earlier 11/11 result was on the preceding source and tests, not the revised versions.

**Two independent remaining prerequisites:**

1. The old DEV container historically exposed `/home/frappe/.ssh`. Do not install/run an agent in it even if OLD application processes are exited. Use a **new** isolated worker with no SSH, NAS, production DB/config or Docker-socket mounts; no privileged mode, host network or host-wide sudo. Verify egress/network rules and that only synthetic test DB endpoints are reachable.
2. This ChatGPT session has **connected GitHub tools but no direct SSH/remote-terminal connector to the original server**. A host-side installation alone does not confer terminal access in chat. We must explicitly choose a supported GitHub-driven test bridge or establish a real supported remote-execution connector; avoid claiming direct interaction until a real end-to-end command and result are verified.

**Fastest meaningful interim result:** use the existing GitHub code connector and separately authorized opt-in hosted disposable Frappe/MariaDB CI to perform actual integration tests while preparing the on-premises isolated worker. An on-premises self-hosted Actions runner is **not** automatically safe merely because it has a GitHub label; do not install one with host Docker socket or untrusted PR triggers.

## Staged access implementation

1. **GitHub baseline — DONE:** Added `scripts/development/operator/ccpc_dev_execution_boundary_readonly.py` and `tests/test_ccpc_dev_execution_boundary_readonly.py` on the `review/development-execution-access-2026-11-15` branch. The audit is read-only: exact operator/legacy host, old Compose project active count, pinned DEV container active/project, privileged flag, presence of credential mounts/Docker socket. It emits only YES/NO/count and PASS/STOP, not raw Docker inspect, mount paths, secrets or site data.
2. **Owner-run read-only host evidence — PENDING:** Verify legacy host still matches exact known identities and whether OLD PRODUCTION Compose containers are active. The owner's network/site cutoff alone does not establish no background jobs or writes. If the preflight reports STOP, investigate/reconcile; **do not automatically stop/remove containers or change the existing DEV container's SSH mount**.
3. **Separate isolated worker — PENDING:** On the legacy host **after** boundary and backup review, provision a dedicated non-root, non-sudo test-execution identity in a fresh isolated DEV worker (or use existing hosted disposable CI). Require no host Docker socket, no SSH/credential/NAS/prod mounts, no host network, no automatic secrets injection, no access to unrelated host processes/data, appropriate resource and outbound-network limits. DO NOT run an agent in the existing SSH-exposed DEV container. Source and exact versions must be pinned and reviewed before any installation.
4. **Transport and execution — PENDING:** Add an authenticated, auditable, narrow command interface supporting only named diagnostics/tests on **allowlisted DEV synthetic sites and paths**. No arbitrary inbound shell, public unauthenticated endpoint, blanket root Docker privileges, untrusted PR automatic self-hosted workflow, or unreviewed scripts. Prefer a reviewed outbound-only link or existing hosted CI; select the actual connection mechanism only after host evidence and available provider tools are verified. Avoid installing an unbounded self-hosted GitHub Actions runner on a secret-bearing shared host.
5. **Acceptance — PENDING:** Prove source SHA, fixed target, no production/OLD/backup reachability, worktree protection, redacted audit logs, failure STOP, and disposable Frappe/MariaDB stock/GL/billing/permissions/rollback test run. Only then label DEV automatic execution operational. NEW PROD release and cutover remain separate.

## Safety gate semantics

The preflight's PASS means only: the specific Docker metadata assertions at that instant matched. It **does not** prove OLD site inaccessible, no external writers, no orphaned credentials anywhere, firewall isolation, private DB separation, or an approved automated agent. A STOP is actionable evidence, not permission to change host settings.

### One safe next operator observation

At `gani@ccpcerpserver`, run a **read-only** Docker status check, not a setup script:

```bash
test "$(hostname -s)" = "ccpcerpserver" &&
sudo docker ps -a --format '{{.Names}} {{.State}}' |
grep -E '^frappe_docker(-|_devcontainer-)' || true
```

Share only the container names and running/exited states. Do **not** print Docker inspect environmental values, keys, passwords or database records. After names and states are verified, a separately reviewed source-hash-pinned preflight can be run. No production action is part of this command.

## Verified milestones vs pending

**Implemented in GitHub:** review-only source and mock tests for the boundary inspection, plus this access-design record. **Not done:** actual test execution/host preflight, agent/transport installation, DEV operational access, CI activation, source pull, Docker/systemd changes or business DB tests. Don't imply a fully working remote link until a legitimate connection has been created and tested in a subsequent explicitly authorized operator step.
