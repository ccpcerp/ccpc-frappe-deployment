# CCPC ERPNext — CURRENT HANDOFF

**Last verified update:** 2026-10-13 (GitHub connector, test output attachment, and operator terminal reports).  
**Purpose:** This is the **single rolling GitHub handoff** for CCPC ERPNext. Maintain **this same path** at meaningful milestones, during longer conversations before a thread limit is reached, and when the operator requests a handoff. Do not create a new dated Project Source attachment every time.

> **Read first in every new project conversation:** [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), then this handoff, then verify relevant live GitHub branches and commits with the GitHub connection. The permanent ChatGPT Project Instructions define policy; older Project Sources and dated handoffs supply historical context only. If information conflicts, the most recently verified GitHub state takes precedence. If GitHub is inaccessible, report the inability to verify rather than treating old snapshots as current.

## Fifth-checkpoint protected; TISS-to-TREQ internal parties created and verified — 2026-10-13

Operator ran the **already approved** single guarded insert command on isolated DEVELOPMENT site `ccpc-integration2.localhost` only, after confirming the fifth recovery snapshot at `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-accounts-pre-parties-20261013` with artifact prefix `20261013_151050-ccpc-integration2_localhost` and matching database identity. Script preflight confirmed two company accounting configurations, eight correct intercompany accounts, parent party groups and Philippines Territory, no existing party/transaction records, then used normal `frappe.get_doc(...).insert(ignore_permissions=True)` APIs to create **exactly four** parent/party master records (plus corresponding child rows), verified everything before a single `frappe.db.commit()`, and printed:

```text
Isolated site: VERIFIED
Fifth recovery checkpoint: VERIFIED
Two-company accounting configuration: VERIFIED
Party groups and Territory: VERIFIED
No existing party records or transactions: VERIFIED
Creating approved internal trading parties...

Customer Group: Intercompany VERIFIED
Supplier Group: Intercompany VERIFIED

Internal Customer: Integration Test Requester
Represents: Integration Test Requester
Allowed company: Integration Test Issuer
Receivable account: 1312 - Intercompany Receivable - TISS

Internal Supplier: Integration Test Issuer
Represents: Integration Test Issuer
Allowed company: Integration Test Requester
Payable account: 2121 - Intercompany Payable - TREQ

Customer count: 1
Supplier count: 1
Party Account rows: 2
Allowed company rows: 2
Financial transaction baseline: EMPTY

INTERNAL TRADING PARTIES: CREATED AND VERIFIED
```

Specific new records:
- `Customer Group` **Intercompany** (leaf under `All Customer Groups`).
- `Supplier Group` **Intercompany** (leaf under `All Supplier Groups`).
- Internal `Customer` name **Integration Test Requester**, `customer_name=Integration Test Requester`, `customer_type=Company`, `customer_group=Intercompany`, `territory=Philippines`, `is_internal_customer=1`, `represents_company=Integration Test Requester`, `disabled=0`, sole `Allowed To Transact With` **Integration Test Issuer**, sole `Party Account` **1312 - Intercompany Receivable - TISS** owned by issuer.
- Internal `Supplier` name **Integration Test Issuer**, `supplier_name=Integration Test Issuer`, `supplier_type=Company`, `supplier_group=Intercompany`, `is_internal_supplier=1`, `represents_company=Integration Test Issuer`, `disabled=0`, sole allowed company **Integration Test Requester**, sole `Party Account` **2121 - Intercompany Payable - TREQ** owned by requester.
- Explicit non-self-company mappings; `tabCustomer` 1, `tabSupplier` 1, `tabParty Account` 2, `tabAllowed To Transact With` 2. Company count 2, account count 198. Empty `Stock Entry`, `Stock Ledger Entry`, `Sales Invoice`, `Purchase Invoice`, `GL Entry`, `Intercompany Material Billing Batch` checked before and immediately prior to commit.

**Verification status:** Results from operator-pasted terminal output, including normal Frappe DocType reads immediately before commit. Separate **post-commit independent read-only SQL validation is still outstanding**. Backup archive integrity checked, **not** full restoration. These parties support **TISS issuing to TREQ only**, not reverse direction. No material-issue Stock Entries, withdrawal slip records, submitted transaction, billing batch, finance-approval, or actual DB integration tests yet. Persistent `development.localhost` and PRODUCTION untouched by authorized procedure.

**Next step:** one read-only independent SQL inspection of the persisted Customer/Supplier parent fields, both exact `Allowed To Transact With` child rows and `Party Account` child rows, the two Intercompany groups, and all transaction tables. Confirm separate site database identity before connecting. If verified, plan the next synthetic document fixtures by reviewing GitHub current CCPC withdrawal slip, stock issue and billing code/DocTypes, requirements and account correctness. **Request fresh explicit approval before any synthetic Stock Entry, withdrawal slip, invoice, billing batch or other substantive data writes**. Do not rerun already-successful party creation or historical real-company patches.

## Fifth recovery checkpoint independently archive-verified before synthetic internal parties — 2026-10-13

After explicit owner approval, operator ran the **guarded fifth full site backup only** on `ccpc-integration2.localhost` and provided command output. Pre-backup read-only preconditions passed: isolation from persistent `development.localhost`, exactly two test companies with 198 accounts total and eight exact intercompany ledger accounts, intended customer/supplier group parents, leaf `Philippines` Territory, zero internal Customer/Supplier/Party Account/Stock Entry/Stock Ledger Entry/Sales Invoice/Purchase Invoice/GL Entry/Billing Batch records, and four earlier full snapshot artifacts preserved. No synthetic party writes were performed by this backup command.

Official `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"` wrote into the protected **absolute directory** `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-accounts-pre-parties-20261013` with prefix `20261013_151050-ccpc-integration2_localhost`. Operator's verification:
```text
Isolated site: VERIFIED
Both companies and 198 accounts: VERIFIED
Eight dedicated intercompany accounts: VERIFIED
Customer/Supplier group prerequisites: VERIFIED
Territory: VERIFIED
Party and transaction baseline: VERIFIED
Four earlier recovery checkpoints: PRESERVED
Creating fifth recovery checkpoint...
Backup for Site ccpc-integration2.localhost has been successfully completed with files
Verifying fifth recovery checkpoint...
database.sql.gz | 980410 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
FIFTH RECOVERY CHECKPOINT: VERIFIED AND SECURED
```
This confirms **five distinct archive-verified recovery checkpoints**. The new files contain site configuration secrets, remain restricted to protected private directory, and must never be committed to GitHub. No recovery restore test has been performed.

Reviewed current authoritative `ccpcerp` application branch `review/intercompany-approval-failure-tests` at `806fa23516490ec7beefcff03a1baa09d722120e`, especially batch `_get_internal_party` and historical real-CCPC-only party patch. Reviewed ERPNext v16 `Customer`, `Supplier`, `Customer Group`, `Supplier Group` controllers and `erpnext.accounts.party.validate_party_accounts`: Customer/Supplier identity may be by name or naming series; each document supports child tables `companies` (Allowed To Transact With) and `accounts` (Party Account), which validates account belongs to expected company. Customer/Supplier group parent records `All Customer Groups`/`All Supplier Groups` are groups; `Intercompany` should be leaf. `Customer` should represent TREQ and only be allowed under TISS with TISS `1312` receivable; `Supplier` should represent TISS and only allowed under TREQ with TREQ `2121` payable. The other direction is not yet being tested.

**Next authorized action:** one guarded, test-site-only standard-ERPNext document insert of exactly two `Intercompany` group masters plus one internal Customer and one internal Supplier with a single allowed-company row and a single Party Account row apiece; check fifth snapshot identity first, absence of all parties, intact eight dedicated accounts and empty transaction baseline, verify all created fields and counts before a single commit, on error rollback and do **not** blindly rerun. No invoice, billing batch, GL, stock, migration or PRODUCTION scope. Current documentation records verified backup only, **not** that internal party creation succeeded.

## Owner approved fifth snapshot and minimal TISS-to-TREQ internal parties — 2026-10-13

Operator explicitly replied **Approved** to a scoped plan for (1) a new **post-eight-accounts, pre-internal-parties** full recovery snapshot and (2) only the test-site `Intercompany` Customer Group and Supplier Group, internal Customer representing `Integration Test Requester (TREQ)` allowed to transact only with `Integration Test Issuer (TISS)` and linked to issuer receivable `1312 - Intercompany Receivable - TISS`, and internal Supplier representing `Integration Test Issuer (TISS)` allowed only with `Integration Test Requester (TREQ)` and linked to requester payable `2121 - Intercompany Payable - TREQ`.

Authority is **exclusively isolated DEVELOPMENT site `ccpc-integration2.localhost`**. The fifth recovery snapshot should use protected directory `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-accounts-pre-parties-20261013` and site-specific, absolute backup path; must check correct DB identity distinct from persistent `development.localhost`, verify prior four snapshots remain, eight dedicated ledger records retained/each test company has 99 accounts, Customer and Supplier groups absent, one leaf Philippines Territory, and zero Customer, Supplier, Party Account, billing, GL, stock and sales/purchase invoice data. Account/group/root/party details must be reconfirmed read-only before any write; Frappe backup housekeeping can delete standard-backup files older than configured hours, so guard default retention before running `bench backup` with absolute `--backup-path`. Validate resulting database gzip, public/private tar, site_config JSON/db identity and secure permissions. **Do not create internal parties until fifth snapshot is confirmed successful.** All preexisting snapshots must remain.

Internal-party writes later (after snapshot confirmation) must use standard ERPNext document APIs, company and account allowlists, exact reciprocal per-direction Party Account mappings, group validation, and postinsert checks before single DB commit. Customer and Supplier DocType names may be naming series, so validate their actual `customer_name`, `supplier_name` and `represents_company`, not assume primary keys. Existing real-company-only CCPC historical patches are out of scope and must not run. No reverse-direction parties, stock entries, invoices, billing batches, migrations, or persistent DEVELOPMENT/PRODUCTION changes were authorized. No snapshot or party writes have been reported yet in response to this approval.

## Post-commit synthetic ledger and internal-party prerequisites audit verified — 2026-10-13

Operator ran a **read-only post-commit** MySQL audit on isolated `ccpc-integration2.localhost` after the fourth snapshot and eight account insertions. Readout confirms eight exact-account records persisted:
```text
Integration Test Issuer | 1312 | 1312 - Intercompany Receivable - TISS | Receivable
Integration Test Issuer | 2121 | 2121 - Intercompany Payable - TISS | Payable
Integration Test Issuer | 5150 | 5150 - Intercompany Materials Expense - TISS | [blank]
Integration Test Issuer | 6050 | 6050 - Intercompany Material Charges - TISS | [blank]
Integration Test Requester | 1312 | 1312 - Intercompany Receivable - TREQ | Receivable
Integration Test Requester | 2121 | 2121 - Intercompany Payable - TREQ | Payable
Integration Test Requester | 5150 | 5150 - Intercompany Materials Expense - TREQ | [blank]
Integration Test Requester | 6050 | 6050 - Intercompany Material Charges - TREQ | [blank]
Dedicated account count: 8
```
Customer Group master has `All Customer Groups` (is_group=1) and non-group `Commercial`, `Government`, `Individual`, `Non Profit` (no `Intercompany`). Supplier Group has `All Supplier Groups` (is_group=1) and non-group `Distributor`, `Electrical`, `Hardware`, `Local`, `Pharmaceutical`, `Raw Material`, `Services` (no `Intercompany`). Territory `Philippines` (leaf) exists under `All Territories`. `tabCustomer`, `tabSupplier`, `tabParty Account`, `tabStock Entry`, `tabSales Invoice`, `tabPurchase Invoice`, `tabIntercompany Material Billing Batch` all remain count 0 at audit.

Further reviewed `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` on verified `review/intercompany-approval-failure-tests` app branch: `approve_and_create_invoices` obtains exactly one enabled **Customer representing requesting company** and exactly one enabled **Supplier representing issuing company**. For **one-direction integration test only**, minimum synthetic party design (not yet authorized/executed):
1. `Customer Group` `Intercompany` as leaf under `All Customer Groups`; `Supplier Group` `Intercompany` leaf under `All Supplier Groups`.
2. One Customer named in `customer_name` field `Integration Test Requester` (actual document identifier may follow naming series), `customer_type=Company`, `territory=Philippines`, `is_internal_customer=1`, `represents_company=Integration Test Requester`, `disabled=0`, with sole `Allowed To Transact With` company `Integration Test Issuer` and one Party Account row for issuer `1312 - Intercompany Receivable - TISS`.
3. One Supplier named in `supplier_name` field `Integration Test Issuer` (actual document identifier may use naming series), `supplier_type=Company`, `is_internal_supplier=1`, `represents_company=Integration Test Issuer`, `disabled=0`, sole allowed company `Integration Test Requester` and Party Account row for requester `2121 - Intercompany Payable - TREQ`.
4. No self-trading links or own-company Party Account rows. Company and account scope must be validated. This minimal two-party configuration only supports `TISS` -> `TREQ` billing; reverse direction would require two additional parties later.
5. ERPNext version-16 Customer/Supplier controllers run `validate_party_accounts` plus internal uniqueness checks and may generate naming series IDs. Use supported document inserts, preflight table schema/defaults and naming, followed by postcommit read-only validation. Existing `ccpcerp/patches/v1_0/create_intercompany_parties.py` is **not applicable** because it targets actual CCPC-company names.

**Next approval gate**: obtain explicit operator authorization for taking a **new post-account/pre-party recovery snapshot** and creating only two `Intercompany` group records + exactly one internal Customer, one internal Supplier, each with one allowed-companies row and one Party Account row. Preserve prior four snapshots; archive verification != tested restore. No additional data was written by the audit, and no party fixtures have yet been created. Invoice submission, stock movements, GL entries, persistent `development.localhost`, or PRODUCTION are outside scope.

## Eight isolated intercompany ledger accounts created and verified — 2026-10-13

