---
type: Pattern
title: The three-export stacking drawer recurs in trikin and wiley by divergent evolution
description: Both repos export Drawer / DrawerViewport / closeHighestDrawer over a reference-counted scroll lock, and the APIs diverged, so the shape corroborates while wiley's accessibility work stays wiley-only.
tags: [ui, drawer, corroboration, portal, framer-motion]
generated: { by: claude/opus-5, at: 2026-07-30T14:56:42Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: instance-of, target: /meta/workflows/corroboration-requires-independent-sources.md }
not:
  - term: "promoting wiley's drawer implementation as the shared pattern"
    why: "it would tell an agent that a drawer without push mode and focus trapping is incomplete, which is not true of trikin's and would license rewriting working code"
    instead: "promote the shape (portal, viewport owning the stack, module-level closeHighestDrawer, reference-counted scroll lock) and leave the modes, the position prop, and the tab trap in the wiley layer"
sources:
  - id: trikin-drawer
    resource: "projects/trikin/web/src/components/drawer.tsx (190 lines)"
    title: "Drawer, closeHighestDrawer, DrawerViewport; hash-driven open state; CircleX close"
  - id: wiley-drawer
    resource: "projects/wiley/web/components/shared/drawer.tsx (380 lines)"
    title: "same three exports plus DrawerMode overlay/push, position left/right, FOCUSABLE_SELECTOR tab trap"
  - id: wiley-concept
    resource: brain/projects/wiley/patterns/drawer.md
    title: "the existing wiley pattern concept this was checked against"
---

# The pattern

[wiley's drawer concept](../../wiley/patterns/drawer.md) records wiley's version.
trikin has a drawer exporting **the same three symbols**, `Drawer`,
`DrawerViewport`, and `closeHighestDrawer`, over the same `useFreezeScroll`
reference-counted scroll lock, the same `useDebouncedValue`, the same framer-motion
animation, and the same `useId`-keyed stack.

That looks like corroboration, and
[corroboration requires independent sources](../../../meta/workflows/corroboration-requires-independent-sources.md)
requires diffing before counting it. I diffed. **Verdict: common ancestry,
independently evolved, so it is one source seen twice in part and two sources in
part.**

Of 159 unique non-blank lines in trikin's file, 68 also appear in wiley's (43%), and
most of that overlap is imports and closing braces. The APIs have diverged:

| | trikin (190 lines) | wiley (380 lines) |
|---|---|---|
| open state | `hash?: string` — URL-hash driven | `id` + `useDrawerState` |
| modes | overlay only | `DrawerMode` overlay **and** push, `onModeChange` |
| position | right only | `left` \| `right` |
| focus | none | `FOCUSABLE_SELECTOR` tab trap |
| escape hatch | `drawerRef` prop | `PanelRight` mode toggle button |

trikin is the simpler, earlier variant; wiley added modes, positioning, and
accessibility on top.

# Why it matters

The distinction changes what promotes. The **shape** is corroborated and is a real
recurring solution: a portal-rendered drawer, a viewport component owning the stack,
a module-level `closeHighestDrawer()` for stack-aware Escape, and a
reference-counted scroll lock so N open drawers do not fight over `overflow`. Two
repos reached it independently, so it is worth having as a meta `Pattern`.

wiley's specific work stays in the wiley layer. The existing wiley concept also
flags two real defects in that implementation: `closeHighestDrawer()` simulates a
DOM click and depends on document order matching stack order, and there are two
independent stack accountants in the same component family. Those are reasons to be
careful about promoting the implementation, and no reason at all not to promote the
shape.

# Evidence

Both files import `useFreezeScroll` from a repo-local hook of the same name and both
derive their stack key from `useId()`. That shared, slightly unusual pair is what
makes common ancestry the right reading rather than convergent design.

# Not yet checked

`components/composed-table.tsx` (152 lines) in trikin deserves the same diff against
wiley's data-table pattern before that one is counted as corroboration. I have not
diffed it.
