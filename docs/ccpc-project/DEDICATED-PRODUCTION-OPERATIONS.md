# CCPC ERPNext — Dedicated PRODUCTION Operations and Deployment Record

## EXISTING OLD-HOST SSH PUBLIC KEY INVENTORY — 2026-11-06

**Owner ran read-only filenames-only key inventory** under `gani@ccpcerpserver` using `find "$HOME/.ssh" -maxdepth 1 -type f -name '*.pub' -printf '%f\\n' 2>/dev/null`. Output was exactly:

```text
id_ed25519_ccpc_backup.pub
```

This is **not** evidence that the backup key should be reused for the dedicated-production transfer, that the corresponding private key exists, or that the NEW `ccpcadmin` account authorizes it. The custom filename suggests backup-specific purpose, and SSH may not auto-offer it absent matching configuration. Do **not** read/publish the private key, automatically copy the public key into `authorized_keys`, replace the backup key or change existing backup authentication.

**Next ONE read-only command on OLD host `gani@ccpcerpserver`** to display only effective authentication key filename choices (no private key content or SSH login attempts):

```bash
ssh -G -o BatchMode=yes ccpcadmin@192.168.50.186 | awk '$1=="identityfile" || $1=="identitiesonly" {print}'
```

Interpret carefully: `ssh -G` shows configuration, **not** proof that files exist, keys are offered or a login will succeed. If only default keys show, the backup-named key was not selected by default. Choose a minimally scoped, dedicated transfer authentication path after reviewing results; adding a key to the NEW host changes SSH access policy and needs separate explicit approval. The user has already approved transfer of the **image archive only**, not unrestricted SSH account access changes or loading/running Docker on the NEW host. The source archive remains protected at `/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar`, with source SHA-256 `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`. No transfer has occurred.

## SAFE RECHECK AFTER TERMINAL EXIT — SSH AUTH REJECTED, 2026-11-06

**Owner successfully reconnected to OLD `gani@ccpcerpserver`** and ran `hostnamectl --static` → `ccpcerpserver`. A subsequent SSH login test was correctly run inside a child `bash <<'EOF'` shell, preserving their interactive terminal, with host fingerprint checked against independently verified NEW-host key `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`, `StrictHostKeyChecking=yes`, `BatchMode=yes`, ED25519-only server algorithm and `PreferredAuthentications=publickey`.

**Actual owner output:**

```text
ccpcadmin@192.168.50.186: Permission denied (publickey).
SSH_AUTH_NOT_AVAILABLE
```

**Result:** Network and previously matched host fingerprint were sufficient to reach the expected SSH service; **authentication from OLD user `gani` to NEW user `ccpcadmin` is not currently authorized/working.** No tar file sent; original archive remains on OLD and no destination archive known. The test had no Docker, app, database or container operation. This is **not** a reason to lower host-key checking, use SSH passwords, or change services.

**NEXT single read-only OLD-host step:** inventory **filenames only** for existing SSH public key files (no private keys or key contents):

```bash
find "$HOME/.ssh" -maxdepth 1 -type f -name '*.pub' -printf '%f\n' 2>/dev/null
```

If no keys are present, report no output and stop; an **explicitly authorized dedicated transfer key** can be planned with minimal permissions. If keys are present, assess whether an existing key is suitable for this one-way transfer rather than exposing private credentials or automatically adding long-lived trust. Provisioning destination `authorized_keys` changes access control and needs a clear, scoped approval; it is not implied by a failed login. Preserve the SSH fingerprint, no `StrictHostKeyChecking=no` and no public/writable archive copies. The previously approved image-only transfer is pending, not failed or completed.

## TERMINAL SESSION EXITED DURING SSH AUTHENTICATION PREFLIGHT — 2026-11-06

**Owner reported:** "The Terminal exited after runnibg the last code", immediately after running the assistant-supplied OLD-host SSH-auth test. No stdout/stderr of that test was shared, so **we do not know if the attempted SSH authentication succeeded, failed, or timed out**.

**Operator safety correction:** The previous instruction placed `set -euo pipefail` and an explicit `exit 1` directly into an **interactive** shell, where a failed `ssh-keyscan`, mismatched fingerprint, or unsuccessful `ssh` can terminate that interactive shell and close the SSH terminal. This was an unsafe presentation error in the guidance, **not evidence of ERPNext/Docker service shutdown**. The script did not include image transfer or Docker modification. It may have created a temporary host-key file which, if the trap ran, was removed on exit; do not assume the exact side effects without output.

**IMMEDIATE NEXT STEP (one read-only command, OLD host):** Reconnect normally to `gani@ccpcerpserver` and run **only** `hostnamectl --static`. Expected output `ccpcerpserver`. Do not repeat the earlier interactive `set -e` block. Continue only after OLD-host identity is reconfirmed.

**For any later repeat of this authentication test:** Enclose all error-handling steps in a **separate child** `bash <<'EOF' ... EOF` process so errors exit only the child shell, never the operator's interactive terminal. Print an explicit verdict and preserve the trusted destination ED25519 fingerprint `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`; stop on mismatch. Do not auto-accept unknown host keys, lower strict checking, run unapproved transfers, reveal secrets, or configure cross-host keys without reviewed need.

**Transfer state:** Previously approved secure **image-only** SSH transfer is still **not confirmed executed**. Original root-private OLD-host archive remains the planned source and has full verified creation output; nothing has been shown to prove destination bytes exist. No approval for image import/restore/cutover.

## OLD-TO-NEW SSH NETWORK FINGERPRINT MATCH — 2026-11-06

**Owner-run read-only on OLD `gani@ccpcerpserver`:**

```text
set -o pipefail
ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null | ssh-keygen -lf -
256 SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c 192.168.50.186 (ED25519)
```

