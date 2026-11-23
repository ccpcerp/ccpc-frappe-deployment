# November 23 DEVELOPMENT backup — isolated QEMU/KVM recovery rehearsal plan

**Date:** 2026-11-23 (Asia/Manila)  
**Status:** Reviewed design / approval pending for VM disk, image and guest launch; **NO VM or restore executed**.  
**Owner's scoped recovery objective:** Demonstrate a usable recovery of the latest *DEVELOPMENT-only* backup; no PRODUCTION contact, source mutation, or data egress to third-party CI.

## Verified facts

- Physical host: `ccpcerpserver`, Ubuntu 26.04, ~29 GiB installed RAM, 26 GiB available and 683 GiB free at prior readings. QEMU 10.2.1, `qemu-system-x86`, `qemu-utils`, `cloud-image-utils` installed; `qemu-kvm.service` active/exited. `docker.service` active; `frappe_docker_devcontainer-frappe-1` running.
- `/dev/kvm` root:kvm mode 660. Host account `gani` now belongs to the KVM group; a reused VS Code SSH shell did not inherit it. **Actual read/write KVM device access verified PASS when using `sg kvm -c '...'`** in a scoped child shell. Do not change permissions, run VM as root, restart Docker, or reboot solely for this.
- Source NAS folder: `/mnt/erpnext_backups/ccpc-development-phase1-20261123T014828Z-ee8c493c7b6bbfc9`. The owner's guarded one-shot script reported four local files each for `development.localhost` and `ccpc-integration2.localhost`, checksum-verified NAS 4/4 each and 8/8 total PASS. **These source artifacts may contain private data and secrets.**
- Archived application release source was `ccpcerp` commit `b0cbe5c13cb68499a7920de2879f65e72cff000a`. Pin Frappe and ERPNext runtime versions after separate safe inspection; do not blindly restore into an arbitrary newer runtime.

## Target choice and isolation baseline

Use an **independently running, user-owned QEMU/KVM virtual machine**, not the already-running Docker daemon or persistent DEV Frappe bench. Suggested name `ccpc-dev-restore-lab-20261123`; initial planning budget **8 GiB RAM, up to 60 GiB qcow2 guest virtual disk, 4 vCPUs**, no autostart. The guest must have its **own** storage, service manager, Docker/DB/Redis instances and wholly new site/database identities.

- First boot should explicitly specify QEMU **`-nic none`** to disable QEMU's *otherwise implicit* user-mode NIC (see QEMU system documentation). Do not create libvirt/tap/bridge/NAT services, pass a host Docker socket, share real DEV bench/DB volumes, attach Synology as a guest mount, pass host SSH credentials, or publish guest ports.
- Never assume `-nic user` is an isolation guarantee: its outbound networking can reach host/LAN resources. Guest Internet access for package/bench provisioning requires a **separately reviewed, fail-closed, outbound-restricted transfer or staging procedure** before any NIC is enabled. An entirely offline first boot is feasible, but full ERPNext installation cannot be claimed complete without dependency provisioning.
- Use an official signed/checksummed Ubuntu **24.04 LTS amd64** cloud image (guest OS can differ from Ubuntu 26.04 host). Verify exact download URL, checksum and signature/transport before staging. A cloud image may require cloud-init seed for initial access; guest-only secret and account credentials must be kept out of GitHub/Codex/chat. Do not invent passwords, disable login security, or allow auto-email/webhooks.
- Use a private `0700` host lab directory and `0600` user-owned files; guest disk copy-on-write and no existing path overwrite. Prove unique lab name and absence of preexisting disk/process before allocation. QEMU should run from a normal human-reviewed host terminal with **`sg kvm`** so no root/host network privileges are required. All guest action/backup content should be outside Codex's checkout and log surface.

## Gates: require evidence before execution

