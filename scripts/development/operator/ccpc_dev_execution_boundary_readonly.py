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
    # Count OLD Compose containers, but never print any container names.
    states = docker("ps", "-a", "--filter",
                    "label=com.docker.compose.project=" + OLD_PROJECT,
                    "--format", "{{.State}}").splitlines()
    require(len(states) <= 100)
    require(all(s in ("running", "created", "exited", "paused", "restarting",
                      "dead", "removing") for s in states))
    old_running = sum(s in ("running", "restarting", "paused") for s in states)

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
        "OLD_PRODUCTION_COMPOSE_ACTIVE": old_running,
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
        require(result["OLD_PRODUCTION_COMPOSE_ACTIVE"] == 0)
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
