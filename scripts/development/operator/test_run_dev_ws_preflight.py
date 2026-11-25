"""Offline host, binding and raw read-only transaction tests."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import ast
import json

import run_dev_ws_preflight as preflight
import ws_readiness_audit as audit

TARGET = {
    "host": preflight.HOST, "site": preflight.SITE, "commit": preflight.COMMIT,
    "app_container_id": "a" * 64, "db_container_id": "b" * 64, "network_id": "c" * 64,
    "db_host": "synthetic-db", "db_ip": "192.168.254.2", "port": 3306, "schema": "synthetic_dev",
    "principal": "reader@synthetic", "server_hostname": "synthetic-db",
    "server_id": 7, "timezone": "UTC",
    "pilot": {name: "synthetic-" + name for name in
              ("slip", "company", "requesting", "beneficiary", "equipment", "item", "warehouse", "expense")},
}
SPEC = {"site_reviewer": "synthetic site", "database_reviewer": "synthetic DBA",
        "site_binding": TARGET, "database_binding": deepcopy(TARGET)}
CONFIG = dict(db_type="mariadb", db_name="synthetic_dev", db_host="synthetic-db",
              db_user="reader", db_password="synthetic-fixture")


class BindingTests(TestCase):
    def test_requires_independent_matching_commit_site_and_container_binding(self):
        self.assertEqual(preflight.validated_binding(SPEC), TARGET)
        for path, value in (
            (("database_reviewer",), "SYNTHETIC SITE"),
            (("database_binding", "db_ip"), "192.168.254.3"),
            (("site_binding", "commit"), "0" * 40),
            (("site_binding", "app_container_id"), "app"),
        ):
            spec = deepcopy(SPEC)
            leaf = spec if len(path) == 1 else spec[path[0]]
            leaf[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(preflight.Stop):
                preflight.validated_binding(spec)

    def test_config_mismatch_stops_before_address_resolution(self):
        for override in (dict(db_name="other"), dict(extra_config=["unreviewed"]),
                         dict(db_ssl_ca="present"), dict(db_socket="/synthetic")):
            def forbidden(*args, **kwargs):
                self.fail("resolution called for mismatched site")
            with self.assertRaises(preflight.Stop):
                preflight.verified_database_config(dict(CONFIG, **override), TARGET, forbidden)

    def test_config_requires_single_pinned_resolution(self):
        addr = lambda ip: (None, None, None, None, (ip, 3306))
        preflight.verified_database_config(CONFIG, TARGET, lambda *a, **kw: [addr(TARGET["db_ip"])])
        with self.assertRaises(preflight.Stop):
            preflight.verified_database_config(
                CONFIG, TARGET, lambda *a, **kw: [addr(TARGET["db_ip"]), addr("192.168.254.3")],
            )

    def test_preflight_pins_running_container_and_same_network(self):
        seen = []

        def invoke(args):
            seen.append(args)
            if args[-1] == "--show-toplevel":
                return preflight.HOST_APP
            if args[-1] == "HEAD":
                return preflight.COMMIT
            if args[-3] == "status":
                return ""
            cid = args[-1]
            name, ip = ("/" + preflight.FRAPPE_CONTAINER, "192.168.254.4") if cid == TARGET["app_container_id"] else (
                "/synthetic-db", TARGET["db_ip"],
            )
            return "\n".join((cid, name, "true",
                              json.dumps(dict(net=dict(NetworkID=TARGET["network_id"], IPAddress=ip)))))

        with (patch.object(preflight.socket, "gethostname", return_value=preflight.HOST),
              patch.object(preflight.os, "geteuid", return_value=1000),
              patch.object(Path, "is_dir", return_value=True)):
            preflight.host_preflight(TARGET, invoke)
            with self.assertRaises(preflight.Stop):
                preflight.host_preflight(dict(TARGET, network_id="d" * 64), invoke)
        self.assertTrue(all(cmd[0] in ("/usr/bin/docker", "/usr/bin/git") for cmd in seen))


class FakeConnection:
    def __init__(self, identity):
        self.identity = identity
        self.commands = []
        self.record = SimpleNamespace(
            description=[(k,) for k in identity],
            execute=lambda sql, args=(): self.commands.append((sql, args)),
            fetchall=lambda: [tuple(identity.values())],
            close=lambda: self.commands.append(("cursor closed", ())),
        )

    def cursor(self):
        return self.record

    def close(self):
        self.commands.append(("connection closed", ()))

    def rollback(self):
        self.commands.append(("rollback", ()))


class TransactionTests(TestCase):
    identity = dict(db=TARGET["schema"], principal=TARGET["principal"], hostname=TARGET["server_hostname"],
                    server_id=TARGET["server_id"], version="11.8.6-MariaDB")

    def test_read_only_before_identity_and_rollback_on_query_failure(self):
        conn = FakeConnection(self.identity)

        def snapshot(q, *_):
            for sql in ("UPDATE t SET x=1", "SELECT x FROM t FOR UPDATE",
                        "SELECT x FROM t; SHOW GRANTS", "SELECT x INTO OUTFILE 'x'"):
                with self.assertRaises(preflight.Stop):
                    q(sql)
            q("SELECT x FROM t WHERE name=%s", ("synthetic'; UPDATE t SET x=1",))
            raise preflight.Stop("synthetic follow-up check stopped")

        with patch.object(audit, "run_snapshot", side_effect=snapshot), self.assertRaises(preflight.Stop):
            preflight.audited_snapshot(conn, audit, TARGET, "synthetic", [])
        self.assertEqual([sql for sql, _ in conn.commands[:2]], [
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ",
            "START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY",
        ])
        self.assertTrue(conn.commands[2][0].startswith("SELECT DATABASE()"))
        self.assertEqual(conn.commands[3][1], ("synthetic'; UPDATE t SET x=1",))
        self.assertEqual([sql for sql, _ in conn.commands[-3:]], ["rollback", "cursor closed", "connection closed"])

    def test_wrong_server_stops_before_application_read_and_closes(self):
        conn = FakeConnection(dict(self.identity, server_id=8))
        with patch.object(audit, "run_snapshot") as snapshot, self.assertRaises(preflight.Stop):
            preflight.audited_snapshot(conn, audit, TARGET, "synthetic", [])
        snapshot.assert_not_called()
        self.assertEqual(conn.commands[-1][0], "connection closed")

    def test_verified_audit_is_pinned_and_operator_data_is_not_code(self):
        source = Path(audit.__file__).read_text()
        runner = Path(preflight.__file__).read_text()
        seen = []

        def invoke(argv, **kwargs):
            seen.append(argv)
            script = kwargs["input_text"]
            tree = ast.parse(script)
            call = tree.body[-1].value
            payload = json.loads(ast.literal_eval(call.args[0].args[0]))
            self.assertEqual(payload["issuer"], "synthetic'; forbidden_call()")
            return "private driver log\n" + preflight.FRAME + '["PASS | Binding | Confirmed."]\n'

        self.assertEqual(preflight.execute(SPEC, "synthetic'; forbidden_call()", runner, source,
                                           invoke, lambda *_: None), ["PASS | Binding | Confirmed."])
        self.assertEqual(seen[0][-5:], (TARGET["app_container_id"], "./env/bin/python", "-I", "-B", "-"))
        with self.assertRaises(preflight.Stop):
            preflight.execute(SPEC, "synthetic", runner, source + "\n", invoke, lambda *_: None)
        self.assertEqual(len(seen), 1)
