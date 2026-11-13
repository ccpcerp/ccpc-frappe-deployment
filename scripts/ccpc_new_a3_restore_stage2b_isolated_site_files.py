#!/usr/bin/env python3
"""One-use NEW-only Stage 2B isolated ERPNext site/config + attachment restoration.

--preflight is read only; --execute creates only the fresh independent sites
volume, a new test-only DB user and private test credentials, and writes Frappe
site files there. No apps/ports/workers/scheduler/migrations/OLD/prod changes.
On STOP keep all partial test resources for manual review; NEVER rerun blindly.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import socket
import stat
import subprocess
import tarfile

HOST = "ccpcerp-prod"
OPERATOR = "ccpcadmin"
RUN = "20261112T090214Z-0148d36b2cb678b3"
PREFIX = "ccpc_a3_restore_drill_20261112"
NETWORK = PREFIX + "_internal"
DB = PREFIX + "-db-1"
DB_VOLUME = PREFIX + "_db-data"
SITES_VOLUME = PREFIX + "_sites"
SCHEMA = "ccpc_restore_20261112"
SITE = "ccpcerp.local"
ROOT = Path("/var/lib/ccpc-a3-isolated-restore-20261112")
ROOT_SECRETS = Path("/var/lib/ccpc-a3-restore-db-secrets-20261112")
NEW_SECRETS = Path("/var/lib/ccpc-a3-restore-site-secrets-20261112")
NAS_MOUNT = "/mnt/ccpc-a3-restore-readonly-20261112"
LIVE_NAS_MOUNT = "/mnt/ccpcerp-prod_backups"
APP_IMAGE = "sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8"
DB_IMAGE = "sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4"
REDIS_IMAGE = "sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763"
FILE_PATTERN = re.compile(r"\A\d{8}_\d{6}-ccpcerp_local-(database\.sql\.gz|site_config_backup\.json|files\.tar|private-files\.tar)\Z")
ROLE_BY_SUFFIX = {
    "database.sql.gz": "database",
    "site_config_backup.json": "site_config",
    "files.tar": "public_files",
    "private-files.tar": "private_files",
}
PROTECTED = {
    *(f"ccpc_prod_erpnext-{svc}-1" for svc in
      ("frontend", "backend", "websocket", "redis-cache", "redis-queue", "db")),
    *(f"{project}-{svc}-1" for project in
      ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
      for svc in ("db", "redis-cache", "redis-queue")),
}

class Stop(Exception):
    pass

def insist(condition: bool, reason: str) -> None:
    if not condition:
        raise Stop(reason)

def command(args: list[str], *, data: bytes | None = None, timeout: int = 45,
            check: bool = True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, timeout=timeout,
                                check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Stop("Command timed out or unavailable") from None
    if check:
        insist(result.returncode == 0, "Guarded command failed")
    return result

def docker(*args: str, data: bytes | None = None, timeout: int = 45,
           check: bool = True) -> subprocess.CompletedProcess:
    return command(["docker", "--host", "unix:///var/run/docker.sock", *args],
                   data=data, timeout=timeout, check=check)

def names(*args: str) -> set[str]:
    return set(docker(*args).stdout.decode("utf8", "strict").splitlines())

def inspect(kind: str, name: str) -> dict:
    result = json.loads(docker(kind, "inspect", name).stdout)
    insist(isinstance(result, list) and len(result) == 1, "Docker inspect shape")
    return result[0]

def root_node(path: Path, mode: int, directory: bool) -> None:
    info = path.lstat()
    insist(info.st_uid == 0 and info.st_gid == 0 and
           stat.S_IMODE(info.st_mode) == mode and
           (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)),
           "Protected file or directory identity changed")

def hash_file(path: Path) -> tuple[int, str]:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        first = os.fstat(stream.fileno())
        insist(stat.S_ISREG(first.st_mode) and first.st_nlink == 1 and
               first.st_size > 0, "Backup file identity invalid")
        hasher = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
        last = os.fstat(stream.fileno())
        insist((first.st_dev, first.st_ino, first.st_size, first.st_mtime_ns) ==
               (last.st_dev, last.st_ino, last.st_size, last.st_mtime_ns),
               "Backup file changed during read")
        return first.st_size, hasher.hexdigest()

def read_manifest() -> dict[str, dict]:
    root_node(ROOT, 0o700, True)
    root_node(ROOT / "manifest.json", 0o600, False)
    root_node(ROOT / "NAS_COMPLETED_VERIFIED", 0o600, False)
    insist((ROOT / "NAS_COMPLETED_VERIFIED").read_bytes() == (RUN + "\n").encode(),
           "Independent NAS copy marker mismatch")
    raw = (ROOT / "manifest.json").read_bytes()
    insist(len(raw) <= 16384, "Manifest too large")
    manifest = json.loads(raw)
    insist(isinstance(manifest, dict) and manifest.get("schema") == 1 and
           manifest.get("run_id") == RUN and manifest.get("site") == SITE and
           manifest.get("project") == "ccpc_prod_erpnext" and
           manifest.get("image") == APP_IMAGE, "Unexpected backup source manifest")
    entries = manifest.get("artifacts")
    insist(isinstance(entries, list) and len(entries) == 4, "Four artifacts required")
    roles: dict[str, dict] = {}
    files: set[str] = set()
    for entry in entries:
        insist(isinstance(entry, dict), "Malformed artifact")
        filename, role = entry.get("filename"), entry.get("role")
        insist(type(filename) is str and type(role) is str, "Invalid artifact metadata")
        match = FILE_PATTERN.fullmatch(filename)
        insist(match is not None and ROLE_BY_SUFFIX.get(match.group(1)) == role and
               role not in roles and filename not in files, "Unknown artifact")
        insist(type(entry.get("size")) is int and entry["size"] > 0 and
               type(entry.get("sha256")) is str and
               re.fullmatch(r"[a-f0-9]{64}", entry["sha256"]) is not None,
               "Invalid artifact length/digest")
        root_node(ROOT / filename, 0o600, False)
        insist(hash_file(ROOT / filename) == (entry["size"], entry["sha256"]),
               "Independent recovered backup SHA256 mismatch")
        roles[role] = entry
        files.add(filename)
    insist(set(roles) == set(ROLE_BY_SUFFIX.values()) and
           {p.name for p in ROOT.iterdir()} ==
           files | {"manifest.json", "NAS_COMPLETED_VERIFIED"},
           "Unexpected independent backup scratch contents")
    return roles

def read_archive(path: Path, section: str) -> tuple[str | None, bytes, str]:
    """Audit all tar paths/types and only read the one 16,501-byte private file."""
    directories = 0
    count = 0
    payload = b""
    basename = None
    visited: set[tuple[str, ...]] = set()
    try:
        with tarfile.open(path, "r:") as archive:
            for member in archive:
                raw = member.name
                insist(type(raw) is str and raw and not raw.startswith("/") and
                       not raw.startswith("./") and "//" not in raw and
                       "\\" not in raw and not any(ord(c) < 32 or ord(c) == 127 for c in raw),
                       "Tar entry unsafe")
                parts = tuple(raw.rstrip("/").split("/"))
                insist(parts not in visited and all(p not in ("", ".", "..") for p in parts),
                       "Tar entry duplicate/unsafe")
                visited.add(parts)
                insist(parts[0] == SITE and
                       (len(parts) == 1 or parts[1] == section), "Archive site/section mismatch")
                if member.isdir():
                    insist(parts in ((SITE,), (SITE, section), (SITE, section, "files")),
                           "Unexpected archive directory")
                    directories += 1
                else:
                    insist(member.isfile() and len(parts) == 4 and
                           parts[2] == "files" and section == "private" and
                           member.size == 16501, "Unexpected archive file type/size")
                    entry_name = parts[3]
                    insist(len(entry_name.encode("utf8")) <= 240 and
                           entry_name not in (".", "..") and
                           not any(ord(c) < 32 or ord(c) == 127 for c in entry_name),
                           "Unsafe private attachment basename")
                    src = archive.extractfile(member)
                    insist(src is not None, "Cannot read private file")
                    with src:
                        blob = src.read(16502)
                    insist(len(blob) == 16501, "Private file byte count mismatch")
                    basename, payload = entry_name, blob
                    count += 1
                insist(directories <= 4 and count <= 1, "Archive count exceeded")
    except (OSError, EOFError, tarfile.TarError):
        raise Stop("Backup tar integrity failure") from None
    insist(directories == 1 and count == (1 if section == "private" else 0),
           "Backup archive expected counts mismatch")
    return basename, payload, hashlib.sha256(payload).hexdigest()

def db_query(statement: str, *, schema: str | None = None) -> str:
    opts = ["exec", "-i", DB, "mariadb",
            "--defaults-extra-file=/run/secrets/db-client.cnf",
            "--batch", "--skip-column-names"]
    if schema:
        opts.append("--database=" + schema)
    return docker(*opts, data=(statement + "\n").encode("ascii")).stdout.decode("utf8", "strict").strip()

def read_only_preflight() -> dict:
    insist(os.geteuid() == 0 and os.environ.get("SUDO_USER") == OPERATOR and
           socket.gethostname().split(".")[0] == HOST, "Wrong host/account")
    insist(not any(k in os.environ for k in
                   ("DOCKER_HOST", "DOCKER_CONTEXT", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME")),
           "Unexpected Docker environment override")
    for mount in (NAS_MOUNT, LIVE_NAS_MOUNT):
        p = command(["findmnt", "--mountpoint", mount, "--noheadings"], check=False)
        insist(p.returncode == 1, "Unexpected/ambiguous NAS mount")
    root_node(ROOT_SECRETS, 0o700, True)
    for key in ("DO_NOT_RETRY", "mariadb-root-password", "db-client.cnf"):
        root_node(ROOT_SECRETS / key, 0o600, False)
    insist((ROOT_SECRETS / "DO_NOT_RETRY").read_bytes() == (RUN + "\n").encode(),
           "Test DB root secret marker invalid")
    insist(not NEW_SECRETS.exists() and not NEW_SECRETS.is_symlink(),
           "Stage2B test site secret dir exists; NEVER retry")
    insist(SITES_VOLUME not in names("volume", "ls", "--format", "{{.Name}}"),
           "Test site volume already exists; NEVER retry")
    insist(names("ps", "-a", "--format", "{{.Names}}") == PROTECTED | {DB} and
           names("ps", "--format", "{{.Names}}") == PROTECTED | {DB},
           "Protected container count/running-state changed")
    for image in (APP_IMAGE, DB_IMAGE, REDIS_IMAGE):
        insist(docker("image", "inspect", "--format", "{{.Id}}", image).stdout.strip().decode() == image,
               "Pinned local image missing")
    network = inspect("network", NETWORK)
    db = inspect("container", DB)
    db_volume = inspect("volume", DB_VOLUME)
    insist(network.get("Internal") is True and network.get("Driver") == "bridge" and
           network.get("Labels", {}).get("com.ccpc.test") == "restore-20261112",
           "Test Docker network boundary invalid")
    insist(db.get("Image") == DB_IMAGE and db.get("State", {}).get("Running") is True and
           db.get("State", {}).get("Health", {}).get("Status") == "healthy" and
           db.get("HostConfig", {}).get("PortBindings") in (None, {}) and
           set(db.get("NetworkSettings", {}).get("Networks", {})) == {NETWORK} and
           set(network.get("Containers", {})) == {db.get("Id")},
           "Isolated MariaDB identity/health/network invalid")
    insist(db_volume.get("Driver") == "local" and
           db_volume.get("Labels", {}).get("com.ccpc.test") == "restore-20261112" and
           db_volume.get("Mountpoint") ==
           "/var/lib/docker/volumes/" + DB_VOLUME + "/_data",
           "Test DB named volume identity invalid")
    insist({n for n in names("network", "ls", "--format", "{{.Name}}") if n.startswith(PREFIX)} == {NETWORK} and
           {n for n in names("volume", "ls", "--format", "{{.Name}}") if n.startswith(PREFIX)} == {DB_VOLUME},
           "Unexpected test-only resource")
    configs = network.get("IPAM", {}).get("Config", [])
    insist(isinstance(configs, list) and len(configs) == 1, "Unexpected test network IPAM")
    subnet = ipaddress.ip_network(configs[0].get("Subnet", ""), strict=True)
    insist(isinstance(subnet, ipaddress.IPv4Network) and
           any(subnet.subnet_of(ipaddress.ip_network(x)) for x in
               ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")),
           "Test network IPv4 subnet invalid")
    hostmask = str(subnet.network_address) + "/" + str(subnet.netmask)
    insist(db_query("SELECT 1") == "1" and
           db_query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='" +
                    SCHEMA + "' AND TABLE_TYPE='BASE TABLE'").isdigit() and
           int(db_query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='" +
                        SCHEMA + "' AND TABLE_TYPE='BASE TABLE'")) >= 700 and
           db_query("SELECT COUNT(*) FROM " + chr(96) + SCHEMA + chr(96) +
                    ".tabCompany") == "4",
           "Restored test-only SQL schema/data unavailable")
    insist(db_query("SELECT COUNT(*) FROM mysql.global_priv WHERE User='" + SCHEMA + "'") == "0",
           "Test DB app username already exists")
    roles = read_manifest()
    config = json.loads((ROOT / roles["site_config"]["filename"]).read_bytes())
    insist(isinstance(config, dict) and all(
           isinstance(config.get(k), str) and len(config[k]) >= 1
           for k in ("db_name", "db_password", "encryption_key")) and
           len(config["encryption_key"]) >= 20,
           "Backup historical encryption key unavailable")
    pub_name, pub_blob, _ = read_archive(ROOT / roles["public_files"]["filename"], "public")
    insist(pub_name is None and pub_blob == b"", "Expected zero public attachments")
    attachment, blob, digest = read_archive(ROOT / roles["private_files"]["filename"], "private")
    insist(attachment is not None and len(blob) == 16501, "Private file unavailable")
    print("CCPC_STAGE2B_PRIVATE_AND_PUBLIC_ARCHIVES_SHA256_AND_LAYOUT_PASS", flush=True)
    print("CCPC_STAGE2B_ISOLATED_DATABASE_HEALTH_AND_SCHEMA_PASS", flush=True)
    print("CCPC_STAGE2B_SITE_VOLUME_AND_ACCOUNT_UNUSED_PASS", flush=True)
    return {"hostmask": hostmask, "encryption_key": config["encryption_key"],
            "attachment": attachment, "blob": blob, "digest": digest}

def write_secret(path: Path, content: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(content)
        out.flush()
        os.fsync(out.fileno())
    root_node(path, 0o600, False)

def new_dir(parent: Path, name: str, mode: int) -> Path:
    target = parent / name
    target.mkdir(mode=mode)
    os.chmod(target, mode)
    os.chown(target, 1000, 1000)
    st = target.lstat()
    insist(stat.S_ISDIR(st.st_mode) and st.st_uid == 1000 and st.st_gid == 1000 and
           stat.S_IMODE(st.st_mode) == mode, "New site folder ownership mismatch")
    return target

def new_file(parent: Path, name: str, content: bytes, mode: int) -> Path:
    target = parent / name
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as out:
        out.write(content)
        out.flush()
        os.fchown(out.fileno(), 1000, 1000)
        os.fchmod(out.fileno(), mode)
        os.fsync(out.fileno())
    st = target.lstat()
    insist(stat.S_ISREG(st.st_mode) and st.st_uid == 1000 and st.st_gid == 1000 and
           stat.S_IMODE(st.st_mode) == mode and st.st_nlink == 1,
           "New site file owner/mode mismatch")
    return target

def run_once() -> None:
    data = read_only_preflight()
    # First mutation: mark one-use activity; any failure PRESERVES state, no retry.
    old_umask = os.umask(0o077)
    try:
        NEW_SECRETS.mkdir(mode=0o700)
        root_node(NEW_SECRETS, 0o700, True)
        write_secret(NEW_SECRETS / "DO_NOT_RETRY", (RUN + "\n").encode())
        password = secrets.token_hex(32)
        write_secret(NEW_SECRETS / "site-db.env", ("DB_PASSWORD=" + password + "\n").encode())
        print("CCPC_STAGE2B_NEW_TEST_ONLY_SITE_CREDENTIALS_CREATED", flush=True)

        docker("volume", "create", "--label", "com.ccpc.test=restore-20261112", SITES_VOLUME)
        v = inspect("volume", SITES_VOLUME)
        target_path = "/var/lib/docker/volumes/" + SITES_VOLUME + "/_data"
        insist(v.get("Driver") == "local" and v.get("Labels", {}).get("com.ccpc.test") ==
               "restore-20261112" and v.get("Mountpoint") == target_path and
               v.get("Options") in (None, {}), "New-only site volume identity invalid")
        root = Path(target_path)
        insist(root.is_dir() and not root.is_symlink() and not list(root.iterdir()) and
               root.lstat().st_uid == 0, "New-only site volume not empty/root-owned")
        insist(not os.path.islink("/var/lib/docker") and
               not os.path.islink("/var/lib/docker/volumes"),
               "Unexpected Docker volume parent symlink")
        print("CCPC_STAGE2B_NEW_EMPTY_ISOLATED_SITE_VOLUME_PASS", flush=True)

        username = "'" + SCHEMA + "'@'" + data["hostmask"] + "'"
        ddl = ("CREATE USER " + username + " IDENTIFIED BY '" + password + "';\n" +
               "GRANT ALL PRIVILEGES ON " + chr(96) + SCHEMA + chr(96) +
               ".* TO " + username + ";\n")
        # SQL secret goes exclusively over stdin to TEST DB, never argv/logs.
        db_query(ddl)
        grant_text = db_query("SHOW GRANTS FOR " + username)
        grant_lines = grant_text.splitlines()
        insist(len(grant_lines) == 2 and any(
               x.startswith("GRANT USAGE ON *.*") for x in grant_lines) and any(
               "GRANT ALL PRIVILEGES ON " + chr(96) + SCHEMA + chr(96) + ".*"
               in x for x in grant_lines) and
               not any("GRANT OPTION" in x for x in grant_lines) and
               db_query("SELECT COUNT(*) FROM mysql.global_priv WHERE User='" +
                        SCHEMA + "'") == "1",
               "New schema-scoped test account grant invalid")
        print("CCPC_STAGE2B_NEW_SCHEMA_ONLY_DATABASE_ACCOUNT_PASS", flush=True)

        config = {
            "db_name": SCHEMA, "db_password": password,
            "encryption_key": data["encryption_key"],
            "db_host": "db", "db_port": 3306,
            "maintenance_mode": 0, "pause_scheduler": 1,
            "disable_scheduler": 1, "mute_emails": 1, "developer_mode": 0,
        }
        common = {
            "db_host": "db", "db_port": 3306,
            "redis_cache": "redis://redis-cache:6379",
            "redis_queue": "redis://redis-queue:6379",
            "redis_socketio": "redis://redis-queue:6379",
            "socketio_port": 9000, "maintenance_mode": 0,
            "pause_scheduler": 1, "disable_scheduler": 1,
            "mute_emails": 1, "developer_mode": 0,
        }
        new_file(root, "common_site_config.json",
                 (json.dumps(common, sort_keys=True) + "\n").encode(), 0o600)
        new_file(root, "apps.txt", b"frappe\nerpnext\nccpcerp\n", 0o644)
        site = new_dir(root, SITE, 0o755)
        new_file(site, "site_config.json",
                 (json.dumps(config, sort_keys=True) + "\n").encode(), 0o600)
        pub = new_dir(site, "public", 0o755)
        new_dir(pub, "files", 0o755)
        private = new_dir(site, "private", 0o755)
        files = new_dir(private, "files", 0o755)
        attachment = new_file(files, data["attachment"], data["blob"], 0o600)
        insist(hash_file(attachment) == (16501, data["digest"]),
               "Restored private attachment SHA256 mismatch")
        insist({x.name for x in root.iterdir()} ==
               {"common_site_config.json", "apps.txt", SITE} and
               {x.name for x in site.iterdir()} ==
               {"site_config.json", "public", "private"} and
               not list((pub / "files").iterdir()) and
               {x.name for x in files.iterdir()} == {data["attachment"]},
               "Unexpected restored sites layout")
        confirm = json.loads((site / "site_config.json").read_bytes())
        insist(confirm["db_name"] == SCHEMA and
               confirm["db_password"] == password and
               confirm["encryption_key"] == data["encryption_key"] and
               confirm["mute_emails"] == 1 and confirm["disable_scheduler"] == 1,
               "Restored private site config verification failed")
        print("CCPC_STAGE2B_SITE_CONFIG_HISTORICAL_KEY_NEW_DB_SECRET_PASS", flush=True)
        print("CCPC_STAGE2B_PRIVATE_ATTACHMENT_SHA256_PUBLIC_EMPTY_PASS", flush=True)
        network = inspect("network", NETWORK)
        insist(set(network.get("Containers", {})) == {inspect("container", DB)["Id"]} and
               names("ps", "-a", "--format", "{{.Names}}") == PROTECTED | {DB} and
               names("ps", "--format", "{{.Names}}") == PROTECTED | {DB} and
               {n for n in names("volume", "ls", "--format", "{{.Name}}")
                if n.startswith(PREFIX)} == {DB_VOLUME, SITES_VOLUME},
               "Unexpected Docker test/production resource change after restoration")
        print("CCPC_STAGE2B_PROTECTED_ORIGINALS_AND_TEST_ISOLATION_PASS", flush=True)
        print("CCPC_NEW_A3_RESTORE_STAGE2B_ISOLATED_SITE_AND_ATTACHMENT_PASS_APP_PENDING", flush=True)
    finally:
        os.umask(old_umask)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="New A3 isolated restore Stage 2B")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    opts = parser.parse_args()
    try:
        if opts.preflight:
            read_only_preflight()
            print("CCPC_NEW_A3_RESTORE_STAGE2B_READONLY_PREFLIGHT_PASS", flush=True)
        else:
            run_once()
    except Exception:
        print("CCPC_NEW_A3_RESTORE_STAGE2B_STOP_REVIEW_REQUIRED", flush=True)
        raise SystemExit(1)
