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

### Owner-authorized Finance mapping lifecycle design: GitHub-only completed (2026-10-28)

After the read-only approval safety preflight PASS for TISS synthetic Scope `fie8da5c59` and Maker-owned Draft Revision `fieef2e44j`, the owner answered **Approved** specifically to preparing a GitHub documentation-only design for **Checker Reject Draft** and controlled **Retire/Deactivate Approved mapping**. The owner did **not** authorize source implementation, site/schema modification, any actual rejection or activation, financial posting, main DEVELOPMENT or PRODUCTION changes.

**Created and read-back verified new design** on the docs branch:
[FINANCE-MAPPING-REJECTION-RETIREMENT-LIFECYCLE-DESIGN-2026-10-28.md](FINANCE-MAPPING-REJECTION-RETIREMENT-LIFECYCLE-DESIGN-2026-10-28.md), commit `82b6fa1a9af39f2e8df804e13b0ecbc5759cd01f`.

The design is explicitly a **proposal pending owner/Accounting decisions**:
- A terminal **Rejected** state for unapproved Drafts with independent authenticated Checker, mandatory reason, optimistic modified token, immutable rejected history and one Version audit; existing B/C revision status options do not yet include Rejected.
- A **retirement request + immutable accepted retirement event** with separately authorized Accounting decision, Company/scoped Maker–Checker separation, idempotent unique acceptance, versioning/Version audit and server-owned non-backdated cutoff. Keep original Approved evidence unchanged; compute its effective interval end from original term and accepted retirement cutoff.
- Fail-closed, locked issue-runtime query and Stock Entry before_submit recheck at both posting time and current time; maintain historical GL/stock/expense/center provenance without edits. Current runtime only filters Approved rows and uses original effective_until, so merely changing state to Revoked would break historical as-of semantics.
- Flagged discrepancy: current provenance helper checks present-day roles/Company permissions for historical signed actors, risking failure after personnel offboarding; needs policy and code review.
- Concrete schema/transaction/concurrency/index designs, genuine Accounting evidence verification (text-only approval_reference in current code is insufficient), rollback/recovery, and real MariaDB tests remain future scoped work. No PRODUCTION authorization and no existing Draft approval.

**Next decision gate:** Obtain distinct scope approval for one of (A) revise/finalize this conceptual design and unresolved Accounting governance, or (B) implement the agreed controls on a named reviewed app feature branch after explicit schema/role/evidence decisions; any isolated DEVELOPMENT pull/migrate/write test requires its **own** approval. The previously verified Integration2 Maker Draft remains **Draft**; do not activate or rerun the Maker proposal.

### Owner endorses lifecycle design direction in principle — 2026-10-28

After receiving the completed GitHub-only [Finance mapping rejection/retirement design](FINANCE-MAPPING-REJECTION-RETIREMENT-LIFECYCLE-DESIGN-2026-10-28.md) and handoff, the owner replied **"Approved."** Recorded this as endorsement of the **conceptual direction**: audited terminal Draft rejection, prospectively effective append-only retirement decision, independent Finance Maker/Checker authority, nonretroactive historical accounting, concurrency control and fail-closed mapping resolver behavior. Updated the design document on this docs review branch; no app source or runtime writes.

**Still pending:** exact B/C DocType schema, indexes, state rules, new role/evidence governance decisions, document-backed Accounting reference verification, retirement cutoff policy and recovery/failure handling; explicit design/implementation authorization and tests. The synthetic TISS Expense Scope `fie8da5c59` and Revision `fieef2e44j` are **last verified Draft**, not approved. Do not run any live approval or migration, edit/delete financial history, change shared DEVELOPMENT environment, or touch PRODUCTION.

**Next step:** present a tightly bounded schema and Accounting governance design proposal (documentation only) as the next separate decision. Do not interpret this short approval as authorization for application code or environment changes.

### Owner-authorized lifecycle schema and Accounting governance specification completed — 2026-10-28

The owner explicitly approved **preparing detailed Finance mapping lifecycle schema and Accounting governance specifications in GitHub for review only**. GitHub connected tools reviewed pinned app `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and the latest docs review branch, then created, read back and verified [FINANCE-MAPPING-LIFECYCLE-SCHEMA-ACCOUNTING-GOVERNANCE-SPEC-2026-10-28.md](FINANCE-MAPPING-LIFECYCLE-SCHEMA-ACCOUNTING-GOVERNANCE-SPEC-2026-10-28.md) (creation commit `a50f181c1c25a22e9d8ac5df104ffe49bfcb8241`). The [conceptual lifecycle design](FINANCE-MAPPING-REJECTION-RETIREMENT-LIFECYCLE-DESIGN-2026-10-28.md) also now links to that detailed companion (commit `47b30da5598b2f3bdad84f4cbf152292fd381499`).

**Contents (all proposals):** Add terminal Rejected revision state and audited rejection evidence; candidate immutable Rejection Event, Retirement Request and Retirement Event DocTypes and exact field/type/invariant lists; controlled Accounting decision evidence lookup and signatory authority; Company-scoped Maker/Checker separation; server-owned non-backdated effective cutoff and immutable past Approved decisions; durable uniqueness/idempotency and InnoDB lock ordering; stock issue resolver/before_submit cutoff revalidation; historical actor-grant correction risk; additive migration/backward-worker compatibility, backup/recovery gates and real MariaDB test acceptance.

**Decisions not supplied and still OPEN:** Whether to adopt exact new fields/DocTypes, which named Accounting decision-makers and evidence source are authoritative, whether rejection requires evidence, prospective cutoff/lead time, schema and indexes, role-change provenance, restore readiness, actual business crosswalk, app implementation branch/permissions. The owner's documentation approval is **not** approval of those proposed schemas or business rules and **does not authorize code changes, database migration, credentials/role grants, Maker/Checker financial state changes, stock/GL postings, DEVELOPMENT/PRODUCTION operations or backups/restores**. The last independently verified synthetic TISS Expense Scope `fie8da5c59` / Revision `fieef2e44j` remains **Draft**.

**Next practical decision:** Ask owner/Accounting to review the specification's decision register (G1–G12), focusing first on Accounting source-of-truth/signatory evidence (G4), terminal rejection model (G1/G2) and exact retirement authority/timing (G3/G6). A subsequent explicit bounded GitHub app implementation authorization may then be sought, followed by separate DEVELOPMENT integration gates. PRODUCTION remains NO-GO.

### Finance Accounting authority decision: design policy selected (2026-10-28)

The owner delegated the remaining **technical design choices** with "Approved decide it yourself". The documented decision is [FINANCE-MAPPING-ACCOUNTING-AUTHORITY-DECISION-2026-10-28.md](FINANCE-MAPPING-ACCOUNTING-AUTHORITY-DECISION-2026-10-28.md), created at commit `2c4f0bd05a01e2d028f9f48242a0581826e989e0`. The [detailed schema specification](FINANCE-MAPPING-LIFECYCLE-SCHEMA-ACCOUNTING-GOVERNANCE-SPEC-2026-10-28.md) now identifies the later policy as authoritative for default design choices, commit `505092a9fcfb59b090b432926681d2425d29e246`.

**Selected policy:** Keep exactly two distinct Finance roles (Company-scoped Maker and Checker). Design an internal immutable, authenticated **CCPC Accounting Mapping Decision** as the source of mapping signoff, with one-use Decision Use evidence and exact Company/scope/revision/value/version verification. The same authorized Checker may sign and execute; no employee automatically gains the role. Rejection is terminal and reason-based, with an immutable audit; retirement is Maker-requested, independently Checker-authorized, append-only, with immediate prospective cutoff for the first implementation. History must remain unchanged, and the resolver must fail closed. Signed text alone is not sufficient evidence.

**Authorization boundary:** These are design selections only. Actual human Accounting signatories and Company grants, business crosswalks, application changes, schema/index migration, integration writes and all PRODUCTION activity remain unapproved. Existing synthetic TISS Expense Scope `fie8da5c59` and Draft Revision `fieef2e44j` were last verified Draft. Next task is a separate, bounded GitHub app implementation plan/authorization.

### Finance lifecycle GitHub code implementation: draft PR #21 — NOT DEPLOYED / NOT INTEGRATION TESTED

**Owner authorization, 2026-10-28:** After approving the Finance mapping technical governance decisions, the owner explicitly said **"Approved implement it"**. This authorized **application code implementation in GitHub**, not a change to the existing physical DEVELOPMENT/Integration2 or PRODUCTION environments.

**Verified application baseline:** Review branch `review/circleci-isolated-erpnext-phase2-2026-10-26`, HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` at start of implementation. Created a separate feature branch `feature/finance-mapping-lifecycle-2026-10-28` from the exact commit; feature HEAD **`765bf13b8dd16a5f570ce552b58c31a92ead0d89`** (verified ahead by three commits, behind zero). Created and fetched **[ccpcerp/ccpcerp draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21)** with this feature head and the verified review branch as the base. **PR is OPEN/DRAFT, not merged.** Latest commits include `52447e99347dc7a293cc98342084697ed5f3f7d9` (new implementation/schema), `6dc87599e9717e29cc14a3ce925e8d2a0cb6964b` (signed-decision state and digest checks), and `765bf13b8dd16a5f570ce552b58c31a92ead0d89` (Company-first lock ordering).

