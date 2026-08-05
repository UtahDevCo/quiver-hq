---
type: Observation
title: Flex column children stretch by default, so w-full is redundant and items-start is the wrong opt-out
description: align-items defaults to stretch, so a flex-column child already fills the cross axis; opt a single child out with self-start rather than un-stretching every sibling with parent items-start.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [css, flexbox, tailwind, layout]
status: draft
not:
  - term: "w-full on a child of a flex flex-col container"
    why: "align-items: stretch already makes the child fill the cross axis; the class is a no-op"
    instead: "drop it"
  - term: "adding items-start to the parent to stop one child from stretching"
    why: "it un-stretches every sibling, so Separators and full-width containers silently shrink to content width"
    instead: "put self-start (or self-end / self-center) on the one child that should opt out"
  - term: "wrapping a child in a plain div to break the stretch chain"
    why: "adds a layout node that exists only to defeat a default, and the wrapper itself then stretches"
    instead: "self-start on the child itself"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Flex column children stretch by default'" }
---

# Observation

In a flex column, every child gets `align-items: stretch` unless told otherwise.
Three consequences follow:

- `w-full` on a flex-column child is almost always redundant — drop it.
- To opt **one** child out of stretching, put `self-start` (or `self-end`,
  `self-center`) on *that child*. Don't add `items-start` to the parent, and don't
  wrap the child in a div to break the chain.
- Parent `items-center` is redundant when every child already centers its own
  contents — via `text-center`, an internal `flex flex-col items-center`, or a
  full-width container primitive. Worse than redundant: it prevents children from
  stretching when they'd otherwise want to. Reach for parent `items-*` only when
  children have intrinsic widths needing shared alignment.

```tsx
// ❌ Wrapper div purely to prevent the Button from stretching
<ContentWrapper>
  <div><Button size="sm" /></div>
  <Separator />
  {children}
</ContentWrapper>

// ✅ Opt the one child out; Separator and children still stretch
<ContentWrapper>
  <Button size="sm" className="self-start" />
  <Separator />
  {children}
</ContentWrapper>
```

# Why it matters

The `items-start` mistake is the costly one, because it works. The button stops
stretching, the developer moves on, and the regression lands on the *siblings* —
a `Separator` that no longer spans the container, a full-width row primitive that
collapsed to its content. Those read as unrelated styling bugs later, and the fix
gets applied at the sibling (another `w-full`) rather than at the cause.

`self-start` is the same number of characters and scopes the change to the one
element that wanted it.

# Evidence

Recorded in `patterns.md` with the wrapper-div and parent-`items-center` cases
worked through in JSX. Proposed as `meta`: this is a fact about the CSS flexbox
specification, expressed in Tailwind's utility names, with nothing repo-specific
about it.
