# CCPC local Codex laboratory — security, access and isolation audit

**Workstream:** Local Codex Security, Accessibility and Isolation  
**Snapshot date:** 2026-11-19 (Asia/Manila)  
**Evidence:** Operator-supplied output from read-only Docker/host inspection on `ccpcerpserver`. ChatGPT did **not** directly inspect the Docker host. This is a point-in-time configuration inventory, **not** a penetration test, host-network connectivity test, or authorization to start the agent.

## Authority, purpose and boundaries

Follow [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [CURRENT-HANDOFF-3.md](CURRENT-HANDOFF-3.md). This is a **separate, parallel security workstream** from the four-company UAT and OLD/NEW production cutover. GitHub is authoritative for committed application and deployment source; live host behavior must be separately verified by the operator.

**Objective:** make local Codex usable for *reviewed, bounded development* without access to persistent DEVELOPMENT, either PRODUCTION environment, Docker host control, SSH material, business databases, or sensitive infrastructure.

**Mandatory hold:** Do not start, enter, or execute the agent until isolation, credential, filesystem, network, workspace and approval safeguards have passed. Do not execute test probes inside an untrusted agent; do not change DEV/OLD PROD/NEW PROD services, DBs, volumes, networks, backups, or production data; do not grant unrestricted Docker socket access. The cancelled automatic Codex reporting, scheduled publishing and paid OpenAI API integration remain cancelled. Code changes follow reviewed GitHub branches; merge/DEV pull/DEV migration/production release are independently controlled.

The historical [project context](ccpc-project-context.md) describes a Codex CLI sandbox workaround with `danger-full-access` in a **different** DEVELOPMENT devcontainer. **Do not carry that alias or its trust assumptions into this lab.** No live Codex CLI availability or sandbox behavior in the dedicated lab has yet been verified.

## Host and Compose inventory — operator-reported

- Host/user: `ccpcerpserver` / `gani`; architecture x86_64.
- Reported host capacity: total RAM 30.0 GiB; available RAM 26.5 GiB; Docker-data filesystem free 682.5 GiB, as of the operator's preceding host check (not remeasured here).
- Docker 29.1.3; Compose 2.40.3.
- Compose project `ccpc_codex_dev_agent`: four containers, three running. Separate `ccpc_four_company_uat` was reported as zero containers; this audit did not inspect or modify it.
- `ccpc_codex_dev_agent-agent-1`: image `frappe/bench:latest`; exited 143 (compatible with SIGTERM, but the cause is unverified).
- `ccpc_codex_dev_agent-db-1`: `mariadb:11.8`, running.
- `ccpc_codex_dev_agent-redis-cache-1` and `ccpc_codex_dev_agent-redis-queue-1`: `redis:7-alpine`, running.
- Each container has `RestartPolicy.Name=no` and `AutoRemove=false`. Agent `State.Running=false`; supporting services `State.Running=true`. No automatic Docker restart policy is configured.
- The `PORTS` column showed only container-exposed `3306/tcp` or `6379/tcp` for DB/Redis, not host-published mappings; agent `HostConfig.PortBindings` count was zero. A broader host firewall/route audit remains pending.

## Network observations

The agent, MariaDB and both Redis containers reported **only** network `ccpc_codex_dev_agent_lab`, with `NetworkMode` set to that network; the active endpoint list contained the three running support containers, not the stopped agent.

Docker network inspection returned:

| Property | Operator-observed value |
| --- | --- |
| Driver/scope | `bridge` / `local` |
| `Internal` | `true` |
| `Attachable` | `false` |
| `EnableIPv6` | `false` |
| Connected endpoints at inspection | Laboratory DB and two laboratory Redis containers only |
| Explicit `enable_icc`, IP masquerade, IPv4 gateway mode | Unset/not reported |

The container reports no `ExtraHosts` entries and no custom DNS servers. `HTTP_PROXY` and `HTTPS_PROXY` are configured with hostname endpoints and no embedded URL authentication; `ALL_PROXY` is absent/empty; `NO_PROXY` has five entries and no wildcard. **No proxy hostnames or proxy values were copied to this document.** Neither HTTP nor HTTPS proxy hostname matched known lab network aliases, explicit extra-host mappings or common Docker host aliases.

**Interpretation:** dedicated internal bridge and absence of reported host-published ports are encouraging, **but do not prove** that host, other bridge gateways, LAN services, proxy destinations, DNS, host daemons, or protected network endpoints are unreachable. There has been **no active egress or connectivity test**. The bridge's effective firewall and routing rules remain unverified. No Docker networks were modified.

## Agent privilege and namespace observations

| Property | Operator-observed value |
| --- | --- |
| `Privileged` | `false` |
| User | `1000:1000` |
| `ReadonlyRootfs` | `true` |
| `CapAdd` | `[]` |
| `CapDrop` | `["ALL"]` |
| `SecurityOpt` | `["no-new-privileges:true"]` |
| AppArmor | `docker-default` |
| PID mode | no host PID setting reported |
| IPC namespace | `private` |
| Cgroup namespace | `private` |
| User namespace | no explicit per-container setting reported |
| Devices | zero |
| Host port binding count | zero |

No Docker socket mount appeared among the **resolved** agent mounts. This does **not** establish that the Docker API or other privileged host services are unreachable through networking or other mechanisms. Effective seccomp, host-level user namespace remapping, Compose definitions and all external host access still require review.

## Resolved mounts, Docker volumes and credential boundaries

Agent resolved mounts at inspection:

| Type | Container destination | Writable |
| --- | --- | --- |
| Docker volume | `/home/frappe` | Yes |
| Docker volume | `/home/frappe/.cache` | Yes |
| Bind | `/run/secrets/db-user-password` | No |

`HostConfig.Binds` had two entries while the resolved `.Mounts` list had three mounts. The former is a configuration-entry count and **not a reliable count of resolved mounts of type bind**. Any further host-source review must use sanitized metadata, without printing paths or secret contents.

Three named volumes were observed: `ccpc_codex_dev_agent_agent-home`, `ccpc_codex_dev_agent_agent-cache` and `ccpc_codex_dev_agent_db-data`. The two Redis containers also each have a distinct anonymous `/data` volume. A search of **all existing Docker containers, including stopped ones**, using these five volume identifiers returned **only the four Codex laboratory containers**. This does not prove the contents of those volumes are synthetic, non-sensitive, or free of credentials.

The database credential bind source was found in exactly the lab `db-1` and stopped `agent-1` containers (no external container used the **same direct bind source**). Its host metadata, without revealing its path or contents: regular file, mode `600`, UID/GID `1000:1000`; no symlink at the inspected path. Since the agent is configured to run as UID/GID 1000, the file is **likely readable by the agent even though mounted read-only**. This is not proof of the file's contents, provenance, or lab-only DB account scope. Parent-directory mounts, alternate paths/hardlinks and host credential reuse remain unchecked.

The agent-home volume was checked for these common top-level credential locations: `.ssh`, `.codex`, `.config/gh`, `.git-credentials`, `.netrc`, `.aws`, `.kube`. All were reported `ABSENT`; this is **not** a comprehensive recursive credential scan or evidence that nothing sensitive exists elsewhere in the volumes.

The agent environment **variable names only** were examined. No obvious `GITHUB_TOKEN`, `GH_TOKEN`, `OPENAI_API_KEY` or SSH credential name appeared. Relevant configured names included `DB_HOST`, `DB_PORT`, `REDIS_CACHE`, `REDIS_QUEUE`, `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY`. **No environment values or secrets were printed or committed.**

## Resource constraints — unresolved blocker

The operator's read-only inspection found:

| Container | Memory limit | CPU limit | PID limit |
| --- | --- | --- | --- |
| Agent | Not set (`Memory=0`) | Not set (`NanoCpus=0`, `CpuQuota=0`) | `512` |
| MariaDB | Not set | Not set | Not configured |
| Redis cache | Not set | Not set | Not configured |
| Redis queue | Not set | Not set | Not configured |

**Risk:** unbounded memory/CPU consumption can impair co-hosted environments even without a privilege breakout. Propose and review bounded limits after inspecting the Compose source and actual workload requirements; do not change running services or containers under this documentation-only work.

## Step 18 — host bind-source overlap check (2026-11-19)

Operator ran a host-guarded read-only inspection of all current Docker containers, comparing resolved `Source` values for the agent's `bind` mounts against resolved mount sources outside the Codex Compose project. Reported counts:

| Check | Operator-reported result |
| --- | ---: |
| Docker containers inspected (running and stopped) | 19 |
| Containers outside Codex lab | 15 |
| Agent resolved mounts of type `bind` | 1 |
| Exact source-path matches outside lab | 0 |
| Source-path ancestor/descendant overlap candidates outside lab | 0 |

**Interpretation:** The single resolved agent bind did not match or nest within any resolved Docker mount source on the 15 other containers, as compared lexically after `os.path.normpath`. This is evidence against *direct Docker mount-source sharing* at that point in time. It is **not** proof against symlink aliases, hardlinks, mount propagation, host-level file access, a separate Docker socket connection, or routes into protected networks. The query did not read secret contents or modify containers. Codex remains **NO-GO**.

**Next diagnostic:** read-only check whether Docker's laboratory bridge has a host-side network interface/gateway and whether host IPv4 forwarding is enabled, without printing IP addresses. Then separately examine effective firewall policy. Neither check by itself proves connectivity or isolation.

## Step 19 — host-side Docker bridge and IPv4 forwarding (2026-11-19)

Operator executed a read-only, hostname-guarded query of the `ccpc_codex_dev_agent_lab` network and the host's IPv4 bridge and forwarding metadata. Output was:

| Field | Operator-reported value |
| --- | --- |
| `network_internal` | `True` |
| `host_bridge_present` | `True` |
| `host_bridge_ipv4_present` | `True` |
| `docker_gateway_defined` | `True` |
| `host_ipv4_forwarding` | `1` |

**Interpretation:** the lab uses Docker's internal-network setting but the host has a bridge-side IPv4 interface/gateway and kernel forwarding enabled. This is **not evidence that firewall rules permit traffic** from the lab to the host, protected Docker networks, LAN, or Internet. Conversely, `internal=true` alone is not proof those paths are unreachable. Firewall implementation, effective INPUT/FORWARD filtering, proxy routing, DNS, and controlled negative reachability tests remain pending. No agent execution or host/network changes occurred.

**Next diagnostic:** inventory the effective host firewall rule implementation and hook policies via read-only, *sanitized* counts before examining scoped lab-bridge INPUT/FORWARD handling. Do not print IP addresses or rule targets containing sensitive host details.

## Step 20 — nftables host INPUT/FORWARD policies (2026-11-19)

The operator's read-only `iptables --version` and `nft -j list ruleset` metadata inspection returned:

| Metadata | Operator-reported value |
| --- | --- |
| `iptables_version` | `iptables v1.8.11 (nf_tables)` |
| `input_base_chains` | `1` |
| `input_default_policies` | `accept` |
| `forward_base_chains` | `2` |
| `forward_default_policies` | `accept,drop` |
| `nft_ruleset` | `readable` |

**Interpretation:** the `input` hook includes an `accept` base-chain default; the `forward` hook has two base chains with mixed defaults. This **does not prove** that Codex can reach the Docker host or other networks, nor does it prove isolation: rule expressions, chain priorities, jump paths, and bridge-specific matching were not inspected. Different hooked base chains can have different priorities and a later drop can still block a packet; a base-chain accept by itself is not a global allow. Docker `internal=true` remains configured but is not a substitute for effective packet filtering and host-service boundary verification.

**Next diagnostic:** read-only and sanitized scoped nftables analysis for the Codex bridge: count rules with exact bridge-interface references, show their family/table/chain and action types (never IPs, CIDRs, addresses, proxy values, or raw rule bodies), and print input/forward base-chain priorities. Keep Codex stopped. No production, DEVELOPMENT or UAT activity is authorized.

## Step 21 — nftables lab bridge rule inventory (2026-11-19)

The operator's read-only network-scoped firewall query produced these sanitized results:

| Observation | Reported value |
| --- | --- |
| Network internal | `True` |
| IPv4 `ip filter` INPUT base chain | priority 0, policy `accept` |
| IPv4 `ip filter` FORWARD base chain | priority 0, policy `drop` |
| IPv6 `ip6 filter` FORWARD base chain | priority 0, policy `accept` |
| Rules explicitly matching laboratory bridge name | 6 |
| `DOCKER-FORWARD` | 1 rule containing `accept` |
| `DOCKER-INTERNAL` | 2 rules containing `drop` |
| `DOCKER-USER` | 2 rules containing `drop` |
| `INPUT` | 1 rule containing `drop` |

These rules provide promising evidence that Docker's network separation has additional explicit firewall protection, including an INPUT drop against at least some host-bound lab packets. **This audit has not yet verified interface direction, full match predicates, rule ordering, jump reachability or whether exceptions precede drops.** The DOCKER-FORWARD ACCEPT may be legitimate within-lab traffic or may have conditions not yet inspected. The INPUT default accept and FORWARD drop/accept interactions cannot be interpreted without these details. **Not a connectivity test; no proof of isolation or exposure.** No host, container, network or environment changes occurred.

**Next:** one read-only sanitized rule-order/direction review for the six lab-matching rules and the jump path from FORWARD to Docker chains, without printing IP addresses, CIDRs, proxy values or raw firewall expressions. Codex stays stopped/NO-GO.

## Step 22 — lab firewall jump order and interface-direction report (2026-11-19)

The operator ran a hostname-guarded, read-only `iptables -S` inspection, filtered to interface references for the Codex laboratory bridge. No raw rules, IPs or credentials were published.

| Chain | Reported position | Interface-direction classification | Target |
| --- | ---: | --- | --- |
| `INPUT` | 1 | IN from lab bridge | DROP |
| `FORWARD` | 1 | jump (not bridge-specific in abbreviated output) | DOCKER-USER |
| `FORWARD` | 2 | jump (not bridge-specific in abbreviated output) | DOCKER-FORWARD |
| `DOCKER-USER` | 1, 2 | BOTH lab input/output interfaces referenced | DROP / DROP |
| `DOCKER-FORWARD` | 2 | jump (not bridge-specific in abbreviated output) | DOCKER-INTERNAL |
| `DOCKER-FORWARD` | 8 | BOTH lab input/output interfaces referenced | ACCEPT |
| `DOCKER-INTERNAL` | 1 | OUT toward lab bridge | DROP |
| `DOCKER-INTERNAL` | 2 | IN from lab bridge | DROP |

**Important limitation:** The diagnostic classified `-i` and `-o` appearances but **did not parse `!` negation or match predicates**. For example, `-i LAB ! -o LAB` is *not* an intra-lab match even though both interface tokens appear. Likewise, the INPUT rule may have additional conditions. We cannot conclude the precise allowed/blocked flow or the reachability of alternate chains, stateful exceptions, proxy destinations or host services from this abbreviated output.

**Interpretation:** there are clearly scoped, early firewall DROP rules and jump paths consistent with an isolation design, including an INPUT DROP at position 1 and cross-Docker chain protections. This is stronger evidence than the bridge's `internal=true` metadata alone, but still **not a host-connectivity/isolation pass**. Agent remains stopped/NO-GO.

**Next diagnostic:** sanitized read-only parse of the same bridge-matching rules with interface negation (`!`) and presence of extra predicates preserved. No raw rules, interface names, IPs, ports, credentials, network probes, or container actions.

## Gate status as of 2026-11-19

| Gate | Status |
| --- | --- |
| Identity, count, role and restart policy of four lab containers | Observed; agent stopped |
| Dedicated bridge membership, internal/attachable/IPv6 flags | Observed; favorable |
| Agent non-root, read-only root, capabilities, namespaces, AppArmor | Observed; favorable |
| Five volume identifiers attached only to lab containers | Observed; favorable |
| Direct database credential source shared only by lab DB/agent | Observed; **provenance/least privilege pending** |
| Persistent home contents and alternate credential paths | **Pending**; common locations absent only |
| Proxy reachability, DNS behavior, effective host routing/firewall | **Pending** |
| Effective Docker API/host-service access and credential exfiltration paths | **Pending** |
| CPU/memory resource limits | **Not configured** |
| Approved GitHub authentication mechanism and read/write scopes | **Pending** |
| Local Codex CLI availability, sandbox effectiveness and approval defaults | **Pending**; do not start agent to discover |
| Approved synthetic-data-only workspace and worktree separation | **Pending** |
| Controlled functional tests and safety acceptance | **Not executed** |

**Current disposition: NO-GO for starting Codex.** No tests have been run inside the agent; no lab, DEVELOPMENT, OLD/NEW PRODUCTION, UAT or backup changes have been made in this investigation.

## Safe engineering design direction (proposal, not deployed)

1. Keep the lab worktree and all generated output separate from the shared DEVELOPMENT checkout, business volumes and host SSH directories. Use only reviewed source snapshots or a dedicated, permission-constrained GitHub access method after egress and credential design are approved.
2. Prefer short-lived, minimum-scope GitHub authentication; avoid mounting host SSH private keys, personal GitHub credentials, production tokens or the host Docker socket. A supervised operator-mediated, SHA-pinned GitHub-to-lab source transfer may be safer than live repository credentials inside the agent.
3. Review actual Compose definitions and sanitised host mount/namespace/firewall metadata before any mutation. Design egress allowlists or an isolated network transfer point without defeating `internal=true`; ensure the proxy cannot route to local/protected address ranges.
4. Introduce verified CPU/memory/PID controls before agent execution; preserve laboratory resource headroom for co-hosted services.
5. Keep Codex approval prompts on, dangerous bypass modes off, and a hard block on destructive commands, Docker control, database writes and deployment actions. Confirm actual sandbox mechanics before trusting them.
6. Only then design bounded tests with synthetic workspaces and synthetic data: filesystem deny cases; Docker socket/host mount absence; DNS/proxy/egress deny tests against controlled targets; permitted source fetch only; Git diff/no-production effects; resource-limit observation; kill/restart behavior. Each test requires a narrowly reviewed plan and operator control; do not use live DEV/PROD endpoints as test targets.

**Next step:** continue with **one read-only host diagnostic at a time**, prioritizing sanitized host-side mount/source classifications and access boundaries, then effective host-network restrictions. Do not launch the agent or modify host networking just to make GitHub reachable.

## Documentation maintenance

Update this document with each *verified* security milestone, date and evidence source. Keep it separate from the mutable main delivery handoff; add a short handoff/README link for discoverability. Never commit passwords, keys, tokens, proxy URLs, secret values, sensitive host paths, business records, raw environment or container logs. This audit describes the **operator-reported Docker configuration**, not independently verified runtime connectivity or Codex functional readiness.
