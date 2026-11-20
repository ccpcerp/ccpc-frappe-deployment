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


## Step 113 — Stage B pinned source staging approved; host execution pending (2026-11-20)

**Approval:** The owner explicitly responded **“aPPROVED”** to the exact **Stage B source-only staging** procedure already documented in this file. This authorizes running that exact, bounded block on `ccpcerpserver` **once**, while maintaining the previously confirmed second administrator/recovery connection; it does not authorize any new or changed host command not contained in the reviewed Stage B script. The private Stage A baseline was previously reported complete; do not expose its files.

**GitHub verification before execution:** Connected GitHub on current draft PR #39 branch `review/codex-proxy-network-hardening-2026-11-19` returned the same four blob SHA values as embedded in the approved host script, each verified specifically at immutable source commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`: controller `e07b1afcb39761fb0f5613c83c5f97b4aee46d22`, nft guard `eabbbfd5d5de4cdcf4e5e0c25732bf3c641ffdc4`, original-lab firewall guard `619d8dd962e3c995b53d57ac4c55a85ace2e4eab`, rule ordering `af9a63bc8a390905a7e0da78e8c0b20c7f8af537`. These are Git **blob** hashes, not SHA-256; Stage B verifies them with `git hash-object` before final rename. Review branch head is documentation-only beyond the immutable pinned code. No host operation has been executed by ChatGPT.

**Authorized effects:** After exact hostname, stopped-agent/no-restart and disabled/inactive stock nftables.service checks, and safe destination root ownership/no existing target, create `/opt/ccpc` if absent with mode 0700, create one root-private temporary staging directory, download only the four pinned files using HTTPS, compare all four Git blob hashes, set source files read-only and atomically move the directory to `/opt/ccpc/codex-lab-review` without overwriting existing files. It generates a short local commit marker file. A failed precondition/download/hash leaves firewall and services unchanged; a root-only temporary staging directory may remain. Do not print downloaded source or dump host details.

**Execution status:** **Awaiting operator's sanitized terminal output.** Success requires all nine output lines ending `STAGE_B_SOURCE_ONLY_COMPLETE`; any failure/partial output is STOP, no cleanup or next stage without review. Do **not** create the root approval marker, invoke `install` or `nft -f`, install/enable a service, reload UFW/Docker, or launch Codex/Squid. Stage C kernel table installation remains separately unapproved. Codex activation remains **NO-GO**.



## Step 114 — Stage B source-only staging operator-reported PASS (2026-11-20)

The owner returned the terminal echo `CCPC_STAGE_B` and **all nine exact expected completion lines** from the separately approved Stage B source-only procedure on `ccpcerpserver`:

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

**Interpretation and provenance:** Operator-reported Stage B **PASS**. By the reviewed command, the host checks passed, an originally absent root-controlled `/opt/ccpc/codex-lab-review` directory was created after staging four `scripts/security/*.py` files downloaded by HTTPS at immutable commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af` and checked by exact Git blob IDs. The files are staged root-read-only, and the commit marker was stored. The last command successfully required the temporary staging path to be absent and the final directory to exist. The operator-reported booleans do **not** equal an independent live host inspection by ChatGPT; file bytes, symlinks/modes after staging, services, and current firewall have not yet been rechecked in this conversation.

**Authorized filesystem effect:** Only review-source files and private parent directories; **no authorization marker, systemd unit, nftables table, original firewall mutation, UFW/Docker reload, or Codex/Squid process start**. Stage A private firewall baseline remains on the host, not uploaded or restored. Keep the second independent administrator recovery connection available.

**Next read-only gate — Stage B post-stage recheck, not Stage C installation:** Independently verify only the precise four files and recorded commit under a root-owned, no-symlink review directory, their Git blob IDs/0400 owner-only modes, stopped-agent/restart disabled and inactive/disabled stock nftables.service; verify the proposed nft table remains absent. Do not import or execute downloaded Python in the validation step. No need to print private paths, raw nft/iptables data or secrets. If any value differs, STOP; do not change permissions or delete files without a reviewed recovery step.

**Still not approved:** Creating `/etc/ccpc/codex-lab-nft-guard-authorized`, running `ccpc_codex_nft_scoped_controller.py install`, installing/enabling a systemd service, nft/iptables mutation, UFW/Docker reload or reboot, host test probes, or Codex/Squid activation. The next firewall installation would require separate exact-command approval with a live negative-canary and scoped rollback plan; a staged controller is not runtime/persistence protection.


## Step 115 — independent post-staging verification returned STOP (2026-11-20)

The owner pasted the last lines of the read-only Stage B post-staging verification Python command:

```text
except Exception:
    print("STOP: Stage B post-staging verification failed")
