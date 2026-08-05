---
type: Practice
title: Flex column children stretch by default — self-start is the opt-out, not parent items-start
description: align-items defaults to stretch, so w-full on a flex-column child is a no-op; opting out via the parent un-stretches every sibling and lands the regression somewhere else.
tags: [css, flexbox, tailwind, layout]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "w-full on a child of a flex flex-col container"
    why: "align-items: stretch already makes the child fill the cross axis; the class does nothing"
    instead: "drop it"
  - term: "adding items-start to the parent to stop one child from stretching"
    why: "it un-stretches every sibling, so separators and full-width containers silently shrink to content width"
    instead: "put self-start (or self-end / self-center) on the one child that should opt out"
  - term: "wrapping a child in a div to break the stretch chain"
    why: "adds a layout node whose only job is defeating a default, and the wrapper stretches in its place"
    instead: "self-start on the child itself"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Flex column children stretch by default'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

In a flex column, every child gets `align-items: stretch` unless told otherwise.
Three consequences:

- `w-full` on a flex-column child is almost always redundant. Drop it.
- To opt **one** child out, put `self-start` (or `self-end`, `self-center`) on *that
  child*. Not `items-start` on the parent, and not a wrapper div.
- Parent `items-center` is redundant when every child already centres its own
  contents — via `text-center`, an internal `flex flex-col items-center`, or a
  full-width container primitive. It also prevents children from stretching when
  they'd otherwise want to. Reach for parent `items-*` only when children have
  intrinsic widths that need shared alignment.

```tsx
// ❌ Wrapper div purely to stop the Button stretching
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

# Why parent items-start is the expensive mistake

Because it works. The button stops stretching, the author moves on, and the
regression lands on the *siblings* — a separator that no longer spans its container,
a full-width row that collapsed to its content.

Those read later as unrelated styling bugs, so the fix gets applied at the sibling
(often another `w-full`) rather than at the cause. One `items-start` can seed several
compensating classes elsewhere in the same component. `self-start` is the same length
and scopes the change to the element that asked for it.

# Scope

A fact about the CSS flexbox specification, expressed here in Tailwind's utility
names. The behavior is the same in any styling system; only the class names change.
