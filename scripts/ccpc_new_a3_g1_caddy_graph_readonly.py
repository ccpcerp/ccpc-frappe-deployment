"""NEW A3 G1 Caddyfile and systemd graph FACT inventory; read-only.

Never print Caddy config, TLS locations, unit ExecStart, env or certificates.
This is an inventory, NOT approval of boot, HTTPS trust or routing.
"""
import os
from pathlib import Path
import re
import socket
import stat
import subprocess


def read(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          timeout=20).stdout


def show(unit):
    fields = ("LoadState,ActiveState,UnitFileState,DropInPaths,ExecStart,"
              "Requires,After,Wants,RequiredBy,WantedBy,TriggeredBy,Triggers")
    out = read("systemctl", "show", unit, "--no-pager", "--property=" + fields)
    props = dict(line.split("=", 1) for line in out.splitlines() if "=" in line)
    assert {"LoadState", "ActiveState", "UnitFileState"} <= props.keys()
    return props


def bool_line(label, condition):
    print("CCPC_NEW_A3_G1_" + label + "=" + ("YES" if condition else "NO"))


def inspect():
    assert os.geteuid() == 0
    assert os.environ.get("SUDO_USER") == "ccpcadmin"
    assert socket.gethostname().split(".")[0] == "ccpcerp-prod"
    assert not any(k in os.environ for k in ("DOCKER_HOST", "DOCKER_CONTEXT"))

    names = ("docker.service", "containerd.service", "caddy.service",
             "ccpc-erpnext-upstream.socket", "ccpc-erpnext-upstream.service",
             "caddy-api.service")
    units = {n: show(n) for n in names}
    assert units["caddy.service"]["LoadState"] == "loaded"
    assert units["caddy.service"]["ActiveState"] == "active"
    assert units["caddy.service"]["UnitFileState"] == "disabled"
    assert units["ccpc-erpnext-upstream.socket"]["UnitFileState"] == "disabled"

    caddy = units["caddy.service"]
    sock = units["ccpc-erpnext-upstream.socket"]
    relay = units["ccpc-erpnext-upstream.service"]
    bool_line("CADDY_UNIT_CONFIG_PATH_MATCH",
              bool(re.search(r"--config(?:=|\s+)/etc/caddy/Caddyfile(?:\s|[;}]|$)",
                             caddy.get("ExecStart", ""))))
    for label, item in (("CADDY", caddy), ("SOCKET", sock), ("RELAY", relay)):
        bool_line(label + "_DROPINS_PRESENT", bool(item.get("DropInPaths", "").strip()))
    for label, item in (("CADDY", caddy), ("SOCKET", sock)):
        # Loaded-unit reverse edges only; unloaded units/indirect boot triggers
        # still require a separate graph review. Print no unit-name values.
        bool_line(label + "_REVERSE_EDGES_PRESENT",
                  any(item.get(k, "").strip() for k in
                      ("RequiredBy", "WantedBy", "TriggeredBy")))
    def member(item, prop, name):
        return name in item.get(prop, "").split()
    bool_line("RELAY_REQUIRES_SOCKET",
              member(relay, "Requires", "ccpc-erpnext-upstream.socket"))
    bool_line("RELAY_AFTER_SOCKET",
              member(relay, "After", "ccpc-erpnext-upstream.socket"))
    bool_line("CADDY_DIRECTLY_AFTER_DOCKER",
              member(caddy, "After", "docker.service"))

    file = Path("/etc/caddy/Caddyfile")
    info = file.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_uid == 0
    assert (stat.S_IMODE(info.st_mode) & 0o022) == 0
    config = file.read_text(encoding="utf-8")
    # Expected source is PR #28's review template, ignoring full-line comments
    # and TLS path tokens; an unknown shape is REVIEW, not a security PASS.
    lines = [s for raw in config.splitlines()
             if (s := raw.strip()) and not s.startswith("#")]
    expected = ["{", "admin off", "auto_https off",
                "servers 192.168.50.186:443 {", "protocols h1 h2",
                "strict_sni_host on", "}", "}",
                "https://ccpcerp.internal:443 {", "bind 192.168.50.186",
                "TLS_TWO_PATH_TOKENS", "reverse_proxy 127.0.0.1:8080", "}"]
    actual = []
    for line in lines:
        parts = line.split()
        if len(parts) == 3 and parts[0] == "tls":
            # Never print path strings, even if a template differs.
            actual.append("TLS_TWO_PATH_TOKENS")
        else:
            actual.append(line)
    bool_line("CADDYFILE_REVIEW_TEMPLATE_SHAPE", actual == expected)

    udp443 = False
    for line in read("ss", "-H", "-lun").splitlines():
        fields = line.split()
        assert len(fields) >= 5
        if fields[3].rpartition(":")[2] == "443":
            udp443 = True
    bool_line("UDP443_LISTENER_PRESENT", udp443)
    print("CCPC_NEW_A3_G1_CADDY_GRAPH_READONLY_INVENTORY_COMPLETE")


if __name__ == "__main__":
    try:
        inspect()
    except Exception:
        print("CCPC_NEW_A3_G1_CADDY_GRAPH_STOP_REVIEW_REQUIRED")
        raise SystemExit(1) from None
