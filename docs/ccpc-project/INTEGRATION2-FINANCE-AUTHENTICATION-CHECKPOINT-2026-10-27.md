# Integration2 Finance authentication checkpoint — 2026-10-27

## Verified by owner-executed terminal output

Two previously provisioned Integration2-only Finance test actors for fictional Company Integration Test Issuer (TISS) passed their role and Company grant preflight. The corrected credential preflight reported no existing password records for either actor, username/password login enabled, two-factor authentication disabled and enabled password policy.

A supervised, no-echo, operator-local Frappe v16 password provisioning test verified independent strong passwords for both accounts and reported:

```text
FINANCE PASSWORD SAFETY GUARDS: PASS
Maker password validation: PASS
Checker password validation: PASS
BOTH PASSWORD VALIDATIONS: PASS
FINANCE TEST PASSWORDS: COMMITTED
TWO DISTINCT PASSWORD HASHES: VERIFIED
INTEGRATION2 CREDENTIAL SETUP: PASS
NO FINANCIAL TRANSACTIONS PERFORMED
```

The command operated on the Integration2 site only, pinned CCPC application commit 0c223d7cbe8b27c2392d8b2303c45a99dd4d8b41, guarded the exact two test actors, existing Company permissions, and protected recovery checkpoints, verified hash entries in the same transaction, and committed once. The owner did not disclose any credentials. An earlier maker-only validation attempt had stopped before any database write, followed by a separate successful read-only validation.

## Status and next step

Credential provisioning: **PASS by operator evidence**.

### Authenticated HTTP sessions: PASS — owner-executed Integration2 smoke

The owner then ran the guarded, pinned-application, Integration2-only localhost Frappe v16 session test with separately entered, private Maker and Checker credentials. It POSTed to `/api/method/login` independently for both actors, checked `message=Logged In` and valid, non-Guest session cookies, and GET-verified the actor identity via `frappe.auth.get_logged_user`. Session IDs were checked to be distinct, without printing them. The terminal returned:

```text
INTEGRATION2 AUTHENTICATED HTTP TEST
HTTP LOGIN SAFETY GUARDS: PASS
Maker HTTP LOGIN: PASS
Maker AUTHENTICATED IDENTITY: PASS
Checker HTTP LOGIN: PASS
Checker AUTHENTICATED IDENTITY: PASS
TWO DISTINCT AUTHENTICATED SESSIONS: PASS
INTEGRATION2 HTTP AUTHENTICATION: PASS
NO FINANCIAL TRANSACTIONS PERFORMED
```

**Verified gate:** Normal Frappe HTTP authentication and session-bound identity **PASS** for both Integration2 Finance test users. This is stronger than the prior direct DB-helper 8/8 PASS. It does **not** yet demonstrate actual CSRF-protected Finance workflow endpoint authorization, the Maker-as-Checker/Checker-as-Maker denials through HTTP, company boundary denial through HTTP, browser/Desk UI permissions, mapping draft/approval transaction correctness, concurrency, or stock/GL postings. New login/session metadata can be produced by normal login.

**Next bounded work:** Inspect Frappe v16 POST CSRF handling and reviewed CCPC mapping endpoint entry checks before running a safe, nonmutating HTTP authorization test. A missing or invalid CSRF token, missing revision, or intentionally invalid selector must not be misconstrued as a role-based denial. The checker approval/review endpoint locates an existing draft before authority checking, so a nonexistent revision cannot prove cross-role denial. Do not create Finance mapping records or approve/post transactions without a separately approved fixture. Keep PRODUCTION and main DEVELOPMENT untouched. No passwords/cookies/session IDs printed or committed to GitHub.

### Desk/CSRF initial diagnostic: /app redirects, /desk returns 200 and token

The owner attempted a two-actor Desk/CSRF preflight after the authenticated HTTP PASS; it stopped after "Maker AUTHENTICATED IDENTITY: PASS", before completing any Desk or Checker assertions. The diagnostic lacked reason details because it caught `RuntimeError` and displayed only the exception type. A focused Maker-only follow-up then returned:

```text
INTEGRATION2 DESK DIAGNOSTIC
MAKER AUTHENTICATION: PASS
/app HTTP STATUS: 301
/app CONTENT TYPE HTML: YES
/app CSRF TOKEN: NOT FOUND
/desk HTTP STATUS: 200
/desk CONTENT TYPE HTML: YES
/desk CSRF TOKEN: PRESENT
DESK DIAGNOSTIC: COMPLETED
NO FINANCIAL TRANSACTIONS PERFORMED
```

**Finding:** The initial assumption that `GET /app` must directly return 200 was incorrect for this DEV site; it redirects (301) while the site’s `/desk` route serves the Desk HTML (200) and `frappe.csrf_token`. GitHub Frappe v16 `frappe/www/desk.py` and `desk.html` confirm CSRF generation/rendering for the Desk page. There is no evidence from these checks of a broken authentication setting or missing CSRF support, and no reason to change routing or restart services. Only the Maker's direct Desk/CSRF readiness is shown; Checker Desk and independent CSRF tokens are not yet tested.

**Next one-step acceptance test:** Re-run a guarded two-account login + exact-identity + `GET /desk` (no redirects) + token-present/different validation for Maker and Checker. Use private no-echo passwords, separate HTTP cookie jars, do not display tokens/cookies/passwords or HTML, and no Finance POST endpoint. Normal login/session metadata may be written; no financial data changes intended. Then separately review HTTP authorization tests with true CSRF and role-denial evidence, without financial proposals/approvals or posting.
