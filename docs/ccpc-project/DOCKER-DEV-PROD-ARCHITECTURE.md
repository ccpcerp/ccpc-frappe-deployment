# CCPC ERPNext — Docker DEVELOPMENT and PRODUCTION architecture

> **Status:** Documented checkpoint, 2026-10-10. This is a synthesis of prior CCPC investigation and tracked configuration—not a fresh live Docker inspection. Where runtime details have not been checked, they are explicitly marked **verify before use**. This document is **not** permission to change PRODUCTION, recreate containers, migrate sites, restore databases, or alter backups.

## 2026-10-22 NEW PRODUCTION HOST REBOOT AND FIREWALL PERSISTENCE PASSED — HEADLESS OPERATION POSSIBLE

**Operator-provided post-reboot evidence on separate new host `ccpcerp-prod`:** After a controlled `sudo reboot`, the owner successfully reconnected from Windows PowerShell and reached `ccpcadmin@ccpcerp-prod:~$`. Read-only `uptime -s` returned **2026-10-22 08:02:48 UTC**, confirming the recent reboot. Post-reboot `sudo ufw status verbose` showed **Status: active**, **Logging: on (low)**, **Default: deny (incoming), allow (outgoing), disabled (routed)**, and the SSH rule **`22/tcp ALLOW IN 192.168.50.0/24`**. Thus the LAN key-only remote access and UFW rule persistence have been operator verified across reboot. Separate earlier tests after SSH service reload verified key-only access succeeded and password-only access failed with `Permission denied (publickey)`.

**Operational decision:** The new Ubuntu server can now be managed headlessly via protected SSH; owner may disconnect the monitor and keyboard while leaving Ethernet and power connected, keeping physical console access available for recovery. SSH private key and passphrase remain solely with the owner, not in GitHub. No Docker, ERPNext installation, business records, service cutover, DNS, or old-server operations were performed. **Next safe read-only step:** retrieve the NIC MAC and default gateway on `ccpcerp-prod` (`ip -brief link show enp5s0` and `ip -4 route show default`) to plan router-side **DHCP reservation for 192.168.50.186**, without immediately changing the host networking. Docker port exposure and backup/restore plans require separate review.

## 2026-10-22 NEW HOST UFW FRESH SSH CONNECTION VERIFIED — REBOOT CHECK NEXT

**Operator-confirmed:** A second Windows PowerShell SSH login to the dedicated new Ubuntu PRODUCTION host `ccpcerp-prod` at `192.168.50.186` succeeded **after UFW was enabled**. The operator reported `Last login: Thu Oct 22 07:45:57 2026 from 192.168.50.194` and the expected `ccpcadmin@ccpcerp-prod:~$` prompt. This followed the explicit key-only Windows SSH test command prescribed in the prior step; password-only SSH had previously been confirmed rejected after `ssh.service` reload. Firewall `ufw status verbose` was already verified active, with incoming deny, outgoing allow, and `22/tcp ALLOW IN 192.168.50.0/24`. **Fresh remote access through the live firewall is now verified, but post-reboot access is NOT YET verified.**

**Next controlled operation:** on the *new server only*, while the physically attached monitor/keyboard remain available for local recovery, issue `sudo reboot` and then reconnect from Windows using the dedicated passphrase-protected ED25519 key, with client password and keyboard-interactive fallback explicitly disabled. Verify server identity/IP, SSH and UFW after boot, then arrange a reserved LAN DHCP lease; only later disconnect the console permanently or plan Docker ports around UFW limitations. This new host has no ERPNext or live business data; the existing `ccpcerpserver` live ERPNext PRODUCTION/DEVELOPMENT environments are not touched. No site migration, DNS changes, old-host decommissioning, or cutover approved.

## 2026-10-22 NEW HOST UFW FIREWALL ACTIVATED — FRESH SSH TEST PENDING

