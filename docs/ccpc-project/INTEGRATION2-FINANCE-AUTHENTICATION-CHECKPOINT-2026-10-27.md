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

### Protected backup structural integrity: PASS (not restore validation)

The owner executed the previously issued guarded **Integration2-only read-only** check for the preintegration protected four-part backup and supplied this exact status output:

```text
INTEGRATION2 BACKUP INTEGRITY CHECK
APPLICATION AND SITE GUARDS: PASS
DATABASE GZIP INTEGRITY: PASS
PUBLIC FILES TAR STRUCTURE: PASS
PRIVATE FILES TAR STRUCTURE: PASS
SITE CONFIG JSON STRUCTURE: PASS
BACKUP ARCHIVE CHECK: COMPLETED
NO FILE OR DATABASE CHANGES
```

The command performed `gzip -t` on the protected SQL `.gz`, `tar -tf ... >/dev/null` for both public and private TARs, and Python `json.load` on the site-configuration JSON without printing its contents. These format checks establish readable envelope structure for each existing archive; **they do not establish that SQL will successfully import, ERPNext can boot after restoration, foreign keys and attachments reconcile, or that backup artifacts are a consistent application snapshot**. The historical protected backup remains preserved, and no restore was attempted.

**Next explicitly gated operation (not yet approved):** Ask the owner to authorize one fresh **Integration2-only** pre-fixture four-artifact Frappe backup with `--with-files`, captured under a newly created, non-web-accessible, restricted-permission directory distinct from the preintegration snapshot and main DEVELOPMENT/PRODUCTION backups. Do not assume a specific directory exists; verify it and filesystem/permissions independently. Validate nonempty database, site-config, public/private files; run format checks and optional private checksum manifest without disclosing site config, passwords or secrets. The operation is expected to write backup files and may briefly load shared filesystem/DB services; main DEVELOPMENT and PRODUCTION sites, databases, containers, migrations, and applications remain untouched. **No synthetic Item Group, Account, mapping Draft, Accounting approval, withdrawal issue, Stock Entry or GL Entry is authorized by backup permission.** Restoration and cleanup remain separately gated, no automatic rollback/restore.

### Explicit owner approval for fresh Integration2 backup (execution pending)

After confirmation of nonempty/format-validity of four existing protected preintegration backup artifacts, the owner explicitly replied **"Approved"** to: "Do you approve creating and verifying this fresh backup for `ccpc-integration2.localhost` only?" The scope approved is one new pre-fixture **Integration2-only** four-artifact Frappe recovery set (full DB dump, site config, public/private files) in a newly created nonpublic, restricted-permission directory; verify file sizes and formats, optionally local-only checksums. It does **not** approve any fixture Item Group or Account creation, mapping proposal, mapping approval, withdrawal issue, stock/GL posting, restore, deletion, migration, restarts, main DEVELOPMENT or PRODUCTION action.

**Critical Frappe v16 source review:** `frappe.utils.backups.new_backup` calls `delete_temp_backups()` before constructing `BackupGenerator`, and `bench --site ... backup` uses that helper. This can delete aged files in the site's default backup directory, beyond approved write scope. A safe execution should instantiate `BackupGenerator` **directly** with `ignore_conf=True`, `compress_files=False`, and explicit unique `backup_path`, then `get_backup(force=True,ignore_files=False)`, avoiding the default retention-cleanup helper. Strictly check site/app checkout, explicit site versus main DEV distinct DB identity, protected historical 4/4 still present, auto-encryption compatibility, folder identity and restrictive permissions before writes. Do not log site config/database credentials, and do not remove partial output automatically. A failed backup is STOP and evidence for review.

Expected output is a new, uniquely named four-file archive set within a private site-specific backup folder, with gzip/TAR/JSON format PASS and checksum manifest stored locally, not in GitHub. Backup writes and modest shared DB/disk load are approved; they do **not** establish restore viability. Operator execution and actual files are **pending verification**; GitHub documentation here is not a claim that backup has already been created.

### Fresh Integration2 pre-fixture backup: PASS — owner-executed verification

After specific owner approval for **Integration2-only backup creation**, the owner executed the guarded Frappe v16 `BackupGenerator` direct-call procedure with a uniquely named, private, mode-0700 directory, avoiding `new_backup` default backup retention cleanup. Exact operator output:

```text
INTEGRATION2 FRESH PRE-FIXTURE BACKUP
APPLICATION AND SITE ISOLATION: PASS
PROTECTED HISTORICAL BACKUP: 4/4 PRESENT
DATABASE IDENTITY: PASS
BACKUP ENCRYPTION COMPATIBILITY: PASS
NEW BACKUP DIRECTORY: /workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-finance-prefixture-20261027-u76kev1a
DATABASE: PASS (1,101,731 bytes)
PUBLIC FILES: PASS (10,240 bytes)
PRIVATE FILES: PASS (10,240 bytes)
SITE CONFIG: PASS (212 bytes)
FOUR BACKUP COMPONENTS: VERIFIED
SHA256 MANIFEST: CREATED
HISTORICAL BACKUP HASHES UNCHANGED: PASS
INTEGRATION2 FRESH BACKUP: PASS
NO FINANCE MASTER OR MAPPING CHANGES PERFORMED
NO RESTORATION PERFORMED
```

**Bounded verification:** The new Integration2-only snapshot contains four nonempty, correctly named backup files and a private local `SHA256SUMS` manifest. The operator script checked SQL gzip integrity, public/private TAR structure, site-config JSON and DB identity, restricted file permissions, pinned checkout, separate main DEV database, and original protected four-file SHA-256 consistency. No password, session ID, DB password, backup contents or site configuration was copied into GitHub or chat. These checks do not establish restorability, cross-artifact consistency under concurrent writes, or off-host recovery. The historical protected preintegration backup remains unchanged according to hash comparison. Output indicates no Finance master/mapping mutation or restoration. No access to production or main DEVELOPMENT was authorized.

**Next independently gated proposal — TWO isolated test masters only, not approved yet:** On `ccpc-integration2.localhost` (fictional Company `Integration Test Issuer`, `TISS`), propose exactly:
1. An Item Group with name `CCPC INT2 Expense Mapping Test 20261027`, leaf `is_group=0`, parent `All Item Groups`, with no Items or Item Group defaults.
2. An unnumbered, active, nongroup, Expense-root Account with `account_name=CCPC INT2 Expense Mapping Test`, parent `Indirect Expenses - TISS` and company `Integration Test Issuer`. Expected auto-generated name `CCPC INT2 Expense Mapping Test - TISS` (verify through Frappe). No default account assignment.

Prior nonmutating guards passed zero TISS/TREQ mapping scopes/revisions, absent proposed names, parent Item Group and Expense Account eligibility, and zero TISS Company ancestors/descendants. **Recheck all prerequisites, backup files/manifest and dynamic Company hierarchy immediately before write.** If user separately authorizes, use a single, guarded, ORM/transaction-bound setup with no validation bypass and explicit rollback on error; commit only after verifying exact new records and no other Company Account with the synthetic `account_name`. Do not create mapping Draft, authorize Checker approval, post GL/stock, or restore a backup. Frappe nested-set maintenance and cache/metadata effects may accompany master inserts even with correct checks. Successful fixture records should remain labeled and retained for review; subsequent cleanup or restore needs separate risk review and explicit approval.

### Explicit owner approval for two synthetic Integration2 masters — creation pending

Immediately after verifying the fresh four-artifact Integration2 pre-fixture backup and its preserved historical-backup hashes, the project owner replied **"Approved"** to the *separately scoped* question: "Do you approve creating these two synthetic master records in Integration2 only?" Exact authorized records, and only these:
1. `Item Group` `CCPC INT2 Expense Mapping Test 20261027`, parent `All Item Groups`, leaf `is_group=0`, no Item Group Defaults, no Item assignment.
2. TISS-only unnumbered Expense-root `Account` with `account_name=CCPC INT2 Expense Mapping Test`, generated name expected `CCPC INT2 Expense Mapping Test - TISS`, company `Integration Test Issuer`, parent `Indirect Expenses - TISS`, `is_group=0`, `disabled=0`. No Company default-account configuration.

