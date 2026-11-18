# Phase 1 — authorized two-site DEVELOPMENT fresh recovery-point procedure

**2026-11-18 Asia/Manila.** Owner explicitly approved creation of NEW four-component backups and verified Synology NAS copies for **both** `development.localhost` and `ccpc-integration2.localhost`. This is a **backup-only authorization**. No source checkout/pull, migration, services/scheduler restart, site business write, database restore, older backup deletion, agent automation or PRODUCTION access is approved.

## Authoritative operator script and validation

- GitHub operator script on `review/pr33-dev-acceptance-2026-11-16`: [`scripts/development/operator/ccpc_phase1_two_site_backup_20261118.sh`](../../scripts/development/operator/ccpc_phase1_two_site_backup_20261118.sh).
- Commit creating that script: `d7e4bca43ac7e96d27a91283ba5dec55c800c98c`; verified Git blob `af016cf740fe11af96668214accbfea8b6e20689`.
- Independent local file `sha256sum` expected exact: **`a906876dc05eed65765c8b8cee0228062695a4fb7ce87116cd9e600820a54d00`**. Confirm this before execution and STOP on mismatch.
- Static tests of identical Git blob/local script: Bash `bash -n`, AST parse of host Python and embedded container Python all PASS; simulated four-component SHA256 manifest recognized (4/4 PASS), altered component rejected, synthetic gzip+JSON+public TAR+private TAR format checks PASS, malformed gzip rejected. **These are local mock/static checks only**, not actual Frappe/DB/NAS execution.
- The script revalidates `ccpcerpserver` and operator `gani`, named running DEV container and Compose project, live app HEAD exactly PR33 `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` (DETACHED), worktree only protected untracked `AGENTS.md`, actual `ccpcerp` Python import path, named two DEV site configs, the previous private snapshot root, nonencrypted backup format, local free space, and exact `//192.168.50.132/erpnext_backups cifs` mount. It deliberately excludes broken `ccpc-integration.localhost` from backup and never connects to PROD.
- For each valid site, Frappe `BackupGenerator` creates a **new unique** private local snapshot (database SQL gzip, site_config JSON, public TAR, private TAR) in the existing `.ccpc-pr32-snapshots` root; files are format-scanned and SHA256-manifested. It then independently rehashes both local sets and writes a **new unique** `ccpc-development-phase1-two-site-preswitch-...` Synology directory with both site sets + per-site and global checksum manifests. Every copied backup hash is reverified before final directory rename. No existing backup is overwritten or removed, and there is no automatic retry on failure.
- Backup writes can take place while DEV serves requests; this is **not** a multi-site atomic, quiesced snapshot. SQL/filestore restore consistency and actual site recoverability remain unverified until a separately approved isolated restore rehearsal.

## Operator transfer and execution

Copy the reviewed script from GitHub or the exact SHA256-verified downloadable file to the original server as `/home/gani/ccpc_phase1_two_site_backup_20261118.sh`. For example, from an ordinary local laptop terminal with the downloaded file in `~/Downloads`:

```bash
scp ~/Downloads/ccpc_phase1_two_site_backup_20261118.sh gani@ccpcerpserver:/home/gani/
```

Then on **`gani@ccpcerpserver`**:

```bash
bash <<'SH'
set -euo pipefail
script=/home/gani/ccpc_phase1_two_site_backup_20261118.sh
printf '%s  %s\n' \
  'a906876dc05eed65765c8b8cee0228062695a4fb7ce87116cd9e600820a54d00' \
  "$script" | sha256sum -c -
CCPC_APPROVE_PHASE1_TWO_SITE_BACKUP=YES bash "$script"
SH
echo "BACKUP EXIT CODE: $?"
```

The script may prompt for the operator's own `sudo` password. Do **not** paste any password into chat. Do not attempt to run its `sudo docker exec` blocks separately or turn off guards if a STOP appears.

## Expected successful terminal markers (not reported yet)