**PASS**: Network-presented destination ED25519 SSH fingerprint exactly matches the fingerprint independently obtained directly from NEW `ccpcerp-prod`: `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. The scan does not by itself prove OLD `gani` has authorized login access on NEW `ccpcadmin`; **no authenticated login, source export transfer or destination file creation has yet been confirmed**. SSH transfer was separately approved by owner, but other operations remain excluded.

**HISTORICAL TEST INVALIDATED FOR INTERACTIVE USE (2026-11-06):** The earlier `set -euo pipefail` / `exit 1` snippet that was run directly in the user's interactive shell caused an unexpected terminal exit or coincided with it. **Do not reuse that syntax at the interactive prompt.** The operator must first reconnect to OLD `ccpcerpserver` and confirm `hostnamectl --static`, as stated in the incident section above. Any retry must run inside a bounded child `bash` process with explicit output and verified host key. No SSH success yet reported.

## DESTINATION SSH PUBLIC HOST KEY DIRECTLY VERIFIED — 2026-11-06

**Owner-run read-only directly on NEW `ccpcadmin@ccpcerp-prod`:**

```text
hostnamectl --static
ccpcerp-prod
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
256 SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c root@ccpcerp-prod (ED25519)
```

**PASS (direct-host identity observation):** New host name matches expected `ccpcerp-prod` and a server ED25519 **public** host-key fingerprint was measured locally. This fingerprints the specific currently configured host key, not the network presentation yet. Host-key trust is **not** installed and OLD-to-NEW authentication is **not** established. No transfer made.

**NEXT one OLD-host read-only command** to obtain the key presented by NEW host's SSH listener over the LAN and compare it to the independently measured local fingerprint, without automatically accepting it:

```bash
set -o pipefail
ssh-keyscan -T 5 -t ed25519 192.168.50.186 2>/dev/null | ssh-keygen -lf -
```

Expected fingerprint for `192.168.50.186`: `SHA256:0Cn2sMC+vLfyALVnN0wj+I7YQVz5QKY0OKk7Q42rl/c`. **STOP on mismatch or scan failure.** `ssh-keyscan` alone is not an authenticated trust source; its use here is only comparison against the independently verified out-of-band public key. Do not use `StrictHostKeyChecking=no`, unauthenticated `ssh-keyscan >> ~/.ssh/known_hosts`, loose source permissions or plaintext transfers. After matching, determine an approved secure SSH authentication and root-restricted destination staging procedure, without transferring yet. Prior approval covers image-only SSH transfer; no image import, restore, Compose or cutover.

## OWNER APPROVED SECURE IMAGE-ONLY TRANSFER — 2026-11-06

**Owner explicitly replied "aPPROVED"** to the separately scoped request for a secure, authenticated SSH transfer of **only** the exported existing live PRODUCTION image archive from OLD `ccpcerpserver` to NEW `ccpcerp-prod`, into restricted destination staging, with a destination SHA-256 verification. This is approval for that bounded transfer, **not** for any `docker load`, container startup, Compose deployment, production/site restore, database/config changes, DNS switch, user traffic cutover, deletion or DEV operation.

**Pinned source artifact (already locally exported, not yet transferred):**

- OLD host root-private: `/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar`
- Bytes: `907840000`
- Archive SHA-256: `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009`
- Embedded current live image ID: `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`

**Preflight before any bytes leave OLD host:** Verify SSH host identity and fingerprint of NEW dedicated host; confirm a trusted working SSH authentication path between source and destination. Do not disable StrictHostKeyChecking, automatically trust an unauthenticated `ssh-keyscan` result or expose the archive with world/group-readable permissions. Old admin `gani` and new admin `ccpcadmin` are distinct accounts; do not assume keys or cross-host sudo grants are already configured. Prefer minimal private staging on both sides, no sensitive content to terminal/GitHub, and fail safely on existing targets or interrupted streams. Record source/destination host identities and check the exact destination hash before accepting success. Avoid accidental overwrites and never remove the source archive without a separate retention decision.

**Next single read-only operator step on NEW `ccpcerp-prod`:**

```bash
hostnamectl --static
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Expected hostname `ccpcerp-prod`. The second command displays the new host's **public** ED25519 server-key fingerprint (not a private key). Record it to authenticate the host key seen from OLD before SSH trust or copying. If the public key is missing or unexpected, stop and inspect safely. No transfer, file change or services have yet been run under this fresh approval.

## ACTUAL OLD-HOST LIVE IMAGE EXPORT COMPLETED — 2026-11-06

**Owner-run output from the previously authorized `docker save` on OLD live `gani@ccpcerpserver`:**

```text
Exporting verified production image to protected location: /var/tmp/ccpc-prod-image-export.7blpZWnf
SOURCE_IMAGE_ID=sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8
ARCHIVE_PATH=/var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar
ARCHIVE_BYTES=907840000
8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009  /var/tmp/ccpc-prod-image-export.7blpZWnf/ccpcerp-v16.50.0.tar
```

**PASS — source export checkpoint:** The guarded script completed and printed the expected source image identity, a nonempty final archive (~866 MiB) and full SHA-256 digest. The script used root's `umask 077`, a unique `mktemp -d` private directory, `.partial` staging and a final archive `chmod 600`. This is evidence of the command's reported successful completion; **do not infer destination integrity or independent on-disk permissions verification** yet. No transfer, import, Compose startup, database/site restoration, scheduler/email activation or cutover has occurred in this work.

**Next separate approval gate — encrypted transfer of this archive ONLY:** Propose copying the exact protected tar through authenticated SSH to a new root/private staging location on dedicated `ccpcerp-prod` (LAN address previously recorded `192.168.50.186`), with strict host-key verification and no weak/disabled checking. Avoid exposing the protected source via world-readable temporary files, `chmod 777`, public shares, GitHub, or chat uploads. Stage only under root-owned `0700` directory with `0600` output and perform SHA-256 comparison against `8a8ecc8a98c653105a75c6c77d6457d4ac00ebed7430f0bbd18b4619a2fcb009` before accepting success. Check actual old->new or new->old SSH reachability, key availability and known-host fingerprint without weakening SSH security; do not guess successful connectivity. An authenticated encrypted stream via SSH from OLD root-readable image archive is permissible *only if separately authorized*, and no `docker load` or Docker daemon write should accompany this transfer. Avoid overwriting any pre-existing destination file, stop on checksum mismatch and retain source archive unchanged.

**Current approval state:** User's prior "aPPROVED" authorized the **old-host local export only**. **It did not approve copying the archive to another machine**. The user should be asked separately for consent to a secure, image-only transfer. Independently, the Nov 5 backup is for non-live rehearsal; financial transactions after that backup remain protected on old live PRODUCTION.

## OWNER APPROVED ONE OLD-HOST LOCAL IMAGE EXPORT — 2026-11-06

**Explicit owner approval received** after all six PRODUCTION containers matched the image ID, via message: **"aPPROVED"**, in direct response to scoped request for **one protected local `docker save` archive of existing `ccpcerp:v16.50.0` on OLD `ccpcerpserver` only**. Approval covers local staging writes, image export and source archive checksum/size; **not** secure transfer, image import, new-host stack startup, database/site restore, PRODUCTION or DEVELOPMENT runtime changes, or cutover. Owner must execute commands through SSH (ChatGPT has no host-SSH access). **Approval recorded; execution/output not yet verified.**

**Single guarded OLD-host operator step, after owner approval:**

```bash
sudo bash <<'EOF'
set -euo pipefail
umask 077

expected='sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
actual="$(docker image inspect --format '{{.Id}}' ccpcerp:v16.50.0)"
if [ "$actual" != "$expected" ]; then
  echo "STOP: production image ID changed; no export performed" >&2
  exit 1
fi

stage="$(mktemp -d /var/tmp/ccpc-prod-image-export.XXXXXXXX)"
archive="$stage/ccpcerp-v16.50.0.tar"
echo "Exporting verified production image to protected location: $stage"
docker image save --output "$archive.partial" ccpcerp:v16.50.0
test -s "$archive.partial"
mv -- "$archive.partial" "$archive"
chmod 600 "$archive"

printf 'SOURCE_IMAGE_ID=%s\n' "$actual"
printf 'ARCHIVE_PATH=%s\n' "$archive"
printf 'ARCHIVE_BYTES=%s\n' "$(stat -c %s "$archive")"
sha256sum "$archive"
EOF
```

**Expected safeguards:** `mktemp -d` unique directory is created by root with `0700` in local `/var/tmp`, `umask 077` limits file permissions, only the immutable-ID matched tag is exported, `.partial` is not promoted to final archive on failed save, final image archive is chmod `0600`, source and exported artifact sizes/hash printed for review. If any operation errors, **STOP**, preserve output and any partial archive; do not retry blindly or delete source data. `docker save` reads image layers and causes disk/CPU I/O and a local write, but should not touch running containers. The archive may embed sensitive deployment content; never attach it publicly, push to GitHub, share checksum together with secrets, or put it in the automatic NAS-retention tree.

**Following gate:** Wait for operator's actual archive path, byte count and SHA-256 checksum, then validate status and prepare a separate approval for secure transfer to the isolated new host. Preserve Nov 5 four-artifact backup checksums separately and do not substitute the Nov 5 rehearsal snapshot for later live transactions without a separately approved final reconciliation/cutover plan.

## ALL SIX RUNNING LIVE PROD APP IMAGE IDS MATCH — 2026-11-06

