---
type: Workflow
title: Branch and PR naming enforced by CI regex
description: Linear ticket prefix, lowercase in branches and uppercase in PR titles. Both are CI-gated; commits are not.
tags: [git, ci, linear]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: git-conventions
    resource: projects/zamp/.claude/agents/git-conventions.local.md
    title: Git Conventions — branch, PR title, commit message
    author: human:christopher
  - id: ci
    resource: projects/zamp/.github/workflows/pr-linting.yml
    title: CI enforcement
---

# The rules

**Branch** — `^(eng|rev|cus|fil|pla|out|inn|tax)-\d+-[a-z\d-]+$`
Lowercase prefix. `out-793-my-filings-tab` ✓ · `OUT-793-my-filings-tab` ✗

**PR title** — uppercase prefix, space, title-cased description, no colon.
`OUT-793 Add My Filings tab to admin filing management page` ✓

**Commits** — no CI gate. Either `TICKET-NNN Short imperative description` or, for
typed changes, `fix(OUT-793) Apply Prettier formatting to filters.client.tsx`. Short,
imperative, no trailing period.

Prefixes: `eng`, `rev`, `cus`, `fil`, `pla`, `out`, `inn`, `tax`.

**Shortcut:** copy the branch name from the Linear ticket — its button produces the
correctly-lowercased slug.

# The thing to remember

Case differs between branch (lower) and PR title (upper) for the *same* ticket, and
both are CI-enforced. That asymmetry is the whole trap.
