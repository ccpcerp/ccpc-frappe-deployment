# CCPC ERPNext — four-Company isolated DEVELOPMENT/UAT and continuing Codex delivery

**2026-11-19, Asia/Manila. Owner decision:** Approved the recommended **separate clean four-Company DEVELOPMENT/UAT environment** instead of attempting bulk deletion of 21 test/demo Companies from existing MAIN `development.localhost`. Owner additionally said **"lets not give up codex"**: retain Codex as an active engineering/test path. **Status: architecture and host read-only preflight only; no new UAT host/bench/database/site created, no Codex agent launched, no changes to current DEVELOPMENT or PRODUCTION.**

## Priority revision — 2026-11-19: DEFER UAT provisioning to finish existing DEVELOPMENT first

The owner clarified that removing the 21 non-real Companies was a preference, **not a requirement** for the earliest safe completion of CCPC ERPNext. The approved four-Company isolated UAT architecture is **retained as a future option but its provisioning is now DEFERRED**. Do not treat the earlier UAT design or capacity PASS as authorization to create a bench/site/DB/Redis/volumes, or to clean existing Companies. This revision supersedes the previous document's 'next operator gate' as the active immediate action; earlier sections remain design/historical context.

**Delivery focus:** (1) resolve the existing MAIN DEVELOPMENT zero-worker/queued-job safety blocker with guarded read-only diagnostics, (2) complete and validate Phase 1 Withdrawal Slip → Material Issue → Stock Ledger/expense GL and intercompany controls, permissions, replay/rollback and the four agreed reports, using reviewed GitHub source and available disposable real Frappe/MariaDB integration tests, (3) return to persistent four-Company UAT only if necessary for release-grade acceptance and once its cost/benefit is justified. Existing four Company records (CCPC/RMC/GSL/WFC), 21 demo/test Companies and associated ledgers are to be preserved; no in-place deletion, migration, code switch or service changes are authorized by this pivot. Codex Cloud engineering continues independently; local Codex access remains blocked pending isolation controls.

**Owner-reported read-only host preflight completed:** x86_64; RAM 30.0 GiB total/26.5 GiB available; free home and Docker-root filesystem 682.5 GiB; Docker 29.1.3; Compose 2.40.3; existing Compose projects: `ccpc_codex_dev_agent` four containers, `frappe_docker` ten, `frappe_docker_devcontainer` four; new UAT project has zero containers; three Codex lab containers observed running. `HOST UAT READ-ONLY CAPACITY/IDENTITY: PASS` establishes resource inventory only, **not security isolation**; Codex agent process state is unknown and remains a separate read-only audit priority. No host modifications from that check.


## 1. Why isolated

- Existing MAIN has **25 Companies**, including the four actual Philippine PHP Companies: `Cagayan Corn Products Corporation` (CCPC), `Ricor Mills Corporation` (RMC), `GSL Realty Corporation` (GSL), `Woodland Farms Corporation` (WFC); non-group, no Company parent. GSL and WFC **already exist in MAIN**, so do not create duplicates there. `development.localhost` has original PR33 detached `25a7b6be1801a54f7ed39fef54f4ea4e3a1cea87` and protected untracked `AGENTS.md`; Phase1 release `55eb10b86a57de55a97e293a78228d9dd17b809a` is staged in a separate same-filesystem checkout.
- Remaining 21 MAIN Companies are **not delete-approved**; at least 167 direct Company field pairs were screened, with extensive Accounts, Warehouses, Departments, tax and party links, and several group/child Company trees. `_Test Company` alone has **two submitted Stock Entries** and **two noncancelled Stock Ledger Entries**. Preserve historical data and test fixtures, do not force-delete or use `Delete Company Transactions` or direct SQL.
- DEV `bench doctor` returned **0 online workers** and queued user-contact and route-index tasks for both site-scoped invocations. Phase1 switch/migration of shared DEV remains separately **ON HOLD**, not accepted just because the diagnostic command exited 0.
- Protected Nov19 two-site local/NAS backups and isolated SQL+files restore checks PASS; they do **not** prove full Frappe boot or restore into a new site.

## 2. Target architecture — independent, clean, persistent UAT

