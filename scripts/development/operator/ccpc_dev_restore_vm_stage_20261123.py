#!/usr/bin/env python3
"""One-shot, non-overwriting, offline DEVELOPMENT recovery-VM staging ONLY.

Authorized scope: make private lab folder, fetch and verify an official Ubuntu
24.04 LTS cloud image using a trusted packaged keyring and signed checksum,
create a sparse 60-GiB qcow2 overlay. NEVER launch a VM, open guest networking,
read/copy ERPNext backups, modify Docker, or touch PRODUCTION.

On any STOP leave private partial files untouched; do not retry automatically.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys

HOST = "ccpcerpserver"
USER_UID = 1000
BASE = Path("/home/gani/ccpc-restore-labs")
LAB = BASE / "ccpc-dev-restore-lab-20261123"
IMAGE_ROOT = "https://cloud-images.ubuntu.com/releases/noble/release-20261017"
IMAGE_NAME = "ubuntu-24.04-server-cloudimg-amd64.img"
SIGNER_FINGERPRINT = "D2EB44626FDDC30B513D5BB71A5D6C4C7DB87C81"
KEYRING = Path("/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg")
OVERLAY = LAB / "ccpc-dev-restore-lab-20261123.qcow2"
OVERLAY_VIRTUAL_SIZE = 60 * 1024**3


def stop(reason: str) -> None:
    raise RuntimeError(reason)


def command(argv: list[str], *, label: str) -> str:
    # Do not disclose private command diagnostics or environment variables.
    p = subprocess.run(argv, text=True, capture_output=True, check=False)
    if p.returncode:
        stop(label + " failed (stderr withheld)")
    return p.stdout


def require_dir(p: Path, *, mode: int = 0o700) -> None:
    s = p.lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_uid != USER_UID or stat.S_IMODE(s.st_mode) != mode:
        stop("lab directory has unexpected type, owner or permissions")


def download(item: str, *, max_bytes: int) -> Path:
    if item not in ("SHA256SUMS", "SHA256SUMS.gpg", IMAGE_NAME):
        stop("unapproved image item")
    dest = LAB / item
    if dest.exists() or dest.is_symlink():
        stop("image staging destination already exists")
    command(
        ["curl", "--proto", "=https", "--tlsv1.2",
         "--fail", "--silent", "--show-error",
         "--max-redirs", "0", "--retry", "0",
         "--connect-timeout", "20", "--max-time", "1800",
         "--max-filesize", str(max_bytes),
         "--output", str(dest), IMAGE_ROOT + "/" + item],
        label="official Ubuntu image download",
    )
    s = dest.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid != USER_UID or not 0 < s.st_size <= max_bytes:
        stop("downloaded artifact type, owner or size invalid")
    return dest


def signed_image_hash(manifest: Path, signature: Path) -> str:
    output = command(
        ["gpgv", "--status-fd", "1", "--keyring", str(KEYRING),
         str(signature), str(manifest)],
        label="Ubuntu signed-checksum verification",
    )
    signer = "[GNUPG:] VALIDSIG " + SIGNER_FINGERPRINT
    if not any(line.startswith(signer + " ") for line in output.splitlines()):
        stop("Ubuntu image signer does not match independently pinned fingerprint")
    hashes = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, name = parts
        name = name.lstrip("*")
        if name == IMAGE_NAME and re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            hashes.append(digest.lower())
    if len(hashes) != 1:
        stop("signed manifest does not identify exactly one approved image")
    return hashes[0]


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def image_info(p: Path) -> dict:
    return json.loads(
        command(["qemu-img", "info", "--output=json", str(p)],
                label="qemu-img image inspection")
    )


def main() -> None:
    os.umask(0o077)
    if socket.gethostname().split(".")[0] != HOST or os.geteuid() != USER_UID:
        stop("unexpected host or user; DEVELOPMENT host gani required")
    if Path("/home/gani").is_symlink() or not Path("/home/gani").is_dir():
        stop("unexpected operator home")
    if Path("/home/gani").stat().st_uid != USER_UID:
        stop("unexpected operator home ownership")
    for executable in ("curl", "gpgv", "qemu-img", "docker"):
        if not shutil.which(executable):
            stop("required existing tool unavailable: " + executable)
    if not KEYRING.is_file() or KEYRING.stat().st_size == 0:
        stop("trusted packaged Ubuntu cloud-image keyring unavailable")
    if shutil.disk_usage("/home/gani").free < 20 * 1024**3:
        stop("insufficient free disk space for isolated guest staging")
    running = command(
        ["docker", "inspect", "--format", "{{.State.Running}}",
         "frappe_docker_devcontainer-frappe-1"],
        label="read-only DEVELOPMENT container check",
    ).strip()
    if running != "true":
        stop("persistent DEVELOPMENT container is not running")

    # Never overwrite an earlier attempted lab. No automatic retries.
    if BASE.exists() or BASE.is_symlink():
        require_dir(BASE)
    else:
        BASE.mkdir(mode=0o700)
        require_dir(BASE)
    if LAB.exists() or LAB.is_symlink():
        stop("restore lab already exists; preserve and inspect rather than rerunning")
    LAB.mkdir(mode=0o700)
    require_dir(LAB)

    manifest = download("SHA256SUMS", max_bytes=250_000)
    signature = download("SHA256SUMS.gpg", max_bytes=10_000)
    expected = signed_image_hash(manifest, signature)
    image = download(IMAGE_NAME, max_bytes=1_250_000_000)
    if file_sha256(image) != expected:
        stop("Ubuntu cloud image SHA256 does not match signed manifest")
    meta = image_info(image)
    if (meta.get("format") != "qcow2"
            or "backing-filename" in meta
            or not 1 * 1024**3 <= meta.get("virtual-size", 0) <= OVERLAY_VIRTUAL_SIZE):
        stop("downloaded signed image has unexpected QEMU image format/layout")
    image.chmod(0o400)

    if OVERLAY.exists() or OVERLAY.is_symlink():
        stop("new overlay disk path unexpectedly exists")
    command(
        ["qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
         "-b", str(image), str(OVERLAY), "60G"],
        label="sparse lab overlay creation",
    )
    disk = image_info(OVERLAY)
    if (disk.get("format") != "qcow2"
            or disk.get("virtual-size") != OVERLAY_VIRTUAL_SIZE
            or disk.get("backing-filename") != str(image)
            or disk.get("backing-filename-format") not in (None, "qcow2")):
        stop("sparse lab overlay identity does not match approved image")
    s = OVERLAY.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid != USER_UID or stat.S_IMODE(s.st_mode) != 0o600:
        stop("lab overlay file type or permissions invalid")

    print("OFFICIAL UBUNTU IMAGE SIGNATURE AND SHA256: PASS", flush=True)
    print("IMAGE SHA256: " + expected, flush=True)
    print("PRIVATE RESTORE LAB DIRECTORY: " + str(LAB), flush=True)
    print("SPARSE VIRTUAL DISK: 60 GiB", flush=True)
    print("DEVELOPMENT RESTORE VM STAGING: PASS", flush=True)
    print("VM NOT LAUNCHED; NO NETWORK OR BACKUP ACCESS", flush=True)
    print("NO DOCKER, SERVICE RESTART, OR PRODUCTION OPERATION", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        print("Preserve staging files; do not rerun without review.", file=sys.stderr)
        sys.exit(1)
