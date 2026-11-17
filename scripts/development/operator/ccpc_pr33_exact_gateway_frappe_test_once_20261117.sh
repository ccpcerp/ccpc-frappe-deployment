#!/usr/bin/env bash
# Exact-HEAD GitHub Frappe v16 regression verification, no deployed code update.
# One read-only DB transaction, in-memory candidate modules; no CI or prod.
set -euo pipefail
umask 077
stop() { echo "STOP: $1" >&2; exit 1; }
[[ "$(hostname -s)" = "ccpcerpserver" ]] || stop "wrong host"
[[ "$(id -un)" = "gani" ]] || stop "wrong operator"
[[ -z "${DOCKER_HOST:-}${DOCKER_CONTEXT:-}${DOCKER_CONFIG:-}" ]] || stop "Docker override present"
[[ -z "${GIT_CONFIG_GLOBAL:-}${GIT_CONFIG_SYSTEM:-}" ]] || stop "Git config override present"
sudo -v || stop "operator sudo authentication unavailable"

APP_REPO='git@github.com:ccpcerp/ccpcerp.git'
BRANCH='review/billing-authorization-correction-2026-11-03'
NEW_SHA='25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87'
GATEWAY='ccpcerp/ccpc_erp/executive_reporting.py'
TEST='ccpcerp/ccpc_erp/test_executive_reporting.py'
DEV='frappe_docker_devcontainer-frappe-1'

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
DRIVER="$SCRIPT_DIR/ccpc_pr33_exact_gateway_frappe_test_driver_20261117.py"
[[ -f "$DRIVER" && ! -L "$DRIVER" ]] || stop "reviewed driver unavailable"
[[ "$(git hash-object "$DRIVER")" = '58330751ea03d3ad06a79b142434f7f75002ff4a' ]] ||
  stop "reviewed driver blob mismatch"

[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" = true ]] ||
  stop "DEV container not running"
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" = frappe_docker_devcontainer ]] ||
  stop "wrong DEV Docker project"

# Fetch distinct temporary SOURCE-ONLY checkout on host; never change the
# actual DEV app checkout used by MAIN and Integration2.
SOURCE_DIR="$(mktemp -d "$HOME/ccpc-pr33-gateway-exact-source-XXXXXXXX")"
GIT_TERMINAL_PROMPT=0 \
GIT_SSH_COMMAND='ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10' \
git clone --quiet --depth 1 --single-branch --branch "$BRANCH" "$APP_REPO" "$SOURCE_DIR/app" ||
  stop "private GitHub exact-source fetch failed"
[[ "$(git -C "$SOURCE_DIR/app" rev-parse HEAD)" = "$NEW_SHA" ]] ||
  stop "app PR33 head changed, review required"
[[ "$(git -C "$SOURCE_DIR/app" status --porcelain=v1 --untracked-files=all)" = "" ]] ||
  stop "temporary candidate checkout not clean"
[[ "$(git -C "$SOURCE_DIR/app" hash-object "$SOURCE_DIR/app/$GATEWAY")" = d75ffe318788d1cd8e3b8217a74dc3f9d8860cb4 ]] ||
  stop "candidate gateway hash mismatch"
[[ "$(git -C "$SOURCE_DIR/app" hash-object "$SOURCE_DIR/app/$TEST")" = b78b42a858b9b1a98ca5be79b4037eb7c7b7a1fa ]] ||
  stop "candidate tests hash mismatch"
echo 'EXACT_CANDIDATE_GITHUB_HEAD=PASS'

# tar contains exactly reviewed driver plus two source files. Bootstrap reads
# tar in memory; it never extracts files to the deployed DEV code checkout.
BOOTSTRAP='
import io
import sys
import tarfile
data = sys.stdin.buffer.read(131073)
if len(data) > 131072:
    raise SystemExit("STOP: streamed source exceeded limit")
expected = {
    "ccpcerp/ccpc_erp/executive_reporting.py",
    "ccpcerp/ccpc_erp/test_executive_reporting.py",
    "ccpc_pr33_exact_gateway_frappe_test_driver_20261117.py",
}
try:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        members = archive.getmembers()
        if {m.name for m in members} != expected or not all(m.isfile() for m in members):
            raise ValueError("unexpected tar entries")
        items = {m.name: archive.extractfile(m).read() for m in members}
except (tarfile.TarError, ValueError, OSError):
    raise SystemExit("STOP: exact-source tar validation failed")
driver_name = "ccpc_pr33_exact_gateway_frappe_test_driver_20261117.py"
driver = items.pop(driver_name)
namespace = {"__name__": "__main__", "__file__": driver_name, "payload": items}
exec(compile(driver, driver_name, "exec"), namespace, namespace)
'
# Source files and driver remain only in memory inside Frappe. No installation,
# no writes to existing app checkout, no fixtures, migration or bench CLI.
tar -cf - \
  -C "$SOURCE_DIR/app" "$GATEWAY" "$TEST" \
  -C "$SCRIPT_DIR" 'ccpc_pr33_exact_gateway_frappe_test_driver_20261117.py' |
  sudo -n docker exec -i --user frappe "$DEV" bash -c \
  'set -euo pipefail; cd /workspace/development/frappe-bench/sites; FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -c "$1"' \
  -- "$BOOTSTRAP"
echo 'PR33_OPERATOR_RUNTIME_VERIFICATION=COMPLETE'
