#!/usr/bin/env python3
"""Synthetic-only tests for fixed-label archived Auth SQL operation classification.

No encrypted archive, age identity, running site, database, or network is used.
"""
import gzip
import unittest

import ccpc_archived_auth_operation_shape_probe as probe


SCHEMA = b"""CREATE TABLE `__Auth` (
  `doctype` varchar(140),
  `name` varchar(140),
  `fieldname` varchar(140),
  `password` text,
  `encrypted` tinyint(1)
);
"""


def check_sql(statement):
    return probe.scan_sql(gzip.compress(SCHEMA + statement + b"\n"))


class OperationShapeTests(unittest.TestCase):
    def test_supported_canonical_unencrypted(self):
        self.assertEqual(check_sql(
            b"INSERT INTO `__Auth` VALUES ('X','Y','Z','masked',0);"),
            'NO_ENCRYPTED_AUTH_ROWS')

    def test_supported_canonical_encrypted_rejected_by_status(self):
        self.assertEqual(check_sql(
            b"INSERT INTO `__Auth` VALUES ('X','Y','Z','masked',1);"),
            'ENCRYPTED_ROWS_PRESENT')

    def test_alternative_shapes_fail_closed_with_only_fixed_labels(self):
        cases = (
            (b"INSERT INTO `__Auth` (`doctype`,`name`) VALUES ('x','y');",
             'INCONCLUSIVE_SQL_INSERT_COLUMN_LIST'),
            (b"INSERT INTO `__Auth`  VALUES ('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_VALUES_NONSTANDARD_BEFORE_UPPERCASE_VALUES_SPACE_AFTER'),
            (b"INSERT INTO `__Auth` values ('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_VALUES_STANDARD_BEFORE_NONSTANDARD_CASE_SPACE_AFTER'),
            (b"INSERT INTO `__Auth` SELECT 1;",
             'INCONCLUSIVE_SQL_INSERT_SELECT'),
            (b"INSERT INTO `__Auth` SET encrypted=0;",
             'INCONCLUSIVE_SQL_INSERT_SET'),
            (b"INSERT INTO `__Auth` ON DUPLICATE KEY UPDATE encrypted=0;",
             'INCONCLUSIVE_SQL_INSERT_OTHER'),
            (b"REPLACE INTO `__Auth` VALUES ('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_REPLACE'),
            (b"UPDATE `__Auth` SET encrypted=0;",
             'INCONCLUSIVE_SQL_UPDATE'),
            (b"INSERT INTO __Auth VALUES ('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_UNQUOTED_TABLE'),
            (b"INSERT IGNORE INTO `__Auth` VALUES ('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_INSERT_IGNORE'),
        )
        for statement, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(probe.Classified) as context:
                    check_sql(statement)
                self.assertEqual(context.exception.args, (label,))

    def test_values_variant_features_are_fixed_and_independent(self):
        cases = (
            (b"INSERT INTO `__Auth` VALUES('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_VALUES_STANDARD_BEFORE_UPPERCASE_VALUES_NO_SPACE_AFTER'),
            (b"INSERT INTO `__Auth` VALUES\t('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_VALUES_STANDARD_BEFORE_UPPERCASE_VALUES_TAB_AFTER'),
            (b"INSERT INTO `__Auth` VALUES\n('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_VALUES_STANDARD_BEFORE_UPPERCASE_VALUES_LINEBREAK_AFTER'),
            (b"INSERT INTO `__Auth`  values('x','y','z','masked',0);",
             'INCONCLUSIVE_SQL_VALUES_NONSTANDARD_BEFORE_NONSTANDARD_CASE_NO_SPACE_AFTER'),
            (b"INSERT INTO `__Auth` VALUES;",
             'INCONCLUSIVE_SQL_VALUES_STANDARD_BEFORE_UPPERCASE_VALUES_OTHER_AFTER'),
        )
        for statement, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(probe.Classified) as context:
                    check_sql(statement)
                self.assertEqual(context.exception.args, (label,))

    def test_canonical_malformed_tuples_still_fail_closed(self):
        with self.assertRaises(probe.Classified) as context:
            check_sql(b"INSERT INTO `__Auth` VALUES ('x','y','z','masked',2);")
        self.assertEqual(context.exception.args, ('INCONCLUSIVE_SQL_FLAG_FORMAT',))

    def test_non_auth_operation_is_not_misclassified(self):
        self.assertEqual(check_sql(b"UPDATE `Other` SET x=1;"),
                         'NO_ENCRYPTED_AUTH_ROWS')


if __name__ == '__main__':
    unittest.main()
