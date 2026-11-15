"""Read-only, one-step NEW A3 G1 restart policy audit; no mutations."""
import json
import os
import socket
import stat
import subprocess
from pathlib import Path


def audit():
    assert os.geteuid() == 0
    assert os.environ.get("SUDO_USER") == "ccpcadmin"
    assert socket.gethostname().split(".")[0] == "ccpcerp-prod"
    assert not any(k in os.environ for k in ("DOCKER_HOST", "DOCKER_CONTEXT"))
    path = Path("/var/lib/ccpc-new-a3-r0-manifest-20261113/manifest.json")
    parent, file = path.parent.lstat(), path.lstat()
    assert stat.S_ISDIR(parent.st_mode) and parent.st_uid == 0
    assert stat.S_IMODE(parent.st_mode) == 0o700
    assert stat.S_ISREG(file.st_mode) and file.st_uid == 0
    assert stat.S_IMODE(file.st_mode) == 0o600
    ids = json.loads(path.read_text(encoding="utf-8"))["container_ids"]
    p = "ccpc_prod_erpnext"
    candidates = {f"{p}-{role}-1" for role in
                  ("db", "redis-cache", "redis-queue", "backend", "websocket", "frontend")}
    originals = {f"{prefix}-{role}-1" for prefix in
                 ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107")
                 for role in ("redis-queue", "redis-cache", "db")}
    t = "ccpc_a3_restore_drill_20261112"
    test_running = {f"{t}-{role}-1" for role in
                    ("frontend-completion1", "websocket-completion1", "backend-recovery1",
                     "redis-queue", "redis-cache", "db")}
    test_failed = f"{t}-backend-1"
    expected = candidates | originals | test_running | {test_failed}
    assert len(expected) == 19 and set(ids) == expected
    base = ["docker", "--host", "unix:///var/run/docker.sock"]
    def run(*cmd):
        return subprocess.run(base + list(cmd), check=True, text=True, capture_output=True,
                              timeout=35).stdout
    assert set(run("ps", "-a", "--format", "{{.Names}}").splitlines()) == expected
    objects = json.loads(run("container", "inspect", *sorted(expected)))
    assert isinstance(objects, list) and len(objects) == 19
    rows = {o["Name"].lstrip("/"): o for o in objects}
    assert set(rows) == expected
    assert all(rows[n]["Id"] == ids[n] for n in expected)
    assert all(rows[n]["State"]["Running"] is True for n in
               (candidates | originals | test_running))
    assert rows[test_failed]["State"]["Running"] is False
    assert rows[test_failed]["State"]["ExitCode"] == 1
    def policy(n):
        return rows[n]["HostConfig"]["RestartPolicy"]["Name"]
    assert all(policy(n) == "no" for n in candidates)
    assert all(policy(n) == "no" for n in (expected - candidates))
    print("CCPC_NEW_A3_G1_PROTECTED_IDENTITIES_19_PASS")
    print("CCPC_NEW_A3_G1_CANDIDATE_POLICY_NO_6_PASS")
    print("CCPC_NEW_A3_G1_NONCANDIDATE_POLICY_NO_13_PASS")
    print("CCPC_NEW_A3_G1_POLICY_READONLY_CHECK_PASS")


if __name__ == "__main__":
    try:
        audit()
    except Exception:
        print("CCPC_NEW_A3_G1_POLICY_STOP_REVIEW_REQUIRED")
        raise SystemExit(1) from None