**Operator-verified firewall checkpoint on separate `ccpcerp-prod` host only:** UFW was previously inactive. The operator added `sudo ufw allow from 192.168.50.0/24 to any port 22 proto tcp`, verified the rule using `sudo ufw show added`, and checked default policies in `/etc/default/ufw`: `INPUT=DROP`, `OUTPUT=ACCEPT`, `FORWARD=DROP`. They ran `sudo ufw enable` and confirmed `Firewall is active and enabled on system startup`. Subsequent `sudo ufw status verbose` showed **Status: active**, logging `on (low)`, default `deny (incoming), allow (outgoing), disabled (routed)`, and sole shown allow rule `22/tcp ALLOW IN 192.168.50.0/24`. The original SSH session survived activation. **A fresh key-only SSH connection across enabled UFW is not yet verified.** Do not close the original session, disconnect emergency console access, or reboot until fresh connection and then controlled reboot/SSH validation have passed. UFW permits SSH from this LAN subnet, not from arbitrary networks; Docker-published ports will need a separate exposure review as Docker's rules can bypass UFW.

**Next one safe user step:** from a *second Windows PowerShell window on the LAN*, connect with the dedicated protected ED25519 key and explicitly disabled password fallback to `ccpcadmin@192.168.50.186`; retain the existing session until success. After successful fresh SSH, plan a controlled reboot with local recovery access, then reserve the DHCP IP in the router. No Docker, ERPNext, migration, old host changes or business-data cutover authorized.

## 2026-10-22 NEW HOST SSH KEY-ONLY SECURITY FULLY VERIFIED AFTER RELOAD

**Operator-verified milestone (supersedes the failed negative test recorded below):** On separate new Ubuntu 24.04.5 host `ccpcerp-prod` (`192.168.50.186`), a new drop-in `/etc/ssh/sshd_config.d/10-ccpc-prod-hardening.conf` provides `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin no`. `sshd -t` passed; `sshd -T` showed those four effective values. The first password-only negative test **before applying the service reload** successfully logged in; this failure is retained below as audit evidence. A read-only `systemctl show ssh.service` found `MainPID=9259`, `ActiveState=active`, `SubState=running`, `ActiveEnterTimestamp=2026-10-22 06:54:49 UTC`, preceding the configuration change. The owner ran `sudo systemctl reload ssh.service`; `systemctl is-active ssh.service` returned `active`. A **fresh second Windows SSH session authenticated using the dedicated passphrase-protected ED25519 key while password and keyboard-interactive fallback were disabled**. The subsequent **fresh password-only negative test** with client `PubkeyAuthentication=no`, `PreferredAuthentications=password`, `KbdInteractiveAuthentication=no`, `NumberOfPasswordPrompts=1` failed with `Permission denied (publickey)`. Thus key login and password denial both passed **after reload**. No private keys or passphrases stored in GitHub. Keep at least one working key-based connection/physical console for further network changes.

**Next single safe step:** inspect new-host firewall read-only using `sudo ufw status verbose`; do not blindly enable UFW until the SSH allow rule, subnet access requirements, and actual running services have been reviewed. LAN DHCP address is still `192.168.50.186`, not yet reserved; router reservation and backups remain for later. No Docker, ERPNext deployment, business data copy, old-PRODUCTION change, external port forwarding, DNS change, or cutover authorized/completed.

## 2026-10-22 SSH PASSWORD-ONLY NEGATIVE TEST FAILED — LIVE DAEMON STILL ACCEPTS PASSWORDS

**Actual owner-provided negative-test result:** From Windows PowerShell to the new host `ccpcerp-prod` (`192.168.50.186`), the SSH command **explicitly disabled public-key authentication** (`PubkeyAuthentication=no`), requested `PreferredAuthentications=password` and disabled keyboard-interactive auth. It nevertheless prompted for the Ubuntu account password and **successfully entered the `ccpcadmin` shell**. Therefore **remote password SSH remains ENABLED IN THE RUNNING SERVER** despite on-disk drop-in `10-ccpc-prod-hardening.conf` reporting `PasswordAuthentication no` under `sshd -T` and passing `sshd -t`. Previous fresh key-only login also passed. Do NOT claim SSH password hardening completed. Possible cause is old running `ssh.service` retaining config loaded before the drop-in, or a context-specific runtime override; not yet proved. Ubuntu 24.04 uses `ssh.socket` activation, and service reload/application requires care. **Keep known-working sessions open and physical console accessible**; no blind service restart, disabling socket, firewall lockout or reboot.

