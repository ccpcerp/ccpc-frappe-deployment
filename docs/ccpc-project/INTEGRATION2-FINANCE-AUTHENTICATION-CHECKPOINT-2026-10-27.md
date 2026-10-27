# Integration2 Finance authentication checkpoint — 2026-10-27

## Verified by owner-executed terminal output

Two previously provisioned Integration2-only Finance test actors for fictional Company Integration Test Issuer (TISS) passed their role and Company grant preflight. The corrected credential preflight reported no existing password records for either actor, username/password login enabled, two-factor authentication disabled and enabled password policy.

A supervised, no-echo, operator-local Frappe v16 password provisioning test verified independent strong passwords for both accounts and reported:

```text
FINANCE PASSWORD SAFETY GUARDS: PASS
Maker password validation: PASS
Checker password validation: PASS
BOTH PASSWORD VALIDATIONS: PASS
FINANCE TEST PASSWORDS: COMMITTED
TWO DISTINCT PASSWORD HASHES: VERIFIED
INTEGRATION2 CREDENTIAL SETUP: PASS
NO FINANCIAL TRANSACTIONS PERFORMED
```

The command operated on the Integration2 site only, pinned CCPC application commit 0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41, guarded the exact two test actors, existing Company permissions, and protected recovery checkpoints, verified hash entries in the same transaction, and committed once. The owner did not disclose any credentials. An earlier maker-only validation attempt had stopped before any database write, followed by a separate successful read-only validation.

## Status and next step

Credential provisioning: **PASS by operator evidence**.

### Authenticated HTTP sessions: PASS — owner-executed Integration2 smoke

The owner then ran the guarded, pinned-application, Integration2-only localhost Frappe v16 session test with separately entered, private Maker and Checker credentials. It POSTed to `/api/method/login` independently for both actors, checked `message=Logged In` and valid, non-Guest session cookies, and GET-verified the actor identity via `frappe.auth.get_logged_user`. Session IDs were checked to be distinct, without printing them. The terminal returned:

```text
INTEGRATION2 AUTHENTICATED HTTP TEST
HTTP LOGIN SAFETY GUARDS: PASS
Maker HTTP LOGIN: PASS
Maker AUTHENTICATED IDENTITY: PASS
Checker HTTP LOGIN: PASS
Checker AUTHENTICATED IDENTITY: PASS
TWO DISTINCT AUTHENTICATED SESSIONS: PASS
INTEGRATION2 HTTP AUTHENTICATION: PASS
NO FINANCIAL TRANSACTIONS PERFORMED
```

**Verified gate:** Normal Frappe HTTP authentication and session-bound identity **PASS** for both Integration2 Finance test users. This is stronger than the prior direct DB-helper 8/8 PASS. It does **not** yet demonstrate actual CSRF-protected Finance workflow endpoint authorization, the Maker-as-Checker/Checker-as-Maker denials through HTTP, company boundary denial through HTTP, browser/Desk UI permissions, mapping draft/approval transaction correctness, concurrency, or stock/GL postings. New login/session metadata can be produced by normal login.

**Next bounded work:** Inspect Frappe v16 POST CSRF handling and reviewed CCPC mapping endpoint entry checks before running a safe, nonmutating HTTP authorization test. A missing or invalid CSRF token, missing revision, or intentionally invalid selector must not be misconstrued as a role-based denial. The checker approval/review endpoint locates an existing draft before authority checking, so a nonexistent revision cannot prove cross-role denial. Do not create Finance mapping records or approve/post transactions without a separately approved fixture. Keep PRODUCTION and main DEVELOPMENT untouched. No passwords/cookies/session IDs printed or committed to GitHub.

### Desk/CSRF initial diagnostic: /app redirects, /desk returns 200 and token

The owner attempted a two-actor Desk/CSRF preflight after the authenticated HTTP PASS; it stopped after "Maker AUTHENTICATED IDENTITY: PASS", before completing any Desk or Checker assertions. The diagnostic lacked reason details because it caught `RuntimeError` and displayed only the exception type. A focused Maker-only follow-up then returned:

```text
INTEGRATION2 DESK DIAGNOSTIC
MAKER AUTHENTICATION: PASS
/app HTTP STATUS: 301
/app CONTENT TYPE HTML: YES
/app CSRF TOKEN: NOT FOUND
/desk HTTP STATUS: 200
/desk CONTENT TYPE HTML: YES
/desk CSRF TOKEN: PRESENT
DESK DIAGNOSTIC: COMPLETED
NO FINANCIAL TRANSACTIONS PERFORMED
```

**Finding:** The initial assumption that `GET /app` must directly return 200 was incorrect for this DEV site; it redirects (301) while the site’s `/desk` route serves the Desk HTML (200) and `frappe.csrf_token`. GitHub Frappe v16 `frappe/www/desk.py` and `desk.html` confirm CSRF generation/rendering for the Desk page. There is no evidence from these checks of a broken authentication setting or missing CSRF support, and no reason to change routing or restart services. Only the Maker's direct Desk/CSRF readiness is shown; Checker Desk and independent CSRF tokens are not yet tested.

**Next one-step acceptance test:** Re-run a guarded two-account login + exact-identity + `GET /desk` (no redirects) + token-present/different validation for Maker and Checker. Use private no-echo passwords, separate HTTP cookie jars, do not display tokens/cookies/passwords or HTML, and no Finance POST endpoint. Normal login/session metadata may be written; no financial data changes intended. Then separately review HTTP authorization tests with true CSRF and role-denial evidence, without financial proposals/approvals or posting.

### Corrected two-actor Desk/CSRF: PASS

**Operator-reported completion after fixing `/app` -> `/desk` route assumption**:

```text
INTEGRATION2 CORRECTED DESK AND CSRF TEST
SITE AND APPLICATION GUARDS: PASS
Maker AUTHENTICATED IDENTITY: PASS
Maker DESK HTTP: PASS
Maker CSRF TOKEN: PRESENT
Checker AUTHENTICATED IDENTITY: PASS
Checker DESK HTTP: PASS
Checker CSRF TOKEN: PRESENT
TWO DISTINCT AUTHENTICATED SESSIONS: PASS
INDEPENDENT CSRF TOKENS: PASS
INTEGRATION2 DESK AND CSRF TEST: PASS
NO FINANCE MAPPING OR POSTING REQUESTS PERFORMED
```

Both independently authenticated Finance accounts accessed `GET /desk` with HTTP 200 and received distinct CSRF tokens; user identities and session IDs were separately verified without exposing the secrets. This is actual Desk-page/CSRF readiness, not authorization of Finance write endpoints or Maker-vs-Checker enforcement through HTTP. No master data, Finance draft, GL/stock entry or mapping approval was changed.

**Next guardrail:** The reviewed `ccpcerp.ccpc_erp.bc_mapping_workflow.propose_mapping` endpoint (app SHA `0c223d7...`) validates kind/canonical strings, then runs `_real_authority` on the session user **before any scope/mapping writes**. It is safe to test unauthorized cases with a deliberately nonexistent Item Group and Account to prevent any mapping creation even if expected authority check is bypassed. Test Checker calling Maker proposal for TISS (expected exact role denial) and Maker/Checker attempting the TREQ Company (expected exact Company-grant denial); require correct error class and/or specific message, not just an HTTP failure. Use real independent authenticated `POST` requests with CSRF headers from `/desk`, and never send authorized Maker+TISS proposal request or any approval/review request that needs a real revision. Errors may create ordinary request logs. Do not treat these negatives as proof of a complete Maker–Checker financial approval workflow.

### HTTP Finance authorization denials: PASS (two negative cases)

**Owner-provided Integration2-only operator transcript**, with actual authenticated independent Maker and Checker Frappe login sessions and per-session CSRF extracted from `GET /desk`, using application HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and protected checkout:

```text
INTEGRATION2 FINANCE HTTP AUTHORIZATION TEST
APPLICATION AND FINANCE SAFETY GUARDS: PASS
NONEXISTENT FINANCE INPUT GUARDS: PASS
Maker AUTHENTICATED HTTP AND CSRF: PASS
Checker AUTHENTICATED HTTP AND CSRF: PASS
Checker cannot propose TISS: PASS (denied by Finance policy)
Maker cannot propose TREQ: PASS (denied by Finance policy)
INTEGRATION2 FINANCE HTTP DENIAL CHECK: PASS
NO FINANCE MAPPING OR POSTING REQUEST SUCCEEDED
```