Operator ran the previously approved single-shot Frappe/ERPNext Account fixture insertion **only on isolated `ccpc-integration2.localhost`**. Before writes, script rechecked target-vs-persistent-`development.localhost` database isolation; fourth snapshot `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-requester-pre-accounts-20261013/20261013_135316-ccpc-integration2_localhost-*` (four nonempty files, matching DB identity, archive checks documented separately); exactly two test companies `Integration Test Issuer (TISS)` and `Integration Test Requester (TREQ)`; complete Frappe/ERPNext setup; valid PHP/Philippines Company settings and enabled non-group Cost Centers; 95 Standard CoA accounts per company; eight suitable enabled parent groups; no name/number conflicts, and no Stock Entries, Sales Invoices, Purchase Invoices, Billing Batches, GL Entries, Customers, Suppliers or Party Account rows.

Using `frappe.get_doc({"doctype":"Account", ...}).insert()` (no SQL INSERT, no historical real-company patches), it created and checked **exactly four non-group PHP ledger accounts for each company**:

| Account number | Account name | Parent group | Root / account type |
|---|---|---|---|
| `1312` | `Intercompany Receivable` | `Accounts Receivable - <abbr>` | Asset / Receivable |
| `2121` | `Intercompany Payable` | `Accounts Payable - <abbr>` | Liability / Payable |
| `5150` | `Intercompany Materials Expense` | `Indirect Expenses - <abbr>` | Expense / blank |
| `6050` | `Intercompany Material Charges` | `Indirect Income - <abbr>` | Income / blank |

Full account names are `<number> - <account_name> - TISS` and `<number> - <account_name> - TREQ`, matching `ccpcerp` billing-code string requirements. The command postchecked each account's saved `company`, number, account name, expected parent, root type, account type, ledger/non-group, enabled status and PHP currency; exactly 99 Account rows per company; exactly two Companies; unchanged empty transaction and party baseline. It performed **one `frappe.db.commit()` only after these checks**. User-reported terminal end:
```text
Isolated site: VERIFIED
Fourth recovery checkpoint: VERIFIED
Both company configurations: VERIFIED
All eight parent accounts: VERIFIED
No account name/number conflicts: VERIFIED
Transaction and party baseline: VERIFIED
Creating eight dedicated accounts...

COMPANY: Integration Test Issuer (TISS)
VERIFIED: 1312 - Intercompany Receivable - TISS
VERIFIED: 2121 - Intercompany Payable - TISS
VERIFIED: 5150 - Intercompany Materials Expense - TISS
VERIFIED: 6050 - Intercompany Material Charges - TISS
Total company accounts: 99

COMPANY: Integration Test Requester (TREQ)
VERIFIED: 1312 - Intercompany Receivable - TREQ
VERIFIED: 2121 - Intercompany Payable - TREQ
VERIFIED: 5150 - Intercompany Materials Expense - TREQ
VERIFIED: 6050 - Intercompany Material Charges - TREQ
Total company accounts: 99

Total companies: 2
EIGHT INTERCOMPANY ACCOUNTS: CREATED AND VERIFIED
```
**Completion boundary:** Account fixtures and pre-account archive verified, but no separate post-commit SQL confirmation yet, no restoration drill, no real database integration/rollback/concurrency tests, no internal Customer/Supplier or Party Account fixtures, and **no inventory or financial transactions**. Existing historical patches hardcode real CCPC business companies and must not be run on TISS/TREQ.

**Next:** read-only checks on Customer Group/Supplier Group/Territory defaults, Company ledger Cost Centers, exact eight account records and current empty-party/transaction baseline, then plan scoped internal test Customer representing TREQ for TISS and internal test Supplier representing TISS for TREQ, with company allowlist and dedicated Party Account mapping. Obtain explicit separate operator permission before creating party fixtures; present prior archive-verified snapshot situation and consider a new post-account/pre-party snapshot. Do not change persistent `development.localhost` or PRODUCTION.

## Fourth isolated recovery snapshot verified before intercompany-account inserts — 2026-10-13

Operator executed the **approved** pre-account site-scoped backup on isolated `ccpc-integration2.localhost` after synthetic `TISS` and `TREQ` Companies were created. Read-only safety checks passed: target DB isolated from `development.localhost`, exact two-company names and abbreviations, 95 existing Standard CoA accounts in each Company, verified company-specific enabled parent Account groups `Accounts Receivable`, `Accounts Payable`, `Indirect Expenses`, `Indirect Income`, no dedicated account numbers 1312/2121/5150/6050, no Stock Entries, Sales/Purchase Invoices, billing batches, Customers or Suppliers; prior three backup checkpoints preserved.

Backup command used **absolute path** `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-requester-pre-accounts-20261013` with `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"`. Operator output:
```text
Site isolation: VERIFIED
Two-company baseline: VERIFIED
Standard account parent groups: VERIFIED
No dedicated intercompany accounts: VERIFIED
Transaction and internal party baseline: VERIFIED
Three earlier recovery snapshots: PRESERVED
Backup for Site ccpc-integration2.localhost has been successfully completed with files
database.sql.gz | 979004 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database archive: PASSED
Public/private archives: PASSED
Database identity: VERIFIED
POST-TREQ BACKUP: VERIFIED AND SECURED
```
New snapshot filename prefix `20261013_135316-ccpc-integration2_localhost`. **This is the fourth** archive-verified recovery checkpoint (no full restore drill yet). No intercompany accounts have been inserted yet.

As explicitly approved, next authorized step is **one guarded creation of exactly eight standard-ERPNext Account ledger records**, four numbers `1312`, `2121`, `5150`, `6050` in each of `TISS` and `TREQ`, with exact names and valid parent groups matching the Standard CoA. Use Frappe `Account.insert()` and a single `frappe.db.commit()` only after verifying all eight account records; stop and inspect rather than rerun if exceptions occur. ERPNext v16 source confirms `get_autoname_with_number` returns `<number> - <account_name> - <company_abbr>`, enforces nonduplicate number/company and parent groups, derives account currency from Company, and runs nested-set update on save. Do not execute real-company-specific historical patches. Current operator approval does not include internal Customers/Suppliers, Stock Entries, invoices, or other sites/production. GitHub documentation update is not evidence that those eight accounts have been created.

## Approved isolated post-TREQ backup and eight intercompany ledger fixtures — 2026-10-13

Operator explicitly **approved** creating another full, site-scoped backup and adding the **eight** test-only `Account` ledger rows (four each, two fictional test companies) on isolated `ccpc-integration2.localhost`: `1312 - Intercompany Receivable` (Asset/Receivable, under existing Accounts Receivable group), `2121 - Intercompany Payable` (Liability/Payable, under existing Accounts Payable group), `5150 - Intercompany Materials Expense` (Expense, under existing Indirect Expenses group), `6050 - Intercompany Material Charges` (Income, under existing Indirect Income group), each suffixed by `TISS` or `TREQ`. Scope **excludes** internal party creation, Stock Entries, Sales/Purchase Invoices, broad site migrate, persistent `development.localhost`, PRODUCTION, and historical real-business company patches. Request remains one verified step at a time.

Before account writes: take a fourth recovery snapshot named `post-requester-pre-accounts-20261013` using **absolute** `bench backup --backup-path` (avoid old `sites/sites/` mistake), `--with-files --ignore-backup-conf`. Confirm source target-db isolation, exact two company records, 95 standard accounts each, no existing dedicated 1312/2121/5150/6050 accounts, zero transaction counts, preserved earlier backups, and safe standard-backup retention; validate new database archive with `gzip -t`, public/private TAR listings, JSON and DB identity, and restrict permissions. Previously archived backups, including post-wizard/pre-TREQ `20261013_133756`, are archive checked but **not restore tested**. The backup must be reported as operator-verified before moving to Account inserts; no silent site execution by GitHub tool. Frappe v16 `new_backup` calls `delete_temp_backups` in default backup location even when absolute `--backup-path` is provided, so preflight must guard against any stale standard-directory files that it might delete.

After backup is confirmed, Account document APIs should preflight and verify exact names, unique numbers, valid company-specific enabled parent group/root, company cost center and transaction baseline, create all eight in one guarded transaction, post-verify and commit once. No account fixture changes yet reported as executed.

## Read-only TISS/TREQ intercompany account and party fixture audit — 2026-10-13

Operator's read-only SQL audit completed on isolated `ccpc-integration2.localhost` (explicit target-vs-persistent-DEVELOPMENT database name comparison in command); no write occurred. `Integration Test Issuer` (`TISS`), `Integration Test Requester` (`TREQ`) each have **95 Standard Chart of Accounts records** distributed as Asset=29, Equity=6, Expense=33, Income=7, Liability=20, with default cost centers `Main - TISS` / `Main - TREQ`, and inventory account `Stock In Hand - TISS` / `Stock In Hand - TREQ`. Each has **zero Account records with numbers 1312, 2121, 5150, or 6050**. Global `tabCustomer` count 0 (internal 0), `tabSupplier` count 0 (internal 0), and `tabParty Account` 0. This is a synthetic test fixture gap, not an error in Company insertion.

The TISS chart contains verified parent groups `Accounts Receivable - TISS` (Asset), `Accounts Payable - TISS` (Liability), `Indirect Expenses - TISS` (Expense), `Indirect Income - TISS` (Income). TREQ was created from same Standard template, but **its specific parent group names/properties must be verified** before any new account writes. In `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` reviewed on branch `review/intercompany-approval-failure-tests`, exact invoice defaults per Company abbreviation are `1312 - Intercompany Receivable` (Asset/Receivable), `2121 - Intercompany Payable` (Liability/Payable), `5150 - Intercompany Materials Expense` (Expense), and `6050 - Intercompany Material Charges` (Income); they must be enabled, valid leaf accounts. `_get_internal_party` requires **exactly one enabled internal Customer representing the requester** and **one enabled internal Supplier representing the issuer**. ERPNext v16 `Account` controller `autoname` uses `get_autoname_with_number` and enforces unique account number per company, proper group parent and root. Historical real-company-specific CCPC patches expect a different parent account numbering and must **not** be run here.

**Proposed fixture design (not executed or approved):** create four exact additional ledger accounts per fictional company under existing verified Standard-chart parent groups, e.g. receivable in Accounts Receivable, payable in Accounts Payable, expense in Indirect Expenses, income in Indirect Income. Validate names, numbers, company, root, type, is_group=0, enabled, and parent groups, no duplicate account number/name; use Frappe `Account.insert()` in one guarded test-site-only transaction, no SQL inserts. Verify both company charts preserve baseline. In a later separately approved stage, create appropriate `Intercompany` Customer/Supplier groups as needed and internal Customer/Supplier with company restrictions and Party Accounts, after inspecting group/territory defaults. Before account fixture changes, consider taking a new post-second-company/pre-accounts checkpoint; third verified backup is pre-second-company. No permission to create accounting fixtures yet; request explicit approval. No actual Stock Entry, Sales/Purchase Invoice or real-DB rollback/concurrency test was run.

## Isolated DEVELOPMENT second synthetic company created and verified — 2026-10-13

Operator completed the **explicitly approved** single Frappe/ERPNext Company document insert on isolated `ccpc-integration2.localhost`, after verifying the full `20261013_133756` post-wizard/pre-requester recovery snapshot, correct 2026 fiscal year, both composite indexes and zero transaction baseline. Operator terminal output:
```text
Isolated site: VERIFIED
Post-setup recovery snapshot: VERIFIED
Company, fiscal year, indexes, and transaction baseline: VERIFIED
Creating Integration Test Requester (TREQ)
Requester: Integration Test Requester
Abbreviation: TREQ
Country: Philippines
Currency: PHP
Default cost center: Main - TREQ
Requester accounts: 95
Requester warehouses: 5
Total companies: 2
SECOND TEST COMPANY: CREATED AND VERIFIED
```
The script used `frappe.get_doc({"doctype":"Company", "company_name":"Integration Test Requester", "abbr":"TREQ", "country":"Philippines", "default_currency":"PHP", "enable_perpetual_inventory":1, "create_chart_of_accounts_based_on":"Standard Template", "chart_of_accounts":"Standard"}).insert()` and committed after verifying the returned Company fields, non-group enabled requester Cost Center belonging to TREQ, nonzero chart and warehouses, and exactly two companies. Previously verified issuer is `Integration Test Issuer` (`TISS`, PHP, Philippines, `Main - TISS`). No stock entries, sales invoices, purchase invoices, or billing batches were created by the submitted company-create script; transaction counts were checked before the insert, not rechecked afterward. **No real DB billing workflow, rollback, or concurrency tests executed.**

**GitHub code review**: `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py` requires exact ledger accounts `1312 - Intercompany Receivable - {abbr}`, `2121 - Intercompany Payable - {abbr}`, `5150 - Intercompany Materials Expense - {abbr}`, `6050 - Intercompany Material Charges - {abbr}` and enabled leaf Cost Centers, plus internal Customer representing requester and internal Supplier representing issuer for invoice creation. `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` expects parent accounts tailored to real CCPC chart (`1310`, `2001`, `5100`, `6000`); `create_intercompany_parties.py` targets four actual CCPC-group companies. Neither patch should run blindly on fictional TISS/TREQ standard charts. Do not assume dedicated accounts/parties exist.

**Next safely authorized action:** read-only inspection of TISS/TREQ default accounts, available account parent hierarchies, existing internal Customers/Suppliers/Party Account rows and current transaction baseline. Then design a scoped synthetic account/party fixture plan in GitHub and request explicit permission for master-data writes (current approval covered second Company only). All backup archives remain private with pre-index, pre-wizard and post-wizard/pre-requester snapshots; archive checks are not full restore tests. No modifications to `development.localhost` or PRODUCTION.

## Isolated DEVELOPMENT post-setup/pre-requester backup verified — 2026-10-13

User explicitly **approved creating a new post-setup backup and second fictional test Company** `Integration Test Requester` (`TREQ`, Philippines/PHP, ERPNext Standard CoA), exclusively on `ccpc-integration2.localhost`, after `Integration Test Issuer` (`TISS`) completed its wizard. No authorization for stock moves, invoice creation, historical real-company patches, persistent `development.localhost`, or PRODUCTION.

