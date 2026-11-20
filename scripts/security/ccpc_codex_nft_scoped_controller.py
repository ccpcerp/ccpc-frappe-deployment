#!/usr/bin/env python3
"""Review-only original-lab nftables table controller. NOT INSTALLED.

plan/verify are read-only. An eventual 'install' is a guarded root-only,
owner-marker-authorized, *single project table* transaction. It never
runs nftables.service, reads /etc/nftables.conf, flushes a ruleset,
restarts Docker/UFW, changes other tables, or starts Codex.

This is not a reboot persistence solution, UFW/Docker reload hook, packet-path
test, or proof of zero-gap containment under privileged host modification.
"""
import fcntl
import json
import os
import stat
import subprocess
import sys

import ccpc_codex_nft_guard_review as nft
import ccpc_codex_lab_firewall_guard as original

MARKER = "/etc/ccpc/codex-lab-nft-guard-authorized"
MARKER_BODY = b"CCPC_CODEX_NFT_GUARD_INSTALL_APPROVED\n"
LOCK = "/run/lock/ccpc-codex-nft-guard.lock"


class ControllerFailure(Exception):
    """Fail closed; do not expose raw Docker/firewall host data."""


def command(argv, source=None):
    try:
        p = subprocess.run(
            argv, input=source, text=True, capture_output=True, timeout=25
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ControllerFailure() from exc
    if p.returncode:
        raise ControllerFailure()
    return p.stdout


def authorization_required():
    if os.geteuid() != 0:
        raise ControllerFailure()
    try:
        fd = os.open(MARKER, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            s = os.fstat(fd)
            if (not stat.S_ISREG(s.st_mode) or s.st_uid != 0 or
                    (s.st_mode & 0o077) or s.st_size != len(MARKER_BODY) or
                    os.read(fd, len(MARKER_BODY) + 1) != MARKER_BODY):
                raise ControllerFailure()
        finally:
            os.close(fd)
    except OSError as exc:
        raise ControllerFailure() from exc


def lock_host():
    try:
        fd = os.open(
            LOCK, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
        )
        s = os.fstat(fd)
        if (not stat.S_ISREG(s.st_mode) or s.st_uid != 0 or
                (s.st_mode & 0o077)):
            os.close(fd)
            raise ControllerFailure()
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError as exc:
        raise ControllerFailure() from exc


def stock_service_disabled():
    """The host's stock nftables unit is unsafe: global flush on start/stop."""
    raw = command([
        "systemctl", "show", "--no-pager",
        "--property=ActiveState,UnitFileState", "nftables.service"
    ])
    props = {}
    for line in raw.splitlines():
        if "=" not in line:
            raise ControllerFailure()
        key, value = line.split("=", 1)
        if key in props:
            raise ControllerFailure()
        props[key] = value
    if props != {"ActiveState": "inactive", "UnitFileState": "disabled"}:
        raise ControllerFailure()
    return True


def ready_bridge():
    """Reuse existing hard-fail host/iptables stopped-agent checks."""
    bridge = nft.candidate_host()
    stock_service_disabled()
    return bridge


def table_state():
    """Detect collision in any nft family without reading other table rules."""
    data = json.loads(command(["nft", "-j", "list", "tables"]))
    if not isinstance(data, dict) or set(data) != {"nftables"}:
        raise ControllerFailure()
    objects = data["nftables"]
    if not isinstance(objects, list):
        raise ControllerFailure()
    found = []
    for item in objects:
        if not isinstance(item, dict) or len(item) != 1:
            raise ControllerFailure()
        kind, value = next(iter(item.items()))
        if kind == "metainfo":
            continue
        if kind != "table" or not isinstance(value, dict):
            raise ControllerFailure()
        if not isinstance(value.get("name"), str) or not isinstance(
            value.get("family"), str
        ):
            raise ControllerFailure()
        if value["name"] == nft.TABLE:
            found.append(value["family"])
    if not found:
        return "absent"
    if found != ["inet"]:
        raise ControllerFailure()
    return "present"


def verify_exact(bridge):
    content = command(["nft", "-j", "list", "table", "inet", nft.TABLE])
    try:
        nft.validate_json_snapshot(content, bridge)
    except nft.LayerFailure as exc:
        raise ControllerFailure() from exc
    return True


def plan():
    bridge = ready_bridge()
    state = table_state()
    if state == "present":
        verify_exact(bridge)
    return state


def install():
    authorization_required()  # Marker before lock or any host inspection.
    fd = lock_host()
    try:
        bridge = ready_bridge()
        state = table_state()
        if state == "present":
            verify_exact(bridge)  # Exact idempotence; never modify known table.
            return "already-exact"
        if state != "absent":
            raise ControllerFailure()

        proposal = nft.render_candidate(bridge)
        # Validate native nft parser without changing kernel state.
        command(["nft", "--check", "--file", "-"], proposal)

        # Re-verify stopped agent, unchanged bridge and stock service.
        if ready_bridge() != bridge or table_state() != "absent":
            raise ControllerFailure()

        # One atomic nft transaction for exactly ONE newly absent project table.
        # No global flush/delete; no cleanup on failed post-verify: preserve
        # restrictive rules and require a separate, scoped operator review.
        command(["nft", "--file", "-"], proposal)

        if ready_bridge() != bridge:
            raise ControllerFailure()
        verify_exact(bridge)
        return "installed"
    finally:
        os.close(fd)


def verify():
    bridge = ready_bridge()
    if table_state() != "present":
        raise ControllerFailure()
    return verify_exact(bridge)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["plan"], ["verify"], ["install"]):
        print("STOP: unapproved nft controller mode")
        return 2
    try:
        mode = argv[0] if argv else "plan"
        if mode == "install":
            outcome = install()
            print("PROJECT_NFT_TABLE_" + outcome.upper().replace("-", "_") + "=True")
        elif mode == "plan":
            state = plan()
            print("PROJECT_NFT_TABLE_STATE=" + state)
        else:
            verify()
            print("PROJECT_NFT_TABLE_EXACT=True")
    except (ControllerFailure, original.GuardFailure, nft.LayerFailure,
            ValueError, TypeError, KeyError, IndexError, AttributeError,
            OSError):
        print("STOP: scoped nft controller check failed")
        return 1
    print("agent_launch_authorized=False")
    print("reload_reboot_runtime_enforcement_verified=False")
    print("INSPECTION_COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
