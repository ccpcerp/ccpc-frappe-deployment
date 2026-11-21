#!/usr/bin/env python3
"""CCPC one-shot read-only, offline archive/manifest compatibility probe.

Never prints real file names, metadata, key material, decrypted bytes, or
exceptions. Does not create any file or perform any network/database operation.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile

CIPHERTEXT = Path('/home/gani/ccpc-integration2-encrypted/integration2-restore-20261030-85ff2c424e4cb5cf.tar.age')
IDENTITY = Path('/home/gani/.local/share/ccpc-integration2-restore/identity.txt')
CIPHERTEXT_SHA256 = '92fe1ba22fa6f1ae53828cf6da5276c6d7a7310f8b99be74a33bca0939911560'
CIPHERTEXT_BYTES = 1_137_112
SOURCE_APP_SHA = '0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41'
MAX_ARCHIVE = 32 * 1024 * 1024

class Rejected(Exception):
    pass

def gate(condition, code):
    if not condition:
        raise Rejected(code)

def decode_json(data, code):
    try:
        value = json.loads(data)
    except (ValueError, UnicodeError, TypeError):
        raise Rejected(code) from None
    gate(isinstance(value, dict), code)
    return value

def inspect_plaintext(plaintext):
    gate(len(plaintext) <= MAX_ARCHIVE, 'PLAINTEXT_SIZE')
    try:
        archive = tarfile.open(fileobj=io.BytesIO(plaintext), mode='r:')
    except (tarfile.TarError, OSError):
        raise Rejected('TAR_OPEN') from None
    with archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        gate(len(members) == 5 and len(set(names)) == 5, 'TAR_MEMBER_COUNT')
        gate(all(m.isfile() and '/' not in m.name and '\\' not in m.name
                 and not m.name.startswith('.') for m in members), 'TAR_MEMBER_TYPES')
        gate('SHA256-MANIFEST.json' in names, 'MANIFEST_NAME')
        stream = archive.extractfile('SHA256-MANIFEST.json')
        gate(stream is not None, 'MANIFEST_READ')
        manifest = decode_json(stream.read(), 'MANIFEST_JSON')
        gate(manifest.get('site') == 'ccpc-integration2.localhost', 'MANIFEST_SITE')
        gate(manifest.get('app_sha') == SOURCE_APP_SHA, 'MANIFEST_APP_SHA')
        records = manifest.get('files')
        gate(isinstance(records, dict) and len(records) == 4, 'MANIFEST_FILES_MAP')
        stems = [n.removesuffix('-database.sql.gz') for n in records
                 if isinstance(n, str) and n.endswith('-database.sql.gz')]
        gate(len(stems) == 1 and stems[0].endswith('-ccpc-integration2_localhost'),
             'COMPONENT_STEM')
        stem = stems[0]
        expected = {stem + '-database.sql.gz', stem + '-site_config_backup.json',
                    stem + '-files.tar', stem + '-private-files.tar'}
        gate(set(records) == expected and set(names) == expected | {'SHA256-MANIFEST.json'},
             'COMPONENT_NAMES')
        parts = {}
        for name in expected:
            record = records[name]
            gate(isinstance(record, dict) and isinstance(record.get('size'), int)
                 and isinstance(record.get('sha256'), str)
                 and re.fullmatch(r'[0-9a-f]{64}', record['sha256']) is not None,
                 'COMPONENT_RECORD_SCHEMA')
            stream = archive.extractfile(name)
            gate(stream is not None, 'COMPONENT_READ')
            content = stream.read()
            gate(len(content) == record['size']
                 and hashlib.sha256(content).hexdigest() == record['sha256'],
                 'COMPONENT_CHECKSUM')
            parts[name] = content
        site_config = decode_json(parts[stem + '-site_config_backup.json'], 'SITE_CONFIG_JSON')
        gate('encryption_key' in site_config, 'SITE_CONFIG_KEY_ABSENT')
        key = site_config['encryption_key']
        gate(isinstance(key, str), 'SITE_CONFIG_KEY_TYPE')
        gate(bool(key), 'SITE_CONFIG_KEY_EMPTY')

def main():
    for p in (CIPHERTEXT, IDENTITY):
        info = p.lstat()
        gate(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o600, 'LOCAL_FILE_SECURITY')
    encrypted = CIPHERTEXT.read_bytes()
    gate(len(encrypted) == CIPHERTEXT_BYTES
         and hashlib.sha256(encrypted).hexdigest() == CIPHERTEXT_SHA256,
         'CIPHERTEXT_INTEGRITY')
    result = subprocess.run(['age', '--decrypt', '--identity', str(IDENTITY)],
                            input=encrypted, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=45, check=False,
                            env={'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                                 'HOME': str(Path.home())})
    gate(result.returncode == 0, 'LOCAL_AGE_DECRYPT')
    inspect_plaintext(result.stdout)

if __name__ == '__main__':
    try:
        main()
    except Rejected as e:
        print('LOCAL ARCHIVE COMPATIBILITY: ' + e.args[0] + ' FAIL')
        raise SystemExit(1) from None
    except Exception:
        print('LOCAL ARCHIVE COMPATIBILITY: INTERNAL_CHECK FAIL')
        raise SystemExit(1) from None
    else:
        print('LOCAL ARCHIVE COMPATIBILITY: ALL_CHECKS_PASS')
