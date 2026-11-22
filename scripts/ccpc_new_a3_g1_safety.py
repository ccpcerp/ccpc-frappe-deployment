"""Review-only fail-closed Caddy/boot dependency checks for NEW A3 G1.

No service or Docker mutation. The caller enforces its own activation interlock.
Never log raw unit fields, TLS files, response content, or private data.
"""
from contextlib import contextmanager
from pathlib import Path
import re
import stat
import subprocess
import time

CADDYFILE = Path('/etc/caddy/Caddyfile')
TLS_DROPIN = Path('/etc/systemd/system/caddy.service.d/ccpc-tls-credentials.conf')
SOURCE_KEY = Path('/etc/ccpc-https/ccpcerp.internal.key')
CADDY_CONFIG = (
    '{', 'admin off', 'auto_https off',
    'servers 192.168.50.186:443 {', 'protocols h1 h2',
    'strict_sni_host on', '}', '}',
    'https://ccpcerp.internal:443 {', 'bind 192.168.50.186',
    'tls {$CCPC_TLS_FULLCHAIN_FILE} {$CCPC_TLS_PRIVATE_KEY_FILE}',
    'reverse_proxy 127.0.0.1:8080', '}',
)
TLS_DROPIN_LINES = (
    '[Service]',
    'LoadCredential=ccpc_tls_key:/etc/ccpc-https/ccpcerp.internal.key',
    'Environment="CCPC_TLS_FULLCHAIN_FILE=/etc/caddy/ccpc-https/ccpcerp.internal.50yr.crt.pem"',
    'Environment="CCPC_TLS_PRIVATE_KEY_FILE=%d/ccpc_tls_key"',
)


class SafetyStop(Exception):
    """Non-disclosing abort. Callers must not expose the underlying values."""


def require(condition):
    if not condition:
        raise SafetyStop()


@contextmanager
def deadline_guard(r0, deadline):
    """Temporarily bound every R0 Docker/systemd subprocess to a global clock.

    R0.docker and R0.read_flags call R0.invoke via module globals. Swapping
    the callable ONLY on this freshly imported in-memory R0 module preserves
    the SHA-pinned R0 file, and finally restores the original callable.
    """
    original = r0.invoke

    def invoke(command, *, data=None):
        remaining = deadline - time.monotonic()
        require(remaining > 0)
        try:
            result = subprocess.run(command, input=data, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    timeout=min(35, remaining), check=True)
        except (OSError, subprocess.SubprocessError):
            raise SafetyStop() from None
        require(time.monotonic() <= deadline)
        return result.stdout

    r0.invoke = invoke
    try:
        yield
    finally:
        r0.invoke = original


def approved_file(path, *, private=False):
    try:
        s = path.lstat()
        require(stat.S_ISREG(s.st_mode) and s.st_uid == 0)
        mode = stat.S_IMODE(s.st_mode)
        require((mode & (0o077 if private else 0o022)) == 0)
    except (OSError, ValueError):
        raise SafetyStop() from None


def expected_lines(path):
    try:
        content = path.read_text(encoding='utf-8')
        require(len(content) <= 16384)
        return tuple(line.strip() for line in content.splitlines()
                     if line.strip() and not line.lstrip().startswith(('#', ';')))
    except (OSError, UnicodeError):
        raise SafetyStop() from None


def properties(r0, service):
    raw = r0.invoke(('systemctl', 'show', service,
                     '--property=LoadState,ActiveState,UnitFileState,DropInPaths,ExecStart,'
                     'RequiredBy,WantedBy,TriggeredBy,Requires,After,Environment',
                     '--no-pager'))
    require(len(raw) < 32768)
    try:
        return dict(line.split('=', 1) for line in raw.decode('utf-8').splitlines()
                    if '=' in line)
    except UnicodeError:
        raise SafetyStop() from None


def validate_gateway_config(r0):
    """Check the reviewed *disk* config and loaded unit edges before start.

    This does not prove running Caddy runtime config, cert trust, or WAN denial.
    """
    for path in (CADDYFILE, TLS_DROPIN):
        approved_file(path)
    approved_file(SOURCE_KEY, private=True)
    require(expected_lines(CADDYFILE) == CADDY_CONFIG)
    require(expected_lines(TLS_DROPIN) == TLS_DROPIN_LINES)
    caddy = properties(r0, 'caddy.service')
    upstream = properties(r0, 'ccpc-erpnext-upstream.socket')
    relay = properties(r0, 'ccpc-erpnext-upstream.service')
    require(caddy.get('LoadState') == 'loaded' and
            caddy.get('UnitFileState') == 'disabled' and
            upstream.get('LoadState') == 'loaded' and
            upstream.get('UnitFileState') == 'disabled')
    require(caddy.get('DropInPaths', '').split() == [str(TLS_DROPIN)])
    require(not upstream.get('DropInPaths', '').strip() and
            not relay.get('DropInPaths', '').strip())
    require(bool(re.search(r'--config(?:=|\s+)/etc/caddy/Caddyfile(?:\s|[;}]|$)',
                           caddy.get('ExecStart', ''))))
    require('CCPC_TLS_FULLCHAIN_FILE=' in caddy.get('Environment', '') and
            'CCPC_TLS_PRIVATE_KEY_FILE=' in caddy.get('Environment', ''))
    for field in ('RequiredBy', 'WantedBy', 'TriggeredBy'):
        require(not caddy.get(field, '').strip())
    reverse = set()
    for field in ('RequiredBy', 'WantedBy', 'TriggeredBy'):
        reverse.update(upstream.get(field, '').split())
    require(reverse == {'ccpc-erpnext-upstream.service'})
    require('ccpc-erpnext-upstream.socket' in relay.get('Requires', '').split())
    require('ccpc-erpnext-upstream.socket' in relay.get('After', '').split())
    return True


def validate_tcp_bindings(r0, *, gateway_state):
    """Require cold gateway ports empty, or a LAN-only known pilot listener."""
    require(gateway_state in ('cold', 'pilot'))
    raw = r0.invoke(('ss', '-H', '-ltn'))
    require(len(raw) <= 262144)
    listeners = {'443': set(), '8080': set()}
    try:
        for line in raw.decode('utf-8').splitlines():
            fields = line.split()
            require(len(fields) >= 5)
            addr, sep, port = fields[3].rpartition(':')
            require(sep == ':')
            if port in listeners:
                listeners[port].add(addr.strip('[]'))
    except UnicodeError:
        raise SafetyStop() from None
    expected = {'443': set(), '8080': set()} if gateway_state == 'cold' else {
        '443': {'192.168.50.186'}, '8080': {'127.0.0.1'}}
    require(listeners == expected)
    # The reviewed Caddy template permits HTTP/1.1 and HTTP/2 only; UDP443
    # (QUIC or a different server) is not an approved exposure surface.
    udp = r0.invoke(('ss', '-H', '-lun'))
    require(len(udp) <= 262144)
    try:
        for line in udp.decode('utf-8').splitlines():
            fields = line.split()
            require(len(fields) >= 5)
            require(fields[3].rpartition(':')[2] != '443')
    except UnicodeError:
        raise SafetyStop() from None
    return True
