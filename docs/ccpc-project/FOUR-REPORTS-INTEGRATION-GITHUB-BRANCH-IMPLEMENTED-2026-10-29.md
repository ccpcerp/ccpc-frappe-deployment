# Four day-one reports — integrated GitHub review branch implemented

**Subsequent checkpoint (2026-10-29):** The owner authorized preparation of **one manually held combined MariaDB run**. [Draft app PR #32](https://github.com/ccpcerp/ccpcerp/pull/32), new head **`061e65710eb4b527fc8ac579aaab8ccad4dd131d`**, now includes a strict exact-SHA CI site guard, default-OFF held workflow, ported 21 native suites + 1 cross-report native test, and six source-only static checks, **all NOT YET EXECUTED at the new commit**. This document below describes the **earlier 20-report-file source-only checkpoint** `bfe9477...`; it is preserved as history. See [current PR32 CI/readiness record](FOUR-REPORTS-PR32-MANUALLY-HELD-CI-REVIEW-2026-10-29.md). No paid CI job, merges, DEVELOPMENT or PRODUCTION operations made by ChatGPT.

**2026-10-29, owner authorization:** owner explicitly approved creating a combined **GitHub-only review branch** from the verified Finance base, combining 20 report-only source/JS/JSON/unit-test files and implementing the limited permission/query-bound corrections discovered in the [readiness review](FOUR-REPORTS-GITHUB-INTEGRATION-READINESS-REVIEW-2026-10-29.md). **This is NOT authority to merge source PRs, relax permissions, run new paid CircleCI tests, pull/migrate DEVELOPMENT or touch PRODUCTION.**

## Verified app branch

- Repository: [ccpcerp/ccpcerp](https://github.com/ccpcerp/ccpcerp)
- New review branch: [`review/four-day-one-reports-integration-2026-10-29`](https://github.com/ccpcerp/ccpcerp/tree/review/four-day-one-reports-integration-2026-10-29)
- **Verified new HEAD `bfe9477977fe336917639084757638d2b59d0514`**, directly descendant of reviewed Finance base **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**.
- GitHub compare base→new branch: **20 commits ahead, 0 behind, exactly 20 added paths under `ccpcerp/ccpc_erp/report/`** and **zero** changed existing code, migration, schema, `hooks.py`, `patches.txt` or `.circleci/config.yml`. The new branch was created from exact GitHub Finance commit (not default `version-16`).
- Four distinct Script Report directories (5 files each: `__init__.py`, standard Report JSON, JS, Python report, Python Frappe unit cases):
  - PR28 `ccpc_intercompany_withdrawal_billing_status`, originating [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28), `444d1dcb795e79a97b0db7be487e529fa7a2fba2`.
  - PR29 `ccpc_department_material_consumption`, originating [PR #29](https://github.com/ccpcerp/ccpcerp/pull/29), `dd1375343d84a9b48de8063eb530786d463a4989`.
  - PR30 `ccpc_equipment_job_material_activity`, originating [PR #30](https://github.com/ccpcerp/ccpcerp/pull/30), `872d56b4b908a571daf581df20e4b56661531c6e`.
  - PR31 `ccpc_company_stock_pnl_gl_reconciliation`, originating [PR #31](https://github.com/ccpcerp/ccpcerp/pull/31), **corrected** `5016ad711c8940258850cc602e9c9c58ec41c30b`.
- Blob comparison independently confirms PR30 and PR31 Python report, unit-test and standard JSON files are **byte-identical** to their green PR source. PR28/29 report Python and unit-test files intentionally differ by the approved safeguards. Four PR heads remain original and DRAFT/UNMERGED as of integration implementation.

## Exactly scoped changes made only in combined review branch

### R1 — Per-record permission checks in raw SQL reports

**PR28** Python report now runs `_check_row_visibility(rows)` **after bounded SQL fetch and before `_present`**. All existing returned Stock Entry, Withdrawal Slip and Intercompany Billing Batch records require `frappe.get_doc(...).check_permission("read")`. Every existing linked Sales/Purchase Invoice (including a forged/cross-Company reference) requires explicit read before exposing returned billing status; missing/deleted legacy invoice references remain a `Missing Reference` outcome rather than a fabricated invoice. Repeated records are checked once per (DocType, name). Existing role/DocType and **both** Company permission requirements are preserved. SQL source itself is unchanged except the row limit.

**PR29** source-visibility check `_assert_department_visibility(rows)` now checks each existing Stock Entry, Withdrawal Slip and Item, as well as both source header/detail Department records. Missing legacy Item/Department masters do not become fabricated documents or silent correct attribution. Distinct (DocType, name) permission checks are deduplicated; no conversion to a less privileged report role.

These changes are **fail-closed security hardening**; a report that previously showed a raw-SQL row to a System Manager with source-document restrictions may now reject the entire result. Access-control design and tested Frappe semantics on a real CCPC Company/User Permission configuration remain a DEVELOPMENT acceptance gate. No new role grant or permission bypass was added.

### R2 — Intercompany result bound

**PR28** `MAX_ROWS=1000`; `execute` passes `row_limit=MAX_ROWS+1`; `_source_sql()` orders deterministically and uses `LIMIT %(row_limit)s`. If the SQL returns more than 1,000 joined detail/claim rows, the report raises `frappe.ValidationError` and **does not silently truncate** or return a misleading partial total. Query is still filtered by two distinct Companies and bounded dates. A real representative query plan and realistic volume test are outstanding; a bounded output is not by itself a complete database resource limit.

### Added source-level tests (AUTHORED, not executed)

- PR28 `test_ccpc_intercompany_withdrawal_billing_status.py`: **13 original + 4 new = 17 tests**. New: exact overflow + query limit, deduplicated sensitive linked-record read checks, denied existing Sales Invoice, deleted invoice still flagged as missing reference.
- PR29 `test_ccpc_department_material_consumption.py`: **14 original + 3 new = 17 tests**. New: source Stock Entry/Slip/Item/two Department reads, fail-closed hidden source records, missing legacy master behavior.
- PR30 remains **15** original policy cases; PR31 remains **15** original policy cases.
- **64 report Frappe policy unit tests AUTHORED in combined branch, NOT EXECUTED there.** Previous **57 original unit + 21 native MariaDB cases PASS** occurred on **four separate** original PR commits and cannot be transferred automatically as passing combined tests. The new seven tests have no passing runtime evidence yet.
- GitHub-connected source readback verified both corrected Python reports and all seven new tests present; 20/20 expected paths in compare. Local Frappe bench/native MariaDB, actual Python syntax compilation, CircleCI parser, full integrated regression execution, DEV site security/performance/permissions and real transaction/GL tie-out **have not been executed or independently verified** for this combined head.

## CI and security boundary

The combined branch **intentionally does NOT include** the four mutually conflicting standalone `.circleci/config.yml` edits or CI-only fixtures/site guards/stage scripts. It inherits the exact Finance base default-off CI configuration, so **do not claim its four original SHA-approved report workflows exist on the new branch**. Source branch/approved SHA variables for PR28–31 must never be repurposed for this new commit. The four original PRs retain their independently verified Frappe/MariaDB acceptance. Any future true integrated SQL acceptance must use a **separately reviewed and explicitly authorized disposable harness**, with its own exact-SHA/manual hold, before paid execution. Do not run original synthetic fixture modules on real DEVELOPMENT.

No new app controller, job scheduling, report-writing, data migration, shareable secrets, CI setting or production asset has been modified. All four reports remain read-only, and their distinct accounting measures are **not additive**. PR28 draft invoice/billing status is not submitted invoice GL; PR29 original Department beneficiary is not issue-time requested Section; PR30 Job activity has no frozen issue-to-Job link or labor pricing; PR31 SLE gross value and posted P&L account results are different perspectives.

## Next safe gate (not executed)

1. Review the integrated branch diff and new seven unit tests. If available, validate 64 native Frappe policy tests and a combined snapshot source/GL test on a **separately authorized disposable site**; inspect real per-row user restrictions and performance/row caps. A new hosted CircleCI run needs separate owner approval; **last owner-reported 27,689 credits after Build #49**.
2. After explicit owner approval, run **read-only DEVELOPMENT preflight first**: actual shared app checkout branch/full SHA/index/worktree/untracked files including historical `AGENTS.md`, both valid sites' database/patch/role/master states, existing protected backups, effects of shared bench on both sites, and rollback. Stop on any unexpected drift. **No checkout, pull, migration or restart without a separate authorization after that review.**
3. Real DEVELOPMENT acceptance before release: verify Report registration and Frappe permission/User Permission filtering for the actual Companies, sample issuing vs requesting billing rows, issue-time Department and Equipment provenance, missing/foreign source exceptions, source/SLE posting-date valuation, voucher-level GL and Company P&L, row caps and query plans, negative cases; return any fixes to GitHub and retest.
4. Merges and PRODUCTION cutover remain independent, owner-approved changes after backup/recovery/rollback and genuine accounting acceptance. **PRODUCTION NO-GO.**

**Implementation status:** committed and GitHub-readback verified source-only combined review branch at `bfe9477977fe336917639084757638d2b59d0514`; original report PRs and existing environments unmodified. No new hosted run was initiated by ChatGPT.
