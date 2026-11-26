"""Offline synthetic tests only. No live MariaDB/ERPNext/host execution."""
import ast
import contextlib
import hashlib
import io
import json
import socket
import sys
import types
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("diagnose_ws_2026_00008_finance_readonly.py")
ROOT = ast.parse(SCRIPT.read_text())
GUEST = next(n.value.value for n in ROOT.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "FINANCE_GUEST" for t in n.targets))
FAKE_AUDIT = '''
class Pilot:
    def __init__(self, **kw): self.__dict__.update(kw)
def single(rows): return rows[0] if len(rows) == 1 else None
def leaf(row, pilot):
    return bool(row and row['company'] == pilot.company and row['is_group'] == 0 and row['disabled'] == 0)
def eligible_mapping(read, kind, source, zone, instant, pilot):
    if kind == 'Center' and DENY_CENTER: raise ValueError('synthetic missing approval')
    if kind == 'Center' and WRITE_ATTEMPT: read('UPDATE `tabAccount` SET disabled=1')
    return 'approved-account' if kind == 'Expense' else 'approved-center'
'''


class FakeCursor:
    def __init__(self, altered_slip=False):
        self.queries = []
        self.altered_slip = altered_slip

    def execute(self, sql, args=()):
        self.queries.append(sql)
        if sql.startswith("SELECT "):
            return
        assert sql in ("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ",
                       "START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY")

    def fetchall(self):
        sql = self.queries[-1]
        if "CURRENT_USER()" in sql:
            return [dict(db='db', principal='user@%', hostname='container', server_id=1, version='MariaDB 11')]
        if 'tabWithdrawal Slip`' in sql:
            return [dict(name='WS-2026-00008', docstatus=0, status='Draft',
                         company='Cagayan Corn Products Corporation',
                         requesting_company='Cagayan Corn Products Corporation',
                         department='Maintenance Department - CCPC',
                         work_for_department='Maintenance Department - CCPC' if self.altered_slip else 'Wet Mill Plant - CCPC',
                         equipment='WD-401', ccpc_material_use='Routine Maintenance')]
        if 'tabWithdrawal Slip Item' in sql:
            return [dict(item_code='ITEM-00010', requested_qty=1, issued_qty=0)]
        if 'tabItem`' in sql:
            return [dict(name='ITEM-00010', item_group='Bearings', disabled=0, is_stock_item=1)]
        if 'tabSingles' in sql:
            return [dict(value='Asia/Manila')]
        if 'tabCCPC Expense Mapping Scope' in sql:
            return [dict(name='expense-scope', company='Cagayan Corn Products Corporation', item_group='Bearings')]
        if 'tabCCPC Center Mapping Scope' in sql:
            return [dict(name='center-scope', company='Cagayan Corn Products Corporation',
                         beneficiary_department='Wet Mill Plant - CCPC',
                         selector_kind='Department Only', selector_key='DEPARTMENT_ONLY')]
        if 'tabAccount' in sql:
            return [dict(name='approved-account', company='Cagayan Corn Products Corporation',
                         is_group=0, disabled=0, root_type='Expense')]
        if 'tabCost Center' in sql:
            return [dict(name='approved-center', company='Cagayan Corn Products Corporation',
                         is_group=0, disabled=0)]
        raise AssertionError('unexpected synthetic SQL')

    def close(self): pass


class FakeConnection:
    def __init__(self, altered_slip=False):
        self.cursor_obj = FakeCursor(altered_slip)
        self.rolled_back = False
        self.closed = False

    def cursor(self): return self.cursor_obj
    def rollback(self): self.rolled_back = True
    def close(self): self.closed = True


def fake_execute(*, deny_center=False, write_attempt=False, altered_slip=False, wrong_zone=False):
    connection = FakeConnection(altered_slip)
    mysql = types.ModuleType('MySQLdb')
    cursors = types.ModuleType('MySQLdb.cursors')
    cursors.DictCursor = object()
    mysql.cursors = cursors
    mysql.version_info = (2, 2, 7)
    mysql.connect = lambda **kw: connection
    audit = (f'DENY_CENTER = {deny_center}\nWRITE_ATTEMPT = {write_attempt}\n' + FAKE_AUDIT)
    digest = hashlib.sha256(audit.encode()).hexdigest()
    guest = GUEST.replace(
        "AUDIT_SHA = '556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927'",
        "AUDIT_SHA = '" + digest + "'",
    )
    target = dict(db_host='dbhost', schema='db', port=3306, principal='user@%',
                  db_ip='172.18.0.2', server_hostname='container', server_id=1)
    old_read = Path.read_text
    old_dns = socket.getaddrinfo
    old_mysql = sys.modules.get('MySQLdb')
    old_cursors = sys.modules.get('MySQLdb.cursors')
    buf = io.StringIO()
    try:
        sys.modules['MySQLdb'] = mysql
        sys.modules['MySQLdb.cursors'] = cursors
        Path.read_text = lambda p: json.dumps(dict(db_host='dbhost', db_name='db',
                                                   db_user='user', db_port=3306,
                                                   db_password='synthetic-only'))
        socket.getaddrinfo = lambda *a, **kw: [(None, None, None, None, ('172.18.0.2', 3306))]
        with contextlib.redirect_stdout(buf):
            try:
                exec(compile(guest, '<synthetic finance guest>', 'exec'),
                     dict(AUDIT_SOURCE=audit, TARGET=target,
                          EXPECTED_TIMEZONE='Etc/UTC' if wrong_zone else 'Asia/Manila'))
            except SystemExit as e:
                exitcode = e.code
    finally:
        Path.read_text = old_read
        socket.getaddrinfo = old_dns
        if old_mysql is None: sys.modules.pop('MySQLdb', None)
        else: sys.modules['MySQLdb'] = old_mysql
        if old_cursors is None: sys.modules.pop('MySQLdb.cursors', None)
        else: sys.modules['MySQLdb.cursors'] = old_cursors
    return exitcode, buf.getvalue().splitlines(), connection