**Next one-step read-only diagnosis on the new machine:** run `systemctl show ssh.service -p ActiveState -p SubState -p MainPID -p ActiveEnterTimestamp` to check whether the live daemon is active and when it entered that state. Review evidence before a safe config reload; then retest both key-only acceptance and password-only denial in new sessions. No activity on existing `ccpcerpserver`, no old PRODUCTION or ERPNext changes.

## 2026-10-22 NEW SERVER SSH HARDENING — CONFIGURATION VALIDATED; FRESH KEY-ONLY LOGIN PASSED

The owner on newly installed `ccpcerp-prod` inspected the SSH setting sources, noting `/etc/ssh/sshd_config.d/50-cloud-init.conf` set `PasswordAuthentication yes`. They created new `/etc/ssh/sshd_config.d/10-ccpc-prod-hardening.conf` with `PubkeyAuthentication yes`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin no`. `sudo /usr/sbin/sshd -t` returned success, and `sshd -T` reported exactly these effective settings. A **second fresh Windows PowerShell SSH session** authenticated using the passphrase-protected dedicated ED25519 key with `PasswordAuthentication=no`, `KbdInteractiveAuthentication=no` and `PreferredAuthentications=publickey`, reaching `ccpcadmin@ccpcerp-prod` on `192.168.50.186`. The working original SSH session and physical console are recovery options. **Caution:** successful client key-only login does not independently prove the live daemon rejects password-only logins. The next operator action is to test password-only authentication with public-key authentication explicitly disabled, without entering a password if offered. Do not classify hardening complete until this negative test succeeds. Do not restart SSH or reboot until verified. No Docker, ERPNext, old production or DNS modifications.

## 2026-10-22 NEW SERVER SSH KEY-ONLY LOGIN PASSED — HARDENING PENDING

**Operator-reported proof:** From Windows PowerShell, the owner ran an SSH command with a **distinct passphrase-protected ED25519 key**, `IdentitiesOnly=yes`, `PreferredAuthentications=publickey`, `PasswordAuthentication=no` and `KbdInteractiveAuthentication=no`, and successfully obtained the `ccpcadmin` shell on new host `ccpcerp-prod` at `192.168.50.186`. Thus **public-key login is proven** without SSH password fallback. The host banner reports Ubuntu 24.04.5 LTS, kernel 6.8.0-147-generic, root filesystem roughly 786.37 GB available total and initial updates current. Prior operator check found `ssh.socket` active and `ssh.service` inactive (socket activation). Windows private key/passphrase were never provided or committed. One malformed host-key public file fingerprint check was followed by a successful read-only fingerprint derivation from the existing private host key; do not regenerate host keys without an investigation.

**Next hardening safety gate:** Keep **this working SSH session and local console available** until key-only login still works from a *second connection* after configuration change. Inspect effective `sshd` settings and relevant drop-ins before writing SSH configuration. Only then disable password and keyboard-interactive authentication, validate `sshd -t`, safely apply the configuration with socket activation in mind and test a fresh key-only login. An active SSH socket does **not** prove password authentication has been disabled. No internet port forwarding, no Docker, no ERPNext installation, and no old server changes; distinct later approval required for any real business-data migration/cutover.

## 2026-10-22 NEW SERVER UBUNTU INSTALLED — operator-confirmed first boot and LAN (NO ERPNext)

**Latest owner-reported actual new-server status:** Ubuntu Server **24.04.5 LTS x86-64** installed on the dedicated new machine; successful login under administrator account `ccpcadmin`. Operator reports `hostnamectl` showed hostname `ccpcerp-prod`, Ubuntu 24.04.5 LTS and x86-64. After first reboot, `ip -4 -brief address show scope global` returned `enp5s0 up 192.168.50.186/24 metric 100`. This confirms the reported OS identity and running Ethernet interface; it does **not independently validate** DNS, default route, inbound SSH access, security updates or host firewall. Installer had reached successfully configured apt mirror. The selected proposed install disk was internal GIGABYTE 1 TB NVMe (~931.513 GiB), planned LVM root `/` 800G, `/boot` 2G, `/boot/efi` ~1.049G; **post-install partition layout has not yet been independently checked**.

**Next operator step:** from the **new `ccpcerp-prod` host only**, run `sudo apt update` to check configured APT package indexes/network and report output; this does **not** install upgrades. Then review SSH keys, network reservation, firewall, disk, OS updates and Docker deployment, one safe step at a time. Do not touch existing `ccpcerpserver` production containers, DNS or business site; no data migration authorized. This milestone is operator-report backed, not remotely inspected by ChatGPT; the GitHub connector has no host access.

## 2026-10-22 NEW PRODUCTION hardware OS decision — Windows 11 replacement APPROVED

The owner's new separate PRODUCTION computer currently ships with Windows 11. The owner **explicitly approved replacing Windows 11 completely** because the machine is dedicated to ERPNext PRODUCTION. Proposed new Linux hostname: `ccpcerp-prod` (distinct from existing `ccpcerpserver`); chosen installation baseline: **Ubuntu Server 24.04 LTS (64-bit Intel/AMD if hardware compatible)** with a verified official ISO. This is an **installation plan, not a completed OS installation**. Before destructive installation: verify backup of anything worth keeping, identify exact internal disk(s), ensure external NAS/backup drives are disconnected, validate hardware compatibility and obtain installation media. Do not copy PRODUCTION credentials or data, change current server, or transfer DNS/services until the distinct release/cutover review. An OS replacement authorization for the NEW computer is not authorization to erase the existing server or any backup disk.

## 2026-10-22 dedicated PRODUCTION server preparation checkpoint — staging authorized, no cutover

The owner now requests **preparing a separate new PRODUCTION server**, with the goal of leaving the existing `ccpcerpserver` for more extensive DEVELOPMENT/testing **only after an approved and verified cutover**. This authorization covers planning and non-destructive, new-server setup/inspection; it does **not** authorize copying/restoring live ERPNext data, redirecting DNS/traffic, changing the existing PRODUCTION stack, migrating sites, or retiring old PROD. Live production cutover will require its own explicit approval and proven backup/restore/rollback.

**Fresh operator-supplied read-only inventory from the current Ubuntu server:**
- `docker compose ls --all`: production Compose project `frappe_docker` has nine running and one exited container, and DEVELOPMENT `frappe_docker_devcontainer` has four running containers.
- `docker ps -a`: production's exited container is `frappe_docker-configurator-1`, `Exited (0)` (normal for a completed one-time configurator); the other nine run, production MariaDB shows `healthy`. These data points do not establish a complete ERPNext service health check.
- `docker ps` on DEVELOPMENT: `frappe_docker_devcontainer-frappe-1` is running with published ports `127.0.0.1:8000-8005` and `127.0.0.1:9000-9005`; Redis cache, Redis queue and MariaDB containers are also running. This **verifies currently listed Docker published ports are loopback-only** and supersedes the earlier unverified runtime port-exposure remediation status; it is not a complete network-security audit.

**First step on NEW server, not existing ccpcerpserver:** establish whether the new physical machine is actually provisioned and can be accessed with Ubuntu; inspect hostname, OS, CPU/RAM, storage and LAN addressing **without printing credentials, detailed environment variables or tokens**. Plan dedicated Docker stack, files, DNS and verified Synology/off-host backup without copying production data until a distinct approved migration window. Existing DEVELOPMENT and PRODUCTION remain untouched. ChatGPT GitHub connector has no SSH or physical-host control.

## Owner-stated future server plan — 2026-10-20 (PLANNED, NOT IMPLEMENTED)

The owner plans to commission a **separate physical PRODUCTION server once CCPC ERPNext reaches production readiness**. After a separately authorized, backed-up, validated production cutover, the **existing Ubuntu server is intended to become a DEVELOPMENT and testing server**. This is the owner's stated direction, not evidence that hardware has been purchased, networks/backup/restore are designed, or any migration has occurred. There is **no authorized implementation date or cutover command**.

**Present-day boundary remains unchanged:** the existing host still contains both DEVELOPMENT and PRODUCTION Docker Compose projects. All activities on this host must preserve PRODUCTION containers, MariaDB, site data, credentials, network and backups until a completed, independently verified and explicitly approved production migration. The plan does **not** retroactively make the host disposable.

For a future migration, separately review infrastructure sizing, network/DNS and LAN access, dedicated site/database/volumes, four-part backup and isolated restore, roles/permissions, downtime and rollback, and post-cutover separation before authorizing any move. Do not clone actual production business data into ordinary DEV test fixtures. A GitHub/ChatGPT review connection does not itself grant direct SSH/container access; operator-run tasks and site mutations require their own approval.

## 1. Executive overview

CCPC runs DEVELOPMENT and PRODUCTION as **separate Docker Compose projects on the same Ubuntu host**. Their distinct Compose namespaces and application sites are important operational boundaries, but they **share the host kernel and Docker daemon**; this is **not** equivalent to physical or VM-level isolation.

| Aspect | DEVELOPMENT | PRODUCTION |
| --- | --- | --- |
| Historical Compose project name | `frappe_docker_devcontainer` (inferred from confirmed container prefix) | `frappe_docker` (previously recorded) |
| Known container | `frappe_docker_devcontainer-frappe-1` | Individual production container names: **verify from Docker** |
| Application/site | `development.localhost` — **not disposable** | `ccpcerp.local` — live business site |
| Primary purpose | CCPC app development, Codex investigation, approved DEV tests | Operational ERPNext service for LAN users |
| Access | DEV tools, site, and historically published development port ranges; current runtime port bindings need verification | `http://ccpcerp.com` on LAN → host TCP 80 → frontend container TCP 8080 |
| Source/configuration | Host repository bind-mounted into `/workspace`; local active `.devcontainer/` config is Git-ignored | Tracked `compose.yaml` plus CCPC MariaDB, Redis, and LAN production overrides |
| State | Separate development bench and dev MariaDB volume in tracked devcontainer *template*; live volume names **verify** | Frappe sites, MariaDB and Redis queue volumes declared in tracked production Compose/overrides; actual Docker volume names **verify** |
| Authorization | DEV work only within explicit task scope | Separate explicit approval for *any* production-impacting action |

