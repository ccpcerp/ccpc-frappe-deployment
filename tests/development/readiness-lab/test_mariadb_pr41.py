"""Synthetic, NIC-free QEMU lab only. Never run in a host or ERPNext runtime."""
import hashlib
from pathlib import Path
import os
import socket
import ssl
import subprocess
import time
from unittest.mock import patch

import pymysql

import ws_readiness_audit as audit

LAB = Path("/run/lab")
SOCKET = str(LAB / "mysql.sock")
HOST = "127.0.0.1"
PORT = 33306
SCHEMA = "ccpc_synthetic_lab"
READER = "synthetic_reader"
PILOT = audit.Pilot("synthetic-slip", "synthetic-company", "synthetic-requester",
                    "synthetic-beneficiary", "synthetic-equipment", "synthetic-item",
                    "synthetic-warehouse", "synthetic-expense")


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def isolation():
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    require(os.getuid() == os.geteuid() == 1000 and os.getgroups() == [],
            "guest test identity is not the dedicated non-root UID")
    require(int(status["CapEff"], 16) == 0 and status["NoNewPrivs"].strip() == "1",
            "guest privilege boundary missing")
    try:
        os.setuid(0)
    except PermissionError:
        pass
    else:
        raise RuntimeError("guest test process could regain root")
    require(not any(key in os.environ for key in ("SSH_AUTH_SOCK", "DOCKER_HOST", "DOCKER_CONTEXT")),
            "host agent or Docker routing projected into guest")
    require({name for _, name in socket.if_nameindex()} == {"lo"}, "guest has an external interface")
    routes = Path("/proc/net/route").read_text().splitlines()[1:]
    require(not routes, "guest has an IPv4 route beyond local loopback")
    for path in ("/var/run/docker.sock", "/run/docker.sock", "/mnt/erpnext_backups",
                 "/home/gani", "/workspace", "/root/.ssh", "/run/host-services"):
        require(not Path(path).exists(), "host path visible in guest")
    mounts = Path("/proc/self/mountinfo").read_text().splitlines()
    require(all(line.split(" - ", 1)[1].split()[0] in
                {"rootfs", "tmpfs", "ramfs", "proc", "sysfs", "devtmpfs"} for line in mounts),
            "unexpected guest filesystem type")
    require(socket.gethostname() == "synthetic-db-lab" and Path("/lab/server.key").is_file(),
            "not the disposable lab")
    print("PASS | non-root guest, zero capabilities, no writable escalation, no NIC or host mounts")


def sql_admin():
    return pymysql.connect(unix_socket=SOCKET, user="root", autocommit=True, connect_timeout=2)


def boot():
    subprocess.run(
        ["/usr/bin/mariadb-install-db", "--no-defaults", "--basedir=/usr",
         "--datadir=/run/lab/data", "--auth-root-authentication-method=normal",
         "--skip-test-db", "--skip-name-resolve", "--force"],
        check=True, timeout=60, stdout=subprocess.DEVNULL,
    )
    return subprocess.Popen(
        ["/usr/sbin/mariadbd", "--no-defaults", "--basedir=/usr", "--datadir=/run/lab/data",
         "--socket=" + SOCKET, "--pid-file=/run/lab/mysql.pid", "--bind-address=" + HOST,
         f"--port={PORT}", "--server-id=411", "--skip-name-resolve",
         "--ssl-ca=/lab/ca.pem", "--ssl-cert=/lab/server.pem", "--ssl-key=/lab/server.key",
         "--require-secure-transport=ON", "--innodb-use-native-aio=OFF"],
        stdout=subprocess.DEVNULL,
    )


