#!/usr/bin/env bash
# One-shot MAIN DEVELOPMENT-only Checker approval on the previously finalized original
# CCPC→Ricor billing batch. Creates exactly ONE cross-linked Draft SI/PI pair.
# Requires original backed-up MAIN DEV and separate Step 15 persisted readback PASS.
# No invoice submit, native ledger/stock posting, user grants, migrations or PRODUCTION.
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
  echo 'STOP: pinned off-host pre-billing recovery unavailable' >&2; exit 1;
}
echo 'PINNED_PRE_BILLING_OFF_HOST_RECOVERY=PRESENT'

docker exec -i --user frappe frappe_docker_devcontainer-frappe-1 \
  bash -c 'cd /workspace/development/frappe-bench/sites && exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_CHECKER_PY'
"""One guarded, already-approved, named Checker Draft-invoice operation on MAIN DEV."""
import subprocess
import sys

import frappe
from frappe.utils import flt, getdate, today

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
SHA = "9f174bb9ce9b9ae103bf968c87c0d703aa039c34"
SITE = "development.localhost"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
MAKER = "ccpc-billing-preparer-dev@testing.invalid"
CHECKER = "ccpc-billing-checker-dev@testing.invalid"
COUNT_DOCTYPES = ("Sales Invoice", "Purchase Invoice", "GL Entry", "Stock Ledger Entry")

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def git(*args):
    return subprocess.check_output(
        ["git", "-C", APP, *args], text=True, timeout=30
    ).strip()

def check_actor(user, roles):
    actor = frappe.get_doc("User", user)
    must(bool(actor.enabled) and actor.user_type == "System User", "ACTOR_DISABLED")
    must({row.role for row in actor.roles} == roles, "ACTOR_ROLE_CHANGED")
    grants = frappe.get_all(
        "User Permission", filters={"user": user},
        fields=["allow", "for_value", "apply_to_all_doctypes", "applicable_for"],
        limit_page_length=20,
    )
    must(
        len(grants) == 2
        and {row.for_value for row in grants} == {ISSUER, BUYER}
        and all(row.allow == "Company"
                and int(row.apply_to_all_doctypes) == 1
                and not row.applicable_for for row in grants),
        "ACTOR_COMPANY_GRANTS_CHANGED",
    )

