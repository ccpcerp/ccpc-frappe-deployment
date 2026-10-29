# CCPC ERPNext — PR #28 executable offline validation (2026-10-29)

**Scope:** Owner approved continuation of PR #28 executable testing. This record describes **local Python stubbed-unit and SQLite in-memory SQL-shape execution ONLY**. No Frappe bench, MariaDB service, CircleCI, DEVELOPMENT, Integration2 or PRODUCTION was touched. No billable CI was triggered. Production remains **NO-GO**.

## GitHub source provenance

- App PR: [#28 — CCPC Intercompany Withdrawal Billing Status](https://github.com/ccpcerp/ccpcerp/pull/28).
- Review branch: `review/intercompany-source-billing-report-2026-10-29`, verified HEAD **`dfb63d975de009ea0168ddd5c9e09a60c26ad4c6`** after one test-assertion correction.
- Base Finance feature, unchanged: `feature/finance-mapping-lifecycle-2026-10-28`, SHA **`7cc85cf5bc275ff7d653edc9ae3520d6c89b20cd`**.
- Report Python source local copy confirmed byte-exact using standard Git blob SHA algorithm `sha1(b'blob <length>\\0' + content)`: **`686aaa8aae5de0aee1e2bb9f3aa7cc95be0a209c`**.
- Report existing 13-case test module after correction confirmed same algorithm: **`6c964ee685b274771d68e94c1563c0477b660888`**.
- GitHub update `dfb63d...` corrected **one test assertion only**: original SQL correctly starts its outer clause with `WHERE se.docstatus = 1`; old source-focused test incorrectly demanded `AND se.docstatus = 1`. No SQL, business Controller, schema, environment or permissions were changed.

## Executed results

| Execution | Result | Scope |
|---|---|---|
| `python -m py_compile` of byte-exact report and source test module | **PASS** | Local Python 3 syntax only |
| First run of original 13 report unittest methods | **12 PASS, 1 FAIL** | The lone failure was the incorrect `AND` vs `WHERE` string assertion, not an application SQL validator failure |
| Corrected module: `unittest.TextTestRunner` | **13/13 PASS**, zero errors/failures/skips | All GitHub-authored test methods executed with a deliberately minimal `frappe` module stub; not installed Frappe runtime |
| In-memory SQLite SQL query scenarios | **12/12 PASS** | Executes the exact PR28 `_source_sql()` query in a Python `sqlite3` database using disposable synthetic table definitions and a translation of `%(param)s` placeholders to `:param` |

### SQLite synthetic scenario assertions

1. Two outbound SLE fragments for the same original source produce one billed source row (no duplicate valuation).
2. Exact source's two fragment quantities aggregate to the issued stock quantity.
3. Outbound SLE issue value remains separate from frozen billing amount.
4. Both paired invoice references report **Draft** (not submitted) with matching reciprocal links.
5. Other unbilled original source remains visible with independent SLE value.
6. An unselected requesting Company's issue is excluded.
7. A third-party issuing Company's issue is excluded.
8. Cancelling an active batch restores the source to visible **Unbilled**.
9. Two conflicting active billing claims fail closed rather than duplicate financial rows.
10. A forged cross-Company SI reference does not load foreign invoice status; shows an invalid/missing link.
11. A forged billing child's parent Stock Entry is flagged while the original SLE issue value stays intact.
12. Missing/cancelled original outbound SLE produces an explicit `NO_ORIGINAL_OUTBOUND_SLE` exception, not a fictitious zero cost.

Synthetic data was created **only in local ephemeral SQLite memory** with test Companies (`ISSUER`, `BUYER`, `OTHERBUYER`, `FOREIGN`); no live CCPC master data, real accounting transactions, production records or credentials were accessed.

### Limits

- **NOT** a native Frappe test suite: the import, translation, permissions, `frappe.db.exists`, `frappe.get_doc`, `frappe.has_permission`, and `frappe.db.sql` functions in the first local runner used lightweight stubs; they do **not** prove installed Frappe permissions, Company isolation or actual Report rendering.
- SQLite executes SQL under its own dialect and relational engine, **not MariaDB**. The MySQL/MariaDB SQL parameter placeholders were translated to SQLite placeholders and minimal synthetic tables were created explicitly. These tests do not prove MariaDB execution plans, performance, collations, MySQL connector behavior, live billing Source DocType compatibility, or row-level Frappe permission restrictions.
- The previously owner-supplied CircleCI build #34 **12/12 PASS** covered Finance and Withdrawal-to-paired-invoice-draft functionality at the Finance feature commit. It **did not** execute this newly drafted report. Never add those 12 tests to the 13+12 offline report tests as though one hosted combined run occurred.
- The exact local in-memory fixture scripts/results are available only in the active validation session, not a committed GitHub test fixture; future reproducible official test execution should use a new, reviewed native Frappe/MariaDB disposable test module and saved CI job evidence.

## Next gate — owner-bounded real MariaDB acceptance

1. Implement a **separate exact-SHA held disposable test harness** or verify that the existing manually held Finance bridge job can safely accept the new report test without widening persistent/production reach. Do **not** repurpose or auto-trigger the previously approved build #34 SHA.
2. Test signed actual Withdrawal→submitted Material Issue and SLE/GL→report unbilled row→real billing finalization + draft SI/PI pair; cross-Company Company/role permission, duplicated claims, cancel/replay, multi-SLE, no-SLE, forged source and invoice refs, date-bound reporting and performance. Preserve source-to-GL non-additive reconciliation and issuer currency/UOM.
3. Obtain separate owner approval for the **exact target commit, pipeline flags, expected resource cost and manual hold** before any billable CircleCI execution. No automatic retry, site data update or deployment.
4. Only after real SQL passing evidence and business access review, separately request PR #28 merge and later controlled DEVELOPMENT testing. **PRODUCTION NO-GO.**

**Next report families remain:** Department material consumption, Equipment/Job Order material consumption completion, and overall Company-wide material vs GL/P&L reconciliation. Continue to use [active Handoff 2](CURRENT-HANDOFF-2.md).
