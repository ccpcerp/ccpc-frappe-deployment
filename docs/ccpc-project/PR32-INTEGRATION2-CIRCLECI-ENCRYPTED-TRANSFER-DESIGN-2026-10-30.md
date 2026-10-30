# Integration2 backup — proposed one-time encrypted ingress to CircleCI for isolated restore

**Status: DESIGN REVIEW ONLY — NOT DEPLOYED / NOT TRANSFERRED / NOT TESTED**  
**Date:** 2026-10-30 (Asia/Manila)  
**Authorization:** The owner approved **preparing this secure, temporary, encrypted transfer design** as a follow-up to approval for an isolated Integration2 restore rehearsal. It does **not** approve uploading confidential backup data, procuring/enabling any paid services, generating live CI secrets/contexts, executing CircleCI, changing the app's CI source, or restoring/altering any site.

Read with [Integration2 isolated restore plan](PR32-INTEGRATION2-ISOLATED-RESTORE-REHEARSAL-PLAN-2026-10-30.md), [active handoff](CURRENT-HANDOFF-2.md), and [GitHub-first workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md).

## 1. Validated inputs and limits

- Integration2 four-artifact local backup: `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e`. Operator's read-only `du -sh` printed **1.1M** (rounded). The site's synthetic TISS/TREQ Companies do **not prove** every table, user/secret or attachment is fictitious.
- Original app commit at backup: `ccpcerp/ccpcerp@0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`; Frappe `988e54f3c4c291e2077a83809663f123731abe76` and ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`. **Restore before any PR #32 schema upgrade.**
- NAS mirror directory `/mnt/erpnext_backups/ccpc-development-pr32-20261029T234223Z-f38259861f97ed80` on verified `//192.168.50.132/erpnext_backups cifs`. User reported **8/8 source–destination SHA256** and published `SHA256SUMS`, covering both sites; preserve the original local and NAS copies.
- GitHub app PR #32 draft/unmerged at `061e65710eb4b527fc8ac579aaab8ccad4dd131d`. Existing CircleCI job `four-reports-isolated-integration`, at this head, previously passed 86/86 synthetic native Frappe/MariaDB tests. It has a pinned Frappe/ERPNext installation recipe, sidecar MariaDB 11.8 and Redis, `large` resource class, **but no restore-ingress workflow**. DO NOT insert the backup into or relax this already-green job.
- Planned CircleCI target: **new** manually approved default-off `integration2-backup-restore` job and `ci-integration2-restore.localhost` disposable site in a *separate reviewed app branch* derived from existing tested CI source, with **test app code independently checked out at the original backup SHA**. No CI code/branch has been created under this approval; final branch/job names and exact HEAD must be verified before implementation.
- CI provider can access neither the host-only local backup path nor Synology SMB directly. No connected cloud object storage, restricted CircleCI context, upload endpoint, tool binary, or provider spending commitment has been verified; do not invent these prerequisites.

## 2. Selected design: authenticated client-side encryption + one-time private object

**Cryptography**: use the official, provenance-verified `age` file encryption tool and a **fresh, rehearsal-only age X25519 recipient/identity pair** generated on an owner-controlled trusted device (not in the production Docker container). Protect the private identity with local filesystem protections and a human-controlled encrypted recovery copy. Never reuse the existing NAS, SSH, ERPNext, MariaDB or CircleCI credentials as encryption keys. Public recipient is nonsecret; private identity is secret. Before using a binary, verify publisher, version and checksum/signature using official upstream release sources.

**Packaging**: the exact four Integration2 components **plus a manifest of source file SHA256 and sizes** are streamed into one tar archive and then directly into age encryption **before any network upload**, yielding one opaque ciphertext file with a random run ID and a `.tar.age` suffix. Avoid an unencrypted tar staging file; preserve originals. Perform **local decrypt-verify round-trip** to restricted memory/scratch without exposing its contents and compare each component hash to its unmodified source. A SHA256 of the ciphertext itself is a public-safe transport check; keep the internal plaintext manifest inside encryption. Require 4/4 named components, source-site prefix, gzip and public/private TAR/JSON validity without logging data.

