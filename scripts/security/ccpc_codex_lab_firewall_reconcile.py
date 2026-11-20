#!/usr/bin/env python3
"""Scoped Codex original-lab firewall reconciliation. REVIEW ONLY: NOT INSTALLED.

'plan' and 'verify' never mutate the host. 'restore' changes only missing
original-lab DROP rules, requires a separately installed root-owned marker,
and is NOT authorized on ccpcerpserver until host recovery/rollback approval.
No Docker/Codex/Squid starts, service changes, or firewall flushes here.
An approved invocation is not reboot persistence or launch authorization.
"""
import fcntl
import os
import stat
import sys

import ccpc_codex_lab_firewall_guard as guard
from ccpc_firewall_rule_order import canonical_rule, PROXY_BRIDGE, PROXY_TAGS

MARKER = "/etc/ccpc/codex-lab-firewall-restore-authorized"
MARKER_BODY = b"CCPC_CODEX_FIREWALL_RESTORE_EXPLICITLY_APPROVED\n"
LOCK = "/run/lock/ccpc-codex-original-lab-firewall.lock"


class ReconcileFailure(Exception):
    pass


def authorization_required():
    if os.geteuid() != 0:
        raise ReconcileFailure()
    try:
        fd = os.open(MARKER, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            st = os.fstat(fd)
            if (not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or
                    st.st_mode & 0o077 or st.st_size != len(MARKER_BODY) or
                    os.read(fd, len(MARKER_BODY) + 1) != MARKER_BODY):
                raise ReconcileFailure()
        finally:
            os.close(fd)
    except OSError as exc:
        raise ReconcileFailure() from exc


def lock_host():
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_uid != 0 or
                st.st_mode & 0o077):
            os.close(fd)
            raise ReconcileFailure()
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError as exc:
        raise ReconcileFailure() from exc


def planned_insertions(specs, input_rules, user_rules, forward_rules):
    """Plan exact missing rules, refusing ambiguous tags or unsafe prefixes.

    Never normalize a displaced, duplicated, modified or partially deployed
    policy. Deliberately does not handle the unapproved proxy-client bridge.
    """
    chains = {"INPUT": input_rules, "DOCKER-USER": user_rules}
    tags = {
        "host": "ccpc-codex-deny-host",
        "out": "ccpc-codex-deny-outbound",
        "in": "ccpc-codex-deny-inbound",
    }
    missing = []
    for name in ("host", "out", "in"):
        chain, arguments = specs[name]
        expected = canonical_rule(["-A", chain, *arguments], chain)
        if expected is None:
            raise ReconcileFailure()
        tagged = [
            (current_chain, rule)
            for current_chain, rules in chains.items()
            for rule in rules if tags[name] in rule
        ]
        if len(tagged) > 1:
            raise ReconcileFailure()
        if tagged:
            current_chain, rule = tagged[0]
            if current_chain != chain or canonical_rule(rule, chain) != expected:
                raise ReconcileFailure()
        else:
            missing.append(name)

    if any(
        PROXY_BRIDGE in rule or any(tag in rule for tag in PROXY_TAGS)
        for rule in input_rules + user_rules
    ):
        raise ReconcileFailure()  # No unsafe proxy-bridge half-deployment.

    prospective_input = list(input_rules)
    prospective_user = list(user_rules)
    for name in missing:
        chain, args = specs[name]
        target = prospective_input if chain == "INPUT" else prospective_user
        target.insert(0, ["-A", chain, *args])
    if not guard.precedence_valid(
        specs, prospective_input, prospective_user, forward_rules
    ):
        raise ReconcileFailure()
    return missing


def preflight():
    specs = guard.inspect_host()  # Root, stopped agent, bridge, UFW, DOCKER-USER.
    missing = planned_insertions(
        specs,
        guard.append_rules("INPUT"),
        guard.append_rules("DOCKER-USER"),
        guard.append_rules("FORWARD"),
    )
    return specs, missing


def restore():
    authorization_required()
    fd = lock_host()
    inserted = []
    try:
        specs, missing = preflight()
        try:
            for name in missing:
                chain, args = specs[name]
                guard.command(["iptables", "-w", "5", "-I", chain, "1", *args])
                inserted.append((chain, args))
            guard.inspect_host()  # Agent must still be stopped after inserts.
            guard.check_current_rules(specs)  # Exact -C + leading order.
        except BaseException:
            rollback_incomplete = False
            for chain, args in reversed(inserted):
                try:
                    guard.command(["iptables", "-w", "5", "-D", chain, *args])
                except Exception:
                    rollback_incomplete = True
            if rollback_incomplete:
                raise ReconcileFailure() from None
            raise
        return len(inserted)
    finally:
        os.close(fd)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv not in ([], ["plan"], ["verify"], ["restore"]):
        print("STOP: unapproved reconciliation mode")
        return 2
    try:
        mode = argv[0] if argv else "plan"
        if mode == "restore":
            count = restore()
            print("ORIGINAL_LAB_RULES_RESTORED_COUNT=" + str(count))
        else:
            specs, missing = preflight()
            if mode == "verify":
                if missing:
                    raise ReconcileFailure()
                guard.check_current_rules(specs)
                print("ORIGINAL_LAB_RULES_AND_ORDER_VERIFIED=True")
            else:
                print("ORIGINAL_LAB_RULES_MISSING_COUNT=" + str(len(missing)))
    except (ReconcileFailure, guard.GuardFailure, ValueError, TypeError,
            KeyError, IndexError, AttributeError, OSError):
        print("STOP: original lab firewall reconciliation failed")
        return 1
    print("agent_launch_authorized=False")
    print("reboot_reload_persistence_verified=False")
    print("INSPECTION_COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
