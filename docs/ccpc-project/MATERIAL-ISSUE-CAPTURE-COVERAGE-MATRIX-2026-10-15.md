# First Material Issue — SQL, Redis and callback capture-coverage matrix

**2026-10-15 — GitHub review branch only. NO-GO for a live rollback-only diagnostic or permanent posting.**

## Why this milestone matters

The previous exact-series offline model can reject an unexpected synthetic SQL statement, but cannot show that every real SQL/Redis/cache effect was observed. A trace showing **no Redis events** is not evidence that no Redis write happened if the interception missed its execution path. Similarly, claiming to have wrapped every intended entry point does not prove all lower-level driver or callback paths were covered.

The new pure-Python files, tests/offline/material_issue_capture_coverage.py and tests/offline/test_material_issue_capture_coverage.py, model this **missing-observation** hazard. They accept only typed hypothetical events and a declared set of candidate capture points. They return missing path claims and undeclared observed routes, but **always** set real capture coverage, child SQL scoping, Redis/cache containment, rollback-delta verification, rehearsal and commit readiness to false. They contain no ERPNext, SQL-driver, Redis, Docker, network or subprocess integration. The existing 14/14 exact-series model and earlier 19/19 blocker characterization are separate milestones.

## Candidate surface coverage (all remain unverified)

| Review surface | Reason to inspect | Unresolved proof gate |
| --- | --- | --- |
| Frappe query-builder run | Document child-table synchronization builds a DELETE using parent, parenttype, parentfield and an optional exclusion by existing child names | Confirm actual query rendering, bind values, target child set and zero deleted rows |
| frappe.db.sql and frappe.db.multisql | Naming-series writes, stock/ledger side tables and global-search SQL fallback | Trace all executed SQL and preserve exact statement plus binds; no broad table-only allowlist |
| Raw cursor execute and executemany | Alternative lower-level DB calls could bypass a high-level SQL wrapper | Prove physical driver coverage, call chain and transaction scope |
| Frappe cache lpush and raw Redis client | Global-search queue push can happen BEFORE SQL commit | Isolate or safely intercept all actual cache/Redis targets; SQL rollback alone is insufficient |
| Document cache invalidation | Document post-save clears cache before transaction completion | Trace actual keys and mutations, including lower-level Redis operations |
| Realtime and background enqueue | External dispatch cannot be undone by SQL rollback | Verify all relevant dispatch paths or fail closed |
| DB before/after commit and rollback callbacks | Registered callbacks may trigger SQL or external effects | Inventory registrations, execution order and failure handling |
| Document hooks and filesystem write | Application hooks and attachments may mutate beyond SQL | Review installed hooks and non-DB effects for the exact synthetic fixture |

The test module names 16 candidate surfaces. These are **review targets, not a proven exhaustive interception list**. A complete claimed list remains NO-GO until actual independently verifiable capture is designed. Raw Redis/client and raw SQL/cursor routes cannot be inferred safe from a high-level wrapper.

## Negative fixture tests

Sixteen credential-free unit tests passed in a local isolated source workspace. Cases include: zero observed events; all 16 capture points claimed without actual attestation; child DELETE with plausible parent/type/field binds; an unscoped Bin UPDATE WHERE 1; a precommit Redis global-search push; raw Redis outside a declared hook; raw SQL cursor outside query-builder observation; transaction callbacks without rollback-delta proof; incorrect site; missing or list-type SQL binds; unknown effects/phase; duplicate declarations; untyped event payloads; non-SQL event carrying SQL payload; and source AST inspection ensuring no runtime adapter.

**Interpretation:** 16/16 PASS characterizes reasons to refuse a live run. It does not validate Frappe instrumentation, DB/Redis isolation, data accuracy, zero-row SQL deltas, actual rollback or recoverability. This design deliberately cannot authorize a new diagnostic.

## Source and safety boundaries

- Custom app feature branch: ccpcerp/ccpcerp, feature/withdrawal-material-issue-safety, SHA 2f846a75dc7f1b9e6eb20bed38a1ae3433571ad6; app code unchanged.
- Pinned Frappe SHA: 988e54f3c4c291e2077a83809663f123731abe76.
- Verified Frappe source blobs: document.py e4cc2fbadba02605d6a30bdb5f853e35e60a9e5a; query_builder/utils.py 0b3a2f315346f9813717f8d201b9546989da2761; utils/global_search.py 174ee0479160223aa69bc5df3adb924a6afb9b6a; database/database.py a2ba78e2488f03810d58c43c768b4fbab624c3dc.
- Prior detailed design: MATERIAL-ISSUE-FIRST-COMMIT-EFFECT-BOUNDARY-DESIGN-2026-10-15.md on the same review branch.
- Previous one-run read-only metadata approvals are consumed. They do not allow reruns.

Before proposing any write-then-rollback exercise, independently prove capture completeness, isolate the actual DEVELOPMENT SQL/Redis/queues, resolve exact child DELETE and first naming-series DML, model all auxiliary stock/GL/Bin/Version/payment-ledger operations, and verify backup restorability and rollback with explicit abort conditions. Obtain separate owner approval for staging and for any future isolated DEVELOPMENT execution. Permanent posting and PRODUCTION require distinct approvals.

**Neither posting candidate was changed or staged. The review-only v2 must retain its unconditional early exit. No DEVELOPMENT pull, MariaDB/Redis activity, live Frappe execution, Docker operation, or PRODUCTION change occurred in this milestone.**