**Bounded conclusion:** The real `ccpcerp.ccpc_erp.bc_mapping_workflow.propose_mapping` HTTP POST endpoint enforced explicit *Maker role* denial on the authenticated Checker when scoped to `Integration Test Issuer` (`TISS`) and *Company grant* denial for the authenticated Maker when scoped to `Integration Test Requester` (`TREQ`). The script required HTTP 500, exception class `MappingPolicyError`, and matching specific denial message for each case; generic network/CSRF/missing-master failures would not count as PASS. Both requests supplied deliberately nonexistent Item Group and Expense Account identifiers, independently checked absent before the HTTP test. The reviewed GitHub code calls `_real_authority` **before any draft/scope creation**; test input was not a valid Finance proposal even if authorization were defective. This was a **negative-authorization HTTP milestone**, not a positive proposal or Accounting approval acceptance. Operator confirms no successful Finance mapping or posting requests. Ordinary session or error log metadata may have been generated.

**Remaining acceptance:** Successful authorized Maker+TISS draft creation, authenticated Checker review/approval of that draft, Maker self-approval denial, optimistic-version/race protection and rollback/stock/GL behavior **not tested**. Checker approval endpoint locates an existing mapping draft before role enforcement; a missing draft cannot test Checker-vs-Maker approval. Before any persistent test mapping, first perform a separately guarded **read-only Integration2 census** of mapping Scope/Revision rows and relevant existing fixture masters; then prepare a precise, small, auditable synthetic fixture plan, secure Accounting approval reference handling and backup/rollback strategy, and obtain the owner’s separate approval for the corresponding write transactions. Do not use the CI-only disposable fixture on persistent Integration2. Main DEVELOPMENT and PRODUCTION unchanged by the requested business tests. No secrets or session tokens shared.

### Read-only mapping inventory: empty for TISS and TREQ

**Owner-executed guarded SQL/Frappe inventory output** on Integration2, from the pinned reviewed CCPC app checkout:

```text
INTEGRATION2 FINANCE MAPPING INVENTORY
SITE AND COMPANY GUARDS: PASS
Expense TISS scopes: 0
Expense TISS revisions: 0
Expense TREQ scopes: 0
Expense TREQ revisions: 0
Center TISS scopes: 0
Center TISS revisions: 0
Center TREQ scopes: 0
Center TREQ revisions: 0
FINANCE MAPPING INVENTORY: COMPLETED
NO FINANCIAL DATA CHANGES
```

This establishes a **point-in-time absence of custom CCPC Expense/Center Scope and Revision records** for the fictional TISS and TREQ Companies. It does **not** establish that eligible Item Group, Company-owned expense Account, Department, or Cost Center masters exist, nor that using any present master would be safe. No new mapping, fixture, or master data was written.

**Next one-step test preparation:** Read-only census of eligible Item Group leaf records and TISS Expense-root non-group enabled Accounts (optional Center Department and Cost Center). Check whether only clearly tagged Integration2 synthetic masters can be selected without touching real master data. If none exist, design a synthetic fixture with exact required masters/owners/limits, proposed cleanup and isolated backup/restore strategy, and obtain explicit owner authorization before any write. A clean Scope/Revision census is necessary but not a substitute for a transaction and safety plan. PRODUCTION and main DEVELOPMENT remain untouched.

### Read-only TISS Expense master census: eligible counts, no clearly labeled test fixture

Owner executed the guarded **Integration2-only, read-only** Expense master preflight; the operator transcript reported:

```text
INTEGRATION2 EXPENSE MASTER PREFLIGHT
SITE AND COMPANY GUARDS: PASS
ELIGIBLE LEAF ITEM GROUP COUNT: 5
ELIGIBLE TISS EXPENSE ACCOUNT COUNT: 30
POTENTIAL TEST-LABELED ITEM GROUPS:
 NONE FOUND
POTENTIAL TEST-LABELED EXPENSE ACCOUNTS:
 NONE FOUND
EXPENSE MASTER PREFLIGHT: COMPLETED
NO MASTER OR FINANCIAL DATA CHANGES
```

