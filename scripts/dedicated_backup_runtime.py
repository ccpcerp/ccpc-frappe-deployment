"""Read-only Docker/host identity verifier; inert until an approved caller uses it.

Never starts, stops, execs, mounts, backs up or changes a container.  This verifies
identity only.  It does NOT attest DB/files quiescence, encryption or partial
backup rules, and it MUST NOT be used to authorize a real backup by itself.
"""

from __future__ import annotations

import json
import os
import re
import socket
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

EXPECTED_HOST = "ccpcerp-prod"
EXPECTED_SITE = "ccpcerp.local"
EXPECTED_PROFILE = "dedicated-pre-tls"
EXPECTED_FRAPPE_SHA = "988e54f3c4c291e2077a83809663f123731abe76"
SITE_DESTINATION = "/home/frappe/frappe-bench/sites"
DB_DESTINATION = "/var/lib/mysql"
IMAGE_RE = re.compile(r"sha256:[a-f0-9]{64}\Z")
HASH_RE = re.compile(r"[a-f0-9]{64}\Z")
LABEL_SHA_RE = re.compile(r"[a-f0-9]{40}\Z")
PROJECT_RE = re.compile(r"[a-z0-9][a-z0-9_-]{1,63}\Z")
ID_RE = re.compile(r"[a-f0-9]{12,64}\Z")


class RuntimeRejected(RuntimeError):
    """Failure with intentionally nonsensitive diagnostics."""


@dataclass(frozen=True)
class ApprovedRuntime:
    """Out-of-band, reviewed expectations; never derive these from Docker output."""

    project: str
    backend_image_id: str
    db_image_id: str
    backend_config_hash: str
    db_config_hash: str
    sites_volume: str
    db_volume: str


@dataclass(frozen=True)
class VerifiedIdentity:
    """Validated runtime identity. Deliberately NOT a backup-ready attestation."""

    host: str
    project: str
    site: str
    profile: str
    frappe_sha: str
    backend_image_id: str
    db_image_id: str
    site_volume_verified: bool
    database_volume_verified: bool
    # These gates remain closed until separate independent verification.
    writes_quiesced: bool = False
    no_partial_backup_filters: bool = False
    encryption_disabled: bool = False

    @property
    def backup_ready(self) -> bool:
        return False


def _expect_config(expected: ApprovedRuntime) -> None:
    if not isinstance(expected, ApprovedRuntime):
        raise RuntimeRejected("Approved release expectation missing")
    if not isinstance(expected.project, str) or not PROJECT_RE.fullmatch(expected.project):
        raise RuntimeRejected("Invalid approved Compose project")
    for name in (expected.backend_image_id, expected.db_image_id):
        if not isinstance(name, str) or not IMAGE_RE.fullmatch(name):
            raise RuntimeRejected("Unpinned approved image")
    for label in (expected.backend_config_hash, expected.db_config_hash):
        if not isinstance(label, str) or not HASH_RE.fullmatch(label):
            raise RuntimeRejected("Unapproved Compose configuration hash")
    if (expected.sites_volume, expected.db_volume) != (
        expected.project + "_sites", expected.project + "_db-data"
    ):
        raise RuntimeRejected("Unexpected approved Compose volume names")


def _json_list(query: Callable[[list[str]], str], argv: list[str]) -> list[dict]:
    try:
        data = query(argv)
        if not isinstance(data, str) or len(data) > 1_000_000:
            raise ValueError("Oversized or non-text Docker response")
        out = json.loads(data)
    except (ValueError, TypeError, OSError) as exc:
        raise RuntimeRejected("Docker inspection unavailable") from exc
    if not isinstance(out, list) or len(out) != 1 or not isinstance(out[0], dict):
        raise RuntimeRejected("Ambiguous Docker inspection")
    return out


def _single_inspect(query: Callable[[list[str]], str], kind: str, key: str) -> dict:
    return _json_list(query, ["docker", kind, "inspect", key])[0]


def _labels(record: dict) -> dict:
    config = record.get("Config")
    if not isinstance(config, dict) or not isinstance(config.get("Labels"), dict):
        raise RuntimeRejected("Container labels unavailable")
    return config["Labels"]


