#!/usr/bin/env python3
"""Human operator only. Execute the reviewed DEVELOPMENT preflight in one command."""
import argparse
from contextlib import closing, redirect_stderr, redirect_stdout
from getpass import GetPassWarning, getpass
import hashlib
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import types
import warnings
from zoneinfo import ZoneInfo

HOST = "ccpcerpserver"
SITE = "development.localhost"
BENCH = "/workspace/development/frappe-bench"
HOST_APP = "/home/gani/deployments/frappe_docker/development/frappe-bench/apps/ccpcerp"
FRAPPE_CONTAINER = "frappe_docker_devcontainer-frappe-1"
COMMIT = "e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5"
AUDIT_SHA256 = "556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927"
DOCKER = ("/usr/bin/docker", "--host", "unix:///var/run/docker.sock")
COMMAND_ENV = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LC_ALL": "C"}
FRAME = "CCPC_READONLY_RESULT="
STATUS_LINE = re.compile(r"(PASS|FAIL|UNVERIFIED) \| [A-Za-z0-9 /-]+ \| [^\r\n\x00-\x1f]{1,240}")


class Stop(Exception):
    """An audit stop with a fixed sanitized message."""


def require(condition, message):
    if not condition:
        raise Stop(message)


def validated_binding(spec):
    require(spec["site_reviewer"] and spec["database_reviewer"]
            and spec["site_reviewer"].strip().casefold() != spec["database_reviewer"].strip().casefold(),
            "Independent site and database reviewers required.")
    target = spec["site_binding"]
    require(target == spec["database_binding"]
            and (target["host"], target["site"], target["commit"]) == (HOST, SITE, COMMIT),
            "Independent site, server or commit binding mismatch.")
    for key in ("app_container_id", "db_container_id", "network_id"):
        require(bool(re.fullmatch(r"[0-9a-f]{64}", target[key])), "Exact Docker identities required.")
    require(target["app_container_id"] != target["db_container_id"], "Separate expected app and database containers required.")
    ip = ipaddress.IPv4Address(target["db_ip"])
    require(ip.is_private and not (ip.is_loopback or ip.is_link_local or ip.is_unspecified
                                   or ip.is_multicast or ip.is_reserved),
            "An approved private DEVELOPMENT Docker address is required.")
    require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", target["db_host"]))
            and bool(re.fullmatch(r"[A-Za-z0-9_]+", target["schema"]))
            and bool(re.fullmatch(r"[A-Za-z0-9_]+@[A-Za-z0-9.:%_-]+", target["principal"]))
            and type(target["port"]) is int and 0 < target["port"] < 65536
            and type(target["server_id"]) is int and target["server_id"] >= 0
            and bool(target["server_hostname"]), "Private database identity inputs are invalid.")
    ZoneInfo(target["timezone"])
    keys = {"slip", "company", "requesting", "beneficiary", "equipment", "item", "warehouse", "expense"}
    require(set(target["pilot"]) == keys and all(
        isinstance(value, str) and value and value == value.strip() and len(value) <= 140
        and not any(ord(c) < 32 for c in value) for value in target["pilot"].values()
    ), "The privately agreed exact pilot fields are incomplete.")
    return target


def command(argv, *, input_text=None, timeout=15):
    finished = subprocess.run(
        argv, input=input_text, capture_output=True, text=True, timeout=timeout,
        env=COMMAND_ENV, check=False,
    )
    require(finished.returncode == 0, "A fixed host or container command failed; raw output withheld.")
    return finished.stdout


