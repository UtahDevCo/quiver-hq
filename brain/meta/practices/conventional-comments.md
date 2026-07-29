---
type: Practice
title: Review feedback uses Conventional Comments
description: Every review comment carries an explicit label and blocking-ness, so the reader never has to guess whether feedback is a blocker.
tags: [review, communication, collaboration]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:11Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: git-conventions
    resource: projects/zamp/.claude/agents/git-conventions.local.md
    title: Git Conventions — declared the single source of truth for review feedback
    author: human:christopher
    last_modified: 2026-07-25
  - id: upstream
    resource: https://conventionalcomments.org
    title: Conventional Comments
---

# The practice

Format: `<label> [decorations]: <subject>`, with an optional discussion body.
Bold the label where Markdown renders:

> **suggestion (non-blocking):** Extract this into a shared util so both callers reuse it.

| Label | Meaning | Blocks merge? |
|---|---|---|
| `praise` | Sincere positive callout — **use it at least once per review** | No |
| `nitpick` | Trivial preference | No |
| `suggestion` | Propose an improvement; state what and why | No, unless `(blocking)` |
| `issue` | A specific problem with the change; pair with a fix | **Yes**, unless `(non-blocking)` |
| `todo` | Small necessary change before acceptance | Usually |
| `question` | Seeking clarification | Respond; change only if the answer implies it |
| `thought` | Non-blocking idea that surfaced while reviewing | No |
| `chore` | Process task before acceptance | Context-dependent |
| `note` | Non-blocking FYI | No |
| `typo` / `polish` / `quibble` | Expressive minor labels; treat as `nitpick` | No |

Decorations `(blocking)`, `(non-blocking)`, `(if-minor)` override the label's
default.

# Resolving incoming comments

- `issue` / `todo` / anything `(blocking)` → fix before the next push.
- `suggestion` → apply if quick or clearly better; otherwise reply with the
  rationale.
- `question` → reply with an answer; change code only if the answer implies one.
- `nitpick` / `note` / `thought` / `praise` → optional; a brief ack is fine.

# Why

Unlabeled feedback forces the reader to infer severity, and that inference is
where review friction comes from — a nitpick read as a blocker stalls a PR, and a
blocker read as a nitpick ships a bug.

# This applies to agent output

The source declares it covers "every PR review, every inline comment, every thread
reply, and any critique Claude leaves." An agent's review is only useful if it's
triageable, and the label is what makes it triageable.
