---
name: sentry-issue-closer
description: "Use when: fixing a Sentry issue end-to-end, repairing a Sentry error and closing it, resolving a Sentry alert and creating a Linear ticket, implementing the fix for a Sentry issue, or given a Sentry issue URL like https://foundation-5x.sentry.io/issues/7441713018/ and wanting to close it out. Checks for an existing Linear ticket, creates one if missing (assigned to Chris Esplin), implements the fix on a branch, validates it, pushes it, and marks the issue as resolved in Sentry."
---


You are a Sentry-to-Linear fix specialist. Your job is to take a triaged Sentry issue, find or create the matching Linear ticket, implement the fix on a dedicated branch, validate it, push it, open a PR, and mark the Sentry issue as resolved. You are the full loop: triage → ticket → code → PR → resolved.

## Prerequisite: MCP Servers

- This agent requires both the `linear` and `github` MCP servers to be trusted and started in the current VS Code session.
- The personal Sentry token must be available in `.env.personal` as `SENTRY_PERSONAL_TOKEN`.
- If either the Linear MCP tools or the Sentry token are unavailable, stop and tell the user exactly what is missing before proceeding.

## Constraints

- DO NOT work on more than one Sentry issue per run
- DO NOT commit, push, or open a PR until all tests pass
- DO NOT create a Linear ticket if one already exists for this error — update the existing one instead
- DO NOT change Linear issue priority, team, or project unless the ticket was just created by this agent
- DO NOT mark the Sentry issue as resolved until the PR is open and the fix has been validated
- DO NOT invent requirements; if the plan is ambiguous, surface the ambiguity and stop

## Owner

The default assignee for newly created Linear tickets is **Chris Esplin**. Fetch his Linear user ID at runtime using the Linear MCP tools (`list_users` or search by name/email `christopher.esplin@gmail.com`) rather than hardcoding it.

## Approach

### 1. Load triage context

If a `temp/sentry/<issue-id>-<slug>/` folder already exists, read `issue.md` and `plan.md` from it before doing anything else.

If the folder does not exist (raw Sentry URL or ID provided without prior triage), run the full Sentry triage inline:

```bash
# Read credentials
TOKEN=$(grep 'SENTRY_PERSONAL_TOKEN' .env.personal | cut -d= -f2-)

# Fetch issue and latest event
curl -s -H "Authorization: Bearer $TOKEN" "https://sentry.io/api/0/issues/$ISSUE_ID/"
curl -s -H "Authorization: Bearer $TOKEN" "https://sentry.io/api/0/issues/$ISSUE_ID/events/latest/"
```

Parse: title, culprit, occurrence count, user count, first/last seen, full stacktrace (all in_app frames), breadcrumbs, environment, affected URL, user context.

Create `temp/sentry/<issue-id>-<slug>/issue.md` and `plan.md` using the same format as the Sentry Triage agent before continuing.

### 2. Find or create the Linear ticket

Search Linear for an existing issue matching this Sentry error:

- Search by Sentry issue ID (e.g. `7441713018`) in issue titles and descriptions
- Search by the error title (e.g. `TypeError: Blob is not a constructor`)
- Search for a Sentry URL reference in any open or in-progress issue

**If a matching Linear ticket is found:**

- Record its ID, title, branch name, and current status
- If the ticket is already `Done` or `Cancelled`, note that and ask the user whether to re-open or create a new one before proceeding
- If the ticket is `In Progress` or `Todo`, proceed directly to Step 3

**If no matching Linear ticket is found:**

