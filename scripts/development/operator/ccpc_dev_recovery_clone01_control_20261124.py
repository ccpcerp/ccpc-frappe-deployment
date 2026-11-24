#!/usr/bin/env python3
"""Launch ONLY disposable recovery clone 01, never the provisioned baseline.

Normal host gani, no sudo; source baseline and backing chain are immutable inputs.
Independent one-shot runtime, serial console, guest-native poweroff; no NIC,
host shares, secrets ingestion, production access, or restored backup yet.
Modes: --start / --status / --console. Never use old baseline --start controller.
"""
from __future__ import annotations

import grp
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import socket
import stat
import subprocess
import sys
import termios
import time
import tty

HOST = "ccpcerpserver"
UID = 1000
BASE = Path("/home/gani/ccpc-restore-labs")
STAGE = BASE / "ccpc-dev-restore-lab-20261123"
ORIGINAL_IMAGE = STAGE / "ubuntu-24.04-server-cloudimg-amd64.img"
ORIGINAL_DISK = STAGE / "ccpc-dev-restore-lab-20261123.qcow2"
LAB = BASE / "ccpc-dev-recovery-baseline-20261123"
BASELINE_DISK = LAB / "ubuntu-recovery-baseline.qcow2"
CLONE = BASE / "ccpc-dev-recovery-clone-01-20261124"
DISK = CLONE / "recovery-clone.qcow2"
SEED = LAB / "cloud-init-seed.iso"
PASSWORD = LAB / "guest-console-password.txt"
OLD_RUNTIME = BASE / "ccpc-dev-recovery-runtime-20261123"
MEDIA_RUNTIME = BASE / "ccpc-dev-recovery-media-runtime-20261123"
RUNTIME = BASE / "ccpc-dev-recovery-clone-01-runtime-20261124"
MEDIA_DIR = BASE / "ccpc-recovery-offline-media-20261123"
MEDIA = MEDIA_DIR / "ccpc-recovery-offline.iso"
PID_FILE = RUNTIME / "vm.pid"
SERIAL = RUNTIME / "serial.sock"
QMP = RUNTIME / "qmp.sock"
STDERR_LOG = RUNTIME / "qemu-output.log"
VM_NAME = "ccpc-dev-recovery-clone-01-20261124"
IMAGE_SHA = "04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94"
MEDIA_SHA = "32ac13073a0383a75c6bc0df7b93a8b7995750cfa0406e05133084aad9eb84b4"
MEDIA_BYTES = 1127800832
VIRTUAL_SIZE = 60 * 1024**3


def stop(reason: str) -> None:
    raise RuntimeError(reason)


def check_identity() -> None:
    if socket.gethostname().split(".")[0] != HOST or os.getuid() != UID or os.geteuid() != UID:
        stop("reviewed DEVELOPMENT host normal gani user only, never sudo")


def correct_file(path: Path, directory: bool, mode: int) -> None:
    metadata = path.lstat()
    kind = stat.S_ISDIR(metadata.st_mode) if directory else stat.S_ISREG(metadata.st_mode)
    if not kind or metadata.st_uid != UID or stat.S_IMODE(metadata.st_mode) != mode:
        stop("identity, type, or permissions mismatch for " + path.name)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read_only(argv: list[str]) -> str:
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode:
        stop("read-only subprocess failed: " + Path(argv[0]).name)
    return result.stdout.strip()


def disk_info(path: Path) -> dict:
    return json.loads(read_only(["qemu-img", "info", "--output=json", str(path)]))


def is_matching_qemu(pid: int) -> bool:
    process = Path(f"/proc/{pid}")
    try:
        argv = [a.decode("utf-8", "replace") for a in
                (process / "cmdline").read_bytes().split(b"\0") if a]
        return (process.stat().st_uid == UID and argv and
                Path(argv[0]).name == "qemu-system-x86_64" and
                VM_NAME in argv and any(str(DISK) in x for x in argv))
    except (OSError, FileNotFoundError, PermissionError, ProcessLookupError):
        return False


def existing_lab_qemu() -> bool:
    for item in Path("/proc").iterdir():
        if not item.name.isdecimal():
            continue
        try:
            if is_matching_qemu(int(item.name)):
                return True
        except (OSError, ValueError):
            continue
    return False


