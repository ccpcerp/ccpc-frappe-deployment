#!/usr/bin/env python3
"""Fail-closed, source-only review of CCPC's synthetic Codex Docker Compose project.

The checks do NOT prove Docker runtime isolation, host firewall protection,
Squid DNS rebinding safety, image trust or Codex sandbox/credential safety.
Nothing here authorizes bringing up the online proxy or agent.
"""
import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = "ccpc_codex_dev_agent"
REQUIRED = {"agent", "db", "redis-cache", "redis-queue", "egress-proxy"}
CLIENT_SUBNET = "172.30.250.0/29"
CLIENT_BRIDGE = "br-ccpc-cdxpx"
AGENT_CLIENT_IP = "172.30.250.2"
PROXY_CLIENT_IP = "172.30.250.3"
PROXY_LISTENER = PROXY_CLIENT_IP + ":3128"
PROXY_SOURCE = AGENT_CLIENT_IP + "/32"

EXPECTED_IMAGES = {
    "agent": "frappe/bench:latest",
    "db": "mariadb:11.8",
    "redis-cache": "redis:7-alpine",
    "redis-queue": "redis:7-alpine",
    "egress-proxy": "ubuntu/squid:latest",
}

# Proposed REVIEW-ONLY ceiling values; CPU remains unrestricted by preference.
# Memory+swap equal prevents unbounded swap usage on supported Docker hosts.
# These are candidate budgets, NOT approved runtime sizing or host readiness.
EXPECTED_RESOURCE_BOUNDS = {
    "agent": (8 * 1024**3, 512),
    "db": (2 * 1024**3, 256),
    "redis-cache": (384 * 1024**2, 128),
    "redis-queue": (384 * 1024**2, 128),
    "egress-proxy": (512 * 1024**2, 128),
}

# Preserve the existing allowlist pending a separate domain/SSRF review.
APPROVED_DOMAINS = {
    ".openai.com", ".chatgpt.com", ".oaistatic.com",
    ".oaiusercontent.com", ".github.com", ".githubusercontent.com",
    ".githubassets.com", ".npmjs.org", ".pypi.org", ".pythonhosted.org",
}
PROHIBITED_DESTINATIONS = {
    "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8",
    "169.254.0.0/16", "172.16.0.0/12", "192.0.0.0/24",
    "192.0.2.0/24", "192.88.99.0/24", "192.168.0.0/16",
    "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24",
    "224.0.0.0/4", "240.0.0.0/4", "::/128", "::1/128",
    "fc00::/7", "fe80::/10", "2001:db8::/32",
}
ACCESS_RULES = [
    ("http_access", "deny", "!codex_agent"),
    ("http_access", "deny", "!CONNECT"),
    ("http_access", "deny", "!HTTPS"),
    ("http_access", "deny", "prohibited"),
    ("http_access", "allow", "codex_agent", "CONNECT", "HTTPS", "approved"),
    ("http_access", "deny", "all"),
]


def reject(message):
    raise ValueError(message)


def resource_bytes(value):
    """Accept integer-byte or Docker Compose unit rendering, fail closed."""
    if isinstance(value, bool):
        reject("boolean resource ceiling forbidden")
    if isinstance(value, int) and value > 0:
        return value
    if not isinstance(value, str):
        reject("missing or invalid resource ceiling")
    match = re.fullmatch(r"([1-9][0-9]*)([kmgt]?)b?", value.strip().lower())
    if not match:
        reject("invalid resource ceiling units")
    power = {"": 0, "k": 1, "m": 2, "g": 3, "t": 4}[match.group(2)]
    return int(match.group(1)) * (1024 ** power)


def validate_resource_bounds(name, service):
    expected_memory, expected_pids = EXPECTED_RESOURCE_BOUNDS[name]
    if resource_bytes(service.get("mem_limit")) != expected_memory:
        reject(f"{name}: unexpected memory ceiling")
    if resource_bytes(service.get("memswap_limit")) != expected_memory:
        reject(f"{name}: swap usage must not exceed memory ceiling")
    pids = service.get("pids_limit")
    if isinstance(pids, bool) or not isinstance(pids, (int, str)):
        reject(f"{name}: invalid PID ceiling")
    if str(pids) != str(expected_pids):
        reject(f"{name}: unexpected PID ceiling")