PY
STOP: Stage B post-staging verification failed
```

**Result: independent verification FAILED / specific predicate UNKNOWN.** The prior Step 114 staging reported all four exact Git blobs verified and the final root-only path staged, but that does not substitute for the new check. The Python verification used a broad catch-all that prints only a generic STOP. No exception type, failing predicate or raw state was disclosed. It would be incorrect to infer a hash mismatch, permissions error, firewall drift or failed source staging from this output alone. Operator ran a read-only inspector; no mutation is indicated. **Do not rerun Stage B, chmod, delete staged files, change firewall, create a marker or proceed to Stage C.** Codex/Squid remain NO-GO.

**Next operator-safe action:** a separately supplied *read-only* stage-labelled diagnostic using `sudo python3 -I`: (1) verify host and agent stopped/restart disabled, (2) check exact parent and child directory ownership/modes and entries, (3) marker contents and four Git blob hashes, (4) stock nftables.service inactive/disabled, and (5) project nft table absence. It may print **only the first failing fixed diagnostic label** and no raw configuration, permissions, route, credentials or private baseline paths. Do not execute or import staged Python files, write/fix permissions, or run firewall mutation commands. A failed check still blocks Stage C. Further source-side documentation after owner diagnostic is permitted; Stage C would require separate command-level owner authorization and test/recovery review.


## Step 116 — Stage B first-failure diagnostic now PASS; previous STOP unresolved (2026-11-20)

After the generic STOP in Step 115, the owner ran the separately provided **read-only first-failed-check diagnostic** on `ccpcerpserver` and supplied:

```text
PY
ALL_STAGED_SOURCE_CHECKS_PASSED=True
NO_CHANGES_PERFORMED=True
STAGE_C_AUTHORIZED=False
READ_ONLY_DIAGNOSTIC_COMPLETE
```

`PY` here is the heredoc terminator copied with the console output, **not** an error. The script used `sudo python3 -I`, checked root/hostname, agent stopped and restart disabled, root-only directory ancestry and exact entries, the pinned commit marker, **all four Git blob IDs and owner-only mode 0400**, stock nftables.service inactive/disabled, and named independent nft table absent. Every labelled assertion completed without failure; the command deliberately did not execute/import staged Python and made **no changes**. This is **operator-supplied** evidence, not direct assistant inspection. The earlier generic STOP's root cause remains **unexplained**; no fault is proven or repaired. Current results restore the **Stage B read-only verification gate to PASS at the observed instant**, not Stage C installation authorization.

**Next bounded review candidate:** a newly authorized **read-only controller `plan` execution**, after separate review of staged source/hash, to validate its actual system/iptables preconditions against the live host. This would execute the reviewed controller source as root but should use `python3 -B` to avoid bytecode writes and `plan` only (never `install`). A passing `plan` is necessary but not sufficient for actual firewall installation. The controller has **no effective ongoing runtime guard** and source-only testing cannot establish kernel packet isolation. No authorization marker, systemd unit, nft table, UFW/Docker reload or Codex start is approved; keep **Codex NO-GO**.



## Step 117 — read-only staged controller plan approved; host execution pending (2026-11-20)

**Owner's explicit authorization:** Following the successful Stage B labelled diagnostic in Step 116, the owner replied **“Approved”** to **read-only staged-controller `plan` mode only**, not Stage C installation or any firewall mutation.

**Exact approved command on `ccpcerpserver` only** (with existing independent administrator recovery connection maintained):

```bash
sudo python3 -B /opt/ccpc/codex-lab-review/scripts/security/ccpc_codex_nft_scoped_controller.py plan
```

The GitHub-connected code was re-fetched before this approval was recorded. Its file blob `e07b1afcb39761fb0f5613c83c5f97b4aee46d22` at immutable reviewed code commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af` matches the staged-file provenance from Step 116. The `plan` branch calls `ready_bridge()` (existing root/host/Docker/known stopped-agent, original bridge identity, original three iptables DROP rules and precedence, stock nftables.service disabled/inactive) and `table_state()` (read-only `nft -j list tables`). If the CCPC table were unexpectedly present, the code additionally verifies its exact contents without changing them. There is no root-authorization marker required in `plan` mode and no `nft -f` transaction. The `-B` flag prevents Python bytecode cache writes.

