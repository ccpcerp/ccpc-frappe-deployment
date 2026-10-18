# Original Withdrawal Slip issue — B/C implementation-readiness and Accounting approval gate

**Prepared:** 2026-10-18 (Asia/Manila). **State:** TECHNICAL REVIEW / DECISIONS REQUIRED; **NOT** an Accounting mapping approval, code implementation, or ERPNext change authorization. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**

## 1. GitHub-authoritative basis and verified boundary

- [Decision B](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-B-APPROVED-2026-10-18.md): owner-approved **Company + material/item category → approved valid expense Account**, with no unauthorised fallback to generic Stock Adjustment. Exact account identifiers, category precedence and mapping authority are not approved.
- [Decision C](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-C-APPROVED-2026-10-18.md): owner-approved **Company + actual beneficiary Department → approved Cost Center**, explicitly selected if multiple authorized centers apply, no arbitrary Company/requester defaults. Exact center crosswalk, Section selector, effective authority and storage are not approved.
- [B/C mapping approval worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) remains **blank, unsigned and not executable business data**.
- Combined original-issue [app draft PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) on `review/withdrawal-beneficiary-equipment-integration-2026-10-18`, reviewed head `827993e45ae9321e7a936f48f7fc3b17bf842099`: **open/draft/unmerged**. Isolated Actions runs [39100967156](https://github.com/ccpcerp/ccpcerp/actions/runs/39100967156), [39100967202](https://github.com/ccpcerp/ccpcerp/actions/runs/39100967202), [39100967357](https://github.com/ccpcerp/ccpcerp/actions/runs/39100967357) passed 72 mocked + 13 real Accounting, 12 mocked Equipment and 13 real Equipment tests. Those tests validate approved beneficiary A and Equipment D together but use synthetic ERPNext account/center defaults; **they do not validate B/C**.
- Read-only inspection of exact PR #16 source: `ccpcerp/ccpc_erp/withdrawal_slip_stock.py` `_build_material_issue` sets Item/quantity/provenance, Equipment snapshot and beneficiary Department; it currently **does not set** `expense_account` or `cost_center` from an approved CCPC mapping. `validate_withdrawal_slip_stock_entry` checks beneficiary at `before_submit` but **does not verify** an approved B/C account or center. There is **no B/C fail-closed posting safeguard yet**.
- `ccpcerp/ccpc_erp/doctype/withdrawal_slip/withdrawal_slip.json` already has requesting `department` / `section` distinct from beneficiary `work_for_department` / `work_for_section`. `Withdrawal Slip Item` has `item_code` but **no independent approved category snapshot or accounting allocation selection**. The SQL source lock currently reads `equipment` and `work_for_department` but **not** `work_for_section`; this matters **if and only if** Accounting adopts Section-based allocation. It is a future integration requirement, not evidence that the present A+D issue controls have failed.

## 2. Approval register — no value below constitutes an approval

| Required decision | Minimum unambiguous response to document in GitHub | Current state |
| --- | --- | --- |
| B1: Category authority | Identify exact Item Group, Item-specific override or controlled classification; whether parent inheritance, exclusions, precedence and multi-company overrides apply | **NOT APPROVED** |
| B2: Expense Account crosswalk | For **each in-scope Company/category**, exact active, non-group, eligible P&L ERPNext Account identifier; explicitly sign any deliberate generic Stock Adjustment account use | **NOT PROVIDED** |
| C1: Center crosswalk | For **each in-scope Company/beneficiary Department**, exact active leaf Cost Center(s) and their intended accounting use | **NOT PROVIDED** |
| C2: Multi-center choice | One-center auto-match or explicit selector; if several authorized centers, choose whether selection is per Slip, per Section or per line, and where the approved choice is immutably recorded | **NOT APPROVED** |
| C3: Section role | Decide whether `work_for_section` is required in allocation; if so define Company/Department/Section eligibility, stale-source locks and conflict handling | **NOT APPROVED** |
| BC1: Authoritative storage and audit | Approve mapping source/record, change permissions, effective dating, revocation and approval/revision identifiers | **NOT APPROVED** |
| BC2: Exceptions | Name actual Accounting authorization process for mismatched/expired/ambiguous mappings; whether reviewed revisions are allowed, without silent one-off user overrides | **NOT APPROVED** |
| BC3: Cutover and historical handling | In-scope future issuances, treatment of draft pre-cutover documents and missing historical provenance; no unreviewed backfill/reposting | **NOT APPROVED** |

**Approval must be affirmative, versioned and entered in GitHub by an authorized decision maker.** This document neither identifies a live Account/Cost Center nor uses personal notes or a connected spreadsheet. Exact current master verification on DEVELOPMENT requires separately approved target-identity and read-only procedure; GitHub remains authoritative for the resulting reviewed development record.

## 3. Proposed implementation architecture — RECOMMENDATION, NOT AN APPROVED CHOICE

**Preferred for review:** two controlled, company-scoped **mapping authorities** (potentially dedicated CCPC mapping DocTypes) with Accounting-only approval/versioning and effective windows: (i) material category → expense Account and (ii) beneficiary Department + optional approved selector → Cost Center. Explainable keys, explicit active revisions, unambiguous matching and audit links would separate business signoff from incidental ERPNext defaults. This needs an owner/Accounting **schema, permissions and migration decision** before any app code or site action.

**Alternative requiring equivalent explicit approval:** use an individually validated subset of ERPNext Item/Item Group default expense accounts **only when Accounting declares those particular records and precedence authoritative**; use a separate approved Department→Cost Center authority as needed. Neither the presence of `Item.default_expense_account`, `Item Group`, `Company.stock_adjustment_account` nor a Company default Cost Center is approval by itself. Do not choose between these alternatives from model inference.

For either approved design, require these transactional invariants:

1. At controlled linked issue construction, resolve mapping deterministically for actual **issue Company, each Item's approved category and actual beneficiary Department** (Decision A), plus Section/selector only if explicitly approved. Reject missing, overlapping, stale or unsuitable mappings; no arbitrary first-match or global default.
2. Validate exact ERPNext master ownership/status/type before saving selected `Stock Entry Detail.expense_account` and `cost_center`. Preserve both current beneficiary Department and original Equipment provenance. No generic direct GL/Journal Entry to compensate for a bad Stock Entry.
3. At `before_submit`, under reviewed source and mapping concurrency controls, **re-resolve and compare** to each voucher row and any immutable source selection/approval version; detect stale approval, source-field changes and account/center substitution **before stock ledger or GL effects**. Reject direct forged linked vouchers and changes to saved drafts. Consider race protection where the mapping approval itself changes between resolution and submit.
4. If C2 uses Section, update the current Withdrawal Slip source lock and post-lock comparison to include `work_for_section` (and any new selector), including Company/beneficiary validation. **Do not assume current locking is sufficient for future Section-driven allocation.**
5. After successful genuine posting, preserve **actual original posted** expense Account, Cost Center, Department, Equipment source and SLE cost for any later independently approved source-linked Option A Material Receipt; do not recompute from changed masters.
6. Audit appropriate Financial permission boundaries and who can approve a mapping/exception separately from Stockroom issue submission. Mapping edits/revisions must not retroactively rewrite GL or silently change posted provenance.

## 4. Minimum isolated tests to add **after approval**, without CCPC master data

- Positive: two separately authorized synthetic Company/categories → two approved P&L accounts; two beneficiary Departments → independently approved centers; requesting vs beneficiary differs, and multiple Equipment issue rows retain independent source snapshots. Assert real Stock Entry, SLE and GL account, center and beneficiary Department against **approved synthetic mapping records**.
- Negative B: no/overlapping/wrong-company/expired/disabled/group/asset Account; unapproved Stock Adjustment fallback; changed Item category/default; forged or cleared row expense Account; direct source-link bypass and stale approval revision. Confirm **zero submitted stock/GL**.
- Negative C: no/overlapping/cross-company/disabled/group Cost Center; requestor default leakage; multi-center without explicit reviewed selector; forged Section/center, stale `work_for_section` under lock if applicable. Confirm **zero submitted stock/GL**.
- Concurrent/transactional: change mapping between draft and submit, conflicting approvals, two issuers, failed insert/submit rollback, cancellation, retry/idempotency, update-after-submit integrity. Retest all existing PR #16 A+D functions on the **same exact review head** and preserve previous 72 + 13 + 12 + 13 acceptance evidence.
- Later separate Return Option A: original issue actual account/center/Department/equipment attribution and true SLE rate; partial bound stockroom acceptance, distinct verifier/approver, cancellation, valuation mismatch and accounting exception testing. **No material return implementation authorized by this note**.

## 5. Safe next step

Finance/Accounting and the project owner should complete the [B/C worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) **using approved GitHub records and independently authorized current ERPNext master verification**, select B1–BC3 explicitly, and record the approved decision on the reviewed GitHub documentation branch. **Only after that** create a focused app review implementing approved mapping schema/permissions, source fields and fail-closed validation, with disposable real ERPNext v16/MariaDB/GL tests. Separately verify DEVELOPMENT target, Git state and backups before any consented pull/test. PRODUCTION deployment requires new express approval, backups and rollback plan.

**No code, schema, masters, credentials, site, database, role, migration, DEVELOPMENT or PRODUCTION changes are requested or performed by this document.**
