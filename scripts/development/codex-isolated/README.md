# CCPC ERPNext — separate Codex worker (first stage)

**Date:** 2026-11-16 Asia/Manila. **Status: reviewed operator setup prepared, not executed on `ccpcerpserver`.**

## Why this is a new container

The existing `frappe_docker_devcontainer-frappe-1` has Codex CLI `0.161.0` available, but also has a bind-mounted SSH directory. The host operator `gani` is in the `sudo`, `docker`, and `lxd` groups. Neither is a safe unrestricted agent identity. Old PROD data containers remain on the same legacy server even though normal OLD app services were previously reported stopped.

The new worker uses a **clean Dockerfile built from `node:24-bookworm-slim`**, installing only exact `@openai/codex@0.161.0`; it does **not** use `docker commit`, `docker cp`, `volumes-from`, the existing DEV image, or a copy of that container's authenticated Codex home directory.

## Stage A — prepare/verify the offline worker image (owner approved; operator run pending)

Review `Dockerfile`, `ccpc_codex_stage_offline_worker_20261116.sh`, and `../../../tests/test_ccpc_codex_isolated_offline_worker_static.py` from this exact PR #36 review branch, then pin Git commit and both Git blobs when delivering. Execute as **normal `gani`** on the exact `ccpcerpserver` host; the setup script invokes `sudo docker --host unix:///var/run/docker.sock` only for the narrowly guarded new image/probe.

The script enforces:

- Exact legacy host, operator, local Docker daemon, unchanged named DEV container.
- Ten known OLD PROD Compose members, **zero running/paused/restarting OLD app workers**, but retained old MariaDB/Redis data containers are not a blocker and are **not touched**.
- No pre-existing worker image/probe-name collision.
- Clean image build from public Node base and pinned Codex npm package. **This build fetches container/npm packages over the normal Docker build network** and creates new Docker image layers/cache. It does not start a model session, use paid OpenAI API, receive tokens or alter the Frappe app checkout.
- Exactly one new container created with `--network none`, `--read-only`, fixed nonroot UID/GID, all capabilities dropped, `no-new-privileges`, 64-PID / 768-MB / 1-CPU bounds, restart disabled, **no mounts**.
- Inspect the new probe's security metadata *before* starting it; then run **only `codex --version`**, verify version `0.161.0`, zero exit, and stopped state. Keep the stopped container for later verified review; do not remove/reuse automatically.

**Success marker**: `OFFLINE_WORKER_STAGE=PASS` and `PROBE_STOPPED=YES`, with `NETWORK=NONE`.

**Stop** and share sanitized error labels on unexpected Docker identity, missing OLD services, active OLD workers, image-build failure, unexpected mount/security config or CLI smoke failure. Never retry automatically or run `docker system prune`/global cleanup. Old live credentials/production DBs are not prerequisites or valid inputs.

### Important capability limit

This stage **does not produce a working Codex inference session**. A container with Docker `--network none` cannot contact Codex's model/auth endpoints. It is a hard isolation smoke and a base for a future bounded worker, not a pretense that agentic host analysis is available.

The package/base names are versioned but the public upstream `node:24-bookworm-slim` tag and npm dependency graph are not fully image-digest/lockfile pinned; verify the built image's identity before broadening use. Do not assume clean-image provenance implies sufficient network isolation.

## Stage B — still pending after Stage A evidence

A separately reviewed outbound-only path must allow model authentication/communication **without permitting reachability to PROD hosts, private LAN, OLD/NEW production services, Docker daemon, host metadata or unrelated endpoints**. Do not add host-wide firewall/Docker daemon/network changes under Stage A approval. Prefer allowlisted egress proxy plus enforced network policy, with no `--network host` or unrestricted default bridge. The authenticated state must be created directly under a dedicated worker identity; **never copy** host `~/.codex`, `~/.ssh`, `/home/frappe/.ssh`, ChatGPT web cookies, GitHub tokens or DEV/PROD `site_config.json`.

When networking is securely solved, stage *sanitized code* from reviewed GitHub and count/boolean-only DEV reports into a read-only workspace. Give Codex read-only source and diagnostics, not a DB password, local Docker or an arbitrary host shell. Any live DEV queries must be operator-run through a reviewed allowlisted read-only diagnostic. Require owner approval separately for new persistent site transactions, CI/provider spending, real user-role grants, deployments, migrations, and PRODUCTION actions.

**Practical interim:** the isolated Codex Cloud report and `scripts/development/operator/ccpc_pr33_consolidated_readonly_dev_inventory_20261116.sh` on docs PR #37 already offer broad code coverage plus one read-only two-site host diagnostic, without an on-prem agent.
