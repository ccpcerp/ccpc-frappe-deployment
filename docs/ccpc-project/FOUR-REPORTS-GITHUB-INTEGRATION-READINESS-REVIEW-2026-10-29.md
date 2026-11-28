# Four day-one reports — GitHub-only combined integration readiness review

**Reviewed 2026-10-29 (Asia/Manila). Status: CONDITIONAL NO-GO for combined integration/deployment pending explicit access-control remediation and shared CI composition review.** This is a **source/documentation review only**. No application branch was merged, no new integration branch has been created, no hosted CI run was triggered, and no persistent DEVELOPMENT/PRODUCTION environment was accessed.

## 1. Verifiable provenance

**Authoritative custom app:** [ccpcerp/ccpcerp](https://github.com/ccpcerp/ccpcerp). All four draft PRs use exact same verified Finance base `feature/finance-mapping-lifecycle-2026-10-28` at `7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`, and each is **zero commits behind its Finance base** at review. The release/default `version-16` must not be assumed to contain this Finance work.

| Family / original standalone tests | PR and exact verified head | GitHub compare vs Finance |
| --- | --- | --- |
| Intercompany source/billing statuses; Build #37 **13+5=18/18 PASS** | [PR #28](https://github.com/ccpcerp/ccpcerp/pull/28) `444d1dcb795e79a97b0db7be487e529fa7a2fba2` | 21 commits ahead, **9 new files + only `.circleci/config.yml` modified** |
| Original beneficiary Department gross material; Build #40 **14+6=20/20 PASS** | [PR #29](https://github.com/ccpcerp/ccpcerp/pull/29) `dd1375343d84a9b48de8063eb530786d463a4989` | 13 ahead, **9 added + config modified** |
| Original Equipment gross material + separate unpriced Job activity; Build #43 **15+5=20/20 PASS** | [PR #30](https://github.com/ccpcerp/ccpcerp/pull/30) `872d56b4b908a571daf581df20e4b56661531c6e` | 11 ahead, **9 added + config modified** |
| Company original stock-voucher SLE vs posted P&L GL, independent perspectives; Build #49 **15+5=20/20 PASS** | [PR #31](https://github.com/ccpcerp/ccpcerp/pull/31) `5016ad711c8940258850cc602e9c9c58ec41c30b` | 13 ahead, **9 added + config modified** |

All four **exact-head GitHub CircleCI checks** are green, including their individually approved manual hold and native MariaDB job; source tests **57 Frappe unit + 21 native SQL across independent builds**, NOT one combined 78-case execution. PR31 Build #46 at prior SHA remains an accurately recorded failure; Build #49 passed corrected SHA. All four PRs remain DRAFT/UNMERGED.

**Path topology:** 20 report definition/code/JS/unit-test paths across four distinct Script Report directories, plus 16 unique one-PR CI wrapper/fixture/test paths (four each, including their test guards); **the sole shared modified path is `.circleci/config.yml`**. The four report names and standard JSON `ref_doctype` are distinct; no existing Finance app controller, DocType schema, hooks, patches, invoice code or stock/GL write path is changed by these PR diffs. This proves file-path separation, **not** combined runtime/test validity.

## 2. Blocking review findings

### R1 — Access/Company/row visibility must be reviewed and reinforced before DEVELOPMENT integration (HIGH security review gate)

**PR28:** `ccpc_erp/report/ccpc_intercompany_withdrawal_billing_status/ccpc_intercompany_withdrawal_billing_status.py`:
- `_require_access()` checks **System Manager role plus DocType-level reads** for Company/Stock Entry/Withdrawal Slip/Billing Batch/Sales Invoice/Purchase Invoice. `_validate_filters()` checks **both requested Company document reads**, and SQL filters by issuer/requester Company.
- However `execute()` runs `frappe.db.sql(_source_sql(), ...)` followed by `_present(rows)`, **without explicit per-result Stock Entry, Withdrawal Slip, Billing Batch, Sales Invoice, or Purchase Invoice record-level `check_permission('read')`**. This can matter for Site User Permission / record-specific restrictions even when user has the role and can read a Company. Report JSON `apply_user_permissions=1` is **not evidence that raw SQL automatically applies those per-row permission predicates**.
- **Gate:** design and test fail-closed visibility checks for all existing sensitive source/billing/foreign-linked invoice records and exact Company-matched invoice links, including a System Manager with deliberately restricted Company/document permissions. Confirm the applicable production permission model before shipping. This is a source-level potential disclosure gap, **not a reproduced real-site exploit**.

**PR29:** `ccpc_erp/report/ccpc_department_material_consumption/ccpc_department_material_consumption.py`:
- `_require_access()` checks System Manager + broad source Doctype reads; selected Company and optional Department records are checked, and `_assert_department_visibility()` checks returned **header/detail Department** document reads.
- Returned Stock Entry, linked Withdrawal Slip, and related Item are **not individually checked** before gross source values/identifiers are returned by raw SQL. A user could be able to read the selected Company/Department but be restricted on individual operational records. **Gate:** test/fix per-result Stock Entry/Withdrawal Slip (and Item where user-visibility policy requires) reads, fail-closed if hidden, while preserving explicit missing legacy source quality; do not silently skip sensitive conflict rows or expose partial datasets.
- As above, this is a **permission coverage gap in source review**, not an established exploit on actual CCPC Company/user masters. Unit tests and disposable fixtures were individually green but do not settle all real User Permission combinations.

**PR30** has per-result Stock Entry, Withdrawal Slip, original/current Equipment Registry and Job Order document read checks. **PR31** has per-Stock Entry and per-P&L Account document read checks and Company/DocType role gates; however independently grouped raw `GL Entry` records are not individually checked as documents. **Gate for both:** verify real Company-scoped User Permission semantics in DEVELOPMENT; for PR31, verify authorization to display grouped GL values with the intended privileged role rather than equating Account permission with visibility of every underlying GL document.

### R2 — PR28 unbounded result set (MEDIUM availability/performance gate)

PR28's `execute` directly fetches all matching `_source_sql()` rows; there is no source-row cap / `LIMIT` / overflow rejection in the reviewed query. It restricts **both Companies and dates up to 367 days inclusive**, which reduces scope but does not guarantee safe row count on large active ledgers or corrupted repeated joins. PR29 rejects >1000 source rows, PR30 rejects >800 material/>200 job rows, PR31 rejects >400 vouchers/>800 GL groups. **Gate:** add a clear fail-closed `LIMIT (MAX+1)` bounded result check to PR28 with a unit test and benchmark/explain against a representative non-sensitive DEV dataset. Avoid silent truncation, mixing currencies or adding billing and SLE totals.

### R3 — Shared CI file cannot be mechanically stacked (HIGH integration/build gate)

**All four PRs independently add ~63 lines to `.circleci/config.yml`**: each adds a distinct default-false parameter, a separately guarded disposable native job and a separate manually held workflow. Blindly selecting one final config would **drop three workflows**; naive Git cherry-pick/merge may conflict at shared hunk anchors.

Four branch-specific tests under `.circleci/test_*_ci_config_static.py` also assume exclusivity:
- PR29 explicitly asserts `run_intercompany_report28` **absent**.
- PR30 and PR31 explicitly assert `run_department_report29` **absent**.
- These pass on individually isolated branches but become **false assertions** if all four default-off workflows coexist. These are static CI-test design assumptions, **not proof that app report SQL conflicts**.
- Each original stage script and `ci_*_site_guard.py` expects its **exact original report branch and its own approved SHA**, plus exact job, site and project identities. A combined branch is **not authorized** to reuse them merely by setting a pipeline flag. Preserve these as historic standalone acceptance evidence; do not bypass SHA guards or turn paid jobs on by default.
- **Gate:** choose one auditable combination strategy: (A) recommended low-risk integrated report candidate brings **only the 20 unique read-only report source/metadata/unit-test files** from each PR into a new, isolated GitHub review branch rooted in the verified Finance base; leave original CI harnesses and branch approvals intact in their historical PRs, or (B) preserve all CI wrappers, explicitly merge all four default-OFF config entries and replace the mutually exclusive tests with **positive assertions** (branch/SHA/manual hold/default-off per workflow) before any new paid-run consideration. Both require explicit owner approval to create a combined branch and authorize the chosen integration code change/merge; neither is a completed merged build.
- **Any integrated Frappe/SQL testing on a new branch needs distinct approval and a correctly scoped test harness.** Directly running the CI-only native fixture modules against persistent DEVELOPMENT is prohibited by their site guards and could mutate synthetic data. Do not remove the guards to force DEV tests.

### R4 — Accounting and report scope must not be conflated (release policy gate)

- PR28's **frozen intercompany billing amount, draft/linked invoice status and original issue SLE** are different measures; it does **not** certify submitted SI/PI accounting or double-entry elimination.
- PR29's **verified protected Stock Entry beneficiary Department** is not independently frozen original Requesting/Work-for Section/Department. It displays gross SLE only, not expense GL or net returns.
- PR30's independently captured Equipment pair can identify original Equipment issue. No immutable original **Job Order link** exists on the posted source row, so current Job Order hours are **unpriced and not additive** to material value.
- PR31's `STOCK_ISSUE_VOUCHER_COMPARISON` and `ALL_PNL_GL_VOUCHER_ACCOUNT` are explicitly distinct, **non-additive** perspectives. Its variance compares original outbound SLE against **eligible Expense GL at Stock Entry voucher grain**; it is not item-level GL certification, complete Company P&L tie-out, intercompany elimination, net returns, or multi-company currency consolidation.
- Cross-report source values may represent **the same stock issue** at different grains. Never sum four report values into a Company grand total.

## 3. Recommended shortest safe implementation sequence (not executed)

1. **Scope authorization:** Owner approves creating an integration-only GitHub review branch from Finance base, a specific report-only vs full-CI combination method, and targeted permission/row-cap corrections to R1/R2. Original PRs remain immutable green acceptance references; avoid rewriting them merely to preserve badge status.
2. **GitHub-only integration:** Confirm Finance base + all four exact PR heads have not moved. Build deterministic manifest of the 20 new Report files, validate metadata `is_standard=Yes`, unique Report name/ref_doctype, no conflicting hooks/patches. Assemble on a new review branch **without** modifying Finance base, release default, or source PR heads. If CI wrappers included, compose config and static checks deliberately; retain all default-off and manual/branch/SHA protections. Add safe permissions/limit tests, review SQL grain and docs. Commit, diff and review the *actual integrated SHA*.
3. **Preflight tests:** Read-only GitHub diff/compile/path/security review. Run combined **57** report policy tests on a disposable or separately authorized DEVELOPMENT fixture environment; distinguish those from the **21 original independently passing native tests**. No CircleCI credits without a new precise authorization.
4. **DEVELOPMENT Gate A — separately approved:** Before touching shared bench or either real site, operator captures exact actual `/workspace/development/frappe-bench/apps/ccpcerp` branch/HEAD/remote and porcelain status including untracked files; inspect both `development.localhost` and `ccpc-integration2.localhost`, current patch logs, Finance Account/Cost Center/Company permissions, backups/restore viability, and shared services. Previously observed DEVELOPMENT shared checkout and untracked `AGENTS.md` are **historical**, not current assertions. Never use `git reset --hard`, `git clean`, blind checkout/merge/pull or run prior synthetic CI suites against real business databases. Preserve uncommitted work and untracked operator instructions.
5. **DEVELOPMENT controlled acceptance — separate explicit approval after preflight:** Pin exact review SHA; perform controlled non-destructive checkout/pull only after clean-tree/backup/rollback review; decide which site to migrate/test first given shared code and potential hooks; inspect patch/schema impact (four PRs themselves add **no** patches, but Finance base does). Validate actual report registry, System Manager and Company/record permissions, genuine CCPC masters, real issued SLE vs posted GL by original voucher, unrelated return/reversal and intercompany status, row caps/SQL `EXPLAIN`, and no duplicate material/GL or invoice postings. Any DEV fixes must return to GitHub.
6. **Release decision:** Only after accepted combined GitHub/DEVELOPMENT evidence seek distinct authorized merges and PRODUCTION deployment with confirmed backup/restore, rollback, change window and financial reconciliation. **PRODUCTION NO-GO.**

## 4. Decision checkpoint

**Current recommendation: hold merges and DEVELOPMENT changes.** The fastest safe next change is to authorize a new integration-only GitHub review branch with **report-only aggregation (20 files)** and limited **R1/R2 security/row-cap corrections**, then re-review and test it. This minimizes CI-file collisions and paid-run exposure but intentionally does not preserve individual CircleCI harness files in the combined branch (the exact original PRs retain them). A more conservative alternative is to retain all CI guard infrastructure and explicitly compose the config, at the cost of extra CI-specific code and test maintenance. Neither approach should be mislabeled as approved deployment.

**Credit status:** owner reported **27,689 CircleCI credits remaining** after Build #49; no new paid CI run is authorized under this GitHub-only review. No DEV/PROD resources were accessed by ChatGPT.

**Documentation branch:** `docs/ccpc-checkpoint-2026-10-10`. Supporting details: [current handoff](CURRENT-HANDOFF-2.md), [Build #49 acceptance](COMPANY-GL-REPORT-PR31-CIRCLECI49-REAL-MARIADB-ACCEPTANCE-2026-10-29.md), [DEVELOPMENT guarded integration plan](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md).
