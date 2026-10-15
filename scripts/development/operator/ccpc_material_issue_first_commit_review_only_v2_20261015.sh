#!/usr/bin/env bash
set -euo pipefail
# REVIEW-ONLY V2: Unconditionally INERT even if the old arming variable is set.
# Future removal of this STOP requires a new owner authorization and full review.
printf '%s\n' 'NO-GO: Review-only v2; Docker/SQL execution is deliberately disabled.' >&2
exit 1

# NEW CANDIDATE, PREPARATION ONLY: first committed synthetic one-unit Material Issue.
# NOT AUTHORIZED FOR EXECUTION. Never run the old rollback-only diagnostic again.
# Only exact, fresh owner approval for a SINGLE isolated site DB commit may arm this.
# NO AUTOMATIC RETRIES; a commit attempted with uncertain result requires investigation.
# DEVELOPMENT isolated site only. PRODUCTION and shared checkout protected.
# GitHub-reviewed commit and file SHA256 must be externally verified before use.

umask 077
if [[ "${CCPC_FIRST_ISSUE_EXECUTION_APPROVED:-}" != 'ccpc-integration2-one-unit-stock-gl-commit' ]]; then
  printf '%s\n' 'NOT AUTHORIZED: Candidate script is inert without separate per-run approval.' >&2
  exit 1
fi
if [[ "$(id -u)" -eq 0 || ! -d "$HOME/ccpc-reviewed-scripts" ||
      -L "$HOME/ccpc-reviewed-scripts" || ! -O "$HOME/ccpc-reviewed-scripts" ]]; then
  printf '%s\n' 'STOP: Run only as non-root Ubuntu operator with private staged files.' >&2
  exit 1
fi
ATTEMPT_DIR="$HOME/ccpc-reviewed-scripts/.ccpc-material-issue-first-commit-one-shot-20261015"
if ! mkdir -m 700 -- "$ATTEMPT_DIR"; then
  printf '%s\n' 'STOP: One-shot marker already exists or could not be created. Never retry.' >&2
  exit 1