**Authorized execution bounds:** Single guarded ORM transaction against only `ccpc-integration2.localhost`, using normal ERPNext validation, with fresh preflight of pinned detached app revision, clean protected tracked worktree/untracked `AGENTS.md` only, backup directory `sites/ccpc-integration2.localhost/private/ccpc-finance-prefixture-20261027-u76kev1a` and 4-file SHA256 manifest, original four backup files, distinct site/database identity from main DEV, zero TISS/TREQ mapping scopes/revisions, exact name nonexistence, unchanged eligible parents, and zero TISS Company ancestors/descendants. Explicit rollback on a pre-commit error, and fail-closed behavior with no auto-retry on uncertainty. ERPNext nested-set parent indices/caches may change as an inherent effect of normal master creation. Commit only after checking the exact two new records, counts and absence of financial postings or cross-Company account creation. No bypass of validations. Record actual output and verify persistence after operator executes; no edits can be claimed yet.

**Not authorized:** A Maker Draft or Checker approval, any CCPC Expense/Center mapping scope/revision, Account numbering, other Company accounts, stock movement, GL posting, billing, data cleanup/restore, service restart, migration, branch switch, main DEVELOPMENT changes or PRODUCTION access. No credentials, database contents or backups in GitHub. New records remain clearly tagged, retained pending the separate next test and cleanup decision.

### Two synthetic Integration2 master inserts: owner-reported PASS (commit witnessed by operator)

On 2026-10-28 (Asia/Manila), following the prior narrow owner approval and complete verified pre-fixture local backup, the owner executed the supplied guarded **Integration2-only** two-master Frappe ORM transaction. Actual reported terminal output:

```text
INTEGRATION2 TWO SYNTHETIC MASTERS
NEW BACKUP CHECKSUMS AND ARCHIVES: PASS
HISTORICAL BACKUP: PRESENT
MASTER AND MAPPING PREFLIGHT: PASS
TWO-MASTER TRANSACTION VALIDATION: PASS
SYNTHETIC ITEM GROUP: CREATED AND COMMITTED
SYNTHETIC TISS EXPENSE ACCOUNT: CREATED AND COMMITTED
TWO SYNTHETIC MASTER RECORDS: PASS
NO FINANCE MAPPING, GL OR STOCK TRANSACTIONS CREATED
HISTORICAL AND NEW BACKUPS: UNCHANGED
```

**Bounded result:** The operator script checked pinned detached app HEAD `0c223d7...` and protected checkout `?? AGENTS.md`; existing four-part Integration2 backup SHA-256 manifest and historical protected files; separate Integration2/main DEV DB identity; zero TISS/TREQ custom Finance mapping scopes; valid Company tree and parent eligibility; no name collisions; then used ordinary Frappe DocType ORM `.insert()` for precisely:
- leaf Item Group `CCPC INT2 Expense Mapping Test 20261027` beneath `All Item Groups` (no Item links);
- unnumbered, nongroup, enabled Expense Account `CCPC INT2 Expense Mapping Test - TISS` in `Integration Test Issuer`, parent `Indirect Expenses - TISS`.

Before the single `frappe.db.commit()`, the procedure verified actual field values, only one synthetic account name across Companies, and unchanged table counts for Company, Item, GL Entry, Stock Ledger Entry, and both mapping revision DocTypes; Item Group and Account table counts increased by one each. Backup SHA-256 comparisons passed. The owner-reported transcript explicitly confirms the transaction **was committed** and no GL, stock or mapping records were created. This is successful **operator-run Integration2 verification**, not an independent postcommit database read by ChatGPT; no direct container connection is available.

**Next bounded read-only step:** independently reconnect to `ccpc-integration2.localhost` to verify the two newly committed records, exact fields and parent relationships, no Item assignment and still zero CCPC Expense/Center scopes/revisions in TISS/TREQ. Do not recreate the masters or rerun the successful transaction. After postcommit readback, prepare one narrow **Maker-owned Draft** proposal on the synthetic Item Group and synthetic TISS Account for separate user authorization, followed by independent Checker review/authorization steps. No Checker approval, Version audit activation, GL posting, stock movement, restarts, migration, cleanup, restoration, changes to main DEVELOPMENT or PRODUCTION have been authorized.

### Independent post-commit synthetic master readback: PASS

Following the committed Integration2-only two-master ORM transaction, the project owner executed a **separate, read-only Frappe DB connection** with the same guarded pinned app HEAD, exact isolated site `ccpc-integration2.localhost`, and Company TISS:

