# Step 138 — Exact GitHub Bash regression and safe PR stack integration plan

**2026-10-24 — owner-approved GitHub-only follow-up to Step 137.** Status: **STAGED, OFFLINE TESTED AND CONSOLIDATED ON A SEPARATE REVIEW BRANCH; NOT MERGED OR DEPLOYED**. No existing PR review head, Docker host, GitHub Actions runner, DEVELOPMENT, PRODUCTION, NAS, VPN, SSH credential or business record modified. No paid CI run requested.

## A. Frozen original stack and review heads

| Purpose | Branch | Verified head after this milestone |
| --- | --- | --- |
| Production port profile, original draft PR #27 | `security/dedicated-production-pre-tls-2026-10-23` | `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` (UNCHANGED) |
| Dedicated external credentials, original draft PR #29 | `security/dedicated-prod-external-env-2026-10-23` | `bd92ade7ac859b9f6b21b157bdc1629e93f4540c` (UNCHANGED) |
| Advanced backup framework, original draft PR #30 | `feature/dedicated-prod-backup-safety-2026-10-23` | `fd751ab7c39c252e469e1d59d6ebbb1408381061` (UNCHANGED) |
| PR #27 source-level regression review | `review/pr27-offline-profile-tests-2026-10-24` | `5ed118fd150b37070713cd536c4c97542a346b24` |
| PR #29 Docker-target hardening review | `review/pr29-local-docker-target-2026-10-24` | `b92a0a468b84019580d77fa3b8b1beb76bf51c9d` |

The original PRs are stacked **#27 → #29 → #30**. Both review branches were created from their own exact original parent PR head. They were **not** merged or rebased.

## B. Verified executable source-level tests (not CI)

Test environment: isolated ephemeral local filesystem under `/tmp`, independent `git init` repositories, Bash + Git, no Docker executable/daemon, no CCPC credentials or production route, synthetic test values. The test fixtures were manually reconstructed from connected-GitHub source files and their exact Git blob identities independently verified using `git hash-object`. Do **not** call this a full GitHub checkout or live runtime test.

**PR #27:** Initial newly authored review test contained three unintended `\${...}` escapes, which would prevent correct evaluation; review-branch commit `5ed118fd...` repaired them. The exact corrected Bash smoke file blob `dd7a400b42574a23d1a2c118bbbdf3468f0eb51e` was reconstructed and byte-hash verified alongside:
- `scripts/config.sh`: `32614da1044c768bd67dcb9b9491e7c48ff2653a`.
- `overrides/compose.dedicated-pre-tls.yaml`: `9b69b0c7a1d64191a51da5126ddc82498202446f`.

**Actual observation:** `bash -n` and `bash tests/test_dedicated_profile_offline.sh` **PASS**. This covers default/explicit legacy four-file selection, opt-in dedicated fifth overlay at the end, localhost health check, bad profile rejection, literal `!override`, localhost-only port *source line*, and nonempty password substitution *source line*. It does **not** cover true Compose v2 interpolation/merge or the absence of extra published ports.

**PR #29:** Full checked-in `bash tests/test_dedicated_env_security.sh` **PASS** (with Docker functions mocked) against these exact Git sources, all reconstructed in the isolated scratch repository:
- `scripts/lib.sh`: `7f83828f99273445b6b95d171fb9f9b4862c0587`.
- `scripts/modules/env.sh`: `38a6fdef14abc9e61ae8425ab606dce6201290c1`.
- `scripts/modules/deployment.sh`: `ab862074235f174bf5de042ea7c6562965a34243`.
- **Reviewed/updated** `scripts/modules/docker.sh`: `72381c1e23e6ca8959dfed7bd17286316536b43a`.
- **Reviewed/updated** `tests/test_dedicated_env_security.sh`: `ba0f24eec0900e00385f38650a1d7fd3e0fb95d7`.

`bash -n` on all five Bash files **PASS**. The complete test reports expected acceptance of a synthetic owner-only external environment file, required image name/tag, legacy behavior and dedicated release export, plus rejection of bad credential path/symlinks/modes, ambient password, image mismatch, remote context/host endpoint, `.env` copy/edit, and deliberate rejected Docker image inspection/build target cases. Six new negative test calls cover remote `DOCKER_HOST`, remote `DOCKER_CONTEXT` and nonlocal socket for `verify_image` and `build_image`; the original Compose-specific negative set remains.

For test repeatability, the test script now clears inherited `DB_PASSWORD`, `DOCKER_HOST`, `DOCKER_CONTEXT` and mock-only endpoint/context variables before setting its synthetic fixtures. The full test **also passed while an external shell initially populated those Docker environment variables**, confirming scrub behavior.

**Important review correction:** Step 137's earlier source-review note used the phrase 'local equivalent smoke' for PR #27. Step 138 is the **first observed execution of the actual byte-matched, corrected PR #27 test file**; do not retroactively count the uncorrected test as passing.

## C. Code scope and remaining compatibility risks

