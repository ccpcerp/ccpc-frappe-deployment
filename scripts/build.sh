#!/bin/bash

set -euo pipefail

source scripts/config.sh
source scripts/lib.sh
source scripts/modules/version.sh
source scripts/modules/docker.sh
source scripts/modules/git.sh

###########################################
# Main
###########################################
main() {

  banner "CCPC ERP Release Builder"

  verify_project_directory
  print_configuration

  verify_git_repository
  verify_git_status

  detect_version
  calculate_next_version
  verify_next_version

  build_image
  verify_image "$NEXT_TAG"
}

main "$@"
