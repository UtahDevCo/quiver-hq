---
type: Practice
title: Make misuse unrepresentable, not merely reviewable
description: When you have a house choice among interchangeable options, delete the alternatives from the toolchain instead of documenting a preference.
tags: [api-design, tooling, enforcement, review]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: generalizes, target: /meta/practices/constrain-the-palette-at-config.md }
  - { kind: generalizes, target: /meta/patterns/accessibility-enforced-by-types.md }
not:
  - term: "a review rule saying 'don't use X'"
    why: "requires a human to notice every time, forever, and fails silently when they don't"
    instead: "remove X from the config, types, or exports so using it doesn't work"
sources:
  - id: palette
    resource: /meta/practices/constrain-the-palette-at-config.md
    title: Deleting unused color scales (zamp)
    author: human:christopher
  - id: a11y-types
    resource: /meta/patterns/accessibility-enforced-by-types.md
    title: Discriminated union forcing an accessible label (zamp)
    author: human:christopher
---

# The practice

When the team has settled on one of several interchangeable options, **remove the
alternatives from the toolchain** rather than writing down a preference.

A documented preference costs review attention on every change, forever, and
degrades quietly the moment attention lapses. A deleted alternative costs one
edit and then nothing.

# Where to look for the opportunity

| Surface | The move |
|---|---|
| Design tokens / Tailwind config | Delete redundant scales so they don't compile. |
| Component prop types | Make the unsafe combination fail to type-check. |
| Barrel exports | Omit the deprecated surface so it can't be imported. |
| `tsconfig` | Turn the convention into a compiler error. |
| Lint config | Prefer an error over a documented style note. |
| Dependency allowlist | Remove the library rather than discouraging it. |

# Two worked instances

Both come from zamp's design system:

- **Palette** — Tailwind ships five near-identical gray scales. The config keeps
  `neutral` and deletes slate, gray, zinc, and stone. `bg-slate-500` compiles to
  nothing, so the review rule "use semantic tokens" never has to be enforced for
  grays. See [constrain the palette](constrain-the-palette-at-config.md).
- **Accessibility** — a field's props are a discriminated union over
  `label` | `placeholder` | `aria-label`, so an unlabeled input is a type error
  rather than an audit finding. See
  [accessibility enforced by types](../patterns/accessibility-enforced-by-types.md).

# When this does not apply

Only when the options really are interchangeable *for us*. Deleting a genuinely
useful escape hatch converts a small annoyance into a fork of the toolchain.

The tell that you've gone too far: people start adding `eslint-disable`, casting
to `any`, or reaching for inline styles. That means the removed option was load
bearing — restore it and document the preference instead.

Prefer a **narrow, comment-justified escape hatch** over no escape hatch. See
[semantic tokens only](semantic-tokens-only.md), which permits a primitive's own
custom properties via inline `style` *with an explanatory comment* — an exception
that stays reviewable.

# Provenance note

This concept is **synthesis, not harvest**: it was inferred from the two
instances above rather than found stated in any repo. Promoted on Chris's
explicit approval, 2026-07-29.
