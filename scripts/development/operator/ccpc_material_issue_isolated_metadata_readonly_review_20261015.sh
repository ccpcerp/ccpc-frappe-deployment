#!/usr/bin/env bash
# CCPC REVIEW ONLY: isolated DEVELOPMENT read-only SQL metadata probe.
# Separate specific owner authorization required before any execution.
set -euo pipefail
umask 077
if [[ "$(printenv CCPC_METADATA_READONLY_APPROVED 2>/dev/null || true)" != "ccpc-isolated-readonly-metadata-once" ]]; then
  echo 'NOT AUTHORIZED: read-only metadata probe not approved' >&2
  exit 1
fi
if [[ "$(id -u)" -eq 0 ]]; then echo 'STOP: non-root operator required' >&2; exit 1; fi
if ! command -v docker >/dev/null 2>&1; then echo 'STOP: Docker unavailable' >&2; exit 1; fi
DEV='frappe_docker_devcontainer-frappe-1'
META="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Running}}' "$DEV" 2>/dev/null)" || {
  echo 'STOP: DEV container unavailable' >&2; exit 1;
}
if [[ "$META" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  echo 'STOP: unexpected DEV container identity' >&2; exit 1
fi
docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench && umask 077 && PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -' <<'PYTHON'
import json
import re
from pathlib import Path
import MySQLdb

SITES = Path.cwd() / 'sites'
STAGE = 'read isolated site configs'
conn = cur = None

def stop(reason):
    raise RuntimeError(reason)

def cfg(site):
    path = SITES / site / 'site_config.json'
    if not path.is_file() or path.is_symlink():
        stop('Unsafe site config path')
    obj = json.loads(path.read_text())
    if not isinstance(obj, dict) or not isinstance(obj.get('db_name'), str):
        stop('Invalid database identity')
    return obj

def query(sql, params=()):
    if not re.match(r'^SELECT\b', sql.strip(), re.IGNORECASE):
        stop('Only SELECT queries allowed')
    if any(x in sql for x in (';', '--', '/*', '#')):
        stop('Unapproved SQL syntax')
    cur.execute(sql, params)
    return cur.fetchall()

try:
    isolated = cfg('ccpc-integration2.localhost')
    shared = cfg('development.localhost')
    common_file = SITES / 'common_site_config.json'
    if not common_file.is_file() or common_file.is_symlink():
        stop('Unsafe common site config')
    common = json.loads(common_file.read_text())
    if not isinstance(common, dict) or isolated['db_name'] == shared['db_name']:
        stop('Invalid or overlapping DEV DB config')
    host = isolated.get('db_host') or common.get('db_host')
    try:
        port = int(isolated.get('db_port') or common.get('db_port') or 3306)
    except (TypeError, ValueError):
        stop('Invalid DEV database port')
    if host != 'mariadb' or port != 3306:
        stop('DB endpoint not pinned to DEV mariadb:3306')
    if any(h not in (None, '', 'mariadb') for h in
           (isolated.get('db_host'), common.get('db_host'))):
        stop('Conflicting DB host overrides')
    if not isolated.get('db_password'):
        stop('Isolated DB credentials unavailable')
    print('ISOLATED DEV METADATA CONNECTION CONFIG: VERIFIED', flush=True)

    STAGE = 'establish SELECT-only transaction and confirm database identity'
    conn = MySQLdb.connect(
        host='mariadb', port=3306, user=isolated.get('db_user') or isolated['db_name'],
        passwd=isolated['db_password'], db=isolated['db_name'],
        charset='utf8mb4', connect_timeout=5)
    cur = conn.cursor()
    cur.execute('START TRANSACTION READ ONLY')
    identity = query('SELECT DATABASE()')
    if len(identity) != 1 or identity[0][0] != isolated['db_name']:
        stop('Connected to unexpected SQL database')
    print('ACTUAL ISOLATED DEV DATABASE: VERIFIED', flush=True)

    STAGE = 'read DocType/naming/child search metadata without printing values'
    doctypes = ('Stock Entry', 'Stock Entry Detail', 'Withdrawal Slip',
                'Withdrawal Slip Item', 'Stock Ledger Entry', 'GL Entry')
    meta = query('SELECT name, autoname, track_changes FROM `tabDocType` '
                 'WHERE name IN (%s,%s,%s,%s,%s,%s)', doctypes)
    if {x[0] for x in meta} != set(doctypes) or len(meta) != 6:
        stop('Six expected doctypes not present')
    naming = query('SELECT fieldname, fieldtype, options FROM `tabDocField` '
                   'WHERE parent=%s AND fieldname=%s', ('Stock Entry','naming_series'))
    if len(naming) != 1:
        stop('Stock Entry naming field unavailable')
    searchable = query('SELECT COUNT(*) FROM `tabDocField` '
                       'WHERE parent=%s AND in_global_search=1',
                       ('Stock Entry Detail',))
    if len(searchable) != 1:
        stop('Stock Entry Detail search metadata unavailable')
    print('DOCTYPE NAMING AND CHILD GLOBAL SEARCH METADATA: READ', flush=True)
    print('STOCK ENTRY DETAIL SEARCH FIELDS:',
          'PRESENT' if searchable[0][0] else 'NOT CONFIGURED IN BASE DOCFIELDS',
          flush=True)

    STAGE = 'read customization and naming counter counts only'
    property_setters = query('SELECT COUNT(*) FROM `tabProperty Setter` '
                             'WHERE doc_type IN (%s,%s,%s,%s)', doctypes[:4])
    custom_fields = query('SELECT COUNT(*) FROM `tabCustom Field` '
                          'WHERE dt IN (%s,%s,%s,%s)', doctypes[:4])
    series_count = query('SELECT COUNT(*) FROM `tabSeries` WHERE name LIKE %s',
                         ('MAT-STE-%',))
    if not property_setters or not custom_fields or not series_count:
        stop('Customizations/series counts unavailable')
    if property_setters[0][0] or custom_fields[0][0]:
        print('RELEVANT SITE CUSTOMIZATIONS: PRESENT - REQUIRE REVIEW', flush=True)
    else:
        print('RELEVANT SITE CUSTOMIZATIONS: NONE FOUND IN CHECKED DOCTYPES', flush=True)
    print('STOCK ENTRY NAMING SERIES COUNTER: COUNTED (VALUE NOT PRINTED)', flush=True)

    STAGE = 'end read-only SQL transaction'
    cur.close()
    cur = None
    conn.rollback()
    conn.close()
    conn = None
    print('NO FRAPPE INIT, SQL WRITES, STOCK/GL, BACKUP OR PRODUCTION ACCESS', flush=True)
    print('ISOLATED METADATA READ-ONLY AUDIT: PASSED', flush=True)
except Exception:
    print('ISOLATED METADATA READ-ONLY AUDIT: STOPPED', flush=True)
    print('CHECK STAGE:', STAGE, flush=True)
    print('NO RETRIES OR ENVIRONMENT CHANGES', flush=True)
    raise SystemExit(1)
finally:
    if cur is not None:
        try: cur.close()
        except Exception: pass
    if conn is not None:
        try:
            conn.rollback()
            conn.close()
        except Exception: pass
PYTHON
