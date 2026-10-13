# CCPC ERPNext — CURRENT HANDOFF

**Last verified update:** 2026-10-13 (GitHub connector, test output attachment, and operator terminal reports).  
**Purpose:** This is the **single rolling GitHub handoff** for CCPC ERPNext. Maintain **this same path** at meaningful milestones, during longer conversations before a thread limit is reached, and when the operator requests a handoff. Do not create a new dated Project Source attachment every time.

> **Read first in every new project conversation:** [GitHub-first development workflow](GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md), then this handoff, then verify relevant live GitHub branches and commits with the GitHub connection. The permanent ChatGPT Project Instructions define policy; older Project Sources and dated handoffs supply historical context only. If information conflicts, the most recently verified GitHub state takes precedence. If GitHub is inaccessible, report the inability to verify rather than treating old snapshots as current.

## DEVELOPMENT partial integration-site database and user confirmed absent — 2026-10-13

**Operator terminal evidence:** Following a successful DEV MariaDB local-root authentication using the container's configured `MYSQL_ROOT_PASSWORD` and a successful read-only `SHOW DATABASES`, the operator ran a piped Python/SQL query. The Frappe container read `db_name` and `db_user` from the partial `ccpc-integration.localhost/site_config.json` without printing the identifiers, and the separate **DEVELOPMENT** MariaDB container queried `information_schema.SCHEMATA` and `mysql.user`. Actual reported results:

```text
Partial database exists: False
Partial database user exists: False
```

These checks establish absence of the **configured identifiers** in the DEV MariaDB server at the time of the query; they do not prove there are no unrelated orphan objects. The prior TCP root authentication failure (1045) did not prevent local socket authentication with the configured container root password. The partial site directory remains on disk. No database write, user creation, site deletion, restart, retry, or PRODUCTION operation occurred.

**Next safe decision:** Preserve the partial directory while planning controlled new-site recovery. Do not run `bench new-site --force`, remove files, or overwrite the existing DEVELOPMENT site. Consider choosing a *new, unique* test-site name and new DB identifiers rather than deleting the partial site, after a read-only collision check. Any actual new-site command requires a reviewed, prompt-safe credential procedure; ensure the administrator secret used is accepted from the DEV Frappe network, not merely through the local MariaDB socket. No financial integration tests or PRODUCTION changes authorized.

## DEVELOPMENT MariaDB root login from Frappe container rejected — 2026-10-13

**Operator-reported read-only authentication test:** The operator executed the approved interactive Python `MySQLdb.connect(host="mariadb", user="root", passwd=getpass.getpass(...))` from the **DEVELOPMENT Frappe** container. It returned `Database connection failed. Error code: 1045` (MariaDB access denied), before either `information_schema.SCHEMATA` or `mysql.user` SELECT could run. **Partial test database/user existence remains unverified**. The root password was not shown in the terminal transcript and must not be requested, printed, logged or committed. A 1045 can reflect wrong credentials **or** a root-account host/login restriction, so do not assume the operator entered the wrong secret.

**Next one read-only diagnostic:** On the Ubuntu host, check if the **DEVELOPMENT MariaDB container's local Unix socket** permits OS root to connect as MariaDB root without supplying or printing a password. Use only `frappe_docker_devcontainer-mariadb-1` and a harmless `SELECT 1`, suppressing any auth/error details:

```bash
docker exec --user root frappe_docker_devcontainer-mariadb-1 sh -lc '
if mariadb --protocol=socket --user=root --batch --skip-column-names --execute="SELECT 1" >/dev/null 2>&1; then
  echo "DEV MariaDB local socket root login: available"
else
  echo "DEV MariaDB local socket root login: unavailable"
fi
'
```

This does not modify databases or use production containers; if unavailable, stop and verify the **DEV-only** MariaDB administrator credential source and host-access policy through sanitized inspection, never dumping env vars/secret contents. No new-site retry, `--force`, deletion, password reset, rollback, migrations or real financial integration tests approved. Partial `ccpc-integration.localhost` site directory and config remain present, distinct configured DB name/user from `development.localhost`; no successful MariaDB object creation verified. Earlier approved DEV four-part backup format checked, not restore-tested. If the mistakenly entered superuser name was a real password, treat as exposed and plan controlled rotation after proper credential ownership identification, without repeating it.

## DEVELOPMENT partial site DB identifiers checked without disclosure — 2026-10-13

**Operator-provided read-only results:** Within the DEVELOPMENT Frappe container, read (but did **not** print) `db_name` and `db_user` fields in the partial `sites/ccpc-integration.localhost/site_config.json`; compared its database name to persistent `development.localhost`. Results:

```text
1. Partial site has DB name: True
2. Different from existing DEVELOPMENT DB: True
3. Partial site has DB user: True
```

The partial site has its own *configured* DB name/user, distinct from the persistent site's DB name; **none of these booleans proves that a database or user was actually created**. The original creation failed on MariaDB authentication during Frappe's `create_user -> get_current_host`, before the ordinary database-creation step, making absence plausible but not yet independently verified. Neither partial files nor existing site data were deleted or modified by this check; PRODUCTION untouched.

**Next read-only preflight proposal:** Query **only** the DEVELOPMENT MariaDB service `mariadb` via an interactive Python helper in `frappe_docker_devcontainer-frappe-1`, reading partial config names privately, prompting with `getpass` for MariaDB DEV root password (never in command/history/chat), and querying `information_schema.SCHEMATA` for the partial DB's existence without printing any schema names. If authenticated, optionally query `mysql.user` for the partial DB user's existence; both are SELECT only. Stop on auth error; no password logging, privilege changes, forced site recreation, rollback, or cleanup. This will enable a separately authorized safe partial-site recovery plan. If earlier user-entered SQL-username value was a real password, treat as disclosed and plan rotation separately, not in GitHub.

## DEVELOPMENT partial integration-site directory observed — 2026-10-13

**Operator-reported results after failed approved site creation:** The terminal returned `Aborted!` and prompt `gani@ccpcerpserver` after declining Frappe's rollback, then a read-only `find` of `sites/ccpc-integration.localhost` inside `frappe_docker_devcontainer-frappe-1` reported that the site path **exists** and contains **`logs`, `locks`, `private`, `site_config.json`, `public`**. Do not print/read that JSON raw because it can contain credentials; no secrets are reproduced in this handoff. Successful site creation, separate DB creation, or app installation **NOT verified**. Preserve any partial files; **no `rm`, rollback, `--force`, re-run of `new-site`, migrations, or PROD changes** are authorized at this moment.

**Source check:** Frappe version-16 GitHub `frappe/installer.py` first creates site directories and calls `make_conf` before `setup_database`. MariaDB `setup_database` calls `create_user` before `create_database`. The actual traceback occurred in `DbManager.create_user -> get_current_host -> self.db.sql("select user()")` at MySQL authentication. This strongly suggests **the database creation step was not reached**; it is nevertheless unsafe to assert there are no partial DB artifacts without an independent check.

