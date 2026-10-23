# shellcheck shell=bash

###########################################
# Environment Module
###########################################
###########################################
# Backup Environment File
###########################################
backup_env() {

  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    error "Dedicated profile prohibits .env backup copies"
  fi

  header "Backup Configuration"

  mkdir -p "$BACKUP_DIR"

  BACKUP_FILE="$BACKUP_DIR/env.$(date +%Y%m%d_%H%M%S).bak"

  cp .env "$BACKUP_FILE"

  success "Configuration backed up"

  echo "Backup : $BACKUP_FILE"
}

###########################################
# Update Environment Configuration
###########################################
update_env() {

  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    error "Dedicated profile prohibits editing checkout .env"
  fi

  local IMAGE_TAG="$1"

  header "Update Configuration"

  if [ ! -f ".env" ]; then
    error ".env file not found"
  fi

  CURRENT_TAG=$(grep '^CUSTOM_TAG=' .env | cut -d= -f2)

  if [ -z "$CURRENT_TAG" ]; then
    error "CUSTOM_TAG not found in .env"
  fi

  echo "Current tag : $CURRENT_TAG"

  sed -i "s/^CUSTOM_TAG=.*/CUSTOM_TAG=$IMAGE_TAG/" .env

  UPDATED_TAG=$(grep '^CUSTOM_TAG=' .env | cut -d= -f2)

  if [ "$UPDATED_TAG" != "$IMAGE_TAG" ]; then
    error "Failed to update CUSTOM_TAG"
  fi

  success "Configuration updated"

  echo "New tag     : $UPDATED_TAG"
}

###########################################
# Restore Configuration
###########################################
restore_env() {

  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    warn "Dedicated profile: no .env backup to restore; review container and database state before recovery"
    return 0
  fi

  if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
  fi

  if cp "$BACKUP_FILE" .env; then
    warn "Configuration restored from backup"
  else
    error "Failed to restore configuration from backup"
  fi
}
