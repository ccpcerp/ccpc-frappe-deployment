"""Only synthetic offline data, mocked bench runner, and verified format checks."""

import dataclasses
import gzip
import io
import json
import os
import stat
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import dedicated_backup_capture as capture
from scripts import dedicated_backup_core as core


class CaptureOfflineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "private"
        self.root.mkdir(mode=0o700)
        self.id = "20261023T160201Z-12345678abcdef00"
        self.runtime = capture.CaptureAttestation(
            host="ccpcerp-prod",
            site="ccpcerp.local",
            compose_profile="dedicated-pre-tls",
            compose_project="ccpc-dedicated",
            frappe_sha=capture.FRAPPE_SHA,
            image_digest="sha256:" + "a" * 64,
            service="backend",
            database_service="db",
            site_volume_verified=True,
            database_volume_verified=True,
            writes_quiesced=True,
            no_partial_backup_filters=True,
            encryption_disabled=True,
        )
        self.calls = []

    @property
    def output(self):
        return self.root / (capture.CAPTURE_DIR_PREFIX + self.id)

    def filenames(self, stamp="20261023_160201"):
        return {
            "database": f"{stamp}-ccpcerp_local-database.sql.gz",
            "site_config": f"{stamp}-ccpcerp_local-site_config_backup.json",
            "public_files": f"{stamp}-ccpcerp_local-files.tar",
            "private_files": f"{stamp}-ccpcerp_local-private-files.tar",
        }

    def make_four(self, target, stamp="20261023_160201"):
        names = self.filenames(stamp)
        (target/names["database"]).write_bytes(gzip.compress(b"-- synthetic SQL\nSELECT 1;\n"))
        (target/names["site_config"]).write_text(json.dumps({"db_name": "synthetic"}))
        for role in ("public_files", "private_files"):
            with tarfile.open(target/names[role], "w") as archive:
                blob = b"Synthetic data only"
                member = tarfile.TarInfo("test/sample.txt")
                member.size = len(blob)
                archive.addfile(member, io.BytesIO(blob))
        return names

    def runner(self, argv):
        self.calls.append(tuple(argv))
        self.make_four(Path(argv[-1]))
        return 0

    def call(self, runner=None, attest=None):
        return capture.capture_with_verified_runner(
            capture_root=self.root,
            run_id=self.id,
            attest=attest if attest is not None else lambda: self.runtime,
            runner=runner if runner is not None else self.runner,
        )

    def reject(self, f):
        with self.assertRaises(core.BackupSafetyError):
            f()

    def test_four_artifacts_exact_args_and_private_output(self):
        result = self.call()
        self.assertEqual(result.run_id, self.id)
        self.assertEqual(result.source_dir, self.output)
        self.assertEqual(result.filenames, self.filenames())
        self.assertEqual(result.image_digest, self.runtime.image_digest)
        self.assertEqual(self.calls, [(
            "bench", "--site", "ccpcerp.local", "backup", "--with-files",
            "--ignore-backup-conf", "--backup-path", str(self.output),
        )])
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
        self.assertEqual(set(self.output.iterdir()), {self.output/n for n in self.filenames().values()})

    def test_attestation_rejects_bad_host_site_profile_release(self):
        for field, bad in (("host", "ccpcerpserver"), ("site", "all"),
                           ("compose_profile", "legacy-lan"), ("frappe_sha", "")):
            self.reject(lambda: self.call(attest=lambda: dataclasses.replace(self.runtime, **{field: bad})))
        self.assertFalse(self.output.exists())

    def test_attestation_rejects_wrong_services_project_and_digest(self):
        for field, bad in (("service", "scheduler"), ("database_service", "other"),
                           ("compose_project", ""), ("compose_project", "bad/other"),
                           ("image_digest", "latest")):
            self.reject(lambda: self.call(attest=lambda: dataclasses.replace(self.runtime, **{field: bad})))
        self.assertFalse(self.output.exists())

    def test_attestation_rejects_unverified_consistency_and_encryption(self):
        flags = ("site_volume_verified", "database_volume_verified", "writes_quiesced",
                 "no_partial_backup_filters", "encryption_disabled")
        for field in flags:
            self.reject(lambda: self.call(attest=lambda: dataclasses.replace(self.runtime, **{field: False})))
        self.assertFalse(self.output.exists())

    def test_attestation_must_be_object(self):
        self.reject(lambda: self.call(attest=lambda: {}))
        self.assertFalse(self.output.exists())

    def test_reject_missing_root_or_world_searchable(self):
        self.root.chmod(0o755)
        self.reject(self.call)
        self.root.chmod(0o700)
        self.root.rmdir()
        self.reject(self.call)

    def test_reject_symlinked_root(self):
        actual = self.root.with_name("actual")
        self.root.rename(actual)
        self.root.symlink_to(actual, target_is_directory=True)
        self.reject(self.call)

    def test_reject_target_directly_on_nas(self):
        with patch.object(core, "NAS_MOUNT", self.root):
            self.reject(self.call)
        self.assertFalse(self.output.exists())

    def test_invalid_run_id_does_not_reserve_directory(self):
        self.id = "../bad"
        self.reject(self.call)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_capture_preserved_and_not_reexecuted(self):
        self.output.mkdir()
        (self.output/"preserve").write_text("historical")
        self.reject(self.call)
        self.assertEqual((self.output/"preserve").read_text(), "historical")
        self.assertEqual(self.calls, [])

    def test_nonzero_runner_preserves_incomplete_and_does_not_retry(self):
        invoke = Mock(return_value=1)
        self.reject(lambda: self.call(runner=invoke))
        self.assertEqual(invoke.call_count, 1)
        self.assertTrue(self.output.exists())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_runner_exception_is_sanitized(self):
        def fail(_):
            raise ValueError("synthetic password or secret must not appear")
        with self.assertRaisesRegex(core.BackupSafetyError, "executor failed") as ctx:
            self.call(runner=fail)
        self.assertNotIn("password", str(ctx.exception))
        self.assertTrue(self.output.exists())

    def test_missing_one_of_four_rejected(self):
        def missing(argv):
            self.make_four(Path(argv[-1]))
            (Path(argv[-1])/self.filenames()["private_files"]).unlink()
            return 0
        self.reject(lambda: self.call(runner=missing))
        self.assertTrue(self.output.exists())

    def test_extra_stale_or_untracked_file_rejected(self):
        def extra(argv):
            self.make_four(Path(argv[-1]))
            (Path(argv[-1])/"old-backup.sql.gz").write_bytes(b"X")
            return 0
        self.reject(lambda: self.call(runner=extra))

    def test_different_backup_timestamps_rejected(self):
        def mixed(argv):
            target=Path(argv[-1])
            self.make_four(target)
            prior=self.filenames()["database"]
            (target/prior).rename(target/self.filenames("20261023_165959")["database"])
            return 0
        self.reject(lambda: self.call(runner=mixed))

    def test_modified_gzip_rejected_by_publication_core(self):
        def corrupt(argv):
            target=Path(argv[-1])
            self.make_four(target)
            (target/self.filenames()["database"]).write_bytes(b"not gzip")
            return 0
        self.reject(lambda: self.call(runner=corrupt))

    def test_symlink_artifact_rejected(self):
        def symlink(argv):
            target = Path(argv[-1])
            self.make_four(target)
            p=target/self.filenames()["site_config"]
            p.unlink()
            p.symlink_to("/etc/hosts")
            return 0
        self.reject(lambda: self.call(runner=symlink))

    def test_output_dir_replacement_rejected(self):
        def replaced(argv):
            out=Path(argv[-1])
            out.rmdir()
            out.symlink_to(self.root, target_is_directory=True)
            return 0
        self.reject(lambda: self.call(runner=replaced))

    def test_boolean_runner_result_is_not_success(self):
        self.reject(lambda: self.call(runner=lambda _argv: True))


if __name__ == "__main__":
    unittest.main()
