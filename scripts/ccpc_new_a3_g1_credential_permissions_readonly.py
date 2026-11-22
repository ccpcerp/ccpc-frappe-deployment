"""NEW A3 G1 runtime credential permission metadata inventory; READ ONLY.

No key bytes, directory listings, credential values, or arbitrary paths printed.
The mode observations do not establish effective access across namespaces/ACLs.
"""
import os
from pathlib import Path
import socket
import stat
import subprocess

SERVICE = 'caddy.service'
ROOT_DIR = Path('/run/credentials')
SERVICE_DIR = ROOT_DIR / SERVICE
RUNTIME_KEY = SERVICE_DIR / 'ccpc_tls_key'


def require(ok):
    if not ok:
        raise RuntimeError('review required')


def get_mode(path, *, is_dir):
    info = path.lstat()
    require(stat.S_ISDIR(info.st_mode) if is_dir else stat.S_ISREG(info.st_mode))
    mode = stat.S_IMODE(info.st_mode)
    return mode, info.st_uid, info.st_gid


def output(name, value):
    print('CCPC_NEW_A3_G1_' + name + '=' + value)


def audit():
    require(os.geteuid() == 0)
    require(os.environ.get('SUDO_USER') == 'ccpcadmin')
    require(socket.gethostname().split('.')[0] == 'ccpcerp-prod')
    require(not any(k in os.environ for k in ('DOCKER_HOST', 'DOCKER_CONTEXT')))
    p = subprocess.run(('systemctl', 'show', SERVICE,
                        '--property=LoadState,ActiveState,UnitFileState', '--no-pager'),
                       check=True, capture_output=True, text=True, timeout=20)
    fields = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
    require(tuple(fields.get(k) for k in ('LoadState', 'ActiveState', 'UnitFileState')) ==
            ('loaded', 'active', 'disabled'))
    for name, path, is_dir in (
            ('CREDENTIAL_ROOT_DIR', ROOT_DIR, True),
            ('CREDENTIAL_SERVICE_DIR', SERVICE_DIR, True),
            ('RUNTIME_CREDENTIAL_FILE', RUNTIME_KEY, False)):
        mode, uid, gid = get_mode(path, is_dir=is_dir)
        output(name + '_MODE', format(mode, '04o'))
        output(name + '_OWNER_ROOT', 'YES' if uid == 0 else 'NO')
        output(name + '_GROUP_ROOT', 'YES' if gid == 0 else 'NO')
    print('CCPC_NEW_A3_G1_CREDENTIAL_PERMISSIONS_READONLY_INVENTORY_COMPLETE')


if __name__ == '__main__':
    try:
        audit()
    except Exception:
        print('CCPC_NEW_A3_G1_CREDENTIAL_PERMISSIONS_STOP_REVIEW_REQUIRED')
        raise SystemExit(1) from None
