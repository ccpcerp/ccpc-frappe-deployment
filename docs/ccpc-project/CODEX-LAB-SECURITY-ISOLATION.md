# CCPC local Codex laboratory — security, access and isolation audit

**Workstream:** Local Codex Security, Accessibility and Isolation  
**Snapshot date:** 2026-11-19 (Asia/Manila)  
**Evidence:** Operator-supplied output from read-only Docker/host inspection on `ccpcerpserver`. ChatGPT did **not** directly inspect the Docker host. This is a point-in-time configuration inventory, **not** a penetration test, host-network connectivity test, or authorization to start the agent.

## Topology correction and Step 62 resource checkpoint (2026-11-19)

**Latest operator clarification — supersedes earlier co-hosting assumptions in this historical audit:** The operator states that **PRODUCTION is now on a separate server** and there are **no production workloads on `ccpcerpserver`**. Earlier references in Steps 1–61 to OLD PRODUCTION sharing this host were the working assumption at that time, **not a currently verified infrastructure fact**. Do **not** use those earlier statements as evidence that PRODUCTION still runs on the Codex host. The new topology is **operator-reported and has not been independently verified from host inventory or production infrastructure**. Existing Docker services other than the lab (including possible DEVELOPMENT/UAT) may still share the Codex host, and isolation requirements still apply. Do not touch the separate production server without independent explicit authorization.

**Step 62 (host read-only observation, operator supplied):** Agent remains stopped. Four lab containers were checked; agent has a Docker PID cap but no Docker memory or CPU cap or CPU affinity. Lab `db`, `redis-cache`, and `redis-queue` are running with no Docker memory, CPU, PID, or CPU-affinity cap. `OOMKilled=False` was reported for each. Host point-in-time RAM: **29.96 GiB total, 26.24 GiB available**; swap **8.0 GiB total and 0.0 GiB used**. The available-memory figure is a single snapshot, not a peak-load guarantee. The optional proxy was not included as an existing container (it remains absent by earlier inspection) and has no declared resource limits in Compose (Step 61). No changes or network probes were performed.

**Revised availability risk:** If the current production topology is as reported, Codex activity on this host does **not directly compete with production-server CPU/RAM**. Avoid presenting protection of co-hosted OLD PRODUCTION as a current reason for resource caps. High-performance CPU-unrestricted Codex is a reasonable planning option subject to impact on other local services. Consider protective memory/PID budgets primarily to keep the **local DEVELOPMENT/UAT/host services** stable, not to protect remote production resources. All access, data, Docker/firewall, DNS, proxy-image, listener, and runtime security gates remain **NO-GO** until separately resolved. No CPU/memory cap or Compose change is authorized by these findings.

**Next safe step:** identify whether other nonlab containers are active on this host using Docker metadata only, returning **counts by broad operational category** (not names, images, paths, ports, IDs, IPs, labels, credentials or environment). This is only a local workload inventory and should not be used to infer where remote PRODUCTION resides.

## Step 63 — local nonlaboratory Docker workload inventory (2026-11-19)

The operator ran a hostname-guarded, read-only inventory on `ccpcerpserver` using Docker metadata. Sanitized output: `agent_running=False`, `lab_container_count=4`, `other_container_count=15`, `other_running_count=7`, `other_stopped_count=8`, `other_compose_project_count=2`, `other_running_memory_limited_count=0`, `other_running_cpu_limited_count=0`, `other_running_oom_killed_recorded_count=0`.

**Interpretation:** seven nonlab containers are presently running and eight are stopped, across two other Compose projects (the project count does not independently characterize container roles). None of the seven *running nonlab containers* has an effective Docker HostConfig memory or CPU limit, and none currently reports the Docker state flag `OOMKilled=True`. These facts neither establish the services' identities nor demonstrate where PRODUCTION is hosted. The operator's Step 62 clarification remains authoritative for the intended planning assumption: **PRODUCTION is on a separate server; no production workloads are claimed to reside on `ccpcerpserver`**, although this topology was not independently verified by this Docker inventory. Avoid repeating the earlier cohosted-OLD-PRODUCTION assumption as current fact. Other local services still need protection from resource starvation.

**Resource planning:** the Step 62 host memory snapshot was total 29.96 GiB and available 26.24 GiB, 8 GiB swap unused. The operator prefers unrestricted Codex CPU performance; that remains reasonable to evaluate in this updated topology, but lack of memory/PID ceilings across the lab (Step 61) can still destabilize this host and local DEVELOPMENT/UAT. Do not infer safe memory budgets solely from a point-in-time availability figure. No containers or host settings were changed, no image pulls/activations/network probes, and no DEVELOPMENT, UAT or PRODUCTION actions occurred. **Codex and optional Squid remain inactive/NO-GO** due to independent security gates.

**Next read-only diagnostic:** take a one-shot, sanitized aggregate snapshot of CPU and memory currently used by the seven running nonlab containers and three running laboratory containers (no names, IPs, ports, image references or raw Docker stats), plus host RAM availability. This is for local capacity planning only, not a sustained-load guarantee. No changes or activations.

## Step 64 — aggregate local resource snapshot (2026-11-19)

The operator ran the previously prepared read-only Docker stats and host RAM snapshot on `ccpcerpserver` (no host identities, raw container metrics, credentials or paths reported). Sanitized results: `agent_running=False`, `running_lab_containers=3`, `running_other_containers=7`, `lab_memory_used_mib=102.6`, `other_memory_used_mib=2400.1`, `lab_cpu_percent_sum=0.54`, `other_cpu_percent_sum=9.91`, `lab_container_pid_total=21`, `other_container_pid_total=276`, `host_memory_total_gib=29.96`, `host_memory_available_gib=26.21`.

**Interpretation:** The existing three running lab services consume ~103 MiB RAM and ~0.54% of one logical CPU at the sampling moment; seven other running local containers consume ~2.34 GiB RAM and ~9.91% of one logical CPU. Combined sampled Docker stats memory ~2502.7 MiB; host currently reports 26.21 GiB available of 29.96 GiB total. These metrics are **point-in-time**, container stats memory metrics can differ from host physical RSS accounting, and aggregate CPU percentages may exceed 100% over multiple cores. The **stopped Codex agent and inactive proxy are excluded**; their peak demand remains unknown.

**Topology correction retained:** Operator reported PRODUCTION has moved to a separate server, with no production workload on this Codex host (Step 62). The Step 64 output cannot independently verify remote production placement. Do not treat outdated cohosted OLD PRODUCTION assumptions as current. Other local workloads still require protection. Operator's preference for unrestricted Codex CPU is reasonable to consider with this modest observed load, but peak-load and process-memory ceilings remain unresolved. No resource cap, Docker/host change, Codex/optional proxy start, image pull, network probe or ERPNext DEV/PROD/UAT action was taken. **NO-GO** persists for proxy source-access/listener restrictions, image provenance/default user, DNS/security destinations, safe runtime isolation, sandbox/auth and other gates.

**Next one read-only diagnostic:** before proposing the required Squid source ACL and listener restriction, verify existing internal lab bridge's attached endpoint membership by operator-safe classifications, check expected lab containers only, confirm no external project members, and verify the lab IPv4 IPAM range has no overlap with other host Docker bridge network IPv4 IPAM ranges. Do not disclose raw network names/addresses/subnets/host paths or invoke any network connectivity test. Do not modify any Compose or Squid source yet.

## Step 65 — internal lab network endpoint and IPv4 subnet separation (2026-11-19)

Operator ran a hostname-guarded read-only Docker network inspection on `ccpcerpserver`. Sanitized results: `agent_running=False`, `lab_network_internal=True`, `lab_network_attachable=False`, `lab_ipv4_subnet_count=1`, `lab_attached_endpoint_count=3`, `lab_project_endpoint_count=3`, `outside_project_endpoint_count=0`, `other_bridge_network_count=4`, and `overlapping_bridge_subnet_count=0`.

**Interpretation:** The active internal Docker bridge for the Codex lab has three attached endpoints, all from the lab Compose project, with no attached nonlab endpoints; its one IPv4 network range has no overlap with the configured IPAM subnets of four other Docker bridge networks found on the host. The stopped Codex agent is not currently running. This is favorable *static network metadata* for network segregation, not proof of enforced connectivity restrictions or immunity to privileged Docker changes. `Attachable=False` limits manual connections by ordinary tools but is not a security boundary against Docker daemon administrators. Step 62's correction remains in effect: the operator reports PRODUCTION is on another server; the audit does not independently verify remote production placement.

**Open security issues:** the optional Squid service is inactive, has no current local image under its configured mutable tag with `pull_policy: never`, and is proposed to join both this internal network and a second non-internal bridge. Its configured listener binds all interfaces and no Squid source-address ACL was found (Steps 42, 48). Existing IPv4 firewall static checks do not substitute for a runtime negative test. Source filtering should be planned to permit only the required lab agent/client addresses, without exposing Squid on the second bridge. No container/image/bridge activation, network probes, host settings, DEV/UAT or remote PROD changes were made. **NO-GO** remains.

**Next read-only diagnostic:** classify Compose static IPv4 address assignments for the agent and optional proxy on their shared lab bridge, whether the lab network has declared Compose IPAM, and whether the stopped agent has a Docker-assigned IPv4 address in inspect metadata. Return counts/booleans only; never print IPs, CIDRs, image references, container IDs, hostnames, network names, paths, credentials or Compose file content. No Docker changes or execution.

## Step 66 — guarded inspection stopped without result (2026-11-19)

The operator executed the proposed Step 66 hostname-guarded, read-only host script to classify agent/optional proxy static IPv4 assignments on their shared internal bridge. Instead of an audit record, it returned only `STOP: safe inspection unavailable` and the shell prompt. **No Step 66 address assignment or metadata conclusion can be drawn.** The script deliberately conflates failure modes and suppresses exception details to prevent leaking Docker paths/addresses/configuration; a mismatch in preconditions, normalized Compose structure, Docker network project/key labels, IPAM layout or other parsing/errors may have triggered it. Do **not** infer a security breach, absent static addresses, or a Docker networking failure. No change to Docker, server, files, proxies, Codex, DEVELOPMENT, UAT or remote PRODUCTION occurred. Previous favorable Step 65 observations are unchanged but are not a substitute for Step 66.

**Next single read-only check:** run a narrowly scoped sanitized precondition diagnostic, after verifying the same agent is stopped and belongs to the expected lab Compose project. Print only whether normalized Compose agent/proxy networks intersect once, whether the known runtime lab bridge is internal, its Compose project/network labels *present/matching* (booleans, no values), whether its IPv4 subnet count remains one, whether network IPAM was declared in Compose, and only category labels for static agent/proxy addresses (within/outside lab IPAM, not set, invalid). Never log raw paths, DNS/network names, IPs, environment values, secrets, or exceptions. Preserve NO-GO until actual destination and source controls, image provenance, authentication, and runtime tests pass. Do not alter host or Compose to make an inspection succeed.

## Step 66A — safe precheck completed, address fields undetermined (2026-11-19)

Following Step 66's generic safe-stop output, the operator ran the alternative **read-only** metadata precheck. Sanitized output: `agent_running=False`, `compose_parsed=True`, `shared_network_count=1`, `lab_internal=True`, `lab_bridge=True`, `lab_project_label_present=True`, `lab_project_label_matches=True`, `lab_network_label_present=True`, `lab_network_label_matches_shared=True`, `lab_ipv4_subnet_count=1`, `compose_shared_network_declared=True`, `compose_ipam_entry_count=0`, `agent_static_ipv4_class=UNDETERMINED`, `proxy_static_ipv4_class=UNDETERMINED`, `agent_ipv4_recorded_while_stopped=False`.

**Interpretation:** the expected stopped agent, Compose project, optional proxy shared network, Docker internal bridge and corresponding network labels matched, and Docker's live bridge has one IPv4 IPAM subnet (even though the Compose source declares zero entries under its shared network's `ipam.config`). No static IPv4 classification has **yet** been established for the two services: `UNDETERMINED` is a parser classification, **not evidence of a static IP or its absence**. The precheck's `classify_address` returns `UNDETERMINED` when the normalized Compose network entry is not a mapping, including a valid `null` value. That is a *possible* explanation for Step 66's safe stop; inspect sanitized entry type to establish it. A stopped agent has no recorded IPv4 address at inspection.

**Next one read-only check:** validate both normalized Compose service network entry types (null/dict/list or other) and classify static IPv4 address fields as `NOT_SET`, `WITHIN_LAB_SUBNET`, `OUTSIDE_LAB_SUBNET`, `NOT_IPV4` or `UNPARSEABLE`. Include only booleans and classifications, never actual addresses, network names, host paths, full YAML/JSON, service credentials, raw exception strings or DNS requests. Do not change Docker/Compose files or attempt to start inactive services. No host, DEVELOPMENT, UAT or remote PRODUCTION operations. Security status **NO-GO** remains.

## Step 66B — null network attachments imply no declared static IPv4 (2026-11-19)

The operator ran the corrected, hostname-guarded, read-only Compose and Docker network metadata classifier. Sanitized output: `agent_running=False`, `shared_network_count=1`, `lab_identity_verified=True`, `agent_network_entry_type=NULL`, `proxy_network_entry_type=NULL`, `agent_static_ipv4_class=NOT_SET`, `proxy_static_ipv4_class=NOT_SET`, `INSPECTION_COMPLETE`.

**Interpretation:** The Compose-normalized network connection entries are `null` for **both** the stopped Codex agent and the optional inactive Squid proxy on their single shared internal bridge; neither service declares a static IPv4 address there. Docker assigns addresses dynamically when attached. The earlier Step 66 safe stop resulted from the script failing to handle such a valid null network value; Step 66A's `UNDETERMINED` classification did **not** mean a static address existed. No configuration or network failure is implied. The stopped agent presently has no recorded IPv4 address (Step 66A). Never pin a Squid `src` ACL to a last-observed agent address without a controlled addressing scheme. A broad laboratory-subnet `src` ACL would also allow its DB and Redis members (Step 65), so would not enforce agent-only proxy access.

**Potential preferred design for separate review, not implementation authorization:** isolate a proxy-client-only internal bridge connecting just the Codex agent and Squid, while preserving the existing agent-to-DB/Redis lab bridge and keeping the proxy's outbound bridge separate. Evaluate actual Compose dependency/network layout and Docker firewall/proxy binding before selecting this approach; adding networks or changing membership requires explicit review and later tests. Squid's current wildcard listener, absent source ACL, missing image provenance/default UID, DNS/allowlist issues, Codex sandbox and runtime negative-test gates still block activation. No Docker start, host/network edits or DEV/UAT/remote PRODUCTION actions occurred. Overall **NO-GO**.

**Next one read-only diagnostic:** inspect current normalized Compose network membership for all five services by **boolean relationships and counts only**, especially whether the proxy shares the database/Redis bridge and whether agent and proxy each have direct non-internal bridge membership. Never show network names, identifiers, CIDRs, hostnames, IPs, paths, environment values, credentials or raw source. The result will support choosing a minimally disruptive access-segmentation plan.

## Step 67 — optional Squid shares the database and Redis bridge (2026-11-19)

Operator ran a hostname-guarded, read-only topology check of the current Compose source. Reported `agent_running=False`, `agent_network_count=1`, `proxy_network_count=2`, `agent_proxy_shared_network_count=1`, `agent_db_shared_network_count=1`, `agent_redis_cache_shared_network_count=1`, `agent_redis_queue_shared_network_count=1`, `proxy_db_shared_network_count=1`, `proxy_redis_cache_shared_network_count=1`, `proxy_redis_queue_shared_network_count=1`, `agent_noninternal_network_count=0`, `proxy_noninternal_network_count=1`, `shared_internal_network_count=1`, `agent_only_network_count=0`, `proxy_only_network_count=1`.

**Interpretation:** In the *current proposed optional proxy Compose topology*, Codex agent, MariaDB and both Redis instances use the same internal bridge as Squid. The agent has no declared direct membership in a non-internal network; Squid alone has a second non-internal bridge. If Squid were enabled, database and Redis containers could potentially access its all-interface listener on the shared bridge (subject to effective firewall/service behavior), because Step 42 found no source-address ACL. This is inconsistent with an agent-only proxy access goal. This is **source-level potential exposure**, not observed active access: Squid is inactive, and the second network did not exist at Step 49.

**Recommended design for separate review, NOT an authorized change:** retain the existing agent–DB/Redis internal bridge, remove Squid membership from it, add a **new internal proxy-client-only bridge** shared by agent and Squid, and retain the proxy's separate outbound bridge. Then apply a Squid source ACL/default-deny and constrain listener reachability, verify Docker firewall controls, hostname resolution, DNS/special-use IP destination blocks and negative tests. Because the lab project already has running DB/Redis containers and a stopped agent, do **not** recreate or edit any network or Compose config until dependency/network assumptions and rollback impact are reviewed. Production is operator-reported on a separate server (Step 62); no remote production action. No Docker/host actions, image acquisition or protected ERPNext changes occurred. Agent stopped, proxy inactive, **NO-GO**.

**Next single read-only diagnostic:** classify Compose service `depends_on` relationships and whether custom network aliases or fixed addresses are declared on agent/proxy (including where applicable host networking or alternate network modes) using only booleans and counts. Report no actual aliases, service endpoint values, paths, IPs, hostnames, image refs or secrets. This will help determine compatibility with a separate internal proxy-client network.

## Step 68 — no explicit dependencies or alias/address overrides (2026-11-19)

Operator ran a hostname-guarded, read-only check of the existing Compose source across all five declared lab services. Sanitized output: `agent_running=False`, `service_count_checked=5`, `agent_dependency_count=0`, `agent_depends_on_db=False`, `agent_depends_on_redis_cache=False`, `agent_depends_on_redis_queue=False`, `agent_depends_on_proxy=False`, `proxy_dependency_count=0`, `proxy_depends_on_database_or_redis=False`, `other_services_depend_on_proxy=False`, `agent_network_mode_override=False`, `proxy_network_mode_override=False`, `agent_custom_network_alias_count=0`, `proxy_custom_network_alias_count=0`, `total_custom_network_alias_count=0`, `total_static_ipv4_assignment_count=0`, `agent_extra_hosts_declared=False`, `proxy_extra_hosts_declared=False`.

**Interpretation:** Compose does not declare explicit `depends_on` service ordering for agent or proxy or consumers of the proxy; neither agent nor optional proxy declares `network_mode`, `extra_hosts`, custom network aliases, or static IPv4 assignments (confirming Step 66B). This removes some likely configuration conflicts from the proposed new internal agent–Squid client bridge, while preserving the existing agent/DB/Redis bridge and keeping the outbound proxy bridge separate. **No `depends_on` does not mean no runtime DB/Redis dependency:** application configs or environment variables can still reference service hostnames; and adding a network is not a replacement for source ACLs, listener binding and firewall review. The stopped agent's proxy alias/port relationships were found correct in Steps 50–51. No Docker changes, containers started, proxy image downloaded, host probes or DEV/UAT/remote PRODUCTION changes. **NO-GO remains.**

**Next single read-only diagnostic:** inspect Compose declarations for service links, external links, DNS overrides, hostname/domainname declarations, and per-network gateway/priority properties relevant to adding a second internal client network. Output only sanitized counts and booleans (no actual addresses, endpoints, identities, names, passwords, network identifiers, host paths, raw YAML/JSON or secret values). Do not alter networking or activate Codex or Squid.

## Step 69 — no DNS, legacy links or gateway/interface overrides (2026-11-19)

Operator ran hostname-guarded, read-only Compose source check, reporting: `agent_running=False`, `service_count_checked=5`, `shared_agent_proxy_network_count=1`, `agent_dns_override=False`, `proxy_dns_override=False`, `db_redis_dns_override_count=0`, `agent_legacy_links=False`, `proxy_legacy_links=False`, `other_services_legacy_links_count=0`, `agent_hostname_override=False`, `proxy_hostname_override=False`, `agent_gateway_priority_override_count=0`, `proxy_gateway_priority_override_count=0`, `agent_network_priority_override_count=0`, `proxy_network_priority_override_count=0`, `agent_custom_interface_count=0`, and `proxy_custom_interface_count=0`.

**Interpretation:** The five services declare no explicit custom DNS or legacy links; agent and optional proxy declare no hostname, domainname, gateway/priority or interface-name overrides on the existing normalized network entries. This reduces apparent Compose-level obstacles to a new proxy-client-only internal bridge, but does **not** verify default Docker DNS behavior, network gateway selection, runtime IP addresses or the correct egress firewall policy once networks are added. No host or Docker changes, image downloads, Codex/proxy execution, network traffic or DEV/UAT/remote PRODUCTION actions. Codex stopped; Squid inactive; **NO-GO**.

**Recommended segmentation for design review only:** (1) keep the existing internal application bridge shared by the stopped Codex agent and three running data/Redis services; (2) add a distinct *internal* proxy-client bridge shared by Codex agent and Squid only; (3) keep Squid connected to a separate outbound-facing bridge, but **remove** Squid from the existing database/Redis bridge. Layer explicit Squid source/client ACL and terminal deny, constrain the proxy listener against access from the outbound bridge and host, and verify source filtering, DNS/SSRF restrictions and negative connectivity tests before activation. Static Compose membership alone does not enforce agent-only access against host root/Docker admins or prove packet-level isolation.

**Next one read-only diagnostic before changing any host file:** classify whether the live laboratory Compose source is under local Git version control, tracked, and currently clean or dirty, and whether its repository remote is within the authorized CCPC GitHub organization; report only booleans and categories, not paths, URLs, branch names, source, secrets or exact file names. This is required to avoid overwriting uncommitted server work and to choose a GitHub-first review workflow. If unmanaged, prepare a separately reviewed plan without treating the file as tracked. No approval for Docker Compose, Squid or network mutations yet.

## Step 70 — local Compose tracking classification pending correction (2026-11-19)

The operator ran a hostname-guarded, read-only check as the original nonroot operator via `runuser`. Reported `agent_running=False`, `local_git_repository_found=True`, `compose_file_inside_repository=True`, `compose_file_tracked=False`, `compose_file_modified=False`, `repository_has_tracked_changes=False`, `git_head_class=BRANCH`, `remote_class=AUTHORIZED_CCPC_REPOSITORY`.

**Critical interpretation:** The live Compose source file resides *inside* a Git working tree attached to an authorized CCPC GitHub origin, and HEAD is a branch, but **the script reported that the Compose file is not tracked; Step 71 discovered a pathspec issue that may invalidate this result**. The Step 70 `git status --porcelain=v1 --untracked-files=no` command deliberately **excluded untracked files**, so both `compose_file_modified=False` and `repository_has_tracked_changes=False` only describe tracked-path changes; they **do not prove that the working tree or the live Compose source is clean, safely versioned, or identical to GitHub**. Whether the Compose file is intentionally ignored (local secrets/runtime file) or simply untracked is not yet known. No file contents or branch names were displayed. The prior Step 69 three-network solution is a design recommendation only. **Do not run `git pull`, `git checkout`, `git reset`, `git clean`, `git add`, `docker compose up` or modify the live Compose file.** GitHub-first planning must preserve this local runtime configuration and avoid accidentally committing secrets, credentials, host-specific infrastructure details or deployment values.

**Next one read-only diagnostic:** determine whether this exact local Compose file is matched by ignore/exclude rules using `git check-ignore -q` and whether the working tree has untracked *nonignored* entries using `git ls-files --others --exclude-standard`, reporting booleans and bounded counts only; keep user-level Git invocations read-only with optional locks disabled and do not print filenames, ignore patterns, repo paths/URLs, branch names, file data or credentials. Confirm tracked status separately. If ignored, preserve as local runtime state and develop a reviewed, sanitized template/patch rather than force-adding it. If untracked and not ignored, do not add without explicit approval and a secret-exposure review. Codex and optional Squid inactive; no host/DEV/UAT/remote PROD changes; **NO-GO** remains.

## Step 71 — contradictory tracking checks exposed a pathspec bug (2026-11-19)

Operator ran the hostname-guarded read-only Git classification on `ccpcerpserver`. Output: `agent_running=False`, `git_repository_verified=True`, `compose_file_tracked=False`, `compose_file_ignored=False`, `compose_file_untracked_visible=False`, `compose_file_class=UNDETERMINED`, `repository_untracked_nonignored_count=0`, `INSPECTION_COMPLETE`.

**Important correction to Steps 70–71:** Both inspection scripts construct a Compose file path **relative to the discovered Git repository root** but execute `git -C <Compose working directory>` with that pathspec. If the Compose working directory is a subdirectory of the Git root, the pathspec is relative to the **wrong directory**. This plausibly explains both the Step 70 `compose_file_tracked=False` and the Step 71 internally contradictory state (`tracked=False`, `ignored=False`, `untracked_visible=False`). As a result, **Step 70's claim that the live Compose file is definitely untracked must be considered withdrawn until corrected.** `repository_has_tracked_changes=False` also excludes untracked files and was scoped to the working directory, so it is not a whole-repository cleanliness guarantee. The prior classification was a *tooling-path issue*, not evidence of a Docker/Git failure, secret leak or access violation. Only the safe operating principle remains unchanged: do not overwrite, stage, commit or deploy the live local Compose source until its Git classification and content security are reviewed.

**Next one read-only diagnostic:** rerun `git` commands from the resolved repository **root**, using the verified Compose source path relative to that root, under the nonroot operator with optional Git locks disabled. Print only booleans or bounded counts for repository root versus Compose working directory, tracked/ignored/untracked classifications, and overall working-tree categories. Do not output paths, filenames, patterns, branches, remotes, source contents, environment settings or credentials. No Docker, Codex, Squid, DEV/UAT or remote PROD actions. **NO-GO** unchanged.

## Step 72 — corrected root-relative Git verification confirms tracked clean Compose source (2026-11-19)

The operator ran the guarded, read-only Git inspection with `git -C` explicitly set to the **resolved repository root** and a Compose file pathspec relative to that root. Sanitized output: `agent_running=False`, `git_root_differs_from_workdir=True`, `compose_file_inside_repository=True`, `compose_file_tracked=True`, `compose_file_ignored=False`, `compose_file_untracked_visible=False`, `compose_file_class=TRACKED`, `compose_file_status_clean=True`, `INSPECTION_COMPLETE`.

