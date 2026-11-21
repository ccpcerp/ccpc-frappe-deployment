# Step 130 — read-only Docker/UFW/systemd lifecycle inventory (review-only)

**Date:** 2026-11-20 (Asia/Manila). **Status:** Exact-command REVIEW; not yet authorized for execution. **Source:** PR #39 review branch.

## Intent and limits

Inspect effective systemd metadata for Docker service/socket, UFW and the **disabled** stock nftables unit, and confirm only the already-known original lab agent remains stopped with Docker restart policy `no`. Report fixed, sanitized booleans describing socket activation relationships, direct service ordering/dependencies, reload handlers, startup hooks and service drop-ins. The optional project nft guard and offline launch units must remain absent.

This is not a persistence test, packet probe, systemd boot dependency graph, firewall trace, IPv6 test, cross-bridge isolation test, or an unbypassable Codex launch gate. Existing Step 124 and Step 126 successful single-path IPv4 tests remain narrow, non-causal evidence.

## Proposed exact operator command — NOT YET AUTHORIZED TO RUN

The command invokes only `systemctl show` and `docker inspect --format` from a root Python process. It does not call `systemctl start/stop/restart/reload`, `nft`, `iptables`, `ufw`, `docker start`, `docker compose`, or any write operation. It fails closed if the host identity, active Docker/UFW baseline, disabled stock nftables unit, missing optional project units, stopped agent or disabled restart policy differ. Raw metadata and stderr are suppressed; only fixed booleans are printed. Bounded external calls have eight-second timeouts.

**Residual operational caveat:** A Docker inspection contacts the Docker API. Although `docker.service` is checked active first, there is an unavoidable race: if the daemon exits after that check and the socket remains listening, a Docker client connection could cause systemd socket activation. Consequently, this is a read-only **intent** with a small lifecycle race, not a mathematically guaranteed no-activation operation. An operator who cannot accept even that risk should instead approve a smaller systemd-only metadata variant; do not run this version during concurrent service maintenance.

