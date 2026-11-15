"""NEW A3 G1 systemd credential metadata inventory. READ ONLY, NO KEY BYTES.

A missing systemctl property or host-visible runtime file is INCONCLUSIVE;
it does not prove service credential absence. Never print paths or values.
"""
import os
from pathlib import Path
import socket
import stat
import subprocess

SOURCE_KEY = Path('/etc/ccpc-https/ccpcerp.internal.key')
RUNTIME_KEY = Path('/run/credentials/caddy.service/ccpc_tls_key')
SERVICE = 'caddy.service'


def require(ok):
    if not ok:
        raise RuntimeError('review required')


def unit():
    p = subprocess.run(
        ('systemctl', 'show', SERVICE, '--no-pager',
         '--property=LoadState,ActiveState,UnitFileState,LoadCredential,LoadCredentialEx'),
        capture_output=True, text=True, check=True, timeout=20)
    require(len(p.stdout) < 16384)
    return dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)


def metadata(path):
    try:
        s = path.lstat()
    except OSError:
        return False, False
    regular = stat.S_ISREG(s.st_mode) and s.st_size > 0
    protected = regular and (stat.S_IMODE(s.st_mode) & 0o077) == 0
    return regular, protected


def flag(label, value):
    print('CCPC_NEW_A3_G1_' + label + '=' + ('YES' if value else 'NO'))


def audit():
    require(os.geteuid() == 0)
    require(os.environ.get('SUDO_USER') == 'ccpcadmin')
    require(socket.gethostname().split('.')[0] == 'ccpcerp-prod')
    require(not any(k in os.environ for k in ('DOCKER_HOST', 'DOCKER_CONTEXT')))
    u = unit()
    require(tuple(u.get(k) for k in ('LoadState', 'ActiveState', 'UnitFileState')) ==
            ('loaded', 'active', 'disabled'))
    for key, label in (('LoadCredential', 'LOADCREDENTIAL'),
                       ('LoadCredentialEx', 'LOADCREDENTIALEX')):
        flag('SYSTEMD_' + label + '_PROPERTY_PRESENT', key in u)
        flag('SYSTEMD_' + label + '_NAME_PRESENT', 'ccpc_tls_key' in u.get(key, ''))
    source_regular, source_protected = metadata(SOURCE_KEY)
    runtime_regular, runtime_protected = metadata(RUNTIME_KEY)
    flag('TLS_SOURCE_KEY_METADATA_PRESENT', source_regular)
    flag('TLS_SOURCE_KEY_PRIVATE_MODE', source_protected)
    flag('TLS_RUNTIME_CREDENTIAL_HOST_VISIBLE', runtime_regular)
    flag('TLS_RUNTIME_CREDENTIAL_PRIVATE_MODE', runtime_protected)
    print('CCPC_NEW_A3_G1_CREDENTIAL_METADATA_READONLY_INVENTORY_COMPLETE')


if __name__ == '__main__':
    try:
        audit()
    except Exception:
        print('CCPC_NEW_A3_G1_CREDENTIAL_METADATA_STOP_REVIEW_REQUIRED')
        raise SystemExit(1) from None