**Correction/verified conclusion:** The live Compose file is **tracked in the local Git repository** and has a **clean Git file status** at inspection. The root differs from the laboratory Compose working directory, confirming the likely pathspec mistake in the earlier Steps 70–71 scripts. **Supersede all earlier statements claiming the live Compose file is untracked, intentionally excluded, or has an undetermined status.** The earlier diagnostic failure was procedural rather than a proven infrastructure change. Nevertheless, a file status of clean does **not** prove the whole repository is clean, that the currently checked-out branch matches a remote branch, or that local remote-tracking refs match current GitHub history. No `fetch` or `pull` was performed and no file modified. The reviewed three-network design remains only a recommendation. Codex stopped, Squid inactive, **NO-GO** for agent/proxy activation.

**Next single read-only check:** inspect *entire* local Git working-tree tracked/untracked change counts, HEAD branch-attached status, presence of upstream tracking ref and ahead/behind counts against the **locally cached** upstream ref (no network fetch), with output limited to booleans/numbers and category labels. Guard on expected stopped agent, verified Compose file tracked/clean, repository root and nonroot Git invocation. Do not print path names, branch names, hashes, remotes, secrets or source. Do not use `git pull`, `git checkout`, `git reset`, `git clean`, or modify host containers/networks/DEV/UAT/PRODUCTION.

## Step 73 — clean working tree, 26 commits behind cached upstream (2026-11-19)

Operator ran guarded, read-only, nonroot `git` diagnostics from the resolved repository root after verifying the stopped Codex agent and that its live Compose source is tracked/clean. Sanitized output: `agent_running=False`, `compose_file_tracked=True`, `compose_file_clean=True`, `head_attached_to_branch=True`, `staged_changed_path_count=0`, `unstaged_changed_path_count=0`, `untracked_nonignored_path_count=0`, `upstream_class=CONFIGURED`, `local_commits_ahead_of_cached_upstream=0`, `local_commits_behind_cached_upstream=26`, `INSPECTION_COMPLETE`.

**Interpretation:** No staged/unstaged changes or unignored untracked files were reported across the Git checkout. The live Compose source is tracked and clean. An upstream is configured and the checked-out branch has zero commits ahead and **26 commits behind its *locally cached* upstream reference**. This is evidence of local ref divergence, not proof that the current GitHub branch has precisely 26 newer commits; no `git fetch` or remote query occurred. Ignored files (including potential secrets/runtime data) are outside the status count. A clean worktree neither proves that the proposed remote changes are appropriate for this Compose host nor permits unreviewed pull/recreate operations. The operator reports PRODUCTION is on another server; nothing here changes that topology assumption.

**Safety decision:** **Do not pull, fetch as a prerequisite to changes without additional review, reset, checkout, clean, merge, or modify Compose**. Codex and optional Squid remain inactive; overall NO-GO holds. Before designing a GitHub-first Compose patch, verify the precise local branch/upstream relationship and *whether the 26 cached upstream commits change the live Compose source or any nearby configuration*, without exposing branch names, paths, commit SHAs, remote URLs or file contents.

**Next one read-only diagnostic:** verify the configured upstream remote is among the CCPC-authorized GitHub repos, classify whether local branch and upstream branch names correspond, and count changed tracked paths between HEAD and cached upstream (including Compose workdir and exact live Compose file) using `git diff --no-ext-diff --name-only -z`. Read with nonroot Git and optional locks disabled; print only counts, booleans and stable categories. This does not contact GitHub or update local remote-tracking refs. No Docker or ERPNext changes.

## Step 74 — cached upstream diff leaves Compose working directory unchanged (2026-11-19)

Operator ran hostname-guarded, read-only, nonroot Git comparison from repository root with source file identity/tracking/cleanliness guards. Sanitized result: `agent_running=False`, `compose_file_tracked=True`, `compose_file_clean=True`, `remote_class=CCPC_DEPLOYMENT`, `local_branch_matches_upstream_name=True`, `commits_ahead_of_cached_upstream=0`, `commits_behind_cached_upstream=26`, `total_changed_tracked_paths=4`, `compose_file_differs_from_cached_upstream=False`, `compose_workdir_changed_path_count=0`, `INSPECTION_COMPLETE`.

**Interpretation:** The checked-out local branch matches its upstream's branch name and uses the authorized CCPC deployment GitHub repository. Its HEAD is 26 commits behind the **locally cached** upstream and none ahead. A net `git diff HEAD @{upstream}` reports four changed tracked paths across the repository but **zero net file changes within the live Compose working directory**, including zero net difference for the exact tracked, clean Compose source. This result is *not* evidence that none of the 26 individual commits ever touched Compose-related files; those changes could have been reverted. Neither the actual current GitHub remote state nor the content of the four paths was inspected. There are no reported staged, unstaged, or nonignored untracked files at Step 73, but ignored runtime files still require protection. No `git fetch`, pull, rebase, branch switching, container start, network edits or protected ERPNext operations occurred.

**Safety decision:** Do not pull or change the host. The existing laboratory Compose config is tracked/clean, but remote update relevance and server-drift controls must still be reviewed before any deployment. Codex remains stopped and optional Squid inactive; overall **NO-GO** for activation.

**Next single read-only check:** verify that the local checked-out branch is a known authorized checkpoint/review branch **without revealing the actual branch name**, and count, using `git rev-list --count HEAD..@{upstream} -- <exact Compose path>` and the Compose working-directory path, how many of the 26 cached upstream commits touched these areas—even if reverted. Print only counts/branch category and current stopped-agent safeguards. Do not display paths, URLs, hashes, branch names, source text, remote output or secrets. This classifies *history* separately from Step 74's *net tree difference*. Keep all changes in reviewed GitHub branches and avoid touching host Compose until explicit approval and safety checks.

## Step 75 — 26 cached upstream commits do not touch laboratory Compose area (2026-11-19)

Operator ran the guarded read-only `git rev-list` history check from the correctly discovered Git root, with the nonroot Git user and stopped Codex agent guard. Sanitized result: `agent_running=False`, `compose_file_tracked=True`, `compose_file_clean=True`, `local_branch_class=OTHER_BRANCH`, `cached_upstream_commit_count=26`, `commits_touching_compose_file=0`, `commits_touching_compose_workdir=0`, `INSPECTION_COMPLETE`.

**Interpretation:** None of the 26 commits in `HEAD..@{upstream}` in the **cached local upstream** history touched the exact tracked live Compose file or any tracked path under the laboratory working directory. Combined with Step 74 (zero net tree differences in that directory), this reduces the risk that the *cached 26* are relevant to that local runtime configuration. The check did **not** fetch current GitHub changes, and a cached upstream reference is not proof of the latest remote. The script categorized the checked-out local branch as `OTHER_BRANCH`, meaning only that it was not one of the **two hardcoded comparison names**; it does *not* imply an unauthorized or suspicious branch. Do not invent branch identity or assume it matches the audit-review branch. The agent remains stopped; Squid remains inactive. No repo, host, DEV/UAT or remote PRODUCTION changes were made. Security state remains **NO-GO** pending proxy egress security, image trust, CLI sandbox/auth and runtime tests.

**Next read-only diagnostic:** verify the actual local branch class against current CCPC development branch conventions **without exposing raw branch names, paths, commit SHAs, remote URLs or credentials**, and use existing configured upstream metadata to classify whether a host-local review/work branch is in use. Do not fetch/pull on the server. In parallel, examine GitHub's currently available checkpoint/review branches through connected GitHub tools to choose the appropriate GitHub-first development base. No Compose changes until independently reviewed and explicitly approved.

## Step 76 — local review branch with matching upstream name (2026-11-19)

The operator ran a hostname-guarded, read-only Git branch classifier on the local deployment checkout, after checking that the Codex agent is stopped and the laboratory Compose file is tracked and clean. Sanitized output: `agent_running=False`, `compose_file_tracked_and_clean=True`, `branch_category=REVIEW`, `branch_matches_selected_github_list=False`, `upstream_matches_local_branch_name=True`, `INSPECTION_COMPLETE`.

**Interpretation:** The server is on a local `review/` branch with a configured upstream branch bearing the same branch name. The particular local branch is *not among the seven hardcoded branch names* in Step 76's limited shortlist; this **does not** demonstrate that it is unauthorized, stale, absent from GitHub or invalid. The exact local branch name was intentionally not printed, so no conclusive correspondence to the current GitHub branch inventory can yet be made. Steps 72–75 confirmed tracked/clean live Compose source, no staged/unstaged/nonignored untracked work, and 26 commits behind a *cached* upstream with no Compose area touched among those 26. GitHub's present branch inventory is separate from that cached local ref. No pulls, fetches, branch switches, Docker/Compose operations or DEV/UAT/remote PRODUCTION changes occurred. Agent stopped, Squid inactive, **NO-GO** remains.

**Next safe path:** Avoid repeatedly asserting a branch is unknown solely because of incomplete hardcoded lists. Confirm whether the local review branch is included in a more complete current GitHub review-branch listing using **only a boolean/status classification**, without printing raw names or paths. Do not pull, fetch, switch branches or modify the host to answer this. The reviewed three-network proxy segmentation remains a proposed architecture, not an implementation authorization.

## Step 77 — local review branch present in current GitHub inventory (2026-11-19)

After the connected GitHub branch search returned a complete current listing of 15 `review/` branches (two pages; final cursor null), the operator ran a hostname-guarded, read-only local Git comparison against that branch-name set. Sanitized output: `agent_running=False`, `compose_file_tracked_and_clean=True`, `local_branch_category=REVIEW`, `upstream_branch_name_matches=True`, `github_review_branches_compared=15`, `local_branch_in_current_github_list=True`, `INSPECTION_COMPLETE`.

**Interpretation:** The local server checkout is on a `review/` branch present in the GitHub deployment repository's branch inventory, and its cached upstream uses the same branch name. Step 75's `OTHER_BRANCH` was only a two-name shortlist miss; Step 76's `branch_matches_selected_github_list=False` was a seven-name shortlist miss. Neither was evidence of an unauthorized or deleted branch. The exact matched branch has **not** been identified in output; 15 candidates remain. The local Compose file is tracked and clean; Step 73 found no tracked/unignored working-tree changes. The 26 commits behind upstream and zero Compose history touches in Steps 74–75 apply only to the **locally cached** upstream reference, not the newest GitHub head. No Git fetch/pull/branch switch or Docker, Codex, Squid, DEV/UAT or remote PRODUCTION changes. Codex and optional Squid remain **NO-GO** for activation pending security gates.

**Next one read-only diagnostic:** identify which of the 15 currently known GitHub review branches matches the host's local checkout using a **stable numeric list position only**, while verifying the agent is stopped and the live Compose source is tracked and clean. Do not print raw branch names, commit SHAs, repository paths, remote URLs, host IPs, secrets or file contents. This permits the connected GitHub tools to inspect the correct branch and start a GitHub-first **review-only** segmentation proposal without touching the host. The branch inventory is a snapshot, so re-verify before any future GitHub write.

## Step 78 — local review-branch slot matched; GitHub sources inspected (2026-11-19)

The operator ran guarded, read-only branch identification with a complete 15-name review branch list. Sanitized output: `agent_running=False`, `compose_file_tracked_and_clean=True`, `github_branch_match=True`, `review_branch_slot=15`, `review_branch_count=15`, `INSPECTION_COMPLETE`. The numeric slot resolves to **the existing PR33 development-acceptance review branch** in the connected GitHub repository (rather than this dedicated Codex security audit documentation branch). This disambiguates Steps 75–77; the user-facing host transcript did not reveal a branch name. No local Git fetch, pull, branch switch or Compose modification was made.

**Direct GitHub verification:** On the matched review branch, connected GitHub `fetch_file` successfully read `codex-dev-agent/compose.yaml`, `codex-dev-agent/proxy/squid.conf`, `codex-dev-agent/check_compose.py`, `codex-dev-agent/tests/test_safety_policy.py` and `codex-dev-agent/README.md`. This is verified *GitHub review-branch source*, **not independently compared byte-for-byte with the host's current tracked Compose file or host-local Squid config**. The GitHub Compose source declares the agent and DB/Redis on `lab`, optional proxy on `lab` + `outgoing`, proxy profile `online`, no static IPs, read-only proxy config mount, `ubuntu/squid:latest` mutable tag with `pull_policy: never`, and no explicit proxy user. Squid config uses an all-interface `http_port 3128`, methods/port/destination deny and domain allowlist but no source-address ACL. These independently corroborate the earlier host-source classifications.

**Critical source-change coupling:** Current `check_compose.py` enforces exactly `{'lab'}` for nonproxy services and exactly `{'lab','outgoing'}` for the optional proxy, and its unit-test fixtures reproduce this two-network layout. Any three-network proposal (agent on application lab + new internal proxy-client bridge; proxy on proxy-client bridge + outgoing, with no proxy DB/Redis membership) **must revise Compose, the fail-closed validator, the source-only test fixtures/negative cases, and relevant README/security documentation as one reviewed GitHub change**; editing Compose alone would fail the current safety check. Squid listener binding and source ACL must be designed with stable addressing and independent outbound-bridge/host reachability controls. The proxy image provenance/runtime user, DNS and egress bypass rules remain unresolved.

**Decision and next phase:** Do **not** modify the matched existing development-acceptance review branch or its host checkout simply to test proxy design; prepare a distinct, appropriately based **GitHub review-only change plan** before authorization to implement. Confirm the exact matching GitHub Compose file path on the host without disclosing it if byte-equivalence is needed; a clean host file against its own local commit does not prove equivalence with current GitHub contents. Do not pull the 26 cached-upstream commits or touch ignored host runtime files. Keep all Codex/proxy activation, Docker network changes, image pulling, firewall changes, DEV/UAT and separate PRODUCTION operations on hold. **NO-GO** remains until security gates and controlled validation pass.

## Step 79 — local live source equals GitHub review branch (2026-11-19)

The operator ran the hostname-guarded, read-only equivalence check using root-relative tracked file paths and Git blob SHA-1 over local file bytes, comparing against the blob IDs directly obtained by connected GitHub `fetch_file` for the matched PR33 review branch. The check verified the Codex agent remains stopped. Sanitized output: `agent_running=False`, `source_files_checked=4`, `files_tracked_and_clean=True`, `compose_matches_github=True`, `squid_matches_github=True`, `validator_matches_github=True`, `tests_matches_github=True`, `all_files_match_github=True`, `INSPECTION_COMPLETE`.

**Interpretation:** The live host's tracked and clean Compose configuration, Squid policy, fail-closed Compose validator and static security test suite match the reviewed source files in `ccpcerp/ccpc-frappe-deployment` on the identified PR33 acceptance review branch (at the observed snapshot). These are **file-content identity checks**, not host runtime security tests, secret/access reviews, proof of remote production topology, or an assertion that the *whole local Git checkout* matches current GitHub HEAD. The unchanged Compose service mapping remains agent+DB/Redis on an internal lab bridge, optional Squid on lab+outgoing, with Squid's wildcard listener and no source ACL; none of the NO-GO gates were lifted. No host writes, Docker actions, Git pull/fetch, branch changes, network/agent/proxy starts or DEV/UAT/remote PRODUCTION operations occurred.

### GitHub-first implementation plan — proposal only

1. Prepare an isolated GitHub **code review branch based on the verified PR33 security-source baseline**, without altering the host checkout or existing acceptance/audit branches. Confirm branch history and expected files just before code changes.
2. Make the Compose **segmentation proposal** explicit: preserve the existing agent–MariaDB–Redis internal application bridge; introduce an isolated internal agent+proxy client bridge; remove proxy from the application bridge; retain a separate outbound bridge accessible only to the proxy, with no unnecessary published ports. Verify network alias discovery from both client networks.
3. Harden Squid default-deny source and destination controls, address **listener reachability from its outgoing-facing interface and Docker host**, and review DNS/special-use destinations, permitted domains, image digest/trust/runtime UID, capabilities and process memory controls. Do not treat a Squid `src` ACL or Compose membership alone as protection against container-root, Docker-admin or host-firewall bypass. Prefer a reviewed, reproducible method to configure an interface-bound listener or equivalent stronger enforced ingress policy; this may require stable proxy-client IPAM or host firewall changes and so must not be activated unreviewed.
4. Update `check_compose.py`, `tests/test_safety_policy.py`, README and deployment/security docs in lockstep; add negative checks for forbidden proxy–DB/Redis shared networks, agent outward network membership, missing source ACL, wildcard listener exposure and unexpected proxy image/user. Static tests remain mocked/source-only, not integration evidence.
5. Review CI/unit tests and relevant risks in GitHub, verify commit and branch; **no host deployment** until distinct user authorization plus recoverability/rollback and DEVELOPMENT validation plan. Codex agent and Squid stay stopped/inactive until all separate security gates pass; PRODUCTION requires its own explicit approval and is not in scope.

**Next action:** seek explicit approval before changing even review-branch code. Documentation-only audit changes are recorded here; do not run more repetitive host inventory commands merely to infer source already verified in GitHub.

## Step 80 — GitHub-only Codex proxy hardening implementation and draft PR (2026-11-19)

The operator approved creating a **new dedicated GitHub review branch and implementing proposed security changes for review and testing**. This does **not** authorize any host-side Docker/Compose/network changes, agent/proxy launch, DEVELOPMENT deployment, production deployment, or paid autonomous Codex reporting.

**Confirmed GitHub implementation:** review branch `review/codex-proxy-network-hardening-2026-11-19` was created from the independently verified PR33 development-acceptance review baseline (`review/pr33-dev-acceptance-2026-11-16`). Draft **PR #39** is open against that base: https://github.com/ccpcerp/ccpc-frappe-deployment/pull/39. Connected GitHub comparison verified **8 commits ahead, 0 behind**, exactly **six intended changed paths**: `codex-dev-agent/compose.yaml`, `codex-dev-agent/proxy/squid.conf`, `codex-dev-agent/check_compose.py`, `codex-dev-agent/tests/test_safety_policy.py`, `codex-dev-agent/README.md`, and `.github/workflows/codex-lab-static-review.yml`. Latest implementation commit at review snapshot: `dbfba56b9d48cf4e7850a32a53b9890b9e8ed034`. The prior Step 79 host/GitHub source equivalence applies to the **unchanged PR33 base**, not to this new review branch's proposed code.

**Code changes proposed, NOT deployed:** preserve the existing internal `lab` network for agent, MariaDB and both Redis services; create a separate internal non-attachable IPv4-only `proxy_clients` bridge linking only the agent and optional Squid; remove Squid from `lab`; keep the Squid-only `outgoing` bridge and no published proxy ports. Static client IPs are assigned within a **provisional** `172.30.250.0/29` reservation (agent `.2`, Squid `.3`) solely to support Squid binding its `http_port` to the client-facing IP and an exact agent `src` ACL; the host's actual routes/IPAM overlap have NOT been checked for this new range. Squid retains HTTPS CONNECT/443 and domain/destination restrictions, and adds special-use destination IPv4 ranges. The strict Compose + Squid validator and negative source-only tests were updated together to reject unexpected networks, public listeners, missing source ACL, extra allow rules, unapproved commands, IPC/namespace overrides, widened security options and other changes. User-facing README includes explicit hold/rollback prerequisites. A GitHub-hosted Python stdlib-only PR test workflow was added; it does not use Docker, Codex, OpenAI API keys, or production systems.

**CI verification: not passed and NOT executed.** Two PR-triggered GitHub Actions runs (IDs `44496774014` and `44497509466`) both report `conclusion=failure`, while the connected jobs API showed **zero recorded job steps and no runner**; the job log fetch returned unavailable/404, so no Python assertion result or source test pass can be claimed. This indicates an execution/runner-side blocker *at least insofar as the visible metadata shows*, rather than a demonstrated unit-test assertion failure. It must be investigated or the tests must be executed through an authorized source-only runner before review acceptance. We did verify GitHub commit contents, the base/branch diff, and that the Squid prohibited-address/approved-domain lists match the fail-closed validator constants (20 blocked CIDRs and 10 allowed suffixes). Those static content checks are **not equivalent** to Python unit tests, `docker compose config`, `squid -k parse`, firewall tests or a penetration test.

**Remains NO-GO:** Never run `docker compose up` from PR #39 until a separately approved deployment plan (backups, rollback and no production touch) verifies (1) proposed /29 not colliding with Docker/host/LAN routes; (2) host INPUT and forwarding isolation rules cover **both** agent-attached internal bridges before either bridge is enabled; (3) outgoing Squid listener/host access negative tests; (4) signed/vetted immutable image and proven runtime nonroot Squid UID (current `ubuntu/squid:latest` remains unpinned/unverified); (5) DNS rebinding, address filtering, broad allowlisted domains and direct-socket egress; (6) real Squid parser/runtime, Docker Compose version and resource containment; (7) Codex sandbox, approvals and authentication/secret isolation. All work remains GitHub review-only. The existing lab agent remains stopped and the optional Squid container was never launched. PRODUCTION is on a separate server by operator report and must not be touched.

**Next safe milestone:** Have a trusted source-only test runner execute `python3 -m unittest discover -s codex-dev-agent/tests -p 'test_*.py' -v` against the proposed branch without loading host secrets or starting Docker. Review/fix any failures and update PR #39. Independently resolve the CI runner failure, verify source preflight on an isolated workstation (not the host), and complete review of subnet/host firewall/runtime isolation before asking for a specific DEVELOPMENT-only apply approval. Do not merge PR #39 or pull it to the server based solely on the current static evidence.

## Step 81 — review-only security strengthening and CI recheck (2026-11-19)

Following the operator's approval to continue the approved **GitHub-review-only** work, connected GitHub tools reverified that draft PR #39 was open against `review/pr33-dev-acceptance-2026-11-16` and six intended source/documentation/CI paths were changed. On branch `review/codex-proxy-network-hardening-2026-11-19`, the further verified code commits were:

- `1c7f173955c6999edfaecdf1bac6b19e1f95000e`: require Squid policy validation even when a Python caller does not explicitly pass the policy; reject unreviewed service network attributes, automatic agent or proxy restarts, lowercase `no_proxy` overrides, and unsafe IPv6 settings on the outgoing bridge.
- `0b1c2916935a2a51021ec9f257f2d5be74eab8d5`: explicitly declare `enable_ipv6: false` for the proposed outbound bridge in the review-only Compose source.
- `ecc934a300e4854c941eee00ff880aab1fa17a5b`: add regression cases for these new fail-closed requirements; **51 declared `test_...` methods** now exist in the source-only test suite.
- `714cd3baad896c78eae3e7ac544fd834f585f618`: update the lab README with the current test count and unresolved GitHub Actions runner failure.

Connected GitHub source fetches verified each relevant post-update blob. A separate in-conversation, JavaScript-executed **22-case text/structure consistency audit** across current GitHub Compose/Squid/validator/tests/README sources passed all 22 conditions, including service membership, bridge settings, exact IP/resolver/client ACL constants, ordered `http_access` denies, allowed-domain and prohibited-IP constants, and cross-file coherence. **This was NOT execution of the Python unit tests**, a Docker Compose config check, or Squid binary syntax parsing. Official Squid documentation corroborates that `http_port` accepts an IP:port and `src` ACLs match client source addresses; it does not verify runtime isolation: https://www.squid-cache.org/Doc/config/http_port/ and https://wiki.squid-cache.org/SquidFaq/SquidAcl.

**CI still blocked:** At latest implementation commit `ecc934a300e4854c941eee00ff880aab1fa17a5b`, GitHub Actions run `44540780434` reported `conclusion=failure`, but `fetch_workflow_run_jobs` returned the policy-regression job with **zero steps and no runner name**. Earlier runs had identical metadata; no actual Python test error or passing result was available. Do not misreport tests as passing or attribute a precise billing/runner/root cause without evidence. The draft PR description was updated to record the blocker and 22-case consistency audit; PR remains DRAFT, not merged.

**Next held gates:** (1) acquire a successful trusted Python-only execution of all 51 source-only tests, without touching real site files, credentials or Docker; (2) verify the provisional proxy-client /29 against actual host Docker IPAM, host address and non-default route allocations using a guarded **read-only** operator command; (3) review images/digests/nonroot Squid runtime, memory/PID caps, IPv6 and DNS/SSRF behavior, combined firewall rules for both agent-attached bridges, negative integration tests, and Codex sandbox/auth controls. No Git pull, container start, proxy activation, image download, network modification, main DEVELOPMENT operations, UAT or separate PRODUCTION access occurred. Overall **NO-GO for activation/deployment**.

## Step 82 — proposed proxy-client /29 passes local host overlap check (2026-11-19)

The operator ran the guarded **read-only** local subnet/IPAM inspection on `ccpcerpserver` while the Codex agent remained stopped. Sanitized output: `agent_running=False`, `docker_networks_checked=7`, `candidate_docker_subnet_overlaps=0`, `candidate_host_route_overlaps=0`, `candidate_interface_network_overlaps=0`, `candidate_local_conflict_free=True`, `remote_network_overlap_verified=False`, `INSPECTION_COMPLETE`. The reviewed candidate was the **proposed, currently undeployed** `172.30.250.0/29` internal `proxy_clients` bridge in draft PR #39.

**Interpretation and limits:** Among the Docker IPAM subnet declarations, host IPv4 address networks and non-default IPv4 routes that the script inspected at that instant, no overlap was detected. This supports retaining the candidate /29 for a future **review-only configuration proposal**, but is not a network allocation, an absence-of-conflict guarantee for external/VPN/remote routes (especially behind a default route), or proof of host-gateway/inter-bridge isolation. Recheck immediately before any eventual approval to instantiate the network; don't assume these findings remain true after routing/Docker changes. The agent was stopped. The script made no network changes or probes; the operator supplied the output, not direct ChatGPT host inspection.

**Firewall coupling:** The existing reviewed `scripts/security/ccpc_codex_dev_lab_firewall.sh` from the PR33 source is hard-coded to the **existing lab bridge** for host `INPUT` and `DOCKER-USER` cross-bridge rules and does **not** cover the proposed additional agent-attached `proxy_clients` bridge. Never create/attach/start the agent on that new bridge without a separately reviewed **pre-enforced firewall policy** for the second bridge, appropriate protected host gateways, rollback/persistence checks and negative tests. Do not presume the default `internal: true` setting blocks host SSH or Docker gateway access; the earlier gateway-connectivity failure shows otherwise. The proxy's `outgoing` bridge also requires independently enforced source- and destination-egress boundaries.