**Changes committed in GitHub (not yet accepted as safe):**
- Added **five proposed Finance DocTypes** (CCPC Accounting Mapping Decision, CCPC Mapping Decision Use, CCPC Mapping Rejection Event, CCPC Mapping Retirement Request, CCPC Mapping Retirement Event) with initially empty ordinary permissions, uniqueness on one-use decision/event keys, server-only controller guards, and immutable history restrictions.
- Added `bc_finance_evidence.py` for POST-only authenticated internal signed Accounting decision creation tied to exact Company/Scope/revision/value/modified fingerprint and one-use consumption.
- Added `bc_finance_lifecycle_events.py` for independent Checker terminal Draft rejection, Maker retirement request, and independent Checker acceptance/decline of retirement. An accepted retirement records a non-backdated, server-owned prospective cutoff **without altering Approved revision fields**; pending/declined requests have no accounting effect. 
- Updated `bc_mapping_workflow.py` to require **a verified internal Accounting Decision** rather than a free-text reference before original Draft approval, consume it once within the approval transaction, and block a second unresolved Draft per Scope. Finance Company row is now locked before actor role locks.
- Updated `bc_issue_runtime.py` to read accepted retirement cutoffs under locks and compute effective interval end for Expense and Center, including before-submit re-resolution, without rewriting past Approved fields. Historical signed approval checks no longer depend on current role grants; a narrowly guarded CircleCI-only synthetic fixture token is retained solely on the exact disposable CI site.
- Disabled the legacy mutable replacement/retirement/approve-change HTTP paths in `bc_mapping_lifecycle.py` because their old free-text authorization and direct approved effective_until rewrite conflict with the chosen append-only decision policy. This is an **intentional fail-closed behavior change**; replacement flows are not yet replaced by a safe new endpoint.
- Added a terminal `Rejected` option and provenance fields to both B/C revision schemas, and a new static test file `test_bc_finance_governance_static.py` with five source/schema security tests.

**Verification performed:** GitHub commit, three-commit branch ancestry, 25 changed-file compare, and draft PR head/base independently confirmed. GitHub reported no PR-associated workflow runs for feature HEAD when checked. **NO static unit suite, real MariaDB integration suite, HTTP Maker/Checker tests, schema migrations, concurrency tests, restoration rehearsal or stock/GL behavior were executed in this conversation.** No production-readiness claim.

**IMPORTANT release/implementation review gates still pending:** Review and run static Python compile/tests; review SQL/Frappe DocType field/index compatibility, signed Decision + Use cardinalities, event/state/audit rollback, idempotent replay, lock order and actual InnoDB deadlocks; evaluate existing CI synthetic fixture/old approved-record compatibility; independently verify protected backups and a **separately authorized** additive schema migration against an isolated environment. The code is not installed on Integration2/main DEVELOPMENT. Do not instruct a pull, migrate, restart, deploy or approval POST from this checkpoint. Any real Finance signatory/Company crosswalk requires true CCPC authorization; none was appointed by the assistant. No staff grants and no synthetic TISS activation permitted.

**Preserved runtime milestone:** Integration2 TISS Expense Scope `fie8da5c59` and Revision `fieef2e44j` are **last verified Draft** with zero synthetic stock/GL; this GitHub PR did not touch them. PRODUCTION unchanged and requires separate permission and recovery review.

**Next bounded step:** Review draft PR #21's source and targeted static tests on GitHub; then request owner permission for the exact **isolated DEVELOPMENT integration plan** only after code review/tests and migration risk review. Record the resulting tested state and GitHub commits. Never claim implementation is validated or production-ready until the gates pass.

### Finance lifecycle follow-up code review and source checks — 2026-10-28

**Owner scope:** The owner's most recent response **"Approved"** followed the offer to review and test [draft Finance PR #21](https://github.com/ccpcerp/ccpcerp/pull/21). Interpreted as **GitHub code review and safe static checks only**, not a DEVELOPMENT/Integration2 pull, migration, API write test, GL/stock operation or PRODUCTION deployment. Reconfirmed the GitHub-first workflow, app baseline review head `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41` and open draft PR.

**Latest verified app feature head:** `feature/finance-mapping-lifecycle-2026-10-28` at **`76973699a085d3eb4efd6412d21a773ec1499e19`**, targeting `review/circleci-isolated-erpnext-phase2-2026-10-26` (base still `0c223d7c...`). PR #21 remains **OPEN/DRAFT/UNMERGED**. This review made seven further feature commits after initial `765bf13`:
- `196a7589`: signed internal Accounting Decision + Version insertion wrapped in savepoint/rollback.
- `c2340db6`: idempotent identical Pending retirement request replay, rejection of changed payload, atomic request+Version savepoint.
- `11e561ae`: added static guards for replay and rollback semantics.
- `2a13b542`: Company-scoped Checker POST review of exact retirement request, returning current `modified` token without deciding it.
- `247eb67d`: Checker review endpoint static checks.
- `71975f33`: rejected Draft and accepted/declined retirement request SQL now stamp authenticated Checker in `modified_by`.
- `76973699`: static checks for Checker audit attribution.

**Test evidence, exact limits:** Using the connected GitHub file fetch for **13 exact application source/schema files** at `76973699...`, a local JavaScript structural audit executed **20/20 pass assertions**: seven JSON schemas have aligned field_order, no ordinary permissions and unique fields; both B/C states include Rejected; internal signed Decision and one-use evidence checks are present; four lifecycle endpoints are POST-only; legacy mutable-cutoff APIs are blocked; signed Decision and retirement request have savepoint rollback paths; identical pending-request replay is guarded; Checker review returns exact request version; Reviewer SQL attribution is present; retirement cutoff is applied by the resolver; six Python static test methods are committed; and no direct commit/impersonation appears in the two new service modules.

