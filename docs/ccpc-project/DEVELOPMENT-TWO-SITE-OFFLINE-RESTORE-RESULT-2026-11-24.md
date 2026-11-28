# CCPC ERPNext — DEVELOPMENT two-site offline restore rehearsal result

**Date:** 2026-11-24, Asia/Manila. **Scope:** isolated offline disposable QEMU guest, *not* live DEVELOPMENT or PRODUCTION. **Evidence:** operator-supplied sanitized guest-terminal results plus GitHub-verified pinned application/runtime source, latest rolling handoff, and the previously committed Nov23 two-site backup provenance. Never interpret this report as a PRODUCTION disaster-recovery certification or financial UAT.

## Outcome

**CORE DATABASE / APP CONNECTION / REGULAR ATTACHMENT RECOVERY: PASS FOR BOTH SITES (scoped).**

- Both Nov23 DEVELOPMENT backup sets (`development.localhost`, `ccpc-integration2.localhost`) were staged from a read-only backup ISO in the disposable QEMU clone. All **8/8** original four-component backup files had already passed source-to-protected NAS/ISO SHA256 verification, as documented in [CURRENT-HANDOFF-5](CURRENT-HANDOFF-5.md).
- The recovery clone ran with no network adapter (`-nic none`), only loopback visible in the guest, guest-local `/var/lib/ccpc-recovery-docker` Docker root and private MariaDB/Redis. No original source database credentials/configuration were reused. Distinct new recovery site and schema identities were used for each site; schedulers paused and maintenance enabled.
- First site **`ccpc-restore-dev-20261124.localhost`**, database `ccpc_restore_dev_20261124`: explicit native Frappe `bench restore` reported success; separate read-only pinned-image Frappe `frappe.init()/frappe.connect()` test succeeded, three apps installed, 759 base tables, 832 DocTypes and representative SQL record counts. Public files **0 archived / 0 restored**; private files **1 archived / 1 restored** with independent SHA256 match **PASS**.
- Second site **`ccpc-restore-int2-20261124.localhost`**, database `ccpc_restore_int2_20261124`: original native `bench restore` command's finish output was **not captured** because the guest terminal paste/echo was garbled, so do **not** claim the native success banner was observed. The target schema was confirmed absent before restore staging and present afterward; staged SQL/public/private inputs passed source-vs-staged byte comparison, gzip/TAR readability; subsequently read-only SQL confirmed **832 DocType rows**, exactly **3 Installed Application rows** with `ccpcerp,erpnext,frappe`, and apparent **759 base tables / 765 tables+views** in console-interleaved queries. The restored regular public/private file counts **0/0** each matched the archive regular-file counts **0/0** each. Critically, a separate **read-only pinned-image Frappe runtime command** `bench --site ccpc-restore-int2-20261124.localhost list-apps` successfully connected and returned:
  ```text
  frappe  16.33.1 version-16
  erpnext 16.34.2 version-16
  ccpcerp 0.0.1   HEAD
  ```
  A subsequent read-only `tabStock Ledger Entry` SQL count showed a **visible `1` embedded in interleaved terminal command echo**; this is provisionally treated as approximately one SLE and **not** independently clean count confirmation. No source-vs-restored record-count reconciliation was performed.
- The first site's separate representative query counts: `tabUser` **38**, `tabFile` **3**, `tabCompany` **25**, `tabItem` **42**, `tabSales Invoice` **1**, `tabGL Entry` **88**, `tabStock Ledger Entry` **69**. These values are recovery indicators only; do not disclose individual business rows.

## Acceptance matrix

| Gate | First DEVELOPMENT site | Integration2 |
| --- | --- | --- |
| Nov23 staged backup archive integrity | PASS | PASS |
| Unique guest-only site + DB identity | PASS | PASS |
| Recovered DB exists, queried successfully | PASS | PASS |
| Actual Frappe runtime DB connection | PASS | PASS via `bench list-apps` |
| Registered frappe, erpnext, ccpcerp | PASS | PASS |
| Restored DocTypes | 832 | 832 |
| Base tables | 759 | Approx. 759, console interleaved |
| Public archived / restored regular files | 0 / 0, PASS | 0 / 0, PASS |
| Private archived / restored regular files | 1 / 1, SHA256 PASS | 0 / 0, PASS |
| Representative business data indicators | PASS for selected counts | DocType and app records PASS, SLE count provisionally 1 |
| Native restore completion banner captured | YES | NO — console paste interrupted |