```text
INTEGRATION2 POST-COMMIT MASTER VERIFICATION
SITE AND COMPANY GUARDS: PASS
SYNTHETIC ITEM GROUP PERSISTED: PASS
ITEM ASSIGNMENTS AND DEFAULTS: NONE
SYNTHETIC EXPENSE ACCOUNT PERSISTED: PASS
CROSS-COMPANY ACCOUNT DUPLICATES: NONE
TISS AND TREQ MAPPING SCOPES: ZERO
POST-COMMIT MASTER VERIFICATION: PASS
NO DATABASE CHANGES
```

**Verified bounds:** The owner-operated independent read checks `Item Group` `CCPC INT2 Expense Mapping Test 20261027` is leaf, parent `All Item Groups`, has no Item Group Defaults or assigned Items; the `Account` `CCPC INT2 Expense Mapping Test - TISS` has expected name, no account number, company `Integration Test Issuer`, parent `Indirect Expenses - TISS`, Expense/Profit and Loss, leaf and enabled. Exactly one Account with this synthetic `account_name` exists across companies. Both TISS and TREQ have zero `CCPC Expense Mapping Scope` and `CCPC Center Mapping Scope` rows at the time of readback. No persistent Finance mapping proposal or approval was created by this inspection.

**Next independent owner approval gate:** The reviewed `ccpcerp.ccpc_erp.bc_mapping_workflow.propose_mapping` endpoint (pinned app `0c223d7...`) requires the authenticated actual Maker Role/Company grant before it creates a custom Expense Scope and revision in `Draft` state. Proposed **one and only one** new TISS Expense mapping: `kind=Expense`, `company=Integration Test Issuer`, `source=CCPC INT2 Expense Mapping Test 20261027`, `value=CCPC INT2 Expense Mapping Test - TISS`, `effective_from`/ `effective_until` empty (effective time not activated until separately approved). It will produce **two persistent custom mapping records**: one `CCPC Expense Mapping Scope` and one `CCPC Expense Mapping Revision` (Draft, revision 1), not a ledger posting. After separate explicit approval, use the real authenticated Maker HTTP/CSRF session; require fresh zero-scopes guard, replay/duplicate prevention, exact state/owner and no GL/stock change, and persist/readback revision ID carefully. **Do not invoke** Checker approval until a further separate authorization and Accounting reference review. No stock issue, GL posting, PRODUCTION, main DEVELOPMENT, backup restore, cleanup or migrations authorized.

### Owner authorization: one Maker-only synthetic TISS Expense Draft (HTTP execution pending)

The owner replied **"Approved"** to the separately scoped proposal: "Do you approve creating exactly one synthetic TISS Expense mapping Draft in Integration2 using the authenticated Finance Maker account?" This is **explicit permission for precisely one authenticated, CSRF-protected HTTP proposal POST** to `ccpcerp.ccpc_erp.bc_mapping_workflow.propose_mapping` on isolated `ccpc-integration2.localhost` with fields:
- `kind=Expense`
- `company=Integration Test Issuer`
- `source=CCPC INT2 Expense Mapping Test 20261027`
- `value=CCPC INT2 Expense Mapping Test - TISS`
- no explicit effective time interval.
- authenticated Maker `ccpc-dev-finance-maker@invalid.test`, not Administrator or Checker.

Expected persistent records only: one `CCPC Expense Mapping Scope` for the exact company/source, and revision `CCPC Expense Mapping Revision` revision_no=1, `Draft`, owner Maker, no approval fields. The app review branch remains `review/circleci-isolated-erpnext-phase2-2026-10-26` at `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`; the actual local checkout must be rechecked. Local Frappe v16 Desk template includes `frappe.csrf_token = "{{ csrf_token }}";`, supporting session+Desk extraction. Separate Maker login and `/api/method/frappe.auth.get_logged_user` identity must PASS before the single POST. Read-only database and protected backup safeguards (including fresh four-artifact checksum manifest) and zero mapping scopes must PASS before login. Never print Maker password/session SID/CSRF; use TTY-only private no-echo prompt. **One HTTP proposal attempt only; if response is unknown, timeout or postcheck fails, STOP—never retry without a new read-only inventory.**

