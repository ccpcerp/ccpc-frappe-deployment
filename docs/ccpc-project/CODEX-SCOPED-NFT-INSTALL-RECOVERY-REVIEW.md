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


## Step 112 — Stage A private host baseline reported PASS (2026-11-20)

**Operator execution evidence (sanitized stdout pasted directly by owner):** The owner ran the separately authorized Step 111 Stage A baseline command on `ccpcerpserver` and reported the following exact output:

```text
host_verified=True
agent_stopped=True
private_baseline_saved=True
kernel_rules_modified=False
services_restarted=False
codex_launch_authorized=False
```

**Status: Stage A PASS as reported by the operator.** The command confirmed hostname, stopped known Codex agent, restart policy disabled, and stock nftables.service inactive/disabled before creating a fresh, root-private directory using `mktemp -d` and `umask 077`. It then saved five nonempty private references: IPv4 and IPv6 `iptables-save` output, `nft -j list ruleset`, routes, and selected service states. The command included **no firewall mutation or service restart**. ChatGPT had no direct SSH access; the private saved files and free space/permissions were not independently re-inspected. The owner confirmed a second working recovery session at Step 110. Never upload raw baseline data or even its private filesystem pathname to a public repository or chat.

**Stage B (not yet authorized):** Prepare a pinned, minimal **source-only staging** transaction for the exact GitHub review commit, limited to `ccpc_codex_nft_scoped_controller.py`, `ccpc_codex_nft_guard_review.py`, `ccpc_codex_lab_firewall_guard.py`, and `ccpc_firewall_rule_order.py`. The source staging must create no root approval marker, add no systemd unit, install no kernel nftables table or firewall rule, start/stop no containers, and make no change to DEVELOPMENT/PRODUCTION. Require owner approval of the **exact commands** before staging; do not treat Stage A approval as Stage B authorization. The staged source must have independently verified immutable commit/content provenance and restrictive ownership/mode, no symlinks or existing target overwrite, and a failure path that does not accidentally execute staged code. The source may be reviewed read-only after staging. A later Stage C separate project-table installation remains **NO-GO** until the exact reviewed command, negative canaries, restart/reload lifecycle, trust boundary and rollback are accepted.


## Stage B — exact source-only staging proposal (requires separate approval)

**State:** Stage A baseline reported PASS by the operator. The following is a **candidate for command-level Stage B approval only**; do not run it before the owner explicitly approves Stage B. Stage B is *source-only* and does not authorize kernel firewall changes, creating a marker, adding a systemd unit or Codex/Squid activation.

**Fixed source provenance (checked against connected GitHub by exact immutable code commit):**

- Repository: `ccpcerp/ccpc-frappe-deployment`
- Pinned source commit: `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`
- Four exact Git blob IDs are embedded in the script below; it downloads only these four source modules by commit-pinned unauthenticated HTTPS, compares `git hash-object` to the verified GitHub blob IDs and does not execute the downloaded Python.
- New root-owned staging target: `/opt/ccpc/codex-lab-review/scripts/security/`; require no existing target or symlink, safe root-controlled `/opt` ancestry and a private `/opt/ccpc` directory. No changes to unrelated files; a failed download can leave a **root-only temporary staging directory** for review. No force overwrite or global cleanup.
- Expected kernel/network effect: **NONE**. `curl` makes a short outbound HTTPS fetch of public code from GitHub; Stage B should be skipped if that host does not have approved outbound network access. No credentials or production information are sent.

