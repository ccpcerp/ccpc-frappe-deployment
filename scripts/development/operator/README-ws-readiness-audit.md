# Phase 1 Withdrawal Slip readiness audit

**Review only.** This operator preflight takes a read-only snapshot for one previously authorized DEVELOPMENT draft. It does not perform the workflow or authorize a stock issue.

The policy reference is [CCPC application commit e5c6f4c](https://github.com/ccpcerp/ccpcerp/tree/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5). It allows a same-Company eligible beneficiary for routine Bearings withdrawals and requires independent Finance evidence for the actual beneficiary Department. A shared Cost Center can be independently approved for more than one Department. It does not make the requesting Department's mapping interchangeable with the beneficiary's.

## Operator preconditions

1. Independently verify the exact `development.localhost` site, its running application container, the network route to its database, and the schema and existing account. The site operator and DBA must agree on the endpoint and privately pin the single authorized Draft and its master records. Keep actual record identifiers, topology, endpoint values and audit results in operator custody. The script checks the independently supplied binding against the connection. An attestation is not cryptographic proof of reviewer identity or deployment topology.
2. Use an already approved DEVELOPMENT-only TLS route and an existing direct SELECT-only principal for the literal schema. The DBA must verify no inherited, PUBLIC, proxy or other access and no DEVELOPMENT-to-PRODUCTION route. An active role, broader direct privileges or an unrecognized grant format stops the audit. The script may receive authentication metadata from `SHOW GRANTS` in memory. It does not print that response.
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