**Owner-run read-only `docker inspect` on OLD live `ccpcerpserver`:** All six running PRODUCTION app containers, `frappe_docker-frontend-1`, `frappe_docker-backend-1`, `frappe_docker-queue-short-1`, `frappe_docker-queue-long-1`, `frappe_docker-websocket-1`, and `frappe_docker-scheduler-1`, returned **exactly** `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. **PASS:** a single existing `ccpcerp:v16.50.0` Docker image covers every application service, not just the backend; separate MariaDB and Redis are independent standard images, and their live data/config remain separately required.

**Ready for the next consent gate — not yet authorized:** Ask owner for **explicit, narrowly scoped approval** to create **one protected local `docker save` image archive on OLD `ccpcerpserver` only**. Intended safe procedure, after approval: re-check the tag still resolves to the verified immutable image ID; allocate a unique root-owned `0700` scratch directory on the OLD local filesystem outside NAS/backup retention, using restrictive umask and rejecting collisions; `docker save` only `ccpcerp:v16.50.0`; calculate/archive SHA-256 and actual bytes; leave source image, all running containers, DB, site and backup files untouched; report archive path and checksum without displaying secrets. The operation has bounded local write/storage/CPU/I/O effects and is not a zero-impact read-only check, so it requires owner approval. **Do not perform archive creation, SCP/rsync transfer, image import, Docker Compose startup, restore or go-live merely on this checkpoint.**

**Separation:** The selected November 5, 2026 four-artifact backup was checksum-checked/format-checked and is for **isolated non-live restoration rehearsal** only; post-snapshot transactions must be reconciled and a fresh final consistent backup or an explicit business decision required before any go-live. Never modify old production or DEVELOPMENT while preparing the dedicated server.

## OLD HOST STAGING CAPACITY VERIFIED — 2026-11-06

**Owner-run read-only on OLD `ccpcerpserver`:** `df -h /var/lib/docker /home/gani` reported the same root filesystem `/dev/nvme0n1p2` for both paths: **915G total, 182G used, 687G available, 21% utilization**. These are two views of **one** filesystem, not 1,374G of free space. The NEW `ccpcerp-prod` host separately reported **740G free** on its root logical volume. Both appear to have ample headroom for the approximately 866 MiB source application image, but the actual `docker save` archive, temporary copies, loaded layers and restore footprint remain unmeasured.

**NEXT single OLD-host read-only identity check, all six PRODUCTION application containers:** Confirm their immutable image IDs before proposing an image archive export:

```bash
sudo docker inspect --format '{{.Name}} {{.Image}}' \
  frappe_docker-frontend-1 \
  frappe_docker-backend-1 \
  frappe_docker-queue-short-1 \
  frappe_docker-queue-long-1 \
  frappe_docker-websocket-1 \
  frappe_docker-scheduler-1
```

All six outputs **should match** the already verified backend/container-and-tag image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. If not, STOP; do not export a single image assuming uniform source. Only after this read-only step should the operator be asked for **separate approval** of a bounded archive export. No file transfers, image writes, Docker restarts, database changes, or new-host deployment authorized or performed. The Nov 5 four-file source backup is selected for isolated rehearsal only; post-snapshot live transactions remain protected.

## OLD PRODUCTION IMAGE SIZE VERIFIED — 2026-11-06

**Owner-run read-only on OLD `gani@ccpcerpserver`:** `sudo docker image inspect ccpcerp:v16.50.0 --format 'source_image_bytes={{.Size}}'` returned `source_image_bytes=907815909`, about **866 MiB** (0.908 GB decimal). This is the image identified by the previously verified live backend image ID `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`. The new dedicated host has `740G` free on its single shared root filesystem as last reported.

**Scope:** Image inspection did not write or restart any container. Docker's image `.Size` is **not** a measured `docker save` archive size, and it does not cover the site/database restore, free space on OLD host or any staging overhead. The exact original image is still to be preserved, without a new build from DEVELOPMENT.

**NEXT single read-only operator step, OLD host `ccpcerpserver`:**

```bash
df -h /var/lib/docker /home/gani
```

This confirms actual filesystem headroom for a protected, separately approved *local image export*, without placing export files in the old NAS backup-retention tree or touching active Docker objects. After old-host capacity and the remaining application-container image IDs are verified, propose one bounded export/staging operation for explicit approval; create no archive or transfer yet. The selected Nov 5 backup remains a rehearsal snapshot, not final cutover data.

## DEDICATED HOST DISK SPACE VERIFIED — 2026-11-06

**Owner-run read-only on NEW `ccpcadmin@ccpcerp-prod`:** `df -h / /var/lib/docker /home/ccpcadmin` showed each path on the **same** device `/dev/mapper/ubuntu--vg-ubuntu--lv`, filesystem size `787G`, used `7.1G`, available `740G`, utilization `1%`. **PASS — substantial free space currently available**. These three rows report one shared filesystem, **not three separate 740G reserves**. No allocation or transfer was performed.

This observation alone does **not** prove final capacity for a Docker image archive and loaded layers, database and file staging, restored volumes, logs, temporary duplication, backup and rollback. Do not touch either host's existing Docker/project resources or storage permissions.

**NEXT one read-only OLD-host command** to size the exact already verified `ccpcerp:v16.50.0` image before specifying safe transfer paths:

```bash
sudo docker image inspect ccpcerp:v16.50.0 --format 'source_image_bytes={{.Size}}'
```

Docker's reported image size is **not necessarily the size of a `docker save` archive**, but it provides a useful sizing baseline. Actual image export, transfer, import, restored stack and use of old production secrets remain separately approval-gated. November 5 source snapshot remains the owner-selected **rehearsal** backup, not a final-write-fenced cutover snapshot.

## NOV 5 SOURCE SHA-256 VALUES RECORDED — 2026-11-06

**Owner-run read-only checksums from OLD `ccpcerpserver`:** `sha256sum` completed on the exact four files selected for the isolated November 5 migration rehearsal. These are source-file baselines (not after-transfer verification, not a restore test), and the source NAS artifacts remain unchanged.

```text
8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87  20261105_020001-ccpcerp_local-database.sql.gz
200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6  20261105_020001-ccpcerp_local-files.tar
60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf  20261105_020001-ccpcerp_local-private-files.tar
b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b  20261105_020001-ccpcerp_local-site_config_backup.json
```

**Next migration preflight (read-only NEW host):** Confirm free capacity on intended new-host root/Docker/home filesystems before any image or backup staging:

```bash
df -h / /var/lib/docker /home/ccpcadmin
```

Do not assume enough capacity for the exact Docker image archive, loaded layers, database restoration and rollback until full image size and planned transfer staging are assessed. All actual file transfers, `docker save/load`, credentials provisioning, Compose deployment, database/file restoration, and live cutover remain separate explicit execution approvals. The November 5 backup is **rehearsal data only**; future business writes are preserved on old PRODUCTION and need a final reconciled migration plan.

## FOUR FORMAT CHECKS PASS — OWNER-SELECTED NOV 5 SNAPSHOT, 2026-11-06

**Owner-run exact Nov 5 file-format verification on OLD `ccpcerpserver`:** The previously supplied read-only script tested the compressed database with `gzip -t`, both public/private TAR archives with `tar -tf >/dev/null`, and the site-configuration file with `python3 -m json.tool >/dev/null`. Owner reported four success markers, in order:

```text
DATABASE_GZIP_OK
PUBLIC_FILES_TAR_OK
PRIVATE_FILES_TAR_OK
SITE_CONFIG_JSON_OK
```

**PASS — narrow:** The chosen `2026-11-05_02-00` set contains four nonempty files and these format-level checks succeeded. This is **not** evidence that all expected business records or attachments were captured, that the backup is self-consistent, or that a Frappe restore will succeed. Never print site-config JSON (it may contain secrets), extract to the active production server, or delete an existing restore point.

**NEXT one read-only operator check on OLD host only — capture exact source file SHA-256 digests prior to any approved transfer:**

```bash
sudo bash -c '
set -e
cd /mnt/erpnext_backups/2026-11-05_02-00
sha256sum -- \
  20261105_020001-ccpcerp_local-database.sql.gz \
  20261105_020001-ccpcerp_local-files.tar \
  20261105_020001-ccpcerp_local-private-files.tar \
  20261105_020001-ccpcerp_local-site_config_backup.json
