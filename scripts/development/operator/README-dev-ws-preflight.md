# Operator-only DEVELOPMENT Withdrawal Slip preflight

Review this wrapper before any run. It adapts the existing operator fixed-query baseline to CCPC commit `e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5`. The older baseline described in the handoff was guarded at a different SHA and must not be used unchanged. This wrapper keeps its host, site, and SQL transaction safeguards and reuses the unchanged PR #41 audit body rather than duplicating its Finance evidence checks.

- [Pinned application source](https://github.com/ccpcerp/ccpcerp/tree/e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5)
- [PR #40 audit](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/40), [PR #41 evidence and permissions](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/41), [PR #42 synthetic database compatibility](https://github.com/ccpcerp/ccpc-frappe-deployment/pull/42)

## Boundary and exact inputs

The human operator uses their already authorized DEVELOPMENT terminal on `ccpcerpserver`. Do not run this through an agent, service account, unverified Docker context, or PRODUCTION shell. The fixed Docker invocation verifies both pinned, running container IDs and their common local network using only selected metadata. Host and container CCPC checkouts must be clean at the exact SHA. The configured Frappe socket, configuration hooks, database environment overrides and TLS settings are outside this particular local TCP path and cause a stop. Where one is required, use a separately reviewed connection path and preserve its security requirements.

The site operator and DBA independently verify the exact development site, local Docker account and route, the database container and schema, its MariaDB hostname and ID, and the authorized named pilot scope. Use existing trusted admin evidence. Do not copy site configuration, identities, certificate material or credentials into GitHub. Matching input objects record the checks but cannot prove the operator identities or independent verification by themselves.

Create a private input JSON outside the app checkout with `site_reviewer`, `database_reviewer`, and identical `site_binding` and `database_binding` objects. Each binding object has:

| Field | Required private value |
|---|---|
| `host`, `site`, `commit` | `ccpcerpserver`, `development.localhost`, and the full application SHA above |
| `app_container_id`, `db_container_id`, `network_id` | Full 64-hex IDs of the existing DEVELOPMENT app container, DB container and common local Docker network |
| `db_host`, `db_ip`, `port` | Configured effective DEVELOPMENT service name, its exact private IPv4 address on that network, and the reviewed TCP port as an integer |
| `schema`, `principal` | Verified literal schema and negotiated MariaDB `CURRENT_USER()` identity |
| `server_hostname`, `server_id`, `timezone` | Independently verified MariaDB hostname, numeric server ID, and Frappe IANA timezone |
| `pilot` | Exact privately approved ERPNext record keys under `slip`, `company`, `requesting`, `beneficiary`, `equipment`, `item`, `warehouse`, `expense` |

The operator supplies the proposed Stockroom issuer at a hidden terminal prompt. Do not put it or any password in the binding file.

The guest reads the normal Frappe common and site configuration privately and compares the non-secret binding fields. It does not run Frappe init, configuration hooks, login, worker code, migrations, or document methods. It connects only to the independently verified private container IP. The existing site credential stays inside that short-lived operator process. This route intentionally does not check for a SELECT-only login because the normal site principal may be write-capable. The boundary is the human-run pinned program, fixed parameterized statements, disabled client multi-statements and local infile, and the server-enforced READ ONLY transaction. The first SELECT validates the connected identity inside that transaction. The connection rolls back and closes on every exit. No generic SQL access or credentials are delegated to Codex.

## Single execution command

After independent review and separate authorization, obtain the exact reviewed deployment repository commit in an already trusted review clone. Stage into a new private directory outside the app checkout. Set `approved` to the exact approved 40-character commit SHA from the PR review and `review_clone` to the trusted clone's absolute path. Never fetch or stage from an unverified moving branch or pipe remote source into an interpreter.

```bash
(
  set -euo pipefail
  umask 077
  [[ $approved =~ ^[a-f0-9]{40}$ ]]
  test "$(git -C "$review_clone" rev-parse --verify "$approved^{commit}")" = "$approved"
  stage=$(mktemp -d "$HOME/ccpc-dev-preflight.XXXXXXXX")
  path=scripts/development/operator
  for name in run_dev_ws_preflight.py ws_readiness_audit.py SHA256SUMS-dev-ws-preflight; do
    git -C "$review_clone" show "$approved:$path/$name" > "$stage/$name"
  done
  cd "$stage"
  sha256sum --check --strict SHA256SUMS-dev-ws-preflight
  printf 'Verified private staging directory: %s\n' "$stage"
)
```

Independently match the expected digests from this reviewed commit. Both staged files must report OK. Stop if any step rejects the commit, input, or hash. Keep the private directory owner-writable only and check the hashes again immediately before invoking Python.

| Staged file | Reviewed SHA-256 |
|---|---|
| `run_dev_ws_preflight.py` | `53500835d347e34a5edfc35fdb739802ad5a12eff6de36093257a25db6c09494` |
| `ws_readiness_audit.py` | `556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927` |

From that verified staging directory, after the operator and DBA privately confirm the live binding:

```bash
sha256sum --check --strict SHA256SUMS-dev-ws-preflight >&2 &&
  /usr/bin/python3 -I -B ./run_dev_ws_preflight.py /approved/private/dev-pilot-binding.json
```

Keep staging and checksum output operator-side. Share only the sanitized Python results. The wrapper rechecks the pinned audit digest before Docker access and inside the guest. The guest requires the existing bench MySQLdb 2.2.7 driver and will stop before opening a database connection if its version differs. No package installs or account changes are part of the live operation.

## Scope and outcomes

The reused audit checks the persisted Draft and sole one-unit item, requesting and actual beneficiary Department masters, equipment and section, warehouse ownership, stock and valuation, group and serial/batch flags, signed effective Expense and independently approved beneficiary Center mapping, linked vouchers, posting schema/settings and named-user role/Company evidence. The audit runs in one consistent snapshot. Effective form/document/report permissions, specific serial/batch selection, extra commitments, active web/worker code, and posting-period controls remain human checks. The snapshot never authorizes UAT.

Only fixed `PASS | check | explanation`, `FAIL | check | explanation`, or `UNVERIFIED | check | explanation` lines leave the preflight. An observed failed check has exit 1. Unresolved evidence without a definite failure has exit 2. No identities, grants, configuration, balances, approval references or exception details belong in shared output.

## Validation evidence

19 offline tests passed. The host Python used for validation was 3.14.4. In the NIC-free, unprivileged disposable guest, MariaDB 11.8.6 and native MySQLdb 2.2.7 accepted the exact wrapper connection arguments, including its timeouts. Native capability flags confirmed that multi-statements and local infile were disabled. The actual wrapper accepted the synthetic server identity and executed a parameterized SELECT in an active READ ONLY snapshot. A synthetic account with UPDATE rights received server error 1792 for an attempted write inside that same transaction mode. The wrapper rejected a wrong server identity before any application read. The PR #42 TLS/grants probe passed in the same disposable run.

The synthetic callback exercises the connection and transaction path. It does not validate live DEVELOPMENT binding, authorization, worker state, full ERPNext records or posting. The site's operator and DBA must verify their binding independently and in private.