This proves only that 5 global non-group Item Groups exist and 30 `Integration Test Issuer` Expense-root, enabled, non-group Accounts meet the reviewed code's initial structural criteria. Names containing case-insensitive `test` or `integration` were not found in either eligible candidate list. These weak string heuristics **cannot establish whether masters are synthetic or safe**, and they do not justify using unlabeled existing Item Groups or accounts for a positive HTTP mapping proposal. No mappings, master records, financial transactions or Company configuration changes were made.

**Next safe step:** A guarded read-only, local-only display of the five eligible Item Group names and the 30 TISS eligible Account names/metadata to classify candidates. Do not upload business records to GitHub or include credentials. If none is explicitly synthetic and separately approved, specify a purpose-named isolated Integration2 fixture (Item Group, expense Account, mapping revision) with verified prerequisites, backup/recovery procedure and narrow explicit owner approval before creating anything. Retain the current zero-mapping baseline for both TISS and TREQ, recheck immediately before a future transaction test. No PROD or main DEVELOPMENT modifications.

### Read-only Expense fixture master names: no dedicated Integration2 test master

**Owner-executed Integration2 test fixture candidate inventory** passed site and baseline checks and did not modify DB records:

```text
ELIGIBLE ITEM GROUPS:
Consumable
Products
Raw Material
Services
Sub Assemblies

TISS EXPENSE ACCOUNTS:
5150 - Intercompany Materials Expense - TISS (number 5150)
Administrative Expenses - TISS
Bank Charges - TISS
Commission on Sales - TISS
Cost of Goods Sold - TISS
Depreciation - TISS
Entertainment Expenses - TISS
Exchange Gain/Loss - TISS
Expenses Included In Asset Valuation - TISS
Expenses Included In Valuation - TISS
Freight and Forwarding Charges - TISS
Gain/Loss on Asset Disposal - TISS
Impairment - TISS
Interest Expense - TISS
Legal Expenses - TISS
Marketing Expenses - TISS
Miscellaneous Expenses - TISS
Office Maintenance Expenses - TISS
Office Rent - TISS
Postal Expenses - TISS
Print and Stationery - TISS
Round Off - TISS
Salary - TISS
Sales Expenses - TISS
Stock Adjustment - TISS
Tax Expense - TISS
Telephone Expenses - TISS
Travel Expenses - TISS
Utility Expenses - TISS
Write Off - TISS
```

Five eligible non-group Item Groups are generic global ERPNext names and not clearly synthetic; 30 TISS enabled Expense-root leaf Accounts are ordinary chart-of-accounts entries, including business-specific intercompany code 5150. **Do not designate any of them as a mapping test fixture by default.** There are still zero custom CCPC mapping scopes/revisions for TISS/TREQ from the immediately prior inventory.

**Risk verified in reviewed custom-app code** (`ccpcerp.ccpc_erp.bc_issue_runtime.resolve_locked_original_issue`, pinned app `0c223d7...`): original issue expense resolution explicitly selects approved Company+Item Group scopes and validated linked expense accounts. An approved Expense mapping for a generic existing group could be consulted by later issue tests. An isolated new Item Group plus a clearly named TISS-only synthetic Expense Account is safer, but neither should be created before verifying root/parent hierarchy, exact naming and absence of collisions, fresh site backup, transaction boundaries, no item/stock/GL posting, and the owner's separate explicit approval. A synthetic mapping's approval must not be described as deployment to main DEVELOPMENT/PRODUCTION.

**Next one-step read-only preflight:** Inspect `tabItem Group` root/parent hierarchy and TISS enabled Expense-root group Account parents, plus exact synthetic naming collisions and the current zero-scope baseline. Prefer showing metadata only, not raw chart of accounts exports. Then draft bounded test+cleanup+rollback procedure and request authorization for controlled Integration2 fixture creation and HTTP workflow checks. Never delete or rename existing records as an unapproved cleanup shortcut.

