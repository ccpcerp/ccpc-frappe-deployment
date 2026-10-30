# PR #32 — review-only CircleCI Integration2 restore-test code proposal

**Status: PREPARATION / SECURITY REVIEW ONLY. NOT DEPLOYED OR EXECUTABLE IN THE APP CI.**  
Prepared: 2026-10-30 (Asia/Manila). Owner explicitly approved **preparation and review of GitHub code**, *not* CircleCI credential creation, hosted decryption, execution, billed credits, or changes to existing DEVELOPMENT / PRODUCTION.

## Why staged in the deployment documentation repository

The source app's PR #32 branch, `ccpcerp/ccpcerp:review/four-day-one-reports-integration-2026-10-29` (verified HEAD `061e65710eb4b527fc8ac579aaab8ccad4dd131d`), has a **starter-validation** workflow that runs on ordinary pushes. Opening a new app review branch or committing code could start CircleCI automatically and consume credits even without requesting the expensive restore job. These **non-active draft files** therefore live in this deployment documentation branch until the owner separately approves a precise branch/commit and zero-surprise activation plan. Do not mistake this directory for a runnable CircleCI job.

## Staged source

- **`restore_guard.py`**: exact CircleCI project/job/branch/SHA/ephemeral site and DB validation; explicit hosted-decryption permission and SSH-debugging policy gates; exact private Backblaze B2 object URL allowlist plus short-lived (at most 900-second) AWS SigV4 signature/date requirements; strict ciphertext length/SHA-256/age header; in-memory five-member tar manifest and exact four backup-component digest checks; exposes only the original site's `encryption_key` internally and never installs original site configuration. No network transfer, SQL or site modification functions in this module.
- **`test_restore_guard.py`**: source-only stdlib tests with synthetic, non-sensitive in-memory fixtures, covering good and bad identities, checkout SHA mismatch, database host/site restrictions, URL constraints, wrong ciphertext sizes/digests, overly long/unsigned B2 URLs, expected manifest, corrupted/oversized tar and inert-config hard-stop. Test does not use real backups, age secrets or CI credits.
- **`config-proposal.yml`**: partial configuration proposal with `run_integration2_backup_restore` default `false`, separate branch-filtered manual approval, disposable MariaDB and Redis sidecars, exact project/site checks. **Deliberate `exit 86`** prevents restoration even if accidentally activated. This is not a standalone complete CircleCI YAML document and MUST NOT be pasted as-is into an active config.

## Review against pinned source

| Aspect | Reviewed design / finding |
|---|---|
| Original Integration2 app | **`0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41`**. Restore there first, not directly into PR #32's five extra Finance DocTypes. |
| Framework | Frappe `988e54f3c4c291e2077a83809663f123731abe76`, ERPNext `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd` from existing reviewed disposable CI scripts. Confirm restored source/runtime compatibility before execution. |
| Source archive | One private B2 object: `ccpc-ci-restore-20261030/integration2-restore-20261030/integration2-restore-20261030-85ff2c424e4cb5cf.tar.age`. Length **1,137,112**, SHA-256 **`92fe1ba22fa6f1ae53828cf6da5276c6d7a7310f8b99be74a33bca0939911560`**, Windows/B2-download copy checked. Identity remains outside B2. |
| Site/DB isolation | Proposed unique CI site `ci-ccpc-pr32-restore.localhost`, DB `ci_pr32_restore_20261030`, MariaDB only at `127.0.0.1:3306`. None resembles active CCPC site/database. |
| Dangerous restore behavior | Pinned Frappe `frappe/commands/site.py` calls `_new_site(..., force=True)`, which can recreate/drop its **target** DB. Never pass a real CCPC site/DB. Require existence checks against an isolated freshly created CI DB before each destructive operation. |
| Attachment file names | Pinned Frappe `frappe/installer.py` `extract_files()` calls **`tar xvf`**, which prints attachment names into CI logs and is unsuitable for confidential real backup. Final runner **must avoid** this path, safely inspect nested TAR structure and extract silently under the new ephemeral site; reject links/absolute paths/`..`/special files before writing. |
| Third-party access | Need owner authorization for hosted plaintext decryption separately. Require CircleCI restricted context project+branch and expression **`not job.ssh.enabled`**; `CIRCLE_SSH_ENABLED` environment variable alone is not an authoritative prohibition. No CI secret, private URL, site config or plaintext in code/logs/artifacts/cache. |
| Cost/running | New restore workflow default `false`, held manual approval, exact approved git SHA required, explicit maximum credit budget/timeout approval. Existing `starter-validation` trigger needs independent gating; a Python time limit is not a monetary credit cap. |

## Required remaining implementation before any actual run (UNTESTED)

