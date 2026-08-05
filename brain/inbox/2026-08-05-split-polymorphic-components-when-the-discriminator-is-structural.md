---
type: Observation
title: Split a component into siblings when its prop union discriminates on whether data exists yet
description: A "do we have X yet?" discriminated union forces every render path inside the component to re-branch; two sibling components with flat props move the decision to the JSX call site once.
kind: pattern
proposed_layer: meta
observed_in: zamp
tags: [react, components, typescript, discriminated-unions, api-design]
status: draft
not:
  - term: "one component with a discriminated union prop like { status: 'pending' } | { status: 'resolved', data: T }"
    why: "the variant check reappears in every branch of the render, and the prop type has to describe two unrelated states at once"
    instead: "two sibling components with flat prop types, chosen at the JSX level: <PendingFoo /> vs <ResolvedFoo data={...} />"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Split polymorphic components when the discriminator is structural'" }
  - { id: reference, resource: "projects/zamp/apps/company/.../import-check-row.tsx", title: "PendingImportCheckRow / ResolvedImportCheckRow in the AI CSV import flow" }
---

# Observation

When a component's prop union discriminates on "do we have data X yet?" — pending vs
resolved, loading vs loaded — prefer two sibling components with flat prop types over
one polymorphic component with a discriminated union.

The runtime decision moves to JSX-level component choice (`<PendingFoo />` vs
`<ResolvedFoo />`), which removes "which variant am I in?" from every render path
inside the component. Each component's props stay a handful of flat fields.

Sub-discriminators *within* a variant can stay as plain runtime branching — e.g.
pass vs fail inside the resolved case, branching on `count === 0`. Those are
different: they're decisions about the same data, not about whether the data exists.

# Why it matters

The distinction worth recording is *which* discriminators justify a split. Not all
of them do — that's why this is a `pattern` (opt-in) and not a `practice`.

A **structural** discriminator ("does this field exist?") makes the union's two arms
describe genuinely different shapes, so every access to the data has to be guarded
and the props type documents two components pretending to be one. Splitting removes
the guard entirely: `ResolvedFoo` receives `data: T`, non-optional, and never checks.

A **value** discriminator ("is the count zero?") operates on data that's uniformly
present. Splitting there just duplicates the shared shell.

Applied indiscriminately this pattern produces component sprawl, which is exactly
the failure mode `conventions.md` warns about for patterns treated as practices.
The test is whether the arms differ in *shape* or only in *value*.

# Evidence

`patterns.md` cites `PendingImportCheckRow` / `ResolvedImportCheckRow` in zamp's AI
CSV import flow as the reference, and explicitly notes that the pass/fail
sub-discriminator stays inside `Resolved` as runtime branching on `count === 0` —
which is what makes the shape-vs-value line concrete.

Proposed `meta` as a `Pattern`: available when the problem appears, not something to
retrofit into working components.