### Synthetic fixture hierarchy preflight: PASS — requires Company-tree check before any write

**Owner-reported 2026-10-27 Integration2-only read-only transcript** from pinned app and exact isolated site:

```text
INTEGRATION2 SYNTHETIC FIXTURE PREFLIGHT
SITE AND ZERO-MAPPING GUARDS: PASS
ITEM GROUP ROOT:
All Item Groups: PRESENT | Group: 1
AVAILABLE TISS EXPENSE PARENT ACCOUNTS:
Parent account count: 4
 - Direct Expenses - TISS | Parent: Expenses - TISS
 - Expenses - TISS | Parent: ROOT
 - Indirect Expenses - TISS | Parent: Expenses - TISS
 - Stock Expenses - TISS | Parent: Direct Expenses - TISS
EXISTING ACCOUNT 5150:
Parent: Indirect Expenses - TISS
Root type: Expense
Account type: None
PROPOSED SYNTHETIC NAME COLLISIONS:
Test Item Group: AVAILABLE
Test Expense Account name: AVAILABLE
SYNTHETIC FIXTURE PREFLIGHT: COMPLETED
NO MASTER OR FINANCIAL DATA CHANGES
```

The user has **not approved any persistent fixture or Finance mapping creation/approval**. Proposed precise names, still hypothetical:
- Item Group `CCPC INT2 Expense Mapping Test 20261027`, `is_group=0`, parent `All Item Groups`. Do not assign Items or Item defaults.
- TISS-only Expense Account `CCPC INT2 Expense Mapping Test`, no account number, intended parent `Indirect Expenses - TISS`, `is_group=0`, `disabled=0`, Expense root inherited. ERPNext account autoname should yield `CCPC INT2 Expense Mapping Test - TISS` (verify at execution).
- Proposed CCPC Expense mapping of synthetic Item Group to synthetic TISS Expense Account, one Maker-created Draft, Checker-controlled review; a separate *approval write* requires a further explicit Accounting-fixture decision, unique synthetic reference and observed version token. No original Withdrawal Slip issue, Stock Entry, or GL posting authorized.

**New code-review risk:** ERPNext version-16 `Account.validate_root_company_and_sync_account_to_children` (account.py) can **automatically replicate a new parent-Company Account to descendant companies** or enforce root-first account creation for a child Company. This means a TISS Account insert is not guaranteed to affect TISS alone. **Block all creation until read-only Company nested-set parent/ancestors/descendants and `allow_account_creation_against_child_company` are checked and cross-company side effects ruled out.** Also reconfirm exact source/target absence, parent Account enabled/group/Expense state, counts of mapping scopes/revisions, bank/Company/site backups, and protected checkout immediately before a future write. No permission to bypass ERPNext account validation flags, force-save, use arbitrary default accounts, or delete/overwrite any records.

A suitable next test is a read-only, pinned-application `frappe.db` check of `TISS` Company hierarchy and parent Account fields; return only nonsecret structural metadata and no writes. If TISS has descendants or disallowed root-level account creation, stop and redesign the test fixture, rather than silently allowing propagation. After this, document per-transaction rollback and fixture retention vs cleanup options, verify a **fresh Integration2-specific backup** and receive explicit user approval before making any test masters.

### Company hierarchy isolation preflight: PASS; no authorisation for writes

The owner executed the guarded **Integration2-only read-only** follow-up (no master or Finance data changes):

```text
INTEGRATION2 COMPANY HIERARCHY PREFLIGHT
SITE AND COMPANY GUARDS: PASS
TISS PARENT: NONE
TISS ANCESTOR COUNT: 0
TISS DESCENDANT COUNT: 0
CHILD COMPANY ACCOUNT CREATION ALLOWED: 0
PROPOSED ACCOUNT PARENT:
IS GROUP: 1
DISABLED: 0
ROOT TYPE: Expense
ACCOUNT TYPE: NONE
CROSS-COMPANY CREATION RISK: NO TISS DESCENDANTS
ROOT-COMPANY ACCOUNT RULE: NO IMMEDIATE BLOCKER
COMPANY HIERARCHY PREFLIGHT: COMPLETED
NO MASTER OR FINANCIAL DATA CHANGES
```

