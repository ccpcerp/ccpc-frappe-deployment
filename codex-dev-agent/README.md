# CCPC Codex DEV-only synthetic lab (NOT production)

**Status:** source implemented for review; no container has been started by ChatGPT. This is not connected to the existing Codex Cloud session. The online profile and any live DEVELOPMENT access remain **held** pending a real host-level network/security review.

This new Compose project is intentionally separate from `frappe_docker_devcontainer` and the old `frappe_docker` stack. The actual production site is now on a dedicated host according to the project owner; that does **not** make old host data or secrets disposable.

## What is included

- `compose.yaml`: own `ccpc_codex_dev_agent` Compose project with a non-root, read-only-rootfs `frappe/bench` agent, synthetic MariaDB and Redis, separate named volumes and **internal-only lab network**.
- `proxy/squid.conf`: optional HTTPS-CONNECT-only allowlist proxy, **disabled by default** via Compose profile `online`. Private/RFC1918 and loopback destination addresses are denied in policy. The proxy is not a substitute for host-enforced network isolation; gateway/forwarding exceptions and DNS behavior require live tests.
- `init_local_secrets.py`: creates two randomly generated, strictly owner-only passwords for the **new synthetic MariaDB**, without overwriting old values or displaying them. `local-secrets/` is ignored by Git.
- `check_compose.py`: read-only static validation of actual `docker compose config --format json`, guarding project identity, service/network separation, mounts, secrets, privileges and offline default.
- `../scripts/security/check_codex_dev_agent_container.sh`: host-side **read-only** Docker inspector for the newly created `agent`, allowing only exact expected private volumes and the synthetic user password secret. It does **not** establish internet or production network safety.
- `tests/test_safety_policy.py`: 13 Docker-free negative and secret-lifecycle tests for unsafe Compose modifications and secret creation/reuse. They do not prove that Docker containers boot or that the real host is isolated.

## Isolation boundaries

The agent **never mounts** the legacy shared `/workspace`, host `.ssh`, host Docker socket, existing Frappe sites, `.env`, PRODUCTION data, NAS, or backup paths. The only allowed credential is a disposable synthetic database *user* password; the synthetic DB root password is held only by the DB container. The agent owns a separate `agent-home` named volume. Create its worktree under `/home/frappe` after it starts, preserving the existing detached PR33 checkout and untracked `AGENTS.md`.

`lab.internal: true` keeps the normal agent profile off external Docker routing. **This is not a certified proof of isolation from the Docker host or its legacy services.** Only an operator-verified network/firewall rule set and negative connectivity tests can unlock online agent operation. The optional proxy's external network must not be enabled until that review; no blanket LAN egress, host networking, privileged mode, or production bridge membership is permitted.

## Validate source safely (NO running containers)

From a trusted checkout of the deployment repository on a workstation with Python 3 and Docker Compose v2:

```bash
bash codex-dev-agent/preflight.sh
```

The helper runs the Python regression tests, local synthetic password initialization, and rendered Compose policy gate in sequence. Only its synthetic-password initializer creates two **new local secret files**. It neither opens real site configuration nor connects to any database. The tests may create temporary local files; no Docker services are started. The Compose source check is read-only. Any STOP output means **do not launch the project**.

Host read-only verification on 2026-11-18 found amd64 Frappe Bench (user frappe), MariaDB 11.8 and Redis 7 Alpine, with ~684 GiB available disk. MariaDB's official entrypoint starts as root to adjust ownership of its **new synthetic** database volume, then drops to mysql; the database service uses cap-drop ALL and a five-capability initialization allowlist (CHOWN, SETUID, SETGID, DAC_OVERRIDE, FOWNER). Both Redis services explicitly run as non-root user redis. All images use `pull_policy: never` in this offline lab. Actual startup/permissions remain unverified. Before broader deployment, pin the real image digests and validate the specific runtime user; current source uses the repository-standard `frappe/bench:latest`, `mariadb:11.8`, `redis:7-alpine`, and `ubuntu/squid:latest` as provisional images. Do not treat these moving tags as reproducible production-grade dependencies.

## One-time lab creation (NOT YET AUTHORIZED FOR EXECUTION FROM THIS DOCUMENT)

Only after successful source review, host/legacy service protection review, and explicit operator approval of the exact launch:

```bash
cd codex-dev-agent
docker compose --project-name ccpc_codex_dev_agent up -d --pull never agent db redis-cache redis-queue
docker compose --project-name ccpc_codex_dev_agent ps
../scripts/security/check_codex_dev_agent_container.sh "$(docker compose --project-name ccpc_codex_dev_agent ps -q agent)"
```

This must create **only** the new project. Do not run `docker compose down -v`, `docker system prune`, generic restarts, or commands in `development.localhost` / `ccpcerp-prod` as part of this setup. If a project name or volume already exists unexpectedly, **STOP rather than overwriting it**.

