#!/usr/bin/env python3
"""Stage 3A: isolated NEW A3 restore test Frappe startup. NEVER use on OLD/DEV/prod.

--preflight: strictly read-only; check isolated DB/sites/12 original containers.
--execute: ONE USE; add only new internal-only Redis, backend, websocket,
frontend containers and one NEW test logs volume; check internal /login HTTP 200.
No host ports, external network, jobs, scheduler, email, migration or cutover.
Any STOP preserves partial test state; do not rerun, cleanup or repair blindly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import time

HOST = "ccpcerp-prod"
OPERATOR = "ccpcadmin"
RUN = "20261112T090214Z-0148d36b2cb678b3"
PREFIX = "ccpc_a3_restore_drill_20261112"
NETWORK = PREFIX + "_internal"
DB = PREFIX + "-db-1"
DB_VOLUME = PREFIX + "_db-data"
SITES_VOLUME = PREFIX + "_sites"
LOGS_VOLUME = PREFIX + "_logs"
SCHEMA = "ccpc_restore_20261112"
SITE = "ccpcerp.local"
TEST_SECRETS = Path("/var/lib/ccpc-a3-restore-db-secrets-20261112")
SITE_SECRETS = Path("/var/lib/ccpc-a3-restore-site-secrets-20261112")
APP = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
MYSQL = "sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4"
REDIS = "sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763"
ROLES = ("redis-cache", "redis-queue", "backend", "websocket", "frontend")
NEW = {role: PREFIX + "-" + role + "-1" for role in ROLES}
LABEL = "restore-20261112"
PROTECTED = {
    *(f"ccpc_prod_erpnext-{svc}-1" for svc in
      ("frontend", "backend", "websocket", "redis-cache", "redis-queue", "db")),
    *(f"{project}-{svc}-1" for project in
      ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
      for svc in ("db", "redis-cache", "redis-queue")),
}


class Stop(Exception):
    pass


def insist(ok: bool, reason: str) -> None:
    if not ok:
        raise Stop(reason)


def command(args: list[str], *, timeout: int = 45, check: bool = True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Stop("Guarded command unavailable or timed out") from None
    if check:
        insist(result.returncode == 0, "Guarded command failed")
    return result


def docker(*args: str, timeout: int = 45, check: bool = True) -> subprocess.CompletedProcess:
    return command(["docker", "--host", "unix:///var/run/docker.sock", *args],
                   timeout=timeout, check=check)


def names(*args: str) -> set[str]:
    return set(docker(*args).stdout.decode("utf8", "strict").splitlines())


def inspect(kind: str, name: str) -> dict:
    records = json.loads(docker(kind, "inspect", name).stdout)
    insist(isinstance(records, list) and len(records) == 1, "Invalid Docker inspect response")
    return records[0]


def secure_node(path: Path, mode: int, directory: bool, uid: int = 0) -> None:
    st = path.lstat()
    insist(st.st_uid == uid and st.st_gid == uid and
           stat.S_IMODE(st.st_mode) == mode and
           (stat.S_ISDIR(st.st_mode) if directory else stat.S_ISREG(st.st_mode)),
           "Protected path identity mismatch")


def sha(path: Path) -> str:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as f:
        a = os.fstat(f.fileno())
        insist(stat.S_ISREG(a.st_mode) and a.st_nlink == 1, "Unsafe file identity")
        h = hashlib.sha256()
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
        b = os.fstat(f.fileno())
        insist((a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns) ==
               (b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns), "File changed during read")
        return h.hexdigest()


def mysql_readonly(query: str) -> str:
    # No secret values in args or output; socket authenticated to isolated DB only.
    result = docker("exec", DB, "mariadb",
                    "--defaults-extra-file=/run/secrets/db-client.cnf",
                    "--batch", "--skip-column-names", "--execute=" + query)
    return result.stdout.decode("utf8", "strict").strip()


def guard_protected() -> None:
    actual = names("ps", "-a", "--format", "{{.Names}}")
    insist(actual == PROTECTED | {DB}, "Original twelve plus isolated DB inventory changed")
    insist(names("ps", "--format", "{{.Names}}") == actual,
           "Original or isolated test DB container stopped")
    for name in PROTECTED:
        project = next((p for p in ("ccpc_prod_erpnext",
                     "ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
                     if name.startswith(p + "-")), None)
        insist(project is not None and name.endswith("-1"), "Protected name invalid")
        service = name[len(project) + 1:-2]
        expected = APP if service in ("frontend", "backend", "websocket") else (
            MYSQL if service == "db" else REDIS)
        st = inspect("container", name)
        insist(st.get("Image") == expected and st.get("State", {}).get("Running") is True and
               not st.get("HostConfig", {}).get("PortBindings") and
               set(st.get("NetworkSettings", {}).get("Networks", {})) ==
               {project + "_default"}, "Protected original image/network/port changed")
    print("CCPC_STAGE3A_TWELVE_PROTECTED_ORIGINALS_PASS", flush=True)


def guard_site() -> None:
    for path in (TEST_SECRETS, SITE_SECRETS):
        secure_node(path, 0o700, True)
        secure_node(path / "DO_NOT_RETRY", 0o600, False)
        insist((path / "DO_NOT_RETRY").read_bytes() == (RUN + "\n").encode(),
               "Prior stage one-use marker missing")
    for f in ("mariadb-root-password", "db-client.cnf"):
        secure_node(TEST_SECRETS / f, 0o600, False)
    secure_node(SITE_SECRETS / "site-db.env", 0o600, False)
    account_content = (SITE_SECRETS / "site-db.env").read_bytes()
    insist(re.fullmatch(rb"DB_PASSWORD=[a-f0-9]{64}\n", account_content) is not None,
           "Test DB account secret malformed")
    password = account_content.decode("ascii").split("=", 1)[1].strip()
    volume = inspect("volume", SITES_VOLUME)
    path = "/var/lib/docker/volumes/" + SITES_VOLUME + "/_data"
    insist(volume.get("Driver") == "local" and volume.get("Options") in (None, {}) and
           volume.get("Mountpoint") == path and
           (volume.get("Labels") or {}).get("com.ccpc.test") == LABEL,
           "Test sites volume identity mismatch")
    root = Path(path)
    secure_node(root, 0o755, True, 0)
    secure_node(root / "common_site_config.json", 0o600, False, 1000)
    secure_node(root / "apps.txt", 0o644, False, 1000)
    insist((root / "apps.txt").read_bytes() == b"frappe\nerpnext\nccpcerp\n",
           "Restored apps selection mismatch")
    secure_node(root / SITE, 0o755, True, 1000)
    secure_node(root / SITE / "site_config.json", 0o600, False, 1000)
    insist({p.name for p in root.iterdir()} ==
           {"common_site_config.json", "apps.txt", SITE}, "Site root unexpected entries")
    site = root / SITE
    insist({p.name for p in site.iterdir()} ==
           {"site_config.json", "public", "private"}, "Site path unexpected entries")
    for section in ("public", "private"):
        secure_node(site / section, 0o755, True, 1000)
        secure_node(site / section / "files", 0o755, True, 1000)
    insist(not list((site / "public" / "files").iterdir()), "Unexpected public files")
    private = list((site / "private" / "files").iterdir())
    insist(len(private) == 1, "Unexpected private file count")
    secure_node(private[0], 0o600, False, 1000)
    insist(private[0].stat().st_size == 16501 and
           re.fullmatch(r"[0-9a-f]{64}", sha(private[0])) is not None,
           "Private attachment invalid")
    cfg = json.loads((site / "site_config.json").read_bytes())
    common = json.loads((root / "common_site_config.json").read_bytes())
    for config in (cfg, common):
        insist(config.get("db_host") == "db" and config.get("db_port") == 3306 and
               config.get("disable_scheduler") == 1 and config.get("pause_scheduler") == 1 and
               config.get("mute_emails") == 1 and config.get("developer_mode") == 0 and
               config.get("maintenance_mode") == 0,
               "Site side effect safety flags changed")
    insist(cfg.get("db_name") == SCHEMA and cfg.get("db_password") == password and
           isinstance(cfg.get("encryption_key"), str) and len(cfg["encryption_key"]) >= 20,
           "Restored site DB credentials/config mismatch")
    insist(common.get("redis_cache") == "redis://redis-cache:6379" and
           common.get("redis_queue") == "redis://redis-queue:6379" and
           common.get("redis_socketio") == "redis://redis-queue:6379",
           "Isolated Redis routing mismatch")
    print("CCPC_STAGE3A_SITE_CONFIG_AND_ONE_PRIVATE_FILE_PASS", flush=True)


def preflight() -> None:
    insist(os.geteuid() == 0 and os.environ.get("SUDO_USER") == OPERATOR and
           socket.gethostname().split(".")[0] == HOST, "Wrong NEW host / operator")
    insist(not any(x in os.environ for x in
                   ("DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME")),
           "Ambiguous Docker context")
    for mount in ("/mnt/ccpc-a3-restore-readonly-20261112",
                  "/mnt/ccpcerp-prod_backups"):
        m = command(["findmnt", "--mountpoint", mount, "--noheadings"], check=False)
        insist(m.returncode == 1, "NAS mount state ambiguous")
    insist(not any(os.path.islink(x) for x in
                   ("/var/lib/docker", "/var/lib/docker/volumes")),
           "Docker volume parent is a symlink")
    guard_protected()
    for i in (APP, MYSQL, REDIS):
        insist(docker("image", "inspect", "--format", "{{.Id}}", i).stdout.strip().decode() == i,
               "Pinned local image changed")
    net = inspect("network", NETWORK)
    db = inspect("container", DB)
    vol = inspect("volume", DB_VOLUME)
    insist(net.get("Internal") is True and net.get("Driver") == "bridge" and
           (net.get("Labels") or {}).get("com.ccpc.test") == LABEL and
           set((net.get("Containers") or {})) == {db.get("Id")},
           "Isolated test-only network identity/membership changed")
    insist(db.get("Image") == MYSQL and db.get("State", {}).get("Running") is True and
           db.get("State", {}).get("Health", {}).get("Status") == "healthy" and
           not db.get("HostConfig", {}).get("PortBindings") and
           set(db.get("NetworkSettings", {}).get("Networks", {})) == {NETWORK},
           "Isolated test DB health/network/port invalid")
    insist(vol.get("Driver") == "local" and
           vol.get("Mountpoint") == "/var/lib/docker/volumes/" + DB_VOLUME + "/_data" and
           (vol.get("Labels") or {}).get("com.ccpc.test") == LABEL,
           "Isolated test DB volume mismatch")
    insist({x for x in names("network", "ls", "--format", "{{.Name}}")
            if x.startswith(PREFIX)} == {NETWORK} and
           {x for x in names("volume", "ls", "--format", "{{.Name}}")
            if x.startswith(PREFIX)} == {DB_VOLUME, SITES_VOLUME},
           "Unexpected isolated namespace resources")
    insist(all(n not in names("ps", "-a", "--format", "{{.Names}}") for n in NEW.values()) and
           LOGS_VOLUME not in names("volume", "ls", "--format", "{{.Name}}"),
           "Stage3A already started/partial; never retry")
    insist(mysql_readonly("SELECT 1") == "1" and
           mysql_readonly("SELECT COUNT(*) FROM " + chr(96) + SCHEMA +
                          chr(96) + ".tabCompany") == "4",
           "Test DB credentials/company counts failed")
    guard_site()
    mem = re.search(r"^MemAvailable:\s+(\d+)\s+kB$", Path("/proc/meminfo").read_text(), re.M)
    insist(mem is not None and int(mem.group(1)) * 1024 >= 4 * 1024 ** 3,
           "Insufficient RAM headroom for bounded isolated Frappe startup")
    print("CCPC_STAGE3A_PINNED_IMAGES_AND_INTERNAL_DB_PASS", flush=True)
    print("CCPC_STAGE3A_UNUSED_APP_CONTAINERS_AND_LOGS_VOLUME_PASS", flush=True)


def test_container(name: str, image: str, mounts: int) -> None:
    st = inspect("container", name)
    actual = {(m.get("Type"), m.get("Name"), m.get("Destination")) for m in
              (st.get("Mounts") or [])}
    expected = set() if mounts == 0 else {
        ("volume", SITES_VOLUME, "/home/frappe/frappe-bench/sites"),
        ("volume", LOGS_VOLUME, "/home/frappe/frappe-bench/logs"),
    }
    insist(st.get("Image") == image and st.get("State", {}).get("Running") is True and
           not st.get("HostConfig", {}).get("PortBindings") and
           set(st.get("NetworkSettings", {}).get("Networks", {})) == {NETWORK} and
           (st.get("HostConfig", {}).get("RestartPolicy") or {}).get("Name") == "no" and
           (st.get("HostConfig", {}).get("SecurityOpt") or []) == ["no-new-privileges"] and
           (st.get("Config", {}).get("Labels") or {}).get("com.ccpc.test") == LABEL and
           len(actual) == mounts and actual == expected,
           "New isolated container identity/network/mount/security invalid")


def once() -> None:
    preflight()
    # All mutations below are test-only; never rerun after any partial STOP.
    docker("volume", "create", "--label", "com.ccpc.test=" + LABEL, LOGS_VOLUME)
    vol = inspect("volume", LOGS_VOLUME)
    path = "/var/lib/docker/volumes/" + LOGS_VOLUME + "/_data"
    insist(vol.get("Driver") == "local" and vol.get("Options") in (None, {}) and
           vol.get("Mountpoint") == path and
           (vol.get("Labels") or {}).get("com.ccpc.test") == LABEL,
           "New logs volume identity failed")
    root = Path(path)
    st = root.lstat()
    insist(stat.S_ISDIR(st.st_mode) and st.st_uid == 0 and st.st_gid == 0 and
           not list(root.iterdir()), "Logs volume not empty/root owned")
    os.chown(root, 1000, 1000)
    os.chmod(root, 0o755)
    secure_node(root, 0o755, True, 1000)
    print("CCPC_STAGE3A_NEW_TEST_ONLY_LOGS_VOLUME_PASS", flush=True)

    common = [
        "run", "-d", "--pull=never", "--restart=no",
        "--network", NETWORK,
        "--security-opt", "no-new-privileges", "--cap-drop=ALL",
        "--label", "com.ccpc.test=" + LABEL,
        "--pids-limit", "256",
    ]
    for role in ("redis-cache", "redis-queue"):
        docker(*common, "--name", NEW[role], "--network-alias", role,
               "--memory", "256m", "--cpus", "0.5", "--user", "redis",
               REDIS, "redis-server", "--save", "", "--appendonly", "no",
               "--protected-mode", "no", "--maxmemory", "128mb",
               "--maxmemory-policy", "allkeys-lru", timeout=60)
        test_container(NEW[role], REDIS, 0)
        insist(docker("exec", NEW[role], "redis-cli", "ping", timeout=12).stdout.strip() == b"PONG",
               "Isolated test Redis not responding")
        print("CCPC_STAGE3A_" + role.upper().replace("-", "_") + "_INTERNAL_PASS", flush=True)

    mounts = [
        "--mount", "type=volume,source=" + SITES_VOLUME +
                   ",target=/home/frappe/frappe-bench/sites,volume-nocopy",
        "--mount", "type=volume,source=" + LOGS_VOLUME +
                   ",target=/home/frappe/frappe-bench/logs,volume-nocopy",
    ]
    for role, entry, env in (
        ("backend", ["start.sh"], ["--env", "GUNICORN_WORKERS=2",
                                   "--env", "GUNICORN_THREADS=4"]),
        ("websocket", ["node", "/home/frappe/frappe-bench/apps/frappe/socketio.js"], []),
        ("frontend", ["nginx-entrypoint.sh"], [
            "--env", "BACKEND=backend:8000", "--env", "SOCKETIO=websocket:9000",
            "--env", "FRAPPE_SITE_NAME_HEADER=ccpcerp.local"]),
    ):
        docker(*common, "--name", NEW[role], "--network-alias", role,
               "--memory", "768m" if role == "backend" else "384m",
               "--cpus", "1", "--user", "1000:1000", *env, *mounts,
               APP, *entry, timeout=90)
        test_container(NEW[role], APP, 2)
        print("CCPC_STAGE3A_" + role.upper() + "_INTERNAL_STARTED_PASS", flush=True)

    expected = PROTECTED | {DB} | set(NEW.values())
    insist(names("ps", "-a", "--format", "{{.Names}}") == expected and
           names("ps", "--format", "{{.Names}}") == expected,
           "Protected or isolated containers changed after startup")
    net = inspect("network", NETWORK)
    actual_ids = {inspect("container", n)["Id"] for n in {DB} | set(NEW.values())}
    insist(net.get("Internal") is True and set(net.get("Containers", {})) == actual_ids and
           {n for n in names("volume", "ls", "--format", "{{.Name}}") if n.startswith(PREFIX)}
           == {DB_VOLUME, SITES_VOLUME, LOGS_VOLUME},
           "Isolated namespace/volume membership changed after startup")
    print("CCPC_STAGE3A_PROTECTED_ORIGINALS_AND_NO_PUBLISHED_PORTS_PASS", flush=True)

    # No public ports or host/DNS traffic. Only request the login page inside
    # private frontend; never print page body, headers, cookies or app logs.
    ok = False
    for attempt in range(20):
        response = docker("exec", NEW["frontend"], "curl",
                          "-sS", "--max-time", "5", "-o", "/dev/null",
                          "-w", "%{http_code}", "-H", "Host: ccpcerp.local",
                          "http://127.0.0.1:8080/login", timeout=12, check=False)
        if response.returncode == 0 and response.stdout.strip() == b"200":
            ok = True
            break
        if attempt < 19:
            time.sleep(2)
    insist(ok, "Internal isolated Frappe login did not return HTTP 200; preserve state")
    print("CCPC_STAGE3A_ISOLATED_FRAPPE_LOGIN_HTTP_200_PASS", flush=True)
    print("CCPC_NEW_A3_RESTORE_STAGE3A_INTERNAL_APP_PASS_BUSINESS_ACCEPTANCE_PENDING", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEW A3 Stage3A internal-only Frappe smoke")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            preflight()
            print("CCPC_NEW_A3_RESTORE_STAGE3A_READONLY_PREFLIGHT_PASS", flush=True)
        else:
            once()
    except Exception:
        print("CCPC_NEW_A3_RESTORE_STAGE3A_STOP_REVIEW_REQUIRED", flush=True)
        raise SystemExit(1)