1. Review the app branch's **auto-trigger** behavior and choose a safe staging/porting method with an explicit credit budget before any app-repository ref or CircleCI YAML change. Verify whether `[ci skip]` applies to the project's actual CircleCI trigger: provider documentation cautions exceptions for GitHub App custom webhooks/API/scheduled workflows. No hidden automation.
2. Implement a **no-redirect**, TLS-only single-object download inside the disposable job using a very short-lived restricted private B2 presigned URL. Never log the URL; enforce length, exact object path and SHA-256 **before decrypt**. There are no B2 keys or URL in GitHub.
3. Plan **secure one-run identity delivery** separately from B2: an owner-approved restricted CircleCI context or secret broker that denies SSH debug reruns. Never upload private `identity.txt` to B2 or chat, and never place it in pipeline arguments, job output, cache/workspace, artifacts or logs.
4. With explicit permission, build a **new** ephemeral bench with the source commit and above pinned Frappe/ERPNext; prove MariaDB is the isolated sidecar and the DB/user/site were not present previously. Pinned Frappe has destructive restore internals: the guard must run before every `bench restore` call and must not rely solely on string matching.
5. Decrypt into protected ephemeral scratch, verify inner SHA256 manifest against all four byte streams and verify public/private inner tar contents and safe paths. **Don't call Frappe's verbose `--with-public-files` / `--with-private-files` extraction**. Write a silent, link-safe extractor after verifying actual tar member formats. Create a new site with only CI-generated DB credentials, transferring *only* the original site's `encryption_key` for decrypting existing encrypted application fields. Never restore the source `site_config.json` wholesale.
6. Restore SQL at original source SHA in a new throwaway DB (restore can be destructive **only** there), then safely restore attachments. No migrations into PR #32 HEAD during first recovery proof. Do not launch web workers, schedulers, email, outbound webhooks, payment gateways or other external integrations. Validate TISS/TREQ company reads, app identity, source schema and file reads without printing confidential data.
7. Provide a small **sanitized PASS/FAIL** outcome table, with no original records, credentials, filenames of private attachments, SQL traces, signing URLs, decrypted archives, CI artifacts/workspace/cache. Sanitize failure logs as carefully as success logs. New target teardown only within independently controlled hosted CI sandbox; no generalized DROP/TRUNCATE/DELETE against shared hosts.
8. After separately approved rehearsal, revoke temporary CI credentials and delete **all versions** of the exact B2 object (bucket's current lifecycle: Keep all versions) once the recovery evidence has been recorded. Preserve source Ubuntu and Synology backups and off-server encrypted identity copies. Request a different explicit authorization before any persistent DEVELOPMENT integration or PRODUCTION change.

## Static review findings / limitations

**Prepared and manually/static-code-reviewed; the proposed Python unittests have NOT been executed in this conversation, and no real CircleCI execution occurred.** Current draft guard and source tests can be tested on a disconnected workstation with `python -m unittest discover -s <this-directory> -p test_restore_guard.py -v` (Python 3.10+). A local test, even if green, will **not** substitute for a separately approved real disposable MariaDB restore.

**Blocked by design:** no cloud download/decrypt implementation, no key/context creation, no Frappe installation or DB restore code enabled; `config-proposal.yml` hard exits `86`. These are explicit next engineering tasks, not hidden “successes”. Source SHA/branch and literal date are proposed for this one-off rehearsal and may need updating before activation.

Original app PR #32 and its 86/86 reported MariaDB acceptance are unchanged. DEV on shared Docker host and PRODUCTION were never used for this proposal.

## Authoritative references

- [Project GitHub-first workflow](../GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md)
- [Latest active handoff](../CURRENT-HANDOFF-3.md)
- [Integration2 isolated rehearsal plan](../PR32-INTEGRATION2-ISOLATED-RESTORE-REHEARSAL-PLAN-2026-10-30.md)
- [B2 age-encrypted transfer design/evidence](../PR32-INTEGRATION2-CIRCLECI-ENCRYPTED-TRANSFER-DESIGN-2026-10-30.md)
- [CircleCI context expression restrictions](https://circleci.com/docs/guides/server/security/contexts/)
- [CircleCI skip-CI behavior/limits](https://circleci.com/docs/guides/orchestrate/skip-build/)


## Further source-only integration verification (2026-10-30, owner approved)

After explicit owner approval for continuing review-only code/testing, the offline runtime prototype was connected to a **byte-for-byte copy of the GitHub guard**. The original committed guard copy matched Git blob `c31e85eb86e8861f871b9000a76b16db340e7f57`. **14/14** local synthetic tests then passed, including restricted CircleCI identity, exact source app and branch, safe attachment entry paths, no-overwrite behavior, archive manifest/digest checks and refusal of unapproved database hosts/sites. This did **not** connect to a real MariaDB service, run a CircleCI pipeline, or read the actual encrypted Integration2 snapshot.

The review identified that merely verifying `X-Amz-Expires <= 900` and a signed-date syntax is insufficient: an already-expired URL could pass locally. The existing **review-only GitHub guard and URL tests** were updated to require a current signature timestamp, bounded lifetime, SigV4 credential and signed `host` header, with failure cases for expired dates and unexpected signed headers. GitHub guard commit **`4d27371cd09ed3a8aa4cd1e0d50d7c27e86c2ab4`**, current guard blob `51c555dab230a5b96968849aefd09c20edf80e2e`; associated synthetic test commit **`db2f3f2bd55cc70b2bec7e1ab142c888b00c1503`**. The current hardened local copy matched the new GitHub guard blob exactly and the **14/14** offline runtime/integration tests re-passed.

**Important remaining limitation:** The local `restore_runtime.py` prototype is **not** in GitHub: an earlier GitHub publication was blocked, so no runner was wired to an active CI config. A local test deliberately shows a caller-supplied `db_probe=lambda: True` can make a syntactic preflight pass without proving real MariaDB origin. Therefore **it must not authorize any destructive SQL restore**. A separately auditable, actual CI-sidecar provenance and fresh DB/site provisioning mechanism, source-version Frappe bench, sanitized extraction and rollback tests are not implemented/validated. No CI context, credentials, private identity transfer, hosted decryption, paid CI run, DEVELOPMENT or PRODUCTION changes have been authorized or performed. The GitHub configuration proposal remains **default OFF with hard `exit 86`**.