**G0 – VM approval:** Obtain separate, explicit approval for disk allocation, host-side official image download, private lab directory, and first offline guest boot, with an exact reviewed command/script and stop conditions. Check host capacity again, uniqueness/no preexisting VM, OS image signature/hash, QEMU version/options, host process/user, and `/dev/kvm` group access. Do not re-run the backup script.

**G1 – Offline guest and confinement:** Start *one* bounded local QEMU guest without NIC or host shares; confirm console boot and lab-only guest disk; verify host Docker and DEV Frappe remain up and guest cannot contact host/PROD by lack of network. No secrets or real backups attached yet. Record private VM disk location, virtual disk format, process identity and stop/rollback procedure.

**G2 – Guest dependency provision:** Design a locked-down dependency ingress / offline package path for Frappe/ERPNext/MariaDB/Redis. Any network opening must be scoped, deny routes to CCPC DEV/PROD/NAS and other local subnets, and keep SMTP/webhooks/scheduler off; ensure no default guest network is created accidentally. Verify exact Frappe/ERPNext and CCPC source versions, setup unique guest-only DB user/schema/site.

**G3 – Owner-held backup ingress:** Copy only a private verified copy of the appropriate Nov23 backup set into guest scratch, by a reviewed transfer with local SHA-256 verification, capped disk usage and no host writable shared filesystem. Never paste config/SQL/private attachments into GitHub, Codex, ChatGPT, public URLs or logs. Treat even `ccpc-integration2.localhost` as potentially confidential. Preserve original NAS and local source read-only.

**G4 – Restore and acceptance:** Review *exact* `bench restore` command after proving the target DB/site were created only inside the guest. Be mindful that Frappe restore may drop/recreate a **target** database: never run it against live DEV/PROD or a shared MariaDB. Confirm recovered DB, public/private attachments, required DocTypes and representative read-only records; verify app release parity and record sanitized observed evidence. Positive recovery report must state if only the Integration2 site, not both sites, was restored.

**G5 – Stop/disposal:** Preserve original NAS sets and current DEV work. Stop/teardown guest *only* using exact guest-specific paths and after explicit approval; no glob-based destructive cleanup. Record source hashes and limitations in GitHub handoff.

## Status and authorization boundaries

As of this design, G0 remains **PENDING**: only the *recovery objective* was approved. Package installation and `gani` membership were separately authorized and verified. No approval is assumed for a new disk, image transfer, guest launch, network modification, backup import, database restore, or cleanup. Codex may review scripts and code in its constrained source workspace, but must not be given host-wide Docker/QEMU access or confidential backup contents.

**References:** [CURRENT-HANDOFF-5.md](CURRENT-HANDOFF-5.md), [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), [PR32-INTEGRATION2-ISOLATED-RESTORE-REHEARSAL-PLAN-2026-10-30.md](PR32-INTEGRATION2-ISOLATED-RESTORE-REHEARSAL-PLAN-2026-10-30.md). QEMU network option documentation: https://www.qemu.org/docs/master/system/qemu-manpage.html.

## 2026-11-23 offline temporary boot test — approved script

The owner provided successful **normal-host staging output** for Ubuntu 24.04 cloud image signature and SHA-256 `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94` and 60-GiB qcow2 overlay under `/home/gani/ccpc-restore-labs/ccpc-dev-restore-lab-20261123`. Owner then explicitly replied **"Approved"** to a **first bounded offline boot smoke test**, for exactly the staged disk, 8 GiB/4 vCPU, `-nic none`, `-snapshot`, **no guest backup, host mount, network, credentials, Docker/PRODUCTION, or persistent disk writes**.