**Outcome:** A wholly separate, new, nonproduction Frappe/ERPNext **v16** UAT site/bench, isolated independently from the original MAIN and Integration2 sites and the broken `ccpc-integration.localhost`. Provision **only four Company masters** with the exact names/abbreviations above and country Philippines / currency PHP, after owner verifies actual legal setup; all four are separate legal Companies, not artificial parent/child groups. They may share an ERPNext bench but **not** the persistent old DEV bench, database, Redis, mounted `.ssh`, site configs, files, bind volumes, worker scheduler, or host Docker socket.

Architecture requirements:
1. A **uniquely named Docker Compose project or dedicated isolated VM/host** with non-overlapping volumes, database, Redis queue/cache, site, scheduler, workers, source checkout and backup destination. No shared `--site all`, original DEV volumes, legacy old production or dedicated PRODUCTION host access. Do not bind host ports/public DNS until reviewed and clearly scoped.
2. New UAT source pinned to the GitHub-reviewed CCPC app Phase1 release commit `55eb10b86a57de55a97e293a78228d9dd17b809a` **with no full PR33 merge**, while independently pinning compatible Frappe/ERPNext images and verifying installed-app hooks on a disposable blank site first. Any new UAT compose code is reviewed in GitHub before operator execution.
3. **Fresh installation/seeding** rather than cloning MAIN's 25-Company database and deleting 21 there. Start with safe synthetic test data and Company/Chart of Accounts review; do not copy actual payroll, business transactions, employees, customer details, credentials, Company mappings or signed Finance approvals into an agent environment. Configuration needed for Company-owned Accounts, Cost Centers, Warehouses, Department dimensions, Item Groups and chart structure requires a separate business-master checklist.
4. Create owner-acknowledged snapshot/restore of the **new UAT** before persistent finance/stock testing; make rollback specific to new UAT only. Test same-Company Withdrawal → Stock Entry → SLE/GL → Department costing, negative cross-Company issue/billing-disallowed, duplicate/replay, real distinct approval roles and report reconciliation **only after appropriate Finance mapping data is honestly approved**. Do not use synthetic approvals as real signoffs.
5. If hosting on `ccpcerpserver`, pass host identity/capacity, Docker networks/mounts, port collisions, and documented **network isolation** checks first. Historical `codex-dev-agent` has an offline synthetic Compose lab and firewall rules but remaining cross-bridge/online egress validation; it is **not an automatically safe host for this persistent UAT**. Prefer a separately isolated VM/host if local host segregation cannot be proven. Never touch `ccpcerp-prod` or legacy preserved old production on the shared host.
6. Existing DEV and new UAT must have **separate code updates and maintenance procedures**. New UAT acceptance does not authorize migration or cutover of the existing MAIN/Integration2 bench, and does not authorize PRODUCTION deployment.

## 3. Codex continues in parallel (owner reaffirmed)

