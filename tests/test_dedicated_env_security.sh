#!/usr/bin/env bash
# Offline safety regression checks; replaces Docker with a Bash mock.
# Uses only disposable placeholder data, never a real production credential.
set -euo pipefail

repo=$(git rev-parse --show-toplevel)
cd "$repo"

source scripts/lib.sh
source scripts/modules/docker.sh
source scripts/modules/env.sh
source scripts/modules/deployment.sh

CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls
IMAGE_NAME=ccpcerp
unset DB_PASSWORD DOCKER_HOST DOCKER_CONTEXT TEST_DOCKER_CONTEXT TEST_DOCKER_ENDPOINT || true
unset COMPOSE_PROJECT_NAME COMPOSE_FILE COMPOSE_PROFILES || true

scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
mkdir -m 700 -- "$scratch/secure"
printf '%s\n' 'DB_PASSWORD=TEST_PLACEHOLDER_NOT_REAL' > "$scratch/secure/dedicated.env"
chmod 600 -- "$scratch/secure/dedicated.env"
CCPC_DEDICATED_ENV_FILE="$scratch/secure/dedicated.env"
COMPOSE_FILE_ARGS=(-f compose.yaml -f overrides/compose.dedicated-pre-tls.yaml)

expect_rejected() {
  local check="$1"
  shift
  if ( "$@" ) >/dev/null 2>&1; then
    printf 'FAIL: %s was accepted\n' "$check" >&2
    exit 1
  fi
  printf 'PASS: rejected %s\n' "$check"
}

verify_dedicated_env_file
printf '%s\n' 'PASS: owner-only external environment file accepted'

# The --env-file must not import Docker Compose controls or unrelated keys.
# All fixture values are disposable placeholders; never print file contents.
reject_env_contents() {
  local label="$1" contents="$2"
  printf '%s' "$contents" > "$CCPC_DEDICATED_ENV_FILE"
  expect_rejected "$label" verify_dedicated_env_file
}
reject_env_contents "missing database password key" $'# only a comment\n'
reject_env_contents "empty database password" $'DB_PASSWORD=\n'
reject_env_contents "quoted empty database password" $'DB_PASSWORD=""\n'
reject_env_contents "duplicate database password" $'DB_PASSWORD=FAKE\nDB_PASSWORD=ALSO_FAKE\n'
reject_env_contents "Compose project key in protected file" $'DB_PASSWORD=FAKE\nCOMPOSE_PROJECT_NAME=unexpected\n'
reject_env_contents "Compose file key in protected file" $'DB_PASSWORD=FAKE\nCOMPOSE_FILE=unexpected.yaml\n'
reject_env_contents "Compose profiles key in protected file" $'DB_PASSWORD=FAKE\nCOMPOSE_PROFILES=debug\n'
reject_env_contents "other Compose option in protected file" $'DB_PASSWORD=FAKE\nCOMPOSE_IGNORE_ORPHANS=true\n'
reject_env_contents "unreviewed release tag in protected file" $'DB_PASSWORD=FAKE\nCUSTOM_TAG=unexpected\n'
reject_env_contents "shell export directive in protected file" $'export DB_PASSWORD=FAKE\n'
reject_env_contents "CRLF credential file" $'DB_PASSWORD=FAKE\r\n'
printf 'DB_PASSWORD=FAKE\000COMPOSE_PROJECT_NAME=unexpected\n' > "$CCPC_DEDICATED_ENV_FILE"
expect_rejected "NUL byte credential file" verify_dedicated_env_file
printf 'DB_PASSWORD=%4096s\n' FAKE > "$CCPC_DEDICATED_ENV_FILE"
expect_rejected "oversized credential file" verify_dedicated_env_file

printf '%s\n' '# reviewed comment' '' 'DB_PASSWORD=TEST_PLACEHOLDER_NOT_REAL' > "$CCPC_DEDICATED_ENV_FILE"
verify_dedicated_env_file
printf '%s\n' 'PASS: protected file accepts only one DB_PASSWORD plus comments'
printf '%s\n' 'DB_PASSWORD=TEST_PLACEHOLDER_NOT_REAL' > "$CCPC_DEDICATED_ENV_FILE"

CCPC_DEDICATED_ENV_FILE=relative.env expect_rejected "relative path" verify_dedicated_env_file
CCPC_DEDICATED_ENV_FILE="$repo/compose.yaml" expect_rejected "file inside checkout" verify_dedicated_env_file
ln -s -- "$scratch/secure/dedicated.env" "$scratch/secure/link.env"
CCPC_DEDICATED_ENV_FILE="$scratch/secure/link.env" expect_rejected "symlink" verify_dedicated_env_file

chmod 644 -- "$scratch/secure/dedicated.env"
expect_rejected "world-readable file" verify_dedicated_env_file
chmod 600 -- "$scratch/secure/dedicated.env"

chmod 755 -- "$scratch/secure"
expect_rejected "world-searchable parent" verify_dedicated_env_file
chmod 700 -- "$scratch/secure"

reject_ambient_password() {
  DB_PASSWORD=TEST_PLACEHOLDER_NOT_REAL
  verify_dedicated_env_file
}
expect_rejected "ambient DB_PASSWORD" reject_ambient_password
unset CUSTOM_TAG || true
expect_rejected "missing explicit image tag" ccpc_compose config --quiet
CUSTOM_TAG=review-only-tag
export CUSTOM_TAG
expect_rejected "missing explicit image name" ccpc_compose config --quiet
CUSTOM_IMAGE=unexpected-image
expect_rejected "wrong image name" ccpc_compose config --quiet
CUSTOM_IMAGE="$IMAGE_NAME"
export CUSTOM_IMAGE