```bash
sudo python3 -I - <<'PY'
import json
import os
import subprocess
import sys

HOST = "ccpcerpserver"
AGENT = "ccpc_codex_dev_agent-agent-1"
CORE = ("docker.service", "docker.socket", "ufw.service", "nftables.service")
OPTIONAL = ("ccpc-codex-nft-guard.service", "ccpc-codex-offline-launch.service")
PROPS = ("LoadState", "ActiveState", "UnitFileState", "After", "Before",
         "Requires", "Wants", "Triggers", "TriggeredBy", "DropInPaths",
         "ExecStartPre", "ExecStart", "ExecStartPost", "ExecReload",
         "ExecStop", "ExecStopPost")

class Stop(Exception):
    pass

def read(argv):
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=8, check=False,
                           env={"LC_ALL": "C", "PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Stop() from exc
    if p.returncode or len(p.stdout) > 100000:
        raise Stop()
    return p.stdout.strip()

def unit(name):
    raw = read(["systemctl", "show", "--no-pager",
                "--property=" + ",".join(PROPS), name])
    props = {}
    for line in raw.splitlines():
        if "=" not in line:
            raise Stop()
        key, value = line.split("=", 1)
        if key in props or key not in PROPS:
            raise Stop()
        props[key] = value
    if not {"LoadState", "ActiveState", "UnitFileState"} <= props.keys():
        raise Stop()
    return props

def tokens(p, key):
    return set(p.get(key, "").split())

def docker_field(template):
    result = read(["docker", "--host", "unix:///var/run/docker.sock",
                   "inspect", "--format", template, AGENT])
    try:
        return json.loads(result)
    except (ValueError, TypeError) as exc:
        raise Stop() from exc

def emit(name, value):
    print(name + "=" + ("True" if value else "False"))

def main():
    if os.uname().nodename != HOST or os.geteuid() != 0:
        raise Stop()
    u = {name: unit(name) for name in CORE + OPTIONAL}
    d, s, f, n = (u[name] for name in CORE)
    if not (d["LoadState"] == "loaded" and d["ActiveState"] == "active"
            and s["LoadState"] == "loaded"
            and f["LoadState"] == "loaded" and f["ActiveState"] == "active"
            and n["ActiveState"] == "inactive" and n["UnitFileState"] == "disabled"
            and all(u[name]["LoadState"] == "not-found" for name in OPTIONAL)):
        raise Stop()
    running = docker_field("{{json .State.Running}}")
    restarting = docker_field("{{json .State.Restarting}}")
    policy = docker_field("{{json .HostConfig.RestartPolicy.Name}}")
    if running is not False or restarting is not False or policy != "no":
        raise Stop()
    emit("AGENT_STOPPED_AND_RESTART_DISABLED", True)
    emit("DOCKER_SERVICE_ACTIVE", True)
    emit("DOCKER_SOCKET_ACTIVE", s["ActiveState"] == "active")
    emit("DOCKER_SOCKET_ENABLED", s["UnitFileState"] == "enabled")
    emit("SOCKET_DECLARED_TRIGGER_TO_DOCKER", "docker.service" in tokens(s, "Triggers"))
    emit("DOCKER_DECLARED_TRIGGERED_BY_SOCKET", "docker.socket" in tokens(d, "TriggeredBy"))
    emit("DOCKER_AFTER_UFW", "ufw.service" in tokens(d, "After"))
    emit("UFW_BEFORE_DOCKER", "docker.service" in tokens(f, "Before"))
    emit("DOCKER_REQUIRES_OR_WANTS_UFW", "ufw.service" in (tokens(d, "Requires") | tokens(d, "Wants")))
    emit("UFW_REQUIRES_OR_WANTS_DOCKER", "docker.service" in (tokens(f, "Requires") | tokens(f, "Wants")))
    emit("DOCKER_RELOAD_EXEC_PRESENT", bool(d.get("ExecReload", "")))
    emit("UFW_RELOAD_EXEC_PRESENT", bool(f.get("ExecReload", "")))
    emit("DOCKER_DROPINS_PRESENT", bool(d.get("DropInPaths", "")))
    emit("UFW_DROPINS_PRESENT", bool(f.get("DropInPaths", "")))
    emit("DOCKER_START_HOOKS_PRESENT", bool(d.get("ExecStartPre", "") or d.get("ExecStartPost", "")))
    emit("UFW_START_HOOKS_PRESENT", bool(f.get("ExecStartPre", "") or f.get("ExecStartPost", "")))
    emit("SCOPED_GUARD_UNIT_ABSENT", True)
    emit("OFFLINE_LAUNCH_UNIT_ABSENT", True)
    emit("STOCK_NFT_SERVICE_INACTIVE_DISABLED", True)
    emit("PERSISTENCE_VERIFIED", False)
    emit("CODEX_LAUNCH_AUTHORIZED", False)
    print("STEP_130_READ_ONLY_METADATA_COMPLETE")

try:
    main()
except (Stop, KeyError, TypeError, ValueError):
    print("STOP: Step 130 read-only prerequisites or metadata verification failed")
    sys.exit(1)
PY
```

## Evidence handling and stop conditions

- Do not execute this command merely because its text is in GitHub. It requires **separate exact-command operator approval** after reviewing this version; previous broad permission was only to prepare Step 130.
- Before executing, preserve the two administrator SSH/recovery access paths and private Stage A firewall baseline already used for controlled firewall testing. Confirm no ongoing Docker/UFW maintenance and keep Codex/Squid stopped.
- Expected final marker is `STEP_130_READ_ONLY_METADATA_COMPLETE`; it does **not** mean that persistence is verified. `PERSISTENCE_VERIFIED=False` and `CODEX_LAUNCH_AUTHORIZED=False` are deliberately fixed.
- On `STOP:` or any missing final marker, do **not** rerun automatically, mutate firewall rules, restart services, disable safety checks, or activate the agent. Bring only the sanitized output back for review.
- Even on a clean pass, do not install the optional service, enable stock `nftables.service`, reload UFW/Docker, reboot, create Docker networks/containers, launch Codex/Squid, or contact DEVELOPMENT/UAT/PRODUCTION service targets.
- This command identifies declared immediate unit properties. It does not exhaust transitive systemd ordering, daemon-specific hooks, configuration files, non-systemd launch routes, privileged manual bypass, or a possible Docker daemon/socket state change between checks.

**Next gate after a reviewed result:** Evaluate whether a genuinely fail-closed launch hold can survive all relevant lifecycle changes. Any future active reload/reboot/traffic experiment requires a separate scoped approval and recovery plan; PR #39 remains draft and Codex activation **NO-GO**.