**Anticipated output only if checks pass and the independent table is still absent:**

```text
PROJECT_NFT_TABLE_STATE=absent
agent_launch_authorized=False
reload_reboot_runtime_enforcement_verified=False
INSPECTION_COMPLETE
```

If checks fail, the code returns a nonzero exit and prints `STOP: scoped nft controller check failed` without raw firewall configuration. Do not retry through `install`, create a marker, change permissions, restart any service or use a broader shell wrapper. Request the sanitized output and review the cause before any further action.

**Execution state:** **NOT YET RUN / NOT YET VERIFIED**. Owner will run the single command and paste output. Stage C remains unapproved. No host install/service/reload, negative network tests, proxy or Codex start authorized. This plan cannot verify reboot persistence or zero-gap runtime containment.

## Step 118 — staged controller plan passed; Stage C remains unapproved (2026-11-20)

**Operator-supplied result of precisely authorized read-only `plan`:**

```text
PROJECT_NFT_TABLE_STATE=absent
agent_launch_authorized=False
reload_reboot_runtime_enforcement_verified=False
INSPECTION_COMPLETE
```

**Assessment:** Stage 117's exact `sudo python3 -B /opt/ccpc/codex-lab-review/scripts/security/ccpc_codex_nft_scoped_controller.py plan` command completed its four expected status lines. The pinned source's `plan` path checks the intended host/root, Docker daemon/bridge/subnet identity, known stopped original agent with restart disabled, correct three original-lab INPUT and DOCKER-USER DROP rules and precedence, UFW active, stock nftables.service inactive/disabled, and the absence of the independent named CCPC table. **Read-only installation prerequisites passed at that instant.** The operator output is the evidence; ChatGPT did not directly connect to the server and did not independently examine any private firewall or snapshot files.

**Critical distinctions:** There is **no independently installed `inet ccpc_codex_lab_guard` table**; `agent_launch_authorized=False` and `reload_reboot_runtime_enforcement_verified=False` correctly remain. A read-only plan checks readiness but does not establish live filtering, negative network-test results, daemon reload/reboot persistence, or any guaranteed uninterrupted isolation under privileged host operations.

**Stage C decision hold:** Owner approved only `plan`, **not** authorization-marker creation, root-only filesystem mutations beyond previous Stage B, `install` mode, systemd unit installation, nftables state mutation, Docker/UFW restart, agent/online Squid startup or PRODUCTION/DEVELOPMENT actions. Stage A private baseline and two SSH/admin recovery connections remain the operator-reported prerequisites. Before submitting a bounded Stage C installation command for **separate explicit approval**, review root-marker path/ownership/no-symlink checks, exact immutable source SHA, current host/agent/iptables guard recheck, prior baseline storage, no global `flush ruleset`, limited table-only mutation, preservation of restrictive policy on failure, and an exact, separately authorized project-table-only rollback when agent remains stopped. A one-shot install will not solve future reload loss or Docker manual-start bypass; Codex remains **NO-GO**.



## Proposed Stage C — single-table install and temporary-marker cleanup (NOT APPROVED)

**Status:** Drafted after the operator's read-only **Step 118 `PROJECT_NFT_TABLE_STATE=absent`** result. **NO AUTHORIZATION TO EXECUTE**. This is a proposed Stage C host mutation, unlike Steps A/B and `plan`. It intentionally excludes systemd installation, unit enablement, Docker or UFW reload, reboot, Codex/Squid startup and any proxy bridge. Owner must separately approve the **exact command** after reviewing possible impact on existing synthetic-lab connections.

**Risk and scope:** The rule transaction adds a new **inet** table with four DROP rules: laboratory-bridge → host INPUT, host → laboratory bridge OUTPUT, and both cross-bridge forwarding directions; same-bridge lab traffic should remain unaffected by these rules but only live tests can prove it. The policy cannot guarantee reload/reboot persistence, protection after bridge recreation, or defense against privileged manual Docker starts. It may affect host-to-lab access; keep a second administrator SSH/recovery session and the Stage A private firewall baseline. Do **not** enable/reload/stop stock `nftables.service` because its effective unit lifecycle uses global `flush ruleset`. No other shared chain/table should be touched by the audited controller.

