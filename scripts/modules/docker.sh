# shellcheck shell=bash

###########################################
# Docker Module
###########################################

###########################################
# Build Image
###########################################
build_image() {

  header "Build Image"

  CACHE_BUST=$(date +%s)

  info "Building image: $IMAGE_NAME:$NEXT_TAG"

  docker buildx build \
    --load \
    --build-arg CACHE_BUST="$CACHE_BUST" \
    --build-arg FRAPPE_BRANCH="$APP_BRANCH" \
    --build-arg ERPNEXT_BRANCH="$APP_BRANCH" \
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

  if ! docker compose up -d; then
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

  if ! docker compose ps --status running >/dev/null; then
    restore_env
    error "Unable to verify running containers"
  fi

  docker compose ps

  success "Containers are running"
}
