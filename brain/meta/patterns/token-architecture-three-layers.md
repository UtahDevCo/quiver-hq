---
type: Pattern
title: Layer tokens as scale, then intent, then component semantics
description: A raw scale feeds named intents, which feed component-level semantics. Consumers only ever touch the top layer.
tags: [design-system, tokens, theming, css]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /projects/zamp/patterns/theme-by-data-attribute.md }
sources:
  - id: themes
    resource: projects/zamp/utils/design-system/src/themes/
    title: "zamp theme layer — tw-shared-config.css, per-theme tw-config.css and shadcn.css"
    author: human:christopher
    last_modified: 2026-07-25
---

# The pattern

Opt-in: reach for this when building a token system, not on every change.

1. **Scale** — an 11-step ramp per hue: `--color-brand-{50…950}`, likewise for
   `warning`, `success`.
2. **Intent** — a consistent quartet per meaning:
   `--color-{intent}-{accent,background,border,foreground}`.
3. **Component semantics** — `--background`, `--card`, `--popover`,
   `--primary`, `--muted`, `--ring`, `--sidebar-*`, `--chart-{1..5}`.

Consumers reference layer 3 (and the intent tokens of layer 2). Nobody outside
the theme layer touches layer 1.

# The load-bearing part

**The repeating quartet.** Because every intent exposes the same four roles, a
component can be written once against `{intent}-background` /
`{intent}-foreground` and work for all of them. That is why the component layer
stays small — the intents are swappable by construction.

If you take one thing from this pattern, take the uniform role set, not the
three-layer count.

# Supporting decisions worth copying

- **`oklch()`** for color, so lightness is perceptually uniform across
  light/dark rather than merely numerically equal.
- **Derived radius scale**: one `--radius` base with `--radius-sm` … `--radius-4xl`
  produced by `calc()` offsets. Changing the base rescales the system coherently.
- **Typography composed from abstracted tokens** (`--font-sans`,
  `--font-weight-*`) rather than literal values.

# Layering discipline

Global resets → base theme tokens → semantic utilities → theme color bindings →
component-local CSS. Later layers override earlier ones, and the import order is
what makes that true.
