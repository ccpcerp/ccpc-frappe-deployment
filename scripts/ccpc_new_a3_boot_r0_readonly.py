#!/usr/bin/env python3
"""NEW A3 R0 identity/boot-safety audit. READ-ONLY; no startup or write mode.

Live collection requires a separate, owner-approved, root-only pinned manifest.
Fixture mode is for synthetic offline testing. Never print raw Docker/systemd data.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys

PREFIX = "ccpc_prod_erpnext"
ROLES = ("db", "redis-cache", "redis-queue", "backend", "websocket", "frontend")
CANDIDATE = tuple(f"{PREFIX}-{role}-1" for role in ROLES)
ORIGINAL = tuple(f"{p}-{role}-1" for p in (
    "ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
    for role in ("redis-queue", "redis-cache", "db"))
TEST_PREFIX = "ccpc_a3_restore_drill_20261112"
TEST_RUNNING = tuple(f"{TEST_PREFIX}-{role}-1" for role in (
    "frontend-completion1", "websocket-completion1", "backend-recovery1",
    "redis-queue", "redis-cache", "db"))
TEST_FAILED = f"{TEST_PREFIX}-backend-1"
EXPECTED = set(CANDIDATE + ORIGINAL + TEST_RUNNING + (TEST_FAILED,))
UNITS = {"DOCKER": "docker.service", "CONTAINERD": "containerd.service",
         "CADDY": "caddy.service", "SOCKET": "ccpc-erpnext-upstream.socket",
         "RELAY": "ccpc-erpnext-upstream.service"}
BENCH_SITES = "/home/frappe/frappe-bench/sites"
BENCH_LOGS = "/home/frappe/frappe-bench/logs"
SOCKET_FILE = Path("/etc/systemd/system/ccpc-erpnext-upstream.socket")
SERVICE_FILE = Path("/etc/systemd/system/ccpc-erpnext-upstream.service")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class Stop(Exception):
    pass


def require(condition):
    if not condition:
        raise Stop()


def invoke(command, *, data=None):
    try:
        p = subprocess.run(command, input=data, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=35, check=True)
        return p.stdout
    except (OSError, subprocess.SubprocessError):
        raise Stop() from None


def docker(*args, data=None):
    return invoke(("docker", "--host", "unix:///var/run/docker.sock", *args), data=data)


def strict_json(data):
    try:
        return json.loads(data)
    except (TypeError, ValueError, UnicodeError):
        raise Stop() from None


def fixed_file_value(path, key):
    try:
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 0)
        values = [line.partition("=")[2].strip()
                  for line in path.read_text(encoding="utf-8").splitlines()
                  if line.strip().startswith(key + "=")]
        require(len(values) == 1)
        return values[0]
    except (OSError, UnicodeError):
        raise Stop() from None


def read_flags(backend):
    probe = r'''
import json
import stat
from pathlib import Path
base = Path('/home/frappe/frappe-bench/sites')
def load(name):
    p = base / name
    assert stat.S_ISREG(p.lstat().st_mode)
    d = json.loads(p.read_text(encoding='utf-8'))
    assert isinstance(d, dict)
    return d
common = load('common_site_config.json')
site = load('ccpcerp.local/site_config.json')
result = {}
for key in ('pause_scheduler', 'mute_emails'):
    v = site[key] if key in site else common.get(key)
    result[key] = v is True or (type(v) is int and v == 1) or (isinstance(v, str) and v.strip().lower() in ('true', '1', 'yes', 'on'))
print(json.dumps(result, separators=(',', ':')))
'''
    return strict_json(docker("exec", "-i", "--user", "1000:1000", backend,
                              "python3", "-B", "-", data=probe.encode("utf-8")))


def snapshot_live(manifest):
    require(os.geteuid() == 0 and os.environ.get("SUDO_USER") == "ccpcadmin"
            and socket.gethostname().split(".")[0] == "ccpcerp-prod")
    require(not any(k in os.environ for k in ("DOCKER_HOST", "DOCKER_CONTEXT")))
    actual = set(docker("ps", "-a", "--format", "{{.Names}}").decode("utf-8").splitlines())
    require(actual == EXPECTED)
    raw = strict_json(docker("container", "inspect", *sorted(EXPECTED)))
    require(isinstance(raw, list) and len(raw) == len(EXPECTED))
    rows = {}
    for obj in raw:
        name = obj["Name"].lstrip("/")
        nets = obj["NetworkSettings"]["Networks"]
        mounts = obj["Mounts"]
        rows[name] = {
            "id": obj["Id"], "running": obj["State"]["Running"],
            "exit": obj["State"].get("ExitCode"),
            "health": (obj["State"].get("Health") or {}).get("Status"),
            "restart": obj["HostConfig"]["RestartPolicy"]["Name"],
            "networks": list(nets),
            "ipv4": (nets.get(manifest["network_name"]) or {}).get("IPAddress", ""),
            "image": obj["Image"],
            "volumes": [m.get("Name") for m in mounts if m.get("Type") == "volume"],
            "dest_volumes": {m.get("Destination"): m.get("Name") for m in mounts
                             if m.get("Type") == "volume"},
            "published": bool(obj["HostConfig"].get("PortBindings")) or any(
                bool(v) for v in (obj["NetworkSettings"].get("Ports") or {}).values()),
        }
    require(set(rows) == EXPECTED)
    # Check pinned identity *before* running even a read-only command in a container.
    require(all(rows[k]["id"] == manifest["container_ids"][k] for k in EXPECTED))
    require(all(rows[k]["running"] is True for k in CANDIDATE))
    backend_row = rows[f"{PREFIX}-backend-1"]
    require(backend_row["image"] == manifest["app_image_id"])
    require(backend_row["networks"] == [manifest["network_name"]])
    require(backend_row["dest_volumes"].get(BENCH_SITES) == f"{PREFIX}_sites")
    net = strict_json(docker("network", "inspect", manifest["network_name"]))
    require(isinstance(net, list) and len(net) == 1)
    n = net[0]
    require(n["Name"] == manifest["network_name"] and n["Id"] == manifest["network_id"])
    require(n["Internal"] is True and set((n.get("Containers") or {}).keys()) ==
            {manifest["container_ids"][k] for k in CANDIDATE})
    units = {}
    for label, unit in UNITS.items():
        result = invoke(("systemctl", "show", unit,
                         "--property=LoadState,ActiveState,UnitFileState", "--no-pager"))
        props = dict(line.split("=", 1) for line in result.decode("utf-8").splitlines()
                     if "=" in line)
        require(props.get("LoadState") == "loaded")
        units[label] = [props.get("ActiveState"), props.get("UnitFileState")]
    return {"containers": rows,
            "network": {"name": n["Name"], "id": n["Id"],
                        "internal": n["Internal"],
                        "members": list((n.get("Containers") or {}).keys())},
            "units": units,
            "socket_bind": fixed_file_value(SOCKET_FILE, "ListenStream"),
            "relay_exec": fixed_file_value(SERVICE_FILE, "ExecStart"),
            "flags": read_flags(f"{PREFIX}-backend-1")}


def validate_manifest(m):
    require(isinstance(m, dict) and m.get("schema") == 1)
    require(isinstance(m.get("container_ids"), dict))
    require(set(m["container_ids"]) == EXPECTED)
    require(all(isinstance(v, str) and HEX64.fullmatch(v)
                for v in m["container_ids"].values()))
    require(len(set(m["container_ids"].values())) == len(EXPECTED))
    require(isinstance(m.get("network_name"), str)
            and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{1,100}", m["network_name"]))
    require(isinstance(m.get("network_id"), str) and HEX64.fullmatch(m["network_id"]))
    require(isinstance(m.get("app_image_id"), str)
            and m["app_image_id"].startswith("sha256:")
            and HEX64.fullmatch(m["app_image_id"][7:]))
    try:
        ip = ipaddress.ip_address(m["frontend_ipv4"])
        require(isinstance(ip, ipaddress.IPv4Address) and ip.is_private
                and not ip.is_loopback and not ip.is_link_local)
    except (KeyError, ValueError):
        raise Stop() from None
    return m


def evaluate(m, snap):
    validate_manifest(m)
    require(isinstance(snap, dict))
    rows = snap["containers"]
    require(isinstance(rows, dict) and set(rows) == EXPECTED)
    require(all(rows[k]["id"] == v for k, v in m["container_ids"].items()))
    require(all(rows[k]["running"] is True for k in CANDIDATE + ORIGINAL + TEST_RUNNING))
    require(rows[TEST_FAILED]["running"] is False and rows[TEST_FAILED]["exit"] == 1)
    require(rows[f"{PREFIX}-db-1"]["health"] == "healthy")
    require(all(rows[k]["restart"] == "no" and not rows[k]["published"]
                for k in CANDIDATE))
    require(all(rows[k]["networks"] == [m["network_name"]] for k in CANDIDATE))
    require(all(rows[k]["image"] == m["app_image_id"]
                for k in (f"{PREFIX}-{r}-1" for r in ("backend", "websocket", "frontend"))))
    for r in ("backend", "websocket", "frontend"):
        dest = rows[f"{PREFIX}-{r}-1"]["dest_volumes"]
        require(dest[BENCH_SITES] == f"{PREFIX}_sites"
                and dest[BENCH_LOGS] == f"{PREFIX}_logs")
    require(f"{PREFIX}_db-data" in rows[f"{PREFIX}-db-1"]["volumes"])
    require(f"{PREFIX}_redis-queue-data" in rows[f"{PREFIX}-redis-queue-1"]["volumes"])
    net = snap["network"]
    require(net["name"] == m["network_name"] and net["id"] == m["network_id"]
            and net["internal"] is True
            and len(net["members"]) == len(CANDIDATE)
            and set(net["members"]) == {m["container_ids"][k] for k in CANDIDATE})
    require(rows[f"{PREFIX}-frontend-1"]["ipv4"] == m["frontend_ipv4"])
    units = snap["units"]
    require(units["DOCKER"] == ["active", "enabled"])
    require(units["CONTAINERD"] == ["active", "enabled"])
    require(units["CADDY"] == ["active", "disabled"])
    require(units["SOCKET"] == ["active", "disabled"])
    require(units["RELAY"] == ["active", "static"])
    require(snap["socket_bind"] == "127.0.0.1:8080")
    require(snap["relay_exec"] ==
            "/usr/lib/systemd/systemd-socket-proxyd " + m["frontend_ipv4"] + ":8080")
    require(snap["flags"] == {"pause_scheduler": True, "mute_emails": True})
    return True


def load_json_file(path, root_only=False):
    try:
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode))
        if root_only:
            require(path.is_absolute() and info.st_uid == 0
                    and (stat.S_IMODE(info.st_mode) & 0o077) == 0)
        return strict_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        raise Stop() from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline-fixture", type=Path)
    mode.add_argument("--live-readonly", action="store_true")
    args = parser.parse_args()
    try:
        manifest = validate_manifest(load_json_file(args.manifest, root_only=args.live_readonly))
        if args.live_readonly:
            snap = snapshot_live(manifest)
        else:
            snap = load_json_file(args.offline_fixture)
        require(evaluate(manifest, snap))
        print("CCPC_NEW_A3_R0_IDENTITY_STORAGE_NETWORK_PASS")
        print("CCPC_NEW_A3_R0_GATEWAY_AND_PRECUTOVER_FLAGS_PASS")
        print("CCPC_NEW_A3_R0_READONLY_PREFLIGHT_PASS")
        return 0
    except (Stop, KeyError, TypeError, IndexError, ValueError, UnicodeError):
        print("CCPC_NEW_A3_R0_STOP_REVIEW_REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
