#!/bin/bash

###########################################
# Version Module
###########################################

###########################################
# Detect Version
###########################################
detect_version() {

    header "Version"

    CURRENT_TAG=$(docker images "$IMAGE_NAME" \
        --format "{{.Tag}}" \
        | grep "^${RELEASE_PREFIX}\." \
        | sort -V \
        | tail -n1)

    if [ -z "$CURRENT_TAG" ]; then
        error "No release images found for $IMAGE_NAME"
    fi

    success "Current version : $CURRENT_TAG"

}

###########################################
# Calculate Next Version
###########################################
calculate_next_version() {

    header "Next Version"

    VERSION_NUMBER="${CURRENT_TAG#${RELEASE_PREFIX}.}"

    MAJOR="${VERSION_NUMBER%.*}"
    PATCH="${VERSION_NUMBER##*.}"

    MAJOR=$((MAJOR + 1))
    PATCH=0

    NEXT_TAG="${RELEASE_PREFIX}.${MAJOR}.${PATCH}"

    success "Next version : $NEXT_TAG"

}

###########################################
# Verify Next Version
###########################################
verify_next_version() {

    header "Version Verification"

    if docker image inspect "$IMAGE_NAME:$NEXT_TAG" >/dev/null 2>&1; then
        error "Image already exists: $IMAGE_NAME:$NEXT_TAG"
    fi

    success "Version available : $NEXT_TAG"
}
