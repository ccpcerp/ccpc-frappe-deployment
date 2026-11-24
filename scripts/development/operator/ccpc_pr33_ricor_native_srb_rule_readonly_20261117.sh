#!/usr/bin/env bash
# Exact MAIN DEV Ricor PI: read-only diagnosis of native stock/clearing account rule.
# Does not submit, cancel, edit, revalidate, modify a doc, post or commit.
set -euo pipefail
umask 077
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" && "$(id -un)" == "gani" ]] ||
  stop 'original DEV host/operator required'
[[ "${CCPC_PR33_RICOR_SRB_DIAGNOSTIC_READ_ONLY:-}" == "YES" ]] ||
  stop 'read-only diagnosis gate missing'
DEV="frappe_docker_devcontainer-frappe-1"
sudo -v || stop 'operator sudo failed'
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == "true" ]] ||
  stop 'DEV container is stopped'
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == "frappe_docker_devcontainer" ]] ||
  stop 'wrong Docker project'

sudo -n docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench/sites && FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_SRB_READ_ONLY_PY'
"""Inspect native rule and saved Ricor PI flags. NEVER execute set_expense_account."""
import inspect
import subprocess
from pathlib import Path

import erpnext
import frappe

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
APP_SHA = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
SITE = "development.localhost"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
SI = "ACC-SINV-2026-00001"
PI = "ACC-PINV-2026-00005"
CHECKER = "finance_controller@ccpc.com"

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def yesno(flag):
    return "YES" if flag else "NO"

connected = False
try:
    def git(*args):
        return subprocess.check_output(
            ["git", "-C", APP, *args], text=True, timeout=30
        ).strip()

    must(git("rev-parse", "HEAD") == APP_SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD",
         "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md",
         "APP_WORKTREE_CHANGED")
    must((Path(APP) / "AGENTS.md").is_file()
         and not (Path(APP) / "AGENTS.md").is_symlink(),
         "PROTECTED_APP_FILE_CHANGED")
    print("PINNED_MAIN_DEV_SOURCE=PASS", flush=True)

    frappe.init(site=SITE, sites_path=".")
    frappe.connect()
    connected = True
    must(frappe.local.site == SITE, "WRONG_SITE")
    frappe.db.sql("START TRANSACTION READ ONLY")

    names = frappe.get_all(
        "Intercompany Material Billing Batch",
        filters={"issuing_company": ISSUER, "requesting_company": BUYER},
        pluck="name", limit_page_length=3
    )
    must(len(names) == 1, "BATCH_COUNT_CHANGED")
    batch = frappe.get_doc("Intercompany Material Billing Batch", names[0])
    purchase = frappe.get_doc("Purchase Invoice", PI)
    sale = frappe.get_doc("Sales Invoice", SI)
    must(batch.status == "Approved" and batch.docstatus == 0
         and batch.approved_by == CHECKER
         and batch.sales_invoice == SI and batch.purchase_invoice == PI
         and purchase.docstatus == sale.docstatus == 0
         and purchase.company == BUYER and sale.company == ISSUER
         and purchase.inter_company_invoice_reference == SI
         and sale.inter_company_invoice_reference == PI
         and len(purchase.items) == len(sale.items) == len(batch.items) == 1,
         "ORIGINAL_DRAFT_PAIR_CHANGED")
    must(not purchase.update_stock
         and not purchase.get("taxes")
         and not purchase.is_return
         and frappe.db.count("GL Entry", {"voucher_type": "Purchase Invoice", "voucher_no": PI}) == 0
         and frappe.db.count("Stock Ledger Entry", {"voucher_type": "Purchase Invoice", "voucher_no": PI}) == 0,
         "PI_ALREADY_POSTED_OR_CHANGED")
    line = purchase.items[0]
    must(line.item_code == batch.items[0].item_code,
         "SOURCE_ITEM_CHANGED")
    print("EXACT_DRAFT_PAIR_UNPOSTED=PASS", flush=True)

    item = frappe.db.get_value(
        "Item", line.item_code,
        ["is_stock_item", "is_fixed_asset"],
        as_dict=True,
    )
    must(item is not None, "ITEM_NOT_FOUND")
    perpetual = bool(erpnext.is_perpetual_inventory_enabled(BUYER))
    is_stock = bool(item.is_stock_item)
    is_fixed = bool(line.is_fixed_asset or item.is_fixed_asset)
    has_pr = bool(line.purchase_receipt)
    is_opening_no = purchase.is_opening == "No"
    po_detail = line.po_detail
    dropship = bool(
        po_detail and frappe.db.get_value(
            "Purchase Order Item", po_detail, "delivered_by_supplier"
        )
    )
    clearing = purchase.get_company_default("stock_received_but_not_billed")
    default_expense = frappe.db.get_value(
        "Account", "5150 - Intercompany Materials Expense - RMC", "name"
    )
    must(bool(clearing) and bool(default_expense),
         "EXPECTED_CHART_ACCOUNTS_MISSING")
    native_src = inspect.getsource(type(purchase).set_expense_account)
    native_rule_present = all(
        anchor in native_src
        for anchor in (
            "is_perpetual_inventory_enabled",
            "item.item_code in stock_items",
            'item.expense_account = stock_not_billed_account',
            "if item.purchase_receipt:",
        )
    )
    must(native_rule_present, "INSTALLED_NATIVE_RULE_DIFFERS")
    print("INSTALLED_NATIVE_PI_STOCK_CLEARING_RULE=FOUND", flush=True)
    print("RICOR_PERPETUAL_INVENTORY=" + yesno(perpetual), flush=True)
    print("ITEM_IS_STOCK_ITEM=" + yesno(is_stock), flush=True)
    print("PI_IS_OPENING_NO=" + yesno(is_opening_no), flush=True)
    print("ITEM_IS_FIXED_ASSET=" + yesno(is_fixed), flush=True)
    print("PI_ITEM_HAS_PURCHASE_RECEIPT=" + yesno(has_pr), flush=True)
    print("PI_ITEM_HAS_PO_DETAIL=" + yesno(bool(po_detail)), flush=True)
    print("PI_ITEM_DROPSHIP=" + yesno(dropship), flush=True)
    print("PI_UPDATE_STOCK=" + yesno(bool(purchase.update_stock)), flush=True)
    print("RICOR_COMPANY_STOCK_RECEIVED_NOT_BILLED=" + str(clearing), flush=True)
    print("SAVED_PI_LINE_ACCOUNT=" + str(line.expense_account), flush=True)
    print("INTENDED_RICOR_EXPENSE_ACCOUNT=" + str(default_expense), flush=True)
    predicted = perpetual and is_stock and is_opening_no and not is_fixed and not dropship and not has_pr
    print("NATIVE_NO_RECEIPT_CLEARING_RULE_APPLIES=" + yesno(predicted), flush=True)
    print("SAVED_PI_MATCHES_NATIVE_CLEARING="
          + yesno(predicted and line.expense_account == clearing), flush=True)
    print("NO_PI_REVALIDATION_OR_POSTING_PERFORMED=PASS", flush=True)
    print("READ_ONLY_SRB_DIAGNOSTIC=PASS", flush=True)
finally:
    if connected:
        frappe.db.rollback()
    frappe.destroy()
CCPC_SRB_READ_ONLY_PY