This authorization does **not** extend to Checker review/approval, an `Approved` revision, Accounting reference, changes to mapping master data, Cost Center, GL/stock/issue postings, intercompany billing, backup restore, cleanup, service restart, app branch switch, migration, main DEVELOPMENT or PRODUCTION. All subsequent actions independently gated. Operator execution/output not yet received; do not record PASS prematurely.

### Authenticated synthetic Maker Draft attempt: STOP at login — **NO PROPOSAL POST**

On 2026-10-28 (Asia/Manila) the owner executed the guarded, narrowly approved Integration2-only Maker proposal script. Actual terminal output:

```text
INTEGRATION2 AUTHENTICATED MAKER DRAFT TEST
APPLICATION AND BACKUP GUARDS: PASS
MASTER, ACTOR AND ZERO-MAPPING GUARDS: PASS
Maker password:
INTEGRATION2 MAKER DRAFT TEST: STOP
STAGE: MAKER LOGIN
ERROR TYPE: RuntimeError
REASON: Maker login failed
NO FINANCE PROPOSAL POST WAS ATTEMPTED
```

The script checked `response.status_code==200`, response JSON `message=="Logged In"`, and a nonempty/non-Guest `sid` cookie in one combined assertion. Because it did not report the HTTP status/message/cookie result separately, **cause is not yet isolated**. Previous Maker+Checker login and CSRF passes were verified in earlier operator tests, but do not establish today's credentials/session state. The original output expressly proves `propose_mapping` HTTP POST was **not attempted**. Thus creation of new mapping Scope/Draft revision remains **unverified and not expected**; no approval or accounting activation occurred. Do not rerun the complete proposal script or reset/change credentials speculatively.

**Next safe diagnostic:** One narrow, single-attempt Maker login-only probe on the same pinned Integration2 host/site with a private no-echo password prompt, and sanitized output: HTTP status, recognized message classification (allowlisted only), presence of an authenticated SID cookie (not its value), and exact Maker identity when login actually succeeds. Keep the app/site and database isolation guards and avoid all Finance proposal/approval endpoints. Authentication itself may create session or failed-login metadata; it is not a financial write. Stop after a failed probe; avoid repeated password guesses and lockout. Depending on result, distinguish credentials/policy versus HTTP/session handling, and independently inspect zero mapping scopes before any future proposal attempt. No Checker approval, credential reset, database restore, restart, main DEVELOPMENT or PRODUCTION action authorized.

### Maker login failure explained by operator; guarded one-time retry permitted

Following the failed Maker-only login stage (before any Finance mapping HTTP POST), the owner clarified: **"I entered the wrong password."** This is the operator's explanation of the failed login; no credentials were disclosed or modified, and the underlying response status/message were not separately measured.

The authorized original one-Draft test was **not consumed** because its own output confirmed `NO FINANCE PROPOSAL POST WAS ATTEMPTED`. The owner can re-execute the previously supplied **full guarded Maker Draft** test a single time with the correct existing *Maker* password, rather than using the now-unnecessary login diagnostic. It must recheck the app/site/backup identities, synthetic masters, and zero existing TISS/TREQ mapping scopes before the single authenticated `propose_mapping` POST. If any guard fails or a proposal POST is attempted with an unknown result, STOP; don't retry until a read-only mapping inventory. No Checker approval, GL/stock posting, password reset, PROD or main DEV change is authorized.

### Synthetic TISS Expense Maker Draft: authenticated POST PASS — not approved

On 2026-10-28 (Asia/Manila), after the owner's explicit one-Draft authorization and clarification that the first failed Maker login used the wrong password, the owner re-executed the guarded Integration2 authenticated Maker HTTP proposal script with the correct existing Maker credentials. Owner-supplied terminal result:

```text
INTEGRATION2 AUTHENTICATED MAKER DRAFT TEST
APPLICATION AND BACKUP GUARDS: PASS
MASTER, ACTOR AND ZERO-MAPPING GUARDS: PASS
Maker password:
MAKER AUTHENTICATED IDENTITY: PASS
MAKER DESK AND CSRF: PASS
MAKER EXPENSE DRAFT HTTP POST: PASS
PERSISTED DRAFT AND MAKER OWNERSHIP: PASS
TREQ AND CENTER SCOPES UNCHANGED: PASS
NO GL, STOCK OR MASTER COUNT CHANGES: PASS
EXPENSE SCOPE ID: fie8da5c59
DRAFT REVISION ID: fieef2e44j
INTEGRATION2 MAKER DRAFT TEST: PASS
NO CHECKER APPROVAL OR FINANCIAL POSTING PERFORMED
```

**Verified result by operator procedure:** Actual Frappe HTTP POST `ccpcerp.ccpc_erp.bc_mapping_workflow.propose_mapping` was invoked as authenticated `ccpc-dev-finance-maker@invalid.test` with Desk CSRF header; HTTP response reported a first `Draft` revision. A separate Frappe read-only post-request database connection validated precisely one TISS `CCPC Expense Mapping Scope` `fie8da5c59`, with source `CCPC INT2 Expense Mapping Test 20261027`, and exactly one `CCPC Expense Mapping Revision` `fieef2e44j`, `revision_no=1`, `approval_state=Draft`, owner Maker, Expense Account `CCPC INT2 Expense Mapping Test - TISS`, no approval identity/reference/timestamp or effective interval, and no alternate TISS/TREQ or Center mapping scopes. The procedure checked same GL, stock, Item, Account and related master counts as before the proposal. The fresh protected 4-component backup was verified before the POST. There was **no Checker approval, GL posting, stock movement, database migration, app branch change or PRODUCTION activity**.

**Status and next gate:** Integration2 Maker Draft creation and persistence are **PASS by owner-run authenticated HTTP and independent DB readback evidence**, not a claim of approval/activation or real-account use. Keep identifiers `fie8da5c59` and `fieef2e44j` stable; do not rerun the proposal. The next proposed validation is an **independent authenticated Checker review only** using exact revision `fieef2e44j` and the `get_mapping_review(kind=Expense,revision=...)` endpoint with session/CSRF, checking the returned owner, value, Draft status, modified/version token (do not publish session/CSRF tokens). That endpoint takes a server-side lock and performs read-oriented operations, **not** approval; a real login may create session metadata. Ask owner for specific separate approval before Checker review. A still-further and separate formal decision would be required for `approve_mapping` and a genuine Accounting approval reference; never fabricate an approval reference. No stock/GL posting, main DEVELOPMENT or PRODUCTION activity, restoration, cleanup, Maker replacement proposal, or auto-repeat is approved.

### Owner authorization: authenticated Checker review-only — execution pending

After verified Maker Draft `fieef2e44j` (TISS Expense Scope `fie8da5c59`, Maker `ccpc-dev-finance-maker@invalid.test`), the owner expressly answered **"Approved"** to: "Do you approve proceeding with the authenticated Checker review-only test in Integration2?"

**Exact authority:** Use the real `ccpc-dev-finance-checker@invalid.test` user with an operator-supplied private password, Frappe cookie session and Desk CSRF token to issue **only one authenticated POST** to `ccpcerp.ccpc_erp.bc_mapping_workflow.get_mapping_review` with `kind=Expense` and `revision=fieef2e44j`, against only `ccpc-integration2.localhost`. The endpoint is POST-only but read-oriented: its implementation checks exact Checker role/TISS Company grants, locks TISS Company and the mapping Scope/Revision `FOR UPDATE`, and returns current server fields/optimistic `modified` token. Expected fields: name `fieef2e44j`, company `Integration Test Issuer`, source `CCPC INT2 Expense Mapping Test 20261027`, value `CCPC INT2 Expense Mapping Test - TISS`, owner independent Maker, state `Draft`, blank effectiveness and supersession, change `New`, nonempty modified timestamp. Inspect database before and after the HTTP request to confirm Draft remains unapproved, IDs/counts unchanged and no GL/stock/master count changes; do not print passwords, session IDs or CSRF.

**No approval:** `approve_mapping`, `reject_mapping`, any modification/activation, Accounting reference creation, Finance master changes, issue/stock/GL posting, credentials reset, backup restoration, service restarts, main DEVELOPMENT or PRODUCTION actions remain explicitly unapproved. The Checker login might update HTTP session or auth metadata; that is distinct from financial records. If preflight, login or response validation fails, STOP and inspect state. Actual Checker review result is **pending**.

