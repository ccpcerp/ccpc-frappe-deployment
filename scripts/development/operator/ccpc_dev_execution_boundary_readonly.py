#!/usr/bin/env python3
"""CCPC legacy-host DEV automation boundary audit; read-only, operator initiated.

This is a metadata-only preflight, NOT an agent, a grant of SSH access,
a proof of OLD business-write isolation, or a permission to start services.
Run only on legacy ccpcerpserver as the named operator via sudo AFTER
reviewing the exact checked-out GitHub commit. Never print Docker inspect
JSON, environment variables, credentials, mount paths or app data.
"""
import json
import os
import socket
import subprocess
import sys

HOST = "ccpcerpserver"
OPERATOR = "gani"
DEV = "frappe_docker_devcontainer-frappe-1"
DEV_PROJECT = "frappe_docker_devcontainer"
OLD_PROJECT = "frappe_docker"
# Retained OLD data containers may remain available for recovery; never
# stop or remove them merely to permit DEV testing. The app/worker/scheduler
# services must be inactive and exact project membership must be unchanged.
OLD_SERVICE_NAMES = ("frontend", "queue-short", "backend", "queue-long",
                     "websocket", "scheduler", "configurator",
                     "redis-queue", "redis-cache", "db")
OLD_EXPECTED = {f"{OLD_PROJECT}-{name}-1" for name in OLD_SERVICE_NAMES}
OLD_RETAINED_DATA = {f"{OLD_PROJECT}-{name}-1"
                     for name in ("db", "redis-cache", "redis-queue")}
DOCKER = ("docker", "--host", "unix:///var/run/docker.sock")


class Stop(Exception):
    """Fail closed without disclosing raw Docker output."""


def require(value):
    if not value:
        raise Stop()


def operator_guard():
    require(os.geteuid() == 0)
    require(os.environ.get("SUDO_USER") == OPERATOR)
    require(socket.gethostname().split(".")[0] == HOST)
    require(not any(k in os.environ for k in
                    ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CERT_PATH",
                     "DOCKER_CONFIG", "DOCKER_TLS_VERIFY")))


def docker(*args):
    try:
        proc = subprocess.run(DOCKER + args, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=15)
        require(len(proc.stdout) <= 262144)
        return proc.stdout.decode("utf-8", "strict").strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise Stop() from None


def inspect_value(field):
    # Callers supply only fixed templates below; no user-provided templates.
    return docker("container", "inspect", "--format", field, DEV)


def is_risky_credential_mount(item):
    require(isinstance(item, dict))
    destination = item.get("Destination")
    source = item.get("Source")
    require(isinstance(destination, str) and isinstance(source, str))
    sensitive = ("/home/frappe/.ssh", "/root/.ssh", "/run/credentials",
                 "/etc/ccpc-https", "/mnt/erpnext_backups")
    for path in sensitive:
        if destination == path or destination.startswith(path + "/"):
            return True
        if source == path or source.startswith(path + "/"):
            return True
    if ".ssh" in source.split("/") or ".ssh" in destination.split("/"):
        return True
    return False


def audit():
    # Pin expected OLD project names to avoid mistaking an unknown live
    # container for a harmless retained data service. Never print names.
    raw_states = docker("ps", "-a", "--filter",
                        "label=com.docker.compose.project=" + OLD_PROJECT,
                        "--format", "{{.Names}} {{.State}}").splitlines()
    require(len(raw_states) == len(OLD_EXPECTED))
    states = {}
    valid_states = {"running", "created", "exited", "paused", "restarting",
                    "dead", "removing"}
    for line in raw_states:
        name, sep, state = line.rpartition(" ")
        require(bool(sep) and name in OLD_EXPECTED and
                state in valid_states and name not in states)
        states[name] = state
    require(set(states) == OLD_EXPECTED)
    active_states = {"running", "restarting", "paused"}
    old_app_active = sum(state in active_states for name, state in states.items()
                         if name not in OLD_RETAINED_DATA)
    old_data_active = sum(state in active_states for name, state in states.items()
                          if name in OLD_RETAINED_DATA)

    project = inspect_value('{{index .Config.Labels "com.docker.compose.project"}}')
    require(project == DEV_PROJECT)
    running = inspect_value("{{.State.Running}}") == "true"
    privileged = inspect_value("{{.HostConfig.Privileged}}") == "true"
    mounts = json.loads(inspect_value("{{json .Mounts}}"))
    require(isinstance(mounts, list) and len(mounts) <= 100)
    credential_mount = any(is_risky_credential_mount(m) for m in mounts)
    socket_mount = any(m.get("Destination") in ("/var/run/docker.sock",
                                                "/run/docker.sock") for m in mounts)
    # Never describe these results as proving absent writers, private access
    # control, host network isolation, or readiness for arbitrary AI tools.
    return {
        "OLD_PRODUCTION_APP_ACTIVE": old_app_active,
        "OLD_PRODUCTION_RETAINED_DATA_ACTIVE": old_data_active,
        "DEV_CONTAINER_RUNNING": running,
        "DEV_CREDENTIAL_MOUNT_DETECTED": credential_mount,
        "DEV_DOCKER_SOCKET_MOUNT_DETECTED": socket_mount,
        "DEV_PRIVILEGED": privileged,
    }


def main():
    try:
        operator_guard()
        result = audit()
        for key, value in result.items():
            if isinstance(value, bool):
                value = "YES" if value else "NO"
            print(f"{key}={value}")
        require(result["OLD_PRODUCTION_APP_ACTIVE"] == 0)
        require(result["DEV_CONTAINER_RUNNING"] is True)
        require(result["DEV_CREDENTIAL_MOUNT_DETECTED"] is False)
        require(result["DEV_DOCKER_SOCKET_MOUNT_DETECTED"] is False)
        require(result["DEV_PRIVILEGED"] is False)
        print("CCPC_DEV_EXECUTION_BOUNDARY_PREFLIGHT_PASS")
        return 0
    except Exception:
        print("CCPC_DEV_EXECUTION_BOUNDARY_STOP_REVIEW_REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