def host_preflight(target, invoke=command):
    require(os.geteuid() != 0 and socket.gethostname().split(".", 1)[0] == HOST,
            "Wrong host or operator identity.")
    path = invoke(("/usr/bin/git", "--no-optional-locks", "-C", HOST_APP, "rev-parse", "--show-toplevel")).strip()
    require(path == HOST_APP, "Unexpected DEVELOPMENT app checkout path.")
    git = ("/usr/bin/git", "--no-optional-locks", "-C", HOST_APP)
    require(invoke((*git, "rev-parse", "HEAD")).strip() == COMMIT
            and not invoke((*git, "status", "--porcelain=v1", "--untracked-files=all")).strip()
            and (Path(HOST_APP).parent.parent / "sites" / SITE).is_dir(),
            "Wrong source commit, dirty checkout or missing DEVELOPMENT site directory.")

    def metadata(container_id):
        template = '{{.Id}}\n{{.Name}}\n{{.State.Running}}\n{{json .NetworkSettings.Networks}}'
        actual, name, running, networks = invoke(
            (*DOCKER, "inspect", "--type", "container", "--format", template, container_id),
        ).strip().splitlines()
        require(actual == container_id and running == "true", "Pinned DEVELOPMENT container not running.")
        return name, list(json.loads(networks).values())

    app_name, app_networks = metadata(target["app_container_id"])
    _, db_networks = metadata(target["db_container_id"])
    require(app_name == "/" + FRAPPE_CONTAINER
            and any(n["NetworkID"] == target["network_id"] for n in app_networks)
            and any(n["NetworkID"] == target["network_id"] and n["IPAddress"] == target["db_ip"]
                    for n in db_networks),
            "DEVELOPMENT container or shared database network binding mismatch.")


def load_audit(source):
    require(hashlib.sha256(source.encode()).hexdigest() == AUDIT_SHA256,
            "PR41 audit source digest does not match.")
    mod = types.ModuleType("_ccpc_pinned_ws_audit")
    sys.modules[mod.__name__] = mod
    exec(compile(source, "ws_readiness_audit.py", "exec"), mod.__dict__)
    return mod


def verified_database_config(config, target, resolver=socket.getaddrinfo):
    require(config.get("db_type", "mariadb") == "mariadb" and not config.get("db_socket")
            and not config.get("extra_config")
            and not any(value for key, value in config.items() if key.startswith("db_ssl")),
            "Unsupported socket, TLS or Frappe configuration hook; use separately reviewed access.")
    require(config.get("db_name") == target["schema"]
            and config.get("db_host") == target["db_host"]
            and int(config.get("db_port") or 3306) == target["port"]
            and (config.get("db_user") or config.get("db_name")) == target["principal"].split("@")[0]
            and config.get("db_password"), "Site database configuration did not match the approved binding.")
    resolved = {info[4][0] for info in resolver(target["db_host"], target["port"], type=socket.SOCK_STREAM)}
    require(resolved == {target["db_ip"]}, "Site database hostname did not resolve exclusively to the pinned container.")


def audited_snapshot(connection, audit, target, issuer, lines):
    with closing(connection), closing(connection.cursor()) as cursor:
        try:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            cursor.execute("START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY")

            def read(sql, args=()):
                # Only fixed statements compiled from the two pinned modules call this.
                require(sql.startswith("SELECT ") and not any(
                    token in sql.upper() for token in (";", "FOR UPDATE", "LOCK IN SHARE MODE",
                                                       "OUTFILE", "DUMPFILE", "/*", "--")
                ), "Statement outside fixed SELECT boundary.")
                cursor.execute(sql, args)
                keys = [col[0] for col in cursor.description]
                return [dict(zip(keys, row)) for row in cursor.fetchall()]

            identity = audit.single(read(
                "SELECT DATABASE() AS db,CURRENT_USER() AS principal,@@hostname AS hostname,"
                "@@server_id AS server_id,VERSION() AS version"
            ))
            require(identity and identity["db"] == target["schema"]
                    and identity["principal"] == target["principal"]
                    and identity["hostname"] == target["server_hostname"]
                    and identity["server_id"] == target["server_id"]
                    and "mariadb" in identity["version"].lower(),
                    "Connected server, schema or authenticated site account did not match.")
            result = audit.Results(lines.append)
            result.emit("PASS", "DEVELOPMENT binding",
                        "Source, container, database configuration and server identity confirmed.")
            audit.run_snapshot(read, result, issuer, target["timezone"], audit.Pilot(**target["pilot"]))
            result.finish()
        finally:
            connection.rollback()


