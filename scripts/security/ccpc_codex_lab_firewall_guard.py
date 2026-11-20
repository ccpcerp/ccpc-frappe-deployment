#!/usr/bin/env python3
"""CCPC original synthetic-lab firewall guard (READ ONLY, REVIEW ONLY).

'preflight' checks the stopped lab, host and Docker chain prerequisites
for separately authorized restoration. 'verify' additionally confirms the
exact host and cross-bridge DROP rules and their precedence. There is NO
apply, rollback, container start or persistent-rule installation action.

This protects only the original bridge; it is NOT a Codex launch permit,
reboot-persistence proof, proxy-client firewall check or egress safety proof.
"""
import ipaddress
import json
import os
import re
import shlex
import subprocess
import sys

from ccpc_firewall_rule_order import (
    canonical_rule,
    combined_rule_order_valid,
    proxy_rule_specs,
)

HOST = "ccpcerpserver"
PROJECT = "ccpc_codex_dev_agent"
AGENT = PROJECT + "-agent-1"
NETWORK = PROJECT + "_lab"
EXPECTED_SUBNET = ipaddress.ip_network("172.21.0.0/16")
EXPECTED_GATEWAY = ipaddress.ip_address("172.21.0.1")




class GuardFailure(Exception):
    """Fail closed, without printing raw network or firewall details."""


def command(argv, allow_missing=False):
    try:
        proc = subprocess.run(
            argv, text=True, capture_output=True, timeout=25
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GuardFailure() from exc
    if allow_missing:
        if proc.returncode not in (0, 1):
            raise GuardFailure()
        return proc.returncode == 0
    if proc.returncode:
        raise GuardFailure()
    return proc.stdout


def rule_specs(bridge, subnet):
    """Match the current original-lab firewall contract; never mutate it."""
    return {
        "host": ("INPUT", [
            "-i", bridge, "-s", subnet, "-m", "comment",
            "--comment", "ccpc-codex-deny-host", "-j", "DROP",
        ]),
        "out": ("DOCKER-USER", [
            "-i", bridge, "!", "-o", bridge, "-m", "comment",
            "--comment", "ccpc-codex-deny-outbound", "-j", "DROP",
        ]),
        "in": ("DOCKER-USER", [
            "!", "-i", bridge, "-o", bridge, "-m", "comment",
            "--comment", "ccpc-codex-deny-inbound", "-j", "DROP",
        ]),
    }


def append_rules(chain):
    lines = command(["iptables", "-w", "5", "-S", chain]).splitlines()
    try:
        return [
            shlex.split(line) for line in lines if line.startswith("-A ")
        ]
    except ValueError as exc:
        raise GuardFailure() from exc


def precedence_valid(specs, input_rules, user_rules, forward_rules):
    # The original bridge must remain protected both before and after
    # separately approved installation of the second proxy-client bridge.
    return combined_rule_order_valid(
        specs, proxy_rule_specs(), input_rules, user_rules, forward_rules
    )


def inspect_host():
    if os.geteuid() != 0:
        raise GuardFailure()
    if command(["hostname", "-s"]).strip() != HOST:
        raise GuardFailure()
    if command(["docker", "info", "--format", "{{.Name}}"]).strip() != HOST:
        raise GuardFailure()

    containers = json.loads(command(["docker", "inspect", AGENT]))
    if len(containers) != 1:
        raise GuardFailure()
    agent = containers[0]
    labels = (agent.get("Config") or {}).get("Labels") or {}
    restart = ((agent.get("HostConfig") or {}).get("RestartPolicy") or {}).get("Name")
    if (
        (agent.get("State") or {}).get("Running") is not False or
        labels.get("com.docker.compose.project") != PROJECT or
        labels.get("com.docker.compose.service") != "agent" or
        restart not in ("", "no", None)
    ):
        raise GuardFailure()

    networks = json.loads(command(["docker", "network", "inspect", NETWORK]))
    if len(networks) != 1:
        raise GuardFailure()
    net = networks[0]
    config = (net.get("IPAM") or {}).get("Config") or []
    if (
        net.get("Name") != NETWORK or
        net.get("Driver") != "bridge" or
        net.get("Internal") is not True or
        net.get("EnableIPv6") is not False or
        (net.get("Options") or {}).get("com.docker.network.bridge.name") or
        len(config) != 1 or
        ipaddress.ip_network(config[0]["Subnet"], strict=True) != EXPECTED_SUBNET or
        ipaddress.ip_address(config[0]["Gateway"]) != EXPECTED_GATEWAY or
        not re.fullmatch(r"[0-9a-f]{12,64}", net.get("Id", ""))
    ):
        raise GuardFailure()
    bridge = "br-" + net["Id"][:12]
    command(["ip", "link", "show", "dev", bridge])
    if "nf_tables" not in command(["iptables", "--version"]):
        raise GuardFailure()
    # Persisted firewall ordering is not established; at minimum UFW
    # must currently be active before any separately approved restoration.
    command(["systemctl", "is-active", "--quiet", "ufw.service"])

    # Chain availability and Docker's entry into DOCKER-USER are necessary
    # BEFORE the installer is permitted to modify any project-scoped rules.
    command(["iptables", "-w", "5", "-S", "INPUT"])
    command(["iptables", "-w", "5", "-S", "DOCKER-USER"])
    forward = append_rules("FORWARD")
    if not forward or forward[0] != [
        "-A", "FORWARD", "-j", "DOCKER-USER"
    ]:
        raise GuardFailure()
    return rule_specs(bridge, str(EXPECTED_SUBNET))


def check_current_rules(specs):
    for chain, rule in specs.values():
        if not command(["iptables", "-w", "5", "-C", chain, *rule],
                       allow_missing=True):
            raise GuardFailure()
    if not precedence_valid(
        specs, append_rules("INPUT"),
        append_rules("DOCKER-USER"), append_rules("FORWARD")
    ):
        raise GuardFailure()
    return True


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["preflight"], ["verify"]):
        print("STOP: read-only mode required")
        return 2
    mode = argv[0] if argv else "verify"
    try:
        specs = inspect_host()
        if mode == "verify":
            check_current_rules(specs)
    except (GuardFailure, ValueError, TypeError, KeyError, IndexError,
            json.JSONDecodeError, AttributeError):
        print("STOP: original lab firewall guard failed")
        return 1
    print("CCPC_CODEX_ORIGINAL_LAB_FIREWALL_GUARD")
    print("agent_running=False")
    print("original_lab_identity_verified=True")
    print("original_forward_order_verified=True")
    print("original_three_rules_and_precedence_verified={}".format(
        mode == "verify"
    ))
    print("agent_launch_authorized=False")
    print("firewall_reboot_persistence_verified=False")
    print("INSPECTION_COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
