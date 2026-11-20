#!/usr/bin/env python3
"""Review-only, read-only OFFLINE Codex prelaunch interlock.

Never starts Codex, a container, a proxy or a Docker network. Returns success
only for a stopped synthetic agent with verified original-bridge firewall,
pinned image provenance identifier, bounded effective resources and a separate
root-owned explicit authorization marker. This is a prerequisite, NOT an
unbypassable Docker-launch control or a runtime firewall-loss watchdog.
"""
import json
import os
import re
import stat
import sys

import ccpc_codex_lab_firewall_guard as guard

AGENT = "ccpc_codex_dev_agent-agent-1"
LAB = "ccpc_codex_dev_agent_lab"
MARKER = "/etc/ccpc/codex-lab-offline-launch-authorized"
MARKER_BODY = b"CCPC_CODEX_SYNTHETIC_OFFLINE_LAUNCH_APPROVED\n"
MEMORY = 8 * 1024**3
PIDS = 512


class GateFailure(Exception):
    pass


def authorization_required():
    if os.geteuid() != 0:
        raise GateFailure()
    try:
        fd = os.open(MARKER, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            st = os.fstat(fd)
            if (not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or
                    st.st_mode & 0o077 or st.st_size != len(MARKER_BODY) or
                    os.read(fd, len(MARKER_BODY) + 1) != MARKER_BODY):
                raise GateFailure()
        finally:
            os.close(fd)
    except OSError as exc:
        raise GateFailure() from exc


def validate_agent_runtime(agent, lab):
    """Exact restricted offline profile, not a certification of runtime safety."""
    config = agent.get("Config") or {}
    host = agent.get("HostConfig") or {}
    state = agent.get("State") or {}
    labels = config.get("Labels") or {}
    if (
        state.get("Running") is not False or
        labels.get("com.docker.compose.project") != "ccpc_codex_dev_agent" or
        labels.get("com.docker.compose.service") != "agent" or
        (host.get("RestartPolicy") or {}).get("Name") not in ("", "no") or
        host.get("Privileged") is not False or
        host.get("ReadonlyRootfs") is not True or
        host.get("NetworkMode") == "host" or
        str(config.get("User")) not in ("1000", "1000:1000") or
        set(host.get("CapDrop") or []) != {"ALL"} or
        "no-new-privileges:true" not in (host.get("SecurityOpt") or [])
    ):
        raise GateFailure()

    # Mutable :latest tags are not sufficient provenance, even if the
    # stopped container's image ID happens to match its local tag.
    image = config.get("Image") or ""
    if not re.fullmatch(r"frappe/bench@sha256:[0-9a-f]{64}", image):
        raise GateFailure()
    if (host.get("Memory") != MEMORY or host.get("MemorySwap") != MEMORY or
            host.get("PidsLimit") != PIDS):
        raise GateFailure()
    if host.get("PortBindings") or host.get("Devices") or host.get("Binds"):
        # The historical synthetic DB password was bound as a secret.
        # Any bind-mount must be independently reviewed before this gate
        # may permit even offline launch.
        raise GateFailure()

    networks = (agent.get("NetworkSettings") or {}).get("Networks") or {}
    if set(networks) != {LAB}:
        raise GateFailure()
    if (
        lab.get("Name") != LAB or lab.get("Driver") != "bridge" or
        lab.get("Internal") is not True or
        lab.get("Attachable") is not False or
        lab.get("EnableIPv6") is not False
    ):
        raise GateFailure()

    mounts = agent.get("Mounts") or []
    expected = {"/home/frappe", "/home/frappe/.cache"}
    if len(mounts) != 2:
        raise GateFailure()
    for mount in mounts:
        if mount.get("Type") != "volume" or mount.get("Destination") not in expected:
            raise GateFailure()
        expected.remove(mount["Destination"])
    if expected:
        raise GateFailure()
    return True


def verify():
    authorization_required()
    specs = guard.inspect_host()        # Requires stopped agent; host identity.
    guard.check_current_rules(specs)    # Exact three DROP rules and top order.
    container = json.loads(guard.command(["docker", "inspect", AGENT]))
    network = json.loads(guard.command(["docker", "network", "inspect", LAB]))
    if len(container) != 1 or len(network) != 1:
        raise GateFailure()
    return validate_agent_runtime(container[0], network[0])


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["verify"]):
        print("STOP: no start/monitor/apply mode exists")
        return 2
    try:
        verify()
    except (GateFailure, guard.GuardFailure, OSError, ValueError,
            TypeError, KeyError, IndexError, AttributeError):
        print("STOP: offline Codex startup interlock failed")
        return 1
    print("OFFLINE_PRELAUNCH_STATIC_GUARD_PASSED=True")
    print("agent_launch_authorized=False")
    print("runtime_firewall_loss_monitoring_verified=False")
    print("INSPECTION_COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
