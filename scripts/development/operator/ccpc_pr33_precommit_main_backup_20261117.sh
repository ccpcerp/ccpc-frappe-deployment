#!/usr/bin/env bash
# New one-shot MAIN DEVELOPMENT pre-PERSISTENT-draft-pair recovery snapshot (2026-11-17).
# Owner approved preparing for one committed MAIN DEV draft SI/PI pair.
# This creates a NEW local four-part backup; never overwrites older sets.
# No invoice creation, source checkout, migration, service restart or PRODUCTION.
set -euo pipefail
umask 077
site="${1:-}"
case "$site" in
  development.localhost) ;;
  *) echo "STOP: Only MAIN development.localhost is allowed." >&2; exit 1 ;;
esac
if [[ "$(hostname -s)" != "ccpcerpserver" || "$(id -un)" != "gani" ]]; then
  echo "STOP: original DEV host/operator required" >&2; exit 1
fi
if [[ "${CCPC_APPROVE_PR33_MAIN_FRESH_BACKUP:-}" != "YES" ]]; then
  echo "STOP: fresh-backup execution gate not enabled" >&2; exit 1
fi
# Independent pre-existing off-host recovery copy must remain available.
# This only checks the exact Synology mount and previously published Nov 4 set;
# it does not write, overwrite, or delete anything on the NAS.
if [[ "$(id -u)" -eq 0 ]]; then
  echo "STOP: run as normal operator, not root" >&2
  exit 1
fi
actual_nas="$(findmnt -rn -M /mnt/erpnext_backups -o SOURCE,FSTYPE)"
if [[ "$actual_nas" != "//192.168.50.132/erpnext_backups cifs" ]]; then
  echo "STOP: NAS mount does not match protected Synology share" >&2
  exit 1
fi
if [[ ! -d /mnt/erpnext_backups/ccpc-development-pr33-20261104T010408Z-82316b860fe951ad ]]; then
  echo "STOP: previous off-host DEV recovery set missing" >&2
  exit 1
