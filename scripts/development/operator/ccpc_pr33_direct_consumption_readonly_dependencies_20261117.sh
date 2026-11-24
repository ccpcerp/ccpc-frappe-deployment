#!/usr/bin/env bash
# One-step read-only inventory of Ricor direct-expense mapping dependencies.
# No Item/master/invoice/permission changes, financial writes, posting or PRODUCTION.
set -euo pipefail
umask 077
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" && "$(id -un)" == "gani" ]] ||
  stop 'original DEVELOPMENT host/operator required'
[[ "${CCPC_PR33_DIRECT_CONSUMPTION_INVENTORY_READ_ONLY:-}" == "YES" ]] ||
  stop 'read-only inventory not enabled'
DEV="frappe_docker_devcontainer-frappe-1"
sudo -v || stop 'sudo operator authorization failed'
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == "true" ]] ||
  stop 'DEVELOPMENT container stopped'
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == "frappe_docker_devcontainer" ]] ||
  stop 'wrong Docker project'

sudo -n docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench/sites && FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_DIRECT_EXPENSE_READ_ONLY_PY'
"""Current-only inventory; Item Group and beneficiary snapshots are not issue-time proof."""
import subprocess
from pathlib import Path
import frappe

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
SHA = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
SITE = "development.localhost"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
SI = "ACC-SINV-2026-00001"
PI = "ACC-PINV-2026-00005"

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def git(*args):
    return subprocess.check_output(
        ["git", "-C", APP, *args], text=True, timeout=30
    ).strip()

def dept_company(name):
    return frappe.db.get_value("Department", name, "company") if name else None

