#!/usr/bin/env bash
# One-shot operator-run MAIN DEVELOPMENT maker finalization of existing CCPC→Ricor billing Draft.
# Approved only for controlled persistent DEV acceptance after fresh local + Synology 4/4 backups.
# Does NOT approve, create, submit or cancel invoices; no migrations or production actions.
set -euo pipefail
umask 077

if [[ "$(id -u)" -eq 0 ]]; then
  echo 'STOP: normal nonroot host operator required' >&2
  exit 1
fi
NAS='/mnt/erpnext_backups'
RECOVERY='ccpc-development-pr33-billing-preacceptance-20261104T082044Z-4231b0c38ab77bf0'
SOURCE='development.localhost-20261104T081242Z-d43564b53468'
actual_mount="$(findmnt -rn -M "$NAS" -o SOURCE,FSTYPE)"
[[ "$actual_mount" == '//192.168.50.132/erpnext_backups cifs' ]] || {
  echo 'STOP: unexpected Synology mount' >&2; exit 1;
}
[[ -d "$NAS/$RECOVERY/$SOURCE" && ! -L "$NAS/$RECOVERY" &&
   -f "$NAS/$RECOVERY/SHA256SUMS" && ! -L "$NAS/$RECOVERY/SHA256SUMS" ]] || {
  echo 'STOP: verified pre-billing off-host recovery set unavailable' >&2; exit 1;
}
echo 'PINNED_PRE_BILLING_OFF_HOST_RECOVERY=PRESENT'

docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 \
  bash -c 'cd /workspace/development/frappe-bench/sites && exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_MAKER_PY'
"""Exactly one named Preparer finalization on existing MAIN DEVELOPMENT billing Draft."""
import subprocess
import sys

import frappe
from frappe.utils import getdate, today

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
SHA = "9f174bb9ce9b9ae103bf968c87c0d703aa039c34"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
PREPARER = "ccpc-billing-preparer-dev@testing.invalid"
CHECKER = "ccpc-billing-checker-dev@testing.invalid"
SOURCE = "development.localhost"
MONEY = ("Sales Invoice", "Purchase Invoice", "GL Entry", "Stock Ledger Entry")

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def git(*args):
    return subprocess.check_output(["git", "-C", APP, *args], text=True, timeout=30).strip()

def check_actor(user, required_roles):
    doc = frappe.get_doc("User", user)
    must(bool(doc.enabled) and doc.user_type == "System User", "TEST_ACTOR_STATE")
    must({r.role for r in doc.roles} == required_roles, "TEST_ACTOR_ROLES")
    grants = frappe.db.sql(
        """SELECT allow, for_value, apply_to_all_doctypes, applicable_for
           FROM `tabUser Permission` WHERE user=%s""",
        (user,), as_dict=True,
    )
    must(
        len(grants) == 2
        and {g.for_value for g in grants} == {ISSUER, BUYER}
        and all(g.allow == "Company" and int(g.apply_to_all_doctypes) == 1
                and not g.applicable_for for g in grants),
        "TEST_ACTOR_COMPANY_GRANTS",
    )

