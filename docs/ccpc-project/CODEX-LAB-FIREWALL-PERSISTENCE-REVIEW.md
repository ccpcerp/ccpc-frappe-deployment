# CCPC Codex laboratory — firewall persistence and boot-order design review

**State:** GitHub review proposal ONLY. No host deployment, firewall changes, service enablement, container start, image pull or reboot authorized by this document.
**Related:** draft PR #39 and `docs/ccpc-project/CODEX-LAB-SECURITY-ISOLATION.md` on the dedicated audit branch.

## Evidence: read-only host checkpoints

- Step 85 verified the **exact** original-lab host `INPUT` DROP through `iptables -C`; Step 83 separately verified both expected `DOCKER-USER` cross-bridge DROP rules and that `FORWARD` first jumps to `DOCKER-USER`. This resolves Step 83's false negative from textual token ordering. No live reachability test has been performed after installing the rules.
- Step 86 found the proposed `br-ccpc-cdxpx` interface name unused in current Docker networks, interfaces and inspected IPv4 filter/NAT rules. This was not an exclusive reservation. Step 82 found no *local* conflict for `172.30.250.0/29`; external/VPN/remote routes remain unverified.
- Step 87 found `ufw.service` enabled and active; `nftables.service` and `netfilter-persistent.service` disabled/inactive, no nonempty standard saved IPv4 iptables rules file. The nftables configuration was nonempty but not proven active.
- Step 88 inspected three UFW IPv4 rule files, two UFW startup hooks, and the nftables configuration: none contained the three expected laboratory rule comment tags. The rules remained **active in the kernel**.
- Step 89 scanned one regular administrator systemd service/timer/drop-in file, thirteen selected cron files, the root crontab and `/etc/rc.local`: no reference to the original-lab firewall script or its three tags was found in that **bounded selection**. `rc.local` was absent as a regular file. This does NOT rule out vendor units, indirect startup jobs, non-root crontabs, scripts that install equivalent rules without tags or other persistence mechanisms.

**Conclusion:** original-lab rules exist *now*. Their restoration after reboot, UFW reload, or Docker daemon restart is **not verified**, and no established startup ordering for a future second network was found. Do not assert an established security breach or automatic loss of the rules; fail closed until protection is independently verified.

## Security invariants for any future deployment

1. The original `ccpc_codex_dev_agent_lab` network remains intact; synthetic DB/Redis, unrelated DEVELOPMENT/UAT, host SSH, NAS and PRODUCTION are not modified by Codex setup. Existing 3 tagged lab DROP rules must not be overwritten by an installer for the new network.
2. The optional `proxy_clients` bridge has the reviewed deterministic device name `br-ccpc-cdxpx` and provisional `172.30.250.0/29` reservation only after a fresh preflight. A firewall rule matching a **not-yet-created interface by exact name** can be inserted before network creation; its presence alone is not proof of traffic isolation. No window where the agent is attached to that network without host/forward safeguards is acceptable.
3. Before network creation, exact scoped new-bridge rules must be present and ordered before competing permits: unconditional inbound interface `INPUT DROP` for host-directed traffic and two `DOCKER-USER` cross-interface DROP rules. The read-only `scripts/security/ccpc_codex_proxy_bridge_preflight.py` checks these predicates. These are *proposed rules*, not installed rules.
4. **Squid has a separate outward-facing network**. The new agent-client bridge policy does not constrain Squid's own outbound sockets, DNS, or reachability of host/private/VPN/remote networks via the outgoing bridge. The Squid egress firewall and resolved-IP/DNS controls require separate review and negative canary tests.
5. Rules must be restored **before** any path by which the agent or proxy could start at boot, by operator Docker command, daemon restart or auto-restart. Compose `restart: "no"` and `online` profile are safeguards, not substitutes for host enforcement. Handle UFW reload, Docker-created chains, daemon/network recreation and failed startup in a fail-closed way.
6. An unprivileged Codex process must not have access to Docker sockets, host networking, privileged containers, host secrets or permissive runtime command escape; verify real runtime behavior separately.
7. Persistence, rollback and rule ownership must not impact existing SSH access, nonlab networking, DEVELOPMENT/UAT or the separate PRODUCTION server. Never flush chains, reset UFW, prune Docker or delete shared resources for the laboratory.

## Implementation options — no option selected or applied

**Option A — UFW-managed persistent source:** Use a carefully reviewed UFW-supported startup mechanism only after proving exact chain creation and Docker/UFW ordering on this host. Do not blindly insert `DOCKER-USER` references into UFW `before.rules`: that chain may not exist until Docker constructs it. Do not run `ufw reload` for experimentation.

