"""NEW A3 G1 TLS-drop-in and socket reverse-edge inventory; READ ONLY.

Compares installed metadata/directives to GitHub PR28 review expectations.
Never prints files, environment values, credentials, arbitrary unit names or paths.
This is not an endorsement of HTTPS security or a reboot-readiness test.
"""
import os
from pathlib import Path
import socket
import stat
import subprocess

CADDY_DROPIN = Path('/etc/systemd/system/caddy.service.d/ccpc-tls-credentials.conf')
EXPECTED_LINES = (
    '[Service]',
    'LoadCredential=ccpc_tls_key:/etc/ccpc-https/ccpcerp.internal.key',
    'Environment="CCPC_TLS_FULLCHAIN_FILE=/etc/caddy/ccpc-https/ccpcerp.internal.50yr.crt.pem"',
    'Environment="CCPC_TLS_PRIVATE_KEY_FILE=%d/ccpc_tls_key"',
)
SOCKET = 'ccpc-erpnext-upstream.socket'
RELAY = 'ccpc-erpnext-upstream.service'


def require(condition):
    if not condition:
        raise RuntimeError('review required')


def unit(name):
    fields = ('LoadState,ActiveState,UnitFileState,DropInPaths,Environment,'
              'LoadCredential,RequiredBy,WantedBy,TriggeredBy')
    result = subprocess.run(
        ('systemctl', 'show', name, '--no-pager', '--property=' + fields),
        check=True, text=True, capture_output=True, timeout=20)
    require(len(result.stdout) < 32768)
    return dict(line.split('=', 1) for line in result.stdout.splitlines()
                if '=' in line)


def flag(name, value):
    print('CCPC_NEW_A3_G1_' + name + '=' + ('YES' if value else 'NO'))


def inspect():
    require(os.geteuid() == 0)
    require(os.environ.get('SUDO_USER') == 'ccpcadmin')
    require(socket.gethostname().split('.')[0] == 'ccpcerp-prod')
    require(not any(k in os.environ for k in ('DOCKER_HOST', 'DOCKER_CONTEXT')))

    caddy = unit('caddy.service')
    sock = unit(SOCKET)
    require(tuple(caddy.get(k) for k in ('LoadState', 'ActiveState', 'UnitFileState'))
            == ('loaded', 'active', 'disabled'))
    require(tuple(sock.get(k) for k in ('LoadState', 'ActiveState', 'UnitFileState'))
            == ('loaded', 'active', 'disabled'))

    # Do not open unknown drop-ins, or print any configured path.
    paths = caddy.get('DropInPaths', '').split()
    expected_only = paths == [str(CADDY_DROPIN)]
    flag('CADDY_ONLY_REVIEWED_TLS_DROPIN', expected_only)
    protected, template = False, False
    if str(CADDY_DROPIN) in paths:
        try:
            s = CADDY_DROPIN.lstat()
            protected = (stat.S_ISREG(s.st_mode) and s.st_uid == 0 and
                         (stat.S_IMODE(s.st_mode) & 0o022) == 0)
            if protected:
                text = CADDY_DROPIN.read_text(encoding='utf-8')
                lines = tuple(line.strip() for line in text.splitlines()
                              if line.strip() and not line.lstrip().startswith(('#', ';')))
                template = lines == EXPECTED_LINES
        except (OSError, UnicodeError):
            pass
    flag('CADDY_TLS_DROPIN_ROOT_PROTECTED', protected)
    flag('CADDY_TLS_DROPIN_REVIEW_TEMPLATE_MATCH', template)

    # Read effective service property *names* only, never show their values.
    flag('CADDY_EFFECTIVE_TLS_CREDENTIAL_DECLARED',
         'ccpc_tls_key:' in caddy.get('LoadCredential', ''))
    env = caddy.get('Environment', '')
    flag('CADDY_EFFECTIVE_TLS_ENV_NAMES_PRESENT',
         'CCPC_TLS_FULLCHAIN_FILE=' in env and 'CCPC_TLS_PRIVATE_KEY_FILE=' in env)

    reverse = set()
    for key in ('RequiredBy', 'WantedBy', 'TriggeredBy'):
        reverse.update(sock.get(key, '').split())
    flag('SOCKET_REVERSE_HAS_EXPECTED_RELAY', RELAY in reverse)
    flag('SOCKET_REVERSE_OTHER_UNITS_PRESENT', bool(reverse - {RELAY}))
    print('CCPC_NEW_A3_G1_TLS_DROPIN_REVERSE_READONLY_INVENTORY_COMPLETE')


if __name__ == '__main__':
    try:
        inspect()
    except Exception:
        print('CCPC_NEW_A3_G1_TLS_DROPIN_REVERSE_STOP_REVIEW_REQUIRED')
        raise SystemExit(1) from None
