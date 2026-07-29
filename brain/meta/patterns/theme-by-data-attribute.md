---
type: Pattern
title: One folder per theme, selected by a data attribute
description: A theme is a directory satisfying a token contract, scoped to [data-theme="name"], with dark mode as a nested selector.
tags: [design-system, theming, dark-mode, css]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: themes
    resource: projects/zamp/utils/design-system/src/themes/
    title: "zamp themes — zamp/ and indigo/ variants"
    author: human:christopher
    last_modified: 2026-07-25
---

# The pattern

```
src/themes/
  tw-shared-config.css     # typography utilities + theme-independent base
  <theme>/
    globals.css            # import orchestrator
    tw-config.css          # brand + intent scale bindings
    shadcn.css             # component semantics, light and dark
```

Scoping: `[data-theme="<name>"]` for light,
`[data-theme="<name>"].dark` / `[data-theme="<name>"] .dark` for dark.

Import order inside `globals.css`: external libs → theme palette → shared
utilities → component semantics. Later layers override earlier ones.

# The completeness contract

A theme is valid only if it defines **all** of:

1. the full brand scale (50–950),
2. the intent overrides (destructive, warning, success, chart-*),
3. every component semantic token,

in **both** light and dark. A partial theme fails as a missing CSS variable at
runtime — silently, and only on the screen that uses it — so the contract has to
be written down rather than inferred.

# Why a data attribute

Attribute selection beats class-based theming when themes are **exclusive**
rather than additive: you cannot accidentally apply two themes, and the cascade
does all the work with no runtime cost.

# The real reason to build a second theme

Not because you need it — because it is the cheapest possible audit of your token
layer. Every hardcoded value and every missing abstraction surfaces immediately.
A design system with one theme has never had its abstraction tested.
