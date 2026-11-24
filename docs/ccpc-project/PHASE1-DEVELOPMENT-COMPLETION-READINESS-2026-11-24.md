# CCPC ERPNext — Phase 1 development-completion assessment (2026-11-24)

**Evidence type:** GitHub source, open PR states and branch heads, verified GitHub Actions run metadata, plus operator-reported isolated guest restore tests recorded in the current handoff. This is not a live production or main DEVELOPMENT host inspection, nor a signoff for deployment. Read alongside [CURRENT-HANDOFF-5](CURRENT-HANDOFF-5.md) and [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).

## Scope and target

The **limited, same-Company Phase 1** target in [app PR #35](https://github.com/ccpcerp/ccpcerp/pull/35) is **2026-12-17**, expressly conditional on real DEVELOPMENT acceptance, named Finance/Stockroom users, verified backup and restore, security, rollback and separately approved PRODUCTION deployment. On 2026-11-24 this is 23 calendar days away. This is **not** a date for completing every ERPNext function or custom intercompany billing.

## Verified GitHub status as of November 24

| Workstream | Most recent evidence | Status / remaining release gate |
| --- | --- | --- |
| Phase 1 CCPC application code | `ccpcerp/ccpcerp` release branch `release/withdrawal-department-phase1-2026-11-17` HEAD `b0cbe5c13cb68499a7920de2879f65e72cff000a`. [Draft PR #35](https://github.com/ccpcerp/ccpcerp/pull/35) against Finance branch `a2f0e89f...`, 31 changed files according to current PR file listing. | Implemented review candidate: same-Company Withdrawal to genuine ERPNext Material Issue/SLE/GL and Department report; intercompany-billing batch mutations disabled. PR **open/draft/unmerged** and final release/integration review remains pending. |
| App disposable real-DB tests | [Merged PR #41](https://github.com/ccpcerp/ccpcerp/pull/41) into `b0cbe5c...`; [Actions #44888315575](https://github.com/ccpcerp/ccpcerp/actions/runs/44888315575) **success** on exact test SHA `45c4683...`, covering HTTP/CSRF fault-after-ledger rollback/retry/replay and cancellation/reissue report tests. Finance UI Playwright synthetic 4/4 PASS as described in PR #35. | Targeted synthetic integrated evidence **PASS**; no full current-branch, named-user persistent MAIN DEVELOPMENT UAT or complete accounting release signoff. |
| Maintenance-only Bearings expense guard | Separate [Draft PR #42](https://github.com/ccpcerp/ccpcerp/pull/42) branch `feature/phase1-maintenance-only-2026-11-21`, HEAD `3fa7c6c...`. [Actions #44884746256](https://github.com/ccpcerp/ccpcerp/actions/runs/44884746256) **success** at `33e2729...`; PR records 29 offline/static and 10 real MariaDB cases including concurrency/rollback/cancellation. | Technically tested, but **draft, unmerged**, and not automatically in PR #35; real CCPC Bearings→Repairs Expense mapping still unsigned; pilot capital/other-use exception policy and integration into release need owner review. |
| Live MAIN DEVELOPMENT source | Operator-reported guarded source-only update on 2026-11-22 to exact `b0cbe5c...`, logged and GitHub-referenced in [handoff](CURRENT-HANDOFF-5.md). | Source synchronized; **does not prove current live service, schema, role setup, successful transaction UAT or migration**. No live financial posting acceptance reported. |
| Two-site backup + isolated restore | Nov23 four-part NAS backup of each of `development.localhost` and `ccpc-integration2.localhost`, 8/8 SHA256 PASS, guest readonly ISO SHA PASS. In disposable no-NIC QEMU clone, first DEVELOPMENT site native SQL+both archives restore PASS, real Python/Frappe DB connection PASS, all three apps, 759 tables, representative record counts. Public archive/restored files 0/0; private archive/restored count 1/1, correct TAR layout. | **One of two sites** restored+DB validated; private file SHA256 comparison still pending. Second site **not yet restored**. Encrypted-value recovery not certified: neither backed-up site_config includes an `encryption_key`. |
| Finance mappings and user UAT | [PR #35](https://github.com/ccpcerp/ccpcerp/pull/35) and [PR #42](https://github.com/ccpcerp/ccpcerp/pull/42) require independent named Finance Preparer/Checker effective roles and Company permissions, signed exact Item Group→Expense and beneficiary Department→Cost Center mappings, and separate Stockroom issuer. | **BLOCKED/PENDING business signoff and real MAIN DEVELOPMENT positive+negative UAT**, including replay, cancellation and report/GL reconciliation. Do not infer real Company signoff from synthetic fixtures. |
| Intercompany CCPC↔Ricor billing | Separate [Draft PR #33](https://github.com/ccpcerp/ccpcerp/pull/33) remains open; its active billing logic conflicts with the authorized Phase 1 billing-disabled boundary. | **Deferred from Phase 1**, not a release blocker if kept disabled and tested. Full project completion includes later independent review/integration. |
| Production readiness | [Deployment PR #37](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/37) and production-security/recovery review PRs remain draft; PR #35 requires verified secure access, fresh independent backup/restore, rollback and separate owner authorization. | **NOT READY/NOT APPROVED FOR DEPLOYMENT** based on GitHub evidence. No assumption that source sync modifies PRODUCTION. |
| GitHub confidentiality | Connected GitHub repository metadata on 2026-11-24 reports **public** visibility for both `ccpcerp/ccpcerp` and `ccpcerp/ccpc-frappe-deployment`; PR #42 documents this owner-chosen visibility and a deferred historical secret review. | Treat as a **security audit item**: verify tracked history and Actions/artifacts contain no credentials or real business backups, rotate any found exposed keys; publication alone is not proof that secrets were exposed. |

## Practical completion assessment

- **Code/proof-of-concept** for the limited Phase 1 is well advanced with authentic disposable MariaDB tests; the 2026-12-17 target remains **possible but unconfirmed**, because critical human/UAT/release/production gates do not yet have completed evidence.
- **Not a numerical percentage:** no agreed feature-weighted completion baseline or complete business-process acceptance matrix has been verified. Any precise "X% complete" would be subjective; it would confuse source implemented, tested, running in DEVELOPMENT, signed off, merged and deployed.
- **Overall CCPC ERPNext completion extends beyond Phase 1**. Deferred intercompany billing, additional reporting/integration work, full business masters/operations acceptance and production cutover require their own gates. Earlier framework `roadmap.md` last updated Oct12 is historical; newer handoff and active PR branches supersede it.

## Recommended fastest safe critical path

1. Finish DEVELOPMENT private attachment SHA256; restore + read-only audit Integration2 in the already prepared **offline disposable** QEMU recovery clone (no new host install/VM baseline). Record pass/partial limitations.
2. Review and integrate the **PR #42 maintenance-only safeguard** into the Phase 1 candidate only after exact base/diff, accounting/use-policy and proper regression checks. Keep PR #33 billing disabled/out of Phase 1.
3. Review live MAIN DEVELOPMENT worktree/site state separately; preserve the verified backup and avoid unreviewed pull/migrate. Validate current deployment/roles/patches without assuming VM data equals live DEV.
4. Obtain the real finance owners' signed Item Group→Expense and Department→Cost Center mapping and distinct authorized Stockroom issuer; execute **one scoped MAIN DEVELOPMENT Phase 1 positive and negative UAT** with exact Company/ledger/report readback, cancellation/rollback and role/CSRF checks, under separately approved business-data/test-transaction plan.
5. Resolve PR #35 review and integration, record audited implementation/test SHA and any remaining exclusions.
6. Run separate PRODUCTION readiness review (secure LAN HTTPS/access, backups/restore, isolation, rollback, host configuration and secret/public-history scanning), then request an explicit deployment decision. No automatic merge, database migration or PRODUCTION operation follows from this assessment.

## Source references

- [App Phase 1 release PR #35](https://github.com/ccpcerp/ccpcerp/pull/35)
- [Maintenance-only PR #42](https://github.com/ccpcerp/ccpcerp/pull/42)
- [PR #41 merged test+integration workflow](https://github.com/ccpcerp/ccpcerp/pull/41)
- [Billing-draft PR #33](https://github.com/ccpcerp/ccpcerp/pull/33)
- [Deployment acceptance PR #37](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/37)
- [Latest operator-reported recovery handoff](CURRENT-HANDOFF-5.md)