**Decision:** At test time `Integration Test Issuer` (TISS) has neither Company parent nor descendants; intended existing Account parent `Indirect Expenses - TISS` is an enabled Expense-root group without account_type. The reviewed ERPNext v16 Account model's root/child-Company replication rule therefore has no *currently identified* Company-tree trigger for cross-company replication in this site. Revalidate this dynamic state before creating an Account; no guarantee of zero side effects beyond this guarded scenario. The proposed synthetic Item Group remains site-global, so do not attach real Items or Item Defaults; keep it distinguishable from ordinary CCPC categories.

**Pending, not approved:** Creating `CCPC INT2 Expense Mapping Test 20261027` (leaf Item Group under `All Item Groups`) and `CCPC INT2 Expense Mapping Test - TISS` (new unnumbered TISS-only Expense ledger under `Indirect Expenses - TISS`), a Maker-owned Draft CCPC Expense mapping between them, and any Checker mapping approval require specifically scoped user approval. The approved G1/G2 design principles in GitHub are **not** authorization for real account creation or mapping activation. Finance mapping approval is separate from data fixture creation, and no Stock Entry, GL Entry, issue, billing, migration, production change, or general shared-development master change is proposed.

**Backup and rollback gate before authorization:** The October 27 10:48 Integration2 four-artifact protected preintegration snapshot is historical and must be preserved. Independently inspect its continued presence, current Integration2 site/database binding, backup utility availability and dedicated free space; create/verify a new Integration2-only 4-artifact pre-fixture backup only after owner permission, keeping any created snapshots outside the protected checkout and not inside public file directories. The new backup must include compressed SQL database, public files, private files and site-config archive, have nonzero sizes and integrity checks, and be retained through acceptance. Restoration is an explicitly separately authorized, potentially destructive recovery action; it is not an automatic test rollback, particularly because Integration2 shares infrastructure with main DEVELOPMENT and PRODUCTION. Failure of any fixture operation must abort/rollback its own transaction without touching existing masters and preserve evidence; test records should be retained for audit unless independently approved cleanup validates all dependencies. No passwords, secrets, or config file contents in GitHub/chat.

### Protected backup file presence and capacity preflight: PASS (not restore proof)

The owner ran the guarded, **Integration2-only read-only** backup readiness inspection on the existing pinned application checkout, without touching main DEVELOPMENT/PRODUCTION. The operator reported:

```text
INTEGRATION2 BACKUP READINESS CHECK
APPLICATION AND SITE GUARDS: PASS
database.sql.gz: PRESENT
files.tar: PRESENT
private-files.tar: PRESENT
site_config_backup.json: PRESENT
PROTECTED BACKUP COMPONENTS: 4/4 PRESENT
BACKUP DIRECTORY SIZE: 1.1M
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  915G  184G  686G  22% /workspace
BACKUP READINESS INSPECTION: COMPLETED
NO FILE OR DATABASE CHANGES
```

The original protected snapshot prefix is `20261027_104801-ccpc-integration2_localhost-` in `sites/ccpc-integration2.localhost/private/ccpc-preintegration-2026-10-27/fresh-backup/`. Those four files are nonempty and present, not necessarily valid/restorable. Their contents were **not** integrity-tested or restored by this read-only command. 686 GiB free on the backing filesystem was reported at the time of inspection.

**Near-term follow-up:** Validate compressed SQL with `gzip -t`, public/private TAR central structure with `tar -tf ... >/dev/null`, site-config JSON parsing without printing content; preserve existing files. Then obtain **explicit authorization** for a fresh Integration2-only pre-fixture four-artifact Frappe backup, placed in an isolated non-web-accessible directory *outside both site's source tree and existing protected backup*, with suitable permissions, exact site scoping, completeness and checksums. Do not treat integrity checks as restore rehearsal or suggest automatically restoring a shared-environment DB. No account/Item Group/Finance mapping creation or approval yet; application deployment, service restarts, main DEVELOPMENT and PRODUCTION outside scope.
