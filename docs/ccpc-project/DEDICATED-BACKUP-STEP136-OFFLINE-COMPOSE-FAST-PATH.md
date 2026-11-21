# Step 136 — Offline Compose fast path (proposal; not execution approval)

**Prepared 2026-10-24 from the owner-supplied Ubuntu output and independently reviewed GitHub source.** This is a concise G1/G2 proposal for the named, isolated Hyper-V guest `CCPC-Step136-LAB` (`ccpc-step136-lab`). **No transfer, Docker installation, Compose invocation, guest network modification, VM operation, or production action is approved or reported by this file.**

## Evidence and current gate

- The operator's read-only Ubuntu `df -h /` showed `/dev/sda2`: **58G total, 5.6G used, 50G available, 11% used**. This is the **guest root filesystem** snapshot, not the Windows C: available storage or dynamically allocated VHDX growth.
- The operator's `command -v docker` / `command -v docker-compose` checks found **neither executable on guest PATH**. Do not assume an installed engine, plugin, running daemon or network access.
- Previously verified: static hostname `ccpc-step136-lab`, 4 GiB Hyper-V static assignment, 3.8 GiB guest-visible RAM / 3.4 GiB available and no swap used at the measured instant, private Hyper-V switch and no configured guest IP route/DNS at the last checks.
- **G0 PARTIAL. G1 source review complete but offline source staging pending. G2 Compose config/render NOT EXECUTED.** Extra free disk space is not evidence a full ten-service ERPNext stack fits available memory.

## Fast execution design — CLI-only, no Docker Engine or running services

**Use the official, checksum-verified Linux x86-64 *standalone Docker Compose v2 executable* (`docker-compose`), version >=2.24.4.** This standalone path is proposed because the guest has no `docker` CLI; `docker-compose config` is a client-side render and does **not require a Docker daemon**. Do not install Docker Engine, enable Docker, pull images or relax the Private switch merely to run config. A compatible, provenance-verified offline binary is still to be selected and staged; its exact version, official source URL, archive checksum and in-guest checksum remain **PENDING**. Do not trust an unpinned executable from arbitrary sources.

**Pinned GitHub input:** draft stacked PRs #27 `0bf8c6a2fdef5146344492c6ac1bfe4c25ac7b2f`, #29 `bd92ade7ac859b9f6b21b157bdc1629e93f4540c`, #30 `fd751ab7c39c252e469e1d59d6ebbb1408381061`; all three branches were rechecked unchanged in GitHub on 2026-10-24. Required exact PR #30 file blobs:

| Ordered input | Git blob SHA |
| --- | --- |
| `compose.yaml` | `752b86e1ba4c1977a2636b1916f6015771f4c28c` |
| `overrides/compose.mariadb.yaml` | `94e177c38707a40bdd2715287565c80e41c4f3d3` |
| `overrides/compose.redis.yaml` | `64bc05ac2e955719822718e5118a62d0c9771e24` |
| `overrides/compose.lan-production.yaml` | `3e65debe8d007b73d23f46f880cc53a182a19829` |
| **Last:** `overrides/compose.dedicated-pre-tls.yaml` | `14fd89a3c2371104f464964137483de9f4a35861` |

Also verify `scripts/config.sh` Git blob `32614da1044c768bd67dcb9b9491e7c48ff2653a` without **sourcing** unknown worktree files. Do not use `main` or a branch's moving tip as a substitute for the pinned PR #30 SHA. `!override` is required for the dedicated frontend port to replace the legacy LAN port.

**Proposed host-to-guest transfer:** Stage these **six non-secret source files** and the verified Compose executable on the Windows owner workstation, then transfer them to a new lab-only workspace using a **separately approved offline local host/guest channel**. First assess whether Hyper-V `Guest Service Interface` / Linux file-copy integration is already functional, using read-only inventory. If it is unavailable, propose a separately approved offline media transfer; **do not** toggle guest integration services, connect the VM to the Default Switch, enable a host bridge, add SSH, attach arbitrary VHDX media or mount a real CCPC share without a new operation-specific review. Serial text paste is suitable for small observations but not a substitute for authenticated, checksum-preserving transfer of a large binary. Keep production credentials/keys/dumps out of the lab.

## One approved future G2 run, not separate ad hoc command loops

Once G0 remaining applicable safety review, exact source/CLI staging and a **separate explicit G2 execution approval** are satisfied, the owner may run one reviewed, bounded, **config-only** test batch in an empty lab workspace:

1. Confirm Git blob SHAs after transfer, standalone CLI provenance/checksum, actual Compose version and exact five-file argv order; reject unknown `.env` / `COMPOSE_FILE` / `COMPOSE_PROFILES` inputs.
2. Use a unique lab-only project name and synthetic non-secret environment values, including an obvious dummy `CUSTOM_IMAGE`, `CUSTOM_TAG`, `DB_PASSWORD`, `FRAPPE_SITE_NAME_HEADER` and `HTTP_PUBLISH_PORT`. Isolate inherited environment variables; never read a real `.env`.
3. Render **dedicated** `docker-compose ... config --format json` with the five files in the verified order, save raw data only to owner-controlled restricted temporary storage, and check the **CMP-01 through CMP-12** cases in [Step 135](DEDICATED-BACKUP-STEP135-LAB-ISOLATION-AND-COMPOSE-RENDER-CHECKLIST.md). No `up`, `run`, `pull`, `build`, `exec`, `down`, `prune`, `bench`, database or network commands.
4. Specifically verify one and only one frontend publication `127.0.0.1:8080` TCP; expected `sites` and `logs` named backend volumes; named `db-data`; no DB/Redis published ports; healthcheck; expected ten services; nonempty synthetic DB password required. Run a **separate negative** config case with `DB_PASSWORD` unset and confirm render fails. Compare independent four-file legacy render, with **no legacy execution**.
5. Produce **one sanitized PASS / FAIL / BLOCKED summary** of CMP-01..12, engine version, exact SHA IDs and observed warnings. Do not paste raw JSON, password interpolations or unrestricted config output in GitHub/chat. A config-only PASS is **not** a runtime/container/volume/database validation.

**Approval boundaries:** Read-only host/guest inspection may continue within previous owner-approved scope; **offline source transfer, executable staging, actual config execution, network/VM configuration and any installation are distinct sensitive operation classes** and require their relevant explicit approvals. Stop and report G2 BLOCKED if a trustworthy standalone CLI or acceptable offline transfer channel cannot be established. Preserve the guest's existing two checkpoints and manual RAM/storage safeguards. No changes to `ccpcerpserver` DEVELOPMENT/PRODUCTION, `ccpcerp-prod`, NAS, DNS, GitHub review PR code or live credentials.

## Immediate efficient next owner verification (read-only)

On Windows Administrator PowerShell, inspect only the named lab's Hyper-V Guest Service Interface availability:

```powershell
Get-VMIntegrationService -VMName 'CCPC-Step136-LAB' |
  Where-Object Name -eq 'Guest Service Interface' |
  Select-Object VMName,Name,Enabled,PrimaryStatusDescription
```

This **does not enable** file transfer. Based on the result, choose one separately reviewed offline transport rather than performing more unrelated guest checks. This proposal is not a permission to run either transfer or Compose.