**Proposed command — NOT YET APPROVED, DO NOT EXECUTE:**

```bash
sudo python3 -I - <<'PY'
import os
import stat
import subprocess
import sys
from pathlib import Path

BASE = Path("/opt/ccpc/codex-lab-review")
CONTROLLER = BASE / "scripts/security/ccpc_codex_nft_scoped_controller.py"
MARKER = Path("/etc/ccpc/codex-lab-nft-guard-authorized")
BODY = b"CCPC_CODEX_NFT_GUARD_INSTALL_APPROVED\n"
EXPECTED_COMMIT = "66960f73a69b10b59f508cda7bfd4ac9ea5c21af"
BLOBS = {
    "ccpc_codex_nft_scoped_controller.py":
        "e07b1afcb39761fb0f5613c83c5f97b4aee46d22",
    "ccpc_codex_nft_guard_review.py":
        "eabbbfd5d5de4cdcf4e5e0c25732bf3c641ffdc4",
    "ccpc_codex_lab_firewall_guard.py":
        "619d8dd962e3c995b53d57ac4c55a85ace2e4eab",
    "ccpc_firewall_rule_order.py":
        "af9a63bc8a390905a7e0da78e8c0b20c7f8af537",
}

def require(condition):
    if not condition:
        raise RuntimeError("precondition failed")

def run(*argv, timeout=90):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    require(p.returncode == 0)
    return p.stdout.strip()

def root_dir(path, exact_mode=None):
    st = os.lstat(path)  # Reject symlinks.
    require(stat.S_ISDIR(st.st_mode) and st.st_uid == 0
            and st.st_gid == 0 and not (st.st_mode & 0o022))
    if exact_mode is not None:
        require(stat.S_IMODE(st.st_mode) == exact_mode)

def root_file(path):
    st = os.lstat(path)
    require(stat.S_ISREG(st.st_mode) and st.st_uid == 0
            and st.st_gid == 0 and stat.S_IMODE(st.st_mode) == 0o400)

try:
    require(os.geteuid() == 0)
    require(run("hostname", "-s") == "ccpcerpserver")
    root_dir("/opt")
    root_dir("/opt/ccpc", 0o700)
    root_dir(BASE, 0o700)
    root_dir(BASE / "scripts", 0o700)
    root_dir(BASE / "scripts/security", 0o700)
    root_file(BASE / "REVIEWED_SOURCE_COMMIT")
    require((BASE / "REVIEWED_SOURCE_COMMIT").read_text()
            == EXPECTED_COMMIT + "\n")
    require(set(os.listdir(BASE / "scripts/security")) == set(BLOBS))
    for filename, sha in BLOBS.items():
        target = BASE / "scripts/security" / filename
        root_file(target)
        require(run("git", "hash-object", "--", str(target)) == sha)

    # Stage A was a private recovery reference, not wholesale restore permission.
    found_private_snapshot = False
    for snap in Path("/root").glob("ccpc-codex-nft-preinstall.????????"):
        try:
            root_dir(snap, 0o700)
            if all(
                (snap / name).is_file() and (snap / name).stat().st_size > 0
                for name in ("iptables.v4", "iptables.v6",
                             "nftables.json", "routes.json", "services.txt")
            ):
                found_private_snapshot = True
                break
        except (OSError, RuntimeError):
            continue
    require(found_private_snapshot)

    plan = run(sys.executable, "-B", str(CONTROLLER), "plan")
    require("PROJECT_NFT_TABLE_STATE=absent" in plan.splitlines())
    require("agent_launch_authorized=False" in plan.splitlines())
    require(not os.path.lexists(MARKER))
    root_dir("/etc")
    if not os.path.lexists(MARKER.parent):
        os.mkdir(MARKER.parent, 0o700)
    root_dir(MARKER.parent)
    require(not os.path.lexists(MARKER))

    # Exclusive temporary authority. No marker persists on normal completion
    # or caught failure; after an interruption, inspect before retrying.
    fd = os.open(
        MARKER,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    info = None
    try:
        os.fchmod(fd, 0o600)
        info = os.fstat(fd)
        require(info.st_uid == 0 and stat.S_ISREG(info.st_mode))
        written = os.write(fd, BODY)
        require(written == len(BODY))
        os.fsync(fd)
        os.close(fd)
        fd = None

        outcome = run(sys.executable, "-B", str(CONTROLLER), "install")
        require("PROJECT_NFT_TABLE_INSTALLED=True" in outcome.splitlines())
        verification = run(sys.executable, "-B", str(CONTROLLER), "verify")
        require("PROJECT_NFT_TABLE_EXACT=True" in verification.splitlines())
        run("systemctl", "is-active", "--quiet", "ufw.service")
        run("systemctl", "is-active", "--quiet", "docker.service")
    finally:
        if fd is not None:
            os.close(fd)
        current = os.lstat(MARKER)
        require(info is not None and
                current.st_ino == info.st_ino and
                current.st_dev == info.st_dev and
                stat.S_ISREG(current.st_mode) and
                current.st_uid == 0)
        os.unlink(MARKER)

    require(not os.path.lexists(MARKER))
    print("source_hashes_reverified=True")
    print("private_baseline_reference_present=True")
    print("project_nft_table_installed_and_exact=True")
    print("temporary_authorization_marker_removed=True")
    print("ufw_and_docker_still_active=True")
    print("codex_launch_authorized=False")
    print("reload_reboot_persistence_verified=False")
    print("STAGE_C_ONE_TABLE_ONLY_COMPLETE")
except Exception:
    print("STOP: Stage C verification or bounded install failed")
    print("DO_NOT_REPEAT_OR_ROLL_BACK_AUTOMATICALLY")
    print("codex_launch_authorized=False")
    sys.exit(1)
PY
```