**Transfer**: choose an **already available**, owner-controlled private object store supporting an individually addressable short-lived object with restricted write, one-run read and deletion. Generic compatible provider example: private Amazon S3-style object with a narrowly scoped **short-expiry HTTPS presigned GET** for the ciphertext. *No S3 account/bucket is known to exist; do not create or bill one automatically.* The upload must use an exclusive random object key and fail on collision; no public read ACL or anonymous bucket listing. A presigned URL is a **bearer credential even when the object is encrypted**: keep it secret, preferably only in a dedicated CircleCI context, not in Git, issue titles, pipeline parameters, command arguments visible in process listings, terminal screenshots or logs. Expiration limits use but **does not guarantee one-time consumption or object deletion**. Set a finite object-retention deadline, then verify deletion/version lifecycle if applicable. Explicitly verify the provider's IAM/ACL version behavior before choosing commands; no automatic retention policy affecting existing objects.

**CircleCI secret custody**: create a **new one-purpose restricted context** only upon the next explicit authorization, with e.g. `CCPC_RESTORE_AGE_IDENTITY` and `CCPC_RESTORE_OBJECT_GET_URL`. Store neither in repository YAML nor any branch commit. Context must be restricted to the exact intended project, owner-approved security group (NOT default `All members`), and an expression bound to the exact approved restore branch and **`not job.ssh.enabled`**. CircleCI expression restriction syntax should be verified against the organization's pipeline type, for instance:
```text
pipeline.git.repo_name == "ccpcerp"
and pipeline.git.branch == "<exact approved restore branch>"
and not job.ssh.enabled
```
`<exact approved restore branch>` is a **design placeholder**, not an approved literal branch. If any pipeline field is missing/ambiguous, fail closed rather than widening the context. CircleCI secrets masking is **not a full DLP control**; users who can edit CI code/approve jobs or access debugging may access secrets. Restrict source changes and human approvals accordingly. Use a one-run key and revoke/delete context variables after evidence capture, remembering that earlier logs/retained artifacts cannot be recalled by key deletion.

## 3. New CI workflow security gates (DESIGN — no CI YAML changed)

- **Default-OFF boolean** `run_integration2_restore`; distinct explicit manual approval hold and exact branch/job/HEAD/source-identity guard, no PR labels, schedules, generic `run-ci` trigger or auto-pipeline. Never embed archive data, URL or key in **pipeline parameters** (not secret, max 512 characters per parameter).
- Test only `ci-integration2-restore.localhost`, unique non-PROD database and disposable MariaDB/Redis sidecars; reject `development.localhost`, `ccpc-integration2.localhost`, `ccpcerp.local` and legacy/new PRODUCTION hosts as restore target identifiers. Job must have **no shared host Docker socket, site bind mount, Synology mount, CCPC server SSH material or live DB access**. Use the existing CircleCI installation path but checkout installed app at original SHA `0c223d7...`, separate from the review CI-script SHA.
- Authenticate retrieval via dedicated restricted secret, require TLS and exact trusted private object hostname/path prefix, bounded size/timeout and **ciphertext SHA256** before decrypt. Do not use unrestricted redirects or log the presigned URL. Decrypt to a `0700` scratch folder within job, no root/public shell history, no `set -x` or `echo` of credentials; validate internal four-file manifest. No `store_artifacts`, `store_test_results`, `save_cache`, `persist_to_workspace` or `save` of restored SQL, config, private files, runtime environment, decrypted payload, or job secrets.
- Build pinned Frappe/ERPNext and exact old CCPC app. Create a **unique disposable site/database user** using CI-only credentials, verify its DB is on CI's local sidecar and absent before import. **Important destructive semantics:** Frappe v16's `bench restore` implementation invokes `_new_site(..., force=True)`, so do not use it on shared DEV or a preexisting database. Treat original `site_config` as untrusted: DO NOT use its live db_host/db_name/db_password/db_user; carry only strictly necessary cryptographic keys into disposable site config securely. Review and suppress external email, webhook, scheduler, workers and external integration side effects. Frappe may need Internet to install dependencies; do not claim total network egress isolation without a separately tested constraint.
- Positive checks must cover SQL import, Frappe boot and login with **CI-only** admin account, installed-app & patch identity, **two TISS/TREQ** Company records, representative expected synthetic records, one public and one authorization-scoped private attachment if such files exist (report absence, do not invent), and **no mutation of actual project data**. Do not upgrade into PR32 migration as part of this initial restore proof.
- Print a **small, sanitized outcome matrix**: source SHA, Frappe/ERPNext SHA, restored site identity, backup component/hash PASS, DB read PASS, files PASS/NOT APPLICABLE, authentication PASS, external effects disabled, and remaining limitations. No raw financial/company records, site config, full SQL/error dumps, URLs, password, encryption identity or attachment names. Stop on first security or integrity failure, preserve sensitive data only within transient CI sandbox for the run, and make provider-side retention/deletion explicit.