'
```

The command only **reads** four named backup artifacts and prints hashes and filenames, not file contents. Keep the source backups unchanged and verify corresponding hashes after a separately approved protected transfer. Check disk capacity, secure archive-handling and preservation of old/current transactions before any `docker save`, file copy, isolated restore or cutover. **Nov 5 is a rehearsal source**; do not replace live current business records with a stale snapshot without a separate, explicit reconciliation/data-loss decision.

## OWNER-SELECTED NOVEMBER 5, 2026 PRODUCTION BACKUP — 2026-11-06

**Owner explicitly directed: "USE NOVEMBER 05, 2026".** The selected **existing live-PRODUCTION** recovery set for the **isolated, non-live migration rehearsal** is:

`/mnt/erpnext_backups/2026-11-05_02-00` on **OLD** `ccpcerpserver`, verified mounted from `//192.168.50.132/erpnext_backups` (`cifs`). This is a *source selection*, not a successful restore, host-copy approval, final cutover authorization, or acceptance of any lost transactions.

**Owner-run read-only inventory:**

| Artifact | Verified filename | Bytes |
| --- | --- | ---: |
| Database | `20261105_020001-ccpcerp_local-database.sql.gz` | 1198839 |
| Public files | `20261105_020001-ccpcerp_local-files.tar` | 10240 |
| Private files | `20261105_020001-ccpcerp_local-private-files.tar` | 20480 |
| Site configuration | `20261105_020001-ccpcerp_local-site_config_backup.json` | 280 |

**Verification status:** Four expected *names* present as nonempty regular files. File integrity, contents, application compatibility, restorability and completeness remain unverified. Small tar archives could be legitimate or contain little/no data; inspect safely rather than assuming completeness. Site configuration may contain passwords/encryption keys; **never display or paste its contents**.

**Freshness/RPO boundary:** A snapshot created 2026-11-05 02:00:01 +08 predates the current 2026-11-06 conversation. Transactions, attachments, user changes and other writes **after** the snapshot will not exist in that restored snapshot. Owner's choice authorizes **using it for preparation/rehearsal**; **do not infer** approval to go live with that older dataset while there may be subsequent transactions. Before cutover, either perform a separately approved final consistent synchronized copy with old writes fenced and reconciliation, or obtain an explicit business-signed data-loss/recovery decision—do not silently drop later entries. Keep old production live and untouched.

**Next bounded read-only step on OLD host:** Test this exact source set's gzip/tar archive structures and site-config JSON syntax without extracting or printing sensitive contents, before any transfer. Preserve the original files; no archive rewriting, database restore, service operation or cleanup.

## OLD PROD NAS DIRECTORY RECENCY CHECK — 2026-11-06

**Owner-provided read-only directory name inventory from OLD live `ccpcerpserver`:** `sudo find /mnt/erpnext_backups -mindepth 1 -maxdepth 1 -type d -name '20??-??-??_??-??' -printf '%f\\n' | LC_ALL=C sort -r | head -n 10` returned:

```text
2026-11-05_02-00
2026-11-04_02-00
2026-11-03_02-00
2026-11-02_02-00
2026-11-01_02-00
2026-10-31_02-00
2026-10-30_02-00
2026-10-29_02-00
2026-10-28_02-00
2026-10-27_02-00
```

**Observation:** Ten consecutive **directory names** indicate periodic NAS publication activity through November 5, 2026. A November 6 02:00 directory is **not present among these ten newest matching directories** despite historical 02:00 daily root cron; this is an **unresolved freshness discrepancy** (may be missed job, changed naming, alternate location, schedule or error). Do not assert a Nov 6 backup failed without cron/log evidence. Directory names alone do **not** prove a complete backup or successful restore.

**NEXT one read-only OLD-host check:** Inspect **file names and sizes only** for the latest shown candidate directory, without opening or copying sensitive contents:

```bash
sudo find /mnt/erpnext_backups/2026-11-05_02-00 -mindepth 1 -maxdepth 1 -type f -printf '%f\t%s bytes\n' | LC_ALL=C sort
```

Look for non-empty compressed SQL database, public file archive, private file archive and site-config backup. After this, investigate missing November 6 backup via sanitized scheduler status/log checks before authorizing a fresh production recovery set, image archive or any restore. Do not run backup script, edit cron, delete backups or change production under this read-only approval.

## LIVE LEGACY NAS MOUNT — VERIFIED 2026-11-06, BACKUP CONTENT PENDING

**Owner-run read-only on OLD `gani@ccpcerpserver`:**

```bash
findmnt --mountpoint /mnt/erpnext_backups --output TARGET,SOURCE,FSTYPE --noheadings || echo NOT_MOUNTED
```

Output: `/mnt/erpnext_backups //192.168.50.132/erpnext_backups cifs`.

**PASS (narrow):** The expected Synology filesystem is actually mounted at the correct host location; it is not merely an empty local directory. This does **not** yet prove share writability, scheduled backups running, recent complete four-artifact backup, immutability, archive integrity or restore success. No backup job or Docker operation performed.

The historical GitHub `recovery.md` documents one completed manual four-artifact backup from September 2, 2026, and a proposed 02:00 daily cron/30-day NAS retention; those are historical records and not proof of present scheduled operation.

**NEXT one read-only operator step on OLD host:** list *names only* of the 10 newest-looking timestamp-formatted backup directories without opening files, changing retention or exposing site data:

```bash
sudo find /mnt/erpnext_backups -mindepth 1 -maxdepth 1 -type d -name '20??-??-??_??-??' -printf '%f\n' | LC_ALL=C sort -r | head -n 10
```

If none appear or dates are stale, stop to diagnose the backup schedule before any migration. If recent directories appear, inspect **exactly one selected run's** file names/sizes and verify four mandatory artifacts in a following controlled read-only step, then plan an explicitly approved fresh consistent migration backup and isolated restore. Do not delete/move/rename existing backups or run the backup script merely to test it.

## LIVE IMAGE BUILD LABELS ABSENT — EXACT-IMAGE MIGRATION PATH, 2026-11-06

**Owner read-only result on old `ccpcerpserver`:** `sudo docker image inspect ccpcerp:v16.50.0 --format 'frappe={{index .Config.Labels "org.ccpc.frappe.sha"}} erpnext={{index .Config.Labels "org.ccpc.erpnext.sha"}} ccpcerp={{index .Config.Labels "org.ccpc.ccpcerp.sha"}} patch={{index .Config.Labels "org.ccpc.erpnext.patch.sha256"}} overlay={{index .Config.Labels "org.ccpc.erpnext.overlay.sha256"}}'` printed `frappe= erpnext= ccpcerp= patch= overlay=`. This specific existing image does **not** expose the queried build-input labels. Their absence is **not** an application failure and does **not** undo the verified container/image ID match.

**Chosen approach:** Do **not** waste migration time guessing Git SHAs or rebuilding `ccpcerp:v16.50.0` from later GitHub source. Treat the already verified running image `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8` as the immutable migration baseline. During a **later separately approved** image-transfer stage, make a protected `docker save` archive of the **existing old-host image**, securely transfer, `docker load` only on the new isolated host, and verify the resulting image ID matches exactly before use. Review archive size/destination/free space, checksums, permissions, secure transfer and recovery. Image export/import is not yet authorized. The application image alone does **not** carry the live MariaDB DB or site volumes/files.

**Move to recovery readiness now:** Old legacy recovery guide `recovery.md` names host path `/mnt/erpnext_backups` and a past NAS source `//192.168.50.132/erpnext_backups`. Older manual backup evidence is historical and cannot certify present backups. Next *single read-only old-host step* checks **exact active mount** without reading backup contents or credentials:

```bash
findmnt --mountpoint /mnt/erpnext_backups --output TARGET,SOURCE,FSTYPE --noheadings || echo NOT_MOUNTED
```

