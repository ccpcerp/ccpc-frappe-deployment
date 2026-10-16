"""Offline source-pinned reachability tests. No ERPNext/Frappe/Redis/SQL imports.

Executes selected *exact, GitHub-snapshotted function excerpts* with synthetic
dependencies. This is NOT a live application test or a posting approval.
"""
import ast
import hashlib
import json
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

FIXTURE = Path(__file__).resolve().parent / "fixtures/material_issue_reachability_source_pins_20261016.json"
FIXTURE_BLOB = "7ca589594fb9ed818da75476ddbe68b471eef444"
EXPECTED = {
    "ccpc_issue": "771d27781f8d933fd243415e8286976fbdd1a861",
    "stock_on_submit": "dfe6aeef0f76fbf76af8caeb787a321c773f2bbf",
    "repost_decision": "3d77e45058d47a264009c2a3d2b35c633ce9e363",
    "repost_repeat_guard": "3d77e45058d47a264009c2a3d2b35c633ce9e363",
    "repost_create": "3d77e45058d47a264009c2a3d2b35c633ce9e363",
    "repost_itemwise_create": "3d77e45058d47a264009c2a3d2b35c633ce9e363",
    "riv_on_submit": "66a0f707504ae6958868795ae393c1adcd35765f",
    "riv_worker_repost": "66a0f707504ae6958868795ae393c1adcd35765f",
    "cache_clear": "fc4cb7e0d15c893fd0baf4d289de1e3deb70950d",
    "notify_update": "e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a",
    "webhook_queue": "804560319ffb16c60798d807064a02defb336443",
}


def snapshots():
    data = FIXTURE.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    assert hashlib.sha1(header + data).hexdigest() == FIXTURE_BLOB, "pinned fixture drift"
    return {entry["key"]: entry for entry in json.loads(data)["snapshots"]}


def function(key, globals_=None):
    record = snapshots()[key]
    tree = ast.parse(textwrap.dedent(record["source"]))
    assert len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef), key
    node = tree.body[0]
    assert node.name == record["fn"], key
    node.decorator_list = []  # avoid executing any framework decorator
    names = {"__name__": "ccpc_synthetic_source_excerpts", "StockController": object}
    names.update(globals_ or {})
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<pinned-%s>" % key, "exec"), names)
    return names[node.name]


