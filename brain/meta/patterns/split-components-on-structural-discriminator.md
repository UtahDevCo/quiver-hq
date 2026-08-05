---
type: Pattern
title: Split a component into siblings when its prop union discriminates on whether data exists
description: A "do we have X yet?" union makes every render path re-branch; two sibling components with flat props move the decision to the call site once. Shape-differing arms justify the split; value-differing ones don't.
tags: [react, components, typescript, discriminated-unions, api-design]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "one component with a prop union like { status: 'pending' } | { status: 'resolved', data: T }"
    why: "the variant check reappears in every branch of the render, and the prop type describes two unrelated states at once"
    instead: "two sibling components with flat prop types, chosen at the JSX level"
  - term: "applying this split to every discriminated union you meet"
    why: "arms that differ only in a value share the same shape, so splitting duplicates the shell and produces component sprawl"
    instead: "split when the arms differ in SHAPE (a field exists or doesn't); keep runtime branching when they differ only in VALUE"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Split polymorphic components when the discriminator is structural'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The pattern

When a component's prop union discriminates on "do we have data X yet?" — pending vs
resolved, loading vs loaded — prefer two sibling components with flat prop types over
one polymorphic component.

The runtime decision moves to JSX-level component choice (`<PendingFoo />` vs
`<ResolvedFoo data={...} />`), removing "which variant am I in?" from every render path
inside the component. Each component's props stay a handful of flat fields.

Sub-discriminators *within* a variant stay as plain runtime branching — pass vs fail
inside the resolved case, branching on `count === 0`.

# When it applies — shape, not value

This is the part that decides whether the pattern helps or hurts, and it is why this is
a Pattern (opt-in) rather than a Practice.

A **structural** discriminator ("does this field exist?") makes the arms describe
genuinely different shapes. Every access to the data needs a guard, and the props type
documents two components pretending to be one. Splitting removes the guard entirely:
`ResolvedFoo` takes `data: T`, non-optional, and never checks.

A **value** discriminator ("is the count zero?") operates on data that is uniformly
present. Splitting there duplicates the shared shell for nothing.

The test: do the arms differ in *shape* or only in *value*?

# Do not retrofit

Per [conventions](../../conventions.md), a Pattern is available when the problem
arises and is never retrofitted into working code unprompted. Applied
indiscriminately this one produces exactly the component sprawl it's meant to avoid.
