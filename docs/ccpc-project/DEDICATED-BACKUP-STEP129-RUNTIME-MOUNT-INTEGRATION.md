# Step 129 — Runtime verifier ↔ named logs mount policy reconciliation

**Date: 2026-10-23. GitHub-only implementation and offline tests. Not installed or production-ready.**

Owner approved the narrow follow-up to Step 128: reconcile the read-only Docker runtime verifier with the Step 127 approved-release and exact named `sites`, `logs`, `db-data` mount policy, then run mocked offline regressions. No Docker, Compose deployment edit, NAS mount, DEVELOPMENT pull, application/database access, scheduling, backups, restores or PRODUCTION action was authorized or performed.

## Verified branch and scope

- Stacked feature: [draft PR #30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30), branch `feature/dedicated-prod-backup-safety-2026-10-23`, based on open/draft PR #29, which is stacked on open/draft PR #27. Previous exact-GitHub eight-file offline regression at Step 128: **75/75 PASS** at `27b8344529e133887c040a12e104254390a9b6a6`. Neither dependency PR was modified.
- `scripts/dedicated_backup_runtime.py`: updated in commit **`16912fc09bcb5967a113f53825dc89b6f68584d1`**, verified blob **`49a9c3f9d882cf4296f87b21989e672f3ca3e9fc`**, byte-for-byte matching the locally tested code.
- `tests/test_dedicated_backup_runtime.py`: updated in commit **`1a8d6be3f49911e1e2e9541e07740cdfacf084a8`**, verified blob **`e009f0da977c6e242470de4a66144190923277be`**, byte-for-byte matching the locally tested test file.
- The Step 123 publication, Step 124 capture, Step 127 policy modules and their tests remain **unchanged**.

## Changed behavior

1. **Reviewed manifest input only.** The runtime verifier now accepts `dedicated_backup_policy.ValidatedRelease` instead of the previous independently duplicative `ApprovedRuntime`. The consumer is expected to call `validate_reviewed_release(raw, independently_approved_sha256=...)` using an **independently trusted, externally authorized digest**; it must not calculate that digest from the same untrusted manifest. The runtime checks manifest type, release identity, configuration/image IDs and that `trusted_runtime`/`backup_ready` flags remain false, before querying Docker. This is a schema/integration guard, **not cryptographic proof of approval**, and a caller can still construct a forged dataclass if it violates the documented trust contract. A signer/independent release-verification channel remains missing.
2. **Named volume inventory.** The verifier now requests exactly three **read-only Docker volume inspections**: `<project>_sites`, `<project>_db-data`, `<project>_logs`. It also checks each returned root is an accessible, non-symlink-resolved canonical directory (without reading secrets). It passes backend and DB mount arrays plus all three volume records into the Step 127 `verify_exact_mount_layout()` validator, which requires exactly:
   - Backend: `<project>_sites` RW volume at `/home/frappe/frappe-bench/sites` and `<project>_logs` RW volume at `/home/frappe/frappe-bench/logs`.
   - MariaDB: `<project>_db-data` RW volume at `/var/lib/mysql`.
   - Correct exact volume source paths, names, Compose `project`/`volume` labels; no anonymous, missing, duplicate, bind, read-only, unexpected or additional mounts. Any policy error is redacted into a nonsensitive `RuntimeRejected`.
3. **Read-only invariant and explicit lockout.** Docker CLI allowlist and forced local socket remain unchanged. It only calls inventory and inspect through an injected, trusted `query` callback, and it never starts or stops containers. After successful checks `VerifiedIdentity.backup_ready` remains permanently **False**; `writes_quiesced`, `no_partial_backup_filters` and `encryption_disabled` remain False. No Frappe executor, backup publisher or trusted quiescence attestation is wired. The runtime remains inert on direct invocation.
4. **Controlled negative tests and error handling.** Added checks for missing, anonymous, duplicated, unexpectedly extra, mislabeled, read-only or symlinked `logs` volumes, and nonreviewed/invalid manifest objects. Malformed/missing mocked Docker inspection records now return a sanitized `RuntimeRejected` rather than leaking a synthetic `KeyError`.

## Exact-code offline test result

In disposable local tooling **outside CCPC servers**, all prior PR #30 Python files were copied from the Step 128 workspace. All eight original files were verified against the previous GitHub blob identities *before* editing, and the two updated files' Git blobs were verified against the exact GitHub files *after* commit.

```text
cd /mnt/data/step129
PYTHONPATH=. python -m unittest discover -s tests -p 'test_dedicated_backup_*.py' -q
----------------------------------------------------------------------
Ran 85 tests in 0.078s
OK

python -m compileall -q scripts tests
# succeeded
```

Breakdown: Step 123 publisher 13, Step 124 capture 20, Step 127 policy 15, Step 125+129 runtime **37** (the prior 27 plus 10 new tests) = **85/85 PASS**. Synthetic inputs and mocked Docker; no CI status, real Docker/bench/MariaDB, NAS or actual filesystem backup/restore testing is claimed.

## Remaining blocks, risks and separate approval gates

- **Current Compose has NOT been changed.** `compose.yaml` maps `sites` for backend but does not explicitly map `logs` by name. The custom image declares `VOLUME sites,logs` and can cause a Docker-managed **anonymous** logs volume. The new verifier deliberately **fails closed on that layout**. A subsequent *separately approved* GitHub review/change must explicitly map named logs for the backend, decide whether all worker processes require similar mounts, and independently test the actual Docker behavior. Do not relax this guard to accommodate an anonymous volume.
- Dockerfile still lacks `org.ccpc.frappe.sha` label expected by Step 125 image validation; no approved immutable image and Compose config hashes, independent manifest approval service/signer or real deployed site/DB volume identity exists. Do not fill them with synthetic values from tests.
- Matching a runtime inventory is only a point-in-time observation; Docker socket is a privileged interface, container/mount TOCTOU is unresolved, and no verified site-to-database linkage, cross-artifact quiescence, backup filters/encryption, Frappe cleanup side effects, CIFS publishing semantics or isolated full restore has occurred.
- No runner, Docker build, Compose recreation, database write, backup, unmount, cron, retention, restore, PR merge or host-level action was performed. Existing old production `ccpcerpserver` and legacy Synology `erpnext_backups` remain out of scope.

**Next owner authorization gate:** Review a **GitHub-only** proposed explicitly named logs Compose overlay with safe service mount implications, and image provenance label/build manifest strategy, with offline config/source tests; do not deploy or build images without new consent. Any DEVELOPMENT/PRODUCTION operation requires separate explicit approval and verified Git/backup/rollback checks.
