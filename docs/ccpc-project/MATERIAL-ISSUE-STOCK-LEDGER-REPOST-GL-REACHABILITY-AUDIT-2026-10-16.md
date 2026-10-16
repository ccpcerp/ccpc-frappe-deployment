# CCPC ERPNext — Material Issue Stock Ledger / Repost / GL Reachability Audit

**2026-10-16 | GitHub-only pinned-source audit | No executable changes, no test execution, no DEVELOPMENT/PRODUCTION runtime access | POSTING_NO_GO**

## Authorization and authoritative checkpoints

The owner replied **“Approved, Continue”** after the [E0/E1 inventory and 25-case mocked-ordering checkpoint](MATERIAL-ISSUE-PRECOMMIT-E0-SOURCE-EFFECT-INVENTORY-2026-10-16.md), authorizing the proposed **GitHub-only reachability audit** of Stock Entry `on_submit`, stock ledger, valuation reposting and GL posting. This approval covers reading pinned source and updating GitHub audit/handoff documentation. It does **not** authorize further code changes, Docker/server inspection, loaded-DEVELOPMENT build attestation, a fresh offline test suite, script staging or execution, live Node/RQ/Redis, any database write or rollback-only trial, or PRODUCTION access.

Verified start branch heads:
- `ccpcerp/ccpc-frappe-deployment@review/material-issue-first-commit-preparation-2026-10-15` `ca72a0dabdf5bbd3b1902f8088ed0617e9d42791` (prior E0/E1)
- `ccpcerp/ccpc-frappe-deployment@docs/ccpc-checkpoint-2026-10-10` `12746e2109d333d2a9adcc1b30083cedce888990` (rolling handoff)
- `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6` (unchanged throughout this audit)
- Source **reference**, `frappe/erpnext@5af6561f5aa48104559692fb4fd82f2580e8d338` (v16.51.1 branch head at check time). This **is not attested as installed in DEVELOPMENT**.
- Source **reference**, `frappe/frappe@988e54f3c4c291e2077a83809663f123731abe76`, **not attested as installed in DEVELOPMENT**.

## Pin registry and scope

