# CCPC scoped nftables controller — installation and recovery review

**Status: DRAFT SOURCE REVIEW ONLY — DO NOT EXECUTE AS HOST INSTRUCTIONS.**
**Date:** 2026-11-20 (Asia/Manila). **Authoritative review:** PR #39 branch `review/codex-proxy-network-hardening-2026-11-19`.
**No operational approval yet** to install or run any service, change an iptables/nftables rule, restart Docker or UFW, enable nftables.service, reboot, or start Codex.

## Verified observations and constraints

The owner's read-only Step 109 output from `ccpcerpserver` was:

```text
agent_stopped=True
dedicated_nft_unit_name_available=True
offline_launch_unit_name_available=True
review_install_directory_already_exists=False
host_changes_performed=False
codex_launch_authorized=False
READ_ONLY_CHECK_COMPLETE
```

Step 107 confirmed the independent table absent and the candidate `nft --check` syntax valid on the target host; Step 108 found stock `nftables.service` inactive/disabled, **ExecStart and ExecReload use `/etc/nftables.conf` containing a global `flush ruleset`, and ExecStop also flushes the ruleset**. Therefore **never use or enable stock nftables.service** as the Codex persistence mechanism; it might clear unrelated Docker/UFW rules.

Earlier read-only Steps 103–104 verified the original-lab three iptables DROP rules and their precedence while the agent was stopped. No live network negative tests, UFW/Docker reload, reboot or run-time guard have occurred. The agent's resource/image/mount baseline is not yet approved.

## Proposed source package — not installed on the host

| Review-only artifact | Intended role | Operational status |
|---|---|---|
| `scripts/security/ccpc_codex_nft_guard_review.py` | Render and strictly verify a four-DROP independent nftables policy | Read-only and GitHub-hosted syntax checked |
| `scripts/security/ccpc_codex_nft_scoped_controller.py` | Marker-guarded, locked, one-table-only idempotent installation if absent; strict verification if present | Source only; install mode requires an **absent-by-default** approval marker |
| `scripts/security/systemd/ccpc-codex-nft-guard.service.example` | Manual-only, inert oneshot template with plan/install/verify | **Not a loadable unit**, no `[Install]` or `ExecStop` |
| `scripts/security/ccpc_codex_lab_firewall_reconcile.py` | Separate original-lab scoped iptables restoration proposal | Uninstalled and not an automatic reload hook |
| `scripts/security/ccpc_codex_lab_start_interlock.py` | Read-only offline prelaunch policy check, requiring both layers | Not an unbypassable launch controller |

The controller refuses to operate if the stock nftables service is enabled or active; rejects mismatched source/host/bridge, changed original rules, ambiguous table names, or altered project-table contents. For an absent table only it passes the generated project table through native nftables check mode, reruns preconditions, and submits **one `nft --file -` transaction containing only the new `table inet ccpc_codex_lab_guard`**. It does not call the stock service, `flush ruleset`, UFW/Docker restarts, or automatic Codex startup. On failed post-application verification the table is left in place for scoped administrator investigation, rather than removing restrictive policy.

This design cannot prevent a concurrent privileged system process from recreating Docker networking, flushing nftables or starting the stopped agent between checks. A systemd oneshot cannot ensure an ongoing barrier or recovery after arbitrary UFW/Docker reload.

## Pre-installation approval gate — mandatory, currently incomplete

1. Confirm source review PR #39 has an **exact reviewed full commit SHA**, source install path is absent or a pre-approved root-owned target (no symlinks or uncommitted DEV changes), and intended script bytes match GitHub. Keep a private manifest of installed files and hashes. No on-host network fetch in the service.
2. Confirm root/SSH recovery with a **second independently working administrator session or console**, and a named rollback operator. Verify the current host isn't in a shared infrastructure maintenance operation; preserve other running DEV/UAT services.
3. Preserve a **private, restorable** pre-change snapshot of original iptables/nftables rules, host route/service states, current network identity, and administrator SSH accessibility. Store securely *on host/private backup*, not this public GitHub repository or chat. Inspect snapshots locally for credentials before dissemination.
4. Confirm the Codex agent and optional proxy are stopped, auto-restart disabled, original three iptables rules exact and leading, no unapproved proxy-client bridge, stock nftables.service disabled/inactive and original bridge stable. Confirm no existing project nftables table with unknown content.
5. Approve **individual exact operations** and file ownership/modes (reviewed source checkout, dedicated marker, optional manual-only unit). Never create the marker merely as part of an exploratory read-only diagnostic.
6. Check effective systemd dependency graph and syntax with a local read-only verification, including Docker socket activation, UFW and Docker reload effects. **Do not enable/start stock nftables.service**. Do not add automatic Codex startup/activation hooks.