**Crucial distinction:** These 20 checks are **executed JavaScript checks over GitHub source**, **not Python AST/compileall/unittest**, and **not real Frappe v16/MariaDB integration tests**. The isolated local runtime could not retrieve the GitHub repository for Python execution; the committed six Python tests have **not** been executed. At final status check, there were no workflow runs or GitHub commit status results for the examined previous feature head; do not imply CI success or failure. Review-only static evidence is not proof of transaction safety or production readiness.

**Remaining release blockers:** Run and correct genuine Python compileall/static suite in an explicitly isolated/reviewed environment; test newly added five DocTypes and B/C field migration against disposable Frappe v16/MariaDB, including schema/index/field permission compatibility and rollback; verify actual signed evidence, Maker/Checker/Company denials, transaction atomicity and Version failures, duplicate/parallel reject-or-approve and request-or-retire, InnoDB lock order/deadlocks, approved as-of history, issue stock cutoff at both posting and current times, pre-existing approved records without new evidence and CI-disposable fixture restrictions. Replacement API is intentionally fail-closed until replacement event semantics are designed. No real Accounting signatory/crosswalk is appointed. **Do not merge, pull into DEVELOPMENT, migrate or execute Finance lifecycle write endpoints yet.** Any live environment integration is a *separate authorization gate*.

**Integration2 preserved:** Last verified TISS Expense scope `fie8da5c59` and Maker Draft revision `fieef2e44j` remain untouched and are not approved/activated. Main DEVELOPMENT and PRODUCTION were not modified in this conversation.

### Operator-executed Finance Python static suites: 24/24 PASS (2026-10-28)

Owner-provided terminal results from the **separate temporary clone** `/tmp/ccpc-finance-static-zuTeno` show the exact previously supplied guarded feature-branch test command completed. The shell command guarded `git rev-parse HEAD` against feature commit `76973699a085d3eb4efd6412d21a773ec1499e19` before invoking the following Python unit test discovery suites, each of which returned `OK`:

| Test file | Count | Outcome |
| --- | ---: | --- |
| `test_bc_finance_governance_static.py` | 6 | PASS / 0 failed |
| `test_ccpc_mapping_schema_static.py` | 3 | PASS / 0 failed |
| `test_bc_mapping_policy_static.py` | 15 | PASS / 0 failed |
| **All three suites** | **24** | **PASS / 0 failed** |

Reported execution time per suite: 0.007s / 0.003s / 0.000s. Final marker: `FINANCE STATIC TESTS COMPLETED`. This is **genuine operator-executed Python static and pure policy testing**, superseding the earlier "Python tests not executed" checkpoint for this exact commit. The operator supplied the terminal output; ChatGPT did not remotely execute tests on the Ubuntu server. The prior 20/20 GitHub-file-source structural checks are a distinct review result.

The same result was appended to [draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21), which was independently verified OPEN/DRAFT/UNMERGED and targeted at `review/circleci-isolated-erpnext-phase2-2026-10-26`; feature head remained `76973699a085d3eb4efd6412d21a773ec1499e19`.

**What has NOT been tested:** No real Frappe/ERPNext/MariaDB database connection, schema installation/migration, Maker–Checker HTTPS/CSRF end-to-end process, signed Accounting decision consumption, race/deadlock/transaction rollback, retirement cutoff around GL/stock issue, historical approved records/CI fixture compatibility, restore rehearsal or PRODUCTION behavior. There was no DEVELOPMENT/Integration2 pull or write and no financial mapping approval. The synthetic TISS Expense Scope `fie8da5c59` and Revision `fieef2e44j` remain last verified Draft.

**Next controlled milestone:** Review and separately approve a disposable **Frappe v16/MariaDB integration test plan** with independent site/container/DB identity and safe backup/recoverability checks before changing any environment. Never merge or call this PR production-ready on the strength of static checks alone. Shared Docker infrastructure may still present risks; no main DEVELOPMENT or PRODUCTION operation is approved by these static test results.

### Owner-approved PR21 disposable MariaDB integration test plan completed (2026-10-28)

After the operator reported **24/24 executed Python static tests PASS** for app feature HEAD `76973699a085d3eb4efd6412d21a773ec1499e19`, the owner approved **preparing an isolated ERPNext v16/MariaDB integration test plan in GitHub first**, expressly with NO migrations, DEVELOPMENT/PRODUCTION changes or tests executed under this new approval.

**Completed on docs branch:** [FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md](FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md), verified creation commit **`efa9dcb3aa778e976e0c37945dddde7f903e4e63`**. Document was read back and verified in GitHub. It specifies G0 source/runner approval; P0–P7 gates (strictly new disposable Frappe v16/MariaDB site, schema, actual Maker/Checker HTTP+CSRF authorization, signed decision/one-time Use, Draft rejection, retirement request/review/accept/decline, timestamp boundary, transaction rollback, real SQL locks, GL/stock checks, old-row/CI fixture compatibility, clean teardown), 24 expected adversarial scenarios, isolated evidence, stop conditions, migration/backout constraints and separate later DEVELOPMENT/PRODUCTION gates.

**Important verified CI design blocker:** PR #21 remains [OPEN/DRAFT](https://github.com/ccpcerp/ccpcerp/pull/21), feature branch `feature/finance-mapping-lifecycle-2026-10-28`, HEAD `76973699a085d3eb4efd6412d21a773ec1499e19`, targeting review `review/circleci-isolated-erpnext-phase2-2026-10-26`, HEAD `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. The existing `.circleci/config.yml` opt-in isolated-erpnext-integration job and `ci_disposable_site_guard.py` both enforce **CIRCLE_BRANCH=review/circleci-isolated-erpnext-phase2-2026-10-26** (plus strict CircleCI/site/job identity). Running that original job directly from the **feature** branch should **STOP by design**. Do not spoof variables, loosen persistent-site protections, force-move the review branch or run integration under existing guards. A narrowly targeted, separately authorized, disposable-only CI test-harness code review is the next practical prerequisite, alternatively owner-approved separate VM isolation. No automatic or paid CI run was started.

**Status:** Documentation-only plan complete. No Frappe/ERPNext v16/MariaDB integration test or migration has been run for PR #21. No synthetic Finance state/stock/GL changes, no main DEVELOPMENT/Integration2 app pull or Docker/site changes, no PRODUCTION actions. TISS Expense Scope `fie8da5c59` and Revision `fieef2e44j` remain last verified **Draft**. Existing 24/24 static test PASS remains correct but is not integration validation.

**Next decision gate:** Request separate, specifically scoped owner approval for **G0 CI harness/source-isolation review only** (or a named disposable VM) with exact pinned feature SHA, access/risk/cost bounds and stop conditions. Then request distinct permission for app-side disposable-only test harness implementation, opt-in runtime CI and any eventual persistent DEVELOPMENT site operations; PRODUCTION explicitly excluded.

### Finance PR21 G0 CircleCI harness safety review completed (2026-10-28) — GitHub only

