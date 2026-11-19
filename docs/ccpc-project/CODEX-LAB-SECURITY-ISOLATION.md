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

## Step 23 — interface negation and scoped traffic-direction interpretation (2026-11-19)

Operator ran a hostname-guarded read-only `iptables -S` analysis that explicitly recognizes `!` interface negation, reporting only abstract match categories and not raw firewall rules, addresses, ports or secrets:

| Chain and position | Input match | Output match | Target | Additional options |
| --- | --- | --- | --- | --- |
| `INPUT` #1 | LAB | ANY | DROP | yes |
| `DOCKER-USER` #1 | NOT_LAB | LAB | DROP | yes |
| `DOCKER-USER` #2 | LAB | NOT_LAB | DROP | yes |
| `DOCKER-INTERNAL` #1 | ANY | LAB | DROP | yes |
| `DOCKER-INTERNAL` #2 | LAB | ANY | DROP | yes |
| `DOCKER-FORWARD` #8 | LAB | LAB | ACCEPT | no |

**Interpretation:** The observed interface conditions are consistent with deliberate separation: a lab-origin INPUT drop, both cross-bridge directions denied in DOCKER-USER, and an explicit same-bridge ACCEPT. This corrects the ambiguity of Step 22's abbreviated `BOTH` classification, which did not account for negation. **All five DROP rules have unexamined additional options**, so the actual packet classes they match remain unverified. The apparent DOCKER-INTERNAL broad interface rules also need their extra conditions interpreted to establish whether they block all lab traffic or only crossing traffic. A direct same-bridge ACCEPT does not prove access to DB/Redis is healthy; no connectivity probes were performed. No host/network or container modifications occurred.

**Next one read-only check:** classify the *additional rule predicates* (comment-only versus source/destination/conntrack/protocol/port/other conditions) without printing any predicate values. Keep the agent stopped; do not send packets to DEV, either PRODUCTION environment, the Docker host, or other sensitive services.

## Step 24 — laboratory firewall additional conditions (2026-11-19)

A hostname-guarded read-only classification of the six bridge-matching `iptables -S` rules found:

| Chain / position | Additional condition category |
| --- | --- |
| `INPUT` #1 | `address_filter` |
| `DOCKER-USER` #1 and #2 | `COMMENT_ONLY` |
| `DOCKER-INTERNAL` #1 and #2 | `address_filter` |
| `DOCKER-FORWARD` #8 | `NO_ADDITIONAL_FILTER` |

Total matching rules classified: **6**. The operator did not print address values, ports, comments or raw rules.

**Interpretation:** the two cross-interface `DOCKER-USER` DROP rules found at Step 23 have comments only, so no further packet conditions were observed in those rules beyond interface matches. This is strong configuration evidence for denying forwarded cross-bridge traffic in both directions. The same-bridge `DOCKER-FORWARD` ACCEPT has no additional filters, but earlier rule traversal still matters. The lab-origin `INPUT` and both `DOCKER-INTERNAL` DROP rules use address filters; their actual coverage relative to the lab subnet is **not yet verified**. Do not infer that every host-bound, LAN-bound, proxy-bound or outbound path is blocked merely from the category names. Codex remains stopped/NO-GO. No container, firewall, DEV, UAT or production state changed.

**Next diagnostic:** sanitized read-only comparison of the INPUT/DOCKER-INTERNAL address predicates with the Docker network's own IPAM subnet; report coverage categories (exact, covering, partial, disjoint), not actual IPs, interface names or raw rule text. Negation and direction must be handled correctly.

## Step 25 — firewall address predicates cover lab subnet (2026-11-19)

The operator ran a hostname-guarded, read-only comparison of the lab network's own Docker IPAM IPv4 subnet against source/destination predicates in three matching firewall rules; subnet and address values were not printed:

| Chain / position | Source coverage | Source negated? | Destination coverage | Destination negated? |
| --- | --- | --- | --- | --- |
| `INPUT` #1 | `EXACT_LAB_SUBNET` | no | `ANY` | no |
| `DOCKER-INTERNAL` #1 | `EXACT_LAB_SUBNET` | **yes** | `ANY` | no |
| `DOCKER-INTERNAL` #2 | `ANY` | no | `EXACT_LAB_SUBNET` | **yes** |

**Interpretation with Step 23 interface matches:** `INPUT` #1 matches traffic arriving via the lab bridge and originating from the exact lab IPv4 subnet and drops it. `DOCKER-INTERNAL` #1, which matches egress interface LAB, drops packets sourced **outside** the lab subnet; #2, which matches ingress interface LAB, drops packets destined **outside** the lab subnet. The two `DOCKER-USER` rules (Step 24) impose additional cross-interface DROP restrictions without packet-filtering predicates beyond the interface match. This is strong *static configuration evidence* consistent with host and cross-network isolation while permitting intra-lab bridge forwarding. It is **not proof of live connectivity denial**, host-local proxy isolation, DNS restrictions or full absence of other packet paths. The Step 25 diagnostic did not create packets or change the firewall. No development, old/new production, or UAT services were touched.