Expected if unchanged is filesystem `cifs` and **exact source** `//192.168.50.132/erpnext_backups`; anything else (including `NOT_MOUNTED`) is a **STOP**, not permission to write backups to a local fallback directory. After mount identification, separately verify recent *complete* four-artifact backup and recovery readiness, then seek explicit approval for a fresh consistent production backup and isolated new-host restore. No current PROD or DEV write has been authorized or performed.

## NO .git IN LIVE IMAGE — EXPECTED BUILD PACKAGING, 2026-11-06

**Observed old live `ccpcerpserver`**: operator executed `sudo docker exec frappe_docker-backend-1 bash -lc 'for app in frappe erpnext ccpcerp; do printf "%s " "$app"; git -C "/home/frappe/frappe-bench/apps/$app" rev-parse HEAD; done'`. Each returned `fatal: not a git repository`; this means that **this in-container Git lookup is unavailable**. It is **not** evidence that installed applications are missing or damaged, and no install/migration/restore should be attempted in response.

**Verified GitHub source explanation (2026-11-06):** The reviewed deployment `images/custom/Containerfile` on `review/dedicated-host-readonly-inventory-2026-10-25` deliberately removes `apps/*/.git` after verifying the builder's expected commits (`find apps -mindepth 1 -path "*/.git" | xargs rm -fr`), then writes build-input OCI image labels `org.ccpc.frappe.sha`, `org.ccpc.erpnext.sha`, `org.ccpc.ccpcerp.sha`, `org.ccpc.erpnext.patch.sha256`, `org.ccpc.erpnext.overlay.sha256`. We **have not yet proven** the old running image was built from this exact reviewed Containerfile; inspect actual immutable image labels to find out. These are **build-time claims** and not a cryptographic signature or independent attestation.

**New next operator step — OLD host read-only image labels only** (safe fixed keys, no environment/secrets dump):

```bash
sudo docker image inspect ccpcerp:v16.50.0 --format 'frappe={{index .Config.Labels "org.ccpc.frappe.sha"}} erpnext={{index .Config.Labels "org.ccpc.erpnext.sha"}} ccpcerp={{index .Config.Labels "org.ccpc.ccpcerp.sha"}} patch={{index .Config.Labels "org.ccpc.erpnext.patch.sha256"}} overlay={{index .Config.Labels "org.ccpc.erpnext.overlay.sha256"}}'
```

If labels are absent (e.g. `<no value>`), stop; use `bench version` or package metadata with a separate reviewed read-only step rather than guessing. Do not run `git init`, `git pull`, build, migrate, or change containers. The already verified running backend image SHA-256 remains the primary source identity.

## VERIFIED RUNNING PROD BACKEND IMAGE SHA-256 — 2026-11-06

**Owner-reported from OLD live `gani@ccpcerpserver`, read-only Docker metadata only.** Commands:

```bash
sudo docker inspect --format 'running_backend_image_id={{.Image}}' frappe_docker-backend-1
sudo docker image inspect ccpcerp:v16.50.0 --format 'tag_image_id={{.Id}} created={{.Created}}'
```

Results:

- Backend container actual image ID: `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`
- Local `ccpcerp:v16.50.0` image ID: **the same** `sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8`
- Local image created: `2026-09-16T15:55:49.950715082+08:00`
- Outcome: **PASS for backend container/tag identity at observed time**. Does not yet prove other five app containers' immutable IDs, or the inner application Git SHAs/dirty patch state. No Docker files, application data, or containers modified.

**Next operator step (read-only, on OLD `ccpcerpserver` only):**

```bash
sudo docker exec frappe_docker-backend-1 bash -lc 'for app in frappe erpnext ccpcerp; do printf "%s " "$app"; git -C "/home/frappe/frappe-bench/apps/$app" rev-parse HEAD; done'
```

This reads the three application Git commit IDs from the running backend; do not run `bench migrate`, `git pull`, `git reset`, image build, or app installation. The next gate after commits is checking clean/modified source and compatibility, then separately approved complete four-part backup and a non-live restore rehearsal.

## VERIFIED OLD LIVE PRODUCTION CONTAINER INVENTORY — 2026-11-06

**Owner-run, read-only on old host `gani@ccpcerpserver`**: `hostnamectl --static` printed `ccpcerpserver`; `sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'` showed the active live PRODUCTION Compose project `frappe_docker` and separate DEV Compose project `frappe_docker_devcontainer`.

- **Six PRODUCTION app containers** `frappe_docker-frontend-1`, `frappe_docker-queue-short-1`, `frappe_docker-backend-1`, `frappe_docker-queue-long-1`, `frappe_docker-websocket-1`, `frappe_docker-scheduler-1` all use the same locally tagged application image **`ccpcerp:v16.50.0`** and reported `Up 3 weeks`. **Do not use the earlier `release-2026-09-16` or unmerged billing PR #33 instead.** The tag alone does *not* prove immutable image bytes, application Git SHA, exact Frappe/ERPNext revisions or installed patches.
- **PRODUCTION database** `frappe_docker-db-1` is `mariadb:11.8`, reported `Up 3 weeks (healthy)`; `frappe_docker-redis-cache-1` and `frappe_docker-redis-queue-1` use `redis:8.6-alpine`.
- **Separate DEVELOPMENT project** `frappe_docker_devcontainer`: a `vsc-frappe_docker-…-uid` Frappe container, `mariadb:11.8` database and two `redis:alpine` containers. All four reported `Up 3 weeks`; they are **not** migration sources and must not be copied/reconfigured.
- This was a metadata-only observation, not a full application health or backup validation. No container was restarted, copied, or changed. The source host's sudo password was entered locally; it was not supplied to chat.

**Next operator step (single bounded read-only inspection on OLD host):** Confirm the actual running backend container's image ID matches the local `ccpcerp:v16.50.0` tag before freezing image provenance:

```bash
sudo docker inspect --format 'running_backend_image_id={{.Image}}' frappe_docker-backend-1
sudo docker image inspect ccpcerp:v16.50.0 --format 'tag_image_id={{.Id}} created={{.Created}}'
```

Stop and investigate if the image IDs differ; do not `pull`, `build`, `save`, `commit`, or modify either environment yet. After identity alignment, read installed Frappe/ERPNext/CCPC versions and exact Git commits with a separately reviewed read-only procedure; then plan/authorize complete backup, new-host isolated restore and cutover.

## CURRENT DECISION — 2026-11-06: migrate **only existing live PRODUCTION**, unchanged in functionality

