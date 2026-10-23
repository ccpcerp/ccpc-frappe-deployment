# Step 125 — Dedicated-host runtime identity verification (GitHub-only)

**Checkpoint date: 2026-10-23. STATUS: offline-reviewed implementation; NOT installed, invoked against any Docker host, linked to a backup job, accepted in DEVELOPMENT, or approved for PRODUCTION.**

Owner approved the explicitly proposed Step 125 **GitHub-only** work: develop and offline-test an independent runtime verification layer checking the correct server, Docker containers/services, site, image and storage volumes *before* considering a backup. This builds on [Step 124](DEDICATED-BACKUP-STEP124-CAPTURE-WRAPPER-REVIEW.md), [Step 123](DEDICATED-BACKUP-STEP123-IMPLEMENTATION.md) and the separate [Step 122 design](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/docs/ccpc-checkpoint-2026-10-10/docs/ccpc-project/DEDICATED-PRODUCTION-BACKUP-RECOVERY-DESIGN-2026-10-23.md). There was **no** permission to touch either physical CCPC host, execute Docker remotely or locally on CCPC infrastructure, enable NAS mounts, back up/restore ERPNext, merge, install a runner or schedule a job.

## Code scope and checked reference layout

The stacked draft PR #30 branch `feature/dedicated-prod-backup-safety-2026-10-23` now includes:

- `scripts/dedicated_backup_runtime.py`: **inert library**, direct invocation prints `NOT ENABLED` via SystemExit and does not inventory a host just by being imported.
- `tests/test_dedicated_backup_runtime.py`: **27 offline standard-library unittest cases**, built entirely around synthetic Docker inspection records and disposable local folders, with a mocked `subprocess.run`.
- The existing Step 123 and Step 124 code is unchanged, including the **unwired** `scripts/dedicated_backup_capture.py` runner and `scripts/dedicated_backup_core.py` publisher.

