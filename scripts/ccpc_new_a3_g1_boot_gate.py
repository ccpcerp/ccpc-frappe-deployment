#!/usr/bin/env python3
"""NEW A3 G1 guarded boot gate. NOT APPROVED FOR SERVER EXECUTION.

--offline-fixture and --live-readonly never start services. --gate-once is
explicitly mutating and requires separate owner authorization, installation
review, and post-change/reboot approval. Never alter containers or R0 manifest.
"""
import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import socket
import stat
import sys
import time

R0_SHA256 = "3f4e03d0e5f5d55bacfd16492fb021045eeb06b0199577a1612c9f18e0a3d72b"
MANIFEST_PATH = Path("/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json")
G1_DIR = Path("/root/ccpc-new-a3-g1-20261115")
R0_NAME = "ccpc_new_a3_boot_r0_readonly.py"
SAFETY_NAME = "ccpc_new_a3_g1_safety.py"
SAFETY_SHA256 = "3c50efcc1add9b1350da059fd4570e63c4bf5d491cb6d572ffb1c7883e92ba65"
UNIT_PATH = Path("/etc/systemd/system/ccpc-new-a3-g1-boot-gate.service")
# SHA256 of the draft unit file; this binds gate execution to the reviewed unit bytes.
UNIT_SHA256 = "be8af72e5e05abe1cabe28cdedb184597db9e1510f91b21e4f48af51e85cd274"
GATE_UNIT = "ccpc-new-a3-g1-boot-gate.service"
# Deliberate interlock: activation awaits verified NEW-host Caddy bind/config,
# systemd dependency graph, noncandidate policies, and explicit host consent.
G1_ACTIVATION_REVIEWED = False
PROBE_RESULT = b"CCPC_NEW_A3_G1_INTERNAL_PROBE_PASS\n"


class Stop(Exception):
    """Sanitized failure; never expose raw system details."""


def require(condition):
    if not condition:
        raise Stop()


def private_file(path, mode):
    try:
        s = path.lstat()
        require(stat.S_ISREG(s.st_mode) and s.st_uid == 0 and stat.S_IMODE(s.st_mode) == mode)
    except OSError:
        raise Stop() from None


def private_dir(path):
    try:
        s = path.lstat()
        require(stat.S_ISDIR(s.st_mode) and s.st_uid == 0 and stat.S_IMODE(s.st_mode) == 0o700)
    except OSError:
        raise Stop() from None