**Success interpretation:** Only if the final `STAGE_C_ONE_TABLE_ONLY_COMPLETE` is printed, the pinned source, private baseline reference, exact project table verification, temporary marker removal and existing Docker/UFW availability were checked. It does **not** establish network negative-canary results or persistence. The controller's own static precondition checks also require stopped agent/no restart and exact existing original-lab firewall rules. The only intended filesystem effects are a possible newly created root-owned `/etc/ccpc` directory and a **temporary** marker that is removed on completion, plus a kernel-owned CCPC-only nft table and controller lock file. The first attempt may leave a new `/run/lock/ccpc-codex-nft-guard.lock` with mode 0600. It will not install any systemd unit or enable any service.

**Failure and recovery:** If a precondition fails, the command is intended to refuse the nft transaction. If nft transaction or postcheck fails after the table was created, the controller **deliberately retains restrictive DROP rules** instead of weakening protection; the shell removes its temporary authorization marker in the normal exception path. If power is lost or the process is forcibly interrupted, the marker may remain and must be inspected privately before any retry. **Never rerun Stage C blindly, globally flush the ruleset, restart Docker/UFW, or restore the entire private snapshot**. A proposed *scoped rollback only if separately approved* would first recheck stopped agent/restart disabled, original three DROP rules and exact dedicated table contents, then delete **only** `table inet ccpc_codex_lab_guard` if its existence is proven and no Codex process depends on it; absence/ambiguous contents must STOP. The exact rollback wrapper and live negative tests remain separate operational steps and require independent approval.

**Approval boundary:** No such command is authorized by the owner's Step 117/118 approval for `plan`. Before approving table creation, the owner should confirm the second recovery session remains working, the original lab services' connectivity dependencies are understood, and a minimal rollback command is acceptable. The faster path is to install this single table without a service and test controlled synthetic negative canaries *while the Codex agent is stopped*. The safer isolation fallback is a dedicated Codex VM/host, avoiding shared-host firewall continuity. Neither path licenses agent startup yet.


## Step 119 — owner approves exact Stage C one-table installation; execution pending (2026-11-20)

**Approval provenance:** After the operator-reported read-only controller `plan` PASS in Step 118, the assistant provided the [exact Stage C review](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/01dfeace8dda154d32e2260d61f0d3388644ce2d/docs/ccpc-project/CODEX-SCOPED-NFT-INSTALL-RECOVERY-REVIEW.md), explaining that the upcoming operation **would modify the active kernel firewall** by adding an independent CCPC-only nftables table with four lab-bridge-specific DROP rules. The user answered **“Approved”** to the direct question “Do you approve the proposed Stage C single-table firewall installation, using the exact reviewed procedure?” This is **explicit, bounded authorization for that previously reviewed script only**, not blanket approval for further mutation, rollback, daemon/service changes, container/agent startup or PRODUCTION/DEVELOPMENT changes.

