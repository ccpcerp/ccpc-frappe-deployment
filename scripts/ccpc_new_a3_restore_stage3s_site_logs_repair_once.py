#!/usr/bin/env python3
"""Stage3S: ONE-USE forward-only, test-only site-local logs directory repair.

Read-only --preflight verifies the precise consumed Stage3R recovery state
using the SHA256-pinned Stage3R inspection functions already staged at /root.
--execute checks again, creates a separate no-retry marker, then creates ONLY
ccpcerp.local/logs (1000:1000, 0755) in the independent restored test sites
volume. Does not start/restart/remove any container, migrate, publish ports,
touch OLD PROD/DEV/NEW A3 or change any existing directory's owner/mode.
A STOP after starting --execute is NONRETRYABLE; preserve partial state.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import stat
import sys
import types

HOST = "ccpcerp-prod"
OPERATOR = "ccpcadmin"
PREFIX = "ccpc_a3_restore_drill_20261112"
SITE = "ccpcerp.local"
PRIOR = Path("/var/lib/ccpc-a3-stage3r-repair1-20261113")
MARKER = Path("/var/lib/ccpc-a3-stage3s-site-logs-repair1-20261113")
SOURCE = Path("/root/ccpc_new_a3_restore_stage3r_sites_owner_and_backend_recovery.py")
SHA256 = "a05e3f53d49766f42bd97f7bb508f59e7c282399ce3766cf46082138e626bdbe"

class Stop(Exception):
    pass

def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Stop(reason)

def root_dir(path: Path, uid: int, mode: int) -> None:
    s = path.lstat()
    need(stat.S_ISDIR(s.st_mode) and s.st_uid == uid and
         s.st_gid == uid and stat.S_IMODE(s.st_mode) == mode,
         "Protected directory identity mismatch")

def root_file(path: Path, uid: int, mode: int) -> None:
    s = path.lstat()
    need(stat.S_ISREG(s.st_mode) and s.st_uid == uid and
         s.st_gid == uid and stat.S_IMODE(s.st_mode) == mode,
         "Protected file identity mismatch")

def reviewed_runner():
    # Execute only Python function definitions from the exact reviewed Stage3R
    # source; __main__ code does not run. No bytecode/cache files are written.
    root_file(SOURCE, 0, 0o600)
    data = SOURCE.read_bytes()
    need(hashlib.sha256(data).hexdigest() == SHA256,
         "Stage3R source checksum mismatch")
    module = types.ModuleType("ccpc_reviewed_stage3r_readonly_helpers")
    module.__file__ = str(SOURCE)
    exec(compile(data, str(SOURCE), "exec"), module.__dict__)
    return module

def preflight(r):
    need(os.geteuid() == 0 and os.environ.get("SUDO_USER") == OPERATOR
         and socket.gethostname().split(".")[0] == HOST,
         "Wrong NEW server/operator")
    need(not any(k in os.environ for k in (
         "DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE",
         "COMPOSE_PROJECT_NAME", "DB_PASSWORD")), "Ambient target override")
    need(not any(os.path.islink(x) for x in
         ("/var/lib/docker", "/var/lib/docker/volumes")),
         "Docker path symlink")
    root_dir(PRIOR, 0, 0o700)
    need({p.name for p in PRIOR.iterdir()} == {"DO_NOT_RETRY"},
         "Prior repair marker unexpected")
    root_file(PRIOR / "DO_NOT_RETRY", 0, 0o600)
    need((PRIOR / "DO_NOT_RETRY").read_bytes() ==
         b"STAGE3R_ONE_USE_20261113\n", "Prior repair marker altered")
    need(not MARKER.exists() and not MARKER.is_symlink(),
         "Stage3S already attempted; do not retry")
    expected = r.ORIGINALS | {r.DB, r.RC, r.RQ, r.FAILED, r.RECOVERED}
    need(r.names("ps", "-a", "--format", "{{.Names}}") == expected
         and r.names("ps", "--format", "{{.Names}}") ==
             r.ORIGINALS | {r.DB, r.RC, r.RQ, r.RECOVERED},
         "Unexpected container inventory/states")
    need({n for n in r.names("volume", "ls", "--format", "{{.Name}}")
          if n.startswith(PREFIX)} == {r.DB_VOLUME, r.SITES, r.LOGS}
         and {n for n in r.names("network", "ls", "--format", "{{.Name}}")
              if n.startswith(PREFIX)} == {r.NETWORK},
         "Unexpected test Docker resources")
    r.check_originals()
    r.check_failed_backend()
    db = r.test_service(r.DB, r.MYSQL_IMAGE, require_label=False)
    need((db.get("State", {}).get("Health") or {}).get("Status") == "healthy",
         "Test DB health changed")
    need(r.docker("exec", r.DB, "mariadb",
         "--defaults-extra-file=/run/secrets/db-client.cnf",
         "--batch", "--skip-column-names",
         "--execute=SELECT COUNT(*) FROM `" + r.SCHEMA +
         "`.`tabCompany`;").stdout.decode("ascii", "strict").strip() == "4",
         "Restored Company count changed")
    r.test_service(r.RC, r.REDIS_IMAGE)
    r.test_service(r.RQ, r.REDIS_IMAGE)
    replacement = r.test_service(r.RECOVERED, r.APP_IMAGE)
    need(replacement.get("Config", {}).get("User") == "1000:1000"
         and (replacement.get("Config", {}).get("Labels") or {})
             .get("com.ccpc.stage") == "restore-stage3r-repair1"
         and {(m.get("Type"), m.get("Name"), m.get("Destination"))
              for m in replacement.get("Mounts") or []} ==
             {("volume", r.SITES, "/home/frappe/frappe-bench/sites"),
              ("volume", r.LOGS, "/home/frappe/frappe-bench/logs")},
         "Recovery backend container identity/volume mounts changed")
    network = r.inspect("network", r.NETWORK)
    need(network.get("Internal") is True
         and network.get("Attachable") is False
         and network.get("Driver") == "bridge"
         and (network.get("Labels") or {}).get("com.ccpc.test") == r.TAG
         and set((network.get("Containers") or {})) ==
             {r.inspect("container", n)["Id"]
              for n in (r.DB, r.RC, r.RQ, r.RECOVERED)},
         "Internal network isolation/membership changed")
    ipam = network.get("IPAM", {}).get("Config") or []
    need(len(ipam) == 1 and isinstance(
         ipaddress.ip_network(ipam[0]["Subnet"], strict=True),
         ipaddress.IPv4Network), "Isolated network IPAM invalid")
    r.check_mount(r.DB_VOLUME, owner=None)
    root = r.check_mount(r.SITES, owner=1000)
    r.check_mount(r.LOGS, owner=1000)
    # Stage3R helper confirms exact config, flags, DB target, 16,501-byte
    # private attachment, apps list and original 3-entry site layout.
    r.check_site_and_config(root)
    site = root / SITE
    root_dir(site, 1000, 0o755)
    target = site / "logs"
    need(not target.exists() and not target.is_symlink(),
         "Site-local logs already exists; STOP")
    print("CCPC_STAGE3S_MISSING_TEST_SITE_LOGS_AND_PROTECTED_RESOURCES_PASS",
          flush=True)
    print("CCPC_NEW_A3_RESTORE_STAGE3S_READONLY_PREFLIGHT_PASS", flush=True)
    return site

def once(r):
    site = preflight(r)
    # First mutation consumes this attempt, even if later mkdir fails.
    old_umask = os.umask(0o077)
    try:
        MARKER.mkdir(mode=0o700)
        root_dir(MARKER, 0, 0o700)
        fd = os.open(MARKER / "DO_NOT_RETRY",
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(b"STAGE3S_ONE_USE_20261113\n")
            stream.flush()
            os.fsync(stream.fileno())
        root_file(MARKER / "DO_NOT_RETRY", 0, 0o600)
        print("CCPC_STAGE3S_NEW_ONE_USE_MARKER_PASS", flush=True)

        root_dir(site, 1000, 0o755)
        parent_fd = os.open(site, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            s = os.fstat(parent_fd)
            need(stat.S_ISDIR(s.st_mode) and s.st_uid == 1000
                 and s.st_gid == 1000 and stat.S_IMODE(s.st_mode) == 0o755,
                 "Site changed before isolated mkdir")
            os.mkdir("logs", mode=0o700, dir_fd=parent_fd)
            child_fd = os.open("logs",
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            try:
                os.fchown(child_fd, 1000, 1000)
                os.fchmod(child_fd, 0o755)
                os.fsync(child_fd)
            finally:
                os.close(child_fd)
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)

        root_dir(site / "logs", 1000, 0o755)
        need({p.name for p in site.iterdir()} ==
             {"site_config.json", "public", "private", "logs"},
             "Post-create site layout unexpected")
        r.check_mount(r.SITES, owner=1000)
        r.check_originals()
        print("CCPC_STAGE3S_ONLY_ISOLATED_SITE_LOGS_DIRECTORY_CREATED_PASS",
              flush=True)
        print("CCPC_NEW_A3_RESTORE_STAGE3S_SITE_LOGS_REPAIR_PASS_BACKEND_HTTP_PENDING",
              flush=True)
    finally:
        os.umask(old_umask)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--execute", action="store_true")
    try:
        args = parser.parse_args()
        # Force no Python bytecode/cache writes even in read-only mode.
        sys.dont_write_bytecode = True
        runner = reviewed_runner()
        if args.preflight:
            preflight(runner)
        else:
            once(runner)
    except (Exception, KeyboardInterrupt):
        print("CCPC_NEW_A3_RESTORE_STAGE3S_STOP_PRESERVE_NO_RETRY",
              file=sys.stderr)
        sys.exit(1)
