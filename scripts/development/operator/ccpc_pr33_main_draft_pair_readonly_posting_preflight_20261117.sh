#!/usr/bin/env bash
# PR33 MAIN DEVELOPMENT exact Draft SI/PI READ-ONLY accounting preflight.
# Never submit, commit, grant roles, migrate, restart or target PRODUCTION.
set -euo pipefail
umask 077
stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" && "$(id -un)" == "gani" ]] ||
  stop "original DEV host/user required"
[[ "${CCPC_PR33_READ_ONLY_POSTING_PREFLIGHT:-}" == "YES" ]] ||
  stop "read-only preflight flag missing"
[[ "$(id -u)" -ne 0 ]] || stop "normal operator required"
DEV="frappe_docker_devcontainer-frappe-1"
sudo -v || stop "sudo authentication failed"
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == "true" ]] ||
  stop "named DEV container stopped"
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == "frappe_docker_devcontainer" ]] ||
  stop "wrong Docker Compose project"

sudo -n docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench/sites && FRAPPE_STREAM_LOGGING=1 exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_READ_ONLY_PY'
"""No-write MAIN-only first native accounting-posting prerequisites inventory."""
import subprocess
from pathlib import Path
import frappe
from frappe.utils import flt, getdate

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
SHA = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
SITE = "development.localhost"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
CHECKER = "finance_controller@ccpc.com"
SI = "ACC-SINV-2026-00001"
PI = "ACC-PINV-2026-00005"

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def git(*args):
    return subprocess.check_output(
        ["git", "-C", APP, *args], text=True, timeout=30
    ).strip()

