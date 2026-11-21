#!/usr/bin/env bash
# CCPC new synthetic Codex lab ONLY. Guarded iptables-nft policy.
# No effects on other Docker bridges. Source review + owner approval required.
# "plan" and "verify" never change firewall rules; "apply"/"rollback" require root.
# Ephemeral: these rules do NOT persist across host restart / firewall reload.
set -euo pipefail

ACTION="${1:-plan}"
case "$ACTION" in plan|apply|verify|rollback) ;; *)
  echo "Usage: $0 [plan|apply|verify|rollback]" >&2; exit 2;;
esac

if [[ $EUID -ne 0 ]]; then
  echo "STOP: run through sudo after operator approval; never send passwords to chat" >&2
  exit 2
fi

for command in docker iptables ip python3; do
  command -v "$command" >/dev/null || { echo "STOP: missing $command"; exit 2; }
done
[[ "$(hostname -s)" == "ccpcerpserver" ]] ||
  { echo "STOP: unexpected host"; exit 1; }
[[ "$(docker info --format '{{.Name}}')" == "ccpcerpserver" ]] ||
  { echo "STOP: unexpected Docker daemon"; exit 1; }

NETWORK="ccpc_codex_dev_agent_lab"
INSPECT="$(docker network inspect "$NETWORK")" || { echo "STOP: no lab network"; exit 1; }
VALUES="$(python3 -c '
import json, ipaddress, sys
n, = json.load(sys.stdin)
cfg = (n.get("IPAM") or {}).get("Config") or []
if (n.get("Name") != "ccpc_codex_dev_agent_lab"
    or n.get("Driver") != "bridge"
    or n.get("Internal") is not True
    or n.get("EnableIPv6")
    or len(cfg) != 1
    or (n.get("Options") or {}).get("com.docker.network.bridge.name")):
    raise SystemExit("STOP: unexpected Docker network settings")
subnet = str(ipaddress.ip_network(cfg[0].get("Subnet"), strict=True))
gateway = str(ipaddress.ip_address(cfg[0].get("Gateway")))
if subnet != "172.21.0.0/16" or gateway != "172.21.0.1":
    raise SystemExit("STOP: lab subnet/gateway changed")
print("br-" + n["Id"][:12], subnet, gateway)
' <<< "$INSPECT")" || exit 1

read -r BRIDGE SUBNET GATEWAY <<< "$VALUES"
[[ "$BRIDGE" == "br-a88796be8a7a" ]] ||
  { echo "STOP: lab bridge identity changed"; exit 1; }
ip link show dev "$BRIDGE" >/dev/null ||
  { echo "STOP: no expected bridge device"; exit 1; }

[[ "$(docker inspect --format '{{.State.Running}}' ccpc_codex_dev_agent-agent-1)" == "false" ]] ||
  { echo "STOP: Codex agent must remain stopped for firewall change"; exit 1; }
[[ "$(iptables --version)" == *nf_tables* ]] ||
  { echo "STOP: expected iptables-nft backend"; exit 1; }

iptables -w 5 -S INPUT >/dev/null
iptables -w 5 -S DOCKER-USER >/dev/null
FIRST_FORWARD="$(iptables -w 5 -S FORWARD | awk '$1=="-A" { print; exit }')"
[[ "$FIRST_FORWARD" == "-A FORWARD -j DOCKER-USER" ]] ||
  { echo "STOP: Docker FORWARD/DOCKER-USER chain order changed"; exit 1; }

# INPUT protects the host itself; DOCKER-USER protects routed traffic
# to/from legacy Docker bridges, LAN, NAS and other networks.
# Traffic within the isolated lab bridge remains permitted.
host_rule=(-i "$BRIDGE" -s "$SUBNET" -m comment --comment ccpc-codex-deny-host -j DROP)
out_rule=(-i "$BRIDGE" ! -o "$BRIDGE" -m comment --comment ccpc-codex-deny-outbound -j DROP)
in_rule=(! -i "$BRIDGE" -o "$BRIDGE" -m comment --comment ccpc-codex-deny-inbound -j DROP)

has_host() { iptables -w 5 -C INPUT "${host_rule[@]}" >/dev/null 2>&1; }
has_out() { iptables -w 5 -C DOCKER-USER "${out_rule[@]}" >/dev/null 2>&1; }
has_in() { iptables -w 5 -C DOCKER-USER "${in_rule[@]}" >/dev/null 2>&1; }

printf 'Lab bridge: %s\nLab subnet: %s\nGateway: %s\nAgent: STOPPED\n' "$BRIDGE" "$SUBNET" "$GATEWAY"

case "$ACTION" in
  plan)
    echo "PLAN (NO CHANGES):"
    echo "  INPUT: DROP from lab bridge and subnet to host"
    echo "  DOCKER-USER: DROP lab bridge to any OTHER interface"
    echo "  DOCKER-USER: DROP OTHER interfaces to lab bridge"
    echo "  Same-bridge MariaDB/Redis traffic unaffected"
    echo "  Rules TEMPORARY: host reboot/firewall refresh clears them"
    echo "  NO Docker/SSH restart, existing bridge edit or service mutation"
    ;;
  verify)
    if has_host && has_out && has_in; then
      echo "PASS: all three bridge-specific DROP rules installed"
    else
      echo "STOP: bridge firewall protections incomplete"; exit 1
    fi
    ;;
  apply)
    added_host=0; added_out=0; added_in=0; success=0
    undo_partial() {
      if [[ "$success" != 1 ]]; then
        if [[ "$added_in" == 1 ]]; then iptables -w 5 -D DOCKER-USER "${in_rule[@]}" || true; fi
        if [[ "$added_out" == 1 ]]; then iptables -w 5 -D DOCKER-USER "${out_rule[@]}" || true; fi
        if [[ "$added_host" == 1 ]]; then iptables -w 5 -D INPUT "${host_rule[@]}" || true; fi
        echo "STOP: partial firewall additions rolled back"
      fi
    }
    trap undo_partial EXIT
    if ! has_host; then
      iptables -w 5 -I INPUT 1 "${host_rule[@]}"
      added_host=1
    fi
    if ! has_out; then
      iptables -w 5 -I DOCKER-USER 1 "${out_rule[@]}"
      added_out=1
    fi
    if ! has_in; then
      iptables -w 5 -I DOCKER-USER 1 "${in_rule[@]}"
      added_in=1
    fi
    if ! has_host || ! has_out || ! has_in; then
      echo "STOP: firewall rule verification failed"; exit 1
    fi
    success=1
    echo "PASS: three scoped temporary DROP rules present"
    echo "NEXT: verify blocked SSH gateway and controlled non-PROD canary"
    echo "HOLD: agent/Codex CLI/online proxy until independent negative tests"
    ;;
  rollback)
    # Exact-match removal only; no chain flushing or global firewall reset.
    if has_in; then iptables -w 5 -D DOCKER-USER "${in_rule[@]}"; fi
    if has_out; then iptables -w 5 -D DOCKER-USER "${out_rule[@]}"; fi
    if has_host; then iptables -w 5 -D INPUT "${host_rule[@]}"; fi
    echo "PASS: removed CCPC Codex lab rules only; agent remains stopped"
    ;;
esac