**Reviewed implementation:** review branch `review/dev-restore-vm-staging-2026-11-23`, commit `ccb8cfc2f1b9b6b16859e60eeb6dd99e1c144bb1`; path `scripts/development/operator/ccpc_dev_restore_vm_offline_boot_20261123.py`; Git blob SHA-1 `ca6e0f864db8da7c7a39ce1d5ce6616dd221e910`; script SHA-256 `4e21b3ce4454f1793d87a11c1ec0d794566e8e92ed4c8b987f06084b9c7890d5` (algorithm tested against the standard `abc` SHA256 vector). The script is **not yet executed**. It performs exact staged image + lab file inventory + user/permissions/DEV-container checks, then foreground QEMU with `sg kvm` in an outer trusted-host command, `-no-user-config -nodefaults -machine q35,accel=kvm -cpu host -smp 4 -m 8192 -drive ... -nic none -display none -serial stdio -monitor none -snapshot -no-reboot`, enforced by a `timeout` window of **180 seconds** with 10-second kill-after. QEMU monitor is absent, so no operator disk commit command is exposed. **A completed time window is not boot PASS until serial console evidence shows guest boot**.

**Execution gate:** stage script using exact Git branch/commit/blob/SHA256 pin into `~/ccpc-reviewed-scripts` outside Codex, check AST, run once with `sg kvm -c 'python3 -B /home/gani/ccpc-reviewed-scripts/ccpc_dev_restore_vm_offline_boot_20261123.py'`. Stop and preserve any result on error; no automatic retries. The script requires temporary snapshot space under `/tmp`, leaves original overlay untouched in snapshot mode, no autostart. Do **not** interpret Ubuntu no-cloud-init-datasource/login-not-configured warnings as ERPNext failure; login credential setup is out of scope.

**Next:** collect sanitized Ubuntu serial boot transcript / timeout outcome. If good, separately design guest-only cloud-init identity/seed and controlled dependency ingress before any permanent VM boot or backup restore; preserve NAS and persistent DEV.

## 2026-11-23 — revised detached watchdog procedure prepared (NO LAUNCH APPROVED)

**Owner authorization interpretation:** Following an initial first-boot smoke test that became `T` (suspended) and was safely cleaned up, owner replied **"Approved"** to the recommendation to **revise the boot-test procedure**, record private serial console logs and make time-limit management independent of an interactive terminal. As the prior discussion explicitly separated *reviewing the new procedure* from *authorizing another offline test*, this approval is **for code/review/documentation only, NOT for executing a second guest boot**.

**Prepared source (GitHub verified):** branch `review/dev-restore-vm-staging-2026-11-23`, commit `d7ccb6167d64de3b0c2144ae7436c9f7e3bd0ccc`, script `scripts/development/operator/ccpc_dev_restore_vm_offline_watchdog_20261123.py`, Git blob `fc87b307ebe7c310fb11eb00b21b911d7c3adf86`, SHA-256 **`b4324c08039b223bd9733167e5cc72871941fb3707861524c19374bb1c516fb0`**. GitHub-fetched source SHA-256 matched the local Python-syntax-tested candidate **exactly**; SHA-256 implementation cross-checked against standard `abc` vector.

**Design changes:** `sg kvm` launch will run a dedicated Python supervisor `start_new_session=True`, stdin `DEVNULL`, its own private log file, and immediately return the original shell; it does **not** rely on operator terminal job control to enforce timeout. Supervisor spawns another detached-session GNU `timeout --signal=TERM --kill-after=10s 180s qemu-system-x86_64` and independently monitors elapsed time, with a group-targeted SIGKILL safeguard if the child timeout fails. The supervisor drains QEMU serial/stdout into a **2-MiB capped** private `serial-console.log` and writes status `status.json` (always `guest_boot_confirmed: false` until an independent human validates guest console). Because the supervisor and timeout/QEMU lack the controlling SSH terminal and are different sessions, ordinary `Ctrl+Z` or VS Code disconnect will not suspend their process groups. No command can defend against arbitrary `SIGSTOP` from privileged users or uninterruptible host I/O; the script must not be advertised as an absolute guarantee.

