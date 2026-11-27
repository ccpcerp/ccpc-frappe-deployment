# CCPC ERPNext — Shared Cost Center and Department/Equipment Attribution Proposal

**Status: DESIGN PROPOSAL ONLY — reviewed 2026-11-27 (Asia/Manila). NOT an implementation authorization, Finance approval, deployment instruction, or posting approval.**

**Owner-selected business objective:** Use **one shared `Main - CCPC` Cost Center** for Cagayan Corn Products Corporation while retaining exact beneficiary **Department** and issue-time **Equipment** attribution of consumed materials. Do not require financial P&L/budgets by individual plant in this design. Keep correct stock valuation and Company accounting and prevent double posting.

## 1. Verified context, and important limits

- GitHub is authoritative for application source. Reviewed app [draft PR #44](https://github.com/ccpcerp/ccpcerp/pull/44), branch `review/phase1-maintenance-integrated-tests-2026-11-24`, exact reviewed head `e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5`. **This is review-branch code, not proof of the currently installed DEVELOPMENT checkout at this instant**.
- Owner-provided DEVELOPMENT ERPNext screenshot of `Main - CCPC`: enabled, `Company=Cagayan Corn Products Corporation`, parent `Cagayan Corn Products Corporation - CCPC`, `Is Group` unchecked and `Disabled` unchecked. This validates a **potential shared leaf master**, not a signed Finance mapping or the Company Default Cost Center setting. The precise master record ID is not independently verified beyond the UI label.
- Trusted operator's reviewed, pinned READ ONLY MariaDB diagnostic on 2026-11-27 reported **zero** `CCPC Center Mapping Scope` records with Company `Cagayan Corn Products Corporation` and beneficiary `Wet Mill Plant - CCPC`; preceding Finance diagnostic reported Bearings Expense scope/signed provenance/eligible account PASS. These were **owner-pasted operator outputs, not direct assistant DB access**.
- Existing Withdrawal Slip `WS-2026-00008` is Draft, with requesting Maintenance Department, actual beneficiary Wet Mill Plant, Equipment `WD-401`, Bearings item `ITEM-00010`, 1 Nos, Warehouse 1. Keep it Draft. Its section was edited after the earlier diagnostic; inspect current equipment/section and live record readiness separately before any eventual posting.
- Current app `bc_issue_runtime.py` **requires exactly one approved, effective Department-only Center Mapping Scope and Revision for the beneficiary** and validates the selected same-Company enabled leaf Cost Center. It cannot legally fall back to `Main - CCPC` today. `ccpc_center_mapping_revision` is stored on Stock Entry Detail for traceability.
- `withdrawal_issue_beneficiary.py` preserves the **actual beneficiary Department** on original Stock Entry and detail, rejects incompatible Equipment Department, and checks Perpetual Inventory and Department GL Accounting Dimension metadata. `withdrawal_slip_stock.py` snapshots Equipment onto each new Stock Entry Detail and guards pre-submit financial and equipment provenance, duplicate posting and transaction integrity.
- `CCPC Department Material Consumption` is a read-only **gross original Stock Ledger valuation** report by beneficiary Department, not net returns, Department GL P&L or a certified Department cost ledger. `CCPC Equipment Job Material Activity` separately uses issue-time Equipment snapshots and unpriced Job Order activity; it is **not full equipment/maintenance cost** (labor, downtime, services, returns, and Job Order linkage limitations).
- `bc_mapping_workflow.py` already allows **multiple Department scopes to choose the same Cost Center**, under independently authorized named maker/checker signoffs. `phase1_finance_onboarding.py` provides the controlled proposal/review/sign-and-approve route; ordinary custom mapping DocTypes have no standard permission grants. Administrator is excluded from Finance maker/checker approval.

**Source references at the reviewed app SHA:** [financial issue resolver](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/bc_issue_runtime.py), [stockroom original issue](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/withdrawal_slip_stock.py), [beneficiary and GL dimension](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/withdrawal_issue_beneficiary.py), [Finance workflow](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/phase1_finance_onboarding.py), [mapping revisions](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/bc_mapping_workflow.py), [Department source report](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/report/ccpc_department_material_consumption/ccpc_department_material_consumption.py), [Equipment activity report](https://github.com/ccpcerp/ccpcerp/blob/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5/ccpcerp/ccpc_erp/report/ccpc_equipment_job_material_activity/ccpc_equipment_job_material_activity.py).

## 2. Distinct meanings — do not combine these dimensions

| Dimension | Business question | Proposed meaning and owner |
| --- | --- | --- |
| Expense Account | What type of expense was incurred? | Preserve the eligible, signed Item Group-to-Expense Account policy and Account master. Bearings must remain within approved Routine Maintenance scope. Do **not** assume the displayed `5140 - Repairs & Maintenance - CCPC` is the secretly verified signed mapping target. |
| Beneficiary Department | Which Department actually used the materials? | The true Wet Mill beneficiary, not the Maintenance requester, remains on issue-time Stock Entry header/detail and valid GL Department accounting dimension. |
| Equipment | Which equipment received the materials? | Preserve exact `WD-401` issue-time snapshots per item; report only supported gross material issue, not unsupported job or full maintenance expenses. |
| Cost Center | Which Company financial grouping receives the expense? | The **same** approved `Main - CCPC` leaf may serve multiple Departments. This will produce **shared** Cost Center financial reporting, *not* separate plant Cost Center P&L. |
| Stock Ledger and General Ledger | How much inventory left and what booked in financial accounts? | Keep stock valuation and GL distinct; reconcile separately, and require verified Department GL dimension propagation. |

No new plant Cost Center hierarchy is required for the selected **operational** Department/Equipment reporting objective. A valid same-Company leaf Cost Center can still be needed on stock expense/GL transactions.

## 3. Architecture alternatives and recommended sequencing

| Option | What changes | Benefits | Important tradeoff | Status |
| --- | --- | --- | --- | --- |
| **A. Shared master, existing signed per-Department mappings** | Finance separately approves Wet Mill Department → `Main - CCPC` using existing scope/revision workflow, subject to checking any other historical Department mappings | **Smallest code and migration risk**, no extra Cost Center; retains existing historic signed provenance | Requires a Finance approval record per beneficiary Department | **Recommended first / no code change**, but actual proposal and approval remain separately unauthorized |
| **B. One signed Company-wide shared issue Cost Center policy** | Design/implement one immutable, signed versioned shared-Cost-Center policy for CCPC original Material Issues; remove *future posting dependency* on per-Department Center scopes **only after** safe migration/cutover | Reduces repeated approvals when new Departments legitimately share the same center | **Real code, schema, accounting control and report changes**; requires new review, migration, test and approval gates | **Preferred longer-term simplicity target**, NOT approved to implement |
| **C. Pick current Company Default Cost Center automatically or bypass mapping approval** | Posting falls back to mutable Company default/current form value, no separate signed authorization | Appears simple | Can silently redirect expense postings, lose signed provenance, break before-submit validation and historic reproducibility | **Reject** |

**Recommended decision:** Adopt A as the **lowest-risk interim design** if Accounting confirms `Main - CCPC` is suitable; design B for a *subsequent, explicitly approved* development change once real Finance requirements and current installed/legacy data are inspected. **Do not implement C.** One shared Cost Center does *not* require dropping Finance authorization.

## 4. Proposed future Company-wide center policy (Option B; requirements, not approved implementation)

1. **Explicit Company scope:** one CCPC-only policy key for original **same-Company Withdrawal-linked Material Issues**. Do not extend to all ERPNext GL vouchers, other companies, project/capital issues, stock adjustment, intercompany billing or purchase invoices.
2. **Signed financial target:** an authorized Finance preparer proposes a specific, enabled, non-group Cost Center belonging to the issuing Company; an **independent named Accounting checker** reviews and signs its exact version and purpose. Administrator, Guest and Stockroom role cannot substitute as a signer. Store signed decision/use and full version snapshot.
3. **Effective windows and retirement:** maintain immutable policy revisions with server-owned approval timestamp, future activation/expiry or reviewed retirement; no backdated switches, overlapping active decisions or mutable silent fallback.
4. **Deterministic selection:** at issue creation and immediately before submit, lock the issuing Company/shared policy and validate **exactly one effective, approved policy revision** for the current instant. If missing, expired, unapproved, invalid master, conflicting legacy route, or changed while awaiting locks: **fail closed without SLE/GL**.
5. **Preserve Expense policy:** resolve exact leaf Item Group to signed and eligible Expense Account as now, with the Bearings Routine Maintenance restriction unchanged. Do not use a broad Company expense default.
6. **Preserve beneficiary attribution:** independently validate genuine same-Company beneficiary Department and Equipment affiliation, Department GL Accounting Dimension and issue-time Equipment fields; never substitute requester Department, `Main - CCPC`, or editable current slip for the historical beneficiary.
7. **Record the accounting decision on each issue row:** store the selected **shared-policy revision identifier/type** plus exact resolved Cost Center, Expense mapping revision, actual Department, Equipment snapshot and original slip item. **Do not put a made-up Company policy ID into the existing `ccpc_center_mapping_revision` link**, which is a Department-scoped legacy reference. A versioned typed provenance field/new reviewed schema is likely required; evaluate backward-compatible alternative only if it preserves referential integrity.
8. **Existing records stay authoritative:** never rewrite submitted Stock Entry, Stock Ledger, GL, historical `ccpc_center_mapping_revision`, signed decision/use or Version audit trail. Legacy issues continue to resolve provenance under their original rules. An explicit **per-Company cutover** defines which path new issues use. No automatic preference for whichever mapping happens to exist; never allow two active competing routes for one issue.
9. **Failure and concurrency safety:** keep existing normal authorized stockroom path, unique original linked issue, row-locking, server-stamped posting time and independent before-submit recheck, transaction rollback and no duplicate postings. A failure must leave the Draft Withdrawal Slip, stock and GL unchanged.
10. **Reports:** Department consumption by gross original outbound SLE and Equipment material activity remain operational reports; use GL/Company P&L separately. If ever advertising **Department GL expense** or full maintenance cost, first validate real GL dimension propagation, returns, labor/services and reconciling GL/SLE data in genuine integration tests—not just query labels.

### Suggested implementation touchpoints (future, not touched)

- `bc_issue_runtime.py`, `bc_issue_allocation.py`: choose one protected, exact policy path with typed historical provenance; never return an unapproved Center.
- `withdrawal_slip_stock.py`: server-only assignment, duplicate and before-submit protection, immutable snapshot fields; revise only after accounting design and schema review.
- `phase1_finance_onboarding.py`, `bc_mapping_workflow.py`, `bc_finance_evidence.py`: propose/sign/review/retire the **company** policy, with existing maker/checker, unique decision-use and Company grant checks.
- Reviewed DocType/Custom Field and **migration/index design**: unique Company/version/effective window, immutable references, historical and future records; no blind patch against real site.
- `withdrawal_issue_beneficiary.py`, Department & Equipment reports: **preserve** actual issue-time attribution; test them against real SLE/GL posting and cancellation.
- CI and disposable MariaDB integration tests: exercise all authorization, concurrency, duplication, source-drift, no-rollback-leak and report integrity invariants.

## 5. Required independent checks before either live option

1. **Finance purpose:** Accounting explicitly agrees to one shared `Main - CCPC` bucket and understands it will **not** itself show separate plant Cost Center P&L/budgets; they still want Department/Equipment original material usage reports.
2. **Master identity and settings:** recheck the *full exact* `Main - CCPC` master ID, Company, `is_group=0`, `disabled=0`, any Company Default Cost Center and live accounting dimension setup. Screenshots showed the right properties, but not every runtime/configuration field.
3. **Existing mapping inventory:** review actual signed/retired/draft Maintenance and other Department Center revisions, signed Expense mappings, Account semantics and ledger history with sanitized read-only evidence. **Do not redirect any historical signed or submitted voucher by inference.**
4. **Finance actors:** named enabled preparer and independent Accounting approver, Company-scoped grant, no Stockroom conflict. Do not grant broad mapping DocType permissions to Administrator.
5. **Current DEVELOPMENT readiness:** verified safe Git source state, app SHA, backups/restore/off-host recovery where relevant, Warehouse/Bin/SLE quantity/valuation, named user issue permission, Department GL propagation, Equipment `WD-401` affiliation and current Section, and absence of submitted/draft conflicting linked Material Issues. The earlier offline mocks are not live integration proof.
6. **Document/release governance:** require explicit new owner/Finance approval before writing any scope/proposal/approval, custom code/schema, migrations, DEVELOPMENT pull or any issue submit. **PRODUCTION requires a later separate explicit approval and recovery plan.**

## 6. Proposed future test and release gates for Option B

- **Static/source tests:** scope isolation; no stringly-typed synthetic legacy revision; no default fallback; maker/checker separation; unchanged non-CCPC issue behavior and intercompany Phase 1 block.
- **Policy unit tests:** zero/one/multiple approved company policies, disabled/group/cross-Company center, overlapping effective windows, revoked/expired/superseded version, future approval, race with cutoff, tampered revision.
- **Genuine disposable MariaDB/Frappe integration:** POST Finance proposal/sign/review, unique use and Version, one legitimate Material Issue, revalidation at submit, failure leaves SLE/GL/slip unchanged, no duplicate issue with two issuers, simulated Stock Entry edits fail closed, correct Department GL dimension, correct Equipment snapshot, retained signed Expense account.
- **Historical compatibility:** old submitted linked Stock Entry Details and signed Department revisions unchanged; reports split legacy/new only by authentic typed provenance. No historical backfill or recalculation.
- **Report reconciliation:** original SLE/stock report and equipment activity are internally consistent, amounts distinguish gross issue from posted P&L GL and from returns; no misleading Department profit claims.
- **DEVELOPMENT operator acceptance only after reviewed GitHub change:** check clean source/identity and recovery, pull reviewed exact commit via safe procedure, run controlled tests, log sanitized results back to GitHub.
- **No promotion to PRODUCTION** without separate owner approval, backup/restore proof, rollback plan and accounting signoff.

## 7. Explicit non-decisions and current HOLD

- Owner has **chosen the reporting design**, not the technical implementation or financial signoff.
- Do **not** create a new plant Cost Center; `Main - CCPC` is the leading shared master pending Finance approval, not automatically the current signed posting target.
- Do **not** create a Wet Mill Center Mapping Scope, assign Finance roles, alter existing signed decisions, delete records, update `Company.default_cost_center`, change a DocType, migration or posting hook based on this document.
- Do **not** pull/merge/deploy review branches merely because this document exists.
- `WS-2026-00008` stays **Draft**. Finance Center approval, full preflight, inventory posting, SLE/GL and PRODUCTION remain **HOLD**.

**Decision to return to owner:** Finance should confirm shared-center allocation and choose **A now (no-code, existing signed mapping workflow)** versus authorizing **a separate, future B implementation design/test PR**. Either path must protect the real beneficiary Department and equipment issue-time history.
