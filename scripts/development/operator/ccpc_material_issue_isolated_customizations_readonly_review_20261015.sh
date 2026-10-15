#!/usr/bin/env bash
# CCPC REVIEW ONLY: isolated DEVELOPMENT metadata detail, SQL READ ONLY.
# Prepared in GitHub; never stage or run without separate owner approval.
set -euo pipefail
umask 077

if [[ "$(printenv CCPC_METADATA_DETAILS_APPROVED 2>/dev/null || true)" != "ccpc-isolated-metadata-details-once" ]]; then
  echo 'NOT AUTHORIZED: detailed metadata audit needs separate owner consent' >&2
  exit 1
fi
if [[ "$(id -u)" -eq 0 ]]; then echo 'STOP: non-root operator required' >&2; exit 1; fi
if ! command -v docker >/dev/null 2>&1; then echo 'STOP: Docker CLI unavailable' >&2; exit 1; fi
DEV='frappe_docker_devcontainer-frappe-1'
LABELS="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}|{{index .Config.Labels "com.docker.compose.service"}}|{{.State.Running}}' "$DEV" 2>/dev/null)" || {
  echo 'STOP: expected DEVELOPMENT container unavailable' >&2
  exit 1
}
if [[ "$LABELS" != 'frappe_docker_devcontainer|frappe|true' ]]; then
  echo 'STOP: unexpected DEVELOPMENT Compose container identity' >&2
  exit 1
fi

docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench && umask 077 && PYTHONDONTWRITEBYTECODE=1 ./env/bin/python -' <<'PYTHON'
import json
import re
from pathlib import Path
import MySQLdb

SITES = Path.cwd() / 'sites'
TEST_SITE = 'ccpc-integration2.localhost'
SHARED_SITE = 'development.localhost'
DOCTYPE_SCOPE = (
    'Stock Entry', 'Stock Entry Detail', 'Withdrawal Slip', 'Withdrawal Slip Item',
)
MAX_RECORDS = 80
conn = cur = None
stage = 'verify isolated site configuration'


def stop(reason):
    raise RuntimeError(reason)


def site_config(name):
    path = SITES / name / 'site_config.json'
    if not path.is_file() or path.is_symlink():
        stop('Unsafe or missing site configuration')
    result = json.loads(path.read_text())
    if not isinstance(result, dict) or not isinstance(result.get('db_name'), str):
        stop('Invalid site configuration identity')
    return result


def fetch(sql, args=()):
    if not re.match(r'^SELECT\b', sql.strip(), re.IGNORECASE):
        stop('Not a SELECT statement')
    if any(token in sql for token in (';', '--', '/*', '#')):
        stop('Unsafe SQL query syntax')
    cur.execute(sql, args)
    data = cur.fetchall()
    if len(data) > MAX_RECORDS:
        stop('Too many matching metadata records')
    return data


def safe_identifier(value, allow_space=False):
    if not isinstance(value, str):
        stop('Invalid metadata identifier type')
    pattern = r'[A-Za-z][A-Za-z0-9_ -]{0,79}' if allow_space else r'[A-Za-z][A-Za-z0-9_]{0,79}'
    if not re.fullmatch(pattern, value):
        stop('Unexpected metadata identifier syntax')
    return value


def safe_pattern(value):
    # Only expose recognizable naming patterns, never arbitrary property values.
    if not isinstance(value, str):
        return 'UNAVAILABLE'
    entries = [part.strip() for part in value.splitlines() if part.strip()]
    if not entries:
        return 'EMPTY'
    if len(entries) > 12:
        return 'TOO_MANY_OPTIONS'
    if not all(len(p) <= 110 and re.fullmatch(r'[A-Za-z0-9._#:/-]+', p) for p in entries):
        return 'NONSTANDARD_PATTERN_REDACTED'
    return ','.join(entries)


