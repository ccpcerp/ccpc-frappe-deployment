"""Native MySQLdb test. Called only after the NIC-free lab isolation checks."""
from contextlib import closing
import os
from unittest.mock import patch

import MySQLdb
from MySQLdb.constants import CLIENT

import run_dev_ws_preflight as wrapper
import ws_readiness_audit as audit


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def test_operator_path(admin_connection, schema, host, port, pilot):
    require(host == "127.0.0.1" and schema == "ccpc_synthetic_lab",
            "Synthetic loopback fixture required")
    writer = "synthetic_operator"
    secret = os.urandom(18).hex()
    with admin_connection() as admin:
        with admin.cursor() as cursor:
            # The operator route intentionally uses approved local TCP, not the
            # different TLS-only reader path exercised earlier in this guest.
            cursor.execute("SET GLOBAL require_secure_transport=OFF")
            cursor.execute(f"CREATE USER '{writer}'@'{host}' IDENTIFIED BY %s", (secret,))
            cursor.execute(f"GRANT SELECT, UPDATE ON `{schema}`.`tabAccount` TO '{writer}'@'{host}'")
            cursor.execute(f"UPDATE `{schema}`.`tabAccount` SET id=1")
    target = dict(db_ip=host, port=port, schema=schema, principal=f"{writer}@{host}",
                  server_hostname="synthetic-db-lab", server_id=411, timezone="UTC", pilot=vars(pilot))
    config = dict(db_name=schema, db_user=writer, db_password=secret)

    def connect():
        return wrapper.connect_bound(config, target)

    # Show that native connect actually suppresses both capabilities on the wire.
    with closing(connect()) as connection:
        require(not connection.client_flag & (CLIENT.MULTI_STATEMENTS | CLIENT.LOCAL_FILES),
                "Native client enabled multi-statements or local infile")
        with closing(connection.cursor()) as cursor:
            cursor.execute("UPDATE `tabAccount` SET id=3 WHERE id=1")
            require(cursor.rowcount == 1, "Synthetic site account lacks expected control write privilege")
            connection.rollback()
    print("PASS | MySQLdb 2.2.7 accepted exact wrapper arguments; multi-statements and local infile disabled")

    def read_probe(q, result, *_):
        metadata = q("SELECT @@in_transaction AS active")
        require(metadata == [{"active": 1}], "snapshot transaction is not active")
        require(q("SELECT id FROM `tabAccount` WHERE id=%s", (1,)) == [{"id": 1}],
                "Parameterized native SELECT failed")
        result.emit("PASS", "Synthetic probe", "Parameterized SELECT in active snapshot.")

    lines = []
    with patch.object(audit, "run_snapshot", side_effect=read_probe):
        wrapper.audited_snapshot(connect(), audit, target, "synthetic", lines)
    require(any("DEVELOPMENT binding" in line for line in lines), "identity was not confirmed")
    require(any("Synthetic probe" in line for line in lines), "native payload did not execute")
    print("PASS | exact wrapper accepted MariaDB identity and parameterized SELECT inside active snapshot")

    # Execute the negative UPDATE directly through the native test cursor so
    # this proves MariaDB enforcement, independently of Python's SELECT guard.
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        cursor.execute("START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY")
        try:
            cursor.execute("UPDATE `tabAccount` SET id=3 WHERE id=1")
        except MySQLdb.Error as exc:
            require(exc.args[0] == 1792, "expected MariaDB transaction read-only error")
        else:
            raise RuntimeError("MySQLdb session permitted a write in the READ ONLY snapshot")
        finally:
            connection.rollback()
    print("PASS | MySQLdb writer was blocked by MariaDB error 1792 in READ ONLY transaction")

    with patch.object(audit, "run_snapshot") as unused:
        try:
            wrapper.audited_snapshot(connect(), audit, dict(target, server_id=412), "synthetic", [])
        except wrapper.Stop:
            require(not unused.called, "wrong server reached application SELECT")
        else:
            raise RuntimeError("wrapper accepted the wrong native MariaDB identity")
    print("PASS | exact MySQLdb wrapper rejected wrong server before application SELECT")
