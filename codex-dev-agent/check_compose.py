#!/usr/bin/env python3
"""Read-only, fail-closed static preflight for the new synthetic DEV Compose project.

Uses 'docker compose config --format json' rather than parsing YAML ourselves.
This does NOT establish production network separation or authorize startup.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = "ccpc_codex_dev_agent"
REQUIRED = {"agent", "db", "redis-cache", "redis-queue", "egress-proxy"}


def reject(message):
    raise ValueError(message)


def only_network(service, expected, name):
    networks = service.get("networks", {})
    actual = set(networks if isinstance(networks, list) else networks.keys())
    if actual != expected:
        reject(f"{name}: unexpected networks")


def validate(rendered):
    if rendered.get("name") != PROJECT:
        reject("incorrect Compose project name")
    services = rendered.get("services") or {}
    if set(services) != REQUIRED:
        reject("unexpected Compose services")
    networks = rendered.get("networks") or {}
    if not (networks.get("lab") or {}).get("internal"):
        reject("lab network must be internal")
    if (networks.get("outgoing") or {}).get("internal"):
        reject("proxy outgoing network must be separate from the internal lab")
    for name, service in services.items():
        if service.get("privileged") or service.get("network_mode") or service.get("pid") == "host":
            reject(f"{name}: privileged/host mode")
        if service.get("ports") or service.get("devices") or service.get("extra_hosts"):
            reject(f"{name}: ports/devices/extra_hosts prohibited")
        required_images = {
            "agent": "frappe/bench:latest",
            "db": "mariadb:11.8",
            "redis-cache": "redis:7-alpine",
            "redis-queue": "redis:7-alpine",
            "egress-proxy": "ubuntu/squid:latest",
        }
        if service.get("image") != required_images[name]:
            reject(f"{name}: unreviewed image")
        if service.get("pull_policy") != "never":
            reject(f"{name}: image pulls must be disabled for offline gate")
        # MariaDB official image briefly starts as root to initialize/chown
        # its *new synthetic* data volume, then switches to mysql.
        expected_caps = {"CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "FOWNER"} if name == "db" else set()
        if set(service.get("cap_add") or []) != expected_caps:
            reject(f"{name}: unexpected Linux capabilities")
        if "ALL" not in (service.get("cap_drop") or []):
            reject(f"{name}: missing cap_drop ALL")
        opts = service.get("security_opt") or []
        if not any("no-new-privileges" in str(item) for item in opts):
            reject(f"{name}: missing no-new-privileges")
        only_network(service, {"lab", "outgoing"} if name == "egress-proxy" else {"lab"}, name)

    for name in ("redis-cache", "redis-queue"):
        if services[name].get("user") != "redis":
            reject(f"{name}: Redis must run as the non-root redis user")

    agent = services["agent"]
    if not agent.get("read_only") or str(agent.get("user")) not in ("1000:1000", "1000"):
        reject("agent must run as nonroot with read-only rootfs")
    if set(agent.get("profiles") or []):
        reject("agent must be available in offline default profile")

    proxy = services["egress-proxy"]
    if set(proxy.get("profiles") or []) != {"online"}:
        reject("proxy must only start with explicit online profile")
    if not proxy.get("read_only"):
        reject("proxy must have read-only rootfs")

    mounts = agent.get("volumes") or []
    expected_mounts = {"/home/frappe", "/home/frappe/.cache"}
    destinations = {m.get("target") for m in mounts if isinstance(m, dict)}
    if destinations != expected_mounts or len(mounts) != len(expected_mounts):
        reject("agent mount destinations differ from private named-volume allowlist")
    for m in mounts:
        if m.get("type") != "volume" or m.get("source") not in {"agent-home", "agent-cache"}:
            reject("agent mount may not bind a host path or reuse non-agent volumes")
    for sec in agent.get("secrets") or []:
        source = sec.get("source") if isinstance(sec, dict) else sec
        if source != "db-user-password":
            reject("agent may only hold synthetic database user secret")

    secret_defs = rendered.get("secrets") or {}
    if set(secret_defs) != {"db-user-password", "db-root-password"}:
        reject("unexpected Docker secrets")
    for name, definition in secret_defs.items():
        declared = str(definition.get("file") or "")
        if not declared.endswith("/codex-dev-agent/local-secrets/" + name):
            reject("synthetic secrets must live in locally excluded directory")

    for name in ("db", "redis-cache", "redis-queue"):
        if services[name].get("volumes"):
            for m in services[name]["volumes"]:
                if m.get("type") not in ("volume",):
                    reject(f"{name}: unexpected bind or host mount")
    return True


def main():
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(HERE / "compose.yaml"),
             "--profile", "online", "config", "--format", "json"],
            cwd=HERE, capture_output=True, text=True, check=True,
        )
        validate(json.loads(result.stdout))
    except (ValueError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print("STOP: Compose static preflight FAILED:", type(exc).__name__)
        return 1
    print("PASS: standalone agent Compose source/mount/profile gate")
    print("NOT VERIFIED: host firewall, egress to new/old production, DNS/network bypass")
    print("NOT VERIFIED: image provenance, DB startup, Codex login, actual Frappe bench")
    print("Do not enable online profile or local agent execution without those checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
