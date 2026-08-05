---
type: Practice
title: Learn a shared component's API from its curated examples, not from the nearest call site
description: Stories and docs are written to demonstrate intent; call sites merely accumulate. Copying a call site can launder an inverted convention into new code, and each copy strengthens the wrong precedent.
tags: [design-system, storybook, documentation, code-reuse, judgment]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
relations:
  - { kind: depends-on, target: /meta/practices/follow-local-conventions.md }
not:
  - term: "grepping for an existing usage of a shared component and copying the nearest one"
    why: "call sites are not curated — one can predate the convention or have it inverted, and copying it reproduces the mistake with fresh authority"
    instead: "read the component's stories or equivalent curated example, which exist specifically to demonstrate correct usage"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Storybook is the source of truth for design-system components'"
    author: human:christopher
    last_modified: 2026-08-05
  - id: inverted-callsite
    resource: projects/zamp/apps/company/.../nps-survey.client.tsx
    title: "call site nesting <FieldGroup><FieldSet> where the canonical order is <FieldSet><FieldGroup>"
    last_modified: 2026-08-05
---

# The practice

When reaching for a shared component, read its curated example — in a design system,
its stories — rather than grepping for a call site to copy.

Curated examples are written to demonstrate intended usage. Call sites merely
accumulate: some predate the current convention, some were written against an older
API, and some are simply wrong in a way nobody noticed because they render
acceptably.

# Why copying spreads the error

A wrong call site is self-reinforcing. The concrete case: one file nests
`<FieldGroup><FieldSet>` where the canonical order demonstrated in the stories is
`<FieldSet><FieldGroup>`. Both render. Someone who greps for `FieldGroup`, finds that
file, and copies it now produces a second wrong usage — and two precedents make the
third copy more likely than the first was.

Curated examples don't have that property, because nobody adds to them by accident.

# Boundary — this does not contradict follow-local-conventions

[follow-local-conventions](follow-local-conventions.md) says to read two or three
siblings and match them. That practice governs **internal implementation idiom**, and
it explicitly excludes cross-cutting visible surface, where uniformity wins.

A shared component's API is that visible surface. So the two compose:

- **Internal idiom** (error-return style, module layout) → match the neighbours.
- **Shared component usage, tokens, published exports** → match the curated
  reference, even when the neighbours disagree with it.

When a sibling call site conflicts with the component's own documented usage, the
documentation wins and the sibling is a latent bug. Reading only the neighbours is
exactly how the inverted nesting above survived.
