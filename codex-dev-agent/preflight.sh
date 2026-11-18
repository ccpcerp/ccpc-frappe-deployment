#!/usr/bin/env bash
# Safe one-time synthetic DEV-only agent source check; NO Docker up.
# Creates only two random passwords in ignored local-secrets/.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
echo "[1/3] Docker-free policy unit tests"
python3 -m unittest discover -s tests -p 'test_*.py'
echo "[2/3] Local synthetic-only passwords (never print contents)"
python3 init_local_secrets.py
echo "[3/3] Rendered Compose static policy gate (does not start containers)"
python3 check_compose.py
echo "PASS: source preflight complete; live container/network still NOT VERIFIED"
