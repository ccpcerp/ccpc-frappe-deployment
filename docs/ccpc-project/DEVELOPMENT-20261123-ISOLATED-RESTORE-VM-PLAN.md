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