**Option B — dedicated root-owned systemd oneshot/guard service:** Model an idempotent exact-match firewall preparation action with a matching read-only verifier, explicit `After=` dependencies for Docker/UFW and a separate guarded lab startup unit that **Requires/After** successful firewall verification. Check that the systemd dependency graph actually provides the intended order and fails closed. A systemd service alone cannot prevent an operator from manually starting a container, and a oneshot may not restore rules when UFW/Docker subsequently reload; this must be addressed with additional controlled guards/monitoring or by a stronger persistent firewall integration.

Neither option is approved for host installation. Choose based on **observed** Docker/ufw startup unit properties, possible UFW hooks, actual iptables-nft backend, and operator rollback capability. Do not enable automatic Codex startup as part of persistence design.

## Separate controlled validation and rollback requirements

- Establish a protected host recovery path and a second SSH session before *any separately authorized* firewall mutation; preserve the existing rule snapshot without publishing raw infrastructure details.
- Verify the proposed interface name and /29 are still unused immediately before an approved rule change. Confirm the agent is still stopped; require an operator-approved exact sequence and do not attach the agent while any requisite rule is missing.
- Install only narrowly scoped, tagged rules; immediately prove `iptables -C` matches, precedence and that no existing Docker/host networking changed unexpectedly. On partial failure, delete **only the exact rules added in that attempt**; never broadly reset firewall chains.
- In a separately authorized and carefully isolated test, demonstrate denial of host gateway SSH, Docker bridge and non-production LAN/remote canaries, with synthetic DB/Redis functionality preserved. Never test real PRODUCTION by default.
- Check whether protection survives an approved UFW refresh, Docker restart and eventually a planned reboot **only under a verified maintenance/rollback procedure**; do not run these now. Capture the exact persisted rule lifecycle and verify the agent cannot race startup.
- Run the 60 source-only regression tests and Squid syntax checks in a trusted isolated runner; GitHub Actions PR checks currently fail without any runner steps, so no test pass is available. Pin/check proxy image provenance, runtime UID and resource budget first.

## Step 90 — service startup ordering observations (2026-11-20)

The operator ran the guarded read-only host inspection with stopped-agent and three original-lab firewall-rule checks. Sanitized output:

- `agent_running=False` and `original_lab_three_rules_present=True`.
- Agent Docker restart policy disabled: `True` (reduces unplanned restart risk but not manual-start or configuration-drift risk).
- `docker.service` active and enabled: `True`; `docker.socket` enabled: `True`.
- `ufw.service` active and enabled: `True`.
- Neither `docker.service After=ufw.service` nor `ufw.service Before=docker.service` nor `ufw.service After=docker.service` was directly declared (`False` for all three).
- `complete_boot_order_verified=False` and `firewall_reboot_persistence_verified=False`.

These results mean **no explicit direct Docker/UFW ordering relationship was observed**, not proof that the units run in an unsafe order or that no transitive ordering exists. Even if they execute in a favorable sequence, the original lab rules still have no verified persistence mechanism. Docker's presence and enabled socket activation mean a future design must consider both ordinary Docker boot and on-demand daemon activation. Unattended Codex restart remains disabled in the observed container; preserve this safety gate.

### Preferred design to evaluate, NOT approved for installation

Maintain strict separation between *firewall persistence* and *starting Codex*. A **systemd-guarded firewall preparation + independent read-only verification** approach is now the preferred candidate for design review, because the current Docker/UFW direct ordering does not itself establish a safe UFW-native `DOCKER-USER` lifecycle. This is **not a final selection or permission to install anything**. Require a dry-run/graph-level examination before generating operational units, because Docker's chain initialization and possible UFW reloads can erase rules after a oneshot has reported success.

A reliable implementation would require: (1) a root-owned, narrowly scoped idempotent restore operation referencing only the exact audited bridge rules; (2) ordering after needed Docker chain availability and after UFW has reached a settled state, while forbidding agent startup before protection is verifiably installed; (3) an independent fail-closed health gate that continuously or at least at every potential Codex launch/relaunch revalidates `INPUT` and `DOCKER-USER` rule presence/precedence; (4) recovery of protection after a firewall/Docker reload without permitting the lab to run during a gap; (5) no global UFW/Docker service edits, chain flushing or automatic Codex start; (6) isolated-SSH rollback and real negative connectivity tests before release. A simple `After=ufw.service` relationship on Docker, by itself, is **insufficient** because it neither persists the custom rules nor handles subsequent reloads.

