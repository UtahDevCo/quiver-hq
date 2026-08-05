---
type: Observation
title: Read what a primitive already provides before adding a class, prop, or aria attribute
description: Re-applying a default the component, parent layout, or HTML element already gives you is dead weight that hides real overrides and drifts as the primitive evolves.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [design-system, css, react, html, accessibility, code-review]
status: draft
not:
  - term: "disabled={isPending} alongside loading={isPending}"
    why: "the loading prop already disables the control; the second prop is noise that can drift out of sync"
    instead: "set loading and let it own the disabled state"
  - term: "wrapping children in flex flex-col gap-4 inside a parent that already declares flex flex-col gap-4"
    why: "duplicates the parent's layout contract; the wrapper does nothing and breaks silently if the parent changes"
    instead: "return a Fragment and let the parent's layout apply"
  - term: "adding aria-label to a button that already has visible text"
    why: "the visible text IS the accessible name; a conflicting aria-label overrides it and can make the control unannounceable as labelled"
    instead: "rely on the visible text; add aria-label only for icon-only controls"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Read defaults before overriding'" }
---

# Observation

Before adding a class, prop, attribute, or `aria-*` to a component, read what it
and its underlying element already provide. Defaults arrive from four places, and
each is a common source of redundant code:

- **The design-system primitive** — a card sets its own foreground color; a row
  primitive at default size sets its own gap and padding; a sheet caps its own
  max width; an icon has a default size.
- **The parent layout** — if the wrapper is `flex flex-col gap-4`, children don't
  need their own identical wrapper.
- **The HTML element** — anchors get pointer cursors; `<button>` is
  keyboard-focusable and clickable without any JS boundary; a button's visible
  text is already its accessible name.
- **React/JSX** — boolean props default to `true`, so `open={true}` is just `open`.

# Why it matters

Two costs, and the second is the expensive one.

The immediate cost is noise: a wall of props where most are no-ops makes the two
that *are* real overrides hard to find, in the code and in review.

The durable cost is drift. A re-stated default is a copy of a value the primitive
owns. When the primitive changes its default — new spacing scale, new max width —
every consumer that pinned the old value silently keeps the old behavior while
appearing to inherit. The bug looks like the primitive failing to update.

# Evidence

Recorded in `patterns.md` as a recurring PR-review finding, with concrete instances
across all four default sources: `<Icon size={16}>` (16 is the default),
`open={true}`, `disabled={isPending}` next to `loading`, and a table component that
should return a Fragment because `FailureDetailSheet`'s body already supplies
`flex flex-1 flex-col gap-4`.

The related CSS-specific case — flex-column children stretching by default, so
`w-full` is redundant — is filed separately, since it is a fact about CSS rather
than a review practice.