## 4. Threats, stop conditions and approval gates

| Threat | Required mitigation / STOP |
| --- | --- |
| Accidental GitHub or CI disclosure | Never check in or upload plaintext dumps/keys. Prevent CI logs, artifacts, cache, workspace and PR debug from containing any restored data. STOP if restricted-context or SSH-block cannot be configured. |
| CI script compromise / untrusted PR | Separate protected reviewed branch, exact SHA at runtime, no fork PR access to context, one authorized manual approval; CI job with decryption capability must be treated as trusted code. |
| Temporary-object exposure | Encrypt before upload; private store, least-privilege object key, time-limited bearer link, ciphertext checksum. STOP if store absent or requires public access. |
| Key and URL leakage | Dedicated context restricted by project/group/branch/SSH; short-lived key; no command tracing; delete object/revoke credentials after test. |
| Production/DEVELOPMENT damage | No original site/database/credentials/SSH/NAS mounts in CI, no shared Docker; Frappe destructive restore guarded to new disposable DB and exact site only. |
| Actual records and encryption | Synthetic Company labels do not prove sensitive-free; record an explicit owner data-egress decision and secure handling of original encryption key. |
| Billing and provider quotas | Separate owner-approved one-run execution with bounded resource/credit budget; no automation or future runs. |
| Incomplete restore proof | All 4 original components imported/read on disposable site, no silent synthetic substitute; report missing files/records and uncertain consistency as such. |

**Owners' decisions required only at a meaningful gate**: (a) identify a pre-existing private temporary-object provider and approve its specific confidential-data transfer route and retention; (b) separately authorize code implementation of the reviewed CI job/new restricted context and 1 paid/credit-consuming run after actual price/account allowance is checked. Either (a) or (b) can be declined without affecting local+NAS recovery sets. If no safe temporary-object provider is available without paid service setup, prefer an owner-controlled disposable VM; do not put even encrypted backups in a repository commit or CircleCI artifacts to bypass the missing transfer channel.

## 5. Verified references

