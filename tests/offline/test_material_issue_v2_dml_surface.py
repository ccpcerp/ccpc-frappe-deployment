"""Isolated, offline review of provisional v2 SQL mutation-table gate.

This module MUST NOT import ERPNext, reach Docker/SQL/Redis, or execute the
inert posting script. It parses pure function AST from exact source only.
"""
import ast
import os
from pathlib import Path
import re
import subprocess
import unittest

SCRIPT = Path(os.environ.get(
    'CCPC_V2_SCRIPT',
    Path(__file__).resolve().parent / 'scripts/development/operator/'
    'ccpc_material_issue_first_commit_review_only_v2_20261015.sh',
))


class Blocked(Exception):
    pass


def stop(message):
    raise Blocked(message)


class TestReviewOnlyDML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding='utf-8')
        cls.embed = cls.source.split("<<'PY'\n", 1)[1].rsplit('\nPY\n', 1)[0]
        cls.tree = ast.parse(cls.embed)

    def guard(self):
        # Take only reviewed binding assignments and the DML helper. No Frappe
        # imports, site initialization or database writes are evaluated.
        helper = [n for n in ast.walk(self.tree)
                  if isinstance(n, ast.FunctionDef) and n.name == 'review_dml_scope']
        self.assertEqual(len(helper), 1)
        assignments = [n for n in ast.walk(self.tree)
                       if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name)
                               and t.id in {'REVIEW_INSERT_TARGETS', 'REVIEW_UPDATE_TARGETS'}
                               for t in n.targets)]
        self.assertEqual(len(assignments), 2)
        local = {'stop': stop, 're': re, 'frozenset': frozenset}
        body = ast.fix_missing_locations(ast.Module(body=assignments + helper, type_ignores=[]))
        exec(compile(body, '<static-dml-guard>', 'exec'), local)
        return local['review_dml_scope'], local

    def test_exact_script_is_deliberately_inert(self):
        self.assertTrue(self.source.startswith('#!/usr/bin/env bash\n'))
        self.assertLess(self.source.index('\nexit 1\n'), self.source.index('docker inspect'))
        self.assertLess(self.source.index('\nexit 1\n'), self.source.index('docker exec'))
        self.assertEqual(subprocess.run(['bash', '-n', str(SCRIPT)],
                                        capture_output=True, text=True).returncode, 0)
        ast.parse(self.embed)

    def test_only_provisional_synthetic_dml_tables_permitted(self):
        guard, _ = self.guard()
        for sql in (
            'INSERT INTO `tabStock Entry` (`name`) VALUES (%s)',
            'INSERT INTO `tabStock Entry Detail` (`parent`) VALUES (%s)',
            'INSERT INTO `tabStock Ledger Entry` (`name`) VALUES (%s)',
            'INSERT INTO `tabGL Entry` (`name`) VALUES (%s)',
            'INSERT INTO `tabVersion` (`ref_doctype`) VALUES (%s)',
            'UPDATE `tabWithdrawal Slip` SET `status`=%s WHERE `name`=%s',
            'UPDATE `tabWithdrawal Slip Item` SET `issued_qty`=%s WHERE `name`=%s',
            'UPDATE `tabBin` SET `actual_qty`=%s WHERE `name`=%s',
        ):
            with self.subTest(sql=sql):
                self.assertIsNone(guard(sql))

    def test_unscoped_or_unrelated_dml_fails_closed(self):
        guard, _ = self.guard()
        for sql in (
            'INSERT INTO `tabPayment Entry` (`name`) VALUES (%s)',
            'UPDATE `tabSales Invoice` SET `status`=%s WHERE `name`=%s',
            'UPDATE `tabBin` SET `actual_qty`=0',
            'DELETE FROM `tabStock Ledger Entry` WHERE `name`=%s',
            'INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s,1)',
            'UPDATE `tabSeries` SET `current`=`current`+1 WHERE `name`=%s',
            'INSERT IGNORE INTO `tabGL Entry` (`name`) VALUES (%s)',
            'INSERT INTO tabGL Entry (name) VALUES (%s)',
            'UPDATE `tabGL Entry` JOIN `tabBin` SET `debit`=0 WHERE 1',
            'REPLACE INTO `tabBin` (`name`) VALUES (%s)',
        ):
            with self.subTest(sql=sql):
                if sql.startswith('REPLACE'):
                    # The high-level limited_sql rejects this unknown verb.
                    self.assertNotIn('REPLACE', self.source.split('def limited_sql(', 1)[1]
                                     .split('return original_sql', 1)[0]
                                     .split("if not re.match(", 1)[1].split('q):', 1)[0])
                else:
                    with self.assertRaises(Blocked):
                        guard(sql)

    def test_sql_proxy_invokes_dml_gate(self):
        section = self.source.split('def limited_sql(query,*args,**kwargs):', 1)[1]
        self.assertLess(section.index('review_dml_scope(query)'),
                        section.index('return original_sql(query,*args,**kwargs)'))
        self.assertNotIn("'tabSeries'", self.source.split('REVIEW_INSERT_TARGETS', 1)[1]
                         .split('def review_dml_scope', 1)[0])

    def test_blocked_fields_do_not_create_permission_to_commit(self):
        self.assertIn('NO-GO: Review-only v2', self.source.split('\nexit 1\n', 1)[0])
        self.assertIn('sql_commit_phase', self.source)
        self.assertLess(self.source.index('NO-GO: Review-only v2'),
                        self.source.index('CCPC_FIRST_ISSUE_EXECUTION_APPROVED'))


if __name__ == '__main__':
    unittest.main()
