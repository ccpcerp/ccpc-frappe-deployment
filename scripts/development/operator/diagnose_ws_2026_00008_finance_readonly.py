#!/usr/bin/env python3
"""Operator-only, fixed-scope Finance mapping diagnosis. No writes or attestations."""
import hashlib
import importlib.util
import os
import stat
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PILOT_NAME = "diagnose_ws_2026_00008_readonly.py"
PILOT_SHA256 = "8f9741b49a691796022a08a525e606cf164f77d8bf7d6308696af5c364d7c04b"
AUDIT_NAME = "ws_readiness_audit.py"
AUDIT_SHA256 = "556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927"

# This is the entire guest payload except the two literals inserted immediately
# above it: TARGET from the audited prior host guard and AUDIT_SOURCE from this wrapper.
FINANCE_GUEST = r'''
import hashlib, json, os, socket, sys, types
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import MySQLdb
import MySQLdb.cursors

COMPANY = 'Cagayan Corn Products Corporation'
BENEFICIARY = 'Wet Mill Plant - CCPC'
SLIP = 'WS-2026-00008'
ITEM = 'ITEM-00010'
GROUP = 'Bearings'
AUDIT_SHA = '556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927'


def diagnose():
    assert MySQLdb.version_info[:3] == (2, 2, 7)
    assert not any(k.startswith('FRAPPE_DB_') for k in os.environ)
    cfg = {}
    for path in ('sites/common_site_config.json', 'sites/development.localhost/site_config.json'):
        cfg.update(json.loads(Path(path).read_text()))
    assert cfg.get('db_type', 'mariadb') == 'mariadb'
    assert not cfg.get('db_socket') and not cfg.get('extra_config')
    assert not any(v for k, v in cfg.items() if k.startswith('db_ssl'))
    assert cfg['db_host'] == TARGET['db_host'] and cfg['db_name'] == TARGET['schema']
    assert int(cfg.get('db_port') or 3306) == TARGET['port']
    user = cfg.get('db_user') or cfg['db_name']
    assert user == TARGET['principal'].split('@', 1)[0]
    assert {v[4][0] for v in socket.getaddrinfo(cfg['db_host'], TARGET['port'], type=socket.SOCK_STREAM)} == {TARGET['db_ip']}
    assert cfg.get('db_password')
    assert hashlib.sha256(AUDIT_SOURCE.encode('utf-8')).hexdigest() == AUDIT_SHA

    # This imported policy is the hash-pinned, pre-reviewed audit from PR43.
    # Its main entrypoint is never invoked; only signed mapping policy functions.
    mod = types.ModuleType('_ccpc_pinned_finance_policy')
    sys.modules[mod.__name__] = mod
    exec(compile(AUDIT_SOURCE, 'ws_readiness_audit.py', 'exec'), mod.__dict__)

    connection = MySQLdb.connect(
        host=TARGET['db_ip'], port=TARGET['port'], user=user,
        passwd=cfg['db_password'], db=TARGET['schema'], charset='utf8mb4',
        local_infile=False, multi_statements=False,
        cursorclass=MySQLdb.cursors.DictCursor,
        connect_timeout=5, read_timeout=15, write_timeout=5,
    )
    checks = []

    def emit(ok, label):
        checks.append(bool(ok))
        print(('PASS' if ok else 'FAIL') + ' | ' + label + ' | ' +
              ('verified in read-only snapshot' if ok else 'missing or conflicting live approval evidence'))

    try:
        c = connection.cursor()
        try:
            c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            c.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY')

            def read(sql, args=()):
                upper = sql.upper()
                assert sql.startswith('SELECT ') and not any(
                    token in upper for token in (';', 'FOR UPDATE', 'LOCK IN SHARE MODE',
                                                'OUTFILE', 'DUMPFILE', '/*', '--')
                )
                c.execute(sql, args)
                return list(c.fetchall())

            identity = mod.single(read('SELECT DATABASE() AS db,CURRENT_USER() AS principal,'
                                       '@@hostname AS hostname,@@server_id AS server_id,VERSION() AS version'))
            assert identity and identity['db'] == TARGET['schema']
            assert identity['principal'] == TARGET['principal']
            assert identity['hostname'] == TARGET['server_hostname']
            assert identity['server_id'] == TARGET['server_id']
            assert 'mariadb' in identity['version'].lower()
            print('PASS | MariaDB identity | independently matched private pin')

            slip = mod.single(read('SELECT name,docstatus,status,company,requesting_company,'
                                   'department,work_for_department,equipment,ccpc_material_use '
                                   'FROM `tabWithdrawal Slip` WHERE name=%s', (SLIP,)))
            children = read('SELECT item_code,requested_qty,issued_qty FROM `tabWithdrawal Slip Item` '
                            "WHERE parent=%s AND parenttype='Withdrawal Slip' AND parentfield='items'", (SLIP,))
            item = mod.single(read('SELECT name,item_group,disabled,is_stock_item FROM `tabItem` WHERE name=%s', (ITEM,)))
            correct = bool(
                slip and slip['docstatus'] == 0 and slip['status'] == 'Draft'
                and slip['company'] == slip['requesting_company'] == COMPANY
                and slip['department'] == 'Maintenance Department - CCPC'
                and slip['work_for_department'] == BENEFICIARY
                and slip['equipment'] == 'WD-401' and slip['ccpc_material_use'] == 'Routine Maintenance'
                and len(children) == 1 and children[0]['item_code'] == ITEM
                and children[0]['requested_qty'] == 1 and not children[0]['issued_qty']
                and item and item['item_group'] == GROUP and item['disabled'] == 0
                and item['is_stock_item'] == 1
            )
            emit(correct, 'Exact draft item and beneficiary')
            if not correct:
                print('FAIL | OVERALL | pilot changed; no Finance conclusion or posting authorization')
                return False
            site_zone = mod.single(read("SELECT value FROM `tabSingles` WHERE doctype='System Settings' AND field='time_zone'"))
            zone_ok = bool(site_zone and site_zone['value'] == TARGET['timezone'])
            emit(zone_ok, 'Persisted site timezone')
            if not zone_ok:
                print('FAIL | OVERALL | timezone mismatch; no Finance conclusion or posting authorization')
                return False

            zone = ZoneInfo(TARGET['timezone'])
            instant = datetime.now(timezone.utc)
            pilot = mod.Pilot(
                slip=SLIP, company=COMPANY, requesting='Maintenance Department - CCPC',
                beneficiary=BENEFICIARY, equipment='WD-401', item=ITEM,
                warehouse='Warehouse 1 - CCPC', expense='',
            )

            for kind, source, scope_key, master, extra in (
                ('Expense', GROUP, 'item_group', 'Account', ',root_type'),
                ('Center', BENEFICIARY, 'beneficiary_department', 'Cost Center', ''),
            ):
                label = 'Bearings Expense' if kind == 'Expense' else 'Wet Mill Center'
                selector = ',selector_kind,selector_key' if kind == 'Center' else ''
                scope = mod.single(read(
                    'SELECT name,company,' + scope_key + selector + ' FROM `tabCCPC ' + kind +
                    ' Mapping Scope` WHERE company=%s AND ' + scope_key + '=%s',
                    (COMPANY, source),
                ))
                scope_ok = bool(scope and scope['company'] == COMPANY and scope[scope_key] == source)
                if kind == 'Center':
                    scope_ok = bool(scope_ok and
                        (scope['selector_kind'], scope['selector_key']) == ('Department Only', 'DEPARTMENT_ONLY'))
                emit(scope_ok, label + ' exact scope')
                if not scope_ok:
                    emit(False, label + ' signed provenance')
                    emit(False, label + ' active master')
                    continue
                try:
                    # Uses checked, currently effective, unique approved revision,
                    # signature, maker/checker, decision-use, Version snapshot and retirement policy.
                    target = mod.eligible_mapping(read, kind, source, zone, instant, pilot)
                except ValueError:
                    emit(False, label + ' signed provenance')
                    emit(False, label + ' active master')
                    continue
                emit(True, label + ' signed provenance')
                row = mod.single(read(
                    'SELECT name,company,is_group,disabled' + extra + ' FROM `tab' + master + '` WHERE name=%s',
                    (target,),
                ))
                valid = bool(mod.leaf(row, pilot) and row['name'] == target)
                if kind == 'Expense':
                    valid = bool(valid and row['root_type'] == 'Expense')
                emit(valid, label + ' active master')

            print(('PASS' if all(checks) else 'FAIL') +
                  ' | OVERALL | signed evidence structure only; private binding and posting remain blocked')
            return all(checks)
        finally:
            connection.rollback()
            c.close()
    finally:
        connection.close()

try:
    ok = diagnose()
except Exception:
    print('STOP | SNAPSHOT | finance read-only check interrupted; private details withheld')
    ok = False
sys.exit(0 if ok else 1)
'''


def checked_source(name, expected):
    path = HERE / name
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid() or st.st_nlink != 1 or stat.S_IMODE(st.st_mode) != 0o600:
        raise RuntimeError("Source file must be a non-writable regular file")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError("Pinned script hash mismatch")
    return path, raw.decode('utf-8')


def main():
    # Reuse the exact operator-only host guard that passed the live pilot test.
    path, _ = checked_source(PILOT_NAME, PILOT_SHA256)
    _, audit_source = checked_source(AUDIT_NAME, AUDIT_SHA256)
    spec = importlib.util.spec_from_file_location('_ccpc_pilot_guard', path)
    guard = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = guard
    spec.loader.exec_module(guard)
    guard.GUEST = 'AUDIT_SOURCE = ' + repr(audit_source) + '\n' + FINANCE_GUEST
    guard.main()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print('STOP | HOST GUARD | pinned source or DEVELOPMENT identity rejected; details withheld')
        sys.exit(1)