class SourcePinnedReachability(unittest.TestCase):
    def test_01_pin_manifest_and_syntax(self):
        records = snapshots()
        self.assertEqual(set(records), set(EXPECTED))
        for key, entry in records.items():
            with self.subTest(key=key):
                self.assertEqual(entry["blob"], EXPECTED[key])
                self.assertRegex(entry["ref"], r"^[0-9a-f]{40}$")
                self.assertGreater(entry["start_line"], 0)
                self.assertIn("def " + entry["fn"] + "(", entry["source"])
                self.assertIsInstance(function(key, {}), type(lambda: None))

    def test_02_snippets_contain_no_import_statements(self):
        for key, entry in snapshots().items():
            tree = ast.parse(textwrap.dedent(entry["source"]))
            self.assertFalse(any(isinstance(n, (ast.Import, ast.ImportFrom, ast.Global,
                                               ast.Nonlocal)) for n in ast.walk(tree)), key)

    def riv(self, in_test=False, doc_skip=False, global_skip=False):
        events = []
        frappe = NS(in_test=in_test, flags=NS(dont_execute_stock_reposts=global_skip))
        f = function("riv_on_submit", {"frappe": frappe,
                                       "repost": lambda d: events.append("repost")})
        f(NS(flags=NS(dont_run_in_test=doc_skip)))
        return events

    def test_03_riv_normal_submit_no_inline_worker(self):
        self.assertEqual(self.riv(), [])

    def test_04_riv_test_mode_may_run_inline(self):
        self.assertEqual(self.riv(in_test=True), ["repost"])

    def test_05_riv_test_flags_stop_inline(self):
        self.assertEqual(self.riv(in_test=True, doc_skip=True), [])
        self.assertEqual(self.riv(in_test=True, global_skip=True), [])

    def repeat(self, rows):
        db = NS(get_all=Mock(return_value=[NS(**r) for r in rows]))
        result = function("repost_repeat_guard", {"frappe": NS(db=db)})(
            NS(doctype="Stock Entry", name="SYNTHETIC"))
        db.get_all.assert_called_once()
        return result

    def test_06_no_rows_no_repeat(self):
        self.assertFalse(self.repeat([]))

    def test_07_distinct_pairs_no_repeat(self):
        self.assertFalse(self.repeat([dict(item_code="A", warehouse="W", stock_queue="[[1,1]]"),
                                      dict(item_code="B", warehouse="W", stock_queue="[[1,1]]")]))

    def test_08_repeat_empty_queue_no_trigger(self):
        self.assertFalse(self.repeat([dict(item_code="A", warehouse="W", stock_queue="[]")] * 2))

    def test_09_repeat_queue_triggers(self):
        self.assertTrue(self.repeat([dict(item_code="A", warehouse="W", stock_queue="[[1,1]]")] * 2))

    def decision(self, future=False, repeat=False, itemwise=False, force=False, status=1):
        events = []
        class AttrDict(dict):
            __getattr__ = dict.get
        frappe = NS(_dict=lambda value: AttrDict(value),
                    get_single_value=lambda *args: int(itemwise))
        f = function("repost_decision", {
            "frappe": frappe,
            "future_sle_exists": lambda args, for_update=False: events.append("future") or future,
            "repost_required_for_queue": lambda doc: events.append("repeat") or repeat,
            "create_repost_item_valuation_entry": lambda args: events.append("transaction_repost"),
            "create_item_wise_repost_entries": lambda **kw: events.append("itemwise_repost"),
        })
        f(NS(posting_date="2026-10-16", posting_time="10:00:00",
             doctype="Stock Entry", name="SYNTHETIC", company="TEST", docstatus=status),
          force=force)
        return events

    def test_10_no_future_no_repost(self):
        self.assertEqual(self.decision(), ["future", "repeat"])

    def test_11_future_repost_record_branch(self):
        self.assertEqual(self.decision(future=True), ["future", "transaction_repost"])

    def test_12_repeat_repost_record_branch(self):
        self.assertEqual(self.decision(repeat=True), ["future", "repeat", "transaction_repost"])

    def test_13_itemwise_repost_record_branch(self):
        self.assertEqual(self.decision(future=True, itemwise=True), ["future", "itemwise_repost"])

    def test_14_force_or_cancel_path_differs_from_normal(self):
        self.assertEqual(self.decision(force=True), ["transaction_repost"])
        self.assertEqual(self.decision(status=2), ["transaction_repost"])
        self.assertEqual(self.decision(status=1), ["future", "repeat"])

    def test_15_repost_creation_sources_submit_documents_not_inline_worker(self):
        for key in ("repost_create", "repost_itemwise_create"):
            node = ast.parse(textwrap.dedent(snapshots()[key]["source"]))
            calls = [n.func.attr for n in ast.walk(node) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)]
            self.assertIn("submit", calls)
            self.assertNotIn("repost", calls)

    def test_16_worker_has_commits_but_stock_submit_order_is_separate(self):
        worker = ast.parse(textwrap.dedent(snapshots()["riv_worker_repost"]["source"]))
        commits = [n for n in ast.walk(worker) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute) and n.func.attr == "commit"]
        self.assertGreaterEqual(len(commits), 2)
        stock = ast.parse(textwrap.dedent(snapshots()["stock_on_submit"]["source"]))
        calls = [n.func.attr for n in ast.walk(stock) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and
                 n.func.attr in ("update_stock_ledger", "make_gl_entries",
                                 "repost_future_sle_and_gle")]
        self.assertEqual(calls, ["update_stock_ledger", "make_gl_entries",
                                 "repost_future_sle_and_gle"])

    def cache(self):
        events, after_c, after_r = [], [], []
        frappe = NS(client_cache=NS(erase_persistent_caches=lambda **k: events.append("erase")),
                    local=NS(valid_columns={"Withdrawal Slip": 1}),
                    db=NS(after_commit=NS(add=after_c.append),
                          after_rollback=NS(add=after_r.append)))
        f = function("cache_clear", {"frappe": frappe,
                    "clear_controller_cache": lambda x: events.append("controller"),
                    "_clear_doctype_cache_from_redis": lambda x: events.append("redis")})
        f("Withdrawal Slip")
        return events, after_c, after_r

    def test_17_cache_clears_immediately_and_registers_both_callbacks(self):
        events, ac, ar = self.cache()
        self.assertEqual(events, ["controller", "erase", "redis"])
        self.assertEqual((len(ac), len(ar)), (1, 1))

    def test_18_cache_afterrollback_and_aftercommit_are_separate(self):
        events, ac, ar = self.cache()
        ar[0]()
        self.assertEqual(events.count("redis"), 2)
        ac[0]()
        self.assertEqual(events.count("redis"), 3)

    def test_19_document_notifications_are_after_commit(self):
        output = []
        frappe = NS(flags=NS(in_import=False, in_patch=False, in_migrate=False,
                              in_install=False),
                    publish_realtime=lambda *a, **kw: output.append((a[0], kw["after_commit"])),
                    session=NS(user="synthetic"))
        f = function("notify_update", {"frappe": frappe})
        f(NS(modified="synthetic", doctype="Stock Entry", name="SYNTHETIC",
             meta=NS(get=lambda k: False)))
        self.assertEqual(output, [("doc_update", True), ("list_update", True)])

    def test_20_import_mode_suppresses_notify(self):
        output = []
        frappe = NS(flags=NS(in_import=True, in_patch=False, in_migrate=False,
                              in_install=False),
                    publish_realtime=lambda *a, **kw: output.append(a))
        f = function("notify_update", {"frappe": frappe})
        f(NS(modified="synthetic"))
        self.assertEqual(output, [])

    def test_21_webhook_queue_registers_aftercommit_only_once(self):
        callbacks, local = [], NS()
        frappe = NS(local=local, db=NS(after_commit=NS(add=callbacks.append)),
                    _dict=lambda **kw: kw)
        f = function("webhook_queue", {
            "frappe": frappe, "flush_webhook_execution_queue": lambda: None})
        f(NS(name="WEBHOOK"), NS(name="SYNTHETIC"))
        f(NS(name="WEBHOOK"), NS(name="SYNTHETIC"))
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(len(local._webhook_queue), 2)

    def test_22_ccpc_issue_has_insert_submit_no_explicit_commit(self):
        tree = ast.parse(textwrap.dedent(snapshots()["ccpc_issue"]["source"]))
        calls = [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)]
        self.assertIn("insert", calls)
        self.assertIn("submit", calls)
        self.assertNotIn("commit", calls)
        self.assertNotIn("rollback", calls)


if __name__ == "__main__":
    unittest.main()
