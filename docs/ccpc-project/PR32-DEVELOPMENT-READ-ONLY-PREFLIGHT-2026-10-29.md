# PR32 — DEVELOPMENT read-only preflight, operator evidence (2026-10-29)

**Status:** Seven read-only checks **PASS** as reported by the owner at `gani@ccpcerpserver`. **No Git checkout/pull, migration, new backup, backup restore, service restart, database writes, PR merge, PRODUCTION operation or paid CI run were authorized or executed in this preflight.** User-provided terminal outputs in the active conversation are the evidence, not machine access by ChatGPT. Continue one safe verified step at a time.

## Authority / target

- The owner explicitly approved **read-only DEVELOPMENT preflight only** after [draft PR32](https://github.com/ccpcerp/ccpcerp/pull/32) completed CircleCI Build #52 86/86 PASS on synthetic disposable MariaDB site.
- Intended incoming **GitHub** app branch: `review/four-day-one-reports-integration-2026-10-29`, tested full SHA **`061e65710eb4b527fc8ac579aaab8ccad4dd131d`**, **DRAFT/UNMERGED**, based on Finance commit `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`.
- Shared **actual DEVELOPMENT checkout**, last verified by operator: `/workspace/development/frappe-bench/apps/ccpcerp`; **detached HEAD**, full commit **`0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`**; `git status --porcelain=v1 --untracked-files=all` reports **only `?? AGENTS.md`** (no modified tracked files). **Preserve this untracked file; do not clean, stash, reset or overwrite.**
- Both intended DEVELOPMENT site config files exist: `development.localhost` and `ccpc-integration2.localhost`; each refers to a different configured database name, without printing names or passwords. Site-file separation **does not prove host-level resource isolation**. Known incomplete site `ccpc-integration.localhost` is excluded.

## Seven operator-confirmed read-only checks

| Gate | Direct owner output / interpretation |
|---|---|
| 1. Git checkout/worktree | Path above; blank current branch means detached HEAD; exact `0c223d7...`; only untracked `AGENTS.md`. **PASS**, but cannot assume incoming PR already installed. |
| 2. Site configs | Both config files found and database names distinct. **PASS**. |
| 3. Protected backup inventory | Both site's expected **October 27 four-component sets** found and nonzero. **PASS**. |
| 4. Live installed-app enumeration | Both sites reported `frappe 16.33.1 version-16`, `erpnext 16.34.2 version-16`, `ccpcerp 0.0.1 HEAD`. **PASS**; shared detached application HEAD remains `0c223d7...`. |
| 5. Recorded CCPC patches | On each site, **8 declared / 8 Patch Log records / 0 declared unrecorded**. **PASS** for recorded status, not independent patch result integrity. |
| 6. Finance schema | On each site, **four/four mapping DocTypes, two/two mapping Roles, five/five Stock Entry Detail provenance custom fields**. **PASS** for existence, not business configuration, users, accounting postings or role-level access. |
| 7. Backup archive integrity | On both sites, `gzip -t` database, `tar -tf` public/private files and `python3 -m json.tool` site config all **PASS**. **Archive readability only**; NOT full recovery, consistency or freshness. |

### Protected October 27 recovery file metadata from operator

| Site | Original database gzip | Site config backup | Public archive | Private archive |
|---|---:|---:|---:|---:|
| `development.localhost` | 1,652,142 bytes | 234 bytes | 10,240 bytes | 20,480 bytes |
| `ccpc-integration2.localhost` | 1,079,342 bytes | 212 bytes | 10,240 bytes | 10,240 bytes |

- All four of **main site's** files modified **2026-10-27 02:24:22 UTC**; all four of **integration2 site's** files modified **2026-10-27 02:48:02 UTC**. More current changes may exist. No current recovery point or off-host backup verification yet. Archive read checks were safe and left original backups in place.
- The initial patch log inspection emitted two **nonfatal `sys.prefix` / `sys.exec_prefix` path normalization warnings** because the invocation used `sites/../env/bin/python`; both database checks completed with 8/8/0 output. Subsequent commands should use canonical absolute venv interpreter path.

## Pending gates, strict boundaries

1. **NEXT READ-ONLY operator check:** validate the **four exact Companies and 5 intercompany Account structures per Company** against verified GitHub file `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` at PR32. Inspect actual Company abbreviation, Account number/name/company/parent/root/account type/is_group/disabled. Must print summary counts and field-name discrepancies only, no passwords/business values. A previously applied patch is insufficient proof that masters remain valid.
2. Then separately check internal Customer/Supplier party mappings and actual Company/Department/Cost Center/warehouse readiness and end-user data-access/role signoff, using bounded read-only reports without exposing private business records.
3. **Recoverability remains NO-GO** without verifying a current checkpoint, suitable off-host copy and an independent restore in a disposable, production-disconnected environment. Any creation/restoration, even on DEV, requires fresh scoped approval.
4. Shared DEVELOPMENT bench and host may also serve other sites and coexist with legacy production containers. Review actual `docker ps` / process and host resource scope read-only before any deployment.
5. A **controlled checkout/pull/migration and full real DEVELOPMENT acceptance are not authorized** by this preflight. App PR32 and original PRs remain DRAFT/UNMERGED. Never run CircleCI disposable test fixtures on persistent DEVELOPMENT, as their guards deliberately reject it.
6. **PRODUCTION NO-GO** absent explicit distinct approval, tested recovery, rollback and release signoff. No blanket deployment, additional CircleCI charges or automatic retries.

## References

- [Active handoff](CURRENT-HANDOFF-2.md)
- [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Prior DEVELOPMENT controlled integration plan](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md)
- [PR32 real MariaDB CI acceptance](FOUR-REPORTS-PR32-CIRCLECI52-REAL-MARIADB-ACCEPTANCE-2026-10-29.md)

## Step 8 — Company/account check: main PASS; synthetic Integration2 comparator was inapplicable

**Owner terminal output, 2026-10-29:** The Step 8 GitHub-derived patch checker `ccpcerp/patches/v1_0/create_intercompany_material_accounts.py` verified **4/4 actual Companies and 20/20 intercompany accounts** on `development.localhost`, including expected Company abbreviations and account parent/ledger attributes. **Main DEVELOPMENT: PASS**.

The **same check** on `ccpc-integration2.localhost` reported **0/4** expected real group-Company abbreviation matches and **0/20** accounts, followed by `RuntimeError: Master configuration requires review: ccpc-integration2.localhost`. **Interpretation correction:** The checker `continue`s before account lookups whenever a Company doesn't match, so `0/20` is **NOT evidence that the accounts are absent or invalid**; they were **not evaluated**. The check incorrectly assumed that this historically isolated test site used the four real CCPC group Companies.

**Existing GitHub design resolves the likely explanation without changing any database:** [DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md), milestones D13–D15 and D19, records Integration2 as **synthetic two-Company Finance test fixture**: `Integration Test Issuer` (`TISS`) and `Integration Test Requester` (`TREQ`), with **two** Companies historically confirmed at D14; TISS had 30 eligible Expense Accounts, one eligible Cost Center, 13 eligible leaf Departments and five leaf Item Groups. It also records completed dedicated maker/checker authorization tests. Thus **the production-like four-Company / 20-intercompany-account check is inappropriate for Integration2 and must not be used as an acceptance gate for that site's synthetic fixtures.**

**NEXT single read-only operator action:** On Integration2 only, count `tabCompany` rows, and verify the exact named/abbreviated TISS and TREQ records with bound SQL. Do not list unrelated Company names, secrets, accounts or financial entries. If both identities exist, classify Step 8 by site purpose: **main 4/4 + 20/20 PASS; Integration2 synthetic TISS/TREQ 2/2 PASS (separate criteria)**. If missing or changed, STOP and investigate; do not automatically create/rename Companies or rerun patches. Do not presume historical two-Company status is current without operator readback.

The user authorized **read-only preflight only**, not deployment or remediation. Existing October 27 protected backups remain non-restoration-tested and potentially stale. GitHub app PR32 stays DRAFT/UNMERGED; **no checkout/pull/migration/DB write, CircleCI repeat or PRODUCTION actions**.