## Proposed operator-controlled test and rollback sequence (not authorized)

**Hold before any write:** two recovery channels working, scoped private baseline captured, source verified, agent and proxy stopped, separate command-level approval recorded.

**Bounded test, after approval only:** stage reviewed root-owned source offline; ensure proposed dedicated project service name is unused; add only the exact owner-approved project marker; run controller read-only `plan`; if all prerequisites pass, have the operator run the single project-scoped install action; then independent read-only verification of the exact nft JSON table, original iptables rules, Docker/SSH/DEVELOPMENT health and agent still stopped. Do not set systemd auto-enable or start any agent.

**Failure:** if before the kernel transaction, stop with **no modifications**. If during or after the transaction, stop and retain project-specific restrictive DROP rules until a recovery operator verifies the full exact state. Do not run global nft flush, restore all host firewall rules over UFW/Docker state, restart shared services or undo existing original-lab DROP rules. Do not issue an automatic `ExecStop` deletion.

**Scoped rollback, only after separate approval and exact identity checks:** remove only newly installed project-owned unit/authorization artifacts; if removal of the independently installed *project-only* nft table is specifically required, first independently prove Codex and Squid stopped/restart disabled, existing original-lab firewall protections intact, table contents still match the reviewed policy, no dependency on the table, and recovery access intact. Then authorize an exact deletion of the **single CCPC-owned table** only. If any drift occurs, leave the deny table in place and review rather than guess. Never flush shared chains or alter UFW/Docker service settings.

## Remaining integration and deployment gate

- Validate actual nft JSON representation on the target kernel; strict mock comparison can fail closed on harmless formatting differences.
- Perform **controlled nonproduction negative packet tests** for original bridge → host, other Docker bridges, and permitted synthetic DB/Redis service continuity, with no PRODUCTION target probes.
- Separately validate the **actual lifecycle** of UFW/Docker reload and reboot with known recovery procedure. The original bridge's interface name can change on Docker network recreation, invalidating name-based rules.
- Demonstrate that no Codex process can operate while protection disappears. Cooperative prelaunch checks plus polling do **not** guarantee zero-gap blocking. A privileged Docker/host administrator can bypass these checks.
- Verify image provenance/digest, memory/process ceilings, secret/volume isolation, user privileges, Codex CLI sandbox and authentication, and Squid outbound/DNS enforcement if an online path is ever proposed.
- Consider **dedicated VM/host isolation** for Codex if shared-host reload/startup continuity cannot be independently enforced.

**NO-GO for Codex and Squid.** The owner approved continued **GitHub engineering**, not host installation or production changes.


## Step 110 — operator-confirmed independent recovery channel and proposed baseline capture (2026-11-20)

The owner explicitly confirmed a **second working SSH/administrator recovery connection** to `ccpcerpserver` after Step 109. This is an **owner attestation**, not a ChatGPT-executed connectivity test or a promise of out-of-band access after total network failure. Keep both sessions open; the second connection must not depend on the Codex container.

**Current PR #39 source checkpoint:** `f3b26fb2ebcc5189625cf131cc8454d40f131c93` (draft/unmerged). GitHub Actions [run 44684328438](https://github.com/ccpcerp/ccpc-frappe-deployment/actions/runs/44684328438) executed **161/161 mocked/source-only tests** and native nftables check-only syntax successfully. No real host table is installed and Codex remains NO-GO.

