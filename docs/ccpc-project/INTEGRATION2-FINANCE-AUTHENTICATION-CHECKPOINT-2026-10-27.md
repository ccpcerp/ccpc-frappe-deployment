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
