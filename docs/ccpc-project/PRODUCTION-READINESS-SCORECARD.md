# CCPC ERPNext — evidence-based PRODUCTION readiness scorecard

**Baseline:** 2026-11-17, Asia/Manila. **Overall estimate: approximately 40% (reasonable uncertainty ±10 percentage points).** **Decision: NO-GO for PRODUCTION.**

This score is a **planning estimate**, not a tested release-readiness certification or percentage of code lines written. It reflects the complete frozen target in [PRODUCTION-READINESS-CRITICAL-PATH-2026-10-28.md](PRODUCTION-READINESS-CRITICAL-PATH-2026-10-28.md) as amended by the latest [CURRENT-HANDOFF-4.md](CURRENT-HANDOFF-4.md) and owner-supplied results. The Oct 28 critical-path review explicitly warns against measuring progress from disconnected source/mocked test counts. The owner requested occasional overall estimates; use this **fixed rubric with clear evidence and uncertainty** at significant milestones, not on every minor commit. Recalibrate the estimate only after evidence supports progress. GitHub records do not independently prove current physical host/database state.

## Fixed scoring rubric (100 total points)

| Release gate | Weight | Credited | Evidence and reason it is not complete |
| --- | ---: | ---: | --- |
| **A. Integrated custom application & security controls** | 25 | **17** | App source and substantial role, access, source, transaction, report and regression safeguards exist on review branches. PR #33 and stacked PR #34 are **draft/unmerged**; full current combined app release review, migrations and critical security acceptance pending. |
| **B. Correct end-to-end financial stock/billing/accounting path** | 25 | **10** | Prior genuine isolated Finance/Withdrawal/GL/billing tests (e.g., 12/12 CircleCI #34 on earlier source), and MAIN DEV approved batch + two real reciprocal Draft SI/PI with read-only audits. **Ricor PI uses wrong native 2301 stock-clearing account instead of intended 5150 expense**. No approved historical correction, native submitted SI/PI reconciliation, failure/replay concurrency and accounting cutover. |
| **C. Genuine integrated tests and four reconciled day-one reports** | 20 | **5** | Partial real MariaDB acceptance and report components exist but **no final-source integrated four-report and end-to-end reconciliation signoff**; no hosted CircleCI result for current PR #34's three new SQL fixture tests. |
| **D. Persistent DEVELOPMENT acceptance, roles and recovery** | 15 | **6** | Prior DEVELOPMENT site and rollback/read-only evidence plus verified *pre-Draft* backups. Existing Drafts were owner-reported preserved. Missing real Ricor mapping actors, signed mappings, source issue-time beneficiary provenance, authenticated UAT, and **new post-Draft** local+Synology verified restore point. Shared-host/broken third-site service restrictions remain. |
| **E. Dedicated PRODUCTION infrastructure, TLS, backup restore, rollback and approval** | 15 | **2** | Separate new host and GitHub deployment designs partially prepared. Dedicated live ERPNext/LAN HTTPS, Compose semantic acceptance, credential isolation, native restore rehearsal/cutover and explicit owner release signoff **not verified**. Existing OLD and NEW PRODUCTION remain protected. |
| **Total** | **100** | **40** | **Approximate 40%; PRODUCTION NO-GO** |

**Uncertainty:** approximately 30–50% is defensible given unverified site/CI current state and uneven workstream integration. The numeric values are an engineering planning judgment, not a mechanically audited certification, an ETA, or proof that 40% of production transactions work.

## What changes the score

1. **Current immediate gate:** run *one* guarded disposable CircleCI PR #34 acceptance at its exact GitHub SHA, after official config parser/branch/site/role guards and manual approval; capture all 3 native SQL test results and failures. Only then credit tested native Ricor PI Item/expense behavior. Source checks or a queued CI workflow alone **do not raise the score**.
2. Finish the original-batch Draft Ricor PI accounting correction **design and code**, then verify real history-provenance policy and authentic named distinct Ricor mapping approvals. A synthetic `@testing.invalid` User is not genuine Finance signoff. Existing historical invoice dates must not be backdated to counterfeit mapping effectivity.
3. Verify protected fresh **post-Draft** backup/restore point, run safe exact-source DEVELOPMENT acceptance and reconcile actual invoice links, Company balances, SLE/GL, rights, rollback/replay and four day-one reports. Code merge only after reviews and gates.
4. Complete dedicated PRODUCTION Compose/TLS/credentials/backup/restore/rollback rehearsal and obtain **separate explicit owner deployment authorization**. No default assumption that moving GitHub branches changes PRODUCTION.

## Current immutable evidence pointers (reverify branch heads before operations)

- App draft [PR #33](https://github.com/ccpcerp/ccpcerp/pull/33) and stacked draft [PR #34](https://github.com/ccpcerp/ccpcerp/pull/34). Last verified PR #34 commit **`4744577c86f5ba8d6e7e148ca5cb84d0da7857f7`** (explicit `Company` fixture prerequisite added for disposable mapping-user test); hosted CI for PR34 not observed at this checkpoint.
- Documentation draft [PR #37](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/37) contains active CURRENT-HANDOFF-4. Existing Draft SI `ACC-SINV-2026-00001` / PI `ACC-PINV-2026-00005` and original material `ITEM-00010` must not be mutated by source-only work.
- Legacy Oct 28 [PRODUCTION-READINESS-CRITICAL-PATH-2026-10-28.md](PRODUCTION-READINESS-CRITICAL-PATH-2026-10-28.md) documents a NO-GO state and explicit complete frozen business target. Do not re-open previously settled Item Group/CoA choices or automatic Codex reporting.
- **Update policy:** On each substantive integrated CI PASS, genuinely signed mapping gate, verified full DEVELOPMENT acceptance, report reconciliation, or production recovery milestone, re-score this table; report date, source SHA, evidence, new % and blockers. Minor commits/offline checks do not automatically earn points.

**Operational boundary:** All app changes GitHub-first; MAIN DEVELOPMENT persistent changes only with exact source/worktree review and site-specific backups; OLD and NEW PRODUCTION only under separate explicit approval. No scheduled CI, autonomous publishing, cost-bearing run or auto-retry implied by this scorecard.