**Owner-directed scope change (supersedes the earlier candidate app PR #33 release path and this document's prior 'accounting acceptance first' recommendation):** Relocate the **already running live production** from the shared legacy Ubuntu host `ccpcerpserver` to the new physically dedicated `ccpcerp-prod`, without promoting unfinished DEVELOPMENT features. The application, version, database and business configuration source of truth is the **actual active legacy PRODUCTION deployment**, not DEVELOPMENT Git state and not a future release candidate. The old host's DEVELOPMENT installation remains untouched and continues independently.

**Decision is approved as migration direction and planning scope; production-impacting execution remains separately gated.** Do not interpret the owner's proposal as blanket approval for new-host container creation, exporting/copying the live database, taking new production backups, secrets handling, restoration, migrations, DNS cutover, stopping legacy services or retiring the old production instance. Obtain exact scoped approval for each consequential phase after presenting a verified plan.

**What must be included:** same live ERPNext/Frappe/installed CCPC application code and metadata (verify running image identity, app revisions, patches and versions), all existing PRODUCTION Companies, Chart of Accounts, inventory/Stock Ledger, GL, users/roles/User Permissions, business documents and configuration; **all four Frappe backup artifacts** — database, site configuration, public files and private files — plus independently handled environment secrets, integration config and recovery prerequisites. Keep the Frappe site identity `ccpcerp.local` unless a later separately approved compatibility plan requires otherwise.

**What must NOT be included:** any changes existing only in `development.localhost`, disposable CI/integration sites, unmerged review/feature branches, PR #33's unfinished billing roles/policies, DEV test records, DEV database or DEV credentials. The custom app Git `version-16` HEAD or `release-2026-09-16` pin alone is **not proof** of what currently runs on old production; exact live image/application version must be observed and preserved or reproducibly matched. Do not introduce a newer app release, unapproved DocTypes, database patches, workflows, role grants, or business rules as part of this infrastructure migration.

**Infrastructure compatibility is separate from changing business functionality:** The new host still requires independently protected credentials, Docker/Compose networking, appropriate image availability, volumes, NAS backup, TLS/firewall and restore testing. Those safe host-specific changes may be needed to run the same application, but must be reviewed for unwanted app or data/schema changes. An accidental version mismatch or automatic `bench migrate` could change schema/business behavior; exclude it until independently justified and approved.

### Migration sequence / safety gates

1. **Read-only old-host baseline first:** verify `ccpcerpserver` host identity; current legacy production containers, Compose project, image tags/IDs, installed app and Frappe/ERPNext versions and Git SHAs (including dirty changes), database/site identity, declared volumes, existing backup job and NAS path — without printing secrets or modifying any container. Separate production facts from development data. On the new host, already-verified empty Docker inventory and two clean historical checkouts need not be repeated unless changed.
2. **Freeze exact production-source identity:** choose an immutable, verifiable copy of the *live* app image or a byte-equivalent reproducible build from precisely matched commits and tracked overlays, supported by backups and checksums. Do not use the candidate `1bde04b` billing app or `c12d46f` dedicated review stack as a substitute for live-app identity; the latter may supply **reviewed infrastructure safeguards only** after checking for compatibility.
3. **Approved full recovery point:** produce a new, consistent legacy production four-artifact backup; independently verify files and off-host NAS, preserve an unaffected recovery point, and capture an approved operational settings/credential re-provisioning inventory. Confirm that backup creation alone is not restore proof.
4. **Isolated new-host rehearsal:** on a separately authorized non-live stack, restore old production data and verify documents/attachments, company books, stock/GL totals, permissions, version compatibility and migration behavior. During testing, prevent duplicate scheduled jobs, background workers, email, external integrations, payment/accounting writes and network access to employees; do not let a restored copy and old production both process business events. Do not make the new copy live before validation.
5. **Separate planned cutover:** approved downtime/maintenance window; quiesce/fence writes and background processing on old PRODUCTION; make a **fresh final consistent backup/sync** (not the earlier rehearsal copy); verify checksums, restore and reconciliation; separately approve and configure LAN DNS/TLS/endpoints and start only the new production instance. Ensure no split-brain/simultaneous write access.
6. **Post-cutover:** validate representative real production records, GL/SLE balances, attachments, login, workers, scheduler, integrations and new NAS scheduled backups; retain old production isolated and recoverable until explicit approval of retirement. Define rollback triggers and data reconciliation before any cutover.

**Immediate next operator step (read-only on OLD host only, not on new `ccpcerp-prod`):** Once in the trusted `gani@ccpcerpserver` session, execute:

```bash
hostnamectl --static
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

If hostname differs from `ccpcerpserver`, stop. Output lists container metadata only; **no secrets, volume contents or Frappe data**. This establishes exactly which production image/tag and relevant containers currently run before requesting any backup or restoration actions. Record the date, source host and operator output. Do not stop/restart any container.

**Historical sections below remain as review evidence only:** Previous proposals to deploy PR #33 and resolve its incomplete Finance billing functionality **before** migrating are **superseded for this live-only move**, though still valid for a later independent DEVELOPMENT-to-PRODUCTION release after successful migration. Ignore old 'next step' wording where it conflicts with this current decision.

---

**Created:** 2026-11-06  
**Scope:** Dedicated Ubuntu server `ccpcerp-prod`, **not yet live**.  
**Status:** Preparation/documentation approved; no authorization for container creation, deployment, database restoration/migration, cutover, or old-host changes.  
**Purpose:** Preserve current verified facts and the shortest safe continuation path so subsequent conversations do not repeat completed read-only inventory.

## How to use this file

1. **Read this production record first** for dedicated-host facts, current decisions, checks, and deployment gates. Read [the GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md) and [active app/development handoff](CURRENT-HANDOFF-3.md) for overall engineering state.
2. GitHub controls committed deployment code and documentation; **live host output controls actual running state**. Date every new host observation. Do not silently upgrade a historical observation into current proof.
3. Update this file after meaningful host verification, approved deployment/restore, or recovery milestones. Keep a concise **latest checkpoint at the top**; archive lengthy test transcripts separately. Never store passwords, private keys, complete `.env`, credentials, sensitive configuration, database content, or unredacted logs.
4. Preserve DEV/PROD physical separation and the **old** production server. GitHub merges or preparatory approval do not authorize production runtime changes.

## Latest checkpoint — 2026-11-06 (owner-reported read-only terminal output)

**Host:** New dedicated `ccpcerp-prod`, LAN `192.168.50.186`, account `ccpcadmin`. Historic host provisioning documented in [PRODUCTION-HOST-SETUP-HANDOFF.md](PRODUCTION-HOST-SETUP-HANDOFF.md). Windows SSH uses an owner-held Ed25519 key; do not request or copy private key material. Earlier reported `hostnamectl --static` = `ccpcerp-prod`, Docker context = `default`; this conversation's inspected Docker endpoint was `unix:///var/run/docker.sock` per prior guarded-run status, not independent proof of immutable daemon identity.

**Docker and permissions:** Docker Compose reports `5.6.1`; `sudo systemctl is-active docker` returned `active`. Socket `/var/run/docker.sock` was `root:docker` with mode `srw-rw----`; `ccpcadmin` is in `adm cdrom sudo dip plugdev lxd`, **not** `docker`. Unprivileged inventory failed with `permission denied`; later *explicit owner-performed* read-only `sudo docker ps`, `sudo docker ps -a`, and `sudo docker system df -v` succeeded and showed **zero running/stopped containers, zero Docker images, zero Docker local volumes, and 0 B build cache**. This is **consistent with the brand-new host**, not evidence of deleted ERPNext data. Docker network inventory, actual firewall behavior and effective Compose model have **not** been verified in this checkpoint. Do not change Docker socket mode/groups/ACLs merely for convenience; Docker access is effectively root-level.

**Host Git checkouts (owner-reported):**

| Location | Branch | HEAD (short) | Git state | Remote |
|---|---|---|---|---|
| `/home/ccpcadmin/ccpc-frappe-deployment` | `security/dedicated-production-pre-tls-2026-10-23` | `0bf8c6a` | clean (`git status --short` empty) | `git@github.com:ccpcerp/ccpc-frappe-deployment.git` |
| `/home/ccpcadmin/ccpc-pr29-review` | `security/dedicated-prod-external-env-2026-10-23` | `bd92ade` | clean (`git status --short` empty) | same |

Both checked-out commits matched the GitHub PR branch tips on 2026-11-06. The first checkout tracks `compose.yaml`, `overrides/compose.dedicated-pre-tls.yaml`, `images/production/Containerfile`, and the dedicated port-profile document. The second additionally tracks `docs/04-operations/dedicated-production-external-credentials.md`. **Preserve both checkouts; no blind pull, switch, clean, reset or overwrite.**

**Connected GitHub PR status (2026-11-06):** [PR #27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27) pre-TLS `0bf8c6a`, [PR #29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29) external credentials `bd92ade`, [PR #30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) backup safety `fd751ab` are **OPEN/DRAFT/UNMERGED**, stacked in that order. These are **review candidates**, not approved deployed releases. Later dedicated Compose identity/environment reviews also exist; see [Step 144 inventory record](DEDICATED-PROD-STEP144-READONLY-HOST-INVENTORY-2026-10-25.md) and verify the right final reviewed source revision before use. The app's feature/review branches must also be reverified at release selection; never assume `version-16` includes all reviewed functionality.

## GitHub-only source review — 2026-11-06 (no host execution)

**Owner approval:** Continue non-live preparation and preserve a dedicated production record. Review executed through connected GitHub only; no PR merge, SSH session, credential provision, Compose execution, image build, container start, database operation or production modification.

**Verified review ancestry:** GitHub compare shows PR #29 is 10 commits ahead/0 behind PR #27; PR #30 is 27 ahead/0 behind PR #29; `review/dedicated-host-readonly-inventory-2026-10-25` (`c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` at this review) is 20 ahead/0 behind PR #30. The latter contains later Compose project/credential-selector guards and the read-only host inventory helper, **but is still a review branch and not a final approved production release**. The existing on-host directories are behind these later draft protections; preserve them rather than pulling automatically.

**Candidate source inspection:** On the later review branch, `scripts/config.sh` blob `32614da1044c768bd67dcb9b9491e7c48ff2653a` defines five Compose inputs for `dedicated-pre-tls`, adding `overrides/compose.dedicated-pre-tls.yaml` last. The override blob `14fd89a3c2371104f464964137483de9f4a35861` replaces frontend publication with `127.0.0.1:8080:8080/tcp`, requires nonempty `DB_PASSWORD`, and declares explicit backend sites/logs mounts. The revised Docker module blob `a99bcdb2077f55f5ded118159ad72a90d0a9fd7e` requires the dedicated env file (external, 0600, owner-only parent 0700, one `DB_PASSWORD` key), rejects ambient Compose project/file/profile selection, verifies local default Docker context/socket, and passes the **candidate-only** `--project-name ccpc_prod_erpnext`. These are **source-level findings, not a real `docker compose config` validation**.

**Material pinning gap:** `scripts/config.sh` still pins `CCPC_REF=release-2026-09-16` with `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`; later October/November business application review work exists. **Do not equate this pinned older app revision with the current proposed day-one financial/billing release** or automatically change it to the moving `version-16` tip. Independently select and approve exact app source, Frappe/ERPNext compatibility, image provenance, unresolved permissions/SoD issues, and migrations before any release build.

**No-runtime-render gap:** All five-file Compose inputs still need an exact-source, secret-safe `docker compose config --quiet` validation in an authorized environment, followed by sanitized verification of service/port/mount metadata, Compose project identity, expected volumes and unknown environment-selector behavior. Avoid full config dumps that interpolate credentials. Docker zero-resource inventory reduces name-collision uncertainty only at the time observed; it is not authorization to allocate volumes or start services.

**Next decisive action:** Review the specific app candidate release SHA and unresolved blockers alongside the stacked dedicated Compose review branch; produce a single pinned candidate and a safely executable, credential-free or synthetic Compose-validation plan. The on-host checkouts and old PRODUCTION remain untouched. Real secret provisioning, host checkout updates, image build, starting containers, backups/restores, migration and cutover each retain their respective explicit approval gates.

## Source-pinned candidate selection and Compose validation plan — 2026-11-06

**Outcome:** Identified a **provisional application candidate and provisional deployment-review baseline**, not a buildable/approved release pair. All findings are from connected GitHub; zero server or Compose execution.

### Candidate sources verified

| Part | Provisional source reference | Verified state | Disposition |
|---|---|---|---|
| Application baseline | `ccpcerp/ccpcerp` `version-16` @ `cfcc19394a6646548f2b7050db040c8cf5ebafde` | Older base; 585 commits behind the billing review head (GitHub compare) | **Not sufficient for latest day-one billing behavior** |
| Application candidate | `ccpcerp/ccpcerp` `review/billing-authorization-correction-2026-11-03` @ `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` | PR #33 OPEN/DRAFT/unmerged; GitHub combined commit status SUCCESS with `python-syntax`, `billing-controls-manual-approval`, `billing-controls-isolated-integration` | **Pin for review only**; not live-accepted or production approved |
| Deployment baseline | `ccpcerp/ccpc-frappe-deployment` `review/dedicated-host-readonly-inventory-2026-10-25` @ `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e` | Descends from PRs #27/#29/#30; includes reviewed project-name and local Docker checks | **Pin for source review only**; not merged or production approved |
| Frappe / ERPNext | `FRAPPE_REF=v16.33.1` and `ERPNEXT_REF=v16.34.2` in deployment `scripts/config.sh` | Corresponding SHAs and ERPNext patch/overlay hashes are frozen in that file | **Compatibility and image build still unverified** |

**Critical alignment issue:** The pinned deployment `scripts/config.sh` and `apps.json` still reference `CCPC_REF=release-2026-09-16`, `CCPC_SHA=cfcc19394a6646548f2b7050db040c8cf5ebafde`, and `apps.json` branch `release-2026-09-16`. The image Containerfile explicitly checks the cloned application's actual `HEAD` against `EXPECTED_CCPC_SHA`; therefore **changing only the expected SHA fails unless the Git fetch ref also retrieves that exact revision**. An approved release must introduce an immutable reachable app ref (or deliberate supported exact-SHA checkout design), update `CCPC_REF`, `CCPC_SHA` and `apps.json` coherently on a **new reviewed deployment branch**, then validate private Git fetch, image build, framework/ERPNext version compatibility, and installed app behavior. Do **not** change the existing two server checkouts, copy draft code straight into live production, or substitute a moving branch/ref as an immutable release pin.

**Business and acceptance blockers:** The three GitHub CI statuses establish bounded automated results, **not** persistent DEVELOPMENT named-Checker acceptance, solved Purchase Invoice Submit separation of duties, full authenticated HTTP/concurrency regression coverage, signed image release, or disaster recovery. Consult `CURRENT-HANDOFF-3.md` before asserting these gaps have closed. PR #33 remains draft and requires business/security review before release approval.

### Source-pinned safe Compose validation — plan only

1. Start with an **isolated scratch/lab checkout** of the exact reviewed deployment commit `c12d46f7363c93742f7e9fb88b2e14a67dbd9a7e`; preserve existing production host checkouts. Check blob fingerprints and verify all five Compose files in this exact order: `compose.yaml`, `overrides/compose.mariadb.yaml`, `overrides/compose.redis.yaml`, `overrides/compose.lan-production.yaml`, `overrides/compose.dedicated-pre-tls.yaml`.
2. First use credential-free static/offline tests and Bash syntax checks. The final override must replace `frontend.ports` to `127.0.0.1:8080:8080/tcp`; there should be no published MariaDB/Redis host ports. Review YAML `!override` semantics with real Compose 5.6.1 or an approved known-compatible Compose v2 lab CLI, not a generic YAML parser alone.
3. For a later **explicitly authorized isolated Compose render**, supply **synthetic test-only** `DB_PASSWORD` via an ephemeral protected 0600 external file in an owner-controlled 0700 directory, **not** via checkout `.env` or real production secrets. Use `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls` and reviewed explicit image name/tag. Run only non-deploying `docker compose ... config --quiet` with the pinned five-file configuration and project selector in the authorized lab. Do **not** print full `config` output, because it can expose interpolated secrets. Preserve the security wrapper's environment guards; do not misrepresent a raw `docker compose` invocation as equivalent to the protected wrapper.
4. Validate sanitized expected service set (`configurator`, `backend`, `frontend`, `websocket`, `queue-short`, `queue-long`, `scheduler`, `db`, `redis-cache`, `redis-queue`), candidate Compose project identity `ccpc_prod_erpnext`, loopback-only frontend port, named `sites`/`db-data`/`logs` volumes, and no unexpected external/bind mounts or ambient Compose selectors. Any mismatch is a **stop**.
5. Only after a successful isolated render, obtain separate approval for on-host checkout preparation and any real credential creation, then for image build/containers. Before a restore or employee cutover, separately verify old-production consistent backup, isolated restore, schema, security, ledger, TLS, and rollback.

**Next implementation decision:** Complete focused code and acceptance review for app PR #33 and the inherited deployment guards; specify the exact app immutable release ref and a coherent `apps.json` / `config.sh` change on a fresh **review branch**. Do not merge PRs, create host secrets or run `compose up` based on this plan. The user approved GitHub-only preparation; business-policy changes, merges, persistent DEV actions and any production-impacting operation still require separate scoped approval.

## Owner-delegated next-step selection — 2026-11-06

**Decision:** Prioritize the **existing app PR #33 accounting authorization acceptance gate** ahead of image-source alignment, production image build or Compose execution. This is not a new authorization to change Company permissions, role assignments, DEVELOPMENT records, or any production resources.

**GitHub verified again on 2026-11-06:** app PR #33 remains OPEN/DRAFT at `1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc` against `feature/finance-mapping-lifecycle-2026-10-28`; current commit's combined status SUCCESS with `python-syntax`, `billing-controls-manual-approval` and `billing-controls-isolated-integration`. The reviewed `intercompany_billing_authority.py` explicitly denies Administrator/Guest, disabled users, Stockroom Personnel, absent literal role, and missing Company User Permission for either Company. It requires two different named Maker/Checker users. The controller also has row locking and protected billing state transitions, but no new live tests were executed here.

**Important unresolved distinction:** Application-level `require_billing_actor()` does not establish that ordinary **native Purchase Invoice Submit** permission is denied to every conflicted shared purchasing employee. GitHub's active handoff identifies this separation-of-duties overlap and persistent DEVELOPMENT named-Checker acceptance as unresolved. A CI pass is not proof that real site DocPerm/role memberships cannot bypass the workflow. Do not auto-assign the new roles, revoke other users, alter native PI DocPerm, or change business policy without a separate business/security decision.

**Chosen delivery sequence:** (1) Safely inspect protected DEVELOPMENT branch/status and obtain fresh post-Maker off-host backup under separate approval; (2) run targeted read-only role/Company scope/native PI Submit permission mapping and present the smallest effective policy choice; (3) perform explicitly authorized named Maker/Checker end-to-end acceptance on DEVELOPMENT, with rollback boundaries and test records documented; (4) only after resolution, create a coherent immutable app ref + `apps.json`/`config.sh` pin update on a fresh GitHub review branch, validate actual image and synthetic/isolated Compose render; (5) separately authorize non-live new-host instantiation, migration backup/restore, TLS, and finally cutover. Preserve existing old PRODUCTION unchanged throughout.

**Immediate external dependency:** A safeguarded DEVELOPMENT preflight and later actual acceptance require separate scoped authorization and operator-side access; the GitHub connector does not provide live SSH. No such host operation was performed by this documentation decision.

## Permanent data and release boundaries

- **Migration authority:** Owner approved the **existing old PRODUCTION site/database** on `ccpcerpserver` (internal site `ccpcerp.local`) as the starting source of business records. That approval selects a source; it does **not** permit live data export/transfer/restore or site migration.
- **No DEV substitution:** `development.localhost` and disposable integration sites are test environments, not business migration sources. Do not initialize new live business data independently and later overwrite or splice it into the old source.
- **Protect old operations:** Keep old production serving users unchanged until a separately authorized, backed-up, tested cutover. During final authorized cutover, fence old writes before final sync to prevent split-brain; verify transaction reconciliation and rollback plans.
- **Backup and recovery:** Future migration requires a complete, consistent **database, site configuration, public files, and private files** set; safe handling of secrets; verified integrity and isolated restore; version/schema compatibility; Company, COA, inventory, GL, users/roles, documents and attachments validation. The dedicated NAS share `ccpcerp-prod_backups` has historical SMB smoke-test evidence, **not** evidence of a successful four-artifact production backup or restore.
- **Production safety:** No restart, Compose `up/down`, database migration/restore, material changes, DNS/TLS cutover, backup deletion/retention change or Docker cleanup without separately scoped explicit approval. No accidental use of legacy deployment environment or secrets.

## Reviewed candidate design (not current running state)

- The pre-TLS profile is intended to publish frontend HTTP on **`127.0.0.1:8080` only**, with no MariaDB/Redis host ports; employee-facing `https://ccpcerp.com` on LAN TCP 443 requires a separate validated gateway, certificate trust, WebSocket/Host headers and firewall rules. Refer to [dedicated port profile](../04-operations/dedicated-production-port-profile.md) on the relevant branch.
- The external-credentials draft proposes a **0600**, user-owned, non-symlink env file outside Git checkout, in a **0700** owner-only directory, passed via `CCPC_DEDICATED_ENV_FILE`; never use checkout `.env` for dedicated database secrets. Do not print interpolated `docker compose config` in chat or logs.
- Candidate dedicated Compose project `ccpc_prod_erpnext` and volume names are **unapproved proposals**, not an observed deployed namespace; check selector/env guards and name collisions before any deployment.
- The dedicated backup-safety PR is still a draft. Signed release/source pin, backup identity, recovery, and approval controls require review and execution evidence rather than relying on offline mock tests alone.

## Approved work versus gated work

**Approved on 2026-11-06:** Prepare the dedicated **non-live release candidate**, including GitHub documentation, inspection/review of exact candidate source, and planning the separate credential provisioning and configuration validation. This approval **does not** cover provisioning actual passwords without a controlled procedure, changing SSH/Docker access rights, starting containers, old production backup execution, restoring or migrating any database, switching DNS/TLS traffic, merging draft PRs, or go-live.

**Immediate engineering next action:** Compare the stacked dedicated release candidate (PRs #27/#29/#30 plus later reviewed Compose/identity guards) against the available on-host checkout revisions, identify a single **source-pinned non-live configuration** and a no-secrets `docker compose config --quiet` validation plan. Do GitHub-only source review first; use a separately reviewed checkout or exact pinned commit rather than mutating the two existing checkouts. For any host-side change or real credential setup, present the exact command and seek the necessary scoped approval once.

**Release gates, in order:**

1. Freeze reviewed app + deployment source SHAs, Compose project/overrides, dependencies, and image provenance; resolve draft PR dependencies and unresolved security defects.
2. Independently validate effective Compose project/services/ports/volumes, no remote daemon and no namespace collision in a safe environment; keep 8080 loopback-only prior to HTTPS gateway.
3. Explicitly approve and provision segregated production credentials **outside Git**, with secret backup/rotation and failure recovery; never copy from DEVELOPMENT.
4. Approve and instantiate a **non-live** isolated stack only after volumes, image/version and rollback are reviewed. Validate service and data recovery behavior without live employee transactions.
5. Separately approve source production backup/export, transfer and isolated new-host restoration of the **old production** four-artifact backup. Prove files, data, schema, permissions and reconciled reports.
6. Verify independent NAS backup, restore rehearsal, TLS trust/redirect/WebSocket, LAN segmentation, role/SoD and accounting acceptance, maintenance-window and rollback/runbook.
7. Obtain explicit go-live/cutover approval; fence old writes, make final consistent copy, reconcile, switch access deliberately, observe and retain old recovery assets until separately approved retirement.

## Next-conversation quick start

**Do not repeat** Docker installation, empty-container diagnostics, home directory discovery, or Git checkout identification unless host state actually changed. Start by reading this record, the current workflow and the latest active handoff; compare GitHub draft PR heads/current reviews, then continue the immediate engineering next action above. If the host changes, record exact date, operator-run read-only evidence, affected host, result and new next action. Clearly label historical facts, new observations and unverified assumptions.

**No production deployment or migration occurred in this documentation milestone.**