**Next safe operator inspection:** Use read-only Docker network metadata and `iptables -S` inventory on the host to check current effective lab-bridge host/forward rule presence and ordering, without revealing subnet/bridge identifiers, credentials or raw firewall entries and without calling any `iptables` mutating action. Do not enable the agent/proxy, touch DEVELOPMENT/UAT, modify production, or pull/recreate containers. Draft PR #39 remains DRAFT with the 51 Python tests not verified due to GitHub Actions failures before runner steps; the 22 source-consistency checks are not substitutes for tests. **NO-GO for activation remains.**

## Step 83 — expected host INPUT DROP not detected (2026-11-19)

Operator ran the hostname-guarded **read-only** effective `iptables -S` audit, with stopped-agent and known Docker lab bridge identity checks. Sanitized output: `agent_running=False`, `legacy_lab_host_drop_present=False`, `legacy_lab_outbound_drop_present=True`, `legacy_lab_inbound_drop_present=True`, `legacy_lab_host_drop_first_rule=False`, `legacy_lab_forward_drops_first_two=True`, `forward_first_jump_docker_user=True`, `proposed_proxy_client_network_exists=False`, `INSPECTION_COMPLETE`.

**Interpretation:** Both exact expected `DOCKER-USER` cross-bridge DROP rules for the original lab are present and ordered near the top, and the host `FORWARD` chain first jumps to `DOCKER-USER`. However, the **exact expected `INPUT` rule prohibiting originating-from-lab traffic to host** is absent or not textually identical to the expected `iptables -S` representation, and it is not the first INPUT rule. The check does **not** demonstrate another firewall rule is equivalent or that host SSH is reachable; it establishes an **unresolved protection gap**. This must be treated as a blocker because the agent formerly connected to the Docker bridge gateway SSH port before host-firewall hardening. The new `proxy_clients` bridge has not been created; the agent is still stopped. The operator did not modify firewall, Docker, Git or any DEVELOPMENT/PRODUCTION service.

**GitHub source check:** Connected GitHub `fetch_file` of `scripts/security/ccpc_codex_dev_lab_firewall.sh` on the PR33 baseline confirmed the **expected `host_rule=(-i "$BRIDGE" -s "$SUBNET" ... -j DROP)` is present in source** and is checked by `has_host`. The host inspection is not equivalent to verifying that the original script was applied, remains persistent, or that a semantically equivalent alternative exists. The existing script covers only the old lab bridge, not the proposed second agent-attached bridge.

**Safety decision:** **NO-GO** remains for agent startup, Squid/online profile, and second-bridge creation. Do **not** apply the old script, install new rules, reboot, reconfigure firewalls, pull/checkout, merge/deploy PR #39, or run negative probes without an independently reviewed plan and explicit host-operation approval. A temporary local INPUT rule may have expired on reboot or been replaced; neither cause is established by this output.

**Next one read-only diagnostic:** On the host, check the `INPUT` chain's **policy class, count and placement of DROP/REJECT rules**, whether any lab-interface/source-specific or comment-tagged host-drop candidate exists, and whether the exact rule appears with different formatting; print **only aggregate numbers and booleans**, not raw firewall rules, interface names, IPs, paths, service ports, credentials or network identifiers. Verify stopped-agent identity and existing lab metadata first. Do not mutate the rules. Use the result to decide whether the protection gap is merely exact-match/ordering drift or a clearly absent host INPUT policy. Even if an equivalent rule is discovered, keep the activation gate closed pending controlled negative reachability tests and plan for securing the new bridge *before it exists*.

## Step 84 — host INPUT has candidate laboratory DROP; Step 83 textual mismatch (2026-11-20)

The operator executed the hostname-guarded, read-only `INPUT` policy diagnostic after Step 83 reported that the expected exact rule was not found. Sanitized output: `agent_running=False`, `input_default_policy=ACCEPT`, `input_rule_count=1`, `input_drop_reject_rule_count=1`, `input_lab_interface_drop_candidates=1`, `input_lab_subnet_drop_candidates=1`, `input_exact_interface_subnet_candidates=1`, `input_expected_comment_count=1`, `input_custom_chain_jump_count=0`, `host_input_protection_proven=False`, `INSPECTION_COMPLETE`.

**Correction to Step 83:** The single `INPUT` rule is a DROP/REJECT rule (and the earlier diagnostic establishes it has the expected lab interface **and** exact lab subnet). It also has the project's expected `ccpc-codex-deny-host` comment. Since there is only **one** `INPUT` rule, its existence reconciles the earlier `legacy_lab_host_drop_present=False` result as an **exact token-list/formatting mismatch**, rather than proof that no candidate host rule exists. Step 83's wording “expected host INPUT DROP not detected” is true only of its strict textual comparison; it should **not** be read as “host INPUT protection is absent.” Because Step 84 counts the expected-comment match separately from the interface/source pair, strict code-level correlation remains worth checking, although there is only one INPUT rule in this observation. The `INPUT` default policy is ACCEPT; an effective rule and host input semantics need confirmation. This evidence does not prove full isolation, reboot persistence or negative network reachability.

**Security status:** Two `DOCKER-USER` forwarding DROPs were present and ordered correctly in Step 83, which also verified `FORWARD` jumps first to `DOCKER-USER`; the proposed `proxy_clients` network does not exist. Agent remains stopped and optional Squid inactive. Keep the separate second-bridge host/forward isolation and egress controls as **NO-GO** gates. Do not alter the active firewall to “fix” a rule that might already be present.

**Next single read-only confirmation:** dynamically discover the existing lab network metadata; keep exact project and stopped-agent guards. Use `iptables -C INPUT -i <bridge> -s <subnet> -m comment --comment ccpc-codex-deny-host -j DROP` with the programmatically derived bridge and subnet, without printing them. `iptables -C` checks rule existence and **does not insert/delete** rules; report only boolean match, INPUT count, first-rule/ordering correlation, and `INSPECTION_COMPLETE`. If the exact `-C` check fails, inspect normalized semantics further, still without applying changes or printing sensitive rule contents. Additional controlled negative tests are required after separate authorization before agent startup.

## Step 85 — exact expected host INPUT rule verified (2026-11-20)

Operator ran the hostname-guarded, read-only `iptables -C INPUT` check using dynamically inspected original lab bridge metadata. Sanitized stdout: `agent_running=False`, `lab_network_identity_verified=True`, `expected_input_drop_rule_exists=True`, `host_reachability_test_performed=False`, `new_proxy_network_created=False`, `INSPECTION_COMPLETE`.

**Correction and resolution of Steps 83–84:** The exact expected `INPUT` DROP for the original `ccpc_codex_dev_agent_lab` bridge, its original subnet, and project comment `ccpc-codex-deny-host` was proven to exist using the kernel-facing `iptables -C` rule-existence check; Step 83's `False` result was a **textual representation/token-order comparison error**, not evidence of absent host protection. Step 84 found the one candidate rule, and Step 85 confirmed its exact semantics using `iptables -C`. Step 83 also found the original lab's two expected `DOCKER-USER` cross-bridge DROPs and a first FORWARD jump to DOCKER-USER, so the three scoped original-lab rules are accounted for at this snapshot. **Do not add a duplicate host INPUT rule.** Rule existence by itself does not prove live connectivity blocking or persistence across reboot/firewall reload.

**Scope and decision:** The proposed second internal `proxy_clients` bridge **does not exist** and was not created. The old bridge's firewall rules do not automatically cover a second agent-attached bridge. Codex agent remains stopped, Squid/online profile inactive, host unchanged; no Git fetch/pull/checkout, Docker/network/firewall mutation, host probing, DEVELOPMENT/PRODUCTION operations. Continue GitHub-only review for pre-enforced, rollback-safe isolation for the second bridge; the proposed `172.30.250.0/29` address range passed only local IPAM/route overlap inspection in Step 82, not remote-route verification. Draft PR #39 remains unmerged, CI Python tests not executed/verified, and actual host/Squid/DNS/CLI sandbox isolation remains **NO-GO**.

**Next safe step:** Before any second-bridge creation, inspect the *current* proposed network definition and host bridge-interface naming preconditions read-only; design a deterministic, uniquely reserved bridge interface and scoped host `INPUT`/`DOCKER-USER` policy that can be installed and verified **before** creating or attaching the agent to the new bridge. Review failure-path rollback, bridge-name collisions, route overlap, ordering, persistence and any interaction with Docker forwarding. Do not issue any `apply` or `docker compose up` without separate approval of the exact host operation.

## Step 86 — proposed deterministic bridge name available; review-only firewall plan committed (2026-11-20)

The operator ran the hostname-guarded, read-only proposed proxy-client bridge name precheck on `ccpcerpserver`. Sanitized result: `agent_running=False`, `existing_lab_identity_verified=True`, `candidate_name_length_valid=True`, `candidate_interface_exists=False`, `candidate_docker_network_exists=False`, `candidate_bridge_option_in_use=False`, `candidate_filter_rule_references=0`, `candidate_nat_rule_references=0`, `candidate_name_available=True`, `INSPECTION_COMPLETE`. The proposal was interface name `br-ccpc-cdxpx` on the not-yet-created `proxy_clients` bridge. This is **snapshot availability**, not permanent reservation or proof of remote-route safety; Step 82 separately found no *local* Docker/host-subnet overlap for the proposed `172.30.250.0/29`.

**Verified GitHub-only implementation on draft PR #39:** On `review/codex-proxy-network-hardening-2026-11-19`, the proposed `codex-dev-agent/compose.yaml` gained a pinned `com.docker.network.bridge.name: br-ccpc-cdxpx` driver option **only on the new internal client bridge**; `check_compose.py` now rejects any drift to that bridge name and unexpected modifications to the existing lab/outgoing bridge driver options; `tests/test_safety_policy.py` gained regression tests for wrong/missing/expanded bridge names and existing-lab bridge overrides. A new script `scripts/security/ccpc_codex_proxy_bridge_preflight.py` was added as **strictly read-only**: only `plan` and `verify` modes; its guarded queries check stopped agent, original-lab iptables protection, FORWARD ordering, candidate bridge/network absence, local IPAM/route conflicts, proposed new-rule existence/order and foreign filter/NAT references. It defines but **never installs** a future new-bridge unconditional `INPUT DROP` plus two `DOCKER-USER` cross-bridge DROP rule specs. Its three rules must be independently reviewed, installed and verified **before creating the new network**, and separately authorized on the host; they do not yet exist. It reports only boolean and counts, not raw sensitive host network data. Source-only negative tests for the new rule specifications and rejection of `apply`/`rollback` were added; the relative test helper path was corrected in commit `30cce3bde0771a2726954cc5e488af0e6f73c3c7`.

The lab README and CI workflow path filter were updated in the same review branch. Current connected-GitHub source inspection confirms **60 declared Python source-only unit-test methods**, but **does not establish they executed or passed**; GitHub Actions previously reported jobs failing with zero runner steps. No Docker network, firewall, container, image, secret, Git checkout, DEV/UAT or separate PRODUCTION changes occurred. Original lab firewall present by Step 85. The new proposed bridge remains absent, Squid inactive and agent stopped. Pre-enforcement readiness and negative runtime isolation tests remain **NO-GO**.

**Branch caveat:** At latest GitHub comparison, draft PR #39 had **21 commits ahead of, and 1 commit behind**, the currently updated `review/pr33-dev-acceptance-2026-11-16` base, modifying exactly seven intended Compose/proxy/validator/tests/README/CI/firewall-preflight paths. The base's one new commit affects a separate handoff document, not the Codex source paths; do not force-rebase or overwrite the working host review branch merely to make these counts zero.

**Next safe diagnostic:** inspect how the host persists local `iptables-nft` rules across reboot and whether Docker startup ordering would load scoped new bridge protection **before** any future agent autostart; use a guard-checked **read-only service/status and persistence-file existence inventory**, not raw contents, no package installation or firewall commands that modify rules. Plan any separately authorized firewall application with a second SSH session and verified rollback, and never treat persistent service presence alone as proof of rule persistence.

## Step 87 — firewall service inventory does not prove reboot persistence (2026-11-20)

The operator ran a guarded **read-only** firewall persistence service/file inventory on `ccpcerpserver`; the expected original-lab `iptables -C INPUT` DROP was reverified with stopped-agent guard. Sanitized stdout: `agent_running=False`, `original_lab_host_drop_verified=True`, `netfilter_persistent_enabled=False`, `netfilter_persistent_active=False`, `nftables_enabled=False`, `nftables_active=False`, `ufw_enabled=True`, `ufw_active=True`, `firewalld_enabled=False`, `firewalld_active=False`, `iptables_rules_v4_nonempty=False`, `nftables_config_nonempty=True`, `possible_custom_firewall_units=0`, `firewall_reboot_persistence_verified=False`, `startup_order_verified=False`, `INSPECTION_COMPLETE`.

**Interpretation:** UFW is enabled and active, but UFW service state alone is **not proof** that the custom original-lab `INPUT` and `DOCKER-USER` rules are represented in UFW-managed persistent files or restored at boot; direct `iptables` inserts can disappear on reload/restart. `netfilter-persistent` and the separate `nftables.service` are both disabled/inactive and the standard saved IPv4 `/etc/iptables/rules.v4` file is not known to contain rules (empty or absent). A nonempty `/etc/nftables.conf` does not prove that configuration is loaded or carries the project rules, particularly while its service is inactive. The simple name-filtered systemd unit count does not rule out a differently named persistence mechanism, startup script or UFW `before.rules`/custom init hook. These observations **do not establish that the firewall will disappear after reboot**, nor that it will persist. No reload/reboot/service mutation was performed.

**Verified source limitation:** The existing GitHub original-lab firewall script (`scripts/security/ccpc_codex_dev_lab_firewall.sh` on PR33 acceptance review source) explicitly labels its `iptables` rules **ephemeral/not persistent across reboot or reload**. This is design documentation, not evidence of the host's current persistence arrangement. The new three-network draft PR #39 remains GitHub-only; proposed bridge has not been created; agent stopped and Squid inactive.

**Next safe diagnostic:** Query UFW-managed persistent IPv4 rule files and approved custom startup files on the host for the three precise CCPC original-lab comment tags, outputting only booleans/counts (no raw rules, file contents, IPs, interfaces, keys, credentials or paths). Confirm the original lab and agent identity, the currently installed INPUT host DROP, and UFW service state without modifying anything. A match only indicates a tag exists in a persistent *file*, not correctness, loaded ordering, or verified reboot survival; no tag indicates the common UFW files examined do not explicitly contain them, not proof no other persistence exists.

**Decision:** Firewall persistence and pre-start rule ordering remain unverified and **NO-GO** for Codex/Squid activation or second-bridge creation. Do not reboot, `ufw reload`, `iptables-restore`, or install a persistence tool simply to test this. Retain ability to review and prepare a safe, operator-approved exact host action and rollback separately; no DEVELOPMENT/PRODUCTION operations.

## Step 88 — common UFW persistence files lack lab rule tags (2026-11-20)

The operator executed the guarded **read-only** saved UFW rules and hook inspection on `ccpcerpserver`, verifying all three original laboratory rules remain installed via exact `iptables -C` calls and UFW is active. Sanitized output: `agent_running=False`, `original_lab_three_rules_installed=True`, `ufw_service_active=True`, `ufw_rule_files_checked=3`, `ufw_startup_hooks_checked=2`, `ufw_saved_host_tag_present=False`, `ufw_hook_host_tag_present=False`, `ufw_saved_outbound_tag_present=False`, `ufw_hook_outbound_tag_present=False`, `ufw_saved_inbound_tag_present=False`, `ufw_hook_inbound_tag_present=False`, `nftables_config_checked=True`, `nftables_config_has_ccpc_tags=False`, `reboot_persistence_verified=False`, `INSPECTION_COMPLETE`.

**Interpretation:** All three currently active original-lab `INPUT`/`DOCKER-USER` DROP rules are present, so there is **no demonstrated immediate missing-rule condition** at this checkpoint. Neither the three inspected UFW IPv4 saved-rule files nor two UFW startup hook files contains **any of the three exact project comment tags**; the inspected nonempty `/etc/nftables.conf` also lacks them. Therefore those exact tags are **not visibly recorded in these common persistence sources**. This is not equivalent to proving there is no persistence: an alternate systemd unit, timer, root crontab, rc.local, other startup integration or dynamic restoration script may install rules without embedding the tags directly in the scanned files. Nor does a tag's presence alone guarantee executable semantics, order or reboot restoration. The GitHub original-lab firewall script explicitly describes its directly inserted iptables rules as ephemeral if no separate persistence mechanism exists.

**Security decision:** Treat **reboot/reload persistence as unverified and a NO-GO activation gate**. Do **not** reboot, reload UFW, install `netfilter-persistent`, edit systemd/cron, or alter firewall/containers merely to test. The Codex agent remains stopped and proposed Squid/client bridge has not been created. Separately, the future new bridge requires reliable **pre-enforced** host `INPUT` and routed `DOCKER-USER` rules, persistence ordering before future agent autostart, and controlled negative tests even if original-lab persistence is solved. Draft PR #39 remains review-only, unmerged and without verified execution of its Python tests. No DEVELOPMENT or PRODUCTION changes.

**Next safe one-command diagnostic:** Inspect **selected local startup definitions only**—administrator-managed systemd service/timer definitions/drop-ins, ordinary root cron entries and `/etc/rc.local`—for a literal reference to the original CCPC lab firewall script name or the three exact comment tags. Output only counts and booleans, not contents, file names, paths, secret values or raw unit entries. Confirm agent stopped and original lab rules still active first. This is necessarily a bounded search, not proof that no other persistence mechanism exists. If no mechanism is found, design a separately authorized fail-safe startup persistence strategy in GitHub; do not apply anything on host from this conversation without approval of the exact procedure.

## Step 89 — selected host startup references absent (2026-11-20)

Operator ran the prior guarded, **read-only** systemd/cron/rc.local reference scan on `ccpcerpserver`; three exact original laboratory firewall rules remained installed and agent remained stopped. Sanitized output: `agent_running=False`, `original_lab_three_rules_installed=True`, `systemd_definitions_checked=1`, `systemd_reference_matches=0`, `cron_files_checked=13`, `cron_reference_matches=0`, `root_crontab_reference_present=False`, `rc_local_checked=False`, `rc_local_reference_present=False`, `reboot_persistence_verified=False`, `INSPECTION_COMPLETE`.

**Interpretation:** None of the **one regular file** among the narrowly scanned administrator-managed systemd service/timer/drop-in definitions, **13 selected cron files**, root's crontab, or rc.local referenced the original-lab script name or exact CCPC rule comments. `rc.local` was not present as a regular file. These counts do **not** establish that no other startup mechanism exists: the scan skipped symlinks and other unit/vendor paths, could not resolve indirect calls, did not scan non-root crontabs, and can miss rule restorers without those literal markers. Steps 87–88 separately found UFW active but no rule comments in its three inspected saved IPv4 rule files, two hooks, or nonempty nftables configuration. Taken together, these support **potentially ephemeral** rules without proving reboot loss. Crucially, **all three original-lab DROP rules are presently installed**; no immediate missing-firewall-rule claim is warranted.

**GitHub-only security design milestone:** The approved review workstream created a new **proposal document**, `docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md`, on `review/codex-proxy-network-hardening-2026-11-19`, commit `e0967515c4051927b3b2d22a5fefdbfec47fcbb3` (fetch-verified), for draft PR #39. It documents current evidence, original and new bridge security invariants, two not-yet-selected persistent firewall options (UFW-native if Docker chain ordering allows, or guarded root-owned systemd oneshot/verification with explicit startup dependencies), a pre-enforcement/no-race requirement, independent egress/Squid gating, and scoped rollback/negative testing. **This is documentation only**, not a systemd unit, firewall installer or approved execution plan. Do not install either option without independent host-state verification and explicit operator approval of the exact procedure.

**Next one read-only diagnostic:** Read Docker daemon and UFW unit `UnitFileState`/`ActiveState`, their direct `After` ordering relationship, and the inspected *stopped agent container's* Docker restart policy. Return only sanitized status classes/booleans, not systemd dependency lists, addresses, paths, secrets or unrelated service names. Check agent labels, original-lab bridge and existing exact INPUT/FORWARD rules as preconditions. These facts inform persistence design but will **not** prove transitive ordering, automatic firewall restoration, or isolation. No network or service changes, Docker pull/pull-request merge or PRODUCTION work authorized.

**NO-GO unchanged:** agent stopped; optional Squid off; proposed proxy bridge uncreated; draft PR #39 unmerged and source-only unit tests not executed/verified. Existing DEVELOPMENT and reported separate PRODUCTION untouched.

## Step 90 — Docker and UFW directly unordered; agent Docker restart disabled (2026-11-20)

Operator ran a guarded **read-only** `systemctl show`/Docker restart-policy precheck on `ccpcerpserver`. Sanitized output: `agent_running=False`, `original_lab_three_rules_present=True`, `agent_restart_policy_disabled=True`, `docker_service_active=True`, `docker_service_enabled=True`, `ufw_service_active=True`, `ufw_service_enabled=True`, `docker_socket_enabled=True`, `docker_after_ufw_declared=False`, `ufw_before_docker_declared=False`, `ufw_after_docker_declared=False`, `complete_boot_order_verified=False`, `firewall_reboot_persistence_verified=False`, `INSPECTION_COMPLETE`.

**Interpretation:** the existing agent's actual Docker restart policy is disabled, limiting ordinary unplanned auto-relaunch; however, manual Docker start or future config drift can bypass that safeguard, so it is not a security enforcement boundary. Docker, docker.socket, and UFW are enabled, but no **direct** ordering relation between Docker and UFW was declared among the inspected properties. This is *not proof* of the actual boot order or of absent transitive dependency. Crucially Steps 87–89 did not find a proven restoration mechanism for the original lab firewall protections: UFW service activity does not itself persist the three custom iptables rules. All three are **currently installed** as verified by Step 90; there is no established current missing-rule condition.

**GitHub design update:** The draft PR #39 review branch's `docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md` was amended at verified commit `1fda0244a124943871d5f96142346420f80a0f26`. The document now records Step 90 and favors **evaluating** a dedicated root-owned, narrowly scoped systemd firewall preparation and independent fail-closed verification design, given direct UFW/Docker ordering is not established. **No implementation, unit installation, firewall persistence enablement or operational authorization was performed.** A simple `After=ufw.service` alone would not prove custom rule persistence or protect against post-boot UFW/Docker reloads; boot/start/reload race handling, Docker socket activation, exact scoped rollback, SSH access and nonproduction negative tests remain required.

**Next safe inspection:** inspect selected `systemctl show` state and dependencies of Docker, docker.socket and UFW for potential transitive ordering and reload triggers (sanitized booleans only), while checking stopped agent and three exact installed lab rules. Do not read/share unit files with secrets, run systemctl reload/restart/enable, run Docker network creation or apply iptables rules. The intended output is evidence for a reviewed startup sequence, **not** proof of persistence or deployment readiness.

**NO-GO unchanged:** original lab agent stopped; Squid inactive; new bridge not created; PR #39 unmerged; 60 Python source-only tests still not verified executed/passed and runtime/security integration tests not performed. DEVELOPMENT/PRODUCTION untouched.

## Step 91 — systemd dependency review confirms no dedicated lab firewall boot hook (2026-11-20)

The operator performed the read-only Step 91 systemd property inspection on `ccpcerpserver`, again with agent stopped and the original-lab three exact firewall rules present. Sanitized stdout: `agent_running=False`, `original_lab_three_rules_verified=True`, `docker_requires_ufw=False`, `docker_wants_ufw=False`, `docker_after_network_online=True`, `ufw_before_network_pre=True`, `docker_has_dropins=False`, `ufw_has_dropins=False`, `docker_has_start_pre_hook=False`, `docker_has_start_post_hook=False`, `ufw_has_reload_handler=False`, `docker_socket_requires_service=False`, `complete_dependency_graph_verified=False`, `reboot_persistence_verified=False`, `INSPECTION_COMPLETE`.

**Interpretation:** No direct `Requires/Wants` relationship from Docker to UFW, and no inspected Docker/UFW drop-ins or Docker ExecStart pre/post hooks. The ordering via distinct `network-pre.target` and `network-online.target` is not sufficient to infer a complete startup graph. A false `docker.socket Requires=docker.service` does **not** exclude activation through the socket unit's own Service mapping. No UFW ExecReload handler does **not** prove the `ufw reload` CLI does not change active firewall rules. All three lab firewall DROPs are present *now*, but persistence after reboot, UFW reload or Docker chain reinitialization is **unverified**.

**GitHub-only design progress:** Updated `docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md` on draft PR #39 review branch at verified commit `9598d9401cf0fea389027e13f25607f57c6ca23e`. The design now favors a two-layer **proposal**: (1) narrowly scoped root-owned, fail-closed *original laboratory firewall restoration* after verified Docker chain availability and UFW initial state, with exact-rule checks/idempotence, and (2) **independent per-launch** read-only enforcement checking all original-lab protections and eventually second-bridge pre-enforced rules before any manual Codex startup. This prevents treating a one-time boot firewall service as sufficient protection against later UFW/Docker reloads, unguarded manual starts, or missing rules. Actual startup bypass control, persistence/reload restoration, Squid outbound restrictions, and negative integration tests still require review and separately approved implementation. No systemd units/scripts installed or changed.

**Decision:** Further unfocused read-only host scans have diminishing value. Next GitHub-only milestone is a concrete, testable, **disabled/uninstalled** guarded implementation proposal and rollback plan. A separately explicit host-operation approval, SSH recovery route, nonproduction canaries and tested gate are required before any host firewall modification, Docker network creation or agent/Squid startup. CI Python tests remain not executed/verified. No DEVELOPMENT or PRODUCTION changes. **NO-GO** for activation/deployment.

## Step 92 — GitHub-only original laboratory restore and guard source proposal (2026-11-20)

The project owner approved continuing Step 92 **GitHub-only implementation planning**, following the read-only Step 91 Docker/UFW dependency checkpoint. The agent remains stopped; no current host service, Docker network, systemd unit or firewall setting has been changed or independently probed. GitHub review branch `review/codex-proxy-network-hardening-2026-11-19` on deployment repo draft PR #39 received:

- NEW `scripts/security/ccpc_codex_lab_firewall_guard.py`: strictly **read-only**, modes `preflight` and `verify` only. Guards root/host and Docker daemon identity, known-label agent stopped and restart disabled, precise original lab bridge/subnet/gateway/IPv6 and iptables-nft configuration, active UFW and Docker FORWARD/DOCKER-USER path. In verify mode checks exact `iptables -C` for all three existing original-lab DROP rules and their correct leading INPUT/DOCKER-USER placement through normalized `iptables -S` parsing, correcting Step 83's token-order comparison weakness. **Always prints `agent_launch_authorized=False`**, even on success; cannot start/restart Codex, apply, delete or install rules.
- NEW `scripts/security/systemd/ccpc-codex-lab-firewall-restore.service.example`: **inert, uninstalled** systemd review template with a root-controlled authorization marker requirement and planned fixed source installation path. Hypothetical future flow after Docker/UFW readiness: guard preflight → previously existing unchanged `ccpc_codex_dev_lab_firewall.sh apply` (scoped, guarded original-bridge rules only) → guard verify. No Codex or Squid startup and no ExecStop rollback. Merely adding this file to GitHub cannot enable any host service; the marker is **not** created by this session.
- NEW `codex-dev-agent/tests/test_lab_firewall_guard.py`: 10 mock-only, offline unit tests of precedence semantics, fail-closed verification, illegal modes and inert unit structure. Together with the existing 60, **70 Python test methods are declared**. The review branch's CI workflow path filters and laboratory README were updated for the added source files.
- Updated `docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md`: full Step 92 preconditions, guarded proposed lifecycle, failure paths, read-only per-launch checks and **exact rollback by distinguishing pre-existing rules from newly added ones**. Never blindly call the pre-existing script's general `rollback`, which would remove existing original-lab protection if applied indiscriminately.

**Static consistency review:** Connected GitHub re-fetched the new guard, example unit and source-only tests, checked 14 intended safety/source assertions; all 14 returned true. These are **not actual Python or systemd tests**. The latest observed GitHub Actions run **44646427336** on Step 92 head `6d2aa16e29e5e43a60751bb6c76174f36f6136c7` completed **failure before any runner name/steps were recorded** (zero steps), so the 70 Python tests have **NOT been executed/verified**. Do not infer assertion failures or test passes from this workflow status.

**Branch state:** Draft PR #39 remained open and draft; the compare at this checkpoint was **31 commits ahead, 6 behind** current moving PR33 base, with **11 intended changed paths** confined to Codex lab/CI/security source, test files and review documentation. Do not rebase/force push or pull to the host without safe branch/working-tree review; pending base changes require separate review before merge.

**Remaining NO-GO gates:** The systemd example is **not deployable as-is**, because its approved installed paths/marker, order and reload restoration have not been validated. A oneshot plus manual guard does not prevent a privileged Docker user from bypassing the gate or a later UFW/Docker reload from clearing rules; no complete persistence or runtime-enforced launch boundary exists. Proposed second `proxy_clients` bridge is absent, with host/cross-bridge pre-enforcement and Squid outbound/DNS restrictions pending. Live negative integration tests, image pinning, Python/Squid parsing, CI runner, and rollback/reboot procedures remain unresolved. No real host/DEVELOPMENT/UAT/PRODUCTION changes or tests performed. Keep Codex stopped and Squid offline.

**Next safe step:** inspect the new GitHub review files together, resolve any test/code issues and CI runner pre-run blocker; do not begin server installation merely because this GitHub implementation proposal exists. Any actual host firewall/systemd operation requires separate explicit approval of the exact commands, verified administrative recovery, backups and nonproduction test/rollback scope.

## Step 93 — CI pre-run failure investigated and full offline suite passes (2026-11-20)

The owner approved continued **GitHub-only** CI investigation and independent offline testing (not host or production changes). The connected GitHub tools inspected private deployment repo draft PR #39 at the current review branch, the `codex-lab-static-review.yml` workflow and its Actions run/job. Latest observed failing run at the beginning of this checkpoint: **44646960863**, job **135991884555**; `status=completed`, `conclusion=failure`, **no runner name**, **0 job steps**, and job-log download returned **404 BlobNotFound**. Other prior Codex workflow jobs were likewise step-free. Importantly, an unrelated scheduled `Autoupdate pre-commit hooks` run **44563127843** had **zero steps and no runner name**, strengthening evidence for a GitHub Actions pre-execution account/runner infrastructure issue. Exact cause is **unverified**, not a known Python test failure; possible Actions plan/usage/billing state or runner provisioning/temporary platform failure requires reviewing the GitHub Actions run **Summary/Annotations**. Do not automatically add payment methods, increase budgets, launch self-hosted runners, or repeatedly rerun without owner approval. No workflow settings were changed in GitHub.

**Critical code review finding and fix:** Existing two-bridge source proposal had an impossible condition: the original bridge and new `proxy_clients` bridge each required their own host `INPUT` rule first and their own two `DOCKER-USER` rules in positions 1–2. Corrected on the GitHub review branch using NEW pure `scripts/security/ccpc_firewall_rule_order.py`, shared by `ccpc_codex_lab_firewall_guard.py` and `ccpc_codex_proxy_bridge_preflight.py`. It demands either exact original-only leading DROP prefixes or complete **two `INPUT` / four `DOCKER-USER`** combined restrictive prefixes when proxy-bridge rules are involved, in either safe relative order. Rejects incomplete new-bridge protections, unexpected or permitting earlier rules, and missing legacy protections. Added five additional mock-only regression tests and updated the CI trigger path. This is a source-only fix; nothing was installed or applied on the host.

**Verified independent test result:** Reconstructed all Python source dependencies in a separate isolated local workspace from the connected private GitHub source, cross-checking each file's Git blob SHA against its GitHub blob SHA. No Docker, ERPNext, host, Squid binary, firewall mutation, SSH or production access. Executed `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s codex-dev-agent/tests -p 'test_*.py' -v`. **Ran 75 tests; OK, zero failures/errors**, including negative Compose/Squid/secret restrictions, original lab rule identity/precedence and two-bridge combined ordering. Synthetic-only disposable secrets were generated under temporary test storage; none were disclosed or committed. This is a **real offline Python unit-test pass**, distinct from GitHub Actions (which remains blocked), actual Docker Compose config rendering, `squid -k parse`, live firewall isolation, DNS/Squid runtime, and host negative tests. All remain separate acceptance conditions.

**Documentation:** Updated review-branch `codex-dev-agent/README.md` and `docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md` to record the shared ordering fix and accurately separate 75/75 independent offline tests from the unexecuted GitHub-hosted CI. Draft PR #39 remains DRAFT and not merged. No local server changes, DEVELOPMENT/PRODUCTION operations, or Codex/Squid starts were performed. The last operator-supplied live state in Step 91 remains original lab three exact rules installed, stopped agent, proposed bridge absent and firewall reboot persistence unverified; do **not** assert a fresher host verification.

**NO-GO remains:** Fixes are source-only; actual combined iptables parser compatibility, firewall reload persistence, unbypassable guarded launch, proxy outbound/DNS/SSRF controls and nonproduction connectivity negative tests remain unresolved. Next owner action: open the GitHub Actions failed run Summary, read its failure annotation and check current free Actions usage/billing state **without enabling paid features**. A specific annotated error will allow targeted CI resolution; until then, avoid irrelevant workflow mutations. The independently passed offline tests permit continued review, not activation.

## Step 94 — owner-supplied GitHub Actions billing annotation confirms pre-run block (2026-11-20)