**Source and procedure verification immediately after approval:** Reopened the authoritative GitHub-first workflow, draft PR #39, the Stage C proposal on `review/codex-proxy-network-hardening-2026-11-19`, and exact pinned source controller commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`. The proposed script is the one finalized in [review commit `01dfeace8dda154d32e2260d61f0d3388644ce2d`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/01dfeace8dda154d32e2260d61f0d3388644ce2d). No new host-side script variant is authorized; previous `NOT APPROVED` text documents the proposal's earlier state and is superseded **only for exact Stage C execution** by this decision.

**Required operator hold points:** Keep the second working administrator SSH/recovery connection open, original Codex agent/Squid stopped, and the root-private Stage A snapshot available. Execute the reviewed command **once** on `ccpcerpserver` only. The wrapper verifies the root-only staged four-file pinned source, private baseline reference, and read-only `plan` showing table absent; creates an exclusive temporary root authorization marker; invokes only `ccpc_codex_nft_scoped_controller.py install`; checks the exact CCPC independent table and UFW/Docker running state; removes the marker in the normal execution path. It must never invoke `nftables.service`, `nft flush ruleset`, `ufw reload`, `systemctl restart docker`, or start an agent. Source tests were static/mocked; *this wrapper and actual kernel installation have not been tested on the target*.

**Execution status:** **NOT YET REPORTED / NOT VERIFIED**. No GitHub document update is evidence of host installation. An expected exact success end marker is `STAGE_C_ONE_TABLE_ONLY_COMPLETE`; obtain the complete sanitized boolean output from the owner. If a `STOP` message occurs or a session interrupts, **do not rerun** and do **not automatically delete/restore firewall rules**. The temporary authorization marker could remain after a forced interruption; treat any unknown marker/table state as unsafe pending read-only inventory and operator-specific rollback. The approved action can interrupt legitimate host-to-lab traffic; a private snapshot is a recovery reference, not a license to restore UFW/Docker firewall state wholesale. Neither reload/reboot persistence nor packet isolation nor unbypassable startup is established by a successful one-table installation.

**Unapproved after Stage C:** Installing/enabling a systemd unit or persistence hook, reboot/reload of UFW/Docker/nftables, altering unrelated firewall tables, deleting the table as rollback, starting Codex or Squid, PRODUCTION/DEVELOPMENT operations, or network-probing other services. Each requires separate reviewed authorization. Codex activation remains **NO-GO**.



## Step 120 — Stage C single-table installation operator-reported PASS (2026-11-20)

**Operator-supplied output from the **once-only** command explicitly approved at Step 119:**

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

**Assessment — Stage C execution PASS as reported by owner, independent recheck PENDING.** The reviewed script's successful exit required the staged four Python source Git blob hashes to match pinned reviewed commit `66960f73a69b10b59f508cda7bfd4ac9ea5c21af`, private Stage A snapshot files to exist/nonempty, and `plan` confirming exact stopped lab and original iptables safeguards with independent table absent. The script then created an exclusive temporary root-only marker, called the *reviewed controller* `install` mode, and independently ran `verify`, checked UFW and Docker active, removed the temporary marker and confirmed it absent. Therefore the owner's output is evidence that **a new, CCPC-only `inet ccpc_codex_lab_guard` kernel nft table with four bridge-specific DROP rules was installed and exactly matched the staged controller's JSON validator at that instant**. The approved command made no request to reload/enable stock nftables.service, restart Docker/UFW, or start Codex/Squid. This GitHub entry is **not** a direct assistant/SSH inspection and should not be treated as permanent state.

**Expected host filesystem artifacts:** One possible newly created `/etc/ccpc` root-owned directory (0700), a now-removed temporary `codex-lab-nft-guard-authorized` marker, and a project controller lock file under `/run/lock`; the read-only/staged source under `/opt/ccpc` and private Stage A snapshot remain. The new independent kernel table is deliberately **not automatically removed** in a rollback because removing a protective DROP layer without determining traffic dependencies is unsafe. The original iptables guards and root marker must remain checked in the next read-only verification.