- The initial PR #29 review guard protected **only** `ccpc_compose()`. Source review of `scripts/build.sh`, `scripts/deploy.sh`, `scripts/rollback.sh` and `scripts/modules/docker.sh` confirmed `build_image()` and `verify_image()` invoke the raw Docker CLI **before** the Compose guard in normal workflows. The review branch now calls `verify_dedicated_local_docker_target()` before these operations whenever profile `dedicated-pre-tls` is selected.
- It rejects `DOCKER_HOST` and `DOCKER_CONTEXT` overrides and requires `docker context show` to report `default` with `docker context inspect default` endpoint exactly `unix:///var/run/docker.sock`. It does **not** prove the physical daemon's ownership, actual host identity, Docker socket inode, CLI executable integrity, Compose project namespace, or filesystem isolation. It is defense-in-depth, not a release authorization.
- Compatibility **must** be reviewed against the actual future dedicated host: a rootless Docker socket, nondefault context, other Unix socket or legitimately set environment overrides will deliberately fail. Only review this context on a named, authorized target when office access is available. Keep the old `legacy-lan` call path unchanged.
- Current tests use a **mocked** `docker()` shell function. There is **no** genuine image build, image inspection, Docker Compose config, Frappe bench, MariaDB, NAS CIFS, protected trust-root verification, backup/restore or rollback validation. The original upstream GitHub Actions checks on PR #27 failed before a runner executed steps; root cause unresolved (see Step 137), so no new CI PASS is claimed.

## D. Stack-safe integration decision

**Decision: DO NOT directly merge/fast-forward the original PR #27 or #29 heads yet.** Updating PR #27's head alone would change PR #29's comparison base without moving its descendant commits, and PR #30 is itself stacked on the current #29 head. Uncoordinated cherry-pick/rebase/force-push of parent branches can distort reviewed diffs and invalidate exact SHA pins in Steps 133–136.

Proposed future controlled integration after an explicit owner/reviewer approval naming the branch transition:
1. Review whether the profile test belongs in #27 and the new host-target guard in #29; confirm dedicated host compatibility (local socket vs rootless/nondefault) first.
2. Prepare a **non-destructive test integration** on a new consolidation branch sourced from the **exact #30 head**, applying the #27 new test and #29 Docker/test changes as discrete commits without changing any original PR base or force-pushing. Re-run the combined source/unit regression and inspect final tree diff against PR #30. This can demonstrate source-level integration while preserving all original pinned review heads.
3. Decide the actual stack merge order, handle PR base changes carefully, and refresh all source pins and evidence **before** any original PR head changes. Never use `reset --hard`, blind force pushes or silent rebases.
4. Separately perform true Docker Compose v2 render (Step 136 G2), then isolated runtime/backup/restore gates before deployment. **No cutover** without real, verifiable recovery.

**Next action available without office:** create and review the isolated consolidation branch described in point 2 (GitHub-only), subject to separate review of the exact source merge and no running paid CI. Original PRs remain draft/unmerged. Do not confuse 'mocked Bash test PASS' with installation readiness.

## E. Evidence and publication

Review branch ref comparisons from GitHub showed **PR #27 review branch ahead by 3 commits, 1 file added** and **PR #29 review branch ahead by 4 commits, 2 files modified** as of initial branch comparison (one additional test sanitization commit subsequently advanced PR #29 review head). Corrected PR #27 and updated PR #29 source files were re-fetched / verified by content blob hashes. The production release boundary remains closed.

## F. Same-session Step 138 continuation — consolidation branch CREATED and verified

The owner approved continuing the **GitHub-only review and integration assessment**. A **separate**, non-destructive consolidation branch was created from the original immutable draft PR #30 commit, rather than moving the original stacked PR heads:

- **Branch:** `review/dedicated-prod-stack-consolidation-2026-10-24`
- **Base (original PR #30):** `fd751ab7c39c252e469e1d59d6ebbb1408381061`
- **Verified review HEAD:** `08d725255263ebff9216e7e3b89727b4bf72f792`
- **GitHub compare:** 3 commits ahead, 0 behind; **only three changed files** against PR #30:
  - `tests/test_dedicated_profile_offline.sh` newly added, blob `dd7a400b42574a23d1a2c118bbbdf3468f0eb51e`.
  - `scripts/modules/docker.sh` reviewed target guard, blob `72381c1e23e6ca8959dfed7bd17286316536b43a`.
  - `tests/test_dedicated_env_security.sh` strengthened mocked tests, blob `ba0f24eec0900e00385f38650a1d7fd3e0fb95d7`.

**Independent combined local smoke verification:** constructed one separate temporary `git init` fixture holding those **exact Git blob bytes**, plus unchanged exact PR #30 `scripts/config.sh`, `scripts/lib.sh`, `scripts/modules/env.sh`, `scripts/modules/deployment.sh`, and `overrides/compose.dedicated-pre-tls.yaml` (blob `14fd89a3c2371104f464964137483de9f4a35861`). Both commands passed in this single synthetic workspace:

```bash
bash tests/test_dedicated_profile_offline.sh
bash tests/test_dedicated_env_security.sh
```

The second test used only Docker-function mocks with dummy, disposable `DB_PASSWORD=TEST_PLACEHOLDER_NOT_REAL`; no Docker Engine/Compose, Frappe, network, NAS, paid GitHub Actions, DEVELOPMENT or PRODUCTION execution. This **did not re-run Step 133's 135 Python tests**, nor the full checked-out merged GitHub repository, image provenance validation, Compose v2 merge, live socket identity or restore drill. Treat the observed result as **exact-source Bash regression PASS only**, not general deployment approval.

**Final integration assessment:** The consolidation branch safely demonstrates the patch overlay without rewriting any PR ancestors. Preserve this branch and its source SHAs. A later branch promotion must separately review host compatibility (default local Docker socket), run the full combined regression at a reviewed clean checkout, refresh historical source-pinned evidence, and plan a non-destructive stack merge/PR rebase under explicit owner approval. **PR #27/#29/#30 remain OPEN/DRAFT/UNMERGED and original heads unchanged.** No automatic CI/merge/deploy scheduled.
