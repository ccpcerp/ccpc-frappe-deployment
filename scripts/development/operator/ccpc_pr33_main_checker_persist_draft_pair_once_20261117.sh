#!/usr/bin/env bash
# One-time FIRST PERSISTENT Draft CCPC SI + Draft Ricor PI approval in MAIN DEV.
# Owner approved progression and CONFIRMED real Finance audit checker identity.
# No invoice submit, GL/SLE posting, role grants, migration, service restart or PROD.
# Runs exact controller once; ONLY one explicit commit after all in-transaction checks.
# Stops and NEVER retries on any exception (including post-commit uncertainty).
# Common outbound API monkeypatches are NOT complete OS network isolation.
set -euo pipefail
umask 077

stop() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
[[ "$(hostname -s)" == "ccpcerpserver" ]] || stop 'not original DEV host'
[[ "$(id -un)" == "gani" ]] || stop 'operator gani required'
[[ "${CCPC_APPROVE_PR33_PERSIST_DRAFT_PAIR:-}" == "YES" ]] || stop 'persistent Draft pair execution not enabled'
[[ "${CCPC_CONFIRMED_FINANCE_CHECKER:-}" == "finance_controller@ccpc.com" ]] || stop 'exact owner-nominated Finance Checker not enabled'
[[ "$(id -u)" -ne 0 ]] || stop 'normal nonroot operator required'

NAS='/mnt/erpnext_backups'
RECOVERY='ccpc-development-pr33-main-precommit-20261117T044035Z-591a9f7e2b035cae'
SOURCE='development.localhost-20261117T043152Z-1582f342f870'
actual_mount="$(findmnt -rn -M "$NAS" -o SOURCE,FSTYPE)"
[[ "$actual_mount" == '//192.168.50.132/erpnext_backups cifs' ]] || stop 'unexpected Synology mount'
[[ -d "$NAS/$RECOVERY/$SOURCE" && ! -L "$NAS/$RECOVERY" &&
   -f "$NAS/$RECOVERY/SHA256SUMS" && ! -L "$NAS/$RECOVERY/SHA256SUMS" &&
   -f "$NAS/$RECOVERY/$SOURCE/SHA256SUMS" && ! -L "$NAS/$RECOVERY/$SOURCE/SHA256SUMS" ]] ||
   stop 'exact fresh off-host MAIN recovery point missing'
# The new NAS set contains exactly one named MAIN snapshot and a global manifest.
[[ "$(find "$NAS/$RECOVERY" -mindepth 1 -maxdepth 1 | wc -l)" == "2" ]] ||
   stop 'unexpected off-host recovery root contents'
[[ "$(wc -l < "$NAS/$RECOVERY/SHA256SUMS")" == "4" ]] || stop 'unexpected off-host manifest line count'
[[ "$(wc -l < "$NAS/$RECOVERY/$SOURCE/SHA256SUMS")" == "4" ]] || stop 'unexpected source manifest line count'
(
  cd "$NAS/$RECOVERY"
  sha256sum --check --status SHA256SUMS
) || stop 'off-host four-part SHA256 verification failed'
(
  cd "$NAS/$RECOVERY/$SOURCE"
  sha256sum --check --status SHA256SUMS
) || stop 'nested off-host SHA256 verification failed'
printf 'PINNED_FRESH_MAIN_OFF_HOST_RECOVERY_SHA256_4_OF_4=PASS\n'