def preflight_start() -> None:
    check_identity()
    if grp.getgrnam("kvm").gr_gid not in (os.getegid(), *os.getgroups()):
        stop("KVM group not active: use sg kvm for clone --start")
    if not os.access("/dev/kvm", os.R_OK | os.W_OK):
        stop("no read/write access to /dev/kvm")
    for program in ("qemu-img", "qemu-system-x86_64", "docker"):
        if not shutil.which(program):
            stop("missing required host tool " + program)
    for folder in (BASE, STAGE, LAB, OLD_RUNTIME, MEDIA_DIR, CLONE):
        correct_file(folder, True, 0o700)
    for file, mode in ((ORIGINAL_IMAGE, 0o400), (ORIGINAL_DISK, 0o600),
                       (BASELINE_DISK, 0o600), (DISK, 0o600),
                       (SEED, 0o600), (PASSWORD, 0o600), (MEDIA, 0o600)):
        correct_file(file, False, mode)
    if MEDIA.stat().st_size != MEDIA_BYTES or digest(MEDIA) != MEDIA_SHA:
        stop("read-only ISO byte count/SHA256 mismatch")
    if digest(ORIGINAL_IMAGE) != IMAGE_SHA:
        stop("original signed Ubuntu image hash mismatch")
    stage_info = disk_info(ORIGINAL_DISK)
    baseline_info = disk_info(BASELINE_DISK)
    clone_info = disk_info(DISK)
    if (stage_info.get("format") != "qcow2"
            or stage_info.get("virtual-size") != VIRTUAL_SIZE
            or stage_info.get("backing-filename") != str(ORIGINAL_IMAGE)
            or stage_info.get("corrupt") is not False
            or baseline_info.get("format") != "qcow2"
            or baseline_info.get("virtual-size") != VIRTUAL_SIZE
            or baseline_info.get("backing-filename") != str(ORIGINAL_DISK)
            or baseline_info.get("corrupt") is not False
            or clone_info.get("format") != "qcow2"
            or clone_info.get("virtual-size") != VIRTUAL_SIZE
            or clone_info.get("backing-filename") != str(BASELINE_DISK)
            or clone_info.get("corrupt") is not False):
        stop("clone/baseline/Ubuntu QCOW2 backing chain mismatch or corruption flag")
    # No QEMU may write the baseline while the immutable clone is in use.
    for item in Path("/proc").iterdir():
        if not item.name.isdecimal():
            continue
        try:
            pid = int(item.name)
            if (item.stat().st_uid != UID):
                continue
            parts = [v.decode("utf-8", "replace") for v in
                     (item / "cmdline").read_bytes().split(b"\\0") if v]
            if (parts and Path(parts[0]).name == "qemu-system-x86_64"
                    and any(str(path) in argument for argument in parts for
                            path in (BASELINE_DISK, ORIGINAL_DISK, DISK))):
                stop("baseline, old guest or clone QEMU already active; do not double-open")
        except (OSError, ProcessLookupError, PermissionError):
            continue
    if RUNTIME.exists() or RUNTIME.is_symlink():
        stop("clone one-shot runtime exists; inspect without deleting or rerunning")
    if shutil.disk_usage(BASE).free < 12 * 1024**3:
        stop("less than 12GiB free disk")
    available_kib = next((int(line.split()[1])
                         for line in Path("/proc/meminfo").read_text().splitlines()
                         if line.startswith("MemAvailable:")), 0)
    if available_kib < 11 * 1024**2:
        stop("less than 11GiB available RAM")
    if read_only(["docker", "inspect", "--format", "{{.State.Running}}",
                  "frappe_docker_devcontainer-frappe-1"]) != "true":
        stop("existing DEVELOPMENT Frappe container not running")
    # Older baseline guest controllers may leave historical PID files; never
    # reuse their runtime paths or shut down their existing processes.
    for prior in (OLD_RUNTIME, MEDIA_RUNTIME):
        old_pid_file = prior / "vm.pid"
        if old_pid_file.exists():
            correct_file(old_pid_file, False, 0o600)
            try:
                old_pid = int(old_pid_file.read_text().strip())
            except ValueError:
                stop("historical guest PID unreadable")
            if old_pid > 1 and Path(f"/proc/{old_pid}").exists():
                prior_argv = (Path(f"/proc/{old_pid}") / "cmdline").read_bytes()
                if b"qemu-system-x86_64" in prior_argv:
                    stop("historical guest controller still has active QEMU; STOP")


def qemu_args() -> list[str]:
    return [
        "qemu-system-x86_64",
        "-name", VM_NAME,
        "-no-user-config", "-nodefaults",
        "-machine", "q35,accel=kvm", "-cpu", "host",
        "-smp", "4", "-m", "8192",
        "-drive", f"file={DISK},format=qcow2,if=virtio",
        "-drive", f"file={SEED},format=raw,if=virtio,readonly=on",
        "-drive", f"file={MEDIA},format=raw,if=virtio,readonly=on",
        "-boot", "order=c,menu=off", "-nic", "none",
        "-display", "none",
        "-serial", f"unix:{SERIAL},server=on,wait=off",
        "-qmp", f"unix:{QMP},server=on,wait=off",
        "-monitor", "none", "-no-reboot",
    ]


