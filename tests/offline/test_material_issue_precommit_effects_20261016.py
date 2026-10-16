"""Credential-free E1 ordering checks of pinned-source-derived models, not integration tests.

The extracted behaviors are intentionally isolated. No import of Frappe, Redis,
Docker, SQL clients, HTTP clients or CCPC app. See GitHub E0 source map for pins.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import Mock

# These reduced excerpts model selected paths of pinned Frappe/CCPC source;
# they are not a running-site/build attestation. Check E0 document for exact refs.
CACHE_EXCERPT = '''
def clear_doctype_cache(doctype=None):
    clear_controller_cache(doctype)
    frappe.client_cache.erase_persistent_caches(doctype=doctype)

    if doctype:
        frappe.local.valid_columns.pop(doctype, None)
    else:
        frappe.local.valid_columns = {}

    _clear_doctype_cache_from_redis(doctype)
    if hasattr(frappe.db, "after_commit"):
        frappe.db.after_commit.add(lambda: _clear_doctype_cache_from_redis(doctype))
        frappe.db.after_rollback.add(lambda: _clear_doctype_cache_from_redis(doctype))
'''
DB_EXCERPT = '''
def commit(self, *, chain=False):
    if self._disable_transaction_control:
        return
    self.before_rollback.reset()
    self.after_rollback.reset()
    self.before_commit.run()
    if chain:
        self.sql("commit and chain")
    else:
        self.sql("commit")
        self.begin()
    self.value_cache.clear()
    self.after_commit.run()

def rollback(self, *, save_point=None, chain=False):
    if save_point:
        self.sql(f"rollback to savepoint {save_point}")
        self.value_cache.clear()
    elif not self._disable_transaction_control:
        self.before_commit.reset()
        self.after_commit.reset()
        self.before_rollback.run()
        if chain:
            self.sql("rollback and chain")
            self.value_cache.clear()
        else:
            self.sql("rollback")
            self.begin()
        self.value_cache.clear()
        self.after_rollback.run()
'''
# This reproduces only the branching of Frappe publish_realtime's documented
# after_commit and task-progress semantics; it is a synthetic callback model.
REALTIME_MODEL = '''
def publish_realtime(event="test", message=None, task_id=None, after_commit=False):
    if message is None:
        message = {}
    if task_id:
        after_commit = False
        message["task_id"] = task_id
    if after_commit:
        if not hasattr(local, "_realtime_log"):
            local._realtime_log = []
            db.after_commit.add(flush_realtime_log)
            db.after_rollback.add(clear_realtime_log)
        params = [event, message, "all"]
        if params not in local._realtime_log:
            local._realtime_log.append(params)
    else:
        emit_via_redis(event, message, "all")

def flush_realtime_log():
    if not hasattr(local, "_realtime_log"):
        return
    for args in local._realtime_log:
        emit_via_redis(*args)
    clear_realtime_log()

def clear_realtime_log():
    if hasattr(local, "_realtime_log"):
        del local._realtime_log
'''
ISSUE_EXCERPT = '''
def issue_withdrawal_slip(withdrawal_slip):
    _require_stockroom_user()
    locked = _lock_withdrawal_slip(withdrawal_slip)
    slip = _get_issuable_slip(withdrawal_slip, locked)
    _assert_no_submitted_material_issue(slip.name)
    drafts = _get_existing_draft_names(slip.name)
    if drafts:
        raise ValueError("Existing draft blocks issue")
    stock_entry = _build_material_issue(slip)
    stock_entry.flags.ignore_permissions = True
    stock_entry.insert(ignore_permissions=True)
    stock_entry.submit()
    return {"name": stock_entry.name, "submitted": 1}
'''


def compiled(source, env):
    """Compile offline excerpt after allowlisting AST and never importing external modules."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                             ast.AsyncFunctionDef)):
            raise AssertionError("disallowed source operation")
    exec(compile(tree, "<pinned-scope-offline-excerpt>", "exec"), env)
    return env


class Callbacks:
    def __init__(self, events, name):
        self.callbacks = []
        self.events = events
        self.name = name

    def add(self, callback):
        self.callbacks.append(callback)
        self.events.append("register:" + self.name)

    def run(self):
        self.events.append("run:" + self.name)
        for fn in list(self.callbacks):
            fn()
        self.callbacks.clear()

    def reset(self):
        self.events.append("reset:" + self.name)
        self.callbacks.clear()


class FakeDB:
    def __init__(self, events):
        self.events = events
        self._disable_transaction_control = False
        self.before_commit = Callbacks(events, 'before_commit')
        self.after_commit = Callbacks(events, 'after_commit')
        self.before_rollback = Callbacks(events, 'before_rollback')
        self.after_rollback = Callbacks(events, 'after_rollback')
        self.value_cache = SimpleNamespace(clear=lambda: events.append('clear:db_local'))
        ns = compiled(DB_EXCERPT, {})
        self.commit = ns['commit'].__get__(self)
        self.rollback = ns['rollback'].__get__(self)

    def sql(self, statement):
        self.events.append('sql:' + statement)

    def begin(self):
        self.events.append('sql:begin')


