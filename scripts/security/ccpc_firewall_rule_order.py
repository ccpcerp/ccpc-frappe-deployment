"""Pure, offline rule-order comparison for the two CCPC Codex lab bridges.

No Docker, subprocess, iptables calls, sockets, filesystem changes or secrets.
The caller must verify actual iptables -C rule existence and host identity.
"""
from collections import Counter

OPTIONS = {"-i", "-o", "-s", "-m", "--comment", "-j"}
PROXY_BRIDGE = "br-ccpc-cdxpx"
PROXY_TAGS = (
    "ccpc-codex-px-deny-host",
    "ccpc-codex-px-deny-out",
    "ccpc-codex-px-deny-in",
)


def canonical_rule(tokens, chain):
    """Normalize narrowly accepted iptables -S token order; reject extensions."""
    if tokens[:2] != ["-A", chain]:
        return None
    parts = tokens[2:]
    parsed = []
    i = 0
    while i < len(parts):
        inverse = False
        if parts[i] == "!":
            inverse = True
            i += 1
        if i >= len(parts) or parts[i] not in OPTIONS:
            return None
        field = parts[i]
        i += 1
        if i < len(parts) and parts[i] == "!":
            if inverse or field not in {"-i", "-o", "-s"}:
                return None
            inverse = True
            i += 1
        if i >= len(parts):
            return None
        value = parts[i]
        i += 1
        if inverse and field not in {"-i", "-o", "-s"}:
            return None
        parsed.append((inverse, field, value))
    if len({field for _, field, _ in parsed}) != len(parsed):
        return None
    return tuple(sorted(parsed))


def proxy_rule_specs(bridge=PROXY_BRIDGE):
    return {
        "host": ("INPUT", [
            "-i", bridge, "-m", "comment", "--comment", PROXY_TAGS[0],
            "-j", "DROP",
        ]),
        "outbound": ("DOCKER-USER", [
            "-i", bridge, "!", "-o", bridge, "-m", "comment",
            "--comment", PROXY_TAGS[1], "-j", "DROP",
        ]),
        "inbound": ("DOCKER-USER", [
            "!", "-i", bridge, "-o", bridge, "-m", "comment",
            "--comment", PROXY_TAGS[2], "-j", "DROP",
        ]),
    }


def _ordered_prefix(actual, expected, chain):
    if len(actual) < len(expected):
        return False
    actual_signatures = [canonical_rule(x, chain)
                         for x in actual[:len(expected)]]
    expected_signatures = [canonical_rule(["-A", spec[0], *spec[1]], chain)
                           for spec in expected]
    if any(x is None for x in actual_signatures + expected_signatures):
        return False
    return Counter(actual_signatures) == Counter(expected_signatures)


def combined_rule_order_valid(
    original, proxy, input_rules, user_rules, forward_rules,
    require_proxy=False,
):
    """Verify safe top-of-chain prefixes for original-only or both bridges.

    When any candidate proxy-bridge reference is present, require ALL THREE
    proxy rules together (two INPUT prefix rules, four DOCKER-USER prefix
    rules). This avoids the impossible design where both bridges must
    independently occupy INPUT position one / DOCKER-USER positions one-two.
    """
    has_candidate_reference = any(
        PROXY_BRIDGE in rule or any(tag in rule for tag in PROXY_TAGS)
        for rule in input_rules + user_rules
    )
    joint = require_proxy or has_candidate_reference

    expected_input = [original["host"]]
    expected_user = [original["out"], original["in"]]
    if joint:
        expected_input.append(proxy["host"])
        expected_user += [proxy["outbound"], proxy["inbound"]]

    return (
        bool(forward_rules) and
        forward_rules[0] == ["-A", "FORWARD", "-j", "DOCKER-USER"] and
        _ordered_prefix(input_rules, expected_input, "INPUT") and
        _ordered_prefix(user_rules, expected_user, "DOCKER-USER")
    )