- CCPC [PR #32](https://github.com/ccpcerp/ccpcerp/pull/32), `.circleci/config.yml`, `.circleci/four_reports_stage.sh`, and `ccpcerp/ccpc_erp/ci_four_reports_site_guard.py` at app SHA `061e65710eb4b527fc8ac579aaab8ccad4dd131d`.
- [CircleCI Using contexts](https://circleci.com/docs/guides/server/security/contexts/): restricted contexts, `not job.ssh.enabled`, secrets masking caveats, and 32k environment value limit.
- [CircleCI pipeline values and parameters](https://circleci.com/docs/guides/orchestrate/pipeline-variables/): pipeline parameters are NOT secret; API max 512-character value.
- [CircleCI 2026 context expression examples](https://support.circleci.com/en/articles/16968400-pipeline-values-you-can-use-in-context-expression-restrictions): repo/branch/SSH gating and fail-closed restrictions.
- [age encryption official reference](https://pkg.go.dev/filippo.io/age): per-purpose encryption keys, explicit authenticated file encryption and identity custody.
- [Amazon S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html): temporary **bearer** URLs can be reused until expiry; one-time upload/download cannot be assumed.

**Current outcome:** Design ready for separate implementation/security review. **No cloud resource created, no GitHub app/CI code changed, no CircleCI context/key configured, no credential generated, no encrypted/plaintext backup moved beyond the existing local/NAS copies, no CI credits consumed, no site/DB/process modified, no restore executed. PRODUCTION remains NO-GO.**

## 6. Free/private object-store research and recommended candidate (2026-10-30)

**Owner confirmed they have no existing S3/R2/private object storage and requested a genuinely free or very cheap provider for this 1.1 MB disposable Integration2 rehearsal.** No provider signup or resource creation is authorized yet. Official current pricing/feature documentation checked as follows:

| Provider | Relevant official free plan and setup | Tradeoff / decision |
| --- | --- | --- |
| **Backblaze B2** | First **10 GB** of storage free, free Class A/B/C API operations on pay-as-you-go, and up to **3× average-monthly-storage egress** free; beyond included egress **$0.01/GB** (US dollar; regional/taxes/account conditions may vary). [Official pricing](https://www.backblaze.com/cloud-storage/pricing), [official signup](https://www.backblaze.com/sign-up/cloud-storage) specifically advertises **no credit card required**. [S3-compatible API](https://www.backblaze.com/docs/cloud-storage-s3-compatible-api) supports **private bucket** and **presigned upload/download URLs**. [Standard app keys](https://www.backblaze.com/docs/cloud-storage-application-keys) can be restricted to bucket/file prefix and made expiring. | **Preferred first candidate** for 1.1 MB encrypted one-time object, no compulsory payment method for initial free setup per vendor signup. No charge expected for storage under included 10GB; tiny download generally free or de minimis. Need actual account/region/quotas and presigned-URL test before uploading secrets. |
| Cloudflare R2 Standard | **10 GB-month/month**, 1M Class A and 10M Class B monthly free, no egress charges. [Pricing](https://developers.cloudflare.com/r2/pricing/). [Setup](https://developers.cloudflare.com/r2/get-started/) requires R2 subscription checkout, potentially payment/billing profile. | Technically excellent, but unwanted billing/subscription setup for 1 MB single use. |
| Google Drive personal | Small ciphertext would fit normal free storage, but [official download API](https://developers.google.com/workspace/drive/api/guides/manage-downloads) requires OAuth-authorized media retrieval when file stays private. | Avoid fresh Drive OAuth/service-account grants and broad Drive scopes just to deliver one CI file; a public anonymous link would weaken the private-URL requirement, even though data is client-encrypted. |

**Backblaze-specific safety and implementation amendments (still design-only):**

1. Use **one dedicated private B2 bucket**, new opaque file name/prefix, and **scoped temporary application key** rather than a master key. Keep object and bucket names free of business/identity details. Do not share the master key, account password or actual presigned URL in chat/GitHub/logs.
2. Locally encrypt using the fresh `age` public recipient before upload, then verify ciphertext hash, and generate a **very short-expiry presigned GET URL** into a new restricted CircleCI context. The URL grants temporary bearer access and may be reused during its validity; do not describe it as strictly single-use or cryptographically revoked merely because CircleCI downloaded once.
3. **Versioned objects are an important cleanup risk:** B2 buckets are versioned by default, and deleting an object name can leave older versions recoverable. After the CI test, revoke the temporary app key and URL and **inspect/delete every stored ciphertext version using the provider's supported version-aware delete operation**, or plan reviewed lifecycle expiry. [Version behavior](https://www.backblaze.com/docs/cloud-storage-s3-compatible-api-bucket-versions), [version-deletion API](https://www.backblaze.com/docs/cloud-storage-file-versions). Do not apply blanket lifecycle/delete commands to any preexisting user bucket.
4. Price is **expected $0 for the proposed tiny storage** subject to current free-tier terms and use; egress quota is based on monthly average byte-hours, so a short-lived upload followed by a download is **not mathematically guaranteed** zero egress. The published excess cost is just **$0.01/GB**; the anticipated 1.1MB transfer's raw variable egress is far below one cent before any minimums/taxes/payment-policy effects. CircleCI executor credits/cost are **separate** and remain unapproved.
5. **Next narrow owner action:** decide whether to use new **Backblaze B2 Free** account, viewing its signup/terms and creating no bucket/key yet. If owner selects it, review actual account setup/payment requirements and plan private-bucket/app-key + source-side age encryption as separate explicitly scoped implementation steps. No CI code changes, no cloud object, no live data upload or restore has occurred.

Research checked: 2026-10-30. Providers' offerings and account conditions may change; verify at signup. This is a cloud storage **selection recommendation**, not final third-party confidential-data transfer authorization or permanent CCPC backup design.

## 7. Backblaze B2 private test bucket created — owner-supplied UI evidence (2026-10-30)

Owner completed Backblaze B2 Free signup and created a **dedicated bucket** `ccpc-ci-restore-20261030`, with region endpoint `s3.us-west-004.backblazeb2.com`. Owner-supplied UI screenshot of the bucket card shows **Type: Private**, **Encryption: Enabled** (Backblaze-managed SSE-B2), **Object Lock: Disabled**, **File Lifecycle: Keep all versions**, **Current Files: 0**, **Current Size: 0 bytes**; created October 30, 2026. The screenshot is UI evidence of these settings, not an independently API-tested bucket ACL, encryption or transport test. Deliberately do not store account identifiers, bucket ID or any future keys here. There was **no backup, ciphertext, or other file uploaded**. These are separate from the legacy Synology NAS backups. Existing DEV and PRODUCTION unchanged.

**Operational decision:** The bucket is a suitable initially empty **private storage target for future age-encrypted single-object transfer**. SSE-B2 is only server-side protection; client-side authenticated encryption remains mandatory prior to cloud egress. Default `Keep all versions` can retain hidden prior versions **indefinitely**; after the authorized rehearsal, cleanup must enumerate and delete the exact run's object versions, and independently verify no versions remain. Do not alter lifecycle settings prematurely or adopt global wildcard deletion.

**Next narrow UI-only task:** Owner navigates Backblaze **Access Control → Application Keys** and views the *New Application Key* configuration form, **without creating the key yet**, so we can restrict bucket, read/write or later separate upload/read keys, file-prefix and expiry. Do not use account master key. No key text, secret value, presigned URL, backup data, or site config should appear in chat screenshots. Actual key creation and external transfer remain separate scopes; CircleCI CI-source/secret context, credit-consuming run and restore remain unapproved.

## 8. Backblaze application-key form inspected; avoid unnecessary write key (2026-10-30)

Owner supplied an **Add Application Key** screenshot before any key creation. Form includes Name, Allow access to Bucket(s) (default `All`), Type of Access (default `Read and Write`, other options `Read Only`/`Write Only`), File name prefix, Duration (seconds). **Defaults are overbroad and must not be submitted.**

For this **~1.1 MB** one-time archive, official [Backblaze console upload documentation](https://www.backblaze.com/docs/cloud-storage-upload-and-manage-files) allows browser-upload of files up to 500 MB directly from an authorized owner device. This eliminates the need to create or temporarily store a `Write Only` app key to upload the payload; our sequence is **(a)** generate and independently decrypt-verify the **age-encrypted bundle** on the trusted side, **(b)** upload ciphertext **only** with the owner's authenticated browser to a path matching the anticipated prefix, **(c)** then create a narrowly restricted **Read Only** single-bucket, prefix-scoped key solely for short-lived CI download/presigning when the CI job is actually ready. Never upload a plaintext tar, four original components, or site-config files. Never give CircleCI any `Read and Write` or `Write Only` bucket key.

Proposed later read key settings (do NOT create while job/backup is not ready):
- Alias `ccpc-ci-restore-read-20261030` (date/name can be refreshed);
- Bucket **`ccpc-ci-restore-20261030`**, NOT `All`;
- **Read Only**;
- Object key **name prefix `integration2-restore-20261030/`** (the browser-uploaded ciphertext must be stored under this exact prefix; check actual B2 web upload folder/path behavior beforehand);
- Duration **86400 seconds (24 hours)**, starting at creation. If the test will not run promptly, wait instead of consuming expiry. A presigned GET URL should be substantially shorter-lived than the app key and treated as sensitive bearer material. For S3-compatible clients, some list-buckets operations require optional `listAllBucketNames` (visible only after selecting a single bucket); avoid granting this unless chosen tooling requires it. Direct `GetObject` signing may avoid bucket listing. [Official B2 key options](https://help.backblaze.com/hc/en-us/articles/360052129034-Creating-and-Managing-Application-Keys), [S3 compatibility](https://www.backblaze.com/docs/cloud-storage-s3-compatible-app-keys).

**Immediate direction:** Cancel key form; no key generation, no secret screenshot, no upload, no API setup. Next safe step is read-only check whether owner-controlled workstation/server already has `age` and `age-keygen` tools, plus design of a provenance-verified installation if absent. Any software installation or sensitive copy still needs exact scope review. Cloud backup ingress and one CircleCI restore run remain unapproved.

## 9. Protected age identity generated and canary round-trip verified (owner output, 2026-10-30)

After the user-local Ubuntu 26.04 `age 1.2.1` binary installation, owner executed the reviewed identity creation/canary script on `gani@ccpcerpserver`. Exact owner-reported status:

```text
AGE KEY GENERATION: PASS
PRIVATE KEY PERMISSIONS: PASS
ENCRYPTION/DECRYPTION TEST: PASS
PRIVATE KEY NOT DISPLAYED
```

**Evidence scope:** `~/.local/share/ccpc-integration2-restore/identity.txt` was created via `age-keygen -o` in a restricted mode-0700 directory, private identity mode 0600, public recipient derived in-process and a **nonsecret canary** successfully encrypted/decrypted. No keys, public recipient, plaintext application backups or protected data appeared in the user's output; **no real archive encryption, transfer, Backblaze upload, CI context or restore is proven**. A 0600 owner-local file is protected against ordinary users but remains accessible to host root; it is not an off-host disaster-recovery key backup.

**Next explicitly bounded owner-local action:** Create one **new** restricted `~/ccpc-integration2-encrypted` directory separate from the identity; confirm existing four Integration2 October 29 snapshot components and site-origin prefix, individually SHA256 hash in memory; create a tar stream of exactly the four files plus embedded SHA256/size/source-commit manifest; encrypt with `age -r` using the public recipient derived from the protected identity; persist **only the `.tar.age` ciphertext** under an exclusive random filename (0600), never an unencrypted `.tar` file. Locally decrypt that ciphertext **in memory only** with the existing identity; verify tar membership, manifest equality, four byte sizes and SHA256s, then print the fixed PASS statuses, encrypted output path and ciphertext SHA256 only. Guard duplicate output-directory existence and unexpected source size; STOP rather than overwriting. The accepted source directory is `/home/gani/deployments/frappe_docker/development/frappe-bench/.ccpc-pr32-snapshots/ccpc-integration2.localhost-20261029T132329Z-99d6786e`. The owner has not yet executed this stage. This will read backup bytes locally but will **not** restore, modify original backups, create a cloud object, generate Backblaze app keys or spend CircleCI credits.

**Key continuity:** Keep the private identity and ciphertext **separate**. Before any future deletion of this original local identity, arrange a separately approved, tested, protected offline recovery copy or CI-secret handoff; losing the identity means the encrypted archive cannot be decrypted. Do **not** show identity contents to ChatGPT or commit them. The external transfer of ciphertext, CI context creation and CI build remain separate deliberate decisions.

## 10. Local Integration2 backup encryption succeeded and was independently decrypted/re-hashed (owner output, 2026-10-30)

The operator executed the reviewed local-only `age` encryption command against **only** the original protected October 29 Integration2 four-artifact snapshot. Exact returned status:

```text
SOURCE BACKUP COMPONENTS: 4/4 PASS
AGE ENCRYPTED ARCHIVE: PASS
LOCAL DECRYPT/VERIFY: 4/4 SHA256 PASS
CIPHERTEXT FILE: /home/gani/ccpc-integration2-encrypted/integration2-restore-20261030-85ff2c424e4cb5cf.tar.age
CIPHERTEXT SHA256: 92fe1ba22fa6f1ae53828cf6da5276c6d7a7310f8b99be74a33bca0939911560
NO CLOUD UPLOAD OR SITE CHANGES
```

**Evidence:** The guarded command checked private age identity ownership/mode (user-local `~/.local/share/ccpc-integration2-restore/identity.txt`), derived only public recipient internally, validated the exact four component filenames and source-site prefix, packed four original file streams and a JSON SHA256/byte-size/source-app-commit manifest into an **in-memory tar**, encrypted via user-local `age` 1.2.1, wrote **one new ciphertext only** to `~/ccpc-integration2-encrypted` under mode 0600, decrypted it locally in-memory, and verified tar membership, embedded manifest and original file byte lengths/hashes **4/4 PASS**. No plaintext TAR was written to disk by this script. The resulting ciphertext SHA-256 is safe to use as a transport integrity comparison (not a decryption key). Command's status is **operator-reported**; GitHub connector has no independent access to the host file or age identity.

**Status distinction:** The 1.1 MB original Integration2 backup and separate eight-file Synology copy are still intact as last reported; ciphertext has **not** been uploaded to Backblaze, placed in CI, transferred to a workstation, or restored. The owner-created private bucket `ccpc-ci-restore-20261030` remains previously verified empty from UI; no subsequent live bucket read performed. No B2 application key or CI restricted context has been created. Original `identity.txt` is on the shared CCPC host and is **not an independently retained recovery key**; before relying on cloud ciphertext, plan a protected, separate key backup/handoff that does not expose secret text in chat, GitHub or screenshots.

**Next minimal operator step:** Move **only the encrypted `.tar.age` ciphertext** to the owner's local browser workstation using the already trusted existing SSH/SFTP connection (Windows built-in OpenSSH `scp` or operator's approved SFTP client), never copying `identity.txt`, original SQL/site-config/TARs or any other backup files. Verify workstation SHA-256 against the exact ciphertext hash `92fe1ba22fa6f1ae53828cf6da5276c6d7a7310f8b99be74a33bca0939911560` before considering upload. Avoid public links, browser sync folders, cloud auto-upload directories and clipboard transfer of private secrets. A separate approval is needed for actual cloud egress and CI billing/secret setup; don't initiate upload simply because local ciphertext is ready.

## 11. Ciphertext-only download to owner Windows workstation: matching SHA-256 (2026-10-30)

Owner used **Windows PowerShell via Windows OpenSSH** (VS Code Remote SSH host alias `erpnext`) to copy only the already generated encrypted artifact from the Ubuntu shared host to the Windows Downloads folder:

```text
scp "erpnext:/home/gani/ccpc-integration2-encrypted/integration2-restore-20261030-85ff2c424e4cb5cf.tar.age" "$env:USERPROFILE\Downloads\"
```

The `scp` terminal reported `100%` / `1110KB` transferred. Then the owner executed `Get-FileHash -Algorithm SHA256` on the Windows ciphertext; PowerShell reported:

```text
92FE1BA22FA6F1AE53828CF6DA5276C6D7A7310F8B99BE74A33BCA0939911560
```

This matches the source-side ciphertext SHA256 case-insensitively: `92fe1ba22fa6f1ae53828cf6da5276c6d7a7310f8b99be74a33bca0939911560`. **Transport byte-integrity PASS; local source encrypt/decrypt/integrity 4/4 PASS**. No indication that private `identity.txt`, a plaintext SQL/file backup or any site credential was copied to Windows. Owner's username/home path intentionally omitted here. Original host ciphertext and protected source/NAS backups remain separate.

**Important scope:** A matching checksum alone does not authorize off-owner-network egress. **No Backblaze upload, bucket ACL recheck, new application key, CircleCI secret/job/build or actual restore has yet been evidenced or authorized.** Before instructions for the private B2 browser upload, ask for explicit *separate informed owner approval* to upload only this age-encrypted ciphertext to `ccpc-ci-restore-20261030` (external third-party retention; B2 `Keep all versions` lifecycle, delete exact versions after rehearsal). Confirm the private identity will **not** be uploaded to B2, GitHub or chat. Later CircleCI-hosted decryption of the actual Integration2 snapshot is a *different* high-trust exposure requiring another scoped permission and secured ephemeral environment. Plan identity recovery custody separately, avoiding plaintext key disclosure.
