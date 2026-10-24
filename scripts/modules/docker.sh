# shellcheck shell=bash

###########################################
# Docker Module
###########################################

###########################################
# Run Docker Compose
###########################################
# Dedicated-host secrets are never stored in this repository's .env file.
# This guard is opt-in and leaves the legacy-lan path unchanged.
verify_dedicated_env_file() {
  local secret_path="${CCPC_DEDICATED_ENV_FILE:-}"
  local repo_root resolved_path parent_dir uid

  [[ "$secret_path" == /* ]] ||
    error "Dedicated profile requires an absolute CCPC_DEDICATED_ENV_FILE path"

  [[ ! -L "$secret_path" && -f "$secret_path" && -r "$secret_path" ]] ||
    error "Dedicated environment file must be a readable regular file (not a symlink)"

  [[ ! ${DB_PASSWORD+x} ]] ||
    error "Unset DB_PASSWORD in the shell; dedicated credentials must come from the protected file"

  repo_root=$(git rev-parse --show-toplevel 2>/dev/null) ||
    error "Cannot identify the deployment Git checkout"
  repo_root=$(realpath -e -- "$repo_root") ||
    error "Cannot resolve the deployment Git checkout"
  resolved_path=$(realpath -e -- "$secret_path") ||
    error "Cannot resolve the dedicated environment file"

  case "$resolved_path" in
    "$repo_root"|"$repo_root"/*)
      error "Dedicated environment file must be outside the Git checkout"
      ;;
  esac

  [[ ! -e "$repo_root/.env" && ! -L "$repo_root/.env" ]] ||
    error "Dedicated profile forbids a checkout .env file"

  uid=$(id -u)
  parent_dir=$(dirname -- "$resolved_path")

  [[ "$(stat -c %u -- "$resolved_path")" == "$uid" &&
     "$(stat -c %a -- "$resolved_path")" == "600" ]] ||
    error "Dedicated environment file must be owned by this user and mode 0600"

  [[ "$(stat -c %u -- "$parent_dir")" == "$uid" &&
     "$(stat -c %a -- "$parent_dir")" == "700" ]] ||
    error "Dedicated environment directory must be owned by this user and mode 0700"

  # This protected file has one purpose: supply the DB password. Compose
  # accepts COMPOSE_* controls from --env-file, so other keys are forbidden.
  # Do not source, eval, echo, or log any secret values.
  local file_size nonnul_bytes line password_count=0
  file_size=$(stat -c %s -- "$resolved_path") ||
    error "Cannot size dedicated environment file"
  [[ "$file_size" =~ ^[0-9]+$ && "$file_size" -gt 0 && "$file_size" -le 4096 ]] ||
    error "Dedicated environment file has invalid size"

  nonnul_bytes=$(LC_ALL=C tr -d '\000' < "$resolved_path" | wc -c) ||
    error "Cannot validate dedicated environment encoding"
  [[ "$nonnul_bytes" -eq "$file_size" ]] ||
    error "Dedicated environment file must not contain NUL bytes"

  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ "$line" != *$'\r'* ]] ||
      error "Dedicated environment file must use Unix line endings"
    case "$line" in
      ''|\#*) ;;
      DB_PASSWORD=*)
        password_count=$((password_count + 1))
        [[ "$password_count" -eq 1 && -n "${line#DB_PASSWORD=}" &&
           "${line#DB_PASSWORD=}" != '""' && "${line#DB_PASSWORD=}" != "''" ]] ||
          error "Dedicated environment file requires one nonempty DB_PASSWORD assignment"
        ;;
      *)
        error "Dedicated environment file contains an unapproved key or format"
        ;;
    esac
  done < "$resolved_path"
  [[ "$password_count" -eq 1 ]] ||
    error "Dedicated environment file requires exactly one DB_PASSWORD assignment"

  CCPC_VERIFIED_ENV_FILE="$resolved_path"
}

# The dedicated deployment must not silently target a remote Docker Engine.
# A context name alone is insufficient: require the built-in default context to
# resolve to the expected LOCAL Unix socket. No container is started by this check.
verify_dedicated_local_docker_target() {
  local selected_context endpoint

  [[ ! ${DOCKER_HOST+x} && ! ${DOCKER_CONTEXT+x} ]] ||
    error "Dedicated profile forbids DOCKER_HOST/DOCKER_CONTEXT overrides"

  selected_context=$(docker context show 2>/dev/null) ||
    error "Cannot determine Docker context"
  [[ "$selected_context" == "default" ]] ||
    error "Dedicated profile requires Docker default context"

  endpoint=$(docker context inspect default --format '{{.Endpoints.docker.Host}}' 2>/dev/null) ||
    error "Cannot verify Docker default endpoint"
  [[ "$endpoint" == "unix:///var/run/docker.sock" ]] ||
    error "Dedicated profile requires local Docker Unix socket"
}

ccpc_compose() {
  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    verify_dedicated_env_file
    [[ -n "${CUSTOM_TAG:-}" ]] ||
      error "Dedicated profile requires an explicit CUSTOM_TAG (no default image)"
    [[ -n "${IMAGE_NAME:-}" && "${CUSTOM_IMAGE:-}" == "$IMAGE_NAME" ]] ||
      error "Dedicated profile requires an explicit CUSTOM_IMAGE matching IMAGE_NAME"

    # Prevent inherited Compose variables from redirecting the project, file
    # model, or service selection behind this dedicated-only wrapper.
    [[ ! ${COMPOSE_PROJECT_NAME+x} && ! ${COMPOSE_FILE+x} &&
       ! ${COMPOSE_PROFILES+x} ]] ||
      error "Dedicated profile forbids ambient Compose project/file/profile overrides"

    verify_dedicated_local_docker_target
    # REVIEW CANDIDATE ONLY: this proposed project must be compared with the
    # dedicated host's actual existing Compose/volume inventory BEFORE rollout.
    # The hardcoded project prevents caller-selected project names in this path.
    local reviewed_project="ccpc_prod_erpnext"
    local argument
    for argument in "$@"; do
      case "$argument" in
        -p*|--project-name|--project-name=*)
          error "Dedicated Compose forbids caller project-name overrides"
          ;;
      esac
    done
    docker compose --project-name "$reviewed_project" --env-file "$CCPC_VERIFIED_ENV_FILE" "${COMPOSE_FILE_ARGS[@]}" "$@"
  else
    docker compose "${COMPOSE_FILE_ARGS[@]}" "$@"
  fi
}

###########################################
# Build Image
###########################################
build_image() {

  header "Build Image"

  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    verify_dedicated_local_docker_target
  fi

  CACHE_BUST=$(date +%s)

  local BUILD_SSH_KEY="${CCPC_BUILD_SSH_KEY:-$HOME/.ssh/id_ed25519_ccpc_backup}"
  local BUILD_KNOWN_HOSTS="${CCPC_BUILD_KNOWN_HOSTS:-$HOME/.ssh/known_hosts}"

  if [ ! -r "$BUILD_SSH_KEY" ]; then
    error "CCPC build SSH key is not readable: $BUILD_SSH_KEY"
  fi

  if [ ! -r "$BUILD_KNOWN_HOSTS" ]; then
    error "SSH known_hosts file is not readable: $BUILD_KNOWN_HOSTS"
  fi

  if ! ssh-keygen -F github.com -f "$BUILD_KNOWN_HOSTS" >/dev/null; then
    error "github.com is not present in $BUILD_KNOWN_HOSTS"
  fi

  info "Building image: $IMAGE_NAME:$NEXT_TAG"

  docker buildx build \
    --load \
    --build-arg CACHE_BUST="$CACHE_BUST" \
    --build-arg FRAPPE_BRANCH="$FRAPPE_REF" \
    --build-arg EXPECTED_FRAPPE_SHA="$FRAPPE_SHA" \
    --build-arg EXPECTED_ERPNEXT_SHA="$ERPNEXT_SHA" \
    --build-arg EXPECTED_ERPNEXT_PATCH_SHA="$ERPNEXT_PATCH_SHA" \
    --build-arg EXPECTED_ERPNEXT_OVERLAY_STATE_SHA="$ERPNEXT_OVERLAY_STATE_SHA" \
    --build-arg EXPECTED_CCPC_SHA="$CCPC_SHA" \
    --ssh "default=$BUILD_SSH_KEY" \
    --secret "id=github_known_hosts,src=$BUILD_KNOWN_HOSTS" \
    --secret id=apps_json,src=apps.json \
    --tag "$IMAGE_NAME:$NEXT_TAG" \
    --file "$DOCKERFILE" .

  success "Image built successfully"
}

###########################################
# Verify Image
###########################################
verify_image() {

  local IMAGE_TAG="$1"

  header "Verify Image"

  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    verify_dedicated_local_docker_target
  fi

  if ! docker image inspect "$IMAGE_NAME:$IMAGE_TAG" >/dev/null 2>&1; then
    error "Image verification failed: $IMAGE_NAME:$IMAGE_TAG"
  fi

  IMAGE_ID=$(docker image inspect \
    --format '{{.Id}}' \
    "$IMAGE_NAME:$IMAGE_TAG")

  IMAGE_SIZE=$(docker image inspect \
    --format '{{.Size}}' \
    "$IMAGE_NAME:$IMAGE_TAG")

  success "Image verified"

  echo "Image ID : $IMAGE_ID"
  echo "Size     : $IMAGE_SIZE bytes"
}

###########################################
# Deploy Containers
###########################################
deploy_containers() {

  header "Deploy Containers"

  if ! ccpc_compose up -d; then
    restore_env
    error "Container deployment failed"
  fi

  success "Containers deployed"
}

###########################################
# Wait for Services
###########################################
wait_for_services() {

  header "Wait for Services"

  echo "Waiting ${SERVICE_STARTUP_WAIT} seconds..."

  sleep "$SERVICE_STARTUP_WAIT"

  success "Services are ready for verification"
}

###########################################
# Verify Containers
###########################################
verify_containers() {

  header "Verify Containers"

  if ! ccpc_compose ps --status running >/dev/null; then
    restore_env
    error "Unable to verify running containers"
  fi

  ccpc_compose ps

  success "Containers are running"
}