**Fail-closed one-shot preflight:** Host `ccpcerpserver`, UID1000 `gani` without sudo, actual `kvm` group and R/W device access; original staged 0700 directory, original 0400 Ubuntu cloud image hash `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`, expected 0600 60GiB qcow2 overlay and exact backing file; no unexpected extra files in original lab; sufficient disk/memory, running DEV Frappe Docker container; no currently active matching QEMU/timeout process; exclusive not-previously-existing one-shot run folder `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123` (0700), owner-only logs 0600. **No write to the original Ubuntu image/overlay:** QEMU `-snapshot` handles temporary writes. No `-nic user` fallback; `-nic none -nodefaults -no-user-config -monitor none -display none -serial stdio`, 8GiB/4vCPU, no host shares or backup ingress. Operator never pastes any raw console content that contains sensitive data; first guest is a clean cloud image.

**Local static + controlled mocks only (NOT actual VM/host tests):**
- `python3 -m py_compile`: PASS.
- Mock supervisor with short non-QEMU success exit: PASS; writes `QEMU_EXITED_ZERO` status and console text.
- Mock supervisor with nonzero exit: PASS; writes `QEMU_EXIT_NONZERO`.
- Mock supervisor emitting 2,200,000 stdout bytes: PASS; log capped at exactly 2,097,152 bytes with truncation flag.
These tests establish log/status control flow only; they do **not** verify runtime QEMU, guest boot, complete host isolation, actual 180s timeout behavior or recovery.

**Gate for execution:** Obtain **new, separate, explicit operator approval** for this revised single-use offline boot. After approval, human fetches exact GitHub commit/blob/SHA-256, AST-checks script, then runs one reviewed `sg kvm -c 'python3 -B ...'` command in normal host shell. Read `status.json`, last safe relevant lines of private console log, and `supervisor.log`, examine guest console and process states. Do not call test PASS solely because watchdog's timer completed. No new packages, cloud-init seed, networking, database writes, restore, cleanup, Docker restart, or PRODUCTION operation without separately scoped approval.

## 2026-11-23 — G1 offline Ubuntu guest boot and shutdown: PASS

**Owner verified real Ubuntu boot:** serial log showed the `Ubuntu 24.04.5 LTS` banner, `Reached target multi-user.target - Multi-User System.` and `ubuntu login:`. This is direct guest boot evidence on QEMU/KVM (not a simulated mock).

**Watchdog real shutdown evidence:** one-shot private result `/home/gani/ccpc-restore-labs/ccpc-dev-restore-offline-test2-20261123/status.json` returned `state: TIMEOUT_WINDOW_ELAPSED`, `timeout_returncode:124`, `console_bytes_observed:78790`, `console_truncated_at_2mib:false`, `guest_network:none`, `snapshot:true`, `backup_restore_executed:false`. Normal read-only `ps` for supervisor PID2699269, timeout PID2699271 and QEMU PID2699272 showed only header (all absent), and supervisor log was empty. **G1 PASS** for offline guest boot **and** watchdog-bounded shutdown. Script automatically left `guest_boot_confirmed:false` as a conservative status field; separate console text confirms real login prompt. The test ran using `-nic none` and `-snapshot` with no guest-mounted host directories and was a **temporary disk-write smoke test**; owner did not report any restore operation. Earlier stopped foreground test (first attempt) was inconclusive, cleaned up, and superseded by this successful revised attempt.

**Next gate G2** is **NOT yet authorized**. Work needed before a meaningful backup restore: independently verify target application version compatibility; plan guest-only persistent identity/credentials and cloud-init seed, preserved without logging secrets; devise tightly bounded offline dependency transfer or audited network access that blocks existing DEVELOPMENT and PRODUCTION/NAS and email/webhooks; check guest-only DB/Redis and a uniquely named test Frappe site. Restore input and schema changes must stay VM-local. Original private Nov23 NAS snapshot remains an 8/8 verified checksum backup but **a recoverability test has NOT yet occurred**. No current consent for extra QEMU boot, guest provisioning, network changes, copying confidential backup contents or restoring DB. G1 log bundle should be preserved as audit evidence.