**Before implementation:** inspect relevant `systemctl show` unit ordering properties beyond the three direct checks (for example `Requires/Wants/PartOf/ExecStartPost` status as sanitised flags), and check whether UFW is using a rule management hook that could safely restore the exact original lab rules once Docker chains exist. No edits to service files, UFW configuration or host containers are authorized by this review.

## Step 91 — dependency and hook precheck (2026-11-20)

The operator ran a guarded **read-only** Docker/UFW/socket systemd property inspection with all three original laboratory firewall rules present and the agent stopped. Sanitized output:

- `docker_requires_ufw=False`, `docker_wants_ufw=False`.
- `docker_after_network_online=True`, `ufw_before_network_pre=True`.
- `docker_has_dropins=False`, `ufw_has_dropins=False`.
- `docker_has_start_pre_hook=False`, `docker_has_start_post_hook=False`.
- `ufw_has_reload_handler=False`.
- `docker_socket_requires_service=False`.
- `complete_dependency_graph_verified=False`, `reboot_persistence_verified=False`.

**Interpretation:** This narrows the observed host design: no Docker dependency on UFW; no inspected service drop-in or Docker pre/post-start hook; UFW reports `Before=network-pre.target` and Docker reports `After=network-online.target`. Those *distinct target relationships* are **not proof** of a full dependency path, successful firewall persistence, nor of an ordering guarantee after a reload. `docker.socket Requires=docker.service` being false does **not** rule out socket activation; systemd socket `Service=` wiring and unit dependencies must be independently reviewed before assuming Docker cannot start on demand. Likewise absence of an `ExecReload` in `ufw.service` does not mean `ufw reload` is impossible or harmless.

### Design decision for the GitHub-only review stage

Adopt a **two-layer candidate design**, strictly for review; **do not install it**:

1. A root-owned, idempotent *original-lab firewall restoration* action, guarded for hostname, Docker daemon and known lab/bridge identity, stopped-agent state, iptables-nft backend, and no change to other chains or namespaces. Intended to run after Docker chains exist and after UFW's initial setup. It must check exact three existing rules before adding only missing ones, and preserve existing tags without duplication.
2. A separate, fail-closed *manual Codex startup gate*, explicitly invoked **every time** the agent would be launched, not merely once during boot. The gate must verify all original lab INPUT/FORWARD rules **and**, if the proposed second `proxy_clients` network is to be attached, its pre-enforced INPUT/FORWARD rules, precedence and collision checks. If any rule is missing or altered, the agent must remain stopped. Disallow or operationally restrict bypass via unguarded `docker start` or `docker compose up`. Do not create any auto-start systemd unit for Codex itself.

A single systemd oneshot is **insufficient** to make the lab secure after arbitrary later UFW reloads or Docker chain re-creation. Before approving implementation, decide whether the host needs UFW-supported persisted rules, a dedicated post-Docker firewall reconciliation unit plus explicit hooks for reload paths, or a stricter service dependency design. Protect administrative SSH recovery, preserve DEVELOPMENT/UAT networking, and test exact-match rollback. The optional Squid `outgoing` network needs its own enforced egress isolation. No component should silently grant Squid broad internet/host/private-network access.

**Important remaining blockers:** The source-only validator and all 75 declared Python tests have now executed successfully in an isolated, independent Python workspace; GitHub Actions itself still fails before runner steps, and real Docker/Squid/firewall negative integration tests are still outstanding. There has been no approved host firewall modification, Docker pull/start, network creation, or controlled negative reachability validation. The proposed systemd/UFW plan is **not production-ready**.

## Step 92 — uninstalled original-lab restoration implementation (2026-11-20)

The owner approved continuation of **GitHub-only Step 92 implementation planning**, not execution on `ccpcerpserver`. Source was added on `review/codex-proxy-network-hardening-2026-11-19` to make the proposal inspectable and testable:

- `scripts/security/ccpc_codex_lab_firewall_guard.py`: NEW, **read-only** `preflight`/`verify` for the *original* lab. Fails closed unless root, hostname and Docker daemon identity, stopped/known-label agent with restart disabled, intended original Docker bridge+gateway and iptables-nft backend match. Confirms UFW active and availability/ordering of the `FORWARD → DOCKER-USER` path. `verify` additionally uses exact `iptables -C` calls for the existing `INPUT` host and two `DOCKER-USER` cross-bridge DROPs, and a **token-order-independent** narrow parser of `iptables -S` to ensure they precede other INPUT and forwarding rules. No mutation or container startup mode; every success prints `agent_launch_authorized=False`.
- `scripts/security/systemd/ccpc-codex-lab-firewall-restore.service.example`: NEW, **uninstalled** systemd service *template*, not a `.service` unit. It requires an absent-by-default root-controlled approval marker, intended reviewed scripts in a specifically installed, pinned source tree, and Docker/UFW startup. Its hypothetical future actions would be original-lab guard `preflight` → existing `ccpc_codex_dev_lab_firewall.sh apply` → guard `verify`; it neither starts Codex nor creates a network. The existing original firewall script is unchanged; no ExecStop removes protection. This unit is **inert in GitHub**, not enabled or executed anywhere.
- `codex-dev-agent/tests/test_lab_firewall_guard.py`: NEW, 15 offline mock-only regression methods on rule matching, precedence, refusal of unsafe modes, fail-closed behavior and inert unit structure. Alongside the prior 60 source-only methods the PR now declares **75**; the full Python suite later **executed successfully with 75 tests and 0 failures** in an independent isolated workspace, after each required source file's Git blob SHA was matched. GitHub Actions runner execution remains unverified because jobs fail before any runner steps. The CI path filter also watches the new code and unit template.

### Source-only operational sequence (NOT AUTHORIZATION TO APPLY)

1. Independently verify current host access, operator SSH recovery, agent stopped/restart disabled, no pending host changes, UFW/Docker readiness, the source SHA, script file ownership/mode and the exact existing network bridge ID. Before any future use, inspect the full effective unit dependency graph, Docker socket activation and reload hooks. Reject if the expected state has changed.
2. Preserve a **private**, restorable snapshot of the current *scoped* active firewall/DOCKER-USER rule state without recording raw infrastructure data in GitHub/chat. Record which of the three exact original-lab rules exist and at which positions **before** an operator-approved action.
3. In a reviewed maintenance window and *only after distinct host approval*, choose an approved root-owned installation path and install/validate the scripts and a real service file derived from the template; the example paths and approval marker are placeholders. Do not install new packages or enable any service as part of the GitHub proposal. Require UFW and Docker settled and no other Docker/firewall mutation racing the operation. Do not add automatic Codex startup.
4. The template's intended flow is `preflight` (fails before write on unexpected identity, running agent or changed Docker firewall) → existing exact-scoped `apply` (adds missing original-lab DROP rules idempotently; it rolls back only additions on its own detected partial apply failure) → independent `verify` (checks exact rule existence **and precedence**).
5. On a failed preflight, **make no changes**. On failed apply, use the script's verified partial-addition cleanup and keep Codex stopped. If post-verify fails, leave newly present protective DROP rules in place until an operator reviews the exact state; **do not automatically flush/remove security rules or restart UFW/Docker**.
6. Recheck rules after a separately approved reload or Docker service restart and demonstrate they are reliably restored *without* running Codex while unprotected. The example **does not implement** automatic restore after a later reload. Before any agent launch a separately enforced guard must verify the original rules, new bridge host/cross-bridge rules if deployed, and independently enforced Squid outbound/DNS isolation. This requirement remains unsatisfied by the proposal.

### Exact rollback concept (independently approved host operation only)

- First verify the Codex agent **and optional proxy are stopped**, that the reviewed host identity still matches, and that an administrative SSH/recovery session remains available. Stop and disable only a newly installed CCPC-specific service **if one was actually installed**, then remove only its exact project files/approval marker under an approved, recorded path. Never disable UFW or Docker, and never clean up other workloads.
- Compare before/after exact rule existence and chain positions. If **no new rules were added**, rollback must not remove any original protection. If specific new DROP rules were added by the approved attempt, remove **only those exact additions, by their verified identity**, and only with a separate explicit firewall-removal approval and assurance no agent/proxy could run unprotected. Do not blindly invoke the legacy script's broad `rollback` mode: it removes all matching original lab rules, including rules present before the attempt.
- Post-rollback verification must demonstrate original active lab protections are at least as strong as the pre-change snapshot, Docker/SSH/DEV unaffected, and that neither Codex nor Squid was activated. If state is ambiguous, preserve restrictive DROP rules and hold all starts pending review.
- If an approved installation produced a partial or failed unit, **do not assume systemd will automatically undo its iptables changes**. No `ExecStop` cleanup is included for precisely this reason.

### Specific unresolved go/no-go items

