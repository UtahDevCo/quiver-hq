---
type: Observation
title: Comments explain non-obvious why, never what
description: Prefer self-documenting code. A comment that restates the code is noise.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [comments, readability]
status: draft
not:
  - term: "docblock paraphrasing a function's name and signature"
    why: "adds maintenance burden and drifts out of sync with the code"
    instead: "no comment; let the signature speak"
  - term: "multi-line explanatory block comment in an implementation file"
    why: "if the code needs paragraphs to explain, the code is the problem"
    instead: "one terse line on the genuinely non-obvious why, or refactor"
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
sources:
  - id: claude-local
    resource: projects/zamp/CLAUDE.local.md
    title: zamp CLAUDE.local.md — code comments section
    author: human:christopher
---

# Observation

Prefer self-documenting code. Only comment a genuinely non-obvious **why** — a
subtle invariant, a workaround, a gotcha — and keep it to a single terse line.
No docblocks that paraphrase a signature. Storybook story descriptions: one line.

# Why it matters

This is the single highest-frequency style decision an agent makes. Getting it
wrong produces a diff that is technically correct and unpleasant to read.

# Scope caveat, carried from the source

Applies to code you write or edit. **Do not touch pre-existing comments authored
by others** — only trim comments that are part of your own change.

# Promotion note

Found in `CLAUDE.local.md`, which is git-ignored and therefore Chris's personal
standard rather than a zamp team rule. Strong meta candidate.