**Do not abandon or replace Codex with endless owner terminal micro-checks.** There are two distinct Codex paths, both retained:
- **Codex Cloud, productive now:** Owner-established/published Codex Cloud environment for `ccpcerp/ccpcerp` with the reviewed release branch, code task in `CODEX-PHASE1-DEVELOPMENT-TASK.md`, tracking [app issue #36](https://github.com/ccpcerp/ccpcerp/issues/36). Use existing ChatGPT/Codex sign-in, ordinary task branch/PR and independently review tests/commits in GitHub. Authorized Codex actions include code analysis, test improvements, reviewable PRs, and *disposable/synthetic* Frappe/MariaDB integration testing where available. Do not grant it host SSH, NAS, production or shared DEV database. It does not automatically provision local UAT.
- **Local isolated Codex agent, HOLD pending security proof:** [deployment issue #38](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/38), `codex-dev-agent` reviewed lab and `CODEX-CROSS-BRIDGE-CANARY-REVIEW-2026-11-18.md` describe completed source/firewall work and remaining network/agent online controls. Do not run the old `ccpc-codex --sandbox danger-full-access` inside `frappe_docker_devcontainer-frappe-1`: it still has host `.ssh` and broad writable workspace mounts. Do not start the agent/online proxy or expose UAT/MAIN persistent credentials before missing isolation gates pass. The user's reaffirmation of Codex does **not** reinstate the **cancelled automated Codex report-to-GitHub publisher**, paid API integration, unattended/scheduled pipelines, or uncontrolled auto-merge.
- **Delivery:** Codex Cloud implements and tests reviewed source in GitHub; UAT independently verifies that precise source against a clean persistent four-Company setup; ChatGPT can inspect/implement agreed GitHub changes and review results in the active conversation. The connected GitHub integration does not itself start a Codex Cloud task.

## 4. First operator gate — host capacity and project topology READ ONLY

**Goal:** Decide whether there is sufficient space and isolation feasibility on the **old `ccpcerpserver` DEVELOPMENT host**, without touching any live service, filesystem data or firewall settings. Do not assume the old host is the final UAT host; an independent VM/host may be safer. No secrets, Docker mount paths, IPs or private volumes should be printed.

At `gani@ccpcerpserver` Ubuntu prompt, run exactly:

```bash
bash <<'HOST'
set -euo pipefail
test "$(hostname -s)" = ccpcerpserver && test "$(id -un)" = gani || {
  echo "STOP: WRONG HOST/OPERATOR"; exit 1;
}
dev=frappe_docker_devcontainer-frappe-1
test "$(sudo docker inspect --format '{{.State.Running}}' "$dev")" = true || {
  echo "STOP: ORIGINAL DEV IS NOT RUNNING"; exit 1;
}
test "$(sudo docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$dev")" = frappe_docker_devcontainer || {
  echo "STOP: WRONG DEV COMPOSE PROJECT"; exit 1;
}
echo "HOST ARCHITECTURE: $(uname -m)"
awk '/^MemTotal:/ {total=$2} /^MemAvailable:/ {avail=$2} END {
  printf "HOST MEMORY TOTAL GiB: %.1f\nHOST MEMORY AVAILABLE GiB: %.1f\n",total/1048576,avail/1048576
}' /proc/meminfo
df -Pk /home/gani | awk 'NR==2 {
  printf "HOST HOME FILESYSTEM FREE GiB: %.1f\n", $4/1048576
}'
docker_root=$(sudo docker info --format '{{.DockerRootDir}}')
test -n "$docker_root" && test -d "$docker_root" || { echo "STOP: DOCKER DATA ROOT UNAVAILABLE"; exit 1; }
sudo df -Pk "$docker_root" | awk 'NR==2 {
  printf "DOCKER DATA FILESYSTEM FREE GiB: %.1f\n", $4/1048576
}'
echo "DOCKER SERVER VERSION: $(sudo docker version --format '{{.Server.Version}}')"
echo "DOCKER COMPOSE VERSION: $(sudo docker compose version --short)"
echo "EXISTING COMPOSE PROJECT CONTAINER COUNTS:"
sudo docker ps -a --format '{{.Label "com.docker.compose.project"}}' |
  sed '/^$/d' | sort | uniq -c
echo "DEDICATED UAT PROJECT EXISTING CONTAINERS: $(sudo docker ps -a -q --filter label=com.docker.compose.project=ccpc_four_company_uat | wc -l)"
echo "CODEX LAB RUNNING CONTAINERS: $(sudo docker ps -q --filter label=com.docker.compose.project=ccpc_codex_dev_agent | wc -l)"
echo "HOST UAT READ-ONLY CAPACITY/IDENTITY: PASS"
echo "NO CONTAINERS/NETWORKS/DBS/SITES/SECRETS MODIFIED"
HOST
```

**STOP/interpret:** Any unexpected Docker/host identity or error means no new project creation. A PASS shows only capacity/project inventory; it does not prove port, network, egress or credential segregation. Verify those before provisioning. Do not run `docker compose up/down`, Docker pruning, user creation or new UAT DB/Company setup on the basis of this single check.

## 5. Remaining milestones

- Review host capacity/topology output and choose a deployment location without reusing current protected DEV/PROD/Codex volumes.
- Implement pinned isolated UAT Compose/bench deployment config and operator acceptance/rollback gates **in GitHub**, with static and CI validation before making host changes.
- Obtain/review the four real Company account setup choices and plan safe UAT-only test fixtures; test new UAT full site boot and independent backup/restore.
- Use Codex Cloud in parallel for isolated application tests and code PRs; review test result provenance. Local Codex lab remains held until verified network isolation.
- Maintain existing Phase1 shared-DEV source-switch HOLD until worker backlog is understood; UAT may progress independently without deleting MAIN test Companies or migrating shared DEV.

**PRODUCTION:** Never change dedicated `ccpcerp-prod` or protected legacy data/services on old host under this approval. Explicitly separate any future PRODUCTION rollout, backup/recovery and permission signoff.
