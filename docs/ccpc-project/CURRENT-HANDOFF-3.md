# CCPC ERPNext — CURRENT HANDOFF 3

**Active compact GitHub-first checkpoint, 2026-10-30 (Asia/Manila).** Start with [GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md); verify live GitHub state before further actions. [CURRENT-HANDOFF-2.md](CURRENT-HANDOFF-2.md) is preserved as the detailed historical checkpoint and **must not** be appended to further. Refer to linked technical records for evidence rather than repeating full transcripts.

## GitHub source of truth and approvals

- App: [ccpcerp/ccpcerp](https://github.com/ccpcerp/ccpcerp); deployment/docs: [ccpcerp/ccpc-frappe-deployment](https://github.com/ccpcerp/ccpc-frappe-deployment), active docs branch `docs/ccpc-checkpoint-2026-10-10`.
- Report candidate: [app PR #32](https://github.com/ccpcerp/ccpcerp/pull/32), **draft/unmerged**, review branch `review/four-day-one-reports-integration-2026-10-29`, exact head `061e65710eb4b527fc8ac579aaab8ccad4dd131d`. It combines four read-only reports. [Build #52](FOUR-REPORTS-PR32-CIRCLECI52-REAL-MARIADB-ACCEPTANCE-2026-10-29.md) completed **86/86 real installed-Frappe/MariaDB** cases on disposable CI only, **not** persistent DEV acceptance or a backup restore.
- Owner-approved latest scope: **plan** a secure encrypted one-time transfer of the **actual October 29 synthetic Integration2 four-part backup** into a separately isolated CircleCI restore rehearsal. The owner already approved the isolated rehearsal objective. **Not approved**: encrypted or plain backup data egress/upload, provider account/object creation, CI source/secret/context changes, paid/credit-consuming CircleCI job, any actual backup restoration, DEV code checkout/migration/Honcho stop/restart or business transaction writes. PRODUCTION is entirely **NO-GO**, and release/cutover requires a separate production-specific authorization.
- No automatic Codex reporting, scheduled source publishing, extra OpenAI API billing or generic repeat infrastructure preflights.

## Current DEVELOPMENT source and schema

- Shared DEVELOPMENT bench/app code on `ccpcerpserver`: last operator guard detached `HEAD=0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`, worktree status **only `?? AGENTS.md`**, a protected untracked file. Preserve it. Recheck exact state immediately before any authorized source change.
- Intended live DEVELOPMENT sites: **`development.localhost`** (real four-group Company configuration) and **`ccpc-integration2.localhost`** (intentionally synthetic TISS/TREQ Company fixture). They have distinct MariaDB databases but share app checkout/bench/services on the old server. Known broken `ccpc-integration.localhost` **excluded**.
- Prior read-only main DEV master checks: 4/4 Companies, 20/20 intercompany accounts, 4/4 internal Customers, 4/4 internal Suppliers, eight party header configurations and **24/24** child receivable/payable account mappings PASS. Synthetic site TISS/TREQ identities verified. These are not transactional invoicing/GL or real user-authorization acceptance; details in [PR32 read-only preflight](PR32-DEVELOPMENT-READ-ONLY-PREFLIGHT-2026-10-29.md).
- New PR32 integration compared to *installed* DEV SHA: **77 commits ahead, 0 behind, 62 changed files**, not just four reports; five Finance lifecycle DocTypes and two existing Revision DocType extensions require schema sync. The owner's two-site read-only inventory found **0/5 of those five new DocTypes** present in either database; that is expected for the old app. GitHub comparison shows `ccpcerp/hooks.py`, `ccpcerp/setup.py`, `ccpcerp/patches.txt` **unchanged** across these two exact app commits, but migrating two sites can still write schema, metadata and setup effects. No site migration has been authorized.

## Recovery protection as of October 30, 2026

- Two October 29, 2026 **local four-part** backups were created via Frappe `BackupGenerator` into separate private directories outside `sites/`, preserving older October 27 backup sets. Each full database gzip, site config JSON, public and private TAR passed readability checks.
- **Integration2** local directory: `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e`; host-mapped `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots/...`. Operator read-only size: **`du -sh = 1.1M`**. **Main** local directory: `/workspace/development/frappe-bench/.ccpc-pr32-snapshots/development.localhost-20261029T134505Z-f9d195ea`.
- **Both site backups copied to Synology**, matching **8/8 source/destination SHA256** plus `SHA256SUMS` manifest and final publication on `//192.168.50.132/erpnext_backups` at `/mnt/erpnext_backups/ccpc-development-pr32-20261029T234223Z-f38259861f97ed80`. Existing PRODUCTION backup tree and scripts were untouched. A separate empty failed staging directory `.partial-ccpc-development-pr32-7895c72462f41cae` was preserved, not deleted.
- Synology DSM screenshots: `erpnext_backups` local group `administrators` Read/Write, default `users`, `http`, `Maintenance` No Access, `guest` No Access; three Read/Write local accounts are owner-controlled administrator identities and fourth is designated backup service account. CIFS client `0755` is not definitive NAS ACL evidence; no permission change required for reviewed copy.
- **Recovery still NOT independently restored.** Archive/HMAC? No: **SHA256 copying** proves byte identity only. Not a proven atomic DB/files snapshot, immutable backup, geographically separate disaster domain or recovered ERPNext site. Do not falsely claim rollback can be performed just by switching Git SHA.

## Current priority — encrypted CircleCI restore candidate

[**New one-time encrypted CircleCI transfer specification**](PR32-INTEGRATION2-CIRCLECI-ENCRYPTED-TRANSFER-DESIGN-2026-10-30.md) is **design-only** and based on confirmed [CircleCI config](https://github.com/ccpcerp/ccpcerp/blob/061e65710eb4b527fc8ac579aaab8ccad4dd131d/.circleci/config.yml) and [existing combined test job](https://github.com/ccpcerp/ccpcerp/blob/061e65710eb4b527fc8ac579aaab8ccad4dd131d/.circleci/four_reports_stage.sh). It proposes:

1. Preserve exact original Integration2 snapshot; encrypt a streamed four-artifact plus SHA256 manifest `tar` into **age ciphertext** with new, single-use X25519 recipient generated on trusted owner-controlled device. Local decrypt-verify, no plaintext upload and no ciphertext committed to Git or CircleCI artifacts.
2. Use an **already available owner-controlled private temporary object store** if one is confirmed; one random object, least-privilege short-lived read URL/credential, deletion and verification. **No existing S3/R2/other object store has been established**. Don't create a paid service by assumption. Its bearer URL and the age private identity must be protected in a **new restricted CircleCI context**, never in config/pipeline parameters, and expression must deny `job.ssh.enabled`.
3. Prepare a **separate manual/default-OFF CircleCI restore job** in a new reviewed GitHub app branch. Use exact reviewed CI script source identity but install the CCPC app **at original backup SHA `0c223d7...`**, not PR32 schema. Distinct disposable sidecar MariaDB/Redis/site `ci-integration2-restore.localhost`, strict no legacy DEV/PROD credentials/mounts, no outbound email/hooks, no data artifacts or secret logs.
4. Run only upon **separate exact-scope owner approval** for confidential data egress, new context/storage, GitHub CI code creation and one bounded CI-credit run. Verify actual four-file import, unique database, two synthetic Companies, app/patch metadata, and representative public/private attachments. Record any missing fixture files honestly. Delete/revoke temporary data/key after authorized completion.

**Provider reality:** CircleCI's pipeline parameters are not secret and current CircleCI context docs allow restrictions by project, branch and `not job.ssh.enabled`. Secrets masking does not secure artifacts, redirected logs or SSH debug. Existing Build #52 tests are not proof of actual archived-backup recovery.

## Immediate decision and next meaningful steps

**Next decision:** Identify whether the owner already has a private temporary object-storage provider with controlled access (S3/R2/equivalent) **without paid provisioning**; this is the only essential external dependency before specifying executable upload steps. **If none**, compare a secure user-owned disposable VM alternative rather than making new paid infrastructure mandatory.

After the provider and approval: implement reviewed CI code + no-secret source guard, perform local encryption/source verification, separately approve/upload into the private temporary object, configure restricted CI context and approve **one** CI run. Later, if actual restore passes, request separate approval for coordinated **DEVELOPMENT-only** exact-SHA app switch, migrations on both sites, service smoke and actual four-report acceptance. **PRODUCTION NO-GO**.

## Key technical references

- [PR32 two-site read-only preflight and backup/NAS/schema evidence](PR32-DEVELOPMENT-READ-ONLY-PREFLIGHT-2026-10-29.md)
- [Integration2 isolated restore/recovery gate](PR32-INTEGRATION2-ISOLATED-RESTORE-REHEARSAL-PLAN-2026-10-30.md)
- [Secure CircleCI encrypted transfer spec](PR32-INTEGRATION2-CIRCLECI-ENCRYPTED-TRANSFER-DESIGN-2026-10-30.md)
- [Controlled DEVELOPMENT integration](DEVELOPMENT-CONTROLLED-INTEGRATION-PLAN.md)
- [CircleCI 86/86 acceptance record](FOUR-REPORTS-PR32-CIRCLECI52-REAL-MARIADB-ACCEPTANCE-2026-10-29.md)
- [Legacy Synology recovery design](recovery.md)
- [Shared-host DEV/PROD infrastructure](DOCKER-DEV-PROD-ARCHITECTURE.md)