**Limits:** The host may have been affected by the new rules (host-to-original-lab traffic can be blocked). Only service **active** state was tested, not successful end-to-end UAT/DEVELOPMENT availability. The four nftables DROP rules were validated as *present and exact*, but **no negative packet-path canary tests, legitimate synthetic DB/Redis continuity tests, independent reload/reboot survival, bridge recreation handling or unbypassable Codex process denial have been performed**. `reload_reboot_persistence_verified=False` and `codex_launch_authorized=False` remain authoritative limitations. This is not a production-ready Codex firewall or a permission to start the agent. Operator's previously confirmed second administrator session and private baseline should stay available.

**Next read-only gate, not new modification approval:** A fresh, bounded operator-owned **read-only** check should confirm exact controller `verify` (without marker or bytecode writes), absent authorization marker, stopped/no-auto-restart agent, independent table/chain/rule count, UFW and Docker active, and stock nftables.service still inactive/disabled. Use fixed output booleans/check labels, do not expose raw host/private rules or snapshot paths. Independently confirm both administrator SSH connections remain working. If the recheck fails, **STOP**; do not remove the table or any other rules, change authorization, run global flush, restart Docker/UFW, or rerun Stage C. Later controlled packet tests, scoped rollback, and any persistence design require separate review and authorization.

**Unapproved:** Enabling/installing a project or stock systemd unit, service reload/reboot, network canaries, changing any existing rule or CCPC table, starting/attaching Codex/Squid, or touching DEVELOPMENT/PRODUCTION workloads. PR #39 remains draft/unmerged. **Codex activation: NO-GO.**


## Step 121 — independent post-install read-only verification PASS, operator-reported (2026-11-20)

**Owner-supplied result of the separately initiated read-only post-install verification after Step 120:**

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

**Assessment — post-install read-only verification PASS based on operator command output.** The precise previously provided `sudo python3 -I` inspector checked: root/hostname, stopped original Codex agent and disabled restart policy, staged controller Git blob integrity, absence of `/etc/ccpc/codex-lab-nft-guard-authorized`, stock nftables.service still inactive/disabled, UFW and Docker active, the staged controller's own **read-only** `verify` result `PROJECT_NFT_TABLE_EXACT=True`, and a separate read-only native `nft -j list table inet ccpc_codex_lab_guard` check for exactly one project inet table, three expected base chains, and four DROP rules at priority -301. The command reported `HOST_CHANGES_PERFORMED=False`. **This is operator-reported host observation, not a ChatGPT-executed SSH inspection or an independent penetration test.** The earlier Step 120 installation and readback has now been followed by a distinct, new read-only observation of the intended kernel table.

**One outstanding recovery prerequisite:** At Step 110 the owner had confirmed two administrator SSH/recovery sessions, but has **not explicitly reconfirmed** that the second one still works after the live nft table installation. Request confirmation before any proposed active network tests. The Stage A private firewall reference remains private and should not be pasted or wholesale restored.

**What remains unverified and unapproved:** Real negative packet-path canaries from controlled synthetic endpoints, legitimate DEVELOPMENT/UAT service connectivity after the DROP rules, IPv4 and IPv6 path coverage, reload/reboot survival, bridge identity following Docker recreation, and denial of privileged manual Codex starts. `reload_reboot_persistence_verified=False` and `CODEX_LAUNCH_AUTHORIZED=False` remain. No new service activation, UFW/Docker restart or reload, nft policy change, scoped rollback, network probes, PRODUCTION/DEVELOPMENT changes, or Codex/Squid launch has been approved. A proper future isolated canary plan must fix both a positive reachable control and a forbidden path while avoiding agent start, sensitive credentials, existing business services and uncontrolled packet traffic; obtain separate exact-script approval. **Codex activation: NO-GO.**



## Step 122 — second administrator SSH reconfirmed after nft install; canary planning held (2026-11-20)

**Operator-reported recovery readiness:** The owner explicitly answered **“Confirmed”** to the question: “Can you confirm that your second independent SSH administrator connection to `ccpcerpserver` is still working after the firewall installation?” This is a renewed attestation **after** Stage C table installation (Step 120) and separate read-only exact-table verification (Step 121), not evidence of a physically separate management network or tested total-host recovery. Both administrator sessions should remain open for the next planned checks. The private Stage A snapshot is kept on host as a **reference**, not a wholesale restore script.