**Do not assume that a DEV command is harmless merely because the Compose project is named DEVELOPMENT.** A Docker-privileged host user can affect both projects. The DEV Codex container has a host workspace bind mount; its nested sandbox has previously failed. Keep production credentials and Docker daemon access away from unattended Codex workflows.

## 2. Host and source layout

- Ubuntu host: `ccpcerpserver`; administrator account: `gani`. Prior SSH LAN address is historical and should be reconfirmed before use.
- Deployment working tree seen during investigation: `/home/gani/deployments/frappe_docker`.
- DEVELOPMENT container: `frappe_docker_devcontainer-frappe-1`; `frappe` user maps to host UID 1000.
- The DEVELOPMENT repository is mounted **read/write** as `/workspace` inside that container. The CCPC application path is `/workspace/development/frappe-bench/apps/ccpcerp`.
- DEVELOPMENT site `development.localhost` has real persistent development state. Never wipe or reinitialize it as though it were a disposable test bench.
- The live `.devcontainer/docker-compose.yml` is **Git-ignored**. The tracked reference `devcontainer-example/docker-compose.yml` may not exactly reflect an already-running container's settings.
- Git source: private deployment repository `ccpcerp/ccpc-frappe-deployment` and custom app repository `ccpcerp/ccpcerp`. Tracked deployment configuration and existing commits are **not** an instruction to rebuild or deploy a running stack.