- A oneshot template and a human-operated `verify` are *not* an unbypassable runtime launch gate. Docker-enabled operators can start containers directly, and firewall rules can be changed by a later UFW/Docker reload. An enforcement strategy for all launch/relaunch paths and runtime firewall drift is still required before activation.
- Proposed `proxy_clients` network has not been created. Its pre-enforced firewall and Squid's independent `outgoing` egress/DNS restrictions remain untested and uninstalled.
- Manual negative connectivity tests, UFW/Docker restart/reload tests, actual Python/Squid tests, runner availability, bridge IPAM conflicts and a reviewed proxy image digest/runtime UID are all pending. None of these gates is closed by a test *declaration* or by a GitHub commit alone.
- The service template needs target-host dependency and security review before deriving any installable `.service` file; the approval marker must be root-controlled, and source pinned to reviewed commit rather than arbitrary mutable checkout.

## Step 93 — combined firewall ordering fix and isolated full-test validation (2026-11-20)

**Source-review defect discovered:** `ccpc_codex_lab_firewall_guard.py` and `ccpc_codex_proxy_bridge_preflight.py` initially each required **their own** bridge rule to occupy the first `INPUT` position and first two `DOCKER-USER` positions. Those requirements are mutually incompatible once both networks' protections are pre-installed. Neither a successful isolated unit test nor the old firewall's present state could justify activation with that inconsistency.

**GitHub-only correction:** Added pure, shared `scripts/security/ccpc_firewall_rule_order.py`; both verifiers now use its narrow canonical iptables rule parser, which tolerates reordered nonpermissive flags and either inversion spelling while rejecting unreviewed expressions. It permits the exact original-only prefix (one host DROP, two cross-bridge DROPs), or the complete two-bridge prefix (**two host INPUT DROPs and four DOCKER-USER cross-bridge DROPs in either relative order**) when the new bridge has any rule reference or `require_proxy=True`. A partially installed new bridge, intervening ACCEPT/unknown jump, missing original rule, or unexpected rule before the prefixes causes fail-closed rejection. The helper never executes iptables, Docker, subprocess or network calls.

Added five `test_lab_firewall_guard.py` regression cases for both ordering permutations, partial proxy protection, permits ahead of protections, missing old-bridge rule and alternate inversion syntax. Also updated source-test import paths and the CI file path filters. Total **75 Python unit tests** (60 original + 15 firewall guard).

**Independent execution:** Reconstructed the full source-only test tree in a private isolated local Python workspace using exact content fetched from the private GitHub connector. For each dependent file, computed Git blob SHA and compared with the returned GitHub blob SHA before invoking tests. Executed `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s codex-dev-agent/tests -p 'test_*.py' -v` with no Docker, host network, external credential, Squid binary or host file modifications. **Result: Ran 75 tests; OK; 0 failures, 0 errors.** Synthetic-secret test data was generated only under a temporary directory, without sharing values. This validates the Python source-only security assertions, not actual Docker Compose renderer semantics, proxy resolution, rule persistence, or live isolation.

**Persistent CI blocker remains separate:** The latest GitHub Actions job on the review branch has still failed before assigning a runner or recording any steps, with job log requests returning `BlobNotFound`/404. An unrelated scheduled `Autoupdate pre-commit hooks` workflow also failed with no runner and zero steps (run `44563127843`), supporting a broader runner provisioning/account-level concern rather than blaming only the new test code. Root cause is **not verified**; possible runner provisioning, plan/usage/billing restriction or temporary GitHub service issues should be checked via the **workflow-run Summary/Annotations and account Actions usage**, with no payment-method/budget changes authorized. Do not repeatedly rerun or change workflow syntax without concrete evidence.

**NO-GO unchanged:** Draft PR #39 remains unmerged. No host firewall persistence or reload recovery mechanism installed, no unbypassable runtime launch gate, no second bridge created, no Squid egress/DNS enforcement or actual negative tests. Nothing was deployed to DEVELOPMENT/PRODUCTION. A successful source-only suite is necessary but insufficient for activation.

## Immediate next action

The offline 75-test suite has passed independently; next resolve the GitHub Actions runner **pre-execution** failure by reading the run Summary/Annotations and Actions usage status without enabling paid services, then address unbypassable runtime startup gating, firewall reload persistence, the second bridge and Squid egress. No host command is requested at this checkpoint.

**Release gate:** NO-GO. Draft PR #39 remains unmerged. Agent stopped, Squid inactive, bridge uncreated, DEVELOPMENT and PRODUCTION untouched.
