#!/usr/bin/env bash
# PR #27: source-only smoke tests. No Docker daemon, network, image build or secrets.
set -euo pipefail

repo=$(git rev-parse --show-toplevel)
cd "$repo"
bash -n scripts/config.sh

run_profile() {
  local profile="$1"
  local -a clean_env=(-u HTTP_PUBLISH_PORT -u FRAPPE_SITE_NAME_HEADER)
  if [[ "$profile" == UNSET ]]; then
    clean_env+=(-u CCPC_DEPLOYMENT_PROFILE)
  else
    clean_env+=("CCPC_DEPLOYMENT_PROFILE=$profile")
  fi
  env "\${clean_env[@]}" bash -c '
    set -euo pipefail
    source scripts/config.sh
    printf "health=%s\n" "$HEALTHCHECK_URL"
    printf "%s\n" "\${COMPOSE_FILE_ARGS[@]}"
  '
}

expected_legacy=$'health=http://127.0.0.1:80\n-f\ncompose.yaml\n-f\noverrides/compose.mariadb.yaml\n-f\noverrides/compose.redis.yaml\n-f\noverrides/compose.lan-production.yaml'
expected_dedicated=$'health=http://127.0.0.1:8080\n-f\ncompose.yaml\n-f\noverrides/compose.mariadb.yaml\n-f\noverrides/compose.redis.yaml\n-f\noverrides/compose.lan-production.yaml\n-f\noverrides/compose.dedicated-pre-tls.yaml'

[[ "$(run_profile UNSET)" == "$expected_legacy" ]] ||
  { echo "FAIL: default profile changed" >&2; exit 1; }
[[ "$(run_profile legacy-lan)" == "$expected_legacy" ]] ||
  { echo "FAIL: explicit legacy profile changed" >&2; exit 1; }
[[ "$(run_profile dedicated-pre-tls)" == "$expected_dedicated" ]] ||
  { echo "FAIL: dedicated Compose file order or health check changed" >&2; exit 1; }

if run_profile INVALID-PROFILE >/dev/null 2>&1; then
  echo "FAIL: unsupported deployment profile accepted" >&2
  exit 1
fi

grep -Fqx '    ports: !override' overrides/compose.dedicated-pre-tls.yaml ||
  { echo "FAIL: explicit published port override absent" >&2; exit 1; }
grep -Fqx '      - "127.0.0.1:8080:8080/tcp"' overrides/compose.dedicated-pre-tls.yaml ||
  { echo "FAIL: dedicated port is not local-only" >&2; exit 1; }
grep -Fqx '      MYSQL_ROOT_PASSWORD: "\${DB_PASSWORD:?Dedicated production requires a nonempty DB_PASSWORD}"' overrides/compose.dedicated-pre-tls.yaml ||
  { echo "FAIL: nonempty dedicated DB password guard absent" >&2; exit 1; }

printf '%s\n' 'PASS: PR #27 profile and source guard smoke tests (STATIC only; Compose v2 not run)'