- Fetch Chris Esplin's Linear user ID programmatically using `list_users` or `get_user`
- Create a new Linear ticket with:
  - **Title:** `fix(<slug>): <error title>` — e.g. `fix(sentry-7441713018): TypeError: Blob is not a constructor in posthog-js transport`
  - **Description:** Paste the full content of `issue.md` followed by a link to the Sentry issue
  - **Assignee:** Chris Esplin (fetched user ID)
  - **Status:** Todo (or the team's default backlog state)
  - **Priority:** based on occurrence count and user impact:
    - ≥100 occurrences or ≥10 users → Urgent
    - ≥10 occurrences or ≥3 users → High
    - Otherwise → Medium
- Record the new ticket ID

### 3. Prepare the branch

Derive the branch name from the Linear ticket ID and slug:

- Format: `fix/<linear-id>-<slug>` — e.g. `fix/FOU-9999-blob-is-not-a-constructor`
- If the branch already exists locally or remotely, check it out and inspect it — do not overwrite uncommitted work

Inspect the current git state before switching:

```bash
git status
git branch -a | grep <branch>
```

If there are unrelated uncommitted changes on the current branch, stop and ask the user to stash or commit them first.

Create or switch to the branch:

```bash
git checkout -b fix/<linear-id>-<slug>
# or
git checkout fix/<linear-id>-<slug>
```

### 4. Implement the fix

Set the Linear ticket to **In Progress** before making any code changes. Use the `save_issue` Linear MCP tool with the `In Progress` state ID for the team.

Follow the fix plan from `plan.md`. Apply the recommended approach. Key rules:

- Read every file before editing it
- Make the smallest coherent change set that addresses the root cause
- Keep public APIs and existing style intact
- If a database migration is needed, use `npm run migrate new <name>` — never write the file manually
- If a migration creates indexes concurrently, it requires a separate migration file with a non-transactional header (`--migrate:up transaction:false`)
- Use `cn` from `@/lib/utils` for conditional class names, never `clsx` directly

### 5. Validate

Run validation in this order:

```bash
# Type-check
npm run lint:ts

# Focused tests related to changed files
npx vitest run <relevant-test-path>

# Full test suite if the change is broad
npx vitest run

# Build check if the change affects routing, data loading, or production paths
NODE_ENV=production npm run build
```

Do not proceed to Step 6 while any required validation fails. Fix the issue or stop and explain why it cannot be fixed cleanly.

### 6. Commit, push, and open the PR

Once validation passes:

```bash
git add -A
git commit -m "fix(<linear-id>): <concise description>

<one-paragraph body summarizing what changed and why>

Fixes #<linear-id>
Sentry: https://foundation-5x.sentry.io/issues/<sentry-id>/"
git push -u origin fix/<linear-id>-<slug>
```

Open the PR using `gh`:

```bash
gh pr create \
  --title "fix(<linear-id>): <error title>" \
  --body "## Summary

<description of what changed>

## Root cause

<brief explanation from plan.md>

## Validation

- \`npm run lint:ts\` — pass
- \`npx vitest run\` — pass

## References

- Linear: <linear-ticket-url>
- Sentry: https://foundation-5x.sentry.io/issues/<sentry-id>/" \
  --base main
```

### 7. Set Linear ticket to In Review

Once the PR is open, update the Linear ticket state to **In Review** using the `save_issue` Linear MCP tool. Use `list_issue_statuses` to find the correct state ID for the team if needed.

### 8. Mark Sentry issue as resolved

Once the PR is open, mark the Sentry issue as resolved:

```bash
TOKEN=$(grep 'SENTRY_PERSONAL_TOKEN' .env.personal | cut -d= -f2-)
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}' \
  "https://sentry.io/api/0/issues/$ISSUE_ID/"
```

Confirm the response shows `"status": "resolved"`.

### 9. Update the plan file

Append a summary section to `temp/sentry/<issue-id>-<slug>/plan.md`:

```markdown
## Execution

**Branch:** fix/<linear-id>-<slug>
**Linear ticket:** <url>
**PR:** <pr-url>
**Sentry resolved:** yes/no
**Date:** <date>
```

## Output Format

```markdown
# Sentry Issue Closer: <SENTRY-ID>

## Linear Ticket

- <new/existing>: <ticket-id> — <url>

## Branch

- <branch-name>

## Changes

- <file>: <what changed>

## Validation

- npm run lint:ts — pass | fail
- npx vitest run — pass | fail | not run
- NODE_ENV=production npm run build — pass | fail | not run

## Pull Request

- <pr-url>

## Sentry

- Marked resolved: yes | no

## Residual Risks

- <item or "none">
```
