"""Offline synthetic regression tests only; no Docker, MariaDB, ERPNext or project config."""
import ast
import contextlib
from decimal import Decimal
import io
import json
import re
from pathlib import Path
import socket
import sys
import types
import unittest
from unittest import mock

SOURCE = Path(__file__).with_name('diagnose_ws_2026_00008_wet_mill_scope_readonly.py')
TREE = ast.parse(SOURCE.read_text())
GUEST = next(node.value.value for node in TREE.body if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'GUEST' for t in node.targets))


class FakeCursor:
    def __init__(self, count=1, kinds=1, keys=1, exacts=1, changed=False,
                 invalid_identity=False, missing=False):
        self.counts = dict(n=count, kind_matches=Decimal(kinds),
                           key_matches=Decimal(keys), exact_matches=Decimal(exacts))
        self.changed = changed
        self.invalid_identity = invalid_identity
        self.missing = missing
        self.queries = []
        self.closed = False

    def execute(self, sql, args=()):
        self.queries.append((sql, args))
        if sql.startswith('SELECT '):
            if 'tabCCPC Center Mapping Scope' in sql:
                assert args == ('Department Only', 'DEPARTMENT_ONLY', 'Department Only',
                                'DEPARTMENT_ONLY', 'Cagayan Corn Products Corporation',
                                'Wet Mill Plant - CCPC')
            return
        assert sql in ('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ',
                       'START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY')

    def fetchall(self):
        sql = self.queries[-1][0]
        if 'CURRENT_USER()' in sql:
            return [dict(db='private_dev', principal='site_user@%',
                         hostname='pinned-db', server_id=12 if not self.invalid_identity else 13,
                         version='MariaDB 11')]
        if 'tabWithdrawal Slip' in sql:
            return [] if self.missing else [dict(
                name='WS-2026-00008', docstatus=0, status='Draft',
                company='Cagayan Corn Products Corporation',
                requesting_company='Cagayan Corn Products Corporation',
                department='Maintenance Department - CCPC',
                work_for_department='Maintenance Department - CCPC'
                if self.changed else 'Wet Mill Plant - CCPC')]
        if 'tabCCPC Center Mapping Scope' in sql:
            return [self.counts]
        raise AssertionError('unexpected synthetic SELECT')

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, **kwargs):
        self.cursor_obj = FakeCursor(**kwargs)
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def run_fake(**kwargs):
    conn = FakeConnection(**kwargs)
    mysql = types.ModuleType('MySQLdb')
    cursors = types.ModuleType('MySQLdb.cursors')
    cursors.DictCursor = object()
    mysql.cursors = cursors
    mysql.version_info = (2, 2, 7)
    mysql.connect = lambda **params: conn
    target = dict(db_host='mariadb', schema='private_dev', port=3306,
                  principal='site_user@%', db_ip='172.18.0.3', server_hostname='pinned-db',
                  server_id=12)
    prev_mysql = sys.modules.get('MySQLdb')
    prev_cursors = sys.modules.get('MySQLdb.cursors')
    output = io.StringIO()
    try:
        sys.modules['MySQLdb'] = mysql
        sys.modules['MySQLdb.cursors'] = cursors
        with mock.patch.object(Path, 'read_text', return_value=json.dumps({
                'db_host': 'mariadb', 'db_name': 'private_dev',
                'db_user': 'site_user', 'db_port': 3306, 'db_password': 'offline-only'})), \
                mock.patch.object(socket, 'getaddrinfo', return_value=[
                    (None, None, None, None, ('172.18.0.3', 3306))]):
            with contextlib.redirect_stdout(output):
                with self_exit() as catcher:
                    exec(compile(GUEST, '<offline synthetic guest>', 'exec'),
                         dict(TARGET=target, __name__='__main__'))
        code = catcher[0]
    finally:
        if prev_mysql is None: sys.modules.pop('MySQLdb', None)
        else: sys.modules['MySQLdb'] = prev_mysql
        if prev_cursors is None: sys.modules.pop('MySQLdb.cursors', None)
        else: sys.modules['MySQLdb.cursors'] = prev_cursors
    return code, output.getvalue().splitlines(), conn


@contextlib.contextmanager
def self_exit():
    result = [None]
    try:
        yield result
    except SystemExit as exc:
        result[0] = exc.code


class ScopeDiagnostics(unittest.TestCase):
    def expect(self, opts, status, output):
        result, lines, conn = run_fake(**opts)
        self.assertEqual(result, status)
        self.assertTrue(lines[-1].startswith(output), lines)
        self.assertTrue(conn.rolled_back)
        self.assertTrue(conn.closed)
        self.assertTrue(conn.cursor_obj.closed)
        self.assertFalse(any(x[0].upper().startswith(('UPDATE', 'DELETE', 'INSERT', 'REPLACE'))
                             for x in conn.cursor_obj.queries))
        self.assertFalse(any('private_dev' in l or 'site_user' in l or 'pinned-db' in l
                             for l in lines))
        # Reused operator host guard filters printed lines by this exact pattern.
        host_line = re.compile(r'(PASS|FAIL|STOP) \| [A-Za-z0-9 /-]{1,60} \| [A-Za-z0-9 ;.,-]{1,120}')
        self.assertTrue(all(host_line.fullmatch(line) for line in lines), lines)
        return lines

    def test_missing_scope_classified(self):
        x = self.expect(dict(count=0, kinds=0, keys=0, exacts=0), 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Wet Mill scope count | zero exact Company and Department records', x)

    def test_one_valid_scope_classified(self):
        x = self.expect({}, 0, 'PASS | OVERALL')
        self.assertIn('PASS | Wet Mill scope count | exactly one record', x)
        self.assertIn('PASS | Wet Mill selector key | required selector key confirmed', x)

    def test_one_wrong_selector_kind(self):
        x = self.expect(dict(kinds=0, exacts=0), 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Wet Mill selector kind | not Department Only', x)

    def test_one_wrong_selector_key(self):
        x = self.expect(dict(keys=0, exacts=0), 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Wet Mill selector key | selector key differs', x)

    def test_multiple_eligible_scopes_still_fail(self):
        x = self.expect(dict(count=2, kinds=2, keys=2, exacts=2), 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Wet Mill scope count | multiple exact Company and Department records', x)

    def test_multiple_mixed_scopes(self):
        x = self.expect(dict(count=3, kinds=2, keys=2, exacts=1), 1, 'FAIL | OVERALL')
        self.assertIn('FAIL | Wet Mill selector | one or more selectors differ', x)

    def test_changed_beneficiary_stops_before_scope(self):
        x = self.expect(dict(changed=True), 1, 'FAIL | OVERALL')
        self.assertFalse(any('scope count' in s for s in x))

    def test_wrong_database_identity_stops(self):
        self.expect(dict(invalid_identity=True), 1, 'STOP | SNAPSHOT')

    def test_missing_draft_stops(self):
        self.expect(dict(missing=True), 1, 'STOP | SNAPSHOT')

    def test_inconsistent_aggregate_stops(self):
        self.expect(dict(count=1, kinds=0, keys=1, exacts=1), 1, 'STOP | SNAPSHOT')


if __name__ == '__main__':
    unittest.main()