Repository `compose.yaml` (reviewed from this PR's parent) maps exactly one named `sites` volume to `/home/frappe/frappe-bench/sites` for `backend`; `overrides/compose.mariadb.yaml` maps `db-data` to `/var/lib/mysql` for `db`, with a MariaDB health check. `scripts/config.sh` pins Frappe v16.33.1 to Git SHA `988e54f3c4c291e2077a83809663f123731abe76`. No actual dedicated-host Docker project/volume/image IDs, running containers, site or site configuration were assumed to exist.

### Checks implemented

1. **Approved external expectations:** `ApprovedRuntime` must be independently populated with a reviewed Compose project, exact backend and database **immutable image IDs** (`sha256:...`), exact backend/database Compose config hashes, and matching project-scoped `<project>_sites` and `<project>_db-data` volume names. The verifier does **not** invent or learn trusted expectations by copying labels from Docker.
2. **Right host first:** `socket.gethostname` short name must equal `ccpcerp-prod`; wrong host aborts **before any Docker query**.
3. **Read-only local Docker inventory:** An allowlisted Docker CLI transport supports only `container ls`, `container inspect`, `image inspect`, `volume inspect`, with shell-free argv, 8-second subprocess timeout, ignored inherited `DOCKER_*` environment and explicit `--host unix:///var/run/docker.sock`. No `docker exec`, `compose up`, image builds, mounts, or write-capable Docker commands. Inspection output and secrets are **not printed**. However, access to the Docker socket itself is a privileged capability and the allowlisted transport is **not** a host security boundary; deployment must separately review operator privilege and the daemon socket.
4. **Compose provenance:** One and only one `backend` and one `db` container identified by project/service labels; Docker's shortened `ps` IDs must be confirmed as prefixes of the complete 64-char IDs from inspect. Require exact project/config-hash labels, expected immutable container image IDs, stable running state, nonprivileged, not host PID/network, healthy MariaDB. Ambiguous duplicates, missing or replaced services, inconsistent image/config IDs and unhealthy DB all fail.
5. **Image identity:** Each image inspect ID matches its owner-approved immutable expected ID. The backend image additionally **must declare** an `org.ccpc.frappe.sha` label matching the pinned Frappe SHA. This provenance label is **not known to be present in current build code**; without it, verification intentionally fails. An image label alone cannot cryptographically certify source authenticity. Image build/release attestation and labels require separate review/approval.
6. **Named-volume provenance:** Docker volume inspect names and Compose labels must match exactly; container mounts must consist of precisely the expected one read/write **volume** each at the fixed site/database destination. Other bind mounts (including Docker socket) or extra/unrelated volumes fail. The volume's canonical host directory is verified; its path must not pass through a symlink.
7. **Site metadata:** Check only that `<sites-volume-mountpoint>/ccpcerp.local` is a canonical directory and contains a nonempty, regular, single-link `site_config.json`. **Do not open, print or parse site configuration secrets.** This proves site-path presence only, not Frappe initialization, site-to-database linkage, credentials validity, installed app revision or a working website.
8. **No premature authorization:** `VerifiedIdentity` explicitly sets `writes_quiesced=False`, `no_partial_backup_filters=False`, `encryption_disabled=False`, and `backup_ready=False`, even on a fully matching **synthetic** runtime inventory. It is deliberately **not** a `CaptureAttestation` with all-green flags and is **not connected** to the Step 124 `capture_with_verified_runner`. No Frappe bench invocation or NAS publication is enabled.

### Offline tests

Executed **only** in disposable Python 3.13 tooling, not CCPC servers:

```text
cd /mnt/data/step125
python -m unittest discover -s tests -p test_dedicated_backup_runtime.py -q
Ran 27 tests in 0.035s
OK

python -m compileall -q scripts tests
# no output; succeeded
```

Test scenarios include correct synthetic backend and DB state with backup still denied, host mismatch before Docker, invalid/unapproved images/projects/volume names, duplicate or abbreviated container IDs, missing or duplicated backend, Compose project/config-hash mismatch, wrong image or missing source label, unready DB, privileged backend, volume name/labels/mount type or mount count mismatch, missing/symlinked site/config/volume parents, malformed/oversize inspect JSON, redaction of an injected fake password in Docker data, disallowing any write-capable Docker argv, and enforcing the local Docker socket (rejects Docker endpoint redirection). No actual Docker daemon, real MariaDB, ERPNext or Synology SMB was accessed.

**Tested-source matches GitHub** using local `git hash-object` and connected GitHub `fetch_file`:
- Module blob `d94648baf0aa6385cce04e4e45e49e0466a63e65`; SHA-256 `4e9dac03e6f09f1a759ea3e7627cb066876eac83e85f87b6936486c610f083dd`.
- Test blob `e4463e96a524a7c0fba2cd97ec5636cc0944095b`; SHA-256 `c2c9029c33f412dd22bf51e97bed7caf753b239673134315aac115817975d7ca`.

Prior Step 123/124 suites **previously** passed 33 tests and were unchanged. They were **not rerun together** with Step 125 during this checkpoint; do **not** report 60 tests as one combined executed suite, and do not equate mocking with real integration.

## Review findings and unresolved gates

- The **approved runtime manifest** with current project config hashes and true immutable image IDs has **not** been created. These cannot be populated before reviewed image build/release, nor taken uncritically from the same Docker daemon being attested.
- The backend image must be built with a reviewable immutable provenance label `org.ccpc.frappe.sha` (or an independently verified equivalent). The current image may not have that label; fail-closed behavior is intentional. An OCI image source label by itself does not prove that the image actually contains a specific Frappe commit.
- Docker label/config and site-file metadata are point-in-time observations. There is **no atomic hold of container IDs, image, volume mounts or site state** across future Frappe capture/publication. Need a separately designed stable workload boundary, reviewed race controls, privileges and live retry behavior.
- **Backup consistency / uploads and DB quiescence**, actual `bench backup --with-files` execution, full backup configuration/filter/encryption checks, safe secret/key recovery, available free space, output path translation to container filesystem, Docker daemon privilege minimization and vetted operator identity are still unresolved. Frappe's `delete_temp_backups()` behavior needs disposable integration tests before any backup execution. Site presence is not Frappe site health.
- Safe NAS publication (actual CIFS `renameat2` semantics, disconnected mounts, non-clobber, partial reconciliation), full restore and disaster recovery drill, monitoring, schedule and retention remain unapproved and untested. Old production and shared DEVELOPMENT must remain unchanged.
- Do not integrate this module into an executable runner or enable it in production based only on this synthetic test result.

**Next gate:** owner may approve a further GitHub-only review of runtime-attestation provenance and quiescence policies, or plan **non-executing** isolated DEVELOPMENT validation with explicit preservation of uncommitted work and shared infrastructure. No actual DEV pull/test or dedicated PRODUCTION deployment is implied by Step 125.
