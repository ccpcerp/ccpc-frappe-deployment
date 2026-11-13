#!/usr/bin/env python3
"""Stage 2A: ONE USE, NEW-only isolated MariaDB import of the independently verified NAS copy.

--preflight: read only. --execute: exclusive test-only internal bridge, named DB volume,
fresh DB container and new credentials; import SQL to a new test schema. NEVER clean
up or repeat after any partial attempt. No app/worker/site container, migrations, host
ports, mail or existing environment changes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import stat
import subprocess
import time

HOST = "ccpcerp-prod"
USER = "ccpcadmin"
RUN = "20261112T090214Z-0148d36b2cb678b3"
ROOT = Path("/var/lib/ccpc-a3-isolated-restore-20261112")
SECRETS = Path("/var/lib/ccpc-a3-restore-db-secrets-20261112")
NAS_MOUNT = Path("/mnt/ccpc-a3-restore-readonly-20261112")
CURRENT_NAS_MOUNT = Path("/mnt/ccpcerp-prod_backups")
PREFIX = "ccpc_a3_restore_drill_20261112"
NETWORK = PREFIX + "_internal"
VOLUME = PREFIX + "_db-data"
DB = PREFIX + "-db-1"
SCHEMA = "ccpc_restore_20261112"
MYSQL = "sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4"
APP = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
REDIS = "sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763"
ROLES = {"database.sql.gz": "database", "site_config_backup.json": "site_config",
         "files.tar": "public_files", "private-files.tar": "private_files"}
NAME = re.compile(r"\A\d{8}_\d{6}-ccpcerp_local-(database\.sql\.gz|site_config_backup\.json|files\.tar|private-files\.tar)\Z")
PROTECTED = {
    *(f"ccpc_prod_erpnext-{s}-1" for s in
      ("frontend", "websocket", "backend", "redis-cache", "redis-queue", "db")),
    *(f"{p}-{s}-1" for p in
      ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
      for s in ("db", "redis-cache", "redis-queue")),
}

class Stop(Exception):
    pass

def insist(ok: bool, reason: str) -> None:
    if not ok:
        raise Stop(reason)

def safe_run(cmd: list[str], timeout: int = 30, stdin=None, check: bool = True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            cmd, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=timeout, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        raise Stop("Guarded command unavailable or timed out") from None
    if check:
        insist(result.returncode == 0, "Guarded command failed")
    return result

def docker(*args: str, timeout: int = 30, check: bool = True) -> subprocess.CompletedProcess:
    return safe_run(["docker", "--host", "unix:///var/run/docker.sock", *args], timeout, check=check)

def listing(*args: str) -> set[str]:
    return set(docker(*args).stdout.decode("utf-8", "strict").splitlines())

def protected_root(path: Path, mode: int, directory: bool) -> None:
    s = path.lstat()
    insist(s.st_uid == 0 and s.st_gid == 0 and stat.S_IMODE(s.st_mode) == mode and
           (stat.S_ISDIR(s.st_mode) if directory else stat.S_ISREG(s.st_mode)),
           "Unexpected protected file/directory identity")

def digest(path: Path) -> tuple[int, str]:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    h = hashlib.sha256()
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        insist(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size > 0,
               "Backup artifact file identity invalid")
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
        after = os.fstat(stream.fileno())
        insist((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
               (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
               "Backup artifact changed during reading")
        return before.st_size, h.hexdigest()

def manifest() -> dict[str, dict]:
    protected_root(ROOT, 0o700, True)
    protected_root(ROOT / "manifest.json", 0o600, False)
    protected_root(ROOT / "NAS_COMPLETED_VERIFIED", 0o600, False)
    insist((ROOT / "NAS_COMPLETED_VERIFIED").read_bytes() == (RUN + "\n").encode(),
           "Independent NAS readback marker invalid")
    raw = (ROOT / "manifest.json").read_bytes()
    insist(len(raw) < 16384, "Manifest unexpectedly large")
    data = json.loads(raw)
    insist(isinstance(data, dict) and data.get("schema") == 1 and
           data.get("run_id") == RUN and data.get("site") == "ccpcerp.local" and
           data.get("project") == "ccpc_prod_erpnext" and data.get("image") == APP,
           "Backup source manifest identity mismatch")
    artifacts = data.get("artifacts")
    insist(isinstance(artifacts, list) and len(artifacts) == 4, "Expected four backup artifacts")
    role_map: dict[str, dict] = {}
    names: set[str] = set()
    for item in artifacts:
        insist(isinstance(item, dict), "Malformed backup manifest")
        name, role = item.get("filename"), item.get("role")
        insist(type(name) is str and type(role) is str, "Invalid backup role/name")
        match = NAME.fullmatch(name)
        insist(match is not None and ROLES.get(match.group(1)) == role and
               role not in role_map and name not in names, "Unexpected archive role/name")
        insist(type(item.get("size")) is int and item["size"] > 0 and
               type(item.get("sha256")) is str and
               re.fullmatch(r"[a-f0-9]{64}", item["sha256"]) is not None,
               "Invalid artifact metadata")
        protected_root(ROOT / name, 0o600, False)
        insist(digest(ROOT / name) == (item["size"], item["sha256"]), "Backup checksum mismatch")
        role_map[role] = item
        names.add(name)
    insist(set(role_map) == set(ROLES.values()) and
           {x.name for x in ROOT.iterdir()} ==
           names | {"manifest.json", "NAS_COMPLETED_VERIFIED"},
           "Unexpected recovery scratch contents")
    return role_map

def no_mount(path: Path) -> None:
    p = safe_run(["findmnt", "--mountpoint", str(path), "--noheadings"], check=False)
    insist(p.returncode == 1, "Unexpected active/unknown Synology mount")

def preflight() -> dict[str, dict]:
    insist(os.geteuid() == 0 and os.environ.get("SUDO_USER") == USER and
           socket.gethostname().split(".")[0] == HOST, "Wrong operator/host")
    insist(not any(k in os.environ for k in
                   ("DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME")),
           "Unexpected Docker environment override")
    no_mount(NAS_MOUNT)
    no_mount(CURRENT_NAS_MOUNT)
    insist(not SECRETS.exists() and not SECRETS.is_symlink(), "Test secrets already exist; no retry")
    protected_root(ROOT, 0o700, True)
    roles = manifest()
    for image in (APP, MYSQL, REDIS):
        insist(docker("image", "inspect", "--format", "{{.Id}}", image).stdout.strip().decode() == image,
               "Pinned local Docker image unavailable")
    insist(listing("ps", "-a", "--format", "{{.Names}}") == PROTECTED and
           listing("ps", "--format", "{{.Names}}") == PROTECTED,
           "Protected twelve-container inventory/running status changed")
    for kind in ("volume", "network"):
        insist(not any(n.startswith(PREFIX) for n in listing(kind, "ls", "--format", "{{.Name}}")),
               "A test resource already exists")
    insist(shutil.disk_usage("/var/lib/docker").free > 20 * 1024 ** 3,
           "Insufficient test database free disk")
    mem = re.search(r"^MemAvailable:\s+(\d+)\s+kB$",
                    Path("/proc/meminfo").read_text(), re.MULTILINE)
    insist(mem is not None and int(mem.group(1)) * 1024 >= 3 * 1024 ** 3,
           "Insufficient available RAM for test-only MariaDB without risk to A3")
    archive = ROOT / roles["database"]["filename"]
    total = 0
    try:
        with gzip.open(archive, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                total += len(chunk)
                insist(total <= 1024 * 1024 * 1024, "SQL dump expands beyond approved 1GiB limit")
    except (OSError, EOFError, gzip.BadGzipFile):
        raise Stop("SQL gzip integrity check failed") from None
    insist(total > 128, "SQL dump empty")
    cfg = json.loads((ROOT / roles["site_config"]["filename"]).read_bytes())
    insist(isinstance(cfg, dict) and
           all(isinstance(cfg.get(k), str) and cfg[k] for k in
               ("db_name", "db_password", "encryption_key")),
           "Backup site config incomplete")
    # No live credentials stored or displayed; backup config is read only.
    print("CCPC_STAGE2A_BACKUP_GZIP_SHA256_AND_CONFIG_PASS", flush=True)
    print("CCPC_STAGE2A_PROTECTED_DOCKER_AND_IMAGES_PASS", flush=True)
    print("CCPC_STAGE2A_NEW_TEST_NAMESPACE_UNUSED_PASS", flush=True)
    return roles

def create_secret(path: Path, content: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="ascii") as writer:
        writer.write(content)
        writer.flush()
        os.fsync(writer.fileno())
    protected_root(path, 0o600, False)

def sql_query(query: str, *, schema: str | None = None) -> str:
    cmd = [
        "exec", DB, "mariadb",
        "--defaults-extra-file=/run/secrets/db-client.cnf",
        "--batch", "--skip-column-names",
    ]
    if schema:
        cmd.append("--database=" + schema)
    cmd.append("--execute=" + query)
    return docker(*cmd, timeout=45).stdout.decode("utf-8", "strict").strip()

def verify_test_network() -> None:
    network = json.loads(docker("network", "inspect", NETWORK).stdout)[0]
    container = json.loads(docker("inspect", DB).stdout)[0]
    insist(network.get("Internal") is True and network.get("Driver") == "bridge",
           "Test network is not internal-only bridge")
    insist(set(network.get("Containers", {})) == {container.get("Id")},
           "Unexpected test network member")
    insist(container.get("Image") == MYSQL and container.get("State", {}).get("Running") is True and
           container.get("HostConfig", {}).get("PortBindings") in (None, {}) and
           set(container.get("NetworkSettings", {}).get("Networks", {})) == {NETWORK},
           "Test DB image/state/network/published port mismatch")
    mounts = container.get("Mounts", [])
    insist(len(mounts) == 3 and
           any(x.get("Type") == "volume" and x.get("Name") == VOLUME and x.get("Destination") == "/var/lib/mysql" for x in mounts) and
           any(x.get("Type") == "bind" and x.get("Source") == str(SECRETS / "mariadb-root-password") and x.get("RW") is False for x in mounts) and
           any(x.get("Type") == "bind" and x.get("Source") == str(SECRETS / "db-client.cnf") and x.get("RW") is False for x in mounts),
           "Unexpected test MariaDB mounts")

def execute() -> None:
    roles = preflight()
    # First mutation: exclusive root-only recovery-test secrets. Never rerun after this.
    SECRETS.mkdir(mode=0o700)
    protected_root(SECRETS, 0o700, True)
    create_secret(SECRETS / "DO_NOT_RETRY", RUN + "\n")
    secret = secrets.token_hex(32)
    create_secret(SECRETS / "mariadb-root-password", secret + "\n")
    create_secret(SECRETS / "db-client.cnf", "[client]\nuser=root\npassword=" + secret + "\nprotocol=socket\n")
    del secret
    print("CCPC_STAGE2A_NEW_TEST_ONLY_SECRETS_CREATED", flush=True)
    docker("network", "create", "--driver", "bridge", "--internal",
           "--label", "com.ccpc.test=restore-20261112", NETWORK, timeout=45)
    net = json.loads(docker("network", "inspect", NETWORK).stdout)[0]
    insist(net.get("Internal") is True and net.get("Driver") == "bridge" and
           not net.get("Containers"), "New test network isolation check failed")
    print("CCPC_STAGE2A_NEW_INTERNAL_NETWORK_PASS", flush=True)
    docker("volume", "create", "--label", "com.ccpc.test=restore-20261112", VOLUME, timeout=45)
    docker(
        "run", "--detach", "--pull=never", "--name", DB,
        "--network", NETWORK, "--network-alias", "db",
        "--restart", "no", "--security-opt", "no-new-privileges",
        "--pids-limit", "256", "--memory", "2g", "--cpus", "2",
        "--env", "MARIADB_ROOT_PASSWORD_FILE=/run/secrets/mariadb-root-password",
        "--env", "MARIADB_ROOT_HOST=localhost",
        "--health-cmd", "healthcheck.sh --connect --innodb_initialized",
        "--health-interval", "5s", "--health-timeout", "5s", "--health-retries", "15",
        "--mount", "type=volume,source=" + VOLUME + ",target=/var/lib/mysql,volume-nocopy",
        "--mount", "type=bind,source=" + str(SECRETS / "mariadb-root-password") +
                   ",target=/run/secrets/mariadb-root-password,readonly",
        "--mount", "type=bind,source=" + str(SECRETS / "db-client.cnf") +
                   ",target=/run/secrets/db-client.cnf,readonly",
        MYSQL, timeout=60,
    )
    verify_test_network()
    print("CCPC_STAGE2A_NEW_ISOLATED_DB_CONTAINER_PASS", flush=True)
    ready = False
    for _ in range(60):
        state = json.loads(docker("inspect", DB).stdout)[0].get("State", {})
        insist(state.get("Running") is True and
               state.get("Health", {}).get("Status") != "unhealthy",
               "Isolated DB stopped or became unhealthy")
        p = docker("exec", DB, "mariadb",
                   "--defaults-extra-file=/run/secrets/db-client.cnf",
                   "--batch", "--skip-column-names", "--execute=SELECT 1",
                   timeout=10, check=False)
        if (p.returncode == 0 and p.stdout.strip() == b"1" and
                state.get("Health", {}).get("Status") == "healthy"):
            ready = True
            break
        time.sleep(2)
    insist(ready, "New isolated DB did not become ready; preserve partial")
    state = json.loads(docker("inspect", DB).stdout)[0].get("State", {})
    insist(state.get("Health", {}).get("Status") == "healthy",
           "Isolated DB never reached healthy")
    insist(set(sql_query("SHOW DATABASES").splitlines()) ==
           {"information_schema", "mysql", "performance_schema", "sys"},
           "Test DB unexpectedly has existing schema")
    print("CCPC_STAGE2A_ISOLATED_EMPTY_MARIADB_READY_PASS", flush=True)
    verify_test_network()
    sql_query("CREATE DATABASE " + chr(96) + SCHEMA + chr(96) +
              " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("CCPC_STAGE2A_NEW_SCHEMA_CREATED", flush=True)
    archive = ROOT / roles["database"]["filename"]
    cmd = [
        "docker", "--host", "unix:///var/run/docker.sock",
        "exec", "-i", DB, "mariadb",
        "--defaults-extra-file=/run/secrets/db-client.cnf", "--database=" + SCHEMA,
    ]
    try:
        with gzip.open(archive, "rb") as src:
            child = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            assert child.stdin is not None
            try:
                total = 0
                for chunk in iter(lambda: src.read(1024 * 1024), b""):
                    total += len(chunk)
                    insist(total <= 1024 * 1024 * 1024,
                           "SQL import uncompressed size limit exceeded")
                    child.stdin.write(chunk)
                child.stdin.close()
                code = child.wait(timeout=360)
            except Exception:
                child.kill()
                child.wait(timeout=30)
                raise
    except Exception:
        raise Stop("Partial SQL import; do not rerun or clean") from None
    insist(code == 0, "Isolated SQL import failed; preserve partial DB")
    print("CCPC_STAGE2A_ISOLATED_SQL_IMPORT_CLIENT_EXIT_ZERO", flush=True)
    def qcount(stmt: str) -> int:
        try:
            return int(sql_query(stmt, schema=SCHEMA))
        except ValueError:
            raise Stop("Recovered DB count response invalid") from None
    base_tables = qcount("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND TABLE_TYPE='BASE TABLE'")
    companies = qcount("SELECT COUNT(*) FROM " + chr(96) + "tabCompany" + chr(96))
    doctypes = qcount("SELECT COUNT(*) FROM " + chr(96) + "tabDocType" + chr(96))
    insist(base_tables >= 700 and companies == 4 and doctypes >= 700,
           "Restored DB structure/company counts unexpectedly different")
    print("CCPC_STAGE2A_RESTORED_DB_COMPANY_AND_SCHEMA_COUNTS_PASS", flush=True)
    verify_test_network()
    insist(listing("ps", "-a", "--format", "{{.Names}}") == PROTECTED | {DB} and
           listing("ps", "--format", "{{.Names}}") == PROTECTED | {DB},
           "Protected services changed after isolated SQL restore")
    print("CCPC_STAGE2A_PROTECTED_ORIGINAL_CONTAINERS_PRESERVED_PASS", flush=True)
    print("CCPC_NEW_A3_RESTORE_STAGE2A_ISOLATED_DATABASE_PASS_SITE_PENDING", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            preflight()
            print("CCPC_NEW_A3_RESTORE_STAGE2A_READONLY_PREFLIGHT_PASS", flush=True)
        else:
            execute()
    except Exception:
        print("CCPC_NEW_A3_RESTORE_STAGE2A_STOP_REVIEW_REQUIRED", flush=True)
        raise SystemExit(1)