Operator ran guarded full-site `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path "$DEST"`, using an **absolute** path to avoid the earlier accidental `sites/sites` duplication. All post-setup/pre-requester baseline checks and archive integrity succeeded:
```text
Isolated site: VERIFIED
Initial ERPNext setup: VERIFIED
Previous recovery backups: PRESERVED
Pre-requester transaction baseline: VERIFIED
Backup for Site ccpc-integration2.localhost has been successfully completed with files
database.sql.gz | 973014 bytes
files.tar | 10240 bytes
private-files.tar | 10240 bytes
site_config_backup.json | 212 bytes
Database gzip integrity: PASSED
Public and private archives: PASSED
Database identity: VERIFIED
POST-SETUP BACKUP: VERIFIED AND SECURED
```
Protected backup location within bench:
`sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/post-setup-pre-requester-20261013/`
Four files have common filename prefix `20261013_133756-ccpc-integration2_localhost`. This is the **third** preserved checkpoint, after the pre-index and pre-wizard backups. Gzip/TAR/JSON verification and live DB name identity checks passed; **no full restore test** performed. No second Company has yet been created, no transaction records created.

Source-reviewed `erpnext/version-16/erpnext/setup/doctype/company/company.py`: new `frappe.get_doc({"doctype":"Company",...}).insert()` invokes standard `on_update` routines creating chart of accounts, default warehouses, default cost center, and company departments. Use ERPNext standard chart name `Standard`; do not rerun setup wizard nor run `bench migrate`. Require a one-site preflight showing `TISS` only, valid post-setup snapshot, isolated DB, zero transactional records, existing 2026 fiscal year, company abbreviations, and previously verified indexes before the **one-time** insertion. Then verify TREQ’s exactly matching Company fields, default leaf cost center, nonzero chart of accounts and warehouses, and issuer preservation; stop and inspect on any failure. Frappe Company hooks may make broader fixture/config changes; do not blindly retry. Do not run old CCPC account/customer/supplier patches hardcoded for real group entities, and dedicated billing accounts/parties are not yet created.

## Post-wizard isolated integration baseline independently checked — 2026-10-13

User pasted read-only `MySQLdb` result for `ccpc-integration2.localhost`, confirming site database remains different from persistent `development.localhost` (command would stop otherwise). Verified exact values:
```text
Companies: (('Integration Test Issuer', 'TISS', 'PHP', 'Philippines', 'Main - TISS'),)
Fiscal years: (('2026', datetime.date(2026, 1, 1), datetime.date(2026, 12, 31)),)
Billing indexes:
idx_icmb_scope VERIFIED
idx_icmbi_source_parent VERIFIED
Transaction baseline:
tabStock Entry: 0
tabSales Invoice: 0
tabPurchase Invoice: 0
tabIntercompany Material Billing Batch: 0
POST-SETUP READ-ONLY CHECK: COMPLETED
```
Both composite indexes retain full ordered nonunique BTREE definitions without prefixes after wizard, and the four tested transaction DocTypes remain empty. **No Purchase or Sales Invoices, Stock Entries, or Billing Batches have been created.** One Company is present, with issuer default enabled-leaf Cost Center not independently checked yet. No tests of actual accounting/inventory operations, deadlocks or transaction rollback yet.

Reviewed relevant source on verified `ccpcerp/ccpcerp` branch `review/intercompany-approval-failure-tests`: `_validate_companies` in batch DocType only rejects identical issuing/requesting company (it does not restrict to the four actual-group-name constants of historical seed patches). `_get_company_invoice_defaults` requires exact non-group receivable/payable/expense/income accounts `1312`, `2121`, `5150`, `6050` with names suffixed by test-company abbreviations, plus valid Cost Centers. In ERPNext v16 `Company` document insertion can create default COA, cost centers and warehouses; new test requester should use standard Frappe document API, not direct SQL or re-run setup wizard.

**Next approval gate:** take distinct **post-wizard pre-second-company** site-scoped full backup in a unique protected location, verify archives and preserve older snapshots; then create one additional fictional `Integration Test Requester` (suggest abbreviation `TREQ`, country Philippines, PHP, Standard COA) on `ccpc-integration2.localhost` only. User's prior approval covered the first issuer company setup, not the second company or synthetic financial transactions. Seek their separate approval for backup + second Company before any write. Use site-scoped permissions and preflight. Do not invoke historic real-company party/account patches automatically; plan separate test-fixture account/party and synthetic transaction steps. No PRODUCTION action.

## Isolated DEVELOPMENT ERPNext initial setup verified — 2026-10-13

Operator completed previously approved **one-time Frappe/ERPNext version-16 initial setup** exclusively on isolated `ccpc-integration2.localhost`, using the official `frappe.desk.page.setup_wizard.setup_wizard.setup_complete(args)` entrypoint called once from the site context rather than `bench execute`. Inputs were `Integration Test Issuer` (abbreviation `TISS`), `Philippines`, `PHP`, `Asia/Manila`, `2026-01-01` through `2026-12-31`, chart template `Standard`, `setup_demo=0`, `enable_telemetry=0`. Preflight confirmed distinct target DB versus persistent `development.localhost`, four archive-verified pre-setup snapshot files in `sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/pre-setup-20261013` and an initially uninitialized/empty master-data baseline.

Operator terminal output (reported, not independently queried by connector):
```text
Site isolation: VERIFIED
Pre-setup recovery snapshot: VERIFIED
Initial setup preconditions: VERIFIED
Initializing Integration Test Issuer (TISS)
Updating Dashboard for frappe
Updating Dashboard for erpnext
Updating Dashboard for ccpcerp
Setup wizard returned: SUCCESS
frappe setup_complete = 1
erpnext setup_complete = 1
ccpcerp setup_complete = 0
Test company abbreviation: TISS
Fiscal Year: 1 records
Account: 95 records
Cost Center: 2 records
Warehouse: 5 records
UOM: 239 records
Item Group: 6 records
INITIAL ERPNEXT SETUP: VERIFIED
```
Python produced nonfatal warnings because interpreter was invoked with `../env/bin/python` while inside `sites`; command completed successfully. The CCPC flag remains 0 as app has no active wizard setup-complete hook; Frappe and ERPNext 1 signify base wizard completion. Only one fictional Company was created, **not** the second `Integration Test Requester`. Do **not** infer default chart is compatible with the custom billing code's exact accounts `1312`, `2121`, `5150`, `6050`; source review found these must be provisioned intentionally for each test Company. Do not run real-group-only historical intercompany account/party patches with fictional firms. Existing two composite intercompany billing indexes were separately verified before wizard, but **should be checked read-only afterward**. No Stock Entries, Sales/Purchase Invoices or real DB integration/rollback/concurrency tests performed. Do not touch persistent `development.localhost` or PRODUCTION. Pre-setup backup is archive verified, not restoration tested.

**Next:** read-only post-wizard verification of `Company`, `Global Defaults`/`System Settings`, `Fiscal Year`, `Account` / `Cost Center` / `Warehouse` essentials, and retained billing index definitions. Then plan a post-setup checkpoint and request separate user approval for creating the second fictional Company and scoped test fixtures; do not make unintended transactions.

## Isolated DEVELOPMENT pre-setup snapshot verified and relocated — 2026-10-13

User approved taking a fresh pre-wizard snapshot of **`ccpc-integration2.localhost`** and running initial ERPNext setup for fictional issuer `Integration Test Issuer (TISS)`, Philippines/PHP, 2026-01-01 through 2026-12-31, ERPNext Standard chart, no demo data. During the first backup command Frappe's `--backup-path` interpreted a relative `sites/...` beneath the bench `sites` directory, creating a `sites/sites/...` path and causing the wrapper's immediate verification to fail (not a reported backup failure). Subsequent guarded command validated backup database identity and `gzip -t` / `tar -tf` / JSON, preserved older `20261013_102539` backup, and moved only the new snapshot to the intended site directory. Operator output:
```text
Backup database identity: VERIFIED
Previous backup: PRESERVED
Backup archive integrity: PASSED
20261013_104420-ccpc-integration2_localhost-database.sql.gz | 899304 bytes
20261013_104420-ccpc-integration2_localhost-files.tar | 10240 bytes
20261013_104420-ccpc-integration2_localhost-private-files.tar | 10240 bytes
20261013_104420-ccpc-integration2_localhost-site_config_backup.json | 212 bytes
Backup relocated to: /workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/ccpc-test-snapshots/pre-setup-20261013
PRE-SETUP BACKUP: VERIFIED AND SECURED
```
Archive validation is **not** a full test restore. No ERPNext wizard or synthetic company/data writes yet reported. Preserve both snapshots and never commit their contents. User authorization covers site-scoped initial ERPNext wizard setup and backup only; **not** stock entries, purchase/sales invoices, persistent `development.localhost`, or PRODUCTION.

Source review `frappe/version-16` and `erpnext/version-16` shows authoritative wizard function `frappe.desk.page.setup_wizard.setup_wizard.setup_complete(args)` dispatches ERPNext stages. ERPNext `stage_fixtures`, `setup_company` and `setup_defaults` provision baseline records. The ERPNext Standard chart argument is `"Standard"`; no demo data when `setup_demo=0`. CCPC hooks branch contains no active `setup_wizard_stages` or `setup_wizard_complete` hook; therefore after success **Frappe and ERPNext flags** should be 1 while CCPC may remain 0. Initial setup also changes site system settings and may enable the site scheduler. Next step: run guarded one-site official setup entrypoint (never broad `bench migrate`), report postconditions and any exceptions without rerun, and document actual result.

## Isolated DEVELOPMENT Setup Wizard completion flags verified — 2026-10-13

Operator ran a read-only parameterized `MySQLdb` query of `tabInstalled Application` on **`ccpc-integration2.localhost`**. Results: `ccpcerp setup_complete = 0`, `erpnext setup_complete = 0`, `frappe setup_complete = 0`. This is consistent with no initial setup wizard yet completed and the documented zero UOM / Item Group / Fiscal Year / Account / Cost Center / parties / Warehouse / Company records. Frappe, ERPNext and CCPC apps remain installed, two billing composite indexes independently verified, and pre-index archive-verified backup preserved.

GitHub `ccpcerp/hooks.py` on reviewed app branch shows no active `setup_wizard_stages` or `setup_wizard_complete` declarations; a separate `after_migrate = "ccpcerp.setup.after_migrate"` hook exists but must **not** invoke general `bench migrate` to initialize this test site. Review of Frappe/ERPNext v16 setup source confirms initial setup provisions normal master data through supported setup APIs, including fixtures and a first Company; full setup will write many configuration/master-data rows and should be run **only after explicit approval for isolated site**. Existing historical CCPC accounts/parties patches use actual group company names, and must not be run indiscriminately with fictional companies. No wizard invocation, test master-data writes, or production actions performed yet.

**Next proposed decision:** seek approval to perform supported initial ERPNext setup using entirely fictional issuer company, `Philippines`, `PHP`, fiscal year 2026, without demo/company business data copied from live sites; document complete steps and verify postconditions. Then separately plan a second fictional requester company and accounts/parties/warehouses for real DB integration tests, with backup checkpoints. Do not mark any synthetic transaction as a tested result until executed in this DB.

## Isolated DEVELOPMENT ERPNext setup/master-data readiness confirmed — 2026-10-13

Operator ran read-only table existence and `COUNT(*)` checks **only on `ccpc-integration2.localhost`** after the index milestone. Results: `tabCurrency=149`; `tabUOM=0`, `tabItem Group=0`, `tabFiscal Year=0`, `tabAccount=0`, `tabCost Center=0`, `tabCustomer Group=0`, `tabSupplier Group=0`, and `tabTerritory=0`. Prior checks likewise found zero Company/Warehouse/Item/Stock Entry/Sales Invoice/Purchase Invoice/Billing Batch/Billing Item rows. Installation has created DocTypes but core operational master data is not provisioned, so end-to-end inventory/billing database integration tests cannot yet run. No records created by this check.

**Frappe/ERPNext version-16 source review (GitHub):** `erpnext/setup/setup_wizard/setup_wizard.py` sequences fixtures, company, defaults; `erpnext/setup/setup_wizard/operations/install_fixtures.py` creates UOMs, Item Groups, Territory, Customer/Supplier Groups, fiscal year, first Company and defaults; `frappe/__init__.py:is_setup_complete()` checks `tabInstalled Application.is_setup_complete` for Frappe and ERPNext. Fresh-site configuration is not the same as a completed setup wizard. Review readiness and wizard flags read-only before proposing any write. Avoid direct SQL inserts; use supported Frappe/ERPNext APIs with synthetic company names on the isolated site, after separate authorization, and plan code/fixture prerequisites on GitHub first. Real-business-name-only CCPC account/party historical patches must not be used blindly with fictional test companies. The user has not yet authorized creating fixture or financial records.

## Isolated DEVELOPMENT integration fixture baseline confirmed empty — 2026-10-13

Operator ran read-only `MySQLdb` queries against `ccpc-integration2.localhost` after two required index definitions were created/verified. All eight tables exist and each contained **0 rows**: `tabCompany`, `tabWarehouse`, `tabItem`, `tabStock Entry`, `tabSales Invoice`, `tabPurchase Invoice`, `tabIntercompany Material Billing Batch`, and `tabIntercompany Material Billing Item`. These results do not assert other ERPNext configuration tables are empty. The site is an empty baseline for isolated synthetic data; **there is no current real-DB end-to-end coverage** of stock, billing, rollback, permissions, or concurrency.

**GitHub source review:** `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py` replaces Frappe DB with `MagicMock`, and `test_intercompany_billing_approval_failures.py` explicitly documents mocked failure-path checks, not true MariaDB rollback. Billing invoice defaults in `intercompany_material_billing_batch.py` require both companies with enabled non-group cost centers and dedicated account names by abbreviation `1312` receivable, `2121` payable, `5150` expense, `6050` income. The historical account and internal-party seed patches `create_intercompany_material_accounts.py` and `create_intercompany_parties.py` are hardcoded for four actual business-name companies (CCPC/RMC/GSL/WFC) and expect chart-of-accounts parents; do not execute these patches on arbitrary fictional companies or assume fresh `install-app` executed their bodies. Suitable synthetic tests should use **new fictional company names and abbreviations with explicitly test-scoped prerequisite accounts and parties**, or have separately reviewed fixtures; do not copy any real DEVELOPMENT/PRODUCTION data.

