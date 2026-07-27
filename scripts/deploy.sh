#!/bin/bash

set -euo pipefail

source scripts/config.sh
source scripts/lib.sh
source scripts/modules/env.sh
source scripts/modules/docker.sh
source scripts/modules/database.sh
source scripts/modules/health.sh
source scripts/modules/deployment.sh

###########################################
# Verify Arguments
###########################################
verify_arguments() {

    header "Arguments"

    if [ $# -ne 1 ]; then
        error "Usage: ./scripts/deploy.sh <image-tag>"
    fi

    DEPLOY_TAG="$1"

    success "Deploy tag : $DEPLOY_TAG"
}




###########################################
# Deployment Summary
###########################################
deployment_summary() {

    header "Deployment Summary"

    echo "Image : $IMAGE_NAME:$DEPLOY_TAG"
    echo "Site  : $SITE_NAME"
    echo "URL   : http://localhost:8080"

    success "Deployment completed successfully"
}


###########################################
# Main
###########################################
main() {

    banner "CCPC ERP Deployment"

    verify_project_directory
    print_configuration

    verify_arguments "$@"

    verify_image "$DEPLOY_TAG"

    deploy_release "$DEPLOY_TAG"

    deployment_summary
}

main "$@"
