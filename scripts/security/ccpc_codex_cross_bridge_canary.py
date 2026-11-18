#!/usr/bin/env python3
"""Bounded one-shot synthetic cross-bridge firewall canary for ccpcerpserver.

PLAN inspects only. RUN creates only a new, individually labeled synthetic
bridge and short-lived diagnostic containers, and cleans only matching IDs.
Never touches existing Compose stacks, volumes, host SSH, production IPs,
Codex credentials or the optional proxy. Never runs a Codex agent.
"""
import argparse
import ipaddress
import json
import os
import secrets
import subprocess
import sys
import time

HOST = "ccpcerpserver"
LAB = "ccpc_codex_dev_agent_lab"
AGENT = "ccpc_codex_dev_agent-agent-1"
DB = "ccpc_codex_dev_agent-db-1"
BRIDGE = "br-a88796be8a7a"
LAB_NET = ipaddress.ip_network("172.21.0.0/16")
LAB_GW = "172.21.0.1"
CANARY_NET = ipaddress.ip_network("198.19.255.240/28")  # RFC 2544 testing space
CANARY_GW = "198.19.255.241"
CANARY_IP = "198.19.255.242"
CANARY_PORT = 18080
TAG = "ccpc.codex.bridge-canary"
TAG_VALUE = "20261118"
DOCKER = ("docker", "--host", "unix:///var/run/docker.sock")
IMAGE = "frappe/bench:latest"

class Stop(Exception):
    pass


def call(argv, *, timeout=20, allow_fail=False):
    try:
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise Stop("tool invocation failed or timed out: " + argv[0]) from exc
    if result.returncode and not allow_fail:
        raise Stop("command failed: " + " ".join(argv[:2]))
    return result


def dc(*args, timeout=20, allow_fail=False):
    return call([*DOCKER, *args], timeout=timeout, allow_fail=allow_fail)


def obj(argv):
    return json.loads(call(argv).stdout)


def inspect(kind, name):
    values = json.loads(dc("inspect", "--type", kind, name).stdout)
    if len(values) != 1:
        raise Stop("expected exactly one " + kind)
    return values[0]


def check_lab(net, agent, db):
    opts = net.get("Options") or {}
    ipam = (net.get("IPAM") or {}).get("Config") or []
    if (net.get("Name") != LAB or net.get("Driver") != "bridge"
        or net.get("Internal") is not True or net.get("EnableIPv6")
        or len(ipam) != 1 or opts.get("com.docker.network.bridge.name")
        or str(ipaddress.ip_network(ipam[0]["Subnet"], strict=True)) != str(LAB_NET)
        or ipam[0].get("Gateway") != LAB_GW
        or "br-" + net.get("Id", "")[:12] != BRIDGE):
        raise Stop("lab network identity drift")
    if agent.get("Name") != "/" + AGENT or agent.get("State", {}).get("Running") is not False:
        raise Stop("Codex agent must be STOPPED")
    if agent.get("HostConfig", {}).get("RestartPolicy", {}).get("Name") not in ("no", ""):
        raise Stop("Codex agent restart policy must remain disabled")
    labels = (db.get("Config") or {}).get("Labels") or {}
    membership = (db.get("NetworkSettings") or {}).get("Networks") or {}
    if (db.get("Name") != "/" + DB
        or db.get("State", {}).get("Running") is not True
        or labels.get("com.docker.compose.project") != "ccpc_codex_dev_agent"
        or labels.get("com.docker.compose.service") != "db"
        or set(membership) != {LAB}
        or membership[LAB].get("NetworkID") != net.get("Id")):
        raise Stop("synthetic lab database identity drift")
    dbip = membership[LAB].get("IPAddress")
    if not dbip or ipaddress.ip_address(dbip) not in LAB_NET:
        raise Stop("invalid synthetic lab database IP")
    return dbip


