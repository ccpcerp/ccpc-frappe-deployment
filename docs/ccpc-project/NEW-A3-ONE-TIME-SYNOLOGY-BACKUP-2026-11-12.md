# NEW A3 — one-time, manual, four-artifact candidate backup to Synology (2026-11-12)

**Status: OWNER APPROVED SCOPE; NO BACKUP EXECUTED; preflight and executable procedure pending.** This is a review document on a dedicated branch, based on the active HTTPS checkpoint PR #28. Never run old legacy `erpnext_backup.sh`, `deploy_release`, full Compose `up`, automatic backup schedules, image pulls, migrations, SQL restore, or rerun consumed A2/A3 scripts.

## Owner's exact approval and immutable boundaries

Owner replied **"Approved"** to: "preparing and manually executing this one-time NEW-only ERPNext backup to Synology under those safeguards". Approved source is the already running NEW candidate Docker namespace `ccpc_prod_erpnext`, Frappe site `ccpcerp.local`; target the **dedicated** Synology `//192.168.50.132/ccpcerp-prod_backups` only. Protect four artifacts: complete database SQL dump, site configuration, public files archive, and private files archive. Verify SHA-256, sizes, names, source identity and NAS readback. A one-time temporary authenticated mount and one unique NAS publication are within this scoped backup operation **after code and guards are reviewed**. This does not approve modifying original OLD PROD/DEV, either restored rehearsal, any live ERPNext document/ledger transaction, existing backup or source archive, application images, site/database records, firewall, systemd, Docker restart policy, worker/scheduler/mail or retention jobs. Preserve the owner-approved Nov 5 2026 four-artifact source backup and no newer source backup is required merely because of date. **No employee cutover.**

## Verified NEW-host preflight (operator evidence, not direct access)

- Host `ccpcerp-prod` at `192.168.50.186`; authorized shell `ccpcadmin`.
- Running `ccpc_prod_erpnext-frontend-1`, `-websocket-1`, `-backend-1`, `-redis-queue-1`, `-redis-cache-1` and `-db-1`. MariaDB reports `healthy`. Two protected Nov 7 rehearsal projects each contain three running support containers. Candidate has **blank Compose project/service labels**, so never rely on `--filter label=com.docker.compose.project=ccpc_prod_erpnext`.
- Frontend at `172.20.0.7:8080` is the exact systemd socket-proxyd target; Caddy responds on `192.168.50.186:443` and an authorized Windows account has successfully accessed Desk and viewed Company/Work Request/inventory/accounting history. This is limited owner-reported UI acceptance, not financial posting acceptance.
- Candidate persisted volumes: `ccpc_prod_erpnext_sites`, `ccpc_prod_erpnext_logs`, `ccpc_prod_erpnext_db-data` and `ccpc_prod_erpnext_redis-queue-data`. Backend/frontend/websocket share sites/logs volumes. Candidate DB has **two protected credential bind mounts** under `/run/secrets`; never print/copy credentials in terminal output or GitHub. All six containers have `RestartPolicy=no`; Caddy and loopback socket active but boot-disabled. Do not reboot.
- Root-only mountpoint `/mnt/ccpcerp-prod_backups` mode 0700, credentials `/etc/ccpc-prod-nas/credentials` mode 0600, both root:root; `findmnt` found `NAS_NOT_MOUNTED` at idle. `mount.cifs` available, Synology TCP445 reachable, NEW free host storage 733 GB. **This is not NAS login/share/current capacity validation or backup verification.**

## Crucial pinned Frappe source review — do not accidentally delete prior backups

Frappe public source checked through connected GitHub at **`frappe/frappe` tag `v16.33.1`**:
- `frappe/commands/site.py` Git blob `4b648dbae8afc3757419120c76455a9c4fee7e5d`: CLI `bench backup` delegates to `scheduled_backup`.
- `frappe/utils/backups.py` Git blob `5967c74ee69c403d8a1373dec5c66760df10faee`: `scheduled_backup -> new_backup -> delete_temp_backups()` may **remove older files** in the normal site private backups directory, *even when an explicit `--backup-path` is supplied*. Therefore the standard `bench --site ccpcerp.local backup --with-files --ignore-backup-conf --backup-path ...` is **not authorized blindly**, since this backup approval explicitly forbids deleting any pre-existing backup.
- A safer prospective implementation uses Frappe's `BackupGenerator` **directly** through a narrowly reviewed, fixed child script inside the exact running backend container. That avoids `new_backup` and its cleanup path while forcing a newly absent private output directory and a complete `force=True`, `ignore_files=False`, `ignore_conf=True` backup. It must check the **actual pinned runtime** against these assumptions and reject if method signatures, runtime flags or backup encryption vary. No implicit backup decryption, new key creation, scripts downloaded to the server at run time or shell interpolated credentials.
- Public Frappe backup CLI docs: https://docs.frappe.io/framework/user/en/bench/reference/backup . They specify `--backup-path` and `--with-files`, but not the internal cleanup caveat. GitHub source takes precedence here. **The source tag is a reviewed reference, NOT yet proof of the Frappe version inside `ccpcerp:v16.50.0`; Stage 1 checks actual installed runtime.**

## Stage 1 — NEW backend backup API and safety flags (READ-ONLY; next operator step)