class E1Tests(TestCase):
    def setUp(self):
        self.events = []
        self.db = FakeDB(self.events)

    def cache(self):
        # All side effects are synthetic list appends. Never call real cache.
        e = self.events
        local = SimpleNamespace(valid_columns={'Withdrawal Slip': 1})
        client = SimpleNamespace(erase_persistent_caches=lambda **kw: e.append('cache:erase'))
        frappe = SimpleNamespace(db=self.db, local=local, client_cache=client)
        ns = {'frappe': frappe,
              'clear_controller_cache': lambda doctype: e.append('cache:controller'),
              '_clear_doctype_cache_from_redis': lambda doctype: e.append('cache:redis')}
        return compiled(CACHE_EXCERPT, ns)['clear_doctype_cache']

    def realtime(self):
        local = SimpleNamespace()
        ns = {'local': local, 'db': self.db,
              'emit_via_redis': lambda *args: self.events.append('pubsub:events')}
        compiled(REALTIME_MODEL, ns)
        return ns['publish_realtime'], local

    def issue(self, entry, *, draft=False, fault=None):
        e = self.events
        ns = {
            '_require_stockroom_user': lambda: e.append('auth'),
            '_lock_withdrawal_slip': lambda name: e.append('lock') or {'owner': 'A'},
            '_get_issuable_slip': lambda name, lock: e.append('validate') or SimpleNamespace(name=name),
            '_assert_no_submitted_material_issue': lambda name: e.append('duplicate_guard'),
            '_get_existing_draft_names': lambda name: e.append('draft_guard') or (['DRAFT'] if draft else []),
            '_build_material_issue': lambda slip: e.append('build') or entry,
        }
        if fault:
            ns[fault] = lambda *args: (_ for _ in ()).throw(RuntimeError('synthetic stop'))
        return compiled(ISSUE_EXCERPT, ns)['issue_withdrawal_slip']

    def entry(self, insert_failure=False, submit_failure=False, on_submit=None):
        e = self.events
        class Entry:
            name = 'SYNTHETIC-ENTRY'
            flags = SimpleNamespace()
            def insert(self, **kwargs):
                e.append('db:insert')
                if insert_failure:
                    raise RuntimeError('insert fail')
            def submit(self):
                e.append('db:submit')
                if on_submit:
                    on_submit()
                if submit_failure:
                    raise RuntimeError('submit fail')
        return Entry()

    def test_01_cache_invalidation_occurs_before_callbacks(self):
        self.cache()('Withdrawal Slip')
        self.assertEqual(self.events[:5], ['cache:controller', 'cache:erase', 'cache:redis',
                                            'register:after_commit', 'register:after_rollback'])

    def test_02_full_rollback_does_not_undo_immediate_cache_effect(self):
        self.cache()('Withdrawal Slip')
        self.db.rollback()
        self.assertEqual(self.events.count('cache:redis'), 2)
        self.assertIn('sql:rollback', self.events)

    def test_03_full_commit_runs_cache_callback_again(self):
        self.cache()('Withdrawal Slip')
        self.db.commit()
        self.assertEqual(self.events.count('cache:redis'), 2)
        self.assertIn('sql:commit', self.events)

    def test_04_savepoint_rollback_does_not_flush_transaction_callbacks(self):
        self.cache()('Withdrawal Slip')
        self.db.rollback(save_point='fixture')
        self.assertEqual(self.events.count('cache:redis'), 1)
        self.assertNotIn('run:after_rollback', self.events)
        self.assertEqual(len(self.db.after_rollback.callbacks), 1)

    def test_05_rollback_discards_aftercommit_callback(self):
        self.db.after_commit.add(lambda: self.events.append('should_not_emit'))
        self.db.rollback()
        self.assertNotIn('should_not_emit', self.events)

    def test_06_commit_discards_afterrollback_callback(self):
        self.db.after_rollback.add(lambda: self.events.append('should_not_run'))
        self.db.commit()
        self.assertNotIn('should_not_run', self.events)

    def test_07_realtime_immediate_default_is_not_rollbackable(self):
        emit, _ = self.realtime()
        emit()
        self.db.rollback()
        self.assertEqual(self.events.count('pubsub:events'), 1)

    def test_08_realtime_deferred_on_commit(self):
        emit, _ = self.realtime()
        emit(after_commit=True)
        self.assertNotIn('pubsub:events', self.events)
        self.db.commit()
        self.assertEqual(self.events.count('pubsub:events'), 1)

    def test_09_realtime_deferred_discarded_on_rollback(self):
        emit, local = self.realtime()
        emit(after_commit=True)
        self.db.rollback()
        self.assertNotIn('pubsub:events', self.events)
        self.assertFalse(hasattr(local, '_realtime_log'))

    def test_10_realtime_task_progress_forces_immediate(self):
        emit, _ = self.realtime()
        emit(task_id='fictional', after_commit=True)
        self.assertEqual(self.events.count('pubsub:events'), 1)

    def test_11_duplicate_realtime_deferred_coalesced(self):
        emit, _ = self.realtime()
        emit(event='same', after_commit=True)
        emit(event='same', after_commit=True)
        self.db.commit()
        self.assertEqual(self.events.count('pubsub:events'), 1)

    def test_12_realtime_failed_aftercommit_callback_does_not_prove_rollback(self):
        self.db.after_commit.add(lambda: (_ for _ in ()).throw(RuntimeError('callback failed')))
        with self.assertRaises(RuntimeError):
            self.db.commit()
        self.assertIn('sql:commit', self.events)

    def test_13_full_rollback_callback_failure_does_not_restore_prior_cache(self):
        self.cache()('Withdrawal Slip')
        self.db.after_rollback.add(lambda: (_ for _ in ()).throw(RuntimeError('failure')))
        with self.assertRaises(RuntimeError):
            self.db.rollback()
        self.assertIn('cache:redis', self.events)

    def test_14_issuer_guard_runs_before_build(self):
        entry = self.entry()
        with self.assertRaises(RuntimeError):
            self.issue(entry, fault='_require_stockroom_user')('SLIP')
        self.assertNotIn('build', self.events)

    def test_15_lock_failure_before_build(self):
        with self.assertRaises(RuntimeError):
            self.issue(self.entry(), fault='_lock_withdrawal_slip')('SLIP')
        self.assertNotIn('build', self.events)

    def test_16_duplicate_guard_fails_before_build(self):
        with self.assertRaises(RuntimeError):
            self.issue(self.entry(), fault='_assert_no_submitted_material_issue')('SLIP')
        self.assertNotIn('db:insert', self.events)

    def test_17_existing_draft_blocks_creating_stock_entry(self):
        with self.assertRaises(ValueError):
            self.issue(self.entry(), draft=True)('SLIP')
        self.assertNotIn('build', self.events)

    def test_18_synthetic_happy_path_orders_insert_before_submit(self):
        result = self.issue(self.entry())('SLIP')
        self.assertEqual(result['submitted'], 1)
        self.assertLess(self.events.index('db:insert'), self.events.index('db:submit'))
        self.assertEqual(self.events[:5], ['auth', 'lock', 'validate', 'duplicate_guard', 'draft_guard'])

    def test_19_failure_after_insert_requires_outer_transaction_rollback(self):
        with self.assertRaises(RuntimeError):
            self.issue(self.entry(submit_failure=True))('SLIP')
        self.assertIn('db:insert', self.events)
        self.assertNotIn('sql:rollback', self.events)
        # Endpoint does not catch/rollback: caller/Framework owns transaction.

    def test_20_failure_during_insert_does_not_call_submit(self):
        with self.assertRaises(RuntimeError):
            self.issue(self.entry(insert_failure=True))('SLIP')
        self.assertNotIn('db:submit', self.events)

    def test_21_mocked_submit_cache_effect_precedes_outer_rollback(self):
        clear = self.cache()
        with self.assertRaises(RuntimeError):
            self.issue(self.entry(submit_failure=True, on_submit=lambda: clear('Withdrawal Slip')))('SLIP')
        self.assertEqual(self.events.count('cache:redis'), 1)
        self.db.rollback()
        self.assertEqual(self.events.count('cache:redis'), 2)

    def test_22_mocked_submit_cache_effect_precedes_outer_commit(self):
        clear = self.cache()
        self.issue(self.entry(on_submit=lambda: clear('Withdrawal Slip')))('SLIP')
        self.db.commit()
        self.assertEqual(self.events.count('cache:redis'), 2)

    def test_23_no_external_clients_or_processes_imported(self):
        source = Path(__file__).read_text(encoding='utf-8')
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(n.name.split('.')[0] for n in node.names)
            if isinstance(node, ast.ImportFrom):
                imports.add((node.module or '').split('.')[0])
        self.assertEqual(imports, {'ast', 'pathlib', 'types', 'unittest'})

    def test_24_no_real_network_or_database_connections(self):
        for fragment in (CACHE_EXCERPT, DB_EXCERPT, REALTIME_MODEL, ISSUE_EXCERPT):
            self.assertNotIn('import frappe', fragment)
            self.assertNotIn('redis.Redis(', fragment)
            self.assertNotIn('socket.connect', fragment)
            self.assertNotIn('docker ', fragment)
            self.assertNotIn('sqlalchemy', fragment)

    def test_25_callbacks_are_reentrant_model_not_real_application(self):
        self.assertEqual(self.db.after_commit.callbacks, [])
        self.assertEqual(self.db.after_rollback.callbacks, [])


if __name__ == '__main__':
    main()