def firewall_order(input_lines, user_lines, forward_lines):
    host = [x for x in input_lines.splitlines() if x.startswith("-A INPUT ")]
    rules = [x for x in user_lines.splitlines() if x.startswith("-A DOCKER-USER ")]
    fwd = [x for x in forward_lines.splitlines() if x.startswith("-A FORWARD ")]
    expected_host = ("-A INPUT -i " + BRIDGE + " -s 172.21.0.0/16 -m comment "
                     "--comment ccpc-codex-deny-host -j DROP")
    # iptables-nft may reserialize equivalent -s/-i selectors in either order.
    # Accept exactly these two forms, not arbitrary tokens or added matches.
    expected_host_source_first = (
        "-A INPUT -s 172.21.0.0/16 -i " + BRIDGE +
        " -m comment --comment ccpc-codex-deny-host -j DROP"
    )
    expected_in = ("-A DOCKER-USER ! -i " + BRIDGE + " -o " + BRIDGE +
                   " -m comment --comment ccpc-codex-deny-inbound -j DROP")
    expected_out = ("-A DOCKER-USER -i " + BRIDGE + " ! -o " + BRIDGE +
                    " -m comment --comment ccpc-codex-deny-outbound -j DROP")
    # Inspect EXACT first-match rules, not merely presence of a matching comment.
    if (not host or host[0] not in (expected_host, expected_host_source_first)
        or len(rules) < 2
        or rules[:2] != [expected_in, expected_out]
        or not fwd or fwd[0] != "-A FORWARD -j DOCKER-USER"
        or sum("ccpc-codex-deny-host" in x for x in host) != 1
        or sum("ccpc-codex-deny-inbound" in x for x in rules) != 1
        or sum("ccpc-codex-deny-outbound" in x for x in rules) != 1):
        raise Stop("firewall priority/placement changed; DO NOT run tests")
    return True


def check_firewall():
    if "nf_tables" not in call(["iptables", "--version"]).stdout:
        raise Stop("expected iptables-nft")
    firewall_order(call(["iptables", "-w", "5", "-S", "INPUT"]).stdout,
                   call(["iptables", "-w", "5", "-S", "DOCKER-USER"]).stdout,
                   call(["iptables", "-w", "5", "-S", "FORWARD"]).stdout)


def counts():
    data = call(["iptables", "-w", "5", "-nvxL", "DOCKER-USER"]).stdout
    result = {}
    for direction in ("inbound", "outbound"):
        lines = [x for x in data.splitlines() if "ccpc-codex-deny-" + direction in x]
        if len(lines) != 1:
            raise Stop("missing/duplicate firewall packet counter for " + direction)
        try:
            result[direction] = int(lines[0].split()[0])
        except (IndexError, ValueError) as exc:
            raise Stop("unreadable firewall packet counter") from exc
    return result


def existing_canaries():
    return dc("network", "ls", "-q", "--filter", "label=" + TAG + "=" + TAG_VALUE).stdout.strip()


def host_routes_clear():
    for route in obj(["ip", "-j", "-4", "route", "show", "table", "all"]):
        dst = route.get("dst", "default")
        if dst == "default":
            continue
        try:
            if ipaddress.ip_network(dst, strict=False).overlaps(CANARY_NET):
                raise Stop("synthetic reserved range conflicts with existing host route")
        except ValueError as exc:
            raise Stop("unrecognized host route") from exc
    ids = dc("network", "ls", "-q").stdout.split()
    if ids:
        nets = json.loads(dc("network", "inspect", *ids).stdout)
        for n in nets:
            for cfg in ((n.get("IPAM") or {}).get("Config") or []):
                subnet = cfg.get("Subnet")
                if subnet and ipaddress.ip_network(subnet, strict=False).overlaps(CANARY_NET):
                    raise Stop("synthetic reserved range conflicts with existing Docker network")


