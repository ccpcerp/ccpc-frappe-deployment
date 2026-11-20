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
