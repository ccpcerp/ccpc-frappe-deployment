# shellcheck shell=bash

###########################################
# Docker Module
###########################################

###########################################
# Run Docker Compose
###########################################
ccpc_compose() {

  docker compose "${COMPOSE_FILE_ARGS[@]}" "$@"
}

###########################################
# Build Image
###########################################
build_image() {

  header "Build Image"

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
