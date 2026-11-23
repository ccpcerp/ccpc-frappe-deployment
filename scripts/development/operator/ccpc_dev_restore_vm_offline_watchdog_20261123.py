#!/usr/bin/env python3
"""REVIEW ONLY: safe, detached, 180s offline smoke-test for Nov23 CCPC DEV VM.

Single use; separate approval is required before operator executes.
No NIC, backing-disk writes, guest secrets, ERPNext backup, or VM autostart.
The supervisor and its GNU timeout child are detached from SSH job control.
"""
from __future__ import annotations

import grp
import hashlib
import json
import os
import signal
from pathlib import Path
import selectors
import shutil
import socket
import stat
import subprocess
import sys
import time

HOST = "ccpcerpserver"
UID = 1000
BASE = Path("/home/gani/ccpc-restore-labs")
LAB = BASE / "ccpc-dev-restore-lab-20261123"
IMAGE = LAB / "ubuntu-24.04-server-cloudimg-amd64.img"
DISK = LAB / "ccpc-dev-restore-lab-20261123.qcow2"
RUN = BASE / "ccpc-dev-restore-offline-test2-20261123"
LOG = RUN / "serial-console.log"
STATUS = RUN / "status.json"
SUPERVISOR_LOG = RUN / "supervisor.log"
EXPECTED_IMAGE_SHA = "04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94"
EXPECTED_FILES = {"SHA256SUMS", "SHA256SUMS.gpg", IMAGE.name, DISK.name}
LIMIT_SECONDS = 180
KILL_AFTER_SECONDS = 10
LOG_LIMIT_BYTES = 2 * 1024 * 1024
VIRTUAL_SIZE = 60 * 1024**3


def stop(message: str) -> None:
    raise RuntimeError(message)


def file_metadata(p: Path, is_dir: bool, perm: int) -> None:
    s = p.lstat()  # don't follow a symlink
    if ((not stat.S_ISDIR(s.st_mode) if is_dir else not stat.S_ISREG(s.st_mode))
            or s.st_uid != UID or stat.S_IMODE(s.st_mode) != perm):
        stop(f"unexpected lab file/directory identity: {p.name}")


def read_only(argv: list[str], purpose: str) -> str:
    p = subprocess.run(argv, capture_output=True, text=True, check=False)
    if p.returncode:
        stop(purpose + " failed (private stderr withheld)")
    return p.stdout.strip()


def info(path: Path) -> dict:
    return json.loads(read_only(["qemu-img", "info", "--output=json", str(path)], "disk inspection"))


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def has_active_same_lab() -> bool:
    """Fail closed if any current process appears to operate this lab's VM."""
    for p in Path("/proc").iterdir():
        if not p.name.isdecimal():
            continue
        try:
            if p.stat().st_uid != UID:
                continue
            raw = (p / "cmdline").read_bytes()
            args = [x.decode("utf-8", "replace") for x in raw.split(b"\0") if x]
            if (args and Path(args[0]).name in ("qemu-system-x86_64", "timeout")
                    and ("ccpc-dev-restore-lab-20261123" in args
                         or any(str(DISK) in a for a in args))):
                return True
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return False


def preflight() -> None:
    if socket.gethostname().split(".")[0] != HOST or os.getuid() != UID or os.geteuid() != UID:
        stop("unexpected host/user; use gani non-root on DEVELOPMENT host")
    kvm_gid = grp.getgrnam("kvm").gr_gid
    if kvm_gid not in (os.getegid(), *os.getgroups()):
        stop("effective kvm group missing; use sg kvm")
    if not os.access("/dev/kvm", os.R_OK | os.W_OK):
        stop("KVM device inaccessible to this process")
    for command in ("qemu-img", "qemu-system-x86_64", "timeout", "docker"):
        if not shutil.which(command):
            stop("required preinstalled command missing: " + command)
    file_metadata(BASE, True, 0o700)
    file_metadata(LAB, True, 0o700)
    file_metadata(IMAGE, False, 0o400)
    file_metadata(DISK, False, 0o600)
    if {p.name for p in LAB.iterdir()} != EXPECTED_FILES:
        stop("private staging lab contents unexpectedly changed")
    if digest(IMAGE) != EXPECTED_IMAGE_SHA:
        stop("official Ubuntu image SHA-256 mismatch")
    original = info(IMAGE)
    virtual = info(DISK)
    if original.get("format") != "qcow2" or "backing-filename" in original:
        stop("official cloud image is not the expected standalone qcow2")
    if (virtual.get("format") != "qcow2"
            or virtual.get("virtual-size") != VIRTUAL_SIZE
            or virtual.get("backing-filename") != str(IMAGE)):
        stop("private recovery lab overlay identity mismatch")
    if shutil.disk_usage("/tmp").free < 3 * 1024**3:
        stop("less than 3 GiB temporary snapshot space")
    if shutil.disk_usage(LAB).free < 4 * 1024**3:
        stop("less than 4 GiB recovery lab free space")
    memory_kib = 0
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            memory_kib = int(line.split()[1])
    if memory_kib < 11 * 1024**2:
        stop("less than 11 GiB host available RAM")
    container = read_only(
        ["docker", "inspect", "--format", "{{.State.Running}}",
         "frappe_docker_devcontainer-frappe-1"],
        "DEVELOPMENT running-container check",
    )
    if container != "true":
        stop("DEVELOPMENT Frappe container is not running")
    if has_active_same_lab():
        stop("another process appears to use the recovery VM; do not overlap")
    if RUN.exists() or RUN.is_symlink():
        stop("one-shot test folder already exists; preserve existing result")


