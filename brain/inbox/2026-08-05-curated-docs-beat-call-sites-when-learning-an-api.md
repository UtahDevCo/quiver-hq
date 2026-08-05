---
type: Observation
title: Learn a component's API from its curated docs, not by grepping call sites
description: Storybook stories are written to demonstrate intent, while call sites accumulate; an older call site can have a convention exactly backward and copying it propagates the error.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [design-system, storybook, documentation, code-reuse]
status: draft
not:
  - term: "grepping for an existing usage of a component and copying the nearest one"
    why: "call sites are not curated — an older one can predate the convention or have it inverted, and copying it launders the mistake into new code"
    instead: "read the component's stories (or equivalent curated example), which exist specifically to demonstrate correct usage"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Storybook is the source of truth for design-system components'" }
  - { id: inverted-callsite, resource: "projects/zamp/apps/company/.../nps-survey.client.tsx:114", title: "call site nesting <FieldGroup><FieldSet> where canonical order is <FieldSet><FieldGroup>" }
---

# Observation

When reaching for a shared component, read its curated documentation — in this
codebase, its `*.stories.tsx` — rather than grepping for a call site to copy.

Stories are written to demonstrate intended usage. Call sites merely accumulate:
some predate the current convention, some were written against an older API, and
some are simply wrong in a way nobody noticed because they render acceptably.

# Why it matters

Copying a call site is how a convention inverts and then spreads. The concrete
case: `nps-survey.client.tsx:114` nests `<FieldGroup><FieldSet>`, while the
canonical order demonstrated in the Field/FieldSet stories is
`<FieldSet><FieldGroup>`. Both render. A developer who greps for `FieldGroup`,
finds that call site, and copies it produces new code that is wrong in the same
way — and now there are two precedents, which makes the third copy more likely.

This is a self-reinforcing failure: each copy strengthens the wrong pattern's
apparent authority. Curated examples don't have that property, because nobody
adds to them by accident.

The generalization beyond Storybook: when a codebase has an artifact whose
*purpose* is to show correct usage, that artifact outranks any number of
in-the-wild usages. Prefer it even when a call site is closer to hand.

# Evidence

`patterns.md` records this as a review finding and cites the inverted
`FieldGroup`/`FieldSet` nesting as the worked example.

Proposed `meta` because the principle is about documentation authority rather than
about Storybook or this design system. It would land in a fresh repo as
"read the curated example, not the nearest usage." Corroboration is currently
zamp-only; the Storybook-specific half is already partly reflected in
`projects/zamp/practices/story-per-component.md`.