| Source | Verified Git blob | Audit use |
| --- | --- | --- |
| [CCPC stock issue](https://github.com/ccpcerp/ccpcerp/blob/2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6/ccpcerp/ccpc_erp/withdrawal_slip_stock.py) | `771d27781f8d933fd243415e8286976fbdd1a861` | `_build_material_issue`, `issue_withdrawal_slip`, slip cache-clearing hook |
| [CCPC hooks](https://github.com/ccpcerp/ccpcerp/blob/2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6/ccpcerp/hooks.py) | `023dc7b04b8f4fa019654c074124bd03f3b82489` | Custom Stock Entry `validate`, `before_submit`, `on_submit` |
| [ERPNext Stock Entry](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/stock/doctype/stock_entry/stock_entry.py) | `dfe6aeef0f76fbf76af8caeb787a321c773f2bbf` | Core `on_submit` (619–653), source/target SLE (2407+), GL (2580+) |
| [StockController](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/controllers/stock_controller.py) | `3d77e45058d47a264009c2a3d2b35c633ce9e363` | `make_gl_entries` (333+), `repost_future_sle_and_gle` (1964+), `repost_required_for_queue` (2356+), repost constructors (2584+) |
| [ERPNext stock ledger](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/stock/stock_ledger.py) | `2d69427a9b5da086d40c47f458a269a3b98c44c9` | `make_sl_entries` (109+), `repost_current_voucher` (177+), `repost_future_sle` (270+), repost checkpoint commits (418, 921) |
| [Stock Ledger Entry](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.py) | `53143294669ba2c56e33b5f1ad45e77e5b9fa5c2` | `on_submit` (265+) conditional serial/batch work |
| [Bin](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/stock/doctype/bin/bin.py) | `f31221d8dbfd06dc5b9e424600aaa0b79dbb22e5` | `update_qty` (263+) DB updates |
| [Repost Item Valuation](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/stock/doctype/repost_item_valuation/repost_item_valuation.py) | `66a0f707504ae6958868795ae393c1adcd35765f` | `on_submit` (267+) gated by `frappe.in_test`; `repost` (408+) explicit commits; scheduler/worker (650–755) |
| [ERPNext general ledger](https://github.com/frappe/erpnext/blob/5af6561f5aa48104559692fb4fd82f2580e8d338/erpnext/accounts/general_ledger.py) | `a4018f50f61a375438c8702690112e14a474870a` | `make_gl_entries` (29+), `save_entries` (408+), `make_entry` (426+) |
| [Frappe Document](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/model/document.py) | `e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a` | `run_method` (1245+), notification/event hooks; post-save (1445+); `notify_update` (1493+) |
| [Frappe webhooks](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/integrations/doctype/webhook/__init__.py) | `804560319ffb16c60798d807064a02defb336443` | Conditional event scheduling via `after_commit` |
| [Frappe Notifications](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/email/doctype/notification/notification.py) | `df575e826ef16b96ea8aa379a2227d900b8e8a50` | `evaluate_alert` (826+) may call `alert.send`; actual enabled alerts and channel configuration unknown |
| [Frappe Server Script dispatch](https://github.com/frappe/frappe/blob/988e54f3c4c291e2077a83809663f123731abe76/frappe/core/doctype/server_script/server_script_utils.py) | `292a70c93f3fe2a39bcd56d5abe4b7397a5eebe2` | Configured document-event scripts conditional |
| Previous [E0/E1 evidence map](MATERIAL-ISSUE-PRECOMMIT-E0-SOURCE-EFFECT-INVENTORY-2026-10-16.md) | `6be92dcae1122178cf69a1ead07f9ec220e83db2` | Actual pre-COMMIT CCPC `frappe.clear_cache` and 25 synthetic tests |

## Reachability graph — source-derived, not executed

```text
CCPC issue_withdrawal_slip [after permissions/locking/duplicate checks]
  -> _build_material_issue (Material Issue; each slip row appended, source warehouse)
  -> Stock Entry.insert() -> Stock Entry.submit()
     -> Frappe Document post-save: on_update + on_submit + on_change;
        installed hooks, notifications, webhooks, scripts (runtime set UNKNOWN)
     -> ERPNext Stock Entry.on_submit
        -> update_stock_ledger()
           -> make_sl_entries(source legs, then target legs) [quantity/validation conditional]
           -> SLE.submit, current-voucher valuation, Bin DB updates
           -> Stock Ledger Entry serial/batch callback when applicable
        -> make_gl_entries()
           -> only when perpetual inventory / provisional accounting /
              asset requirements activate the relevant GL path
           -> general_ledger.make_gl_entries -> GL Entry.submit (if gl_map permits)
        -> repost_future_sle_and_gle()
           -> ONLY when future_sle_exists(locking read) OR
              repost_required_for_queue (repeat item/warehouse + nonempty FIFO/LIFO queue)
           -> create one or more Repost Item Valuation documents -> submit
              -> Repost Item Valuation.on_submit:
                   ordinary non-test: RETURN without executing repost()
                   frappe.in_test and flags permit: repost() INLINE
              -> separate scheduler/worker may execute queued repost LATER
     -> CCPC on_submit sync_withdrawal_slip_issue_status
        -> transactional slip/child DB updates
        -> frappe.clear_cache(doctype="Withdrawal Slip")
           -> immediate client/Redis cache invalidation ATTEMPTS
           -> after-COMMIT and after-ROLLBACK invalidation callbacks
     -> Frappe Document.notify_update: after_commit=True doc/list realtime
     -> configured notifications/webhooks/server scripts: effects depend on live config
```

The diagram is a **bounded architectural tracing aid**, not a guarantee of precise order between every ERPNext and installed hook. Frappe `Document.run_post_save_methods` runs the controller method and registered hooks through `run_method`. Conditional branches and installed extensions can change which effects occur and whether processing aborts.

## Reachability findings and confidence

| Potential effect | Reachability from CCPC Material Issue in cited source | Commit / external-side-effect interpretation | Remaining proof gap |
| --- | --- | --- | --- |
| Stock Entry insert/submit | **Direct**, after issue guards | DB and controller hooks run before normal request completion; no explicit `frappe.db.commit()` in CCPC `issue_withdrawal_slip`. | Outer transaction/version and all installed hooks not attested |
| SLE + Bin updates | **Direct, conditional on stock legs/items** (`stock_entry.py:2407+`; `stock_ledger.py:109+`; `bin.py:263+`) | Creates/submits Stock Ledger Entries and updates Bin quantities; no explicit immediate COMMIT in the inspected current-voucher `make_sl_entries` path. | Additional child hooks, serial/batch, valuation side effects and actual item conditions |
| GL entries | **Conditional** (`stock_controller.py:333+`; `general_ledger.py:29+,408+,426+`) | `make_gl_entries` is called by `Stock Entry.on_submit`; actual GL Entry submissions require inventory/perpetual-accounting or other accounting branches and a valid GL map. The inspected direct GL functions do not show an explicit `db.commit()`. | Chart of accounts, settings, stock value, actual GL map and additional GL hooks |
| Future-stock/queue repost record creation | **Conditionally reachable** (`stock_controller.py:1964+,2356+,2584+,2605+`) | On ordinary submitted `docstatus=1`, no forced repost; selection depends on future SLE from locking read or repeated consuming SLE item+warehouse with nonempty stock queue. CCPC builder iterates slip rows and does not coalesce duplicate item rows, so the repeated-row branch is **plausibly reachable**, not verified with live data. May create/submit Repost Item Valuation records **in the request transaction**. | Actual SLE data, valuation method, repost settings, execution flags, concurrent state and doc hooks |
| Full valuation repost internal commits `stock_ledger.py:418,921` | **NOT shown reachable in ordinary inline Stock Entry submission under non-test semantics.** `RIV.on_submit` returns early when `not frappe.in_test`. | Explicit commits sit in `repost_future_sle` checkpoint/update paths with a `repost_doc`, associated with **later scheduled/worker repost processing**. In `repost_current_voucher`, `update_entries_after` is called with `sle_id` and no repost document, using the *current-voucher* build path rather than `update_data_in_repost`. | No proof of absence via other installed hooks, nested helpers, or nonstandard/test execution |
| Full RIV worker `repost(doc)` commits and progress / failure notification | **Separate worker/manual entrypoint; no direct call shown from normal non-test `RIV.on_submit`.** Exception for `frappe.in_test` with flags permitting synchronous repost. | `repost()` contains explicit `db.commit` outside test mode, failure-handling rollback, final commit, progress realtime, and possible notification. These are real **worker-path** capabilities; not evidence that ordinary CCPC request issues them before its COMMIT. | Actual scheduler/queue startup, tested framework mode, installed hooks and process routing |
| Frappe document update notifications | **Framework-direct post-save mechanism** (`document.py:1445–1513`) | `notify_update` publishes `doc_update` / `list_update` with `after_commit=True` by default, unless flags disable/suppress. These are **registered for after-COMMIT**, not immediate in the cited path. | Other event type/hook emission and live flags |
| Configured Frappe webhooks | **Conditional framework dispatch**, config not established | `run_webhooks` queues webhook work in an **after-COMMIT** callback (`webhook/__init__.py:33–115`); condition evaluation occurs on event dispatch. Not evidence of an actual enabled webhook. | Effective DEV Webhook records/conditions, other custom dispatch and downstream behavior |
| Configured Notification alerts | **Conditional framework dispatch**, config not established | `Document.run_notifications` can call `evaluate_alert`, whose event-path invokes `alert.send`. Do **not** assume all sends are after-COMMIT; channel-dependent effects and templates require independent inspection. | Enabled Notification records, channel handlers, side effects and actual installed build |
| Configured Server Scripts / additional hooks | **Conditional framework dispatch** via `Document.run_method` and server-script map; actual registration unknown | Arbitrary extensions may have effects unrelated to the audited CCPC hook list. Never infer negative evidence from absence of those extensions in this repo alone. | Effective installed apps, runtime hooks, enabled Server Scripts, customizations; NO DEV query authorized |
| CCPC Withdrawal Slip cache clear | **Direct** (`withdrawal_slip_stock.py:381`; Frappe cache manager) | Immediate cache/Redis invalidation attempts **before** after-COMMIT/after-ROLLBACK callback registrations. Full SQL rollback does not undo already completed external cache effects. | Actual shared Redis instance/other subscribers, installed version and impact |

## Reposting proof: avoid conflating two paths

1. **Current voucher**: `StockEntry.update_stock_ledger` calls `stock_ledger.make_sl_entries`. For a stock-consuming leg, `repost_current_voucher` invokes `update_entries_after` with a nonempty `sle_id`, which selects `build()`'s **current-entry branch**. The code there does **not** call `update_data_in_repost` or its conditional `frappe.db.commit()`.
2. **Future valuation adjustment**: after current SLE/GL work, `StockEntry.on_submit` calls `repost_future_sle_and_gle`. A conditionally created RIV doc's `on_submit` exits if `frappe.in_test` is false. Therefore the **worker repost and its explicit checkpoint COMMITs are not on the ordinary direct call path shown here**. Their later execution can affect already committed stock/GL and requires separate recovery/concurrency review.
3. **Test mode matters**: when `frappe.in_test` is true and suppression flags are off, RIV `on_submit` calls `repost(doc)` inline; the internal explicit commit statements reviewed are generally conditional on `not frappe.in_test`, but other effects, worker callbacks and test-mode realtime behavior still merit exact-source review. **Do not infer that a write-then-rollback trial in DEVELOPMENT is harmless merely by setting a test flag.**

## Material Issue safety and next controlled gate

- **Supported:** No explicit internal `frappe.db.commit()` was found on the inspected **ordinary** CCPC → StockEntry → current SLE + conditional GL + RIV-document creation call chain in the pinned **reference** sources. This is a **positive bounded finding**, not a universal no-commit proof.
- **Still risky:** Proven immediate CCPC/Frappe cache invalidation; unverified installed Notification/Server Script and other hooks; serial/batch/valuation helper transitive effects; conditional repost document creation; future worker reposting; physical Redis and DEV/PROD separation; installed source and active stock/GL settings.
- **No execution evidence:** Source review only. **No new tests were run in this reachability-audit turn.** The historical 25/25 E1 tests remain **reduced synthetic models** and must not be presented as actual framework tests or as fresh validation of this audit.
- **Current evidence status:** `SOURCE_REACHABILITY_PARTIAL`; `INSTALLED_HOOKS_UNVERIFIED`; `RIV_ASYNC_PATH_CONDITIONAL`; `WORKER_ROUTE_UNVERIFIED`; `NODE_ROUTE_UNVERIFIED`; `REDIS_INSTANCE_IDENTITY_UNVERIFIED`; `DEV_PROD_SEPARATION_UNVERIFIED`; **`POSTING_NO_GO`**.

**Recommended single next authorization step:** a focused **GitHub-only exact-source/negative-path offline regression suite** for the distinction between current SLE processing and conditional RIV creation, test-mode `repost(doc)` gate, framework notification/webhook timing and CCPC cache clearing. It must use pinned source assertions or truly isolated extraction (rather than inventing a test event model), fail closed on source drift, and never import the live ERPNext/Frappe apps. A subsequent independently scoped **DEVELOPMENT-only effective-hook and installed-commit attestation design** would still be necessary for any real transaction test; shared Docker/PRODUCTION reads remain unapproved.

**Release state:** No approval for DEVELOPMENT write-then-rollback, permanent Stock Entry/SLE/GL, PROD data access or PROD deployment. Production remains untouched. **POSTING_NO_GO.**