connected = False
try:
    must(git("rev-parse", "HEAD") == SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD",
         "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md",
         "PROTECTED_APP_WORKTREE_CHANGED")
    must((Path(APP) / "AGENTS.md").is_file()
         and not (Path(APP) / "AGENTS.md").is_symlink(), "PROTECTED_FILE_CHANGED")
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
    must(len(names) == 1, "ONE_BATCH_REQUIRED")
    batch = frappe.get_doc("Intercompany Material Billing Batch", names[0])
    sales = frappe.get_doc("Sales Invoice", SI)
    purchase = frappe.get_doc("Purchase Invoice", PI)
    must(batch.status == "Approved" and batch.docstatus == 0
         and batch.sales_invoice == SI and batch.purchase_invoice == PI
         and sales.docstatus == purchase.docstatus == 0
         and sales.company == ISSUER and purchase.company == BUYER
         and sales.inter_company_invoice_reference == PI
         and purchase.inter_company_invoice_reference == SI
         and len(batch.items) == len(purchase.items) == len(sales.items) == 1,
         "ORIGINAL_DRAFT_PAIR_CHANGED")
    for dt, name in (("Sales Invoice", SI), ("Purchase Invoice", PI)):
        for ledger in ("GL Entry", "Stock Ledger Entry"):
            must(frappe.db.count(ledger, {
                "voucher_type": dt, "voucher_no": name
            }) == 0, "VOUCHER_ALREADY_POSTED")
    print("PRESERVED_DRAFT_PAIR_UNPOSTED=PASS", flush=True)

    source = batch.items[0]
    item = frappe.db.get_value(
        "Item", source.item_code,
        ["item_group", "stock_uom", "is_stock_item", "disabled"],
        as_dict=True
    )
    must(item and item.is_stock_item and not item.disabled
         and item.stock_uom == source.stock_uom,
         "ORIGINAL_STOCK_ITEM_CHANGED")
    print("SOURCE_STOCK_ITEM=" + str(source.item_code), flush=True)
    print("SOURCE_CURRENT_ITEM_GROUP=" + str(item.item_group), flush=True)
    print("SOURCE_FROZEN_UOM=" + str(source.stock_uom), flush=True)
    print("ITEM_GROUP_HISTORICAL_PROVENANCE=NOT_FROZEN_IN_BATCH", flush=True)
    num = frappe.db.count("Item", {
        "is_stock_item": 0, "disabled": 0, "stock_uom": source.stock_uom
    })
    print("AVAILABLE_NONSTOCK_SAME_UOM_ITEM_COUNT=" + str(num), flush=True)
    print("NONSTOCK_ITEM_ACCOUNTING_APPROVAL=NOT_INFERRED_FROM_COUNT", flush=True)

    requester_company = dept_company(source.requesting_department)
    workfor_company = dept_company(source.work_for_department)
    print("SOURCE_REQUESTING_DEPARTMENT_COMPANY="
          + str(requester_company or "NONE_OR_UNKNOWN"), flush=True)
    print("SOURCE_WORKFOR_DEPARTMENT_COMPANY="
          + str(workfor_company or "NONE_OR_UNKNOWN"), flush=True)
    print("BENEFICIARY_ISSUE_TIME_PROVENANCE=NOT_CERTIFIED_BY_BILLING_SNAPSHOT",
          flush=True)

    if (frappe.db.table_exists("CCPC Expense Mapping Scope")
            and frappe.db.table_exists("CCPC Expense Mapping Revision")):
        scopes = frappe.get_all(
            "CCPC Expense Mapping Scope",
            filters={"company": BUYER, "item_group": item.item_group},
            pluck="name", limit_page_length=20
        )
        print("RICOR_SOURCE_ITEM_GROUP_EXPENSE_SCOPES_COUNT="
              + str(len(scopes)), flush=True)
        revisions = frappe.get_all(
            "CCPC Expense Mapping Revision",
            filters={
                "mapping_scope": ["in", scopes],
                "approval_state": "Approved",
            },
            fields=["name", "expense_account"],
            limit_page_length=30,
        ) if scopes else []
        print("RICOR_APPROVED_EXPENSE_REVISIONS_COUNT="
              + str(len(revisions)), flush=True)
        matches = [r for r in revisions
                   if r.expense_account == "5150 - Intercompany Materials Expense - RMC"]
        print("RICOR_REVISIONS_MAPPED_TO_5150_COUNT="
              + str(len(matches)), flush=True)
        print("SIGNED_MAPPING_EFFECTIVE_DATES_AND_USE=NOT_EVALUATED", flush=True)
    else:
        print("RICOR_EXPENSE_MAPPING_SCHEMA=NOT_AVAILABLE", flush=True)

    candidate = None
    if requester_company == BUYER:
        candidate = source.requesting_department
    elif workfor_company == BUYER:
        candidate = source.work_for_department
    if not candidate:
        print("RICOR_BENEFICIARY_CROSSWALK=REQUIRES_EXPLICIT_ACCOUNTING_REVIEW",
              flush=True)
    elif (frappe.db.table_exists("CCPC Center Mapping Scope")
          and frappe.db.table_exists("CCPC Center Mapping Revision")):
        scopes = frappe.get_all(
            "CCPC Center Mapping Scope",
            filters={"company": BUYER, "beneficiary_department": candidate},
            pluck="name", limit_page_length=20
        )
        revisions = frappe.get_all(
            "CCPC Center Mapping Revision",
            filters={"mapping_scope": ["in", scopes], "approval_state": "Approved"},
            pluck="name", limit_page_length=30,
        ) if scopes else []
        print("RICOR_BENEFICIARY_CENTER_SCOPES_COUNT=" + str(len(scopes)),
              flush=True)
        print("RICOR_BENEFICIARY_APPROVED_CENTER_REVISIONS_COUNT="
              + str(len(revisions)), flush=True)
        print("RICOR_BENEFICIARY_VALIDATION=NOT_ESTABLISHED_BY_COUNT", flush=True)
    else:
        print("RICOR_CENTER_MAPPING_SCHEMA=NOT_AVAILABLE", flush=True)
    print("DIRECT_EXPENSE_DEPENDENCIES_READ_ONLY=PASS", flush=True)
    print("NO_MASTER_INVOICE_GL_OR_STOCK_CHANGES=PASS", flush=True)
finally:
    if connected:
        frappe.db.rollback()
    frappe.destroy()
CCPC_DIRECT_EXPENSE_READ_ONLY_PY
