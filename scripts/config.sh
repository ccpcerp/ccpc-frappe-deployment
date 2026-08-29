#!/bin/bash
# shellcheck disable=SC2034  # Configuration variables are consumed by sourcing scripts.

###########################################
# Framework
###########################################

FRAMEWORK_NAME="CCPC ERP Deployment Framework"
FRAMEWORK_VERSION="1.0.0"

###########################################
# CCPC ERP Release Configuration
###########################################

# Git
APP_BRANCH="version-16"
RELEASE_PREFIX="v16"
APP_PATH="development/frappe-bench/apps/ccpcerp"

# Docker
IMAGE_NAME="ccpcerp"
DOCKERFILE="images/custom/Containerfile"
COMPOSE_FILE_ARGS=(
  -f compose.yaml
  -f overrides/compose.lan-production.yaml
)

# ERPNext
SITE_NAME="ccpcerp.local"
export FRAPPE_SITE_NAME_HEADER="${FRAPPE_SITE_NAME_HEADER:-$SITE_NAME}"
ERP_ACCESS_URL="http://ccpcerp.com"
export HTTP_PUBLISH_PORT="${HTTP_PUBLISH_PORT:-80}"
HEALTHCHECK_URL="http://127.0.0.1:$HTTP_PUBLISH_PORT"

# Build logs
LOG_DIR="logs"

# Directories
LOG_DIR="logs"
BACKUP_DIR="backups"

# Timing
SERVICE_STARTUP_WAIT=10
