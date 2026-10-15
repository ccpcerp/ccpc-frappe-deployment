"""Credential-free AST audit of one pinned Frappe method; never renders SQL.

This checks the exact reviewed *source shape*. It never imports Frappe, runs
Document.update_child_table, queries a DB, or approves any live experiment.
"""

import ast
import hashlib


PINNED_FRAPPE_COMMIT = "988e54f3c4c291e2077a83809663f123731abe76"
PINNED_DOCUMENT_BLOB = "e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a"
PINNED_METHOD_AST_SHA256 = "feff34221f70388a6f5802d55f167e6937cd1832aef329404b5ab9a8352d96a6"
EXPECTED_SCOPE = frozenset({
    "tbl.parent == str(self.name)",
    "tbl.parenttype == self.doctype",
    "tbl.parentfield == fieldname",
})


class ChildSourceUnverified(ValueError):
    """Unpinned, changed, malformed or ambiguous child-delete source."""


def review_pinned_child_update_source(source: str) -> dict:
    """Prove only that a fixture matches the reviewed AST, NOT actual effects.

    Any source revision requires a fresh, independent review and pin update.
    A positive static match is NEVER authorization to execute the method.
    """
    if type(source) is not str or not source.strip():
        raise ChildSourceUnverified("Expected nonempty method source text")
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError) as exc:
        raise ChildSourceUnverified("Invalid method source") from exc
    fingerprint = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
    if fingerprint != PINNED_METHOD_AST_SHA256:
        raise ChildSourceUnverified("Method AST differs from the pinned GitHub source")
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ChildSourceUnverified("Expected exactly one pinned method")
    function = tree.body[0]
    if function.name != "update_child_table":
        raise ChildSourceUnverified("Wrong pinned method")
    comparisons = {ast.unparse(node) for node in ast.walk(function) if isinstance(node, ast.Compare)}
    if not EXPECTED_SCOPE.issubset(comparisons):
        raise ChildSourceUnverified("Missing scoped child-table predicate")
    all_calls = [ast.unparse(node) for node in ast.walk(function) if isinstance(node, ast.Call)]
    if not any("tbl.name.notin(existing_row_names)" == call for call in all_calls):
        raise ChildSourceUnverified("Missing conditional retained-child-name exclusion")
    if "qry.run()" not in all_calls or not any(call.endswith(".delete()") for call in all_calls):
        raise ChildSourceUnverified("Expected query-builder DELETE and one run")
    return {
        "frappe_commit": PINNED_FRAPPE_COMMIT,
        "document_blob": PINNED_DOCUMENT_BLOB,
        "ast_matched_pinned_source": True,
        "source_predicate_names": ("parent", "parenttype", "parentfield"),
        "retained_child_name_exclusion_in_source": True,
        "virtual_child_guards_in_pinned_source": True,
        "generated_sql_text_verified": False,
        "bound_arguments_verified": False,
        "actual_affected_row_count_verified": False,
        "runtime_hook_or_driver_coverage_verified": False,
        "database_rollback_and_external_effects_verified": False,
        "safe_to_stage": False,
        "safe_to_rehearse": False,
        "safe_to_commit": False,
        "decision": "NO_GO_STATIC_SOURCE_ONLY",
    }
