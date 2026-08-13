---
type: Practice Override
title: There is no wrapper layer here for ds-wrapper-passthrough to govern
overrides: /meta/practices/ds-wrapper-passthrough.md
mode: suspend
why: "The practice specifies what goes in the middle layer of a three-layer design system, and trikin has no middle layer. Suspended rather than replaced, so the gap expires on its own if a wrapper layer is ever introduced."
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2026-11-11
not:
  - term: "writing ComponentProps-typed passthroughs around each components/ui primitive to satisfy the practice"
    why: "it builds the layer the practice governs purely so the practice has something to govern, and doubles the cost of every shadcn update"
    instead: "leave the primitives as the editable surface, and revisit this suspension if a genuine wrapper layer appears"
sources:
  - id: ui-dir
    resource: projects/trikin/web/src/components/ui/
    title: "24 primitives, imported directly by feature code, no barrel and no wrapper layer"
  - id: components-json
    resource: projects/trikin/web/components.json
    title: "aliases.ui = @/components/ui — feature code imports the primitive path directly"
---

# The suspension

[Wrapper components are explicit passthroughs](../../../meta/practices/ds-wrapper-passthrough.md)
tells you how to type and spread a wrapper. trikin has no wrapper layer, because the
shadcn primitive is the editable surface here. See
[shadcn primitives are the wrapper layer](shadcn-primitives-are-the-wrapper-layer.md)
for the underlying fact; these two overrides record one situation against two meta
practices.

Parts of the practice still apply wherever a component does wrap another: derive
prop types with `ComponentProps` rather than hand-writing them, spread the
remainder, and skip manual ref forwarding under React 19.

# What would end the suspension

Either a wrapper layer appears in trikin, in which case this becomes compliance, or
the review at `stale_after` confirms shadcn-in-place is the settled shape and this
converts to `mode: replace` with the applicable fragments spelled out.

# Evidence

There is no `components/ui/index.ts`, and feature code imports
`@/components/ui/button` directly.
