---
type: Practice
title: Read what a primitive already provides before overriding it
description: Defaults come from the primitive, the parent layout, the HTML element, and JSX. Re-stating one is a pinned copy of a value you don't own, and it drifts silently.
tags: [design-system, react, css, html, accessibility]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "disabled={isPending} alongside loading={isPending}"
    why: "the loading prop already disables the control; the duplicate can drift out of sync"
    instead: "set loading and let it own the disabled state"
  - term: "wrapping children in flex flex-col gap-4 inside a parent that already declares flex flex-col gap-4"
    why: "duplicates the parent's layout contract and breaks silently if the parent changes"
    instead: "return a Fragment and let the parent's layout apply"
  - term: "adding aria-label to a button that already has visible text"
    why: "the visible text is already the accessible name; a conflicting aria-label overrides it"
    instead: "rely on the visible text; reserve aria-label for icon-only controls"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Read defaults before overriding'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

Before adding a class, prop, attribute, or `aria-*` to a component, read what it and
its underlying element already give you. Defaults arrive from four places, and each
is a routine source of redundant code:

- **The design-system primitive** — a card sets its own foreground colour; a row
  primitive at default size sets its own gap and padding; a sheet caps its own max
  width; an icon has a default size.
- **The parent layout** — if the wrapper is `flex flex-col gap-4`, children don't
  need an identical wrapper of their own.
- **The HTML element** — anchors get pointer cursors; `<button>` is
  keyboard-focusable and clickable with no JavaScript boundary; a button's visible
  text is already its accessible name.
- **React/JSX** — boolean props default to `true`, so `open={true}` is just `open`.

# Why the drift matters more than the noise

The immediate cost is legibility: when most props on a component are no-ops, the two
that are real overrides are hard to find, in the editor and in review.

The durable cost is drift. A re-stated default is a *copy* of a value the primitive
owns. When the primitive changes — new spacing scale, new max width — every consumer
that pinned the old value keeps the old behavior while appearing to inherit the new
one. The resulting bug looks like the primitive failing to update, which sends the
investigation to the wrong file.

# Boundary

This is about *redundant* overrides, not about deference. Overriding a primitive
deliberately is fine and often necessary; the practice asks only that you know what
you are overriding, so the diff shows intent rather than noise.

Related: [ds-wrapper-passthrough](ds-wrapper-passthrough.md) for the authoring side —
a wrapper derives its prop types from the primitive rather than re-declaring them,
which is the same principle one layer down.
