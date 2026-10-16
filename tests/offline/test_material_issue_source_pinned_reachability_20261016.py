"""Offline source-pinned reachability tests. No ERPNext/Frappe/Redis/SQL imports.

Executes selected *exact, GitHub-snapshotted function excerpts* with synthetic
dependencies. This is NOT a live application test or a posting approval.
"""
import ast
import hashlib
import json
import hmac
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

FIXTURE = Path(__file__).resolve().parent / "fixtures/material_issue_reachability_source_pins_20261016.json"
FIXTURE_BLOB = "7ca589594fb9ed818da75476ddbe68b471eef444"
FIXTURE_SHA256 = "57344e05f07c2f31445e4140ef6bf543cd97660fb34aa2c18db8dd9443f38bb9"
MAX_FIXTURE_BYTES = 65536

# Only six functions have approved isolated mock executions; all others AST-only.
EXECUTABLE_KEYS = frozenset({"riv_on_submit", "repost_repeat_guard", "repost_decision",
                             "cache_clear", "notify_update", "webhook_queue"})
SAFE_BUILTINS = {"bool": bool, "len": len, "set": set, "hasattr": hasattr, "getattr": getattr,
                 "isinstance": isinstance, "Exception": Exception, "super": super}
BANNED_NAMES = frozenset({"__builtins__", "__import__", "open", "eval", "exec",
                          "compile", "globals", "locals", "vars", "breakpoint",
                          "input", "dir", "help", "exit", "quit"})
BANNED_AST = (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.AsyncFunctionDef,
              ast.Await, ast.ClassDef, ast.Delete, ast.Yield, ast.YieldFrom, ast.NamedExpr)


class FixtureIntegrityError(ValueError):
    """Fail-closed, optimization-independent fixture or AST validation error."""

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


def _parse_excerpt(entry):
    key = entry["key"]
    try:
        src = textwrap.dedent(entry["source"])
        tree = ast.parse(src, filename="<trusted-CCPC-excerpt:%s>" % key)
    except (SyntaxError, TypeError, KeyError) as error:
        raise FixtureIntegrityError("unparseable pinned source: " + key) from error
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise FixtureIntegrityError("non-single function excerpt: " + key)
    fn = tree.body[0]
    if fn.name != entry["fn"] or fn.decorator_list:
        raise FixtureIntegrityError("decorated or mismatched excerpt: " + key)
    # Function defaults and annotations run at DEFINITION time, before the
    # tested function is ever called. Explicitly admit only the pinned forms.
    defaults = [*fn.args.defaults, *(x for x in fn.args.kw_defaults if x is not None)]
    if any(not isinstance(value, ast.Constant) for value in defaults):
        raise FixtureIntegrityError("executable function default in " + key)
    arguments = (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)
    annotations = [arg.annotation for arg in arguments if arg.annotation is not None]
    if fn.returns is not None:
        annotations.append(fn.returns)
    if any(not isinstance(value, ast.Name) or value.id not in ("StockController", "bool")
           for value in annotations):
        raise FixtureIntegrityError("executable or unexpected annotation in " + key)
    # Validation happens before even the first selected function is compiled.
    # Not a general Python sandbox; these snapshots must remain pinned and reviewed.
    for node in ast.walk(tree):
        if isinstance(node, BANNED_AST):
            raise FixtureIntegrityError("unsafe AST node in " + key)
        if isinstance(node, ast.Name) and (node.id in BANNED_NAMES or node.id.startswith("__")):
            raise FixtureIntegrityError("unsafe name in " + key)
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise FixtureIntegrityError("unsafe attribute in " + key)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if (len(node.args) < 2 or not isinstance(node.args[1], ast.Constant)
                    or node.args[1].value != "_webhook_queue"):
                raise FixtureIntegrityError("dynamic attribute access in " + key)
    return fn


def snapshots():
    # A true byte cap, not a read-all-then-check and not an assert removed by -O.
    with FIXTURE.open("rb") as stream:
        data = stream.read(MAX_FIXTURE_BYTES + 1)
    if len(data) > MAX_FIXTURE_BYTES:
        raise FixtureIntegrityError("oversize pinned fixture")
    if not hmac.compare_digest(hashlib.sha256(data).hexdigest(), FIXTURE_SHA256):
        raise FixtureIntegrityError("SHA256 pinned fixture drift")
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    if not hmac.compare_digest(hashlib.sha1(header + data).hexdigest(), FIXTURE_BLOB):
        raise FixtureIntegrityError("Git blob pinned fixture drift")
    try:
        manifest = json.loads(data)
        entries = manifest["snapshots"]
    except (ValueError, KeyError, TypeError) as error:
        raise FixtureIntegrityError("malformed pinned fixture") from error
    if (not isinstance(entries, list) or len(entries) != len(EXPECTED)
            or any(not isinstance(e, dict) or not isinstance(e.get("key"), str) for e in entries)):
        raise FixtureIntegrityError("unexpected fixture shape")
    result = {}
    for entry in entries:
        key = entry["key"]
        if (key not in EXPECTED or key in result or entry.get("blob") != EXPECTED[key]
                or not isinstance(entry.get("ref"), str) or len(entry["ref"]) != 40
                or not isinstance(entry.get("source"), str)):
            raise FixtureIntegrityError("unknown or conflicting fixture item")
        _parse_excerpt(entry)
        result[key] = entry
    if set(result) != set(EXPECTED):
        raise FixtureIntegrityError("missing fixture item")
    return result


