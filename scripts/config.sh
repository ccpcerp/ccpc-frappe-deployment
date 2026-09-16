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

# Frozen release inputs.
# Upstream version-16 branches may advance independently; production images
# must be built only from these explicitly validated refs and commits.
FRAPPE_REF="v16.33.1"
FRAPPE_SHA="988e54f3c4c291e2077a83809663f123731abe76"

ERPNEXT_REF="v16.34.2"
ERPNEXT_SHA="4048fb70e14d1843956fcdabb7c3cca75a1cbcdd"
ERPNEXT_PATCH_SHA="b543d14453d4370c6ddaf53bee8f8b786bf9199d5ce33182eb80aa5080e85ba1"
ERPNEXT_OVERLAY_STATE_SHA="13bfff41433c9ac380b9ed632911674b9b87f7e7cb728388912ed50c79c63d0e"

CCPC_REF="release-2026-09-16"
CCPC_SHA="cfcc19394a6646548f2b7050db040c8cf5ebafde"

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
