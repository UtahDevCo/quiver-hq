---
type: Observation
title: A stock shadcn/ui repo cannot satisfy constrain-the-palette-at-config
description: shadcn's generated primitives reference Tailwind's full palette, so deleting redundant scales breaks them — the meta practice needs a suspend override, not compliance.
kind: practice
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [design-system, tailwind, shadcn, override, practice-override]
status: draft
not:
  - term: "deleting Tailwind's grey scales down to one in a shadcn repo"
    why: "the generated primitives in components/ui reference palette steps directly; removing scales breaks them at build or silently changes rendering"
    instead: "record a dated `mode: suspend` Practice Override so the gap is visible and expires, rather than either complying or ignoring the practice"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: components-json, resource: projects/trikin/web/components.json, title: "shadcn config — style new-york, baseColor neutral, cssVariables true, no prefix" }
  - { id: globals, resource: projects/trikin/web/src/app/globals.css, title: "@theme inline block — semantic tokens over Tailwind 4's stock palette" }
  - { id: ui-dir, resource: projects/trikin/web/src/components/ui/, title: "24 generated primitives consumed directly, no wrapper layer" }
---

# Observation

`constrain-the-palette-at-config` tells an agent to delete redundant token scales
so misuse cannot compile. In a stock shadcn/ui repo that instruction is actively
harmful: the generated primitives under `components/ui/` reference Tailwind's
palette, and the whole point of shadcn is that those files are yours to keep in
sync with upstream.

trikin is exactly this shape — `components.json` with `baseColor: neutral`,
`cssVariables: true`, 24 primitives, Tailwind 4's full palette present.

The resolution is a `Practice Override` with `mode: suspend` and a dated
`stale_after`, targeting `/meta/practices/constrain-the-palette-at-config.md`.
Suspend rather than replace, because the practice is right and the repo is simply
not able to satisfy it yet — and `brain/conventions.md` makes a suspension expire
on its own instead of quietly becoming the new normal.

# Why it matters

The meta index is loaded into every session and the practice is default-on, so an
agent opening this repo has a standing instruction to go delete palette scales.
That is a change with no ticket, no request, and a real chance of breaking
rendering — and it violates "the brain describes; it does not retrofit" while
believing it is complying.

Checked and *passing* in the same repo, worth recording so a future audit does not
re-litigate them: `semantic-tokens-only` holds, because shadcn is semantically
tokenised (`--color-primary`, `--color-muted`, `--color-destructive`);
`typography-and-layout-as-utilities` holds, because the repo puts Tailwind
utilities on semantic HTML and has no `Text`/`Heading`/`Box` components. The
`Column`/`Main` components in `components/layout/` are fine — banning layout
primitives outright is the zamp-only half of that practice.

# Evidence

`web/components.json`:

```json
{ "style": "new-york", "tailwind": { "baseColor": "neutral", "cssVariables": true, "prefix": "" } }
```

`web/src/app/globals.css` maps semantic names onto values in an `@theme inline`
block. Raw hex appears there (`--color-secondary: #e06c5e`), which is correct —
config is exactly where raw values belong under `semantic-tokens-only`.
