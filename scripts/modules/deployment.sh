#!/bin/bash

###########################################
# Deployment Module
###########################################

###########################################
# Deploy Release
###########################################
deploy_release() {

    local IMAGE_TAG="$1"

    backup_env

    update_env "$IMAGE_TAG"

    deploy_containers

    wait_for_services

    verify_containers

    run_migrations

    health_check

}
