#!/bin/bash

###########################################
# Common functions for release scripts
###########################################

line() {
    echo "----------------------------------------"
}

header() {
    echo
    line
    echo "$1"
    line
}

info() {
    echo "[INFO] $1"
}

success() {
    echo "[ OK ] $1"
}

warn() {
    echo "[WARN] $1"
}

error() {
    echo "[FAIL] $1"
    exit 1
}

###########################################
# Banner
###########################################
banner() {

    echo "========================================"
    echo " $1"
    echo "========================================"
    echo
}

###########################################
# Verify Project Directory
###########################################
verify_project_directory() {

    if [ ! -f "compose.yaml" ]; then
        error "Run this script from the frappe_docker directory."
    fi

    success "Project directory verified"
}

###########################################
# Print Configuration
###########################################
print_configuration() {

    header "Configuration"

    echo "Branch     : $APP_BRANCH"
    echo "App Path   : $APP_PATH"
    echo "Image      : $IMAGE_NAME"
    echo "Dockerfile : $DOCKERFILE"
    echo "Site       : $SITE_NAME"
}

###########################################
# Verify Git Repository
###########################################
verify_git_repository() {

    header "Git Verification"

    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        error "This is not a Git repository."
    fi

    success "Git repository detected"

    if [ ! -d "$APP_PATH/.git" ]; then
        error "Cannot find Git repository at $APP_PATH"
    fi

    success "Development app found"
}
