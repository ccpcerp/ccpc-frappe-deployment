#!/usr/bin/env python3
"""Read-only firewall pre-enforcement review for a PROPOSED Codex proxy bridge.

No apply, rollback, iptables INSERT/DELETE, Docker create/start, DNS, or TCP probes.
Must not be interpreted as authorization to start Codex/Squid or create a bridge.
The existing host-only lab firewall script is separate and MUST remain intact.
"""
import ipaddress
import json
import os
import shlex
import subprocess
import sys

from ccpc_firewall_rule_order import (
    combined_rule_order_valid,
    proxy_rule_specs,
)

HOST = "ccpcerpserver"
PROJECT = "ccpc_codex_dev_agent"
OLD_LAB = PROJECT + "_lab"
NEW_NETWORK = PROJECT + "_proxy_clients"
BRIDGE = "br-ccpc-cdxpx"
SUBNET = ipaddress.ip_network("172.30.250.0/29")
OLD_SUBNET = ipaddress.ip_network("172.21.0.0/16")


def fail():
    print("STOP: safe proxy bridge preflight unavailable")
    raise SystemExit(1)


def command(args, missing_ok=False):
    try:
        p = subprocess.run(args, text=True, capture_output=True, timeout=25)
    except (OSError, subprocess.TimeoutExpired):
        fail()
    if missing_ok:
        if p.returncode not in (0, 1):
            fail()
        return p.returncode == 0
    if p.returncode:
        fail()
    return p.stdout


def check_rule(chain, tokens):
    # 'iptables -C' checks only; it does not append/insert or flush.
    return command(["iptables", "-w", "5", "-C", chain, *tokens],
                   missing_ok=True)


def rules_for_new_bridge():
    # Shared reviewed source of exact proxy DROP specifications.
    return proxy_rule_specs()


def first_forward_jump_is_docker_user():
    entries = [
        shlex.split(line) for line in
        command(["iptables", "-w", "5", "-S", "FORWARD"]).splitlines()
        if line.startswith("-A ")
    ]
    return bool(entries and entries[0] == [
        "-A", "FORWARD", "-j", "DOCKER-USER"
    ])


def top_rule_order_for_proposed_bridge(old_specs, new_specs):
    # Old and new bridge rules coexist in contiguous restrictive prefixes:
    # two INPUT drops and four DOCKER-USER drops, in either relative order.
    # The original client bridge rules must never be displaced by the new.
    def append_rules(chain):
        return [
            shlex.split(line) for line in
            command(["iptables", "-w", "5", "-S", chain]).splitlines()
            if line.startswith("-A ")
        ]

    return combined_rule_order_valid(
        old_specs, new_specs,
        append_rules("INPUT"), append_rules("DOCKER-USER"),
        append_rules("FORWARD"), require_proxy=True
    )