def _require_container(record: dict, *, service: str, container_id: str,
                       expected: ApprovedRuntime, image_id: str,
                       config_hash: str) -> None:
    actual_id = record.get("Id")
    if (not isinstance(actual_id, str) or len(actual_id) != 64
            or not ID_RE.fullmatch(actual_id) or not actual_id.startswith(container_id)
            or record.get("Image") != image_id):
        raise RuntimeRejected("Container identity/image mismatch")
    labels = _labels(record)
    if (labels.get("com.docker.compose.project"), labels.get("com.docker.compose.service"),
        labels.get("com.docker.compose.config-hash")) != (expected.project, service, config_hash):
        raise RuntimeRejected("Container Compose provenance mismatch")
    state = record.get("State", {})
    if not isinstance(state, dict) or state.get("Running") is not True or state.get("Paused") is True or state.get("Restarting") is True:
        raise RuntimeRejected("Container is not stably running")
    if service == "db" and (not isinstance(state.get("Health"), dict)
                            or state["Health"].get("Status") != "healthy"):
        raise RuntimeRejected("MariaDB is not healthy")
    host = record.get("HostConfig", {})
    if not isinstance(host, dict) or host.get("Privileged") is not False or host.get("PidMode") == "host" or host.get("NetworkMode") == "host":
        raise RuntimeRejected("Unexpected privileged container")


def _verify_mount(record: dict, *, volume_name: str, dest: str, source: str) -> None:
    mounts = record.get("Mounts")
    if not isinstance(mounts, list) or len(mounts) != 1:
        raise RuntimeRejected("Container mount inventory is ambiguous")
    mount = mounts[0]
    if not isinstance(mount, dict) or (
        mount.get("Type"), mount.get("Name"), mount.get("Destination"),
        mount.get("Source"), mount.get("RW")
    ) != ("volume", volume_name, dest, source, True):
        raise RuntimeRejected("Container storage volume is not approved")


def _volume_root(query: Callable[[list[str]], str], name: str, project: str, logical: str) -> Path:
    volume = _single_inspect(query, "volume", name)
    if volume.get("Name") != name or not isinstance(volume.get("Labels"), dict):
        raise RuntimeRejected("Volume identity unavailable")
    if (volume["Labels"].get("com.docker.compose.project"),
        volume["Labels"].get("com.docker.compose.volume")) != (project, logical):
        raise RuntimeRejected("Volume provenance mismatch")
    value = volume.get("Mountpoint")
    if not isinstance(value, str) or not value.startswith("/"):
        raise RuntimeRejected("Volume mountpoint unavailable")
    return Path(value)


def _safe_dir(path: Path) -> None:
    if not path.is_absolute() or ".." in path.parts:
        raise RuntimeRejected("Unsafe site volume path")
    try:
        if path.resolve(strict=True) != path or not stat.S_ISDIR(path.lstat().st_mode):
            raise RuntimeRejected("Noncanonical site volume path")
    except (OSError, RuntimeError) as exc:
        raise RuntimeRejected("Site volume inaccessible") from exc


def _verify_site_presence(sites_root: Path) -> None:
    """Check metadata only. Never read secrets from site_config.json."""
    _safe_dir(sites_root)
    site_dir = sites_root / EXPECTED_SITE
    _safe_dir(site_dir)
    site_file = site_dir / "site_config.json"
    try:
        info = site_file.lstat()
    except OSError as exc:
        raise RuntimeRejected("Frappe site config missing") from exc
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size == 0:
        raise RuntimeRejected("Frappe site config metadata unsafe")


def _ids(query: Callable[[list[str]], str], project: str) -> list[str]:
    try:
        raw = query(["docker", "container", "ls", "--all", "--quiet",
                     "--filter", "label=com.docker.compose.project=" + project])
    except (OSError, ValueError, TypeError) as exc:
        raise RuntimeRejected("Container inventory unavailable") from exc
    if not isinstance(raw, str) or len(raw) > 2500:
        raise RuntimeRejected("Unexpected container inventory")
    ids = raw.split()
    if len(ids) < 2 or len(ids) > 24 or len(set(ids)) != len(ids) or any(not ID_RE.fullmatch(i) for i in ids):
        raise RuntimeRejected("Missing/duplicate/malformed container inventory")
    return ids


def _verify_image(query: Callable[[list[str]], str], image_id: str, *, frappe: bool) -> None:
    image = _single_inspect(query, "image", image_id)
    if image.get("Id") != image_id:
        raise RuntimeRejected("Image ID changed")
    if frappe:
        config = image.get("Config")
        labels = config.get("Labels") if isinstance(config, dict) else None
        if not isinstance(labels, dict) or labels.get("org.ccpc.frappe.sha") != EXPECTED_FRAPPE_SHA:
            raise RuntimeRejected("Frappe source provenance not verified")