## 3. Architecture at a glance

```text
                        Same Ubuntu host + Docker daemon
             ┌──────────────────────────────────────────────┐
             │                                              │
  DEV        │  Compose project: frappe_docker_devcontainer │
  workflow   │   frappe container /workspace (host RW bind) │
             │    └─ development.localhost                  │
             │   template: dev MariaDB + dev Redis services│
             │   dev-only volumes/networks (verify runtime) │
             │                                              │
             │  ===== logical Compose separation =====      │
             │                                              │
  LAN users  │  Compose project: frappe_docker              │
      ↓      │   host TCP 80 → frontend:8080                 │
  ccpcerp.com│     ├─ backend:8000 → ccpcerp.local           │
             │     └─ websocket:9000                        │
             │   db/MariaDB, Redis cache/queue, workers,    │
             │   scheduler and production persistent state  │
             │                                              │
             └──────────────────────────────────────────────┘
                            │
              Host backup job → verified Synology NAS mount
              (backup and restore are separate operations)
```

This diagram is a **logical representation**, not a complete enumeration of live container names or network IDs.

## 4. DEVELOPMENT Compose project

Tracked **template**: [`devcontainer-example/docker-compose.yml`](../../devcontainer-example/docker-compose.yml).

Template services include:
- `frappe` running a bench image with `..:/workspace` and working directory `/workspace/development`;
- `mariadb` with a named `mariadb-data` volume at `/var/lib/mysql`;
- `redis-cache` and `redis-queue`.

