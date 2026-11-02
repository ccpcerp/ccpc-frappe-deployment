#!/usr/bin/env bash
# CCPC ERPNext — one-shot, owner-approved MAIN DEVELOPMENT authenticated HTTP check.
# Run manually ONCE only after exact GitHub commit+SHA256 staging verification.
# Creates a short-lived DEVELOPMENT System User, commits it for HTTP login,
# then disables the account and revokes its sessions in finally.
# Power interruption can leave an enabled test account: inspect/disable before retry.
# Does NOT pull or modify the protected DEVELOPMENT app checkout or PRODUCTION.
set -euo pipefail

docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 bash -lc 'cd /workspace/development/frappe-bench/sites && /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_EXEC_HTTP_PY'
import json
import re
import secrets
import subprocess
from pathlib import Path

BENCH = Path('/workspace/development/frappe-bench')
APP = BENCH / 'apps/ccpcerp'
MAIN = 'development.localhost'
OTHER = 'ccpc-integration2.localhost'
EXPECTED_SHA = '532a28d99bd0548241854495156a61f94eb1ac6b'
OLD_USER = 'ccpc-exec-http-once@example.test'
USER = 'ccpc-exec-http-desk-20261102@example.test'
ROLE = 'CCPC Group Executive Reporting'
BASE = 'http://127.0.0.1:8000'
METHOD = '/api/method/ccpcerp.ccpc_erp.executive_reporting.run_group_report'
DATES = {'from_date': '2026-10-01', 'to_date': '2026-10-31'}
COMPANIES = {
    'Cagayan Corn Products Corporation': 'CCPC',
    'Ricor Mills Corporation': 'RMC',
    'GSL Realty Corporation': 'GSL',
    'Woodland Farms Corporation': 'WFC',
}


def must(value, label):
    if not value:
        raise AssertionError(label)


head = subprocess.check_output(
    ['git', '-C', str(APP), 'rev-parse', 'HEAD'], text=True
).strip()
status = subprocess.check_output(
    ['git', '-C', str(APP), 'status', '--porcelain'], text=True
).splitlines()
must(head == EXPECTED_SHA and status == ['?? AGENTS.md'], 'SOURCE / AGENTS GUARD')
config = [
    json.loads((BENCH / 'sites' / site / 'site_config.json').read_text())
    for site in (MAIN, OTHER)
]
must(
    config[0].get('db_name') and config[1].get('db_name')
    and config[0]['db_name'] != config[1]['db_name'],
    'MAIN / INTEGRATION2 DATABASE GUARD',
)

import frappe
import requests
from frappe.utils.password import update_password
from frappe.sessions import clear_sessions
from ccpcerp.ccpc_erp import executive_reporting as gateway

must(gateway.COMPANIES == COMPANIES, 'GATEWAY COMPANY SOURCE GUARD')

client = requests.Session()
client.trust_env = False
client.headers.update({
    'Host': MAIN,
    'X-Frappe-Site-Name': MAIN,
})
ping = client.get(BASE + '/api/method/ping', timeout=9, allow_redirects=False)
must(
    ping.status_code == 200 and ping.json().get('message') == 'pong',
    'WEB PING',
)
frappe.init(site=MAIN, sites_path='.')
frappe.connect()
phase = 'preflight'
reason = None
created = False
checks = []


def call(key, filters, csrf=None):
    headers = {'X-Frappe-CSRF-Token': csrf} if csrf else {}
    return client.post(
        BASE + METHOD,
        data={'report_key': key, 'filters': json.dumps(filters)},
        headers=headers,
        timeout=25,
        allow_redirects=False,
    )


def denied(reply):
    if reply.status_code in (401, 403, 405, 417):
        return True
    if reply.status_code == 200:
        return False
    try:
        data = reply.json()
    except ValueError:
        return False
    return 'PermissionError' in str(data.get('exc_type', ''))


