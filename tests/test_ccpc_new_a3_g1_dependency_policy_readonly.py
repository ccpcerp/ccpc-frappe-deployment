"""Offline-only synthetic tests; no Docker or server access."""
import copy
import hashlib
import importlib.util
import io
import json
import os
import stat
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("g1audit", str(Path(__file__).resolve().parents[1] / "scripts/ccpc_new_a3_g1_dependency_policy_readonly.py"))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def data():
    p = "ccpc_prod_erpnext"
    cand = {f"{p}-{x}-1" for x in ("db", "redis-cache", "redis-queue", "backend", "websocket", "frontend")}
    orig = {f"{p}-{x}-1" for p in ("ccpc_full_acceptance_20261107", "ccpc_restore_rehearsal_20261107") for x in ("redis-queue", "redis-cache", "db")}
    t = "ccpc_a3_restore_drill_20261112"
    test = {f"{t}-{x}-1" for x in ("frontend-completion1", "websocket-completion1", "backend-recovery1", "redis-queue", "redis-cache", "db")}
    failed = f"{t}-backend-1"
    expected = cand | orig | test | {failed}
    ids = {n: hashlib.sha256(n.encode()).hexdigest() for n in expected}
    rows = [{"Name": "/"+n, "Id": ids[n], "State": {"Running": n != failed, "ExitCode": 1 if n==failed else 0}, "HostConfig": {"RestartPolicy": {"Name":"no"}}} for n in expected]
    return expected, ids, rows, cand, failed


class TestAudit(unittest.TestCase):
    def run_audit(self, change=None, host="ccpcerp-prod", sudo="ccpcadmin"):
        names, ids, rows, cand, failed = data()
        if change:
            change(rows, ids, names, cand, failed)
        def lstat(path):
            return SimpleNamespace(st_mode=(stat.S_IFDIR|0o700) if path.name != "manifest.json" else (stat.S_IFREG|0o600), st_uid=0)
        def run(command, **kw):
            if command[3] == "ps":
                return SimpleNamespace(stdout="\n".join(sorted(names)))
            if command[3] == "container":
                return SimpleNamespace(stdout=json.dumps(rows))
            raise AssertionError("unknown command")
        out = io.StringIO()
        with patch.object(audit.os, "geteuid", return_value=0), \
             patch.object(audit.socket, "gethostname", return_value=host), \
             patch.dict(audit.os.environ, {"SUDO_USER": sudo}, clear=True), \
             patch.object(audit.Path, "lstat", lstat), \
             patch.object(audit.Path, "read_text", lambda *_args, **_kw: json.dumps({"container_ids": ids})), \
             patch.object(audit.subprocess, "run", side_effect=run), \
             redirect_stdout(out):
            try:
                audit.audit()
                good = True
            except Exception:
                good = False
        return good, out.getvalue()

    def test_success(self):
        ok, out=self.run_audit()
        self.assertTrue(ok)
        self.assertIn("NONCANDIDATE_POLICY_NO_13_PASS", out)
        self.assertNotIn("0", out)  # Do not disclose any container IDs

    def test_candidate_policy_drift(self):
        def change(rows,ids,names,cand,failed):
            next(r for r in rows if r["Name"].lstrip("/") in cand)["HostConfig"]["RestartPolicy"]["Name"]="always"
        self.assertFalse(self.run_audit(change)[0])

    def test_noncandidate_policy_drift(self):
        def change(rows,ids,names,cand,failed):
            next(r for r in rows if r["Name"].lstrip("/") not in cand)["HostConfig"]["RestartPolicy"]["Name"]="unless-stopped"
        self.assertFalse(self.run_audit(change)[0])

    def test_id_drift(self):
        def change(rows,ids,names,cand,failed):
            rows[0]["Id"]="0"*64
        self.assertFalse(self.run_audit(change)[0])

    def test_extra_name(self):
        def change(rows,ids,names,cand,failed):
            names.add("unknown")
        self.assertFalse(self.run_audit(change)[0])

    def test_failed_backend_auto_started(self):
        def change(rows,ids,names,cand,failed):
            next(r for r in rows if r["Name"].lstrip("/")==failed)["State"]["Running"] = True
        self.assertFalse(self.run_audit(change)[0])

    def test_wrong_host_and_operator(self):
        self.assertFalse(self.run_audit(host="other")[0])
        self.assertFalse(self.run_audit(sudo="root")[0])

if __name__=="__main__":
    unittest.main()