After approving the [disposable MariaDB integration test plan](FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md), the project owner answered **Approved** to exactly a **GitHub-only CircleCI feature-harness safety review**, explicitly without starting any pipeline or changing any ERPNext environment. Connected GitHub tools verified authoritative docs workflow, both repo branches and [ccpcerp/ccpcerp draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21), plus the existing CI YAML, disposable-site guard, guard negative tests and synthetic Finance fixture.

**Completed GitHub docs:**
- New [FINANCE-PR21-CIRCLECI-FEATURE-HARNESS-G0-SAFETY-REVIEW-2026-10-28.md](FINANCE-PR21-CIRCLECI-FEATURE-HARNESS-G0-SAFETY-REVIEW-2026-10-28.md), independently read-back verified after creation commit `c9e678adea164c8a12569b40a84b34fe3ca2013d`.
- Updated the [PR21 isolated ERPNext v16/MariaDB plan](FINANCE-MAPPING-PR21-ISOLATED-ERPNext-V16-MARIADB-INTEGRATION-TEST-PLAN-2026-10-28.md) with this G0 review and its separate next permissions, commit `47d6dc9bd13c0c52c9c582d42171cf286bb8813a`.

**Verified code-level findings (not executed CI):** At feature HEAD `76973699a085d3eb4efd6412d21a773ec1499e19`, `.circleci/config.yml` was identical to base at blob `5a9f023c0105bad333ddedfe1976939049447151`. The existing opt-in `isolated-erpnext-integration` job and the underlying `is_reviewed_circleci_disposable_site` guard hard-pin CIRCLE_BRANCH to the earlier `review/circleci-isolated-erpnext-phase2-2026-10-26`; PR21 is on `feature/finance-mapping-lifecycle-2026-10-28`. That job will fail closed for PR21 as intended and currently runs only older Withdrawal/Intercompany suites, **not** the new Maker/Checker Finance lifecycle SQL/HTTP integration cases. Original negative tests and synthetic Approved-looking fixture should **not** be broadened or treated as real Accounting signoff. Source branch guards alone do **not** prove runner network isolation.

**G0 design recommendation, not implemented:** Add a **new, separate, opt-in, Finance-lifecycle-only CircleCI job** with a distinct synthetic site and separate strong guard binding actual CircleCI org/repo, exact feature branch, job, checked-out commit and reviewer-approved post-change SHA, plus negative tests and genuine disposable Frappe v16/MariaDB Finance lifecycle tests. Preserve original job/guard and CI-only synthetic fixtures. Confirm real runner/DB/network isolation, resource cost/timeout, floating Frappe/ERPNext version pins, no PROD/DEV context/SSH/NAS/Docker sockets, no auto expensive runs. No environment variables may be spoofed or old review branch force-moved to defeat CI guard.

**NEXT GATES:** (1) Separately authorize GitHub-only app/CI test harness implementation (G1) after this G0 review, still no CircleCI run, merge or site modification; (2) separately authorize an exact paid/opt-in disposable CI run (G2) only after post-change code/guard tests and source SHA re-pin; (3) separately review any persistent DEVELOPMENT adoption (G3); (4) separate production release authorization (G4). No G1/G2/G3/G4 execution permission was granted by the latest **Approved** message.

**Preserved status:** PR #21 OPEN/DRAFT/UNMERGED; app feature last verified at `76973699a085d3eb4efd6412d21a773ec1499e19`; owner-executed Python static tests **24/24 PASS**; real PR21 Frappe/MariaDB tests **not run**; no app CI code edits, migrations, DEV/Integration2/PRODUCTION changes, staff signatories or financial transactions. Synthetic TISS Expense Scope `fie8da5c59`, Revision `fieef2e44j` last verified **Draft**.

### Finance PR21 G1 CircleCI harness implementation committed — GitHub only (2026-10-28)

After reviewing the [Finance PR21 G0 CircleCI source isolation safety review](FINANCE-PR21-CIRCLECI-FEATURE-HARNESS-G0-SAFETY-REVIEW-2026-10-28.md), the owner explicitly replied **"Approved"** to **GitHub-only implementation of a dedicated Finance CircleCI harness and its security tests**, without starting any CI pipeline, migrating databases, or touching DEVELOPMENT/Integration2/PRODUCTION. Source edits were performed directly through connected GitHub tools on the existing PR21 feature branch; no runtime site interaction.

**G1 completed:** [FINANCE-PR21-CIRCLECI-HARNESS-G1-IMPLEMENTATION-CHECKPOINT-2026-10-28.md](FINANCE-PR21-CIRCLECI-HARNESS-G1-IMPLEMENTATION-CHECKPOINT-2026-10-28.md), GitHub creation commit `e83978a6e1ff45fa541a6331a6b06abfc18bccca`. See this document for exact changes, CI isolation limits and next approval gates.

**Verified application feature:** [ccpcerp/ccpcerp draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) OPEN/DRAFT/UNMERGED, source `feature/finance-mapping-lifecycle-2026-10-28`, new HEAD **`375de12e7bf79210fdb7ec54b6e7184d0b27ead6`**, target reviewed base `review/circleci-isolated-erpnext-phase2-2026-10-26` at `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`. The prior 24/24 owner-executed Python static test PASS belongs to **older feature SHA `76973699...`**, not the new head, and does not certify new CI tests.

**Code committed:** Added `ci_finance_lifecycle_site_guard.py` requiring an exact disposable site, actual CircleCI organization/branch/job/IDs and externally approved 40-char commit SHA; six independent negative guard tests; extended `.circleci/config.yml` with a separate `run_finance_lifecycle` **default false**, a manual approval job and a dependent isolated Finance job; four static CircleCI YAML-policy test methods; eight guarded **real MariaDB/Frappe direct-service test candidates** for Expense/Center Maker–Checker sign/reject, one-use decisions, request/decline/accept retirement, prospective cutoff and rollback. GitHub commit sequence `1d814b0`, `b77b968`, `1281689`, `259b2ae`, `aa0b3ac`, `a725727`, `9aa4a7e`, `375de12`. Independent source comparison confirmed the original legacy CI job commands and workflows unchanged and original CI guard file **byte-identical**. Verified upstream candidate pins: Frappe `988e54f...` (v16.33.1) and ERPNext `4048fb7...` (v16.34.2).

**Current status / release blockers:** This is **committed but NOT RUN**. No Python compile/unit tests or CircleCI config compiler validation executed for the new HEAD; no CircleCI pipeline, installed DocTypes, Frappe/MariaDB integration, actual HTTP session/CSRF, ledger posting, multi-connection concurrency, migration or PROD test. New job requires independently configured `CCPC_FINANCE_APPROVED_SHA` and opt-in parameter plus CircleCI human approval **after** distinct G2 consent. The config/guard does not prove underlying runner network or host isolation, which must be reviewed. Database module uses Frappe service calls under synthetic user identity, **not authenticated HTTP**; stock/GL behavior remains untested. PR21 stays draft; do not merge or deploy.

**Next controlled action:** Separate **G1.1 offline static test approval** (temporary isolated clone; Python compileall, original static suites, new six guard + four config suites, CircleCI YAML parser) and independent readback of results. Then request **G2 explicit single disposable CircleCI run approval** including exact new commit, trusted project-level SHA pin, runner/DB isolation, cost and specific synthetic test scopes. Any persistent DEVELOPMENT pull/migrate and any PRODUCTION action require their own distinct gates. Do not use TISS Expense Scope `fie8da5c59` / synthetic Revision `fieef2e44j`: last verified Draft, with no financial posting.