**Static IPv4 firewall review:** provisionally passed on the verified scoped predicates, subject to controlled negative runtime tests and any review of alternate network/host routes. **Codex startup remains NO-GO** pending resource caps, sandbox/approval posture, workspace and credential boundaries, and approved GitHub access design.

**Next read-only host diagnostic:** inventory Compose provenance for the stopped lab agent and its image/configuration identity, *without printing command-line arguments, env values, host filesystem paths or credentials*, before reviewing sandbox/approval settings. The audit should distinguish the live container from the tracked source template and avoid any agent execution.

## Step 26 — startup argv-only flag scan (2026-11-19)

Operator ran a hostname-guarded read-only parse of Docker `.Config.Entrypoint` and `.Config.Cmd` for the **stopped** agent, without printing argument contents. Results: `entrypoint_arg_count=0`, `command_arg_count=2`, `references_codex=False`, `danger_full_access=False`, `bypass_approvals_and_sandbox=False`, `full_auto=False`, and `approval_never=False`.

**Interpretation:** None of the five searched Codex invocation strings was present directly in this two-argument command/entrypoint configuration. **This is not a complete command/script/config review:** the arguments may launch a shell, wrapper or other executable; runtime scripts or config files could still set unsafe flags; CLI installation and its effective approval/sandbox posture remain **unverified**. The absence of a direct `codex` string does not establish whether Codex is installed or can execute. The agent remains stopped/NO-GO; no host or protected environment was modified.

**Next single read-only check:** classify the agent startup command interpreter/executable and shell-mode flags without printing its raw argv, commands, host paths or values. Do not launch the container or agent to inspect this.

## Step 27 — configured agent keepalive startup (2026-11-19)

Operator's read-only classification of the stopped agent's Docker Entrypoint/Cmd reported `program_category=KEEPALIVE`, `shell_command_mode=False`, `known_idle_keepalive=True`. The classifier recognizes the exact Docker command arrays `["sleep","infinity"]` or `["tail","-f","/dev/null"]`. Its two command arguments match a recognized idle keepalive pattern, so Docker's **direct configured startup command** is not a Codex agent or a shell `-c` expression. The prior stopped/restart=no result remains the latest reported runtime state.

**Limit:** This does **not** establish which CLI tools are installed in the image, whether Codex configuration/sandbox would be safe if invoked manually, or whether any other process can start it. No running agent or additional process was inspected or executed. It is **not permission to start the container**.

**Next diagnostic:** read-only review of the stopped agent's immutable image ID, local image tag match and repository-digest availability, without printing labels, image history, Docker args, env values, paths or secrets. A mutable `frappe/bench:latest` tag was observed earlier; pinning/provenance must be reviewed before execution. Then evaluate Codex executable/sandbox by a separate approved plan.

## Step 28 — stopped agent image identity and mutable tag (2026-11-19)

Operator ran a hostname-guarded, read-only `docker inspect` plus `docker image inspect` comparison. Reported sanitized output:

| Field | Operator-reported result |
| --- | --- |
| Agent running | `False` |
| Configured image is `frappe/bench:latest` | `True` |
| Container image ID (partial only) | `sha256:49cdcb679e3c` |
| Local configured tag resolves to container image ID | `True` |
| Recorded repository digests | `1` |

**Interpretation:** the stopped container's immutable image ID matches the local image currently tagged `frappe/bench:latest`. This is local *identity consistency*, **not image provenance verification, image signature/attestation verification, or a secure pinned configuration**. The `latest` tag remains mutable, and a recorded repo digest does not by itself prove trust in the image publisher, what was built into the image, or installed Codex CLI/sandbox behavior. The hash is intentionally recorded only as a partial diagnostic identifier, not as a fully usable pinned digest. No agent execution, pull, container restart or protected-environment change occurred.

**Next read-only check:** check that the recorded `RepoDigests` entry uses the expected `frappe/bench@sha256:<64 hex>` shape and whether the *container's local image* and current tag still agree; print only boolean/counters, not the digest itself. Do not pull or build the image. This cannot establish supply-chain trust; further work must inspect approved Compose source, local CLI installation, sandbox settings, and resource controls before any startup.

## Step 29 — recorded repository digest shape (2026-11-19)

Operator ran a hostname-guarded read-only Docker inspection against the stopped lab agent and its local immutable image reference. Reported `agent_running=False`, `image_reference_is_expected=True`, `repository_digest_count=1`, `expected_repository_digest_count=1`, `all_digests_expected=True`. The test uses the complete regular expression for optional official Docker registry prefix followed by `frappe/bench@sha256:` and 64 lowercase hexadecimal characters, without disclosing the actual digest.

