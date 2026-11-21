# CCPC Withdrawal Slip B/C — Owner approval of detailed mapping schema design

**Date:** 2026-10-18 (Asia/Manila). **Status:** OWNER APPROVED THE DESCRIBED SCHEMA DESIGN AND REVIEW-ONLY IMPLEMENTATION DIRECTION; FINANCIAL MAPPING APPROVALS AND SITE CHANGES STILL PENDING. **POSTING_NO_GO / PRODUCTION NO-GO / DEV_TARGET_ORIGIN_UNKNOWN_STOP.**

## Decision origin, applicable scope and priority

The owner replied **“Approved, continue”** immediately after the detailed [four-DocType schema and control design proposal](WITHDRAWAL-ISSUE-B-C-MAPPING-SCHEMA-AND-CONTROL-DESIGN-PROPOSAL-2026-10-18.md) was presented for review. This approves development of the proposed **two Company-scoped stable scopes plus two immutable revision families** as an **unmerged GitHub review**, retaining the previously approved [controlled/versioned mapping architecture](WITHDRAWAL-ISSUE-B-C-VERSIONED-MAPPING-ARCHITECTURE-APPROVED-2026-10-18.md).

**Owner-selected initial category rule for review:** For B, the matching key is the item's **exact, leaf Item Group**; no silent parent-category inheritance or Item-specific overriding. Changes to the category hierarchy or precedence need separate approval.

**Owner-selected safety rule for multiple Centers:** No arbitrary first match. A beneficiary Department with more than one eligible approved Center requires **positive, separately validated selection of the appropriate approved C mapping revision**. The exact Slip/per-item field, Section eligibility and user authority for that choice remain to be defined before any live posting workflow.

**Approved source model for scoped development:** four logical proposed Frappe DocTypes (names remain design-level, to be reviewed as code):
1. `CCPC Expense Mapping Scope`: Company + exact Item Group category identity, unique stable normalized key.
2. `CCPC Expense Mapping Revision`: scope reference, revision identifier, Account, approval provenance and applicable effective interval; preserve previously approved revisions.
3. `CCPC Center Mapping Scope`: Company + actual beneficiary Department + any explicitly approved selector identity, normalized stable key.
4. `CCPC Center Mapping Revision`: scope reference, revision identifier, Cost Center, approval provenance and applicable effective interval; immutable approved history.

**Implementation sequence authorized:** Create a distinct **GitHub-only draft review branch from exact verified app PR #16 head**; build a fail-closed, inert initial schema and static tests only. No active approval workflow, no approved mapping rows, no Account/Center default fallback, no new role grants, no original issue posting behavior change, no migration executed. Separately seek approval of concrete approval actors, permissions, state transitions, revision activation, effective-time/backdating rule, C selector location/Section behavior and financial crosswalk records before enabling mappings or changing financial postings.

## Still not decided or authorized

- Exact Company, Item Group, consumption Expense Account, Department and Cost Center mapping rows; [Accounting worksheet](WITHDRAWAL-ISSUE-B-C-MAPPING-APPROVAL-WORKSHEET-2026-10-18.md) stays blank/unsigned.
- Approval identities/roles, maker-checker rules, exemption procedures, event-based revocation and effective-time/backdate semantics.
- Whether Section is part of Cost Center selection, mandatory selection field/granularity and source-lock extension (necessary if Section selected).
- Live schema/index migration, Permission changes, DEVELOPMENT target pull/migrate/test, existing stored documents, cutover/historical remediation, production release. These are separate approval and testing gates.
- **No B/C posting validation may be declared operational** based on this design approval; prior PR #16 CI covers A+D only.

**Review acceptance requirements:** schema fields match authorized principles; no non-Admin approved mapping creation; server-side deny unapproved state transitions; unambiguous scope/revision identity; proposed uniqueness/overlap and locking documented for later genuine MariaDB tests; syntax/static mocked tests pass on exact reviewed branch; Finance must approve and test full workflow before any DEV/PROD deployment.

No private Google Drive notes or unapproved master values were consulted or copied.