connected = False
committed = False
try:
    must(git("rev-parse", "HEAD") == SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD", "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1") == "?? AGENTS.md", "APP_WORKTREE_CHANGED")
    must(git("ls-tree", "-r", "--name-only", "HEAD", "--", "AGENTS.md") == "", "PROTECTED_FILE_TRACKED")
    print("PINNED_DEV_APP_AND_WORKTREE=PASS", flush=True)

    frappe.init(site=SOURCE, sites_path=".")
    frappe.connect()
    connected = True
    must(frappe.local.site == SOURCE, "WRONG_FRAPPE_SITE")
    frappe.set_user("Administrator")
    frappe.db.sql("START TRANSACTION")

    check_actor(PREPARER, {"CCPC Billing Preparer"})
    check_actor(CHECKER, {"Finance Controller", "CCPC DEV Billing Master Reader"})
    must(PREPARER != CHECKER, "ACTORS_NOT_DISTINCT")
    must(frappe.db.count("Custom DocPerm", {"role": "CCPC DEV Billing Master Reader"}) == 4,
         "READER_PERMISSION_RULES_CHANGED")

    batches = frappe.get_all(
        "Intercompany Material Billing Batch",
        filters={"issuing_company": ISSUER, "requesting_company": BUYER, "status": "Draft"},
        pluck="name",
        limit_page_length=3,
    )
    must(len(batches) == 1, "EXPECTED_ONE_ORIGINAL_DRAFT")
    original = frappe.get_doc("Intercompany Material Billing Batch", batches[0])
    must(
        original.docstatus == 0 and original.status == "Draft"
        and original.issuing_company == ISSUER and original.requesting_company == BUYER
        and not original.sales_invoice and not original.purchase_invoice
        and not original.approved_by and not original.approved_on
        and original.period_end and getdate(today()) > getdate(original.period_end),
        "DRAFT_PREFLIGHT_CHANGED",
    )
    must(len(original.items) == 1 and bool(original.items[0].stock_entry_detail),
         "SAVED_ONE_SOURCE_LINE_CHANGED")
    original_source = original.items[0].stock_entry_detail
    original_period = getdate(original.period_end)
    original_company = (original.issuing_company, original.requesting_company)
    counts_before = {doctype: frappe.db.count(doctype) for doctype in MONEY}
    print("ORIGINAL_DRAFT_AND_ACTORS=PASS", flush=True)

    # Explicitly adopt the synthetic named user's roles. No ignore_permissions,
    # Administrator role bypass, manual status write or direct SQL mutation.
    frappe.set_user(PREPARER)
    must(frappe.session.user == PREPARER, "MAKER_SESSION_CHANGED")

    maker_doc = frappe.get_doc("Intercompany Material Billing Batch", original.name)
    result = maker_doc.finalize_month()

    # The real controller locks/reloads, validates the eligible Material Issue
    # and Company grants, rebuilds one child line and saves the workflow transition.
    persisted = frappe.get_doc("Intercompany Material Billing Batch", original.name)
    must(
        persisted.docstatus == 0 and persisted.status == "Under Review"
        and persisted.issuing_company == original_company[0]
        and persisted.requesting_company == original_company[1]
        and getdate(persisted.period_end) == original_period
        and persisted.finalized_by == PREPARER and bool(persisted.finalized_on)
        and not persisted.sales_invoice and not persisted.purchase_invoice
        and not persisted.approved_by and not persisted.approved_on,
        "MAKER_POST_STATE_INVALID",
    )
    must(
        len(persisted.items) == 1
        and persisted.items[0].stock_entry_detail == original_source,
        "MAKER_SOURCE_MEMBERSHIP_CHANGED",
    )
    must(
        isinstance(result, dict)
        and result.get("status") == "Under Review"
        and int(result.get("line_count") or 0) == 1,
        "MAKER_RETURN_INVALID",
    )
    must(
        all(frappe.db.count(doctype) == counts_before[doctype] for doctype in MONEY),
        "UNEXPECTED_INVOICE_OR_LEDGER_ROW_COUNT_CHANGE",
    )
    print("MAKER_FINALIZATION_IN_TRANSACTION=PASS", flush=True)
    print("ONE_SOURCE_LINE_AND_NO_INVOICE_LINKS=PASS", flush=True)
    print("INVOICE_AND_GL_STOCK_ROW_COUNTS_UNCHANGED=PASS", flush=True)

    frappe.db.commit()
    committed = True
    print("MAKER_FINALIZATION_TRANSACTION=COMMITTED", flush=True)
    print("PRODUCTION_NOT_TARGETED=PASS", flush=True)
except Exception as exc:
    if connected and not committed:
        frappe.db.rollback()
    print("STOP: maker finalization not verified; no automatic retry", file=sys.stderr)
    print("FAILURE_CLASS=" + type(exc).__name__, file=sys.stderr)
    raise SystemExit(1)
finally:
    if connected:
        if not committed:
            frappe.db.rollback()
        frappe.destroy()
CCPC_MAKER_PY
