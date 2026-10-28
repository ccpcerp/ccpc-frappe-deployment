# CCPC Finance mapping — selected Accounting authority and lifecycle policy

**Decision date:** 2026-10-28 (Asia/Manila)  
**Authority:** Following the detailed schema/governance proposal, the owner said **"Approved decide it yourself."** This delegates selection of a **safe technical/governance design** for documentation. It does not appoint real personnel or authorize the assistant to sign Accounting decisions, assign user roles, activate financial mappings, modify app code/database schema, deploy, or alter DEVELOPMENT/PRODUCTION.  
**Status:** OWNER-DELEGATED DESIGN CHOICES RECORDED; IMPLEMENTATION AND ACTUAL BUSINESS AUTHORITY SEPARATELY GATED.

**Primary references:**
- [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Detailed lifecycle schema and Accounting governance specification](FINANCE-MAPPING-LIFECYCLE-SCHEMA-ACCOUNTING-GOVERNANCE-SPEC-2026-10-28.md)
- [Versioned rejection/retirement design](FINANCE-MAPPING-REJECTION-RETIREMENT-LIFECYCLE-DESIGN-2026-10-28.md)
- [Integration2 Finance handoff](INTEGRATION2-FINANCE-AUTHENTICATION-CHECKPOINT-2026-10-27.md)
- App review HEAD: ccpcerp/ccpcerp **review/circleci-isolated-erpnext-phase2-2026-10-26** @ **0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41**.

## 1. Selected authority — a controlled ERPNext decision record, not a text reference

**Decision G4: use CCPC ERPNext as the sole authoritative *mapping approval decision register*.** Proposed new internal DocType **CCPC Accounting Mapping Decision** stores signed, uniquely identified, exact-company-and-revision-scoped approval/retirement decisions, with immutable event-time identity and financial facts. This does not assert that a DocType exists today or that any historical approval has been granted.

**Two human identities for ordinary operations:**
1. Maker: enabled named user with **CCPC Mapping Preparer** role and explicit exact Company grant; proposes a Draft, never signs or executes approval.
2. Checker/Accounting decision signer: enabled named user with **CCPC Accounting Mapping Approver** role and explicit exact Company grant; signs a structured Accounting mapping decision and applies it **only to the exact version reviewed**, or rejects a Draft with a reason. Checker must be different from the Maker (and from the retirement requestor). No Administrator/Guest, Stockroom or roleless implicit bypass.

This is a **two-person** control, not an assertion that two distinct Accounting officers or a third approval tier are required. The same properly authorized Checker can sign the controlled decision and invoke its corresponding approval/retirement acceptance; the durable signed decision record provides purposeful, verifiable evidence of precisely what they authorized, not additional independent personnel. Any future requirement for an external or second signature needs a new signed policy change.

**Real staffing is a remaining release prerequisite:** The project owner or authorized CCPC Accounting management must assign/approve actual named employee Users and Company grants under ordinary personnel controls. This document does NOT appoint any individual or treat synthetic users as real-world Accounting signatories. Until named authorization is recorded and the system implements the verifier, financial activation remains blocked.

### Source-of-truth and trust boundary

The protected decision row is authoritative evidence of **an authenticated, internally approved ERPNext mapping decision**, not proof of an outside board authorization, a handwritten signature, a legal digital signature, or any external regulator's requirement. Only a designated server method may create/sign it, on an authenticated CSRF-protected session after exact Checker and Company checks. Ordinary DocType Create/Write/DELETE permissions on decision and event DocTypes are absent; read access is Company-scoped and audited. Caller cannot set signatory, Company, status, signed_at, target identity, approved financial value, or canonical fingerprint.

A free-text approval_reference (currently allowed by the pinned workflow) is **not valid authorization evidence**. A future approve/retire endpoint must require the exact CCPC Accounting Mapping Decision ID, freshly verify its signed scope/version and single-use status, and retain that ID on the approving event/revision and Version audit. The legacy text field may hold the server-generated decision ID for display/compatibility, never independently authorize activation.

## 2. Detailed decision-record contract — fields are PROPOSED, not installed

Proposed DocType **CCPC Accounting Mapping Decision** (append-only after signing):

