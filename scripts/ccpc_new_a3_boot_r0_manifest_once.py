#!/usr/bin/env python3
"""Capture exactly one root-only NEW A3 R0 identity manifest, then stop.

This is NOT a boot script. Does not change Docker containers, systemd, ERPNext,
database contents, credentials, firewall, users, email or background jobs.
After obtaining an immutable point-in-time snapshot, call the *existing*
read-only R0 checker before any file is created. Never rerun after a partial run.
"""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import socket
import stat
import sys

import ccpc_new_a3_boot_r0_readonly as guard

ROOT = Path("/var/lib")
DESTINATION = ROOT / "ccpc-new-a3-r0-manifest-20261113"
FILE = DESTINATION / "manifest.json"
EXPECTED_APP_IMAGE = (
    "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
)
EXPECTED_FRONTEND_IP = "172.20.0.7"


def stop_unless(condition):
    guard.require(condition)


def make_manifest():
    """Inspect, never mutate, the exact currently running candidate + originals."""
    listing = guard.docker("ps", "-a", "--format", "{{.Names}}").decode("utf-8")
    stop_unless(set(listing.splitlines()) == guard.EXPECTED)

    data = guard.strict_json(guard.docker(
        "container", "inspect", *sorted(guard.EXPECTED)))
    stop_unless(isinstance(data, list) and len(data) == len(guard.EXPECTED))

    by_name = {obj["Name"].lstrip("/"): obj for obj in data}
    stop_unless(set(by_name) == guard.EXPECTED)
    ids = {name: obj["Id"] for name, obj in by_name.items()}
    stop_unless(len(set(ids.values())) == len(guard.EXPECTED))

    for name in guard.CANDIDATE + guard.ORIGINAL + guard.TEST_RUNNING:
        stop_unless(by_name[name]["State"]["Running"] is True)
    failed = by_name[guard.TEST_FAILED]["State"]
    stop_unless(failed["Running"] is False and failed["ExitCode"] == 1)

    stop_unless(by_name[guard.PREFIX + "-db-1"]["State"]
                .get("Health", {}).get("Status") == "healthy")
    app_roles = ("backend", "frontend", "websocket")
    for role in app_roles:
        obj = by_name[f"{guard.PREFIX}-{role}-1"]
        stop_unless(obj["Image"] == EXPECTED_APP_IMAGE)

    for name in guard.CANDIDATE:
        obj = by_name[name]
        stop_unless(obj["HostConfig"]["RestartPolicy"]["Name"] == "no")
        stop_unless(not obj["HostConfig"].get("PortBindings"))
        stop_unless(not any(bool(v) for v in
                        (obj["NetworkSettings"].get("Ports") or {}).values()))

    frontend = by_name[f"{guard.PREFIX}-frontend-1"]
    nets = frontend["NetworkSettings"]["Networks"]
    stop_unless(isinstance(nets, dict) and len(nets) == 1)
    network_name = next(iter(nets))
    stop_unless(all(set(by_name[k]["NetworkSettings"]["Networks"]) ==
                    {network_name} for k in guard.CANDIDATE))
    ipv4 = nets[network_name]["IPAddress"]
    stop_unless(ipv4 == EXPECTED_FRONTEND_IP)
    ip = ipaddress.ip_address(ipv4)
    stop_unless(isinstance(ip, ipaddress.IPv4Address) and ip.is_private
                and not ip.is_loopback and not ip.is_link_local)

    net_data = guard.strict_json(guard.docker("network", "inspect", network_name))
    stop_unless(isinstance(net_data, list) and len(net_data) == 1)
    network = net_data[0]
    stop_unless(network["Name"] == network_name
                and network["Internal"] is True
                and set((network.get("Containers") or {}).keys()) ==
                {ids[k] for k in guard.CANDIDATE})

    manifest = {
        "schema": 1,
        "container_ids": ids,
        "network_name": network_name,
        "network_id": network["Id"],
        "frontend_ipv4": ipv4,
        "app_image_id": EXPECTED_APP_IMAGE,
    }
    guard.validate_manifest(manifest)
    # Full independent read-only R0 check, including all protected services,
    # protected volumes, enabled/disabled systemd units and two safe site flags.
    snapshot = guard.snapshot_live(manifest)
    stop_unless(guard.evaluate(manifest, snapshot))
    return manifest


def write_once(manifest, *, parent=ROOT, destination=DESTINATION):
    """Fail closed if target exists. No replacement/deletion/permission rewrite."""
    base = parent.lstat()
    stop_unless(stat.S_ISDIR(base.st_mode) and base.st_uid == 0
                and (stat.S_IMODE(base.st_mode) & 0o022) == 0)
    stop_unless(destination.parent == parent)
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError:
        raise guard.Stop() from None
    info = destination.lstat()
    stop_unless(stat.S_ISDIR(info.st_mode) and info.st_uid == 0
                and stat.S_IMODE(info.st_mode) == 0o700)
    payload = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(destination / "manifest.json", flags, 0o600)
    with os.fdopen(fd, "wb") as f:
        os.fchmod(f.fileno(), 0o600)
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    record = (destination / "manifest.json").lstat()
    stop_unless(stat.S_ISREG(record.st_mode) and record.st_uid == 0
                and stat.S_IMODE(record.st_mode) == 0o600)
    dfd = os.open(destination, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-once", action="store_true", required=True)
    args = parser.parse_args()
    try:
        stop_unless(args.capture_once)
        stop_unless(os.geteuid() == 0
                    and os.environ.get("SUDO_USER") == "ccpcadmin"
                    and socket.gethostname().split(".")[0] == "ccpcerp-prod")
        stop_unless(not any(v in os.environ for v in
                        ("DOCKER_HOST", "DOCKER_CONTEXT")))
        stop_unless(not DESTINATION.exists() and not DESTINATION.is_symlink())
        manifest = make_manifest()
        write_once(manifest)
        print("CCPC_NEW_A3_R0_IDENTITY_CAPTURE_VERIFIED_PASS")
        print("CCPC_NEW_A3_R0_ROOT_ONLY_MANIFEST_CREATED_PASS")
        return 0
    except (guard.Stop, OSError, TypeError, KeyError, ValueError, IndexError,
            UnicodeError, AttributeError):
        # Even after an incomplete write, do NOT delete/retry; inspect first.
        print("CCPC_NEW_A3_R0_CAPTURE_STOP_REVIEW_REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
