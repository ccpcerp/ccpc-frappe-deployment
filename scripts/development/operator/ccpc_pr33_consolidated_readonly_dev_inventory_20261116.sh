#!/usr/bin/env bash
# CCPC PR33: one bounded, READ-ONLY two-site DEVELOPMENT inventory.
# No migration, bench, restart, real role changes, invoices or PRODUCTION.
set -euo pipefail
umask 077
stop() { echo "STOP: $1" >&2; exit 1; }
[[ "$(hostname -s)" = "ccpcerpserver" ]] || stop "unexpected host"
[[ "$(id -un)" = "gani" ]] || stop "normal operator required"
NAS=/mnt/erpnext_backups
[[ "$(findmnt -rn -M "$NAS" -o SOURCE,FSTYPE)" = "//192.168.50.132/erpnext_backups cifs" ]] || stop "NAS mount changed"
[[ -f "$NAS/ccpc-development-pr33-20261104T010408Z-82316b860fe951ad/SHA256SUMS" ]] || stop "two-site manifest absent"
[[ -f "$NAS/ccpc-development-pr33-billing-preacceptance-20261104T082044Z-4231b0c38ab77bf0/SHA256SUMS" ]] || stop "MAIN manifest absent"
DEV=frappe_docker_devcontainer-frappe-1
[[ "$(sudo docker inspect --format '{{.State.Running}}' "$DEV")" = true ]] || stop "DEV not running"
[[ "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" = frappe_docker_devcontainer ]] || stop "wrong Compose project"
sudo docker exec -i --user frappe "$DEV" bash -c 'cd /workspace/development/frappe-bench/sites && FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -' <<'PY'
import re
import subprocess
import frappe
from pathlib import Path

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
SHA = "1bde04bf6d51d2c1b3197ef41696e8b6df7b0ecc"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
ACTORS = (
    ("MAKER", "ccpc-billing-preparer-dev@testing.invalid", {"CCPC Billing Preparer"}),
    ("CHECKER", "ccpc-billing-checker-dev@testing.invalid",
     {"Finance Controller", "CCPC DEV Billing Master Reader"}),
)
REPORTS = (
    "CCPC Department Material Consumption",
    "CCPC Equipment Job Material Activity",
    "CCPC Intercompany Withdrawal Billing Status",
    "CCPC Company Stock PNL GL Reconciliation",
)

def git(*args):
    return subprocess.check_output(["git", "-C", APP, *args], text=True, timeout=30).strip()
def guard(ok, label):
    if not ok:
        raise RuntimeError("STOP: " + label)
def flag(label, ok):
    print(label + "=" + ("PASS" if ok else "REVIEW"), flush=True)
def scalar(sql, args=()):
    return frappe.db.sql(sql, args, as_list=True)[0][0]
def safe_tag(value):
    return re.sub("[^A-Z0-9_]", "_", str(value or "UNKNOWN").upper().replace(" ", "_"))[:45]

guard(Path.cwd() == Path("/workspace/development/frappe-bench/sites"), "wrong working directory")
guard(git("rev-parse", "HEAD") == SHA, "DEV commit changed")
guard(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md",
      "DEV worktree changed")
guard(Path(APP, "AGENTS.md").is_file() and not Path(APP, "AGENTS.md").is_symlink(),
      "protected file changed")