try:
    frappe.set_user('Administrator')
    must(frappe.local.site == MAIN, 'SITE IDENTITY')
    must(not frappe.conf.get('ignore_csrf'), 'CSRF DISABLED IN SITE CONFIG')
    must(
        all(frappe.db.get_value('Company', name, 'abbr') == abbr
            for name, abbr in COMPANIES.items()),
        'FOUR REAL COMPANY IDENTITIES',
    )
    must(
        frappe.db.exists('Role', ROLE)
        and frappe.db.exists('Page', 'ccpc-group-executive-reporting'),
        'ROLE / PAGE INSTALLED',
    )
    old_enabled = frappe.db.get_value('User', OLD_USER, 'enabled')
    must(old_enabled is not None and int(old_enabled) == 0,
         'PREVIOUS TEST ACCOUNT NOT CONFIRMED DISABLED')
    must(not frappe.db.exists('User', USER), 'NEW TEST USER ALREADY EXISTS')
    current = frappe.db.sql('''
        SELECT COUNT(DISTINCT u.name)
        FROM `tabUser` u INNER JOIN `tabHas Role` h
          ON h.parent=u.name AND h.parenttype='User'
        WHERE h.role=%s AND u.enabled=1
          AND u.user_type='System User'
          AND u.name NOT IN ('Guest','Administrator')
    ''', (ROLE,))[0][0]
    must(int(current) == 0, 'EXISTING ACTIVE EXECUTIVE USER: STOP')
    print('PINNED DEVELOPMENT / PREVIOUS DISABLEMENT: PASS', flush=True)
    print('NEW TEMP ACCOUNT RESCUE ID: ' + USER, flush=True)

    phase = 'temporary account provisioning'
    secret = secrets.token_urlsafe(48)
    user = frappe.get_doc({
        'doctype': 'User',
        'email': USER,
        'first_name': 'CCPC One-Time Desk HTTP Check',
        'enabled': 1,
        'user_type': 'System User',
        'send_welcome_email': 0,
    })
    user.flags.no_welcome_mail = True
    user.append('roles', {'role': ROLE})
    user.insert(ignore_permissions=True)
    must(user.name == USER, 'TEMP USER NAME')
    update_password(USER, secret)
    roles = set(frappe.get_roles(USER))
    must(ROLE in roles, 'TEMP ROLE ASSIGNMENT')
    must(not roles.intersection({
        'System Manager', 'Accounts Manager', 'Accounts User',
        'Stock Manager', 'Stock User', 'Finance Controller',
    }), 'TEMP USER HAS FINANCE/ADMIN ROLE')
    frappe.db.commit()
    created = True
    print('TEMP ACCOUNT CREATED FOR ONE TEST', flush=True)

    phase = 'authenticated cookie login'
    login = client.post(
        BASE + '/api/method/login',
        data={'usr': USER, 'pwd': secret},
        timeout=15,
        allow_redirects=False,
    )
    secret = None
    must(login.status_code == 200, 'LOGIN HTTP STATUS')
    must(login.json().get('message') == 'Logged In', 'LOGIN RESPONSE')
    must(bool(client.cookies.get('sid')), 'SESSION COOKIE')
    identity = client.get(
        BASE + '/api/method/frappe.auth.get_logged_user',
        timeout=12, allow_redirects=False,
    )
    must(identity.status_code == 200, 'IDENTITY STATUS')
    must(identity.json().get('message') == USER, 'COOKIE IDENTITY')
    print('REAL COOKIE LOGIN / IDENTITY: PASS', flush=True)

    phase = 'canonical Desk CSRF bootstrap'
    desk = client.get(BASE + '/desk', timeout=20, allow_redirects=False)
    must(desk.status_code == 200, 'DESK HTTP 200')
    must('text/html' in desk.headers.get('Content-Type', ''), 'DESK HTML TYPE')
    must('frappe.boot' in desk.text, 'DESK BOOT MARKER')
    match = re.search(r'''frappe\.csrf_token\s*=\s*["']([^"']+)["']''', desk.text)
    must(match is not None, 'DESK CSRF ASSIGNMENT')
    csrf = match.group(1)
    must(csrf not in ('None', '{{ csrf_token }}'), 'DESK CSRF PLACEHOLDER')
    must(re.fullmatch(r'[A-Za-z0-9]{20,128}', csrf) is not None, 'CSRF TOKEN FORMAT')
    print('CANONICAL /desk CSRF BOOTSTRAP: PASS', flush=True)

    ccpc, rmc = 'Cagayan Corn Products Corporation', 'Ricor Mills Corporation'
    common = {'company': ccpc, **DATES}
    pair = {'issuing_company': ccpc, 'requesting_company': rmc, **DATES}

    phase = 'missing CSRF rejection'
    must(denied(call('department', common)), 'POST WITHOUT CSRF ACCEPTED')
    checks.append('HTTP POST WITHOUT CSRF: DENIED (PASS)')

    phase = 'four CSRF-protected report POSTs'
    for key, filters, expected_cols, expected_rows in (
        ('department', common, 19, 2),
        ('equipment', common, 24, 2),
        ('intercompany', pair, 22, 1),
        ('stock_gl', common, 17, 4),
    ):
        response = call(key, filters, csrf)
        must(response.status_code == 200, key + ' HTTP STATUS')
        value = response.json().get('message')
        must(isinstance(value, dict), key + ' RESPONSE FORMAT')
        cols, rows = value.get('columns'), value.get('rows')
        must(isinstance(cols, list) and len(cols) == expected_cols,
             key + ' COLUMNS')
        must(isinstance(rows, list) and len(rows) == expected_rows,
             key + ' ROWS')
        must(all(r.get('issuing_company', r.get('company')) == ccpc for r in rows),
             key + ' ISSUER SCOPE')
        if key == 'intercompany':
            must(all(r.get('requesting_company') == rmc for r in rows),
                 key + ' REQUESTER SCOPE')
        checks.append(f'HTTP {key}: PASS columns={len(cols)} rows={len(rows)}')

    phase = 'all four allowed Company filters'
    for company, abbr in COMPANIES.items():
        reply = call('department', {'company': company, **DATES}, csrf)
        must(reply.status_code == 200, abbr + ' HTTP STATUS')
        value = reply.json().get('message')
        must(isinstance(value, dict), abbr + ' RESPONSE TYPE')
        rows = value.get('rows')
        must(isinstance(value.get('columns'), list) and len(value['columns']) == 19,
             abbr + ' COLUMNS')
        must(isinstance(rows, list), abbr + ' ROWS TYPE')
        must(all(r.get('issuing_company') == company for r in rows),
             abbr + ' ROW COMPANY SCOPE')
        checks.append(f'HTTP COMPANY {abbr}: PASS rows={len(rows)}')

    phase = 'company and input denials'
    for label, key, filters in (
        ('UNLISTED COMPANY', 'department', {'company': 'Unlisted Test Company', **DATES}),
        ('SAME COMPANY PAIR', 'intercompany', {
            'issuing_company': ccpc, 'requesting_company': ccpc, **DATES}),
        ('UNKNOWN FILTER', 'department', {**common, 'ignore_permissions': '1'}),
    ):
        must(denied(call(key, filters, csrf)), label + ' NOT DENIED')
        checks.append('HTTP ' + label + ': DENIED (PASS)')

    phase = 'GET method deny'
    get = client.get(
        BASE + METHOD,
        params={'report_key': 'department', 'filters': json.dumps(common)},
        timeout=12, allow_redirects=False,
    )
    must(denied(get), 'GET METHOD NOT BLOCKED')
    checks.append('HTTP GET REPORT METHOD: DENIED (PASS)')