def sha256_file(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        raise Stop() from None


def get_r0(*, offline):
    path = Path(__file__).with_name(R0_NAME)
    if not offline:
        private_dir(G1_DIR)
        require(Path(__file__).parent == G1_DIR)
        private_file(Path(__file__), 0o600)
        private_file(path, 0o600)
        require(sha256_file(path) == R0_SHA256)
        private_dir(MANIFEST_PATH.parent)
        private_file(MANIFEST_PATH, 0o600)
    spec = importlib.util.spec_from_file_location("ccpc_new_a3_g1_pinned_r0", path)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_safety(*, offline):
    path = Path(__file__).with_name(SAFETY_NAME)
    if not offline:
        private_file(path, 0o600)
        require(sha256_file(path) == SAFETY_SHA256)
    spec = importlib.util.spec_from_file_location("ccpc_new_a3_g1_pinned_safety", path)
    require(spec is not None and spec.loader is not None)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_host(*, gate_once=False):
    require(os.geteuid() == 0 and socket.gethostname().split(".")[0] == "ccpcerp-prod")
    require(not any(k in os.environ for k in ("DOCKER_HOST", "DOCKER_CONTEXT")))
    # Under systemd there is no SUDO_USER; read-only checks also permit the
    # named operator via sudo. Never spoof R0's separate sudo-only context.
    require(os.environ.get("SUDO_USER") in (None, "ccpcadmin"))
    if gate_once:
        require("SUDO_USER" not in os.environ)
    private_file(UNIT_PATH, 0o644)
    require(sha256_file(UNIT_PATH) == UNIT_SHA256)


def collect(r0, manifest):
    # Reuse R0's safe parsing and Docker/systemd probes, but not its R0-only
    # snapshot_live: it rejects systemd roots and the approved G1 policy state.
    actual = set(r0.docker("ps", "-a", "--format", "{{.Names}}").decode().splitlines())
    require(actual == r0.EXPECTED)
    raw = r0.strict_json(r0.docker("container", "inspect", *sorted(r0.EXPECTED)))
    require(isinstance(raw, list) and len(raw) == len(r0.EXPECTED))
    rows = {}
    for obj in raw:
        name = obj["Name"].lstrip("/")
        nets, mounts = obj["NetworkSettings"]["Networks"], obj["Mounts"]
        rows[name] = {
            "id": obj["Id"], "running": obj["State"]["Running"],
            "health": (obj["State"].get("Health") or {}).get("Status"),
            "exit": obj["State"].get("ExitCode"),
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
    require(set(rows) == r0.EXPECTED)
    # Pin IDs before any command is run inside candidate containers.
    require(all(rows[k]["id"] == manifest["container_ids"][k] for k in r0.EXPECTED))
    require(all(rows[k]["running"] is True for k in r0.CANDIDATE))
    backend = rows[f"{r0.PREFIX}-backend-1"]
    require(backend["image"] == manifest["app_image_id"])
    require(backend["networks"] == [manifest["network_name"]])
    require(backend["dest_volumes"].get(r0.BENCH_SITES) == f"{r0.PREFIX}_sites")
    nets = r0.strict_json(r0.docker("network", "inspect", manifest["network_name"]))
    require(isinstance(nets, list) and len(nets) == 1)
    net = nets[0]
    require(net["Name"] == manifest["network_name"] and net["Id"] == manifest["network_id"])
    require(net["Internal"] is True)
    require(set((net.get("Containers") or {}).keys()) ==
            {manifest["container_ids"][k] for k in r0.CANDIDATE})
    units = {}
    for k, u in {**r0.UNITS, "GATE": GATE_UNIT, "CADDY_API": "caddy-api.service"}.items():
        result = r0.invoke(("systemctl", "show", u,
                            "--property=LoadState,ActiveState,UnitFileState", "--no-pager"))
        props = dict(line.split("=", 1) for line in result.decode().splitlines() if "=" in line)
        require(props.get("LoadState") in ("loaded", "masked") if k == "CADDY_API"
                else props.get("LoadState") == "loaded")
        units[k] = [props.get("ActiveState"), props.get("UnitFileState")]
    return {
        "containers": rows,
        "network": {"name": net["Name"], "id": net["Id"], "internal": net["Internal"],
                    "members": list((net.get("Containers") or {}).keys())},
        "units": units,
        "socket_bind": r0.fixed_file_value(r0.SOCKET_FILE, "ListenStream"),
        "relay_exec": r0.fixed_file_value(r0.SERVICE_FILE, "ExecStart"),
        "flags": r0.read_flags(f"{r0.PREFIX}-backend-1"),
    }


def evaluate(r0, m, s, *, profile, gateway_state="cold"):
    r0.validate_manifest(m)
    require(profile in ("prechange", "postchange"))
    require(gateway_state in ("pilot", "cold"))
    require(profile != "prechange" or gateway_state == "pilot")
    rows = s["containers"]
    require(isinstance(rows, dict) and set(rows) == r0.EXPECTED)
    require(all(rows[k]["id"] == m["container_ids"][k] for k in r0.EXPECTED))
    require(all(rows[k]["running"] is True for k in r0.CANDIDATE))
    require(rows[r0.TEST_FAILED]["running"] is False and rows[r0.TEST_FAILED]["exit"] == 1)
    require(rows[f"{r0.PREFIX}-db-1"]["health"] == "healthy")
    # 13 protected noncandidate containers must never auto-resume unexpectedly.
    other = r0.EXPECTED - set(r0.CANDIDATE)
    require(all(rows[k]["restart"] == "no" for k in other))
    restart = "no" if profile == "prechange" else "unless-stopped"
    require(all(rows[k]["restart"] == restart for k in r0.CANDIDATE))
    require(all(not rows[k]["published"] for k in r0.CANDIDATE))
    require(all(rows[k]["networks"] == [m["network_name"]] for k in r0.CANDIDATE))
    require(all(rows[f"{r0.PREFIX}-{name}-1"]["image"] == m["app_image_id"]
                for name in ("backend", "websocket", "frontend")))
    for role in ("backend", "websocket", "frontend"):
        vols = rows[f"{r0.PREFIX}-{role}-1"]["dest_volumes"]
        require(vols[r0.BENCH_SITES] == f"{r0.PREFIX}_sites" and
                vols[r0.BENCH_LOGS] == f"{r0.PREFIX}_logs")
    require(f"{r0.PREFIX}_db-data" in rows[f"{r0.PREFIX}-db-1"]["volumes"])
    require(f"{r0.PREFIX}_redis-queue-data" in rows[f"{r0.PREFIX}-redis-queue-1"]["volumes"])
    net = s["network"]
    require(net["name"] == m["network_name"] and net["id"] == m["network_id"]
            and net["internal"] is True and len(net["members"]) == len(r0.CANDIDATE)
            and set(net["members"]) == {m["container_ids"][k] for k in r0.CANDIDATE})
    require(rows[f"{r0.PREFIX}-frontend-1"]["ipv4"] == m["frontend_ipv4"])
    require(s["socket_bind"] == "127.0.0.1:8080")
    require(s["relay_exec"] ==
            "/usr/lib/systemd/systemd-socket-proxyd " + m["frontend_ipv4"] + ":8080")
    require(s["flags"] == {"pause_scheduler": True, "mute_emails": True})
    units = s["units"]
    require(units["DOCKER"] == ["active", "enabled"])
    require(units["CONTAINERD"] == ["active", "enabled"])
    require(units["CADDY_API"] == ["inactive", "masked"])
    if gateway_state == "pilot":
        require(units["CADDY"] == ["active", "disabled"])
        require(units["SOCKET"] == ["active", "disabled"])
        require(units["RELAY"] == ["active", "static"])
    else:
        require(units["CADDY"] == ["inactive", "disabled"])
        require(units["SOCKET"] == ["inactive", "disabled"])
        require(units["RELAY"] == ["inactive", "static"])
    if profile == "prechange":
        require(units["GATE"] == ["inactive", "disabled"])
    else:
        require(units["GATE"] in (["activating", "enabled"], ["inactive", "enabled"]))
    return True


# Runs inside the *pinned* candidate backend, connecting only across the private
# Docker network. No raw HTTP bodies or site config are sent back to the host.
PROBE = r'''
import socket
import urllib.request

def http(url):
    request = urllib.request.Request(url, headers={'Host': 'ccpcerp.local'})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=5) as reply:
        assert reply.status == 200

def redis_ping(host):
    with socket.create_connection((host, 6379), timeout=5) as conn:
        conn.settimeout(5)
        conn.sendall(b'*1\r\n$4\r\nPING\r\n')
        assert conn.makefile('rb').readline() == b'+PONG\r\n'

redis_ping('redis-cache')
redis_ping('redis-queue')
http('http://127.0.0.1:8000/login')
http('http://frontend:8080/login')
with socket.create_connection(('websocket', 9000), timeout=5):
    pass
print('CCPC_NEW_A3_G1_INTERNAL_PROBE_PASS')
'''


def probe(r0):
    reply = r0.docker("exec", "-i", "--user", "1000:1000",
                      f"{r0.PREFIX}-backend-1", "python3", "-B", "-",
                      data=PROBE.encode())
    require(reply == PROBE_RESULT)


def start_gateway(r0):
    # Only the preexisting loopback socket and preexisting LAN-scoped Caddy.
    # If either start fails, no automatic stop or restart of healthy services.
    r0.invoke(("systemctl", "start", "ccpc-erpnext-upstream.socket"))
    r0.invoke(("systemctl", "start", "caddy.service"))
    for unit in ("ccpc-erpnext-upstream.socket", "caddy.service"):
        value = r0.invoke(("systemctl", "show", unit,
                           "--property=ActiveState,UnitFileState", "--no-pager"))
        require(b"ActiveState=active" in value.splitlines() and
                b"UnitFileState=disabled" in value.splitlines())


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--offline-fixture", type=Path)
    modes.add_argument("--live-readonly", action="store_true")
    modes.add_argument("--gate-once", action="store_true")
    p.add_argument("--profile", choices=("prechange", "postchange"), default="postchange")
    p.add_argument("--gateway-state", choices=("pilot", "cold"), default="cold")
    args = p.parse_args(argv)
    try:
        require(not args.gate_once or
                (G1_ACTIVATION_REVIEWED and args.profile == "postchange"
                 and args.gateway_state == "cold"))
        offline = args.offline_fixture is not None
        r0 = get_r0(offline=offline)
        safety = get_safety(offline=offline)
        if offline:
            manifest = r0.validate_manifest(r0.load_json_file(args.manifest))
            snapshot = r0.load_json_file(args.offline_fixture)
            evaluate(r0, manifest, snapshot, profile=args.profile,
                     gateway_state=args.gateway_state)
            print("CCPC_NEW_A3_G1_READONLY_PREFLIGHT_PASS")
            return 0

        check_host(gate_once=args.gate_once)
        require(args.manifest == MANIFEST_PATH)
        manifest = r0.validate_manifest(r0.load_json_file(MANIFEST_PATH, root_only=True))
        deadline = time.monotonic() + 180
        # The context bounds EVERY R0 subprocess, including docker exec probes
        # and systemd operations, without modifying the SHA-pinned R0 on disk.
        with safety.deadline_guard(r0, deadline):
            while True:
                try:
                    snapshot = collect(r0, manifest)
                    evaluate(r0, manifest, snapshot, profile=args.profile,
                             gateway_state=args.gateway_state)
                    probe(r0)
                    break
                except (Stop, r0.Stop, safety.SafetyStop, KeyError,
                        ValueError, TypeError, IndexError):
                    if time.monotonic() >= deadline:
                        raise Stop() from None
                    time.sleep(min(5, max(0, deadline - time.monotonic())))
            # Security gate is never retried: unexpected Caddy files, systemd
            # activation edges, TLS/drop-in metadata or bound ports STOP.
            safety.validate_gateway_config(r0)
            safety.validate_tcp_bindings(r0, gateway_state=args.gateway_state)
            evaluate(r0, manifest, snapshot, profile=args.profile,
                     gateway_state=args.gateway_state)
            if args.gate_once:
                # Reserve enough budget for both sequential systemctl starts.
                require(deadline - time.monotonic() >= 70)
                snapshot = collect(r0, manifest)
                evaluate(r0, manifest, snapshot,
                         profile="postchange", gateway_state="cold")
                probe(r0)
                safety.validate_gateway_config(r0)
                safety.validate_tcp_bindings(r0, gateway_state="cold")
                require(deadline - time.monotonic() >= 70)
                start_gateway(r0)
                safety.validate_tcp_bindings(r0, gateway_state="pilot")
                print("CCPC_NEW_A3_G1_GATEWAY_STARTED_PASS")
            else:
                print("CCPC_NEW_A3_G1_READONLY_PREFLIGHT_PASS")
        return 0
    except Exception:  # includes the independently imported R0 Stop; no raw error output
        print("CCPC_NEW_A3_G1_STOP_REVIEW_REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