def guest(payload):
    lines = []
    # App imports, drivers, unexpected exception messages and config data never
    # reach the host terminal. Only the pinned code's structured status frame does.
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        try:
            target = validated_binding(payload["binding"])
            audit = load_audit(payload["audit"])
            require(Path.cwd() == Path(BENCH) and os.geteuid() != 0, "Wrong bench path or container user.")
            audit.require_source()
            require(not any(key.startswith("FRAPPE_DB_") for key in os.environ),
                    "Unsupported environment override for site database identity.")
            # Load only the two normal Frappe configuration files. Do not invoke
            # Frappe config hooks, login, document controllers or worker code.
            config = {}
            for file in ("sites/common_site_config.json", f"sites/{SITE}/site_config.json"):
                config.update(json.loads(Path(file).read_text()))
            verified_database_config(config, target)
            import MySQLdb

            connection = MySQLdb.connect(
                host=target["db_ip"], port=target["port"],
                user=config.get("db_user") or config["db_name"],
                passwd=config["db_password"], db=target["schema"],
                charset="utf8mb4", local_infile=False, multi_statements=False,
                connect_timeout=5, read_timeout=15, write_timeout=5,
            )
            audited_snapshot(connection, audit, target, payload["issuer"], lines)
        except (Stop, audit_stop_type()) as exc:
            lines.append(f"UNVERIFIED | Operator preflight | {exc}")
        except Exception:
            lines.append("UNVERIFIED | Operator preflight | Restricted audit stopped; raw error withheld.")
    print(FRAME + json.dumps(lines, ensure_ascii=True))


def audit_stop_type():
    module = sys.modules.get("_ccpc_pinned_ws_audit")
    return module.Stop if module else Stop


def execute(spec, issuer, runner_source, audit_source, invoke=command, preflight=host_preflight):
    target = validated_binding(spec)
    require(hashlib.sha256(audit_source.encode()).hexdigest() == AUDIT_SHA256, "PR41 audit source digest does not match.")
    preflight(target, invoke)
    # Source modules are reviewed and pinned. The private input is serialized
    # as a quoted JSON string, so operator data cannot become Python code.
    payload = json.dumps({"binding": spec, "issuer": issuer, "audit": audit_source}, ensure_ascii=True)
    script = ("import types\n"
              "module = types.ModuleType('_ccpc_operator_guest')\n"
              "import sys\nsys.modules[module.__name__] = module\n"
              f"exec(compile({runner_source!r}, 'operator_preflight.py', 'exec'), module.__dict__)\n"
              f"module.guest(module.json.loads({payload!r}))\n")
    out = invoke((*DOCKER, "exec", "-i", "--user", "frappe", "--workdir", BENCH,
                  target["app_container_id"], "./env/bin/python", "-I", "-B", "-"),
                 input_text=script, timeout=120)
    frames = [line.removeprefix(FRAME) for line in out.splitlines() if line.startswith(FRAME)]
    require(len(frames) == 1, "Container did not return one valid sanitized audit frame.")
    lines = json.loads(frames[0])
    require(isinstance(lines, list) and 1 <= len(lines) <= 100
            and all(isinstance(line, str) and STATUS_LINE.fullmatch(line) for line in lines),
            "Container did not return valid sanitized audit statuses.")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_binding", type=Path)
    args = parser.parse_args()
    try:
        require(sys.stdin.isatty(), "A human operator terminal is required.")
        me = Path(__file__).resolve()
        spec = json.loads(args.private_binding.read_text())
        with warnings.catch_warnings():
            warnings.simplefilter("error", GetPassWarning)
            issuer = getpass("Proposed Stockroom issuer login (hidden): ").strip()
        require(0 < len(issuer) <= 140 and not any(ord(c) < 32 for c in issuer), "Valid proposed issuer required.")
        lines = execute(spec, issuer, me.read_text(), me.with_name("ws_readiness_audit.py").read_text())
    except Stop as exc:
        lines = [f"UNVERIFIED | Operator preflight | {exc}"]
    except (Exception, KeyboardInterrupt):
        lines = ["UNVERIFIED | Operator preflight | Host or container check stopped; raw error withheld."]
    lines = [line for line in lines if " | OVERALL | " not in line]
    for line in lines:
        print(line)
    states = {line.partition(" | ")[0] for line in lines}
    status = "FAIL" if "FAIL" in states else "UNVERIFIED" if "UNVERIFIED" in states else "PASS"
    print(f"{status} | OVERALL | No posting performed. Separate authorization required before UAT.")
    return {"PASS": 0, "FAIL": 1, "UNVERIFIED": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
