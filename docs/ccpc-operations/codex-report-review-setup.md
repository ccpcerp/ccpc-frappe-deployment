# CCPC Codex Report AI Review — Setup Guide (DRAFT)

**Status:** Draft workflow on a separate review branch, not merged or enabled.

## Purpose

Read a single, sanitized Codex DEVELOPMENT completion report published as a text comment on [Issue #22](https://github.com/ccpcerp/ccpc-frappe-deployment/issues/22), request a bounded AI review, and post one concise review comment back to the same issue.

There is **no** access to ERPNext, Docker, MariaDB, Redis, production, SSH credentials, Git write, or deployment scripts in the GitHub Actions job. No repository checkout occurs. This automation is not an approval to execute reviewed recommendations.

## Why GitHub storage stays small

- Reports and reviews are issue comments only, not files committed to Git.
- Maximum report input: **12,000 UTF-8 bytes**; target review output: **6,000 characters**.
- Zero artifact uploads and zero caches.
- Runs only on `issue_comment: created` events, and only for Issue #22 with a matching configured report publisher.
- A distinct report marker is required: `<!-- ccpc-codex-report:v1 -->`.
- A review marker tied to the original GitHub comment ID prevents ordinary duplicate review on re-runs.
- A short job timeout and bounded response-token setting reduce, but do not fully eliminate, Actions and API costs.

## Requirements before enabling

1. **Separate approved Codex publisher:** The current DEVELOPMENT container has an SSH directory available to the `frappe` user and cannot run Codex's Linux namespace sandbox. Do not store a new GitHub token in that container for unattended Codex use. Design a separately controlled report-only publisher first.
2. **Reporter identity:** Set repository variable `CCPC_CODEX_REPORTER_LOGIN` to the dedicated report publisher's GitHub login. The job will skip all other authors.
3. **Explicit enable switch:** Set repository variable `CCPC_CODEX_REVIEW_ENABLED` to `true` only after setup and approval. If unset or any other value, the review job skips.
4. **Model choice:** Set repository variable `CCPC_REVIEW_MODEL` to a supported, cost-approved OpenAI API model identifier. Do not rely on ChatGPT subscription entitlements for API billing.
5. **API credential:** Store the restricted, funded AI API key only as repository **Actions secret** `CCPC_OPENAI_API_KEY`, never in source code, issue comments, logs or chat.
6. **Budget:** Establish GitHub Actions and OpenAI API spending/usage limits appropriate to the account, and inspect ongoing costs.
7. **Manual review:** Review the workflow YAML and this guide, then merge the PR to `main` separately. GitHub `issue_comment` workflows need to exist on the default branch to trigger; the enable switch must stay off until all safety gates are complete.

## Security behavior

- Issue number, repository, issue type, report marker and exact author are checked before contacting the model.
- The same reporter identity is independently checked again via the GitHub API.
- Report text is treated as untrusted data. It is not executed.
- Model instructions request evidence-based review, limitations, and approval gates.
- Only `issues: write` is granted to the job, allowing it to read/post issue comments. The token **may** technically write other issue comments in this repository, so the script explicitly targets Issue #22.
- No GitHub or production credentials are supplied to the AI request. Only the bounded report text is transmitted to the AI API.
- Original report content must already be sanitized by the publisher. This workflow is **not** a secret-scanning or data-loss prevention substitute.
- The workflow does not modify, review or merge application code; it produces a text assessment from the published report alone.

## Expected verification sequence

1. Review the PR and configuration before merge. Confirm review job is gated off.
2. Configure the reporter and OpenAI credentials outside of source control.
3. Verify the reporter's scope and revocation path.
4. Use a **synthetic** report with the marker to test exactly one review comment.
5. Confirm no unrelated issue comments are reviewed, no loop occurs, and no artifacts are stored.
6. Verify GitHub Actions and API consumption.
7. Enable routine use only after explicit operational approval.

## Current state

Draft workflow only. **No publishing bot, AI secret, repository variables, default-branch workflow, test run, or automatic AI review has been configured by this change.**
