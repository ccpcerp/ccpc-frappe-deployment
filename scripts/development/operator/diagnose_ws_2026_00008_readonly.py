#!/usr/bin/env python3
"""CCPC operator-only, fixed-scope DEVELOPMENT pilot diagnosis; NEVER writes business data."""
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys

HOST = 'ccpcerpserver'
SITE = 'development.localhost'
SHA = 'e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5'
APP = '/home/gani/deployments/frappe_docker/development/frappe-bench/apps/ccpcerp'
BENCH = '/workspace/development/frappe-bench'
BINDING = Path.home() / 'ccpc-ws-preflight.ib55cS30/dev-pilot-binding.json'
NETWORK = 'frappe_docker_devcontainer_default'
APP_NAME = 'frappe_docker_devcontainer-frappe-1'
DB_NAME = 'frappe_docker_devcontainer-mariadb-1'
DOCKER = ('/usr/bin/docker', '--host', 'unix:///var/run/docker.sock')

# This payload never accesses the private binding file or writes to the site.
GUEST = r'''
import json, os, socket, sys
import MySQLdb
import MySQLdb.cursors
from pathlib import Path

EXPECTED = {
    'slip': 'WS-2026-00008',
    'company': 'Cagayan Corn Products Corporation',
    'requesting': 'Maintenance Department - CCPC',
    'beneficiary': 'Wet Mill Plant - CCPC',
    'equipment': 'WD-401',
    'warehouse': 'Warehouse 1 - CCPC',
    'item': 'ITEM-00010',
}

def diagnosis():
    assert MySQLdb.version_info[:3] == (2, 2, 7)
    assert not any(k.startswith('FRAPPE_DB_') for k in os.environ)
    cfg = {}
    for file in ('sites/common_site_config.json', 'sites/development.localhost/site_config.json'):
        cfg.update(json.loads(Path(file).read_text()))
    assert cfg.get('db_type', 'mariadb') == 'mariadb'
    assert not cfg.get('db_socket') and not cfg.get('extra_config')
    assert not any(v for k,v in cfg.items() if k.startswith('db_ssl'))
    assert cfg['db_host'] == TARGET['db_host']
    assert cfg['db_name'] == TARGET['schema']
    assert int(cfg.get('db_port') or 3306) == TARGET['port']
    user = cfg.get('db_user') or cfg['db_name']
    assert user == TARGET['principal'].split('@', 1)[0]
    assert {a[4][0] for a in socket.getaddrinfo(cfg['db_host'], TARGET['port'], type=socket.SOCK_STREAM)} == {TARGET['db_ip']}
    assert cfg.get('db_password')

    conn = MySQLdb.connect(host=TARGET['db_ip'], port=TARGET['port'], user=user,
        passwd=cfg['db_password'], db=TARGET['schema'], charset='utf8mb4',
        local_infile=False, multi_statements=False,
        cursorclass=MySQLdb.cursors.DictCursor,
        connect_timeout=5, read_timeout=15, write_timeout=5)
    checks = []
    def emit(ok, label):
        checks.append(ok)
        print(('PASS' if ok else 'FAIL') + ' | ' + label + ' | ' +
              ('matched' if ok else 'does not match expected saved/master data'))

    try:
        c = conn.cursor()
        try:
            c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            c.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY')
            def one(sql, args):
                assert sql.startswith('SELECT ') and ';' not in sql and 'FOR UPDATE' not in sql
                c.execute(sql, args)
                rows = c.fetchall()
                return rows[0] if len(rows) == 1 else None
            def many(sql, args):
                assert sql.startswith('SELECT ') and ';' not in sql and 'FOR UPDATE' not in sql
                c.execute(sql, args)
                return c.fetchall()

            ident = one('SELECT DATABASE() AS db,CURRENT_USER() AS principal,'
                        '@@hostname AS hostname,@@server_id AS server_id,VERSION() AS version', ())
            assert ident and ident['db'] == TARGET['schema']
            assert ident['principal'] == TARGET['principal']
            assert ident['hostname'] == TARGET['server_hostname']
            assert ident['server_id'] == TARGET['server_id']
            assert 'mariadb' in ident['version'].lower()
            print('PASS | MariaDB identity | independently matched private pin')

            slip = one('SELECT name,docstatus,status,company,requesting_company,department,'
                       'work_for_department,work_for_section,equipment,source_warehouse,ccpc_material_use '
                       'FROM `tabWithdrawal Slip` WHERE name=%s', (EXPECTED['slip'],))
            emit(slip is not None, 'Saved slip exists once')
            if slip is None:
                print('FAIL | OVERALL | diagnostic only; no business data changed')
                return False
            emit(slip['docstatus'] == 0 and slip['status'] == 'Draft', 'Draft state')
            emit(slip['company'] == slip['requesting_company'] == EXPECTED['company'], 'Company fields')
            emit(slip['department'] == EXPECTED['requesting'], 'Requesting Department exact ID')
            emit(slip['work_for_department'] == EXPECTED['beneficiary'], 'Beneficiary Department exact ID')
            emit(slip['equipment'] == EXPECTED['equipment'], 'Equipment exact ID')
            emit(slip['source_warehouse'] == EXPECTED['warehouse'], 'Warehouse exact ID')
            emit(slip['ccpc_material_use'] == 'Routine Maintenance', 'Material use')

            child = many('SELECT item_code,requested_qty,issued_qty,uom FROM `tabWithdrawal Slip Item` '
                         "WHERE parent=%s AND parenttype='Withdrawal Slip' AND parentfield='items'",
                         (EXPECTED['slip'],))
            emit(len(child) == 1, 'Exactly one persisted child row')
            if len(child) == 1:
                row = child[0]
                emit(row['item_code'] == EXPECTED['item'] and row['requested_qty'] == 1
                     and not row['issued_qty'] and row['uom'] == 'Nos', 'Saved item and quantity')

            for field, key in (('Requesting', 'requesting'), ('Beneficiary', 'beneficiary')):
                dept = one('SELECT name,company,is_group,disabled FROM `tabDepartment` WHERE name=%s',
                           (EXPECTED[key],))
                emit(bool(dept and dept['company'] == EXPECTED['company']
                          and dept['is_group'] == 0 and dept['disabled'] == 0), field + ' Department master')

            eq = one('SELECT name,company,department,section,status FROM `tabEquipment Registry` WHERE name=%s',
                     (EXPECTED['equipment'],))
            emit(bool(eq and eq['company'] == EXPECTED['company'] and eq['department'] == EXPECTED['beneficiary']
                      and eq['status'] == 'Active'), 'Equipment master affiliation')
            emit(bool(eq and (not eq['section'] or eq['section'] == slip['work_for_section'])),
                 'Equipment section alignment')
            sections = many('SELECT name FROM `tabCCPC Section` WHERE department=%s AND company=%s AND disabled=0',
                            (EXPECTED['beneficiary'], EXPECTED['company']))
            emit(not sections and not slip['work_for_section'] or any(
                s['name'] == slip['work_for_section'] for s in sections), 'Beneficiary Section master')

            wh = one('SELECT company,is_group,disabled FROM `tabWarehouse` WHERE name=%s',
                     (EXPECTED['warehouse'],))
            emit(bool(wh and wh['company'] == EXPECTED['company'] and wh['is_group'] == 0
                      and wh['disabled'] == 0), 'Warehouse master')
            item = one('SELECT name,item_group,disabled,is_stock_item FROM `tabItem` WHERE name=%s',
                       (EXPECTED['item'],))
            group = one('SELECT name,is_group FROM `tabItem Group` WHERE name=%s',
                        ('Bearings',))
            emit(bool(item and item['item_group'] == 'Bearings' and item['disabled'] == 0
                      and item['is_stock_item'] == 1 and group and group['is_group'] == 0),
                 'Item and Bearings group')
            company = one('SELECT name FROM `tabCompany` WHERE name=%s', (EXPECTED['company'],))
            emit(company is not None, 'Company master')
            linked = many('SELECT docstatus FROM `tabStock Entry` WHERE withdrawal_slip=%s',
                          (EXPECTED['slip'],))
            emit(not any(r['docstatus'] != 2 for r in linked), 'No live linked Stock Entry')
            print(('PASS' if all(checks) else 'FAIL') +
                  ' | OVERALL | diagnostic only; expense mapping and posting remain blocked')
            return all(checks)
        finally:
            conn.rollback()
            c.close()
    finally:
        conn.close()

try:
    ok = diagnosis()
except Exception:
    print('STOP | SNAPSHOT | fixed read-only checks could not complete; private details withheld')
    ok = False
sys.exit(0 if ok else 1)
'''