**Current observed security state at prior Step 121:** One `inet ccpc_codex_lab_guard` table with three base chains and four lab-bridge DROP rules (priority -301) matched the reviewed source; the temporary `/etc/ccpc/codex-lab-nft-guard-authorized` marker was absent; stopped Codex agent/no auto-restart, original iptables guards, inactive/disabled stock `nftables.service`, and active UFW/Docker were owner-reported. No new firewall change is associated with this SSH confirmation. These are point-in-time observations, not actual packet-denial or reboot persistence evidence.

**Proposed next low-impact gate:** Collect a minimal **read-only, sanitized topology inventory** from `ccpcerpserver` by inspecting Docker's existing original lab network `ccpc_codex_dev_agent_lab` and known existing stopped agent plus synthetic MariaDB and two Redis services. Do not execute `docker compose up`, `docker exec`, `docker run`, test connections, query DB/Redis, read environment secrets, print raw routes/firewall/network IDs or expose DEVELOPMENT/PRODUCTION services. A non-mutating status-only inspector can confirm current original bridge internal/driver/subnet identity and whether synthetic service containers are still running, so that the **separately authorized later** traffic canaries use only controlled synthetic endpoints. Avoid assuming the review-branch `codex-dev-agent/compose.yaml` matches currently deployed host topology; its proxy and outgoing networks remain a proposal.

**Hold:** Explicit approval is still required before any active packet-path test, new disposable container, network connection, service restart, UFW/Docker reload, nft policy mutation, persistence service, Codex/Squid activation or PRODUCTION/DEVELOPMENT operation. Positive and negative synthetic-only path checks, IPv4/IPv6 and legitimate service continuity, reboot/reload resilience and unbypassable runtime process restrictions are NOT YET TESTED. **Codex launch NO-GO.**


## Step 123 — read-only original-lab Docker topology reported PASS (2026-11-20)

The owner ran the previously provided, limited **read-only topology** command on `ccpcerpserver` after the successful Step 121 independent nft table readback and Step 122 reconfirmation that the second administrator SSH session works. The operator returned the complete expected, sanitized output:

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

**Assessment:** The exact verifier checked host identity, Docker network `ccpc_codex_dev_agent_lab` with internal Linux bridge and expected `172.21.0.0/16` / gateway `172.21.0.1`, existence of the matching Docker bridge interface, known original four project containers, agent stopped and restart disabled, and running synthetic `db`, `redis-cache` and `redis-queue` containers each attached to the original lab. No `docker exec/run`, credential use, network probe or service/firewall change occurred. This is **operator-reported stdout** only; the assistant did not independently access Docker. The latest exact nft table readback (Step 121) and recovery SSH confirmation (Step 122) are prior point-in-time evidence, not guarantees of unchanged state.

**Next planned active canary — NOT YET APPROVED:** Before sending packets, require a separately approved **exact command** designed for the *existing synthetic lab only*, with both an allowed-path control and a forbidden-path attempt. Suggested first IPv4 pair: (a) short `PING` (Redis protocol, not ICMP) from the synthetic `redis-cache` container to the existing synthetic `redis-queue` service over the same lab bridge, reading only `PONG`; (b) one bounded host TCP connect attempt to the **same synthetic redis-queue IP and port 6379**, retrieved from sanitized Docker inspection, expected to be blocked by currently installed host/bridge firewall rules. The allowed peer test proves the target service is listening through an approved same-bridge route; it does not prove which firewall rule denied a host-to-lab attempt. Do not print IPs or network identifiers, authenticate to MariaDB, use other services, use agent, attach any container to another network, or create/start/restart a container. Both SSH sessions and private snapshot should remain available. Any test must validate source/target Docker compose project and exact Docker lab membership, agent stopped, nft independent table exact and no install marker, and stop on a failed control. Do not accept `ConnectionRefused` as proof of filtering. Passing this one pair does **not** verify lab-to-host, other bridges, IPv6, Docker/UFW reload/reboot persistence, or Codex launch safety.

**Still held:** No active network canaries, firewall mutation/removal, daemon reload/restart, reboot, service/proxy/agent start, DEVELOPMENT or PRODUCTION operations have been approved. Codex **NO-GO**.
