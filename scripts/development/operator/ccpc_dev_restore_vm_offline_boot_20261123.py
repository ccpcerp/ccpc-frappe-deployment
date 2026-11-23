#!/usr/bin/env python3
"""Single bounded, ephemeral, OFFLINE QEMU boot smoke test for DEV recovery lab.

Owner-authorized only for the staged, checksum-pinned Ubuntu 24.04 image and
60-GiB qcow2 overlay. No network, VM autostart, backup access or persistent
guest writes. Does not claim ERPNext restore success or even guest boot PASS
without operator console review. Execute as gani under 'sg kvm'.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys

HOST = "ccpcerpserver"
USER_UID = 1000
BASE = Path("/home/gani/ccpc-restore-labs")
LAB = BASE / "ccpc-dev-restore-lab-20261123"
IMAGE = LAB / "ubuntu-24.04-server-cloudimg-amd64.img"
DISK = LAB / "ccpc-dev-restore-lab-20261123.qcow2"
IMAGE_SHA256 = "04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94"
VIRTUAL_SIZE = 60 * 1024 ** 3
RUNTIME_SECONDS = 180
PERMITTED_FILES = {
    "SHA256SUMS",
    "SHA256SUMS.gpg",
    IMAGE.name,
    DISK.name,
}


def stop(message: str) -> None:
    raise RuntimeError(message)


def run_readonly(argv: list[str], name: str) -> str:
    p = subprocess.run(argv, text=True, capture_output=True, check=False)
    if p.returncode != 0:
        stop(name + " failed; private subprocess stderr withheld")
    return p.stdout.strip()


def strict_path(p: Path, *, directory: bool = False, mode: int) -> None:
    s = p.lstat()  # reject symlinks, unusual files, and wrong owner
    desired_type = stat.S_ISDIR if directory else stat.S_ISREG
    if not desired_type(s.st_mode) or s.st_uid != USER_UID or stat.S_IMODE(s.st_mode) != mode:
        stop("unexpected file/directory type, owner or permissions")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def qemu_info(p: Path) -> dict:
    return json.loads(
        run_readonly(["qemu-img", "info", "--output=json", str(p)], "QEMU disk info")
    )


def preflight() -> None:
    if socket.gethostname().split(".")[0] != HOST or os.getuid() != USER_UID:
        stop("incorrect host/user for DEVELOPMENT-only offline boot")
    if os.geteuid() != USER_UID:
        stop("do not run this script with sudo")
    kvm_group = __import__("grp").getgrnam("kvm").gr_gid
    if os.getegid() != kvm_group and kvm_group not in os.getgroups():
        stop("current process lacks effective kvm group; use reviewed sg command")
    if not os.access("/dev/kvm", os.R_OK | os.W_OK):
        stop("hardware /dev/kvm is not available read/write")
    for binary in ("qemu-system-x86_64", "qemu-img", "timeout", "docker"):
        if not shutil.which(binary):
            stop("required command missing: " + binary)
    strict_path(BASE, directory=True, mode=0o700)
    strict_path(LAB, directory=True, mode=0o700)
    strict_path(IMAGE, mode=0o400)
    strict_path(DISK, mode=0o600)
    if {p.name for p in LAB.iterdir()} != PERMITTED_FILES:
        stop("unexpected files in protected staging folder")
    if sha256_file(IMAGE) != IMAGE_SHA256:
        stop("official Ubuntu image SHA-256 changed")
    backing = qemu_info(IMAGE)
    overlay = qemu_info(DISK)
    if backing.get("format") != "qcow2" or "backing-filename" in backing:
        stop("original cloud image no longer has expected backing layout")
    if (
        overlay.get("format") != "qcow2"
        or overlay.get("virtual-size") != VIRTUAL_SIZE
        or overlay.get("backing-filename") != str(IMAGE)
    ):
        stop("lab overlay is not the exact staged 60-GiB disk")
    if shutil.disk_usage("/tmp").free < 1 * 1024**3:
        stop("temporary snapshot workspace has less than 1 GiB free")
    if shutil.disk_usage(LAB).free < 3 * 1024**3:
        stop("insufficient free storage margin on lab filesystem")
    dev = run_readonly(
        ["docker", "inspect", "--format", "{{.State.Running}}",
         "frappe_docker_devcontainer-frappe-1"],
        "DEVELOPMENT container state",
    )
    if dev != "true":
        stop("protected persistent DEVELOPMENT container is not running")


def main() -> None:
    preflight()
    print("OFFLINE VM BOOT SAFETY PREFLIGHT: PASS", flush=True)
    print("BOUNDED BOOT WINDOW: 180 SECONDS", flush=True)
    print("NO NIC, NO GUEST NETWORK, NO SHARED HOST PATHS", flush=True)
    print("GUEST WRITES TEMPORARY; STAGED QCOW2 NOT COMMITTED", flush=True)
    print("--- Guest serial console begins ---", flush=True)

    # -nodefaults/-no-user-config prevent hidden auto-created devices.
    # -nic none is required even if -nodefaults is used.
    # -snapshot stores writes to temporary files; monitor is disabled so the
    # guest cannot trigger an operator monitor 'commit' action.
    # QEMU is foreground, never daemonized or autostarted.
    argv = [
        "timeout", "--signal=TERM", "--kill-after=10s", str(RUNTIME_SECONDS) + "s",
        "qemu-system-x86_64",
        "-name", "ccpc-dev-restore-lab-20261123",
        "-no-user-config",
        "-nodefaults",
        "-machine", "q35,accel=kvm",
        "-cpu", "host",
        "-smp", "4",
        "-m", "8192",
        "-drive", "file=" + str(DISK) + ",format=qcow2,if=virtio",
        "-boot", "order=c,menu=off",
        "-nic", "none",
        "-display", "none",
        "-serial", "stdio",
        "-monitor", "none",
        "-snapshot",
        "-no-reboot",
    ]
    p = subprocess.run(argv, check=False)
    print("--- Guest serial console ends ---", flush=True)
    if p.returncode == 124:
        print("BOUNDED OFFLINE BOOT WINDOW: ENDED AT TIME LIMIT", flush=True)
    elif p.returncode == 0:
        print("BOUNDED OFFLINE BOOT WINDOW: QEMU EXITED NORMALLY", flush=True)
    elif p.returncode in (130, 143):
        print("BOUNDED OFFLINE BOOT WINDOW: INTERRUPTED BY OPERATOR", flush=True)
    else:
        stop("QEMU returned non-success exit code " + str(p.returncode))
    print("VM LAUNCH ATTEMPT COMPLETED; BOOT SUCCESS REQUIRES CONSOLE REVIEW", flush=True)
    print("NO BACKUP RESTORE, NETWORK ACCESS OR PRODUCTION OPERATION", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        print("Do not retry before reviewing the failure and guest state.", file=sys.stderr)
        sys.exit(1)
