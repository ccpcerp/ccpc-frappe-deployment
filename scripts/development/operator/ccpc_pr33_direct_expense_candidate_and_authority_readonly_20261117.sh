#!/usr/bin/env bash
# MAIN DEV read-only candidate and mapping-role inventory, no financial writes.
set -euo pipefail
umask 077
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" && "$(id -un)" == "gani" ]] ||
  stop 'original DEV host/user required'
[[ "${CCPC_DIRECT_EXPENSE_CANDIDATE_READ_ONLY:-}" == "YES" ]] ||
  stop 'read-only gate missing'
DEV="frappe_docker_devcontainer-frappe-1"
sudo -v || stop 'sudo authentication failed'
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == "true" ]] ||
  stop 'DEV container stopped'
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == "frappe_docker_devcontainer" ]] ||
  stop 'wrong Docker Compose project'

sudo -n docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench/sites && FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_CANDIDATE_READ_ONLY_PY'
"""Read-only item/role inventory; it NEVER approves mappings or Items."""
from pathlib import Path
import subprocess
import frappe

APP="/workspace/development/frappe-bench/apps/ccpcerp"
SHA="25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
ISSUER="Cagayan Corn Products Corporation"
BUYER="Ricor Mills Corporation"
SI="ACC-SINV-2026-00001"
PI="ACC-PINV-2026-00005"

def must(flag, label):
    if not flag:
        raise RuntimeError("STOP: " + label)

def yn(flag):
    return "YES" if flag else "NO"

def eligible_count(role):
    memberships=frappe.get_all(
        "Has Role",filters={"parenttype":"User","role":role},
        fields=["parent"],limit_page_length=101)
    must(len(memberships)<101,"ROLE_CENSUS_TRUNCATED")
    eligible=set()
    for h in memberships:
        name=h.parent
        if not name or name in ("Administrator","Guest") or name.endswith(
            ("@testing.invalid","@invalid.test")):
            continue
        user=frappe.db.get_value("User",name,["enabled","user_type"],as_dict=True)
        if not user or not user.enabled or user.user_type!="System User":
            continue
        if frappe.db.exists("Has Role",{
            "parenttype":"User","parent":name,"role":"Stockroom Personnel"}):
            continue
        grants=frappe.get_all(
            "User Permission",
            filters={"user":name,"allow":"Company","for_value":BUYER},
            fields=["apply_to_all_doctypes","applicable_for"],
            limit_page_length=101)
        must(len(grants)<101,"COMPANY_GRANT_CENSUS_TRUNCATED")
        if any(int(g.apply_to_all_doctypes or 0)==1
               and not g.applicable_for for g in grants):
            eligible.add(name)
    return len(eligible)