connected = False
try:
    must(git("rev-parse", "HEAD") == SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD",
         "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md",
         "PROTECTED_DEV_WORKTREE_CHANGED")
    must((Path(APP) / "AGENTS.md").is_file()
         and not (Path(APP) / "AGENTS.md").is_symlink(), "PROTECTED_FILE_CHANGED")
    print("PINNED_DEVELOPMENT_READ_ONLY_SOURCE=PASS", flush=True)

    frappe.init(site=SITE, sites_path=".")
    frappe.connect()
    connected = True
    must(frappe.local.site == SITE, "UNEXPECTED_CONNECTED_SITE")
    frappe.db.sql("START TRANSACTION READ ONLY")

    names = frappe.get_all(
        "Intercompany Material Billing Batch",
        filters={"issuing_company": ISSUER, "requesting_company": BUYER},
        pluck="name", limit_page_length=3
    )
    must(len(names) == 1, "BATCH_COUNT_CHANGED")
    batch = frappe.get_doc("Intercompany Material Billing Batch", names[0])
    must(batch.docstatus == 0 and batch.status == "Approved"
         and batch.approved_by == CHECKER and bool(batch.approved_on)
         and batch.sales_invoice == SI and batch.purchase_invoice == PI,
         "PERSISTED_APPROVAL_CHANGED")
    sales = frappe.get_doc("Sales Invoice", SI)
    purchase = frappe.get_doc("Purchase Invoice", PI)
    must(sales.docstatus == purchase.docstatus == 0, "DRAFT_STATUS_CHANGED")
    must(sales.company == ISSUER and purchase.company == BUYER,
         "COMPANY_CHANGED")
    must(sales.inter_company_invoice_reference == PI
         and purchase.inter_company_invoice_reference == SI,
         "RECIPROCAL_LINK_CHANGED")
    must(not sales.update_stock and not purchase.update_stock
         and not sales.get("taxes") and not purchase.get("taxes"),
         "TAX_OR_STOCK_FLAGS_CHANGED")
    must(len(sales.items) == len(purchase.items) == len(batch.items) == 1,
         "FROZEN_LINE_COUNT_CHANGED")
    frozen = batch.items[0]
    for row in (sales.items[0], purchase.items[0]):
        must(
            row.item_code == frozen.item_code
            and abs(flt(row.qty) - flt(frozen.quantity)) <= 0.000001
            and abs(flt(row.rate) - flt(frozen.frozen_basic_rate)) <= 0.000001,
            "FROZEN_SOURCE_LINE_CHANGED",
        )
    must(getdate(sales.posting_date) == getdate(batch.period_end)
         and getdate(purchase.posting_date) == getdate(batch.period_end),
         "POSTING_DATE_CHANGED")
    for doc in (sales, purchase):
        must(abs(flt(doc.grand_total) - flt(batch.total_amount)) <= 0.01,
             "BILLING_AMOUNT_CHANGED")
        must(
            not flt(doc.get("discount_amount"))
            and not flt(doc.get("rounding_adjustment"))
            and not flt(doc.get("write_off_amount"))
            and not doc.get("is_return")
            and not doc.get("is_paid")
            and not doc.get("is_pos")
            and not doc.get("apply_tds"),
            "NONSTANDARD_POSTING_AMOUNTS_OR_FLAGS",
        )
        for ledger_type in ("GL Entry", "Stock Ledger Entry"):
            must(
                frappe.db.count(ledger_type, {
                    "voucher_type": doc.doctype,
                    "voucher_no": doc.name,
                }) == 0,
                "INVOICE_ALREADY_HAS_LEDGER_OR_STOCK_ROWS",
            )
    print("EXACT_PERSISTED_DRAFT_PAIR_NO_LEDGER=PASS", flush=True)

    company_info = {}
    for company in (ISSUER, BUYER):
        row = frappe.db.get_value(
            "Company", company, ["abbr", "default_currency", "cost_center"],
            as_dict=True,
        )
        must(row and row.abbr and row.default_currency and row.cost_center,
             "COMPANY_ACCOUNTING_DEFAULT_MISSING")
        company_info[company] = row

    must(
        sales.currency == company_info[ISSUER].default_currency
        and purchase.currency == company_info[BUYER].default_currency
        and sales.currency == purchase.currency,
        "CURRENCY_MISMATCH",
    )
    must(
        abs(flt(sales.conversion_rate) - 1) <= 0.000001
        and abs(flt(purchase.conversion_rate) - 1) <= 0.000001,
        "FX_CONVERSION_RATE_NOT_ONE",
    )
    must(
        abs(flt(sales.base_grand_total) - flt(sales.grand_total)) <= 0.01
        and abs(flt(purchase.base_grand_total) - flt(purchase.grand_total)) <= 0.01,
        "BASE_AMOUNT_MISMATCH",
    )

    issuer_abbr = company_info[ISSUER].abbr
    buyer_abbr = company_info[BUYER].abbr
    accounts = (
        (sales.debit_to, f"1312 - Intercompany Receivable - {issuer_abbr}",
         ISSUER, "Asset", "Receivable"),
        (sales.items[0].income_account,
         f"6050 - Intercompany Material Charges - {issuer_abbr}",
         ISSUER, "Income", None),
        (purchase.items[0].expense_account,
         f"5150 - Intercompany Materials Expense - {buyer_abbr}",
         BUYER, "Expense", None),
        (purchase.credit_to, f"2121 - Intercompany Payable - {buyer_abbr}",
         BUYER, "Liability", "Payable"),
    )
    for selected, expected, company, root, account_type in accounts:
        must(selected == expected, "INVOICE_ACCOUNT_MISMATCH")
        info = frappe.db.get_value(
            "Account", expected,
            ["company", "root_type", "account_type", "is_group", "disabled"],
            as_dict=True,
        )
        must(info and info.company == company and info.root_type == root
             and not info.is_group and not info.disabled
             and (not account_type or info.account_type == account_type),
             "INVOICE_LEDGER_ACCOUNT_INVALID")
    must(
        sales.items[0].cost_center == company_info[ISSUER].cost_center
        and purchase.items[0].cost_center == company_info[BUYER].cost_center,
        "COST_CENTER_CHANGED",
    )
    print("DRAFT_ACCOUNT_CURRENCY_COST_CENTER_MAPPING=PASS", flush=True)

    frappe.set_user(CHECKER)
    si_submit = bool(frappe.has_permission(
        doctype="Sales Invoice", ptype="submit", doc=sales, user=CHECKER
    ))
    pi_submit = bool(frappe.has_permission(
        doctype="Purchase Invoice", ptype="submit", doc=purchase, user=CHECKER
    ))
    print("CHECKER_SI_NATIVE_SUBMIT_PERMISSION=" + ("YES" if si_submit else "NO"), flush=True)
    print("CHECKER_PI_NATIVE_SUBMIT_PERMISSION=" + ("YES" if pi_submit else "NO"), flush=True)
    print("POSTING_COMPANY_CURRENCY=" + str(sales.currency), flush=True)
    print("POSTING_AMOUNT_EACH_SIDE=" + str(round(flt(batch.total_amount), 2)), flush=True)
    print("POSTING_DATE=" + str(batch.period_end), flush=True)
    print("EXPECTED_CCPC_DR=" + accounts[0][0], flush=True)
    print("EXPECTED_CCPC_CR=" + accounts[1][0], flush=True)
    print("EXPECTED_RICOR_DR=" + accounts[2][0], flush=True)
    print("EXPECTED_RICOR_CR=" + accounts[3][0], flush=True)
    print("EXPECTED_FOUR_LINE_JOURNAL_PATTERN=SOURCE_DERIVED_NOT_POSTED", flush=True)
    print("FISCAL_PERIOD_AND_OTHER_NATIVE_SUBMIT_HOOKS=NOT_YET_VALIDATED", flush=True)
    print("READ_ONLY_POSTING_PREFLIGHT=PASS", flush=True)
finally:
    if connected:
        frappe.db.rollback()
    frappe.destroy()
CCPC_READ_ONLY_PY
