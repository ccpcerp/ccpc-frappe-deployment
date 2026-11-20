# CCPC Codex DEV-only synthetic lab (NOT production)

**Status:** review-only security hardening proposal. The operator has previously run synthetic lab services, but the Codex agent is stopped and optional Squid has not been activated. No container has been started by ChatGPT. This is not connected to an existing Codex Cloud session. The online profile, Codex CLI and any live DEVELOPMENT access remain **held** pending separate host-level isolation review and explicit operational approval.

This new Compose project is intentionally separate from `frappe_docker_devcontainer` and the old `frappe_docker` stack. The actual production site is now on a dedicated host according to the project owner; that does **not** make old host data or secrets disposable.

## What is included

- `compose.yaml`: own `ccpc_codex_dev_agent` Compose project with a non-root, read-only-rootfs `frappe/bench` agent, synthetic MariaDB and Redis, separate named volumes, an existing internal application bridge, and a proposed second **internal proxy-client-only bridge**.
- `proxy/squid.conf`: optional HTTPS-CONNECT-only allowlist proxy, **disabled by default** via Compose profile `online`. Its listener binds to the proposed internal client bridge IP and accepts only the agent's fixed source IP; private, special-use and loopback destinations are denied by the provisional Squid policy. The proxy is not a substitute for host-enforced network isolation; gateway/forwarding exceptions and DNS behavior require live tests.
- `init_local_secrets.py`: creates two randomly generated, strictly owner-only passwords for the **new synthetic MariaDB**, without overwriting old values or displaying them. `local-secrets/` is ignored by Git.
- `check_compose.py`: read-only static validation of actual `docker compose config --format json`, guarding project identity, service/network separation, mounts, secrets, privileges and offline default.
- `../scripts/security/check_codex_dev_agent_container.sh`: host-side **read-only** Docker inspector for the newly created `agent`, allowing only exact expected private volumes and the synthetic user password secret. It does **not** establish internet or production network safety.
- `tests/test_safety_policy.py` (66 declared tests) and `tests/test_lab_firewall_guard.py` (15 tests): 81 Docker-free policy regression and secret-lifecycle tests for unsafe Compose networks, listener/ACL changes, restart/routing bypasses, and secret creation/reuse. They do not prove that Docker containers boot or that the real host is isolated.

## Resource governance proposal — review source only (2026-11-20)

The draft review branch now proposes **memory, memory+swap and PID ceilings** for every lab service. These are candidate **maximums**, not a reservation, operator-approved sizing or proof of safe capacity on the current shared host:

| Service | Memory ceiling | Memory+swap ceiling | PID ceiling |
| --- | ---: | ---: | ---: |
| Stopped Codex agent | 8 GiB | 8 GiB | 512 |
| Synthetic MariaDB | 2 GiB | 2 GiB | 256 |
| Redis cache | 384 MiB | 384 MiB | 128 |
| Redis queue | 384 MiB | 384 MiB | 128 |
| Optional offline-by-default Squid proxy | 512 MiB | 512 MiB | 128 |

The maximum combined memory budget is **11.25 GiB** if all five services run at their limits. CPU is **not explicitly capped**, consistent with the owner's performance preference; the tradeoff is that CPU contention remains possible. The Compose safety validator now refuses missing/modified memory, swap or PID ceilings. Six additional source-only regression tests are **declared but not yet executed**; historical 75/75 offline pass evidence applies only to the prior test set. Actual Docker Compose schema rendering, Docker host compatibility, resource enforcement and workload sizing remain **unverified**. The lab must not be started or reconfigured based on these review-only edits. All earlier firewall, network, Squid egress, image provenance, credential and sandbox **NO-GO** gates remain.

## Isolation boundaries

The agent **never mounts** the legacy shared `/workspace`, host `.ssh`, host Docker socket, existing Frappe sites, `.env`, PRODUCTION data, NAS, or backup paths. The only allowed credential is a disposable synthetic database *user* password; the synthetic DB root password is held only by the DB container. The agent owns a separate `agent-home` named volume. Create its worktree under `/home/frappe` after it starts, preserving the existing detached PR33 checkout and untracked `AGENTS.md`.

`lab.internal: true` keeps the normal agent profile off external Docker routing. **This is not a certified proof of isolation from the Docker host or its legacy services.** Only an operator-verified network/firewall rule set and negative connectivity tests can unlock online agent operation. The optional proxy's external network must not be enabled until that review; no blanket LAN egress, host networking, privileged mode, or production bridge membership is permitted.

## Proposed three-network proxy design (REVIEW ONLY — NOT DEPLOYED)

The separate review branch proposes the following future topology; the active host still has its original two-network Compose declaration until an independently approved deployment:

