"""Offline static source regression checks, using an exact pinned Frappe excerpt."""
import ast
import hashlib
from pathlib import Path
import unittest

from material_issue_child_delete_source_guard import (
    ChildSourceUnverified, PINNED_DOCUMENT_BLOB, PINNED_FRAPPE_COMMIT,
    PINNED_METHOD_AST_SHA256, EXPECTED_SCOPE, review_pinned_child_update_source,
)

FIXTURE = Path(__file__).parent / "fixtures" / "frappe_document_update_child_table_988e54f3.py.txt"
EXPECTED_FIXTURE_SHA256 = "4a971d4471dc82bdacd7232dc73454a5eff8fcefb30dc8b40a1bb9097f233d9f"


class PinnedChildSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = FIXTURE.read_text()

    def audit(self, source=None):
        return review_pinned_child_update_source(self.source if source is None else source)

    def test_exact_pinned_source_ast_passes_but_never_authorizes(self):
        output = self.audit()
        self.assertTrue(output["ast_matched_pinned_source"])
        self.assertEqual(output["frappe_commit"], PINNED_FRAPPE_COMMIT)
        self.assertEqual(output["document_blob"], PINNED_DOCUMENT_BLOB)
        for key in ("safe_to_stage", "safe_to_rehearse", "safe_to_commit",
                    "generated_sql_text_verified", "bound_arguments_verified",
                    "actual_affected_row_count_verified", "runtime_hook_or_driver_coverage_verified"):
            self.assertFalse(output[key], key)

    def test_fixture_hash_and_ast_hash_match_separately(self):
        self.assertEqual(hashlib.sha256(self.source.encode()).hexdigest(), EXPECTED_FIXTURE_SHA256)
        self.assertEqual(hashlib.sha256(ast.dump(ast.parse(self.source), include_attributes=False).encode()).hexdigest(),
                         PINNED_METHOD_AST_SHA256)

    def test_three_scope_predicates_are_explicit_source_assertions(self):
        self.assertEqual(EXPECTED_SCOPE, frozenset({
            "tbl.parent == str(self.name)", "tbl.parenttype == self.doctype",
            "tbl.parentfield == fieldname",
        }))

    def test_parent_predicate_removed_denied(self):
        self.reject_replace(".where(tbl.parent == str(self.name))", "")

    def test_parenttype_predicate_removed_denied(self):
        self.reject_replace(".where(tbl.parenttype == self.doctype)", "")

    def test_parentfield_predicate_removed_denied(self):
        self.reject_replace(".where(tbl.parentfield == fieldname)", "")

    def test_predicate_altered_to_global_where_true_denied(self):
        self.reject_replace(".where(tbl.parent == str(self.name))", ".where(1 == 1)")

    def test_wrong_parent_source_denied(self):
        self.reject_replace("str(self.name)", "str(self.owner)")

    def test_optional_retained_child_exclusion_removed_denied(self):
        self.reject_replace("\t\tif existing_row_names:\n\t\t\tqry = qry.where(tbl.name.notin(existing_row_names))",
                            "\t\tpass")

    def test_exclusion_inverted_denied(self):
        self.reject_replace("tbl.name.notin(existing_row_names)", "tbl.name.isin(existing_row_names)")

    def test_child_virtual_guard_removed_denied(self):
        self.reject_replace("\tif df.is_virtual:\n\t\treturn", "\tpass")

    def test_ignored_child_type_guard_removed_denied(self):
        self.reject_replace("df.options in (self.flags.ignore_children_type or ())", "False")

    def test_child_meta_virtual_guard_removed_denied(self):
        self.reject_replace("frappe.get_meta(df.options).is_virtual == 1", "False")

    def test_delete_replaced_by_select_denied(self):
        self.reject_replace(".delete()", ".select(tbl.name)")

    def test_qry_run_removed_denied(self):
        self.reject_replace("\t\tqry.run()", "\t\tpass")

    def test_qry_run_moved_out_of_scoped_guard_denied(self):
        self.reject_replace("\t\tqry.run()", "\tqry.run()")

    def test_extra_commit_or_unreviewed_sql_denied(self):
        for extra in ("\tfrappe.db.commit()\n", "\tfrappe.db.sql('DELETE FROM tabBin')\n"):
            with self.subTest(extra=extra):
                with self.assertRaises(ChildSourceUnverified):
                    self.audit(self.source + extra)

    def test_unreviewed_rename_or_extra_method_denied(self):
        self.reject_replace("def update_child_table", "def update_parent_table")
        with self.assertRaises(ChildSourceUnverified):
            self.audit(self.source + "\ndef something_else():\n\tpass\n")

    def test_comment_change_alone_does_not_affect_ast(self):
        self.assertTrue(self.audit(self.source.replace("# delete rows", "# reviewed rows"))[
            "ast_matched_pinned_source"])

    def test_untyped_and_invalid_python_denied(self):
        for source in (None, 0, "", "def update_child_table("):
            with self.subTest(source=source), self.assertRaises(ChildSourceUnverified):
                review_pinned_child_update_source(source)

    def test_no_frappe_import_runtime_execution_or_service_calls(self):
        source = (Path(__file__).parent / "material_issue_child_delete_source_guard.py").read_text()
        tree = ast.parse(source)
        imports = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertEqual(imports, set())
        for bad in ("import frappe", "import redis", "import MySQLdb", "subprocess", "docker",
                    "exec(", "eval(", "conn.commit(", "frappe.db.sql("):
            self.assertNotIn(bad, source)

    def reject_replace(self, old, new):
        self.assertIn(old, self.source, "The source fixture unexpectedly changed")
        with self.assertRaises(ChildSourceUnverified):
            self.audit(self.source.replace(old, new, 1))


if __name__ == "__main__":
    unittest.main()
