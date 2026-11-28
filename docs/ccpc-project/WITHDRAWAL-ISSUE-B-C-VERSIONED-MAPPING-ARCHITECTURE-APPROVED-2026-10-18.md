# Original Withdrawal Slip Issue — B/C Controlled Versioned Mapping Architecture

**Owner decision:** APPROVED IN PRINCIPLE, 2026-10-18 (Asia/Manila), in the active CCPC ERPNext conversation.  
**Decision scope:** The owner explicitly approved the recommendation to use **a controlled, versioned mapping arrangement** for original Withdrawal Slip Material Issue accounting decisions B and C. This is an **architecture/policy authorization** only, not an approval of specific Account or Cost Center records, exact DocType fields, permission assignments, ERPNext migrations, financial posting implementation, or DEVELOPMENT/PRODUCTION deployment.

**GitHub authoritative record:** This decision lives on the existing documentation review branch `docs/ccpc-checkpoint-2026-10-10` in [ccpcerp/ccpc-frappe-deployment](https://github.com/ccpcerp/ccpc-frappe-deployment), draft documentation PR [#24](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/24). It supplements owner-approved [Decision B](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-B-APPROVED-2026-10-18.md), [Decision C](WITHDRAWAL-ISSUE-ACCOUNTING-DECISION-C-APPROVED-2026-10-18.md), and the [B/C readiness and approval gate](WITHDRAWAL-ISSUE-B-C-IMPLEMENTATION-READINESS-AND-APPROVAL-GATE-2026-10-18.md). No personal Drive notes or outside accounting records were consulted.

## 1. Now approved — the architectural direction

1. **Controlled authority rather than implicit ERPNext defaults.** Material Issue expense Account and beneficiary Cost Center selections must come from explicit, company-scoped, reviewable **CCPC-controlled approved mapping records**. A native Item, Item Group or Company fallback is not inherently authorized; any such source can only participate under a separately approved rule and matching approved record. In particular, the generic `stock_adjustment_account` is **never** an automatic consumption-expense authorization.
2. **Two distinct mapping decisions.**
   - **B:** issue Company + *Accounting-approved material category* → eligible consumption expense Account.
   - **C:** issue Company + *actual beneficiary Department under Decision A* + any **separately approved explicit selector** → eligible Cost Center.
   This does not decide whether Item Group, Item-specific category, Section or an additional selector is the canonical input; those remain owner/Accounting choices.
3. **Version-controlled, auditable lifecycle.** Mapping decisions shall have identifiable revision/approval provenance, explicit authorization and time applicability. Proposed or superseded values must not be silently treated as current approvals. Once referenced by a submitted transaction, the effective approval/version and posted account/center must remain traceable for later returns and audits.
4. **Fail-closed posting contract.** Missing, ambiguous, revoked, stale, overlapping, cross-company or unsuitable mapping evidence prevents automatic posting. Do not silently select the first match, reuse the requesting Department's Cost Center or accept unapproved native defaults.
5. **Prospective development only after separate scope review.** Implement on a focused reviewed GitHub feature/review branch with isolated synthetic tests; test on DEVELOPMENT only after target/backup/Git-state verification and explicit approved operation. PRODUCTION remains separately controlled.

## 2. Concrete candidate specification for the next design review — NOT YET SCHEMA-APPROVED

A recommended realization is **two CCPC-owned, controlled mapping families**, potentially implemented as versioned ERPNext/Frappe DocTypes or equivalent approved records. The following are **proposed data contracts**, not authoritative fieldnames, role names, installed DocTypes or approved Company masters.

| Proposed mapping record | Proposed keys / audit information | Approved application behavior it must support |
| --- | --- | --- |
| B — Expense Account allocation | Company; approved material category key and key authority; exact eligible Account; revision ID; effective interval; approval status/by/at/reference; supersedes/revoked information | Resolve one and only one approved eligible account for the issue Company's original material category |
| C — Beneficiary Cost Center allocation | Company; beneficiary Department; optional separately authorized Section/selection key; exact eligible Cost Center; revision ID; effective interval; approval status/by/at/reference; supersedes/revoked information | Resolve exactly one approved valid center, or require explicit validated selection if multiple candidates apply |

**Suggested lifecycle for detailed approval:** Draft → reviewed/approved → active for defined effective interval → superseded/revoked with preserved history; implement with immutable approved revisions, uniquely auditable approval actions and a policy for non-overlapping effective intervals. Do not guess who may approve, which role names exist, whether two approvers are required, the transition rules, whether approval may be retrospective, or what date/time is authoritative. Those need a separately reviewed authorization and concurrency design.

**Candidate technical safeguards for later code review:**
- No overlapping simultaneously effective approvals for the same complete matching key; reject ambiguous records rather than resolving by arbitrary sort order.
- Server-side Company, Account (non-group, enabled, valid expense root/type) and Cost Center (active, non-group, matching Company) checks, plus Frappe-level permission and SQL-level transaction-safety review.
- Re-resolve against a locked, effective approved revision when preparing and submitting the Stock Entry; preserve the selected mapping's identity/version and actual posted row `expense_account` / `cost_center` for audit and later original-cost return. Detect changes to Item/category, beneficiary Department, selector and authorization between draft and submit; block forged direct vouchers.
- Preserve Decision A beneficiary Department GL and Decision D Equipment-at-issue immutable snapshot invariants. If Section is an approved selector, include `work_for_section` in issue-time source locking and validated provenance.
- Migration and schema/index design must be separately reviewed for concurrency, unique keys, version archival, rollback, idempotent installation and safe coexistence with any historical Stock Entry.
- A posted historical voucher is not reallocated because an Accounting mapping revision changes; historical corrections, if needed, require independent authorization.

## 3. Explicit outstanding decisions — this owner approval does NOT fill them

| Gate | Still pending |
| --- | --- |
| **B1** | Canonical Item/material category and precedence: Item Group, Item-specific override, hierarchy inheritance or controlled category; whether mapping operates per Item or per Slip line |
| **B2** | Every exact Company/category → approved expense Account mapping and any explicitly authorized Stock Adjustment exception |
| **C1** | Every exact Company/beneficiary Department → approved Cost Center mapping |
| **C2/C3** | Multi-center explicit selector, whether `work_for_section` participates, and the immutable auditable selection field |
| **BC1 — partially resolved** | **Approved principle:** controlled, versioned CCPC mapping authority. **Pending:** exact DocType/record model, field/schema and indexes, revision mechanics, role permissions, approval actors, effective timestamp rule and concurrent edit controls |
| **BC2** | Exception decision-maker, exception procedure and audit/override constraints |
| **BC3** | Prospective cutover scope, handling of in-flight drafts, historical data and any permitted correction policy |
| **Environment and release** | Authorized current ERPNext master verification; implementation scope/PR; test procedures, DEVELOPMENT identity/clean checkout/backups, and separately approved PRODUCTION release |

The [blank B/C mapping approval worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) must still receive the genuine approved Account and Cost Center crosswalk rows before posting-related implementation can be regarded as complete. Synthetic CI defaults do not supply those approvals.

## 4. Current application / testing boundary

The latest inspected joint [draft app PR #16](https://github.com/ccpcerp/ccpcerp/pull/16) head `827993e45ae9321e7a936f48f7fc3b17bf842099` is **not merged**. It combines Decision A beneficiary GL Department enforcement with Decision D Equipment-at-issue snapshots, and its isolated Accounting and Equipment tests passed. It **does not implement** the newly selected B/C mapping architecture and **does not provide an Accounting-approved mapping registry, schema, permissions, or posting safeguard**. PR #16 and its prior tests must remain distinct from any later B/C integration tests.

**Operational decision:** **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP** remains. No CCPC financial mapping data is created or inferred; no app code, ERPNext schema/site/role, DEVELOPMENT or PRODUCTION operation is authorized by this architecture-only approval.