fi
echo "PREVIOUS_OFF_HOST_DEV_RECOVERY: PRESENT"
# Only named DEV Compose container; read identity before creating snapshot.
DEV=frappe_docker_devcontainer-frappe-1
sudo -v
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == "true" ]] || {
  echo "STOP: DEV container not running" >&2; exit 1;
}
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == "frappe_docker_devcontainer" ]] || {
  echo "STOP: DEV Docker Compose identity mismatch" >&2; exit 1;
}
# One-time marker is intentionally never removed, even on an error.
MARKER="$HOME/.ccpc-pr33-main-precommit-fresh-backup-once-20261117"
mkdir "$MARKER" || { echo "STOP: fresh backup already attempted; no automatic retry" >&2; exit 1; }
# Backup runs only inside the named DEVELOPMENT Frappe container, as frappe.
sudo -n docker exec -i --user frappe "$DEV" bash -lc '
set -euo pipefail
cd /workspace/development/frappe-bench/sites
FRAPPE_STREAM_LOGGING=1 /workspace/development/frappe-bench/env/bin/python - "$1"
' _ "$site" <<'CCPC_BACKUP_PY'
"""One-site, protected DEVELOPMENT snapshot; supplied on stdin, not installed in Frappe."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys
import tarfile
from datetime import datetime, timezone

os.umask(0o077)
BENCH = Path('/workspace/development/frappe-bench')
ROOT = BENCH / '.ccpc-pr32-snapshots'
APP = BENCH / 'apps' / 'ccpcerp'
EXPECTED_SHA = '25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87'
SITES = {'development.localhost'}
HISTORIC = (
    'ccpc-integration2.localhost-20261104T000538Z-9c1ee27e4166',
    'development.localhost-20261104T005618Z-060922e4189d',
)

def must(condition, code):
    if not condition:
        raise RuntimeError(code)

def git(*args):
    result = subprocess.run(['git', '-C', str(APP), *args], capture_output=True, text=True, timeout=30, check=True)
    return result.stdout.strip()

def checksum(path):
    h = hashlib.sha256()
    with path.open('rb') as fh:
        while block := fh.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()

def validate(name, path):
    must(path.parent == stage and not path.is_symlink() and path.is_file(), 'BAD_BACKUP_FILE')
    must(path.stat().st_size > 0, 'EMPTY_BACKUP_FILE')
    os.chmod(path, 0o600)
    if name == 'database':
        must(path.name.endswith('.sql.gz'), 'WRONG_SQL_FORMAT')
        with gzip.open(path, 'rb') as fh:
            must(bool(fh.read(1)), 'EMPTY_SQL_STREAM')
            while fh.read(1024 * 1024):
                pass
    elif name == 'config':
        must(path.name.endswith('.json'), 'WRONG_CONFIG_FORMAT')
        with path.open('r', encoding='utf8') as fh:
            must(isinstance(json.load(fh), dict), 'BAD_CONFIG_JSON')
    else:
        must(path.name.endswith('.tar'), 'WRONG_FILES_FORMAT')
        with tarfile.open(path, mode='r:') as archive:
            for member in archive:
                if member.isfile():
                    source = archive.extractfile(member)
                    must(source is not None, 'BAD_TAR_ENTRY')
                    with source:
                        while source.read(1024 * 1024):
                            pass
    return checksum(path)

stage = None
try:
    must(len(sys.argv) == 2 and sys.argv[1] in SITES, 'UNEXPECTED_SITE')
    site = sys.argv[1]
    must(Path.cwd() == BENCH / 'sites', 'WRONG_DIRECTORY')
    must((BENCH / 'sites' / site).is_dir() and not (BENCH / 'sites' / site).is_symlink(), 'SITE_MISSING')
    must(git('rev-parse', 'HEAD') == EXPECTED_SHA, 'APP_SHA_CHANGED')
    must(git('rev-parse', '--abbrev-ref', 'HEAD') == 'HEAD', 'NOT_DETACHED')
    must(git('status', '--porcelain=v1', '--untracked-files=all') == '?? AGENTS.md', 'WORKTREE_CHANGED')
    protected = APP / 'AGENTS.md'
    must(protected.is_file() and not protected.is_symlink(), 'PROTECTED_AGENTS_FILE_CHANGED')
    must(git('hash-object', 'ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py')
         == 'a9a6e609759e77948d40d31bdbd342f727b208a9', 'BILLING_CONTROLLER_BLOB_CHANGED')
    must(git('hash-object', 'ccpcerp/ccpc_erp/intercompany_billing_authority.py')
         == '8de2d6ba2aa0f8995b727157491e236d2a0a8ae2', 'BILLING_AUTHORITY_BLOB_CHANGED')
    must(git('ls-tree', '-r', '--name-only', 'HEAD', '--', 'AGENTS.md') == '', 'AGENTS_TRACKED_STOP')
    must(ROOT.is_dir() and not ROOT.is_symlink(), 'SNAPSHOT_ROOT_MISSING')
    must(ROOT.stat().st_uid == os.getuid(), 'SNAPSHOT_OWNER_MISMATCH')
    must(stat.S_IMODE(ROOT.stat().st_mode) & 0o077 == 0, 'SNAPSHOT_ROOT_NOT_PRIVATE')
    for existing in HISTORIC:
        p = ROOT / existing
        must(p.is_dir() and not p.is_symlink(), 'HISTORIC_SNAPSHOT_MISSING')
        must((p / 'SHA256SUMS').is_file() and not (p / 'SHA256SUMS').is_symlink(), 'HISTORIC_MANIFEST_MISSING')
        manifest_lines = (p / 'SHA256SUMS').read_text(encoding='utf8').splitlines()
        must(len(manifest_lines) == 4, 'HISTORIC_MANIFEST_BAD_COUNT')
        historic_names = set()
        for line in manifest_lines:
            digest, marker, name = line.partition('  ')
            must(marker and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'HISTORIC_MANIFEST_BAD_HASH')
            must(name and Path(name).name == name and name not in historic_names, 'HISTORIC_MANIFEST_BAD_NAME')
            historic_names.add(name)
            old_file = p / name
            must(old_file.is_file() and not old_file.is_symlink() and old_file.stat().st_size > 0, 'HISTORIC_FILE_MISSING')
            must(checksum(old_file) == digest, 'HISTORIC_CHECKSUM_FAILED')
    available = os.statvfs(ROOT)
    must(available.f_bavail * available.f_frsize >= 1024**3, 'INSUFFICIENT_SPACE')
    print('DEVELOPMENT SNAPSHOT PRECHECK: PASS', flush=True)

    import frappe
    from frappe.utils.backups import BackupGenerator
    from frappe.utils import cint, getdate, today
    frappe.init(site=site, sites_path='.')
    try:
        frappe.connect()
        must(frappe.local.site == 'development.localhost', 'WRONG_SITE_CONNECTED')
        must(not cint(frappe.get_system_settings('encrypt_backup')), 'BACKUP_ENCRYPTION_CONFIGURED_STOP')
        batches = frappe.db.sql("""
            SELECT name, status, docstatus, period_end,
                   finalized_on, finalized_by, approved_on, approved_by,
                   IFNULL(sales_invoice, '') AS si,
                   IFNULL(purchase_invoice, '') AS pi
            FROM `tabIntercompany Material Billing Batch`
            WHERE issuing_company=%s AND requesting_company=%s
        """, ('Cagayan Corn Products Corporation', 'Ricor Mills Corporation'), as_dict=True)
        must(len(batches) == 1, 'BILLING_BATCH_COUNT_CHANGED')
        batch = batches[0]
        must(batch.docstatus == 0 and batch.status == 'Under Review'
             and not batch.si and not batch.pi and not batch.approved_by
             and not batch.approved_on and bool(batch.finalized_by)
             and bool(batch.finalized_on) and batch.period_end
             and getdate(today()) > getdate(batch.period_end),
             'UNDER_REVIEW_BILLING_STATE_CHANGED')
        must(frappe.db.count('Intercompany Material Billing Item', {'parent': batch.name}) == 1,
             'SAVED_BATCH_ITEM_COUNT_CHANGED')
        remarks = 'Intercompany material billing batch ' + batch.name
        must(frappe.db.count('Sales Invoice', {'remarks': remarks}) == 0
             and frappe.db.count('Purchase Invoice', {'remarks': remarks}) == 0,
             'RELATED_INVOICE_ALREADY_EXISTS')
        print('MAIN_UNDER_REVIEW_BATCH_AND_ZERO_DRAFT_PAIRS: PASS', flush=True)
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        token = secrets.token_hex(6)
        stage = ROOT / ('.partial-' + site + '-' + timestamp + '-' + token)
        dest = ROOT / (site + '-' + timestamp + '-' + token)
        must(not stage.exists() and not dest.exists(), 'BACKUP_DESTINATION_EXISTS')
        stage.mkdir(mode=0o700)
        must(stat.S_IMODE(stage.stat().st_mode) == 0o700, 'BACKUP_DESTINATION_NOT_PRIVATE')
        bg = BackupGenerator(
            frappe.conf.db_name, frappe.conf.db_user, frappe.conf.db_password,
            db_socket=frappe.conf.db_socket, db_host=frappe.conf.db_host,
            db_port=frappe.conf.db_port, db_type=frappe.conf.db_type,
            backup_path=str(stage), ignore_conf=True, compress_files=False,
            verbose=False,
        )
        bg.get_backup(force=True, ignore_files=False)
        paths = {
            'database': Path(bg.backup_path_db),
            'config': Path(bg.backup_path_conf),
            'public': Path(bg.backup_path_files),
            'private': Path(bg.backup_path_private_files),
        }
        must(len({str(x) for x in paths.values()}) == 4, 'BACKUP_PATH_COLLISION')
        must({x.name for x in stage.iterdir()} == {p.name for p in paths.values()}, 'UNEXPECTED_BACKUP_CONTENTS')
        hashes = {name: validate(name, p) for name, p in paths.items()}
        manifest = stage / 'SHA256SUMS'
        with manifest.open('x', encoding='utf8') as fh:
            for name in ('database', 'config', 'public', 'private'):
                fh.write(f'{hashes[name]}  {paths[name].name}\n')
        os.chmod(manifest, 0o600)
        must(len(tuple(stage.iterdir())) == 5, 'MANIFEST_FILE_COUNT_MISMATCH')
        stage.rename(dest)
        # Recheck the original financial state at the end of the backup
        # without refreshing/finalizing or changing any business document.
        persisted = frappe.db.get_value('Intercompany Material Billing Batch', batch.name,
                       ['status', 'sales_invoice', 'purchase_invoice', 'approved_by', 'approved_on'],
                       as_dict=True)
        must(persisted and persisted.status == 'Under Review'
             and not persisted.sales_invoice and not persisted.purchase_invoice
             and not persisted.approved_by and not persisted.approved_on,
             'BILLING_STATE_CHANGED_DURING_BACKUP')
        print('DATABASE BACKUP: PASS')
        print('SITE CONFIG BACKUP: PASS')
        print('PUBLIC FILES BACKUP: PASS')
        print('PRIVATE FILES BACKUP: PASS')
        print('SHA256 MANIFEST: PASS')
        print('BACKUP DIRECTORY: ' + str(dest))
        print('FRESH_PRECOMMIT_MAIN_DEV_BACKUP: PASS')
        print('NO_INVOICE_ACTIONS_OR_COMMIT: PASS')
    finally:
        frappe.destroy()
except Exception:
    print('STOP: Backup was not verified. Do not retry automatically or modify existing snapshots.', file=sys.stderr)
    if stage is not None and stage.exists():
        print('STOP: Private partial directory retained for manual review.', file=sys.stderr)
    raise SystemExit(1)
CCPC_BACKUP_PY