Execute only from NEW `ccpcadmin@ccpcerp-prod`. This will inspect the Frappe API and the effective pause/email/encryption state; does **not** invoke a backup, create an output directory, print credentials, restart or publish any data.

```bash
(
set -euo pipefail
[[ "$(hostname -s)" == "ccpcerp-prod" && "$(id -un)" == "ccpcadmin" ]] || { echo 'STOP: wrong NEW host/account'; exit 1; }
backend="ccpc_prod_erpnext-backend-1"
[[ "$(sudo docker inspect -f '{{.State.Running}}' "$backend")" == "true" ]] || { echo 'STOP: NEW backend not running'; exit 1; }
[[ "$(sudo docker inspect -f '{{.Image}}' "$backend")" == "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8" ]] || { echo 'STOP: unexpected image digest'; exit 1; }
echo '=== NEW Frappe backup API and safety FLAGS (no secret values) ==='
sudo docker exec -i --user 1000:1000 --workdir /home/frappe/frappe-bench/sites "$backend" /home/frappe/frappe-bench/env/bin/python - <<'PY'
import inspect
from pathlib import Path
import frappe
from frappe.utils.backups import BackupGenerator
try:
    signature = inspect.signature(BackupGenerator)
    required = {"backup_path", "ignore_conf"}
    if not required.issubset(signature.parameters) or not hasattr(BackupGenerator, "get_backup"):
        raise RuntimeError("unexpected backup API")
    source = inspect.getsource(BackupGenerator.get_backup)
    if "delete_temp_backups" in source:
        raise RuntimeError("unexpected generator cleanup")
    frappe.init(site="ccpcerp.local", sites_path=".")
    frappe.connect()
    def enabled(v):
        return str(v or "").strip().lower() in {"1","true","yes","on"}
    print("FRAPPE_VERSION=" + str(frappe.__version__))
    print("BACKUP_GENERATOR_API=PASS")
    print("SCHEDULER_PAUSED=" + str(enabled(frappe.conf.get("pause_scheduler"))))
    print("MUTE_EMAILS=" + str(enabled(frappe.conf.get("mute_emails"))))
    print("BACKUP_ENCRYPTION=" + ("ENABLED" if enabled(frappe.get_system_settings("encrypt_backup")) else "DISABLED"))
    root = Path("ccpcerp.local/private/backups")
    print("EXISTING_DEFAULT_BACKUP_ENTRY_COUNT=" + str(len(list(root.iterdir())) if root.is_dir() else 0))
    frappe.destroy()
    print("CCPC_NEW_BACKUP_RUNTIME_API_PREFLIGHT_COMPLETE")
except Exception:
    print("STOP: API or site read-only probe failed")
    raise SystemExit(1)
PY
)
```

**Interpretation:** No execution approval is inferred from an unexpected flag or failed inspect. If runtime API unavailable, `pause_scheduler`/muted email false, or encryption enabled, STOP and review exactly; do not weaken guards or run `bench backup` as fallback. The entry count is diagnostic only; do not disclose backup filenames or delete them. A successful runtime inspection is not a backup.

## Planned Stage 2 (NOT YET PREPARED OR EXECUTED)

Implement a reviewed, one-use, **NEW A3-specific** operator script on this GitHub branch after Stage 1. This must:
1. Lock against concurrent candidate backup, reject wrong host/account/container/image/site/volume, verify existing six candidate + six protected rehearsal containers and source read consistency, detect any scheduler/workers/mail/integration activity inconsistent with an isolated pre-cutover backup, and require a no-business-update window.
2. Reserve one new root-only local scratch run and one **new, absent** output path in the candidate sites volume. Invoke installed `BackupGenerator` directly without `new_backup/delete_temp_backups`, complete DB+config+public+private files, and fail if different/missing/empty or unsafe files. Take SHA256/size/source metadata, verify output format, preserve any partials on error with no automatic retries.
3. Transfer only the four protected backup artifacts to a root-only local scratch space without exposing bytes or credentials in stdout. Check exact source/destination digest.
4. If NAS mount not already active, mount **only** `//192.168.50.132/ccpcerp-prod_backups` via `mount.cifs`/root-only credentials and SMB3.1.1, `nosuid,nodev,noexec`, exact `findmnt` source, `cifs` and `rw` guards before each write. **Never write to unmounted local fallback**. If mount already exists or mismatch, STOP (do not silently reuse).
5. Create one non-overwriting NAS `.partial-<run_id>` directory, copy and verify four file sizes/SHA256 on NAS, record a nonsecret manifest, publish to new final run directory safely, then make and verify a final `COMPLETED` marker. No retention/deletion. Unmount only the mount that this run created, report failed unmount plainly; preserve partials for review without cleanup.
6. Distinguish completed capture/copy from **independently verified restore**. A backup remains a candidate recovery artifact until a separate restore drill in a truly isolated new target with an explicit scoped approval, not in A3/OLD/DEV/two protected rehearsals.

## After Stage 2 (not part of this approval)

Review isolated restore, current OLD source/no-post-Nov05-write reconciliation, single-writer cutover/rollback, boot-safe persistent Caddy+socket/containers (currently disabled/no restart), employee public Root CA deployment, authorized staff network and negative WAN test. No automatic cron/systemd backup schedule or retention changes until separately approved.