### Finance PR21 G1.1 offline tests: 10/10 new CI tests PASS (2026-10-28)

The owner explicitly approved the **offline static-test step only**, without CircleCI execution, database migrations or DEVELOPMENT/PRODUCTION changes. App review GitHub remained [draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21), feature `feature/finance-mapping-lifecycle-2026-10-28` at `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`, base `review/circleci-isolated-erpnext-phase2-2026-10-26` at `0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`.

**New executable evidence:** Direct Git clone was unavailable due GitHub DNS resolution failure inside the assistant's isolated container. GitHub connector supplied the source of five exact files, locally reconstructed into a separate temporary directory, and verified by matching Git blob SHAs against current GitHub contents. Executed `python3 -m unittest discover -s .circleci -p 'test_finance_lifecycle_ci_guard.py' -v` **6/6 PASS**; `test_finance_ci_config_static.py` **4/4 PASS**; 10/10 new CI security/config checks, 0 failures. `python3 -m compileall -q` succeeded on the four exact guard/negative-test Python files. PyYAML 6.0.3 parsed exact `.circleci/config.yml` and assertions passed for default-off Finance/integration parameters and human approval dependency. This is NOT the full CircleCI CLI semantic validator.

**Original Finance Python static suite:** Owner-run **24/24 PASS** at `76973699...` remains documented. A GitHub blob comparison confirmed the three static suites and seven relevant Finance source/policy/schema files are **byte-identical** at current `375de12...`. The 24 Python tests were **not rerun** at current head; do not label new-head aggregate as 34 executed tests.

**Remaining work:** Full current-source clone `python3 -m compileall -q ccpcerp`, 24 original test suites at new HEAD, and CircleCI CLI config compiler validation (if tool installed). Revalidate runner/network/service separation, approved exact SHA and cost before seeking a distinct G2 opt-in CircleCI integration run. The exact results and five source blob SHAs were documented in [G1 implementation checkpoint §5](FINANCE-PR21-CIRCLECI-HARNESS-G1-IMPLEMENTATION-CHECKPOINT-2026-10-28.md), update commit `169943a6d88bc9429732e367b4963fe2fc85c284`, and PR #21 body.

**No execution approval:** PR21 OPEN/DRAFT/UNMERGED, no CI pipeline, no Frappe v16/MariaDB integration, no persistent DEVELOPMENT/Integration2 access, no GL/stock posting and no PRODUCTION operation. Synthetic TISS Scope `fie8da5c59` and Draft revision `fieef2e44j` remain at last verified Draft with zero financial activation. No changes to app branch under this owner-approved test step.

### Finance PR21 G1.1 full static suite: 34/34 PASS at feature SHA (2026-10-28)

The owner supplied successful terminal output from the previously approved and provided **temporary full-clone Ubuntu script**. It began with `set -euo pipefail`, used a new `/tmp/ccpc-finance-g11-...` checkout, and asserted exact feature commit **`375de12e7bf79210fdb7ec54b6e7184d0b27ead6`**. The final `G1.1 FULL STATIC VERIFICATION COMPLETED` marker confirms that `python3 -m compileall -q ccpcerp .circleci` and all five sequential `unittest discover` commands exited successfully. Per-test output: Finance governance **6/6**, mapping schema **3/3**, B/C mapping policy **15/15**, Finance CI guard **6/6**, CircleCI config static tests **4/4**; **34/34 Python tests PASS**, zero failures and errors. Timings 0.007s / 0.003s / 0.000s / 0.005s / 0.000s. Evidence is an **owner-provided terminal result**, not a ChatGPT-executed Frappe or CircleCI test.

**Authoritative code state:** [Draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) verified OPEN/DRAFT/UNMERGED, feature branch `feature/finance-mapping-lifecycle-2026-10-28` HEAD **`375de12e7bf79210fdb7ec54b6e7184d0b27ead6`** targeting review `review/circleci-isolated-erpnext-phase2-2026-10-26`. Its body now records full test results. The [G1 Finance harness checkpoint §6](FINANCE-PR21-CIRCLECI-HARNESS-G1-IMPLEMENTATION-CHECKPOINT-2026-10-28.md) records precise outputs and outstanding gates; update commit `6677b2bbb1b2e69fb7acb44250a5476b15be400a`. No app source was changed to record the results.

**Milestone update:** G1.1 **full offline Python compile + original 24 + new 10 = 34/34 PASS** complete. Previous statements of pending full clone/compile or older 24 tests at current SHA have been superseded **for this unchanged feature commit**. The earlier 10/10 source reconstructed subset remains supplementary provenance, not another 10 additional tests.

**Still unverified / blocked:** CircleCI CLI **semantic config compilation** (PyYAML parse only), independently reviewed runner/org/DB isolation, trusted project variable `CCPC_FINANCE_APPROVED_SHA`, any **G2 separately authorized opt-in paid CircleCI job**, fresh Frappe/ERPNext v16/MariaDB schema installation, real Maker/Checker HTTP+CSRF, concurrency/rollback, Stock Entry/GL/ledger and historical event-time behavior. The new eight direct-service integration tests have **not run**. Do not merge PR, change DEVELOPMENT/Integration2 database/worktree, run migrations, approve synthetic TISS revision, change backups or touch PRODUCTION under this checkpoint. Last independently verified TISS Scope `fie8da5c59` and Revision `fieef2e44j` remain **Draft**. Any proposed G2 execution needs a new exact SHA, runner, cost and scope approval.

### Finance PR21 G1.2 CircleCI CLI availability and runner cost review — 2026-10-28

After verified owner-run **34/34 full Python static test PASS** at feature app HEAD `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`, the owner answered **"Approved"** to the next **offline CircleCI CLI configuration validation and runner isolation/resource-cost review**. No authorization to start CircleCI, set approved-SHA project variables, spend credits, deploy, migrate, execute Finance POSTs or modify any CCPC site was granted.