Operator copied the exact GitHub Actions **Annotations → policy-regression** failure message from [run #44650795584](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44650795584) on open draft deployment PR #39:

> The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings

Run reports **Failure after 3 seconds**, **1 annotation**, **no artifacts**. Earlier GitHub connector inspection confirmed **0 runner steps and no runner name**; `BlobNotFound` on job-log download is consistent with no job execution. **Diagnosis:** GitHub-hosted Actions is blocked **before any Python execution** by an account **payment/spending-eligibility restriction**. This does *not* identify which of the two offered account-specific conditions (failed payment vs spending limit) applies, nor authorize a payment or settings change. It is not a Python test assertion failure.

**Decision:** As required by the project's no-unrequested-paid-automation policy, do not add payment methods, increase spending limits, change GitHub billing settings, install self-hosted Actions runners, or repeatedly trigger failed workflows. The owner may read Billing & plans themselves if desired; no change is requested. Maintain **GitHub Actions CI = blocked/unexecuted**, distinct from **75/75 offline Python mock/source-only tests successfully executed** using exact GitHub blob-hash-verified files in Step 93. Those offline results do **not** prove Docker, live firewall/host security, Squid parsing, reload resilience, DNS/egress restrictions, or PRODUCTION isolation.

**GitHub-only documentation:** Updated `docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md` on `review/codex-proxy-network-hardening-2026-11-19`, commit `ef21a58a8b2888f0df5bc9126520bddaaae58603` (refetch-verified). No source code, workflow implementation, firewall script or host configuration was modified for this diagnosis. Draft PR #39 remains open, draft and unmerged; last operator-reported Codex agent stopped, Squid inactive, optional second bridge absent; there was no fresh host test or operation. No DEVELOPMENT/PRODUCTION changes.

**Next safe development:** Continue GitHub review and no-cost isolated offline tests. Address launch-gate bypass prevention, reload persistence, egress/DNS controls and isolated negative tests before any separately approved host operation. No server command required for Step 94.

## Step 95 — CircleCI manual-only source test proposal in GitHub (2026-11-20)

The owner offered CircleCI instead of relying on GitHub Actions, whose run `44650795584` has an account billing/spending eligibility annotation and **no runner test execution**. Confirmed in connected GitHub: the **custom app** `ccpcerp/ccpcerp` already has a CircleCI configuration on the current Finance release branch using opt-in test/approval workflows. By contrast, the **deployment repo** `ccpcerp/ccpc-frappe-deployment` had **no** `.circleci/config.yml` on the Codex review branch, PR33 base or main before Step 95. CircleCI connection, org identity, plan/credits and permission to add the deployment repo remain **unverified**; the plugin directory search returned no available CircleCI plugin.

**GitHub-only change:** Added `.circleci/config.yml` on `review/codex-proxy-network-hardening-2026-11-19`, verified GitHub commit `11e7b3944a76d74047e3b936d27438ee038ea013`. Source-only `cimg/python:3.14`, small-resource job defaults **off** via boolean `run_codex_source_tests=false`; requires separately supplied `approved_codex_commit` (40-char exact reviewed Git SHA), a manual `authorize-codex-source-tests` approval hold, strict PR #39 review branch filters, GitHub checkout hash and CircleCI project/runner identity checks, 75 expected unittest discoveries and 120-second execution limit. No Docker, Codex, Squid, ERPNext, database, credentials, contexts, package installation, GitHub writeback, schedules or deployment operations. Ordinary pushes/PR sync do **not** run this workflow by default. Adding the YAML does NOT connect the deployment repo, use credits or start a pipeline.

Added `docs/ccpc-project/CODEX-LAB-CIRCLECI-REVIEW.md`, verified commit `a9fe5b09f8b131fe502b160abd8ed1490754837e`. Updated the source security design with Step 95, verified commit `db5a996f4adc30c6e0aede991a76764125b89197`. CircleCI source YAML was copied byte-for-byte into a separate local validation file, with computed Git blob SHA **`06548b915e3685f655cccefa4bd9a122613a8cce`** matching GitHub. **PyYAML 6.0.3 successfully parsed** the file and **six static guard assertions** passed. This proves only local YAML structure, **not** CircleCI's own config acceptance or a CircleCI-run Python pass. The **75/75 isolated Python suite** remains a separate previously verified Step 93 result, not newly re-run here.

**No-cost policy:** Do not trigger a CircleCI build, connect a new project, spend credits, alter billing, run paid GitHub Actions, or configure autonomous jobs until owner separately confirms exact deployment repository CircleCI connection/available credit and authorizes the manual run. Existing `ccpcerp/ccpcerp` CircleCI config and the blocked GitHub Actions workflow were not modified. No host/DEV/PROD changes.

**Next one question:** Is the deployment repository **`ccpcerp/ccpc-frappe-deployment`**, distinct from the custom app `ccpcerp/ccpcerp`, already connected/listed in CircleCI? If yes, have operator inspect plan/credits and manual pipeline parameters. If not, review separate onboarding permission and automatic trigger policy before any connection. Draft PR #39 remains OPEN/DRAFT/unmerged; host/Squid/network activation **NO-GO**.

## Step 96 — public runner smoke workflow committed, not executed (2026-11-20)

Owner created a new, **public and separate** GitHub test repository, `ccpcerp/ccpc-ci-sandbox`, to check whether standard GitHub-hosted Actions can start despite the existing private deployment repo's Step 94 account billing/spending eligibility error. Repository visibility verified `public`, default branch `main`, installation connected with permissions after owner explicitly extended the GitHub app's selected-repositories access to include only the sandbox. Prior write attempts were rejected 403 until the owner updated that connection; no bypass occurred.

**Verified GitHub write:** On **only** `ccpcerp/ccpc-ci-sandbox` `main`, created `.github/workflows/public-runner-smoke.yml` and refetched byte-for-byte. Successful commit `78fb63e156915766a7fef510abe2908f0499a678` with content blob `691d2cd6e173fa3e013355fa161bcbdc6235ef8b`. The workflow has **only manual `workflow_dispatch` trigger**, read-only `permissions: {}`, `ubuntu-latest` 3-minute timeout and **two inline Python stdlib test cases** with no checkout, secrets, private CCPC code, Docker, credentials, network requests or deployments. No CircleCI, repository billing or existing workflow modified.

**Verification limit:** GitHub source/commit exist; **the public smoke workflow has not run or produced a pass/failure**. This test cannot prove that account-level billing restrictions do or do not affect a public job until the owner manually dispatches and inspects the result. Public standard-runner usage policy does not supersede a possible account-level eligibility blocker. The 75/75 previously passed offline synthetic Codex source-only suite was **not copied to the public repository**. Keep private deployment and internal firewall/security details private.

**Next operator step:** In the public repo `ccpcerp/ccpc-ci-sandbox`, navigate to **Actions → Public runner smoke test → Run workflow → main → Run workflow**. Operator should report the new run result and any Summary/Annotations error without secrets. Do not enable billing, paid runners or change Actions settings. Public test is manually triggered by the owner, never automated by this milestone.

**NO-GO unchanged:** Draft deployment PR #39 unmerged and Codex/Squid stopped at last operator snapshot. Firewall persistence, proxy egress and live isolation remain unverified. No DEVELOPMENT or PRODUCTION changes were performed.

## Step 97 — public GitHub-hosted runner smoke PASS (2026-11-20)

**Verified outcome:** The owner manually dispatched the public standard-runner test. The connected GitHub API independently confirmed exactly one run for `ccpcerp/ccpc-ci-sandbox`: [run 44660189430](https://github.com/ccpcerp/ccpc-ci-sandbox/actions/runs/44660189430), event `workflow_dispatch`, `status=completed`, `conclusion=success`, created 2026-11-20 02:21:24 UTC (10:21:24 Asia/Manila), running commit `78fb63e156915766a7fef510abe2908f0499a678` on `main`. GitHub job `Public standard runner / Python smoke` also concluded `success` (job ID `136036250169`). Operator-provided job logs show both Python standard-library assertions passed, 0 failures.

**What this proves:** A manually dispatched public GitHub-hosted `ubuntu-latest` runner executed successfully for this account/repository at that moment. **What it does not prove:** private CCPC repository Actions eligibility, suitability for Frappe/MariaDB integration, CircleCI availability or free-credit budget, or safety/authorization to activate the local Codex lab. The public repo workflow does not contain or check out private CCPC application code or secrets. No lab/DEV/PRODUCTION changes occurred as part of this verification, and no CI rerun or paid runner was initiated by ChatGPT.

**Disposition:** Public smoke test **PASS**. Existing independent Codex/Squid isolation and shared-host resource blockers remain **NO-GO**; production and protected DEVELOPMENT controls are unchanged. For actual ERPNext integration testing, review the existing private-repository/approved hosted-CI path and its cost/security gates separately.

---

## Step 98 — automatic public CI with synthetic MariaDB PASS (2026-11-20)

**Owner authorization:** The owner explicitly requested that the public sandbox testing run automatically, with the intention of considering private visibility later. This authorization was scoped to the **public-safe CI sandbox**; it did not authorize publishing existing private CCPC custom application code, credentials, business data, automatic Codex reporting, or changes to DEVELOPMENT/PRODUCTION.

**GitHub change independently verified:** [commit `84e55ff7581edae7db6447ad3e25dd18940d74f2`](https://github.com/ccpcerp/ccpc-ci-sandbox/commit/84e55ff7581edae7db6447ad3e25dd18940d74f2) on the public `ccpcerp/ccpc-ci-sandbox` `main` branch updated `.github/workflows/public-runner-smoke.yml` to run automatically on `push` to `main` and `pull_request` targeting `main`, while retaining manual `workflow_dispatch`. The workflow uses standard GitHub-hosted `ubuntu-latest`, `permissions: {}`, concurrency cancellation, no private checkout, no secrets or protected resources, and bounded 3-/8-minute job timeouts. It contains the previous two inline Python smoke tests plus two synthetic SQL tests against an isolated `mariadb:10.11` service, checking rollback and database duplicate-reference rejection. The MariaDB root password is an explicitly public, throwaway CI-only fixture, not a CCPC credential.

**Automatic execution verified:** The workflow change itself triggered [run `44664017862`](https://github.com/ccpcerp/ccpc-ci-sandbox/actions/runs/44664017862) on event `push`, SHA `84e55ff7581edae7db6447ad3e25dd18940d74f2`, created 2026-11-20 02:54:08 UTC. GitHub API reported `status=completed`, `conclusion=success`; both jobs `Public standard runner / Python smoke` and `Disposable MariaDB / synthetic SQL transactions` completed with `success`. All four synthetic checks passed under the implemented job steps.

**Limits and next gate:** This is real disposable MariaDB integration, **not** a Frappe installation or CCPC Withdrawal Slip/Material Issue/stock ledger/GL/intercompany acceptance. Adding private application source or real data to public GitHub would create irreversible exposure even if the repository were made private later. Public-runner availability does not establish private-repo billing eligibility. Current lab Codex/Squid activation **NO-GO** and separate DEVELOPMENT/PRODUCTION controls remain unchanged. Next, consider a public-source-only disposable Frappe test before designing a separately authorized private-code testing boundary.

---

## Step 99 — automatic disposable Frappe/ERPNext v16 PASS (2026-11-20)

**Owner-approved public-only CI extension; completed and verified.** The public repository `ccpcerp/ccpc-ci-sandbox` now has a third automatically triggered GitHub-hosted Actions job: real public Frappe/ERPNext v16 installation plus MariaDB DocType verification. The implementation used review branch `ci/automatic-public-frappe-smoke-2026-11-20`, PR [#1](https://github.com/ccpcerp/ccpc-ci-sandbox/pull/1), and was **squash-merged into public `main`** at verified commit [`3bce6b72296b47e58f4f5e2a72af73f74ec059a1`](https://github.com/ccpcerp/ccpc-ci-sandbox/commit/3bce6b72296b47e58f4f5e2a72af73f74ec059a1). GitHub branch/file reads confirmed the exact merged workflow and Compose stack on `main`.

**Verified passing CI:** The corrected PR [run 44665541094](https://github.com/ccpcerp/ccpc-ci-sandbox/actions/runs/44665541094) completed `success` for all three jobs. Independently, the **automatic push event caused by merging** initiated [run 44665949106](https://github.com/ccpcerp/ccpc-ci-sandbox/actions/runs/44665949106) on the exact merge SHA `3bce6b7`, with `status=completed` and `conclusion=success` for **all three jobs**. The Frappe job output explicitly confirmed the new synthetic `ci.localhost` site, Frappe `16.60.2`, ERPNext `16.60.0`, and actual MariaDB `Sales Invoice` and `Stock Entry` DocTypes. Docker volume and network removals were visible in the successful post-job log. The job uses public `frappe/erpnext:v16.60.0`, public MariaDB 11.8 and Redis 6.2, a synthetic known CI-only password, a private-to-container Docker network with no host-published ports, GitHub-hosted-only runtime guard, cleanup trap, no fork-PR heavy job, and 18-minute timeout. Existing two Python and two MariaDB synthetic tests still passed.

**Failure corrections recorded:** The first PR attempt failed because the `bench new-site` command supplied the site operand twice; fix [`44b5136`](https://github.com/ccpcerp/ccpc-ci-sandbox/commit/44b5136eee5ce9eb695d2349ab2253747f2df2f0) corrected this. The second attempt actually installed ERPNext but incorrectly parsed a Frappe container startup banner together with the generated DB name; fix [`aa024da`](https://github.com/ccpcerp/ccpc-ci-sandbox/commit/aa024da79dff5054b4bfc7701a364e2a4fbd3d8d) extracted only the final result line. Subsequent PR and merge-push executions both passed. Failed historical runs remain visible as evidence; do not describe them as passing.

**Boundaries unchanged:** Public CI carries **no private CCPC application code**, GitHub private credentials, production/business data, server access, or local Codex proxy activation. These checks prove an actual generic Frappe/MariaDB setup, **not** CCPC-specific stock movement/GL/intercompany business acceptance, real concurrency safety, or DEVELOPMENT acceptance. Public repository visibility cannot retroactively protect previously published material if changed to private. This is **not** authorization for private-code publication, Codex/Squid activation, development/production changes, or a paid CI provider. Existing local Codex/Squid security gates remain independent **NO-GO**.

**Next delivery gate:** Scope a secure, private-source-capable CI method for the real CCPC custom app and synthetic transactional acceptance. Retain automatic public-only Frappe smoke tests as reusable preliminary infrastructure validation.

---

## Step 100 — Codex review-only memory and PID ceilings (2026-11-20)

**Scope and authorization:** After confirming that the public ERPNext Actions checks are operating, the owner requested continuation of the local Codex readiness work. Continued **GitHub source-only review** on deployment draft [PR #39](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/39), branch `review/codex-proxy-network-hardening-2026-11-19`. No Docker or server changes, agent/proxy start, firewall reload, source pull, DEVELOPMENT/PRODUCTION operation, or paid CI execution was authorized or performed. PR #39 remains open, draft, **unmerged**.

**Verified GitHub commits** (read after write and checked commit file lists):
- [`8376fbd`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/8376fbd29bf8638903a13c4a416cc759c269813a): review-only proposed `codex-dev-agent/compose.yaml` resource ceilings for all five lab services (agent **8 GiB/512 PIDs**; synthetic MariaDB **2 GiB/256 PIDs**; two Redis services **384 MiB/128 PIDs each**; optional Squid **512 MiB/128 PIDs**). `memswap_limit` equals each `mem_limit` to avoid unbounded swap consumption where Docker supports enforcement. The sum of configured maxima is **11.25 GiB**; not a reservation or validated shared-host budget. **No CPU cap** added, consistent with the operator's maximum-performance preference. This does not guarantee host availability under concurrent workloads.
- [`27cd260`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/27cd2608f19deec24d8c6c560de7a6718c7fa816): `check_compose.py` now fails closed on missing or changed memory, memory+swap or PID caps; accepts Compose memory-unit strings or normalized positive integer byte counts.
- [`95bb2a4`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/95bb2a4b4a1c495df43321bc4d146ce9a9703168): six additional source-only regression methods cover missing/expanded caps, excessive swap, PID omissions and accepted unit formats.
- [`60ca788`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/60ca788280030598149a7d0558c36ba0c96e1ece): review README documents candidate ceilings, nondeployment status and execution limits.

**Verification and limits:** Connected GitHub refetch confirmed exactly five `mem_limit`, five `memswap_limit` and five `pids_limit` entries with intended values. Validator includes the bound check, and all six new test methods are present. The `test_safety_policy.py` class now declares 66 test methods; combined with the unchanged 15 firewall-guard tests, **81 source-only tests are declared**. Only the earlier **75/75** tests were independently executed at Step 93; **the six new tests, full 81-test suite, rendered Docker Compose config and actual runtime enforcement have not been executed or verified**. Existing private GitHub-hosted runner eligibility remains separately blocked by the observed Step 94 billing/spending annotation. No source-only check can establish resource behavior on `ccpcerpserver`, image authenticity, effective firewall protection or agent sandboxing.

**NO-GO unchanged:** This commit set is only a review proposal; the host still runs its previously verified Compose configuration and effective runtime caps, with agent stopped at last operator observation. Local Codex CLI installation/authentication, sandbox enforcement, persistent firewall restoration, safe per-launch guard, proposed proxy-client and outward Squid reachability/DNS controls, credential provenance, negative canary tests, resource sizing under host peak load and DEV acceptance remain outstanding. Do not merge/deploy PR #39 or start the agent based on these source changes. Next advance is the exact source-only test execution in an approved isolated runner or trusted offline workspace, followed by a separately authorized host-only dry-run and isolation verification; keep public synthetic ERPNext CI separate from private security source.

---

## Step 101 — focused resource-gate tests and CircleCI 81-count fix (2026-11-20)

**Owner authorization and scope:** Owner explicitly approved continuing the previously planned source-only Codex security test work. All repository writes remained limited to the private deployment repo's existing draft [PR #39](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/39), branch `review/codex-proxy-network-hardening-2026-11-19`, and this private audit branch. No Codex agent start, Docker host operations, DEV/PRODUCTION changes, CircleCI runs/connections, billing changes, extra paid APIs or private-to-public repository code transfer occurred.

**Source integrity and executed focused tests:** The connected GitHub plugin fetched `codex-dev-agent/check_compose.py` from the review branch, blob SHA `4e1be61a27b73ee7afd39e82995db4e0b094f93d`. A 1,497-byte excerpt containing the proposed `EXPECTED_RESOURCE_BOUNDS`, `resource_bytes`, and `validate_resource_bounds` definitions was reassembled in an isolated, ephemeral local Python workspace and matched to the fetched excerpt by exact byte length and FNV-1a 32-bit checksum `c3fff151`. This checksum is a consistency check, not cryptographic proof of complete file/repo identity. **Seven focused Python unittest scenarios executed and passed (0 errors/failures)**: five-service valid baseline, missing agent cap, expanded agent cap, excessive MariaDB swap, missing Redis PID cap, missing proxy cap, and Compose string-unit acceptance. No Docker, network, credential, Squid, server or Frappe runtime was used. The scratch workspace was cleaned after inspection. The temporary private first-party source-transfer Page was moved to Trash and no private source was put in the public CI repository.

**Critical distinction:** This was **NOT** execution of the complete `codex-dev-agent/tests/test_safety_policy.py` or `test_lab_firewall_guard.py` modules. The current private review source **declares 81 tests** (66 + 15), but **81/81 has not been run or established**. Only historical Step 93's **75/75** full-suite pass for an earlier source and the seven new focused excerpt checks are independently executable evidence. The user must not be told the current 81-test suite passed.

**Verified GitHub source correction:** Existing manual-only `.circleci/config.yml` still hardcoded `75` and would reject the 81-test suite. On the draft PR branch changed its expected-discovery gate, job label and pass label to **81** at verified commit [`0ac2a588`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/0ac2a58808e3def622dd78e155afeee8969bea2d). Updated `docs/ccpc-project/CODEX-LAB-CIRCLECI-REVIEW.md` at [`eacdd8e`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/eacdd8e75e79b3eb31b0cb427df06f50f2eb42f5) and Codex README at [`7b7021f`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/7b7021faa08149f80e2f5e512cb59e473652df50) to separate the 81 declared tests, seven focused excerpt checks and previous historical 75/75 executed tests. Refetch verified exact CircleCI `!= 81` gate, default-off pipeline parameter, manual approval hold and updated README. **No CircleCI pipeline started**, provider connection/credits still unverified.

**Private Actions blocker independently reconfirmed:** [GitHub Actions run 44671454505](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44671454505) on PR head `7b7021f` completed `failure` **before execution**: the `policy-regression` job has **zero runner steps**. The precise latest annotation was not reread; the earlier Step 94 owner-provided account billing/spending annotation remains the last known cause and must not be restated as independently reconfirmed for this run. The successful public ERPNext runner does not waive private repository Actions eligibility. Do not re-trigger failed private Actions, add payment methods or claim a Python assertion failure.

**Disposition and next gate:** Codex agent **NO-GO**, draft PR #39 unmerged. The complete **81-test exact-SHA source-only suite remains pending** execution in a trusted local isolated private checkout or owner-approved manual CircleCI pipeline with verified organization/repository onboarding and remaining credits. Keep firewall persistence, proxy DNS/egress isolation, image provenance, Codex CLI sandbox/auth and guarded launch as separate unresolved security gates. Do not begin host modifications or activation merely because focused tests passed.

---

## Step 102 — public repository GitHub-hosted 81/81 source tests PASS (2026-11-20)

**Owner's explicit visibility decision:** After reviewing disclosure risks and acknowledging that making a repository private later cannot retroactively undo public copies/history access, the owner manually changed `ccpcerp/ccpc-frappe-deployment` from private to **public**, intending to make it private after the project is completed. The connected GitHub `get_repo` and API read independently confirmed `visibility=public` and `private=false` (2026-11-20). **This public exposure includes deployment/infrastructure and security documentation, branches/history and accessible workflow logs**; no secret-history audit has been completed, and public status is not a claim of safety. ChatGPT did not perform the repository visibility change.

**Full-suite execution now verified:** The existing previously failing [GitHub Actions run `44671454505`, attempt **2**](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44671454505/attempts/2) was explicitly retried **once** using the connected GitHub Actions `rerun_failed_workflow_run_jobs` after the visibility change; the API returned `success=true`. The run was `event=pull_request`, at **exact PR #39 head commit `7b7021faa08149f80e2f5e512cb59e473652df50`**, and was reported `status=completed`, `conclusion=success`, `run_attempt=2`. Latest job `policy-regression`, job ID `136084989045`, completed `success`, including a real checked-out `actions/checkout@v4` source and `python3 -m unittest discover -s codex-dev-agent/tests -p 'test_*.py' -v` step. The **actual decoded job log** explicitly reports `Ran 81 tests in 0.008s` followed by `OK`. All six previously unexecuted resource-governance tests are visible as `... ok`. No assertion failures or errors. The test output's `STOP: safe proxy bridge preflight unavailable` lines are expected negative-case outputs, **not a CI failure**; the job and entire run finished successfully.

**What passed and what remains unverified:** This is genuine GitHub-hosted execution of **81/81 source-only Python regression tests**, superseding Step 101's pending test status; it does **not** constitute Docker Compose runtime/resource-limit enforcement, image provenance, Squid parser/live egress, iptables/UFW restore persistence, guarded launch, host isolation, Codex CLI authentication/sandbox operation, MariaDB integration or CCPC-specific business-transaction acceptance. The previously passing separate public `ccpcerp/ccpc-ci-sandbox` ERPNext+MariaDB workflow remains independently distinct. The local Codex agent was **not started**; the proxy, firewall, DEVELOPMENT and PRODUCTION were untouched. Draft [PR #39](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/39) remains open and unmerged; its review-head commit remains the tested SHA. Current disposition: **Codex activation NO-GO** pending host/runtime controls and separately scoped approval.

**Next safe decision:** Leave the exact tested PR #39 source intact until review/next work authorization. Review the public repository for accidentally exposed secrets and sensitive infrastructure details, rotate/revoke any found secrets immediately, and consider minimizing the public visibility interval; switching to private later cannot erase external copies. Continue with a tightly scoped read-only host checkpoint and controlled negative isolation tests before any agent or proxy startup.

---

## Step 103 — host read-only original-lab firewall presence PASS (2026-11-20)

**Owner authorization:** The owner explicitly approved continuing host-isolation and guarded-start validation after the public GitHub-hosted 81/81 source test pass. Initial step was restricted to a read-only operator-run diagnostic on `ccpcerpserver`, not an agent/proxy start, Docker/iptables mutation, UFW reload, DEVELOPMENT/PRODUCTION operation, or code pull. ChatGPT did not have SSH/host access; the verification below is the **owner's supplied terminal stdout**, not an independent host inspection.

**Exact sanitized operator output** (followed by the `gani@ccpcerpserver` prompt):

```text
agent_stopped=True
agent_auto_restart_disabled=True
original_lab_identity_verified=True
original_lab_three_firewall_rules_present=True
rule_order_and_reboot_persistence_verified=False
codex_launch_authorized=False
READ_ONLY_CHECK_COMPLETE
```

**Interpretation:** The hostname/Docker identity and stopped-agent/Compose-label/restart-policy checks passed; original internal laboratory bridge metadata was as expected; **all three existing original-laboratory INPUT and DOCKER-USER iptables rules were found by exact `iptables -C`** at the instant of the operator observation. This **does not yet establish rule precedence** ahead of permissive rules, whether FORWARD enters DOCKER-USER first, persistence through UFW/Docker reload or reboot, actual host/network denial, absent proxy/client paths, Codex sandbox/auth, image trust, or a safe launch. The host was not modified and no server secrets, private credentials, raw IPs, container IDs, or firewall table dumps were shared.

**Next single read-only checkpoint:** With the agent still stopped, inspect normalized top-of-chain `INPUT` and `DOCKER-USER` prefixes and the first FORWARD jump to DOCKER-USER, guarding expected lab identity and exact three existing rule semantics. If any unexpected chain order or new proxy candidate appears, **STOP** and review sanitized booleans only; do not insert/reorder rules. If ordered correctly, advance separately to persistence and guarded startup design, with explicit host mutation approval and rollback/recovery planning before any change. Codex activation remains **NO-GO**.

---

## Step 104 — original lab firewall order PASS; persistence/start gate remains NO-GO (2026-11-20)

**Owner-provided read-only host evidence** from the previously reviewed Step 2 Python diagnostic on `ccpcerpserver` (not independently executed by ChatGPT):

```text
agent_stopped=True
host_input_rule_priority_verified=True
docker_user_rule_priority_verified=True
forward_hook_priority_verified=True
firewall_persistence_verified=False
runtime_network_isolation_verified=False
codex_launch_authorized=False
READ_ONLY_ORDER_CHECK_COMPLETE
```

**Interpretation:** With the known-label Codex agent stopped and Docker restart policy disabled, the operator's diagnostic compared normalized `iptables -S INPUT` first appended rule and `iptables -S DOCKER-USER` first two appended rules to the exact expected original-lab tagged DROP specifications, including inverse-match syntaxes and order-independent comparison of the two restrictive `DOCKER-USER` prefix positions. It also required the first `FORWARD` jump to be `DOCKER-USER`. **All reported assertions passed**. Together with Step 103's exact `iptables -C` presence checks, this establishes **presence and rule priority at the observed moment**. It is not proof of actual traffic denial, unbypassability, persistent rules or absence of alternate host paths; direct host/runtime network testing remains pending. No Linux firewall, Docker container/network, Codex process, UFW/systemd service, persistent DEVELOPMENT or separate PRODUCTION change occurred.

**Persistence engineering implication:** Steps 87–91 already checked common UFW saved sources/hooks, selected systemd/cron startup references and direct Docker/UFW ordering, and **did not establish automatic restoration** after reboot, Docker chain rebuild, or UFW reload. Repeating the same static inventory will not prove persistence. PR #39 contains a **review-only, uninstalled** systemd restore template and a read-only guard, but it does not enforce an unbypassable per-launch guard or Squid outgoing egress policy. Its pre-existing original-lab `ccpc_codex_dev_lab_firewall.sh` declares temporary rules; unscoped use of its `rollback` can remove protective rules and is not authorized.

**Next meaningful gate:** Design and review an idempotent, exact-rule, fail-closed original-lab firewall persistence/install transaction and a separately verified **manual Codex launch gate**. Prove recovery/rollback boundaries and that a firewall reload or daemon reinitialization cannot permit Codex to continue running with missing rules. A privileged Docker administrator can bypass a cooperative startup script, so operational restriction/enforcement must be addressed before launch approval. Host changes (UFW/iptables/systemd, reboot, network creation, agent start or proxy image pull) require **separate explicit scoped approval**, admin recovery and negative nonproduction-canary tests. Further host read-only checks may support design only; they cannot alone prove reload persistence. Keep PR #39 open/draft, and **NO-GO** for Codex start.

---

## Step 105 — review-only original-lab restore and offline prelaunch sources (2026-11-20)

**Approval and scope:** Owner replied **“Approved”** to the proposed next engineering phase for firewall restoration and a Codex startup gate after Step 104. All work performed was **GitHub-only code, mocked security tests and documentation**, in the existing Codex draft PR #39 review branch; no SSH connection, server image pull, Docker container start/stop, firewall mutation/UFW reload, systemd installation, marker creation, or DEVELOPMENT/PRODUCTION/UAT operation. Actual host installation remains subject to separately approved exact commands, backups/recovery and rollback review.

**Review-only implementation (confirmed GitHub commits and affected paths):**
- [`7242020`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/7242020d24ee4ff32efd053d77b06688c6e228b5): added `scripts/security/ccpc_codex_lab_firewall_reconcile.py` plus 16 initial mocked tests. The script defaults to read-only `plan`; `verify` performs read-only exact policy checks. A hypothetical `restore` requires root and an exact-content, root-owned restrictive marker at `/etc/ccpc/codex-lab-firewall-restore-authorized`, a lock, and existing stopped-agent/host/UFW/Docker identity checks. It refuses partial/unapproved proxy bridge, duplicate/altered/displaced original-lab tags and unsafe resulting rule precedence; inserts only missing scoped original-bridge rules and checks exact presence and order afterward. There is no global chain flush, Codex start, broad rollback or network recreation.
- [`2814302`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/2814302d064f2510f45b5657d387ac6bd4059d69): added **read-only** `scripts/security/ccpc_codex_lab_start_interlock.py` and 20 mocked tests. It verifies its own separate root-owned offline-launch marker; existing original bridge firewall, stopped agent labels/restart state, nonroot/read-only/no host bind policy, strict existing internal-lab network only, effective memory/PID caps and immutable pinned image reference. It **never starts or stops a container or Codex**, and always prints `agent_launch_authorized=False`. Its constraints purposely **cannot be assumed to pass on the present host** (previous stopped agent image tag mutable, runtime memory limits not installed; historical synthetic secret bind also needs separate assessment).
- [`1c75fbc`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/1c75fbc026d189a7b16b2c910b5f53cfae980a68) and [`4a67885`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/4a678851fd79472333e387e9eb14cddbf6f829d2): added a conservative failure path: if stopped-agent/host prerequisites cannot be reverified during reconciliation rollback, **retain newly inserted restrictive rules** rather than removing them while a potentially running agent could be exposed; added a mock regression. No protection is claimed against concurrent privileged Docker/UFW changes.
- [`54747b9`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/54747b99575966768e1807be55f08c0f37c863ed) and [`0416571`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/04165711e910c286da38cca3c27bf966b202b07a): changed **uninstalled** `systemd/ccpc-codex-lab-firewall-restore.service.example` to invoke new reconciler instead of the older lab firewall script; updated existing inert-unit regression. The template is NOT installed/enabled and does not survive arbitrary UFW/Docker later reload by itself.
- [`5690d27`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/5690d27183619956c6500e73a2525d4030b2b967): documented review-only scope in the Codex README and firewall persistence review, expanded path triggers and an exact-count discovery gate in GitHub Actions, and synchronized the manual-only CircleCI source count to **118**. Draft PR #39 remains open/unmerged at this commit.

**Actual CI proof:** The GitHub-hosted security regression workflow [run `44678949706`](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44678949706) on **exact PR head `5690d27183619956c6500e73a2525d4030b2b967`** reports `status=completed`, `conclusion=success`; the job log verified `118 source-only security regressions discovered`, `Ran 118 tests in 0.020s`, `OK` with no assertion failures. The expanded suite consists of **66 Compose/policy + 15 original-lab guard + 17 reconciler + 20 offline interlock** methods. Tests mock or avoid live firewall/Docker/systemd operations; these are **not** tests of actual host restoration, reload persistence, systemd ordering, concurrent operator starts, kernel enforcement, image provenance, actual resource caps, Squid egress or Codex CLI sandbox/auth.

**NO-GO and next priority:** No true fail-closed runtime-continuation mechanism is yet present: a oneshot plus a per-launch check cannot stop a privileged `docker start` or prevent an exfiltration interval if UFW/Docker rebuild destroys the DROP policy while Codex is running. Until stronger host-enforced networking, reliable reload restoration, a controlled supervisor/authority boundary and nonproduction network-canary tests are designed and demonstrated, **do not activate Codex**. The proposed second `proxy_clients` network and Squid's separate outgoing/DNS path remain unverified and must not be created/enabled. Before any host mutation, review SSH recovery, root-controlled source/install permissions, precise service unit dependencies, exact approved commands and rollback that touches only added project artifacts. The user-approved engineering work did not constitute approval of those host operations.

---

## Step 106 — independent nft deny-layer reviewed and native syntax-tested (2026-11-20)

**Owner authorization and boundary:** After the previously reviewed 118-test restoration/offline-interlock milestone, owner approved continued work on runtime protection and verification of recovery across firewall reloads. This session performed **GitHub code/docs work and hosted disposable CI only**. No ChatGPT SSH or Docker host access, no UFW/nftables/iptables/systemd/kernel rules modified on ccpcerpserver, no reload/reboot, no Codex or Squid start, no DEVELOPMENT/UAT or separate PRODUCTION mutation. User has not yet seen or approved exact host installation/reload commands or recovery steps.

**Source milestone:** Added review-only **scripts/security/ccpc_codex_nft_guard_review.py**, a pure renderer and read-only exact JSON verifier for a candidate separate **nftables inet ccpc_codex_lab_guard** table with input, output and forward hook chains at **priority -301**, and four restrictive interface-name DROP rules limited to the verified original-lab bridge. It has no installer, apply, reload, delete or container-start mode. Uses the strict existing host/stopped-agent/iptables prerequisites. Updated the existing **read-only** scripts/security/ccpc_codex_lab_start_interlock.py to require the separate nft layer and fail closed if missing. Added 20 nft-layer mock tests and one startup-interlock failure regression, total **139 tests** (66+15+17+21+20); synchronized GitHub Actions, optional manual CircleCI discovery counts and workflow path trigger. GitHub commit [5dd2cfa](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/5dd2cfae04243d0276ae7c7aac87c34b2ef318c7). A later GitHub code-only correction aligned the 139-discovery error message ([6b1359e](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/6b1359e2cca5850b62a457ba69a3e102c8e99a7b)).

**Executed CI evidence:**
- [Run 44680095608](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44680095608): 139/139 source-only Python tests passed at code commit 5dd2cfa.
- [Run 44680327848](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44680327848), at exact CI/source commit **1c2f1f0195c068f3fe4d119b144d28dc50fe5190**: run status completed/conclusion success, decoded job logs include **nftables_check_only_candidate_syntax_passed=True**, **Ran 139 tests in 0.025s**, **OK**. It installed nftables only on GitHub's throwaway Ubuntu runner and used **nft --check --file -** with a synthetic bridge name, causing *no applied rules*. The CI configuration addition itself is commit [1c2f1f0](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/1c2f1f0195c068f3fe4d119b144d28dc50fe5190).
- On PR #39, the follow-on docs-only change ([afbada1](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/afbada19080618a66712568b4e790f6156051797)) appends Step 106 to docs/ccpc-project/CODEX-LAB-FIREWALL-PERSISTENCE-REVIEW.md without altering tested security code.

**Crucial engineering limit:** The separate inet nft DROP table is a *candidate independent kernel enforcement layer*, not an installed persistent policy. It could be lost on **nft flush ruleset**, nftables.service reload (depending on host config) or bridge recreation; ordinary UFW/Docker reload retention has **not** been tested. Docker bridge traffic may have different hook behavior than the simulated matcher assumptions; no host firewall negative canary or reload scenario has executed. No privileged Docker authorization plugin, unbypassable agent launch path, zero-gap dynamic defense or verified Squid egress exists. Both original and independent protection would need fresh host verification under failure conditions before agent start. Keep **Codex activation NO-GO**.

**Next operator step:** A read-only, sanitized host check while Codex is stopped: verify nft command/kernel availability, syntax-only candidate using nft --check (without installation), whether the named table already exists, the enabled/active nftables.service state, and whether the main nftables config contains a flush ruleset directive. Do not send raw firewall tables, network identifiers, credentials or paths beyond known project names into public logs. Then plan *separately approved* installation with two SSH/recovery sessions, private baseline snapshot, strict rollback scope, offline negative canaries and guarded UFW/Docker reload tests. A successful read-only preflight is **not authorization to install, reload or start**.

---

## Step 107 — target-host nftables compatibility and global-flush hazard (2026-11-20)

**Source of evidence:** Owner pasted stdout of the specifically requested *read-only* `sudo python3` nftables preflight on `ccpcerpserver`. ChatGPT has no SSH connection and did not independently execute this host code. The output, sanitized to booleans, was:

```text
main_nft_config_flush_ruleset=True
main_nft_config_has_includes=False
agent_stopped=True
original_bridge_identity_verified=True
independent_nft_table_already_present=False
nft_userspace_and_kernel_query_available=True
nft_candidate_check_only_passed=True
nftables_service_active=False
nftables_service_enabled=False
nft_reload_persistence_verified=False
ufw_docker_reload_persistence_verified=False
agent_launch_authorized=False
NO_HOST_CHANGES_PERFORMED
```

**Interpretation:** The original agent was stopped with known Docker/bridge identity at that instant. The host's native `nft` tool accepted the independent rule candidate in **check-only** mode; the review table does **not exist** in the active kernel ruleset, so no independent protection is currently enforced. The *main* `/etc/nftables.conf` contains an uncommented **`flush ruleset`** directive (per bounded Python grep) and has no top-level active `include` line. The `nftables.service` is currently **inactive and disabled**. These results **do not prove** how `systemctl start/reload/stop nftables` or any other wrapper will behave, but if a future command loads the main file with `nft -f`, its global flush can erase nftables rulesets managed by UFW and Docker (which may share the nf_tables kernel backend), cause downtime or remove Codex protections. No reload/reboot persistence or live packet blocking was verified, and a successful `nft --check` is not evidence of applied rules.

**Operational hold:** Do **not** enable, start, reload, restart or stop `nftables.service` or execute `nft -f /etc/nftables.conf`; do not run `nft flush ruleset`, `ufw reload`, `systemctl restart docker` or create/attach/start the Codex network/agent. Do not modify `/etc/nftables.conf` as a shortcut, nor rely on the nftables service for persistence without first inspecting its **effective systemd ExecStart/ExecReload/ExecStop** properties, their input file usage and how they interact with UFW and Docker. The previous original-lab INPUT and DOCKER-USER rules were verified present/ordered in Steps 103–104, but not now rechecked; do not treat those historical observations as a runtime safety guarantee.

**Preferred next step:** Operator-run **read-only**, fail-closed, sanitized effective-unit inspection for nftables.service, UFW and Docker service entrypoints/hook ordering and configuration loading. This must use only `systemctl show`, bounded existence/regular-file checks and no printing of raw service commands, IP addresses, filesystem secrets, network IDs or rules. The relevant property checks can narrow the hazard; no snapshot alone proves reload survival. After that, compare safe scoped independent-table installation options **without activating the stock nftables.service**, require a separate recovery+rollback plan, second SSH session and explicit approval of exact host mutation commands. Static code changes remain draft PR #39, and **Codex launch NO-GO** persists.

---

## Step 108 — effective nftables unit loads and flushes global ruleset (2026-11-20)

**Evidence provenance:** Owner pasted the sanitized result of the immediately preceding `python3` read-only `systemctl show` inspection on `ccpcerpserver`; ChatGPT has **not** directly executed any command on that host. The inspection classified the service's effective `ExecStart`, `ExecReload`, `ExecStop`, direct `Requires/Wants/After` dependencies and drop-in state; it did not print raw unit commands or execute them.

```text
nft_service_active=False
nft_service_enabled=False
nft_start_loads_main_config=True
nft_reload_loads_main_config=True
nft_stop_flushes_ruleset=True
nft_service_has_dropins=False
docker_directly_depends_on_nftables=False
ufw_directly_depends_on_nftables=False
effective_unit_properties_inspected=True
reload_persistence_verified=False
agent_launch_authorized=False
READ_ONLY_CHECK_COMPLETE
```

**Combined with Step 107:** The main nftables configuration contains an active `flush ruleset` directive, and the effective `nftables.service` `ExecStart` and `ExecReload` reference that main configuration; the effective `ExecStop` contains `flush ruleset`. The service is currently **inactive and disabled**, has no observed drop-ins, and the inspected Docker/UFW units have no direct declared `Requires/Wants/After` dependency on nftables.service. This makes the **stock nftables.service unsafe as an installation/reload path** for the proposed CCPC table while UFW/Docker manage other rules: starting/reloading could flush the global ruleset via the main file; stopping could do the same via ExecStop. These read-only booleans do not establish the impact of an actual service action, nor exclude transitive dependencies, out-of-band commands, or other firewall controllers. No active CCPC independent nftables table was found at Step 107. The original iptables laboratory rules were previously checked at Steps 103–104, not rechecked here.

**Design decision:** **Do not use or enable the stock nftables.service** and do not edit its main global-flush file as a shortcut. For a separately authorized next review phase, prefer a **dedicated, root-owned, CCPC-scoped nftables table controller** which reads only an immutable, reviewed per-project policy; never uses `flush ruleset` or `nftables.service`, never touches UFW/Docker-owned tables, and verifies table identity before any mutation. It must have no broad stop/remove handler, be idempotent and fail closed when unexpected rules/table exist, and refuse action unless Codex is stopped with automatic restart disabled and the correct bridge identity is verified. Coupling to Docker/UFW boot/reload events must be reviewed independently; a systemd oneshot is **not proof** of reload persistence.

**Unresolved zero-gap problem:** A dedicated CCPC table or service can still be removed by privileged firewall operations or bypassed by Docker network recreation, and no polling watchdog can guarantee zero traffic exposure. Until offline lab network-path denial, reboot/reload survivability, negative non-PRODUCTION canaries, isolated image/resources and operator-override prevention are validated, **Codex activation remains NO-GO**. Do not start, stop, enable, reload or restart `nftables.service`; do not restart Docker, reload UFW, flush any firewall table, or start/attach Codex/Squid.

**Next safe decision:** complete a review-only scoped-service and rollback plan in GitHub, followed by one bounded operator-safe pre-installation inventory of potential systemd-unit/path conflicts and recovery options. **Separate explicit approval** will be necessary for every actual host installation, authorization-marker creation, kernel rule modification or controlled reload, after a second SSH/recovery channel and private firewall snapshot are established.

---

## Step 109 — service name availability, scoped nft source and recovery review (2026-11-20)

**Owner-supplied read-only host checkpoint:** After Step 108 confirmed stock nftables.service references a main global-flush config for start/reload and a global-flush stop action, the owner ran the requested read-only name/path inventory on `ccpcerpserver` and pasted:

```text
agent_stopped=True
dedicated_nft_unit_name_available=True
offline_launch_unit_name_available=True
review_install_directory_already_exists=False
host_changes_performed=False
codex_launch_authorized=False
READ_ONLY_CHECK_COMPLETE
```

This proves **only** that the operator's sanitized diagnostic found the agent stopped, proposed systemd unit names unused and the prospective review path absent at that instant. It is not permission to install, reserve the paths permanently, or start containers. ChatGPT has **no SSH access** to the host; no local host modification occurred.

**GitHub engineering on existing PR #39 branch:** At [commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/66960f73a69b10b59f508cda7bfd4ac9ea5c21af), added:

- `scripts/security/ccpc_codex_nft_scoped_controller.py`: root-only controller with **read-only `plan` and `verify`**, and review-only uninstalled `install` gated behind a separately created exact-content, root-owned, owner-only marker `/etc/ccpc/codex-lab-nft-guard-authorized` plus a root-owned lock. It reuses strict original Docker/host identity, stopped agent, original three iptables rules/precedence and requires stock nftables.service **inactive and disabled**. Uses `nft -j list tables` to reject ambiguous/colliding existing table identity. If the named independent table is already present and exact, it makes no changes; unknown contents fail closed. If absent, it native-checks `render_candidate` and submits **one `nft --file -` transaction** comprising only the reviewed `inet ccpc_codex_lab_guard` table, then re-verifies exact contents and stopped agent. It **does not** read/run `/etc/nftables.conf`, call stock nftables.service, flush any shared ruleset, change existing UFW/Docker tables or start Codex/Squid. Failure after applying a table does **not** automatically remove restrictive DROP rules.
- `scripts/security/systemd/ccpc-codex-nft-guard.service.example`: manual-only and **uninstalled** sample unit, with `plan → install → verify`, **no `[Install]` section and no ExecStop/ExecReload**; actual ordering, parser compliance and on-host service installation remain untested. Its existence in GitHub is **not a scheduled/persistent service**.
- `codex-dev-agent/tests/test_scoped_nft_controller.py`: 22 mock-only tests covering absent/exact/foreign table, nftables-service state, no unauthorized installation, atomic project-only command shape, rollback safety, bridge recreation, refusal of unsafe modes and inert unit structure.
- `.github/workflows/codex-lab-static-review.yml` and default-off `.circleci/config.yml` now expect **161 discovered source-only regression tests**; GitHub Actions also keeps the already verified native syntax-only `nft --check` step.

**Successful CI at exact code commit:** [GitHub Actions run 44684035488](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44684035488) `completed/success` and actual decoded job log includes `161 source-only security regressions discovered`, `nftables_check_only_candidate_syntax_passed=True`, `Ran 161 tests in 0.017s`, `OK`. These are **mock/static tests**, not an actual nft install, systemd execution, negative packet test, or reload/reboot persistence verification.

**Documented host installation/recovery design:** [PR head commit `f3b26fb2ebcc5189625cf131cc8454d40f131c93`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/f3b26fb2ebcc5189625cf131cc8454d40f131c93) adds `docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md` and updates the Codex README and firewall persistence design review. The **exact PR-head** hosted GitHub Actions [run 44684328438](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44684328438) completed **success**: source discovery **161**, native nft check-only PASS, **161 tests OK**. The recovery document outlines root-owned verified/pinned source, a private firewall state snapshot, two independent SSH/admin recovery channels, exact-table-only application, failure preserving restrictive protection and removal only of newly installed project artifacts under a separate reviewed operation.

**Limits and release disposition:** This is source-tested **project-scoped table installation logic only**, not a live persistence/reload solution. A one-time service call cannot guarantee uninterrupted filtering after UFW/Docker/nftables reload, Docker network recreation or privileged manual agent start. There is **no demonstrated zero-exposure runtime containment** or approved offline/online Codex launch. The original bridge may be recreated and change its interface name, the stock nftables global flush could erase a table, the target host `nft -j` output may differ from mocks, and Squid's separate outbound network is unverified. The agent was last observed stopped; this session did **not** install markers, create directories, write kernel firewall rules, pull Docker images, change DEVELOPMENT/UAT, or touch separate PRODUCTION. **Codex activation remains NO-GO**. Next work requires an operator-approved command-level host installation and recovery procedure plus controlled negative-canary and reload tests, or choosing a dedicated Codex VM/host to avoid shared-host policy continuity risk. Do not advise stock nftables.service start/reload/stop, UFW reload, Docker restart, or agent activation without separate owner authorization and recovery planning.

---

## Step 110 — second administrator recovery connection confirmed; Stage A private baseline awaits explicit approval (2026-11-20)

**Owner attestation:** After Step 109, the owner replied **“confirmED”** to the request to verify that a second independently working administrator SSH/recovery connection to `ccpcerpserver` exists while the original session remains open. This is **operator-reported**, not an assistant-run connectivity test or a demonstrated out-of-band console in a total network failure. There is no stated authorization yet for privileged filesystem writes, kernel changes or startup; **Codex remains stopped and NO-GO**.

**Exact reviewed GitHub state:** Draft [PR #39](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/39) retains scoped nft source, review-only service template and 161 mocked security tests. Last verified code+docs checkpoint `f3b26fb2ebcc5189625cf131cc8454d40f131c93` passed source-only GitHub Actions [run `44684328438`](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44684328438), with native `nft --check` on a disposable runner. This is not live host isolation/persistence evidence.

**Next scoped decision — Stage A only:** The revised [installation and recovery review](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/codex-proxy-network-hardening-2026-11-19/docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md) at review commit `5d03a5a01b2795c4c9fdb3f70bad19d20efe7da0` contains an **exact proposed, but NOT YET APPROVED** root-only host baseline capture: stopped-agent/restart disabled and stock `nftables.service` inactive/disabled checks, then writes private `iptables-save`, `ip6tables-save`, `nft -j list ruleset`, routing and service-state reference files under a newly created root-owned `/root/ccpc-codex-nft-preinstall.XXXXXXXX` directory with mode restricted by umask. It would make a small local filesystem write but **no iptables/nftables kernel mutation, systemctl action, Docker restart, service enablement or Codex start**. Raw snapshots must remain private on-host; they are **not safe to upload to this public GitHub repository or chat**, and must not be restored wholesale over UFW/Docker. A partial directory may remain if the snapshot aborts. The script is for command-level owner approval **before** use.

**Later stages remain unapproved:** immutable/pinned source staging, install-path ownership, root authorization marker creation, single project-only nft table installation, separate manual-only unit, controlled negative non-PRODUCTION canaries and UFW/Docker reload/reboot validation each require scope-specific approval and recovery verification. **Do not enable or start/reload/stop stock nftables.service** given its global-flush configuration; do not activate Codex/Squid. A second SSH session does not alone prove zero-gap runtime network isolation.

---

## Step 112 — private firewall baseline captured, operator-reported PASS (2026-11-20)

**Host evidence provenance:** Under the distinct Stage A approval from Step 111, the owner ran the pre-approved, bounded `sudo bash` baseline snapshot command on `ccpcerpserver` and pasted exactly:

```text
host_verified=True
agent_stopped=True
private_baseline_saved=True
kernel_rules_modified=False
services_restarted=False
codex_launch_authorized=False
```

**Interpretation:** The script's successful completion means hostname, known stopped Codex agent and no-auto-restart, and inactive/disabled stock nftables.service were tested; then `iptables-save`, `ip6tables-save`, `nft -j list ruleset`, `ip -j route show table all`, and selected systemd service state were written to nonempty files inside a fresh, private directory under `/root` (using `umask 077`). By code inspection the authorized command makes **no kernel firewall writes, daemon restarts, Docker/agent operations, or Codex launch**. ChatGPT did not access the host, independently check the snapshot or prove the files would restore safely; owner reported output is the evidence. Do not upload the private data, credentials, raw firewall configuration, or private path to this public repository or chat.

**Recovery checkpoint:** A second working SSH/recovery session was confirmed by the owner at Step 110. Preserve it while doing any further host work. The snapshots are **reference evidence**, not a reviewed `iptables-restore`/`nft -f` procedure: wholesale restoration could overwrite UFW/DEVELOPMENT/Docker rules.

**Next staged boundary — NOT YET APPROVED:** Stage B may eventually stage only the four reviewed Python source files (`ccpc_codex_nft_scoped_controller.py`, `ccpc_codex_nft_guard_review.py`, `ccpc_codex_lab_firewall_guard.py`, `ccpc_firewall_rule_order.py`) from the verified GitHub code commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`, under a new root-owned non-symlinked review directory, with per-file Git blob SHA verification. **No Python execution, marker, systemd unit, firewall modification, container start, or service reload**. Do not start this stage until explicit owner approval of exact commands and expected filesystem effects; the owner approved Stage A only. Remaining Stage C firewall installation and runtime tests are separately gated. **Codex/Squid activation remains NO-GO**.

---

## Step 114 — Stage B source-only GitHub-pinned files staged, operator-reported PASS (2026-11-20)

**Operator output:** Owner pasted the closing shell heredoc marker and nine expected sanitized success lines from the **separately approved Stage B** command on `ccpcerpserver`:

```text
host_verified=True
agent_stopped=True
source_commit_pinned=True
all_four_git_blobs_verified=True
root_only_review_source_staged=True
firewall_modified=False
services_modified=False
codex_launch_authorized=False
STAGE_B_SOURCE_ONLY_COMPLETE
```

**Verified scope via command review, not direct host inspection:** The approved shell command checked hostname, known stopped/no-restart Codex agent, and stock nftables.service inactive/disabled; required a previously absent final target and root-safe parent; downloaded four Python files from `ccpcerp/ccpc-frappe-deployment` at immutable commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`, verified each with the connected GitHub blob ID using `git hash-object`, set them root-read-only, and atomically renamed the private staging directory into `/opt/ccpc/codex-lab-review`. No staged Python code was executed, no systemd unit or root authorization marker installed, no firewall rules changed, and no Docker/UFW service or Codex/Squid process started by the approved script. ChatGPT did **not** independently re-read the host files or service/firewall state. The earlier Stage A root-private firewall snapshot remains a recovery *reference only*. Preserve second SSH/recovery connection.

**GitHub plan record:** [Step 114 recovery-plan checkpoint](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/6ee6edb73f7e434014ead62a2c9510acc8e22f71) on draft PR #39 review branch. This changes documentation only, not the pinned executable source. Next safe operator command is a separate **read-only post-staging verification**: inspect owner/mode/no-symlink, exact four blobs and commit marker, stopped agent/restart policy, stock nftables.service inactive/disabled, and independent nft table absence; never import/execute staged Python for this verification. Keep raw firewall data, private snapshot paths and credentials out of chat and GitHub.

**Release gate:** **NO-GO**. Stage C kernel table install, authorization-marker creation, systemd unit registration, reload/reboot, network canaries and Codex/Squid start remain **unapproved**. Staging does not provide active independent firewall protection or zero-gap continuity.

---

## Step 115 — read-only independent staged-source verification STOP; cause unknown (2026-11-20)

**Owner-supplied host evidence:** After Step 114 reported source-only Stage B PASS, the owner executed the supplied **read-only** post-staging `sudo python3 -I` inspector. Output contained the generic failure message `STOP: Stage B post-staging verification failed` (preceded by the pasted command's `except Exception` clause). The broad exception handler did not reveal which predicate failed. No raw config, credentials or firewall contents were sent. **This does not establish whether staging, file ownership, exact Git blobs, stopped agent, nftables.service, or table-absence checks caused the STOP.** No server code or firewall was changed by this inspector, and ChatGPT has no direct SSH session.

**Decision:** Stage C is **blocked**. Preserve staged files and Stage A private baseline; **do not** rerun Stage B, change file permissions, delete root-only paths, create the root nft approval marker, run `nft -f`, install units, restart Docker/UFW, or launch Codex/Squid. The next permitted step is a fixed-stage, sanitized **read-only** diagnostic reporting the first failing check label without printing sensitive contents. The [scoped install and recovery review](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/codex-proxy-network-hardening-2026-11-19/docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md) was updated in [commit `7eb85cf`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/7eb85cf13baf77b804b988f0b309d04f587e352e).

---

## Step 116 — staged-source first-failure diagnostic PASS; prior STOP unexplained (2026-11-20)

**Host evidence from owner:** The owner ran the previously supplied read-only labelled diagnostic and pasted `ALL_STAGED_SOURCE_CHECKS_PASSED=True`, `NO_CHANGES_PERFORMED=True`, `STAGE_C_AUTHORIZED=False`, `READ_ONLY_DIAGNOSTIC_COMPLETE`, preceded by `PY` (the here-document terminator). No `FIRST_FAILED_CHECK` label was reported.

The Python script's successful path verified root and `ccpcerpserver` identity, stopped/no-restart agent, all required review-directory ancestry/ownership/mode and exact four file entries, pinned Git commit marker, all four exact source blob hashes with 0400 root-owned file permissions, stock nftables.service inactive and disabled, and the absence of the CCPC independent nftables table. It **never imports or executes staged Python** and performs no kernel/file/service mutations. Evidence is **operator-reported**, not a direct ChatGPT host inspection.

The earlier generic `STOP: Stage B post-staging verification failed` has no known cause, and the later successful diagnostic does not retroactively explain it. At this observed moment Stage B verification passed all independently labelled checks; **no changes or repairs were made**. The recovery review [Step 116 commit `8e50f3e`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/8e50f3e43402796dcf9360b95b1ebb52affc5b1c) records the same evidence.

**Next:** Only a separately reviewed, read-only **staged controller `plan`** execution could check the actual original three firewall rules/current bridge by running pinned code with Python bytecode writes disabled. A read-only `plan` result would not authorize firewall installation. **No authorization marker, nftables installation, systemd registration, Docker/UFW reload, reboot, Codex/Squid start, or PRODUCTION/DEVELOPMENT operation is approved. Codex stays NO-GO.**

---

## Step 117 — owner approves read-only staged nft controller plan (2026-11-20)

Following the operator-reported success of Step 116 read-only per-check verification, the owner replied **“Approved”** to a strictly **read-only staged controller `plan`** execution on `ccpcerpserver`, with Python `-B` to suppress bytecode creation. The exact single command is recorded in [review-plan Step 117](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/review/codex-proxy-network-hardening-2026-11-19/docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md), GitHub commit `d97282e747fd3463905eb536996633ae1dcfba4f`.

**Approval is not execution:** No operator result has yet been received, no new host changes are claimed, and no live nft firewall installation or isolation is confirmed. The exact original host/bridge/iptables and stock nftables.service checks are read-only; expected absent-state output is `PROJECT_NFT_TABLE_STATE=absent`, `agent_launch_authorized=False`, `reload_reboot_runtime_enforcement_verified=False`, `INSPECTION_COMPLETE`. Any failure is STOP for review. Owner has **not approved** creating authorization markers, applying firewall rules, registering/enabling systemd units, restarting Docker/UFW, rebooting, launching Codex/Squid or touching DEVELOPMENT/PRODUCTION. Codex remains **NO-GO**.

---

## Step 118 — staged controller plan PASS; no install authorized (2026-11-20)

**Owner-run preflight output:** After explicit Step 117 approval for **read-only `plan`**, the owner ran the staged pinned controller on `ccpcerpserver` and pasted exactly:

```text
PROJECT_NFT_TABLE_STATE=absent
agent_launch_authorized=False
reload_reboot_runtime_enforcement_verified=False
INSPECTION_COMPLETE
```

The reviewed controller `plan` verified the intended root/host and Docker network identity, known original-lab bridge, stopped/no-restart Codex agent, UFW active, exact original three iptables DROP rules and safe precedence, stock nftables.service inactive/disabled, and absence of the project-specific `inet ccpc_codex_lab_guard` table. **Read-only guard PASS at this point in time** is supported by operator-supplied status output; ChatGPT did not directly access the host. The earlier Stage A private snapshot and verified Stage B source hashes remain the owner-reported recovery/staging checkpoints.

**Not established:** The separate nft table is **not installed**. No actual kernel isolation, negative network canaries, Docker/UFW reload/reboot persistence, source runtime safety or zero-gap launch enforcement has been shown. The apparent success does **not** authorize any code installation or Codex/Squid start. There was no host mutation in the approved `plan` call.

**Next decision:** Draft a separate **exact, scoped Stage C installation command** which verifies the immutable four-file source, checks restrictive and non-symlinked marker directory, keeps stock nftables.service disabled, applies only one new owned CCPC nft table through the independently approved controller, verifies host health and exact rules, revokes the temporary authorization marker, and leaves project DROP rules in place on unexpected errors while Codex remains stopped. Command execution requires the owner's **separate explicit approval** and an independently working recovery session plus private baseline. Do not run `nft flush ruleset`, restore the whole firewall baseline, restart Docker/UFW or start Codex. Reboot/reload continuity and Codex runtime safety remain **NO-GO**.

Recorded also in [Step 118 scoped recovery plan](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/988bbe859263a7f3084ad09426c2d3c41235ab50).

---

### Step 118 supplement — unapproved one-table Stage C command review

Following owner-reported read-only controller `plan` PASS, the review branch added a **NOT APPROVED** exact Stage C single-project-table installation proposal in `docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md`, finalized at [commit `01dfeac`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/01dfeace8dda154d32e2260d61f0d3388644ce2d). **This is documentation only** and not a performed host operation. It rechecks pinned source blobs, agent-stopped controller plan and private baseline existence, rejects any existing authorization marker, optionally creates a root-controlled `/etc/ccpc` directory, installs a **temporary** strictly permissioned marker, invokes the reviewed controller's `install` mode (one new inet table only), independently re-verifies the exact table and Docker/UFW availability, then removes the marker on normal completion or caught failure. Controller code itself remains unchanged and mock-tested; the newly proposed wrapper has not been executed on a host. A hard interruption may leave an authorization marker, and a post-transaction failure can leave restrictive rules—**do not blindly rerun or automatically roll back**.

**Approval and operational hold:** The user's prior approval was `plan` only. The new proposed Stage C kernel firewall operation is **not authorized**. It can affect legitimate host-to-synthetic-lab communications, is not reboot/reload persistent and does not prevent privileged manual Docker starts or validate Codex. Keep Codex/Squid stopped, stock nftables.service inactive/disabled, second independent SSH recovery access available, and Stage A private snapshot unshared. Real negative canaries and scoped table-only recovery need separate review. The original bridge and existing UFW/Docker rules must not be globally flushed.

---

## Step 119 — owner approval for exact, bounded single-table Stage C nft install; not yet run (2026-11-20)

**Explicit owner approval recorded:** After Stage 118 reported `PROJECT_NFT_TABLE_STATE=absent` from the **read-only** controller `plan`, the user explicitly said **“Approved”** to the already linked [proposed exact Stage C single-project-table installation procedure](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/01dfeace8dda154d32e2260d61f0d3388644ce2d/docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md). This allows the specific reviewed script, **once on `ccpcerpserver`**, and **nothing else**. Exact approval was checkpointed in review PR #39 branch [commit `837a2bb0f40309ff48418d3d147c6f57cbe5ebb4`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/837a2bb0f40309ff48418d3d147c6f57cbe5ebb4).

**Mutation scope, not execution:** The command would recheck four pinned source hashes, root/stopped agent and original IPTables through the controller `plan`, private snapshot presence, and disabled/inactive stock nftables.service; create a distinct temporary root marker; call only the reviewed controller's `install` for **`inet ccpc_codex_lab_guard`** with four lab-bridge-specific DROP rules; verify the table and UFW/Docker state; and remove the temporary marker on its normal completion/error-handling path. The kernel table installation is a **real active firewall write**, potentially interrupting legitimate host-to-original-lab connections. Avoid global nft flushes, stock nftables.service, Docker/UFW reload/restart and any Codex/Squid agent starts. The second operator-confirmed SSH recovery connection and Stage A private firewall snapshot must remain available. If any unexpected STOP/interruption occurs, do not rerun, clear rules or restore a whole ruleset automatically; independently inspect table and marker before a separately approved scoped rollback.

**Execution status:** The user has **approved**, but has **not yet provided the installation's terminal output**. ChatGPT has **not installed any firewall table or logged into the host**. A future success status from the owner would be only initial installation and exact readback—not proven packet-blocking, reboot/reload persistence, uninterrupted isolation, privileged manual-start prevention, or Codex runtime security. **Codex activation stays NO-GO**. Approval does not extend to systemd unit install/enablement, PRODUCTION/DEVELOPMENT, reboot, UFW/Docker changes, network canaries, Squid or Codex launch.

---

## Step 120 — independent CCPC nft firewall table installed, operator-reported PASS (2026-11-20)

**Operator's exact sanitized final output of separately approved, once-only Step 119 installation on `ccpcerpserver`:**

```text
source_hashes_reverified=True
private_baseline_reference_present=True
project_nft_table_installed_and_exact=True
temporary_authorization_marker_removed=True
ufw_and_docker_still_active=True
codex_launch_authorized=False
reload_reboot_persistence_verified=False
STAGE_C_ONE_TABLE_ONLY_COMPLETE
```

**Current evidence:** The owner explicitly executed the reviewed script and reported full successful completion. The exact source hash checks, root-private baseline existence, scoped CCPC table installation and exact validator readback, authorization-marker removal, and continuing UFW/Docker active state are evidenced by the approved command's success path. This represents the **first reported actual kernel nftables mutation** in this security review: installing **only** the project-controlled `inet ccpc_codex_lab_guard` table containing four original-bridge-specific DROP rules. The operator output does **not** prove uninterrupted legitimate traffic, negative packet isolation, permanence after UFW/Docker reload or reboot, or isolation from privileged manual Docker agent starts. ChatGPT did not run any host commands or independently inspect the kernel. The [Step 120 recovery record](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/2cda65b32a72ae11ea508b025f00a3ed5c375bca) is the paired checkpoint.

**Post-install operating hold:** Keep the operator-confirmed second working administrator SSH connection available, Codex stopped with no restart, and private Stage A firewall reference files on host. The temporary root installation marker was reported absent at the end, but its current absence awaits a fresh read-only verification. Do not delete or flush the newly installed table, globally restore the baseline or alter UFW/Docker or stock `nftables.service`. The scoped controller remains manual-only; no systemd service/persistence hook was installed. Next owner step is an independently initiated **read-only** check of table identity and exact rules/chain count, original lab stopped state, stock nftables.service inactive/disabled, UFW/Docker active and marker absence, plus confirmation that both SSH sessions are healthy. On any anomaly STOP and do not rerun Stage C or attempt an unapproved rollback.

**Unresolved release gates:** Controlled synthetic-only packet-path negative canaries, legitimate lab service continuity checks, reload/reboot preservation, bridge-name-recreation handling, separate proxy egress isolation, digest/resource/secret binding, and prevention of privileged manual agent start are all unverified. **Codex/Squid activation NO-GO**. PRODUCTION remains outside the authorized scope, and do not modify DEVELOPMENT services without separate specific approval.

---

## Step 121 — operator-reported independent nft post-install read-only verification PASS (2026-11-20)

After Stage C reported a live CCPC-only nft table install at Step 120, the owner ran the separately provided **read-only** post-install verification command. Exactly these nine sanitized status lines were supplied:

```text
PROJECT_NFT_TABLE_VERIFIED=True
ORIGINAL_FIREWALL_GUARDS_VERIFIED=True
TEMPORARY_AUTH_MARKER_ABSENT=True
UFW_DOCKER_ACTIVE=True
AGENT_STOPPED=True
STOCK_NFT_SERVICE_INACTIVE_DISABLED=True
HOST_CHANGES_PERFORMED=False
CODEX_LAUNCH_AUTHORIZED=False
READ_ONLY_VERIFICATION_COMPLETE
```

**Evidence and scope:** The one-time independent read-only check confirmed the staged controller's Git blob, original stopped agent with no restart, no persistent install marker, stock nftables.service inactive/disabled, UFW/Docker active, the staged controller's `verify` JSON exact match, and a separate `nft -j list table inet ccpc_codex_lab_guard` structural check: exactly one project inet table, three expected named chains (`input`, `output`, `forward` hooks; priority -301) and four DROP rules. This is **operator-reported successful command output**, not direct ChatGPT SSH access or packet-flow verification. No changes were made by the inspection. Recorded with matching [Step 121 recovery-plan commit](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/895cc4fde4554b5f0488fdeb6bf4505d15a8e6c3).

**Critical outstanding prerequisites:** The owner previously confirmed a separate active administrator SSH connection but has **not yet reconfirmed that it still works after the new kernel rules**; check before any traffic test. Real traffic-denial and allowed-path negative/positive canaries, DEVELOPMENT/UAT service continuity, IPv6 coverage, UFW/Docker reload and reboot persistence, Docker bridge recreation handling, and privileged manual-launch bypass remain **NOT TESTED**. The project's table cannot be treated as ongoing reload/reboot enforcement, and `CODEX_LAUNCH_AUTHORIZED=False` remains. No network probes, systemd changes, firewall rollback, reload/restart, Docker/agent/Squid start, or PRODUCTION/DEVELOPMENT modifications are approved. Prepare a bounded **synthetic-only canary proposal with both allowed and forbidden paths** for separately reviewed user authorization. Preserve Stage A private snapshot, independent SSH access, original lab stopped state and stock nftables.service inactive/disabled. **Codex activation remains NO-GO.**

---

## Step 122 — second admin SSH recovery session reconfirmed after nft installation (2026-11-20)

**Operator's direct reply:** The owner answered **“Confirmed”** to the specific Step 121 post-install question asking whether the independent second administrator SSH connection to `ccpcerpserver` still works after the newly installed CCPC nftables table. This is operator-attested current accessibility, not ChatGPT-run SSH inspection or a guaranteed out-of-band link. The original SSH and second administrator recovery session should both remain open. The private Stage A baseline has not been exposed or used for global restoration.

**Current known host checkpoint:** Step 120 reported `inet ccpc_codex_lab_guard` installed via separately approved exact code; Step 121 reported independent read-only exact table structural/content verification and other UFW/Docker/iptables/agent state checks. The latter status predates this reconfirmation, so it is not a guarantee after any later reconfiguration. The new second-SSH confirmation involves no firewall, service, Docker, or Codex change.

**Next read-only inventory, not active network test:** Review original Docker lab network identity, existing original stopped Codex agent and synthetic DB/Redis container states using only bounded, sanitized Docker inspections. The review branch's `codex-dev-agent/compose.yaml` includes un-deployed network/proxy proposals; do not mistake it for live host topology. No `docker exec/run/up`, traffic probes, DB authentication or access to DEVELOPMENT/PRODUCTION. Prepare future **synthetic-only, positive and negative canary tests** to assess exact allowed and prohibited packet paths, but obtain separate exact-command approval before running them.

**Still NO-GO:** Codex/Squid startup, proxy bridge configuration, nftables persistence service, stock nftables.service start/reload/stop, UFW/Docker reload/restart, reboot, lab/DEVELOPMENT/PRODUCTION mutations, or firewall rollback. Neither reload/reboot continuity nor zero-gap launch isolation has been proven. Paired [Step 122 recovery checkpoint](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/1eeb99a2e143e94563e053f734b8123020af82b9).

---

## Step 123 — original laboratory topology read-only check passed; Step 124 IPv4 canary proposed (2026-11-20)

**Owner-supplied Step 123 stdout from separately presented read-only Docker topology inspector:**

```text
ORIGINAL_LAB_NETWORK_VERIFIED=True
LAB_BRIDGE_PRESENT=True
SYNTHETIC_DB_REDIS_CONTAINERS_RUNNING=True
CODEX_AGENT_STOPPED=True
NETWORK_PROBES_PERFORMED=False
HOST_CHANGES_PERFORMED=False
CODEX_LAUNCH_AUTHORIZED=False
READ_ONLY_TOPOLOGY_COMPLETE
```

**Meaning:** On `ccpcerpserver`, the exact command validated expected Docker network `ccpc_codex_dev_agent_lab` internal bridge, IPv4 subnet/gateway identity, actual Linux bridge device, presence of four known project containers, stopped/no-auto-restart Codex agent and running `db`, `redis-cache`, `redis-queue` synthetic containers attached to the intended lab. This is an **operator-reported read-only observation**, not a direct ChatGPT host inspection or traffic test. Second administrator SSH recovery session was separately reconfirmed after nft installation in Step 122. The Stage A private baseline remains available on host, but must not be globally restored without review.

**New next proposed step, separately gated:** The review plan at [Step 123 and Proposed Step 124 commit `7b80866`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/7b80866b54bb72d9d97c05ba5942c49ba4093d89) contains an exact **NOT APPROVED** synthetic Redis IPv4 canary script. It checks pinned source hashes, project nft table exact, no marker, stopped agent, and correct Docker lab/Redis identity before (a) running an existing same-bridge Redis `PING` from `redis-cache` to `redis-queue` (positive control), (b) attempting exactly one host TCP connect to that same synthetic `redis-queue:6379` target (expected denial, no auth or payload, 2-second timeout), then (c) checking that same-bridge Redis remains reachable and guards remain exact. It prints fixed pass/fail labels without disclosing IPs, credentials or business information.

**Boundaries:** The test is active traffic and a small ephemeral process via `docker exec`; it has not run and is **not** covered by prior source-staging or firewall-install approvals. It only compares one same-bridge allowed path against one host-to-lab denied IPv4 TCP path; it cannot attribute packet drops to a particular nft/iptables/UFW rule and does not prove lab-to-host, inter-bridge, IPv6, reload/reboot or prevention of manual privileged Docker starts. It must not start/restart containers, alter rules, connect to UAT/DEVELOPMENT/PRODUCTION or invoke Codex/Squid. Ask owner for **separate approval of the exact Step 124 test command** before sending executable steps. **Codex activation remains NO-GO.**

---

## Step 124 — exact bounded synthetic Redis canary approved, operator run pending (2026-11-20)

**Owner authorization:** After the read-only Step 123 original laboratory topology PASS, the owner expressly replied **“Approved”** to the exact proposed Step 124 synthetic-only active IPv4 Redis positive/negative test. The separate approved procedure is on review PR #39 at [commit `24a7952`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/24a79526255607c449052f5d99fd986875d4dbaa). No host result has been received and ChatGPT has no direct SSH access: **approval is not execution or evidence of packet isolation**.

**Approved action boundary:** On `ccpcerpserver` only, with both administrator sessions and private baseline available, the exact one-time script rechecks pinned GitHub source hashes and deployed original-lab/current nft policy identity; verifies agent stopped/no restart, existing internal Docker bridge `ccpc_codex_dev_agent_lab` and lab-only existing Redis service identities; then executes only `redis-cli PING` twice from running synthetic `redis-cache` to running synthetic `redis-queue`, wrapping one bounded host IPv4 TCP connect attempt to the same synthetic Redis-queue port 6379, with 2-second timeout and no data payload. STOP if the positive control fails, if the host connects, or if the firewall/agent drifts. No new/restarted containers or services, no new policy/authorization marker and no DEVELOPMENT/PRODUCTION or other routes/ports are touched by the script.

**Evidence limits:** This checks a narrow representative allowed Redis bridge path plus a host-to-lab blocked path; timeout/route denial can reflect overlapping existing iptables/UFW controls rather than just new nft table. It cannot certify other traffic paths, IPv6, reload/reboot persistence, ongoing zero-gap safety or readiness to run Codex. Output must remain sanitized fixed status labels; on failure do **not** rerun blindly or weaken firewalls. Keep Codex/Squid **NO-GO**.

---

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

## Step 33 — optional egress proxy Compose service (2026-11-19)

The operator used a hostname-guarded, read-only lookup of the one additional service in the current Compose source. Sanitized result: `extra_service_count=1`, `service_name=egress-proxy`, `optional_profile=True`, `image_declared=True`, `build_declared=False`. The source therefore defines a fifth service named `egress-proxy` with one or more Compose profiles and an image reference rather than a local build declaration.

**Interpretation:** An opt-in/profile-gated service may be used as an outbound access path, but this inspection did **not** establish whether it is running, whether it is connected to the lab or other Docker networks, or whether its configuration enforces egress policy. Compose profiles ordinarily exclude the service from default `up` unless the profile is enabled or the service is directly targeted. The currently active state and any host/protected-network reachability must be verified separately without launching the proxy or Codex.

**Operator preference carried forward:** prioritize maximum possible Codex CPU performance; resource controls, especially a cohosted memory ceiling and support-service protections, remain unresolved and require separate explicit agreement. No change authorized to agent, proxy, databases, Compose, DEVELOPMENT, OLD/NEW PRODUCTION or UAT; Codex remains **NO-GO**.

**Next read-only check:** determine whether a Compose-managed egress-proxy container exists/is running, and count its attached networks if present. Report sanitized counts only; do not display host addresses, proxy settings, Docker labels or raw paths.

## Step 34 — no active egress-proxy container (2026-11-19)

The operator ran a hostname-guarded, read-only Docker inspection of all present containers, filtered by Compose project `ccpc_codex_dev_agent` and service `egress-proxy`. Results: `agent_running=False`, `proxy_containers_found=0`, `proxy_containers_running=0`, `proxy_attached_to_lab=0`, `proxy_attached_to_other_networks=0`, `proxy_containers_with_port_bindings=0`.

**Interpretation:** no container with the specific expected Compose labels exists for the optional egress-proxy service at inspection time; the optional profile has not produced an active or stopped Compose-managed proxy container. This does **not** demonstrate that all other proxy services, host listeners, DNS/proxy destinations or alternate outbound routes are absent. The agent's earlier environment-name inspection found HTTP_PROXY/HTTPS_PROXY settings, whose actual endpoint identity and reachability remain unverified. No packets were sent and no Docker, host, DEV, OLD/NEW PROD or UAT state changed. Codex remains stopped/NO-GO.

**Next diagnostic:** read-only source configuration inspection of optional `egress-proxy` service: report only service network topology classifications, host exposure indicators, privilege and relevant mount-presence booleans. Do not display paths, raw config, addresses, proxy targets, tokens or environment variables. No Compose activation.

## Step 35 — optional proxy dual-network Compose topology (2026-11-19)

Operator ran a hostname-guarded, read-only parse of the current Compose source for the stopped lab agent and configured-but-inactive `egress-proxy` service. Results: `agent_running=False`, `proxy_optional_profile=True`, `proxy_network_count=2`, `networks_shared_with_agent=1`, `networks_not_shared_with_agent=1`, `proxy_external_network_count=0`, `proxy_host_network_mode=False`, `proxy_published_ports_defined=False`, `proxy_privileged=False`.

**Interpretation:** the proxy is designed to bridge two Compose-managed network attachments: one shared with the agent and one that is not. This is consistent with a controlled egress proxy but is **not** proof of access control, routing safety, or ability to reach GitHub. In particular, `external=false` refers to whether Compose manages the network, **not** whether that network has outbound/Internet connectivity. The second network's `internal` setting and gateway properties are pending verification. In Step 34 no running/stopped `egress-proxy` container was found; no activation or runtime network test occurred. No host, DEVELOPMENT, OLD/NEW PRODUCTION, or UAT state was modified. The agent remains stopped/NO-GO.

**Next step:** sanitized source-only comparison of the second network's `internal`, `external`, `driver`, `attachable` settings and the agent's attachment count, avoiding raw network names, addresses or proxy values. Check allowed target policy and proxy service hardening before even considering approval to activate the optional profile. Resource and authentication gates also remain open.

## Step 36 — optional proxy two-network definitions (2026-11-19)

The operator ran a hostname-guarded, read-only parse of the current Compose source for the stopped agent and inactive optional proxy; reported `agent_network_count=1`, with one proxy network shared with the agent and one not shared:

| Sanitized field | Shared lab network | Unshared proxy network |
| --- | --- | --- |
| Definition present | true | true |
| `internal` | true | **false** |
| `external` | false | false |
| Driver declared, bridge | true, true | true, true |
| `attachable` | false | false |
| Driver options present | false | false |

**Interpretation:** The agent is defined on one internal Compose-managed Docker bridge. The optional `egress-proxy` is defined on both that lab bridge and a separate Compose-managed `bridge` with `internal=false`. This is consistent with a proposed egress gateway. `external=false` describes Compose ownership, **not** Internet isolation: the second network could potentially access outbound destinations or host/private networks depending on Docker routing, firewall rules and proxy application policy. The proxy's ability to relay traffic, its ACLs and actual reachability **have not been verified**; Step 34 found no Compose-managed proxy container. No network, container, host or protected-environment changes occurred. Codex remains stopped/NO-GO.

**Next read-only inspection:** audit the optional proxy Compose service's local hardening flags (user, read-only root filesystem, privilege, security options, capabilities, ports, mounts, resource limits, configuration input presence) without printing paths, environment variable values, service commands, credentials or raw Compose content. Review the actual proxy application allow/deny policy in a separate sanitized inspection before any activation. Resource headroom/sandbox/authentication remain unresolved.

## Step 37 — optional proxy hardening declarations (2026-11-19)

Operator ran hostname-guarded read-only parse of the current Compose source for the configured but inactive optional `egress-proxy`, while checking the agent remains stopped. Reported `agent_running=False` and these service declarations:

| Setting | Reported value |
| --- | --- |
| `proxy_read_only_root` | `True` |
| `proxy_privileged` | `False` |
| `proxy_user_explicitly_set` | `False` |
| `proxy_all_capabilities_dropped` | `True` |
| `proxy_added_capability_count` | `0` |
| `proxy_no_new_privileges` | `True` |
| `proxy_mount_count` | `1` |
| `proxy_secret_count` | `0` |
| `proxy_published_ports` | `0` |
| `proxy_memory_limit_defined` | `False` |
| `proxy_cpu_limit_defined` | `False` |
| `proxy_pid_limit_defined` | `False` |

**Interpretation:** The source declares valuable container hardening: read-only root, unprivileged container mode, no-new-privileges, drop-all capabilities with no additions, and no host published ports. However, the proxy user is omitted (so the *image's default user*, not yet inspected, would be used), there is one mount of as-yet-unknown type/source/read-write state, and no CPU/memory/PID caps. `proxy_secret_count=0` means no Compose-managed secret references, **not** that the mount, image or environment is free of secrets. The proxy's application-level destination/ACL policy and actual reachability are still unknown. This is config inspection, not execution. No host, Docker, DEVELOPMENT, OLD/NEW PRODUCTION or UAT changes. Codex remains stopped/NO-GO.

**Next diagnostic:** read-only sanitized classification of the proxy's single source-declared mount: type, read-only setting, whether it references Docker's control socket, and whether source path is a symlink (only if safe to determine), without showing paths, target names, config contents, proxy addresses or credentials. Later verify the image default user and outbound ACLs; resource limits remain an availability blocker on cohosted infrastructure.

## Step 38 — optional proxy bind-mount classification (2026-11-19)

Operator ran a hostname-guarded read-only inspection of the configured but inactive optional `egress-proxy` service's one Compose-declared mount. Sanitized results: `agent_running=False`, `mount_type=bind`, `mount_read_only=True`, `source_is_absolute=True`, `bind_source_exists=True`, `bind_source_is_symlink=False`, `source_is_docker_socket=False`, `target_is_docker_socket=False`.

**Interpretation:** A currently existing absolute host path is declared as the proxy's read-only bind source, not itself a symlink and not resolving directly to the standard Docker Unix control socket; its container target is not the standard socket either. This is promising but not proof of source safety: the source could be a directory, a file containing credentials, an alias through a parent directory, or overlap other protected containers' mounted host filesystems. A read-only mount does not prevent reading sensitive material, and this check does not detect nonstandard Docker daemon endpoints. No configuration content, source paths or secrets were displayed; no Docker or protected-environment state changed. Codex remains stopped and proxy inactive/NO-GO.

**Next one read-only diagnostic:** classify the proxy bind source as regular file/directory, detect parent-path symlink resolution, and count exact/nested host-mount-source overlaps with containers outside the lab. Report only booleans/counts; never print raw source paths, file contents, proxy addresses or credentials. If safe, later inspect *sanitized policy categories* and image default user before any proxy activation.

## Step 39 — proxy bind source host-path isolation (2026-11-19)

Operator ran a hostname-guarded, read-only comparison of the optional proxy's single Compose-declared bind source against all other containers' resolved mount sources. Reported:

| Check | Operator-reported value |
| --- | --- |
| `agent_running` | `False` |
| `source_is_regular_file` | `True` |
| `source_is_directory` | `False` |
| `source_path_uses_symlink` | `False` |
| `source_within_compose_workdir` | `True` |
| `outside_lab_containers_inspected` | `15` |
| `external_exact_mount_matches` | `0` |
| `external_mount_overlap_candidates` | `0` |

**Interpretation:** the bind source currently resolves to a regular, non-symlink-path file within the laboratory's Compose working directory, and there were no exact or ancestor/descendant source path overlaps with the 15 Docker containers outside the lab. This is positive evidence against accidental Docker mount-source sharing, **not** proof that the file has no sensitive contents, that a proxy could not reach protected systems, or that no other host process can access the file. Prior Step 38 established read-only inside the proxy configuration, and Step 34 found no proxy container. The file's permissions, semantics and outbound rules remain unverified. No host file contents were displayed; no containers, Docker networks or protected environments were modified. The Codex agent remains stopped/NO-GO.

**Next read-only diagnostic:** classify host permission exposure of the proxy's bind source and whether its content looks like a proxy-policy configuration, without printing any source path, file content, host identity, proxy address, destination, or credentials. Follow with a separate policy-specific rule review once the file format has been safely identified. No proxy activation.

## Step 40 — Squid policy format and host file permission flags (2026-11-19)

Operator ran a hostname-guarded, read-only classification of the configured but inactive optional proxy's single read-only bind source, checking file permissions and counting policy directives without exposing policy content. Reported:

| Field | Operator-reported value |
| --- | --- |
| `agent_running` | `False` |
| `source_regular_file` | `True` |
| `source_group_readable` | `True` |
| `source_world_readable` | `True` |
| `source_group_writable` | **`True`** |
| `source_world_writable` | `False` |
| `proxy_image_family` | `SQUID` |
| `active_directive_count` | `14` |
| `squid_acl_count` | `4` |
| `squid_http_access_count` | `5` |
| `nginx_proxy_pass_count` | `0` |
| `generic_allow_count`, `generic_deny_count` | `0`, `0` |

**Interpretation:** the declared proxy image family appears to be Squid, and its mounted host source contains an apparent Squid policy with four `acl` and five `http_access` directives. Crucially, group-write and world-read permission bits are set on that regular host file. These bits raise **potential integrity and confidentiality concerns**: a suitably authorized member of the file's group may be able to modify the proxy's access rules, and users with directory traversal permission may be able to read them. This **does not yet establish effective access**: parent directory mode/ACLs, file ownership, any POSIX ACLs and execution identity need review. The file is read-only *inside the optional proxy container* (Steps 37–38), but that does not protect the host-side source from writes by authorized host identities. Squid counts alone do not verify private-network deny policies, ACL definition correctness, `http_access` order or CONNECT restrictions. No filenames, ACL contents, destinations, source addresses, credentials or paths were printed, and no file, container or host changes were made. **Codex/proxy remain inactive and NO-GO.**

**Next read-only diagnostic:** check the mounted file's effective host access boundaries by reporting only source/parent-directory permission indicators and presence of extended POSIX ACLs, without disclosing identities, paths or configuration contents. If appropriate, subsequently inspect sanitized Squid `http_access` ordering/allowlist semantics. Do not chmod, chown, modify ACLs, start the proxy, or run Codex until a separate safe change is reviewed.

## Step 41 — Squid host file access boundary flags (2026-11-19)

Operator ran a hostname-guarded, read-only stat and extended-ACL presence check on the configured but inactive Squid proxy's single bind-source file and its ancestor directories. Reported:

| Observation | Operator-reported value |
| --- | --- |
| `agent_running` | `False` |
| `file_owned_by_root` | `False` |
| `file_group_readable` | `True` |
| `file_group_writable` | **`True`** |
| `file_world_readable` | `True` |
| `all_parent_directories_world_searchable` | `False` |
| `all_parent_directories_group_searchable` | `False` |
| `any_parent_directory_world_writable` | `False` |
| `source_extended_acl` | `NOT_SET` |

**Interpretation:** parent directory permissions impose some traversal restrictions, so world-read bits alone do not prove every local user can read the file. The file is not owned by root, has group-write and world-read bits, and has no file-level extended POSIX ACL in this check. This does **not** establish effective access by particular identities: owning UID/GID, group memberships, ownership and ACLs of each ancestor, as well as other authorized access routes, remain unknown. Group write remains a **potential policy-integrity risk** if an identity can traverse the directory chain and write the file; a world-readable configuration could be confidential if directory access exists. No unauthorized access was demonstrated. The bind is read-only inside the proxy but that does not prevent host-side edits. No chmod/chown or file/config/container changes were performed; Codex and Squid remain inactive/NO-GO.

**Next single read-only check:** inspect sanitized Squid `acl` types and `http_access` ordering, including whether an explicit terminal `deny all` exists and whether a source- or destination-constraining ACL is actually referenced. Print *only classifications/counts*, never ACL names, domain/IP values, paths, credentials, or raw config. Effective policy/security still requires deeper review; do not activate the proxy or agent.

## Step 42 — Squid outbound access order and ACL classification (2026-11-19)

The operator ran a hostname-guarded, read-only sanitized parse of the configured but inactive Squid proxy's local policy file (no source values displayed). Results: `agent_running=False`, `policy_include_directives=0`, `acl_definition_count=4`, `acl_source_count=0`, `acl_destination_ip_count=1`, `acl_destination_name_count=1`, `acl_port_count=1`, `acl_method_count=1`, `acl_other_count=0`, `http_access_rule_count=5`, and `explicit_terminal_deny_all=True`.

| http_access rule position | Action | ACL predicates | Negations | Destination scope? | Unknown references? |
| --- | --- | ---: | ---: | --- | ---: |
| 1 | DENY | 1 | 1 | no | 0 |
| 2 | DENY | 1 | 1 | no | 0 |
| 3 | DENY | 1 | 0 | yes | 0 |
| 4 | ALLOW | 1 | 0 | yes | 0 |
| 5 | DENY | 1 (all) | 0 | no | 0 |

**Interpretation:** This is consistent with an outbound allowlist pattern: two early conditional denies (possibly port/method checks; their specific types were not printed), a destination-based deny, destination-based allow, and explicit terminal deny-all. Squid evaluates `http_access` sequentially. The audit has **not** verified that the destination deny targets protected/private subnets, that the allow targets only intended domains, that DNS resolutions cannot bypass IP restrictions, or that port/method restrictions are correctly mapped. No source-address ACL is declared; network-side access to the proxy listener must be separately constrained. Directive counts and classifications **do not prove a secure policy**. No proxy/agent execution, network packets, or changes to any protected environment. Codex and proxy remain stopped/inactive and NO-GO.

**Next read-only check:** classify which ACL type is actually referenced by each rule and report coverage (only boolean categories) of major private/reserved IPv4/IPv6 blocks by the *destination-deny* ACL, plus a count of permitted destination-name patterns without displaying their contents. This should not publish ACL names, host paths, domain names, IPs, raw directives, or credentials. Avoid image pull, proxy activation or Codex launch.

## Step 43 — Squid private-range coverage and destination ACL shape (2026-11-19)

The operator ran a hostname-guarded, read-only classifier of the inactive Squid proxy configuration. It confirmed the five `http_access` rule types and the specific reference types (not raw ACL values): `DENY_NOT_METHOD`, `DENY_NOT_PORT`, `DENY_DST`, `ALLOW_DSTDOMAIN`, `DENY_ALL`. The destination IP deny rule was correctly referenced (`destination_ip_deny_verified=True`), with `deny_network_entry_count=13` and `deny_unparsed_entry_count=0`. The destination-name allow rule was correctly referenced (`destination_name_allow_verified=True`), with `allowed_name_pattern_count=10` and `allowed_name_has_star_wildcard=False`.

Each coverage check returned true: IPv4 private `10/8`, `172.16/12`, `192.168/16`; loopback `127/8`; link-local `169.254/16`; shared `100.64/10`; IPv6 loopback `::1/128`, unique-local `fc00::/7`, and link-local `fe80::/10`. Coverage is defined here as **the full indicated block being contained by at least one parsable network entry**. No actual proxy policy values, host paths, hostnames, or secrets were shown.

**Interpretation:** The observed Squid rule order is consistent with method/port restrictions, protection of the tested private/special-use destination ranges, a destination-name allowlist and terminal default-deny. This is strong static configuration evidence, **not approval to activate Squid/Codex**: exact method/port values are unverified, other reserved ranges and DNS rebinding/lookup behavior are untested, destination-name patterns may match suffixes even without `*`, and no runtime traffic testing has occurred. The absence of a wildcard `*` is insufficient to establish narrow exact-host matching. The proxy is inactive, Codex stopped, and there were no host, Docker, DEVELOPMENT, OLD/NEW PRODUCTION or UAT changes.

**Next single diagnostic:** safely classify actual method and port ACL values (e.g. CONNECT-only, 443-only), and destination-name pattern shapes (exact-name versus suffix, IP literals, potentially overly broad entries), outputting only booleans and counts. No raw allowed domains, proxy endpoints, paths, configuration text, credentials, or network probes. Continue separately to evaluate DNS/IPv6 edge cases and file integrity before any activation.

## Step 44 — Squid method port and suffix-allowlist inspection (2026-11-19)

The operator used a hostname-guarded, read-only classifier of the inactive optional proxy's current host-mounted Squid configuration. Sanitized reported results: `agent_running=False`, `method_value_count=1`, `method_connect_only=True`, `port_value_count=1`, `port_443_only=True`, `allowed_domain_pattern_count=10`, `allowed_leading_dot_patterns=10`, `allowed_single_label_patterns=0`, `allowed_ip_literal_patterns=0`, `allowed_pathlike_patterns=0`, `allowed_nonstandard_patterns=0`, `terminal_deny_all=True`.

**Interpretation:** The configured method and port ACL values are CONNECT-only and destination port 443 only. The allowlist contains 10 syntactically conventional **leading-dot domain suffix patterns**, not 10 verified exact-host matches. In Squid `dstdomain`, such entries can match the domain and its subdomains. There are no literal IP, path-like or syntactically unusual allow patterns from the checks performed. This supports a restricted HTTPS proxy *design*, but **the actual allowlist breadth is still unknown**, as are TLS CONNECT handling, DNS rebinding/forward resolution behavior, special-use IP coverage beyond Step 43, proxy default user, and runtime enforcement. The source ACL logic has not been validated with live negative tests. No proxy activation, container launch, networking/host modifications or protected CCPC environment changes. The agent and optional proxy remain inactive, **NO-GO**.

**Next sanitized read-only diagnostic:** characterize the depth of each allowed domain suffix (number of DNS labels after leading dot), confirm none is a one-label/public-suffix-like pattern, and check for duplicates or suffix overlaps without publishing actual names, domains or proxy destinations. This *cannot* fully validate eTLD/public suffix or trustworthiness without controlled review of the exact patterns. Keep secrets and raw config private and do not start the proxy.

## Step 45 — Squid allowlist suffix depth and overlap (2026-11-19)

Operator ran a hostname-guarded, read-only parser of the inactive Squid proxy's allowlist without printing the permitted domains, ACL names, host paths, or secrets. Sanitized results: `agent_running=False`, `domain_pattern_count=10`, `all_domain_labels_valid=True`, `minimum_domain_label_count=2`, `maximum_domain_label_count=2`, `single_label_pattern_count=0`, `two_label_pattern_count=10`, `three_or_more_label_pattern_count=0`, `duplicate_pattern_count=0`, `nested_suffix_overlap_pairs=0`.

**Interpretation:** all ten entries are syntactically valid leading-dot **two-label suffix patterns**, with no duplicate or nested overlapping suffix entries under case-normalized comparison. This gives useful structural evidence, but does **not** establish that each suffix is a privately administered organization/service domain, rather than a registry/public suffix, nor does it prove safe DNS resolution or narrow host access. A leading-dot Squid `dstdomain` entry may match the parent domain and its subdomains. All actual suffix values were withheld and need a separately controlled, privacy-safe review before approval. No proxy/agent execution, network traffic, host changes, or DEV/OLD/NEW PROD/UAT modifications; Codex and the optional proxy remain inactive/NO-GO.

**Next read-only check:** determine whether the *locally available* image declared for the optional Squid proxy specifies a non-root default user. Use Docker image metadata only; no image pull, creation, build or execution; report only default-user classification, not image reference, labels, paths, or environment. An absent image is an acceptable finding, not an instruction to pull it. Review image trust, proxy domain safety/DNS and cohosted resource controls separately before any activation.

## Step 46 — optional proxy image not available locally (2026-11-19)

Operator performed a hostname-guarded read-only inspection of the current Compose-declared `egress-proxy` image reference, checking local Docker image availability and the image's default user *only if available*, without image pull, container creation or execution. Operator reported `agent_running=False`, `compose_user_explicitly_set=False`, `proxy_image_available_locally=False`, and `image_default_user_class=UNVERIFIED`.

**Interpretation:** the proxy has no explicit Compose `user` and the named image is absent from the local Docker image store under that reference, so its default runtime user **cannot yet be classified**. This is not proof no similar image exists under another reference. Launching the service may attempt an image pull unless explicitly controlled, which is **not authorized**. Do not infer the proxy runs as non-root or that image provenance has been checked. Agent remains stopped; optional proxy remains inactive. No image downloads, host/Compose changes, or DEV, OLD/NEW PROD or UAT operations occurred. **NO-GO**.

**Next single read-only diagnostic:** classify the configured proxy image reference as an immutable SHA-256 digest versus a mutable tag, and inspect whether the Compose source declares an image pull policy, without displaying image names, registry hostnames, paths, user identities or secret values. If unpinned or pull behavior is not controlled, flag for review before future proxy activation. Do not pull or start the image.

## Step 47 — unpinned proxy image with explicit never-pull (2026-11-19)

The operator's hostname-guarded read-only Compose check produced: `agent_running=False`, `proxy_optional_profile=True`, `image_reference_declared=True`, `image_reference_uses_variables=False`, `image_reference_digest_pinned=False`, `image_reference_mutable_or_unresolved=True`, `build_declared=False`, `pull_policy_declared=True`, `pull_policy_class=NEVER`.

**Interpretation:** the optional Squid proxy declares a literal mutable image reference, with no Compose build declaration, and explicitly requests `pull_policy: never`. This is a useful guard against **automatic image download**. At Step 46 Docker did not have the configured image locally, so activation should not be attempted; it would require separately reviewed acquisition or config changes. The missing local image means image metadata and default user remain **unverified**. Neither mutable tag nor pull-policy alone proves trusted provenance. No proxy image pull/build, container start, network change, host mutation or DEV/OLD/NEW PRODUCTION/UAT modification was performed. Codex remains stopped and optional Squid proxy inactive/NO-GO.

**Next one read-only diagnostic:** inspect the configured Squid policy's **proxy listener interface scope** (`http_port` / `https_port`, wildcard versus loopback versus explicit bind) and whether transparent/intercept/reverse-proxy modes are configured. Report only classification/booleans and counts, no host addresses, raw config, domain suffixes, credentials, image refs or paths. Since the optional proxy is on two networks and has no source ACL (Step 42), listener accessibility to the proxy-only network is a distinct exposure risk requiring examination before any activation. Do not download/start services.

## Step 48 — Squid listener bound on all container interfaces (2026-11-19)

The operator ran a hostname-guarded, read-only parser of the optional/inactive Squid configuration and reported:

| Setting | Operator-reported value |
| --- | --- |
| Agent running | `False` |
| Policy include directives | `0` |
| `http_port` listeners | `1` |
| `https_port` listeners | `0` |
| All-interfaces listeners | **`1`** |
| Loopback-bound listeners | `0` |
| Explicit-address-bound listeners | `0` |
| Named/unknown listeners | `0` |
| Intercept/transparent, accel, tproxy listeners | `0` each |

**Risk and interpretation:** The optional Squid service declares a general HTTP proxy listener on all interfaces, rather than restricting it to the isolated laboratory side. Steps 35–36 showed that if activated, this proxy would attach to both the internal lab bridge and another non-internal Compose-managed bridge; Step 42 found no source-address ACL in `http_access`. Consequently, unless additional network controls intervene, other peers on the second bridge (and potentially host-side networking) could reach and use the proxy, even with **no published Docker host ports**. The destination allowlist, CONNECT/443 restriction and deny-all remain useful, but do not substitute for *who may access* the proxy. **This is a pre-activation security blocker**, not a confirmed current exposure: Step 34 found no proxy container, the source uses `pull_policy: never`, Step 46 found no configured image locally, and the Codex agent is stopped. No probe or mutation occurred, and DEV, OLD/NEW PRODUCTION and UAT remain untouched.

**Required design direction before activation:** enforce an explicit lab-source allow rule followed by source deny (carefully ordered before destination allows), and evaluate binding exclusively to the lab-facing interface/address plus Docker/firewall network controls. Do not assume these alone are sufficient: DNS resolution, private destinations, listener reachability and current image behavior require validation in a separate controlled test using synthetic targets. Review image provenance/user and resource limits first. No change is authorized yet.

**Next one read-only diagnostic:** determine whether the proxy's *second* declared Compose network has been instantiated, and whether any current containers are attached to it, with no raw names, IPs, ports, commands, environment or network addresses reported. Never start Squid or Codex to perform this check.

## Step 49 — second outbound-facing proxy network absent (2026-11-19)

The operator ran a hostname-guarded, read-only inspection of Docker network labels against the optional Squid proxy's Compose-declared network that is not shared with the agent. Reported `agent_running=False`, `compose_network_found=False`, `attached_container_count=0`, and `outside_lab_attached_count=0`.

**Interpretation:** the optional proxy's proposed second Compose-managed Docker network has not been instantiated under its expected Compose project/network labels at the time of inspection. Together with Step 34 (no Compose-managed `egress-proxy` container), this supports a conclusion of **no active exposure through this *specific planned proxy topology***. It does not rule out alternate or preexisting network paths, independently managed proxies, or reachability of the existing `HTTP_PROXY`/`HTTPS_PROXY` hostnames configured for the stopped agent (Steps 11–13). These endpoint relationships and effective routing remain unverified. The broad Squid listener remains a **pre-activation design issue**, not a demonstrated active exposure. No network or containers were created, no probes sent, no change to host/DEV/OLD or NEW PROD/UAT. Agent stopped, proxy inactive, overall Codex **NO-GO**.

**Next read-only diagnostic:** compare sanitized configured HTTP/HTTPS proxy URL hostnames/ports from the stopped agent's Docker metadata against the optional Compose service's names and network aliases. Report only equality, URL scheme, host-is-IP and host-is-lab-service classifications; never print endpoint values, DNS answers, addresses, credentials, raw environment values or proxy configuration. Do not start any containers or make DNS/network requests.

## Step 50 — agent proxy host resolves to optional service alias (2026-11-19)

Operator ran a hostname-guarded, read-only classifier on the **stopped** agent's Docker environment metadata and the current Compose source's optional proxy service/network aliases, without logging URL values or ports. Reported `agent_running=False`, `http_proxy_configured=True`, `https_proxy_configured=True`, `both_proxy_urls_parseable=True`, `proxy_destinations_equal=True` (same host and port), `http_matches_optional_service_alias=True`, `https_matches_optional_service_alias=True`, `any_proxy_host_is_ip_literal=False`, `any_proxy_host_is_docker_host_alias=False`, `embedded_auth_detected=False`.

**Interpretation:** HTTP(S) proxy environment settings point at the optional `egress-proxy` Compose service alias (same host and port) instead of an IP literal, Docker host alias, or different observed endpoint. Steps 34 and 49 found no Compose-managed Squid container and no second proxy bridge instantiated; thus the *intended optional service path* is not currently active. The result does not establish effective DNS resolution, exclude alternative routes or prove that all outbound traffic is denied. Credentials embedded in the proxy URLs were not detected, but unrelated stored credentials were not ruled out. No DNS queries, network traffic, Docker/host operations or DEV/OLD PROD/NEW PROD/UAT changes occurred. Agent remains stopped; proxy inactive; **NO-GO**.

**Next single read-only diagnostic:** compare both agent proxy URL ports to the inactive Squid `http_port` listener and classify whether `NO_PROXY` can bypass the proxy for protected/private addresses or broad wildcards. Report matches/counters only, never numeric port values, raw URL/NO_PROXY values, destinations, host paths or credentials. No proxy activation or host network probing.

## Step 51 — aligned Squid listener ports and NO_PROXY categories (2026-11-19)

Operator ran a hostname-guarded, read-only comparison of the stopped Codex agent's stored proxy environment settings with the inactive optional Squid configuration. Reported: `agent_running=False`, `squid_http_listener_count=1`, `http_proxy_port_matches_listener=True`, `https_proxy_port_matches_listener=True`, `no_proxy_configured=True`, `no_proxy_entry_count=5`, `no_proxy_global_wildcard=False`, `no_proxy_wildcard_pattern_count=0`, `no_proxy_ip_or_cidr_entries=1`, `no_proxy_private_or_special_entries=1`, `no_proxy_known_service_alias_matches=3`.

**Interpretation:** both HTTP(S) proxy URLs refer to the same port configured as Squid's single `http_port` listener (consistent with Step 50's alias match). The five `NO_PROXY` tokens contain no obvious wildcard; three exactly match known Compose service names, and one is a parsable private/special-use IP/CIDR entry. This diagnostic does not establish whether that bypass is loopback-only, strictly within lab, or reaches a broader protected/private address range; remaining unmatched entries also need classification. Since cooperating HTTP clients use `NO_PROXY` to bypass an explicit proxy, the scope matters, although proxy bypass alone **does not grant network reachability** in the presence of Docker/firewall isolation. Not all applications honor `NO_PROXY`; arbitrary outbound socket traffic may bypass proxy environment variables regardless. The agent remains stopped and Squid inactive. No traffic, Docker/host changes or DEV/OLD/NEW PROD/UAT operations were performed. **NO-GO remains**.

**Next read-only diagnostic:** classify each `NO_PROXY` token by category only (lab-service alias, loopback literal/network, RFC1918 or other nonloopback CIDR, localhost label, other hostname/suffix), including whether any IP/CIDR entry overlaps the laboratory's Docker IPAM subnet. Report counts and booleans only: no raw token, address, hostname, port or credentials. Do not start Codex, Squid or containers, or perform DNS/probes. Resource availability, proxy listener source filtering, image provenance, authentication and sandbox controls remain unresolved.

## Step 52 — NO_PROXY limited to loopback and local services (2026-11-19)

The operator ran a hostname-guarded, read-only check against the stopped agent's Docker container metadata and the existing internal lab network's Docker IPAM subnet. Sanitized output: `agent_running=False`, `no_proxy_entry_count=5`, `parsed_ip_network_count=1`, `loopback_only_network_count=1`, `non_loopback_network_count=0`, `network_entries_overlapping_lab=0`, `network_entries_covering_entire_lab=0`, `known_service_name_entries=3`, `localhost_name_entries=1`, and `other_hostname_entries=0`.

**Interpretation:** The single parseable `NO_PROXY` IP/CIDR item is loopback-only and does not overlap the lab bridge subnet; three hostname entries are known laboratory service aliases, one is a localhost name, and there are no other hostname entries. No broad network proxy bypass was found among these five entries. This validates only the **reported uppercase `NO_PROXY` setting for the stopped agent**, not lowercase or application-specific overrides. `NO_PROXY` is an application preference rather than a firewall; direct sockets and non-proxy-aware clients can bypass proxy settings. Docker/firewall static rules remain relevant, and live negative tests and IPv6 isolation are unverified. No agent/proxy execution, host mutations, DNS queries, network traffic or DEV/OLD/NEW PROD/UAT modifications. **NO-GO** unchanged.

**Next read-only diagnostic:** classify alternate lowercase/mixed-case proxy variables, `ALL_PROXY`, and additional bypass settings from stopped agent Docker metadata. Report names/categories and equality to existing uppercase proxy endpoints, never reveal values, hosts, ports, credentials, raw Compose files or paths. No container activation. Later: harden all-interface Squid listener with source controls, verify image provenance/user, special-use/DNS behavior, and address host-shared resource risks before any runtime test.

## Step 53 — no alternative proxy environment configuration detected (2026-11-19)

The operator ran a hostname-guarded, read-only inspection of existing **stopped** Codex agent Docker metadata for alternative proxy environment variables. Sanitized output: `agent_running=False`, `duplicate_environment_key_count=0`, `lowercase_http_proxy_configured=False`, `lowercase_http_matches_upper=NOT_SET`, `lowercase_https_proxy_configured=False`, `lowercase_https_matches_upper=NOT_SET`, `lowercase_no_proxy_configured=False`, `lowercase_no_proxy_matches_upper=NOT_SET`, `lowercase_no_proxy_has_wildcards=NOT_SET`, `any_all_proxy_configured=False`, `any_ftp_proxy_configured=False`, and `other_proxy_named_env_key_count=0`.

**Interpretation:** No conflicting lowercase HTTP(S)/NO_PROXY, ALL_PROXY, FTP_PROXY, or other suffix-`_proxy` variables were present in the *inspected agent Docker environment*. Existing uppercase HTTP(S) proxy and narrowly scoped `NO_PROXY` settings remained established in Steps 50–52. This is a positive static configuration finding, not runtime network enforcement: app-specific settings or direct sockets can still bypass proxy environment variables. No Codex/optional Squid execution, Docker/host changes, image download or DEV/OLD PROD/NEW PROD/UAT actions occurred; agent remains stopped, proxy inactive, **NO-GO**.

**Next read-only diagnostic:** determine whether the lab bridge has IPv6 enabled, whether the stopped agent has an IPv6 address, and whether host IPv6 forwarding is enabled; classify any IPv6 ingress/forward firewall controls without printing interface names, IPs, network topology specifics or policy rules. This is the unverified counterpart of Steps 20–25's IPv4-only static inspection. No packet probes, service starts or firewall changes.

## Step 54 — lab IPv6 disabled and host forwarding off (2026-11-19)

Operator ran a hostname-guarded, read-only Docker inspection and Linux kernel settings check. Reported `agent_running=False`, `lab_network_internal=True`, `lab_network_driver_bridge=True`, `lab_ipv6_enabled=False`, `lab_ipv6_ipam_subnet_count=0`, `stopped_agent_ipv6_address_recorded=False`, `host_ipv6_disabled_all=0`, `host_ipv6_forwarding_all=0`, and `host_ipv6_forwarding_default=0`.

**Interpretation:** IPv6 capability is **not globally disabled** on the Ubuntu host, but the existing internal Codex lab bridge has IPv6 disabled, contains no IPv6 IPAM subnet, and Docker records no stopped-agent IPv6 address. Host-wide and default IPv6 forwarding controls are disabled. This is favorable **static evidence** against IPv6 forwarding via the existing lab bridge. It does not prove every host interface setting or a future optional proxy network's IPv6 configuration; no runtime negative connectivity tests have been performed. No Docker/network/firewall changes, processes started, packets sent or DEV/OLD PROD/NEW PROD/UAT modifications. Codex stopped; optional Squid inactive; **NO-GO remains**.

**Next one read-only diagnostic:** revisit Step 40–41's proxy policy file host-side group writability. Classify whether file-owning group has any non-owner local members and whether parent directory permissions are broadly writable; no raw file/parent paths, usernames, group names, UID/GID values, file contents, domains, credentials, or other metadata to be displayed. The proxy must not be activated while its source policy's change authority is uncertain. Keep other blockers (all-interface Squid listener/no source ACL, absent unpinned image, DNS, resource limits and runtime isolation tests) open.

## Step 55 — Squid policy file group-writable and parent directories (2026-11-19)

Operator ran a hostname-guarded, read-only inspection of the inactive optional Squid proxy policy file's ownership and standard POSIX file/directory mode bits, including local POSIX group membership. Sanitized findings: `agent_running=False`, `file_owner_is_root=False`, `file_owner_is_operator=True`, `file_group_writable=True`, `file_world_writable=False`, `nonowner_group_member_count=0`, `interactive_nonowner_group_member_count=0`, `group_writable_parent_count=3`, `world_writable_parent_count=0`.

**Interpretation:** the source policy is operator-owned and group-writable, with no **enumerated local** non-owner members of that file's owning group; zero world-writable parents were found. Three ancestor directories are group-writable, but their owners, groups, memberships, effective access, sticky bits and POSIX ACL/default ACLs are not yet characterized. Directory write+search permissions may permit replacement or rename despite file mode, even without direct write access to the file. Enumerated local POSIX memberships are not a complete proof of effective permissions (NSS/external identities, ACLs, host Docker admins, and privileged accounts may have access). No unauthorized editor has been demonstrated. **Do not chmod/chown** or make other host changes without targeted review and user approval. No Docker/host mutations, container starts or DEV/OLD PROD/NEW PROD/UAT changes. Codex stopped, optional Squid inactive, **NO-GO**.

**Next one read-only diagnostic:** classify the three group-writable parent directories' owning-group nonowner membership (including interactive accounts), whether their group write+execute permissions can permit rename/replacement, sticky bits, and any POSIX ACL/default ACL indicators, using sanitized counts/booleans only—no paths, identities, group names, UID/GID, file content or raw ACL entries. Do not start proxy/agent or alter existing services.

## Step 56 — writable parent directories operator-owned without extra local group members (2026-11-19)

The operator ran a hostname-guarded, read-only check of the three group-writable ancestors of the optional inactive Squid proxy policy file. Sanitized output: `agent_running=False`, `group_writable=3`, `group_write_and_search=3`, `nonsticky_group_write_and_search=3`, `writable_owned_by_operator=3`, `writable_owned_by_root=0`, `with_nonowner_group_members=0`, `with_interactive_nonowner_members=0`, `with_access_acl=0`, `with_default_acl=0`, `acl_unknown=0`, and `world_writable=0`.

**Interpretation:** All three parent directories have POSIX group write+search bits and are not sticky, but they are owned by the operator, with no **enumerated local nonowner group members**, no detected POSIX ACL or default ACL, and no world-writable parents. No demonstrated unauthorized replace/rename opportunity via the evaluated group permissions. However, this does not exhaust NSS/central directory accounts, privileged users, file-server access, Docker daemon operators, or parent bind-mount exposure. Avoid unnecessary permission changes; `chmod`/`chown` not authorized or performed. Codex stopped; Squid proxy inactive; no Docker changes, network probes or DEV/OLD PROD/NEW PROD/UAT operations; overall **NO-GO** remains due to independent blockers (all-interface listener with no source ACL, missing mutable image provenance/user, DNS/address policy edge cases, resource limits and runtime validation).

**Next one read-only diagnostic:** inspect the current local Squid policy for proxy behaviors that could alter the intended simple outbound CONNECT design (redirectors, cache peers, alternate routing, authentication, TLS bump, named DNS resolvers). Report only boolean presence and sanitized counts without raw directive values, paths, hostnames, secrets or extra host/network operations. No proxy activation or file edit.

## Step 57 — optional Squid proxy extra-feature static audit (2026-11-19)

The operator ran a hostname-guarded, read-only parser of the optional inactive Squid policy file's directive names and listener option classifications. Reported: `agent_running=False`, `policy_include_count=0`, `directive_total=14`, `unique_directive_count=7`, `upstream_proxy_directive_count=0`, `alternate_routing_directive_count=0`, `redirector_directive_count=0`, `external_acl_directive_count=0`, `authentication_directive_count=0`, `tls_interception_directive_count=0`, `custom_dns_directive_count=0`, `cache_storage_directive_count=1`, and `listener_tls_interception_option=False`.

**Interpretation:** none of the specifically examined Squid directives for upstream peers, alternate routing, redirectors, external ACLs, proxy authentication, TLS interception or custom DNS was found. This is consistent with a relatively simple restricted CONNECT proxy source configuration; it does not exclude every possible Squid directive, built-in default, or runtime behavior. **One cache/storage-family directive** was found (`cache_dir` or `cache_store_log` within the Step 57 parser), but the exact classification and storage implications have not yet been determined. Given Step 37's read-only root filesystem and only one config-file bind, storage/cache/logging configuration deserves a separate static review. No image acquisition, agent/proxy start, DNS queries, network traffic, host/Compose edits, or protected DEV/OLD PROD/NEW PROD/UAT actions. Codex stopped; Squid inactive; **NO-GO**.

**Next single read-only diagnostic:** classify the existing cache/storage directive and Squid logging directives, explicit cache-disable/cache memory settings, and proxy `tmpfs` declarations in Compose. Report only directive names or booleans/counts (never path arguments, raw configuration, domains, usernames, ports, image refs or secrets). Do not create directories, containers or traffic. Remaining gates: source ACL and all-interface listener, image provenance/default user, DNS/security allowlist, safe resource governance and runtime-negative testing.

## Step 58 — Squid storage and logging directive counts (2026-11-19)

The operator ran a hostname-guarded read-only check of the inactive optional Squid proxy's Compose filesystem declaration and sanitized policy directive counts. Reported: `agent_running=False`, `proxy_read_only_rootfs=True`, `proxy_volume_count=1`, `proxy_tmpfs_count=4`, `cache_dir_directive_count=0`, `cache_store_log_directive_count=1`, `cache_mem_directive_count=0`, `cache_directive_count=1`, `cache_deny_directive_count=0`, `cache_allow_directive_count=0`, `access_log_directive_count=1`, `cache_log_directive_count=0`, `pid_filename_directive_count=0`, `coredump_dir_directive_count=0`, `logfile_rotate_directive_count=0`, `policy_include_count=0`.

**Interpretation:** One config-file bind was identified earlier as read-only and the root filesystem is configured read-only; four `tmpfs` mounts are declared, but their destination suitability and mode/size have not yet been verified. The Squid source declares no `cache_dir`, but has one `cache`, one `cache_store_log`, and one `access_log` directive. **Directive counts alone do not determine** whether caching or logging is enabled, redirected, or disabled; do not assume either that caching is off or that logging has writable storage. No custom `cache_log`, `pid_filename`, `coredump_dir` or `logfile_rotate` directive appears, leaving image/default behavior unverified. Squid has not been executed and its image is not locally available under the Compose reference (Step 46). No host, Compose, Docker, network, DEV/OLD PROD/NEW PROD/UAT mutations occurred; agent stopped, proxy inactive, **NO-GO**.

**Next single read-only diagnostic:** safely classify only the first arguments of `cache`, `cache_store_log`, and `access_log` into enabled/disabled/path-like/stdout classifications, without disclosing destinations or raw configuration lines; additionally classify four Compose `tmpfs` mount destinations against conventional Squid runtime directory categories without displaying paths or any environment variable value. Strictly stop on changed Compose or missing evidence. No proxy, image or Docker activation.

## Step 59 — Squid caching disabled and access logs to stdout (2026-11-19)

Operator ran a hostname-guarded, read-only parser of the optional Squid configuration and Compose filesystem declarations. Sanitized results: `agent_running=False`, `proxy_read_only_rootfs=True`, `cache_rule_deny_all=True`, `cache_rule_allows_requests=False`, `cache_store_log_class=DISABLED`, `access_log_class=STDOUT`, `tmpfs_mount_count=4`, `tmpfs_known_runtime_directory_count=4`, `tmpfs_other_directory_count=0`, `tmpfs_duplicate_target_count=0`.

**Interpretation:** The source explicitly declares `cache deny all`, disables `cache_store_log`, directs the `access_log` to standard output, and declares four nonduplicated `tmpfs` mounts at conventional runtime paths, alongside a read-only root filesystem. These static choices support nonpersistent cache storage and Docker-compatible logging. They do not prove that the image has no other log files/runtime-write requirements or establish Docker's log retention/driver, and the optional proxy image is still absent under its Compose reference (Step 46). `tmpfs` consumes host memory; its configured sizes/security mount flags and proxy/agent resource governance remain unverified on this shared host. No agent/proxy launch, image acquisition, host or Docker mutation, network probes or DEV/OLD PROD/NEW PROD/UAT changes. Codex stopped; proxy inactive; **NO-GO remains** due to independent blockers.

**Next one read-only diagnostic:** classify all four Compose `tmpfs` mount options and size restrictions (counts of explicit sizes, noexec/nosuid/nodev and unusual flags), using only sanitized counts/booleans and optionally a bounded total-size summary, without mount destinations, raw source, identities or secrets. No changes to services or host. Respect the shared host's availability risk and do not treat unused host memory as a guarantee of future safety.

## Step 60 — Squid tmpfs size and mount options (2026-11-19)

The operator ran a hostname-guarded, read-only inspection of the inactive optional Squid proxy's Compose `tmpfs` declaration. Sanitized findings: `agent_running=False`, `proxy_read_only_rootfs=True`, `tmpfs_mount_count=4`, `size_option_count=4`, `mounts_without_size_option=0`, `unparseable_size_count=0`, `total_declared_size_mib=144.0`, `noexec_mount_count=2`, `nosuid_mount_count=4`, `nodev_mount_count=0`, `explicit_exec_mount_count=0`, `explicit_suid_mount_count=0`, `explicit_dev_mount_count=0`, `mode_option_mount_count=0`, `unknown_mount_option_count=0`.

**Interpretation:** all four tmpfs mounts specify parseable capacity maxima, totaling **144 MiB**, rather than leaving each at an unspecified default. This is a combined configured ceiling, not pre-allocated RAM and not an overall process memory cap. All four explicitly use `nosuid`, two explicitly use `noexec`, and none explicitly declares `nodev` (whether it is effective as a Docker/kernel default was **not tested**). No suspicious unknown options were reported. Combined with Step 59, these are favorable source-level storage controls, but the actual image's default behavior and mounts are untested; Step 46 found no locally available proxy image. **Resource governance remains a blocker:** Step 32 found no CPU/RAM limits on the four main lab services, and Step 37 found no proxy CPU/RAM/PID limits; capped `tmpfs` does not cap Squid process memory on the shared production host. No docker/container start, image pull, network probes, host file change, or DEV/OLD/NEW PROD/UAT action. Codex stopped, proxy inactive, **NO-GO**.

**Next single read-only diagnostic:** reclassify the *current* Compose source's per-service CPU, memory, swap, OOM and PID controls for the agent/db/redis pair and optional proxy. Return classifications only; no raw host paths, container identities other than generic service classes, resource values, image references, credentials, environment variables or config contents. Afterward assess a resource protection plan that respects operator performance preference while preserving OLD PRODUCTION, with explicit approval before any changes.

## Step 61 — resource controls absent for all five lab services (2026-11-19)

The operator ran the hostname-guarded read-only Compose-source resource controls check across `agent`, `db`, `redis-cache`, `redis-queue`, and the optional `egress-proxy`. Reported `agent_running=False`, `service_count_checked=5`. **For all five services** the following were `False`: `memory_limit_declared`, `cpu_limit_declared`, `cpu_affinity_declared`, `swap_control_declared`, `memory_reservation_declared`, and `oom_kill_disabled`. Only `agent_pid_limit_declared=True`; the other four services reported `pid_limit_declared=False`.

**Interpretation:** The current **Compose source** lacks per-service CPU, memory, swap, reservations, and affinity constraints; the only declared process-count cap is for the stopped agent. This independently confirms and extends Steps 31–32 and 37. OOM protection is **not explicitly disabled**, but that does not ensure production availability against lab overconsumption. The bounded 144 MiB Squid tmpfs (Step 60) does **not** bound process or other lab services' memory. The host co-runs OLD PRODUCTION and related ERPNext environments: **resource governance is an outstanding availability gate** before any lab/proxy activation. Operator prefers maximum Codex performance with no CPU slowdown; consider unrestricted CPU only after understanding cohost peak capacity and workload priorities, while recommending protective memory/process caps to preserve production. This is a planning recommendation, **not authorization** to change host/Compose settings.

**Next one read-only diagnostic:** inspect the already-existing four lab containers' effective Docker HostConfig resource ceilings, their running/stopped states, plus host current total/available/swap memory, outputting only sanitized booleans and rounded capacity metrics. Do not inspect or alter production containers, start agent/proxy, pull images, modify Docker, host configs or protected DEV/OLD PROD/NEW PROD/UAT data. A single memory snapshot is not a safe capacity allocation proof; dynamic loads need separate review.

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
