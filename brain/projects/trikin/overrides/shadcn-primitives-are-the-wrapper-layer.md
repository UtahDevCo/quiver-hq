---
type: Practice Override
title: In a shadcn repo the generated primitives are the wrapper layer
overrides: /meta/practices/ds-vendor-wrap-export-layering.md
mode: replace
why: "shadcn copies the primitive into the repo so that you can edit it. There is no upstream package to drift from and no wrapper layer to hold opinions, because the opinions go in the primitive."
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "adding a components/wrapped/ layer that re-types and re-exports each components/ui primitive"
    why: "duplicates the surface shadcn already gives you ownership of, and every upstream update then has to be applied twice"
    instead: "edit the primitive in place; that is shadcn's model. Record a Practice Override rather than building the missing layer."
sources:
  - id: ui-dir
    resource: projects/trikin/web/src/components/ui/
    title: "24 primitives, imported directly by feature code, no barrel and no wrapper layer"
  - id: components-json
    resource: projects/trikin/web/components.json
    title: "aliases.ui = @/components/ui — feature code imports the primitive path directly"
---

# The replacement

[The meta practice](../../../meta/practices/ds-vendor-wrap-export-layering.md)
describes three layers: generated primitives treated as untouched third-party code, a
thin wrapper layer holding your opinions, and a curated barrel. In trikin the layering
is shadcn's: 24 files in `components/ui/`, edited in place, imported directly by
feature code, with no barrel.

The rule that survives is the provenance comment and the discipline of keeping a
primitive close enough to upstream that a future `shadcn add` diff is readable. The
rule that does not survive is "never edit a generated primitive", because editing it
is the mechanism the tool provides.

# Why this is an override rather than compliance

An agent following the meta practice literally will build a redundant wrapper layer,
doubling the cost of every future shadcn update, or refuse to edit a primitive that
shadcn intends it to edit and work around it instead.

The practice came from zamp, where the generated-versus-wrapper split is real and
load-bearing. This is the boundary of its applicability.

# Evidence

`components.json` aliases `ui` to `@/components/ui`, and feature code imports
`@/components/ui/button` directly rather than through any curated surface. There is
no `components/ui/index.ts`.

The passthrough practice that depends on the wrapper layer is suspended separately:
[no wrapper layer for ds-wrapper-passthrough to govern](shadcn-has-no-wrapper-layer-to-govern.md).
