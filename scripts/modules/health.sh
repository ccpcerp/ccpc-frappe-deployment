# shellcheck shell=bash

###########################################
# Health Module
###########################################

###########################################
# Health Check
###########################################
health_check() {

  header "Health Check"

  if curl -fsS \
    --header "Host: $FRAPPE_SITE_NAME_HEADER" \
    "$HEALTHCHECK_URL" >/dev/null; then
    success "ERPNext is responding"

    echo "URL : $HEALTHCHECK_URL"
    echo "Site: $FRAPPE_SITE_NAME_HEADER"
  else
    error "ERPNext health check failed"
  fi
}