## 2026-11-23 — Owner-approved streamlined reusable recovery lab (G2 preparation)

Owner explicitly approved continuing after G1 boot + shutdown PASS and added: **"dont make it to strick that it will takes a lot of time every recovery test"**. This replaces an unnecessarily repetitive approval/runbook pattern with a **one-time baseline setup and repeatable fast rehearsal**. Do **not** treat this as blanket permission for live DEVELOPMENT database overwrite, host firewall/Docker changes, real backup import, external network access, cleanup of original assets, or PRODUCTION.

**Practical fast path — one-time only:**
1. Read the running DEVELOPMENT Frappe/ERPNext/CCPC versions and three Git revisions using a **read-only** Docker `exec` (no DB access). Match the recovery guest's application versions to the archive's source, not simply upstream latest; the Nov23 custom app was confirmed as `b0cbe5c13cb68499a7920de2879f65e72cff000a` at the time of source backup.
2. Configure an isolated guest-only admin identity/cloud-init and guest-only database; no host Docker socket, host paths, source DB, NAS mount or production accounts. Use the already staged signed Ubuntu image and 60GiB disk. **Do not rerun G0 image staging or the G1 boot smoke test.**
3. Provision Frappe/ERPNext/CCPC and MariaDB/Redis **once** in that guest. Use one explicitly reviewed dependency-ingress method during **empty guest provisioning**, then turn all guest networking **off before real archived data enter**. Avoid requiring independent time-consuming approvals for each ordinary guest-only package/config step once the bounded provisioning command and networking scope are approved. No mail, scheduled jobs, webhooks, hostfwd or inbound ports.
4. Verify the guest baseline only once, stop, then preserve a clean read-only guest image/checkpoint for fast clone-based restore rehearsals. Never use `-snapshot` for initial persistent provisioning (it discards guest changes); use disposable overlays for each future restore.

**Repeat for each new backup:** take a **disposable copy-on-write guest overlay** from the clean baseline, prove VM-local MariaDB/site target, load only the owner-approved four components (database `sql.gz`, site config, public `tar`, private `tar`) through a reviewed private, checksum-verified transfer, run `bench --site <guest-only-site> restore ... --with-public-files ... --with-private-files ...`, then inspect **database, installed apps, critical DocTypes, representative record counts, public/private files and a small read-only application check**. Produce one concise PASS/FAIL report and retain only necessary sanitized evidence. A restored site must get a guest-only site config/encryption key handling without publishing real credentials. Subsequent tests must never repeat package installs, official image downloads, or G1 smoke tests. Prefer same-day operator review rather than numerous unrelated preflights.

**Safety minimum retained:** target the isolated QEMU guest only; prevent accidental connection to running DEVELOPMENT/PRODUCTION MariaDB and to Synology; restrict real backup access; verify source checksums, DB+files completeness and version compatibility; deny guest outbound access whenever confidential data are present; preserve original backup, clean baseline, and active DEVELOPMENT dirty work; do not use forceful DB changes on live services. These checks are brief and automated where feasible, not separate manual approval stages each time.

**Current G2 authorization:** approved to prepare/review guest-only recovery baseline and inspect non-sensitive app versions with read-only commands. A first real backup **ingress + restore** and any guest Internet/LAN egress should be included in **one clearly scoped operator approval** after the exact method is known; thereafter repeat only the already-approved restore flow in the disposable guest without repeated infrastructure setup. PRODUCTION always requires separate explicit permission and is categorically out of scope for these tests.

**Immediate verified next operator check (read only, in current DEVELOPMENT container only):**

```bash
docker exec frappe_docker_devcontainer-frappe-1 bash -lc '
set -e
cd /workspace/development/frappe-bench
echo "=== APPLICATION VERSIONS ==="
bench version
echo "=== SOURCE COMMITS ==="
for app in frappe erpnext ccpcerp; do
  printf "%s: " "$app"
  git -C "apps/$app" rev-parse HEAD
done
'
```

