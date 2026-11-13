#!/usr/bin/env python3
"""Stage3T: ONE-USE, isolated frontend/websocket completion after Stage3S.

--preflight is read-only; --execute first consumes a fresh one-use marker,
then creates ONLY distinct internal-only frontend and websocket containers.
No OLD PROD/DEV, working NEW A3, migrations, workers, external host ports,
restarts, cleanup or retry. Preserve partial state after any STOP.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import sys
import time
import types

OPERATOR = "ccpcadmin"
HOSTNAME = "ccpcerp-prod"
PREFIX = "ccpc_a3_restore_drill_20261112"
WEBSOCKET = PREFIX + "-websocket-completion1-1"
FRONTEND = PREFIX + "-frontend-completion1-1"
STAGE = "restore-stage3t-frontend-websocket1"
MARKER = Path("/var/lib/ccpc-a3-stage3t-frontend-websocket1-20261113")
R_SOURCE = Path("/root/ccpc_new_a3_restore_stage3r_sites_owner_and_backend_recovery.py")
R_SHA = "a05e3f53d49766f42bd97f7bb508f59e7c282399ce3766cf46082138e626bdbe"
S_SOURCE = Path("/root/ccpc_new_a3_restore_stage3s_site_logs_repair_revision2.py")
S_SHA = "c4bcea4abfcd946c3b39850a492efd7d0c7f216d45e5159fb3c735070e5c7290"

class Stop(Exception):
    pass

def need(ok, reason):
    if not ok:
        raise Stop(reason)

def root_node(p, mode, directory):
    st = p.lstat()
    need((stat.S_ISDIR(st.st_mode) if directory else stat.S_ISREG(st.st_mode))
         and st.st_uid == 0 and st.st_gid == 0
         and stat.S_IMODE(st.st_mode) == mode,
         "Root-only source or marker identity changed")

def load_helper(p, sha, name):
    root_node(p, 0o600, False)
    raw = p.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == sha, "Reviewed helper checksum changed")
    mod = types.ModuleType(name)
    mod.__file__ = str(p)
    exec(compile(raw, str(p), "exec"), mod.__dict__)
    return mod

def check_marker(p, payload):
    root_node(p, 0o700, True)
    need({f.name for f in p.iterdir()} == {"DO_NOT_RETRY"},
         "One-use marker contents changed")
    root_node(p / "DO_NOT_RETRY", 0o600, False)
    need((p / "DO_NOT_RETRY").read_bytes() == payload,
         "One-use marker payload changed")

def preflight(r, s):
    need(os.geteuid() == 0 and os.environ.get("SUDO_USER") == OPERATOR
         and socket.gethostname().split(".")[0] == HOSTNAME,
         "Wrong host/operator")
    need(not any(x in os.environ for x in
                 ("DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE",
                  "COMPOSE_PROJECT_NAME", "DB_PASSWORD")),
         "Ambient Docker/DB override")
    need(not any(os.path.islink(x) for x in
                 ("/var/lib/docker", "/var/lib/docker/volumes",
                  "/var/lib/ccpc-a3-restore-site-secrets-20261112")),
         "Protected host path symlink")
    for mp in ("/mnt/ccpc-a3-restore-readonly-20261112",
               "/mnt/ccpcerp-prod_backups"):
        proc = r.run(["findmnt", "--mountpoint", mp, "--noheadings"],
                     allow_failure=True)
        need(proc.returncode == 1, "Unexpected NAS mount state")
    check_marker(r.REPAIR_MARKER, b"STAGE3R_ONE_USE_20261113\n")
    check_marker(s.MARKER, b"STAGE3S_ONE_USE_20261113\n")
    need(not MARKER.exists() and not MARKER.is_symlink(),
         "Stage3T previously attempted; NEVER retry")
    existing = r.ORIGINALS | {r.DB, r.RC, r.RQ, r.FAILED, r.RECOVERED}
    need(r.names("ps", "-a", "--format", "{{.Names}}") == existing
         and r.names("ps", "--format", "{{.Names}}") == existing - {r.FAILED},
         "Unexpected protected or test container inventory")
    need({v for v in r.names("volume", "ls", "--format", "{{.Name}}")
          if v.startswith(PREFIX)} == {r.DB_VOLUME, r.SITES, r.LOGS}
         and {v for v in r.names("network", "ls", "--format", "{{.Name}}")
              if v.startswith(PREFIX)} == {r.NETWORK},
         "Unexpected isolated test Docker resources")
    r.check_originals()
    r.check_failed_backend()
    for image in (r.APP_IMAGE, r.MYSQL_IMAGE, r.REDIS_IMAGE):
        need(r.docker("image", "inspect", "--format", "{{.Id}}", image)
             .stdout.decode("ascii", "strict").strip() == image,
             "Pinned local image unavailable")
    db = r.test_service(r.DB, r.MYSQL_IMAGE, require_label=False)
    need((db.get("State", {}).get("Health") or {}).get("Status") == "healthy",
         "Test database unhealthy")
    result = r.docker(
        "exec", r.DB, "mariadb",
        "--defaults-extra-file=/run/secrets/db-client.cnf",
        "--batch", "--skip-column-names",
        "--execute=SELECT COUNT(*) FROM " + chr(96) + r.SCHEMA +
        chr(96) + "." + chr(96) + "tabCompany" + chr(96) + ";")
    need(result.stdout.strip() == b"4", "Test database Company count changed")
    r.test_service(r.RC, r.REDIS_IMAGE)
    r.test_service(r.RQ, r.REDIS_IMAGE)
    backend = r.test_service(r.RECOVERED, r.APP_IMAGE)
    mounts = {(m.get("Type"), m.get("Name"), m.get("Destination"))
              for m in backend.get("Mounts") or []}
    aliases = ((backend.get("NetworkSettings", {}).get("Networks") or {})
               .get(r.NETWORK, {}).get("Aliases") or [])
    need(backend.get("Config", {}).get("User") == "1000:1000"
         and (backend.get("Config", {}).get("Labels") or {})
             .get("com.ccpc.stage") == "restore-stage3r-repair1"
         and mounts == {
             ("volume", r.SITES, "/home/frappe/frappe-bench/sites"),
             ("volume", r.LOGS, "/home/frappe/frappe-bench/logs")}
         and "backend" in aliases,
         "Existing recovery backend identity/alias changed")
    net = r.inspect("network", r.NETWORK)
    members = {r.DB, r.RC, r.RQ, r.RECOVERED}
    ipam = net.get("IPAM", {}).get("Config") or []
    need(net.get("Internal") is True and net.get("Attachable") is False
         and net.get("Driver") == "bridge"
         and (net.get("Labels") or {}).get("com.ccpc.test") == r.TAG
         and set(net.get("Containers") or {}) ==
             {r.inspect("container", n)["Id"] for n in members}
         and len(ipam) == 1, "Existing internal network changed")
    subnet = ipaddress.ip_network(ipam[0]["Subnet"], strict=True)
    need(isinstance(subnet, ipaddress.IPv4Network)
         and any(subnet.subnet_of(ipaddress.ip_network(cidr)) for cidr in
                 ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")),
         "Isolated network subnet unexpected")
    r.check_mount(r.DB_VOLUME, owner=None)
    sites_root = r.check_mount(r.SITES, owner=1000)
    r.check_mount(r.LOGS, owner=1000)
    s.check_restored_site_with_runtime_assets(r, sites_root, logs_created=True)
    mem = re.search(r"^MemAvailable:\s+(\d+)\s+kB$",
                    Path("/proc/meminfo").read_text(), re.M)
    need(mem is not None and int(mem.group(1)) >= 4 * 1024 * 1024,
         "Insufficient available memory")
    need(shutil.disk_usage("/var/lib/docker").free >= 20 * 1024 ** 3,
         "Insufficient free Docker filesystem")
    print("CCPC_STAGE3T_PROTECTED_ORIGINALS_AND_EXISTING_BACKEND_PASS", flush=True)
    print("CCPC_STAGE3T_PINNED_NETWORK_SITE_AND_RESOURCES_PASS", flush=True)
    print("CCPC_NEW_A3_RESTORE_STAGE3T_READONLY_PREFLIGHT_PASS", flush=True)

def check_new(r, name, alias):
    obj = r.test_service(name, r.APP_IMAGE)
    hc = obj.get("HostConfig", {})
    labels = obj.get("Config", {}).get("Labels") or {}
    mounts = {(m.get("Type"), m.get("Name"), m.get("Destination"))
              for m in obj.get("Mounts") or []}
    aliases = ((obj.get("NetworkSettings", {}).get("Networks") or {})
               .get(r.NETWORK, {}).get("Aliases") or [])
    need(labels.get("com.ccpc.stage") == STAGE
         and labels.get("com.ccpc.test") == r.TAG
         and obj.get("Config", {}).get("User") == "1000:1000"
         and (hc.get("SecurityOpt") or []) in
             (["no-new-privileges"], ["no-new-privileges:true"])
         and {str(x).lower() for x in hc.get("CapDrop") or []} == {"all"}
         and hc.get("Memory") == 384 * 1024 * 1024
         and hc.get("PidsLimit") == 256
         and alias in aliases
         and mounts == {
             ("volume", r.SITES, "/home/frappe/frappe-bench/sites"),
             ("volume", r.LOGS, "/home/frappe/frappe-bench/logs")},
         "New isolated container has unexpected security/mount identity")

FRONT_PROBE = (
    "import http.client\n"
    "c=http.client.HTTPConnection('127.0.0.1',8080,timeout=5)\n"
    "c.request('GET','/login',headers={'Host':'ccpcerp.local'})\n"
    "print(c.getresponse().status)\n"
    "c.close()\n"
)
WS_PROBE = (
    "import socket\n"
    "s=socket.create_connection(('websocket',9000),timeout=4)\n"
    "s.close()\n"
    "print('READY')\n"
)

def once(r, s):
    preflight(r, s)
    # First mutation consumes the attempt, including if subsequent actions fail.
    umask = os.umask(0o077)
    try:
        MARKER.mkdir(mode=0o700)
        root_node(MARKER, 0o700, True)
        fd = os.open(MARKER / "DO_NOT_RETRY",
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(b"STAGE3T_ONE_USE_20261113\n")
            f.flush()
            os.fsync(f.fileno())
        check_marker(MARKER, b"STAGE3T_ONE_USE_20261113\n")
        print("CCPC_STAGE3T_NEW_ONE_USE_MARKER_PASS", flush=True)
        common = [
            "run", "-d", "--pull=never", "--restart=no",
            "--network", r.NETWORK,
            "--security-opt", "no-new-privileges", "--cap-drop=ALL",
            "--pids-limit", "256", "--memory", "384m", "--cpus", "1",
            "--user", "1000:1000",
            "--label", "com.ccpc.test=" + r.TAG,
            "--label", "com.ccpc.stage=" + STAGE,
            "--mount", "type=volume,source=" + r.SITES +
                       ",target=/home/frappe/frappe-bench/sites,volume-nocopy",
            "--mount", "type=volume,source=" + r.LOGS +
                       ",target=/home/frappe/frappe-bench/logs,volume-nocopy",
        ]
        r.docker(*common, "--name", WEBSOCKET,
                 "--network-alias", "websocket", r.APP_IMAGE,
                 "node", "/home/frappe/frappe-bench/apps/frappe/socketio.js",
                 seconds=90)
        check_new(r, WEBSOCKET, "websocket")
        print("CCPC_STAGE3T_ISOLATED_WEBSOCKET_STARTED_PASS", flush=True)
        r.docker(*common, "--name", FRONTEND,
                 "--network-alias", "frontend",
                 "--env", "BACKEND=backend:8000",
                 "--env", "SOCKETIO=websocket:9000",
                 "--env", "FRAPPE_SITE_NAME_HEADER=ccpcerp.local",
                 r.APP_IMAGE, "nginx-entrypoint.sh", seconds=90)
        check_new(r, FRONTEND, "frontend")
        print("CCPC_STAGE3T_ISOLATED_FRONTEND_STARTED_PASS", flush=True)
        all_names = r.ORIGINALS | {
            r.DB, r.RC, r.RQ, r.FAILED, r.RECOVERED, WEBSOCKET, FRONTEND}
        need(r.names("ps", "-a", "--format", "{{.Names}}") == all_names
             and r.names("ps", "--format", "{{.Names}}") == all_names - {r.FAILED},
             "Protected Docker container inventory changed after startup")
        net = r.inspect("network", r.NETWORK)
        need(net.get("Internal") is True
             and set(net.get("Containers") or {}) == {
                 r.inspect("container", name)["Id"] for name in
                 (r.DB, r.RC, r.RQ, r.RECOVERED, WEBSOCKET, FRONTEND)},
             "Isolated test network membership changed after startup")
        r.check_originals()
        r.check_failed_backend()
        r.test_service(r.RECOVERED, r.APP_IMAGE)
        r.check_mount(r.SITES, owner=1000)
        r.check_mount(r.LOGS, owner=1000)
        print("CCPC_STAGE3T_PROTECTED_ORIGINALS_AND_NO_HOST_PORTS_PASS",
              flush=True)
        frontend_ready = False
        for attempt in range(12):
            p = r.docker("exec", FRONTEND, "python3", "-B", "-c",
                         FRONT_PROBE, seconds=12, allow_failure=True)
            if p.returncode == 0 and p.stdout.strip() == b"200":
                frontend_ready = True
                break
            if attempt < 11:
                time.sleep(2)
        need(frontend_ready, "Isolated frontend HTTP200 not established")
        print("CCPC_STAGE3T_ISOLATED_FRONTEND_LOGIN_HTTP200_PASS", flush=True)
        websocket_ready = False
        for attempt in range(12):
            p = r.docker("exec", FRONTEND, "python3", "-B", "-c",
                         WS_PROBE, seconds=12, allow_failure=True)
            if p.returncode == 0 and p.stdout.strip() == b"READY":
                websocket_ready = True
                break
            if attempt < 11:
                time.sleep(2)
        need(websocket_ready, "Isolated websocket TCP listener not established")
        print("CCPC_STAGE3T_ISOLATED_WEBSOCKET_TCP_PASS", flush=True)
        print("CCPC_NEW_A3_RESTORE_STAGE3T_FRONTEND_HTTP200_WEBSOCKET_TCP_PASS_AUTH_PENDING",
              flush=True)
    finally:
        os.umask(umask)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--execute", action="store_true")
    try:
        options = parser.parse_args()
        sys.dont_write_bytecode = True
        r = load_helper(R_SOURCE, R_SHA, "ccpc_stage3r_reviewed")
        s = load_helper(S_SOURCE, S_SHA, "ccpc_stage3s_reviewed")
        if options.preflight:
            preflight(r, s)
        else:
            once(r, s)
    except (Exception, KeyboardInterrupt):
        print("CCPC_NEW_A3_RESTORE_STAGE3T_STOP_PRESERVE_NO_RETRY",
              file=sys.stderr)
        sys.exit(1)
