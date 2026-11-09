#!/usr/bin/env python3
"""Read-only NEW-host synthetic Compose v2.24.4+ validation; never deploys.

Use on a previously established PRIVATE scratch directory containing exactly
five independently pinned source YAMLs and sixth Option A overlay.
No real credentials; no Docker engine mutation; no raw config/env printing.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path("/home/ccpcadmin/.ccpc-compose-review-c12d46f/source-only")
FILES = (
    "compose.yaml",
    "overrides/compose.mariadb.yaml",
    "overrides/compose.redis.yaml",
    "overrides/compose.lan-production.yaml",
    "overrides/compose.dedicated-pre-tls.yaml",
    "compose.option-a-precutover.yaml",
)
GIT_BLOB_HASHES = (
    "752b86e1ba4c1977a2636b1916f6015771f4c28c",
    "94e177c38707a40bdd2715287565c80e41c4f3d3",
    "64bc05ac2e955719822718e5118a62d0c9771e24",
    "3e65debe8d007b73d23f46f880cc53a182a19829",
    "14fd89a3c2371104f464964137483de9f4a35861",
)
OVERLAY_SHA256 = "bc283e1a48a314c0321f48f8636d30142f49edc2560ef24663efbe39408b5114"
ACCEPTANCE = {"backend", "frontend", "websocket", "db", "redis-cache", "redis-queue"}
DISABLED = {"configurator", "scheduler", "queue-short", "queue-long"}
VOLUMES = {"sites", "logs", "db-data", "redis-queue-data"}
APP_IMAGE = "ccpcerp:v16.50.0"


def stop(phase):
    print("STOP:OPTION_A_" + phase)
    sys.exit(1)


def git_blob_sha(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


if not ROOT.is_dir() or (ROOT / ".env").exists():
    stop("SOURCE_PATH_OR_ENV")
try:
    contents = [(ROOT / name).read_bytes() for name in FILES]
except OSError:
    stop("SOURCE_MISSING")

if any(git_blob_sha(contents[i]) != GIT_BLOB_HASHES[i] for i in range(5)):
    stop("FIVE_SOURCE_BLOB_MISMATCH")
if hashlib.sha256(contents[-1]).hexdigest() != OVERLAY_SHA256:
    stop("SIXTH_OVERLAY_HASH_MISMATCH")
print("OPTION_A_SIX_FILE_SOURCE_HASH_PASS")

env = {
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "HOME": "/home/ccpcadmin",
    "DB_PASSWORD": "CCPC_SYNTHETIC_TEST_ONLY",
    "CUSTOM_IMAGE": "ccpcerp",
    "CUSTOM_TAG": "v16.50.0",
    "PULL_POLICY": "never",
}
base = ["docker", "compose", "--project-name", "ccpc_prod_erpnext"]
for name in FILES:
    base += ["-f", name]


def render(profile=None):
    cmd = base.copy()
    if profile is not None:
        cmd += ["--profile", profile]
    try:
        result = subprocess.run(
            cmd + ["config", "--format", "json"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        if result.returncode:
            stop("COMPOSE_PARSER")
        return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        stop("COMPOSE_PARSER")


# Compose config renders only enabled services. All-profile mode exposes all
# definitions for static validation; this does NOT activate any runtime service.
all_model = render("*")
active_model = render("ccpc-acceptance")
off_model = render()
print("OPTION_A_COMPOSE_PARSER_PASS")

all_services = all_model.get("services", {})
active_services = active_model.get("services", {})
off_services = off_model.get("services", {})
if set(all_services) != ACCEPTANCE | DISABLED:
    stop("ALL_SERVICE_SET")
if set(active_services) != ACCEPTANCE:
    stop("ACCEPTANCE_SERVICE_SET")
if off_services:
    stop("DEFAULT_PROFILE_SERVICES")
for name in ACCEPTANCE:
    if set(all_services[name].get("profiles", [])) != {"ccpc-acceptance"}:
        stop("ACCEPTANCE_PROFILES")
for name in DISABLED:
    profiles = all_services[name].get("profiles", [])
    if not profiles or "ccpc-acceptance" in profiles:
        stop("DISABLED_PROFILES")
print("OPTION_A_SERVICE_PROFILE_BOUNDARIES_PASS")

for service_name, svc in all_services.items():
    if svc.get("ports") or svc.get("privileged") or svc.get("network_mode"):
        stop("PUBLISHED_OR_PRIVILEGED")
    if svc.get("restart") != "no" or svc.get("pull_policy") != "never":
        stop("RESTART_OR_PULL")
    if svc.get("cap_add") or svc.get("devices") or svc.get("pid") == "host":
        stop("PRIVILEGE_SCOPE")
    if svc.get("image") != (
        "mariadb:11.8" if service_name == "db"
        else "redis:8.6-alpine" if service_name in {"redis-cache", "redis-queue"}
        else APP_IMAGE
    ):
        stop("IMAGE_TAG")
    for volume in svc.get("volumes", []):
        if volume.get("type") != "volume" or volume.get("source") not in VOLUMES:
            stop("UNEXPECTED_MOUNT")
    deps = svc.get("depends_on", {})
    if set(deps) & DISABLED and service_name in ACCEPTANCE:
        stop("DEPENDENCY_STARTS_DISABLED_SERVICE")
    if set(svc.get("networks", {})) - {"default"}:
        stop("ADDITIONAL_SERVICE_NETWORK")
print("OPTION_A_NO_PORT_PULL_RESTART_OR_DISABLED_DEPENDENCY_PASS")

networks = all_model.get("networks", {})
if set(networks) != {"default"}:
    stop("NETWORK_KEYS")
network = networks["default"]
if network.get("internal") is not True or network.get("external") is True:
    stop("INTERNAL_NETWORK")
if set(all_model.get("volumes", {})) != VOLUMES:
    stop("NAMED_VOLUMES")
print("OPTION_A_INTERNAL_NETWORK_AND_VOLUMES_PASS")
print("OPTION_A_SIX_FILE_SYNTHETIC_VALIDATION_COMPLETE_NO_RUNTIME")