def tests():
    password = os.urandom(18).hex()  # Synthetic guest-only secret.
    with sql_admin() as admin:
        with admin.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            server_version = cursor.fetchone()[0]
            require(server_version.startswith("11.8."), "expected MariaDB 11.8")
            cursor.execute(f"CREATE DATABASE `{SCHEMA}`")
            cursor.execute(f"CREATE USER '{READER}'@'{HOST}' IDENTIFIED BY %s REQUIRE SSL", (password,))
            for table in sorted(audit.AUDIT_TABLES):
                cursor.execute(f"CREATE TABLE `{SCHEMA}`.`{table}` (id INT PRIMARY KEY) ENGINE=InnoDB")
                cursor.execute(f"GRANT SELECT ON `{SCHEMA}`.`{table}` TO '{READER}'@'{HOST}'")
            cursor.execute(f"INSERT INTO `{SCHEMA}`.`tabAccount` VALUES (1)")

    ca = Path("/lab/ca.pem").read_bytes()
    leaf = ssl.PEM_cert_to_DER_cert(Path("/lab/server.pem").read_text())
    target = dict(host=HOST, port=PORT, username=READER, database=SCHEMA,
                  principal=f"{READER}@{HOST}", hostname="synthetic-db-lab",
                  server_id=411, timezone="UTC", leaf_sha256=hashlib.sha256(leaf).hexdigest())

    def native_snapshot(q, *_):
        for table in sorted(audit.AUDIT_TABLES):
            q(f"SELECT id FROM `{table}` WHERE id=%s", (1,))
        rows = q("SELECT COUNT(*) AS n FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE()")
        require(rows[0]["n"] == len(audit.AUDIT_TABLES), "metadata scope differs")

    checks = audit.Results(lambda line: print(line.replace(" | DEVELOPMENT connection | ",
                                                           " | synthetic connection | ")))
    with patch.object(audit, "run_snapshot", side_effect=native_snapshot):
        audit.inspect_connection(audit.connect(target, ca, password), target, "synthetic", checks, PILOT)
    print(f"PASS | MariaDB {server_version}; actual TLS leaf, direct 33-table grants and read-only snapshot")

    try:
        audit.connect(dict(target, leaf_sha256="0" * 64), ca, password).close()
    except audit.Stop:
        print("PASS | wrong TLS leaf rejected")
    else:
        raise RuntimeError("wrong leaf was accepted")

    for invalid in (dict(target, server_id=0), dict(target, database="unexpected_schema")):
        with patch.object(audit, "run_snapshot") as snapshot:
            try:
                audit.inspect_connection(audit.connect(target, ca, password), invalid,
                                         "synthetic", audit.Results(), PILOT)
            except audit.Stop:
                require(not snapshot.called, "snapshot reached after wrong site binding")
            else:
                raise RuntimeError("wrong server or database binding was accepted")
    print("PASS | wrong server ID and database rejected before application SELECT")

    try:
        pymysql.connect(host=HOST, port=PORT, user=READER, password=password,
                        database=SCHEMA, connect_timeout=2).close()
    except pymysql.MySQLError as exc:
        require(exc.args[0] in (1045, 3159), "unexpected non-TLS error")
    else:
        raise RuntimeError("server accepted non-TLS authentication")
    print("PASS | MariaDB rejected the unencrypted synthetic connection")

    with sql_admin() as admin:
        with admin.cursor() as cursor:
            cursor.execute(f"GRANT UPDATE ON `{SCHEMA}`.`tabAccount` TO '{READER}'@'{HOST}'")
    try:
        with patch.object(audit, "run_snapshot") as snapshot:
            audit.inspect_connection(audit.connect(target, ca, password), target, "synthetic", audit.Results(), PILOT)
    except audit.Stop:
        require(not snapshot.called, "application snapshot executed with broad grants")
        print("PASS | actual extra UPDATE grant rejected before snapshot")
    else:
        raise RuntimeError("broader grant was accepted")

    with sql_admin() as admin:
        with admin.cursor() as cursor:
            cursor.execute(audit.ISOLATION)
            cursor.execute(audit.SNAPSHOT)
            try:
                cursor.execute(f"UPDATE `{SCHEMA}`.`tabAccount` SET id=2 WHERE id=1")
            except pymysql.MySQLError as exc:
                require(exc.args[0] == 1792, "expected server read-only transaction error")
            else:
                raise RuntimeError("server permitted write through a read-only transaction")
    print("PASS | MariaDB enforces READ ONLY on a write-capable synthetic control account")


def main():
    isolation()
    server = boot()
    try:
        for _ in range(120):
            require(server.poll() is None, "synthetic MariaDB stopped")
            try:
                connection = sql_admin()
            except pymysql.MySQLError:
                time.sleep(0.25)
            else:
                connection.close()
                break
        else:
            raise RuntimeError("synthetic MariaDB did not become available")
        tests()
    finally:
        server.terminate()
        server.wait(timeout=15)


if __name__ == "__main__":
    main()
