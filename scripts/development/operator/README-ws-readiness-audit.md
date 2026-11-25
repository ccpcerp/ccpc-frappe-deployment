# Phase 1 Withdrawal Slip readiness audit

**Review only.** This operator preflight takes a read-only snapshot for one previously authorized DEVELOPMENT draft. It does not perform the workflow or authorize a stock issue.

The policy reference is [CCPC application commit e5c6f4c](https://github.com/ccpcerp/ccpcerp/tree/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5). It allows a same-Company eligible beneficiary for routine Bearings withdrawals and requires independent Finance evidence for the actual beneficiary Department. A shared Cost Center can be independently approved for more than one Department. It does not make the requesting Department's mapping interchangeable with the beneficiary's.

## Operator preconditions

1. Independently verify the exact `development.localhost` site, its running application container, the network route to its database, and the schema and existing account. The site operator and DBA must agree on the endpoint and privately pin the single authorized Draft and its master records. Keep actual record identifiers, topology, endpoint values and audit results in operator custody. The script checks the independently supplied binding against the connection. An attestation is not cryptographic proof of reviewer identity or deployment topology.
2. Use an already approved DEVELOPMENT-only TLS route and an existing principal with direct SELECT limited to the exact tables listed below. The DBA must verify no inherited, PUBLIC, proxy or other access and no DEVELOPMENT-to-PRODUCTION route. An active role, broader direct privileges or an unrecognized grant format stops the audit. The script may receive authentication metadata from `SHOW GRANTS` in memory. It does not print that response.
3. Use the approved operator terminal in the independently verified DEVELOPMENT bench root. Stage this script in a private directory outside the app checkout. Confirm the reviewed GitHub commit and script SHA-256 before running it. PyMySQL 1.1.2 must already be available to the operator's chosen Python. This draft uses that version's TLS upgrade to pin the leaf before sending credentials. Stop if the required route, existing account, driver or verified certificate is unavailable.

## Private inputs

Supply two private JSON attestations. Each has `reviewer_role` (respectively `site-operator` and `database-operator`), a distinct `reviewer`, `development_endpoint_exclusive: true`, and an identical `target` object. The DBA attestation also requires `direct_select_only_no_inherited_access: true`.

The target contains `site` (`development.localhost`), `environment` (`DEVELOPMENT`), `commit` (the full pinned app SHA), `host`, `port`, `database`, `username`, `principal` (`CURRENT_USER()`), `hostname` (MariaDB server hostname), `server_id`, the verified Frappe IANA `timezone`, `ca_sha256` (approved PEM bytes), `leaf_sha256` (endpoint certificate in DER form), and `pilot`.

`pilot` has exactly the independently verified ERPNext record IDs for `slip`, `company`, `requesting`, `beneficiary`, `equipment`, `item`, `warehouse` and expected `expense` account. Pin one already authorized Draft, its one-unit item and the actual beneficiary. Use ERPNext record keys. Do not include passwords or the proposed issuer's identity in the JSON.

After independent source review and separate operator authorization:

```bash
./env/bin/python -B /approved/private/ws_readiness_audit.py \
  /approved/private/site-attestation.json \
  /approved/private/db-attestation.json \
  /approved/private/approved-development-ca.pem
```

The script prompts privately for the proposed Stockroom issuer login and existing database password. It opens a consistent READ ONLY snapshot after the TLS, server, schema, principal and direct grant checks. It closes the connection after rollback.

## Output and limits

Share only sanitized status lines. Examples below are illustrative.

```text
PASS | Persisted item row | Confirmed in snapshot.
FAIL | Signed Center | Missing or conflicting eligible revision, or approval/retirement evidence did not reconcile.
UNVERIFIED | Effective named-user permissions | Confirm saved-record access, Workflow actions, issuer write, and reviewer report access in read-only named sessions.
FAIL | OVERALL | Read-only preflight. Separate authorization required for UAT.
```

Exit 1 means an observed failure and exit 2 means unresolved evidence with no observed failure. The parser reserves exit 0 for an all-pass snapshot; this draft leaves at least the external UAT gate unresolved. The script does not print stock quantities, valuation, personal identities, approval references or raw exceptions. A linked draft or submitted Stock Entry blocks issue. Cancelled history requires operator review. The planned issuer must be distinct from the Draft creator and have effective Slip write access. The normal controlled issue path does not require broad native Stock Entry create/submit rights.

Use separately approved read-only UI or runtime evidence for effective named-user permissions, worker code, posting-period restrictions, availability commitments and any specific serial or batch selection. A snapshot does not establish availability or mapping eligibility at a later posting instant. Keep the Draft unchanged pending separate authorization.

Offline tests use fake cursors and synthetic records. Actual MariaDB grant rendering, TLS interoperability, and the DEVELOPMENT database binding remain unverified.

```bash
cd scripts/development/operator
python3 -B -m unittest -v test_ws_readiness_audit
```

## Proposed privilege change for separate approval

Use an already verified principal with these exact effective grants if available.
The existing operator-run baseline remains available without granting access to
this Codex session. Before any new principal can be used, verify a dedicated
runner with the Docker API, SSH material, backups and other host mounts absent.
Restrict its egress to the independently verified DEVELOPMENT database address
and port. A host label or missing default-route entry does not establish isolation.
Keep the credential in the operator's approved secret channel.

If no matching principal exists after that verification, the DEVELOPMENT DBA
may propose one dedicated, source-host-bound MariaDB account for this single
audit. The only permitted grant change is the table SELECT set below. Use a
unique account restricted to the verified runner source address, enforce TLS,
assign no roles or proxy privileges, and verify effective permissions before
operator approval to run. Substitute the literal DEVELOPMENT schema and exact
runner account privately. The following is a review template, not a command
to paste with placeholder values. Provision the secret via the approved DBA
mechanism and never put it in shell history, this repository, or the audit bundle.

```sql
GRANT SELECT ON `DEV_SCHEMA`.`tabAccount` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabAccounting Dimension` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabBin` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Accounting Mapping Decision` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Center Mapping Revision` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Center Mapping Scope` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Expense Mapping Revision` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Expense Mapping Scope` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Mapping Decision Use` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Mapping Retirement Event` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Mapping Retirement Request` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCCPC Section` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCompany` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCost Center` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabCustom DocPerm` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabDepartment` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabDocPerm` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabEquipment Registry` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabHas Role` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabInstalled Application` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabItem` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabItem Group` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabSingles` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabStock Entry` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabStock Ledger Entry` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabUser` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabUser Permission` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabVersion` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabWarehouse` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabWithdrawal Slip` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabWithdrawal Slip Item` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabWorkflow` TO 'AUDIT_USER'@'RUNNER_SOURCE';
GRANT SELECT ON `DEV_SCHEMA`.`tabWorkflow Transition` TO 'AUDIT_USER'@'RUNNER_SOURCE';
```

No database-wide SELECT, write, DDL, role, proxy, grant option, or additional
listener is requested. MariaDB exposes relevant information_schema column
metadata through existing table visibility. Table grants still allow reads of
other rows in those tables to anyone holding the credential. For tighter scope,
keep the credential operator-side and expose only the fixed audit and sanitized
statuses through an allowlisted interface.

**Revocation:** After the approved window, the DBA closes any sessions belonging
to that dedicated account, drops only that audit account with
`DROP USER 'AUDIT_USER'@'RUNNER_SOURCE';`, removes its secret from the approved
store, and verifies the account is absent. Remove any temporary runner routing
rule separately. For a reused account, revoke only the exact temporary grants
approved for that account. Do not drop the reused account.

**Disposable validation gate:** Before adopting the new grant rendering, use an
isolated MariaDB 11.8 lab with synthetic schema and TLS to confirm current
SHOW GRANTS output, exact source-host matching, correct leaf pin, successful
snapshot startup and rejection of a harmless write attempt. Separately run the
readiness snapshot against synthetic Frappe/ERPNext records at the pinned
application commit. Keep this review draft off live DEVELOPMENT until that
handshake and the independently verified deployment binding pass.
