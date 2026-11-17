"""Isolated synthetic safety tests for one-time NEW A3 candidate backup.
No Docker, MariaDB, NAS, business data, mount or backup generator execution.
"""
import importlib.util
import gzip
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock

p = Path(__file__).resolve().parents[1] / "scripts" / "ccpc_new_a3_one_time_backup.py"
spec = importlib.util.spec_from_file_location("ccpc_bk", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestStatic(unittest.TestCase):
    def test_wrong_host_stops_before_any_host_access(self):
        with mock.patch.object(m.socket, "gethostname", return_value="old-ccpcerpserver"):
            with self.assertRaisesRegex(RuntimeError, "Wrong host"):
                m.inspect_runtime()

    def test_names_roles(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for suffix in m.ROLES:
                (folder / ("20261112_080000-ccpcerp_local-" + suffix)).write_bytes(b"x")
            self.assertEqual(set(m.artifacts_at(folder)), set(m.ROLES.values()))
            (folder / "unexpected").write_text("unexpected")
            with self.assertRaisesRegex(RuntimeError, "exactly four"):
                m.artifacts_at(folder)

    def test_mixed_timestamp_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for suffix in m.ROLES:
                date = "20261112_080001" if suffix == "private-files.tar" else "20261112_080000"
                (folder / (date + "-ccpcerp_local-" + suffix)).write_bytes(b"x")
            with self.assertRaisesRegex(RuntimeError, "mixed"):
                m.artifacts_at(folder)

    def test_copy_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d, "src")
            dst = Path(d, "dst")
            src.write_bytes(b"synthetic")
            m.copy_new(src, dst)
            self.assertEqual(dst.read_bytes(), b"synthetic")
            with self.assertRaises(FileExistsError):
                m.copy_new(src, dst)
            self.assertEqual(dst.read_bytes(), b"synthetic")

    def test_generated_formats(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            db = base / "database.sql.gz"
            with gzip.open(db, "wb") as gz:
                gz.write(b"-- begin frappe metadata\nselect 1;\n")
            m.check_format("database", db)
            conf = base / "config.json"
            conf.write_text(json.dumps({"db_name": "x", "db_password": "dummy"}))
            m.check_format("site_config", conf)
            for role in ("public_files", "private_files"):
                fn = base / (role + ".tar")
                with tarfile.open(fn, "w") as tf:
                    info = tarfile.TarInfo("ccpcerp.local/public/files")
                    info.type = tarfile.DIRTYPE
                    tf.addfile(info)
                m.check_format(role, fn)

    def test_child_never_invokes_scheduled_backup_cleanup(self):
        self.assertIn("gen.get_backup(force=True, ignore_files=False)", m.CHILD)
        self.assertNotIn("scheduled_backup(", m.CHILD)
        self.assertNotIn("delete_temp_backups(", m.CHILD)
        self.assertNotIn("bench backup", m.CHILD)

    def test_no_generic_destructive_host_ops(self):
        source = p.read_text()
        for needle in ("reset --hard", "docker restart", "docker rm", "docker compose up",
                       "rmtree(", "os.unlink(", ".unlink(", "rm -rf"):
            self.assertNotIn(needle, source)


if __name__ == "__main__":
    unittest.main()