def start() -> None:
    os.umask(0o077)
    preflight_start()
    RUNTIME.mkdir(mode=0o700)
    correct_file(RUNTIME, True, 0o700)
    descriptor = os.open(STDERR_LOG, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb", buffering=0) as log:
        proc = subprocess.Popen(qemu_args(), cwd=str(RUNTIME),
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True, close_fds=True)
    with os.fdopen(os.open(PID_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                           0o600), "w") as output:
        output.write(str(proc.pid) + "\n")
    for _ in range(60):
        if proc.poll() is not None:
            stop("QEMU exited at media guest startup; preserve private qemu-output.log")
        if SERIAL.is_socket() and QMP.is_socket():
            break
        time.sleep(0.1)
    else:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        stop("new QEMU did not create control sockets; only new process was terminated")
    print("DISPOSABLE CLONE 01: START REQUESTED; QEMU PID:", proc.pid)
    print("ISO SHA256 VERIFIED:", MEDIA_SHA)
    print("SOURCE BASELINE: READ-ONLY BACKING; WRITES ONLY TO:", DISK)
    print("OFFLINE MEDIA AND CLOUD-INIT SEED: READ-ONLY VIRTIO DRIVES")
    print("NETWORK: NONE; LIVE DEVELOPMENT / PRODUCTION: UNTOUCHED")
    print("NO CONFIDENTIAL BACKUP TRANSFER OR RESTORE")
    print("GUEST LOGIN: ccpc-restore (original private host-only password)")
    print("GUEST CONSOLE: python3 -B <this-script> --console")
    print("GUEST SHUTDOWN: sudo systemctl poweroff INSIDE CLONE, then host --status")


def guest_pid() -> int:
    correct_file(RUNTIME, True, 0o700)
    correct_file(PID_FILE, False, 0o600)
    pid = int(PID_FILE.read_text().strip())
    if not (1 < pid < 2**22):
        stop("invalid new runtime PID file")
    return pid


def status() -> None:
    check_identity()
    pid = guest_pid()
    if not is_matching_qemu(pid):
        print("DISPOSABLE CLONE 01: NOT RUNNING; REVIEW WITHOUT RERUNNING")
        return
    argv = [v.decode("utf-8", "replace") for v in
            Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0") if v]
    if not any(str(MEDIA) in v for v in argv):
        stop("running guest does not reference the reviewed ISO")
    if "-nic" not in argv or argv[argv.index("-nic") + 1] != "none":
        stop("running guest NIC is not disabled")
    print("DISPOSABLE CLONE 01: RUNNING; PID:", pid)
    print("QEMU NETWORK: NONE; ISO: READ-ONLY (launch argument)")
    print("NO HOST SHARES / PORT FORWARDS")


def console() -> None:
    status()
    if not SERIAL.is_socket() or not sys.stdin.isatty():
        stop("serial socket unavailable or no interactive terminal")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(str(SERIAL))
    sock.setblocking(False)
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    tty.setraw(fd)
    print("\r\nGUEST CONSOLE ATTACHED. Ctrl+] to detach.\r\n", end="", flush=True)
    selector = selectors.DefaultSelector()
    selector.register(sock, selectors.EVENT_READ)
    selector.register(fd, selectors.EVENT_READ)
    try:
        while True:
            for key, _ in selector.select():
                if key.fileobj == sock:
                    data = sock.recv(16384)
                    if not data:
                        return
                    os.write(sys.stdout.fileno(), data)
                else:
                    data = os.read(fd, 1024)
                    if not data:
                        return
                    if b"\x1d" in data:
                        before = data.split(b"\x1d", 1)[0]
                        if before:
                            sock.sendall(before)
                        return
                    sock.sendall(data)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)
        sock.close()
        print("\nCONSOLE DETACHED; CHECK --status FOR VM STATE", flush=True)


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            stop("usage: --start | --status | --console")
        if sys.argv[1] == "--start":
            start()
        elif sys.argv[1] == "--status":
            status()
        elif sys.argv[1] == "--console":
            console()
         else:
            stop("unsupported control mode")
    except (OSError, RuntimeError, ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
        print("STOP: " + str(exc), file=sys.stderr, flush=True)
        sys.exit(1)
