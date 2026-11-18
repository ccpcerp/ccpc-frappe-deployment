"""Docker-free negative tests for the reviewed synthetic canary safety gate."""
import importlib.util
import ipaddress
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/security/ccpc_codex_cross_bridge_canary.py'
spec = importlib.util.spec_from_file_location('ccpc_bridge_canary', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def policy():
    return (
        '-A INPUT -i br-a88796be8a7a -s 172.21.0.0/16 -m comment --comment ccpc-codex-deny-host -j DROP',
        '-A DOCKER-USER ! -i br-a88796be8a7a -o br-a88796be8a7a -m comment --comment ccpc-codex-deny-inbound -j DROP\n'
        '-A DOCKER-USER -i br-a88796be8a7a ! -o br-a88796be8a7a -m comment --comment ccpc-codex-deny-outbound -j DROP',
        '-A FORWARD -j DOCKER-USER'
    )


def fixture():
    net = {'Name':m.LAB,'Driver':'bridge','Internal':True,'EnableIPv6':False,
           'IPAM':{'Config':[{'Subnet':'172.21.0.0/16','Gateway':'172.21.0.1'}]},
           'Options':{},'Id':m.BRIDGE[3:]+'0'*52}
    agent = {'Name':'/'+m.AGENT,'State':{'Running':False},'HostConfig':{'RestartPolicy':{'Name':'no'}}}
    db = {'Name':'/'+m.DB,'State':{'Running':True},
          'Config':{'Labels':{'com.docker.compose.project':'ccpc_codex_dev_agent',
                              'com.docker.compose.service':'db'}},
          'NetworkSettings':{'Networks':{m.LAB:{'NetworkID':net['Id'],'IPAddress':'172.21.0.8'}}}}
    return net,agent,db


class CanarySafetyTests(unittest.TestCase):
    def test_exact_firewall_order(self):
        self.assertTrue(m.firewall_order(*policy()))

    def test_observed_iptables_nft_input_selector_order_is_accepted(self):
        # Owner's 2026-11-18 read-only iptables -S output; no firewall edit.
        host, user, forward = policy()
        observed_host = ('-P INPUT ACCEPT\n'
                         '-A INPUT -s 172.21.0.0/16 -i br-a88796be8a7a '
                         '-m comment --comment ccpc-codex-deny-host -j DROP')
        observed_user = '-N DOCKER-USER\n' + user
        observed_forward = '-P FORWARD DROP\n' + forward + '\n-A FORWARD -j DOCKER-FORWARD'
        self.assertTrue(m.firewall_order(observed_host, observed_user, observed_forward))

    def test_host_rule_first_match_remains_required(self):
        h, u, f = policy()
        h = '-A INPUT -j ACCEPT\n' + h.replace(
            '-i br-a88796be8a7a -s 172.21.0.0/16',
            '-s 172.21.0.0/16 -i br-a88796be8a7a')
        with self.assertRaises(m.Stop):
            m.firewall_order(h, u, f)

    def test_host_selector_drift_still_rejected(self):
        h, u, f = policy()
        h = h.replace('-i br-a88796be8a7a -s 172.21.0.0/16',
                      '-s 172.21.0.0/16 -i br-a88796be8a7a')
        for changed in (h.replace('172.21.0.0/16', '172.22.0.0/16'),
                        h.replace('br-a88796be8a7a', 'br-other'),
                        h.replace('-j DROP', '-j ACCEPT'),
                        h.replace('-j DROP', '-m tcp -j DROP')):
            with self.subTest(changed=changed), self.assertRaises(m.Stop):
                m.firewall_order(changed, u, f)

    def test_route_probe_has_no_external_ip_binary_dependency(self):
        code = m.lab_route_probe_code()
        compile(code, "<synthetic-route-probe>", "exec")
        for bad in ('subprocess', 'shutil.which', 'os.system', '/bin/ip', '/sbin/ip'):
            self.assertNotIn(bad, code)
        self.assertIn('NETLINK_ROUTE', code)
        self.assertIn('198.19.255.240/28', code)
        self.assertIn('172.21.0.1', code)
        self.assertIn('LAB_TO_CANARY: BLOCKED', code)

    def test_route_message_is_exact_scoped_rtnetlink(self):
        namespace = {'__name__': 'synthetic_route_unit'}
        exec(compile(m.lab_route_probe_code(), '<synthetic-route-probe>', 'exec'),
             namespace)
        data = namespace['route_message'](2)
        self.assertEqual(struct.unpack_from('=IHHII', data),
                         (len(data), 24, 0x605, 1, 0))
        self.assertEqual(struct.unpack_from('=BBBBBBBBI', data, 16),
                         (2, 28, 0, 0, 254, 3, 0, 1, 0))
        self.assertEqual(data[28:], bytes.fromhex(
            '08000100c613fff008000500ac1500010800040002000000'))

    def test_route_proof_does_not_accept_wrong_gateway(self):
        from io import StringIO
        namespace = {'__name__': 'synthetic_route_unit'}
        exec(compile(m.lab_route_probe_code(), '<synthetic-route-probe>', 'exec'),
             namespace)
        fields = 'eth0 F0FF13C6 010015AC 0003 0 0 0 F0FFFFFF 0 0 0\n'
        with patch('builtins.open', return_value=StringIO(fields)):
            self.assertTrue(namespace['verify_route']())
        with patch('builtins.open', return_value=StringIO(
                fields.replace('010015AC', '020015AC'))):
            self.assertFalse(namespace['verify_route']())

    def test_routable_probe_rejects_other_network_and_target(self):
        with self.assertRaises(m.Stop):
            m.routable_probe('some-other-network', 'probe', 'fake-image', m.CANARY_IP)
        with self.assertRaises(m.Stop):
            m.routable_probe(m.LAB, 'probe', 'fake-image', '198.19.255.243')

    def test_counter_deltas_are_required_in_both_directions(self):
        before = {'inbound': 5, 'outbound': 0}
        self.assertEqual(m.confirm_counter_deltas(
            before, {'inbound': 6, 'outbound': 1}),
            {'inbound': 1, 'outbound': 1})
        for after in ({'inbound': 6, 'outbound': 0},
                      {'inbound': 5, 'outbound': 1},
                      {'inbound': 4, 'outbound': 1}):
            with self.subTest(after=after), self.assertRaisesRegex(
                    m.Stop, 'firewall counter deltas insufficient'):
                m.confirm_counter_deltas(before, after)

    def test_route_negative_probe_returns_classified_reason(self):
        from types import SimpleNamespace
        response = SimpleNamespace(returncode=0, stdout=(
            'ROUTE PROOF: PASS\nLAB_TO_CANARY: BLOCKED\n'
            'LAB_TO_CANARY_REASON: HOST_UNREACHABLE\n'))
        with patch.object(m, 'dc', return_value=response):
            self.assertEqual(
                m.routable_probe(m.LAB, 'ccpc-canary-1234-from-lab',
                                 'fake-image-id', m.CANARY_IP),
                'LAB_TO_CANARY_REASON: HOST_UNREACHABLE')

    def test_route_negative_probe_rejects_missing_or_changed_reason(self):
        from types import SimpleNamespace
        for ending in ('', 'LAB_TO_CANARY_REASON: UNKNOWN\n',
                       'LAB_TO_CANARY_REASON: TIMEOUT\n'
                       'LAB_TO_CANARY_REASON: NETWORK_UNREACHABLE\n'):
            response = SimpleNamespace(returncode=0, stdout=(
                'ROUTE PROOF: PASS\nLAB_TO_CANARY: BLOCKED\n' + ending))
            with self.subTest(ending=ending), patch.object(
                    m, 'dc', return_value=response), self.assertRaises(m.Stop):
                m.routable_probe(m.LAB, 'ccpc-canary-1234-from-lab',
                                 'fake-image-id', m.CANARY_IP)

    def test_preceding_accept_is_rejected(self):
        h,u,f=policy()
        with self.assertRaises(m.Stop):
            m.firewall_order(h, '-A DOCKER-USER -j ACCEPT\n'+u,f)

    def test_changed_interface_is_rejected(self):
        h,u,f=policy()
        with self.assertRaises(m.Stop):
            m.firewall_order(h,u.replace('br-a88796be8a7a','br-other'),f)

    def test_missing_or_duplicate_drop_is_rejected(self):
        h,u,f=policy()
        for value in (u.split('\n')[0],u+'\n'+u.split('\n')[1]):
            with self.assertRaises(m.Stop):
                m.firewall_order(h,value,f)

    def test_exact_lab(self):
        self.assertEqual(m.check_lab(*fixture()),'172.21.0.8')

    def test_agent_running_rejected(self):
        n,a,d=fixture();a['State']['Running']=True
        with self.assertRaises(m.Stop):m.check_lab(n,a,d)

    def test_agent_autostart_rejected(self):
        n,a,d=fixture();a['HostConfig']['RestartPolicy']['Name']='unless-stopped'
        with self.assertRaises(m.Stop):m.check_lab(n,a,d)

    def test_db_outside_lab_rejected(self):
        n,a,d=fixture();d['NetworkSettings']['Networks']['other']={'IPAddress':'10.1.1.1'}
        with self.assertRaises(m.Stop):m.check_lab(n,a,d)

    def test_wrong_network_identity_rejected(self):
        n,a,d=fixture();n['Internal']=False
        with self.assertRaises(m.Stop):m.check_lab(n,a,d)

    def test_existing_route_conflict_rejected(self):
        with patch.object(m,'obj',return_value=[{'dst':'198.19.255.240/28'}]):
            with self.assertRaises(m.Stop):m.host_routes_clear()

    def test_unknown_listener_is_never_stopped(self):
        class Response:
            def __init__(self, code=0, data=''):
                self.returncode=code; self.stdout=data
        seen=[]
        def fake_dc(*args,**kwargs):
            seen.append(args)
            if args[0]=='inspect' and args[3]=='the-listener-id':
                return Response(data='[{"Id":"the-listener-id","Name":"/different", "Config":{"Labels":{}}}]')
            return Response(code=1)
        with patch.object(m,'dc',side_effect=fake_dc):
            self.assertFalse(m.cleanup(None,'the-listener-id','ccpc-canary-aabbccdd'))
        self.assertFalse(any(x[0] in ('stop','rm','network') for x in seen))

    def test_counter_parser_fail_closed(self):
        class Response:
            stdout='pkts bytes target prot opt in out source destination\n'
        with patch.object(m,'call',return_value=Response()):
            with self.assertRaises(m.Stop):m.counts()

    def test_probes_use_hardcoded_synthetic_targets(self):
        code=m.probe_code('127.0.0.1',12345,False)
        compile(code,'<probe>', 'exec')
        text=SOURCE.read_text()
        for forbidden in ('docker system prune','docker compose down','--privileged',
                          '--network host','192.168.50.186','docker exec frappe_docker-'):
            self.assertNotIn(forbidden,text)
        self.assertIn('--cap-add=NET_ADMIN',text)
        self.assertIn('--cap-drop=ALL',text)

if __name__=='__main__':unittest.main()
