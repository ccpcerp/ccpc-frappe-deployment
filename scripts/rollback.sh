#!/bin/bash

set -euo pipefail

source scripts/config.sh
source scripts/lib.sh

source scripts/modules/env.sh
source scripts/modules/docker.sh
source scripts/modules/health.sh
source scripts/modules/deployment.sh
source scripts/modules/database.sh

###########################################
# Verify Arguments
###########################################
verify_arguments() {

  header "Arguments"

  if [ $# -ne 1 ]; then
    error "Usage: ./scripts/rollback.sh <image-tag>"
  fi

  ROLLBACK_TAG="$1"

  success "Rollback tag : $ROLLBACK_TAG"
}

###########################################
# Rollback Summary
###########################################
rollback_summary() {

  header "Rollback Summary"

  echo "Image : $IMAGE_NAME:$ROLLBACK_TAG"
  echo "Site  : $SITE_NAME"
  echo "URL   : http://localhost:8080"

  success "Rollback completed successfully"
}

main() {

  banner "CCPC ERP Rollback"

  verify_project_directory
  print_configuration

  verify_arguments "$@"
  verify_image "$ROLLBACK_TAG"
  deploy_release "$ROLLBACK_TAG"
  rollback_summary

}

main "$@"