def local_overlap_counts(networks):
    docker_matches = 0
    for net in networks:
        for cfg in (net.get("IPAM") or {}).get("Config") or []:
            value = cfg.get("Subnet")
            if value:
                addr = ipaddress.ip_network(value, strict=False)
                if addr.version == 4 and addr.overlaps(SUBNET):
                    docker_matches += 1

    routes = json.loads(command(["ip", "-j", "-4", "route", "show",
                                 "table", "all"]))
    route_matches = 0
    for row in routes:
        dst = row.get("dst")
        if dst and dst != "default":
            addr = ipaddress.ip_network(dst, strict=False)
            if addr.version == 4 and addr.overlaps(SUBNET):
                route_matches += 1

    addr_matches = 0
    addresses = json.loads(command(["ip", "-j", "-4", "address", "show"]))
    for interface in addresses:
        for entry in interface.get("addr_info") or []:
            if entry.get("family") == "inet":
                addr = ipaddress.ip_interface(
                    "{}/{}".format(entry["local"], entry["prefixlen"])
                ).network
                if addr.overlaps(SUBNET):
                    addr_matches += 1
    return docker_matches, route_matches, addr_matches


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["plan"], ["verify"]):
        fail()
    mode = argv[0] if argv else "plan"
    if os.geteuid() != 0 or command(["hostname", "-s"]).strip() != HOST:
        fail()
    if command(["docker", "info", "--format", "{{.Name}}"]).strip() != HOST:
        fail()

    agent = json.loads(command(["docker", "inspect", PROJECT + "-agent-1"]))
    if len(agent) != 1:
        fail()
    labels = (agent[0].get("Config") or {}).get("Labels") or {}
    if (agent[0].get("State", {}).get("Running") is not False or
            labels.get("com.docker.compose.project") != PROJECT or
            labels.get("com.docker.compose.service") != "agent"):
        fail()

    existing_lab = json.loads(command(["docker", "network", "inspect", OLD_LAB]))
    if len(existing_lab) != 1:
        fail()
    lab = existing_lab[0]
    ipam = (lab.get("IPAM") or {}).get("Config") or []
    if (lab.get("Name") != OLD_LAB or lab.get("Driver") != "bridge" or
            lab.get("Internal") is not True or lab.get("EnableIPv6") or
            (lab.get("Options") or {}).get("com.docker.network.bridge.name") or
            len(ipam) != 1 or
            ipaddress.ip_network(ipam[0]["Subnet"]) != OLD_SUBNET):
        fail()
    old_bridge = "br-" + lab["Id"][:12]
    old_subnet = str(OLD_SUBNET)
    old_rules = [
        ("INPUT", ["-i", old_bridge, "-s", old_subnet, "-m", "comment",
                   "--comment", "ccpc-codex-deny-host", "-j", "DROP"]),
        ("DOCKER-USER", ["-i", old_bridge, "!", "-o", old_bridge,
                         "-m", "comment", "--comment",
                         "ccpc-codex-deny-outbound", "-j", "DROP"]),
        ("DOCKER-USER", ["!", "-i", old_bridge, "-o", old_bridge,
                         "-m", "comment", "--comment",
                         "ccpc-codex-deny-inbound", "-j", "DROP"]),
    ]
    if not all(check_rule(chain, rule) for chain, rule in old_rules):
        fail()
    old_specs = {
        "host": old_rules[0],
        "out": old_rules[1],
        "in": old_rules[2],
    }
    if not first_forward_jump_is_docker_user():
        fail()

    network_ids = command(["docker", "network", "ls", "-q"]).split()
    if not network_ids:
        fail()
    networks = json.loads(command(["docker", "network", "inspect",
                                   *network_ids]))
    if (any(n.get("Name") == NEW_NETWORK or
            (n.get("Options") or {}).get(
                "com.docker.network.bridge.name") == BRIDGE
            for n in networks)):
        fail()
    links = json.loads(command(["ip", "-j", "link", "show"]))
    if any(link.get("ifname") == BRIDGE for link in links):
        fail()
    if any(local_overlap_counts(networks)):
        fail()

    specs = rules_for_new_bridge()
    present = {
        key: check_rule(chain, tokens)
        for key, (chain, tokens) in specs.items()
    }
    if 0 < sum(present.values()) < len(present):
        fail()  # Do not normalize partial firewall state automatically.

    # Refuse any additional filter/nat rule that mentions the reserved name,
    # including one that could bypass later pre-enforced DROP rules.
    for table in ("filter", "nat"):
        lines = command(["iptables", "-w", "5", "-t", table, "-S"]).splitlines()
        refs = [
            shlex.split(line) for line in lines
            if BRIDGE in shlex.split(line)
        ]
        expected_count = sum(present.values()) if table == "filter" else 0
        if len(refs) != expected_count:
            fail()

    # Output contains no network IDs, raw rules, subnet addresses or routes.
    print("CODEX_PROXY_BRIDGE_FIREWALL_READ_ONLY_REVIEW")
    print("agent_running=False")
    print("original_lab_three_firewall_rules_present=True")
    print("original_forward_chain_order_verified=True")
    print("proposed_network_and_bridge_absent=True")
    print("proposed_subnet_local_overlap_free=True")
    print("proposed_host_rule_present={}".format(present["host"]))
    print("proposed_outbound_rule_present={}".format(present["outbound"]))
    print("proposed_inbound_rule_present={}".format(present["inbound"]))
    ordered = (
        top_rule_order_for_proposed_bridge(old_specs, specs)
        if all(present.values()) else False
    )
    print("proposed_rules_first_in_chains={}".format(ordered))
    ready = all(present.values()) and ordered
    print("pre_enforcement_verified={}".format(ready))
    print("remote_route_and_runtime_isolation_verified=False")
    print("INSPECTION_COMPLETE")
    # 'verify' only succeeds once all three candidate rules have been
    # separately and explicitly approved, installed and correctly ordered.
    if mode == "verify" and not ready:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError, IndexError,
            json.JSONDecodeError):
        fail()