def network_entries(service):
    values = service.get("networks")
    if isinstance(values, dict):
        result = values
    elif isinstance(values, list):
        result = {name: None for name in values}
    elif values is None and not service.get("network_mode"):
        result = {"default": None}
    else:
        reject("unsupported service network structure")
    if not all(isinstance(name, str) and
               (entry is None or isinstance(entry, dict))
               for name, entry in result.items()):
        reject("invalid network entries")
    return result


def only_network(service, expected, name):
    actual = set(network_entries(service))
    if actual != expected:
        reject(f"{name}: unexpected networks")


def network_config(entry, address=None):
    # Match the whole entry rather than accepting unreviewed route priorities,
    # links, aliases, or other attributes that happen to be falsey.
    if entry is None:
        return address is None
    if not isinstance(entry, dict):
        return False
    if address is None:
        return entry == {}
    return entry == {"ipv4_address": address}


def validate_proxy_policy(source):
    """Fail closed on extra Squid listeners, ACLs or access rules.

    Static syntax shape only; use 'squid -k parse' with a VETTED image in a
    separate approved non-host test before any deployment.
    """
    if not isinstance(source, str):
        reject("missing Squid policy")
    statements = [
        tuple(line.split("#", 1)[0].split())
        for line in source.splitlines()
        if line.split("#", 1)[0].strip()
    ]
    listeners = [s for s in statements if s[0] == "http_port"]
    if listeners != [("http_port", PROXY_LISTENER)]:
        reject("Squid listener is not bound exclusively to proxy client IP")
    if [s for s in statements if s[0] == "http_access"] != ACCESS_RULES:
        reject("Squid ordered source/method/port/destination policy changed")

    acls = [s for s in statements if s[0] == "acl"]
    expected_keys = {"codex_agent", "CONNECT", "HTTPS", "prohibited", "approved"}
    if len(acls) != len(expected_keys) or {s[1] for s in acls} != expected_keys:
        reject("Squid ACL set changed")
    by_name = {s[1]: s[2:] for s in acls}
    if by_name["codex_agent"] != ("src", PROXY_SOURCE):
        reject("Squid agent source ACL changed")
    if by_name["CONNECT"] != ("method", "CONNECT"):
        reject("Squid CONNECT ACL changed")
    if by_name["HTTPS"] != ("port", "443"):
        reject("Squid HTTPS ACL changed")
    if (len(by_name["prohibited"]) != len(PROHIBITED_DESTINATIONS) + 1
            or by_name["prohibited"][0] != "dst"
            or set(by_name["prohibited"][1:]) != PROHIBITED_DESTINATIONS):
        reject("Squid prohibited destinations changed")
    if (len(by_name["approved"]) != len(APPROVED_DOMAINS) + 1
            or by_name["approved"][0] != "dstdomain"
            or set(by_name["approved"][1:]) != APPROVED_DOMAINS):
        reject("Squid domain allowlist changed")

    # Disallow include files, extra listeners, cache configuration, upstream
    # proxies, request rewriting, and unreviewed DNS/client access directives.
    miscellaneous = {("visible_hostname", "ccpc-codex-dev-proxy"),
                     ("cache", "deny", "all"),
                     ("access_log", "stdio:/dev/stdout"),
                     ("cache_store_log", "none")}
    others = [s for s in statements if s[0] not in
              {"http_port", "http_access", "acl"}]
    if len(others) != len(miscellaneous) or set(others) != miscellaneous:
        reject("unreviewed Squid directives")
    return True


