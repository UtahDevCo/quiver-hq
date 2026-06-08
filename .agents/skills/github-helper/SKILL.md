---
name: github-helper
description: Provides capabilities to use the GitHub CLI (gh) to fetch PR comments, and git commands to stage, commit, and push changes. Use when performing git operations or pulling PR reviews/comments.
---

# GitHub and Git Helper Skill

This skill equips agents with standard guidelines and procedures for working with git repositories and using the GitHub CLI (`gh`) to manage pull requests, pull down comments, commit, and push changes.

## Core Capabilities

### 1. Fetching PR Comments and Details
Before addressing PR comments or review feedback, fetch the comments using the GitHub CLI:
*   **View PR Status and Recent Comments**:
    ```bash
    gh pr view --json comments,reviews,status,url
    ```
*   **List all Review Comments in JSON**:
    ```bash
    gh api repos/{owner}/{repo}/pulls/{pr_number}/comments --jq '.[] | {id, body, path, line, user: .user.login}'
    ```

### 2. Staging, Committing, and Pushing Changes
When tasks are completed, commit and push changes directly:
*   **Check changes**: `git status` and `git diff`
*   **Stage files**: `git add <file1> <file2>` (or `git add .` if staging all changes)
*   **Commit changes**:
    ```bash
    git commit -m "feat/fix: <descriptive message>"
    ```
*   **Push changes**:
    ```bash
    git push origin <branch-name>
    ```

## Execution Safeguards
*   Always run local builds or tests (e.g., `npm run build`, `go test ./...`) before committing and pushing.
*   Verify your active branch matches the ticket branch using `git branch --show-current`.
