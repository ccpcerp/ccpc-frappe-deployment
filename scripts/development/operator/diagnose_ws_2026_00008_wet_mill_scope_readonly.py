#!/usr/bin/env python3
"""Operator-only DEVELOPMENT Wet Mill Center scope classification; never writes."""
import hashlib
import importlib.util
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
GUARD_NAME = "diagnose_ws_2026_00008_readonly.py"
GUARD_SHA256 = "8f9741b49a691796022a08a525e606cf164f77d8bf7d6308696af5c364d7c04b"

# The existing pinned host guard supplies the private TARGET in the DEVELOPMENT
# Frappe container. The guest receives no credential/configuration file from host.
GUEST = r'''
import json
import os
from decimal import Decimal
from pathlib import Path
import socket
import sys
import MySQLdb
import MySQLdb.cursors

COMPANY = 'Cagayan Corn Products Corporation'
BENEFICIARY = 'Wet Mill Plant - CCPC'
SLIP = 'WS-2026-00008'
REQUESTING = 'Maintenance Department - CCPC'


def diagnostic():
    assert MySQLdb.version_info[:3] == (2, 2, 7)
    assert not any(k.startswith('FRAPPE_DB_') for k in os.environ)
    cfg = {}
    for path in ('sites/common_site_config.json', 'sites/development.localhost/site_config.json'):
        cfg.update(json.loads(Path(path).read_text()))
    assert cfg.get('db_type', 'mariadb') == 'mariadb'
    assert not cfg.get('db_socket') and not cfg.get('extra_config')
    assert not any(v for k, v in cfg.items() if k.startswith('db_ssl'))
    assert cfg['db_host'] == TARGET['db_host']
    assert cfg['db_name'] == TARGET['schema']
    assert int(cfg.get('db_port') or 3306) == TARGET['port']
    user = cfg.get('db_user') or cfg['db_name']
    assert user == TARGET['principal'].split('@', 1)[0]
    assert cfg.get('db_password')
    assert {v[4][0] for v in socket.getaddrinfo(
        cfg['db_host'], TARGET['port'], type=socket.SOCK_STREAM
    )} == {TARGET['db_ip']}

    connection = MySQLdb.connect(
        host=TARGET['db_ip'], port=TARGET['port'], user=user,
        passwd=cfg['db_password'], db=TARGET['schema'], charset='utf8mb4',
        local_infile=False, multi_statements=False,
        cursorclass=MySQLdb.cursors.DictCursor,
        connect_timeout=5, read_timeout=15, write_timeout=5,
    )
    try:
        cursor = connection.cursor()
        try:
            cursor.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            cursor.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY')

            def one(sql, args=()):
                upper = sql.upper()
                assert sql.startswith('SELECT ') and not any(
                    token in upper for token in (';', 'FOR UPDATE', 'LOCK IN SHARE MODE',
                                                'OUTFILE', 'DUMPFILE', '/*', '--')
                )
                cursor.execute(sql, args)
                rows = cursor.fetchall()
                assert len(rows) == 1
                return rows[0]

            ident = one('SELECT DATABASE() AS db,CURRENT_USER() AS principal,'
                        '@@hostname AS hostname,@@server_id AS server_id,VERSION() AS version')
            assert ident['db'] == TARGET['schema']
            assert ident['principal'] == TARGET['principal']
            assert ident['hostname'] == TARGET['server_hostname']
            assert ident['server_id'] == TARGET['server_id']
            assert 'mariadb' in ident['version'].lower()
            print('PASS | MariaDB identity | matched pinned DEVELOPMENT server')

            slip = one('SELECT name,docstatus,status,company,requesting_company,department,'
                       'work_for_department FROM `tabWithdrawal Slip` WHERE name=%s', (SLIP,))
            if not (slip['name'] == SLIP and slip['docstatus'] == 0
                    and slip['status'] == 'Draft'
                    and slip['company'] == slip['requesting_company'] == COMPANY
                    and slip['department'] == REQUESTING
                    and slip['work_for_department'] == BENEFICIARY):
                print('FAIL | Pilot scope | saved Draft intent differs from fixed DEVELOPMENT pilot')
                print('FAIL | OVERALL | inspection blocked; no Finance or posting authorization')
                return False
            print('PASS | Pilot scope | saved Draft beneficiary matched')

            counts = one(
                'SELECT COUNT(*) AS n,'
                'COALESCE(SUM(CASE WHEN selector_kind=%s THEN 1 ELSE 0 END),0) AS kind_matches,'
                'COALESCE(SUM(CASE WHEN selector_key=%s THEN 1 ELSE 0 END),0) AS key_matches,'
                'COALESCE(SUM(CASE WHEN selector_kind=%s AND selector_key=%s THEN 1 ELSE 0 END),0) AS exact_matches '
                'FROM `tabCCPC Center Mapping Scope` WHERE company=%s AND beneficiary_department=%s',
                ('Department Only', 'DEPARTMENT_ONLY', 'Department Only', 'DEPARTMENT_ONLY',
                 COMPANY, BENEFICIARY),
            )
            raw = tuple(counts[k] for k in
                        ('n', 'kind_matches', 'key_matches', 'exact_matches'))
            # MySQLdb may return decimal.Decimal for integer SUM expressions.
            assert all(type(v) in (int, Decimal) and v == int(v) for v in raw)
            n, kinds, keys, exacts = map(int, raw)
            assert n >= 0 and 0 <= exacts <= kinds <= n and 0 <= exacts <= keys <= n

            if n == 0:
                print('FAIL | Wet Mill scope count | zero exact Company and Department records')
                print('FAIL | Wet Mill selector | no matching record to examine')
            elif n == 1:
                print('PASS | Wet Mill scope count | exactly one record')
                print(('PASS' if kinds == 1 else 'FAIL') +
                      ' | Wet Mill selector kind | ' + ('Department Only' if kinds == 1 else 'not Department Only'))
                print(('PASS' if keys == 1 else 'FAIL') +
                      ' | Wet Mill selector key | ' + ('required selector key confirmed' if keys == 1 else 'selector key differs'))
            else:
                print('FAIL | Wet Mill scope count | multiple exact Company and Department records')
                print(('PASS' if exacts == n else 'FAIL') +
                      ' | Wet Mill selector | ' + ('all records have required selector' if exacts == n
                                                  else 'one or more selectors differ'))
            ok = (n == 1 and exacts == 1)
            print(('PASS' if ok else 'FAIL') +
                  ' | OVERALL | scope classified; signed Finance and posting remain blocked')
            return ok
        finally:
            connection.rollback()
            cursor.close()
    finally:
        connection.close()


try:
    status = diagnostic()
except Exception:
    print('STOP | SNAPSHOT | fixed scope inspection interrupted; private details withheld')
    status = False
sys.exit(0 if status else 1)
'''


def main():
    guard_file = HERE / GUARD_NAME
    st = guard_file.lstat()
    if not (stat.S_ISREG(st.st_mode) and st.st_nlink == 1
            and st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o600):
        raise RuntimeError('Pinned guard not private regular file')
    if hashlib.sha256(guard_file.read_bytes()).hexdigest() != GUARD_SHA256:
        raise RuntimeError('Pinned DEVELOPMENT guard source mismatch')
    spec = importlib.util.spec_from_file_location('_ccpc_pinned_dev_guard_scope', guard_file)
    guard = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = guard
    spec.loader.exec_module(guard)
    guard.GUEST = GUEST
    guard.main()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print('STOP | HOST GUARD | fixed DEVELOPMENT host or staged source rejected')
        sys.exit(1)