def preflight():
    if os.geteuid() != 0 or call(["hostname", "-s"]).stdout.strip() != HOST:
        raise Stop("wrong user/host (requires sudo on ccpcerpserver)")
    if dc("info", "--format", "{{.Name}}").stdout.strip() != HOST:
        raise Stop("wrong Docker daemon")
    net = inspect("network", LAB)
    db_ip = check_lab(net, inspect("container", AGENT), inspect("container", DB))
    check_firewall()
    if existing_canaries():
        raise Stop("existing canary-labeled network; manual review required")
    host_routes_clear()
    image_id = dc("image", "inspect", "--format", "{{.Id}}", IMAGE).stdout.strip()
    if not image_id.startswith("sha256:"):
        raise Stop("cached diagnostic image unavailable")
    if not dc("ps", "-q", "--filter", "label=" + TAG + "=" + TAG_VALUE).stdout.strip() == "":
        raise Stop("existing canary-labeled container; manual review required")
    print("PREFLIGHT: PASS (agent stopped; synthetic lab only)")
    print("FIREWALL PRIORITY: PASS")
    print("RESERVED CANARY SUBNET: AVAILABLE")
    return db_ip, image_id


def probe_code(host, port, want_connect):
    return ("import socket,errno,sys; "
            "host=sys.argv[1];port=int(sys.argv[2]);want=sys.argv[3]=='yes'; "
            "state='other'; "
            "\ntry:\n"
            " s=socket.create_connection((host,port),timeout=3);s.close();state='connected'\n"
            "except (TimeoutError,socket.timeout): state='blocked'\n"
            "except OSError as e:\n"
            " state='blocked' if e.errno in (errno.EHOSTUNREACH,errno.ENETUNREACH) else 'other'\n"
            "print('CONNECTIVITY:',state); "
            "sys.exit(0 if (state=='connected')==want and state!='other' else 1)")


def probe(network, name, image_id, host, port, want, *, extra=()):
    argv = ["run", "--rm", "--pull=never", "--name", name,
            "--label", TAG + "=" + TAG_VALUE,
            "--network", network, "--read-only", "--cap-drop=ALL",
            "--security-opt", "no-new-privileges", "--pids-limit", "64",
            "--memory", "192m", "--cpus", "0.5", *extra,
            "--entrypoint", "python3", image_id, "-c", probe_code(host, port, want),
            host, str(port), "yes" if want else "no"]
    result = dc(*argv, timeout=40, allow_fail=True)
    if result.returncode != 0:
        raise Stop("probe failed: " + name.split("-")[0])
    # Enforce probe result text too; no raw errors or addresses printed.
    expected = "CONNECTIVITY: connected" if want else "CONNECTIVITY: blocked"
    if expected not in result.stdout:
        raise Stop("probe did not supply expected result")