**Interpretation:** exactly one recorded repository digest conforms to the expected **name and digest syntax**; the container is stopped and still configured as `frappe/bench:latest`. This verifies neither image authorship nor a trusted build provenance, attestation, digest pinning in the Compose source, CLI installation, sandbox enforcement, resource safety or runtime connectivity. `latest` is still mutable. No image pull/build or container start occurred. Codex remains **NO-GO**.

**Next read-only diagnostic:** classify the container's Compose provenance labels and whether it refers to an explicitly tracked source configuration, without displaying source paths, labels' values, startup arguments, environment or secrets. Then use that provenance to examine planned installation/invocation without starting the agent.

## Step 30 — stopped agent Compose provenance (2026-11-19)

The operator ran a hostname-guarded, read-only Docker metadata check for the stopped laboratory agent, reporting: `agent_running=False`, `compose_project_expected=True`, `compose_service_expected=True`, `compose_workdir_recorded=True`, `compose_workdir_exists=True`, `compose_config_files_recorded=1`, `compose_config_files_existing=1`.

**Interpretation:** Docker's Compose project/service labels correspond to the expected `ccpc_codex_dev_agent` / `agent`. One recorded Compose file and the working directory currently exist on the host. Their names/paths and contents were not printed. The file is a suitable candidate for **read-only source configuration inspection**, but existence alone does not prove the source file is unchanged from the container's original creation, matches its current configuration, or contains no sensitive information. The container was not started or modified. Codex remains **NO-GO**.

**Next single read-only check:** parse the agent service in the recorded Compose file and report only security-relevant key presence/type and resource-limit presence (never raw paths, environment or secret values). First guard against a moving file or ambiguous service. Do not run `docker compose up`, pull images, or execute the agent.

## Step 31 — Compose agent resource and privilege declarations (2026-11-19)

Operator ran a hostname-guarded, read-only `docker compose config --format json --no-interpolate --no-env-resolution` inspection of the single Compose file identified by Docker's stopped-agent metadata, reporting only selected settings from service `agent`:

| Field | Operator-reported value |
| --- | --- |
| `agent_running` | `False` |
| `source_service_found` | `True` |
| `memory_limit_defined` | `False` |
| `cpu_limit_defined` | `False` |
| `pids_limit_defined` | `True` |
| `source_read_only` | `True` |
| `source_privileged` | `None` (omitted in Compose source) |

**Interpretation:** the current parsed Compose source contains no configured agent CPU or memory cap, although it does contain a PID cap and read-only root filesystem setting. The omitted Compose `privileged` key should not be treated as privileged mode being enabled: the earlier Docker runtime inspection reported `privileged=false`. Prior read-only runtime inspection also found **no CPU or memory caps on all four laboratory containers**, and the three support services are still running in the last confirmed container-state observation. Missing resource limits are an outstanding **cohosted availability risk** and a mandatory blocker before any Codex agent start. A current Compose file need not exactly match the settings at the original time of container creation; the earlier runtime verification provides an independent check. No changes made to containers, Docker, host, DEV, OLD/NEW PROD or UAT.

**Next single read-only check:** inspect the same Compose source for CPU, memory and PID limits of **all lab services** (agent, DB, Redis), reporting only service names and boolean limit presence, not raw Compose configuration, paths or environment values. Do not run `docker compose up`, recreate containers, pull images, or restart services. Design approved and reviewed changes in GitHub before any lab-only host operation, protecting cohosted workloads.

## Step 32 — four laboratory services and extra Compose service (2026-11-19)

Operator ran a hostname-guarded, read-only parse of the current Compose source for the stopped laboratory agent. Reported `agent_running=False`, `expected_services_present=True`, `extra_service_count=1`, and these resource-limit presence flags:

| Compose service | Memory limit present | CPU limit present | PID limit present |
| --- | --- | --- | --- |
| `agent` | false | false | true |
| `db` | false | false | false |
| `redis-cache` | false | false | false |
| `redis-queue` | false | false | false |

**Important:** The Compose source contains **one additional service** beyond these four; it was not named or investigated in Step 32. It is not proof of a fifth running container. Earlier runtime checks also showed no CPU/memory caps on the four corresponding containers. No Docker or host mutations occurred.

**User preference:** operator wants Codex to access maximum resources and questions whether any caps are needed. This is a performance preference, **not approval to launch Codex or risk cohosted protected services**. A possible compromise is generous CPU availability without a hard quota *after* checking host capacity/contention, while retaining a protective memory ceiling, PID caps, and limits on DB/Redis as appropriate. A dedicated Codex machine/VM may support a less restricted policy without competing with CCPC services. Actual bounds require review of host resource headroom, protected workloads and rollback approach; no caps have been agreed or applied. **NO-GO remains** until isolation, authentication, sandbox, and availability risks have been addressed or explicitly resolved without weakening protected-environment safeguards.

**Next step:** identify the extra Compose service using a sanitized, read-only classification without disclosing paths, credentials or configuration values; then inspect aggregate host resources, if needed, before proposing any GitHub-first resource plan. Keep agent stopped; do not run `docker compose up` or change DEV, OLD/NEW PROD or UAT.

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
