#!/usr/bin/env python3
"""Stage3R: ONE-USE forward-only recovery after isolated Stage3A backend STOP.

--preflight is strictly read-only. It verifies the consumed Stage3A partial
state, original 12 protected containers, isolated database/Redis, sites and
logs volumes, root ownership mismatch, and absent repair marker/backend.
--execute rechecks guards, writes a new no-retry marker, changes ONLY the test
sites-volume ROOT owner 0:0 -> 1000:1000 (no recursive chown), and starts a
SEPARATELY NAMED internal-only replacement backend. Tests only localhost HTTP.

Never start the previously failed backend, rerun Stage3A, alter any existing
container, perform migrations, publish ports, start workers, or cleanup after
a STOP. Preserve partial resources for review.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import time

OPERATOR = "ccpcadmin"
HOSTNAME = "ccpcerp-prod"
PREFIX = "ccpc_a3_restore_drill_20261112"
NETWORK = PREFIX + "_internal"
DB = PREFIX + "-db-1"
RC = PREFIX + "-redis-cache-1"
RQ = PREFIX + "-redis-queue-1"
FAILED = PREFIX + "-backend-1"
RECOVERED = PREFIX + "-backend-recovery1-1"
SITES = PREFIX + "_sites"
LOGS = PREFIX + "_logs"
DB_VOLUME = PREFIX + "_db-data"
SITE = "ccpcerp.local"
SCHEMA = "ccpc_restore_20261112"
RUN_MARKER = "20261112T090214Z-0148d36b2cb678b3"
SITE_SECRETS = Path("/var/lib/ccpc-a3-restore-site-secrets-20261112")
DB_SECRETS = Path("/var/lib/ccpc-a3-restore-db-secrets-20261112")
REPAIR_MARKER = Path("/var/lib/ccpc-a3-stage3r-repair1-20261113")
APP_IMAGE = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
MYSQL_IMAGE = "sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4"
REDIS_IMAGE = "sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763"
TAG = "restore-20261112"
ORIGINALS = {
    *(f"ccpc_prod_erpnext-{s}-1" for s in
      ("frontend", "backend", "websocket", "redis-cache", "redis-queue", "db")),
    *(f"{p}-{s}-1" for p in
      ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
      for s in ("db", "redis-cache", "redis-queue")),
}


class Stop(Exception):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Stop(reason)


def run(argv: list[str], *, seconds: int = 35, allow_failure: bool = False) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(argv, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, timeout=seconds,
                                check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Stop("Command unavailable or timed out") from None
    require(allow_failure or result.returncode == 0, "Command failed")
    return result


def docker(*args: str, seconds: int = 35, allow_failure: bool = False) -> subprocess.CompletedProcess:
    return run(["docker", "--host", "unix:///var/run/docker.sock", *args],
               seconds=seconds, allow_failure=allow_failure)


def names(*args: str) -> set[str]:
    return set(docker(*args).stdout.decode("utf8", "strict").splitlines())


def inspect(kind: str, name: str) -> dict:
    result = json.loads(docker(kind, "inspect", name).stdout)
    require(isinstance(result, list) and len(result) == 1, "Inspect response invalid")
    return result[0]


def check_path(path: Path, *, uid: int, mode: int, directory: bool) -> None:
    s = path.lstat()
    require((stat.S_ISDIR(s.st_mode) if directory else stat.S_ISREG(s.st_mode))
            and s.st_uid == uid and s.st_gid == uid
            and stat.S_IMODE(s.st_mode) == mode,
            "Isolated recovery path owner/type/mode unexpected")


def check_mount(volname: str, *, owner: int) -> Path:
    obj = inspect("volume", volname)
    path = Path("/var/lib/docker/volumes") / volname / "_data"
    require(obj.get("Name") == volname and obj.get("Driver") == "local"
            and obj.get("Options") in ({}, None)
            and obj.get("Mountpoint") == str(path)
            and (obj.get("Labels") or {}).get("com.ccpc.test") == TAG,
            "Unexpected isolated Docker volume identity")
    check_path(path, uid=owner, mode=0o755, directory=True)
    return path


def check_originals() -> None:
    for name in ORIGINALS:
        project = next((p for p in
                        ("ccpc_prod_erpnext", "ccpc_full_acceptance_20261107",
                         "ccpc_restore_rehearsal_20261107")
                        if name.startswith(p + "-")), None)
        require(project is not None and name.endswith("-1"),
                "Protected original identity unexpected")
        service = name[len(project) + 1:-2]
        image = APP_IMAGE if service in ("frontend", "backend", "websocket") else (
            MYSQL_IMAGE if service == "db" else REDIS_IMAGE)
        obj = inspect("container", name)
        require(obj.get("Image") == image and obj.get("State", {}).get("Running") is True
                and not obj.get("HostConfig", {}).get("PortBindings")
                and set((obj.get("NetworkSettings", {}).get("Networks") or {})) ==
                {project + "_default"},
                "Protected container changed")
    print("CCPC_STAGE3R_TWELVE_PROTECTED_ORIGINALS_PASS", flush=True)


def test_service(name: str, image: str) -> dict:
    obj = inspect("container", name)
    require(obj.get("Image") == image
            and obj.get("State", {}).get("Running") is True
            and not obj.get("HostConfig", {}).get("PortBindings")
            and set((obj.get("NetworkSettings", {}).get("Networks") or {})) == {NETWORK}
            and (obj.get("HostConfig", {}).get("RestartPolicy") or {}).get("Name") == "no"
            and (obj.get("Config", {}).get("Labels") or {}).get("com.ccpc.test") == TAG,
            "Isolated test service changed")
    return obj


def check_failed_backend() -> None:
    obj = inspect("container", FAILED)
    state = obj.get("State", {})
    require(obj.get("Image") == APP_IMAGE
            and state.get("Status") == "exited"
            and state.get("ExitCode") == 1
            and state.get("OOMKilled") is False
            and state.get("Error") in ("", None)
            and obj.get("RestartCount") == 0
            and not obj.get("HostConfig", {}).get("PortBindings")
            and (obj.get("HostConfig", {}).get("RestartPolicy") or {}).get("Name") == "no"
            and (obj.get("Config", {}).get("User") == "1000:1000")
            and (obj.get("Config", {}).get("Labels") or {}).get("com.ccpc.test") == TAG,
            "Failed test backend state changed")
    mounts = {(m.get("Type"), m.get("Name"), m.get("Destination"))
              for m in obj.get("Mounts") or []}
    require(mounts == {
        ("volume", SITES, "/home/frappe/frappe-bench/sites"),
        ("volume", LOGS, "/home/frappe/frappe-bench/logs"),
    }, "Failed backend volume mounts unexpected")
    print("CCPC_STAGE3R_FAILED_BACKEND_PRESERVED_EXIT1_PASS", flush=True)


def check_site_and_config(root: Path) -> None:
    check_path(root / "common_site_config.json", uid=1000, mode=0o600, directory=False)
    check_path(root / "apps.txt", uid=1000, mode=0o644, directory=False)
    require((root / "apps.txt").read_bytes() == b"frappe\nerpnext\nccpcerp\n",
            "Installed app listing changed")
    require({p.name for p in root.iterdir()} ==
            {"common_site_config.json", "apps.txt", SITE},
            "Isolated sites root entries changed")
    site = root / SITE
    check_path(site, uid=1000, mode=0o755, directory=True)
    require({p.name for p in site.iterdir()} == {"site_config.json", "public", "private"},
            "Restored site layout changed")
    check_path(site / "site_config.json", uid=1000, mode=0o600, directory=False)
    for s in ("public", "private"):
        check_path(site / s, uid=1000, mode=0o755, directory=True)
        check_path(site / s / "files", uid=1000, mode=0o755, directory=True)
    require(not list((site / "public" / "files").iterdir()),
            "Public test files unexpected")
    private_files = list((site / "private" / "files").iterdir())
    require(len(private_files) == 1, "Restored private file count changed")
    check_path(private_files[0], uid=1000, mode=0o600, directory=False)
    require(private_files[0].stat().st_size == 16501,
            "Restored private attachment size changed")
    config = json.loads((site / "site_config.json").read_bytes())
    common = json.loads((root / "common_site_config.json").read_bytes())
    for item in (config, common):
        require(item.get("db_host") == "db" and item.get("db_port") == 3306
                and item.get("disable_scheduler") == 1
                and item.get("pause_scheduler") == 1
                and item.get("mute_emails") == 1
                and item.get("developer_mode") == 0
                and item.get("maintenance_mode") == 0,
                "Forbidden application side-effect configuration")
    require(config.get("db_name") == SCHEMA
            and isinstance(config.get("encryption_key"), str)
            and len(config["encryption_key"]) >= 20,
            "Restored DB schema/encryption key invalid")
    require(common.get("redis_cache") == "redis://redis-cache:6379"
            and common.get("redis_queue") == "redis://redis-queue:6379"
            and common.get("redis_socketio") == "redis://redis-queue:6379",
            "Redis connection points outside test-only service names")
    check_path(SITE_SECRETS, uid=0, mode=0o700, directory=True)
    check_path(DB_SECRETS, uid=0, mode=0o700, directory=True)
    for directory in (SITE_SECRETS, DB_SECRETS):
        check_path(directory / "DO_NOT_RETRY", uid=0, mode=0o600, directory=False)
        require((directory / "DO_NOT_RETRY").read_bytes() ==
                (RUN_MARKER + "\n").encode(),
                "Previous one-use marker changed")
    check_path(SITE_SECRETS / "site-db.env", uid=0, mode=0o600, directory=False)
    account = (SITE_SECRETS / "site-db.env").read_bytes()
    require(re.fullmatch(rb"DB_PASSWORD=[0-9a-f]{64}\n", account) is not None
            and config.get("db_password") ==
            account.decode("ascii").split("=", 1)[1].strip(),
            "Test-only DB credentials changed")
    print("CCPC_STAGE3R_RESTORED_SITE_SECRETS_AND_FLAGS_PASS", flush=True)


def preflight() -> None:
    require(os.geteuid() == 0 and os.environ.get("SUDO_USER") == OPERATOR
            and socket.gethostname().split(".")[0] == HOSTNAME,
            "Wrong host or operator")
    require(not any(k in os.environ for k in
                    ("DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE",
                     "COMPOSE_PROJECT_NAME", "DB_PASSWORD")),
            "Ambient target override present")
    require(not any(os.path.islink(x) for x in
                    ("/var/lib/docker", "/var/lib/docker/volumes",
                     "/var/lib/ccpc-a3-restore-site-secrets-20261112")),
            "Unsafe host path symlink")
    for mount in ("/mnt/ccpc-a3-restore-readonly-20261112", "/mnt/ccpcerp-prod_backups"):
        cmd = run(["findmnt", "--mountpoint", mount, "--noheadings"],
                  allow_failure=True)
        require(cmd.returncode == 1, "Unexpected NAS mount")
    require(not REPAIR_MARKER.exists() and not REPAIR_MARKER.is_symlink(),
            "Repair already attempted; NEVER retry")
    required = ORIGINALS | {DB, RC, RQ, FAILED}
    running = ORIGINALS | {DB, RC, RQ}
    require(names("ps", "-a", "--format", "{{.Names}}") == required
            and names("ps", "--format", "{{.Names}}") == running
            and RECOVERED not in required, "Unexpected test or protected containers")
    require({n for n in names("volume", "ls", "--format", "{{.Name}}")
             if n.startswith(PREFIX)} == {DB_VOLUME, SITES, LOGS}
            and {n for n in names("network", "ls", "--format", "{{.Name}}")
                 if n.startswith(PREFIX)} == {NETWORK},
            "Unexpected isolated test volume/network inventory")
    check_originals()
    for image in (APP_IMAGE, MYSQL_IMAGE, REDIS_IMAGE):
        require(docker("image", "inspect", "--format", "{{.Id}}", image).
                stdout.decode("ascii", "strict").strip() == image,
                "Pinned image not available")
    db = test_service(DB, MYSQL_IMAGE)
    require((db.get("State", {}).get("Health") or {}).get("Status") == "healthy",
            "Isolated database no longer healthy")
    test_service(RC, REDIS_IMAGE)
    test_service(RQ, REDIS_IMAGE)
    net = inspect("network", NETWORK)
    require(net.get("Internal") is True and net.get("Attachable") is False
            and net.get("Driver") == "bridge"
            and (net.get("Labels") or {}).get("com.ccpc.test") == TAG
            and set((net.get("Containers") or {})) ==
            {inspect("container", n)["Id"] for n in (DB, RC, RQ)},
            "Test network membership or isolation changed")
    ipam = net.get("IPAM", {}).get("Config") or []
    require(len(ipam) == 1, "Unexpected test network subnet")
    subnet = ipaddress.ip_network(ipam[0]["Subnet"], strict=True)
    require(isinstance(subnet, ipaddress.IPv4Network) and
            any(subnet.subnet_of(ipaddress.ip_network(cidr)) for cidr in
                ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")),
            "Non-private isolated network")
    check_failed_backend()
    check_mount(DB_VOLUME, owner=0)
    sites_root = check_mount(SITES, owner=0)
    check_mount(LOGS, owner=1000)
    check_site_and_config(sites_root)
    # Root is 0:0 mode 0755, Frappe runs as UID/GID 1000. This is the
    # specific repair target; don't change site children or other volumes.
    require(os.stat(sites_root).st_mode & stat.S_IWOTH == 0,
            "Root ownership mismatch already altered")
    mem = re.search(r"^MemAvailable:\s+(\d+)\s+kB$", Path("/proc/meminfo").read_text(), re.M)
    require(mem is not None and int(mem.group(1)) >= 2 * 1024 * 1024,
            "Insufficient available host memory for repair backend")
    print("CCPC_STAGE3R_ONLY_TEST_SITES_ROOT_OWNER_MISMATCH_PASS", flush=True)
    print("CCPC_STAGE3R_UNUSED_REPAIR_MARKER_AND_BACKEND_PASS", flush=True)


PROBE = (
    "import http.client\n"
    "c=http.client.HTTPConnection('127.0.0.1',8000,timeout=4)\n"
    "c.request('GET','/login',headers={'Host':'ccpcerp.local'})\n"
    "r=c.getresponse()\n"
    "print(r.status)\n"
    "r.read(0)\n"
    "c.close()\n"
)


def once() -> None:
    preflight()
    # ONE-USE marker is first mutation; any subsequent failure is non-retryable.
    old_umask = os.umask(0o077)
    try:
        REPAIR_MARKER.mkdir(mode=0o700)
        check_path(REPAIR_MARKER, uid=0, mode=0o700, directory=True)
        marker = REPAIR_MARKER / "DO_NOT_RETRY"
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(b"STAGE3R_ONE_USE_20261113\n")
            output.flush()
            os.fsync(output.fileno())
        check_path(marker, uid=0, mode=0o600, directory=False)
        print("CCPC_STAGE3R_NEW_ONE_USE_REPAIR_MARKER_PASS", flush=True)

        sites_root = Path("/var/lib/docker/volumes") / SITES / "_data"
        check_path(sites_root, uid=0, mode=0o755, directory=True)
        os.chown(sites_root, 1000, 1000, follow_symlinks=False)
        check_path(sites_root, uid=1000, mode=0o755, directory=True)
        print("CCPC_STAGE3R_ONLY_SITES_ROOT_OWNER_REPAIRED_PASS", flush=True)

        docker(
            "run", "-d", "--pull=never", "--restart=no",
            "--name", RECOVERED, "--network", NETWORK,
            "--network-alias", "backend",
            "--security-opt", "no-new-privileges", "--cap-drop=ALL",
            "--pids-limit", "256", "--memory", "768m", "--cpus", "1",
            "--user", "1000:1000",
            "--label", "com.ccpc.test=" + TAG,
            "--label", "com.ccpc.stage=restore-stage3r-repair1",
            "--env", "GUNICORN_WORKERS=2", "--env", "GUNICORN_THREADS=4",
            "--mount", "type=volume,source=" + SITES +
                       ",target=/home/frappe/frappe-bench/sites,volume-nocopy",
            "--mount", "type=volume,source=" + LOGS +
                       ",target=/home/frappe/frappe-bench/logs,volume-nocopy",
            APP_IMAGE, "start.sh", seconds=90,
        )
        obj = test_service(RECOVERED, APP_IMAGE)
        mounts = {(m.get("Type"), m.get("Name"), m.get("Destination"))
                  for m in obj.get("Mounts") or []}
        require(mounts == {
            ("volume", SITES, "/home/frappe/frappe-bench/sites"),
            ("volume", LOGS, "/home/frappe/frappe-bench/logs"),
        } and (obj.get("Config", {}).get("User") == "1000:1000")
                and (obj.get("HostConfig", {}).get("SecurityOpt") or []) in
                (["no-new-privileges"], ["no-new-privileges:true"]),
                "Recovered backend mounts/user/security unexpected")
        print("CCPC_STAGE3R_NEW_SEPARATE_INTERNAL_BACKEND_STARTED_PASS", flush=True)

        expected_all = ORIGINALS | {DB, RC, RQ, FAILED, RECOVERED}
        expected_running = ORIGINALS | {DB, RC, RQ, RECOVERED}
        require(names("ps", "-a", "--format", "{{.Names}}") == expected_all
                and names("ps", "--format", "{{.Names}}") == expected_running,
                "Original or test container inventory changed after repair")
        check_originals()
        require(inspect("container", FAILED).get("State", {}).get("Status") == "exited",
                "Original failed test backend should remain exited")
        net = inspect("network", NETWORK)
        require(net.get("Internal") is True
                and set((net.get("Containers") or {})) ==
                {inspect("container", n)["Id"] for n in (DB, RC, RQ, RECOVERED)},
                "Test-only network membership unexpectedly changed")
        check_path(sites_root, uid=1000, mode=0o755, directory=True)
        print("CCPC_STAGE3R_PROTECTED_ORIGINALS_AND_TEST_ISOLATION_PASS", flush=True)

        ok = False
        for i in range(20):
            status = docker("exec", RECOVERED, "python3", "-c", PROBE,
                            seconds=12, allow_failure=True)
            if status.returncode == 0 and status.stdout.strip() == b"200":
                ok = True
                break
            if i < 19:
                time.sleep(2)
        require(ok, "Recovered backend HTTP 200 not established; preserve partial state")
        print("CCPC_STAGE3R_RECOVERED_BACKEND_LOCAL_LOGIN_HTTP_200_PASS", flush=True)
        print("CCPC_NEW_A3_RESTORE_STAGE3R_BACKEND_RECOVERY_PASS_FRONTEND_AND_BUSINESS_PENDING", flush=True)
    finally:
        os.umask(old_umask)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEW isolated Stage3R forward-only recovery")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--execute", action="store_true")
    arguments = parser.parse_args()
    try:
        if arguments.preflight:
            preflight()
            print("CCPC_NEW_A3_RESTORE_STAGE3R_READONLY_PREFLIGHT_PASS", flush=True)
        else:
            once()
    except Exception:
        print("CCPC_NEW_A3_RESTORE_STAGE3R_STOP_PRESERVE_NO_RETRY", flush=True)
        raise SystemExit(1)