def lab_route_probe_code():
    # The cached frappe/bench:latest image has NO "ip" binary (owner-verified).
    # Use Python stdlib rtnetlink only inside this ephemeral NET_ADMIN namespace;
    # never add a route to the Docker host, existing agent, or persistent service.
    return r'''import errno
import ipaddress
import socket
import struct
import sys

NETWORK = ipaddress.IPv4Network("198.19.255.240/28")
GATEWAY = ipaddress.IPv4Address("172.21.0.1")
DEST = ipaddress.IPv4Address("198.19.255.242")
PORT = 18080

def attr(kind, payload):
    length = 4 + len(payload)
    return struct.pack("=HH", length, kind) + payload + b"\0" * ((-length) % 4)

def route_message(ifindex):
    # RTM_NEWROUTE for this container's namespace: exact /28 via lab gateway.
    rtm = struct.pack("=BBBBBBBBI", socket.AF_INET, NETWORK.prefixlen,
                      0, 0, 254, 3, 0, 1, 0)
    attrs = (attr(1, NETWORK.network_address.packed) +
             attr(5, GATEWAY.packed) +
             attr(4, struct.pack("=I", ifindex)))
    payload = rtm + attrs
    flags = 1 | 4 | 0x400 | 0x200  # REQUEST|ACK|CREATE|EXCLUSIVE
    return struct.pack("=IHHII", 16 + len(payload), 24, flags, 1, 0) + payload

def install_route():
    try:
        ifindex = socket.if_nametoindex("eth0")
        with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE) as netlink:
            netlink.bind((0, 0))
            netlink.settimeout(3)
            netlink.sendto(route_message(ifindex), (0, 0))
            response = netlink.recv(65535)
    except (OSError, AttributeError, ValueError):
        print("ROUTE SETUP: KERNEL REQUEST FAILED")
        return False
    offset = 0
    while offset + 16 <= len(response):
        length, mtype, _, seq, _ = struct.unpack_from("=IHHII", response, offset)
        if length < 16 or offset + length > len(response):
            break
        if seq == 1 and mtype == 2 and length >= 20:  # NLMSG_ERROR / ACK
            code, = struct.unpack_from("=i", response, offset + 16)
            if code != 0:
                print("ROUTE SETUP: KERNEL REJECTED", abs(code))
                return False
            return True
        offset += (length + 3) & ~3
    print("ROUTE SETUP: NO ACK")
    return False

def verify_route():
    # Read only the kernel's route table in this disposable container netns.
    def kernel_hex(address):
        return "%08X" % int.from_bytes(address.packed, "little")
    expect_dst = kernel_hex(NETWORK.network_address)
    expect_gateway = kernel_hex(GATEWAY)
    expect_mask = kernel_hex(NETWORK.netmask)
    try:
        with open("/proc/net/route", encoding="ascii") as routefile:
            for line in routefile:
                fields = line.split()
                if (len(fields) > 7 and fields[0] == "eth0" and
                    fields[1].upper() == expect_dst and
                    fields[2].upper() == expect_gateway and
                    fields[7].upper() == expect_mask and
                    int(fields[3], 16) & 3 == 3):
                    return True
    except (OSError, ValueError):
        pass
    print("ROUTE PROOF: MISSING OR DIFFERENT")
    return False

def main():
    if not install_route() or not verify_route():
        sys.exit(3)
    print("ROUTE PROOF: PASS")
    try:
        with socket.create_connection((str(DEST), PORT), timeout=3):
            print("LAB_TO_CANARY: REACHABLE")
            sys.exit(1)
    except (TimeoutError, socket.timeout):
        print("LAB_TO_CANARY: BLOCKED")
        print("LAB_TO_CANARY_REASON: TIMEOUT")
        sys.exit(0)
    except OSError as exc:
        if exc.errno in (errno.EHOSTUNREACH, errno.ENETUNREACH):
            print("LAB_TO_CANARY: BLOCKED")
            print("LAB_TO_CANARY_REASON: " +
                  ("HOST_UNREACHABLE" if exc.errno == errno.EHOSTUNREACH
                   else "NETWORK_UNREACHABLE"))
            sys.exit(0)
        print("LAB_TO_CANARY: UNEXPECTED SOCKET", exc.errno)
        sys.exit(2)

if __name__ == "__main__":
    main()
'''


def routable_probe(network, name, image_id, target):
    # Only this one ephemeral lab diagnostic container receives NET_ADMIN.
    if target != CANARY_IP or network != LAB:
        raise Stop("routed test target or lab identity changed")
    out = dc("run", "--rm", "--pull=never", "--name", name,
             "--label", TAG + "=" + TAG_VALUE,
             "--network", network, "--user", "0:0", "--read-only",
             "--cap-drop=ALL", "--cap-add=NET_ADMIN", "--security-opt", "no-new-privileges",
             "--pids-limit", "64", "--memory", "192m", "--cpus", "0.5",
             "--entrypoint", "python3", image_id, "-c", lab_route_probe_code(),
             timeout=40, allow_fail=True)
    if out.returncode or "ROUTE PROOF: PASS" not in out.stdout or "LAB_TO_CANARY: BLOCKED" not in out.stdout:
        # Only a bounded, classified status from our own disposable probe is
        # returned. Do not echo Docker runtime output or secret-bearing logs.
        reason = next((line[:96] for line in reversed(out.stdout.splitlines())
                       if line.startswith(("ROUTE SETUP:", "ROUTE PROOF:", "LAB_TO_CANARY:"))),
                      "PROBE EXIT WITHOUT CLASSIFIED STATUS")
        raise Stop("lab-to-canary routed test incomplete (" + reason + ")")
    classified = [line for line in out.stdout.splitlines()
                  if line.startswith("LAB_TO_CANARY_REASON: ")]
    if len(classified) != 1 or classified[0] not in (
        "LAB_TO_CANARY_REASON: TIMEOUT",
        "LAB_TO_CANARY_REASON: HOST_UNREACHABLE",
        "LAB_TO_CANARY_REASON: NETWORK_UNREACHABLE",
    ):
        raise Stop("lab-to-canary route-probe classification missing or changed")
    return classified[0]