| Candidate field | Type / rule |
| --- | --- |
| name/decision_id | Server-generated immutable unique ID |
| decision_type | Select **Approve Expense / Approve Center / Retire Expense / Retire Center**; reject others |
| company | Link/Company, server-derived from exact Scope |
| expense_revision / center_revision | Two typed Links; exactly one set, matching decision_type |
| expense_scope / center_scope | Two typed Links; exactly one set, Company-validated; no dynamic SQL from HTTP |
| source_identifier | Exact locked Item Group or beneficiary Department/selector snapshot |
| target_value | Exact locked leaf Account or Cost Center; Company and eligibility rechecked at execution |
| reviewed_modified | Exact server-observed revision version token |
| reviewed_fingerprint | SHA-256 of canonical typed decision payload and revision/scope/proposal facts |
| signed_by, signed_at | Authenticated Checker User and server timestamp, immutable |
| approved_from_utc / proposed_retirement_cutoff_utc | Prospective intent only; retirement MVP has **immediate server cutoff only** |
| reason | Mandatory for retirement; nonempty bounded explanation |
| decision_fingerprint | SHA-256 of canonical signed snapshot, unique/validated |
| evidence_origin | Constant **CCPC_ERP_INTERNAL**; never assert external signature |
| status | Signed only after protected server transition; withdrawal/correction is a **new append-only event**, not row edit |
| request_id (retirement only) | Link to one exact pending immutable Maker retirement request |

Proposed **CCPC Mapping Decision Use** record binds exact decision_id to one approved revision transition or one accepted retirement event. Unique(decision_id) prevents using a decision twice. The use record, state change/event, and Frappe Version audit **commit atomically**. Signed decision alone has **no accounting effect**. A signed-but-unused record does not constitute an activated mapping.

**Signature verification contract:** Re-fetch the decision under row lock, verify it originated from the controlled server workflow, confirm signed_by has the required role/grant **at decision time** and executing Checker is authenticated/currently authorized; use immutable snapshot for historical reporting. Check same Checker for signing/applying in initial policy, the exact requested action, Company, scope key, revision name, source/value, reviewed_modified and fingerprint, status=Signed, allowed timing, absence of invalidating/correction event, and no prior unique Use. Validate target and actor again under locks just before state change. Do not infer signatures from merely setting Frappe owner or uploading a PDF. Protect logs and public GitHub against passwords, session values, attachments or private Accounting approval content.

**Integrity limitation:** A normal database digest is not a tamper-proof signature against an Administrator with full DB privileges. Use restricted write paths, least privilege, immutable audit/event rows, backup provenance and independent review; if external legally binding digital signature is later required, explicitly design that integration instead of claiming the current design provides it.

## 3. Selected lifecycle policies from decision register G1–G10

| Gate | Selected safe default | Implementation notes / guardrails |
| --- | --- | --- |
| G1 Draft rejection | **Add terminal Rejected to both B and C Revision states**, with server-owned rejected_by/at/reason and immutable event | Never reject or edit Approved; correction creates new revision |
| G2 event schema | **Three lifecycle DocTypes**: Rejection Event, Retirement Request, Retirement Event; plus protected Accounting Mapping Decision and unique Decision Use | Exact fields/indexes remain for separate code/schema review |
| G3 retirement actors | **Maker opens request; different Checker accepts/declines**, with exact Company grants; same named Checker role may also sign Accounting decision | Never self-authorize; no third user mandated |
| G4 evidence authority | **Internal signed CCPC Accounting Mapping Decision**, tied to exact revision/value/version and consumed once | No external-file requirement for standard internal mappings; add external authorization only if CCPC policy requires |
| G5 rejection | **Independent Checker + mandatory reason; no separate Accounting signature for rejection** | Reject cannot activate or write financial journal/stock |
| G6 retirement timing | **Immediate, server-owned prospective cutoff only for first implementation** | No scheduled/future cutoff until separate policy/tests; no backdating; original Approved history retained |
| G7 cardinality/idempotency | **One unresolved Draft per Scope, one pending retirement request per Approved revision, one accepted retirement event per target** | Enforce with locking and DB-backed uniqueness; idempotent replay only for exact canonical request |
| G8 history | **Immutable event-time approval provenance; historical audits and returns do not depend on former actors' current roles** | Current actor permission checked for new decisions; resolver needs code review/change |
| G9 schema | **Additive fields and event DocTypes; no auto-backfill of signed decisions or historical approved rows; indexes after data inspection** | Migration and lock-order test under real InnoDB, deploy resolver before event writer |
| G10 failure/recovery | **Fail closed, transactional Version audit, ambiguous HTTP response = read-only inventory before retry; do not restore site as financial rollback** | Controlled new prospective decision for correction; verified backup and separate restore authorization |

