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

## November 12, 2026 — STAGE1_RUNTIME_CONFIRMED_AND_BACKUP_RUNNER_PREPARED_2026_11_12

**Operator Stage 1 result (NEW candidate):**

```text
FRAPPE_VERSION=16.33.1
BACKUP_GENERATOR_API=PASS
SCHEDULER_PAUSED=True
MUTE_EMAILS=True
BACKUP_ENCRYPTION=DISABLED
EXISTING_DEFAULT_BACKUP_ENTRY_COUNT=0
CCPC_NEW_BACKUP_RUNTIME_API_PREFLIGHT_COMPLETE
```

These results confirm exact Frappe version/API and backup safety settings on NEW A3 as of the operator test. It is not a full backup, restore, site-data write freeze or NAS mount confirmation.

**New owner-approved one-use runner, not yet transferred/executed:**

- GitHub code file `scripts/ccpc_new_a3_one_time_backup.py`, source Git blob **`46a12197e427e54a2f89c253e83cf4da398ea616`**, SHA-256 **`daa3f1d2ad906b0d3be1dc331bee9724d0d868ec386f3ab5fc13a7ee53f9101b`**, 20,167 bytes, code commit **`2675c69fa0903d2f7f56976c8d5c27c71f46cb21`**.
- Synthetic offline tests `tests/test_ccpc_new_a3_one_time_backup.py`, Git blob **`9b334466c1e26a93b621fb373da7f9d591d7f72c`**, test commit **`755b68bd1117539203ea66b683b2253e90ca6c10`**. Ran 7 Python unittest cases **all PASS**, `python3 -m py_compile` PASS, exact local Git blobs independently matched GitHub. The 7 tests are mock/file-fixture tests only, not real Docker, Frappe DB, SMB/NAS, host root, SQL restore or publication integration results.
- Script supports **`--preflight` read-only** and **`--execute` once**, not automatic jobs. It requires `sudo` from exact `ccpcadmin` on `ccpcerp-prod`; exact 12 expected running protected containers, pinned app image, candidate internal Docker network, healthy MariaDB, source persistent volumes, no published candidate port, source site and private directory, protected NAS root-only mountpoint/credential file, sufficient local free space and NAS *not* mounted. A failure halts with sanitized output.
- On one approved execution it acquires an exclusive lock, creates an unrepeatable root-only attempt marker and a new immutable run ID; runs Frappe **`BackupGenerator` directly** through the existing backend only, with existing scheduler paused and email muted, no config backup encryption, empty excludes/includes and four output artifacts generated under a new private site directory **outside the standard backup cleanup path**. It validates gzip/tar/JSON, exact four names and sizes, and copies them with exclusive destination creation to private NEW local staging with SHA-256 hashes. Temporary `mount.cifs` to exact dedicated NAS share is guarded by `findmnt` source/type/rw (no local fallback), verifies free space, publishes only a new run via no-replace `renameat2`, rechecks all digests, writes a `COMPLETED` marker last and cleanly unmounts *only* a mount created by this run.
- Backup may create new nonbusiness backup files on candidate site volume and root-only local/NAS directories; never delete an existing production file. A failed/partial run **must not be blindly retried or cleaned up**; inspect state and prepare a separately reviewed recovery continuation if necessary. The one-time marker deliberately blocks replay, even if failed after marker creation. This manual backup operation does not restart containers, change restart policies, enable scheduler/workers/mail, restore Nov05, touch OLD PROD/DEV/rehearsals, or approve employee go-live.
- The backup files contain confidential company data and unencrypted site config secrets (the ERPNext application `encrypt_backup` setting is off). Keep exact root-only local and Synology access controls; share only nonsecret PASS/STOP markers and the run ID, never dumps, site config, `.env` or passwords. SMB3.1.1 transport/recovery is still to be validated in the actual one-use run. A published four-artifact backup is not an independently restored rollback until an isolated restore drill passes.

### Next operator action — trusted Windows transfer + SHA-256, not execution

1. Obtain the exact reviewed `ccpc_new_a3_one_time_backup.py` bytes from ChatGPT's current-turn verified artifact or the GitHub file at the **pinned commit**, save to the trusted Windows `Downloads` directory. **Verify SHA-256 `daa3f1d2ad906b0d3be1dc331bee9724d0d868ec386f3ab5fc13a7ee53f9101b` before SCP**. Do not run the script locally on Windows.
2. Securely SCP to the pre-existing NEW `ccpcadmin` home under original filename (no SSH password/passphrase ever pasted here). On NEW, verify SHA-256 again, then stage as a new protected `root:root` mode0600 script without overwriting. Verify staged SHA-256 and run only `sudo python3 /root/ccpc_new_a3_one_time_backup.py --preflight` first; this is read-only and must return exact `CCPC_A3_BACKUP_HOST_DOCKER_NAS_LOCAL_PREFLIGHT_PASS` before any one-use `--execute`.
3. **Do not run `--execute` yet** until the preflight result is reviewed and an actual no-business-write window is established. Source archive Nov05 stays protected. Operator already approved one time, so no second approval for same bounded operation is needed if all guards PASS and no new risk emerges.
