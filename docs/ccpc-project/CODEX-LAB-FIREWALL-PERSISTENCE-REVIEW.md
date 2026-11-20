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

## Immediate next action

Use a single guard-checked **read-only** host inspection to identify whether Docker and UFW are enabled at boot, whether the existing Codex agent has a Docker restart policy, and whether the Docker service is ordered with respect to UFW. Report booleans/status only, no raw unit contents, network details or secrets. This will inform (but not approve) a persistent fail-closed design.

**Release gate:** NO-GO. Draft PR #39 remains unmerged. Agent stopped, Squid inactive, bridge uncreated, DEVELOPMENT and PRODUCTION untouched.