**G11 remains business data, not a design choice:** Actual Company/category-to-Account and beneficiary Department-to-Cost Center crosswalks, authorized named employees and whether higher-level Accounting decisions are mandated cannot be invented. App code should not hard-code a company/person. **G12 remains operational authorization:** Coding, branch selection, migrations, DEVELOPMENT pull and PRODUCTION release require separate specifically scoped approvals.

## 4. Transaction and runtime acceptance invariants

- Exact Company from server-side Scope; current roles and Company grants from Frappe User/Has Role/User Permission. Authenticate distinct Maker and Checker. All signature creation and lifecycle operations are CSRF-protected POST; no public/Guest methods and no System Manager fallback.
- Deterministic lock order across Company, scope, revision, signed decision, Decision Use and lifecycle request/event. In pinned code, _real_authority also acquires User/Role/Permission locks **before** Company; the new implementation must reconcile all actual lock ordering with issue resolver and prevent deadlocks under real MariaDB concurrency tests. Do not claim locks make uniqueness automatically durable.
- Approve only unchanged Draft with matching decision's exact reviewed version, allowed Account/Center, nonoverlapping effective interval, verified signatory/Company. The execution must insert the unique Use and Version audit atomically with Approved state. No decision may be accepted merely because the caller supplied a string.
- Reject only unchanged Draft. Set Rejected fields and event + Version in one transaction. No Decision record needed; reason mandatory; Maker cannot reject own proposal; no reactivation of Rejected.
- Accept retirement only against Approved target and the one pending Maker request, signed matching Checker decision, and locked absence of accepted retirement; set server-owned cutoff at acceptance, no earlier than event acceptance time or original start. Preserve original Approved fields. If target has future effective_from, reject immediate retirement (no pre-start cancel by rewriting history); a separate future policy is required. Compute effective end = min(original end if set, accepted cutoff). No double insert/Version on retry.
- Issue resolver and before_submit must lock accepted event and use the computed end; validate at voucher posting timestamp and **now**, fail if cutoff passed while waiting. Retirement of sole Center prevents future eligible issues until a new approved Center exists; never use Item/Company native defaults.
- No alteration to historical submitted Stock Entries, SLEs, GL Entries, Equipment or signed source mapping IDs. Correction of a mistaken retirement uses a new prospective Maker/Checker-approved revision, not deletion of an event or backdated SQL.
- Verify rejection-vs-approval race, approval-vs-retirement, retirement-vs-issue, role revocation at signature and at execution, wrong Company/value, session/CSRF, dual Checker replay, one-use uniqueness, forced Version failure and transaction rollback. Distinguish mocked policy tests from **real** Frappe v16/MariaDB schema/HTTP transaction tests.

## 5. Implementation and accounting authority remain separately gated

**No source change in this decision.** Next proposed deliverable is a targeted GitHub **application implementation plan**, with exact DocType/field/index diff, endpoint signatures, permission and audit contract, tests, and isolated DEVELOPMENT upgrade procedure, submitted for separate owner approval. Before any actual code implementing financial activation can be considered ready, named Company-specific signatories and real Accounting crosswalk/evidence policy must be independently validated. Do not use an unauthenticated or synthetic internal "Signed" record as a substitute for those decisions.

**Existing Integration2 fixture:** Synthetic TISS Expense Scope **fie8da5c59**, Maker Draft **fieef2e44j**, last independently read back as Draft with zero financial postings and zero Version approval events. Leave unchanged. No new Checker approval, rejection or retirement HTTP endpoint execution is authorized by this decision. No main DEVELOPMENT or PRODUCTION migration/restart/backup restore/deployment is authorized.

**Status summary:** Technical policy **selected** under delegated owner discretion; precise implementation still DESIGN ONLY; actual employee appointment, Accounting business crosswalk and release remain blocked until evidence/approval is provided.
