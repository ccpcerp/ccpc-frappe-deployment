# CCPC Codex security regression tests — CircleCI manual-only review

**Status:** GitHub-only configuration proposal on deployment repo draft PR #39. No CircleCI project connection, manual run, context, account plan, credit balance, deployment, or host action has been verified or executed by ChatGPT.

## Why this exists

On 2026-11-20, GitHub-hosted Actions run `44650795584` failed **before running tests**. Its exact operator-supplied annotation said: “The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings”. This identifies an account payments/spending eligibility condition, not a Python assertion failure. No payment changes are authorized.

The project owner volunteered availability of CircleCI. The connected GitHub source for **the separate custom-app repository** `ccpcerp/ccpcerp`, release branch `release/withdrawal-department-phase1-2026-11-17`, already includes a CircleCI config with opt-in test pipelines and approval gates. We **have not verified** that the **deployment repository** `ccpcerp/ccpc-frappe-deployment` is connected to CircleCI, that its project/org identity matches, or what credits are available.

The deployment review branch previously had no `.circleci/config.yml`. Added one for a **single source-only Python unittest job**, without altering the custom-app CircleCI config or the existing (blocked) GitHub Actions YAML.

## Safety contract for this configuration

- `run_codex_source_tests` is a **boolean pipeline parameter defaulting to false**. A normal push/PR does **not** run tests or consume compute time under this workflow.
- Workflow additionally requires a **human approval job** before the actual compute job.
- Branch filter locks both jobs to `review/codex-proxy-network-hardening-2026-11-19`.
- `approved_codex_commit` is a **40-character exact commit SHA**, default empty. The runner checks `git rev-parse HEAD` equals both `CIRCLE_SHA1` and the explicitly supplied approved SHA.
- Runner validates `CIRCLECI=true`, expected project repo name, branch, job and nonempty CircleCI identity values before checkout; a mismatched instance fails closed.
- Uses only `cimg/python:3.14`, `resource_class: small`, checkout and stdlib unittest. No orbs, workflows on a schedule, Docker-in-Docker, sidecar database, Codex CLI, Squid execution, `pip install`, API credentials, secrets, contexts, GitHub releases, file uploads, writes to GitHub, or deployment commands. The suite is limited to the two known offline Python test modules and requires **exactly 81 discovered tests** for the current review head. Test execution is bounded at 120 seconds. CircleCI images still entail normal external registry/download behavior; inspect company policy and credits before any manual run.
- The job does **not** use the actual DEVELOPMENT or PRODUCTION host, private databases, NAS, Docker bridge, firewall or network reachability. A CircleCI PASS must not be described as a live isolation, Squid-parser, reboot persistence or deployment test.

## Manual onboarding steps — NOT executed

1. **First check current plan/credits and policy** in CircleCI, without adding a payment method or changing budgets. Manual jobs may consume CircleCI credits, including on the Free plan.
2. Confirm the **deployment repository**, not just `ccpcerp/ccpcerp`, is already connected to CircleCI. If not, obtain **separate owner approval** before connecting it, since connecting could add triggers. Do not create a new integration solely because a YAML file exists.
3. Verify that CircleCI reads the review branch's `.circleci/config.yml` and accepts pipeline-parameter triggers for this project/integration. Check the CircleCI project's actual organization and repository identity; if it differs from the guarded identity, correct the reviewed GitHub source before execution rather than weakening security checks at runtime.
4. Obtain a **fresh owner-approved exact PR #39 HEAD SHA** after reviewing its diff and any moving base changes. Do not reuse an obsolete commit from this document.
5. Only if credits and integration are independently confirmed, deliberately trigger a CircleCI pipeline **on the exact review branch** with `run_codex_source_tests=true` and `approved_codex_commit=<approved full 40-char HEAD SHA>`. This is an **explicit manual action**; ChatGPT has not performed it.
6. The workflow should remain at `authorize-codex-source-tests` (approval hold). Review project identity/credit allowance, then manually approve the hold. If either condition is uncertain, cancel/leave unapproved.
7. Examine actual CircleCI job logs: preflight identity, exact SHA, exactly 81 unittest methods, complete success. Report pipeline URL, commit SHA, job status and exact test count. If failed, diagnose the specific step; do not auto-rerun or change billing settings.

**CircleCI project integration and credit status are UNVERIFIED.** This document does not assert that CircleCI is free for this account, that GitHub Actions is repaired, or that any CircleCI job has run. Do not instruct the user to enter credentials in ChatGPT.

## What is still required before any release

Source-only regressions already passed **75/75 independently** in an isolated Python workspace at Step 93, after GitHub blob-hash verification. A future CircleCI PASS would provide an independent CI rerun, **not** proof of live isolation. Keep original lab firewall reload/reboot persistence, per-launch bypass protection, two-bridge pre-enforcement, Squid outgoing DNS/SSRF controls, image pinning/nonroot runtime, and controlled nonproduction network-canary tests as separate NO-GO gates.

**No merge, Docker/network/firewall/UFW/systemd service operation, DEVELOPMENT pull or PRODUCTION deployment is authorized by this CircleCI source addition.**

## Updated resource-gate test count (2026-11-20)

The review branch now declares **81** stdlib-only Python regressions (66 in `test_safety_policy.py`, 15 in `test_lab_firewall_guard.py`), following the six proposed resource-governance tests. The CircleCI configuration was corrected to refuse any count other than 81 in [commit `0ac2a588`](https://github.com/ccpcerp/ccpc-frappe-deployment/commit/0ac2a58808e3def622dd78e155afeee8969bea2d). Historical **75/75** offline verification at Step 93 applies only to the earlier source version, not this expanded suite.

Seven **focused, manually isolated Python checks** of the unchanged resource-bound validation functions were executed successfully against a byte-for-byte matched excerpt of `codex-dev-agent/check_compose.py` (source blob `4e1be61a27b73ee7afd39e82995db4e0b094f93d`), including the six scenarios modeled by the new tests and a baseline across all five services. These were **not** executed via the repository's actual `test_safety_policy.py` module and **do not** constitute an 81/81 suite pass. The official 81-test suite still requires execution from the exact reviewed private checkout on an eligible, trusted isolated runner; private GitHub-hosted Actions is known to be blocked by its pre-run billing/spending annotation. No CircleCI pipeline, provider-connection change or credits were consumed by this documentation change.