except BaseException as e:
    reason = phase + ': ' + (str(e) if isinstance(e, AssertionError) else type(e).__name__)
finally:
    try:
        frappe.set_user('Administrator')
        frappe.db.rollback()
        if frappe.db.exists('User', USER):
            frappe.db.set_value('User', USER, 'enabled', 0, update_modified=False)
            frappe.db.commit()
            clear_sessions(user=USER, force=True)
            frappe.clear_cache(user=USER)
            must(int(frappe.db.get_value('User', USER, 'enabled')) == 0,
                 'USER NOT DISABLED')
            must(frappe.db.count('Sessions', {'user': USER}) == 0,
                 'ACTIVE SESSION REMAINS')
            print('TEMP ACCOUNT: DISABLED; SESSIONS REVOKED (PASS)', flush=True)
        else:
            print('TEMP ACCOUNT: ABSENT AFTER ROLLBACK', flush=True)
    except BaseException as e:
        reason = 'CLEANUP NOT VERIFIED: ' + (
            str(e) if isinstance(e, AssertionError) else type(e).__name__
        )
    finally:
        try:
            frappe.db.rollback()
        finally:
            frappe.destroy()
            client.close()

for line in checks:
    print(line)
if reason:
    raise SystemExit('AUTHENTICATED HTTP TEST: FAIL / ' + reason)
print('AUTHENTICATED CSRF-PROTECTED FOUR-REPORT HTTP: PASS')
print('TEMP ACCOUNT RETAINED ONLY AS DISABLED DEVELOPMENT AUDIT ROW')
print('NO FINANCIAL TRANSACTION WRITES REQUESTED')
print('PRODUCTION: NOT TOUCHED')
CCPC_EXEC_HTTP_PY
