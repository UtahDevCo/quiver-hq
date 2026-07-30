---
type: Observation
title: In a shadcn repo the generated primitives *are* the wrapper layer
description: ds-vendor-wrap-export-layering and ds-wrapper-passthrough assume a vendor layer you don't edit plus your own wrapper; shadcn collapses both into one editable copy, so both practices need overrides.
kind: practice
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [design-system, shadcn, override, practice-override]
status: draft
not:
  - term: "adding a components/wrapped/ layer that re-types and re-exports each components/ui primitive"
    why: "duplicates the surface shadcn already gives you ownership of, and every upstream update then has to be applied twice"
    instead: "edit the primitive in place; that is shadcn's model. Record a Practice Override rather than building the missing layer."
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: ui-dir, resource: projects/trikin/web/src/components/ui/, title: "24 primitives, imported directly by feature code, no barrel and no wrapper layer" }
  - { id: components-json, resource: projects/trikin/web/components.json, title: "aliases.ui = @/components/ui — feature code imports the primitive path directly" }
---

# Observation

Two meta practices describe a three-layer design system: generated primitives
treated as untouched third-party code, a thin wrapper layer holding your opinions,
and a curated barrel. `ds-wrapper-passthrough` then says to type wrappers off the
primitive with `ComponentProps` and never bare re-export.

shadcn/ui does not work that way. The primitive is copied into your repo
*so that you can edit it*; there is no upstream package to drift from and no
wrapper layer to hold opinions, because the opinions go in the primitive. trikin
has 24 files in `components/ui/`, imported directly, with no barrel.

So: `mode: replace` against `/meta/practices/ds-vendor-wrap-export-layering.md`
(shadcn's layering is the layering here), and `mode: suspend` against
`/meta/practices/ds-wrapper-passthrough.md` (there is no wrapper layer for it to
govern). Two override files, one underlying fact.

# Why it matters

An agent following the meta practices literally will either build a redundant
wrapper layer — doubling the cost of every future shadcn update — or refuse to
edit a primitive that shadcn intends it to edit, and work around it instead.

Both practices came from zamp, where the generated-vs-wrapper split is real and
load-bearing. This is the boundary of their applicability, and finding it is worth
more than the practices losing a little scope.

# Evidence

`components.json` aliases `ui` to `@/components/ui`, and feature code imports
`@/components/ui/button` directly rather than through any curated surface. There is
no `components/ui/index.ts`.