**GitHub documentation completed and verified:**
- [FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md](FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md), created `a0b9066887756da2b70ef288e8d1023e97e9c2db`, with GitHub readback.
- [G1 Finance harness checkpoint §7](FINANCE-PR21-CIRCLECI-HARNESS-G1-IMPLEMENTATION-CHECKPOINT-2026-10-28.md), updated `c9ef24d1513769b8849c53a9dda5f009b2cc2f27`.
- Source for app [PR #21](https://github.com/ccpcerp/ccpcerp/pull/21), feature SHA `375de12...`, `.circleci/config.yml` blob `0f23d7ce0f1a1e94cad0debbee865ac813ed1509`, read back. No change to app/CI source.

**G1.2 outcome:** The assistant's isolated container had **no installed CircleCI CLI**; attempts to access CircleCI failed due outbound DNS. Accordingly **no CircleCI CLI `config validate` command ran**. Previous owner-run full compileall and **34/34 static PASS**, plus earlier exact-blob PyYAML parse, remain documented **but cannot be represented as CircleCI CLI semantic validation**. A safe readonly, exact-SHA, temporary-checkout `circleci config validate .circleci/config.yml --json` command is in the new review for later operator execution if the CLI already exists and is trusted. No CLI installation or login attempted on the shared CCPC server.

**Security/cost assessment:** New job is `resource_class: large`, opt-in parameter default false, manual CircleCI approval, separate Finance site and source-SHA gate. Source has no DEV/PROD mounted files/contexts, but CircleCI project-scoped secrets, true runner network isolation, approval rights and org settings **remain unverified**. Official CircleCI price list updated 2026-10-08 gives standard x86 Docker large **20 credits/min** (4 CPU, 8 GB), before additional charges. `no_output_timeout: 20m` controls output silence, not total run length or spending. CircleCI documentation lists plan-dependent maximum job runtimes of 1/3/5 hours; actual CCPC plan/balance are not known. Demand explicit owner credit/time budget, active cancellation plan, no unauthorized retries, and independently verified org/project/settings before any G2 CI run.

**Current gate: G2 NO-GO.** PR21 still OPEN/DRAFT/UNMERGED at unchanged app SHA. No CircleCI project setting change, job approval, pipeline, MariaDB installation, Finance/stock/GL posting, DEVELOPMENT/Integration2 pull or migration, or PRODUCTION work occurred. Last independently verified TISS synthetic Expense Scope `fie8da5c59` and Draft revision `fieef2e44j` remain last-known Draft; not queried or mutated by this review. Next step: operator performs exact-SHA CircleCI CLI config validation from a safe isolated clone (prefer developer workstation), provides CLI version and output; review against the G1.2 risk checklist. Only then seek a distinct, bounded G2 execution decision.

### Finance PR21 CircleCI opt-in CLI compiler failure — 2026-10-28

After the G1.2 review, the owner verified an official downloaded CircleCI CLI v1.11.0 and ran **actual CircleCI config validation** on an exact-SHA temporary checkout. The default `circleci config validate .circleci/config.yml --json` returned `valid:true`, compiling **only starter-validation** because the Finance pipeline parameter defaults false. The separate Finance opt-in `circleci config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: true'` **FAILED exit 7**, citing the literal Python shell heredoc `python - <<'PY'` at CI file line 194 as an unclosed CircleCI `<<` template tag. It is a **real Finance opt-in CI YAML compiler issue**, not a running ERPNext failure.

See [G1.2 review §6](FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md), updated documentation commit `b8e379e3d31222d29b91b26f593fd19c2071a964`. Official CircleCI guidance requires escaping heredoc operators in v2.1 source by preceding `<<` with a single backslash, leaving the two real CircleCI template expressions unchanged. **Only a copy-only temporary YAML fix/compile test is being considered under current offline authorization.** No GitHub feature commit fix, code deployment, CircleCI pipeline or CI setting change is authorized by the reported error. If copy test passes, seek explicit GitHub-only fix authorization and regenerate the reviewed SHA, repeat needed checks; G2 remains NO-GO.

### Finance PR21 corrected COPY-only CircleCI opt-in config compiled successfully — 2026-10-28

The owner executed the guarded **temporary-file-only** test of the diagnosed CircleCI CLI heredoc escape, using official CLI v1.11.0 and existing isolated source checkout. The command verified app HEAD `375de12e7bf79210fdb7ec54b6e7184d0b27ead6`, original `.circleci/config.yml` blob `0f23d7ce0f1a1e94cad0debbee865ac813ed1509`, copied the YAML to `/tmp`, escaped the one Finance-job Python heredoc `<<` with a preceding backslash **only in the copy**, and compiled with opt-in pipeline parameter `run_finance_lifecycle: true`. Terminal result **`FINANCE CONFIGURATION: PASS`**; compiled `opt-in-finance-lifecycle` includes `finance-lifecycle-manual-approval` and `finance-lifecycle-isolated-integration` requiring that approval. This supersedes the earlier failure for the **corrected copy only**.

**No GitHub feature code fix has been authorized or applied.** The committed YAML on PR #21 still contains the unescaped heredoc and is not Finance-opt-in-compiler-valid. [G1.2 review §7](FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md) documents the operator transcript, G1.2 docs commit `f6adfd86480129782f1208e8c48a47c5c14c8504`, and a precise one-line source patch pending owner authorization. Any future approved feature commit changes SHA; repeat Python/static and both CLI compilation modes at the committed post-fix SHA, and update GitHub handoff.

**Next owner decision:** authorize just the GitHub-only one-line Finance job `python - <<'PY'` → escaped heredoc patch, with no CircleCI pipeline/approval job, approved-SHA setting, MariaDB/DEV/PROD operation, or PR merge. G2 remains NO-GO pending runtime isolation, cost and standalone authorization.

### Finance PR21 one-line CircleCI heredoc fix committed to feature branch — 2026-10-28

After the owner-provided official CircleCI CLI v1.11.0 **Finance opt-in temporary YAML COPY** compiler result `FINANCE CONFIGURATION: PASS`, the owner explicitly **approved only the one-line feature-branch GitHub source fix and static verification**, not executing CircleCI, setting project variables, modifying sites, or merging.

**Authoritative implementation:** App GitHub `ccpcerp/ccpcerp`, draft [PR #21](https://github.com/ccpcerp/ccpcerp/pull/21), feature `feature/finance-mapping-lifecycle-2026-10-28`, **NEW exact HEAD `d154886ab45c51878a87a4ecf42e45602d8d9ccb`**. One commit with exact `.circleci/config.yml` single-line heredoc escape: in Finance job line 194 `python - <<'PY'` becomes `python - \\<<'PY'` in YAML source. GitHub diff confirms **1 line added/1 removed in one file**, resulting config blob `9aa8c676dfa7b22e7b7035d70a0b461af773908d`. Original CI job and existing workflows are source-identical to the established review base; original CircleCI security guard, new Finance guard, all 8 database service-test methods and original Python static tests **unchanged**. Draft PR remains open, unmerged, targeting `review/circleci-isolated-erpnext-phase2-2026-10-26`.

**Verification:** GitHub reads verified the new branch and PR SHA, exact-only substitution, original old-job equality, default false flags, Finance approval dependencies, exact SHA and disposable-site checks. These are **source checks**. Earlier **34/34 Python PASS + full compileall** are operator-provided for the **previous SHA `375de12...`**. Earlier Finance CLI opt-in `PASS` was for an **identically corrected temporary YAML copy from previous SHA**, not the new committed SHA. A **fresh exact-`d154886...` temporary clone, full 34 Python static tests/compileall and both default + Finance opt-in CLI compiler checks remain PENDING**. Do not claim post-commit executable tests passed until the owner supplies output.

**Documentation:** [G1.2 review §8](FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md), written on docs branch in commit `fc65d259710c7e9455fc363595212f8806dad993`, captures the exact commit and safeguards. **G2 integration execution remains NO-GO** without separate approval for project/runner isolation, budget, protected SHA, disposable MariaDB, etc. No CI pipeline triggered, no CI project variable changed, no DEVELOPMENT/Integration2/PRODUCTION action, no ERPNext posting. Last synthetic TISS scope `fie8da5c59` and revision `fieef2e44j` are last independently verified Draft.

### Finance PR21 committed-SHA G1.2 post-fix checks PASS — 34/34 + both CircleCI compiler modes (2026-10-28)

**Owner-executed Ubuntu terminal evidence:** Using the approved `set -euo pipefail` script in a **fresh `/tmp/ccpc-finance-postfix-...` checkout**, the operator verified exact application commit `d154886ab45c51878a87a4ecf42e45602d8d9ccb`, successfully completed `python3 -m compileall -q ccpcerp .circleci`, and passed all **34/34 Python static/security/config tests**: governance 6, mapping schema 3, mapping policy 15, Finance CI isolation 6, CI config policy 4. The terminal ends in `POST-FIX STATIC AND CIRCLECI VALIDATION: PASS`. Earlier old-SHA pass reports are superseded for the current GitHub commit.

**Actual CircleCI CLI compiler results, same post-fix checkout:** Official temporary Linux AMD64 CircleCI CLI v1.11.0 returned **`valid: true`** for default `config validate .circleci/config.yml --json`, compiling the default `starter-validation` job. A separate `config process .circleci/config.yml --pipeline-parameters 'run_finance_lifecycle: true'` **succeeded** and printed the `opt-in-finance-lifecycle` workflow, with `finance-lifecycle-manual-approval` type approval and `finance-lifecycle-isolated-integration` explicitly requiring that hold. Both default and Finance opt-in compilation are now **PASS on committed SHA**, not merely on a temporary patched copy.

**Verified GitHub project checkpoint:** [G1.2 config/runner/cost review §9](FINANCE-PR21-G1-2-CIRCLECI-CONFIG-RUNNER-COST-REVIEW-2026-10-28.md), documentation commit `c919e61bfbfbafb45bfc69eeb6b9c3661855f89a`. Independently read current [draft PR #21](https://github.com/ccpcerp/ccpcerp/pull/21) OPEN/DRAFT/UNMERGED at same app SHA `d154886...`, `.circleci/config.yml` blob `9aa8c676dfa7b22e7b7035d70a0b461af773908d`; the one-line heredoc fix remains intact. No feature-branch code changes during this documentation milestone.

**Current gate:** **G1.2 offline static/compiler complete; G2 finance MariaDB CI run NOT APPROVED / NO-GO**. Real CircleCI Cloud job execution, runner/organization settings and secrets/cost audit, approved-SHA env configuration, disposable Frappe/ERPNext/MariaDB transaction tests, true authenticated HTTP/CSRF, concurrency or financial posting remain untested. No CI pipeline trigger, approval job, site migration, DEVELOPMENT/Integration2 checkout/pull, PRODUCTION deployment or changes to Accounting signatories. Last independently verified synthetic TISS Scope `fie8da5c59` and Expense Revision `fieef2e44j` are **Draft**; not accessed here. Next phase requires independent read-only verification of CircleCI project/runner isolation, owner-defined credit/time cap and **separate explicit one-run G2 approval** before touching CircleCI project settings or scheduling any job.

### Finance PR21 G2 read-only runner/security/cost readiness reviewed — 2026-10-28

The owner replied **"Approved"** to starting the proposed **read-only G2 CircleCI account/runner/cost readiness review**, not to any paid CI run or settings change. ChatGPT re-read the authoritative workflow, draft app PR #21 (still OPEN/DRAFT/UNMERGED) at **`d154886ab45c51878a87a4ecf42e45602d8d9ccb`**, CI YAML blob `9aa8c676dfa7b22e7b7035d70a0b461af773908d`, latest G1.2 docs, and official CircleCI pricing/security/approval/budget references. GitHub combined commit-status response had zero entries, which **does not prove CircleCI has never run**. Search for a connected CircleCI plugin found none, and current authorized tools cannot read private CircleCI account settings, network policy or credits. No CircleCI login, credentials, run, job approval, project variable or runner changes were made.

**G2 review recorded** in [FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md) via docs commit `78299fd830327d9125be695376caccd9fb55fdef`. G1.2 **34/34 Python static + two CircleCI CLI compile PASS** remains valid at exact app SHA. The dedicated Finance opt-in workflow has default false, branch filter, separate manual approval and SHA guard. No explicit DEV/PROD mount or context in YAML, but **project-level environment vars/secrets are inherited and external access is not attested**. Also **CircleCI approval can be granted by repository push-access holders**, not necessarily solely CCPC owner. `CCPC_FINANCE_APPROVED_SHA` is an externally managed project-level gate, not a cryptographic authorization; status and admin controls still unknown. Hosted Docker vs effective project runner/network, actual CircleCI org slug, triggers, plan/balance, checkout credentials, contexts and variable names also require read-only inspection.

**Published price evidence:** CircleCI 2026-10-08 list standard x86 Docker `large` at **20 credits/min**, examples 15m 300/30m 600/60m 1200 base compute, potential Gen 2 class **24 credits/min** plus eligible charges. The YAML's `no_output_timeout: 20m` is **not** a job runtime/cost limit; CircleCI Scale budgets are **soft** (notifications, no job auto-stop), so owner-approved concrete maximum and human cancel playbook are mandatory before a future run.

**Disposition: G2 paid MariaDB integration execution remains NO-GO.** Single next operator step is **read-only**: open CircleCI project `ccpcerp` **Project Settings / Overview** and report only linked organization/project/provider metadata, without exposing tokens or clicking Run/Rerun/Approve/Cancel. Then assess plan/balance, VCS/secret/network access and trusted SHA provenance one step at a time. Any variable creation, pipeline trigger, hold approval, migration, MariaDB write, DEV/PROD action or PR merge requires *separate explicit owner approval*. No app code change during this review.

### Finance PR21 G2 owner-provided CircleCI project identity — 2026-10-28

Owner copied the **live read-only** CircleCI Project Settings / Overview for `ccpcerp`, displaying **`CCPCerp_2026 / ccpcerp`**. Both strings exactly match the CircleCI Finance CI guard/preflight's expected org/repo names. The CircleCI UI displays its modern opaque project slug (`circleci/FQEH9eqNmWE9hhYurkcaW2/5zfreN96yqR3PVoA3gjuRB`) and settings menu. **G2 project display identity PASS**, but this does **not** independently prove VCS branch/trigger settings, any CI variables/context values, checkout keys, approver rights, server/network isolation, plan or credit balance. Source: owner-pasted CircleCI Overview, not an API setting export. Reviewed and recorded in [G2 read-only review §6](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md) with documentation commit `102eca37023b151d0e361e0ad569dc685af80219`.

**Next single read-only check:** Project Settings → Environment Variables: owner should report **only** whether any variables are listed, and whether `CCPC_FINANCE_APPROVED_SHA` is present. Do not share values or screenshots showing secret values, and do not change anything. Other G2 controls still unknown. **G2 paid integration and all ERPNext DEV/PROD operations remain NO-GO.** Draft PR #21 app code unchanged at `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.

### Finance PR21 G2 CircleCI Free credits and empty project environment — 2026-10-28

Owner provided live CircleCI settings screenshots for `CCPCerp_2026 / ccpcerp` after the G2 read-only project identity check. The **Plan screenshot says FREE, 952 credits used this billing period and 29,048 credits remaining**. Official price list (2026-10-08) indicates standard x86 Docker `large` 4CPU/8GB, **20 credits/minute**, eligible on Free; actual credit spend and max job duration remain subject to runtime/plan controls and a later per-run budget/cancel signoff. The **Project Settings → Environment Variables screenshot displays an empty list**, so **no project-level variables were shown; in particular `CCPC_FINANCE_APPROVED_SHA` is absent**. This should fail closed in source's Finance preflight if no alternative injection occurs, but do not test-trigger it under current approval. **Do not set the variable** until a separate explicit G2 run authorization.

**Verified documentation:** [G2 read-only runner/security/cost review §7](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md), new docs commit `c75d270469f66a54bb0ecad1fcd566eeb169a5c0`. Screenshots provide account-state observations, **not evidence of absence of organization contexts, SSH keys, VCS token/checkouts, DEV/PROD routing or other source credentials**. No CI jobs, environment settings or DEVELOPMENT/PRODUCTION touched. **G2 paid integration NO-GO**; next read-only step Project Settings → SSH Keys to report only whether checkout and additional keys exist (yes/no), with no fingerprints, hostnames, values or screenshots containing secrets.

### Finance PR21 G2 additional SSH keys not listed — checkout key pending (2026-10-28)

Owner read-only CircleCI Project Settings → SSH Keys supplied **only the Additional SSH Keys section**. It showed the Add SSH Key action and guidance, **with no existing additional key entries shown**. This is a narrow screenshot/pasted-page observation; **Checkout SSH Key section was not shared**, so existence/type/access remain unverified. In [G2 read-only review §8](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md), commit `4ea622b2cd77f28abe0e9f079dc066d4bf1cf7bd`, this is recorded as additional keys not listed, checkout still pending. Next read-only step: view Checkout SSH Key on same page, report only exists Yes/No; no key values/fingerprints, no Add/Remove, no job triggering. **G2 paid MariaDB integration NO-GO**, app PR21 remains draft at `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.

### Finance PR21 G2 checkout SSH key not listed (2026-10-28)

Owner answered **No** when asked whether the CircleCI Project Settings → SSH Keys **Checkout SSH Key** section shows an existing key. Combined with previous read-only Additional SSH Keys section, **both SSH key types show no existing entries in the supplied CircleCI UI**. This is limited project settings evidence, not proof that GitHub App/integration access, organization contexts, environment injections or DEV/PROD network access are absent. Do not create SSH keys, grant permissions or run any job to test connectivity. **Current G2 read-only review §9**, docs commit `a53e80cd71eab0caef1d19f64fbc782ec15398ee`, records this evidence. Next one-step review: CircleCI Project Settings → **People**, ask only whether any other members have project access (without identities), and whether roles are listed; reconcile actual GitHub push rights later. **G2 paid job remains NO-GO**, PR21 app SHA remains `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.

### Finance PR21 G2 project People: one listed Admin; inherited org access unknown (2026-10-28)

Owner-provided **CircleCI Project Settings → People** screenshot lists **one explicit project member** with project role **Admin**. The same page warns that **Organization Settings** Contributor and Admin role holders can access the project by inheritance. Do not treat `1 Person` as proof that only one human may access pipelines or approve held jobs. No personal email/name was entered into GitHub documentation. See [G2 read-only review §10](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md) recorded in docs commit `a1ca0baad12a1f1e7737b8f71d72bf53f92f57ba`.

**Next read-only single step:** CircleCI Project Settings → People → **Organization Settings** link → organization member roles. Owner to report only **whether any other Admin/Contributor members exist besides the displayed project Admin (Yes/No/Not clear)**; do not share names/emails or modify roles. GitHub push access, CircleCI groups/contexts, runner network isolation and hard budget/cancel control remain pending. G2 Finance paid integration is **NO-GO**. PR21 still OPEN/DRAFT at app SHA `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.

### Finance PR21 G2 org People one Admin / pending zero — 2026-10-28

Owner screenshot of **CircleCI Organization Settings → People** shows **one visible member** with **Org Admin** role and **Pending (0)** invitations. Earlier CircleCI Project Settings → People showed one listed Project Admin. No other Org Admin or Contributor is shown in the supplied view; the member's email/profile is deliberately **not recorded**. This narrowly improves CircleCI operator/access assurance but does **not** prove GitHub push access or CircleCI hold approval eligibility is exclusive, nor certify VCS/contexts/runner networking. Current [G2 read-only review §11](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md) was updated at documentation commit `8e69eeff98dedfebd01ee918f546e106ba99e5e5`.

**Next read-only step:** CircleCI **Organization Settings → Contexts**; report only **any contexts listed: Yes / No / Not clear**, without names or secret values or any modifications. GitHub repo push permissions, triggers, network isolation and budget/cancel remain outstanding. **G2 paid CI run NO-GO**, app PR21 remains OPEN/DRAFT at SHA `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.

### Finance PR21 G2 owner reports no CircleCI contexts — 2026-10-28

The owner answered **No** to whether any **CircleCI Organization Settings → Contexts** are listed. This is **read-only owner-reported UI evidence**, not an organization API audit; it supports no configured contexts visible at that time. Together with the earlier Project Settings Environment Variables empty-state screenshot, **no project variables and no organization contexts were shown**, and the approved-commit gate `CCPC_FINANCE_APPROVED_SHA` is still **absent from the project list**. No CI settings were modified and no pipeline/job executed.

**G2 read-only review §12** [FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md) was updated at docs commit `7e777f68044e092274c2200e0c0816f68bc49a31`. Do not interpret empty context/variable UI as proof no VCS credentials or DEV/PROD network routes.

**Next read-only action:** Owner inspects private GitHub repo `ccpcerp/ccpcerp` **Settings → Collaborators and teams** (or Settings → Access → Collaborators) to report **Yes/No/Not clear whether any other users or teams have write/maintain/admin access**, without identities. No role change, invitation or GitHub app modification. CircleCI trigger/provider settings, runner/egress isolation, time/credit cap and cancel operator still pending. **G2 paid Finance integration NO-GO.** Draft PR #21 HEAD remains `d154886ab45c51878a87a4ecf42e45602d8d9ccb`.

### Finance PR21 GitHub collaborator access independently checked — 2026-10-28

The owner shared private GitHub repo **`ccpcerp/ccpcerp` → Settings → Collaborators and teams**, showing **one direct non-owner collaborator**. The owner asked whether this was already recorded. Review of current G2 checkpoint and this handoff showed **write permissions were previously marked PENDING**, not verified; access settings live in GitHub but are not mirrored automatically into versioned project docs.

**Independent read-only verification:** Connected GitHub `get_repo_collaborator_permission` returned **`write`** for the direct collaborator displayed in the owner's screenshot. Repo metadata confirms owner type **User**, owner login `ccpcerp`, repository private. Collaborator identifier/email deliberately omitted from permanent documentation. **One additional direct collaborator with WRITE/push rights is a confirmed finding**, and current CircleCI Org People (one listed Org Admin) is not proof of exclusive manual-approval rights. CircleCI [workflow docs](https://circleci.com/docs/guides/orchestrate/workflows/) state that repository users with push access can approve/cancel a hold job, subject to effective identity/permission sync. No attempt was made to test whether this GitHub collaborator has a usable CircleCI account or can approve a particular workflow; do not claim either way. No permission revocation should occur automatically or as part of this read-only review.

**Authoritative checkpoint:** [G2 review §13](FINANCE-PR21-G2-READ-ONLY-CIRCLECI-RUNNER-SECURITY-COST-REVIEW-2026-10-28.md), docs commit `64d0b9667a42fdb2388ae5c154e3682bde27671f`. The previously empty CircleCI project SHA variable still blocks the Finance job's fail-closed exact-SHA guard. **No CircleCI pipeline/job/approval, collaborator setting change, deployment or database action authorized.** G2 paid MariaDB integration **NO-GO**, PR21 still OPEN/DRAFT at app SHA `d154886ab45c51878a87a4ecf42e45602d8d9ccb`. Next read-only G2 checks should focus on CircleCI project trigger/VCS type, hosted runner/network isolation and spend/cancellation review, not repeated identity questions that the connected GitHub tools can resolve.