docker() {
  if [[ "${1:-}" == context && "${2:-}" == show ]]; then
    printf '%s\n' "${TEST_DOCKER_CONTEXT:-default}"
    return 0
  fi
  if [[ "${1:-}" == context && "${2:-}" == inspect && "${3:-}" == default &&
        "${4:-}" == --format && "${5:-}" == '{{.Endpoints.docker.Host}}' ]]; then
    printf '%s\n' "${TEST_DOCKER_ENDPOINT:-unix:///var/run/docker.sock}"
    return 0
  fi
  [[ "${1:-}" == "compose" && "${2:-}" == "--project-name" &&
     "${3:-}" == "ccpc_prod_erpnext" && "${4:-}" == "--env-file" &&
     "${5:-}" == "$CCPC_DEDICATED_ENV_FILE" ]] || return 85
  [[ "${CUSTOM_TAG:-}" == "review-only-tag" ]] || return 86
  [[ "${CUSTOM_IMAGE:-}" == "$IMAGE_NAME" ]] || return 87
  return 0
}

CUSTOM_TAG=review-only-tag
export CUSTOM_TAG
ccpc_compose config --quiet
printf '%s\n' 'PASS: dedicated Compose uses explicit candidate project name and protected env file'
expect_rejected "caller --project-name override" ccpc_compose --project-name unexpected config --quiet
expect_rejected "caller --project-name= override" ccpc_compose config --project-name=unexpected
expect_rejected "caller -p override" ccpc_compose -p unexpected config --quiet
expect_rejected "caller -punexpected override" ccpc_compose up -punexpected
printf '%s\n' 'PASS: dedicated Compose blocks project override flags'
DOCKER_HOST=tcp://192.0.2.1:2375 expect_rejected "remote DOCKER_HOST override" ccpc_compose config --quiet
DOCKER_CONTEXT=remote expect_rejected "remote DOCKER_CONTEXT override" ccpc_compose config --quiet
TEST_DOCKER_CONTEXT=remote expect_rejected "selected nondefault Docker context" ccpc_compose config --quiet
TEST_DOCKER_ENDPOINT=ssh://lab@example.invalid expect_rejected "nonlocal default Docker endpoint" ccpc_compose config --quiet
TEST_DOCKER_ENDPOINT=tcp://127.0.0.1:2375 expect_rejected "TCP default Docker endpoint" ccpc_compose config --quiet
COMPOSE_PROJECT_NAME=unreviewed expect_rejected "ambient Compose project" ccpc_compose config --quiet
COMPOSE_FILE=unexpected.yaml expect_rejected "ambient Compose file" ccpc_compose config --quiet
COMPOSE_PROFILES=unexpected expect_rejected "ambient Compose profiles" ccpc_compose config --quiet
printf '%s\n' 'PASS: dedicated Compose rejects inherited project, file and profile selectors'
printf '%s\n' 'PASS: dedicated Compose rejects remote or unreviewed Docker targets'

# These paths use raw Docker CLI calls, not ccpc_compose. They must fail
# before any image inspection or build when the target is untrusted.
DOCKER_HOST=tcp://192.0.2.1:2375 expect_rejected "remote image inspection" verify_image review-only-tag
DOCKER_CONTEXT=remote expect_rejected "remote image context" verify_image review-only-tag
TEST_DOCKER_ENDPOINT=ssh://lab@example.invalid expect_rejected "nonlocal image endpoint" verify_image review-only-tag
DOCKER_HOST=tcp://192.0.2.1:2375 expect_rejected "remote image build" build_image
DOCKER_CONTEXT=remote expect_rejected "remote build context" build_image
TEST_DOCKER_ENDPOINT=tcp://127.0.0.1:2375 expect_rejected "nonlocal build endpoint" build_image
printf '%s\n' 'PASS: dedicated image inspect/build reject unreviewed Docker targets'

expect_rejected "dedicated .env backup" backup_env
expect_rejected "dedicated .env editing" update_env another-tag
unset BACKUP_FILE || true
restore_env >/dev/null
printf '%s\n' 'PASS: dedicated recovery never copies a checkout .env'

# Exercise the actual deploy_release orchestration with all side effects mocked.
backup_env() { return 87; }
update_env() { return 88; }
deploy_containers() { ccpc_compose config --quiet; }
wait_for_services() { :; }
verify_containers() { :; }
run_migrations() { :; }
health_check() { :; }
unset CUSTOM_TAG CUSTOM_IMAGE
deploy_release review-only-tag
[[ "$CUSTOM_TAG" == "review-only-tag" && "$CUSTOM_IMAGE" == "$IMAGE_NAME" ]]
[[ "$(declare -p CUSTOM_TAG)" == *" -x "* ]]
[[ "$(declare -p CUSTOM_IMAGE)" == *" -x "* ]]
printf '%s\n' 'PASS: dedicated release skips .env backup/edit and exports explicit tag'

# The old profile must retain the original docker compose argument order.
CCPC_DEPLOYMENT_PROFILE=legacy-lan
docker() {
  [[ "$1" == compose && "$2" == -f && "$3" == compose.yaml ]] || return 89
}
ccpc_compose config --quiet
printf '%s\n' 'PASS: legacy-lan Compose invocation unchanged'

printf '%s\n' 'PASS: dedicated external environment regressions'
