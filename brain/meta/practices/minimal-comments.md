---
type: Practice
title: Comments explain non-obvious why, never what
description: Prefer self-documenting code. A comment that restates the code is noise; only a genuinely non-obvious why earns a line.
tags: [comments, readability, style]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "a docblock paraphrasing a function's name and signature"
    why: "adds maintenance burden and drifts out of sync with the code it describes"
    instead: "no comment — let the signature speak"
  - term: "a multi-line explanatory block comment in an implementation file"
    why: "if the code needs paragraphs to explain, the code is the problem"
    instead: "one terse line on the genuinely non-obvious why, or refactor until it isn't needed"
sources:
  - id: claude-local
    resource: projects/zamp/CLAUDE.local.md
    title: zamp CLAUDE.local.md — code comments
    author: human:christopher
    last_modified: 2026-07-25
  - id: trikin-agents
    resource: projects/trikin/AGENTS.md
    title: "trikin AGENTS.md — comments only for complex logic, non-obvious decisions, or important workarounds, stated independently of zamp"
    last_modified: 2026-07-30
---

# The practice

Prefer self-documenting code. Comment only a genuinely non-obvious **why** — a
subtle invariant, a workaround, a gotcha — and keep it to a single terse line
where possible.

- No comment that merely restates what the code already says.
- No multi-line explanatory block comments in implementation files.
- No docblocks that paraphrase a function's name or signature.
- Story and example descriptions: one concise line.

# Scope — this is the part that gets violated

Applies to code **you** write or edit. **Do not touch pre-existing comments
authored by others.** Only trim comments that are part of your own change.

Rewriting someone else's comments turns a focused diff into a style argument and
buries the actual change. If a neighbouring comment is genuinely wrong, say so in
review rather than fixing it silently.

# Why

This is the single highest-frequency style decision in any change. Getting it
wrong produces a diff that is technically correct and unpleasant to read, and it
compounds — comment noise is the thing that makes a file feel unmaintained long
before the code does.

# Provenance

From `CLAUDE.local.md`, which is git-ignored and therefore Chris's personal
standard rather than any team's. That makes it unusually well-evidenced as a meta
practice despite coming from a single repo.