After launch, validate UID ownership of `/home/frappe` as non-root and test the private MariaDB/Redis startup. No Frappe site exists automatically; an independent synthetic site must be bootstrapped and tested. The new environment must not share main DEVELOPMENT credentials or site database.

## Firewall hold after live host SSH gateway reachability — November 18, 2026

**Confirmed live security failure:** Before host firewall controls were installed, the new agent's TCP connect to the `ccpcerpserver` Docker bridge gateway SSH port 22 succeeded even though `lab.internal: true` blocked the test to public `1.1.1.1:443`. Owner then stopped `ccpc_codex_dev_agent-agent-1` and verified `Agent running: false`. The four containers had previously booted, MariaDB SQL `SELECT 1` succeeded and Redis `PONG` returned from both synthetic services. This is NOT a breach report, but a demonstrated inadequate network boundary. **Do not restart the agent, enable online profile or execute Codex CLI until independently proven blocked.**

Read-only firewall inspection on old host: `iptables v1.8.11 (nf_tables)`, `INPUT -P ACCEPT` with no listed policy rules, `DOCKER-USER` exists but empty, `FORWARD -P DROP` with a `DOCKER-USER` jump before `DOCKER-FORWARD`; exact lab interface `br-a88796be8a7a`, subnet `172.21.0.0/16`, gateway `172.21.0.1`. **These values are host-specific; guard and stop if they change.**

A new operator-reviewed script, `../scripts/security/ccpc_codex_dev_lab_firewall.sh`, provides `plan` (read-only), `apply` (three narrowly scoped IPv4 DROP rules), `verify` (read-only) and `rollback` (delete only the exact tagged rules). It never flushes chains, touches other Docker projects or modifies SSH service configurations. Scope: `INPUT` denies traffic originating from this lab to its Docker host; `DOCKER-USER` blocks forwarding out of the lab and into it from other interfaces. Same-bridge traffic to synthetic DB/Redis remains allowed.

**Operator gating and required caution:** The script was authored in GitHub but is **NOT automatically applied**, and firewall safety is not independently tested on the host. Before `apply`, run `bash -n` and the `plan` mode, confirm it targets exactly the expected bridge/subnet and that the agent is still stopped. Applying host firewall rules requires the owner's explicit operational choice and normal sudo authentication. Keep a second SSH session open and the exact `rollback` command available; if any existing service is affected, keep agent stopped and rollback. These iptables rules are **temporary**; they can disappear after host reboot/firewall refresh. Do not enable agent auto-start until a persistent startup-before-agent policy and reboot validation exist.

**Only after firewall apply and verification:** Run negative reachability tests for host gateway and a **non-production canary**; avoid touching real `ccpcerp-prod`, legacy production credentials, or business databases. Host firewall rules do **not** secure a future `online` proxy on a second outgoing bridge; that requires separate strict egress controls before optional proxy activation.

## Enabling internet and interactive Codex CLI — separate held gate

Before `--profile online`, prove at the **host/network-policy level** that the agent and its proxy cannot reach the dedicated production host, old legacy production services, the Docker host's privileged endpoints, NAS, or unrelated LAN networks. Review the Squid allowlist against current Codex authentication/package endpoints, DNS rebinding, and the host's Docker forwarding/firewall configuration. Do not test against the *real* PRODUCTION service without a scoped authorization; use a dedicated non-production canary. If any policy check cannot be proved, keep offline and continue productive development in the already working **Codex Cloud** environment.

Once separately authorized and validated, install/sign in to Codex CLI **inside the new isolated agent** using your existing ChatGPT account, ideally `codex login --device-auth` for a headless container. Do not supply an extra API key or copy existing host `~/.codex` tokens. The agent container should not be connected to persistent MAIN DEVELOPMENT by default.

## Persistent DEVELOPMENT access — a distinct scope

This standalone lab is **not** an unrestricted bridge into the actual `development.localhost` database. The later DEV-only executor needs a reviewed merge/reconciliation of divergent PR33 and Phase 1 branches, fresh four-artifact backup, target-site-only migration scope, logging and rollback. Preserve all historical CCPC/Ricor records; actual Finance Expense/Center mapping approval must use distinct genuine named employees. Production changes and legacy production cleanup remain separately controlled.

## Stop/recovery

To stop **only the new project** while preserving its private volumes:

```bash
cd codex-dev-agent
docker compose --project-name ccpc_codex_dev_agent stop
```

Do not remove named volumes or local secrets during initial troubleshooting. The existing DEVELOPMENT and legacy production Compose projects should be unaffected by a correctly scoped new Compose invocation; verify actual Docker identities before and after launch. A failed security check means keep agent access disabled and continue Codex Cloud.

**Traceability:** [GitHub Issue #38](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/38) and [current DEV-only plan](../docs/ccpc-project/CODEX-DEV-ONLY-AGENT-RUNTIME-PLAN-2026-11-18.md).