**Conclusion:** Both recoveries meet the *scoped* key outcome of usable restored Frappe database/application metadata and matching regular-file attachment counts in an isolated offline test. The first site's lone restored private file also passed a byte-level SHA256 comparison. Integration2's missing native command completion transcript is mitigated by the successful independent restored-site Frappe connection and metadata readback, but should remain an evidence limitation.

## Important exclusions / outstanding validation

1. **Encryption:** Neither archived `site_config_backup.json` included an `encryption_key`. Existing encrypted passwords/settings therefore **cannot be certified recoverable** from the tested backup sets. Develop a separate protected key backup/restore procedure, access permissions, test decryption, and key/credential rotation safeguards; never publish secrets to GitHub.
2. **Business transaction integrity:** No restored-site **submitted** Stock Entry, Sales Invoice/Purchase Invoice, GL reversal, intercompany billing, webhook/email, scheduler processing, authenticated browser login, user permission or stock balance reconciliation was attempted. Those are different acceptance gates and can alter the guest if later approved.
3. **Database exhaustiveness:** No row-by-row / financial-source-to-restore DB checksum or full-table count comparison; selected metadata and counts are not complete reconciliation. Integration2 table/SLE counts were partially obscured by terminal echo; do not treat as definitive exact audit values.
4. **Attachments:** Both Integration2 TAR regular-file counts were zero; source-vs-restored private/public file hashes were **not applicable**, and TAR entry-type completeness (symlinks/special files) was not independently exhaustively audited. First site public set was zero and private one-file SHA comparison passed.
5. **Operations:** No RTO/RPO benchmark, power interruption simulation during restore, browser/UI/service functional test, full backup retention/alerting review, offsite key validation or production cutover/rollback test. Recovery guest remained private, offline and disposable.
6. **Security/rollout:** No real DEVELOPMENT service restart, schema migration, app code switching or PRODUCTION action. Production requires separate explicit authorization, protected backups, rollback and access-security review. Both GitHub repositories currently showed public visibility as of Nov24; audit any exposed history/CI artifacts for secrets separately.

## Next authorized development critical path

1. Preserve this checkpoint and the clone/backup provenance without deleting or repeating restore.
2. Return to the **limited same-Company Phase 1** release, target **2026-12-17**, as documented in [Phase 1 readiness review](PHASE1-DEVELOPMENT-COMPLETION-READINESS-2026-11-24.md): main GitHub release candidate `release/withdrawal-department-phase1-2026-11-17` at `b0cbe5c...`, draft [PR #35](https://github.com/ccpcerp/ccpcerp/pull/35).
3. Resolve review/integration of **draft PR #42** maintenance-only Bearings guard (its synthetic 29 offline/static and 10 real MariaDB acceptance checks previously passed) and confirm business policy/signatures for actual CCPC Bearings → Repairs expense.
4. Perform **separately approved** persistent MAIN DEVELOPMENT acceptance with named Finance maker/checker and independent Stockroom issuer, signed exact Item Group→Expense Account and beneficiary Department→Cost Center maps, real Withdrawal → native submitted Material Issue → SLE/GL → Department report, cancellation/rollback/permission/replay. Preserve source worktree and fresh backups before any site writes/migrations.
5. Keep intercompany billing draft [PR #33](https://github.com/ccpcerp/ccpcerp/pull/33) **out of Phase 1** and disabled until separately reviewed.
6. Only after DEV UAT and production-access/credential/backup/rollback security gates, review PR #35 merge/release and request **separate explicit** PRODUCTION deployment approval.

## References

- [Current rolling handoff](CURRENT-HANDOFF-5.md)
- [Verified Nov24 Phase 1 development readiness](PHASE1-DEVELOPMENT-COMPLETION-READINESS-2026-11-24.md)
- [Original two-site restore VM plan](DEVELOPMENT-20261123-ISOLATED-RESTORE-VM-PLAN.md)
- [GitHub-first operating workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
