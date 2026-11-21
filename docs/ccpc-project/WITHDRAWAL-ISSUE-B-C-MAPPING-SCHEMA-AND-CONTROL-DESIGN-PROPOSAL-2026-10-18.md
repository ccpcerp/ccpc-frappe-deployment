# CCPC Withdrawal Slip B/C — controlled versioned mapping schema and control design (for review)

**Prepared:** 2026-10-18 (Asia/Manila). **Updated review status:** **Four-DocType scope/revision structure and exact leaf Item Group/no inheritance were subsequently OWNER APPROVED for an inert GitHub code-review implementation**, with positive, validated C revision selection required for multi-Center cases. See [new exact owner decision](WITHDRAWAL-ISSUE-B-C-SCHEMA-DESIGN-OWNER-APPROVAL-2026-10-18.md) and [draft app PR #17](https://github.com/ccpcerp/ccpcerp/pull/17). The original [controlled/versioned architecture](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md) remains in effect. **Detailed effective-time semantics, specific selection UI/granularity, Finance permissions, exceptions, real crosswalk rows and posting implementation remain NOT APPROVED.**

**Release boundary:** **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP**. This is documentation on the GitHub draft documentation branch, not application code, site schema, new permissions or financial transactions.

## 1. Verified app baseline and target integration

- [Combined app draft PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) `review/withdrawal-beneficiary-equipment-integration-2026-10-18` at reviewed head `827993e45ae9321e7a936f48f7fc3b17bf842099` has **owner-approved Decision A beneficiary Department and Decision D immutable Equipment snapshots**, with successful isolated mocks and genuine ERPNext v16/MariaDB/GL regression tests. It does **not** implement B/C.
- Exact app `ccpcerp/ccpc_erp/withdrawal_slip_stock.py`: `_lock_withdrawal_slip` and both post-lock comparisons protect `equipment`, `work_for_department`, Company, warehouse, status, issuer controls; `_build_material_issue` constructs per-Item Stock Entry Details and applies beneficiary, **but not approved expense Account or Cost Center**. `validate_withdrawal_slip_stock_entry` checks provenance, quantity, Equipment snapshot and beneficiary before submission, but not B/C mapping. Apply new validation to the controlled linked original **Material Issue** scope only; do not relabel an unrelated Stock Entry as approved.
- `Withdrawal Slip` has **requester** `department` / `section` and separate **beneficiary** `work_for_department` / `work_for_section`; `Withdrawal Slip Item` currently has `item_code` without a category or mapping revision. `CCPC Section` already links its Company and Department and has a `disabled` flag. **Neither the Section field nor Equipment's automatically supplied Section is automatically an approved Cost Center selector.**
- [B/C signoff worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) still has unapproved, blank Company/category Account and Company/beneficiary Department Cost Center rows. No master values may be inferred from fixture defaults.

## 2. Owner-approved FOUR logical DocType design — inert GitHub draft review only

Recommend two **stable scopes/keys** plus two **separately immutable revision records**, all private CCPC doctypes with server-enforced uniqueness and audit. Names and fieldnames in the following table are **proposed**, not existing records or approved schema.

| Proposed DocType | Suggested fields | Purpose |
| --- | --- | --- |
| `CCPC Expense Mapping Scope` | Company (Link); category authority (enum); category key (Link/Data dependent on approved authority); unique normalized scope key; current/revision display only | One lockable identity for Company + category authority/key. Does **not** directly store a mutable expense account as approved truth. |
| `CCPC Expense Mapping Revision` | Parent Scope (Link); revision number/ID; Account (Link); approved state; effective_from, effective_until; approved_by/at, approval reference; superseded/revoked reference + reason; created_by | Append-only approved B decisions and exact Account to select within signed validity window. |
| `CCPC Center Mapping Scope` | Company (Link); actual beneficiary Department (Link); selector mode and normalized selector key **only if approved**; unique normalized scope key | One lockable identity for Company + beneficiary Department + authorized selection scope. |
| `CCPC Center Mapping Revision` | Parent Scope (Link); revision number/ID; Cost Center (Link); approved state; effective_from, effective_until; approved_by/at, approval reference; superseded/revoked reference + reason; created_by | Append-only approved C decisions and exact Cost Center, with immutable history for audit and later original-source returns. |

**Important model decision:** Use distinct immutable approved revision records rather than overwrite the Account/Center field on an approved mapping. Approval/revocation is an auditable transaction, **not** a user's edit to posted history. A separate status or revocation *event* record may be preferable to mutating an approved revision; evaluate this in schema review. The old revision must remain inspectable even if inactive, and never change historical Stock Entry/GL allocations.

**Candidate key integrity:** database unique constraints for each normalized Scope key and `(scope, revision_no)`; when selector is unused, store a **defined non-null sentinel** rather than allowing NULLs to evade uniqueness. Reject duplicate scope or duplicate revision at the database as well as application layer. **Effective-interval overlaps cannot reliably be excluded by ordinary MariaDB UNIQUE indexes alone**; use scope-row locking and transaction-time overlap validation plus tests. Any actual SQL/DB index and naming-series design is subject to a separate reviewed migration and Frappe version check.

## 3. Detailed rules — approved items distinguished from open decisions

| Gate | Proposed simplest safe rule | Why it is not yet authoritative |
| --- | --- | --- |
| **B1 material category** | **OWNER APPROVED for reviewed initial design:** exact leaf **Item Group**, no parent inheritance, no Item-specific silent override. Still reject missing/unapproved category. | No actual Company/Item Group→Account crosswalk is yet signed or installed. |
| **B2 account** | Each Company + approved category maps to precisely one explicitly approved active, non-group eligible P&L Expense Account for the relevant window; never auto-use Company Stock Adjustment. | Actual per-Company/category Account identifiers and allowed exceptions are **not supplied**. |
| **C1 center** | Each Company + beneficiary Department has one active approved leaf Cost Center by default; no requester or Company fallback. | Actual Department→Center rows and multi-center structures are **not supplied**. |
| **C2/C3 multiple centers** | **OWNER APPROVED safety rule:** when several Centers are authorized, require positive, validated selection of the applicable **approved C revision**, never the first/default. | Exact selection source (Slip/row), Section eligibility, authority and audited field **remain unapproved**; draft PR #17 rejects active explicit-selector mode. |
| **Approval workflow** | Proposed draft → submit for independent Accounting review → approved immutable revision → supersede/revoke with preserved prior evidence. Prohibit requester/issuer self-approval and direct role/permission bypass. | No real approving ERPNext Role name, approver group, segregation matrix or exception workflow authorized. |
| **Effective-time rule** | Normalize timestamps to one explicitly declared timezone/UTC storage; recommend `[effective_from, effective_until)` and **forbid retrospective authorization of a transaction by newly approved backdated mappings**. Test submission-time approval status plus posting timestamp. | Exact date/time source, backposting/cutoff policy, future-dated approvals and timezone strategy await Accounting approval. |
| **BC3 cutover** | Prospective controlled linked issues only; old submitted issues remain immutable; existing drafts either revalidate under newly approved B/C before posting or are withdrawn for fresh approval. | Effective cutover date and historical exception decisions are not approved. |

**Owner-approved review direction:** exact leaf Item Group with no parent inheritance or Item-level silent override; positive explicit C revision selection for multi-center cases. **No mapping records or posting fallback may be activated until financial rows and remaining selection/approval controls are authorized.** In particular, do not automatically equate `work_for_section` with a Cost Center, use an Equipment Section as explicit operator selection, or assume one department always has one center.

## 4. Candidate security and lifecycle contract (approval required)

1. **Identity:** A mapping revision requires exact Company ownership for linked category/dept and financial master, an issuer-independent approval identity, approval timestamp/reference, and immutable revision identifier. Reject missing Company, disabled/group/mismatched Department/CCPC Section, or invalid Account/Cost Center. Verify actual standard ERPNext v16 master schema before coding Account suitability rules (do not invent fields).
2. **Authority:** Propose a **dedicated Accounting approval capability/role** distinct from Stockroom Personnel and Withdrawal Slip Requestor; role name, eligible users, reviewer/preparer separation, permissions, administrator emergency override and audit process are **pending owner approval**. No automatic grants from setup/bootstrap.
3. **State transitions:** Only draft records may be edited; approved revisions cannot be altered, deleted, renamed or backdated. Future corrections create a new approved revision; revocation must be append-only in the audit trail. Do not permit user-supplied `approved_by` or timestamps to override server identity/time.
4. **Concurrency:** Both creation of a new revision and issuing stock must lock the **same stable Scope rows** using `SELECT ... FOR UPDATE` in documented consistent order. Implement duplicate scope creation race recovery via database unique constraint; recheck effective overlap and active states while locked. Use consistent lock order: Withdrawal Slip → ordered B Scope keys → C Scope → linked revision validation; approval writers lock only the relevant scope. Verify no deadlocks across cancellation and active mapping edits. Approval outside issuer transaction must not invalidate an already committed issue's historical snapshot.
5. **Historical trace:** Store immutable selected `B_revision_id` and `C_revision_id` on each original Stock Entry Detail along with actually posted `expense_account`, `cost_center`, beneficiary Department and Equipment-at-issue provenance. Never recalculate older GL entries when rules change. Actual posted account/center is the return-reversal target, not a refreshed mapping.
6. **Enforcement layer:** Validate in server methods/hooks, not merely UI, read-only fields or Frappe Workflow screens. Deny unauthorized mapping creation/approval, direct API/Stock Entry provenance forgery and unauthorized modified-after-submit data. A reviewed, auditable exception requires explicit separately approved process rather than `ignore_permissions` or generic System Manager silent bypass.
7. **No secret or production data:** Test only with synthetic `_Test Company`-style fixture records on disposable Actions runners; approval data and live master identifiers arrive via the authorized GitHub accounting review, not personal notes, exports or guessed defaults.

## 5. Exact proposed integration contract for PR #16 follow-on (DO NOT IMPLEMENT YET)

**Build original linked Material Issue:**
- Lock and reload the Withdrawal Slip as current source. Resolve actual beneficiary under Decision A and preserve Equipment under Decision D.
- Resolve each Item/category from **the separately approved B1 authority**. For each row, require one matching approved, effective B revision and validate Account Company, status and suitable P&L usage.
- Resolve C from the **actual beneficiary**, approved explicit selector (if any) and authorized revision; validate Company, Cost Center active leaf and time window. All rows on the same Slip use the same C selection only if that granularity is approved.
- Set Stock Entry Detail `expense_account`/`cost_center` and selected B/C revision provenance before insert; do not depend on standard ERPNext default Account/Center selection.

**Before submit (required even for forged/manual linked vouchers):**
- Under reviewed Slip + B/C scope locking, re-read actual item/category, beneficiary Department, selector and current approved revisions and compare **every** Stock Entry Detail's revision IDs, expense Account, Cost Center and Department. Reject stale source/approval changes, unauthorized values, clearing, missing or overlapping approvals **before any SLE/GL posting**; do not patch a forged record in place as a substitute for rejection.
- If Accounting chooses Section allocation, extend **both** `_lock_withdrawal_slip` SQL and post-lock comparisons to `work_for_section` (plus any new explicit selector), and validate against same-company CCPC Section and beneficiary Department; if C selection can be per item, protect row-level selector and source provenance too.
- Confirm native ERPNext posting produces real expenses against approved Account/Cost Center and correctly propagated beneficiary Department (configured GL Accounting Dimension). Preserve existing PR #16 double issuance, rollback, cancellation, Equipment immutability and report tests.

**Stock Entry draft gap to test:** ERPNext may recalculate defaults during insert/validation. Compare **persisted** document row values and actual final GL after `submit`; do not trust the in-memory builder alone. No custom duplicate GL or compensating Journal Entry.

## 6. Proposed validation matrix and release stop

| Test group | Acceptance evidence on disposable Frappe v16/ERPNext v16/MariaDB | Minimum negative tests |
| --- | --- | --- |
| Approval + revision history | Real DB unique keys, locked mapping approval, revision trace, overlap denial, correction by new revision, approver identity | Forged approval, wrong Company, expired/revoked/overlap, duplicate concurrent approval |
| B — Account | Real two-category two-account issue/GL assertion with valid synthetic approved B revisions | Unapproved generic Stock Adjustment, cross-company/group/disabled/non-expense Account, changed Item category, direct forged row |
| C — Cost Center | Real two-beneficiary distinct Cost Centers, requester differs; exact posted row and GL Department/Cost Center | Missing/ambiguous/multi-center without explicit selection, requester fallback, foreign/disabled/group center, selector forgery |
| Cross-feature A+D | Re-run PR #16 combined beneficiary/equipment tests and inspect the **same** issue row and GL | Conflicting/absent beneficiary, equipment substitution, source change under lock, after-submit mutation |
| Concurrency, rollback + history | Real simultaneous revision/issue and double-issue tests, no orphan SLE/GL, cancellation and retries | Changing approval during issue; failure after draft creation; stock/GL leakage |
| Releases | Approved Finance B1/B2/C1/C2/C3/BC1 details/BC2/BC3, reviewed CI, secure target/origin/backups and explicit DEV authorization | No signature, unverified masters, draft PR, dirty DEV branch, unknown origin, no backup = STOP |

Existing [joint PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) tests **72/72 mocked Withdrawal + 13/13 genuine Accounting; 12/12 mocked Equipment + 13/13 genuine Equipment** passed independently of any mapping control. **Do not claim B/C tests or production readiness based on those passes.**

## 7. Approval checklist for the next owner/Accounting review

**Owner/Accounting must explicitly approve or correct these proposals before code implementation:**

- [x] Four-DocType scope+revision structure **approved for draft GitHub-only review**, not live schema migration, permissions, approval or posting.
- [x] B1 exact **leaf Item Group** selection for the initial reviewed mapping design, with **no automatic parent inheritance or silent Item-specific override**; policy expansion still needs separate approval.
- [ ] B2 signed Company/category/eligible Account crosswalk from [approval worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md).
- [ ] C1 signed Company/actual beneficiary Department/Cost Center crosswalk.
- [ ] C2/C3 Department-only default, when explicit multi-center selection is required, Section eligibility and Slip-vs-line allocation scope.
- [ ] Concrete Accounting approver/permission/segregation and exception procedure (BC2).
- [ ] Effective timestamps, revision/supersede/revoke lifecycle, cutover and historical treatment (BC1/BC3).
- [ ] Then authorize a focused new **GitHub draft review** implementing only approved choices; CI tests first, DEVELOPMENT pull/test only with verified target and backups. PRODUCTION approval remains separate.

**Two design boxes above are checked by the subsequent owner approval**, recorded separately in the decision link at the top. All unresolved Finance fields and controls remain unchecked. The present draft PR #17 is deliberately **inert**: no mapping approvals, row allocations, GL posting control or schema deployment was authorized by these checkboxes.
