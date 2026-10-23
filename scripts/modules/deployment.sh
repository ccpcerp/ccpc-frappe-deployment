# shellcheck shell=bash

###########################################
# Deployment Module
###########################################

###########################################
# Deploy Release
###########################################
deploy_release() {

  local IMAGE_TAG="$1"

  if [[ "${CCPC_DEPLOYMENT_PROFILE:-legacy-lan}" == "dedicated-pre-tls" ]]; then
    # The dedicated host must never back up or rewrite a password-containing .env.
    # CUSTOM_TAG is a command-scoped release input, not a persisted secret or tag file.
    verify_dedicated_env_file
    export CUSTOM_TAG="$IMAGE_TAG"
    info "Dedicated profile: external credentials; no .env copy or update"
  else
    # Preserve the existing legacy LAN deployment behavior, unchanged.
    backup_env
    update_env "$IMAGE_TAG"
  fi

  deploy_containers

  wait_for_services

  verify_containers

  run_migrations

  health_check

}