guard(subprocess.run(["git", "-C", APP, "symbolic-ref", "-q", "HEAD"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 1,
      "DEV checkout not detached")
print("PINNED_SOURCE_AND_PROTECTED_WORKTREE=PASS")

for name in ("development.localhost", "ccpc-integration2.localhost",
             "ccpc-integration.localhost"):
    guard(Path(name, "site_config.json").is_file(), "site configuration missing")
print("THREE_SITE_CONFIGS=PRESENT")
print("BROKEN_THIRD_SITE=NOT_CONNECTED")

def metadata(label):
    for doctype, code in (
        ("Intercompany Material Billing Batch", "BATCH"),
        ("CCPC Intercompany Billing Correction", "CORRECTION"),
    ):
        flag(label + "_" + code + "_SCHEMA",
             bool(frappe.db.exists("DocType", doctype))
             and bool(frappe.db.table_exists(doctype)))
    for role, code in (
        ("CCPC Billing Preparer", "PREPARER"),
        ("Finance Controller", "FINANCE"),
        ("CCPC Group Executive Reporting", "EXECUTIVE"),
    ):
        flag(label + "_" + code + "_ROLE", bool(frappe.db.exists("Role", role)))
    for index, report in enumerate(REPORTS, 1):
        flag(label + "_REPORT_" + str(index), bool(frappe.db.exists("Report", report)))
    flag(label + "_EXECUTIVE_PAGE",
         bool(frappe.db.exists("Page", "ccpc-group-executive-reporting")))

def main_data():
    companies = frappe.db.sql(
        "SELECT name,abbr FROM `tabCompany` WHERE name IN (%s,%s)",
        (ISSUER, BUYER), as_dict=True)
    flag("MAIN_TWO_COMPANIES_ABBR",
         {r.name: r.abbr for r in companies} == {ISSUER: "CCPC", BUYER: "RMC"})
    for label, actor, expected in ACTORS:
        users = frappe.db.sql(
            "SELECT enabled,user_type FROM `tabUser` WHERE name=%s",
            (actor,), as_dict=True)
        roles = frappe.db.sql(
            "SELECT role FROM `tabHas Role` WHERE parenttype='User' AND parent=%s",
            (actor,), as_dict=True)
        grants = frappe.db.sql(
            "SELECT allow,for_value,apply_to_all_doctypes,applicable_for "
            "FROM `tabUser Permission` WHERE user=%s",
            (actor,), as_dict=True)
        flag(label + "_ENABLED",
             len(users) == 1 and int(users[0].enabled or 0) == 1
             and users[0].user_type == "System User")
        flag(label + "_ROLES",
             {r.role for r in roles} == expected and len(roles) == len(expected))
        flag(label + "_COMPANY_GRANTS",
             len(grants) == 2 and {g.for_value for g in grants} == {ISSUER, BUYER}
             and all(g.allow == "Company"
                     and int(g.apply_to_all_doctypes or 0) == 1
                     and not g.applicable_for for g in grants))
    for role, code in (("CCPC Billing Preparer", "PREPARER"),
                       ("Finance Controller", "FINANCE")):
        count = scalar(
            "SELECT COUNT(DISTINCT u.name) FROM `tabUser` u "
            "JOIN `tabHas Role` h ON h.parent=u.name "
            "WHERE h.parenttype='User' AND h.role=%s "
            "AND u.enabled=1 AND u.user_type='System User' "
            "AND u.name NOT IN ('Guest','Administrator')", (role,))
        print("MAIN_ENABLED_NAMED_" + code + "_COUNT=" + str(int(count)))
    perms = frappe.db.sql(
        "SELECT role, `read`, `write`, `create` FROM `tabDocPerm` "
        "WHERE parent='Intercompany Material Billing Batch' "
        "AND role IN ('CCPC Billing Preparer','Finance Controller','System Manager')",
        as_dict=True)
    rights = {r.role: (int(r.get("read") or 0), int(r.get("write") or 0),
                       int(r.get("create") or 0)) for r in perms}
    flag("MAIN_BILLING_DOCPERM",
         rights.get("CCPC Billing Preparer") == (1,1,1)
         and rights.get("Finance Controller") == (1,1,0)
         and rights.get("System Manager") == (1,0,0))
    batches = frappe.db.sql(
        "SELECT status,COUNT(*) n,"
        "SUM(IF(IFNULL(sales_invoice,'')!='',1,0)) sl,"
        "SUM(IF(IFNULL(purchase_invoice,'')!='',1,0)) pl "
        "FROM `tabIntercompany Material Billing Batch` "
        "WHERE issuing_company=%s AND requesting_company=%s "
        "GROUP BY status ORDER BY status", (ISSUER,BUYER), as_dict=True)
    print("MAIN_CCPC_RMC_BATCH_TOTAL=" + str(sum(int(r.n) for r in batches)))
    for row in batches:
        key = "MAIN_BATCH_" + safe_tag(row.status)
        print(key + "_COUNT=" + str(int(row.n)))
        print(key + "_SALES_LINKS=" + str(int(row.sl or 0)))
        print(key + "_PURCHASE_LINKS=" + str(int(row.pl or 0)))
    corrections = frappe.db.sql(
        "SELECT status,COUNT(*) n FROM `tabCCPC Intercompany Billing Correction` "
        "WHERE issuing_company=%s AND requesting_company=%s GROUP BY status",
        (ISSUER, BUYER), as_dict=True)
    print("MAIN_CORRECTION_TOTAL=" + str(sum(int(r.n) for r in corrections)))
    for row in corrections:
        print("MAIN_CORRECTION_" + safe_tag(row.status) + "_COUNT=" + str(int(row.n)))
    total_pairs = int(scalar(
        "SELECT COUNT(*) FROM `tabIntercompany Material Billing Batch` "
        "WHERE issuing_company=%s AND requesting_company=%s "
        "AND (IFNULL(sales_invoice,'')!='' OR IFNULL(purchase_invoice,'')!='')",
        (ISSUER, BUYER)))
    pairs = frappe.db.sql(
        "SELECT b.period_end,b.sales_invoice,b.purchase_invoice,"
        "s.name sn,s.company sc,s.posting_date sd,s.inter_company_invoice_reference sr,"
        "p.name pn,p.company pc,p.posting_date pd,p.inter_company_invoice_reference pr "
        "FROM `tabIntercompany Material Billing Batch` b "
        "LEFT JOIN `tabSales Invoice` s ON s.name=b.sales_invoice "
        "LEFT JOIN `tabPurchase Invoice` p ON p.name=b.purchase_invoice "
        "WHERE b.issuing_company=%s AND b.requesting_company=%s "
        "AND (IFNULL(b.sales_invoice,'')!='' OR IFNULL(b.purchase_invoice,'')!='') "
        "ORDER BY b.creation DESC LIMIT 50",
        (ISSUER, BUYER), as_dict=True)
    wrong = sum(not (r.sales_invoice and r.purchase_invoice
                     and r.sn == r.sales_invoice and r.pn == r.purchase_invoice
                     and r.sc == ISSUER and r.pc == BUYER
                     and r.sr == r.purchase_invoice and r.pr == r.sales_invoice
                     and r.sd == r.period_end and r.pd == r.period_end)
                for r in pairs)
    print("MAIN_INVOICE_PAIR_TOTAL=" + str(total_pairs))
    print("MAIN_INVOICE_PAIR_SAMPLED=" + str(len(pairs)))
    print("MAIN_INVOICE_PAIR_SAMPLED_MISMATCH_COUNT=" + str(wrong))
    if total_pairs > len(pairs):
        print("MAIN_INVOICE_PAIR_AUDIT=PARTIAL_SAMPLE")

def inspect(label, site, main):
    connected = False
    try:
        frappe.init(site=site, sites_path=".")
        frappe.connect()
        connected = True
        guard(frappe.local.site == site, "wrong Frappe site")
        frappe.db.sql("START TRANSACTION READ ONLY")
        print(label + "_READ_ONLY_TRANSACTION=STARTED")
        metadata(label)
        if main:
            main_data()
        print(label + "_READ_ONLY_DIAGNOSTIC=COMPLETE")
    finally:
        if connected:
            try:
                frappe.db.rollback()
            finally:
                frappe.destroy()
        else:
            frappe.destroy()

inspect("MAIN", "development.localhost", True)
inspect("INTEGRATION2", "ccpc-integration2.localhost", False)
print("DEV_CONSOLIDATED_READ_ONLY_AUDIT=COMPLETE")
PY
