---
type: Practice
title: Reference semantic tokens, never raw color values
description: Use semantic and intent tokens. Hardcoded values and raw palette steps both break theming and dark mode.
tags: [design-system, tokens, dark-mode, theming]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /meta/patterns/token-architecture-three-layers.md }
not:
  - term: "bg-blue-500, text-red-200, or any raw palette step"
    why: "a palette step is a commitment to a lightness, which is exactly what the theme must control; not dark-mode safe"
    instead: "a semantic token (primary, muted, destructive) or an intent token (brand-*, warning-*, success-*)"
  - term: "a hardcoded hex or oklch value, including inside a CSS variable"
    why: "invisible to theming and to any future palette change"
    instead: "declare it as a token in the theme layer, then reference the token"
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — color usage rules
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

Color usage is minimal and limited to dark-mode-safe tokens:

- **Semantic set** — `background`, `foreground`, `primary`, `secondary`,
  `muted`, `accent`, `destructive`, `border`, `input`, `ring`.
- **Intent tokens** — `brand-*`, `warning-*`, `success-*`.

This applies to CSS custom properties too, not just utility classes.

# Why

Dark mode is the reason this holds firmly. A raw palette step fixes a lightness;
a theme's whole job is to choose lightness. The failure is invisible in
development and obvious to users.

# The escape hatch, and why it matters

A primitive's own CSS custom properties **may** be used via inline `style` where
design-system classes are insufficient — **with an inline comment explaining
why.** Token-driven inline styles are permitted on the same terms.

The comment requirement is what keeps the rule honest. Without a sanctioned
exception, unavoidable cases get solved silently; with one, they stay reviewable.
This is the pattern to copy whenever a rule needs an exception at all: make the
exception explicit and cheap rather than absent.

# Related

[Delete the tokens you don't want used](constrain-the-palette-at-config.md) makes
the grey half of this rule structurally impossible to violate.
