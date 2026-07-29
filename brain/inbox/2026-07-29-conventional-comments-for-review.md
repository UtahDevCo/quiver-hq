---
type: Observation
title: Review feedback uses Conventional Comments
description: Every review comment carries an explicit label and blocking-ness, so the reader never guesses whether feedback is a blocker.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [review, communication]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
sources:
  - id: git-conventions
    resource: projects/zamp/.claude/agents/git-conventions.local.md
    title: Git Conventions — Review Comment Style (declared canonical source)
    author: human:christopher
  - id: upstream
    resource: https://conventionalcomments.org
    title: Conventional Comments
---

# Observation

Format: `<label> [decorations]: <subject>` with an optional discussion body.
Bold the label where Markdown renders.

| Label | Blocks merge? |
|---|---|
| `issue` | **Yes**, unless `(non-blocking)` |
| `todo` | Usually yes |
| `suggestion` | No, unless `(blocking)` |
| `question` | Respond; change only if the answer implies it |
| `praise` | No — **use it at least once per review** |
| `nitpick` / `note` / `thought` / `typo` / `polish` / `quibble` | No |
| `chore` | Context-dependent |

Decorations: `(blocking)`, `(non-blocking)`, `(if-minor)` — these override the
label's default.

**Resolving incoming comments:** `issue`/`todo`/anything `(blocking)` → fix
before next push. `suggestion` → apply if quick or clearly better, else reply
with rationale. `question` → answer. `nitpick`/`note`/`thought`/`praise` →
optional, brief ack is fine.

# Why it matters

The source file declares this the "single source of truth ... every PR review,
every inline comment, every thread reply, and any critique Claude leaves MUST
follow this format." That is an explicit instruction to agents, not just humans.

Unlabeled feedback forces the reader to infer severity, which is where review
friction comes from. It also makes an agent's review output triageable.