def exclusive_file(path: Path):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    return os.fdopen(fd, "wb", buffering=0)


def qemu_argv() -> list[str]:
    return [
        "qemu-system-x86_64", "-name", "ccpc-dev-restore-lab-20261123",
        "-no-user-config", "-nodefaults", "-machine", "q35,accel=kvm",
        "-cpu", "host", "-smp", "4", "-m", "8192",
        "-drive", f"file={DISK},format=qcow2,if=virtio",
        "-boot", "order=c,menu=off", "-nic", "none",
        "-display", "none", "-serial", "stdio", "-monitor", "none",
        "-snapshot", "-no-reboot",
    ]


def supervisor() -> int:
    """Detached controller: independent of the interactive SSH/VS Code shell."""
    os.umask(0o077)
    file_metadata(RUN, True, 0o700)
    # Reverify identity and no overlapping VM before start; don't repeat
    # one-shot RUN existence check because the launcher created it.
    file_metadata(BASE, True, 0o700)
    file_metadata(LAB, True, 0o700)
    file_metadata(IMAGE, False, 0o400)
    file_metadata(DISK, False, 0o600)
    if os.getuid() != UID or os.geteuid() != UID or not os.access("/dev/kvm", os.R_OK | os.W_OK):
        stop("watchdog identity/access mismatch")
    if has_active_same_lab():
        stop("same-lab VM already active at supervisor launch")

    serial_log = exclusive_file(LOG)
    state = "UNKNOWN"
    code = None
    observed_bytes = 0
    clipped = False
    process = None
    selector = None
    try:
        # GNU timeout is a second independent watchdog in a session with no
        # controlling terminal, so terminal Ctrl+Z cannot suspend it.
        args = ["timeout", "--signal=TERM", "--kill-after=10s", "180s"] + qemu_argv()
        process = subprocess.Popen(
            args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, start_new_session=True,
            close_fds=True, cwd=str(RUN),
        )
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        # Supervisor also has an independent deadline for status collection.
        deadline = time.monotonic() + LIMIT_SECONDS + KILL_AFTER_SECONDS + 15
        while True:
            if time.monotonic() > deadline:
                # This catches unexpected timeout failure; the detached
                # timeout session/process group was created only by us.
                # Kill the WHOLE group so a surviving QEMU isn't orphaned.
                if process.poll() is None:
                    if os.getpgid(process.pid) != process.pid:
                        stop("timeout group identity changed; stop for review")
                    os.killpg(process.pid, signal.SIGKILL)
                state = "SUPERVISOR_HARD_DEADLINE"
                break
            events = selector.select(timeout=0.4)
            for key, _ in events:
                data = os.read(key.fd, 65536)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                if observed_bytes < LOG_LIMIT_BYTES:
                    serial_log.write(data[:LOG_LIMIT_BYTES - observed_bytes])
                observed_bytes += len(data)
                if observed_bytes > LOG_LIMIT_BYTES:
                    clipped = True
            if process.poll() is not None and not selector.get_map():
                break
        try:
            code = process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            if os.getpgid(process.pid) != process.pid:
                stop("timeout group identity changed; stop for review")
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait(timeout=5)
        if state == "UNKNOWN":
            if code == 124:
                state = "TIMEOUT_WINDOW_ELAPSED"
            elif code == 0:
                state = "QEMU_EXITED_ZERO"
            else:
                state = "QEMU_EXIT_NONZERO"
    finally:
        # If a logging/selector/inspection failure occurs while the timeout
        # is still alive, do not leave a guest QEMU behind accidentally.
        if process is not None and process.poll() is None:
            try:
                if os.getpgid(process.pid) == process.pid:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
        if selector is not None:
            selector.close()
        serial_log.close()
        result = {
            "test": "ccpc-dev-restore-offline-test2-20261123",
            "state": state,
            "timeout_returncode": code,
            "console_bytes_observed": observed_bytes,
            "console_truncated_at_2mib": clipped,
            "guest_network": "none",
            "snapshot": True,
            "guest_boot_confirmed": False,
            "backup_restore_executed": False,
        }
        with exclusive_file(STATUS) as file:
            file.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    return 0


def launcher() -> None:
    os.umask(0o077)
    preflight()
    # exclusive one-shot directory: no automatic retries or overwritten logs.
    RUN.mkdir(mode=0o700)
    file_metadata(RUN, True, 0o700)
    with exclusive_file(SUPERVISOR_LOG) as out:
        p = subprocess.Popen(
            [sys.executable, "-B", str(Path(__file__).resolve()), "--supervise"],
            stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
            close_fds=True, start_new_session=True,
            cwd=str(RUN),
        )
    print("DETACHED OFFLINE VM WATCHDOG: LAUNCH REQUESTED")
    print("SUPERVISOR PID:", p.pid)
    print("PRIVATE SERIAL LOG:", LOG)
    print("PRIVATE STATUS FILE (AFTER TEST):", STATUS)
    print("WINDOW: 180s + 10s TERM/KILL GRACE; NOT BOOT PASS")
    print("NO NIC / NO HOST SHARES / GUEST WRITES TEMPORARY")
    print("DO NOT RELAUNCH OR DELETE ONE-SHOT FILES")


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            launcher()
        elif len(sys.argv) == 2 and sys.argv[1] == "--supervise":
            sys.exit(supervisor())
        else:
            stop("unsupported mode")
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError) as err:
        print("STOP: " + str(err), file=sys.stderr, flush=True)
        print("Do not retry; preserve private lab and one-shot logs.", file=sys.stderr, flush=True)
        sys.exit(1)