**Next safe one-step read-only inspection** for operator on Ubuntu host: compare only whether `db_name` is configured for partial site and whether it matches the existing site, without printing names or passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
./env/bin/python -c "
import json
from pathlib import Path
root = Path(\"sites\")
old = json.loads((root / \"development.localhost\" / \"site_config.json\").read_text())
partial = json.loads((root / \"ccpc-integration.localhost\" / \"site_config.json\").read_text())
name = partial.get(\"db_name\")
print(\"Partial site has DB name:\", bool(name))
print(\"DB name differs from existing DEVELOPMENT:\", bool(name) and name != old.get(\"db_name\"))
print(\"Partial site has DB user:\", bool(partial.get(\"db_user\")))
"
'
```

Only boolean results are displayed. If the partial DB name unexpectedly matches the persistent site, STOP; if it differs, proceed with separately planned **read-only existence check** of MariaDB objects in the DEVELOPMENT DB service. Never include passwords in shell history/chat. Determine a safe, exact plan for either restoring a known empty test-site creation or renaming to a new unique test site; any partial artifact deletion needs specific review/authorization. If credential entered as DB username was a real secret, treat it as exposed and arrange safe rotation, preferably not during testing setup.

## DEVELOPMENT integration site creation halted on MariaDB authentication — 2026-10-13

**Operator-reported failed interactive setup** using the previously approved new-site command **only in DEVELOPMENT**: `docker exec -it --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '... bench new-site ccpc-integration.localhost --db-host mariadb --db-type mariadb'`. The Frappe CLI prompted `Enter mysql super user [root]:`. **A value other than `root` was entered at the username prompt**. **Do not copy that value here or into GitHub**, as it resembles a credential and was included in user-shared terminal output. Subsequent password prompt and trace reported `MySQLdb.OperationalError: (1045, "Access denied for user [REDACTED] from DEV-container network")`. Frappe then displayed the interactive prompt `Site creation failed, do you want to rollback the site? [y/N]:`.

**Immediate safety response:** Instruct operator to press **Enter** to choose the default **No**, avoiding automatic rollback/cleanup before inspecting possible partial site artifacts. Do **not** retry or run `--force`; do not assume the failed attempt left nothing. The normal MariaDB administrator username is `root`, with its password entered separately and privately. If the accidentally entered username was a real password, it is exposed in chat transcript and requires **carefully planned credential rotation**, without printing it again.

**Current status:** New site and its DB/app installation **NOT verified as successful**. No further database changes, site rollback, cleanup or real integration tests authorized pending operator report of prompt completion, read-only inspection of `sites/ccpc-integration.localhost` artifacts, and cautious handling of possible partial DB objects. The last successful preflight was an October 13 four-file DEV backup with format checks; `development.localhost` and all PRODUCTION data must be preserved. Approval to create a new DEV site did not grant approval to delete ambiguous partial artifacts or change production.

**Next operator step after returning to shell:** run a read-only presence check **within the DEV Frappe container**, showing only directory existence and filenames, not any site-config contents or passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
if [ -e sites/ccpc-integration.localhost ] || [ -L sites/ccpc-integration.localhost ]; then
  echo "Integration site path exists (partial setup possible)"
  find sites/ccpc-integration.localhost -maxdepth 1 -mindepth 1 -printf "%f\n"
else
  echo "Integration site path absent"
fi
'
```

Then review Frappe installer state/rollback semantics before issuing any recovery or repeat creation command. Site creation may have generated a configuration file containing secrets; never print it. **PRODUCTION untouched in reported operation.**

## Operator approved isolated DEVELOPMENT integration site setup — 2026-10-13

**Explicit operator approval:** User replied **"Approved"** after being asked: "Do you approve creating `ccpc-integration.localhost`, with its own new DEVELOPMENT database and Frappe, ERPNext, and CCPC applications?" This approval covers **test-site/database creation and installing these applications in the existing DEVELOPMENT bench only**. It **does not authorize** financial transaction tests, modifying the persistent `development.localhost`, a `bench migrate` on that existing site, deletion/cleanup of existing sites or data, Docker restarts, copying production records, or **any PRODUCTION changes**.

**Preflight verified in active conversation:** DEV Frappe DB configured host `mariadb`; alias belongs to `frappe_docker_devcontainer-mariadb-1` on network `frappe_docker_devcontainer_default`, whereas PROD DB `frappe_docker-db-1` is on `frappe_docker_default`. MariaDB volumes separate. Only persistent existing DEV site is `development.localhost`. Fresh four-part DEV backup from October 13 passed gzip/tar/JSON format checks but is not restore-proven. Application review branch tip `806fa23516490ec7beefcff03a1baa09d722120e`; 155/155 combined mocked unit tests passed on DEV. Live Frappe `bench new-site --help` confirmed `--db-host`, `--db-type`, `--install-app` and credential prompt options.

**Safe staged procedure:** From host run guarded creation in **DEVELOPMENT Frappe container** `frappe_docker_devcontainer-frappe-1` as `frappe` user, from `/workspace/development/frappe-bench`: check `sites/ccpc-integration.localhost` does not exist (including symlink); run `bench new-site ccpc-integration.localhost --db-host mariadb --db-type mariadb` **without** `--force`, `--db-name`, inline admin/root passwords, or `--install-app` (stage app installations separately). Frappe chooses a new database name and prompts for passwords. Operator should enter prompts privately and **not paste secrets in chat**. Inspect terminal output and successful site creation before installing ERPNext then CCPC into **the new test site only** with explicit `--site ccpc-integration.localhost`. Stop if database provisioning fails, Frappe mentions an existing site/database, or an unexpected environment appears.

**Status:** Approval granted; creation **not yet observed**. Only actual operator terminal output can confirm site/database creation. No real transaction tests authorized. This approach provides logical site/database isolation on shared DEV infrastructure, not physical isolation.

## DEVELOPMENT Frappe new-site CLI options inspected — 2026-10-13

**Operator-provided read-only CLI help output:** On the Ubuntu host the operator executed `bench new-site --help` inside `frappe_docker_devcontainer-frappe-1` at `/workspace/development/frappe-bench` and filtered the help for database/admin/install flags. Verified flags include `--db-name`, `--db-password`, `--db-type [mariadb|postgres|sqlite]` (MariaDB default), `--db-host`, `--db-port`, `--db-root-username` / `--mariadb-root-username`, `--db-root-password` / `--mariadb-root-password`, `--admin-password`, `--install-app`, `--setup-db / --no-setup-db`, `--db-user`, and `--force`. Do **not** use `--force` or pass secret/password arguments in shell commands or history.

**Proposed operation (explicit operator authorization still required):** Prepare dedicated test site `ccpc-integration.localhost` and a distinct new MariaDB schema/user on the **DEVELOPMENT** service `mariadb`, with Frappe/ERPNext/CCPC installed using currently reviewed app checkout `review/intercompany-approval-failure-tests` at last verified commit `806fa23`. Do not copy production or existing persistent DEV business data, do not change default bench site, and use synthetic fixtures for later integration testing. Site creation/app installation writes to the DEV database server and filesystem, can consume CPU/RAM/I/O on the physical host shared with production, and is **not approved by the earlier DEVELOPMENT backup-only authorization**. Explicitly check for site/database naming collisions and password-prompt behavior; avoid displaying/root credentials. Installing apps and executing any test-suite writes must be staged, observed and separately approved when necessary.

**Verified prerequisites:** Only `development.localhost` was enumerated in DEV bench; effective `db_host` was `mariadb`; the DEV Frappe/MariaDB containers share network `frappe_docker_devcontainer_default` with matching `mariadb` alias; PROD MariaDB is on `frappe_docker_default`. DEV/PROD named DB storage volumes are different. Fresh DEV four-part backup `20261013_083457-development_localhost` was created following explicit backup approval and passed nonempty, gzip, tar, JSON syntax checks (not restore-tested). 155/155 mocked unit tests passed together on app review branch `806fa23`. No site creation, data-altering tests or PRODUCTION changes yet.

**Next action:** Ask operator to explicitly approve or reject the creation and app installation of the proposed DEVELOPMENT-only test site/database. If approved, prepare a safe, prompt-driven, collision-checked command sequence **one step at a time**, avoiding plaintext credentials in CLI history; proceed to real transactional/concurrency test plan only after another risk review, backup and explicit approval.

## Live DEVELOPMENT/PRODUCTION Docker network boundaries verified — 2026-10-13

**Operator-provided Docker host read-only inspection** of network names and aliases (no environment variables or secrets):

```text
/frappe_docker_devcontainer-frappe-1
  network=frappe_docker_devcontainer_default aliases=[frappe_docker_devcontainer-frappe-1 frappe]
/frappe_docker_devcontainer-mariadb-1
  network=frappe_docker_devcontainer_default aliases=[frappe_docker_devcontainer-mariadb-1 mariadb]
/frappe_docker-db-1
  network=frappe_docker_default aliases=[frappe_docker-db-1 db]
```

**Confirmed:** The DEVELOPMENT Frappe container and its MariaDB share `frappe_docker_devcontainer_default`, with the MariaDB alias `mariadb` matching effective `development.localhost` DB host. The checked PRODUCTION MariaDB container is on separate `frappe_docker_default`, without an observed connection to the DEV network. Separate live MariaDB storage volumes were previously verified (`frappe_docker_devcontainer_mariadb-data` vs `frappe_docker_db-data`). This **does not guarantee full host-level, credential, or network segmentation**: Docker host/kernel/storage are shared and privileged processes can affect both stacks.

**Readiness:** Persistent `development.localhost` was the only configured site found in the DEV bench. Fresh, explicitly approved DEVELOPMENT four-part backup `20261013_083457-development_localhost` was completed and passed four-file nonzero, gzip, tar and JSON format checks; **no restore rehearsal** has occurred. Combined 155/155 mocked Python tests passed on application review branch `review/intercompany-approval-failure-tests` at `806fa23`. No real MariaDB invoice rollback, transaction, concurrency or schema integration test has run.

**Proposed test isolation plan — not approved/executed:** Create a distinctly named **DEVELOPMENT-only disposable test site** (e.g. `ccpc-integration.localhost`) with **its own new MariaDB database**, reusing only the DEVELOPMENT Frappe bench and MariaDB service. Do not copy persistent DEV or PRODUCTION business data, do not change bench default site or existing `development.localhost` DB, and do not perform migrations on the persistent site. Use synthetic fixtures. Review permissions, storage overhead, Frappe installation/bootstrap requirements, test runner behavior, cleanup, and restoration/recovery strategy. A site within the same DEV bench/database server is **logical isolation only**, not a separate physical server or dedicated MariaDB daemon; broader isolation would require a separate Docker project and DB volume. Request explicit owner approval for new-site/DB creation and separately review/approve any database-changing integration tests, with stop-on-error and no destructive cleanup.

**Next safe read-only step to verify command flags before a site creation proposal:** Run `bench new-site --help` **only** in the DEVELOPMENT container, filtering output for database and administrative options; do not provide or print passwords:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
bench new-site --help | grep -Ei -- "db-|database|mariadb|admin|install" | head -n 35
'
```

After reviewing available options, propose the precise site-creation command and seek separate approval. Do not create site/DB now or touch PRODUCTION.

## Read-only DEVELOPMENT effective database endpoint — 2026-10-13

**Operator-provided output** from a read-only merge of `sites/common_site_config.json` with `sites/development.localhost/site_config.json` inside `frappe_docker_devcontainer-frappe-1`. Command printed ONLY endpoint metadata, no config secrets:

```text
DEVELOPMENT DB host: mariadb
DEVELOPMENT DB port: [default]
```

This is consistent with Docker DNS/service-name lookup to a MariaDB service on the DEVELOPMENT container's network. The default MariaDB/MySQL TCP port is generally 3306, but that was **not explicitly configured** in the files checked. **Database network identity/isolation has not yet been independently confirmed** by live Docker networking inspection. Previously verified DEV and PROD containers have separate named MariaDB data volumes; they still share the Ubuntu host and Docker daemon. Persistent DEV `development.localhost` is the only configured site found, and its fresh Oct 13 backup passed nonempty/gzip/tar/JSON format checks but has not been restore-tested. 155/155 mock tests passed together on review commit `806fa23`.

**Next one-step read-only operator action:** On Ubuntu host, inspect just network names/aliases for the DEVELOPMENT Frappe app container, DEVELOPMENT MariaDB and PRODUCTION MariaDB, **without opening environment variables, site configs or credentials**:

```bash
docker inspect --format '{{.Name}}{{range $name, $net := .NetworkSettings.Networks}}{{printf "\n  network=%s aliases=%v" $name $net.Aliases}}{{end}}' \
  frappe_docker_devcontainer-frappe-1 \
  frappe_docker_devcontainer-mariadb-1 \
  frappe_docker-db-1
```

Confirm DEV Frappe and DEV MariaDB share the relevant network and `mariadb` alias, while PROD MariaDB is on a separate network. Distinct networks and volumes lower risk but are **not complete protection** against host-level effects or privileged access. Do **not** yet create a new site/database, run database-changing integration tests, migrate, restore or touch production. An isolated site-and-database test plan requires explicit approval after further review.

## DEVELOPMENT site inventory — only persistent site exists (2026-10-13)

**Operator-provided read-only output:** A command in `frappe_docker_devcontainer-frappe-1` enumerated site directories containing `site_config.json` in `/workspace/development/frappe-bench/sites`. Its **only result** was:

```text
development.localhost/
```

This confirms there is **no preexisting second Frappe site in this DEVELOPMENT bench** based on the on-disk site directory check. `development.localhost` contains persistent DEV data and **must not be regarded as disposable**. To validate actual MariaDB invoice rollback and concurrency safely, first design a dedicated **new isolated integration-test site and distinct DEV test database**, review connectivity, fixtures and cleanup/rollback procedures, and request explicit user approval before creating any site/database or running tests. Do not use production databases or copies of production data. The fresh four-part October 13 DEV backup successfully passed gzip/tar/JSON syntax checks but is not restore-proven.

**Next one-step read-only preflight:** Review the **effective DEVELOPMENT site DB host/port only**, merging common and site JSON configuration, without printing database name, passwords or other configuration. Execute on the Ubuntu host:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit 1
./env/bin/python -c "
import json
from pathlib import Path
base = Path(\"sites\")
common = json.loads((base / \"common_site_config.json\").read_text())
site = json.loads((base / \"development.localhost\" / \"site_config.json\").read_text())
effective = {**common, **site}
print(\"DEVELOPMENT DB host:\", effective.get(\"db_host\", \"[not set]\"))
print(\"DEVELOPMENT DB port:\", effective.get(\"db_port\", \"[default]\"))
"
'
```

A successful result identifies the configured endpoint only, **not guaranteed isolation**; separately check the Docker networks before site creation. This operation reads two DEV JSON files and prints only non-secret endpoint metadata. No DB or PROD modifications authorized. App review branch remains at verified commit `806fa23516490ec7beefcff03a1baa09d722120e` with 155 combined mocked unit tests passing.

## Fresh DEVELOPMENT backup files verified — 2026-10-13

**Operator-reported validation run** from the Ubuntu host against the approved October 13 **DEVELOPMENT-only** site backup `20261013_083457-development_localhost`, via `docker exec --user frappe frappe_docker_devcontainer-frappe-1`. The shell command checked that each of four expected files is nonempty, then ran `gzip -t` on `-database.sql.gz`, `tar -tf` on **uncompressed** `-files.tar` and `-private-files.tar`, and `python -m json.tool` on `-site_config_backup.json`; it did not print secrets or extract files. The observed output was:

```text
DEVELOPMENT fresh backup format checks: PASS
```

**Verified scope:** existence/nonzero size, gzip integrity, tar archive readability, JSON syntax for all four artifacts in the fresh DEV backup set. This does **not** prove a valid full SQL restoration, database transactional consistency, off-host availability or recovery viability. The backup is on the shared physical server. No PRODUCTION change, migrations, Docker recreation, or database-changing integration tests were executed.

**Current milestone:** Application review branch `review/intercompany-approval-failure-tests`, commit `806fa23`, previously passed **155/155 mocked Python unit tests in one combined run**. DEV and PROD MariaDB volumes were independently distinguished by read-only live Docker inspect. Before any **real** Frappe/MariaDB transactional/concurrency tests, plan and authorize a **separate test site/database** and independent fixtures/rollback; do not run `bench run-tests` directly against persistent `development.localhost` or use production business data.

**Next low-risk read-only operator step:** Enumerate the existing site directories in the DEVELOPMENT bench **without reading site config contents**, so a unique isolation plan can be designed without colliding with existing sites:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit
for d in sites/*/; do
  [ -f "${d}site_config.json" ] && printf "%s\n" "${d#sites/}"
done
'
```

The results list site names only (no database passwords). Decide whether any site is available for isolated testing from explicit ownership/usage evidence; **do not assume a site is disposable**. Then document/review the new test site's database connection, backups, fixtures, migration and rollback procedure and request explicit operator approval before creating or modifying anything.

## Approved fresh DEVELOPMENT backup completed — 2026-10-13

**Explicit operator approval** was obtained in chat to create a fresh backup **only** for the persistent DEVELOPMENT Frappe site `development.localhost`. The operator ran on Ubuntu:

```bash
docker exec -it --user frappe \
  frappe_docker_devcontainer-frappe-1 \
  bash -lc 'cd /workspace/development/frappe-bench && bench --site development.localhost backup --with-files'
```

**Operator-provided successful output**, reporting backup summary at `2026-10-13 08:34:58.481811` and final `Backup for Site development.localhost has been successfully completed with files`:

- `sites/development.localhost/private/backups/20261013_083457-development_localhost-site_config_backup.json` — **234 B**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-database.sql.gz` — **1.6 MiB**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-files.tar` — **10.0 KiB**
- `sites/development.localhost/private/backups/20261013_083457-development_localhost-private-files.tar` — **20.0 KiB**

Unlike the October 9 `.tgz` file archives, this fresh October 13 backup has **uncompressed `.tar` public/private file archives**; therefore validate with `tar -tf` (no gzip flag). **Actual existence, compression/readability, complete database contents, and restore usability have not yet been independently verified after the completed backup command**. Backup is in local DEV site backup directory on host-shared storage, not demonstrated off-host. No database-changing tests, migrations, restore operations, or PROD actions were requested or reported.

**Next one safe, read-only operator action** on the Ubuntu host: validate all four new DEV backup artifacts inside the DEVELOPMENT Frappe container, checking nonzero files, gzip CRC, tar listings and config JSON syntax without printing config:

```bash
docker exec --user frappe frappe_docker_devcontainer-frappe-1 bash -lc '
cd /workspace/development/frappe-bench || exit
B=sites/development.localhost/private/backups/20261013_083457-development_localhost
for suffix in database.sql.gz files.tar private-files.tar site_config_backup.json; do
  test -s "${B}-${suffix}" || exit 1
done
gzip -t "${B}-database.sql.gz" &&
tar -tf "${B}-files.tar" >/dev/null &&
tar -tf "${B}-private-files.tar" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEVELOPMENT fresh backup format checks: PASS"
'
```

Even when these checks pass, do **not** represent them as a tested restore or database transaction-consistency verification. Before real concurrent billing approval/rollback experiments, review isolated test data and recovery/isolation plan, confirm that backup can be restored to an isolated environment, and obtain separate explicit operator approval. The last verified application review branch tip was `806fa23516490ec7beefcff03a1baa09d722120e`, with 155/155 combined mocked Python unit tests passing in DEVELOPMENT.

## DEVELOPMENT backup-destination capacity preflight — 2026-10-13

**Operator-reported read-only Docker container filesystem check** on Ubuntu host:

```bash
docker exec frappe_docker_devcontainer-frappe-1 \
  bash -lc 'df -h /workspace/development/frappe-bench/sites && df -i /workspace/development/frappe-bench/sites'
```

Result for filesystem `/dev/nvme0n1p2` mounted at `/workspace`: **915G total, 182G used, 687G available, 21% utilization**. Inodes: **60,981,248 total; 7,574,738 used; 53,406,510 free; 13% usage**. Capacity is ample relative to the known October 9 DEV archive sizes, but this is host-shared storage and free space alone does not prove successful backup or guarantee no host resource contention.

**Backup readiness checkpoint:** Site `development.localhost` listed Frappe 16.33.1, ERPNext 16.34.2 and CCPC 0.0.1; 155 combined isolated Python mock tests passed; DEV and PROD use separate named MariaDB Docker volumes; Oct 9 four-part DEV backup archives passed gzip/tar/JSON syntax checks but were not restore-tested and are four days old. Live DEV backup freshness, successful restoration, DB transactional/concurrency correctness and independent off-host recovery remain **unverified**.

**Next operator decision (do not execute without approval):** Obtain explicit agreement to create a **new DEVELOPMENT-only four-part site backup** from within `frappe_docker_devcontainer-frappe-1`, bench directory `/workspace/development/frappe-bench`, targeting **only** `development.localhost` using `bench --site development.localhost backup --with-files`. This reads the DEV database and writes new backup artifacts to the DEV site's local backups directory; it may consume shared host disk and I/O but does not intentionally mutate business records. Do not use `--site ccpcerp.local` or any production container. After approval, run safely and verify four new matching-prefix files, syntax and integrity, and consider separate recovery or off-host strategy before database-changing tests. No `bench migrate`, `run-tests`, ERPNext transactions, database restore or PRODUCTION operations authorized.

## Verified distinct live DEV and PROD MariaDB storage volumes — 2026-10-13

**Operator-provided read-only host Docker inspection:** On `gani@ccpcerpserver`, inspecting the `/var/lib/mysql` mounts for both running database containers returned:

```text
/frappe_docker_devcontainer-mariadb-1: volume frappe_docker_devcontainer_mariadb-data /var/lib/docker/volumes/frappe_docker_devcontainer_mariadb-data/_data -> /var/lib/mysql
/frappe_docker-db-1: volume frappe_docker_db-data /var/lib/docker/volumes/frappe_docker_db-data/_data -> /var/lib/mysql
```

**Conclusion:** Verified **separate named Docker volumes and separate host source paths** for DEV and PROD MariaDB data directories, matching the intended Compose project separation. This establishes database *storage directory* separation, **not independent physical servers**, full network/credential segregation, database/schema completeness or restore viability. The environments share the physical Ubuntu host and Docker daemon; direct Docker privileges can affect both. No production mutation occurred from this read-only inspect.

**Safety status:** 155/155 mocked Python tests passed in one combined DEVELOPMENT run at app review commit `806fa23`. The October 9 four-part DEV backup passed gzip/tar/JSON syntax checks but is stale for Oct 13 and has not been restored. Actual MariaDB rollback/durability, locking/concurrency, Frappe integration and indexed schema tests remain pending; no migrations or database-changing tests approved.

**Next safe operator action:** Check the filesystem's available space/inodes for the *DEV site backup destination only*, from the Ubuntu host without opening credentials or touching production:

```bash
docker exec frappe_docker_devcontainer-frappe-1 bash -lc 'df -h /workspace/development/frappe-bench/sites && df -i /workspace/development/frappe-bench/sites'
```

Use the output to plan a new complete `development.localhost` backup and eventual separated restoration rehearsal/rollback review. Do **not** execute a fresh backup, database-integrated test, `bench migrate`, restore, or prod action until its precise scope/safety plan is agreed with the operator.

## Live DEVELOPMENT and PRODUCTION database container discovery — 2026-10-13

**Operator-provided read-only Docker host output** from `gani@ccpcerpserver`:

```text
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -Ei 'NAMES|mariadb|db-'
NAMES                                      STATUS
frappe_docker_devcontainer-mariadb-1       Up 23 hours
frappe_docker-db-1                         Up 24 hours (healthy)
```

Confirms two **distinct running MariaDB containers**, first under the DEVELOPMENT Compose project and second under the PRODUCTION project. **It does not yet establish separate Docker database volume mounts or independent physical storage**; both share the Ubuntu host and Docker daemon. Do not infer "healthy" status for DEV, as its output only says Up.

**Next one-step read-only Docker mount verification** to run on the Ubuntu **host**, with no environment/config secrets printed:

```bash
docker inspect --format '{{.Name}}:{{range .Mounts}}{{if eq .Destination "/var/lib/mysql"}} {{.Type}} {{.Name}} {{.Source}} -> {{.Destination}}{{end}}{{end}}' \
  frappe_docker_devcontainer-mariadb-1 \
  frappe_docker-db-1
```

Compare DEV vs PROD mounts. No DB integration tests, fresh backup, schema changes, restore or PRODUCTION actions have been authorized. October 9 DEV four-file archive validation passed only compression/JSON syntax checks, not restore. The 155 combined mocked unit tests passed on app review commit `806fa23`.

## DEVELOPMENT Oct 9 backup archive syntax verification — 2026-10-13

**Operator-provided terminal output:** From `/workspace/development/frappe-bench` inside DEVELOPMENT, the operator ran read-only validation against the four `sites/development.localhost/private/backups/20261009_061614-development_localhost-*` backup artifacts:

```bash
B=sites/development.localhost/private/backups/20261009_061614-development_localhost
gzip -t "${B}-database.sql.gz" &&
tar -tzf "${B}-private-files.tgz" >/dev/null &&
tar -tzf "${B}-files.tgz" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEV backup files: compression and JSON syntax checks passed"
```

Actual reported output: **`DEV backup files: compression and JSON syntax checks passed`**. This establishes that all four listed files have readable compression/archive syntax or valid JSON structure; it **does NOT** verify SQL consistency/completeness, archive contents against the Frappe site, restoration, or current-day data coverage. These are October 9 artifacts being checked on October 13. No files extracted; no DB connection or write; no PRODUCTION action.

**Next safe operator action, one step at a time:** On the **Ubuntu Docker host** (exit the DEV container shell first), run the following **read-only** database-container discovery, without printing credentials/config:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -Ei 'NAMES|mariadb|db-'
```

Review the returned live DB container names, then use a separately designed **read-only** Docker mount inspection to confirm DEV and PRODUCTION database data mounts/volumes are distinct, without printing secrets. They are separate Compose projects but share host and Docker daemon. Only after verifying boundaries, backup freshness and recovery plans should the operator be asked to authorize a fresh DEVELOPMENT backup and database-integrated transaction tests. Do not run `bench run-tests` or `bench migrate` or backup restore now.

## Read-only DEVELOPMENT backup inventory — 2026-10-13

**Operator-provided listing, not archive integrity or restore verification.** From the DEVELOPMENT container in `/workspace/development/frappe-bench`, listing `sites/development.localhost/private/backups` showed the following four file artifacts with filesystem mtime **2026-10-09 00:46**:

- `20261009_061614-development_localhost-database.sql.gz` — **1,646,365 bytes**
- `20261009_061614-development_localhost-private-files.tgz` — **9,599 bytes**
- `20261009_061614-development_localhost-site_config_backup.json` — **234 bytes**
- `20261009_061614-development_localhost-files.tgz` — **141 bytes**

The file-name timestamp and mtime display differ; do not assume the time zone without checking. There is one four-part matching-prefix backup set in the 20-entry output. Presence of files **does not establish gzip/tar integrity, DB completeness, database origin, restore usability or recovery time**. On 2026-10-13 this backup is roughly four days old and may not contain recent DEVELOPMENT changes. Never expose site-config JSON contents; it can contain passwords and other sensitive values. Do not use production backups for DEV integration tests.

**Next one-step operator preflight (read-only, no extraction or DB access):** Validate archive compression and site_config JSON structure without printing contents, from the DEVELOPMENT bench:

```bash
cd /workspace/development/frappe-bench
B=sites/development.localhost/private/backups/20261009_061614-development_localhost
gzip -t "${B}-database.sql.gz" &&
tar -tzf "${B}-private-files.tgz" >/dev/null &&
tar -tzf "${B}-files.tgz" >/dev/null &&
./env/bin/python -m json.tool "${B}-site_config_backup.json" >/dev/null &&
echo "DEV backup files: compression and JSON syntax checks passed"
```

This checks readable archive structure only, **not** restored database correctness or recovery viability. Subsequently verify DEV/PROD database boundaries and free space; require a new, complete DEV backup and explicit authorization/safe rollback plan before any database-changing integration tests. Preserve DEV persistent state and all production services; no migration, restore, deletion or production access authorized.

## Read-only DEVELOPMENT site installed-app preflight — 2026-10-13

**Operator-provided DEVELOPMENT terminal output:** At `/workspace/development/frappe-bench`, the operator ran `bench --site development.localhost list-apps`; it completed successfully and reported:

```text
frappe  16.33.1 version-16
erpnext 16.34.2 version-16
ccpcerp 0.0.1   feature/intercompany-material-billing
```

This verifies that the named DEVELOPMENT site can provide its installed-application listing, supporting (but not independently proving) site/DB availability. The `ccpcerp` branch field in `list-apps` is app/version metadata and **must not be treated as the active Git branch**; the operator separately confirmed the DEVELOPMENT Git checkout on `review/intercompany-approval-failure-tests`, commit `806fa23`, and the connected GitHub branch was independently confirmed at `806fa23516490ec7beefcff03a1baa09d722120e`.

**Still unverified:** DEV backup freshness/completeness, DEV MariaDB identity/independence, schema/indexes, controlled rollback safety and MariaDB concurrency. DEV site has persistent data; no `bench run-tests`, `bench migrate`, invoice creation, backup restore, or schema changes have been approved. PRODUCTION untouched.

**Next one-step read-only preflight:** From DEVELOPMENT container's `/workspace/development/frappe-bench`, list filenames/timestamps/sizes of DEV site backups if directory exists; do not expose site config contents or passwords:

```bash
cd /workspace/development/frappe-bench
if [ -d sites/development.localhost/private/backups ]; then
  find sites/development.localhost/private/backups -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM  %12s bytes  %f\n' | sort -r | head -n 20
else
  echo 'DEVELOPMENT site backups directory not found at standard path'
fi
```

A directory listing or backup filename alone does not prove a valid/completed/restorable backup. Evaluate freshness, backup artifact sets and separate production boundaries before seeking authorization for persistent-DEV integration tests.

## Combined 155/155 DEVELOPMENT unit tests passed — 2026-10-13

**Operator-provided DEVELOPMENT terminal transcript** (not a CI run or connector-executed command): after prior verified DEV fast-forward to app review branch `review/intercompany-approval-failure-tests`, commit `806fa23`, ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest -q \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes
```

**Observed result: `Ran 155 tests in 0.379s`; `OK`.** All four mocked modules passed *together* in one Python interpreter, providing evidence their test setup and cleanup coexist and removing the earlier need to rely solely on separate runs. GitHub connector independently verified app branch tip `806fa23516490ec7beefcff03a1baa09d722120e`. No new application code change, DB migration, Docker restart or PRODUCTION modification occurred during this milestone.

**Remaining validation:** No actual Frappe/MariaDB multi-connection concurrency, invoice rollback/durability, installed index/schema, workflow hook integration or recovery test has been performed in this testing sequence. DEV site `development.localhost` is **persistent**, and DEV/PRODUCTION share host and Docker daemon even though their Compose projects/DB volumes are distinct. Do not execute `bench --site development.localhost run-tests`, `bench migrate`, invoice creation, schema changes, or any database-changing integration test until DEV backup/isolation and rollback plan are explicitly reviewed and operator-approved; never touch production.

**Next safe one-step preflight:** from the DEVELOPMENT container at `/workspace/development/frappe-bench`, run **read-only** `bench --site development.localhost list-apps`. This checks whether the Frappe site can connect to its site database and reports installed apps/versions without exposing credentials or performing planned writes. Collect output, then separately verify DEV database identity, backup availability and isolated test strategy without exposing secrets. Current known untracked `AGENTS.md` must remain excluded.

## DEVELOPMENT index patch mocks passed — 2026-10-13

**Operator-reported DEVELOPMENT test output:** At the DEVELOPMENT bench after the previously verified safe fast-forward to review branch `review/intercompany-approval-failure-tests`, commit **`806fa23`**, the operator ran:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes \
  -q
```

Terminal result: **`Ran 8 tests in 0.004s` — `OK`**. The patch's logic was exercised with mocked database access; **no actual index creation or migration has been run or proven**. Cumulative separate test-run reports now total **155 passing mocked test executions**: 124 core billing batch, 4 approval failure paths, 19 deletion protection, and 8 index-patch tests. This does not constitute a combined suite run, a CI result, actual MariaDB transaction-rollback/concurrency proof, schema verification, or a production-ready release. App review branch `806fa23516490ec7beefcff03a1baa09d722120e` independently checked through the GitHub connector.

**Recommended next safe operator action:** Run all four mocked test modules in **one standalone `unittest` invocation** at the current DEVELOPMENT commit to verify inter-test isolation, global `frappe.db` mock cleanup and reproducibility across the exact same revision, without database-integrated testing:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest -q \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes
```

Expected count based on separate runs: 155, but **combined execution not yet verified**. If clean, plan a separate read-only DEV site/backup/schema preflight before seeking authorization for any database-integrated tests. Preserve untracked `AGENTS.md`, DEV data and PROD; no migrations, restarts or destructive operations authorized.

## DEVELOPMENT deletion-protection mocked tests passed — 2026-10-13

**Operator-provided DEVELOPMENT terminal output:** With application checkout on `review/intercompany-approval-failure-tests` at **`806fa23`**, the operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.test_transaction_deletion_protection \
  -q
```

Result: **`Ran 19 tests in 0.008s` — `OK`**, with no errors or failures. Together with separately reported 124 passing core Intercompany Billing mocked unit tests and 4 passing invoice failure-propagation mocked tests, **147 mocked test executions passed across three separate runs**. This is not a single combined run, nor evidence of real MariaDB rollback/concurrency behavior. The application review branch tip **`806fa23516490ec7beefcff03a1baa09d722120e`** was independently reverified via connected GitHub tools.

**Next safe action:** Run the existing index patch **mocked** unit tests from the DEVELOPMENT bench, without executing the actual patch or `bench migrate`:

```bash
cd /workspace/development/frappe-bench
./env/bin/python -m unittest ccpcerp.patches.v1_0.test_add_intercompany_material_billing_indexes -q
```

The index mock suite in GitHub initializes/restores a mocked `frappe.db`; no further code change is planned unless tests fail. Keep untracked `AGENTS.md` excluded. Any future actual database tests, migrations, concurrent approval simulations or production release require separate safety review and authorization. **No PRODUCTION changes.**

## DEVELOPMENT mocked billing suite passed — 2026-10-13

**Operator-reported DEVELOPMENT test transcript:** After fast-forwarding `review/intercompany-approval-failure-tests` to **`f49e2e8`**, the operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  -q
```

Result **`Ran 124 tests in 0.345s` — `OK`** (no reported errors/failures). Previously the four mocked invoice failure-propagation tests on the same review line passed **`Ran 4 tests in 0.011s` — `OK`**. These are **128 passing mocked test executions across two independent commands**, not a combined all-suites run, real DB proof, or CI. The previous 45 LocalProxy test-harness errors were eliminated by the `f49e2e8` mocked-`frappe.db` setup.

**Proactive GitHub-only test-harness follow-up:** Source inspection found `ccpcerp/ccpc_erp/test_transaction_deletion_protection.py` uses the same `patch(...frappe.db.sql/get_value)` pattern without a bound database in standalone `unittest`. It was corrected to temporarily replace `frappe.__dict__["db"]` with `MagicMock()` and restore it via cleanup; no runtime code was modified. GitHub connector verified updated app review branch at **`806fa23516490ec7beefcff03a1baa09d722120e`**, one commit / one test file ahead of `f49e2e8`. This follow-up was **not yet pulled into DEVELOPMENT nor executed**, and the index-patch mock tests also remain unrun in the current work session.

**Next safe step:** With DEVELOPMENT still expected on `review/intercompany-approval-failure-tests` at `f49e2e8`, verify local branch and absence of modified *tracked* files, then `git pull --ff-only origin review/intercompany-approval-failure-tests` (preserve untracked `AGENTS.md`). Verify `806fa23`; then run the isolated mocked **Transaction Deletion Record protection** and **index patch** tests, recording actual outputs. Do not run `bench migrate`, Frappe integrated test runner, financial invoices or database concurrency experiments until separate DEV safety/backup approval. PRODUCTION untouched.

## DEVELOPMENT billing mock-suite failure and GitHub test-harness correction — 2026-10-13

**Operator-provided test output:** On DEVELOPMENT at `/workspace/development/frappe-bench` on review branch `review/intercompany-approval-failure-tests` (at the previously verified local commit `12e24c9`), ran:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch \
  -q
```

The uploaded terminal output reported **`Ran 124 tests in 0.344s`, `FAILED (errors=45)`**. Representative/all visible failures were during `unittest.mock.patch` of `frappe.db.sql` or `frappe.db.get_value`, terminating at Frappe's `local.py` with **`RuntimeError: object is not bound`**. This is a **standalone unittest database LocalProxy/mock setup problem**, not a verified billing transaction failure. Tests encountering setup errors **did not validate their asserted billing behavior**.

**GitHub-first correction committed and verified:** App review branch [`review/intercompany-approval-failure-tests`](https://github.com/ccpcerp/ccpcerp/tree/review/intercompany-approval-failure-tests) advanced to **`f49e2e869e6f1c6c64da7f662042b6e0fee80aee`**. Exactly **one file** changed compared with `12e24c9`: `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py`. `TestIntercompanyMaterialBillingBatch.setUp` now temporarily substitutes `frappe.__dict__["db"]` with `MagicMock()` and registers cleanup to restore the original proxy. This mirrors the existing isolated index-patch test setup. **No application runtime code modified.**

**Verification status:** Commit and changed-file list independently verified on GitHub. **The revised 124-test suite has NOT yet been re-run on DEVELOPMENT**, so do not say it passes or assign release readiness based on this change. No CI test result, DB transaction, migration, PROD change, or branch merge.

**One next safe step:** In the DEVELOPMENT app directory, make sure the local branch remains `review/intercompany-approval-failure-tests` and tracked changes are clean; then fast-forward pull from the **same tracked remote branch** (no force, no switch, no destructive cleanup), retaining untracked `AGENTS.md`. Re-run the same `python -m unittest ...test_intercompany_material_billing_batch -q` and report the result. If new failures arise, resolve them in GitHub first. Actual MariaDB rollback and concurrency tests remain separate pending release gates.

## DEVELOPMENT mock unit-test milestone — 2026-10-13

**Operator-reported successful test execution (terminal transcript supplied in chat).** The user had entered the DEVELOPMENT Docker container and confirmed Git branch `review/intercompany-approval-failure-tests` tracking `origin/review/intercompany-approval-failure-tests`, at commit `12e24c9`, with only `?? AGENTS.md` untracked. The branch tip was independently reverified via GitHub connector as **`12e24c99daf020ba488940411379a6c517aa1c20`**.

The operator ran from `/workspace/development/frappe-bench`:

```bash
./env/bin/python -m unittest \
  ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_billing_approval_failures \
  -v
```

Captured transcript shows **4 tests passed**, `Ran 4 tests in 0.011s`, `OK`. All four mocked invoice failure-propagation paths passed: Sales Invoice insert exception, Purchase Invoice insert exception, SI cross-link save exception and final batch save exception. This is **operator-provided terminal evidence, not a remotely executed test via GitHub connector**.

**Strict scope:** This validates isolated Python mock interactions only. It **does not prove** MariaDB rollback, persisted invoice atomicity, two-connection concurrency correctness, hook behavior in a live Frappe request, or migrations. No database-integrated tests, `bench migrate`, application merges, or PRODUCTION modifications were authorized/performed in this step. The existing `AGENTS.md` stays untracked/excluded.

**Next safe action:** Run the **existing mocked billing batch Python unit-test module** on the same verified DEV branch using `./env/bin/python -m unittest ccpcerp.ccpc_erp.doctype.intercompany_material_billing_batch.test_intercompany_material_billing_batch -q`. Inspect the result before expanding to the deletion-protection and patch unit tests. Only after a complete mock-suite baseline should a separate, explicitly reviewed DEVELOPMENT database-integration/backup/isolation procedure be considered.

## Prior development milestone — failure-path tests prepared (2026-10-12)

**GitHub code change complete, execution pending.** ChatGPT created application branch [`review/intercompany-approval-failure-tests`](https://github.com/ccpcerp/ccpcerp/tree/review/intercompany-approval-failure-tests) from preserved DEV checkpoint `f665cf3`. The GitHub connector verified tip **`12e24c99daf020ba488940411379a6c517aa1c20`** (2 commits ahead, zero behind checkpoint), adding **only one new Python test file**: [`test_intercompany_billing_approval_failures.py`](https://github.com/ccpcerp/ccpcerp/blob/review/intercompany-approval-failure-tests/ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_billing_approval_failures.py). No existing application code was altered; no pull/merge/migration/service/PRODUCTION action occurred.

**Four *mocked* failure-propagation test methods prepared** for: Sales Invoice insert failure; Purchase Invoice insert failure after Sales Invoice insert; Sales Invoice cross-link save failure after both inserts; and final billing batch save failure after both invoice inserts. These check exceptions propagate and later actions are skipped when appropriate. **No execution/lint/CI result has yet been verified** for these new tests. In-memory fields changed before final save do **not** establish database durability or rollback. These tests are not an alternative to real Frappe/MariaDB transactional tests.

**First next safe action:** request an operator **read-only DEVELOPMENT Git status/HEAD** before any pull or branch switch:

```bash
git -C /workspace/development/frappe-bench/apps/ccpcerp status --short --branch
git -C /workspace/development/frappe-bench/apps/ccpcerp rev-parse --short HEAD
```

Expect old review checkpoint `f665cf3` and untracked `AGENTS.md` based on earlier operator evidence, **but do not assume it without new output**. Do not overwrite local files or automatically stage `AGENTS.md`. If safe, separately plan bringing the new **GitHub test branch** into DEVELOPMENT with a verified procedure, then execute its test module only with operator approval and awareness Frappe's test runner may mutate the persistent DEV database. Backups/fixture isolation required for database mutation. Prioritize safe read-only assessment of MariaDB version/isolation, real two-connection locking tests, failure rollback, and non-unique-index review. No `bench migrate` without explicit review/authorization.

## Current decisions (standing)

- **GitHub-first:** implement specifically authorized CCPC custom-app changes in GitHub on reviewed feature/review branches, then DEVELOPMENT pulls reviewed commits for testing; push any DEV fixes back to GitHub. **Always verify the resulting GitHub commits** and maintain this handoff after milestones.
- **No automatic Codex reports to GitHub.** The user cancelled this effort; they may paste Codex reports manually. No recurring publisher, new paid OpenAI API integration or autonomous GitHub-reporting task.
- ChatGPT may inspect and update GitHub during **active conversations**; there is **no unattended or automatic handoff update** while no conversation is active. The user cannot know exactly when a thread will reach its limit, so update this handoff **proactively** at milestone boundaries rather than waiting for an explicit thread-transfer request.
- **PRODUCTION is off limits** without separate, explicit approval and backup/recovery/rollback review. DEVELOPMENT and PRODUCTION are separate Compose projects on the same host; database/data and credentials are not equivalent to GitHub code.

## Repositories and latest verified code

| Repository / role | Verified reference | Status |
| --- | --- | --- |
| [CCPC custom app](https://github.com/ccpcerp/ccpcerp) | `review/intercompany-dev-checkpoint-2026-10-12` → [`f665cf3805ba799e5182600286f40e027e3c3120`](https://github.com/ccpcerp/ccpcerp/commit/f665cf3805ba799e5182600286f40e027e3c3120) | **Eight DEV-only files safely committed and pushed, verified via GitHub** |
| Original billing feature branch | `feature/intercompany-material-billing` → `7ac238ee25101207216e601532d545297989b4ee` (last verified) | Earlier committed billing code; **review checkpoint not merged into it** |
| Application default branch | `version-16` → `cfcc193` (last verified) | Older, **does not contain billing/Withdrawal Slip feature** |
| [Deployment and project docs](https://github.com/ccpcerp/ccpc-frappe-deployment) | `docs/ccpc-checkpoint-2026-10-10`, draft [PR #24](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/24) | GitHub-first workflow and this handoff live in a **draft documentation branch; not merged to main** |

**Do not assume these SHAs remain current forever.** Reverify the branch tips when resuming.

### Recovered DEVELOPMENT checkpoint

Operator terminal verified the DEVELOPMENT application folder:

`/workspace/development/frappe-bench/apps/ccpcerp`

The operator staged exactly these eight files (four modified and four added), committed them as `f665cf3`, then pushed to `origin/review/intercompany-dev-checkpoint-2026-10-12`. The GitHub connector independently verified the remote branch tip and eight-file commit:

1. `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/intercompany_material_billing_batch.py`
2. `ccpcerp/ccpc_erp/doctype/intercompany_material_billing_batch/test_intercompany_material_billing_batch.py`
3. `ccpcerp/ccpc_erp/transaction_deletion_protection.py`
4. `ccpcerp/ccpc_erp/test_transaction_deletion_protection.py`
5. `ccpcerp/hooks.py`
6. `ccpcerp/patches.txt`
7. `ccpcerp/patches/v1_0/add_intercompany_material_billing_indexes.py`
8. `ccpcerp/patches/v1_0/test_add_intercompany_material_billing_indexes.py`

`AGENTS.md` was **untracked and deliberately excluded**; it still requires separate content review before any inclusion in GitHub. Do not treat it as operational instructions, automatically stage it, delete it, or run unreviewed agent directions.

At last operator check, DEVELOPMENT was on the local checkpoint branch. The exact **post-push working tree/status has not been rechecked**; do not assume it is completely clean. Never reset, clean, branch-switch or pull over pending work without checking.

A local Windows VS Code clone at `E:\CCPC Files 2025\Plant Wide\ERPnext\ccpcerp` was clean at `version-16`/`cfcc193` and remains optional. The user was told **not to delete it**; it is not required for ChatGPT GitHub inspection.

## Preliminary static code review of `f665cf3`

**Completed:** Verified eight files on GitHub and reviewed their source. Code includes Company and billing-batch `FOR UPDATE` locking, reload/stale-state checks, source-claim locking, guarded Finance approval transitioning to draft Sales/Purchase Invoices, approval/refresh immutability, Transaction Deletion Record protection, and two **non-unique** database indexes registered as a Frappe patch.

**Not completed or not proven:** No newly verified CI/test run, no MariaDB two-connection concurrency experiment, no live Frappe document integration test, no demonstrated atomic rollback if the second invoice insert fails, no migration execution, and no production release validation. Non-unique indexes do **not** guarantee uniqueness; actual isolation and lock ordering must be verified. The checkpoint is **work in progress**, not production-ready.

## Production-readiness assessment — 2026-10-12

**Scope:** Withdrawal Slip → Stock Entry / Material Issue → monthly Intercompany Material Billing only, **not** the entire ERPNext production instance. This is a **GitHub static-review assessment**, not a live DEVELOPMENT integration result. No deployment approval.

**Evidence checked with connected GitHub tools:** app review branch tip remains `f665cf3805ba799e5182600286f40e027e3c3120`, original feature branch tip remains `7ac238ee25101207216e601532d545297989b4ee`. Compare is one commit / eight files ahead; the original feature branch has **not** absorbed the checkpoint. Only a separate older Withdrawal Slip draft app PR #6 appeared in the inspected PR list; no reviewed billing release PR was verified. The billing batch Python test module contains **124 `test_...` methods**, mostly mocked. GitHub Actions query for PR runs associated with `f665cf3` returned **zero runs** (this does not prove no other CI ever ran). No newly verified fresh live DEV tests.

**Implementation appears substantially present:** Withdrawal Slip/Material Issue path, frozen source billing snapshots, Finance-approved paired draft SI/PI, locking and stale-state guards, audit-field immutability, source claim checks, deletion safeguards, and the two index patch definitions.

**Hard release gates still open:**

1. **Test current checkpoint in DEVELOPMENT**, collecting actual repeatable results rather than relying on the 124 test declarations or historical claimed pass counts; include Frappe v16 `extend_doctype_class` hook behavior and permissions.
2. **Two-connection concurrency verification on an approved safe DEVELOPMENT setup:** simultaneous batch creation/claims, preview/finalize/approve races; prove exactly one pair of invoices and clear retry behavior; inspect MariaDB transaction isolation and actual lock behavior. Code's `FOR UPDATE` and Company serialization is a mitigation, **not yet a demonstrated guarantee**.
3. **Failure atomicity/idempotency:** inject a failure after creation of the first draft invoice, prove transaction rollback leaves no orphan invoice and no incorrect Approved batch; test repeated approval calls, deletion/Transaction Deletion Record bypass attempts and accounting/stock consistency.
4. **Database/patch review:** `idx_icmb_scope` and `idx_icmbi_source_parent` are **NON-UNIQUE** and not proven applied. Review DDL and performance/lock effects separately, back up persistent DEV state where appropriate, seek explicit authorization before `bench migrate` or other DDL, test idempotence and clean failure handling.
5. **Review and release preparation:** ensure code review/CI coverage, resolve defects via GitHub-first branches, merge approved code, verify PRODUCTION's exact baseline, backups, restoration/rollback plan, migration scope and business acceptance. Production remains untouched until distinct explicit approval.

**How far:** Implementation is significantly advanced, but production readiness **cannot be assigned a credible percentage or go-live date** until real DEV DB integration tests pass. More verification work than feature scaffolding appears to remain. Treat it as **release blocked, not production-ready**, with at least these five groups of gates. Next practical milestone is a **safe DEVELOPMENT validation plan** that can first run non-mutating tests / review setup, then explicitly approves any fixture creation, DB changes, concurrency experiments and cleanup. No production testing.

## Immediate next priority

**Withdrawal Slip → Material Issue → Intercompany Billing**. Proceed from GitHub review checkpoint `f665cf3` and validate in DEVELOPMENT safely.

1. Inspect existing tests and identify highest-risk concurrency, idempotency, invoice failure rollback, audit-trail and transaction deletion paths. Document any code issues or missing tests **in GitHub**, using a reviewed branch for fixes.
2. Propose a controlled DEVELOPMENT-only validation plan, with transaction isolation and two simultaneous approval requests. **Do not invent results, execute financial transactions against production, or assume mock tests prove real MariaDB concurrency.**
3. Evaluate the new index patch separately before any DEV migration/DDL. Preserve DEV database/configuration and prepare appropriate backup/recovery steps if testing may modify persistent state.
4. After verified tests, push any corrections to GitHub, identify branch/commit, and update **this file** with outcomes, blockers and exact next safe step.

## Operating boundaries and handoff maintenance

- Read current app code and project documents using the connected GitHub tools before making code or workflow claims. Verify relevant branches, especially since the default app branch lacks recent work.
- Keep a clear distinction between **pushed code**, **uncommitted DEV changes**, **mocked tests**, **actual database tests**, **pending changes**, and **approved versus unapproved actions**.
- Protect SSH keys, tokens, business data and operational secrets. Existing DEV container historically exposed mounted SSH materials; **do not run uncontrolled agentic Codex inside it**.
- After **each meaningful code or test milestone**, before a high-risk context switch, and periodically in a long thread, update this *single current GitHub handoff* (and affected design/runbooks where needed); include UTC/date, verified refs, what changed, what was tested, outstanding risks, and the **one next safe step**. Do not churn files if nothing materially changed.
- When a chat reaches a length limit or an unexpected interruption, the **last successfully committed GitHub handoff** is the recovery checkpoint. No claim that ChatGPT can predict an exact thread limit or publish while a thread is inactive.

## Next-conversation starter

> Continue CCPC ERPNext **GitHub-first**. Use the connected GitHub tools to read `docs/ccpc-project/GITHUB-FIRST-DEVELOPMENT-WORKFLOW.md` and `docs/ccpc-project/CURRENT-HANDOFF.md` on the deployment documentation branch (or their newest authoritative locations). Verify the live app review branch/commit before continuing. Do not use old ChatGPT Project Source handoffs as current state. No automatic Codex GitHub reporting, no additional API billing, no production operations. Proceed with the handoff's next safe development step.