This does not print database credentials, restore anything, or modify the container. Use the returned revisions to pin a baseline and plan the shortest safe package/bootstrap process. Current Frappe documentation: https://docs.frappe.io/framework/user/en/bench/reference/restore . The official command supports both public and private file archive flags, and warns against downgrades; never force an unverified version mismatch.

## 2026-11-23 — Matched app revisions and one-time guest seed/overlay operator script

Owner ran **read-only actual DEVELOPMENT `bench version` and `git rev-parse HEAD`** inside `frappe_docker_devcontainer-frappe-1` and reported these exact, pinned versions:
- Frappe **16.33.1**, branch `version-16`, **`988e54f3c4c291e2077a83809663f123731abe76`**.
- ERPNext **16.34.2**, branch `version-16`, **`4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`**.
- CCPC custom app **0.0.1**, `HEAD`, **`b0cbe5c13cb68499a7920de2879f65e72cff000a`** (also exact verified GitHub release-branch head). These are the baseline code identities for a Nov23 backup restore **subject to guest runtime dependencies**.

**New reviewed one-time guest staging script:** `ccpcerp/ccpc-frappe-deployment`, branch `review/dev-restore-vm-staging-2026-11-23`, source `scripts/development/operator/ccpc_dev_recovery_baseline_seed_20261123.py`, commit **`e69ceb9c15e680f15b9ad134f78b4c9a624d20c5`**, blob SHA **`fc2b4efdbe1c51c7d840c22d10ce155797006c55`**, source SHA-256 **`57ed6745a32fdf0fe8576bca2e38960df3cefd95acb52c73a6accfa06afb5860`**. GitHub refetch and SHA-256 known-vector self-test verified the retrieved source identity. Host execution and Python AST syntax preflight **NOT YET REPORTED**.

**Exact bounded host-only action:** On `gani@ccpcerpserver`, run the script from an independently fetched/pinned source outside Codex. It confirms UID1000, original signed Ubuntu cloud image, expected 60GiB qcow2 backing/size, no overlapping QEMU, sufficient disk and unchanged DEV Docker status, then creates exactly one new private `/home/gani/ccpc-restore-labs/ccpc-dev-recovery-baseline-20261123/` directory; generates a random guest-only password stored in its own 0600 `guest-console-password.txt`; writes guest-only hashed cloud-init `user-data` and `meta-data`, makes `cloud-init-seed.iso` using existing `cloud-localds`, and a **new persistent guest qcow2 overlay** backing the earlier staged image. The guest account is `ccpc-restore`, login using only the private serial-console password; guest SSH password auth disabled and no SSH key copied. Script leaves original smoke-test and November23 NAS data untouched. **It does not launch QEMU, run/alter guest packages, install Frappe, copy backup files, change host network, Docker or PRODUCTION.** One-shot and fails closed rather than overwriting an existing baseline folder.

**Next:** Obtain operator staging result, then author one practical persistent guest bootstrap path for exact source revisions with MariaDB/Redis/Python/Node runtimes, keeping all commands inside **the guest**. New current Frappe v16 documentation lists Python 3.14, Node 24, MariaDB 11.8, Yarn 1.22+, Redis 6+, and pip 25.3+; these are **current general installation guidance**, not proof that the Nov23 already-built DEV image uses exactly those versions. Before dependency installation, pin the actual runtime or validate compatibility in a disposable guest, and avoid unreviewed host-version substitutions. Cloud-init NoCloud local seed works without networking; dependency setup may need one scoped, temporary package ingress while the guest is still empty, never after a confidential restore. Treat baseline as complete only after actual guest login and Frappe+ERPNext+ccpcerp verified.

**Standing owner direction:** Future rehearsals must not require redoing Ubuntu download, user creation or Frappe installation. Snapshot a clean *provisioned* guest once and clone an overlay per backup. Avoid redundant approvals for routine guest-only steps, but significant guest egress and first confidential backup import remain specifically scoped. No production operations.
