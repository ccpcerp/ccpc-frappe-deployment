"""Offline-testable, fail-closed publication core for the NEW CCPC NAS share.

NOT an executable backup scheduler or Frappe capture adapter. Import is inert.
A separately reviewed wrapper must authenticate the host, release, containers,
site, source-consistency policy and privilege boundary before using this core.
"""

import contextlib
import ctypes
import fcntl
import gzip
import hashlib
import json
import os
import re
import shutil
import stat
import tarfile
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

NAS_SOURCE = "//192.168.50.132/ccpcerp-prod_backups"
NAS_MOUNT = Path("/mnt/ccpcerp-prod_backups")
SITE = "ccpcerp.local"
ROLES = ("database", "site_config", "public_files", "private_files")
RUN_ID = re.compile(r"\A[0-9]{8}T[0-9]{6}Z-[0-9a-f]{16}\Z")
CHUNK = 1024 * 1024


class BackupSafetyError(RuntimeError):
    """An unsafe or unverified state; caller must stop without retry/cleanup."""


@dataclass(frozen=True)
class Artifact:
    role: str
    filename: str
    path: Path
    size: int
    sha256: str


def _regular_file(path: Path) -> os.stat_result:
    try:
        info = path.lstat()
    except OSError as exc:
        raise BackupSafetyError("Required artifact unavailable") from exc
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size <= 0:
        raise BackupSafetyError("Artifact must be a nonempty single-link regular file")
    return info


def _digest(path: Path) -> tuple[int, str]:
    sha = hashlib.sha256()
    total = 0
    # O_NOFOLLOW prevents following a replaced final-component symlink.
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise BackupSafetyError("Artifact changed type")
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            sha.update(chunk)
            total += len(chunk)
        after = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
        ) or total != before.st_size or not total:
            raise BackupSafetyError("Artifact changed while hashing")
    return total, sha.hexdigest()


def _validate_format(role: str, path: Path) -> None:
    """Inspect format without extracting archives into a running site."""
    try:
        if role == "database":
            count = 0
            with gzip.open(path, "rb") as db:
                for chunk in iter(lambda: db.read(CHUNK), b""):
                    count += len(chunk)
            if count == 0:
                raise BackupSafetyError("Empty compressed database")
        elif role == "site_config":
            if path.stat().st_size > CHUNK:
                raise BackupSafetyError("Unreasonable site config size")
            with path.open("rb") as config:
                if not isinstance(json.load(config), dict):
                    raise BackupSafetyError("Invalid site config JSON")
        else:
            member_count = 0
            with tarfile.open(path, "r:*") as archive:
                for member in archive:
                    parts = Path(member.name).parts
                    if (
                        member.name.startswith("/")
                        or ".." in parts
                        or member.issym()
                        or member.islnk()
                        or not (member.isfile() or member.isdir())
                    ):
                        raise BackupSafetyError("Unsafe tar archive entry")
                    member_count += 1
            if member_count == 0:
                raise BackupSafetyError("Empty archive")
    except (OSError, EOFError, ValueError, json.JSONDecodeError, tarfile.TarError) as exc:
        raise BackupSafetyError("Unreadable artifact format") from exc


def inspect_artifacts(source_dir: Path, filenames: dict[str, str]) -> tuple[Artifact, ...]:
    """Accept EXACTLY four explicit Frappe-generated filenames, never a glob."""
    source_dir = Path(source_dir)
    if source_dir.is_symlink() or not source_dir.is_dir():
        raise BackupSafetyError("Invalid artifact source directory")
    if set(filenames) != set(ROLES) or len(set(filenames.values())) != 4:
        raise BackupSafetyError("Expected exactly four distinct roles/files")
    result = []
    for role in ROLES:
        name = filenames[role]
        if not isinstance(name, str) or not name or name in {".", ".."} or Path(name).name != name or "\x00" in name or "\\" in name:
            raise BackupSafetyError("Unsafe artifact filename")
        if role == "database" and not name.endswith(".sql.gz"):
            raise BackupSafetyError("Unexpected database filename")
        if role == "site_config" and not name.endswith(".json"):
            raise BackupSafetyError("Unexpected config filename")
        if role.endswith("files") and not name.endswith((".tar", ".tar.gz")):
            raise BackupSafetyError("Unexpected file archive filename")
        if "-ccpcerp_local-" not in name:
            raise BackupSafetyError("Wrong Frappe site artifact")
        path = source_dir / name
        info = _regular_file(path)
        _validate_format(role, path)
        size, digest = _digest(path)
        if size != info.st_size:
            raise BackupSafetyError("Artifact size changed")
        result.append(Artifact(role, name, path, size, digest))
    return tuple(result)


