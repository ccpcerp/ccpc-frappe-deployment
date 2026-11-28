# Step 135 — Disposable lab isolation specification and source-pinned Compose render checklist

**2026-10-23 | GitHub-only review/design milestone | NOT APPROVAL TO EXECUTE.**

Owner approved the Step 135 scope proposed in [Step 134](DEDICATED-BACKUP-STEP134-ISOLATED-INTEGRATION-ROLLBACK-PLAN.md): specify a **disposable, independently isolated** Docker/Frappe test environment and an **exact source-pinned** Docker Compose rendering checklist. This is a **documentation-only** gate, not G0 sign-off, G2 execution or authority to build, pull, start, stop, restore, freeze, deploy, schedule, configure secrets, mount the NAS or modify any CCPC host.

## A. Verified source baseline — freeze before any later test

Connected GitHub review confirmed the following OPEN/DRAFT/UNMERGED dependency chain on `ccpcerp/ccpc-frappe-deployment`:

| Review PR | Branch | HEAD reviewed | Status |
| --- | --- | --- | --- |
| [#27](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/27) | `security/dedicated-production-pre-tls-2026-10-23` | `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f` | draft; base `main` |
| [#29](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/29) | `security/dedicated-prod-external-env-2026-10-23` | `bd92ade7ac859b9f6b21b157bdc1629e93f4540c` | draft; based on #27 |
| [#30](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/30) | `feature/dedicated-prod-backup-safety-2026-10-23` | **`fd751ab7c39c252e469e1d59d6ebbb1408381061`** | draft; based on #29 |

At this Step 135 review, these source paths are verified at the **exact PR #30 head**:

| File in intended Compose evaluation order | Git blob SHA |
| --- | --- |
| `compose.yaml` | `752b86e1ba4c1977a2636b1916f6015771f4c28c` |
| `overrides/compose.mariadb.yaml` | `94e177c38707a40bdd2715287565c80e41c4f3d3` |
| `overrides/compose.redis.yaml` | `64bc05ac2e955719822718e5118a62d0c9771e24` |
| `overrides/compose.lan-production.yaml` | `3e65debe8d007b73d23f46f880cc53a182a19829` |
| **`overrides/compose.dedicated-pre-tls.yaml` — must be last** | `14fd89a3c2371104f464964137483de9f4a35861` |
| `scripts/config.sh` (chooses profile and exact file list) | `32614da1044c768bd67dcb9b9491e7c48ff2653a` |

**Do not silently substitute a current default branch or tag.** A later lab checkout must re-read these PR heads, compare all required file blobs and verify a clean working tree before any configuration interpretation. If any dependency branch changes, halt and refresh the reviewed source baseline and tests. Step 133's **135/135 exact-GitHub-blob synthetic/mock/static regressions** remain historical evidence; **Step 135 does not rerun them**.

The configured application source pins are Frappe `v16.33.1` / `988e54f3c4c291e2077a83809663f123731abe76`, ERPNext `v16.34.2` / `4048fb70e14d1843956fcdabb7c3cca75a1cbcdd`, CCPC app `cfcc19394a6646548f2b7050db040c8cf5ebafde`, patch `b543d14453d4370c6ddaf53bee8f8b786bf9199d5ce33182eb80aa5080e85ba1`, and overlay `13bfff41433c9ac380b9ed632911674b9b87f7e7cb728388912ed50c79c63d0e`. Source pinning **is not** a completed image build, container provenance check or approved release manifest.

## B. G0 — lab placement and minimum isolation specification

**Preferred boundary:** a disposable, independently owned VM on infrastructure **outside the old `ccpcerpserver` and new `ccpcerp-prod` hosts**, with its own kernel-visible Docker daemon, storage, networks and operator identity. A dedicated disposable cloud VM is acceptable **only after** its routing, access policy, cost exposure and disposal procedure are reviewed. A separate Compose project, container, Unix namespace or `docker context` that still targets the existing CCPC Docker daemon **does not qualify**. A VM resident on a shared physical CCPC production host is **not presumed isolated**; reject it unless a separate documented risk assessment and owner decision resolve the shared-infrastructure risks.

The owner must separately approve a **named** disposable target and its management access before even read-only environment inventory; Step 135 neither selects nor provisions a VM. The G0 isolation attestation must include:

| ID | Required design evidence and acceptance standard | Stop condition |
| --- | --- | --- |
| **ISO-01** | Lab host/VM ID, asset owner, intended lifecycle/expiry, location/trust zone, hypervisor/cloud isolation boundary, documented **separate** Docker daemon and storage. | Shared production Docker socket, reuse of `ccpcerpserver`/`ccpcerp-prod`, undocumented host ownership. |
| **ISO-02** | Network default-deny: no routable path to old/new CCPC servers, NAS management or SMB, production databases, internal Git/SSH credentials, or private business systems. DNS and IPv4/IPv6 reviewed separately. Egress only to individually approved package/image endpoints if a later pull/build is authorized. | Broad LAN bridge, host network, direct NAS/share reachability, default unrestricted egress, uncontrolled DNS/proxy tunnel. |
| **ISO-03** | No mounted CCPC SSH keys, NAS credentials, site configs, DB dumps, private/public business file archives, Docker socket of another host, agent tokens, home directories or connected cloud credentials. Synthetic non-secret configuration only; test-only keys generated in memory when required. | Any unreviewed credential mount or use of real production datasets. |
| **ISO-04** | Unique lab project/volumes/networks and storage paths; no privileged containers, Docker-in-Docker sharing a production daemon, host PID/network mode or unintended published ports. Rootful Docker/socket administration limited to explicitly authorized isolated lab operators. | Privileged host access, unexpected volume/bind, collision with real project/volume names. |
| **ISO-05** | Lab CPU/RAM/disk quota, maximum runtime, explicit resource owner, access logging/redacted evidence policy, rollback snapshot before state-changing tests, disposal and cost controls. | Unbounded storage/compute or teardown that could affect a non-lab resource. |
| **ISO-06** | An operator/reviewer sign-off sheet recording lab name and approved exact command class; inspection, `compose config`, image pull/build and service creation require **distinct** approvals. | Assumed authority from a prior documentation approval, anonymous operator or unspecified target. |

**Hard exclusion:** Do not use the old legacy NAS share `//192.168.50.132/erpnext_backups`, the new dedicated `//192.168.50.132/ccpcerp-prod_backups`, either CCPC host, production Docker socket, or real company data to validate G0/G2. Synthetic volume names must not be taken as evidence of real Docker volume provenance.

**Host identity:** The production runtime policy intentionally requires `ccpcerp-prod`, site `ccpcerp.local`, and `dedicated-pre-tls`. The isolated lab may exercise static Compose evaluation using a **test-only Compose project name** and synthetics, but must **not** spoof approved production identity to force `backup_ready=True`. Keep runtime release, approval and quiescence gates false in all fixtures; real host-identity acceptance is a separately approved later dedicated-host gate.

## C. G1 prerequisite — source and test workspace approval

Before a later lab render, require a review of the exact stacked dependency ordering, pinned full commit and blob SHAs in section A, clean checkout with no staged/untracked/uncommitted surprises, no `AGENTS.md` or other unreviewed agent instructions introduced as authority, approved dependency versions, and immutable evidence record. Step 133's full regression evidence is the existing baseline, **not** permission to skip a future test. No `reset --hard`, `git clean`, force push, branch switch or pull on shared DEVELOPMENT.

Do not use a production `.env`. The eventual isolated lab should create ephemeral **synthetic-only** values for `DB_PASSWORD`, `CUSTOM_IMAGE`, `CUSTOM_TAG`, `FRAPPE_SITE_NAME_HEADER`, `HTTP_PUBLISH_PORT` and any other required Compose substitutions; the exact value set must be owner/reviewer accepted as non-sensitive before command execution. Render output may contain the *synthetic* password; do not publish raw environment/config payloads as GitHub evidence. Never source the real production secrets to avoid an interpolation error.

## D. G2 — exact source-pinned Compose render checklist (NOT EXECUTED)

**Engine precondition:** Verified Docker Compose CLI version **2.24.4 or newer**, specifically because `!override` is present in both LAN and dedicated frontend overlays. This is a **minimum syntax feature**, not proof that a newer Compose engine has been tested with the CCPC configuration. The future operator must pin the actual Compose CLI version/digest and retain sanitized version evidence.

**Dedicated file precedence:** The sole approved proposed input order from `scripts/config.sh` is:

```text
-f compose.yaml
-f overrides/compose.mariadb.yaml
-f overrides/compose.redis.yaml
-f overrides/compose.lan-production.yaml
-f overrides/compose.dedicated-pre-tls.yaml
```

The `dedicated-pre-tls` file must be **last**, because its `frontend.ports: !override` replaces the LAN override, and its `db.environment.MYSQL_ROOT_PASSWORD` replaces the unsafe legacy fallback. The `backend.volumes` layer intentionally adds a project-scoped named `logs` mount at the prescribed destination alongside the existing `sites` mount. Legacy mode omits the dedicated file entirely; **do not deploy or change the legacy mode as part of this comparison**.

The **future operator** may propose an argv-style `docker compose` `config` render in a separate authorized isolated lab; Step 135 provides **no executable shell script** and does not run Compose. The renderer must use a **synthetic**, nonempty test-only `DB_PASSWORD` for positive checks, and an isolated unset-variable case for the required-field negative test. Treat expanded output as potentially sensitive and keep raw stdout/stderr private. Obtain structured **sanitized** comparison results instead of dumping interpolated environment variables to a PR, CI log or chat.

| ID | Proposed offline lab render check | Expected result | Fail/STOP if |
| --- | --- | --- | --- |
| **CMP-01** | Verify CLI/version, exact Git SHA/blobs, sorted list of input files and **ordered** `-f` operands against section A. | Version ≥2.24.4; **exact 5-file order**; no unseen `COMPOSE_FILE`/profiles or external override substitution. | Unknown engine, reordered/missing file, mutable code ref or hidden Compose file. |
| **CMP-02** | Render dedicated project using a **lab-unique** Compose project ID and synthetic nonempty required environment; inspect only sanitized structured service/port/volume fields. | Compose parses `!override`, provides expected services and no render error. | Parser rejection, interpolation from production `.env`, unexpected services, `extends`/host path or build side effect. |
| **CMP-03** | Inspect frontend **all** published port entries. | Exactly one published mapping to **host 127.0.0.1, port 8080, container port 8080, TCP**; no `0.0.0.0`, `::`, default `80` or extra mappings. | Public or extra listener, incorrect port/protocol, or host-IP normalization ambiguity not resolved by a reviewer. |
| **CMP-04** | Inspect backend mount targets and volume sources after actual Compose merge. | Exactly `sites`→`/home/frappe/frappe-bench/sites` and `logs`→`/home/frappe/frappe-bench/logs`, named volumes, expected writeability; no additional backend mounts. | Anonymous/bind/read-only logs/sites, duplicates, unwanted mount/path, project-crossing `external` or custom volume name. |
| **CMP-05** | Inspect DB mount and declared services. | One DB named `db-data`→`/var/lib/mysql`; `db` service MariaDB healthcheck present; Redis cache/queue and worker/scheduler services expected; any remaining image-declared anonymous logs mounts on **other** services explicitly recorded as unresolved for G5. | Extra DB/bind mount, disabled healthcheck, exposed DB/Redis port or unapproved worker volume. |
| **CMP-06** | Examine sanitized database password interpolation behavior with dummy nonempty value. | Dedicated DB has a **required nonempty `DB_PASSWORD`** substitution, not the base MariaDB `123` fallback; expected value compared in memory and **not logged**. | Empty/default credential accepted or real value printed into evidence. |
| **CMP-07** | Run a separate **negative render** in a sandbox with `DB_PASSWORD` unset/empty; keep failure output private and sanitized. | Compose render **fails before any container action** because of `${DB_PASSWORD:?…}` requirement. | Fallback to `123`, success without password or side-effectful retry. |
| **CMP-08** | Independent legacy **static/render comparison** using only first **four** source files and synthetic env. | No opt-in named backend logs overlay and no dedicated loopback override implicitly applied; identify legacy unsafe fallbacks only as **known legacy behavior, not validation/approval to deploy**. | Dedicated changes leaking into legacy default, accidental modification of existing legacy profiles or execution against active legacy host. |
| **CMP-09** | Inspect `config` project-scoped volume inventory and explicit network/port publications. | Expected named `sites`, `db-data`, `logs`, Redis queue data; no unexpected externally named volumes and no published MariaDB/Redis ports. | External volume, host bind, uncontrolled `name`, port, host network or privilege. |
| **CMP-10** | Check `scripts/config.sh` opt-in profile contract against the independently rendered file list. | Default `legacy-lan`; opt-in **only** `CCPC_DEPLOYMENT_PROFILE=dedicated-pre-tls`; bad value refused; last overlay exact. | Silently switching profiles, fallback to legacy on bad value, or unreviewed environment override. |
| **CMP-11** | Compare expected project-scoped Docker volume names, but **do not call this runtime validation**. | Static naming expectation `<lab-project>_sites`, `<lab-project>_logs`, `<lab-project>_db-data` and no project name shared with a CCPC environment. | Any assumption that a Compose config render alone verifies actual labels, mountpoints, Docker image identity or storage isolation. |
| **CMP-12** | Review error sanitization and reproduction manifest; confirm `config` does not trigger `up`, `run`, `pull`, `build`, `exec`, network creation or volume writes. | Test-only configuration resolution and redacted evidence, with explicit "no Docker runtime integration verified" label. | Unexpected image download, container/volume/network creation, plaintext secret in logs, undocumented side effects. |

**Exact comparison caution:** A YAML source description is **not** a rendered Compose project; the previous PyYAML merge-model tests cannot substitute for actual Compose v2 CLI acceptance. Conversely, a `config` PASS **does not** prove running container mounts, Frappe/database consistency, trusted image provenance or a recoverable backup. The production runtime verifier's exact volume IDs/config hashes must be checked **separately** in an independently approved later G5.

## E. Evidence bundle and fail-closed decision sheet

For every future CMP-* case, use a record with these **required fields** (no real credentials): `lab_target_id`, `operator`, `reviewer`, `approval_reference`, `isolated_host_assessment`, `repo`, `full_head_sha`, `parent_pr_heads`, `source_path_to_blob_sha`, `compose_version`, `ordered_compose_file_list`, `synthetic_variable_names_only`, `test_case_id`, `sanitized_actual`, `expected`, `pass_fail_blocked`, `timestamp_utc`, `no_runtime_side_effects_verified`, `rollback_or_abort_note`.

Record **BLOCKED**, not PASS, for unprovided owner approval, missing lab, missing independently validated isolation, inability to suppress sensitive output, a changed upstream commit or an unsupported Compose CLI. One failed negative test blocks advancement even if other tests pass. A changed source SHA requires a fresh reviewed revision; no auto-update or permissive expected-value edits.

**No test artifacts or generated output exist for G0/G2 as of Step 135.** Source-file hashes in section A and the historical 135 unit tests are separate evidence categories.

## F. Non-destructive abort, rollback and handoff

Before later lab provisioning, the owner must specify: fixture ownership; namespaced image/volume/network inventory; a protected synthetic baseline/snapshot; separate provisioning and teardown approvals; exact resource-specific cleanup list; and who verifies cleanup. For failure or interrupted work: **stop only the scoped lab gate**, preserve diagnostically necessary test artifacts in restricted storage, disable further tests and do not resume scheduled execution (none authorized). Never use `docker compose down -v`, `docker system prune`, broad `rm -rf`, unconditional Git reset/clean, or Docker commands on either CCPC server as shortcuts.

Even a successful disposable lab render or Frappe integration **cannot** modify dedicated `ccpcerp-prod`, active `ccpcerpserver`, the dedicated Synology `ccpcerp-prod_backups` share or legacy `erpnext_backups`. Physical DEVELOPMENT and PRODUCTION changes require distinct target-specific owner approval, clean Git review, backup and rollback.

## G. Step 135 disposition and next approval gate

**Deliverable:** GitHub documentation only: this review and a precise top-of-file update to [PRODUCTION-HOST-SETUP-HANDOFF.md](PRODUCTION-HOST-SETUP-HANDOFF.md). No code, PR feature branch, site master data or environment touched. No Compose CLI, test suites, Frappe, Docker daemon, release signer or NAS requests executed. Prior **135/135** exact-GitHub unit regression remains the last *test* outcome.

**Next proposed Step 136:** Obtain a **specific G0 laboratory-placement decision** and authorization to perform **non-mutating isolation inventory only**, on an explicitly named **disposable, separate VM**. Do **not** interpret generic approval of Step 135 or Step 136 as permission for G2 Compose execution, Docker image pulls/builds, bench, mounts, storage cleanup, DEVELOPMENT or PRODUCTION. If no disposable lab target exists or its access boundary is unclear, remain in design review and ask for the single missing target/owner datum before any tool action.
