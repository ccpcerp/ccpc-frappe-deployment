# Step 130 — Dedicated-only named logs Compose overlay and image-provenance requirements

**2026-10-23 · GitHub-only code and offline config review · NOT DEPLOYED, RELEASED OR BACKUP-READY.**

The owner approved the proposed scope for Step 130: **add an explicit named `logs` Docker volume for the new dedicated-host profile, review image provenance requirements, and accompany it with offline configuration tests**. There was NO approval to change, build, pull, deploy, restart or stop containers on either CCPC host; no NAS writes/mounts, MariaDB/ERPNext changes, `/etc/fstab`, cron, retention, production data migration, backup run or restore.

## Source review / branches

Read the current [GitHub-first workflow](https://github.com/ccpcerp/ccpc-frappe-deployment/blob/docs/ccpc-checkpoint-2026-10-10/docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), Step 129 handoff, `compose.yaml`, `overrides/compose.dedicated-pre-tls.yaml`, image `images/custom/Containerfile`, Frappe/ERPNext version pins in `scripts/config.sh`, and the Step 127/129 release and runtime validators.

Draft PR **[#30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30)** (`feature/dedicated-prod-backup-safety-2026-10-23`) was **OPEN/DRAFT/UNMERGED** before this change, based on OPEN/DRAFT/UNMERGED PR #29 `security/dedicated-prod-external-env-2026-10-23`, itself based on OPEN/DRAFT/UNMERGED PR #27. Latest initial PR #30 head was `f6ed6e5dbdfa8bf80e6ac0848821d145b178ed27`.

Compose upstream rules independently reviewed: [Docker's Compose merge rules](https://docs.docker.com/reference/compose-file/merge/) specify `volumes` uniqueness by **container target**, and [named volume specification](https://docs.docker.com/reference/compose-file/volumes/) distinguishes default project-scoped volumes from `external` or manually overridden names. Existing dedicated frontend uses `!override` requiring supported Compose version (2.24.4+); this step did not add another `!override`.

## Exact GitHub changes

- **`overrides/compose.dedicated-pre-tls.yaml`**, committed **`156ecd3b9478349522bbbf89f170d467e30f826c`** (verified Git blob `14fd89a3c2371104f464964137483de9f4a35861`). Only on the explicitly opted-in NEW dedicated pre-TLS overlay, sets:
  
  ```yaml
  services:
    backend:
      volumes:
        - sites:/home/frappe/frappe-bench/sites
        - logs:/home/frappe/frappe-bench/logs

  volumes:
    logs:
  ```
  
  The dedicated frontend loopback `127.0.0.1:8080:8080/tcp` and MariaDB strict `DB_PASSWORD:?` guard are unchanged. The base `compose.yaml` and other profiles are unchanged. The default project-scoped `logs` volume would be named `<project>_logs` under an approved Compose project and labeled `com.docker.compose.volume=logs`, matching Step 129's exact checker. Not `external`, not a host bind and no insecure custom `name`.
- **`tests/test_dedicated_compose_logs.py`**, committed **`8ce27d5c748484c2fe24fbbbd18302f9731cef3f`** (verified Git blob `8baf9a60b4b3588a7c441b2a454143651f9d6543`). This separate **offline PyYAML 6.0.3 + Python unittest** test suite parses the base and dedicated overlay (retaining the original Compose `!override` tag without executing it) and models the official Compose merge key by target. It asserts exact backend `sites` and `logs` mounts, project-scoped top-level `logs`, preservation of other profiles/loopback frontend/required DB password, and rejects anonymous, bind, unexpected/duplicate/wrong-target/extra/unsafe volume edits, unrelated services, and privileged overrides.

**Test outcome in isolated local tooling, not CCPC hosts:**

```text
cd /mnt/data/step130
python -m unittest discover -s tests -p 'test_dedicated_*.py' -q
----------------------------------------------------------------------
Ran 101 tests in 0.301s

OK
python -m compileall -q scripts tests
# PASS
```

The 101 tests comprise **85 unchanged exact-source mock regressions** from Step 129 plus **16 new Compose YAML/config regression tests**. Original eight Python blob SHAs matched their pinned GitHub sources, and the two changed/new files were fetched after GitHub commits and verified against the **identical locally tested Git blob hashes**. Tests use synthetic files and mocked Docker/Frappe, no secrets, no active Docker daemon and no NAS.

**Verification boundary:** Docker Compose CLI was **not installed** in the isolated environment; no real `docker compose -f ... config` / `--profiles` command, image build, container inspect, mount, volume creation or database operation was run. PyYAML + a carefully scoped merge model checks this one rule but is **not** a full Compose engine or proof that the actual opt-in deployment file chain renders as expected. Before any runtime integration, independently confirm the exact approved file order (including MariaDB/Redis/production LAN/dedicated-last overlays), Compose version support, project name, rendered mount/volume inventory and absence of accidentally published interfaces without revealing interpolated secret values. Obtain separate authorization before accessing DEVELOPMENT or NEW PRODUCTION.

## Image provenance review — requirements, not implemented release

Current `images/custom/Containerfile` confirms pinned Frappe/ERPNext/CCPC Git commits and patch/overlay content during build, but it **does not set** the image label `org.ccpc.frappe.sha` required by `scripts/dedicated_backup_runtime.py`. Its base `python:3.14.2-slim-bookworm` and DB `mariadb:11.8` are version **tags**, not approved immutable manifest digests. A Docker image label merely asserts a claim; it does NOT independently prove contents or a trusted build process. GitHub has no separately reviewed complete release manifest containing final image IDs/config hashes or an independently trusted approval digest at this milestone.

**Proposed provenance gate for separately authorized build implementation/review:**
1. Pin reviewed **base and MariaDB content digests** and track source, patch, overlay and build-context integrity; review third-party package / `curl` / `pip` and other mutable build inputs separately.
2. Add image metadata for `org.ccpc.frappe.sha` (and, as appropriate, reviewed ERPNext/CCPC/patch/overlay SHA labels) **only in a separately reviewed build change**, populated from validated build inputs in the final backend image, not operator environment shortcuts.
3. After an expressly approved isolated build, independently record full immutable backend and database **image IDs**, approved Compose project/service config-hash labels, actual volume identities, inspected base digests and build provenance, with a signed/reviewer-controlled **non-secret** release record. Never let the verified host self-approve its release by hashing its own unchecked manifest. Never commit secrets, site config, private SSH material, credentials or raw Docker environment.
4. Validate the release through a trusted out-of-band approval mechanism before passing `ValidatedRelease` to the Step 129 verifier. No `backup_ready=True` shortcut; verify DB/files quiescence and backup side effects through separate isolation tests.
5. Plan image and Compose rollback, declared/new volume lifecycle and named-log ownership/migration **without modifying existing anonymous volumes automatically**. Check whether configurator/workers/frontend/websocket need coordinated log mounts; current narrow overlay handles **backend only**, while other services using the image may still receive anonymous logs volumes. Never copy or delete logs/data without additional scope approval.

## Unresolved risks and explicit next gate

- **Runtime layout untested.** The dedicated profile is only source code; NEW `ccpcerp-prod` remains not serving ERPNext traffic. Creating/attaching a named log volume upon future approved `up` is a real filesystem and container change; not authorized here. Confirm actual permissions, labels, mount identity, log-sharing/rotation, other-service anonymous volumes and warnings in a separately approved disposable test.
- **No source provenance attestation.** Label and pinned digests/approved image/config identities are missing. Runtime verifier will continue to reject an image lacking the required label, even if named volume check can later pass.
- **Backup execution remains disabled.** No trusted writer quiescence, Frappe cleanup/encryption/filter test, database+attachments consistency, CIFS atomic publication, full isolated restoration, retention, alerting, external key escrow or scheduler.
- **Code safety boundary:** PR #27, #29 and #30 remain draft/unmerged; no DEVELOPMENT checkout/pull/exec, PRODUCTION change or old NAS `erpnext_backups` access was performed in Step 130.

**Next recommended separately approved Step 131:** GitHub-only review and implementation of *static* backend image-provenance labels tied to pinned build arguments with offline source tests, followed by independent release-manifest approval design. No Docker image build, Compose deploy, DEVELOPMENT or PRODUCTION change automatically follows. 