def verify_runtime(expected: ApprovedRuntime, query: Callable[[list[str]], str],
                   *, hostname: Callable[[], str] = socket.gethostname) -> VerifiedIdentity:
    """Verify independent read-only host, Docker and filesystem evidence.

    The query callback must be a trustworthy Docker read-only inspector. No
    database write-quiescence, backup policy or encryption status is inferred.
    """
    _expect_config(expected)
    if hostname().split(".", 1)[0] != EXPECTED_HOST:
        raise RuntimeRejected("Wrong host; refusing inventory")
    if not callable(query):
        raise RuntimeRejected("Docker inspector missing")
    ids = _ids(query, expected.project)
    relevant: dict[str, tuple[dict, str]] = {}
    for container_id in ids:
        obj = _single_inspect(query, "container", container_id)
        labels = _labels(obj)
        if labels.get("com.docker.compose.project") != expected.project:
            raise RuntimeRejected("Unexpected foreign Compose container")
        service = labels.get("com.docker.compose.service")
        if service in ("backend", "db"):
            if service in relevant:
                raise RuntimeRejected("Duplicate critical Compose service")
            relevant[service] = (obj, container_id)
    if set(relevant) != {"backend", "db"}:
        raise RuntimeRejected("Missing required Frappe or MariaDB service")
    backend, backend_id = relevant["backend"]
    db, db_id = relevant["db"]
    _require_container(backend, service="backend", container_id=backend_id,
                       expected=expected, image_id=expected.backend_image_id,
                       config_hash=expected.backend_config_hash)
    _require_container(db, service="db", container_id=db_id, expected=expected,
                       image_id=expected.db_image_id, config_hash=expected.db_config_hash)
    _verify_image(query, expected.backend_image_id, frappe=True)
    _verify_image(query, expected.db_image_id, frappe=False)
    sites = _volume_root(query, expected.sites_volume, expected.project, "sites")
    database = _volume_root(query, expected.db_volume, expected.project, "db-data")
    _safe_dir(database)
    _verify_mount(backend, volume_name=expected.sites_volume, dest=SITE_DESTINATION, source=str(sites))
    _verify_mount(db, volume_name=expected.db_volume, dest=DB_DESTINATION, source=str(database))
    _verify_site_presence(sites)
    return VerifiedIdentity(EXPECTED_HOST, expected.project, EXPECTED_SITE,
                            EXPECTED_PROFILE, EXPECTED_FRAPPE_SHA,
                            expected.backend_image_id, expected.db_image_id, True, True)


def docker_readonly_query(argv: list[str]) -> str:
    """Read-only, shell-free Docker CLI transport; not invoked automatically."""
    if not isinstance(argv, list) or not argv or argv[0] != "docker" or len(argv) < 4:
        raise RuntimeRejected("Unauthorized Docker operation")
    # Permit only the three exact read-only shapes generated above.
    shape = tuple(argv[1:3])
    if shape == ("container", "ls"):
        if len(argv) != 7 or argv[3:6] != ["--all", "--quiet", "--filter"] or not argv[6].startswith("label=com.docker.compose.project="):
            raise RuntimeRejected("Unsupported Docker inventory request")
    elif shape in (("container", "inspect"), ("image", "inspect"), ("volume", "inspect")):
        if len(argv) != 4:
            raise RuntimeRejected("Unsupported Docker inspection request")
    else:
        raise RuntimeRejected("Write-capable Docker operation is forbidden")
    try:
        fixed_local = ["docker", "--host", "unix:///var/run/docker.sock", *argv[1:]]
        safe_env = {key: value for key, value in os.environ.items() if not key.startswith("DOCKER_")}
        proc = subprocess.run(fixed_local, capture_output=True, text=True,
                              check=False, timeout=8, env=safe_env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeRejected("Docker read-only inspection failed") from exc
    if proc.returncode != 0 or len(proc.stdout) > 1_000_000:
        raise RuntimeRejected("Docker inspection unavailable or oversized")
    return proc.stdout


if __name__ == "__main__":
    raise SystemExit("NOT ENABLED: read-only evidence library, no production entry point")