def verify_cifs_mount(
    mount_dir: Path = NAS_MOUNT,
    *,
    findmnt: Callable = subprocess.run,
    is_mount: Callable = os.path.ismount,
) -> None:
    mount_dir = Path(mount_dir)
    if mount_dir.is_symlink() or not mount_dir.is_dir() or not is_mount(mount_dir):
        raise BackupSafetyError("NAS mountpoint is missing or not mounted")
    try:
        proc = findmnt(
            ["findmnt", "-rn", "-M", str(mount_dir), "-o", "SOURCE,FSTYPE,VFS-OPTIONS"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise BackupSafetyError("Cannot validate CIFS mount") from exc
    rows = proc.stdout.strip().splitlines()
    if proc.returncode != 0 or len(rows) != 1:
        raise BackupSafetyError("Cannot identify unique NAS mount")
    parts = rows[0].split()
    if len(parts) != 3 or parts[0] != NAS_SOURCE or parts[1] != "cifs":
        raise BackupSafetyError("Wrong NAS source or filesystem")
    flags = set(parts[2].split(","))
    if "rw" not in flags or "ro" in flags or not {"nosuid", "nodev", "noexec"}.issubset(flags):
        raise BackupSafetyError("NAS share flags are not sufficiently restricted")


@contextlib.contextmanager
def exclusive_lock(lock_path: Path):
    """No symlink following; concurrent run aborts immediately."""
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        s = os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or s.st_mode & 0o077:
            raise BackupSafetyError("Unsafe lock file")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BackupSafetyError("Backup already running") from exc
        yield
    finally:
        os.close(fd)


def _rename_noreplace(source: Path, destination: Path) -> None:
    """Linux atomic no-clobber rename; unsupported CIFS must fail closed."""
    libc = ctypes.CDLL(None, use_errno=True)
    method = getattr(libc, "renameat2", None)
    if method is None:
        raise BackupSafetyError("Atomic no-replace rename is unsupported")
    method.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    method.restype = ctypes.c_int
    rc = method(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    if rc != 0:
        reason = ctypes.get_errno()
        raise BackupSafetyError(f"Atomic publication rejected (errno {reason})")


def _create_file(path: Path, content: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def publish_verified_set(
    source_dir: Path,
    filenames: dict[str, str],
    run_id: str,
    mount_dir: Path,
    lock_path: Path,
    *,
    probe: Callable[[Path], None] = verify_cifs_mount,
) -> Path:
    """Publish one prior-approved, consistent set; NO mount/bench/retention.

    The caller supplies the already-created four artifact filenames, after
    independently establishing site identity and DB/files consistency.
    On failure any partial directory is deliberately preserved for review.
    """
    if not RUN_ID.fullmatch(run_id):
        raise BackupSafetyError("Unsafe run identifier")
    with exclusive_lock(Path(lock_path)):
        artifacts = inspect_artifacts(Path(source_dir), filenames)
        mount_dir = Path(mount_dir)
        probe(mount_dir)
        stage = mount_dir / f".partial-{run_id}"
        final = mount_dir / run_id
        if os.path.lexists(stage) or os.path.lexists(final):
            raise BackupSafetyError("Run directory already exists")
        stage.mkdir(mode=0o700)
        entries = []
        for artifact in artifacts:
            probe(mount_dir)
            if _digest(artifact.path) != (artifact.size, artifact.sha256):
                raise BackupSafetyError("Source artifact changed")
            target = stage / artifact.filename
            source_fd = os.open(artifact.path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(source_fd, "rb") as src:
                source_before = os.fstat(src.fileno())
                if not stat.S_ISREG(source_before.st_mode):
                    raise BackupSafetyError("Source file replaced")
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, "wb") as dst:
                    shutil.copyfileobj(src, dst, CHUNK)
                    dst.flush()
                    os.fsync(dst.fileno())
                source_after = os.fstat(src.fileno())
                if (source_before.st_dev, source_before.st_ino, source_before.st_size, source_before.st_mtime_ns) != (
                    source_after.st_dev, source_after.st_ino, source_after.st_size, source_after.st_mtime_ns
                ):
                    raise BackupSafetyError("Source mutated during copy")
            if _digest(target) != (artifact.size, artifact.sha256):
                raise BackupSafetyError("NAS checksum mismatch")
            entries.append({"role": artifact.role, "filename": artifact.filename, "size": artifact.size, "sha256": artifact.sha256})
        manifest = {"schema": 1, "site": SITE, "run_id": run_id, "artifacts": entries}
        _create_file(stage / "manifest.json", (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode())
        probe(mount_dir)
        for artifact in artifacts:
            if _digest(stage / artifact.filename) != (artifact.size, artifact.sha256):
                raise BackupSafetyError("NAS checksum mismatch before publication")
        if os.path.lexists(final):
            raise BackupSafetyError("Published run already exists")
        _rename_noreplace(stage, final)
        probe(mount_dir)
        _create_file(final / "COMPLETED", (run_id + "\n").encode())
        probe(mount_dir)
        if not (final / "COMPLETED").is_file():
            raise BackupSafetyError("Completion marker absent")
        return final


if __name__ == "__main__":
    raise SystemExit("NOT ENABLED: offline library only; no backup/mount/scheduler CLI")
