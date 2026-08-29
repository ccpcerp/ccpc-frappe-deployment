# shellcheck shell=bash

###########################################
# Health Module
###########################################

###########################################
# Health Check
###########################################
health_check() {

  header "Health Check"

  URL="http://localhost:8080"

  if curl -fsS "$URL" >/dev/null; then
    success "ERPNext is responding"

    echo "URL : $URL"
  else
    error "ERPNext health check failed"
  fi
}