**Next:** plan/version test fixtures in GitHub-first review process, inspect necessary Frappe/ERPNext master-data requirements and then request distinct approval before creating fixtures/financial records on `ccpc-integration2.localhost`. Leave persistent `development.localhost`, PRODUCTION, historical patch log and untracked `AGENTS.md` untouched. Existing site backup is a pre-index recovery point only and restoration has not been tested.

## Isolated DEVELOPMENT billing indexes created and independently verified — 2026-10-13

**Operator-approved schema operation completed successfully** on `ccpc-integration2.localhost` only. Operator submitted terminal output for guarded command executed inside `frappe_docker_devcontainer-frappe-1` as `frappe` user. Preconditions checked `review/intercompany-approval-failure-tests` at exact commit `806fa23516490ec7beefcff03a1baa09d722120e` with no tracked modifications, four pre-change backup artifacts existed, and new site had a different DB name from persistent `development.localhost`. The command used `bench --site ccpc-integration2.localhost execute ccpcerp.patches.v1_0.add_intercompany_material_billing_indexes.execute` (not `bench migrate` or Patch Log change). Output:
```text
Isolated DEVELOPMENT database: VERIFIED
Executing approved index patch on ccpc-integration2.localhost only
Index patch command completed.
idx_icmb_scope: VERIFIED
idx_icmbi_source_parent: VERIFIED
BOTH INDEX DEFINITIONS VERIFIED
```
Independent parameterized `information_schema.STATISTICS` queries on the new site's own DB credentials confirmed the full ordered columns, NON_UNIQUE=1, BTREE index type, no prefix lengths for:
- `idx_icmb_scope` on `tabIntercompany Material Billing Batch` (`issuing_company`, `requesting_company`, `billing_month`)
- `idx_icmbi_source_parent` on `tabIntercompany Material Billing Item` (`stock_entry_detail`, `parent`)

**Status now: indexes are present and verified**; historical notes below that say 'missing' reflect earlier pre-correction observations, not the current state. Pre-change backup dated `20261013_102539` passed gzip/TAR/JSON archive checks; a restoration test was NOT performed. No evidence of changes to persistent `development.localhost` or PRODUCTION, and no general migration was invoked. **Not yet tested:** database integration, financial correctness, idempotency, rollback, concurrency, permissions and actual end-to-end transaction behavior. Proceed with a **read-only** test-fixture readiness check, then separately authorize synthetic test data/transactions (isolation, clean rollback/cleanup strategy, and snapshots) before writes. Do not assume production readiness.

## Isolated DEVELOPMENT pre-index backup archive integrity verified — 2026-10-13

Operator ran read-only archive/config checks on the four full-site backup files under `sites/ccpc-integration2.localhost/private/backups/`, prefix `20261013_102539-ccpc-integration2_localhost`. Reported:
```text
Database gzip integrity: PASSED
Public files archive: PASSED
Private files archive: PASSED
Site configuration JSON: PASSED
BACKUP ARCHIVE CHECKS: PASSED
```
Site config JSON was parsed without displaying secrets. Four nonempty files and basic archive integrity have been verified, **but no restoration test** has been performed. Both requested non-unique composite billing indexes are still absent. Next gate is **distinct user approval** for index DDL on this isolated site only, after backups and checks, using reviewed code and postconditions. DDL has implicit commit/metadata-lock risks. No broad migration, patch-log edit, persistent DEVELOPMENT modification, or PRODUCTION action.

## Isolated DEVELOPMENT full-site backup completed — 2026-10-13

Operator reported successful **site-scoped** `bench --site ccpc-integration2.localhost backup --with-files --ignore-backup-conf --backup-path ...` run at server timestamp `2026-10-13 10:25:40` in the DEVELOPMENT Frappe container, exit success, followed by a four-file non-empty verification printed `BACKUP FILE VERIFICATION: PASSED`. Artifacts under `/workspace/development/frappe-bench/sites/ccpc-integration2.localhost/private/backups/`:

- `20261013_102539-ccpc-integration2_localhost-database.sql.gz` — 899266 bytes
- `20261013_102539-ccpc-integration2_localhost-files.tar` — 10240 bytes
- `20261013_102539-ccpc-integration2_localhost-private-files.tar` — 10240 bytes
- `20261013_102539-ccpc-integration2_localhost-site_config_backup.json` — 212 bytes

Preflight stopped if site config missing, backup path symlink, custom backup destination, existing files in backup directory, or low host free space; `umask 077`, directory permissions `700`, and backup output verified four nonempty artifacts. Backup is **not yet archive-integrity-tested or restore-tested**. The site config backup includes secrets; never copy backup files, database contents, or config JSON to GitHub. Next: read-only integrity verification `gzip -t`, `tar -tf`, JSON parse without printing sensitive content. After that, obtain distinct explicit authorization before any DDL to create two known missing composite indexes exclusively on the isolated site. No `bench migrate`, patch-log edit, existing `development.localhost` changes or PRODUCTION operations authorized.

## Isolated DEVELOPMENT billing index column preflight verified — 2026-10-13

Operator read-only `information_schema.COLUMNS` query against `ccpc-integration2.localhost` confirmed all five requested index columns: `tabIntercompany Material Billing Batch` has `issuing_company varchar(140)`, `requesting_company varchar(140)`, and `billing_month date`; `tabIntercompany Material Billing Item` has `stock_entry_detail varchar(140)` and `parent varchar(140)`. Earlier check established both tables exist, neither requested named index exists, and no equivalent matching non-unique BTREE composite index is present. This satisfies basic column-presence/type preflight; it does not mean indexes have been created or tested under concurrency.

**Next controlled step:** obtain separate authorization and complete a verified backup of only the isolated site (including database/configuration and files), preserving the output securely; then request explicit approval for DDL creating the two narrowly scoped indexes. Any index creation should use the reviewed CCPC patch logic and verify `information_schema.STATISTICS` postconditions. Do not edit `tabPatch Log`, broadly `bench migrate`, touch persistent `development.localhost`, or operate on PRODUCTION. Fresh install may have pre-marked patch as complete.

## Isolated DEVELOPMENT equivalent-index inspection — 2026-10-13

The operator ran a read-only metadata query using MySQLdb on `ccpc-integration2.localhost`. The **only reported secondary indexes** are `creation` on `tabIntercompany Material Billing Batch` and `parent` on `tabIntercompany Material Billing Item`; **no equivalent composite indexes** for either CCPC-defined target were found. Missing named targets `idx_icmb_scope` and `idx_icmbi_source_parent` were separately confirmed earlier. Both tables exist. This is an expected possible fresh-install discrepancy because Frappe v16 `install_app(..., set_as_patched=True)` marks historical patches as completed by inserting Patch Log rows, not calling their `execute()` functions. No conclusion of DB corruption or confirmed runtime error should be made.

GitHub review branch `review/intercompany-approval-failure-tests` still points to `806fa23516490ec7beefcff03a1baa09d722120e`. Its index patch defines two NON-UNIQUE BTREE composite indexes, checks for equivalent/conflicting definitions, and creates indexes using `frappe.db.add_index`; it does not provide database-level uniqueness. No index DDL or patch re-execution has been approved or performed yet. **Next:** read-only check target columns' availability/types and table sizes, then independently approved backup and isolated-site-only index creation with exact schema/postcondition checks; no broad `bench migrate`, no Patch Log editing, no PRODUCTION actions.

## Isolated DEVELOPMENT billing tables confirmed; new-install patch-log semantics reviewed — 2026-10-13

Operator read-only MySQLdb `information_schema.TABLES` checks against `ccpc-integration2.localhost` reported **both** `tabIntercompany Material Billing Batch: PRESENT` and `tabIntercompany Material Billing Item: PRESENT`. Earlier checks found `idx_icmb_scope` and `idx_icmbi_source_parent` absent but the named index patch logged in `tabPatch Log`.

**New source finding:** In GitHub Frappe `version-16` `frappe/installer.py`, `install_app(name, ..., set_as_patched=True)` defaults to marking app patches completed; `set_all_patches_as_completed(app)` inserts Patch Log entries without invoking the patch `execute()`. `frappe/commands/site.py` routes `bench install-app` through that installer. This behavior **plausibly explains** a patch logged on fresh install while two custom indexes remain absent; installed Frappe 16.33.1's exact local source for this function has not yet been read to confirm identical behavior. Avoid describing these logged patches as successfully executed or declaring database corruption.

**Next safe operator action:** read-only inspect `information_schema.STATISTICS` of the two new-site tables for equivalent composite non-unique BTREE indexes under different names, then decide separately whether a backed-up, explicitly approved site-scoped index patch is warranted. No `bench migrate`, patch-log edits, DDL, financial test transactions, or PRODUCTION changes were performed.

## DEVELOPMENT billing index patch inconsistency — 2026-10-13

Operator's read-only MySQLdb queries against **only** `ccpc-integration2.localhost` showed `idx_icmb_scope: MISSING` and `idx_icmbi_source_parent: MISSING`, while a subsequent parameterized query showed `Patch Log table: PRESENT` and `Index patch recorded as executed: True` for `ccpcerp.patches.v1_0.add_intercompany_material_billing_indexes`. The query does not yet prove why patch log and index state differ. Do not treat patch-log presence as evidence that DDL ran, especially on a newly installed site. No migration, patch re-execution, or table/index mutation authorized. Previous standalone `frappe.init` attempt failed due to incorrect sites path, followed by logging path failure; neither reached index query. Direct MySQLdb checks are read-only and succeeded.

**Next:** verify the billing tables actually exist and inspect matching/equivalent index metadata read-only; review installer patch-marking semantics before any site-scoped migration or DDL. Keep DEVELOPMENT persistent site and PRODUCTION untouched.

## Isolated DEVELOPMENT full application registration verified — 2026-10-13

Operator executed read-only `bench --site ccpc-integration2.localhost list-apps` following the successful site and app installation. Output:
```text
frappe  16.33.1 version-16
erpnext 16.34.2 version-16
ccpcerp 0.0.1   review/intercompany-approval-failure-tests
```
All three applications are registered on the isolated site. This does **not** prove the intercompany billing schema indexes/patches, hooks, transaction integrity, permissions, or concurrent operations function correctly. No data-changing integration tests or PRODUCTION actions performed. Next step is read-only checks of applicable index and patch state, then plan synthetic tests with explicit approval and preserved backups.

## Isolated DEVELOPMENT CCPC app installation completed — 2026-10-13

Operator reported `bench --site ccpc-integration2.localhost install-app ccpcerp` completed with `Updating DocTypes for ccpcerp: 100%` and `CCPC installation exit code: 0`. Previous terminal verification established the new site's separate functioning MariaDB schema, Frappe 16.33.1 and ERPNext 16.34.2 installed. Prior to installation, DEVELOPMENT custom-app checkout was `review/intercompany-approval-failure-tests` at `806fa23` with untracked `AGENTS.md` deliberately preserved; the guarded installation command checked the exact full commit `806fa23516490ec7beefcff03a1baa09d722120e` and would stop if mismatched. Installer success is operator-provided output; post-install `list-apps`, schema/migration status, live hooks and integration tests have **not** yet been verified. No financial workflow tests or PRODUCTION operations reported.

**Next safe step:** read-only `bench --site ccpc-integration2.localhost list-apps` and basic installed-app check; then plan isolated, synthetic DEVELOPMENT database tests, migration/index review and backups separately. Do not run real billing transactions, cleanup, `bench migrate`, or PRODUCTION changes without specific approval.

## Isolated DEVELOPMENT integration site created and database verified — 2026-10-13

Operator ran guarded non-interactive `bench new-site ccpc-integration2.localhost --db-root-username=root --db-host=mariadb --db-type=mariadb` in `frappe_docker_devcontainer-frappe-1`, using `pexpect` and an existing verified DEV MariaDB root credential conveyed through an in-memory Docker pipe (not printed). A separate site Administrator password was entered privately. Reported `Installer exit status: 0`, `Installer signal status: None`. Next, a read-only Python/MySQLdb check reported: `New site configuration: PRESENT`, `Separate database name: True`, `New site database connection: SUCCESS`, `Database contains tables: True`. These establish successful Frappe site/database creation. ERPNext and CCPC application installation on the new site **remain unverified/not reported**.

The original failed `ccpc-integration.localhost` directory remains preserved; its configured DB/user were verified absent earlier. Persistent `development.localhost` was not intentionally targeted; no PRODUCTION operation was authorized. The new site is logically database-separated on shared DEV host, not physically isolated. **Next safe action:** read-only inspect installed apps for `ccpc-integration2.localhost`, confirm installed bench apps and current custom-app review branch before a separately staged `bench --site ccpc-integration2.localhost install-app erpnext` followed by CCPC app. No financial test transactions, migrations on existing DEV site, forced cleanup, or PRODUCTION actions.

## DEVELOPMENT partial integration-site database and user confirmed absent — 2026-10-13

**Operator terminal evidence:** Following a successful DEV MariaDB local-root authentication using the container's configured `MYSQL_ROOT_PASSWORD` and a successful read-only `SHOW DATABASES`, the operator ran a piped Python/SQL query. The Frappe container read `db_name` and `db_user` from the partial `ccpc-integration.localhost/site_config.json` without printing the identifiers, and the separate **DEVELOPMENT** MariaDB container queried `information_schema.SCHEMATA` and `mysql.user`. Actual reported results:

```text
Partial database exists: False
Partial database user exists: False
```

These checks establish absence of the **configured identifiers** in the DEV MariaDB server at the time of the query; they do not prove there are no unrelated orphan objects. The prior TCP root authentication failure (1045) did not prevent local socket authentication with the configured container root password. The partial site directory remains on disk. No database write, user creation, site deletion, restart, retry, or PRODUCTION operation occurred.

**Next safe decision:** Preserve the partial directory while planning controlled new-site recovery. Do not run `bench new-site --force`, remove files, or overwrite the existing DEVELOPMENT site. Consider choosing a *new, unique* test-site name and new DB identifiers rather than deleting the partial site, after a read-only collision check. Any actual new-site command requires a reviewed, prompt-safe credential procedure; ensure the administrator secret used is accepted from the DEV Frappe network, not merely through the local MariaDB socket. No financial integration tests or PRODUCTION changes authorized.

