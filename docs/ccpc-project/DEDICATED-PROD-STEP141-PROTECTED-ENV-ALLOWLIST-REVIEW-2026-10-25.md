# Step 141 — Protected external Compose env-file allowlist (GitHub-only review)

**Date:** 2026-10-25 Asia/Manila. **Owner-approved scope:** design and test a narrow protected-credential-file restriction, on a fresh source-pinned review branch. **Status: CODE + MOCK TESTS STAGED, STANDALONE PARSER TESTS PASS; NOT MERGED, NOT DEPLOYED, FULL REPOSITORY BASH REGRESSION STILL PENDING.** No office server, SSH/PuTTY, Docker, GitHub Actions or billable runner, live ERPNext/DB, Synology NAS, business data, production credential, image or TLS operation.

## Source and repository identity

- Parent review branch: `review/dedicated-compose-env-guard-2026-10-24` at exact Step 140 head `dd86e8cff71d848e4f88383d7481a2f78b8545da`.
- New separate review branch: `review/dedicated-env-file-allowlist-2026-10-25` at verified head `284f8b0b14cc823b93ccaf36152a524798b9705e`.
- GitHub compare against the parent: ahead, **three changed files only**, with existing unrelated review code preserved:
  1. `scripts/modules/docker.sh`: 33-line added fail-closed contents validator, Git blob `b4314a58892b0f0b64a0086d5e31cbe2d2c4963e`.
  2. `tests/test_dedicated_env_security.sh`: synthetic fixture tests for rejected keys and invalid formats, Git blob `64da988eb7d347bdda4a3e4416f939535cbb976f`.
  3. `docs/04-operations/dedicated-production-external-credentials.md`: candidate procedure updated to explicitly permit only DB_PASSWORD, Git blob `a5cbf9baf890efcc8dd87aae393d6fc3db7bfdea`.
- Branch creation, file contents, affected paths, blob identities and current HEAD were re-fetched and verified through connected GitHub. Original stacked PRs #27/#29/#30 **not advanced**, no review branch rebased or merged.

## Source-derived design

`verify_dedicated_env_file()` previously checked external path, symlink, owning user, file 0600, immediate directory 0700, absence of checkout `.env`, and ambient shell `DB_PASSWORD`; it then accepted **all file contents**. Step 139 already rejects three ambient Compose selector variables in `ccpc_compose()`, but this cannot block the same selector keys if supplied **inside the protected `--env-file`**. Docker documents `COMPOSE_PROJECT_NAME` as a project selector and describes Compose pre-defined variables in environment files (see below).

The new review-only contents check is intentionally narrower than a generic dotenv parser:

- Exactly **one** literal `DB_PASSWORD=` assignment is permitted; blank lines and full-line `#` comments permitted.
- Rejects every other assignment/control/directive, including `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `COMPOSE_PROFILES`, other `COMPOSE_*`, `CUSTOM_TAG`, and `export DB_PASSWORD=...`.
- Rejects missing, duplicate, empty, obviously quoted-empty password, NUL bytes, Windows-style CR bytes, zero-length files, and files larger than 4096 bytes.
- Checks size and bytes without logging or sourcing/evaluating secret values. Keeps the existing dedicated-only access and Docker-context guards unchanged and legacy `legacy-lan` Compose path unmodified.
- This is **not** a cryptographic pin on the file's future contents, nor a complete Docker credential vault. Race-free open/read handoff, real Compose dotenv quoting/interpolation, password strength/rotation, and exact final project identity require separate scrutiny.

**Compatibility change:** The older candidate documentation permitted additional reviewed non-secret Compose interpolation keys in the protected file. This staged design **does not** permit them; any future need must go through a separately reviewed allowlist change. This is intentional to prevent accidental Compose project/profile redirection.

## Verification performed — distinguish actual tests from unexecuted suites

1. Reviewed current source at the frozen Step 140 parent, actual Compose template interpolations, new GitHub patch and tests. The five-file candidate Compose source shows DB_PASSWORD is the only required **credential** from the protected file; `CUSTOM_IMAGE` and `CUSTOM_TAG` are explicitly supplied from the invoking release shell. This is a **source-based compatibility inference**, not an observed live deployment.
2. **15/15 standalone synthetic Bash parser behavior tests PASS**, and `bash -n` PASS, in a disposable local directory. The executed test was a **standalone adaptation of the new contents-validation logic**, not a byte-for-byte checkout of the full GitHub `scripts/modules/docker.sh`. Its cases included valid single key/comments and rejection of missing/empty/quoted-empty/duplicate password, project/file/profile/other Compose keys, release tag, export syntax, CRLF, NUL and oversize. The complete GitHub-checked-in Bash script `tests/test_dedicated_env_security.sh` **was not executed in this Step**. Do not count this as an additional full exact-source suite PASS.
3. Source review after GitHub write verified both new code and fixture cases, their file hashes, and only the expected three-file diff against Step 140 parent. No GitHub Actions tests were run. No Docker binary/Compose v2 parser, realistic app stack, DB writes, backup or restore was exercised.

**Correction audit:** An early source-file update on this **new review branch only** accidentally interpolated a JavaScript replacement token in Bash syntax and duplicated text. This was detected immediately by source length/diff inspection; a follow-up non-destructive commit **`026fd1da2951478492b157339288803afa08e70d`** restored the intended single function and verified exact content. The **final reviewed HEAD** contains the corrected file; neither original PR nor prior review branch was changed.

## Remaining release identity and operational gates

- Rejecting protected-file `COMPOSE_*` keys does **not** pin the Compose project's actual identity, which can still derive from explicit CLI/project name configuration or working-directory/Compose file paths. An explicit, reviewed project-name policy (often `docker compose -p <reviewed_name>`) and verifying volumes/container identity is a **separate decision** requiring actual dedicated-host evidence; do not invent `ccpcerp-prod` project name from hostname.
- Other ambient `COMPOSE_*` switches, trust in the local Docker socket/CLI, symlink/race or ancestor-directory protections, precise secret interpolation, privilege and release rollback remain open for review.
- The original PRs #27/#29/#30 remain DRAFT/UNMERGED. Step 138 consolidation and Steps 139/140 staging are preserved; Step 133 135/135 Python mocks were not rerun. Step 136 G0 remains partial and G2 Compose v2 semantic render unexecuted.
- Before any integration/promotion, run the **entire exact-blob GitHub Bash test suite** and independently review inherited shell/env-file effects; test effective Compose project, named sites/logs/database volumes, port mappings, generated config without emitting credentials, TLS and eventual backup/restore under separate approval.
- Do not run live migrations, images/containers, production cutover, or modify old shared PROD/DEV/NAS based on this review.

## External reference for technical rationale

- [Docker: Compose pre-defined environment variables](https://docs.docker.com/compose/how-tos/environment-variables/envvars/)
- [Docker: Specify a project name and precedence](https://docs.docker.com/compose/how-tos/project-name/)
- [Docker: Interpolation and external --env-file](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation)
