#!/usr/bin/env python3
"""One-shot offline read-only authentic archive versus revised keyless CI Auth guard.

No plaintext files, network, database access, secret display or dynamic errors.
Original pinned ciphertext and manifest-integrity checks remain unchanged.
Original ciphertext/TAR/manifest guards remain. New CI guard classifies SQL in memory.
A NO_ENCRYPTED_AUTH_ROWS result covers only standard __Auth rows, not arbitrary
custom-app encrypted fields, external credentials, or historical key recovery.
This diagnostic does not authorize a database restore.
"""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile
import zlib

CIPHERTEXT = Path('/home/gani/ccpc-integration2-encrypted/integration2-restore-20261030-85ff2c424e4cb5cf.tar.age')
IDENTITY = Path('/home/gani/.local/share/ccpc-integration2-restore/identity.txt')
AGE = Path('/home/gani/.local/opt/ccpc-age-1.2.1-1build1/usr/bin/age')
CIPHERTEXT_HASH = '92fe1ba22fa6f1ae53828cf6da5276c6d7a7310f8b99be74a33bca0939911560'
SOURCE_APP_SHA = '0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41'
MAX_TAR = 32 * 1024 * 1024
MAX_SQL = 256 * 1024 * 1024
MAX_SQL_LINE = 32 * 1024 * 1024
EXPECTED_COLUMNS = [b'doctype', b'name', b'fieldname', b'password', b'encrypted']

class Classified(Exception):
    pass

def require(test, label):
    if not test:
        raise Classified(label)

def scan_sql(sql_gz):
    # Import only the immutable, locally pinned CI guard; it has no I/O on import.
    from importlib.util import module_from_spec, spec_from_file_location
    guard_path = Path(__file__).with_name('restore_guard.py')
    require(guard_path.is_file(), 'GUARD_SOURCE_MISSING')
    source = guard_path.read_bytes()
    git_blob = b'blob ' + str(len(source)).encode('ascii') + b'\0' + source
    require(hashlib.sha1(git_blob).hexdigest() ==
            'ccc3574acc12b0d9596af4a9df3daa4b62d061dd',
            'GUARD_SOURCE_INTEGRITY')
    spec = spec_from_file_location('ccpc_pinned_restore_guard', guard_path)
    require(spec is not None and spec.loader is not None, 'GUARD_SOURCE_MISSING')
    guard = module_from_spec(spec)
    spec.loader.exec_module(guard)
    try:
        return ('NO_ENCRYPTED_AUTH_ROWS' if
                guard.no_encrypted_auth_entries(sql_gz) else
                'ENCRYPTED_ROWS_PRESENT')
    except (ValueError, RuntimeError, OSError):
        return 'INCONCLUSIVE_SQL_VALIDATION'

def run():
    for path in (CIPHERTEXT, IDENTITY):
        s = path.lstat()
        require(stat.S_ISREG(s.st_mode) and s.st_uid == os.geteuid()
                and stat.S_IMODE(s.st_mode) == 0o600, 'LOCAL_FILE_SECURITY')
    require(AGE.is_file() and os.access(AGE, os.X_OK), 'AGE_EXECUTABLE_MISSING')
    ciphertext = CIPHERTEXT.read_bytes()
    require(len(ciphertext) == 1_137_112 and
            hashlib.sha256(ciphertext).hexdigest() == CIPHERTEXT_HASH,
            'CIPHERTEXT_INTEGRITY')
    result = subprocess.run([str(AGE), '--decrypt', '--identity', str(IDENTITY)],
                            input=ciphertext, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=45, check=False,
                            env={'HOME': str(Path.home()), 'PATH': '/usr/bin:/bin'})
    require(result.returncode == 0 and len(result.stdout) <= MAX_TAR,
            'ARCHIVE_DECRYPT')
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode='r:') as tar:
        members = tar.getmembers()
        require(len(members) == 5 and all(m.isfile() for m in members),
                'ARCHIVE_INTEGRITY')
        manifest_file = tar.extractfile('SHA256-MANIFEST.json')
        require(manifest_file is not None, 'ARCHIVE_INTEGRITY')
        manifest = json.loads(manifest_file.read())
        require(isinstance(manifest, dict) and
                manifest.get('site') == 'ccpc-integration2.localhost' and
                manifest.get('app_sha') == SOURCE_APP_SHA, 'ARCHIVE_INTEGRITY')
        records = manifest.get('files')
        require(isinstance(records, dict) and len(records) == 4, 'ARCHIVE_INTEGRITY')
        names = set(records)
        require({m.name for m in members} == names | {'SHA256-MANIFEST.json'},
                'ARCHIVE_INTEGRITY')
        database_names = [x for x in names if isinstance(x, str) and x.endswith('-database.sql.gz')]
        require(len(database_names) == 1, 'ARCHIVE_INTEGRITY')
        database_name = database_names[0]
        member = tar.extractfile(database_name)
        require(member is not None, 'ARCHIVE_INTEGRITY')
        sql_gz = member.read()
        record = records[database_name]
        require(isinstance(record, dict) and isinstance(record.get('size'), int)
                and isinstance(record.get('sha256'), str) and
                record['size'] == len(sql_gz) and
                hashlib.sha256(sql_gz).hexdigest() == record['sha256'],
                'ARCHIVE_INTEGRITY')
    return scan_sql(sql_gz)

if __name__ == '__main__':
    try:
        output = run()
    except Classified as e:
        print('ARCHIVED_AUTH_GUARD: ' + e.args[0])
        raise SystemExit(1) from None
    except Exception:
        print('ARCHIVED_AUTH_GUARD: INCONCLUSIVE_INTERNAL_ERROR')
        raise SystemExit(1) from None
    print('ARCHIVED_AUTH_GUARD: ' + output)
