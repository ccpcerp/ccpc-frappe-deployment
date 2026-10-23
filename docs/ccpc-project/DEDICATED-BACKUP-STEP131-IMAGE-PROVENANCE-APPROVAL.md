# Step 131 — Backend image provenance metadata and independent release-approval design

**2026-10-23 | GITHUB-ONLY CODE + OFFLINE SOURCE CHECKS | DRAFT / NOT DEPLOYED / NOT BACKUP-READY**

The owner approved the Step 131 scope proposed after Step 130: implement and offline-test *static image-provenance metadata* tied to the existing pinned Frappe, ERPNext, CCPC, patch and overlay build arguments, and document an **independent release-approval mechanism**. No Docker build, image pull, DEVELOPMENT checkout, service change, dedicated PRODUCTION operation, Synology NAS access, backup, database update, retention or restore is included.

## GitHub branch and exact code

- Source of truth is [draft PR #30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) `feature/dedicated-prod-backup-safety-2026-10-23` stacked on draft PR #29, stacked on draft PR #27; none merged by this step.
- `images/custom/Containerfile` GitHub commit **`4ccb6f8a84142e643b735e8c88e0c39a975ede6d`**, exact Git blob **`523ad5f3a7a58c8c9da23ad822d3f3d8526e16d2`**, fetched and verified. After `FROM base AS backend`, the final backend stage re-declares **five existing builder-verified ARGs** and uses them in five Docker `LABEL` values. Labels are:
  - `org.ccpc.frappe.sha` = `EXPECTED_FRAPPE_SHA`
  - `org.ccpc.erpnext.sha` = `EXPECTED_ERPNEXT_SHA`
  - `org.ccpc.ccpcerp.sha` = `EXPECTED_CCPC_SHA`
  - `org.ccpc.erpnext.patch.sha256` = `EXPECTED_ERPNEXT_PATCH_SHA`
  - `org.ccpc.erpnext.overlay.sha256` = `EXPECTED_ERPNEXT_OVERLAY_STATE_SHA`
- `tests/test_dedicated_image_provenance.py` GitHub commit **`1bff4588d99f2681d864f235855eb5c2ed4ef706`**, exact blob **`15f79170a26cd3da10b71fb4d6963c750d293b99`**, fetched and confirmed byte-identical to the offline-tested Python file. It contains **seven** focused positive/negative tests for presence, wrong values, missing final ARG, wrong build-arg forwarding, changed frozen release pins, absent builder verification, and extra unapproved label.
- Existing `scripts/config.sh` blob `32614da1044c768bd67dcb9b9491e7c48ff2653a` contains pinned source/patch/overlay digests. Existing `scripts/modules/docker.sh` blob `453959daf3b548fa67f8bdc647be0f147acd603e` passes those five `--build-arg EXPECTED_*=...` inputs. Existing builder re-checks the actual source commits, patch file and resulting ERPNext overlay. **No new secret-bearing label or build argument** was added and no existing deployment/Compose code was modified.

**Why this matters:** Step 125/129's read-only runtime inventory expects `org.ccpc.frappe.sha`. The metadata label is now declared in the backend image *source definition*, but **no image has been built** to demonstrate the actual output includes or accurately represents it.

## Offline verification (clearly separated evidence)

1. In a disposable local **Python 3.13.5 / PyYAML 6.0.3** workspace outside CCPC infrastructure, ran `python -m unittest discover -s tests -p 'test_dedicated_*.py' -q` -> **Ran 108 tests in 0.169s / OK**, and `python -m compileall -q scripts tests` -> successful. Breakdown: 101 unchanged synthetic/mock regressions from Step 130 plus 7 new provenance source-contract tests.
2. The new test file's **exact local tested blob** `15f79170a26cd3da10b71fb4d6963c750d293b99` matches the fetched GitHub file. The older 101 tests were copied from the previous Step 130 isolated test environment and were unchanged.
3. **Important qualification:** The isolated Python environment's `images/custom/Containerfile`, `scripts/modules/docker.sh` and `scripts/config.sh` were **representative offline source fixtures**, not byte-identical copies of the complete GitHub source files. The 7 Python tests therefore establish that the parser/negative scenarios behave on those fixtures, **not** that those seven tests were executed against the complete committed Dockerfile/build script/config.
4. To close the most relevant static-source gap, a **separate direct exact-GitHub-source inspection** independently fetched all three complete repository files after the Containerfile commit and checked each of the five release pins, corresponding `--build-arg` mappings, builder/final `ARG` declarations and final `LABEL` interpolation, plus the final `COPY --from=builder`. **All five mapping sets passed**. The Containerfile GitHub blob and exact test file GitHub blob were independently re-fetched. The full exact-GitHub checkout/new Python suite and Docker build are **not yet tested**. No GitHub Actions/CI success is claimed.

**Offline PASS is not build provenance, a validated image, running Docker identity, consistent backup, or a recovery test.** The new labels remain unverified metadata claims without an independent attestor or signed release process.

## Proposed independent release-approval workflow — DESIGN ONLY

This is a **trust-boundary specification**, not a functioning signing system or authorization to publish:

1. **Freeze reviewed inputs:** Record the full deployment Git commit, applicable PR relationships, pinned Frappe/ERPNext/CCPC commits, ERPNext patch and overlay hashes, Containerfile/build context digest, exact Compose file order/profile/project, source dependency lockfiles and their known reproducibility limits.
2. **Approve immutable upstream images:** Record verified content-digests (not mutable tag strings) for the Python base and MariaDB image; analyze mutable `apt`, `curl`, Node, `pip` and build dependencies before claiming reproducibility. Current source still uses the version tags `python:3.14.2-slim-bookworm` and `mariadb:11.8`; **no digest values have been approved**.
3. **Separate controlled build (requires NEW authorization):** A restricted, audited builder tied to the reviewed code emits an immutable backend image ID, registry manifest digest if pushed, a build provenance attestation (builder identity, complete material/source digests), declared labels and logs of verification outcomes. Record and independently review the intended MariaDB image ID as well. Metadata alone cannot prove those built bytes were generated from the asserted source.
4. **Separate approval signer:** Two-role control: a release preparer proposes a **non-secret, canonical versioned release manifest** and its SHA-256; a distinct authorized reviewer verifies it against the source-controlled build evidence and independently signs/approves its exact digest and release identifier. Protected signing credentials and approval records must be stored/managed **off the target host and outside the image**. Do not commit signatures' private keys, database passwords, site configs, SSH secrets, raw environment dumps or business data to GitHub.
5. **Trusted verifier and distribution:** A future backup/deployment runtime must fetch the manifest plus approval through a **separately authenticated trust channel**, verify the trusted reviewer's signature/digest, release validity/revocation, the expected host/site/profile, image IDs, Compose service config hashes and volume layout. Never self-approve by computing the expected digest from the same unchecked Docker daemon/manifest. If the trust channel is unavailable, signature invalid, release expired/revoked or any observation differs, fail closed with no backup authorization.
6. **Rollback/operational safeguards:** Plan protected rollback image identifiers, Compose/volume state and secret recovery independently. GitHub merge does not automatically deploy; there must be separate DEVELOPMENT validation and PRODUCTION approval, with backup/rollback. No `backup_ready=True` shortcut while quiescence, Frappe backup side effects, NAS publication and isolated restore are unproven.

## Unresolved blockers and proposed next gate

- **No actual image was built**; Dockerfile `ARG`/LABEL rules, final runtime labels and image ID have not been exercised by Docker. No Docker Compose CLI/engine, Frappe or MariaDB instance was contacted in Step 131.
- **Exact full-source Python provenance tests** (all 7 against the complete GitHub Containerfile, config and build script) still need an isolated SHA-pinned checkout or safe byte-for-byte transfer; the direct exact-GitHub mapping inspection was successful but does not substitute for the full Python test suite on that checkout.
- **No trusted release manifest, signed approval, immutable base/database digest, verified final image ID or actual Compose config hash** exists yet. Existing Step 127 `ValidatedRelease.trusted_runtime=False` and Step 129 `VerifiedIdentity.backup_ready=False` remain unchanged.
- DB/file capture consistency, Frappe default-backup cleanup, encryption/filters, NAS CIFS publication semantics, verified restore, alerts, retention and secret/key recovery remain separately gated.

**Next approval gate:** GitHub-only Step 132 can specify/check the *non-secret release manifest approval/evidence schema and offline verification interface* without populating real image IDs, handling private signing keys, building images, deploying containers, executing backups or accessing either host. Before any real DEVELOPMENT or NEW PRODUCTION integration, obtain fresh approval, inspect uncommitted work, verify Docker/Compose version/overlay order and prepare rollback. Existing legacy PROD/DEV on `ccpcerpserver` and Synology legacy `erpnext_backups` remain untouched.
