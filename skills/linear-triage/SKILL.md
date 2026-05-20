---
name: linear-triage
description: Triage and download Linear issues into local date-indexed Markdown files for easy offline viewing and context loading. Use when asked to triage issues, fetch assigned tickets, download comments, or review tickets from a specific team, cycle, or URL (including active cycles like team/FOU/cycle/active).
---

# Linear Triage Skill

This skill allows the agent to pull issues from Linear using the community-maintained `linear` CLI via `bunx`, downloading their descriptions, states, priorities, metadata, and comments directly into the active workspace's local `./temp/linear/YYYY-MM-DD/` folder.

## Core Capabilities
1. **Assigned Tickets Triage:** Defaults to pulling the current authenticated user's unstarted and started tickets.
2. **Cycle Triage:** Can pull all tickets from a specific cycle (including the `active` cycle) for a given team.
3. **URL Parsing:** Automatically extracts team keys, cycle IDs, or specific issue IDs from Linear URLs.
4. **Offline Markdown Files:** Generates a separate `.md` file for each issue and a master `summary.md` index file for the day.

---

## When to Use This Skill
Use this skill whenever the user says:
- *"Triage my issues"* or *"What's on my plate?"*
- *"Fetch issues from the active cycle"* or *"Triage the FOU team's active cycle"*
- *"Triage this Linear URL: <url>"*
- *"Import comments and details for issue FOU-1234"*

---

## Execution Guide

The skill executes via a helper script `triage.js` bundled in its `scripts` directory.

### Step 1: Execute the Triage Script
Run the script using `bun` from the root of the active workspace. Pass the relevant flags based on the user's request.

#### 1. Default (My Assigned Issues)
```bash
bun /Users/chris/dev/quiver-hq/skills/linear-triage/scripts/triage.js
```

#### 2. Triage a specific Cycle or Team URL
```bash
bun /Users/chris/dev/quiver-hq/skills/linear-triage/scripts/triage.js --url "https://linear.app/buildwithfoundation/team/FOU/cycle/active"
```

#### 3. Triage a specific Single Issue URL
```bash
bun /Users/chris/dev/quiver-hq/skills/linear-triage/scripts/triage.js --url "https://linear.app/buildwithfoundation/issue/FOU-3556/sms-stand-up"
```

#### 4. Filter by specific assignee or team manually
```bash
bun /Users/chris/dev/quiver-hq/skills/linear-triage/scripts/triage.js --assignee chris.esplin --team FOU --todo
```

### Step 2: Read the Generated Files
Once the script completes:
1. Locate the output directory (typically `./temp/linear/YYYY-MM-DD/`).
2. Read `summary.md` to see the complete table of contents and quick statistics of triaged issues.
3. Read individual `<issue-id>.md` files for full details, descriptions, and comments.

### Step 3: Present Results to the User
1. Show a clean, well-formatted summary of the triaged issues.
2. Provide a list of the files that were written to their local workspace.
3. Offer to help them tackle the most urgent or relevant issues (e.g., "Would you like me to start working on FOU-3556?").

---

## Troubleshooting
- **No Workspace Credential Error:** If the command fails because of missing credentials, ask the user to log in in their terminal using:
  ```bash
  bunx linear auth login
  ```
- **Directory / Team Scope Error:** The script will automatically try to resolve the authenticated user, but if it fails, make sure you pass `--team FOU` or `--all-teams`.