**Template configuration is not proof of live runtime values.** The active `.devcontainer/docker-compose.yml` is ignored by Git and its running container may predate tracked changes.

### DEV port exposure investigation — PR #9

Previously observed running DEV container had Docker host mappings for `8000-8005` and `9000-9005` bound to all interfaces. At the time, independent LAN tests did not connect to the checked ports and no application listener was present; nonetheless the host bindings were a **latent exposure**.

PR #9 changed the **tracked template** to:

```yaml
ports:
  - 127.0.0.1:8000-8005:8000-8005
  - 127.0.0.1:9000-9005:9000-9005
```

The ignored local active Compose file was also updated, **but the running DEV container was not restarted/recreated at the time of verification**. Docker only applies changed published-port settings when containers are created/recreated. Therefore **do not claim the runtime ports have been remediated** without fresh `docker port` / `docker ps` checks. A recreation must be scheduled and explicitly approved, with DEV data and mounts protected.

### DEV Codex and publisher boundary

The DEV Codex workflow can write a development-report outbox at:

- Container: `/workspace/development/.ccpc-codex-report-outbox`
- Host: `/home/gani/deployments/frappe_docker/development/.ccpc-codex-report-outbox`

The separate `ccpc-reporter` system account was tested with the outbox bind-mounted **read-only**, while the wider host workspace and Docker socket were inaccessible. The first manual GitHub report was posted successfully; the general automatic publisher is **disabled** and its temporary token was revoked and removed. This reporting helper is **not part of production ERPNext containers**.

The DEV container previously exposed SSH material through its bind mounts. Do not put new GitHub API credentials, ERPNext production secrets, or NAS credentials inside the Codex workspace.

### P20A-3J SSH exposure audit — 2026-10-10

A read-only host/Docker audit verified that the running DEVELOPMENT container has a **direct bind mount at** `/home/frappe/.ssh`. As the `frappe` user (UID 1000), the SSH directory was accessible and **six regular files were readable**; no file content, key material, or file names were collected. The Docker socket was not visible in the preceding P20A-3I preflight. These facts were observed in the **running** DEV container, not merely inferred from a Compose template.

**Safety decision:** do not execute unattended or experimental Codex tasks in that existing container, even with `--sandbox read-only`, until effective isolation from SSH and other credentials is verified. The Codex nested sandbox previously failed inside this Docker environment, so a flag alone is insufficient assurance. Prefer planning a separate ephemeral execution container with no SSH or production mounts and no Docker socket. Do not remove or alter the operator's existing keys or restart containers solely for this investigation.

P20A-3B through P20A-3H passed offline schema, bridge, collector, and host validation tests; P20A-3I verified CLI option availability; **no real Codex task or automatic GitHub publication was performed**. The automatic publisher and AI reviewer remain disabled. Next: a non-mutating image/CLI availability preflight for an isolated runner before any Codex API call.
### VS Code Codex manual investigation — location to verify

The operator reports the Codex extension is open in VS Code. **Its extension-host location is not yet verified** (Windows local, remote SSH host, or DEV container). Merely opening VS Code does not prove isolation. In VS Code use **Ctrl+Shift+P -> Developer: Show Running Extensions**, find the Codex extension and record whether it runs **Local** or **Remote**; also check the bottom-left remote-window indicator. Share only this information, never credentials.

