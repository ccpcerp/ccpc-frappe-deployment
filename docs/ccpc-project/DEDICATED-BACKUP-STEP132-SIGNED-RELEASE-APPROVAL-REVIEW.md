# Step 132 — Independently signed release approval and revocation snapshot interface

**2026-10-23 — GITHUB-ONLY / OFFLINE UNIT TESTS / NO DEPLOYMENT OR BACKUP AUTHORIZATION.**

Owner approved the specifically proposed **Step 132 GitHub-only implementation**: verify a non-secret release manifest against an independently approved, tamper-evident approval record, reject revoked releases and missing/stale approvals, and test failures offline. This is a policy-verification *library*, not an operating release authority, signer, backup runner, cron job, image builder, production deployment, or permission to handle any CCPC credentials.

## GitHub code and source of truth

Work based on current authoritative GitHub-first workflow and handoff; draft **PR [#30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30)** `feature/dedicated-prod-backup-safety-2026-10-23` remains stacked on unmerged draft PR #29 and unmerged draft PR #27.

1. **`scripts/dedicated_backup_approval.py`**, commit **`22be2baad43fd674bd0e762665d5b362fa0f3c0c`**, Git blob **`8ff82b242192628104b1c2fd82df9566e3af7ca6`**. Added an inert importable module using **Ed25519 public-key verification** through Python's optional third-party `cryptography` package. No signing/private key implementation, network calls, filesystem/host operations, Docker, bench, MariaDB, NAS, cron or privileged service calls.
2. **`tests/test_dedicated_backup_approval.py`**, commit **`8654b6c2952b87e91b70cb89a1a972457adbb145`**, Git blob **`bd095a874d12906e943041e13cb2a677fe1e12be`**. Twenty-seven tests use **ephemeral in-memory synthetic Ed25519 keys**, fake image IDs/config hashes, synthetic manifests and signed approval snapshots. No private signing material committed. Both changed GitHub files were fetched and **verified byte-for-byte against locally executed Git blob hashes**.
3. **No changes to** `scripts/dedicated_backup_policy.py` (Step 127), `scripts/dedicated_backup_runtime.py` (Step 129), source pins, Docker image/Compose or earlier capture/publication code. There is no new runtime wiring. The new verifier calls the existing `validate_reviewed_release()` against the digest from the verified signed approval, which checks source pins, named mounts and exact manifest structure.

## Signed snapshot schema and validation

A future **independently trusted caller** must supply:
- Exact unsigned but non-secret `manifest_raw` bytes; **signed** authority snapshot bytes (`snapshot_raw`); and its raw 64-byte Ed25519 `signature`.
- A `TrustedApprovalAnchor` with a 32-byte pinned reviewer **public key**, reviewer `key_id`, a **minimum accepted sequence** from independent protected high-water mark, and revoked reviewer key IDs from a separately authoritative channel.
- A trusted timezone-aware UTC clock value. None of these trust inputs may be derived from the same unchecked Docker daemon, untrusted manifest, snapshot, or an operator-editable environment file.

Snapshot v1 permits **exactly** `schema_version`, `authority_id`, `key_id`, `sequence`, `issued_utc`, `expires_utc`, `approval`, and `revoked_release_ids`. The nested `approval` requires `release_id`, `manifest_sha256`, `prepared_by`, `approved_by`, `approved_utc`, and `decision=approved`. Rejects duplicate/unknown fields, bad types, invalid UTC timestamps, mismatched authority/key ID, absent/invalid signature, missing reviewer separation, stale, future-issued or >15-minute validity snapshots, sequence below externally pinned minimum, rejected or revoked releases, revoked reviewer key, duplicate or malformed revocations, and any change to manifest bytes. Signature input includes **`CCPC-RELEASE-APPROVAL-SNAPSHOT-v1\x00`** domain separation before raw snapshot bytes. Snapshot data must be present and is size-capped at 16 KiB.

The signed approval record contains the independently reviewer-approved **SHA-256 of the exact release manifest bytes**; the final step calls the existing strict manifest parser and ensures the parsed release ID matches the signed record. Exception diagnostics are intentionally nonsensitive. `VerifiedApproval.trust_source_authenticated=False`, `VerifiedApproval.backup_ready=False`, and the nested `ValidatedRelease.backup_ready=False` remain default and unconditionally unchanged; signature PASS is **not** a backup/production authorization.

## Observed offline verification

Disposable **Python 3.13** tooling outside CCPC servers with **`cryptography 46.0.4`**:

```text
cd /mnt/data/step132
PYTHONPATH=. python -m unittest discover -s tests -p 'test_dedicated_backup_approval.py' -q
----------------------------------------------------------------------
Ran 27 tests in 0.012s

OK

python -m compileall -q scripts tests
# PASS
git hash-object scripts/dedicated_backup_approval.py tests/test_dedicated_backup_approval.py
8ff82b242192628104b1c2fd82df9566e3af7ca6
bd095a874d12906e943041e13cb2a677fe1e12be
```

**Crucial evidence limit:** Both **new** files match their exact GitHub blobs; their 27 tests were executed against a **local contract-compatible subset fixture** of Step 127's `dedicated_backup_policy.py` rather than a byte-identical full original policy file. Thus this is **signed verifier unit testing**, not a complete exact-GitHub-checkout integration/regression run. The earlier 108 Step 131 tests were NOT rerun here. Do **not** report 135 tests as one run or claim CI. GitHub source inspection confirmed the existing policy provides the named `RELEASE_ID`, `PolicyRejected`, `ValidatedRelease` and `validate_reviewed_release` interface the verifier uses.

Scenarios tested: valid synthetic signature, manifest modification/identity mismatch, missing/forged/altered signature and signed snapshot, wrong signer public key, revoked signer and release, missing/duplicate revocation records, stale sequence, future/expired/overlong snapshot, bad timezone, wrong authority/key ID, wrong decision, same preparer and approver, signed wrong manifest digest, unknown fields, bad trusted clock/anchor, duplicate signed JSON keys and assurance that success never sets `backup_ready` or runtime-trust flags.

## Security limitations / production blockers

**This is an interface, not a deployed approval system.** It does **not** authenticate or fetch the supplied trust anchor, trusted UTC clock, reviewer registry, revocation state or high-water sequence, and cannot prove the named reviewers actually approved a build. An untrusted caller could invent a key pair and sign its own release; **external trust-anchor provisioning, protected key management, human reviewer authentication and an auditable approval workflow remain mandatory**.

**Replay/availability risk:** Ed25519 prevents tampering with an issued snapshot, but does not prevent replay of a previously valid snapshot **within its up-to-15-minute lifetime** if the externally maintained minimum sequence has not advanced. The independently authenticated monotonic generation provider and revocation freshness/availability are **not implemented**. If the trusted source, signed status, key distribution or clock is unavailable or out of date, future integration must fail closed. Revocation and key rotation require separate recovery and emergency lockout procedures.

**Dependency and runtime:** The `cryptography` import is deliberately inside the verification method; if unavailable, verification fails closed. Third-party library version pinning, packaging, security updates, key verification/trust-root publication and use in a future restricted process require separate review. No signer/private-key material has been created for any live CCPC release; ephemeral test keys remain entirely local and disposable.

**No operational gates cleared:** The code does not change `VerifiedIdentity.backup_ready=False`, partial/encryption/quiescence evidence, Frappe v16 backup cleanup side effects, Docker privileged socket review, real image provenance or independently verified image IDs, MariaDB/file consistency, CIFS atomic publish tests, isolated four-artifact restore, monitoring/retention or encryption key escrow. No real release manifest or snapshot values are generated or committed. Do NOT merge dependent PRs #27/#29/#30, pull on DEVELOPMENT, build images, mount NAS, run backup/restore or change PRODUCTION based on these tests.

**Next suggested separate authorization gate:** Run an **exact PR #30 GitHub-blob combined offline test checkout** with this new verifier and existing complete policy, plus source review of revocation high-water persistence, key-trust distribution and the signing workflow. Only after these tests and separate owner authorization consider isolated disposable Docker/Frappe integration. Production changes require explicit additional approval, backups and rollback review.