```text
DEV CONTAINER/NAS PRECHECK: PASS
CREATING TWO LOCAL DEV BACKUPS (NO SITE MIGRATION)
LOCAL DEV SNAPSHOTS: 2/2, FOUR FILES EACH, SHA256 PASS
COPYING BOTH SNAPSHOTS TO VERIFIED NAS
NAS DEV SNAPSHOTS: 2/2, FOUR FILES EACH, SHA256 PASS
LOCAL/NAS BACKUPS: MATCH
MAIN DEV SNAPSHOT: development.localhost-<new-UTC-timestamp>-<token>
INTEGRATION2 DEV SNAPSHOT: ccpc-integration2.localhost-<new-UTC-timestamp>-<token>
FINAL NAS BACKUP DIRECTORY: /mnt/erpnext_backups/ccpc-development-phase1-two-site-preswitch-...
PHASE1_TWO_SITE_OFFHOST_BACKUP: PASS
RESTORE TEST: NOT PERFORMED
SOURCE SWITCH / MIGRATION / RESTART: NOT PERFORMED
BACKUP EXIT CODE: 0
```

**If there is any `STOP:` or nonzero exit code**, do not blindly retry, rename, chmod, delete files, or bypass snapshot guards. New partial directories may have been left for deliberate recovery inspection. Send only the nonsecret PASS/STOP/status lines and snapshot directory names back to ChatGPT. **Never paste or upload** `site_config_backup.json`, SQL archives, TAR contents, private business data, passwords, or private NAS ACL/credentials.

After both copies are verified, separately decide whether to perform an isolated restore rehearsal and a shared-bench, two-site-aware maintenance window. A successful backup alone is **not** authorization to activate the Phase 1 release.


## 2026-11-19 — Operator-reported two-site backup completed, SHA256 checks passed

**Evidence source:** On 2026-11-19 (Asia/Manila), owner pasted terminal output from running the approved, SHA256-preverified `ccpc_phase1_two_site_backup_20261118.sh` on `gani@ccpcerpserver`. The exact emitted markers were:

```text
DEV CONTAINER/NAS PRECHECK: PASS
CREATING TWO LOCAL DEV BACKUPS (NO SITE MIGRATION)
LOCAL DEV SNAPSHOTS: 2/2, FOUR FILES EACH, SHA256 PASS
COPYING BOTH SNAPSHOTS TO VERIFIED NAS
NAS DEV SNAPSHOTS: 2/2, FOUR FILES EACH, SHA256 PASS
LOCAL/NAS BACKUPS: MATCH
MAIN DEV SNAPSHOT: development.localhost-20261118T233442Z-8db803832468
INTEGRATION2 DEV SNAPSHOT: ccpc-integration2.localhost-20261118T233442Z-8db803832468
FINAL NAS BACKUP DIRECTORY: /mnt/erpnext_backups/ccpc-development-phase1-two-site-preswitch-20261118T233444Z-35c00130d53b457e
PHASE1_TWO_SITE_OFFHOST_BACKUP: PASS
RESTORE TEST: NOT PERFORMED
SOURCE SWITCH / MIGRATION / RESTART: NOT PERFORMED
BACKUP EXIT CODE: 0
```

**Assessment:** Verified local/remote checksums are **script-reported and operator-provided** (8 expected backup components: 2 sites × database SQL gzip, configuration JSON, public TAR, private TAR; per-site and NAS SHA256 manifests). ChatGPT did **not** independently access/read backup bytes, inspect MariaDB content, or run a restore. These backups are asynchronous sequential site copies, not a coordinated atomic two-site snapshot. Restore viability remains **NOT TESTED**. The Nov17 MAIN local/NAS checkpoint remains a separate historically verified recovery point.

**Current approved scope is exhausted:** No Phase1 app checkout/pull, Frappe migration, site metadata/Finance data change, Docker restart, NAS/old backup cleanup, persistent test fixtures, restore, or PRODUCTION operation was executed or is authorized by the backup approval. A new, separate DEV-only approval is required before any recovery rehearsal using a new isolated test DB/site or any source switch. Next prefer a backed-up DEV-only isolation/restore strategy, then a two-site-aware maintenance/cutover plan that avoids replacing protected `AGENTS.md` and does not import PR33 unreleased billing paths.