class SyntheticFinanceTests(unittest.TestCase):
    def verify(self, opts, exit_code, last_prefix):
        status, lines, conn = fake_execute(**opts)
        self.assertEqual(status, exit_code)
        self.assertTrue(lines[-1].startswith(last_prefix), lines)
        self.assertTrue(conn.rolled_back)
        self.assertTrue(conn.closed)
        self.assertTrue(all(not q.startswith(('UPDATE', 'DELETE', 'INSERT'))
                            for q in conn.cursor_obj.queries))
        return lines

    def test_operator_host_handoff_injects_pinned_timezone(self):
        # Unlike the original fixture, exercise the real Finance wrapper's
        # construction of the guest payload without a live Docker/DB call.
        import tempfile
        from unittest import mock

        scope = {'__name__': '_ccpc_finance_test_module', '__file__': str(SCRIPT)}
        exec(compile(SCRIPT.read_text(), str(SCRIPT), 'exec'), scope)
        seen = []
        with tempfile.TemporaryDirectory() as folder:
            binding = Path(folder) / 'binding.json'
            binding.write_text(json.dumps({
                'verification_mode': 'sole-administrator-two-technical-checks',
                'operator_acknowledgement': False,
                'expected_binding': {
                    'host': 'ccpcerpserver', 'site': 'development.localhost',
                    'timezone': 'Asia/Manila',
                },
            }))
            binding.chmod(0o600)
            fake_guard = types.SimpleNamespace(
                HOST='ccpcerpserver', SITE='development.localhost',
                BINDING=binding, GUEST=None)
            fake_guard.main = lambda: seen.append(fake_guard.GUEST)
            stub_spec = types.SimpleNamespace(
                name='_ccpc_test_guard_module',
                loader=types.SimpleNamespace(exec_module=lambda _: None))
            scope['checked_source'] = lambda name, digest: (SCRIPT, 'synthetic-source-only')
            with mock.patch.object(scope['importlib'].util, 'spec_from_file_location',
                                   return_value=stub_spec), mock.patch.object(
                    scope['importlib'].util, 'module_from_spec', return_value=fake_guard):
                try:
                    scope['main']()
                finally:
                    sys.modules.pop(stub_spec.name, None)
        self.assertEqual(len(seen), 1)
        self.assertTrue(seen[0].startswith(
            "EXPECTED_TIMEZONE = 'Asia/Manila'\\nAUDIT_SOURCE = 'synthetic-source-only'\\n"
        ), 'operator handoff must pass pinned timezone independent of TARGET')
        self.assertNotIn("TARGET['timezone']", scope['FINANCE_GUEST'])

    def test_two_mappings_present_in_synthetic_snapshot(self):
        lines = self.verify({}, 0, 'PASS | OVERALL')
        self.assertEqual(sum(x.startswith('PASS | ') for x in lines), 10)

    def test_missing_center_approval_fails_closed(self):
        lines = self.verify({'deny_center': True}, 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Wet Mill Center signed provenance', '\n'.join(lines))

    def test_changed_beneficiary_fails_closed(self):
        lines = self.verify({'altered_slip': True}, 1, 'FAIL | OVERALL')
        self.assertFalse(any('signed provenance' in line for line in lines))

    def test_private_timezone_mismatch_fails_closed(self):
        lines = self.verify({'wrong_zone': True}, 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Persisted site timezone', '\n'.join(lines))
        self.assertFalse(any('signed provenance' in line for line in lines))

    def test_policy_attempt_to_write_is_rejected(self):
        lines = self.verify({'write_attempt': True}, 1, 'STOP | SNAPSHOT')
        self.assertIn('STOP | SNAPSHOT', lines[-1])


if __name__ == '__main__':
    unittest.main()