connected = False
committed = False
try:
    must(git("rev-parse", "HEAD") == SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD", "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1") == "?? AGENTS.md", "APP_WORKTREE_CHANGED")
    must(git("ls-tree", "-r", "--name-only", "HEAD", "--", "AGENTS.md") == "",
         "PROTECTED_FILE_TRACKED")
    print("PINNED_DEV_APP_AND_WORKTREE=PASS", flush=True)

    frappe.init(site=SITE, sites_path=".")
    frappe.connect()
    connected = True
    must(frappe.local.site == SITE, "WRONG_FRAPPE_SITE")
    frappe.set_user("Administrator")
    frappe.db.sql("START TRANSACTION")

    check_actor(MAKER, {"CCPC Billing Preparer"})
    check_actor(CHECKER, {"Finance Controller", "CCPC DEV Billing Master Reader"})
    must(MAKER != CHECKER, "MAKER_CHECKER_NOT_DISTINCT")
    must(frappe.db.count("Custom DocPerm",
         {"role": "CCPC DEV Billing Master Reader"}) == 4,
         "MASTER_READ_ROLE_RULES_CHANGED")

    names = frappe.get_all(
        "Intercompany Material Billing Batch",
        filters={"issuing_company": ISSUER, "requesting_company": BUYER,
                 "status": "Under Review"},
        pluck="name", limit_page_length=3,
    )
    must(len(names) == 1, "EXPECTED_ONE_ORIGINAL_UNDER_REVIEW_BATCH")
    original = frappe.get_doc("Intercompany Material Billing Batch", names[0])
    must(
        original.docstatus == 0 and original.status == "Under Review"
        and original.issuing_company == ISSUER and original.requesting_company == BUYER
        and original.finalized_by == MAKER and bool(original.finalized_on)
        and bool(original.last_refreshed_on) and bool(original.period_end)
        and getdate(original.finalized_on) > getdate(original.period_end)
        and getdate(today()) > getdate(original.period_end)
        and not original.sales_invoice and not original.purchase_invoice
        and not original.approved_by and not original.approved_on,
        "ORIGINAL_BATCH_GUARD_FAILED",
    )
    must(len(original.items) == 1 and bool(original.items[0].stock_entry_detail),
         "ORIGINAL_SOURCE_LINE_CHANGED")
    source = original.items[0]
    detail = frappe.db.get_value(
        "Stock Entry Detail", source.stock_entry_detail,
        ["parent", "item_code", "withdrawal_slip_item"], as_dict=True,
    )
    must(bool(detail) and detail.parent == source.stock_entry
         and detail.item_code == source.item_code and bool(detail.withdrawal_slip_item),
         "SOURCE_DETAIL_CHANGED")
    entry = frappe.db.get_value(
        "Stock Entry", detail.parent,
        ["docstatus", "purpose", "company", "withdrawal_slip", "posting_date"],
        as_dict=True,
    )
    must(
        bool(entry) and entry.docstatus == 1
        and entry.purpose == "Material Issue" and entry.company == ISSUER
        and bool(entry.withdrawal_slip)
        and getdate(original.period_start) <= getdate(entry.posting_date)
        <= getdate(original.period_end),
        "SOURCE_STOCK_ENTRY_CHANGED",
    )
    slip = frappe.db.get_value(
        "Withdrawal Slip", entry.withdrawal_slip,
        ["company", "requesting_company"], as_dict=True,
    )
    must(bool(slip) and slip.company == ISSUER and slip.requesting_company == BUYER,
         "SOURCE_WITHDRAWAL_SLIP_CHANGED")

    before_counts = {doctype: frappe.db.count(doctype) for doctype in COUNT_DOCTYPES}
    original_finalized_on = str(original.finalized_on)
    original_amount = flt(original.total_amount)
    original_period = getdate(original.period_end)
    original_source = source.stock_entry_detail
    original_rate = flt(source.frozen_basic_rate)
    original_qty = flt(source.quantity)
    original_item = source.item_code
    must(original_qty > 0 and original_rate >= 0, "SOURCE_AMOUNT_INVALID")
    print("UNDER_REVIEW_SOURCE_AND_ACTORS=PASS", flush=True)

    # Real controller under synthetic Finance Checker. Never use
    # Administrator/System Manager permission bypass or SQL status mutation.
    frappe.set_user(CHECKER)
    must(frappe.session.user == CHECKER, "CHECKER_SESSION_CHANGED")
    batch = frappe.get_doc("Intercompany Material Billing Batch", original.name)
    result = batch.approve_and_create_invoices()
    persisted = frappe.get_doc("Intercompany Material Billing Batch", original.name)
    must(
        persisted.docstatus == 0 and persisted.status == "Approved"
        and persisted.issuing_company == ISSUER and persisted.requesting_company == BUYER
        and persisted.finalized_by == MAKER
        and str(persisted.finalized_on) == original_finalized_on
        and persisted.approved_by == CHECKER and bool(persisted.approved_on)
        and bool(persisted.sales_invoice) and bool(persisted.purchase_invoice)
        and persisted.sales_invoice != persisted.purchase_invoice
        and getdate(persisted.period_end) == original_period
        and len(persisted.items) == 1
        and persisted.items[0].stock_entry_detail == original_source
        and flt(persisted.total_amount) == original_amount,
        "CHECKER_APPROVED_BATCH_INVALID",
    )
    must(
        isinstance(result, dict)
        and result.get("status") == "Approved"
        and result.get("name") == persisted.name
        and result.get("sales_invoice") == persisted.sales_invoice
        and result.get("purchase_invoice") == persisted.purchase_invoice
        and result.get("approved_by") == CHECKER,
        "CHECKER_CONTROLLER_RETURN_INVALID",
    )

    si = frappe.get_doc("Sales Invoice", persisted.sales_invoice)
    pi = frappe.get_doc("Purchase Invoice", persisted.purchase_invoice)
    must(
        si.docstatus == 0 and pi.docstatus == 0
        and si.company == ISSUER and pi.company == BUYER
        and not si.update_stock and not pi.update_stock
        and not si.get("taxes") and not pi.get("taxes")
        and si.inter_company_invoice_reference == pi.name
        and pi.inter_company_invoice_reference == si.name
        and getdate(si.posting_date) == original_period
        and getdate(pi.posting_date) == original_period
        and abs(flt(si.grand_total) - original_amount) <= 0.01
        and abs(flt(pi.grand_total) - original_amount) <= 0.01,
        "DRAFT_PAIR_LINK_COMPANY_TOTAL_INVALID",
    )
    must(
        len(si.items) == 1 and len(pi.items) == 1
        and si.items[0].item_code == original_item
        and pi.items[0].item_code == original_item
        and abs(flt(si.items[0].qty) - original_qty) <= 0.000001
        and abs(flt(pi.items[0].qty) - original_qty) <= 0.000001
        and abs(flt(si.items[0].rate) - original_rate) <= 0.000001
        and abs(flt(pi.items[0].rate) - original_rate) <= 0.000001,
        "DRAFT_PAIR_LINE_FROZEN_SOURCE_INVALID",
    )
    customer = frappe.db.get_value(
        "Customer", si.customer,
        ["is_internal_customer", "represents_company", "disabled"], as_dict=True,
    )
    supplier = frappe.db.get_value(
        "Supplier", pi.supplier,
        ["is_internal_supplier", "represents_company", "disabled"], as_dict=True,
    )
    must(
        bool(customer) and bool(customer.is_internal_customer)
        and customer.represents_company == BUYER and not customer.disabled
        and bool(supplier) and bool(supplier.is_internal_supplier)
        and supplier.represents_company == ISSUER and not supplier.disabled,
        "INTERNAL_PARTY_PAIR_INVALID",
    )
    print("CROSS_LINKED_DRAFT_SI_PI=PASS", flush=True)

    after_counts = {doctype: frappe.db.count(doctype) for doctype in COUNT_DOCTYPES}
    must(
        after_counts["Sales Invoice"] == before_counts["Sales Invoice"] + 1
        and after_counts["Purchase Invoice"] == before_counts["Purchase Invoice"] + 1,
        "INVOICE_ROW_DELTA_NOT_EXACT_PAIR",
    )
    must(
        after_counts["GL Entry"] == before_counts["GL Entry"]
        and after_counts["Stock Ledger Entry"] == before_counts["Stock Ledger Entry"],
        "UNEXPECTED_LEDGER_OR_STOCK_ROW_DELTA",
    )
    print("ONLY_TWO_DRAFT_INVOICES_CREATED=PASS", flush=True)
    print("GL_AND_STOCK_ROW_COUNTS_UNCHANGED=PASS", flush=True)

    # Exactly one deliberate commit, only after all assertions.
    frappe.db.commit()
    committed = True
    print("CHECKER_APPROVAL_TRANSACTION=COMMITTED", flush=True)
    print("PRODUCTION_NOT_TARGETED=PASS", flush=True)
    print("STEP_16_CHECKER_EXECUTION=PASS", flush=True)
except Exception as exc:
    if connected and not committed:
        frappe.db.rollback()
    print("STOP: Checker operation not verified; do NOT automatically retry",
          file=sys.stderr)
    print("FAILURE_CLASS=" + type(exc).__name__, file=sys.stderr)
    raise SystemExit(1)
finally:
    if connected:
        if not committed:
            frappe.db.rollback()
        frappe.destroy()
CCPC_CHECKER_PY
