"""Read-only NEW A3 G1 service states and TCP listener scope."""
import os
import socket
import subprocess


def read(*command):
    return subprocess.run(command, check=True, text=True,
                          capture_output=True, timeout=20).stdout


def unit(name):
    raw = read('systemctl', 'show', name, '--no-pager',
               '--property=LoadState,ActiveState,UnitFileState')
    data = dict(line.split('=', 1) for line in raw.splitlines() if '=' in line)
    assert {'LoadState', 'ActiveState', 'UnitFileState'} <= set(data)
    return data


def check():
    assert os.geteuid() == 0
    assert os.environ.get('SUDO_USER') == 'ccpcadmin'
    assert socket.gethostname().split('.')[0] == 'ccpcerp-prod'
    assert not any(key in os.environ for key in ('DOCKER_HOST', 'DOCKER_CONTEXT'))

    expected = {
        'docker.service': ('loaded', 'active', 'enabled'),
        'containerd.service': ('loaded', 'active', 'enabled'),
        'caddy.service': ('loaded', 'active', 'disabled'),
        'ccpc-erpnext-upstream.socket': ('loaded', 'active', 'disabled'),
        'ccpc-erpnext-upstream.service': ('loaded', 'active', 'static'),
    }
    for name, want in expected.items():
        got = unit(name)
        assert tuple(got[k] for k in ('LoadState', 'ActiveState', 'UnitFileState')) == want
    api = unit('caddy-api.service')
    assert api['LoadState'] in ('loaded', 'masked')
    assert api['ActiveState'] == 'inactive' and api['UnitFileState'] == 'masked'
    print('CCPC_NEW_A3_G1_SYSTEMD_BASELINE_PASS')

    gate = unit('ccpc-new-a3-g1-boot-gate.service')
    assert gate['LoadState'] == 'not-found' and gate['ActiveState'] == 'inactive'
    print('CCPC_NEW_A3_G1_GATE_UNIT_NOT_INSTALLED_PASS')

    listeners = {'443': set(), '8080': set()}
    for line in read('ss', '-H', '-ltn').splitlines():
        parts = line.split()
        assert len(parts) >= 5
        local = parts[3]
        address, delim, port = local.rpartition(':')
        assert delim
        if port in listeners:
            listeners[port].add(address.strip('[]'))
    assert listeners['443'] == {'192.168.50.186'}
    print('CCPC_NEW_A3_G1_HTTPS_443_LAN_BIND_PASS')
    assert listeners['8080'] == {'127.0.0.1'}
    print('CCPC_NEW_A3_G1_RELAY_8080_LOOPBACK_BIND_PASS')
    print('CCPC_NEW_A3_G1_SYSTEMD_LISTENERS_READONLY_PASS')


if __name__ == '__main__':
    try:
        check()
    except Exception:
        print('CCPC_NEW_A3_G1_SYSTEMD_LISTENERS_STOP_REVIEW_REQUIRED')
        raise SystemExit(1) from None