**Next separate authorization requested: Stage A private baseline snapshot only**, before code staging, project marker creation, installing project nftables policy, any service file, enabling units, UFW/Docker reload, reboot, or Codex start. The following command block is **PROPOSED FOR OWNER REVIEW — DO NOT EXECUTE WITHOUT SPECIFIC STAGE A APPROVAL**:

```bash
sudo bash <<'CCPC_PRIVATE_BASELINE'
set -euo pipefail
test "$(hostname -s)" = "ccpcerpserver"
test "$(docker inspect --format '{{.State.Running}}' ccpc_codex_dev_agent-agent-1)" = "false"
test "$(docker inspect --format '{{.HostConfig.RestartPolicy.Name}}' ccpc_codex_dev_agent-agent-1)" = "no"
test "$(systemctl show --value -p ActiveState nftables.service)" = "inactive"
test "$(systemctl show --value -p UnitFileState nftables.service)" = "disabled"
umask 077
snapshot="$(mktemp -d /root/ccpc-codex-nft-preinstall.XXXXXXXX)"
iptables-save > "$snapshot/iptables.v4"
ip6tables-save > "$snapshot/iptables.v6"
nft -j list ruleset > "$snapshot/nftables.json"
ip -j route show table all > "$snapshot/routes.json"
systemctl show --no-pager -p ActiveState -p UnitFileState     nftables.service ufw.service docker.service > "$snapshot/services.txt"
for file in iptables.v4 iptables.v6 nftables.json routes.json services.txt; do
    test -s "$snapshot/$file"
done
printf 'host_verified=True\nagent_stopped=True\nprivate_baseline_saved=True\n'
printf 'kernel_rules_modified=False\nservices_restarted=False\n'
printf 'codex_launch_authorized=False\n'
CCPC_PRIVATE_BASELINE
```

This block creates a **new root-only directory under /root** and writes reference snapshots into it; it does **not** install/reload/flush a firewall or start/stop Docker. There is a small storage/I/O footprint and it saves raw firewall, routes and service context that must remain **private on the server**. It is a recovery reference, **not** permission to blindly run `iptables-restore` or `nft -f` against the snapshot: full restoring could overwrite shared DEVELOPMENT/UFW/Docker networking. If any precondition fails, stop and investigate privately; the command may leave a partial, root-only directory for administrator inspection. Do not paste the raw files, the private snapshot path, Docker env, credentials or rule dumps into this public repository or chat. Send back only the six booleans.

**Separate later installation approval:** Before any attempt to create the marker or run `ccpc_codex_nft_scoped_controller.py install`, verify the exact source SHA/hash on the host, the project path ownership/no symlinks, current original bridge iptables rule checks and nft table absence, and a specific, scoped project-table rollback. Do not enable stock nftables.service, change global rules or start Codex. A dedicated controller is not reload persistence or zero-gap runtime enforcement.



## Step 111 — Stage A baseline capture approved, execution not yet verified (2026-11-20)

**Explicit owner authorization:** In response to the Step 110 command-level question, the owner replied **“Approved”**. Authorization is limited to executing the **exact private baseline capture** block documented above on `ccpcerpserver`: pre-check host identity, agent stopped/no auto-restart, stock nftables.service inactive/disabled; create a fresh root-only directory under `/root` and save `iptables-save`, `ip6tables-save`, `nft -j list ruleset`, full route JSON and selected service state outputs, then check that the files are nonempty. Keep raw snapshot data local and private. A second independent SSH recovery connection was confirmed in Step 110.

**Execution status:** **NOT EXECUTED BY CHATGPT and NOT YET VERIFIED ON THE HOST.** Connected GitHub does not provide host access; only the operator can run the already approved block and return its sanitized booleans. Snapshot creation writes private local files but makes no kernel firewall changes, service starts, reloads or container operations. If a command fails, preserve the stopped agent and do not proceed to Stage B.

**Still NOT approved:** Copying/pulling source into host paths, creating the authorization marker, installing/running the scoped nft controller or systemd unit, enabling `nftables.service`, restarting/reloading UFW or Docker, any reboot, running Codex/Squid, network probes, or PRODUCTION/DEVELOPMENT changes. A saved snapshot alone is not a verified restore/rollback procedure; never restore it wholesale over UFW/Docker.