def validate(rendered, proxy_policy=None):
    if rendered.get("name") != PROJECT:
        reject("incorrect Compose project name")
    services = rendered.get("services") or {}
    if set(services) != REQUIRED:
        reject("unexpected Compose services")
    networks = rendered.get("networks") or {}
    if set(networks) != {"lab", "proxy_clients", "outgoing"}:
        reject("unexpected Docker networks")
    if not all(isinstance(x, dict) and
               not x.get("external") and x.get("driver") == "bridge"
               for x in networks.values()):
        reject("unsafe network types")
    if not networks["lab"].get("internal"):
        reject("application bridge must be internal")
    client = networks["proxy_clients"]
    if (client.get("internal") is not True or
            client.get("attachable") is not False or
            client.get("enable_ipv6") is not False):
        reject("proxy client bridge must be internal and nonattachable IPv4")
    if client.get("driver_opts") != {
        "com.docker.network.bridge.name": CLIENT_BRIDGE
    }:
        reject("proxy client bridge device name changed")
    ipam = client.get("ipam") or {}
    if ipam.get("config") != [{"subnet": CLIENT_SUBNET}]:
        reject("unexpected proxy client IPAM; needs pre-activation overlap review")
    if networks["outgoing"].get("internal") is True:
        reject("outgoing bridge must not be internal")
    if networks["outgoing"].get("attachable") is not False:
        reject("outgoing bridge must not be attachable")
    if networks["outgoing"].get("enable_ipv6") is not False:
        reject("outgoing bridge must explicitly disable IPv6")
    # Preserve the existing live application bridge: no source-level IPAM
    # changes to lab or outgoing are permitted as part of this PR.
    if any((networks[name].get("ipam") or {}).get("config")
           for name in ("lab", "outgoing")):
        reject("existing network IPAM may not be changed")
    if any(networks[name].get("driver_opts")
           for name in ("lab", "outgoing")):
        reject("existing network bridge identity must not be changed")

    # Static address must be inside the dedicated internal /29, not its gateway.
    subnet = ipaddress.ip_network(CLIENT_SUBNET, strict=True)
    if not all(ipaddress.ip_address(ip) in subnet.hosts() for ip in
               (AGENT_CLIENT_IP, PROXY_CLIENT_IP)):
        reject("proxy client addresses out of subnet")

    for name, service in services.items():
        if (service.get("privileged") or service.get("network_mode") or
                any(service.get(key) for key in
                    ("pid", "ipc", "uts", "cgroup", "userns_mode", "volumes_from",
                     "device_cgroup_rules", "cgroup_parent"))):
            reject(f"{name}: privileged/host namespace or external resource mode")
        if any(service.get(key) for key in
               ("ports", "devices", "extra_hosts", "links", "external_links",
                "dns", "dns_search", "dns_opt")):
            reject(f"{name}: forbidden port/device/link/dns host override")
        if service.get("image") != EXPECTED_IMAGES[name]:
            reject(f"{name}: unreviewed image")
        if service.get("pull_policy") != "never":
            reject(f"{name}: image pulls must stay disabled")
        validate_resource_bounds(name, service)
        expected_caps = (
            {"CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "FOWNER"}
            if name == "db" else set()
        )
        if set(service.get("cap_add") or []) != expected_caps:
            reject(f"{name}: unexpected Linux capabilities")
        if "ALL" not in (service.get("cap_drop") or []):
            reject(f"{name}: missing cap_drop ALL")
        if set(service.get("security_opt") or []) != {"no-new-privileges:true"}:
            reject(f"{name}: unexpected security profile override")
        if name == "agent":
            expected_networks = {"lab", "proxy_clients"}
        elif name == "egress-proxy":
            expected_networks = {"proxy_clients", "outgoing"}
        else:
            expected_networks = {"lab"}
        only_network(service, expected_networks, name)

    agent = services["agent"]
    if not agent.get("read_only") or str(agent.get("user")) not in ("1000:1000", "1000"):
        reject("agent must run nonroot with read-only rootfs")
    if agent.get("entrypoint") or agent.get("command") != ["sleep", "infinity"]:
        reject("offline agent command/entrypoint must not change")
    if agent.get("profiles"):
        reject("agent must be in offline default profile")
    # A restart policy must not auto-start the intentionally stopped agent.
    if agent.get("restart") not in (None, "no"):
        reject("agent must not automatically restart")
    if not network_config(network_entries(agent)["lab"]):
        reject("agent application bridge overrides forbidden")
    if not network_config(network_entries(agent)["proxy_clients"], AGENT_CLIENT_IP):
        reject("agent proxy-client static address changed")

    proxy = services["egress-proxy"]
    if set(proxy.get("profiles") or []) != {"online"}:
        reject("proxy must only start with explicit online profile")
    if proxy.get("restart") not in (None, "no"):
        reject("proxy must not automatically restart")
    if not proxy.get("read_only"):
        reject("proxy must have read-only rootfs")
    if proxy.get("entrypoint") or proxy.get("command") != [
        "squid", "-N", "-f", "/etc/squid/squid.conf"
    ]:
        reject("Squid command/entrypoint must load the reviewed policy")
    if proxy.get("environment"):
        reject("unreviewed Squid environment overrides")
    if not network_config(network_entries(proxy)["proxy_clients"], PROXY_CLIENT_IP):
        reject("proxy client IP changed")
    if not network_config(network_entries(proxy)["outgoing"]):
        reject("proxy outgoing network overrides forbidden")
    if proxy.get("secrets"):
        reject("Squid must not receive secrets")

    for name in ("db", "redis-cache", "redis-queue"):
        if not network_config(network_entries(services[name])["lab"]):
            reject(f"{name}: lab network overrides forbidden")
    for name in ("redis-cache", "redis-queue"):
        if services[name].get("user") != "redis":
            reject(f"{name}: Redis must run as nonroot")

    env = agent.get("environment") or {}
    if not isinstance(env, dict):
        reject("unexpected agent environment shape")
    if env.get("HTTP_PROXY") != "http://egress-proxy:3128" or \
       env.get("HTTPS_PROXY") != "http://egress-proxy:3128" or \
       env.get("ALL_PROXY", None) != "":
        reject("agent proxy routing changed")
    if env.get("NO_PROXY") != "localhost,127.0.0.1,db,redis-cache,redis-queue":
        reject("agent no-proxy route changed")
    if any(key.lower() in {"http_proxy", "https_proxy", "all_proxy", "no_proxy"}
           and key not in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}
           for key in env):
        reject("conflicting agent proxy environment")

    mounts = agent.get("volumes") or []
    expected_mounts = {"/home/frappe", "/home/frappe/.cache"}
    destinations = {m.get("target") for m in mounts if isinstance(m, dict)}
    if destinations != expected_mounts or len(mounts) != len(expected_mounts):
        reject("agent mount destinations differ from private allowlist")
    for m in mounts:
        if m.get("type") != "volume" or m.get("source") not in {"agent-home", "agent-cache"}:
            reject("agent may not bind host path or reuse shared volume")
    for sec in agent.get("secrets") or []:
        source = sec.get("source") if isinstance(sec, dict) else sec
        if source != "db-user-password":
            reject("agent may hold only synthetic DB user secret")

    proxy_mounts = proxy.get("volumes") or []
    if len(proxy_mounts) != 1 or not isinstance(proxy_mounts[0], dict):
        reject("proxy must mount only its read-only policy file")
    mount = proxy_mounts[0]
    if (mount.get("type") != "bind" or
        not str(mount.get("source") or "").endswith("/codex-dev-agent/proxy/squid.conf") or
        mount.get("target") != "/etc/squid/squid.conf" or
        mount.get("read_only") is not True):
        reject("proxy policy bind mount unreviewed")

    secret_defs = rendered.get("secrets") or {}
    if set(secret_defs) != {"db-user-password", "db-root-password"}:
        reject("unexpected Docker secrets")
    for name, definition in secret_defs.items():
        declared = str(definition.get("file") or "")
        if not declared.endswith("/codex-dev-agent/local-secrets/" + name):
            reject("synthetic secrets must stay in excluded local directory")

    for name in ("db", "redis-cache", "redis-queue"):
        for mount in services[name].get("volumes") or []:
            if mount.get("type") != "volume":
                reject(f"{name}: unexpected bind or host mount")

    # Never silently skip the Squid policy gate for callers of validate().
    # The on-disk source file is the same one the proxy bind-mount would use.
    if proxy_policy is None:
        try:
            proxy_policy = (HERE / "proxy" / "squid.conf").read_text(
                encoding="utf-8"
            )
        except OSError:
            reject("Squid policy unavailable")
    validate_proxy_policy(proxy_policy)
    return True


def main():
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(HERE / "compose.yaml"),
             "--profile", "online", "config", "--format", "json"],
            cwd=HERE, capture_output=True, text=True, check=True,
        )
        policy = (HERE / "proxy" / "squid.conf").read_text(encoding="utf-8")
        validate(json.loads(result.stdout), proxy_policy=policy)
    except (ValueError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print("STOP: Compose/Squid static preflight FAILED:", type(exc).__name__)
        return 1
    print("PASS: proposed Compose + Squid source-only review gate")
    print("NOT VERIFIED: host subnet/route overlap, host INPUT/forwarding, DNS rebinding")
    print("NOT VERIFIED: image digest/user, Squid parser/runtime, allowlist suitability")
    print("NOT VERIFIED: Codex CLI sandbox/auth, socket bypass or production isolation")
    print("Do not run the agent or online Squid profile without separate tests and approval.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
