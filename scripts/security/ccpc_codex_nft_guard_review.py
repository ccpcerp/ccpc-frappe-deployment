#!/usr/bin/env python3
"""Independent nftables original-lab deny policy — REVIEW ONLY, UNINSTALLED.

This is a pure candidate renderer and read-only exact-table verifier. It has
NO install/apply/reload/delete mode, no Codex start, and no privileged host
mutation. It is an additional layer to existing iptables DROP rules, not
proof of persistence, path coverage or unbypassable runtime enforcement.
"""
from collections import Counter
import json
import re
import sys

import ccpc_codex_lab_firewall_guard as guard

TABLE = "ccpc_codex_lab_guard"
PRIORITY = -301
CHAINS = {"host_in": "input", "host_out": "output",
          "cross_bridge": "forward"}
BRIDGE_NAME = re.compile(r"br-[0-9a-f]{12}\Z")


class LayerFailure(Exception):
    """Fail closed without printing firewall or host data."""


def _bridge(bridge):
    if not isinstance(bridge, str) or not BRIDGE_NAME.fullmatch(bridge):
        raise LayerFailure()
    return bridge


def render_candidate(bridge):
    """Return scoped, separate-table nftables candidate; do not install it.

    An inet table covers IPv4 and IPv6. The host-out rule also prevents
    host-originated access to lab services. No other bridge is matched.
    A host nftables.service flush ruleset or interface recreation can still
    destroy or bypass these rules: runtime host tests are mandatory.
    """
    b = _bridge(bridge)
    return (
        f"table inet {TABLE} {{\n"
        f"  chain host_in {{\n"
        f"    type filter hook input priority {PRIORITY}; policy accept;\n"
        f'    iifname "{b}" drop\n'
        f"  }}\n"
        f"  chain host_out {{\n"
        f"    type filter hook output priority {PRIORITY}; policy accept;\n"
        f'    oifname "{b}" drop\n'
        f"  }}\n"
        f"  chain cross_bridge {{\n"
        f"    type filter hook forward priority {PRIORITY}; policy accept;\n"
        f'    iifname "{b}" oifname != "{b}" drop\n'
        f'    oifname "{b}" iifname != "{b}" drop\n'
        f"  }}\n"
        f"}}\n"
    )


def _match(field, op, bridge):
    return {"match": {"op": op, "left": {"meta": {"key": field}},
                      "right": bridge}}


def _rule(chain, *matches):
    return {"rule": {"family": "inet", "table": TABLE, "chain": chain,
                     "expr": [*matches, {"drop": None}]}}


def expected_json_entries(bridge):
    b = _bridge(bridge)
    entries = [{"table": {"family": "inet", "name": TABLE}}]
    entries.extend(
        {"chain": {"family": "inet", "table": TABLE, "name": name,
                   "type": "filter", "hook": hook, "prio": PRIORITY,
                   "policy": "accept"}}
        for name, hook in CHAINS.items()
    )
    entries.extend([
        _rule("host_in", _match("iifname", "==", b)),
        _rule("host_out", _match("oifname", "==", b)),
        _rule("cross_bridge", _match("iifname", "==", b),
              _match("oifname", "!=", b)),
        _rule("cross_bridge", _match("oifname", "==", b),
              _match("iifname", "!=", b)),
    ])
    return entries


def validate_json_snapshot(raw, bridge):
    """Conservative comparison against nft -j list table output.

    Kernel object handles are ignored, but extra/modified tables/chains/rules,
    unexpected actions, missing hook or wrong priority are rejected. Actual
    nft JSON normalization must be checked on the real host (fail closed).
    """
    _bridge(bridge)
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError as exc:
            raise LayerFailure() from exc
    if not isinstance(raw, dict) or set(raw) != {"nftables"}:
        raise LayerFailure()
    objects = raw["nftables"]
    if not isinstance(objects, list):
        raise LayerFailure()
    observed = []
    for item in objects:
        if not isinstance(item, dict) or len(item) != 1:
            raise LayerFailure()
        kind, obj = next(iter(item.items()))
        if kind == "metainfo":
            continue
        if kind not in {"table", "chain", "rule"} or not isinstance(obj, dict):
            raise LayerFailure()
        observed.append({kind: {k: v for k, v in obj.items() if k != "handle"}})
    want = expected_json_entries(bridge)
    canonical = lambda items: Counter(json.dumps(x, sort_keys=True) for x in items)
    if canonical(observed) != canonical(want):
        raise LayerFailure()
    return True


def candidate_host():
    """Use existing strict host identity guard; require stopped agent."""
    specs = guard.inspect_host()
    guard.check_current_rules(specs)
    chain, argv = specs["host"]
    if chain != "INPUT" or argv[:2] != ["-i", argv[1]]:
        raise LayerFailure()
    return _bridge(argv[1])


def verify_kernel():
    bridge = candidate_host()
    output = guard.command(["nft", "-j", "list", "table", "inet", TABLE])
    return validate_json_snapshot(output, bridge)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["plan"], ["verify"]):
        print("STOP: nft guard is read-only")
        return 2
    try:
        mode = argv[0] if argv else "plan"
        if mode == "plan":
            bridge = candidate_host()
            render_candidate(bridge)  # In memory only, never printed/applied.
            print("INDEPENDENT_NFT_POLICY_CANDIDATE_VALID=True")
        else:
            verify_kernel()
            print("INDEPENDENT_NFT_POLICY_PRESENT_AND_EXACT=True")
    except (LayerFailure, guard.GuardFailure, ValueError, TypeError,
            KeyError, IndexError, AttributeError, OSError):
        print("STOP: independent nft policy unavailable or unexpected")
        return 1
    print("agent_launch_authorized=False")
    print("reload_and_reboot_persistence_verified=False")
    print("INSPECTION_COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
