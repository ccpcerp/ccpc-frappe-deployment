# CCPC ERPNext — Source-pinned offline Material Issue reachability regressions

**2026-10-16 | GitHub-only approved test implementation | NO DEVELOPMENT/PRODUCTION runtime contact | POSTING_NO_GO**

## Authorization, exact sources and resulting artifacts

After the [pinned stock-ledger/reposting/GL reachability audit](MATERIAL-ISSUE-STOCK-LEDGER-REPOST-GL-REACHABILITY-AUDIT-2026-10-16.md), the owner approved the specifically proposed **GitHub-only source-pinned static/negative regression suite**. The approval did **not** authorize any Ubuntu staging, live DEVELOPMENT site, Docker, Node/RQ, Redis, SQL, installed-source attestation, application deployment, write-then-rollback transaction, or PRODUCTION operation.

Branch: `ccpcerp/ccpc-frappe-deployment@review/material-issue-first-commit-preparation-2026-10-15`.

- [Immutable-excerpt fixture](../../tests/offline/fixtures/material_issue_reachability_source_pins_20261016.json), Git blob `7ca589594fb9ed818da75476ddbe68b471eef444`, SHA256 `57344e05f07c2f31445e4140ef6bf543cd97660fb34aa2c18db8dd9443f38bb9`; first created `e061238076b308e1d23e9bb69a0ea345c81a4bfa`; multiline function-signature extraction fixed `24ef6e662a2f2d1f453487c55ede8711c2abbe57`.
- [22-case offline Python test suite](../../tests/offline/test_material_issue_source_pinned_reachability_20261016.py), Git blob `b537279f0ace2a2f689f79bc43654bd3d059daac`, SHA256 `ee5a5d91152c93e10c2b4cb4a5f5d7478d6b4ec2bcbe9d4752024afbf09d683c`; initial create commit `291d5375a07cc2496a6b220e4251c40f6ee0903e`; safe `StockController` type-annotation binding fix `5581860fab4e0a43ac6ce39996d4b0fcfb51438e`.
- **Custom app unchanged:** `ccpcerp/ccpcerp@feature/withdrawal-material-issue-safety` verified at `2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6`. Frappe `988e54f3c4c291e2077a83809663f123731abe76` and ERPNext `5af6561f5aa48104559692fb4fd82f2580e8d338` are **GitHub reference source**, *not proven loaded into DEVELOPMENT*.

The fixture stores **exact function text excerpts** retrieved from known GitHub file blobs along with repo, immutable commit, path, function name and starting line. Its complete Git blob is checked before test execution; unexpected local edits fail. The fixture is a *captured review artifact*, not a live upstream-source fetch or code-signature/provenance attestation.

## Actual test execution and verified file identity

```bash
cd /mnt/data/ccpc-reachability
PYTHONDONTWRITEBYTECODE=1 python3 -W error -m unittest discover \
  -s tests/offline \
  -p 'test_material_issue_source_pinned_reachability_20261016.py' -v
```

**Observed: Ran 22 tests — OK. 22/22 PASS (offline).** Earlier initial test run with an otherwise identical fixture failed **5/28** due to a missing `StockController` *type annotation* in a separate local exploratory test harness. The final committed suite was fixed by injecting `StockController: object` only in the isolated namespace; the committed 22-case suite then passed 22/22. This was a test harness defect, **not** a reported ERPNext production defect.

The exact **locally executed fixture bytes** and **locally executed 22-case test file bytes** were independently checked via `git hash-object`-equivalent SHA1 Git blob calculations against GitHub readback, and both matched the blobs listed above. Python unittest used only the stdlib; no Frappe or ERPNext packages were imported and no Docker, Redis, SQL, HTTP or production data were accessed.

## Verified source-derived results and correct limits