1. `lab` (existing internal bridge): agent, synthetic MariaDB, Redis cache and Redis queue. **Squid does not join this bridge**; database and Redis service discovery should stay on `lab`.
2. `proxy_clients` (new internal, non-attachable, IPv6-disabled bridge): **only agent and Squid**, with reserved static /29 addresses for the agent and Squid. Squid binds its `http_port` to the internal client-facing address only, not to every container interface. An explicit Squid source ACL permits the agent's fixed address; HTTPS CONNECT, port 443, the restricted destination-IP list and provisional allowed-domain list remain enforced in order. This is **not user identity authentication**.
3. `outgoing` (separate bridge): Squid only, for outbound traffic following host firewall policy. The agent does **not** join this network; Squid must not accept inbound proxy clients through its outgoing-facing address.

The `172.30.250.0/29` block in this **review-only source** is a provisional IPAM reservation, not an assertion it is safe for this host. Step 82 confirmed no overlaps among seven current Docker networks, host IPv4 routes and interface networks; external/remote route overlap remains unverified. The **proposed Linux bridge device name `br-ccpc-cdxpx`** was absent from current host interfaces, Docker network settings and iptables filter/NAT references at Step 86. Neither the address nor the interface name has been reserved. **Before any Docker Compose apply**, recheck real Docker bridge allocations, host routes, external/LAN routes, address availability and subnet collision. Readdress and update `compose.yaml`, `proxy/squid.conf`, `check_compose.py` and tests together if necessary; do not modify or recreate the existing `lab` network to make this reservation fit.

### Pre-enforcement firewall design — no changes authorized

The review branch adds `../scripts/security/ccpc_codex_proxy_bridge_preflight.py`, a **read-only** `plan`/`verify` checker. It checks host identity, stopped agent, existing original-lab firewall rules, FORWARD chain order, proposed network/bridge absence, and local route/IPAM collision. It does not apply, remove, start, or create anything and **intentionally rejects `apply` and `rollback` modes**.

For the eventual new `br-ccpc-cdxpx` device, an independently reviewed change must **pre-install** and verify three exact scoped rules **while this device and Docker network do not exist**: (a) `INPUT`: DROP all packets arriving on that bridge destined for the Docker host, regardless of source IP; (b) `DOCKER-USER`: DROP packets entering from the new bridge that are forwarded out through another interface; (c) `DOCKER-USER`: DROP packets entering from another interface that are forwarded toward the new bridge. The expected `INPUT` rule should precede any competing accept rule, and both `DOCKER-USER` rules must precede generic accepts. The read-only verifier reports whether they are installed with the expected precedence. **This source does not implement firewall application or authorize it.**

Separate operational approval and independent testing are required before writing even these scoped rules: validate current host/iptables-nft backend, inspect existing rule interactions and operator SSH recovery access, capture a recovery path, verify remote/VPN route conflicts, and document a narrow exact-match rollback that removes only the new project's tagged rules after the agent is stopped and the network is safely detached. Ensure persistence/re-establishment **before** any agent autostart after reboot; temporary iptables rules alone are insufficient.