**Manual-only workflow:** The user declined any additional paid OpenAI API billing. Do not provision API keys or credits. Existing ChatGPT/Codex subscription access is subject to plan limits and does not guarantee unattended automation. Prefer a local Windows checkout free of secrets for initial code-only analysis. If Codex actually runs in the existing DEV container, stop before task execution: /home/frappe/.ssh is bind-mounted and readable, and nested sandbox failures were observed. Remote SSH sessions need separate exposure review. Review Withdrawal Slip -> Material Issue -> Intercompany Billing Batch code read-only for isolation, duplicate invoices, idempotency and tests; do not execute migrations, live ERPNext transactions, Git operations or arbitrary shell actions without review. CLI preflights do not prove the VS Code extension was tested.


## 5. PRODUCTION Compose project

Tracked sources:

- [`compose.yaml`](../../compose.yaml) — Frappe frontend, backend, WebSocket, configurator, workers, scheduler and shared `sites` volume.
- [`overrides/compose.mariadb.yaml`](../../overrides/compose.mariadb.yaml) — `db` service with `db-data` volume.
- [`overrides/compose.redis.yaml`](../../overrides/compose.redis.yaml) — Redis cache/queue and `redis-queue-data` volume.
- [`overrides/compose.lan-production.yaml`](../../overrides/compose.lan-production.yaml) — front-end host port and site routing.
- [`scripts/config.sh`](../../scripts/config.sh) — definitive deployment-framework Compose-file list and site settings.

The **tracked files** declare named volumes `sites`, `db-data` and `redis-queue-data` (Compose typically prefixes these with the project name); the exact live volume resource names, mount locations, and current state **must be checked on the host** before backup/restore or maintenance.

### LAN traffic and networking

```text
LAN browser
  → LAN DNS ccpcerp.com
  → Ubuntu host TCP 80
  → production frontend container TCP 8080
  → Frappe backend:8000 / websocket:9000
  → production Frappe site ccpcerp.local
```

Prior read-only verification confirmed:
- the production frontend alone had an application port published to the host;
- backend, WebSocket, MariaDB, Redis, queues and scheduler did **not** publish host application ports;
- internal connectivity from frontend to backend and websocket worked;
- LAN users could load the Frappe login at `http://ccpcerp.com`;
- tested router NAT/DMZ/port forwarding, public DNS and external network paths did not expose the app to the public Internet **at that time**.

The design is **LAN HTTP**, not HTTPS. These findings are historical checks, not a continuing guarantee against network changes. Firewall and router segmentation, cookies/HSTS and internal HTTPS are separate hardening topics.

**Important:** Using `docker compose` with only `compose.yaml` omits the CCPC LAN override. The deployed production operations framework uses the `ccpc_compose` helper and configured override set. Do not substitute plain Compose commands for production lifecycle actions.

## 6. Data boundaries, persistent volumes, and backups

| Data class | Known location / source | Critical rule |
| --- | --- | --- |
| DEV app source and bench | DEV `/workspace/development`, host repository bind mount | RW host bind; do not delete, reset or treat site as disposable |
| DEV MariaDB data | `mariadb-data` in tracked dev template | Live volume name and backup method unverified |
| Production Frappe site data | `sites` volume declared in production base Compose | Contains persistent site material; do not remove with Compose `-v` |
| Production MariaDB data | `db-data` declared by production override | Protect from volume deletion and destructive tests |
| Production queue state | `redis-queue-data` declared by production override | Runtime persistence and recovery method should be checked |
| Production Frappe backups | `/usr/local/bin/erpnext_backup.sh` on host | Includes DB, site config, public files, private files |
| Off-host backup destination | Synology mount `/mnt/erpnext_backups` | Verify **mounted filesystem and expected NAS source**, not just directory existence |
| Recovery copy from NAS mount issue | `/home/gani/erpnext-backup-recovery-2026-09-02` | Protected historical backup state; deletion needs specific approval |
| Protected local Compose backup | `compose.yaml.backup` (untracked) | Do not git-add, reset, clean, or remove |

Production backup workflow and the restored NAS mount were manually verified on **2026-09-02**; see [recovery.md](recovery.md) for the four mandatory artifacts, retention, schedule, mount checks, historical gaps and restore prerequisites. A successful backup is **not** proof of a successful restore: a disposable, isolated restore rehearsal is still a separate planned task.

Avoid copying production databases, private files, `.env`, passwords or dumps into DEV for testing. Compose project separation does not enforce this policy automatically.

