#!/usr/bin/env bash
# CCPC ERPNext: isolated DEVELOPMENT-only READ-ONLY stock/GL baseline and recovery audit.
# NEW artifact; preparation only. Never execute before separate scoped owner approval.
# No Frappe init, stock posting, SQL writes, Docker lifecycle or PRODUCTION access.
set -euo pipefail
umask 077
if [[ "$(id -u)" -eq 0 ]]; then
  printf '%s\n' 'STOP: run as the normal Ubuntu operator, not root' >&2
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  printf '%s\n' 'STOP: Docker CLI unavailable' >&2
  exit 1
fi
DEV_META="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Running}}' frappe_docker_devcontainer-frappe-1 2>/dev/null)" || {
  printf '%s\n' 'STOP: Expected DEVELOPMENT container unavailable' >&2
  exit 1
}
if [[ "$DEV_META" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  printf '%s\n' 'STOP: Unexpected DEVELOPMENT container/project identity' >&2
  exit 1
fi
docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 \
  bash -c 'cd /workspace/development/frappe-bench && umask 077 && PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -' <<'PYTHON'
import hashlib
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import MySQLdb

SITE = 'ccpc-integration2.localhost'
OTHER_SITE = 'development.localhost'
SLIP = 'WS-2026-00001'
ITEM = 'CCPC-INT-TEST-CONSUMABLE-001'
WAREHOUSE = 'Stores - TISS'
COMPANY = 'Integration Test Issuer'
REQUESTER_COMPANY = 'Integration Test Requester'
DEPARTMENT = 'Operations - TREQ'
A = 'ccpc-int-stockroom-a@example.test'
B = 'ccpc-int-stockroom-b@example.test'
REQUESTOR = 'ccpc-int-requestor@example.test'
RECEIVER = 'CCPC Fictional Integration Test Receiver'
FEATURE_SHA = '2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6'
BASE_SHA = '806fa23516490ec7beefcff03a1baa09d722120e'
FRAPPE_SHA = '988e54f3c4c291e2077a83809663f123731abe76'
ERPNEXT_SHA = '4048fb70e14d1843956fcdabb7c3cca75a1cbcdd'
BENCH = Path.cwd()
SITES = BENCH / 'sites'
SHARED = BENCH / 'apps/ccpcerp'
FEATURE = BENCH / '.ccpc-peer-issuance-tests-2f846a75'
SNAP_ROOT = SITES / SITE / 'private/ccpc-test-snapshots'
BASE_BACKUP = SITES / SITE / 'private/backups'
LATEST = SNAP_ROOT / 'post-verified-withdrawal-slip-pre-material-issue-20261015'
BACKUP_PREFIX = '20261015_085718-ccpc-integration2_localhost'

stage = 'initial source/config checks'
connected = False
transaction_started = False
rollback_ok = False
posting_exercised = False
entry_name = None
observed_exc = None
observed_trace = None
observed_stage = None

def stop(reason):
    raise RuntimeError('STOP: ' + reason)

def git(repo, *args):
    p = subprocess.run(['git', '-c', 'core.optionalLocks=false', '-C', str(repo), *args],
                       text=True, capture_output=True,
                       env={'PATH':'/usr/local/bin:/usr/bin:/bin', 'GIT_OPTIONAL_LOCKS':'0'})
    if p.returncode:
        stop('Protected Git inspection failed')
    return p.stdout.strip()

def verify_git():
    if git(SHARED, 'branch', '--show-current') != 'review/intercompany-approval-failure-tests':
        stop('Shared DEVELOPMENT branch changed')
    if git(SHARED, 'rev-parse', 'HEAD') != BASE_SHA or git(SHARED, 'status', '--porcelain') != '?? AGENTS.md':
        stop('Shared DEVELOPMENT commit or protected untracked file changed')
    if not FEATURE.is_dir() or FEATURE.is_symlink() or FEATURE.resolve() == SHARED.resolve():
        stop('Pinned detached source is missing or unsafe')
    if git(FEATURE, 'rev-parse', 'HEAD') != FEATURE_SHA or git(FEATURE, 'status', '--porcelain'):
        stop('Pinned feature source changed')
    if git(BENCH / 'apps/frappe', 'rev-parse', 'HEAD') != FRAPPE_SHA:
        stop('Installed Frappe differs from reviewed commit')
    if git(BENCH / 'apps/erpnext', 'rev-parse', 'HEAD') != ERPNEXT_SHA:
        stop('Installed ERPNext differs from reviewed commit')

def config(site):
    p = SITES / site / 'site_config.json'
    if not p.is_file() or p.is_symlink():
        stop('Site configuration unavailable')
    return json.loads(p.read_text())

def sha256(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def verify_snapshots():
    # Snapshot file contents never enter GitHub/logs; only fingerprints stay in memory.
    for d in (SNAP_ROOT, BASE_BACKUP, LATEST):
        if not d.is_dir() or d.is_symlink():
            stop('Expected protected snapshot directory missing/unsafe')
    dirs = sorted(d for d in SNAP_ROOT.iterdir() if d.is_dir())
    if len(dirs) != 11 or LATEST not in dirs or any(d.is_symlink() for d in dirs):
        stop('12th isolated snapshot count/destination changed')
    artifacts = []
    regex = r'\d{8}_\d{6}-ccpc-integration2_localhost-(?:database\.sql\.gz|files\.tar|private-files\.tar|site_config_backup\.json)'
    for folder in [BASE_BACKUP] + dirs:
        matches = sorted(p for p in folder.iterdir() if re.fullmatch(regex, p.name))
        if len(matches) != 4:
            stop('One protected backup set is incomplete')
        for p in matches:
            if not p.is_file() or p.is_symlink() or p.stat().st_size == 0:
                stop('Protected backup artifact missing/unsafe')
        if folder != BASE_BACKUP and len(list(folder.iterdir())) != 4:
            stop('Unexpected file in protected recovery folder')
        artifacts.extend(matches)
    if len(artifacts) != 48:
        stop('Expected 48 protected artifacts not found')
    for suffix in ('-database.sql.gz','-files.tar','-private-files.tar','-site_config_backup.json'):
        if not (LATEST / (BACKUP_PREFIX + suffix)).is_file():
            stop('Latest pre-issue backup missing')
    return {str(p): (p.stat().st_size, sha256(p)) for p in artifacts}

def verify_source_modules():
    for name, module in sys.modules.items():
        if name == 'ccpcerp' or name.startswith('ccpcerp.'):
            origin = getattr(module, '__file__', None)
            if origin and not Path(origin).resolve().is_relative_to(FEATURE.resolve()):
                stop('Mixed CCPC module loaded: ' + name)

def one(db, sql, params=()):
    rows = db.sql(sql, params)
    return rows[0] if rows else None

def count(db, table):
    return int(one(db, f'SELECT COUNT(*) FROM `{table}`')[0])

def money(v):
    return Decimal(str(v or 0))

def verify_db_baseline(db, user_checks=True):
    if one(db, 'SELECT DATABASE()')[0] != iso['db_name']:
        stop('Connected database is not isolated test database')
    for table, expected in (
        ('tabWithdrawal Slip',1), ('tabStock Entry',0),
        ('tabIntercompany Material Billing Batch',0),
        ('tabStock Ledger Entry',1), ('tabGL Entry',2), ('tabStock Reconciliation',1)
    ):
        if count(db, table) != expected:
            stop('Unexpected pre-issue business baseline: ' + table)
    row = one(db, '''SELECT owner, approving_supervisor, status, docstatus,
                           company, requesting_company, department, source_warehouse,
                           received_by, issued_by, issued_on
                    FROM `tabWithdrawal Slip` WHERE name=%s''', (SLIP,))
    if not row or row[:8] != (A,A,'Stockroom Review',0,COMPANY,REQUESTER_COMPANY,DEPARTMENT,WAREHOUSE) or any(row[8:]):
        stop('Previously approved Slip altered')
    rows = db.sql('''SELECT name, item_code, requested_qty, issue_qty, issued_qty, returned_qty
                     FROM `tabWithdrawal Slip Item` WHERE parent=%s AND parenttype='Withdrawal Slip' ''', (SLIP,))
    if len(rows) != 1 or rows[0][1] != ITEM or tuple(money(x) for x in rows[0][2:]) != (Decimal('1'),Decimal('1'),Decimal('0'),Decimal('0')):
        stop('Pre-issue Slip child quantities altered')
    binrow = one(db, '''SELECT actual_qty, stock_value, valuation_rate, reserved_qty
                        FROM `tabBin` WHERE item_code=%s AND warehouse=%s''',(ITEM,WAREHOUSE))
    if not binrow or tuple(money(x) for x in binrow[:3]) != (Decimal('10'),Decimal('1000'),Decimal('100')) or money(binrow[3]) != 0:
        stop('Pre-issue inventory Bin differs from snapshot')
    if user_checks:
        for user, roles in (
            (REQUESTOR, {'Withdrawal Slip Requestor'}),
            (A, {'Stockroom Personnel','Withdrawal Slip Requestor'}),
            (B, {'Stockroom Personnel','Withdrawal Slip Requestor'}),
        ):
            record = one(db, 'SELECT enabled, user_type FROM `tabUser` WHERE name=%s',(user,))
            if record != (1, 'System User'):
                stop('Test User modified or missing')
            present = {r[0] for r in db.sql("SELECT role FROM `tabHas Role` WHERE parent=%s AND parenttype='User'", (user,))}
            if present != roles:
                stop('Test User permissions changed')
        co = one(db, '''SELECT enable_perpetual_inventory, stock_adjustment_account,
                               default_inventory_account, cost_center
                        FROM `tabCompany` WHERE name=%s''',(COMPANY,))
        if not co or co != (1,'Stock Adjustment - TISS','Stock In Hand - TISS','Main - TISS'):
            stop('Expected test accounting defaults changed')
        for account, root, typ in (
            ('Stock Adjustment - TISS','Expense','Stock Adjustment'),
            ('Stock In Hand - TISS','Asset','Stock'),
        ):
            acc = one(db, '''SELECT company,root_type,account_type,is_group,disabled
                             FROM `tabAccount` WHERE name=%s''',(account,))
            if not acc or acc != (COMPANY,root,typ,0,0):
                stop('Test posting account changed')
        settings = dict(db.sql("SELECT field, value FROM `tabSingles` WHERE doctype='Stock Settings' AND field IN ('valuation_method','allow_negative_stock')"))
        if settings.get('valuation_method') != 'Moving Average' or settings.get('allow_negative_stock') != '0':
            stop('Stock valuation or negative stock settings changed')
    return rows[0][0]


class ReadOnlyDB:
    def __init__(self, cursor):
        self.cursor=cursor
    def sql(self, query, params=()):
        if not isinstance(query,str) or not re.match(r'^\s*SELECT\b',query,re.IGNORECASE):
            stop('Only parameterized SELECT statements allowed')
        if ';' in query or '--' in query or '/*' in query:
            stop('SQL comment/delimiter is not permitted')
        self.cursor.execute(query,params)
        return self.cursor.fetchall()

# This audit runs only a read-only transaction against the isolated DB.
conn=None
cur=None
stage='read-only source and database identity preflight'
try:
    verify_git()
    iso=config(SITE)
    shared=config(OTHER_SITE)
    common_path=SITES/'common_site_config.json'
    if not common_path.is_file() or common_path.is_symlink():
        stop('Bench-wide settings file missing or unsafe')
    common=json.loads(common_path.read_text())
    if not isinstance(common,dict) or not iso.get('db_name'):
        stop('Database configuration invalid or missing')
    if iso['db_name']==shared.get('db_name'):
        stop('Isolated DB name overlaps persistent DEVELOPMENT DB')
    if not isinstance(iso.get('db_password'),str) or not iso.get('db_password'):
        stop('Isolated site credential missing')
    db_host=iso.get('db_host') or common.get('db_host')
    db_port=int(iso.get('db_port') or common.get('db_port') or 3306)
    if db_host != 'mariadb' or db_port != 3306:
        stop('Refusing a connection outside documented DEVELOPMENT MariaDB service')
    db_name=iso['db_name']
    db_user=iso.get('db_user') or db_name
    if not isinstance(db_name,str) or not isinstance(db_user,str):
        stop('Missing or invalid isolated DB identity')
    config_before=(sha256(SITES/SITE/'site_config.json'),
                   sha256(SITES/OTHER_SITE/'site_config.json'),
                   sha256(common_path))
    print('PINNED DEV SOURCE AND TEST/SHARED SITE CONFIGS: VERIFIED',flush=True)

    stage='hash and verify all historical isolated recovery artifacts'
    backups_before=verify_snapshots()
    print('12 HISTORICAL RECOVERY SETS, 48 NONEMPTY FILES: SHA256 HASHED',flush=True)

    stage='read only SQL connection against isolated DEV MariaDB service'
    conn=MySQLdb.connect(host=db_host,port=db_port,user=db_user,
                         passwd=iso['db_password'],db=db_name,
                         charset='utf8mb4',connect_timeout=5)
    cur=conn.cursor()
    cur.execute('START TRANSACTION READ ONLY')
    ro=ReadOnlyDB(cur)
    if one(ro,'SELECT DATABASE()')[0] != db_name:
        stop('SQL-selected database differs from isolated site configuration')
    print('ACTUAL ISOLATED SQL DATABASE NAME: VERIFIED',flush=True)

    stage='compare unissued Slip, test users, Bin and ledger/accounting baseline'
    child=verify_db_baseline(ro)
    if not isinstance(child,str) or not child:
        stop('Missing expected single Slip child item')
    if one(ro,'SELECT COUNT(*) FROM `tabStock Entry` WHERE withdrawal_slip=%s',(SLIP,))[0]!=0:
        stop('Previously linked Stock Entry unexpectedly found')
    if count(ro,'tabEmail Queue') < 0:
        stop('Email queue count invalid')
    print('UNISSUED SLIP AND 10 NOS/PHP1000 STOCK BIN: VERIFIED',flush=True)
    print('0 STOCK ENTRIES, 1 HISTORICAL SLE, 2 HISTORICAL GL: VERIFIED',flush=True)
    print('TEST USERS, ROLES AND SYNTHETIC ACCOUNTING DEFAULTS: VERIFIED',flush=True)

    stage='end read-only SQL session; independently compare config and backup fingerprints'
    cur.close();cur=None
    conn.rollback()  # Close SELECT-only transaction; no SQL business writes.
    conn.close();conn=None
    after=(sha256(SITES/SITE/'site_config.json'),
           sha256(SITES/OTHER_SITE/'site_config.json'),
           sha256(common_path))
    if after!=config_before or verify_snapshots()!=backups_before:
        stop('Protected configuration or recovery artifact changed during audit')
    verify_git()
    print('48 RECOVERY ARTIFACT SHA256/SIZE FINGERPRINTS: STABLE IN THIS RUN',flush=True)
    print('PINNED SOURCE AND SITE CONFIGURATION: UNCHANGED',flush=True)
    print('NO PRODUCTION ACCESS, SQL WRITES, STOCK ISSUE OR DOCKER SERVICE CHANGE',flush=True)
    print('ISOLATED PRECOMMIT READ-ONLY BASELINE AUDIT: PASSED',flush=True)
except Exception:
    # Raw SQL/database exceptions may carry secrets; never print exception or traceback.
    print('ISOLATED PRECOMMIT READ-ONLY BASELINE AUDIT: STOPPED',flush=True)
    print('CHECK STAGE:',stage,flush=True)
    print('PRESERVE ALL STOCK, BACKUPS AND DEVELOPMENT/PRODUCTION STATE',flush=True)
    raise SystemExit(1)
finally:
    if cur is not None:
        try: cur.close()
        except Exception: pass
    if conn is not None:
        try:
            conn.rollback()
            conn.close()
        except Exception: pass
PYTHON
