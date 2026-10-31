#!/usr/bin/env python3
"""One-shot offline read-only OPERATION SHAPE classifier for archived Frappe __Auth.

No plaintext files, network, database access, secret display or dynamic errors.
The original pinned archive checks and encrypted-row rejection are unchanged.
Fixed labels distinguish unsupported Auth SQL operation shapes; never accept them.
VALUES variants emit only three fixed categorical features, not SQL text.
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

def parse_values(data):
    """Strictly read only fifth column of each MariaDB extended-insert tuple."""
    buf = data.strip()
    require(buf.endswith(b';'), 'INCONCLUSIVE_SQL_TERMINATOR')
    buf = buf[:-1].strip()
    i = 0
    rows = 0
    encrypted = 0
    while i < len(buf):
        require(buf[i] == 40, 'INCONCLUSIVE_SQL_TUPLE_START')
        i += 1
        last_start = i
        commas = 0
        quote = None
        closed = False
        while i < len(buf):
            c = buf[i]
            if quote is not None:
                if c == 92:
                    i += 2
                    continue
                if c == quote:
                    if i + 1 < len(buf) and buf[i + 1] == quote:
                        i += 2
                        continue
                    quote = None
            elif c in (39, 34):
                quote = c
            elif c == 44:
                commas += 1
                require(commas <= 4, 'INCONCLUSIVE_SQL_EXTRA_COLUMN')
                if commas == 4:
                    last_start = i + 1
            elif c == 41:
                require(commas == 4, 'INCONCLUSIVE_SQL_COLUMN_COUNT')
                val = buf[last_start:i].strip()
                require(val in (b'0', b'1'), 'INCONCLUSIVE_SQL_FLAG_FORMAT')
                encrypted += val == b'1'
                rows += 1
                i += 1
                closed = True
                break
            elif c == 40:
                raise Classified('INCONCLUSIVE_SQL_UNQUOTED_PAREN')
            i += 1
        require(closed, 'INCONCLUSIVE_SQL_TUPLE_UNCLOSED')
        while i < len(buf) and buf[i] in b' \r\t\n':
            i += 1
        if i < len(buf):
            require(buf[i] == 44, 'INCONCLUSIVE_SQL_TUPLE_SEPARATOR')
            i += 1
            while i < len(buf) and buf[i] in b' \r\t\n':
                i += 1
            require(i < len(buf), 'INCONCLUSIVE_SQL_TRAILING_COMMA')
    require(rows > 0, 'INCONCLUSIVE_SQL_NO_ROWS')
    return encrypted

CANONICAL_INSERT = b'INSERT INTO `__Auth` VALUES '

def classify_operation(line):
    """Return a fixed failure label only; never return SQL contents or credentials."""
    if line.startswith(CANONICAL_INSERT):
        return None
    prefix = b'INSERT INTO `__Auth`'
    if line.startswith(prefix):
        suffix = line[len(prefix):]
        if re.match(rb'\s*\(', suffix):
            return 'INCONCLUSIVE_SQL_INSERT_COLUMN_LIST'
        values = re.match(rb'([ \t]+)(VALUES)\b', suffix, re.IGNORECASE)
        if values:
            # All three features are chosen from fixed categories, not SQL data.
            # This reports multiple simultaneous deviations in one safe label.
            before = ('STANDARD_BEFORE' if values.group(1) == b' '
                      else 'NONSTANDARD_BEFORE')
            keyword = ('UPPERCASE_VALUES' if values.group(2) == b'VALUES'
                       else 'NONSTANDARD_CASE')
            tail = suffix[values.end():]
            if tail.startswith(b' '):
                after = 'SPACE_AFTER'
            elif tail.startswith(b'('):
                after = 'NO_SPACE_AFTER'
            elif tail.startswith(b'\t'):
                after = 'TAB_AFTER'
            elif tail.startswith((b'\r', b'\n')):
                after = 'LINEBREAK_AFTER'
            else:
                after = 'OTHER_AFTER'
            return 'INCONCLUSIVE_SQL_VALUES_' + '_'.join((before, keyword, after))
        if re.match(rb'\s+SELECT\b', suffix, re.IGNORECASE):
            return 'INCONCLUSIVE_SQL_INSERT_SELECT'
        if re.match(rb'\s+SET\b', suffix, re.IGNORECASE):
            return 'INCONCLUSIVE_SQL_INSERT_SET'
        return 'INCONCLUSIVE_SQL_INSERT_OTHER'
    if line.startswith(b'REPLACE INTO `__Auth`'):
        return 'INCONCLUSIVE_SQL_REPLACE'
    if line.startswith(b'UPDATE `__Auth`'):
        return 'INCONCLUSIVE_SQL_UPDATE'
    if (line.startswith(b'INSERT INTO __Auth') or
        line.startswith(b'REPLACE INTO __Auth') or
        line.startswith(b'UPDATE __Auth')):
        return 'INCONCLUSIVE_SQL_UNQUOTED_TABLE'
    if line.startswith(b'INSERT IGNORE INTO `__Auth`'):
        return 'INCONCLUSIVE_SQL_INSERT_IGNORE'
    return None

def scan_sql(sql_gz):
    auth_schema_seen = False
    schema_done = False
    collecting_schema = False
    columns = []
    auth_inserts = False
    encrypted_count = 0
    decompressed_total = 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(sql_gz), mode='rb') as stream:
            while True:
                line = stream.readline(MAX_SQL_LINE + 1)
                if not line:
                    break
                require(len(line) <= MAX_SQL_LINE, 'INCONCLUSIVE_SQL_SIZE')
                decompressed_total += len(line)
                require(decompressed_total <= MAX_SQL, 'INCONCLUSIVE_SQL_SIZE')
                stripped = line.lstrip()
                if stripped.startswith(b'CREATE TABLE `__Auth`'):
                    require(not auth_schema_seen, 'INCONCLUSIVE_SCHEMA')
                    auth_schema_seen = True
                    collecting_schema = True
                    continue
                if collecting_schema:
                    if stripped.startswith(b')'):
                        collecting_schema = False
                        schema_done = True
                        continue
                    match = re.match(rb'`([a-zA-Z_]+)`\s+', stripped)
                    if match:
                        columns.append(match.group(1))
                    continue
                operation = classify_operation(stripped)
                if operation is not None:
                    raise Classified(operation)
                if stripped.startswith(CANONICAL_INSERT):
                    require(schema_done, 'INCONCLUSIVE_SCHEMA')
                    require(columns == EXPECTED_COLUMNS, 'INCONCLUSIVE_SCHEMA')
                    auth_inserts = True
                    encrypted_count += parse_values(stripped[len(CANONICAL_INSERT):])
    except (OSError, EOFError, gzip.BadGzipFile, zlib.error):
        raise Classified('INCONCLUSIVE_GZIP') from None
    require(auth_schema_seen and schema_done and columns == EXPECTED_COLUMNS,
            'INCONCLUSIVE_SCHEMA')
    return 'ENCRYPTED_ROWS_PRESENT' if encrypted_count else 'NO_ENCRYPTED_AUTH_ROWS'

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
        print('ARCHIVED_AUTH_FORMAT: ' + e.args[0])
        raise SystemExit(1) from None
    except Exception:
        print('ARCHIVED_AUTH_FORMAT: INCONCLUSIVE_INTERNAL_ERROR')
        raise SystemExit(1) from None
    print('ARCHIVED_AUTH_FORMAT: ' + output)
