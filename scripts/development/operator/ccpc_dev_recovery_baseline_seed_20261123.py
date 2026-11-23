#!/usr/bin/env python3
"""Stage one persistent, guest-only Ubuntu recovery baseline without launching it.

Development host gani@ccpcerpserver ONLY. Creates ONE new, private recovery
qcow2 overlay and offline cloud-init seed with a local-only random console
password. No VM is launched; no network, Docker modification, database access,
backup transfer, package installation, or production operation is performed.
Do not rerun after a STOP: inspect and preserve the one-shot output directory.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import stat
import subprocess
import sys

HOST = "ccpcerpserver"
UID = 1000
BASE = Path("/home/gani/ccpc-restore-labs")
STAGED = BASE / "ccpc-dev-restore-lab-20261123"
ORIGINAL_IMAGE = STAGED / "ubuntu-24.04-server-cloudimg-amd64.img"
ORIGINAL_OVERLAY = STAGED / "ccpc-dev-restore-lab-20261123.qcow2"
BASELINE = BASE / "ccpc-dev-recovery-baseline-20261123"
BASELINE_DISK = BASELINE / "ubuntu-recovery-baseline.qcow2"
SEED = BASELINE / "cloud-init-seed.iso"
USER_DATA = BASELINE / "user-data"
META_DATA = BASELINE / "meta-data"
PASSWORD_FILE = BASELINE / "guest-console-password.txt"
IMAGE_SHA256 = "04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94"
EXPECTED_STAGED = {"SHA256SUMS", "SHA256SUMS.gpg", ORIGINAL_IMAGE.name, ORIGINAL_OVERLAY.name}
VIRTUAL_SIZE = 60 * 1024**3


def stop(reason: str) -> None:
    raise RuntimeError(reason)


def run(argv: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        argv, input=input_text, text=True, capture_output=True, check=False
    )
    if result.returncode:
        stop("reviewed command failed: " + Path(argv[0]).name + " (stderr withheld)")
    return result.stdout.strip()


def check_owner_mode(path: Path, *, directory: bool, mode: int) -> None:
    metadata = path.lstat()
    good_type = stat.S_ISDIR(metadata.st_mode) if directory else stat.S_ISREG(metadata.st_mode)
    if not good_type or metadata.st_uid != UID or stat.S_IMODE(metadata.st_mode) != mode:
        stop("unexpected owner/type/mode for " + path.name)


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def disk_info(path: Path) -> dict:
    return json.loads(run(["qemu-img", "info", "--output=json", str(path)]))


def existing_recovery_vm() -> bool:
    for item in Path("/proc").iterdir():
        if not item.name.isdecimal():
            continue
        try:
            if item.stat().st_uid != UID:
                continue
            args = (item / "cmdline").read_bytes().decode("utf-8", "replace").split("\0")
            if args and Path(args[0]).name == "qemu-system-x86_64":
                if any(
                    "ccpc-dev-restore-lab-20261123" in a
                    or "ccpc-dev-recovery-baseline-20261123" in a
                    for a in args[1:]
                ):
                    return True
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return False


def create_private_file(path: Path, text: str) -> None:
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)
    check_owner_mode(path, directory=False, mode=0o600)


def main() -> None:
    os.umask(0o077)
    if socket.gethostname().split(".")[0] != HOST or os.getuid() != UID or os.geteuid() != UID:
        stop("wrong host/user: gani on DEVELOPMENT only, without sudo")
    for program in ("cloud-localds", "qemu-img", "openssl", "docker"):
        if shutil.which(program) is None:
            stop("missing preinstalled program: " + program)
    check_owner_mode(BASE, directory=True, mode=0o700)
    check_owner_mode(STAGED, directory=True, mode=0o700)
    check_owner_mode(ORIGINAL_IMAGE, directory=False, mode=0o400)
    check_owner_mode(ORIGINAL_OVERLAY, directory=False, mode=0o600)
    if {p.name for p in STAGED.iterdir()} != EXPECTED_STAGED:
        stop("staged cloud image folder unexpectedly changed")
    if sha256(ORIGINAL_IMAGE) != IMAGE_SHA256:
        stop("official source Ubuntu image SHA mismatch")
    base_info = disk_info(ORIGINAL_IMAGE)
    image_info = disk_info(ORIGINAL_OVERLAY)
    if base_info.get("format") != "qcow2" or "backing-filename" in base_info:
        stop("source cloud image format/backing mismatch")
    if (
        image_info.get("format") != "qcow2"
        or image_info.get("virtual-size") != VIRTUAL_SIZE
        or image_info.get("backing-filename") != str(ORIGINAL_IMAGE)
    ):
        stop("source 60GiB overlay format/backing mismatch")
    if shutil.disk_usage(BASE).free < 15 * 1024**3:
        stop("less than 15GiB disk free before recovery guest baseline setup")
    if existing_recovery_vm():
        stop("an overlapping recovery VM process is present")
    running = run([
        "docker", "inspect", "--format", "{{.State.Running}}",
        "frappe_docker_devcontainer-frappe-1",
    ])
    if running != "true":
        stop("DEVELOPMENT Frappe container unexpectedly not running")
    if BASELINE.exists() or BASELINE.is_symlink():
        stop("baseline one-shot directory already exists; preserve, do not overwrite")

    BASELINE.mkdir(mode=0o700)
    check_owner_mode(BASELINE, directory=True, mode=0o700)

    # The password never appears on GitHub or the command line; the local
    # plaintext file remains 0600 and is only for operator console login.
    console_password = secrets.token_urlsafe(24)
    password_hash = run(["openssl", "passwd", "-6", "-stdin"], input_text=console_password + "\n")
    if not password_hash.startswith("$6$"):
        stop("unexpected password-hash format")

    userdata = (
        "#cloud-config\n"
        "hostname: ccpc-recovery\n"
        "manage_etc_hosts: true\n"
        "disable_root: true\n"
        "ssh_pwauth: false\n"
        "package_update: false\n"
        "package_upgrade: false\n"
        "users:\n"
        "  - name: ccpc-restore\n"
        "    gecos: CCPC private recovery guest console\n"
        "    groups: [sudo]\n"
        "    shell: /bin/bash\n"
        "    lock_passwd: false\n"
        "    passwd: " + json.dumps(password_hash) + "\n"
        "    sudo: ['ALL=(ALL) ALL']\n"
    )
    metadata = "instance-id: ccpc-recovery-baseline-20261123\nlocal-hostname: ccpc-recovery\n"
    create_private_file(USER_DATA, userdata)
    create_private_file(META_DATA, metadata)
    create_private_file(PASSWORD_FILE, console_password + "\n")

    # Cloud-init consumes this local ISO as an offline NoCloud datasource.
    # The persistent guest disk is a NEW COW overlay; original backing chain
    # and prior boot-test evidence cannot be overwritten by this operation.
    run(["cloud-localds", str(SEED), str(USER_DATA), str(META_DATA)])
    check_owner_mode(SEED, directory=False, mode=0o600)
    run([
        "qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
        "-b", str(ORIGINAL_OVERLAY), str(BASELINE_DISK),
    ])
    check_owner_mode(BASELINE_DISK, directory=False, mode=0o600)
    disk = disk_info(BASELINE_DISK)
    if (disk.get("format") != "qcow2"
            or disk.get("virtual-size") != VIRTUAL_SIZE
            or disk.get("backing-filename") != str(ORIGINAL_OVERLAY)):
        stop("new persistent guest overlay did not match source/size")

    print("RECOVERY BASELINE DISK + OFFLINE CLOUD-INIT SEED: STAGED")
    print("PRIVATE DIRECTORY:", BASELINE)
    print("GUEST USER: ccpc-restore")
    print("GUEST PASSWORD: STORED LOCALLY IN 0600 FILE; DO NOT SHARE")
    print("SOURCE UBUNTU IMAGE/DISK AND PREVIOUS LOGS: PRESERVED")
    print("VM NOT LAUNCHED; NO GUEST NETWORK; NO BACKUP TRANSFER")
    print("NO DOCKER, DATABASE, SERVICE OR PRODUCTION MODIFICATION")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as err:
        print("STOP: " + str(err), file=sys.stderr)
        print("If a private baseline folder was created, preserve it for review; do not rerun.", file=sys.stderr)
        sys.exit(1)