connected=False
try:
    def git(*args):
        return subprocess.check_output(
            ["git","-C",APP,*args],text=True,timeout=30).strip()
    must(git("rev-parse","HEAD")==SHA,"APP_SHA_CHANGED")
    must(git("rev-parse","--abbrev-ref","HEAD")=="HEAD","APP_NOT_DETACHED")
    must(git("status","--porcelain=v1","--untracked-files=all")=="?? AGENTS.md",
         "WORKTREE_CHANGED")
    must((Path(APP)/"AGENTS.md").is_file()
         and not (Path(APP)/"AGENTS.md").is_symlink(),
         "PROTECTED_AGENTS_FILE_CHANGED")
    print("PINNED_MAIN_DEV_SOURCE=PASS",flush=True)
    frappe.init(site="development.localhost",sites_path=".")
    frappe.connect()
    connected=True
    must(frappe.local.site=="development.localhost","WRONG_SITE")
    frappe.db.sql("START TRANSACTION READ ONLY")
    names=frappe.get_all(
        "Intercompany Material Billing Batch",
        filters={"issuing_company":ISSUER,"requesting_company":BUYER},
        pluck="name",limit_page_length=3)
    must(len(names)==1,"BATCH_COUNT_CHANGED")
    batch=frappe.get_doc("Intercompany Material Billing Batch",names[0])
    sales=frappe.get_doc("Sales Invoice",SI)
    purchase=frappe.get_doc("Purchase Invoice",PI)
    must(batch.docstatus==0 and batch.status=="Approved"
         and batch.approved_by=="finance_controller@ccpc.com"
         and batch.sales_invoice==SI and batch.purchase_invoice==PI
         and sales.docstatus==purchase.docstatus==0
         and sales.company==ISSUER and purchase.company==BUYER
         and sales.inter_company_invoice_reference==PI
         and purchase.inter_company_invoice_reference==SI
         and len(batch.items)==len(sales.items)==len(purchase.items)==1,
         "DRAFT_PAIR_CHANGED")
    for dt,name in (("Sales Invoice",SI),("Purchase Invoice",PI)):
        for ledger in ("GL Entry","Stock Ledger Entry"):
            must(frappe.db.count(ledger,{
                "voucher_type":dt,"voucher_no":name})==0,
                "INVOICE_ALREADY_POSTED")
    source=batch.items[0]
    must(source.item_code=="ITEM-00010" and source.stock_uom=="Nos"
         and purchase.items[0].item_code==source.item_code
         and purchase.items[0].expense_account==
             "2301 - Stock Received But Not Billed - RMC",
         "SOURCE_ACCOUNT_CHANGED")
    print("EXACT_DRAFT_PAIR_UNPOSTED=PASS",flush=True)
    orig=frappe.db.get_value(
        "Item",source.item_code,
        ["item_group","is_stock_item","disabled","stock_uom"],as_dict=True)
    must(orig and orig.is_stock_item and not orig.disabled
         and orig.item_group=="Bearings" and orig.stock_uom=="Nos",
         "SOURCE_MASTER_CHANGED")
    print("CURRENT_BEARINGS_ITEM_GROUP_LEAF="+
          yn(frappe.db.get_value("Item Group","Bearings","is_group")==0),
          flush=True)
    print("ITEM_GROUP_AT_ORIGINAL_ISSUE=NOT_FROZEN",flush=True)

    fields=["name","item_name","item_group","is_purchase_item","is_sales_item",
            "is_fixed_asset","enable_deferred_expense","has_variants",
            "variant_of","stock_uom"]
    candidates=frappe.get_all("Item",
        filters={"is_stock_item":0,"disabled":0,"stock_uom":"Nos"},
        fields=fields,limit_page_length=11)
    must(len(candidates)<=10,"CANDIDATE_LIST_TRUNCATED")
    print("SAME_UOM_NONSTOCK_CANDIDATES="+str(len(candidates)),flush=True)
    if len(candidates)==1:
        item=candidates[0]
        print("CANDIDATE_ITEM_CODE="+str(item.name),flush=True)
        print("CANDIDATE_ITEM_NAME="+str(item.item_name),flush=True)
        print("CANDIDATE_ITEM_GROUP="+str(item.item_group),flush=True)
        for field in ("is_purchase_item","is_sales_item","is_fixed_asset",
                      "enable_deferred_expense","has_variants"):
            print("CANDIDATE_"+field.upper()+"="+yn(item[field]),flush=True)
        print("CANDIDATE_VARIANT_OF="+str(item.variant_of or "NONE"),flush=True)
    print("NONSTOCK_BILLING_ITEM_APPROVED=NOT_ESTABLISHED",flush=True)

    for label,key in (("REQUESTING","requesting_department"),
                      ("WORKFOR","work_for_department")):
        value=source.get(key)
        info=frappe.db.get_value("Department",value,
            ["company","disabled","is_group"],as_dict=True) if value else None
        print(label+"_DEPARTMENT="+str(value or "NONE"),flush=True)
        print(label+"_RICOR_ACTIVE_LEAF="+yn(
            info and info.company==BUYER and not info.disabled
            and not info.is_group),flush=True)
    if frappe.get_meta("Stock Entry Detail").has_field("department"):
        original_dept=frappe.db.get_value(
            "Stock Entry Detail",source.stock_entry_detail,"department")
        print("ORIGINAL_STOCK_ENTRY_DETAIL_DEPARTMENT="+
              str(original_dept or "NONE"),flush=True)
    else:
        print("ORIGINAL_STOCK_ENTRY_DETAIL_DEPARTMENT=FIELD_UNAVAILABLE",flush=True)
    print("BENEFICIARY_ISSUE_TIME_PROVENANCE=NOT_CERTIFIED",flush=True)

    print("RICOR_MAPPING_PREPARER_ELIGIBLE_COUNT="+
          str(eligible_count("CCPC Mapping Preparer")),flush=True)
    print("RICOR_MAPPING_APPROVER_ELIGIBLE_COUNT="+
          str(eligible_count("CCPC Accounting Mapping Approver")),flush=True)
    print("MAPPING_ACTOR_NOMINATION=NOT_INFERRED_FROM_ROLE_COUNT",flush=True)
    print("READ_ONLY_CANDIDATE_AND_AUTHORITY_INVENTORY=PASS",flush=True)
    print("NO_MASTER_INVOICE_GL_OR_STOCK_CHANGES=PASS",flush=True)
finally:
    if connected:
        frappe.db.rollback()
    frappe.destroy()
CCPC_CANDIDATE_READ_ONLY_PY