def function(key, globals_=None):
    if key not in EXECUTABLE_KEYS:
        raise FixtureIntegrityError("function not allowlisted for offline execution")
    record = snapshots()  # Always validate entire fixture before any exec.
    node = _parse_excerpt(record[key])
    names = {"__name__": "ccpc_offline_pinned_source",
             "__builtins__": SAFE_BUILTINS, "StockController": object}
    names.update(globals_ or {})
    # Disallow overriding restricted __builtins__ and the annotation placeholder.
    names["__builtins__"] = SAFE_BUILTINS
    names["StockController"] = object
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 "<pinned-offline:%s>" % key, "exec"), names)
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
                self.assertIsInstance(_parse_excerpt(entry), ast.FunctionDef)
                if key in EXECUTABLE_KEYS:
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
        rollback_events, _, rollback_callbacks = self.cache()
        rollback_callbacks[0]()  # synthetic full-rollback callback ONLY
        self.assertEqual(rollback_events.count("redis"), 2)
        commit_events, commit_callbacks, _ = self.cache()
        commit_callbacks[0]()  # separate synthetic committed transaction ONLY
        self.assertEqual(commit_events.count("redis"), 2)

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


    def test_23_nonallowlisted_worker_cannot_be_executed(self):
        for key in set(EXPECTED) - EXECUTABLE_KEYS:
            with self.subTest(key=key), self.assertRaises(FixtureIntegrityError):
                function(key, {})

    def test_24_integrity_rejects_mutated_fixture_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "pins.json"
            bad.write_bytes(FIXTURE.read_bytes().replace(b'"cache_clear"', b'"cache_clear_tampered"'))
            with patch.dict(globals(), {"FIXTURE": bad}):
                with self.assertRaisesRegex(FixtureIntegrityError, "SHA256"):
                    function("riv_on_submit", {})

    def test_25_optimized_python_rejects_tampered_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "pins.json"
            bad.write_bytes(FIXTURE.read_bytes() + b" ")
            code = (
                "import importlib.util, pathlib, sys; "
                "p=pathlib.Path(sys.argv[1]); "
                "sp=importlib.util.spec_from_file_location('ccpc_fixture',p); "
                "m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); "
                "m.FIXTURE=pathlib.Path(sys.argv[2]); "
                "m.snapshots()"
            )
            result = subprocess.run([sys.executable, "-O", "-I", "-B", "-S", "-c",
                                     code, str(Path(__file__).resolve()), str(bad)],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, timeout=8)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FixtureIntegrityError", result.stderr)
            self.assertNotIn("Traceback", result.stdout)

    def test_26_optimized_python_accepts_original_fixture(self):
        code = (
            "import importlib.util,pathlib,sys; "
            "p=pathlib.Path(sys.argv[1]); "
            "sp=importlib.util.spec_from_file_location('ccpc_fixture',p); "
            "m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); "
            "print(len(m.snapshots()))"
        )
        result = subprocess.run([sys.executable, "-O", "-I", "-B", "-S", "-c", code,
                                 str(Path(__file__).resolve())], capture_output=True,
                                text=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "11\n")

    def adversarial_ast(self, change):
        # Red-team a copy while recalculating *both* fixture digests. This checks
        # preflight AST safety independent of content-digest mismatch rejection.
        manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))
        record = next(x for x in manifest["snapshots"] if x["key"] == "riv_on_submit")
        record["source"] = change
        data = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "pins.json"
            bad.write_bytes(data)
            header = b"blob " + str(len(data)).encode() + b"\0"
            with patch.dict(globals(), {"FIXTURE": bad,
                                        "FIXTURE_BLOB": hashlib.sha1(header + data).hexdigest(),
                                        "FIXTURE_SHA256": hashlib.sha256(data).hexdigest()}):
                with self.assertRaises(FixtureIntegrityError):
                    function("cache_clear", {})  # ensures full-fixture preflight

    def test_27_ast_rejects_import_even_with_recomputed_digests(self):
        self.adversarial_ast("def on_submit(self):\n    import os\n")

    def test_28_ast_rejects_exec_even_with_recomputed_digests(self):
        self.adversarial_ast("def on_submit(self):\n    exec('raise Exception()')\n")

    def test_29_ast_rejects_dunder_even_with_recomputed_digests(self):
        self.adversarial_ast("def on_submit(self):\n    return self.__class__\n")

    def test_30_ast_rejects_dynamic_getattr_even_with_recomputed_digests(self):
        self.adversarial_ast("def on_submit(self):\n    return getattr(self, x)\n")

    def test_31_safe_builtin_scope_explicit(self):
        self.assertNotIn("__import__", SAFE_BUILTINS)
        self.assertNotIn("open", SAFE_BUILTINS)
        self.assertNotIn("exec", SAFE_BUILTINS)
        self.assertTrue(EXECUTABLE_KEYS.issubset(EXPECTED))

    def test_32_callback_tests_do_not_fire_both_for_one_transaction(self):
        events, commit_callbacks, rollback_callbacks = self.cache()
        self.assertEqual(events.count("redis"), 1)
        # These are separate possibilities; the test never runs both.
        self.assertEqual(len(commit_callbacks), 1)
        self.assertEqual(len(rollback_callbacks), 1)

    def test_33_oversized_fixture_fails_before_json_and_ast(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "large.json"
            bad.write_bytes(b"A" * (MAX_FIXTURE_BYTES + 300))
            with patch.dict(globals(), {"FIXTURE": bad}):
                with self.assertRaisesRegex(FixtureIntegrityError, "oversize"):
                    snapshots()


    def test_34_ast_rejects_executable_default_pre_compile(self):
        self.adversarial_ast("def on_submit(self, x=side_effect()):\n    return x\n")

    def test_35_ast_rejects_executable_annotation_pre_compile(self):
        self.adversarial_ast("def on_submit(self: side_effect()):\n    return None\n")


if __name__ == "__main__":
    unittest.main()
