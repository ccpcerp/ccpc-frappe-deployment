"""Offline tests: synthetic files only; no Docker, NAS, host mounts or secrets."""
import json
import gzip
import io
import tarfile
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import dedicated_backup_core as core


class TestBackupCore(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.nas = self.base / 'fake-nas'
        self.source.mkdir()
        self.nas.mkdir()
        self.lock = self.base / 'run.lock'
        self.names = {
            'database': '20261023-ccpcerp_local-database.sql.gz',
            'site_config': '20261023-ccpcerp_local-site_config_backup.json',
            'public_files': '20261023-ccpcerp_local-files.tar',
            'private_files': '20261023-ccpcerp_local-private-files.tar',
        }
        (self.source / self.names['database']).write_bytes(gzip.compress(b'-- synthetic SQL only\nSELECT 1;\n'))
        (self.source / self.names['site_config']).write_text('{"db_name":"synthetic_only"}')
        for role in ('public_files','private_files'):
            with tarfile.open(self.source/self.names[role], 'w') as archive:
                data=io.BytesIO(b'synthetic archive data')
                entry=tarfile.TarInfo('safe/placeholder.txt')
                entry.size= len(data.getvalue())
                archive.addfile(entry, data)
        self.run_id = '20261023T120000Z-00000000deadbeef'
        self.probe = Mock(return_value=None)

    def publish(self):
        return core.publish_verified_set(self.source, self.names, self.run_id, self.nas, self.lock, probe=self.probe)

    def rejected(self, action):
        with self.assertRaises(core.BackupSafetyError):
            action()

    def test_four_artifacts_manifest_marker_and_copy(self):
        target = self.publish()
        self.assertEqual(target, self.nas / self.run_id)
        self.assertEqual((target / 'COMPLETED').read_text(), self.run_id+'\n')
        manifest = json.loads((target / 'manifest.json').read_text())
        self.assertEqual([i['role'] for i in manifest['artifacts']], list(core.ROLES))
        self.assertEqual(set(p.name for p in target.iterdir()), set(self.names.values()) | {'manifest.json','COMPLETED'})
        for name in self.names.values():
            self.assertEqual((target/name).read_bytes(), (self.source/name).read_bytes())
        self.assertFalse((self.nas / ('.partial-'+self.run_id)).exists())
        self.assertGreaterEqual(self.probe.call_count, 6)

    def test_reject_missing_empty_duplicate_and_unexpected_roles(self):
        (self.source/self.names['database']).unlink()
        self.rejected(self.publish)
        (self.source/self.names['database']).write_bytes(b'')
        self.rejected(self.publish)
        self.rejected(lambda: core.inspect_artifacts(self.source, {**self.names,'other':'other.tar'}))
        self.rejected(lambda: core.inspect_artifacts(self.source, {**self.names,'private_files':self.names['public_files']}))
        self.assertEqual(list(self.nas.iterdir()), [])

    def test_reject_invalid_content_and_wrong_site(self):
        (self.source/self.names['database']).write_bytes(b'not a gzip')
        self.rejected(self.publish)
        (self.source/self.names['database']).write_bytes(gzip.compress(b'SELECT 1;'))
        (self.source/self.names['site_config']).write_bytes(b'not json')
        self.rejected(self.publish)
        (self.source/self.names['site_config']).write_bytes(b'{}')
        self.names['database'] = self.names['database'].replace('ccpcerp_local','other_site')
        self.rejected(self.publish)

    def test_reject_paths_and_symlinks(self):
        self.rejected(lambda: core.inspect_artifacts(self.source, {**self.names,'database':'../escape.sql.gz'}))
        (self.source/self.names['database']).unlink()
        (self.source/self.names['database']).symlink_to('/etc/hosts')
        self.rejected(self.publish)
        self.assertEqual(list(self.nas.iterdir()), [])

    def test_reject_existing_run_and_partial_without_change(self):
        existing = self.nas/self.run_id
        existing.mkdir()
        (existing/'keep').write_text('preserve')
        self.rejected(self.publish)
        self.assertEqual((existing/'keep').read_text(),'preserve')
        existing.rename(self.nas/'moved')
        partial = self.nas/('.partial-'+self.run_id)
        partial.mkdir()
        self.rejected(self.publish)
        self.assertTrue(partial.is_dir())

    def test_mount_probe_fails_before_write(self):
        self.probe.side_effect=core.BackupSafetyError('wrong source')
        self.rejected(self.publish)
        self.assertEqual(list(self.nas.iterdir()), [])

    def test_failure_during_transfer_preserves_partial_for_review(self):
        count=0
        def test_probe(path):
            nonlocal count
            count += 1
            if count==3:
                raise core.BackupSafetyError('NAS connection lost')
        self.probe.side_effect=test_probe
        self.rejected(self.publish)
        partial=self.nas/('.partial-'+self.run_id)
        self.assertTrue(partial.is_dir())
        self.assertFalse((self.nas/self.run_id).exists())
        self.assertFalse((partial/'COMPLETED').exists())

    def test_hash_mismatch_keeps_unpublished(self):
        orig=core._digest
        def bad_hash(path):
            size, value=orig(path)
            if str(path).startswith(str(self.nas)):
                return size, '0'*64
            return size, value
        with patch.object(core, '_digest', side_effect=bad_hash):
            self.rejected(self.publish)
        self.assertFalse((self.nas/self.run_id).exists())
        self.assertTrue((self.nas/('.partial-'+self.run_id)).exists())

    def test_lock_rejects_concurrent_run(self):
        with core.exclusive_lock(self.lock):
            self.rejected(self.publish)
        self.assertEqual(list(self.nas.iterdir()), [])

    def test_unsafe_run_id(self):
        self.run_id='../unsafe'
        self.rejected(self.publish)
        self.assertEqual(list(self.nas.iterdir()), [])

    def test_no_clobber_rename(self):
        left=self.nas/'left'
        right=self.nas/'right'
        left.mkdir()
        right.mkdir()
        (right/'keep').write_text('never overwrite')
        self.rejected(lambda: core._rename_noreplace(left,right))
        self.assertTrue(left.is_dir())
        self.assertEqual((right/'keep').read_text(),'never overwrite')

    def test_mount_guard_good_and_negative_cases(self):
        success=lambda value: subprocess.CompletedProcess(['findmnt'],0,value+'\n','')
        good=core.NAS_SOURCE+' cifs rw,nosuid,nodev,noexec'
        with patch.object(core.os.path,'ismount',return_value=True):
            core.verify_cifs_mount(self.nas,findmnt=lambda *a,**k: success(good), is_mount=lambda _p: True)
            for bad in ('//192.168.50.132/erpnext_backups cifs rw',
                        core.NAS_SOURCE+' ext4 rw',
                        core.NAS_SOURCE+' cifs ro',
                        core.NAS_SOURCE+' cifs rw,nosuid,nodev',
                        core.NAS_SOURCE+' cifs rw,ro',
                        core.NAS_SOURCE+' cifs rw\n'+core.NAS_SOURCE+' cifs rw'):
                self.rejected(lambda: core.verify_cifs_mount(self.nas,findmnt=lambda *a,**k: success(bad), is_mount=lambda _p: True))
        self.rejected(lambda: core.verify_cifs_mount(self.nas))

    def test_invalid_lock_symlink(self):
        self.lock.symlink_to(self.source/self.names['database'])
        with self.assertRaises(OSError):
            with core.exclusive_lock(self.lock):
                pass


if __name__=='__main__':
    unittest.main()
