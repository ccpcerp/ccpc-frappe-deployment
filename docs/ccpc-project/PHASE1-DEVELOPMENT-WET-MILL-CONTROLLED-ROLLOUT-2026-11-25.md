# CCPC ERPNext — controlled DEVELOPMENT preflight for cross-Department routine maintenance

**Owner authorization, 2026-11-25:** Owner approved **preparing a controlled DEVELOPMENT update** after a verified hosted GitHub MariaDB run. This document prepares and gates that update; it **does not** report a DEVELOPMENT pull, migration, user/Finance master change, stock posting, or production deployment.

## GitHub exact-source checkpoint

- Authoritative application: `ccpcerp/ccpcerp` draft PR [#44](https://github.com/ccpcerp/ccpcerp/pull/44), head branch `review/phase1-maintenance-integrated-tests-2026-11-24`, current reviewed head `e5c6f4c7f8f2121b26198bc2ff94d7be42c948b5`. PR open/draft/unmerged. This is an explicit **reviewed commit pin**, not an instruction to checkout an arbitrary default branch.
- GitHub-hosted isolated acceptance [Actions run #45557491302](https://github.com/ccpcerp/ccpcerp/actions/runs/45557491302): **success**, 32 offline policy/static/CI tests, 10 native MariaDB integration tests, two separate real DB/HTTP regressions: **44/44 PASS**, **20/20 workflow steps successful**. Synthetic disposable CI only.
- Previous operator-reported running MAIN DEVELOPMENT app code at `b599395f9c65cc6c6b8cc1b2750bc4559547161a`; **must recheck live**. GitHub compare `b599395...e5c6f4...` confirmed **ahead 7, behind 0**, 11 changed files: one application runtime policy file `ccpcerp/ccpc_erp/phase1_maintenance_use.py`, plus CI/test/docs; **no modified migration/DocType JSON/code files in this exact compare**. This does not prove live DEV has no private changes or other deployed modifications.

## Original requirement, now approved

The department actually benefiting from material consumption must receive the original material issue attribution, irrespective of which Department requests it. Maintenance personnel may use a bearing on Wet Mill equipment. Exact `Work For Department` **must remain Wet Mill**, not Maintenance. The report `CCPC Department Material Consumption` records **gross original issue** from outbound SLE valuation, not net after returns or a certified per-Department GL cost. **A Department is not a Cost Center**. The existing B/C allocation still requires separately signed, effective, Finance-approved **Department-only Center Mapping Scope for each actual beneficiary**; multiple Department scopes may independently map to the same approved shared Cost Center. Do not auto-copy Maintenance mapping to Wet Mill or create new Finance approvals as part of a source rollout.

## STOP condition: inspect before touching MAIN DEVELOPMENT

Physical DEVELOPMENT server `ccpcerpserver` (PRODUCTION is a separate, entirely prohibited host), app checkout previously reported as `/home/gani/deployments/frappe_docker/development/frappe-bench/apps/ccpcerp`, bench site `development.localhost`. Only the operator has trusted console access; ChatGPT's GitHub connector **cannot directly inspect host checkout or DB**.

First, operator runs only an unprivileged **read-only terminal preflight**, showing the exact host, absolute app path, HEAD SHA, branch/detached status, tracked and untracked change **counts** and existence of the expected local bench site; do not paste tokens, secrets or site configuration contents. No `git pull`, `git reset`, `git checkout`, `git switch`, `bench migrate`, `docker restart`, or write operation in this first step. If git tracked/untracked changes are nonzero, review them safely before considering any source update and preserve all uncommitted ERPNext changes outside this app directory too.

Then independently inspect the site's **recent usable with-files backup** and restore/off-host recoverability (previous 2026-11-25 09:10 archives were only checksum-tested, not restore-tested or verified off-host); verify Docker/bench mounts and `development.localhost` identity before any possible command requiring them. Do not weaken backup gate merely because hosted CI passed. Any migration or source pull is a **separately controlled reviewed execution step** after these gates. Production untouched.

## Draft Withdrawal Slip — preserve, do not post

Operator-supplied Draft `WS-2026-00008` was reported `docstatus=0`; prepare identity `mechanical_supv@ccpc.com`, requesting Department `Maintenance Department - CCPC`, **genuine beneficiary** `Wet Mill Plant - CCPC`, Equipment `WD-401`, Item **`ITEM-00010`**, one unit, Warehouse 1, Routine Maintenance. The original one-unit acceptance was previously specifically scoped to **`ITEM-00004`** and Maintenance beneficiary; owner has since approved changing the eligible beneficiary **rule**, but this does **not** automatically authorize posting a different live item without a fresh business/inventory readiness check. Do not create another slip or change the true Wet Mill beneficiary to force legacy test criteria.

Before any approval or **Issue Materials**, independently check from the live DEVELOPMENT site:
1. Reload the saved Draft and verify persisted child item row (the owner's JSON included `__unsaved:1`), exact item group (must not infer Bearings solely from name), active status, serial/batch controls, Warehouse/stock balance and valuation, correct same-Company issuer/requestor and all applicable effective named-user permissions; independent Stockroom issuer required.
2. Equipment Registry `WD-401` Company, Department and Section must support the explicit beneficiary or the conflict guard deliberately denies posting; do not silently override master data.
3. Finance revisions: current signed, independently authorized and effective Expense scope for actual Item Group and **separate Wet Mill beneficiary Center Mapping Scope**, exact approved account and valid Cost Center, required Department GL dimension, current posted-date applicability, no duplicate/retired/conflicting approvals. The previously reported Maintenance Center revision `dogpv13jma` alone does **not** authorize Wet Mill.
4. Distinct real Stockroom user with effective authorization; no existing linked Stock Entry for this Slip, pre-issue SLE/GL/Bin baseline and recovery assurance.
5. Owner and Accounting confirm whether to use the owner's actual `ITEM-00010` request as the one-unit DEVELOPMENT acceptance, rather than the earlier `ITEM-00004` scenario. Real account/report posting requires a fresh one-time final human go/no-go before any irreversible submit.

## Controlled update after preflight

If the operator's **read-only** preflight confirms the correct host/site, no uncommitted work at risk, and recoverable backup, prepare an exact, reviewed, safe Git operation **without resetting, switching, stashing, merging or modifying unrelated ERPNext app changes**. Prefer fetched exact commit with verified ancestry; do not pull `main`/unverified PR head. Record pre/post HEAD and changes and keep transaction/report state intact. The actual command must be chosen from verified DEV output. No blanket source pull or migration is authorized by merely completing this checklist.

Post-update DEV verification must include code SHA, no unexpected schema changes, compiled module import, UAT security and signed mapping checks with no real voucher, then explicit posting gate. If anything fails, stop with state intact and document to GitHub; no blind retry/cancellation.

## Status

- GitHub policy correction and hosted CI: **verified complete**.
- MAIN DEVELOPMENT host preflight, recoverability, financial/scope authority, source rollout, one-unit posting: **NOT verified; on hold**.
- PRODUCTION: **outside scope and untouched**.