## DEVELOPMENT MariaDB root login from Frappe container rejected — 2026-10-13

**Operator-reported read-only authentication test:** The operator executed the approved interactive Python `MySQLdb.connect(host="mariadb", user="root", passwd=getpass.getpass(...))` from the **DEVELOPMENT Frappe** container. It returned `Database connection failed. Error code: 1045` (MariaDB access denied), before either `information_schema.SCHEMATA` or `mysql.user` SELECT could run. **Partial test database/user existence remains unverified**. The root password was not shown in the terminal transcript and must not be requested, printed, logged or committed. A 1045 can reflect wrong credentials **or** a root-account host/login restriction, so do not assume the operator entered the wrong secret.

**Next one read-only diagnostic:** On the Ubuntu host, check if the **DEVELOPMENT MariaDB container's local Unix socket** permits OS root to connect as MariaDB root without supplying or printing a password. Use only `frappe_docker_devcontainer-mariadb-1` and a harmless `SELECT 1`, suppressing any auth/error details:

```bash
docker exec --user root frappe_docker_devcontainer-mariadb-1 sh -lc '
if mariadb --protocol=socket --user=root --batch --skip-column-names --execute="SELECT 1" >/dev/null 2>&1; then
  echo "DEV MariaDB local socket root login: available"
else
  echo "DEV MariaDB local socket root login: unavailable"
fi
'
```

This does not modify databases or use production containers; if unavailable, stop and verify the **DEV-only** MariaDB administrator credential source and host-access policy through sanitized inspection, never dumping env vars/secret contents. No new-site retry, `--force`, deletion, password reset, rollback, migrations or real financial integration tests approved. Partial `ccpc-integration.localhost` site directory and config remain present, distinct configured DB name/user from `development.localhost`; no successful MariaDB object creation verified. Earlier approved DEV four-part backup format checked, not restore-tested. If the mistakenly entered superuser name was a real password, treat as exposed and plan controlled rotation after proper credential ownership identification, without repeating it.

## DEVELOPMENT partial site DB identifiers checked without disclosure — 2026-10-13

**Operator-provided read-only results:** Within the DEVELOPMENT Frappe container, read (but did **not** print) `db_name` and `db_user` fields in the partial `sites/ccpc-integration.localhost/site_config.json`; compared its database name to persistent `development.localhost`. Results:

```text
1. Partial site has DB name: True
2. Different from existing DEVELOPMENT DB: True
3. Partial site has DB user: True
```

The partial site has its own *configured* DB name/user, distinct from the persistent site's DB name; **none of these booleans proves that a database or user was actually created**. The original creation failed on MariaDB authentication during Frappe's `create_user -> get_current_host`, before the ordinary database-creation step, making absence plausible but not yet independently verified. Neither partial files nor existing site data were deleted or modified by this check; PRODUCTION untouched.

**Next read-only preflight proposal:** Query **only** the DEVELOPMENT MariaDB service `mariadb` via an interactive Python helper in `frappe_docker_devcontainer-frappe-1`, reading partial config names privately, prompting with `getpass` for MariaDB DEV root password (never in command/history/chat), and querying `information_schema.SCHEMATA` for the partial DB's existence without printing any schema names. If authenticated, optionally query `mysql.user` for the partial DB user's existence; both are SELECT only. Stop on auth error; no password logging, privilege changes, forced site recreation, rollback, or cleanup. This will enable a separately authorized safe partial-site recovery plan. If earlier user-entered SQL-username value was a real password, treat as disclosed and plan rotation separately, not in GitHub.

## DEVELOPMENT partial integration-site directory observed — 2026-10-13

**Operator-reported results after failed approved site creation:** The terminal returned `Aborted!` and prompt `gani@ccpcerpserver` after declining Frappe's rollback, then a read-only `find` of `sites/ccpc-integration.localhost` inside `frappe_docker_devcontainer-frappe-1` reported that the site path **exists** and contains **`logs`, `locks`, `private`, `site_config.json`, `public`**. Do not print/read that JSON raw because it can contain credentials; no secrets are reproduced in this handoff. Successful site creation, separate DB creation, or app installation **NOT verified**. Preserve any partial files; **no `rm`, rollback, `--force`, re-run of `new-site`, migrations, or PROD changes** are authorized at this moment.

**Source check:** Frappe version-16 GitHub `frappe/installer.py` first creates site directories and calls `make_conf` before `setup_database`. MariaDB `setup_database` calls `create_user` before `create_database`. The actual traceback occurred in `DbManager.create_user -> get_current_host -> self.db.sql("select user()")` at MySQL authentication. This strongly suggests **the database creation step was not reached**; it is nevertheless unsafe to assert there are no partial DB artifacts without an independent check.

