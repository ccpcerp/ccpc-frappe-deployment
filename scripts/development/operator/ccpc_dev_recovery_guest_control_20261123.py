#!/usr/bin/env python3
"""Control ONLY the isolated Nov23 CCPC DEVELOPMENT recovery baseline guest.

Commands: --start (once), --status, --console, --shutdown.
No NIC, no host shares, no backup transfer, no host Docker or MariaDB changes.
Unlike the earlier ephemeral tests, --start PERSISTS writes in the separate
guest-only baseline qcow2. Never use this script with sudo or on PRODUCTION.
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
DISK = LAB / "ubuntu-recovery-baseline.qcow2"
SEED = LAB / "cloud-init-seed.iso"
PRIVATE_PASSWORD = LAB / "guest-console-password.txt"
RUNTIME = BASE / "ccpc-dev-recovery-runtime-20261123"
PID_FILE = RUNTIME / "vm.pid"
SERIAL = RUNTIME / "serial.sock"
QMP = RUNTIME / "qmp.sock"
STDERR_LOG = RUNTIME / "qemu-output.log"
VM_NAME = "ccpc-dev-recovery-baseline-20261123"
IMAGE_SHA = "04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94"
VIRTUAL_SIZE = 60 * 1024**3


def stop(reason: str) -> None:
    raise RuntimeError(reason)


def correct_file(path: Path, directory: bool, mode: int) -> None:
    md = path.lstat()
    kind = stat.S_ISDIR(md.st_mode) if directory else stat.S_ISREG(md.st_mode)
    if not kind or md.st_uid != UID or stat.S_IMODE(md.st_mode) != mode:
        stop("file identity, type or permissions mismatch for: " + path.name)


def read_only(argv: list[str]) -> str:
    result = subprocess.run(argv, text=True, capture_output=True, check=False)
    if result.returncode:
        stop("read-only command failed: " + Path(argv[0]).name)
    return result.stdout.strip()


def disk_info(path: Path) -> dict:
    return json.loads(read_only(["qemu-img", "info", "--output=json", str(path)]))


def check_identity() -> None:
    if socket.gethostname().split(".")[0] != HOST or os.getuid() != UID or os.geteuid() != UID:
        stop("DEVELOPMENT host gani only; never use sudo")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_lab_vm() -> bool:
    for item in Path("/proc").iterdir():
        if not item.name.isdecimal():
            continue
        try:
            if item.stat().st_uid != UID:
                continue
            argv = [a for a in (item / "cmdline").read_bytes().split(b"\0") if a]
            if argv and Path(argv[0].decode("utf-8", "replace")).name == "qemu-system-x86_64":
                parts = [v.decode("utf-8", "replace") for v in argv]
                if (VM_NAME in parts
                        or "ccpc-dev-restore-lab-20261123" in parts
                        or any(str(DISK) in v or str(ORIGINAL_DISK) in v for v in parts)):
                    return True
        except (PermissionError, FileNotFoundError, ProcessLookupError):
            continue
    return False


def preflight_start() -> None:
    check_identity()
    if grp.getgrnam("kvm").gr_gid not in (os.getegid(), *os.getgroups()):
        stop("KVM group not active; run '--start' using sg kvm")
    if not os.access("/dev/kvm", os.R_OK | os.W_OK):
        stop("KVM device read/write access missing")
    for program in ("qemu-img", "qemu-system-x86_64", "docker"):
        if not shutil.which(program):
            stop("preinstalled program missing: " + program)
    for folder in (BASE, STAGE, LAB):
        correct_file(folder, True, 0o700)
    correct_file(ORIGINAL_IMAGE, False, 0o400)
    correct_file(ORIGINAL_DISK, False, 0o600)
    correct_file(DISK, False, 0o600)
    correct_file(SEED, False, 0o600)
    correct_file(PRIVATE_PASSWORD, False, 0o600)
    if sha256_file(ORIGINAL_IMAGE) != IMAGE_SHA:
        stop("official Ubuntu cloud image checksum has changed")
    staged = disk_info(ORIGINAL_DISK)
    baseline = disk_info(DISK)
    if (staged.get("format") != "qcow2"
            or staged.get("virtual-size") != VIRTUAL_SIZE
            or staged.get("backing-filename") != str(ORIGINAL_IMAGE)):
        stop("original Nov23 60GiB recovery disk mismatch")
    if (baseline.get("format") != "qcow2"
            or baseline.get("virtual-size") != VIRTUAL_SIZE
            or baseline.get("backing-filename") != str(ORIGINAL_DISK)):
        stop("new guest-only persistent qcow2 backing chain mismatch")
    if current_lab_vm():
        stop("another matching CCPC recovery QEMU process is already present")
    if RUNTIME.exists() or RUNTIME.is_symlink():
        stop("one-shot runtime already exists; use --status / --console / --shutdown")
    if shutil.disk_usage(BASE).free < 12 * 1024**3:
        stop("insufficient recovery lab free disk")
    mem = next((int(x.split()[1]) for x in Path("/proc/meminfo").read_text().splitlines()
                if x.startswith("MemAvailable:")), 0)
    if mem < 11 * 1024**2:
        stop("less than 11 GiB host available memory")
    if read_only(["docker", "inspect", "--format", "{{.State.Running}}",
                  "frappe_docker_devcontainer-frappe-1"]) != "true":
        stop("persistent DEVELOPMENT Frappe container is not running")


def qemu_argv() -> list[str]:
    return [
        "qemu-system-x86_64",
        "-name", VM_NAME,
        "-no-user-config", "-nodefaults",
        "-machine", "q35,accel=kvm", "-cpu", "host",
        "-smp", "4", "-m", "8192",
        "-drive", f"file={DISK},format=qcow2,if=virtio",
        "-drive", f"file={SEED},format=raw,if=virtio,readonly=on",
        "-boot", "order=c,menu=off",
        "-nic", "none",
        "-display", "none",
        "-serial", f"unix:{SERIAL},server=on,wait=off",
        "-qmp", f"unix:{QMP},server=on,wait=off",
        "-monitor", "none",
        "-no-reboot",
    ]


def write_exclusive(path: Path, text: str) -> None:
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(text)


def start() -> None:
    os.umask(0o077)
    preflight_start()
    RUNTIME.mkdir(mode=0o700)
    correct_file(RUNTIME, True, 0o700)
    fd = os.open(STDERR_LOG, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    proc = None
    with os.fdopen(fd, "wb", buffering=0) as log:
        proc = subprocess.Popen(
            qemu_argv(), stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            cwd=str(RUNTIME), start_new_session=True, close_fds=True,
        )
    write_exclusive(PID_FILE, str(proc.pid) + "\n")
    for _ in range(60):
        if proc.poll() is not None:
            stop("QEMU exited at startup; preserve private qemu-output.log for review")
        if SERIAL.is_socket() and QMP.is_socket():
            break
        time.sleep(0.1)
    else:
        # Only the process we created is eligible for termination here.
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        stop("QEMU control sockets not created; this specific new guest was stopped")
    print("PERSISTENT GUEST START: REQUESTED; QEMU PID:", proc.pid)
    print("NETWORK: NONE; BACKUP TRANSFER: NONE")
    print("PERSISTENT GUEST DISK:", DISK)
    print("GUEST LOGIN: ccpc-restore (password in private host-only file)")
    print("CONSOLE: python3 -B <this-script> --console")
    print("SHUTDOWN: python3 -B <this-script> --shutdown")
    print("NO DOCKER / DEVELOPMENT DB / PRODUCTION OPERATION")


def get_vm_pid() -> int:
    correct_file(RUNTIME, True, 0o700)
    correct_file(PID_FILE, False, 0o600)
    pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    if not 1 < pid < 2**22:
        stop("invalid private PID file")
    return pid


def vm_status() -> None:
    check_identity()
    pid = get_vm_pid()
    proc = Path(f"/proc/{pid}")
    if not proc.exists():
        print("PERSISTENT GUEST: STOPPED; PID NO LONGER EXISTS")
        return
    argv = [a.decode("utf-8", "replace") for a in
            (proc / "cmdline").read_bytes().split(b"\0") if a]
    if (proc.stat().st_uid != UID or not argv
            or Path(argv[0]).name != "qemu-system-x86_64"
            or VM_NAME not in argv or not any(str(DISK) in a for a in argv)):
        stop("saved PID no longer identifies the reviewed guest (do not signal)")
    print("PERSISTENT GUEST: RUNNING; PID:", pid)
    print("QEMU NETWORK DISABLED:", argv[argv.index("-nic") + 1] == "none"
          if "-nic" in argv else False)
    print("QEMU MONITOR DISABLED:", argv[argv.index("-monitor") + 1] == "none"
          if "-monitor" in argv else False)


def console() -> None:
    check_identity()
    vm_status()
    if not SERIAL.is_socket() or not sys.stdin.isatty():
        stop("guest serial socket unavailable or terminal is not interactive")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(str(SERIAL))
    sock.setblocking(False)
    stdin_fd = sys.stdin.fileno()
    previous = termios.tcgetattr(stdin_fd)
    tty.setraw(stdin_fd)
    print("\r\nGUEST CONSOLE ATTACHED. Press Ctrl+] to detach.\r\n", end="", flush=True)
    selector = selectors.DefaultSelector()
    selector.register(sock, selectors.EVENT_READ)
    selector.register(stdin_fd, selectors.EVENT_READ)
    try:
        while True:
            for key, _ in selector.select():
                if key.fileobj == sock:
                    data = sock.recv(16384)
                    if not data:
                        return
                    os.write(sys.stdout.fileno(), data)
                else:
                    data = os.read(stdin_fd, 1024)
                    if not data:
                        return
                    if b"\x1d" in data:
                        before = data.split(b"\x1d", 1)[0]
                        if before:
                            sock.sendall(before)
                        return
                    sock.sendall(data)
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, previous)
        sock.close()
        print("\nCONSOLE DETACHED; VM CONTINUES UNTIL SHUTDOWN", flush=True)


def shutdown() -> None:
    check_identity()
    vm_status()
    if not QMP.is_socket():
        stop("QMP socket missing; no shutdown sent")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(5)
        client.connect(str(QMP))
        reader = client.makefile("rb")
        greeting = json.loads(reader.readline())
        if "QMP" not in greeting:
            stop("QMP greeting invalid")
        client.sendall(b'{"execute":"qmp_capabilities"}\r\n')
        if "return" not in json.loads(reader.readline()):
            stop("QMP handshake failed")
        client.sendall(b'{"execute":"system_powerdown"}\r\n')
        result = json.loads(reader.readline())
        if "return" not in result:
            stop("QMP guest ACPI shutdown rejected")
    print("GUEST SHUTDOWN REQUESTED (ACPI); confirm with --status")
    print("Do not use forced kill for a persistent guest without separate review")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            stop("usage: script --start | --status | --console | --shutdown")
        action = sys.argv[1]
        if action == "--start":
            start()
        elif action == "--status":
            vm_status()
        elif action == "--console":
            console()
        elif action == "--shutdown":
            shutdown()
        else:
            stop("unsupported action")
    except (OSError, RuntimeError, ValueError, KeyError, IndexError, json.JSONDecodeError) as err:
        print("STOP: " + str(err), file=sys.stderr, flush=True)
        sys.exit(1)
