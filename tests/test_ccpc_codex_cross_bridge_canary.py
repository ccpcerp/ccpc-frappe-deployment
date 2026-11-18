"""Docker-free negative tests for the reviewed synthetic canary safety gate."""
import importlib.util
import ipaddress
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