DEV='frappe_docker_devcontainer-frappe-1'
sudo -v || stop 'sudo operator authentication failed'
[[ "$(sudo -n docker inspect --format '{{.State.Running}}' "$DEV")" == 'true' ]] || stop 'DEV container stopped'
[[ "$(sudo -n docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$DEV")" == 'frappe_docker_devcontainer' ]] || stop 'wrong Docker project'

# A private one-shot marker is created before any persistent invoice write could occur.
# Never automatically delete it to make a second run possible.
RUN_MARKER="$HOME/.ccpc-pr33-main-persist-draft-pair-once-20261117"
mkdir "$RUN_MARKER" || stop 'one-shot marker already exists; do not retry'

sudo -n docker exec -i --user frappe "$DEV" \
  bash -c 'cd /workspace/development/frappe-bench/sites && exec /workspace/development/frappe-bench/env/bin/python -' <<'CCPC_DIAGNOSTIC_PY'
"""ONE guarded persistent Draft pair; no invoice submit or other financial writes."""
import re
import subprocess
import sys
import traceback
import smtplib
import inspect
from contextlib import ExitStack
from unittest.mock import patch
from pathlib import Path

import requests

import frappe
from frappe.utils import flt, getdate, today

APP = "/workspace/development/frappe-bench/apps/ccpcerp"
SHA = "25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87"
SITE = "development.localhost"
ISSUER = "Cagayan Corn Products Corporation"
BUYER = "Ricor Mills Corporation"
MAKER = "ccpc-billing-preparer-dev@testing.invalid"
CHECKER = "finance_controller@ccpc.com"
COUNT_DOCTYPES = ("Sales Invoice", "Purchase Invoice", "GL Entry", "Stock Ledger Entry")

def must(condition, label):
    if not condition:
        raise RuntimeError("STOP: " + label)

def git(*args):
    return subprocess.check_output(
        ["git", "-C", APP, *args], text=True, timeout=30
    ).strip()

def check_actor(user, roles, *, exact_roles=True):
    actor = frappe.get_doc("User", user)
    must(bool(actor.enabled) and actor.user_type == "System User", "ACTOR_DISABLED")
    actual_roles = {row.role for row in actor.roles}
    must(actual_roles == roles if exact_roles else roles.issubset(actual_roles),
         "ACTOR_ROLE_CHANGED")
    must("Stockroom Personnel" not in actual_roles,
         "ACTOR_FORBIDDEN_STOCKROOM_ROLE")
    grants = frappe.get_all(
        "User Permission", filters={"user": user},
        fields=["allow", "for_value", "apply_to_all_doctypes", "applicable_for"],
        limit_page_length=100,
    )
    company_grants = {
        row.for_value for row in grants
        if row.allow == "Company" and int(row.apply_to_all_doctypes or 0) == 1
        and not row.applicable_for
    }
    must({ISSUER, BUYER}.issubset(company_grants),
         "ACTOR_COMPANY_GRANTS_CHANGED")
    if exact_roles:
        must(len(grants) == 2 and company_grants == {ISSUER, BUYER},
             "MAKER_COMPANY_GRANTS_CHANGED")

connected = False
original_commit = None
original_sql = None
phase = "INITIAL_GUARDS"
completed_checks = False
failure = None
postcheck_ok = False
before_counts = None
original_name = None
new_invoice_names = ()
outbound_stack = ExitStack()
deferred_ui_notification_count = 0
commit_window = False
commit_sql_count = 0
new_transaction_after_commit = 0
commit_sql_completed = False
commit_call_completed = False
rollback_completed = False
try:
    must(git("rev-parse", "HEAD") == SHA, "APP_SHA_CHANGED")
    must(git("rev-parse", "--abbrev-ref", "HEAD") == "HEAD", "APP_NOT_DETACHED")
    must(git("status", "--porcelain=v1", "--untracked-files=all") == "?? AGENTS.md", "APP_WORKTREE_CHANGED")
    protected = Path(APP) / "AGENTS.md"
    must(protected.is_file() and not protected.is_symlink(),
         "PROTECTED_AGENTS_FILE_CHANGED")
    must(git("ls-tree", "-r", "--name-only", "HEAD", "--", "AGENTS.md") == "",
         "PROTECTED_FILE_TRACKED")
    must(git("hash-object",
             "ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py"
             ) == "a9a6e609759e77948d40d31bdbd342f727b208a9",
         "BILLING_CONTROLLER_BLOB_CHANGED")
    must(git("hash-object", "ccpcerp/ccpc_erp/intercompany_billing_authority.py"
             ) == "8de2d6ba2aa0f8995b727157491e236d2a0a8ae2",
         "BILLING_AUTHORITY_BLOB_CHANGED")
    print("PINNED_DEV_APP_AND_WORKTREE=PASS", flush=True)

    # Runtime preflight: only suppress Frappe's known after-commit UI
    # document notifications when the installed implementation matches.
    from frappe.model.document import Document
    notify_src = inspect.getsource(Document.notify_update)
    post_src = inspect.getsource(Document.run_post_save_methods)
    must(
        "self.notify_update()" in post_src
        and "frappe.publish_realtime(" in notify_src
        and "after_commit=True" in notify_src
        and '"doc_update"' in notify_src
        and '"list_update"' in notify_src,
        "INSTALLED_FRAPPE_NOTIFICATION_IMPLEMENTATION_CHANGED",
    )
    print("INSTALLED_FRAPPE_UI_NOTIFICATION_PREFLIGHT=PASS", flush=True)

    frappe.init(site=SITE, sites_path=".")
    frappe.connect()
    connected = True
    must(frappe.local.site == SITE, "WRONG_FRAPPE_SITE")
    frappe.set_user("Administrator")
    frappe.db.sql("START TRANSACTION")
    original_commit = frappe.db.commit

    def block_commit(*args, **kwargs):
        raise RuntimeError("STOP: UNEXPECTED_COMMIT_OUTSIDE_SINGLE_APPROVAL_BOUNDARY")

    # Fail closed if a hook tries a direct frappe.db.commit().
    frappe.db.commit = block_commit
    original_sql = frappe.db.sql

    def sql_guard(query, *args, **kwargs):
        global commit_sql_count, new_transaction_after_commit, commit_sql_completed
        if isinstance(query, str):
            head = query.strip().upper()
            if head == "COMMIT":
                must(commit_window and commit_sql_count == 0,
                     "UNAUTHORIZED_SQL_COMMIT")
                result = original_sql(query, *args, **kwargs)
                commit_sql_count += 1
                commit_sql_completed = True
                return result
            if head == "START TRANSACTION":
                must(commit_window and commit_sql_count == 1
                     and new_transaction_after_commit == 0,
                     "UNAUTHORIZED_SQL_BEGIN")
                result = original_sql(query, *args, **kwargs)
                new_transaction_after_commit += 1
                return result
            if (head.startswith(("COMMIT", "START TRANSACTION", "SET AUTOCOMMIT"))
                    or head in ("BEGIN", "ROLLBACK", "LOCK TABLES", "UNLOCK TABLES")
                    or head.startswith((
                        "BEGIN ", "ROLLBACK ", "LOCK TABLES ",
                        "UNLOCK TABLES ", "ALTER ", "CREATE ", "DROP ",
                        "TRUNCATE ", "RENAME "
                    ))):
                # ROLLBACK TO SAVEPOINT is used by the real controller's
                # compensating path and never performs a persistent commit.
                if not head.startswith("ROLLBACK TO SAVEPOINT "):
                    raise RuntimeError("STOP: FORBIDDEN_SQL_TRANSACTION_CONTROL")
        return original_sql(query, *args, **kwargs)

    frappe.db.sql = sql_guard
    print("SINGLE_COMMIT_AND_SQL_CONTROL_GUARDS=PASS", flush=True)

    # Native Document.notify_update normally emits doc_update/list_update
    # after-commit UI events. For this one operator-controlled persistent
    # draft creation, deliberately suppress these UI notifications (record
    # count) to avoid unrelated outgoing effects; invoice records still commit.
    # Any other realtime event/email/job/HTTP/SMTP attempt fails closed.
    phase = "OUTBOUND_GUARDS"
    def forbidden(label):
        def stop_side_effect(*_args, **_kwargs):
            raise RuntimeError("STOP: BLOCKED_" + label)
        return stop_side_effect

    def guard_realtime(event, *args, **kwargs):
        global deferred_ui_notification_count
        if event not in ("doc_update", "list_update"):
            raise RuntimeError("STOP: BLOCKED_REALTIME_EVENT")
        if kwargs.get("after_commit") is not True:
            raise RuntimeError("STOP: BLOCKED_REALTIME_NOT_DEFERRED")
        deferred_ui_notification_count += 1
        return None

    for name in ("enqueue", "sendmail", "publish_realtime"):
        must(hasattr(frappe, name), "OUTBOUND_GUARD_API_MISSING")

    outbound_stack.enter_context(
        patch.object(frappe, "publish_realtime",
                     side_effect=guard_realtime))
    outbound_stack.enter_context(
        patch.object(frappe, "enqueue", side_effect=forbidden("FRAPPE_ENQUEUE")))
    outbound_stack.enter_context(
        patch.object(frappe, "sendmail", side_effect=forbidden("FRAPPE_SENDMAIL")))
    import frappe.utils.background_jobs as background_jobs
    outbound_stack.enter_context(
        patch.object(background_jobs, "enqueue",
                     side_effect=forbidden("BACKGROUND_JOB_ENQUEUE")))
    outbound_stack.enter_context(
        patch.object(requests.sessions.Session, "request",
                     side_effect=forbidden("HTTP_REQUEST")))
    outbound_stack.enter_context(
        patch.object(smtplib, "SMTP",
                     side_effect=forbidden("SMTP")))
    outbound_stack.enter_context(
        patch.object(smtplib, "SMTP_SSL",
                     side_effect=forbidden("SMTP_SSL")))
    print("SELECTIVE_REALTIME_AND_OUTBOUND_API_GUARDS_ACTIVE=PASS",
          flush=True)
    phase = "ACTOR_AND_SOURCE_GUARDS"

    check_actor(MAKER, {"CCPC Billing Preparer"})
    check_actor(CHECKER, {"Finance Controller"}, exact_roles=False)
    must(CHECKER != "Administrator" and not CHECKER.endswith("@testing.invalid"),
         "SYNTHETIC_OR_ADMIN_CHECKER_FORBIDDEN")
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
    must(frappe.db.count("Intercompany Material Billing Batch",
            {"issuing_company": ISSUER, "requesting_company": BUYER}) == 1,
         "EXPECTED_ONE_TOTAL_ISSUER_BUYER_BATCH")
    original = frappe.get_doc("Intercompany Material Billing Batch", names[0])
    original_name = original.name
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
    source_marker = "Intercompany material billing batch " + original.name
    must(
        frappe.db.count("Sales Invoice", {"remarks": source_marker}) == 0
        and frappe.db.count("Purchase Invoice", {"remarks": source_marker}) == 0,
        "RELATED_INVOICE_PAIR_ALREADY_EXISTS",
    )
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

    # Real controller under owner-confirmed named Finance Checker. Never use
    # Administrator/System Manager permission bypass or SQL status mutation.
    phase = "CHECKER_SESSION"
    frappe.set_user(CHECKER)
    must(frappe.session.user == CHECKER, "CHECKER_SESSION_CHANGED")
    batch = frappe.get_doc("Intercompany Material Billing Batch", original.name)
    batch.check_permission("read")
    batch.check_permission("write")
    print("NAMED_CHECKER_NATIVE_BATCH_PERMISSIONS=PASS", flush=True)
    phase = "CONTROLLER_APPROVE_AND_CREATE"
    result = batch.approve_and_create_invoices()
    phase = "APPROVED_BATCH_POSTCHECK"
    persisted = frappe.get_doc("Intercompany Material Billing Batch", original.name)
    new_invoice_names = (persisted.sales_invoice, persisted.purchase_invoice)
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

    phase = "DRAFT_PAIR_POSTCHECK"
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
    phase = "DRAFT_PAIR_FROZEN_LINE_POSTCHECK"
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
    phase = "DRAFT_PAIR_INTERNAL_PARTIES_POSTCHECK"
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
    print("CROSS_LINKED_DRAFT_SI_PI_IN_TRANSACTION=PASS", flush=True)

    phase = "ROW_COUNT_POSTCHECK"
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

    completed_checks = True
    print("DEFERRED_UI_NOTIFICATIONS_SUPPRESSED_COUNT="
          + str(deferred_ui_notification_count), flush=True)
    print("PRECOMMIT_DRAFT_PAIR_AND_ZERO_GL_SLE=PASS", flush=True)
    # Explicit one and only commit, never available to controller/hooks.
    # A post-commit exception may not undo this SQL COMMIT; never auto-retry.
    phase = "SINGLE_EXPLICIT_COMMIT"
    commit_window = True
    try:
        original_commit()
        commit_call_completed = True
    finally:
        commit_window = False
    must(commit_sql_count == 1 and new_transaction_after_commit == 1,
         "EXPECTED_SINGLE_COMMIT_AND_NEW_TRANSACTION")
    print("SINGLE_EXPLICIT_DB_COMMIT=PASS", flush=True)
except Exception as exc:
    failure = exc
finally:
    if connected:
        # Restore original transaction methods before read-only verification.
        if original_sql is not None:
            frappe.db.sql = original_sql
        if original_commit is not None:
            frappe.db.commit = original_commit
        try:
            # On failure BEFORE COMMIT rollback all transient records. After
            # COMMIT, this only rolls back Frappe's new empty transaction.
            frappe.db.rollback()
            rollback_completed = True
            print("ACTIVE_TRANSACTION_CLEANUP=PASS", flush=True)
            if before_counts is not None and original_name:
                phase_before_postcheck = phase
                phase = "INDEPENDENT_READ_ONLY_PERSISTED_STATE_POSTCHECK"
                frappe.db.sql("START TRANSACTION READ ONLY")
                try:
                    after_counts = {
                        doctype: frappe.db.count(doctype)
                        for doctype in COUNT_DOCTYPES
                    }
                    persisted = frappe.get_doc(
                        "Intercompany Material Billing Batch", original_name)
                    marker = "Intercompany material billing batch " + original_name
                    if commit_sql_completed:
                        must(
                            after_counts["Sales Invoice"] == before_counts["Sales Invoice"] + 1
                            and after_counts["Purchase Invoice"] == before_counts["Purchase Invoice"] + 1
                            and after_counts["GL Entry"] == before_counts["GL Entry"]
                            and after_counts["Stock Ledger Entry"] == before_counts["Stock Ledger Entry"],
                            "PERSISTED_ROW_COUNT_DELTA_INVALID")
                        must(
                            persisted.docstatus == 0 and persisted.status == "Approved"
                            and persisted.approved_by == CHECKER
                            and bool(persisted.approved_on)
                            and (persisted.sales_invoice, persisted.purchase_invoice) == new_invoice_names
                            and all(new_invoice_names),
                            "PERSISTED_APPROVED_BATCH_LINK_INVALID")
                        sales = frappe.get_doc("Sales Invoice", new_invoice_names[0])
                        purchase = frappe.get_doc("Purchase Invoice", new_invoice_names[1])
                        must(sales.docstatus == 0 and purchase.docstatus == 0
                             and sales.company == ISSUER and purchase.company == BUYER
                             and sales.inter_company_invoice_reference == purchase.name
                             and purchase.inter_company_invoice_reference == sales.name
                             and not sales.update_stock and not purchase.update_stock
                             and frappe.db.count("Sales Invoice", {"remarks": marker}) == 1
                             and frappe.db.count("Purchase Invoice", {"remarks": marker}) == 1,
                             "PERSISTED_DRAFT_INVOICE_PAIR_INVALID")
                        postcheck_ok = True
                        print("PERSISTED_DRAFT_PAIR_AND_COUNTS_POSTCHECK=PASS", flush=True)
                        print("PERSISTED_SALES_INVOICE_NAME=" + sales.name, flush=True)
                        print("PERSISTED_PURCHASE_INVOICE_NAME=" + purchase.name, flush=True)
                    else:
                        must(after_counts == before_counts,
                             "ABORT_LEFT_ROW_COUNT_CHANGE")
                        must(persisted.status == "Under Review"
                             and persisted.docstatus == 0
                             and not persisted.approved_by and not persisted.approved_on
                             and not persisted.sales_invoice and not persisted.purchase_invoice
                             and frappe.db.count("Sales Invoice", {"remarks": marker}) == 0
                             and frappe.db.count("Purchase Invoice", {"remarks": marker}) == 0,
                             "ABORT_LEFT_ORIGINAL_BATCH_CHANGED")
                        postcheck_ok = True
                        print("PRECOMMIT_ABORT_PERSISTED_STATE=UNCHANGED", flush=True)
                finally:
                    frappe.db.rollback()
                phase = phase_before_postcheck
        except Exception as post_exc:
            if failure is None:
                failure = post_exc
            print("STOP: TRANSACTION_CLEANUP_OR_POSTCHECK_CLASS="
                  + type(post_exc).__name__, file=sys.stderr, flush=True)
            try:
                frappe.db.rollback()
            except Exception:
                print("STOP: SECOND_ROLLBACK_FAILED", file=sys.stderr, flush=True)
        finally:
            outbound_stack.close()
            frappe.destroy()

print("COMMIT_SQL_COMPLETED=" + str(commit_sql_completed), flush=True)
print("COMMIT_CALL_COMPLETED=" + str(commit_call_completed), flush=True)
print("POSTCOMMIT_READ_ONLY_VALIDATED=" + str(postcheck_ok), flush=True)
print("PRODUCTION_NOT_TARGETED=PASS", flush=True)
if failure is not None:
    print("PERSISTENT_APPROVAL_FAILURE_PHASE=" + phase, flush=True)
    print("PERSISTENT_APPROVAL_FAILURE_CLASS=" + type(failure).__name__, flush=True)
    error_text = str(failure)
    if isinstance(failure, RuntimeError) and re.fullmatch(
        r"STOP: [A-Z][A-Z0-9_]*", error_text
    ):
        print("PERSISTENT_APPROVAL_FAILURE_LABEL=" + error_text[6:], flush=True)
    else:
        frames = traceback.extract_tb(failure.__traceback__)
        safe_frames = [f for f in frames if "/ccpcerp/" in f.filename]
        if safe_frames:
            frame = safe_frames[-1]
            fn = re.sub(r"[^A-Za-z0-9_]", "", frame.name)[:80]
            print("PERSISTENT_APPROVAL_FAILURE_FUNCTION=" + fn, flush=True)
            print("PERSISTENT_APPROVAL_FAILURE_SOURCE_LINE=" + str(frame.lineno),
                  flush=True)
    print("PERSISTENT_APPROVAL_RESULT=STOP_REVIEW_STATE_NO_RETRY", flush=True)
    raise SystemExit(1)
if not completed_checks or not commit_sql_completed or not commit_call_completed or not postcheck_ok:
    print("STOP: INCOMPLETE_PERSISTENT_APPROVAL_VERIFY_STATE_NO_RETRY", file=sys.stderr, flush=True)
    raise SystemExit(1)
print("PERSISTENT_DRAFT_PAIR_APPROVAL=PASS", flush=True)
print("INVOICE_SUBMISSION_NOT_REQUESTED=PASS", flush=True)
print("DO_NOT_REPEAT_THIS_ONE_SHOT=PASS", flush=True)
CCPC_DIAGNOSTIC_PY
