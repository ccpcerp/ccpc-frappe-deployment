# Phase 1 isolated readiness audit lab

This is a disposable synthetic lab for the exact [PR #41 audit](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/41) at `bef7813487036e226ccb03d9daf56ab7ca033279`. It has no live site configuration, live database, externally reachable network, Docker daemon or host filesystem shares. The guest is a fresh initramfs and all MariaDB fixture writes happen in guest RAM.

## Boundary and test scope

- The host launcher refuses UID 0 and runs QEMU with software emulation, no NIC, no disks or host shares, no management monitor, and closed console input. It copies a bounded system runtime and reviewed source into a fresh guest image. It requires a pinned SHA-256 for the audited Python file.
- Guest PID 1 mounts only guest pseudo-filesystems and enables guest loopback. MariaDB and the test process run as UID/GID 1000 with no supplementary groups, no effective capabilities, and no-new-privileges. The test checks that regaining root fails, loopback is the only interface, and host credential and Docker paths are not present.
- The lab creates a synthetic TLS-required reader bound to guest loopback, with direct SELECT on each of the audit's exact 33 table names. It checks actual MariaDB grant rendering, SELECTs on each table and column metadata, and transaction startup through the unchanged PR41 adapter. It tests rejection of wrong TLS leaf, cleartext login, wrong server/schema identity and an extra UPDATE grant. A synthetic administrative control session proves MariaDB rejects UPDATE in the transaction with server code 1792.
- The SQL payload is a minimal synthetic schema. The test replaces the application snapshot callback with a compatibility probe. It does not verify real Frappe schema, mapping provenance at a live site, loaded workers, actual permissions, or stock/GL behavior.

## Reproduce locally

On an unprivileged x86-64 Ubuntu environment with QEMU, cpio, OpenSSL, dpkg-deb, setpriv, static BusyBox and system Python, acquire public, integrity-verified packages into a private disposable directory without installing them. Provide one matching `.deb` for each of `linux-image-unsigned-*-generic`, `mariadb-server-core`, `mariadb-server`, `mariadb-client-core`, `mariadb-common`, `libaio1t64`, and `liburing2`. Save the verified PyMySQL 1.1.2 wheel as `pymysql-1.1.2.whl` there. Supply the exact audit file fetched from the reviewed commit, kept outside any installed app checkout.

```bash
bash tests/development/readiness-lab/run.sh /private/synthetic-assets /private/ws_readiness_audit.py \
  556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927
```

The guest powers down on completion. The launcher exits nonzero if the final PASS marker is absent. It prints the private temporary lab directory so the operator can remove its synthetic inputs and logs after review. The script does not create a networked runner or configure a service.

## Observed evidence

- Host UID 1000. Rootless user/mount/network namespace creation was blocked; no host setting was changed to work around it. The rootless QEMU/TCG run completed with the NIC-free boundary above.
- Ubuntu guest kernel `7.0.0-44-generic`, MariaDB `11.8.6-MariaDB-5ubuntu0.1`, PyMySQL `1.1.2`. All local guest boundary, native TLS, exact grants, binding, and write-rejection checks passed. An initial harness run exposed a guest file permission problem, and a second exposed a missing test argument. Both were corrected and the complete suite reran successfully.
- The unchanged audit's 12 offline tests also passed. No live database, Docker daemon or external ERPNext environment was contacted.

## Gate for independently binding a real DEVELOPMENT site

The verified guest has no network path to any live database. Keep that boundary by default. The smallest live route is the existing human-operated, site-scoped fixed-query baseline returning sanitized statuses. No new Codex permission is needed for that route.

If a direct diagnostic runner is required, keep a separate operator-owned fixed audit process, with no Docker API, SSH material, backup/NAS mounts, host shares, or interactive command entry point. Keep the credential in operator custody and return only the audit status schema. Before connecting, independently verify the following on DEVELOPMENT through trusted operator and DBA evidence.

1. The operator verifies the exact running DEVELOPMENT service and mounted app commit, the site `development.localhost`, and that the site's resolved database binding agrees with the DBA's literal DEVELOPMENT schema. The DBA independently verifies the corresponding server identity, route and allowed source address. Compare the two privately. Matching JSON alone does not establish provenance.
2. Pin the verified dedicated MariaDB endpoint, CA and DER leaf, and validate effective direct grants with no inherited, public or proxy access. Require a host-side egress policy limited to that exact DEVELOPMENT address and port before giving a runner any network. Inspect rule metadata and use local synthetic negative tests. Do not probe PRODUCTION.
3. If an existing verified principal can meet the exact grant set, reuse it. Otherwise the only proposed database change is one short-lived source-bound, TLS-required DEVELOPMENT audit account with the 33 table SELECT grants and no roles. Apply the [exact grant and revocation template](../../../scripts/development/operator/README-ws-readiness-audit.md) only after specific approval. The DBA closes its sessions and drops only that account on revocation, removes the credential, and the network administrator removes the narrow temporary egress rule if one was separately approved. Verify the endpoint is then unreachable from that runner using policy metadata or a synthetic fixture.
4. Record only sanitized proof and obtain separate authorization before the pinned live audit. Keep the pilot slip in Draft pending the audit and separate UAT approval.