def confirm_counter_deltas(before, after):
    deltas = {direction: after[direction] - before[direction]
              for direction in ("inbound", "outbound")}
    if min(deltas.values()) <= 0:
        raise Stop("firewall counter deltas insufficient: inbound=" +
                   str(deltas["inbound"]) + " outbound=" + str(deltas["outbound"]))
    return deltas


def cleanup(network_id, listener_id, prefix):
    # Exact matching IDs/labels only; never global rm, prune or stop.
    ok = True
    for name in (prefix + "-same", prefix + "-from-canary", prefix + "-from-lab", prefix + "-lab-positive"):
        result = dc("inspect", "--type", "container", name, allow_fail=True)
        if result.returncode:
            continue
        data = json.loads(result.stdout)
        if len(data) != 1 or (data[0].get("Config") or {}).get("Labels", {}).get(TAG) != TAG_VALUE:
            ok = False
            continue
        # A still-running --rm probe is unexpected: leave it for inspection instead of force-killing.
        ok = False
    if listener_id:
        result = dc("inspect", "--type", "container", listener_id, allow_fail=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if (len(data) == 1 and data[0].get("Id") == listener_id
                and (data[0].get("Config") or {}).get("Labels", {}).get(TAG) == TAG_VALUE
                and (data[0].get("Name") or "") == "/" + prefix + "-listener"):
                try:
                    dc("stop", "--time", "5", listener_id, timeout=20)
                except Stop:
                    ok = False
            else:
                ok = False
    if network_id and ok:
        # Docker --rm listener teardown may be asynchronous. Wait only for
        # this new, labeled network to become empty; never disconnect peers.
        for attempt in range(5):
            result = dc("inspect", "--type", "network", network_id, allow_fail=True)
            if result.returncode:
                ok = False
                break
            net = json.loads(result.stdout)
            if (len(net) != 1 or net[0].get("Id") != network_id
                or (net[0].get("Labels") or {}).get(TAG) != TAG_VALUE):
                ok = False
                break
            if not net[0].get("Containers"):
                try:
                    dc("network", "rm", network_id, timeout=20)
                except Stop:
                    ok = False
                break
            if attempt == 4:
                ok = False
            else:
                time.sleep(0.3)
    if not ok:
        print("CLEANUP: REVIEW REQUIRED (only labeled temporary resources)")
    else:
        print("CLEANUP: PASS (temporary canary resources removed)")
    return ok


def execute(db_ip, image_id):
    token = secrets.token_hex(4)
    prefix = "ccpc-canary-" + token
    net_name = prefix + "-net"
    network_id = None
    listener_id = None
    passed = False
    cleaned = False
    try:
        # Non-internal temporary network has a default route; only synthetic probes are attached.
        network_id = dc("network", "create", "--driver", "bridge",
                        "--subnet", str(CANARY_NET), "--gateway", CANARY_GW,
                        "--label", TAG + "=" + TAG_VALUE, net_name).stdout.strip()
        if not network_id:
            raise Stop("canary network creation did not return an ID")
        created = inspect("network", network_id)
        if (created.get("Name") != net_name or created.get("Internal") is not False
            or (created.get("Labels") or {}).get(TAG) != TAG_VALUE
            or created.get("EnableIPv6") or created.get("Driver") != "bridge"):
            raise Stop("canary network changed after creation")
        if created.get("Containers"):
            raise Stop("canary bridge unexpectedly acquired another endpoint")
        check_firewall()
        listener = '''import socket
s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(("0.0.0.0",18080));s.listen(8)
while True:
 c,_=s.accept();c.close()
'''
        listener_id = dc("run", "-d", "--rm", "--pull=never",
                         "--name", prefix + "-listener", "--label", TAG + "=" + TAG_VALUE,
                         "--network", net_name, "--ip", CANARY_IP,
                         "--user", "1000:1000", "--read-only", "--cap-drop=ALL",
                         "--security-opt", "no-new-privileges", "--pids-limit", "64",
                         "--memory", "192m", "--cpus", "0.5", "--entrypoint", "python3",
                         image_id, "-c", listener).stdout.strip()
        if not listener_id:
            raise Stop("synthetic canary listener not created")
        running_listener = inspect("container", listener_id)
        networks = (running_listener.get("NetworkSettings") or {}).get("Networks") or {}
        if (running_listener.get("Name") != "/" + prefix + "-listener"
            or (running_listener.get("Config") or {}).get("Labels", {}).get(TAG) != TAG_VALUE
            or (running_listener.get("State") or {}).get("Running") is not True
            or (running_listener.get("HostConfig") or {}).get("PortBindings")
            or running_listener.get("Mounts")
            or set(networks) != {net_name}
            or networks[net_name].get("IPAddress") != CANARY_IP):
            raise Stop("synthetic listener identity/privilege boundary changed")
        print("CANARY NETWORK/HEALTH: CREATED (no ports published)")
        # Bound the listener startup rather than treating connection-refused as a firewall pass.
        for attempt in range(5):
            try:
                probe(net_name, prefix + "-same", image_id, CANARY_IP, CANARY_PORT, True,
                      extra=("--user", "1000:1000"))
                break
            except Stop:
                if attempt == 4:
                    raise
                time.sleep(0.3)
        probe(LAB, prefix + "-lab-positive", image_id, db_ip, 3306, True,
              extra=("--user", "1000:1000"))
        print("SYNTHETIC SAME-BRIDGE CONTROLS: PASS")
        before = counts()
        probe(net_name, prefix + "-from-canary", image_id, db_ip, 3306, False,
              extra=("--user", "1000:1000"))
        negative_reason = routable_probe(LAB, prefix + "-from-lab", image_id, CANARY_IP)
        print(negative_reason)
        after = counts()
        endpoints = (inspect("network", network_id).get("Containers") or {})
        if set(endpoints) != {listener_id}:
            raise Stop("unexpected endpoint joined the temporary canary network")
        confirm_counter_deltas(before, after)
        check_firewall()
        if inspect("container", AGENT).get("State", {}).get("Running") is not False:
            raise Stop("agent unexpectedly started")
        print("CROSS-BRIDGE INBOUND: BLOCKED, COUNTER INCREASED")
        print("CROSS-BRIDGE OUTBOUND: BLOCKED WITH EXPLICIT ROUTE, COUNTER INCREASED")
        passed = True
    finally:
        try:
            cleaned = cleanup(network_id, listener_id, prefix)
        except (Stop, ValueError, KeyError):
            print("CLEANUP: REVIEW REQUIRED (no broad cleanup authorized)")
            cleaned = False
    if not passed or not cleaned:
        raise Stop("canary incomplete; Codex remains on HOLD")
    print("ONE-SHOT SYNTHETIC CROSS-BRIDGE CANARY: PASS")
    print("STILL HELD: Codex agent, online proxy, reboot persistence, persistent DEV")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "run"))
    args = parser.parse_args()
    try:
        db_ip, image_id = preflight()
        if args.action == "plan":
            print("PLAN ONLY: no network/container/firewall changes")
            print("RUN requires one fresh temporary Docker bridge and disposable probes")
            return 0
        execute(db_ip, image_id)
        return 0
    except (Stop, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("STOP:", str(exc))
        print("NO CODEX AGENT OR PROXY START AUTHORIZED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