```bash
sudo bash <<'CCPC_STAGE_B'
set -euo pipefail
test "$(hostname -s)" = "ccpcerpserver"
test "$(docker inspect --format '{{.State.Running}}' ccpc_codex_dev_agent-agent-1)" = "false"
test "$(docker inspect --format '{{.HostConfig.RestartPolicy.Name}}' ccpc_codex_dev_agent-agent-1)" = "no"
test "$(systemctl show --value -p ActiveState nftables.service)" = "inactive"
test "$(systemctl show --value -p UnitFileState nftables.service)" = "disabled"
command -v curl >/dev/null
command -v git >/dev/null
test ! -e /opt/ccpc/codex-lab-review
test ! -L /opt/ccpc/codex-lab-review

python3 - <<'PY'
import os, stat
for path in ("/opt", "/opt/ccpc"):
    if os.path.lexists(path):
        s = os.lstat(path)
        if (not stat.S_ISDIR(s.st_mode) or
                s.st_uid != 0 or s.st_gid != 0 or
                (stat.S_IMODE(s.st_mode) & 0o022)):
            raise SystemExit("STOP: unsafe staging parent")
        if path == "/opt/ccpc" and stat.S_IMODE(s.st_mode) != 0o700:
            raise SystemExit("STOP: unexpected parent permissions")
PY

umask 077
if test ! -d /opt/ccpc; then
    mkdir -m 0700 /opt/ccpc
fi
stage="$(mktemp -d /opt/ccpc/.codex-review-stage.XXXXXXXX)"
mkdir -m 0700 -p "$stage/scripts/security"
commit="66960f73a69b10b59f508cda7bfd4ac9ea5c21af"

while read -r filename git_blob; do
    target="$stage/scripts/security/$filename"
    curl --fail --silent --show-error --location --proto '=https'         --proto-redir '=https' --tlsv1.2 --connect-timeout 10         --max-time 45 --retry 2         --output "$target"         "https://raw.githubusercontent.com/ccpcerp/ccpc-frappe-deployment/$commit/scripts/security/$filename"
    test -s "$target"
    test "$(git hash-object -- "$target")" = "$git_blob"
    chmod 0400 "$target"
done <<'CCPC_BLOBS'
ccpc_codex_nft_scoped_controller.py e07b1afcb39761fb0f5613c83c5f97b4aee46d22
ccpc_codex_nft_guard_review.py eabbbfd5d5de4cdcf4e5e0c25732bf3c641ffdc4
ccpc_codex_lab_firewall_guard.py 619d8dd962e3c995b53d57ac4c55a85ace2e4eab
ccpc_firewall_rule_order.py af9a63bc8a390905a7e0da78e8c0b20c7f8af537
CCPC_BLOBS

printf '%s\n' "$commit" > "$stage/REVIEWED_SOURCE_COMMIT"
chmod 0400 "$stage/REVIEWED_SOURCE_COMMIT"

# Refuse to overwrite an existing review installation.
test ! -e /opt/ccpc/codex-lab-review
test ! -L /opt/ccpc/codex-lab-review
mv -T -n -- "$stage" /opt/ccpc/codex-lab-review
test ! -e "$stage"
test -d /opt/ccpc/codex-lab-review

printf 'host_verified=True\nagent_stopped=True\n'
printf 'source_commit_pinned=True\nall_four_git_blobs_verified=True\n'
printf 'root_only_review_source_staged=True\n'
printf 'firewall_modified=False\nservices_modified=False\n'
printf 'codex_launch_authorized=False\nSTAGE_B_SOURCE_ONLY_COMPLETE\n'
CCPC_STAGE_B
```

**Proposed successful report:** `host_verified=True`, `agent_stopped=True`, `source_commit_pinned=True`, `all_four_git_blobs_verified=True`, `root_only_review_source_staged=True`, `firewall_modified=False`, `services_modified=False`, `codex_launch_authorized=False`, `STAGE_B_SOURCE_ONLY_COMPLETE`. Do not share a root-only filesystem dump; the status flags suffice.

**Recovery boundary:** If the pinned source cannot be fetched or one blob does not match, STOP. Nothing operational is installed. Do not change permissions on an existing `/opt/ccpc` directory, delete a suspicious existing path, or force a Git branch switch. No host code is executed as part of this stage. Removal of staged files, installation of an approval marker, execution of `install`, any service manipulation, canaries, restart/reload and Codex start each require a new explicitly reviewed action.