def ensure(ok):
    if not ok:
        raise RuntimeError('guard rejected')


def run(argv, *, stdin=None, timeout=15):
    r = subprocess.run(argv, input=stdin, capture_output=True, text=True,
                       timeout=timeout, check=False)
    ensure(r.returncode == 0)
    return r.stdout


def inspect(name, cid, target):
    raw = run((*DOCKER, 'inspect', '--type', 'container', '--format',
               '{{.Id}}|{{.Name}}|{{.State.Running}}|{{json .NetworkSettings.Networks}}', cid))
    actual, named, running, networks = raw.strip().split('|', 3)
    ensure(actual == cid and named == '/' + name and running == 'true')
    net = json.loads(networks)[NETWORK]
    ensure(net['NetworkID'] == target['network_id'])
    return net


def main():
    ensure(os.geteuid() != 0 and socket.gethostname().split('.', 1)[0] == HOST)
    st = BINDING.lstat()
    ensure(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_uid == os.getuid()
           and stat.S_IMODE(st.st_mode) == 0o600)
    spec = json.loads(BINDING.read_text())
    target = spec['expected_binding']
    ensure(spec['verification_mode'] == 'sole-administrator-two-technical-checks'
           and spec['operator_acknowledgement'] is False)
    ensure(target['host'] == HOST and target['site'] == SITE and target['commit'] == SHA)
    ensure(target['pilot']['slip'] == 'WS-2026-00008' and not any(
        target['pilot'][k] for k in ('company','requesting','beneficiary','equipment','item','warehouse','expense')))
    ensure(type(target['server_id']) is int and target['server_id'] >= 0
           and type(target['port']) is int and 0 < target['port'] < 65536)
    ensure(all(isinstance(target[k], str) and target[k] for k in
               ('db_host','db_ip','schema','principal','server_hostname','timezone')))
    ensure(ipaddress.ip_address(target['db_ip']).is_private)
    for name in ('app_container_id', 'db_container_id', 'network_id'):
        ensure(re.fullmatch(r'[0-9a-f]{64}', target[name]) is not None)
    ensure(run(('/usr/bin/git', '--no-optional-locks', '-C', APP, 'rev-parse', 'HEAD')).strip() == SHA)
    ensure(not run(('/usr/bin/git', '--no-optional-locks', '-C', APP,
                    'status', '--porcelain=v1', '--untracked-files=all')).strip())
    ensure((Path(APP).parent.parent / 'sites' / SITE).is_dir())
    app_net = inspect(APP_NAME, target['app_container_id'], target)
    db_net = inspect(DB_NAME, target['db_container_id'], target)
    ensure(db_net['IPAddress'] == target['db_ip']
           and app_net['NetworkID'] == db_net['NetworkID'])
    # Bind privately to the pinned site/DB. Only source code and fixed checks on stdin;
    # no passwords or private binding file are passed to another environment.
    safe = {k: target[k] for k in
            ('db_host','db_ip','port','schema','principal','server_hostname','server_id')}
    payload = 'import json\nTARGET = json.loads(' + repr(json.dumps(safe)) + ')\n' + GUEST
    proc = subprocess.run((*DOCKER, 'exec', '-i', '--user', 'frappe', '--workdir', BENCH,
                           target['app_container_id'], './env/bin/python', '-I', '-B', '-'),
                          input=payload, capture_output=True, text=True, timeout=60, check=False)
    lines = proc.stdout.splitlines()
    pattern = re.compile(r'(PASS|FAIL|STOP) \| [A-Za-z0-9 /-]{1,60} \| [A-Za-z0-9 ;.,-]{1,120}')
    for line in lines:
        ensure(bool(pattern.fullmatch(line)))
        print(line)
    ensure(bool(lines) and lines[-1].startswith(('PASS | OVERALL |','FAIL | OVERALL |',
                                                 'STOP | SNAPSHOT |')))
    if proc.returncode:
        raise SystemExit(1)

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print('STOP | HOST GUARD | private binding, pinned runtime, or fixed diagnostic failed; details withheld')
        sys.exit(1)