def flag_state(value):
    # Frappe config merges common first and site-specific second.
    if value in (None, False, 0, '', '0', 'false', 'False'):
        return 'NOT_DISABLED_BY_CONFIG'
    if value in (True, 1, '1', 'true', 'True'):
        return 'DISABLED_BY_CONFIG'
    return 'UNKNOWN_CONFIG_FORMAT'


try:
    isolated = site_config(TEST_SITE)
    shared = site_config(SHARED_SITE)
    common_path = SITES / 'common_site_config.json'
    if not common_path.is_file() or common_path.is_symlink():
        stop('Unsafe common site configuration')
    common = json.loads(common_path.read_text())
    if not isinstance(common, dict) or isolated['db_name'] == shared['db_name']:
        stop('Invalid or overlapping DEVELOPMENT database configuration')
    host = isolated.get('db_host') or common.get('db_host')
    try:
        port = int(isolated.get('db_port') or common.get('db_port') or 3306)
    except (TypeError, ValueError):
        stop('Invalid DEV database port')
    if host != 'mariadb' or port != 3306:
        stop('Unexpected DEVELOPMENT MariaDB endpoint')
    if any(h not in (None, '', 'mariadb') for h in
           (isolated.get('db_host'), common.get('db_host'))):
        stop('Conflicting database host override')
    if not isolated.get('db_password'):
        stop('Missing isolated database password')
    merged = {**common, **isolated}
    print('ISOLATED DEV DB CONFIG AND ENDPOINT: VERIFIED', flush=True)
    print('GLOBAL SEARCH FILE-CONFIG STATUS:',
          flag_state(merged.get('disable_global_search')), flush=True)
    print('NOTE: FILE CONFIG DOES NOT VERIFY LIVE REDIS OR RUNTIME HOOKS', flush=True)

    stage = 'connect to identified isolated database, read-only'
    conn = MySQLdb.connect(
        host='mariadb', port=3306,
        user=isolated.get('db_user') or isolated['db_name'],
        passwd=isolated['db_password'], db=isolated['db_name'],
        charset='utf8mb4', connect_timeout=5)
    cur = conn.cursor()
    cur.execute('START TRANSACTION READ ONLY')
    if fetch('SELECT DATABASE()') != ((isolated['db_name'],),):
        stop('Wrong SQL database selected')
    print('ACTUAL ISOLATED SQL DATABASE: VERIFIED', flush=True)

    stage = 'read Property Setter and Custom Field names only'
    property_rows = fetch(
        'SELECT doc_type, field_name, property, property_type FROM `tabProperty Setter` '
        'WHERE doc_type IN (%s,%s,%s,%s) ORDER BY doc_type, field_name, property',
        DOCTYPE_SCOPE)
    custom_rows = fetch(
        'SELECT dt, fieldname, fieldtype FROM `tabCustom Field` '
        'WHERE dt IN (%s,%s,%s,%s) ORDER BY dt, fieldname',
        DOCTYPE_SCOPE)
    print('PROPERTY SETTER NAME RECORDS:', len(property_rows), flush=True)
    for dtype, field_name, property_name, property_type in property_rows:
        if dtype not in DOCTYPE_SCOPE:
            stop('Unexpected Property Setter DocType')
        field = safe_identifier(field_name) if field_name else '(DOCTYPE)'
        prop = safe_identifier(property_name)
        ptype = safe_identifier(property_type, allow_space=True) if property_type else 'UNSPECIFIED'
        print('PROPERTY:', dtype, field, prop, ptype, flush=True)
    print('CUSTOM FIELD NAME RECORDS:', len(custom_rows), flush=True)
    for dtype, field_name, field_type in custom_rows:
        if dtype not in DOCTYPE_SCOPE:
            stop('Unexpected Custom Field DocType')
        print('CUSTOM FIELD:', dtype, safe_identifier(field_name),
              safe_identifier(field_type, allow_space=True), flush=True)

    stage = 'read base naming and targeted override patterns'
    dt = fetch('SELECT autoname FROM `tabDocType` WHERE name=%s',
               ('Stock Entry',))
    naming = fetch(
        'SELECT options, `default` FROM `tabDocField` '
        'WHERE parent=%s AND fieldname=%s',
        ('Stock Entry', 'naming_series'))
    if len(dt) != 1 or len(naming) != 1:
        stop('Required Stock Entry naming metadata not found')
    print('STOCK ENTRY BASE AUTONAME:', safe_pattern(dt[0][0]), flush=True)
    print('STOCK ENTRY BASE SERIES OPTIONS:', safe_pattern(naming[0][0]), flush=True)
    print('STOCK ENTRY BASE SERIES DEFAULT:', safe_pattern(naming[0][1]), flush=True)
    # The values of only exact naming overrides are inspected; no other
    # Property Setter values or business records are printed.
    overrides = fetch(
        'SELECT field_name, property, value FROM `tabProperty Setter` '
        'WHERE doc_type=%s AND (((field_name IS NULL OR field_name=%s) AND property=%s) '
        'OR (field_name=%s AND property IN (%s,%s))) '
        'ORDER BY field_name, property',
        ('Stock Entry', '', 'autoname', 'naming_series', 'options', 'default'))
    print('STOCK ENTRY NAMING OVERRIDES:', len(overrides), flush=True)
    for field_name, prop, value in overrides:
        prop = safe_identifier(prop)
        if prop not in ('autoname', 'options', 'default'):
            stop('Unexpected naming override property')
        kind = 'DOCTYPE' if not field_name else safe_identifier(field_name)
        print('STOCK ENTRY NAMING OVERRIDE:', kind, prop,
              safe_pattern(value), flush=True)

    stage = 'read restricted series existence and search field names'
    has_series = fetch(
        'SELECT COUNT(*) FROM `tabSeries` WHERE name LIKE %s',
        ('MAT-STE-%',))
    if len(has_series) != 1:
        stop('Naming counter query failed')
    print('MAT-STE PREFIX COUNTER RECORDS:',
          'PRESENT' if has_series[0][0] else 'ABSENT', flush=True)
    base_search = fetch(
        'SELECT fieldname FROM `tabDocField` '
        'WHERE parent=%s AND in_global_search=1 ORDER BY fieldname',
        ('Stock Entry Detail',))
    extra_search = fetch(
        'SELECT fieldname FROM `tabCustom Field` '
        'WHERE dt=%s AND in_global_search=1 ORDER BY fieldname',
        ('Stock Entry Detail',))
    print('STOCK ENTRY DETAIL BASE SEARCH FIELDS:',
          ','.join(safe_identifier(r[0]) for r in base_search) or '(NONE)', flush=True)
    print('STOCK ENTRY DETAIL CUSTOM SEARCH FIELDS:',
          ','.join(safe_identifier(r[0]) for r in extra_search) or '(NONE)', flush=True)

    stage = 'close SELECT-only transaction'
    cur.close()
    cur = None
    conn.rollback()
    conn.close()
    conn = None
    print('NO SQL WRITES, FRAPPE INIT, REDIS, STOCK/GL OR PRODUCTION ACCESS', flush=True)
    print('ISOLATED CUSTOMIZATION DETAILS READ-ONLY AUDIT: PASSED', flush=True)
except Exception:
    # Do not print raw errors, SQL data, credentials or configuration values.
    print('ISOLATED CUSTOMIZATION DETAILS READ-ONLY AUDIT: STOPPED', flush=True)
    print('CHECK STAGE:', stage, flush=True)
    print('DO NOT RETRY; REVIEW WITHOUT MODIFYING SITE SETTINGS', flush=True)
    raise SystemExit(1)
finally:
    if cur is not None:
        try:
            cur.close()
        except Exception:
            pass
    if conn is not None:
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
PYTHON