| Area | Pin and tested condition | Result supported by isolated execution |
| --- | --- | --- |
| **RIV submission** | Exact `RepostItemValuation.on_submit`; `frappe.in_test` false/true and suppression flags | Ordinary non-test branch does not directly call `repost(doc)`. Test-mode, if not suppressed, **may call it inline**. Not a live worker observation |
| **Repeated consuming SLEs** | Exact `repost_required_for_queue` with mocked `get_all` rows | Distinct item/warehouse pairs do not trigger; repeated pairs with nonempty `stock_queue` can trigger; empty `[]` queues do not |
| **Reposting decision** | Exact `StockController.repost_future_sle_and_gle` | Ordinary no-future/no-repeat returns without RIV creation; future SLE, repeated queue, explicit force or cancellation can select transaction or itemwise RIV record creation. All database reads mocked |
| **RIV creation versus worker** | Exact `create_repost_item_valuation_entry`, `create_item_wise_repost_entries`, `repost` and `StockEntry.on_submit` AST | Creation source calls `submit`, not `repost`; worker source contains explicit `commit` calls; Stock Entry source calls SLE → GL → conditional RIV decision in order. Does NOT prove no internal commit through other paths |
| **Immediate cache effects** | Exact `clear_doctype_cache` with mock cache/transaction callback objects | Immediate cache deletion attempt precedes registering after-COMMIT and after-ROLLBACK callbacks; each callback could invalidate again |
| **Document realtime** | Exact `Document.notify_update` with fake `frappe.publish_realtime` | `doc_update` and `list_update` carry `after_commit=True`; import flag suppresses this branch |
| **Webhook event queue** | Exact `_add_webhook_to_queue` | Two queued synthetic events register the flush callback once when queue persists; no actual webhook/HTTP |
| **CCPC issue entrypoint** | Exact `issue_withdrawal_slip` AST | Explicit `insert` and `submit`; no direct literal `commit` or `rollback` calls in this function. Does NOT inspect transitive hooks or outer request transaction |

## Scope and unresolved release blockers

- **Tested source is limited to eleven selected excerpts.** Executing extracted definitions with mocked globals is stronger than a newly invented copy of business logic, but it is **not** the complete effective Frappe/ERPNext call graph, live database integration, Redis isolation proof, or transaction atomicity proof. In particular, Python `ast` checks do not establish runtime hook registration or application-side effects.
- **Version mismatch STOP:** Frappe/ERPNext references were pinned from GitHub but no installed DEVELOPMENT commits, installed apps, hooks, enabled Notification/Webhook/Server Script records, credentials or process connections were read. A clean test run cannot assert their absence.
- **Pre-COMMIT external effects:** The prior direct source finding for `frappe.clear_cache(doctype="Withdrawal Slip")` remains. Redis cache invalidation may occur before database COMMIT and cannot be undone by SQL rollback. Realtime/pubsub, worker route and RIV worker effects remain only conditionally modeled.
- **SLE/GL and future repost risks:** Physical SLE/GL integration, valuation settings, duplicate/concurrent issues, batch/serial behavior, repost worker scheduling, recovery/rollback remain untested; posting and write-then-rollback stay **NO-GO**.

**Recommended next separate decision:** a **GitHub-only final usefulness/security review of this new source-pinned suite and the remaining installed-DEVELOPMENT effective-hook attestability gap**, to determine whether the next step should be a completely nontransactional DEV build/hook-identification design. No runtime attestation or staging should occur without new specific owner consent and an independently verified genuine-DEVELOPMENT scope; shared Docker daemon and PRODUCTION metadata remain outside authorization.

**End status:** `SOURCE_PINNED_OFFLINE_PASS` (22/22), `INSTALLED_SOURCE_UNVERIFIED`, `EFFECTIVE_HOOKS_UNVERIFIED`, `NODE_ROUTE_UNVERIFIED`, `WORKER_ROUTE_UNVERIFIED`, `DEV_PROD_SEPARATION_UNVERIFIED`, **`POSTING_NO_GO`**. No changes in DEVELOPMENT or PRODUCTION.