fi
# Keep the marker even after errors; no automated cleanup.
trap 'printf "%s\n" "STOP: INTERRUPTED / COMMIT OUTCOME UNKNOWN. NEVER AUTO-RETRY." >&2' INT TERM HUP
DEV_META="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Running}}' frappe_docker_devcontainer-frappe-1 2>/dev/null)" || {
  printf '%s\n' 'STOP: expected DEVELOPMENT container unavailable' >&2; exit 1
}
if [[ "$DEV_META" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  printf '%s\n' 'STOP: unexpected DEVELOPMENT container/project identity' >&2; exit 1
fi

docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 \
  bash -c 'cd /workspace/development/frappe-bench && umask 077 && FRAPPE_STREAM_LOGGING=1 PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -' <<'PY'
import hashlib
import importlib
import json
import re
import subprocess
import sys
from decimal import Decimal
import traceback
from pathlib import Path
from unittest.mock import patch

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
EXPECTED_DEV_DB_HOST = 'mariadb'
EXPECTED_DEV_DB_PORT = 3306
BENCH = Path.cwd()
SITES = BENCH / 'sites'
SHARED = BENCH / 'apps/ccpcerp'
FEATURE = BENCH / '.ccpc-peer-issuance-tests-2f846a75'
SNAP_ROOT = SITES / SITE / 'private/ccpc-test-snapshots'
BASE_BACKUP = SITES / SITE / 'private/backups'
LATEST = SNAP_ROOT / 'post-verified-withdrawal-slip-pre-material-issue-20261015'
BACKUP_PREFIX = '20261015_085718-ccpc-integration2_localhost'

stage = 'initial guarded first committed-issue preflight'
connected = False
transaction_started = False
rollback_ok = False
commit_attempted = False
commit_returned = False
posting_exercised = False
entry_name = None
observed_exc = None
observed_trace = None
observed_stage = None

def stop(reason):
    raise RuntimeError('STOP: ' + reason)

def git(repo, *args):
    p = subprocess.run(['git', '-C', str(repo), *args], text=True, capture_output=True)
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

def verify_snapshots(*, metadata_only=False):
    # Snapshot file contents are never read into logs; only fingerprints stay in memory.
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
    if metadata_only:
        # Low-cost fstat metadata gate inside SQL lock, NOT cryptographic proof.
        return {str(p): (p.stat().st_size, p.stat().st_mtime_ns,
                         p.stat().st_ctime_ns, p.stat().st_dev, p.stat().st_ino)
                for p in artifacts}
    return {str(p): sha256(p) for p in artifacts}

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

def verify_issued_state(db, stock_entry_name, child_name, email_count):
    if count(db,'tabWithdrawal Slip') != 1 or count(db,'tabStock Entry') != 1 or count(db,'tabIntercompany Material Billing Batch') != 0:
        stop('Unexpected issue/Slip/billing record count')
    if count(db,'tabStock Ledger Entry') != 2 or count(db,'tabGL Entry') != 4:
        stop('Unexpected stock or GL row count after one-unit issue')
    if count(db,'tabStock Reconciliation') != 1:
        stop('Opening Stock Reconciliation changed')
    header = one(db, '''SELECT name, owner, docstatus, company, purpose,
                               withdrawal_slip, withdrawal_slip_issued_by
                        FROM `tabStock Entry` WHERE name=%s''',(stock_entry_name,))
    if not header or header != (stock_entry_name,B,1,COMPANY,'Material Issue',SLIP,B):
        stop('Posted Stock Entry header/provenance differs')
    details = db.sql('''SELECT item_code, qty, transfer_qty, s_warehouse,
                               t_warehouse, withdrawal_slip_item,
                               expense_account, cost_center
                        FROM `tabStock Entry Detail` WHERE parent=%s AND parenttype='Stock Entry' ''',(stock_entry_name,))
    if len(details) != 1 or details[0][0] != ITEM or money(details[0][1]) != 1 or money(details[0][2]) != 1 or details[0][3] != WAREHOUSE or details[0][4] not in (None,'') or details[0][5] != child_name:
        stop('Posted Stock Entry item/qty/provenance differs')
    if details[0][6:] != ('Stock Adjustment - TISS','Main - TISS'):
        stop('Posted Stock Entry expense/cost center not as expected')
    parent = one(db,'''SELECT status,docstatus,received_by,issued_by,approving_supervisor,owner
                      FROM `tabWithdrawal Slip` WHERE name=%s''',(SLIP,))
    if not parent or parent != ('Fully Issued',0,RECEIVER,B,A,A):
        stop('Slip status or authorization identity not updated correctly')
    child = one(db,'''SELECT issued_qty, shortage_qty, returned_qty, net_used_qty
                     FROM `tabWithdrawal Slip Item` WHERE name=%s''',(child_name,))
    if not child or tuple(money(x) for x in child) != (Decimal('1'),Decimal('0'),Decimal('0'),Decimal('1')):
        stop('Slip issue tracking totals incorrect')
    binrow = one(db,'''SELECT actual_qty,stock_value,valuation_rate,reserved_qty
                      FROM `tabBin` WHERE item_code=%s AND warehouse=%s''',(ITEM,WAREHOUSE))
    if not binrow or money(binrow[0]) != 9 or money(binrow[3]) != 0 or abs(money(binrow[1])-Decimal('900')) > Decimal('0.05'):
        stop('Inventory stock/valuation after issue differs from 1-unit forecast')
    sle = db.sql('''SELECT actual_qty,stock_value_difference,warehouse,item_code,qty_after_transaction
                    FROM `tabStock Ledger Entry`
                    WHERE voucher_type='Stock Entry' AND voucher_no=%s''',(stock_entry_name,))
    if len(sle) != 1 or money(sle[0][0]) != -1 or abs(money(sle[0][1])+Decimal('100')) > Decimal('0.05') or sle[0][2:4] != (WAREHOUSE,ITEM) or money(sle[0][4]) != 9:
        stop('Stock Ledger Entry does not reflect -1 unit / ~PHP100')
    gl = db.sql('''SELECT account,debit,credit,cost_center
                   FROM `tabGL Entry` WHERE voucher_type='Stock Entry' AND voucher_no=%s''',(stock_entry_name,))
    if len(gl) != 2:
        stop('Expected exactly 2 GL rows for synthetic issue')
    by_account = {name:(money(debit),money(credit),center) for name,debit,credit,center in gl}
    if set(by_account) != {'Stock Adjustment - TISS','Stock In Hand - TISS'}:
        stop('Actual GL accounts differ from verified Material Issue defaults')
    exp=by_account['Stock Adjustment - TISS']
    asset=by_account['Stock In Hand - TISS']
    if abs(exp[0]-Decimal('100'))>Decimal('0.05') or exp[1]!=0 or exp[2]!='Main - TISS':
        stop('Stock Adjustment debit/cost center unexpected')
    if asset[0]!=0 or abs(asset[1]-Decimal('100'))>Decimal('0.05'):
        stop('Stock In Hand credit unexpected')
    if abs(sum(x[0] for x in by_account.values())-sum(x[1] for x in by_account.values()))>Decimal('0.01'):
        stop('Material Issue GL not balanced')
    if count(db,'tabEmail Queue') != email_count:
        stop('Unexpected email queued during stock posting')
    return (binrow[0],binrow[1],sle[0][1])


def _safe_frames(tb):
    """Only module-relative path/function/line from supported checked-out code; no traceback source values."""
    if tb is None:
        return []
    result = []
    for frame in traceback.extract_tb(tb):
        filename = frame.filename
        if filename == '<stdin>':
            location = 'GUARDED_DIAGNOSTIC'
        else:
            try:
                location = Path(filename).resolve().relative_to(BENCH.resolve()).as_posix()
            except (ValueError, OSError):
                continue
            if not (location.startswith('apps/frappe/')
                    or location.startswith('apps/erpnext/')
                    or location.startswith('.ccpc-peer-issuance-tests-2f846a75/')
                    or location.startswith('env/lib/')):
                continue
            # Never emit site-specific paths, file contents, argument values, or excerpts.
        if not re.fullmatch(r'[A-Za-z0-9_<>]+', frame.name):
            continue
        result.append(f'{location}:{frame.lineno}:{frame.name}')
    return result[-12:]

def _safe_reason(exc):
    # Only report known deliberate STOP reasons from this pinned operator script.
    message = str(exc)
    if (type(exc) is RuntimeError and message.startswith('STOP: ')
            and '\n' not in message and len(message) < 200
            and re.fullmatch(r'[A-Za-z0-9 .:_\-/]+', message)):
        return message
    return 'HIDDEN (unknown application/framework exception message)'

def independent_sql_readback():
    # Strictly use already pinned DEVELOPMENT DB endpoint; NO localhost fallback.
    c = MySQLdb.connect(
        host=EXPECTED_DEV_DB_HOST,
        port=EXPECTED_DEV_DB_PORT,
        user=iso.get('db_user') or iso['db_name'],
        passwd=iso['db_password'],db=iso['db_name'],charset='utf8mb4',connect_timeout=5)
    try:
        cur = c.cursor()
        cur.execute('START TRANSACTION READ ONLY')
        class ReadOnlyDB:
            def sql(self, sql, params=()):
                cur.execute(sql,params)
                return cur.fetchall()
        verify_db_baseline(ReadOnlyDB())
        if one(ReadOnlyDB(),'SELECT COUNT(*) FROM `tabStock Entry` WHERE withdrawal_slip=%s', (SLIP,))[0] != 0:
            stop('Readback discovered a linked Stock Entry')
        if count(ReadOnlyDB(), 'tabEmail Queue') != email_count:
            stop('Readback found unexpected persisted Email Queue record')
        c.rollback()
    finally:
        c.close()


def independent_sql_postcommit_readback(stock_entry_name, child_name):
    # The connection here is separate from Frappe's committed/closed transaction.
    # Strictly use already pinned DEVELOPMENT DB endpoint; NO localhost fallback.
    c = MySQLdb.connect(
        host=EXPECTED_DEV_DB_HOST,
        port=EXPECTED_DEV_DB_PORT,
        user=iso.get('db_user') or iso['db_name'],
        passwd=iso['db_password'],db=iso['db_name'],charset='utf8mb4',connect_timeout=5)
    try:
        cur = c.cursor()
        cur.execute('START TRANSACTION READ ONLY')
        class ReadOnlyDB:
            def sql(self, sql, params=()):
                cur.execute(sql,params)
                return cur.fetchall()
        db = ReadOnlyDB()
        if one(db,'SELECT DATABASE()')[0] != iso['db_name']:
            stop('Postcommit readback connected to unexpected database')
        verify_issued_state(db,stock_entry_name,child_name,email_count)
        c.rollback()
    finally:
        c.close()

try:
    stage = 'protect pinned Git, site and all 48 backup artifacts'
    verify_git()
    iso = config(SITE)
    other = config(OTHER_SITE)
    common_path = SITES / 'common_site_config.json'
    if not common_path.is_file() or common_path.is_symlink():
        stop('Unsafe or missing common site configuration')
    common = json.loads(common_path.read_text())
    if not isinstance(common,dict) or not iso.get('db_name') or iso['db_name'] == other.get('db_name'):
        stop('Isolated and shared DEVELOPMENT DB identities overlap')
    host = iso.get('db_host') or common.get('db_host')
    port = int(iso.get('db_port') or common.get('db_port') or 3306)
    if host != EXPECTED_DEV_DB_HOST or port != EXPECTED_DEV_DB_PORT:
        stop('Writable DB endpoint is not exact DEVELOPMENT mariadb:3306')
    if any(h not in (None,'',EXPECTED_DEV_DB_HOST) for h in (iso.get('db_host'),common.get('db_host'))):
        stop('Conflicting site/global DB host override')
    site_config_hash = sha256(SITES / SITE / 'site_config.json')
    common_config_hash = sha256(common_path)
    old_backups = verify_snapshots()  # full hashes done outside SQL transaction
    old_backup_metadata = verify_snapshots(metadata_only=True)
    print('PINNED SOURCE, ISOLATED SITE, AND 12 RECOVERY CHECKPOINTS: VERIFIED',flush=True)

    if any(k == 'ccpcerp' or k.startswith('ccpcerp.') for k in sys.modules):
        stop('CCPC already loaded before selecting isolated feature')
    sys.path.insert(0,str(FEATURE))
    import frappe
    from frappe.model.document import Document
    from frappe.utils import background_jobs
    pinned_names = (
        'ccpcerp','ccpcerp.hooks','ccpcerp.setup',
        'ccpcerp.ccpc_erp.doctype.withdrawal_slip.withdrawal_slip',
        'ccpcerp.ccpc_erp.withdrawal_slip_stock',
        'ccpcerp.ccpc_erp.equipment_costing',
    )
    mods={n:importlib.import_module(n) for n in pinned_names}
    verify_source_modules()
    stock=mods['ccpcerp.ccpc_erp.withdrawal_slip_stock']
    hooks=mods['ccpcerp.hooks'].doc_events['Stock Entry']
    for hookname,key in (
        ('validate_withdrawal_slip_stock_entry','validate'),
        ('validate_withdrawal_slip_stock_entry','before_submit'),
        ('sync_withdrawal_slip_issue_status','on_submit'),
    ):
        mapped=hooks.get(key)
        expected='ccpcerp.ccpc_erp.withdrawal_slip_stock.'+hookname
        if expected not in ([mapped] if isinstance(mapped,str) else mapped or []):
            stop('Pinned Stock Entry guard/status hook missing: '+key)
    print('PINNED MATERIAL ISSUE HANDLERS: VERIFIED',flush=True)

    stage = 'initialize isolated Frappe site and verify unposted baseline'
    frappe.init(site=SITE,sites_path=str(SITES))
    frappe.connect()
    connected=True
    frappe.set_user('Administrator')
    if frappe.local.site != SITE or one(frappe.db,'SELECT DATABASE()')[0] != iso['db_name']:
        stop('Initialized wrong database')
    if 'ccpcerp' not in frappe.get_installed_apps():
        stop('Pinned CCPC app not installed on isolated test site')
    actual_hooks=frappe.get_hooks('doc_events').get('Stock Entry',{})
    for key in ('validate','before_submit','on_submit'):
        must=hooks[key]
        for h in ([must] if isinstance(must,str) else must):
            actual=actual_hooks.get(key) or []
            if h not in ([actual] if isinstance(actual,str) else actual):
                stop('Installed Stock Entry hook mapping differs: '+key)
    verify_source_modules()
    child_name=verify_db_baseline(frappe.db)
    for user in (A,B):
        if 'Stockroom Personnel' not in frappe.get_roles(user):
            stop('Required real Stockroom role missing')
        if (frappe.has_permission('Stock Entry','create',user=user)
                or frappe.has_permission('Stock Entry','submit',user=user)):
            stop('Fictional test User gained ordinary Stock Entry rights')
    if not frappe.has_permission('Withdrawal Slip','write',
                                 doc=frappe.get_doc('Withdrawal Slip',SLIP),user=B):
        stop('Stockroom B cannot write the selected Slip')
    email_count=count(frappe.db,'tabEmail Queue')
    print('ONE UNPOSTED SLIP, STOCK AND ACCOUNTING BASELINE: VERIFIED',flush=True)

    def deny_async(*args,**kwargs):
        stop('Outbound email/background enqueue outside diagnostic scope')
    def deny_commit(*args,**kwargs):
        stop('Unexpected internal database COMMIT attempted')

    # Review-only callback harness. Frappe Document.notify_update() normally
    # queues Redis realtime events via Database.after_commit; suppress ONLY
    # expected synthetic document events and deny everything else.
    allowed_realtime_doctypes = {'Withdrawal Slip','Stock Entry','Stock Ledger Entry','GL Entry'}
    def limited_realtime(event=None, message=None, doctype=None, docname=None,
                         after_commit=False, **kwargs):
        target = doctype if event == 'doc_update' else (
            message.get('doctype') if event == 'list_update' and isinstance(message,dict) else None)
        if (after_commit is True and event in ('doc_update','list_update')
                and target in allowed_realtime_doctypes):
            return None   # no Redis, no callback scheduled for synthetic update
        stop('Unexpected realtime event or outbound side effect')

    # Block unreviewed SQL transaction-control/DDL through normal Frappe SQL
    # interface. NOT a comprehensive DML allowlist: direct driver paths,
    # child tables, and ancillary mutations require separate full tracing.
    original_sql = frappe.db.sql
    sql_commit_phase = 'locked'
    def limited_sql(query,*args,**kwargs):
        global sql_commit_phase
        q = str(query).strip().upper()
        if kwargs.get('auto_commit'):
            stop('Unapproved SQL auto_commit requested')
        if re.match(r'^(ALTER|CREATE|DROP|TRUNCATE|RENAME|GRANT|REVOKE|LOCK|UNLOCK|CALL|LOAD|REPLACE)\\b',q):
            stop('DDL/implicit commit operation blocked in review candidate')
        if re.match(r'^(COMMIT|ROLLBACK|BEGIN|START\\s+TRANSACTION|SAVEPOINT|RELEASE\\s+SAVEPOINT|SET\\s+AUTOCOMMIT)\\b',q):
            if q == 'COMMIT' and sql_commit_phase == 'one_commit':
                sql_commit_phase = 'committed_sql'
            elif q == 'START TRANSACTION' and sql_commit_phase == 'committed_sql':
                sql_commit_phase = 'postcommit_begin'
            else:
                stop('Unexpected SQL transaction control')
        return original_sql(query,*args,**kwargs)

    original_insert=Document.insert
    original_submit=Document.submit
    # Stock Entry is inserted as a DRAFT before submit() is called.
    allowed = {'entry': None, 'stock_object': None, 'stock_inserts': 0,
               'stock_entries': 0, 'sle': 0, 'sle_object': None, 'sle_inserts': 0,
               'gl_debit': 0, 'gl_credit': 0, 'gl_objects': [],
               'gl_inserted': []}
    def limited_insert(doc,*args,**kwargs):
        if doc.doctype in {'Sales Invoice','Purchase Invoice','Payment Entry',
                           'Journal Entry','Intercompany Material Billing Batch',
                           'Stock Reconciliation'}:
            stop('Unexpected unrelated business document insertion: '+doc.doctype)
        if doc.doctype in {'Stock Ledger Entry','GL Entry'}:
            if (allowed['entry'] is None
                    or doc.get('voucher_type') != 'Stock Entry'
                    or doc.get('voucher_no') != allowed['entry']):
                stop('Unexpected ledger document insertion')
            if doc.doctype == 'Stock Ledger Entry':
                if (doc is not allowed['sle_object'] or allowed['sle_inserts'] != 0):
                    stop('Unapproved Stock Ledger Entry insertion')
                allowed['sle_inserts'] += 1
            else:
                # Strong document references prevent Python id() reuse when ERPNext
                # builds and releases the two GL Entries sequentially.
                if (not any(obj is doc for obj in allowed['gl_objects'])
                        or any(obj is doc for obj in allowed['gl_inserted'])):
                    stop('Unapproved or duplicate GL Entry insertion')
                allowed['gl_inserted'].append(doc)
        if doc.doctype == 'Stock Entry':
            if (allowed['stock_inserts'] != 0
                    or doc.get('withdrawal_slip') != SLIP
                    or doc.get('company') != COMPANY
                    or doc.get('purpose') != 'Material Issue'
                    or doc.get('from_warehouse') != WAREHOUSE):
                stop('Unexpected or duplicate Stock Entry insertion')
            items = doc.get('items') or []
            if (len(items) != 1 or items[0].get('item_code') != ITEM
                    or items[0].get('withdrawal_slip_item') != child_name
                    or items[0].get('s_warehouse') != WAREHOUSE
                    or money(items[0].get('qty')) != 1):
                stop('Unexpected Stock Entry items at initial insertion')
            allowed['stock_inserts'] += 1
            allowed['stock_object'] = doc
            result = original_insert(doc,*args,**kwargs)
            if not doc.name or not re.fullmatch(r'[A-Za-z0-9_.\-]+',str(doc.name)):
                stop('Unexpected inserted Stock Entry name')
            allowed['entry'] = str(doc.name)
            return result
        if doc.doctype == 'Version':
            if (doc.get('ref_doctype') not in ('Withdrawal Slip', 'Stock Entry')
                    or doc.get('docname') not in (SLIP, allowed['entry'])):
                stop('Unexpected Version record insertion')
        elif doc.doctype not in {'Stock Entry','Stock Ledger Entry','GL Entry'}:
            stop('Unexpected document insert outside Material Issue scope: '+doc.doctype)
        return original_insert(doc,*args,**kwargs)
    # Scope the necessary ERPNext ledger submissions to the ONE synthetic issue.
    # ERPNext calls Stock Ledger Entry.submit() and GL Entry.submit() internally;
    # those are required journal/stock operations, not unrelated documents.
    def limited_submit(doc,*args,**kwargs):
        kind = doc.doctype
        if kind == 'Stock Entry':
            if (allowed['stock_entries'] != 0 or allowed['stock_inserts'] != 1
                    or allowed['entry'] != str(doc.name)
                    or allowed['stock_object'] is not doc
                    or not doc.name or not re.fullmatch(r'[A-Za-z0-9_.\-]+',str(doc.name))
                    or doc.get('withdrawal_slip') != SLIP
                    or doc.get('company') != COMPANY
                    or doc.get('purpose') != 'Material Issue'
                    or doc.get('from_warehouse') != WAREHOUSE):
                stop('Unexpected or duplicate Stock Entry submission')
            items = doc.get('items') or []
            if (len(items) != 1 or items[0].item_code != ITEM
                    or items[0].get('withdrawal_slip_item') != child_name
                    or items[0].get('s_warehouse') != WAREHOUSE
                    or items[0].get('t_warehouse') not in (None,'')
                    or money(items[0].get('qty')) != 1):
                stop('Unexpected Stock Entry item/provenance before submission')
            allowed['entry'] = str(doc.name)
            allowed['stock_entries'] += 1
        elif kind == 'Stock Ledger Entry':
            if (allowed['stock_entries'] != 1 or allowed['entry'] is None
                    or allowed['sle'] != 0
                    or doc.get('voucher_type') != 'Stock Entry'
                    or doc.get('voucher_no') != allowed['entry']
                    or doc.get('company') != COMPANY
                    or doc.get('item_code') != ITEM
                    or doc.get('warehouse') != WAREHOUSE
                    or money(doc.get('actual_qty')) != -1
                    or money(doc.get('is_cancelled')) != 0):
                stop('Unexpected or duplicate Stock Ledger Entry submission')
            allowed['sle'] += 1
            allowed['sle_object'] = doc
        elif kind == 'GL Entry':
            if (allowed['stock_entries'] != 1 or allowed['sle'] != 1
                    or allowed['entry'] is None
                    or doc.get('voucher_type') != 'Stock Entry'
                    or doc.get('voucher_no') != allowed['entry']
                    or doc.get('company') != COMPANY
                    or money(doc.get('is_cancelled')) != 0):
                stop('Unexpected GL Entry voucher/company or sequence')
            account = doc.get('account')
            debit = money(doc.get('debit'))
            credit = money(doc.get('credit'))
            tolerance = Decimal('0.05')
            if account == 'Stock Adjustment - TISS':
                if (allowed['gl_debit'] != 0 or credit != 0
                        or abs(debit - Decimal('100')) > tolerance
                        or doc.get('cost_center') != 'Main - TISS'):
                    stop('Unexpected or duplicate Material Issue expense GL')
                allowed['gl_debit'] += 1
            elif account == 'Stock In Hand - TISS':
                if (allowed['gl_credit'] != 0 or debit != 0
                        or abs(credit - Decimal('100')) > tolerance):
                    stop('Unexpected or duplicate Material Issue inventory GL')
                allowed['gl_credit'] += 1
            else:
                stop('Unexpected GL Entry account')
            # Retain a strong reference; compare actual object identity, not id() integers.
            allowed['gl_objects'].append(doc)
        else:
            stop('Unexpected document submission: '+kind)
        return original_submit(doc,*args,**kwargs)

    # Retain an unpatched bound COMMIT method. The patched frappe.db.commit below
    # prohibits ERPNext internals from committing during the reviewable transaction.
    original_commit = frappe.db.commit
    stage = 'single isolated commit-capable transaction: save Received By under Stockroom B'
    frappe.db.begin()
    transaction_started = True
    with (
        patch.object(frappe,'sendmail',side_effect=deny_async),
        patch.object(frappe,'enqueue',side_effect=deny_async),
        patch.object(background_jobs,'enqueue',side_effect=deny_async),
        patch.object(frappe,'publish_realtime',side_effect=limited_realtime),
        patch.object(frappe.realtime,'emit_via_redis',side_effect=deny_async),
        patch.object(frappe.db,'sql',side_effect=limited_sql),
        patch.object(frappe.db,'commit',side_effect=deny_commit),
        patch.object(Document,'insert',limited_insert),
        patch.object(Document,'submit',limited_submit),
    ):
        frappe.set_user(B)
        slip = frappe.get_doc('Withdrawal Slip',SLIP)
        if not frappe.has_permission('Withdrawal Slip','write',doc=slip,user=B):
            stop('Stockroom B lacks per-document write permission')
        slip.received_by = RECEIVER
        slip.save()
        saved = one(frappe.db,'SELECT received_by,status FROM `tabWithdrawal Slip` WHERE name=%s',(SLIP,))
        if saved != (RECEIVER,'Stockroom Review'):
            stop('Received By or workflow status wrong within transaction')
        print('FICTIONAL RECEIVED BY: SAVED INSIDE UNCOMMITTED TRANSACTION',flush=True)
        stage = 'invoke the pinned handler exactly once under Stockroom B'
        posting_exercised = True
        outcome = stock.issue_withdrawal_slip(SLIP)
        if not isinstance(outcome,dict) or outcome.get('submitted') != 1:
            stop('Posting handler returned no submitted outcome')
        entry_name = outcome.get('name')
        if not entry_name or not re.fullmatch(r'[A-Za-z0-9_.\-]+',entry_name):
            stop('Unexpected submitted Stock Entry name')
        if (allowed['entry'] != entry_name or allowed['stock_entries'] != 1
                or allowed['stock_inserts'] != 1 or allowed['sle'] != 1
                or allowed['sle_inserts'] != 1 or len(allowed['gl_inserted']) != 2
                or allowed['gl_debit'] != 1 or allowed['gl_credit'] != 1):
            stop('Expected exactly one Stock Entry, one SLE and two GL submissions')
        stage = 'verify ledger and status in SQL before any commit'
        verify_issued_state(frappe.db,entry_name,child_name,email_count)
        if (sha256(SITES / SITE / 'site_config.json') != site_config_hash
                or sha256(SITES / 'common_site_config.json') != common_config_hash):
            stop('Site configuration altered before COMMIT')
        # Full SHA256 here would hold the Withdrawal Slip row lock for too long.
        if verify_snapshots(metadata_only=True) != old_backup_metadata:
            stop('Protected backup metadata changed within SQL transaction')
        verify_git()
        verify_source_modules()
        if frappe.db.before_commit._functions or frappe.db.after_commit._functions:
            stop('Unreviewed before/after commit callbacks pending')
        print('STRICT ONE-STOCK-ENTRY ONE-SLE TWO-GL PRECOMMIT GATE: PASSED',flush=True)
        stage = 'ONE explicit isolated database COMMIT (outcome must be independently checked)'
        # The only place this script is permitted to COMMIT.
        commit_attempted = True
        sql_commit_phase = 'one_commit'
        original_commit()
        if sql_commit_phase != 'postcommit_begin':
            stop('Expected single SQL COMMIT and subsequent transaction BEGIN not observed')
        commit_returned = True
        transaction_started = False
        print('SQL COMMIT METHOD RETURNED; INDEPENDENT READBACK REQUIRED',flush=True)

    stage = 'independent new-connection postcommit SQL readback'
    independent_sql_postcommit_readback(entry_name,child_name)
    if (sha256(SITES / SITE / 'site_config.json') != site_config_hash
            or sha256(SITES / 'common_site_config.json') != common_config_hash):
        stop('Postcommit site config fingerprint differs')
    if verify_snapshots() != old_backups:
        stop('Postcommit recovery artifact fingerprint differs')
    verify_git()
    verify_source_modules()
    print('ONE LINKED MATERIAL ISSUE: COMMITTED',flush=True)
    print('INDEPENDENT POST-COMMIT SQL READBACK: PASSED',flush=True)
    print('BACKUPS, CONFIGURATION AND SOURCE: UNCHANGED',flush=True)
    print('ISOLATED SINGLE MATERIAL ISSUE TEST: PASSED',flush=True)
    print('ONE-SHOT COMMITTED TEST MUST NOT BE RERUN',flush=True)
except Exception as exc:
    print('ISOLATED ONE-UNIT MATERIAL ISSUE TEST: STOPPED',flush=True)
    print('STAGE:',stage,flush=True)
    print('ERROR CLASS:',type(exc).__name__,flush=True)
    print('CHECK:',_safe_reason(exc),flush=True)
    for label in _safe_frames(exc.__traceback__):
        print('SAFE TRACEBACK LOCATION:',label,flush=True)
    if commit_attempted:
        print('CRITICAL: COMMIT WAS ATTEMPTED; PERSISTENCE MAY HAVE OCCURRED',flush=True)
        print('DO NOT RERUN, ROLLBACK AS IF UNCOMMITTED, OR AUTOMATICALLY RESTORE',flush=True)
        print('INVESTIGATE USING A SEPARATELY APPROVED READ-ONLY SQL AUDIT',flush=True)
    else:
        if connected and transaction_started:
            try:
                frappe.db.rollback()
                rollback_ok = True
                print('SQL PRECOMMIT ROLLBACK: REPORTED',flush=True)
            except Exception:
                print('CRITICAL: PRECOMMIT ROLLBACK FAILED; PERSISTENCE UNKNOWN',flush=True)
        if connected and rollback_ok:
            try:
                independent_sql_readback()
                print('INDEPENDENT POST-ROLLBACK SQL BASELINE: PASSED',flush=True)
            except Exception:
                print('WARNING: INDEPENDENT ROLLBACK READBACK FAILED; PRESERVE STATE',flush=True)
        print('NO SCRIPT-LEVEL COMMIT ATTEMPTED; DO NOT ASSUME ZERO CACHE SIDE EFFECTS',flush=True)
        print('DO NOT RERUN OR DELETE BACKUPS',flush=True)
    raise SystemExit(1)
finally:
    if connected:
        try:
            frappe.destroy()
        except Exception:
            pass
PY
