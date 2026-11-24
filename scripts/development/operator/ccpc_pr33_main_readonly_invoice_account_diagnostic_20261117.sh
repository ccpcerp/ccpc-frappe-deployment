#!/usr/bin/env bash
# Read-only diagnosis of the existing MAIN DEV Draft CCPC SI / Ricor PI account mismatch.
# Does NOT run invoice submission, alter accounts/permissions, commit or target PROD.
set -euo pipefail
umask 077
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" && "$(id -un)" == "gani" ]] ||
  stop 'original DEVELOPMENT host/operator required'
[[ "${CCPC_PR33_ACCOUNT_DIAGNOSTIC_READ_ONLY:-}" == "YES" ]] ||
  stop 'read-only diagnostic authorization missing'
DEV="frappe_docker_devcontainer-frappe-1"
sudo -v || stop 'sudo authentication failed'
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == "true" ]] ||
  stop 'DEVELOPMENT container stopped'
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == "frappe_docker_devcontainer" ]] ||
  stop 'wrong Docker Compose project'

sudo -n docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench/sites && FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_ACCOUNT_DIAGNOSTIC_PY'
"""Independent no-write comparison of saved invoice account fields with controller defaults."""
import subprocess
from pathlib import Path
import frappe

SITE = "development.localhost"
APP = "/workspace/development/frappe-bench/apps/ccpcerp"
APP_SHA = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
SI = "ACC-SINV-2026-00001"
PI = "ACC-PINV-2026-00005"
CHECKER = "finance_controller@ccpc.com"

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def git(*args):
    return subprocess.check_output(
        ["git", "-C", APP, *args], text=True, timeout=30
    ).strip()

connected = False
try:
    must(git("rev-parse", "HEAD") == APP_SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD",
         "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md",
         "PROTECTED_APP_WORKTREE_CHANGED")
    must((Path(APP) / "AGENTS.md").is_file()
         and not (Path(APP) / "AGENTS.md").is_symlink(),
         "PROTECTED_AGENTS_FILE_CHANGED")
    print("PINNED_MAIN_DEV_SOURCE=PASS", flush=True)

    frappe.init(site=SITE, sites_path=".")
    frappe.connect()
    connected = True
    must(frappe.local.site == SITE, "UNEXPECTED_SITE")
    frappe.db.sql("START TRANSACTION READ ONLY")

    batches = frappe.get_all(
        "Intercompany Material Billing Batch",
        filters={"issuing_company": ISSUER, "requesting_company": BUYER},
        pluck="name", limit_page_length=3
    )
    must(len(batches) == 1, "EXPECTED_ONE_BATCH")
    batch = frappe.get_doc("Intercompany Material Billing Batch", batches[0])
    must(batch.docstatus == 0 and batch.status == "Approved"
         and batch.approved_by == CHECKER
         and batch.sales_invoice == SI and batch.purchase_invoice == PI,
         "ORIGINAL_APPROVAL_CHANGED")

    sales = frappe.get_doc("Sales Invoice", SI)
    purchase = frappe.get_doc("Purchase Invoice", PI)
    must(sales.docstatus == 0 and purchase.docstatus == 0
         and sales.company == ISSUER and purchase.company == BUYER
         and sales.inter_company_invoice_reference == PI
         and purchase.inter_company_invoice_reference == SI
         and len(sales.items) == len(purchase.items) == 1,
         "PERSISTED_DRAFT_PAIR_CHANGED")
    for dt, name in (("Sales Invoice", SI), ("Purchase Invoice", PI)):
        for ledger in ("GL Entry", "Stock Ledger Entry"):
            must(frappe.db.count(ledger, {"voucher_type": dt, "voucher_no": name}) == 0,
                 "INVOICE_LEDGER_OR_STOCK_POSTING_PRESENT")
    print("DRAFT_PAIR_NO_POSTING=PASS", flush=True)

    issuer = frappe.db.get_value("Company", ISSUER, "abbr")
    buyer = frappe.db.get_value("Company", BUYER, "abbr")
    must(bool(issuer) and bool(buyer), "COMPANY_ABBR_MISSING")

    checks = (
        ("CCPC_RECEIVABLE", sales.debit_to,
         f"1312 - Intercompany Receivable - {issuer}", ISSUER, "Asset", "Receivable"),
        ("CCPC_INCOME", sales.items[0].income_account,
         f"6050 - Intercompany Material Charges - {issuer}", ISSUER, "Income", None),
        ("RICOR_EXPENSE", purchase.items[0].expense_account,
         f"5150 - Intercompany Materials Expense - {buyer}", BUYER, "Expense", None),
        ("RICOR_PAYABLE", purchase.credit_to,
         f"2121 - Intercompany Payable - {buyer}", BUYER, "Liability", "Payable"),
    )
    matches = 0
    for label, actual, expected, company, root, account_type in checks:
        exact = actual == expected
        matches += int(exact)
        print(label + "_EXACT_NAME=" + ("MATCH" if exact else "MISMATCH"), flush=True)
        print(label + "_EXPECTED=" + str(expected), flush=True)
        print(label + "_ACTUAL=" + str(actual), flush=True)
        for kind, name in (("ACTUAL", actual), ("EXPECTED", expected)):
            info = frappe.db.get_value(
                "Account", name,
                ["company", "root_type", "account_type", "is_group", "disabled"],
                as_dict=True
            ) if name else None
            if not info:
                print(label + "_" + kind + "_ACCOUNT=NOT_FOUND", flush=True)
            else:
                valid = (
                    info.company == company and info.root_type == root
                    and not info.is_group and not info.disabled
                    and (not account_type or info.account_type == account_type)
                )
                print(label + "_" + kind + "_ACCOUNT="
                      + ("VALID_FOR_ROLE" if valid else "INVALID_FOR_ROLE"),
                      flush=True)
                print(label + "_" + kind + "_COMPANY=" + str(info.company), flush=True)
                print(label + "_" + kind + "_ROOT=" + str(info.root_type), flush=True)
                print(label + "_" + kind + "_TYPE=" + str(info.account_type), flush=True)
    print("EXACT_ACCOUNT_NAMES_MATCHED=" + str(matches) + "/4", flush=True)
    print("DIAGNOSTIC_ONLY_NO_ACCOUNT_CHANGES=PASS", flush=True)
    print("READ_ONLY_NO_COMMIT_OR_SUBMIT=PASS", flush=True)
finally:
    if connected:
        frappe.db.rollback()
    frappe.destroy()
CCPC_ACCOUNT_DIAGNOSTIC_PY