## 7. Safe host inventory — read-only only

These commands are for a separately scheduled **inspection** by an authorized host operator. Do **not** run mutating `up`, `down`, `restart`, `stop`, `rm`, `prune`, `build`, `exec bench migrate`, `bench restore`, or `docker compose ... -v` based on this document.

```bash
# Verify project membership and actual running containers.
docker compose ls --all
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Verify current DEVELOPMENT host port publication (important after PR #9).
docker port frappe_docker_devcontainer-frappe-1

# Read-only inventory; these show resource names, not contents.
docker network ls
docker volume ls

# Check the NAS mount is real before treating its contents as a backup.
findmnt --target /mnt/erpnext_backups
```

Do **not** paste full `docker inspect` output, environment variables, `.env` files, credentials, Compose-expanded secrets or ERPNext configuration into GitHub or AI chats. For deeper diagnostics, agree a sanitized scope first.

### Live inventory still needed

- Confirm **actual** DEV and PROD project labels and service/container names with `docker compose ls --all` and `docker ps`.
- Record active networks, volume names and mounts, without exposing environment secrets.
- Recheck running DEV published-port addresses after PR #9 and decide whether a controlled DEV-only recreation is needed.
- Establish which persistent volumes are backed up by which mechanisms; check last completed automatic NAS backup and later isolated restore test.
- Recheck LAN/VLAN/firewall/HTTPS assumptions before a production network change.
- Validate whether any local `.devcontainer` SSH mounts still expose material to Codex.

## 8. Change / restart / recovery decision rules

**DEFAULT: observe, don't change.**

1. Identify the exact target environment and Compose project. Never run an operation with an implicit or unverified project name.
2. Capture a current sanitized inventory (containers, ports, volumes, mounts, disk capacity and relevant health checks).
3. Separate **source changes in Git** from **applying changes to a running container**. Merging a PR does not authorize a Docker restart or deployment.
4. For DEV container recreation, first inspect the live Git-ignored Compose file, RW bind mounts, persistent DEVELOPMENT site/DB, data safety and planned downtime. Only proceed after explicit approval of the actual command.
5. For PROD deployment or rollback, use the approved CCPC framework and override set; verify a recent **complete** backup and a tested recovery plan, agree downtime and user impact, and obtain a separate production-specific approval. Never do uncontrolled `docker compose down -v` or Docker prune.
6. For incident recovery, preserve evidence, check NAS mount source, confirm known-good artifacts, and follow [recovery.md](recovery.md). Do not test restores against the live site.
7. Document verified outcomes and unresolved findings; no implied approval is carried over from investigations or earlier test runs.

## 9. References and traceability

- [CCPC project context](ccpc-project-context.md) — observed LAN and Docker investigations, PRs #7 and #9, historical status.
- [CCPC operations manual](operations.md) — reporting isolation and operational boundaries.
- [CCPC recovery guide](recovery.md) — NAS backups, retention, checks and recovery.
- [CCPC project handoff](P20-HANDOFF-2026-10-10.md) — verified P19G/P20A milestone and next implementation work.
- [LAN production access guide](../04-operations/lan-production-access.md) — Compose override and routing details.
- [DEV port-hardening PR #9](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/9).
- [Production LAN PR #7](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/7).

**Last documentation consolidation:** 2026-10-10. Refresh claims against live Docker state before using this page as an operational baseline.


**VS Code terminal confirmation (2026-10-12):** Operator ran `hostname` and tested `/.dockerenv` after `docker exec -it frappe_docker_devcontainer-frappe-1 bash`: hostname `48a951912597`, Docker marker present, prompt `/workspace/development`. Separately the Codex 0.161.0 terminal UI displayed `/workspace/development/frappe-bench`. This confirms the checked shell runs inside the DEV container and strongly suggests the CLI session launched there; it does **not** independently locate the VS Code extension host. Do **not** run Codex analysis from the existing credential-mounted DEV container. For manual code investigation, use a vetted credential-free local Windows checkout or another isolated environment, and note that remote Git may not include uncommitted DEV work. No extra API billing authorized. Do not restart PROD or remove SSH mounts without an explicit maintenance plan.