### Authenticated Checker review-only: PASS (owner-executed, 2026-10-28)

The operator reported `INTEGRATION2 CHECKER REVIEW-ONLY TEST: PASS` for the isolated site `ccpc-integration2.localhost` and pinned app at `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. The preflight passed app/backup checks, actual Checker role and TISS Company grant, and exact Maker-owned Draft. The real Checker login, authenticated identity, Desk CSRF, and POST-only `ccpcerp.ccpc_erp.bc_mapping_workflow.get_mapping_review` all passed. Response confirmed Maker owner, TISS synthetic Expense Account and Item Group, Draft state, and unchanged `modified` review token.

**Persisted IDs:** TISS Expense Scope `fie8da5c59`; Expense Draft Revision `fieef2e44j` (revision 1). The separate read-only DB postcheck confirmed the Draft remained unapproved, the revision version did not change, and no Finance mapping, GL, stock, or master count changes occurred. No approval endpoint or financial posting was attempted. No secrets, passwords, cookie values or CSRF values were disclosed.

**Next boundary:** Checker review is verified, but `approve_mapping` is **not authorized**. It would write Approved state, audit Version, and effective timestamp potentially consumed by issue-runtime accounting. Require separately scoped owner consent and genuine Accounting approval evidence after reviewing activation/rollback risks. Prefer a read-only approval safety review first. Do not create another Draft, make stock/GL postings, modify main DEVELOPMENT or PRODUCTION, restore backups, or restart services without distinct authorization.

### Read-only Finance approval safety review: owner approved; static source findings and runtime gate

After the operator-confirmed authenticated Maker Draft and Checker review-only PASS, the project owner explicitly approved **the read-only approval safety review first, without activation**. This is **not approval of the mapping** and not authorization to run `approve_mapping`.

**Pinned code reviewed**: App branch `review/circleci-isolated-erpnext-phase2-2026-10-26`, HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. `ccpcerp/ccpc_erp/bc_mapping_workflow.py`, `bc_mapping_policy.py`, `bc_issue_runtime.py`, `withdrawal_slip_stock.py`, DocType controller `ccpc_expense_mapping_revision.py` and `ccpcerp/hooks.py`. Docs branch verified at start of review.

**Static findings:**
- `approve_mapping` requires a named authenticated Checker with exact role/company permission, independent Maker, fresh exact Draft `modified` token, valid synthetic Company/Item Group/Expense Account and a Company/scope/revision locking order. It checks interval overlap and sets server-owned `approved_at` and `effective_from` no earlier than approval.
- The endpoint directly updates Approved fields in SQL, then inserts a `Version` row with reviewed decision details in the same HTTP transaction. A failed database transaction should roll back both together; **no live approval/audit behavior has yet been exercised**. The Version audit is not a cryptographic independent signature.
- `approval_reference` is checked only as a canonical nonempty string, maximum 140 characters. The endpoint **does not independently look up or verify genuine Accounting approval evidence**; the operator must not invent a reference to pass a test.
- The reviewed workflow module exposes `propose_mapping`, `get_mapping_review`, and `approve_mapping`; **no reversible rejection/revocation/deactivation endpoint is present** in that file. Ordinary revision controller rejects non-Draft state through normal validate/save and disallows deletion. Before authorizing activation, resolve a separately authorized controlled deactivation/cleanup plan; never use blind DB edits or destructive site restore as a routine rollback.
- `withdrawal_slip_stock.py` actually imports/calls `assign_original_issue_b_c` during stock issue construction, and `validate_original_issue_b_c` before submission; `hooks.py` wires the Withdrawal Slip Stock Entry validators. The resolver filters Approved/temporally effective scope revisions, and requires a unique approved Center scope; incomplete prerequisites fail closed. A newly approved Expense mapping can affect eligible future TISS Item Group issue accounting, subject to the remaining policy gates.
- The synthetic Item Group was previously observed with **zero linked Items and no Item Group Defaults**, and TISS/TREQ Center scopes were zero. These were historical checks and need a fresh read-only verification; the group is global and could later be assigned to real Items. No current assertion that approvals would be harmless can rely on earlier snapshots alone.
- Protected recovery assets remain local snapshots, not an off-host or proven restorable recovery procedure. Restoring an old site backup would overwrite newer approved integration records and needs entirely separate authorization.

**Next gate: runtime-only inspection, NOT approval.** Re-verify exact isolated site/database/app checkout, backup manifest, scope `fie8da5c59` and revision `fieef2e44j` remain Maker-owned Draft without effective/approval fields, current Checker/Maker roles/grants, no linked Items/Item Group defaults, zero other TISS/TREQ scope/revisions, no synthetic-account GL/stock references or other defaults, Company tree isolation, and Version/audit counts. Use read-only Frappe connection followed by explicit `frappe.db.rollback()`. No login, review API call, approval, service restart, migration, fixture creation, stock/GL posting or PRODUCTION interaction in this phase. Next approval decision requires separately scoped owner permission, accounting decision evidence and a safe fallback plan. Runtime inspection results are pending, not yet PASS.

### Approval safety runtime preflight: PASS — operator read-only report, no activation

On 2026-10-28 (Asia/Manila), the project owner ran the previously authorized **read-only Integration2 approval safety preflight** and provided the following output:

```text
INTEGRATION2 APPROVAL SAFETY PREFLIGHT
SITE ISOLATION AND BACKUP CHECKSUMS: PASS
TISS COMPANY ISOLATION: PASS
MAKER AND CHECKER AUTHORITY: PASS
SYNTHETIC MASTERS AND ITEM ISOLATION: PASS
DRAFT STATE AND MAPPING ISOLATION: PASS
SYNTHETIC GL AND STOCK REFERENCES: ZERO
EXISTING REVISION VERSION RECORDS: 0
APPROVAL SAFETY DATABASE PREFLIGHT: PASS
REVISION STATUS: Draft
NO APPROVAL OR FINANCIAL DATA CHANGES
```

**Verified via owner-run checks:** Application was guarded at pinned detached review commit `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`; Integration2 DB was separated from main DEVELOPMENT; the private prefixture backup's four SHA-256 hashes matched; TISS Company has no ancestors or descendants. Named Maker and Checker users remained enabled, distinct, with expected roles and explicit TISS grants and no Stockroom Personnel role. Synthetic Item Group `CCPC INT2 Expense Mapping Test 20261027` had no linked Items/defaults; the synthetic TISS Expense Account `CCPC INT2 Expense Mapping Test - TISS` remained active, unnumbered, correctly scoped, and unique by account title.

TISS Expense mapping Scope `fie8da5c59` and Revision `fieef2e44j` (`revision_no=1`) remain the sole TISS/TREQ expense/center test mapping, Maker-owned **Draft** with no approved_by/approved_at/approval_reference/effective interval. There are **zero** `GL Entry` records for the synthetic Account, **zero** `Stock Entry Detail` rows referencing the Account or synthetic revision, and **zero** `Version` rows referencing the Revision. Zero Version rows are expected before any approval and do **not** independently test audit insertion. The preflight did not use the approval endpoint and did not make financial-data writes.

**Decision — approval activation remains BLOCKED, despite PASS:** Static review in the prior section found that `approve_mapping` would set `Approved`, create a `Version` audit and an effective timestamp; it accepts a textual accounting approval reference without independently checking a genuine approval document. No direct reject/revoke/deactivate operation was found in the current workflow module, and a controlled unwind plan is not yet validated. Only a **separately requested, explicit owner approval** with genuine Accounting evidence, a reviewed deactivation/reversal strategy and fresh site/runtime preflight could authorize any real Checker approval POST. Do not invent references, activate a fake mapping, edit SQL as rollback, restore a site as an automatic test remedy, modify main DEVELOPMENT/PRODUCTION, or create stock/GL transactions.

**Recommended next GitHub-first step (separate scope):** Propose and review the financial-mapping lifecycle safety design for authenticated Checker **reject Draft** and controlled **retire/deactivate Approved mapping**, with locking/idempotency, no backward rewrites, effective-interval cutoff semantics, audit Version creation, prevention of duplicate financial effects, permission & Company constraints, transaction failure handling, and targeted unit/integration tests. Do not treat this read-only review as permission to implement, deploy, or test write paths.