The existing original-lab firewall script must remain unchanged. Steps 83–85 verified its three expected exact rules (with Step 83's text-token mismatch resolved by read-only `iptables -C`), but those rules **do not cover the proposed second bridge**. A new outbound bridge/egress policy for Squid is a further independent requirement. A successful plan or `iptables -C` check is not a substitute for controlled negative reachability tests using non-production targets.

### Original laboratory firewall restoration and start guard (Step 92 — SOURCE ONLY)

The draft PR also includes `../scripts/security/ccpc_codex_lab_firewall_guard.py`, an **independent, read-only** `preflight`/`verify` checker for the *original laboratory network*. Its preflight validates host/Docker identity, the intended original lab network and stopped agent, disabled agent restart policy, current UFW activity, iptables-nft backend, Docker chain availability and the first `FORWARD` jump to `DOCKER-USER`. Its `verify` mode additionally checks all **three exact original-lab DROP rules with `iptables -C`**, and checks precedence using a normalized, token-order-independent parser of `iptables -S`. It rejects `apply`, `rollback`, `start` and all other unapproved actions, and **always prints `agent_launch_authorized=False`**, including on a successful check.

The template `../scripts/security/systemd/ccpc-codex-lab-firewall-restore.service.example` is **not a loadable/installed systemd unit** and contains a deliberately absent, root-owned authorization-marker requirement. Its intended *future, separately approved* flow is: wait for Docker/UFW, run guard `preflight`, invoke the **existing** guarded original-lab firewall script's `apply` mode, then run guard `verify`. Nothing here starts Codex, Squid or containers. A failed post-check leaves any added protective DROP rules in place for safe investigation rather than weakening the host automatically. The original firewall script has not been modified.

A boot-time oneshot remains insufficient by itself: the rules have **no verified reboot persistence**, may be lost after UFW/Docker reloads, and a privileged user with Docker access could bypass an external launch gate. This PR includes **no operable Codex startup command**; runtime activation remains NO-GO until the host can fail closed at every launch, the second proxy-client bridge and Squid egress are independently protected, actual negative connectivity is demonstrated, and Python integration/runtime checks are successful. Do not copy/install the example unit, create its authorization marker, or run the original script `apply` without a distinct, explicit host-operation approval and rollback/SSH recovery plan.

The `tests/test_lab_firewall_guard.py` module now contains **15 mock-only** regressions, including combined original/new bridge firewall prefix ordering, partial installations, unexpected ACCEPT rules and alternate iptables inversion syntax. The total is **75** Python source-only tests. **All 75 executed and passed (0 failures) in a separate isolated Python workspace on 2026-11-20**, after reproducing every required source file byte-for-byte and matching the GitHub blob hashes. This was not the GitHub Actions runner, not an actual Docker/Compose or Squid parser run, and not a host firewall/negative-connectivity integration test. GitHub Actions remains blocked before job steps.

**Combined two-bridge ordering correction (Step 93):** The old original-lab checker and the proposed new proxy-bridge checker initially each demanded the first rule positions in `INPUT` and `DOCKER-USER`. This is impossible after both rule sets coexist. Both now call `../scripts/security/ccpc_firewall_rule_order.py` to enforce the **original-only** leading DROP prefixes or, upon detection/requirement of the second bridge, the **combined two INPUT / four DOCKER-USER** leading restrictive prefixes. All three new-bridge rules are required together; unknown or permitting rules ahead of those prefixes fail closed. New negative unit tests cover these cases. This fixes source-only ordering logic, not host rule persistence or live isolation.

**Important new-host-boundary risk:** even an internal Docker network can expose its bridge gateway/host services to containers. Before the new `proxy_clients` network is instantiated, extend and review the *existing host-deny and Docker isolation policy* to cover that second bridge, including rollback and reboot persistence. Verify client-to-host gateway, client-to-other-bridge, client-to-production-canary, and outgoing-bridge-to-listener **negative tests** under separately approved isolated conditions. A correctly bound Squid listener and `src` ACL do not secure Docker host routing or Squid's own outbound sockets.

**Automated test execution status:** Source-only policy/test files have been inspected and cross-checked, but GitHub Actions currently reports job failures **before any runner steps are recorded**. Do not interpret these as a pass or as Python assertion failures. The 75 Python tests independently passed in an isolated Python workspace; GitHub Actions has **not** executed them due to pre-run failure. They still require trustworthy CI execution before merge acceptance. A text-level source consistency audit alone is not equivalent to running the Python tests.

**Unresolved NO-GO gates:** source inspection does not verify Squid binary parsing, DNS-resolved destination-IP enforcement, DNS rebinding, redirect/CNAME handling, suitability of broad approved domain suffixes, or bypass via raw sockets. `ubuntu/squid:latest` is an unpinned mutable image absent locally under the configured reference at last inspection, and its effective runtime UID, provenance and filesystem permissions remain unverified. Do **not** pull images, change `pull_policy: never`, enable the online profile, authenticate Codex, or call this production-ready solely because static tests pass. Confirm resource budgets, credential isolation and actual Codex sandbox/approval policy independently.

**GitHub-first review:** keep the host's current development-acceptance review branch and its tracked/clean laboratory source unchanged. Review the new Compose/ACL/validator/tests in GitHub, record commit/test results, and later prepare a separately authorized, backup/rollback-reviewed DEVELOPMENT-only handoff. PRODUCTION is on a separate server per the operator and is not in scope.

## Validate source safely (NO running containers)

From a trusted checkout of the deployment repository on a workstation with Python 3 and Docker Compose v2:

```bash
bash codex-dev-agent/preflight.sh
```

The helper runs Python regression tests, local synthetic password initialization, and the rendered Compose **and Squid source** policy gate in sequence. Only its synthetic-password initializer creates two **new local secret files**. It neither opens real site configuration nor connects to any database. The tests may create temporary local files; no Docker services are started. The Compose and Squid source checks are read-only. To run **source-only tests without even creating the local synthetic password files**, use `python3 -m unittest discover -s codex-dev-agent/tests -p 'test_*.py' -v` from the repository root. Any STOP output means **do not launch the project**.

Host read-only verification on 2026-11-18 found amd64 Frappe Bench (user frappe), MariaDB 11.8 and Redis 7 Alpine, with ~684 GiB available disk. MariaDB's official entrypoint starts as root to adjust ownership of its **new synthetic** database volume, then drops to mysql; the database service uses cap-drop ALL and a five-capability initialization allowlist (CHOWN, SETUID, SETGID, DAC_OVERRIDE, FOWNER). Both Redis services explicitly run as non-root user redis. All images use `pull_policy: never` in this offline lab. Actual startup/permissions remain unverified. Before even considering online activation, pin the real image digests and validate the specific Squid runtime user and non-root feasibility; current source uses the repository-standard `frappe/bench:latest`, `mariadb:11.8`, `redis:7-alpine`, and `ubuntu/squid:latest` as provisional images. Do not treat these moving tags as reproducible production-grade dependencies.

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