**Next safe one-step read-only inspection** for operator on Ubuntu host: compare only whether `db_name` is configured for partial site and whether it matches the existing site, without printing names or passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
./env/bin/python -c "
import json
from pathlib import Path
root = Path(\"sites\")
old = json.loads((root / \"development.localhost\" / \"site_config.json\").read_text())
partial = json.loads((root / \"ccpc-integration.localhost\" / \"site_config.json\").read_text())
name = partial.get(\"db_name\")
print(\"Partial site has DB name:\", bool(name))
print(\"DB name differs from existing DEVELOPMENT:\", bool(name) and name != old.get(\"db_name\"))
print(\"Partial site has DB user:\", bool(partial.get(\"db_user\")))
"
'
```

Only boolean results are displayed. If the partial DB name unexpectedly matches the persistent site, STOP; if it differs, proceed with separately planned **read-only existence check** of MariaDB objects in the DEVELOPMENT DB service. Never include passwords in shell history/chat. Determine a safe, exact plan for either restoring a known empty test-site creation or renaming to a new unique test site; any partial artifact deletion needs specific review/authorization. If credential entered as DB username was a real secret, treat it as exposed and arrange safe rotation, preferably not during testing setup.

## DEVELOPMENT integration site creation halted on MariaDB authentication — 2026-10-13

**Operator-reported failed interactive setup** using the previously approved new-site command **only in DEVELOPMENT**: `docker exec -it --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '... bench new-site ccpc-integration.localhost --db-host mariadb --db-type mariadb'`. The Frappe CLI prompted `Enter mysql super user [root]:`. **A value other than `root` was entered at the username prompt**. **Do not copy that value here or into GitHub**, as it resembles a credential and was included in user-shared terminal output. Subsequent password prompt and trace reported `MySQLdb.OperationalError: (1045, "Access denied for user [REDACTED] from DEV-container network")`. Frappe then displayed the interactive prompt `Site creation failed, do you want to rollback the site? [y/N]:`.

**Immediate safety response:** Instruct operator to press **Enter** to choose the default **No**, avoiding automatic rollback/cleanup before inspecting possible partial site artifacts. Do **not** retry or run `--force`; do not assume the failed attempt left nothing. The normal MariaDB administrator username is `root`, with its password entered separately and privately. If the accidentally entered username was a real password, it is exposed in chat transcript and requires **carefully planned credential rotation**, without printing it again.

**Current status:** New site and its DB/app installation **NOT verified as successful**. No further database changes, site rollback, cleanup or real integration tests authorized pending operator report of prompt completion, read-only inspection of `sites/ccpc-integration.localhost` artifacts, and cautious handling of possible partial DB objects. The last successful preflight was an October 13 four-file DEV backup with format checks; `development.localhost` and all PRODUCTION data must be preserved. Approval to create a new DEV site did not grant approval to delete ambiguous partial artifacts or change production.

**Next operator step after returning to shell:** run a read-only presence check **within the DEV Frappe container**, showing only directory existence and filenames, not any site-config contents or passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
if [ -e sites/ccpc-integration.localhost ] || [ -L sites/ccpc-integration.localhost ]; then
  echo "Integration site path exists (partial setup possible)"
  find sites/ccpc-integration.localhost -maxdepth 1 -mindepth 1 -printf "%f\n"
else
  echo "Integration site path absent"
fi
'
```

Then review Frappe installer state/rollback semantics before issuing any recovery or repeat creation command. Site creation may have generated a configuration file containing secrets; never print it. **PRODUCTION untouched in reported operation.**

## Operator approved isolated DEVELOPMENT integration site setup — 2026-10-13

**Explicit operator approval:** User replied **"Approved"** after being asked: "Do you approve creating `ccpc-integration.localhost`, with its own new DEVELOPMENT database and Frappe, ERPNext, and CCPC applications?" This approval covers **test-site/database creation and installing these applications in the existing DEVELOPMENT bench only**. It **does not authorize** financial transaction tests, modifying the persistent `development.localhost`, a `bench migrate` on that existing site, deletion/cleanup of existing sites or data, Docker restarts, copying production records, or **any PRODUCTION changes**.

**Preflight verified in active conversation:** DEV Frappe DB configured host `mariadb`; alias belongs to `frappe_docker_devcontainer-mariadb-1` on network `frappe_docker_devcontainer_default`, whereas PROD DB `frappe_docker-db-1` is on `frappe_docker_default`. MariaDB volumes separate. Only persistent existing DEV site is `development.localhost`. Fresh four-part DEV backup from October 13 passed gzip/tar/JSON format checks but is not restore-proven. Application review branch tip `806fa23516490ec7beefcff03a1baa09d722120e`; 155/155 combined mocked unit tests passed on DEV. Live Frappe `bench new-site --help` confirmed `--db-host`, `--db-type`, `--install-app` and credential prompt options.

**Safe staged procedure:** From host run guarded creation in **DEVELOPMENT Frappe container** `frappe_docker_devcontainer-frappe-1` as `frappe` user, from `/workspace/development/frappe-bench`: check `sites/ccpc-integration.localhost` does not exist (including symlink); run `bench new-site ccpc-integration.localhost --db-host mariadb --db-type mariadb` **without** `--force`, `--db-name`, inline admin/root passwords, or `--install-app` (stage app installations separately). Frappe chooses a new database name and prompts for passwords. Operator should enter prompts privately and **not paste secrets in chat**. Inspect terminal output and successful site creation before installing ERPNext then CCPC into **the new test site only** with explicit `--site ccpc-integration.localhost`. Stop if database provisioning fails, Frappe mentions an existing site/database, or an unexpected environment appears.

**Status:** Approval granted; creation **not yet observed**. Only actual operator terminal output can confirm site/database creation. No real transaction tests authorized. This approach provides logical site/database isolation on shared DEV infrastructure, not physical isolation.

## DEVELOPMENT Frappe new-site CLI options inspected — 2026-10-13

**Operator-provided read-only CLI help output:** On the Ubuntu host the operator executed `bench new-site --help` inside `frappe_docker_devcontainer-frappe-1` at `/workspace/development/frappe-bench` and filtered the help for database/admin/install flags. Verified flags include `--db-name`, `--db-password`, `--db-type [mariadb|postgres|sqlite]` (MariaDB default), `--db-host`, `--db-port`, `--db-root-username` / `--mariadb-root-username`, `--db-root-password` / `--mariadb-root-password`, `--admin-password`, `--install-app`, `--setup-db / --no-setup-db`, `--db-user`, and `--force`. Do **not** use `--force` or pass secret/password arguments in shell commands or history.

**Proposed operation (explicit operator authorization still required):** Prepare dedicated test site `ccpc-integration.localhost` and a distinct new MariaDB schema/user on the **DEVELOPMENT** service `mariadb`, with Frappe/ERPNext/CCPC installed using currently reviewed app checkout `review/intercompany-approval-failure-tests` at last verified commit `806fa23`. Do not copy production or existing persistent DEV business data, do not change default bench site, and use synthetic fixtures for later integration testing. Site creation/app installation writes to the DEV database server and filesystem, can consume CPU/RAM/I/O on the physical host shared with production, and is **not approved by the earlier DEVELOPMENT backup-only authorization**. Explicitly check for site/database naming collisions and password-prompt behavior; avoid displaying/root credentials. Installing apps and executing any test-suite writes must be staged, observed and separately approved when necessary.

**Verified prerequisites:** Only `development.localhost` was enumerated in DEV bench; effective `db_host` was `mariadb`; the DEV Frappe/MariaDB containers share network `frappe_docker_devcontainer_default` with matching `mariadb` alias; PROD MariaDB is on `frappe_docker_default`. DEV/PROD named DB storage volumes are different. Fresh DEV four-part backup `20261013_083457-development_localhost` was created following explicit backup approval and passed nonempty, gzip, tar, JSON syntax checks (not restore-tested). 155/155 mocked unit tests passed together on app review branch `806fa23`. No site creation, data-altering tests or PRODUCTION changes yet.

**Next action:** Ask operator to explicitly approve or reject the creation and app installation of the proposed DEVELOPMENT-only test site/database. If approved, prepare a safe, prompt-driven, collision-checked command sequence **one step at a time**, avoiding plaintext credentials in CLI history; proceed to real transactional/concurrency test plan only after another risk review, backup and explicit approval.

## Live DEVELOPMENT/PRODUCTION Docker network boundaries verified — 2026-10-13

**Operator-provided Docker host read-only inspection** of network names and aliases (no environment variables or secrets):

```text
/frappe_docker_devcontainer-frappe-1
  network=frappe_docker_devcontainer_default aliases=[frappe_docker_devcontainer-frappe-1 frappe]
/frappe_docker_devcontainer-mariadb-1
  network=frappe_docker_devcontainer_default aliases=[frappe_docker_devcontainer-mariadb-1 mariadb]
/frappe_docker-db-1
  network=frappe_docker_default aliases=[frappe_docker-db-1 db]
```

**Confirmed:** The DEVELOPMENT Frappe container and its MariaDB share `frappe_docker_devcontainer_default`, with the MariaDB alias `mariadb` matching effective `development.localhost` DB host. The checked PRODUCTION MariaDB container is on separate `frappe_docker_default`, without an observed connection to the DEV network. Separate live MariaDB storage volumes were previously verified (`frappe_docker_devcontainer_mariadb-data` vs `frappe_docker_db-data`). This **does not guarantee full host-level, credential, or network segmentation**: Docker host/kernel/storage are shared and privileged processes can affect both stacks.

**Readiness:** Persistent `development.localhost` was the only configured site found in the DEV bench. Fresh, explicitly approved DEVELOPMENT four-part backup `20261013_083457-development_localhost` was completed and passed four-file nonzero, gzip, tar and JSON format checks; **no restore rehearsal** has occurred. Combined 155/155 mocked Python tests passed on application review branch `review/intercompany-approval-failure-tests` at `806fa23`. No real MariaDB invoice rollback, transaction, concurrency or schema integration test has run.

**Proposed test isolation plan — not approved/executed:** Create a distinctly named **DEVELOPMENT-only disposable test site** (e.g. `ccpc-integration.localhost`) with **its own new MariaDB database**, reusing only the DEVELOPMENT Frappe bench and MariaDB service. Do not copy persistent DEV or PRODUCTION business data, do not change bench default site or existing `development.localhost` DB, and do not perform migrations on the persistent site. Use synthetic fixtures. Review permissions, storage overhead, Frappe installation/bootstrap requirements, test runner behavior, cleanup, and restoration/recovery strategy. A site within the same DEV bench/database server is **logical isolation only**, not a separate physical server or dedicated MariaDB daemon; broader isolation would require a separate Docker project and DB volume. Request explicit owner approval for new-site/DB creation and separately review/approve any database-changing integration tests, with stop-on-error and no destructive cleanup.

**Next safe read-only step to verify command flags before a site creation proposal:** Run `bench new-site --help` **only** in the DEVELOPMENT container, filtering output for database and administrative options; do not provide or print passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
bench new-site --help | grep -Ei -- "db-|database|mariadb|admin|install" | head -n 35
'
```

After reviewing available options, propose the precise site-creation command and seek separate approval. Do not create site/DB now or touch PRODUCTION.

## Read-only DEVELOPMENT effective database endpoint — 2026-10-13

**Operator-provided output** from a read-only merge of `sites/common_site_config.json` with `sites/development.localhost/site_config.json` inside `frappe_docker_devcontainer-frappe-1`. Command printed ONLY endpoint metadata, no config secrets:

```text
DEVELOPMENT DB host: mariadb
DEVELOPMENT DB port: [default]
```

This is consistent with Docker DNS/service-name lookup to a MariaDB service on the DEVELOPMENT container's network. The default MariaDB/MySQL TCP port is generally 3306, but that was **not explicitly configured** in the files checked. **Database network identity/isolation has not yet been independently confirmed** by live Docker networking inspection. Previously verified DEV and PROD containers have separate named MariaDB data volumes; they still share the Ubuntu host and Docker daemon. Persistent DEV `development.localhost` is the only configured site found, and its fresh Oct 13 backup passed nonempty/gzip/tar/JSON format checks but has not been restore-tested. 155/155 mock tests passed together on review commit `806fa23`.

**Next one-step read-only operator action:** On Ubuntu host, inspect just network names/aliases for the DEVELOPMENT Frappe app container, DEVELOPMENT MariaDB and PRODUCTION MariaDB, **without opening environment variables, site configs or credentials**:

```bash
docker inspect --format '{{.Name}}{{range $name, $net := .NetworkSettings.Networks}}{{printf "\n  network=%s aliases=%v" $name $net.Aliases}}{{end}}' \
  frappe_docker_devcontainer-frappe-1 \
  frappe_docker_devcontainer-mariadb-1 \
  frappe_docker-db-1
```

Confirm DEV Frappe and DEV MariaDB share the relevant network and `mariadb` alias, while PROD MariaDB is on a separate network. Distinct networks and volumes lower risk but are **not complete protection** against host-level effects or privileged access. Do **not** yet create a new site/database, run database-changing integration tests, migrate, restore or touch production. An isolated site-and-database test plan requires explicit approval after further review.

## DEVELOPMENT site inventory — only persistent site exists (2026-10-13)

**Operator-provided read-only output:** A command in `frappe_docker_devcontainer-frappe-1` enumerated site directories containing `site_config.json` in `/workspace/development/frappe-bench/sites`. Its **only result** was:

```text
development.localhost/
```

This confirms there is **no preexisting second Frappe site in this DEVELOPMENT bench** based on the on-disk site directory check. `development.localhost` contains persistent DEV data and **must not be regarded as disposable**. To validate actual MariaDB invoice rollback and concurrency safely, first design a dedicated **new isolated integration-test site and distinct DEV test database**, review connectivity, fixtures and cleanup/rollback procedures, and request explicit user approval before creating any site/database or running tests. Do not use production databases or copies of production data. The fresh four-part October 13 DEV backup successfully passed gzip/tar/JSON syntax checks but is not restore-proven.

**Next one-step read-only preflight:** Review the **effective DEVELOPMENT site DB host/port only**, merging common and site JSON configuration, without printing database name, passwords or other configuration. Execute on the Ubuntu host:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
./env/bin/python -c "
import json
from pathlib import Path
base = Path(\"sites\")
common = json.loads((base / \"common_site_config.json\").read_text())
site = json.loads((base / \"development.localhost\" / \"site_config.json\").read_text())
effective = {**common, **site}
print(\"DEVELOPMENT DB host:\", effective.get(\"db_host\", \"[not set]\"))
print(\"DEVELOPMENT DB port:\", effective.get(\"db_port\", \"[default]\"))
"
'
```

A successful result identifies the configured endpoint only, **not guaranteed isolation**; separately check the Docker networks before site creation. This operation reads two DEV JSON files and prints only non-secret endpoint metadata. No DB or PROD modifications authorized. App review branch remains at verified commit `806fa23516490ec7beefcff03a1baa09d722120e` with 155 combined mocked unit tests passing.

## Fresh DEVELOPMENT backup files verified — 2026-10-13

**Operator-reported validation run** from the Ubuntu host against the approved October 13 **DEVELOPMENT-only** site backup `20261013_083457-development_localhost`, via `docker exec --user frappe frappe_docker_devcontainer-frappe-1`. The shell command checked that each of four expected files is nonempty, then ran `gzip -t` on `-database.sql.gz`, `tar -tf` on **uncompressed** `-files.tar` and `-private-files.tar`, and `python -m json.tool` on `-site_config_backup.json`; it did not print secrets or extract files. The observed output was:

```text
DEVELOPMENT fresh backup format checks: PASS
```

**Verified scope:** existence/nonzero size, gzip integrity, tar archive readability, JSON syntax for all four artifacts in the fresh DEV backup set. This does **not** prove a valid full SQL restoration, database transactional consistency, off-host availability or recovery viability. The backup is on the shared physical server. No PRODUCTION change, migrations, Docker recreation, or database-changing integration tests were executed.

**Current milestone:** Application review branch `review/intercompany-approval-failure-tests`, commit `806fa23`, previously passed **155/155 mocked Python unit tests in one combined run**. DEV and PROD MariaDB volumes were independently distinguished by read-only live Docker inspect. Before any **real** Frappe/MariaDB transactional/concurrency tests, plan and authorize a **separate test site/database** and independent fixtures/rollback; do not run `bench run-tests` directly against persistent `development.localhost` or use production business data.

**Next low-risk read-only operator step:** Enumerate the existing site directories in the DEVELOPMENT bench **without reading site config contents**, so a unique isolation plan can be designed without colliding with existing sites:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit
for d in sites/*/; do
  [ -f "${d}site_config.json" ] && printf "%s\n" "${d#sites/}"
done
'
```

The results list site names only (no database passwords). Decide whether any site is available for isolated testing from explicit ownership/usage evidence; **do not assume a site is disposable**. Then document/review the new test site's database connection, backups, fixtures, migration and rollback procedure and request explicit operator approval before creating or modifying anything.

## Approved fresh DEVELOPMENT backup completed — 2026-10-13

**Explicit operator approval** was obtained in chat to create a fresh backup **only** for the persistent DEVELOPMENT Frappe site `development.localhost`. The operator ran on Ubuntu:

```bash
docker exec -it --user frappe \
  frappe_docker_devcontainer-frappe-1 \
  bash -lc 'cd /workspace/development/frappe-bench && bench --site development.localhost backup --with-files'
```

**Operator-provided successful output**, reporting backup summary at `2026-10-13 08:34:58.481811` and final `Backup for Site development.localhost has been successfully completed with files`:

- `sites/development.localhost/private/backups/20261013_083457-development_localhost-site_config_backup.json` — **234 B**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-database.sql.gz` — **1.6 MiB**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-files.tar` — **10.0 KiB**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-private-files.tar` — **20.0 KiB**

Unlike the October 9 `.tgz` file archives, this fresh October 13 backup has **uncompressed `.tar` public/private file archives**; therefore validate with `tar -tf` (no gzip flag). **Actual existence, compression/readability, complete database contents, and restore usability have not yet been independently verified after the completed backup command**. Backup is in local DEV site backup directory on host-shared storage, not demonstrated off-host. No database-changing tests, migrations, restore operations, or PROD actions were requested or reported.

**Next one safe, read-only operator action** on the Ubuntu host: validate all four new DEV backup artifacts inside the DEVELOPMENT Frappe container, checking nonzero files, gzip CRC, tar listings and config JSON syntax without printing config:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit
B=sites/development.localhost/private/backups/20261013_083457-development_localhost
for suffix in database.sql.gz files.tar private-files.tar site_config_backup.json; do
  test -s "${B}-${suffix}" || exit 1
done
gzip -t "${B}-database.sql.gz" &&
tar -tf "${B}-files.tar" >/dev/null &&
tar -tf "${B}-private-files.tar" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEVELOPMENT fresh backup format checks: PASS"
'
```

Even when these checks pass, do **not** represent them as a tested restore or database transaction-consistency verification. Before real concurrent billing approval/rollback experiments, review isolated test data and recovery/isolation plan, confirm that backup can be restored to an isolated environment, and obtain separate explicit operator approval. The last verified application review branch tip was `806fa23516490ec7beefcff03a1baa09d722120e`, with 155/155 combined mocked Python unit tests passing in DEVELOPMENT.

## DEVELOPMENT backup-destination capacity preflight — 2026-10-13

**Operator-reported read-only Docker container filesystem check** on Ubuntu host:

```bash
docker exec frappe_docker_devcontainer-frappe-1 \
  bash -lc 'df -h /workspace/development/frappe-bench/sites && df -i /workspace/development/frappe-bench/sites'
```

Result for filesystem `/dev/nvme0n1p2` mounted at `/workspace`: **915G total, 182G used, 687G available, 21% utilization**. Inodes: **60,981,248 total; 7,574,738 used; 53,406,510 free; 13% usage**. Capacity is ample relative to the known October 9 DEV archive sizes, but this is host-shared storage and free space alone does not prove successful backup or guarantee no host resource contention.

**Backup readiness checkpoint:** Site `development.localhost` listed Frappe 16.33.1, ERPNext 16.34.2 and CCPC 0.0.1; 155 combined isolated Python mock tests passed; DEV and PROD use separate named MariaDB Docker volumes; Oct 9 four-part DEV backup archives passed gzip/tar/JSON syntax checks but were not restore-tested and are four days old. Live DEV backup freshness, successful restoration, DB transactional/concurrency correctness and independent off-host recovery remain **unverified**.

**Next operator decision (do not execute without approval):** Obtain explicit agreement to create a **new DEVELOPMENT-only four-part site backup** from within `frappe_docker_devcontainer-frappe-1`, bench directory `/workspace/development/frappe-bench`, targeting **only** `development.localhost` using `bench --site development.localhost backup --with-files`. This reads the DEV database and writes new backup artifacts to the DEV site's local backups directory; it may consume shared host disk and I/O but does not intentionally mutate business records. Do not use `--site ccpcerp.local` or any production container. After approval, run safely and verify four new matching-prefix files, syntax and integrity, and consider separate recovery or off-host strategy before database-changing tests. No `bench migrate`, `run-tests`, ERPNext transactions, database restore or PRODUCTION operations authorized.

## Verified distinct live DEV and PROD MariaDB storage volumes — 2026-10-13

**Operator-provided read-only host Docker inspection:** On `gani@ccpcerpserver`, inspecting the `/var/lib/mysql` mounts for both running database containers returned:

```text
/frappe_docker_devcontainer-mariadb-1: volume frappe_docker_devcontainer_mariadb-data /var/lib/docker/volumes/frappe_docker_devcontainer_mariadb-data/_data -> /var/lib/mysql
/frappe_docker-db-1: volume frappe_docker_db-data /var/lib/docker/volumes/frappe_docker_db-data/_data -> /var/lib/mysql
```

**Conclusion:** Verified **separate named Docker volumes and separate host source paths** for DEV and PROD MariaDB data directories, matching the intended Compose project separation. This establishes database *storage directory* separation, **not independent physical servers**, full network/credential segregation, database/schema completeness or restore viability. The environments share the physical Ubuntu host and Docker daemon; direct Docker privileges can affect both. No production mutation occurred from this read-only inspect.

**Safety status:** 155/155 mocked Python tests passed in one combined DEVELOPMENT run at app review commit `806fa23`. The October 9 four-part DEV backup passed gzip/tar/JSON syntax checks but is stale for Oct 13 and has not been restored. Actual MariaDB rollback/durability, locking/concurrency, Frappe integration and indexed schema tests remain pending; no migrations or database-changing tests approved.

**Next safe operator action:** Check the filesystem's available space/inodes for the *DEV site backup destination only*, from the Ubuntu host without opening credentials or touching production:

```bash
docker exec frappe_docker_devcontainer-frappe-1 bash -lc 'df -h /workspace/development/frappe-bench/sites && df -i /workspace/development/frappe-bench/sites'
```

Use the output to plan a new complete `development.localhost` backup and eventual separated restoration rehearsal/rollback review. Do **not** execute a fresh backup, database-integrated test, `bench migrate`, restore, or prod action until its precise scope/safety plan is agreed with the operator.

## Live DEVELOPMENT and PRODUCTION database container discovery — 2026-10-13

**Operator-provided read-only Docker host output** from `gani@ccpcerpserver`:

```text
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -Ei 'NAMES|mariadb|db-'
NAMES                                      STATUS
frappe_docker_devcontainer-mariadb-1       Up 23 hours
frappe_docker-db-1                         Up 24 hours (healthy)
```

Confirms two **distinct running MariaDB containers**, first under the DEVELOPMENT Compose project and second under the PRODUCTION project. **It does not yet establish separate Docker database volume mounts or independent physical storage**; both share the Ubuntu host and Docker daemon. Do not infer "healthy" status for DEV, as its output only says Up.

**Next one-step read-only Docker mount verification** to run on the Ubuntu **host**, with no environment/config secrets printed:

```bash
docker inspect --format '{{.Name}}:{{range .Mounts}}{{if eq .Destination "/var/lib/mysql"}} {{.Type}} {{.Name}} {{.Source}} -> {{.Destination}}{{end}}{{end}}' \
  frappe_docker_devcontainer-mariadb-1 \
  frappe_docker-db-1
```

Compare DEV vs PROD mounts. No DB integration tests, fresh backup, schema changes, restore or PRODUCTION actions have been authorized. October 9 DEV four-file archive validation passed only compression/JSON syntax checks, not restore. The 155 combined mocked unit tests passed on app review commit `806fa23`.

## DEVELOPMENT Oct 9 backup archive syntax verification — 2026-10-13

**Operator-provided terminal output:** From `/workspace/development/frappe-bench` inside DEVELOPMENT, the operator ran read-only validation against the four `sites/development.localhost/private/backups/20261009_061614-development_localhost-*` backup artifacts:

```bash
B=sites/development.localhost/private/backups/20261009_061614-development_localhost
gzip -t "${B}-database.sql.gz" &&
tar -tzf "${B}-private-files.tgz" >/dev/null &&
tar -tzf "${B}-files.tgz" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEV backup files: compression and JSON syntax checks passed"
```

Actual reported output: **`DEV backup files: compression and JSON syntax checks passed`**. This establishes that all four listed files have readable compression/archive syntax or valid JSON structure; it **does NOT** verify SQL consistency/completeness, archive contents against the Frappe site, restoration, or current-day data coverage. These are October 9 artifacts being checked on October 13. No files extracted; no DB connection or write; no PRODUCTION action.

**Next safe operator action, one step at a time:** On the **Ubuntu Docker host** (exit the DEV container shell first), run the following **read-only** database-container discovery, without printing credentials/config:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -Ei 'NAMES|mariadb|db-'
```

Review the returned live DB container names, then use a separately designed **read-only** Docker mount inspection to confirm DEV and PRODUCTION database data mounts/volumes are distinct, without printing secrets. They are separate Compose projects but share host and Docker daemon. Only after verifying boundaries, backup freshness and recovery plans should the operator be asked to authorize a fresh DEVELOPMENT backup and database-integrated transaction tests. Do not run `bench run-tests` or `bench migrate` or backup restore now.

## Read-only DEVELOPMENT backup inventory — 2026-10-13

**Operator-provided listing, not archive integrity or restore verification.** From the DEVELOPMENT container in `/workspace/development/frappe-bench`, listing `sites/development.localhost/private/backups` showed the following four file artifacts with filesystem mtime **2026-10-09 00:46**:

- `20261009_061614-development_localhost-database.sql.gz` — **1,646,365 bytes**
- `20261009_061614-development_localhost-private-files.tgz` — **9,599 bytes**
- `20261009_061614-development_localhost-site_config_backup.json` — **234 bytes**
- `20261009_061614-development_localhost-files.tgz` — **141 bytes**

The file-name timestamp and mtime display differ; do not assume the time zone without checking. There is one four-part matching-prefix backup set in the 20-entry output. Presence of files **does not establish gzip/tar integrity, DB completeness, database origin, restore usability or recovery time**. On 2026-10-13 this backup is roughly four days old and may not contain recent DEVELOPMENT changes. Never expose site-config JSON contents; it can contain passwords and other sensitive values. Do not use production backups for DEV integration tests.

**Next one-step operator preflight (read-only, no extraction or DB access):** Validate archive compression and site_config JSON structure without printing contents, from the DEVELOPMENT bench:

```bash
cd /workspace/development/frappe-bench
B=sites/development.localhost/private/backups/20261009_061614-development_localhost
gzip -t "${B}-database.sql.gz" &&
tar -tzf "${B}-private-files.tgz" >/dev/null &&
tar -tzf "${B}-files.tgz" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEV backup files: compression and JSON syntax checks passed"
```

This checks readable archive structure only, **not** restored database correctness or recovery viability. Subsequently verify DEV/PROD database boundaries and free space; require a new, complete DEV backup and explicit authorization/safe rollback plan before any database-changing integration tests. Preserve DEV persistent state and all production services; no migration, restore, deletion or production access authorized.

## Read-only DEVELOPMENT site installed-app preflight — 2026-10-13

**Operator-provided DEVELOPMENT terminal output:** At `/workspace/development/frappe-bench`, the operator ran `bench --site development.localhost list-apps`; it completed successfully and reported:

```text
frappe  16.33.1 version-16
erpnext 16.34.2 version-16
ccpcerp 0.0.1   feature/intercompany-material-billing
```

This verifies that the named DEVELOPMENT site can provide its installed-application listing, supporting (but not independently proving) site/DB availability. The `ccpcerp` branch field in `list-apps` is app/version metadata and **must not be treated as the active Git branch**; the operator separately confirmed the DEVELOPMENT Git checkout on `review/intercompany-approval-failure-tests`, commit `806fa23`, and the connected GitHub branch was independently confirmed at `806fa23516490ec7beefcff03a1baa09d722120e`.

**Still unverified:** DEV backup freshness/completeness, DEV MariaDB identity/independence, schema/indexes, controlled rollback safety and MariaDB concurrency. DEV site has persistent data; no `bench run-tests`, `bench migrate`, invoice creation, backup restore, or schema changes have been approved. PRODUCTION untouched.

**Next one-step read-only preflight:** From DEVELOPMENT container's `/workspace/development/frappe-bench`, list filenames/timestamps/sizes of DEV site backups if directory exists; do not expose site config contents or passwords:

```bash
cd /workspace/development/frappe-bench
if [ -d sites/development.localhost/private/backups ]; then
  find sites/development.localhost/private/backups -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM  %12s bytes  %f\n' | sort -r | head -n 20
else
  echo 'DEVELOPMENT site backups directory not found at standard path'
fi
```

A directory listing or backup filename alone does not prove a valid/completed/restorable backup. Evaluate freshness, backup artifact sets and separate production boundaries before seeking authorization for persistent-DEV integration tests.

## Combined 155/155 DEVELOPMENT unit tests passed — 2026-10-13

**Operator-provided DEVELOPMENT terminal transcript** (not a CI run or connector-executed command): after prior verified DEV fast-forward to app review branch `review/intercompany-approval-failure-tests`, commit `806fa23`, ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest -q \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes
```

**Observed result: `Ran 155 tests in 0.379s`; `OK`.** All four mocked modules passed *together* in one Python interpreter, providing evidence their test setup and cleanup coexist and removing the earlier need to rely solely on separate runs. GitHub connector independently verified app branch tip `806fa23516490ec7beefcff03a1baa09d722120e`. No new application code change, DB migration, Docker restart or PRODUCTION modification occurred during this milestone.

**Remaining validation:** No actual Frappe/MariaDB multi-connection concurrency, invoice rollback/durability, installed index/schema, workflow hook integration or recovery test has been performed in this testing sequence. DEV site `development.localhost` is **persistent**, and DEV/PRODUCTION share host and Docker daemon even though their Compose projects/DB volumes are distinct. Do not execute `bench --site development.localhost run-tests`, `bench migrate`, invoice creation, schema changes, or any database-changing integration test until DEV backup/isolation and rollback plan are explicitly reviewed and operator-approved; never touch production.

**Next safe one-step preflight:** from the DEVELOPMENT container at `/workspace/development/frappe-bench`, run **read-only** `bench --site development.localhost list-apps`. This checks whether the Frappe site can connect to its site database and reports installed apps/versions without exposing credentials or performing planned writes. Collect output, then separately verify DEV database identity, backup availability and isolated test strategy without exposing secrets. Current known untracked `AGENTS.md` must remain excluded.

## DEVELOPMENT index patch mocks passed — 2026-10-13

**Operator-reported DEVELOPMENT test output:** At the DEVELOPMENT bench after the previously verified safe fast-forward to review branch `review/intercompany-approval-failure-tests`, commit **`806fa23`**, the operator ran:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes \
  -q
```

Terminal result: **`Ran 8 tests in 0.004s` — `OK`**. The patch's logic was exercised with mocked database access; **no actual index creation or migration has been run or proven**. Cumulative separate test-run reports now total **155 passing mocked test executions**: 124 core billing batch, 4 approval failure paths, 19 deletion protection, and 8 index-patch tests. This does not constitute a combined suite run, a CI result, actual MariaDB transaction-rollback/concurrency proof, schema verification, or a production-ready release. App review branch `806fa23516490ec7beefcff03a1baa09d722120e` independently checked through the GitHub connector.

**Recommended next safe operator action:** Run all four mocked test modules in **one standalone `unittest` invocation** at the current DEVELOPMENT commit to verify inter-test isolation, global `frappe.db` mock cleanup and reproducibility across the exact same revision, without database-integrated testing:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest -q \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes
```

Expected count based on separate runs: 155, but **combined execution not yet verified**. If clean, plan a separate read-only DEV site/backup/schema preflight before seeking authorization for any database-integrated tests. Preserve untracked `AGENTS.md`, DEV data and PROD; no migrations, restarts or destructive operations authorized.

## DEVELOPMENT deletion-protection mocked tests passed — 2026-10-13

**Operator-provided DEVELOPMENT terminal output:** With application checkout on `review/intercompany-approval-failure-tests` at **`806fa23`**, the operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  -q
```

Result: **`Ran 19 tests in 0.008s` — `OK`**, with no errors or failures. Together with separately reported 124 passing core Intercompany Billing mocked unit tests and 4 passing invoice failure-propagation mocked tests, **147 mocked test executions passed across three separate runs**. This is not a single combined run, nor evidence of real MariaDB rollback/concurrency behavior. The application review branch tip **`806fa23516490ec7beefcff03a1baa09d722120e`** was independently reverified via connected GitHub tools.

**Next safe action:** Run the existing index patch **mocked** unit tests from the DEVELOPMENT bench, without executing the actual patch or `bench migrate`:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes -q
```

The index mock suite in GitHub initializes/restores a mocked `frappe.db`; no further code change is planned unless tests fail. Keep untracked `AGENTS.md` excluded. Any future actual database tests, migrations, concurrent approval simulations or production release require separate safety review and authorization. **No PRODUCTION changes.**

## DEVELOPMENT mocked billing suite passed — 2026-10-13

**Operator-reported DEVELOPMENT test transcript:** After fast-forwarding `review/intercompany-approval-failure-tests` to **`f49e2e8`**, the operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  -q
```

Result **`Ran 124 tests in 0.345s` — `OK`** (no reported errors/failures). Previously the four mocked invoice failure-propagation tests on the same review line passed **`Ran 4 tests in 0.011s` — `OK`**. These are **128 passing mocked test executions across two independent commands**, not a combined all-suites run, real DB proof, or CI. The previous 45 LocalProxy test-harness errors were eliminated by the `f49e2e8` mocked-`frappe.db` setup.

**Proactive GitHub-only test-harness follow-up:** Source inspection found `ccpcerp/ccpc_erp/test_transaction_deletion_protection.py` uses the same `patch(...frappe.db.sql/get_value)` pattern without a bound database in standalone `unittest`. It was corrected to temporarily replace `frappe.__dict__["db"]` with `MagicMock()` and restore it via cleanup; no runtime code was modified. GitHub connector verified updated app review branch at **`806fa23516490ec7beefcff03a1baa09d722120e`**, one commit / one test file ahead of `f49e2e8`. This follow-up was **not yet pulled into DEVELOPMENT nor executed**, and the index-patch mock tests also remain unrun in the current work session.

**Next safe step:** With DEVELOPMENT still expected on `review/intercompany-approval-failure-tests` at `f49e2e8`, verify local branch and absence of modified *tracked* files, then `git pull --ff-only origin review/intercompany-approval-failure-tests` (preserve untracked `AGENTS.md`). Verify `806fa23`; then run the isolated mocked **Transaction Deletion Record protection** and **index patch** tests, recording actual outputs. Do not run `bench migrate`, Frappe integrated test runner, financial invoices or database concurrency experiments until separate DEV safety/backup approval. PRODUCTION untouched.

## DEVELOPMENT billing mock-suite failure and GitHub test-harness correction — 2026-10-13

**Operator-provided test output:** On DEVELOPMENT at `/workspace/development/frappe-bench` on review branch `review/intercompany-approval-failure-tests` (at the previously verified local commit `12e24c9`), ran:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  -q
```

The uploaded terminal output reported **`Ran 124 tests in 0.344s`, `FAILED (errors=45)`**. Representative/all visible failures were during `unittest.mock.patch` of `frappe.db.sql` or `frappe.db.get_value`, terminating at Frappe's `local.py` with **`RuntimeError: object is not bound`**. This is a **standalone unittest database LocalProxy/mock setup problem**, not a verified billing transaction failure. Tests encountering setup errors **did not validate their asserted billing behavior**.

**GitHub-first correction committed and verified:** App review branch [`review/intercompany-approval-failure-tests`](https://github.com/ccpcerp/ccpcerp/tree/review/intercompany-approval-failure-tests) advanced to **`f49e2e869e6f1c6c64da7f662042b6e0fee80aee`**. Exactly **one file** changed compared with `12e24c9`: `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py`. `TestIntercompanyMaterialBillingBatch.setUp` now temporarily substitutes `frappe.__dict__["db"]` with `MagicMock()` and registers cleanup to restore the original proxy. This mirrors the existing isolated index-patch test setup. **No application runtime code modified.**

**Verification status:** Commit and changed-file list independently verified on GitHub. **The revised 124-test suite has NOT yet been re-run on DEVELOPMENT**, so do not say it passes or assign release readiness based on this change. No CI test result, DB transaction, migration, PROD change, or branch merge.

**One next safe step:** In the DEVELOPMENT app directory, make sure the local branch remains `review/intercompany-approval-failure-tests` and tracked changes are clean; then fast-forward pull from the **same tracked remote branch** (no force, no switch, no destructive cleanup), retaining untracked `AGENTS.md`. Re-run the same `python -m unittest ...test_intercompany_material_billing_batch -q` and report the result. If new failures arise, resolve them in GitHub first. Actual MariaDB rollback and concurrency tests remain separate pending release gates.

## DEVELOPMENT mock unit-test milestone — 2026-10-13

**Operator-reported successful test execution (terminal transcript supplied in chat).** The user had entered the DEVELOPMENT Docker container and confirmed Git branch `review/intercompany-approval-failure-tests` tracking `origin/review/intercompany-approval-failure-tests`, at commit `12e24c9`, with only `?? AGENTS.md` untracked. The branch tip was independently reverified via GitHub connector as **`12e24c99daf020ba488940411379a6c517aa1c20`**.

The operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  -v
```

Captured transcript shows **4 tests passed**, `Ran 4 tests in 0.011s`, `OK`. All four mocked invoice failure-propagation paths passed: Sales Invoice insert exception, Purchase Invoice insert exception, SI cross-link save exception and final batch save exception. This is **operator-provided terminal evidence, not a remotely executed test via GitHub connector**.

**Strict scope:** This validates isolated Python mock interactions only. It **does not prove** MariaDB rollback, persisted invoice atomicity, two-connection concurrency correctness, hook behavior in a live Frappe request, or migrations. No database-integrated tests, `bench migrate`, application merges, or PRODUCTION modifications were authorized/performed in this step. The existing `AGENTS.md` stays untracked/excluded.

**Next safe action:** Run the **existing mocked billing batch Python unit-test module** on the same verified DEV branch using `./env/bin/python -m unittest ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch -q`. Inspect the result before expanding to the deletion-protection and patch unit tests. Only after a complete mock-suite baseline should a separate, explicitly reviewed DEVELOPMENT database-integration/backup/isolation procedure be considered.

## Prior development milestone — failure-path tests prepared (2026-10-12)

**GitHub code change complete, execution pending.** ChatGPT created application branch [`review/intercompany-approval-failure-tests`](https://github.com/ccpcerp/ccpcerp/tree/review/intercompany-approval-failure-tests) from preserved DEV checkpoint `f665cf3`. The GitHub connector verified tip **`12e24c99daf020ba488940411379a6c517aa1c20`** (2 commits ahead, zero behind checkpoint), adding **only one new Python test file**: [`test_intercompany_billing_approval_failures.py`](https://github.com/ccpcerp/ccpcerp/blob/review/intercompany-approval-failure-tests/ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_billing_approval_failures.py). No existing application code was altered; no pull/merge/migration/service/PRODUCTION action occurred.

**Four *mocked* failure-propagation test methods prepared** for: Sales Invoice insert failure; Purchase Invoice insert failure after Sales Invoice insert; Sales Invoice cross-link save failure after both inserts; and final billing batch save failure after both invoice inserts. These check exceptions propagate and later actions are skipped when appropriate. **No execution/lint/CI result has yet been verified** for these new tests. In-memory fields changed before final save do **not** establish database durability or rollback. These tests are not an alternative to real Frappe/MariaDB transactional tests.

**First next safe action:** request an operator **read-only DEVELOPMENT Git status/HEAD** before any pull or branch switch:

```bash
git -C /workspace/development/frappe-bench/apps/ccpcerp status --short --branch
git -C /workspace/development/frappe-bench/apps/ccpcerp rev-parse --short HEAD
```

Expect old review checkpoint `f665cf3` and untracked `AGENTS.md` based on earlier operator evidence, **but do not assume it without new output**. Do not overwrite local files or automatically stage `AGENTS.md`. If safe, separately plan bringing the new **GitHub test branch** into DEVELOPMENT with a verified procedure, then execute its test module only with operator approval and awareness Frappe's test runner may mutate the persistent DEV database. Backups/fixture isolation required for database mutation. Prioritize safe read-only assessment of MariaDB version/isolation, real two-connection locking tests, failure rollback, and non-unique-index review. No `bench migrate` without explicit review/authorization.

## Current decisions (standing)

- **GitHub-first:** implement specifically authorized CCPC custom-app changes in GitHub on reviewed feature/review branches, then DEVELOPMENT pulls reviewed commits for testing; push any DEV fixes back to GitHub. **Always verify the resulting GitHub commits** and maintain this handoff after milestones.
- **No automatic Codex reports to GitHub.** The user cancelled this effort; they may paste Codex reports manually. No recurring publisher, new paid OpenAI API integration or autonomous GitHub-reporting task.
- ChatGPT may inspect and update GitHub during **active conversations**; there is **no unattended or automatic handoff update** while no conversation is active. The user cannot know exactly when a thread will reach its limit, so update this handoff **proactively** at milestone boundaries rather than waiting for an explicit thread-transfer request.
- **PRODUCTION is off limits** without separate, explicit approval and backup/recovery/rollback review. DEVELOPMENT and PRODUCTION are separate Compose projects on the same host; database/data and credentials are not equivalent to GitHub code.

## Repositories and latest verified code

| Repository / role | Verified reference | Status |
| --- | --- | --- |
| [CCPC custom app](https://github.com/ccpcerp/ccpcerp) | `review/intercompany-dev-checkpoint-2026-10-12` → [`f665cf3805ba799e5182600286f40e027e3c3120`](https://github.com/ccpcerp/ccpcerp/commit/f665cf3805ba799e5182600286f40e027e3c3120) | **Eight DEV-only files safely committed and pushed, verified via GitHub** |
| Original billing feature branch | `feature/intercompany-material-billing` → `7ac238ee25101207216e601532d545297989b4ee` (last verified) | Earlier committed billing code; **review checkpoint not merged into it** |
| Application default branch | `version-16` → `cfcc193` (last verified) | Older, **does not contain billing/Withdrawal Slip feature** |
| [Deployment and project docs](https://github.com/ccpcerp/ccpc-frappe-deployment) | `docs/ccpc-checkpoint-2026-10-10`, draft [PR #24](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/24) | GitHub-first workflow and this handoff live in a **draft documentation branch; not merged to main** |

**Do not assume these SHAs remain current forever.** Reverify the branch tips when resuming.

### Recovered DEVELOPMENT checkpoint

Operator terminal verified the DEVELOPMENT application folder:

`/workspace/development/frappe-bench/apps/ccpcerp`

The operator staged exactly these eight files (four modified and four added), committed them as `f665cf3`, then pushed to `origin/review/intercompany-dev-checkpoint-2026-10-12`. The GitHub connector independently verified the remote branch tip and eight-file commit:

1. `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py`
2. `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py`
3. `ccpcerp/ccpc_erp/transaction_deletion_protection.py`
4. `ccpcerp/ccpc_erp/test_transaction_deletion_protection.py`
5. `ccpcerp/hooks.py`
6. `ccpcerp/patches.txt`
7. `ccpcerp/patches/v1_0/add_intercompany_material_billing_indexes.py`
8. `ccpcerp/patches/v1_0/test_add_intercompany_material_billing_indexes.py`

`AGENTS.md` was **untracked and deliberately excluded**; it still requires separate content review before any inclusion in GitHub. Do not treat it as operational instructions, automatically stage it, delete it, or run unreviewed agent directions.

At last operator check, DEVELOPMENT was on the local checkpoint branch. The exact **post-push working tree/status has not been rechecked**; do not assume it is completely clean. Never reset, clean, branch-switch or pull over pending work without checking.

A local Windows VS Code clone at `E:\CCPC Files 2025\Plant Wide\ERPnext\ccpcerp` was clean at `version-16`/`cfcc193` and remains optional. The user was told **not to delete it**; it is not required for ChatGPT GitHub inspection.

## Preliminary static code review of `f665cf3`

**Completed:** Verified eight files on GitHub and reviewed their source. Code includes Company and billing-batch `FOR UPDATE` locking, reload/stale-state checks, source-claim locking, guarded Finance approval transitioning to draft Sales/Purchase Invoices, approval/refresh immutability, Transaction Deletion Record protection, and two **non-unique** database indexes registered as a Frappe patch.

**Not completed or not proven:** No newly verified CI/test run, no MariaDB two-connection concurrency experiment, no live Frappe document integration test, no demonstrated atomic rollback if the second invoice insert fails, no migration execution, and no production release validation. Non-unique indexes do **not** guarantee uniqueness; actual isolation and lock ordering must be verified. The checkpoint is **work in progress**, not production-ready.

## Production-readiness assessment — 2026-10-12

**Scope:** Withdrawal Slip → Stock Entry / Material Issue → monthly Intercompany Material Billing only, **not** the entire ERPNext production instance. This is a **GitHub static-review assessment**, not a live DEVELOPMENT integration result. No deployment approval.

**Evidence checked with connected GitHub tools:** app review branch tip remains `f665cf3805ba799e5182600286f40e027e3c3120`, original feature branch tip remains `7ac238ee25101207216e601532d545297989b4ee`. Compare is one commit / eight files ahead; the original feature branch has **not** absorbed the checkpoint. Only a separate older Withdrawal Slip draft app PR #6 appeared in the inspected PR list; no reviewed billing release PR was verified. The billing batch Python test module contains **124 `test_...` methods**, mostly mocked. GitHub Actions query for PR runs associated with `f665cf3` returned **zero runs** (this does not prove no other CI ever ran). No newly verified fresh live DEV tests.

**Implementation appears substantially present:** Withdrawal Slip/Material Issue path, frozen source billing snapshots, Finance-approved paired draft SI/PI, locking and stale-state guards, audit-field immutability, source claim checks, deletion safeguards, and the two index patch definitions.

**Hard release gates still open:**

1. **Test current checkpoint in DEVELOPMENT**, collecting actual repeatable results rather than relying on the 124 test declarations or historical claimed pass counts; include Frappe v16 `extend_doctype_class` hook behavior and permissions.
2. **Two-connection concurrency verification on an approved safe DEVELOPMENT setup:** simultaneous batch creation/claims, preview/finalize/approve races; prove exactly one pair of invoices and clear retry behavior; inspect MariaDB transaction isolation and actual lock behavior. Code's `FOR UPDATE` and Company serialization is a mitigation, **not yet a demonstrated guarantee**.
3. **Failure atomicity/idempotency:** inject a failure after creation of the first draft invoice, prove transaction rollback leaves no orphan invoice and no incorrect Approved batch; test repeated approval calls, deletion/Transaction Deletion Record bypass attempts and accounting/stock consistency.
4. **Database/patch review:** `idx_icmb_scope` and `idx_icmbi_source_parent` are **NON-UNIQUE** and not proven applied. Review DDL and performance/lock effects separately, back up persistent DEV state where appropriate, seek explicit authorization before `bench migrate` or other DDL, test idempotence and clean failure handling.
5. **Review and release preparation:** ensure code review/CI coverage, resolve defects via GitHub-first branches, merge approved code, verify PRODUCTION's exact baseline, backups, restoration/rollback plan, migration scope and business acceptance. Production remains untouched until distinct explicit approval.

**How far:** Implementation is significantly advanced, but production readiness **cannot be assigned a credible percentage or go-live date** until real DEV DB integration tests pass. More verification work than feature scaffolding appears to remain. Treat it as **release blocked, not production-ready**, with at least these five groups of gates. Next practical milestone is a **safe DEVELOPMENT validation plan** that can first run non-mutating tests / review setup, then explicitly approves any fixture creation, DB changes, concurrency experiments and cleanup. No production testing.

## Immediate next priority

**Withdrawal Slip → Material Issue → Intercompany Billing**. Proceed from GitHub review checkpoint `f665cf3` and validate in DEVELOPMENT safely.

1. Inspect existing tests and identify highest-risk concurrency, idempotency, invoice failure rollback, audit-trail and transaction deletion paths. Document any code issues or missing tests **in GitHub**, using a reviewed branch for fixes.
2. Propose a controlled DEVELOPMENT-only validation plan, with transaction isolation and two simultaneous approval requests. **Do not invent results, execute financial transactions against production, or assume mock tests prove real MariaDB concurrency.**
3. Evaluate the new index patch separately before any DEV migration/DDL. Preserve DEV database/configuration and prepare appropriate backup/recovery steps if testing may modify persistent state.
4. After verified tests, push any corrections to GitHub, identify branch/commit, and update **this file** with outcomes, blockers and exact next safe step.

## Operating boundaries and handoff maintenance

- Read current app code and project documents using the connected GitHub tools before making code or workflow claims. Verify relevant branches, especially since the default app branch lacks recent work.
- Keep a clear distinction between **pushed code**, **uncommitted DEV changes**, **mocked tests**, **actual database tests**, **pending changes**, and **approved versus unapproved actions**.
- Protect SSH keys, tokens, business data and operational secrets. Existing DEV container historically exposed mounted SSH materials; **do not run uncontrolled agentic Codex inside it**.
- After **each meaningful code or test milestone**, before a high-risk context switch, and periodically in a long thread, update this *single current GitHub handoff* (and affected design/runbooks where needed); include UTC/date, verified refs, what changed, what was tested, outstanding risks, and the **one next safe step**. Do not churn files if nothing materially changed.
- When a chat reaches a length limit or an unexpected interruption, the **last successfully committed GitHub handoff** is the recovery checkpoint. No claim that ChatGPT can predict an exact thread limit or publish while a thread is inactive.

## Next-conversation starter

> Continue CCPC ERPNext **GitHub-first**. Use the connected GitHub tools to read `docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md` and `docs/ccpc-project/CURRENT-HANDOFF.md` on the deployment documentation branch (or their newest authoritative locations). Verify the live app review branch/commit before continuing. Do not use old ChatGPT Project Source handoffs as current state. No automatic Codex GitHub reporting, no additional API billing, no production operations. Proceed with the handoff's next safe development step.
