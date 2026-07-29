---
type: Pattern
title: Make accessible usage the only thing that type-checks
description: A discriminated union requiring a label, placeholder, or aria-label turns an accessibility rule into a compile error.
tags: [accessibility, typescript, api-design, design-system]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: instance-of, target: /meta/practices/make-misuse-unrepresentable.md }
sources:
  - id: input-field
    resource: projects/zamp/utils/design-system/src/components/input-field.tsx
    title: InputField — discriminated union over label / placeholder / aria-label
    author: human:christopher
    last_modified: 2026-07-25
  - id: field
    resource: projects/zamp/utils/design-system/src/components/field.tsx
    title: Field, FieldLabel, FieldError, FieldDescription composition
---

# The pattern

```ts
export type InputFieldProps =
  | LabelInputFieldProps        // has label
  | PlaceholderInputFieldProps  // or placeholder
  | AriaLabelInputFieldProps    // or aria-label
```

An unlabeled input **fails to compile**. There is no valid prop combination that
produces one.

Supporting composition: `Field` + `FieldLabel` + `FieldDescription` +
`FieldError` + `FieldStatus`, so label, above/below description, error text, and
required/optional affordances each have exactly one home.

# Why

An unlabeled input is among the most common real accessibility defects, and it is
invisible in a screenshot. Auditing for it forever is strictly worse than making
it unrepresentable — see
[make misuse unrepresentable](../../../meta/practices/make-misuse-unrepresentable.md).

# Why this is project-layer

Held in `meta/patterns/` until 2026-07-29, then demoted on Chris's ruling: *don't
worry about it outside of zamp.*

Harvesting `tools` and `wiley` found neither implements the union. Both expose
`aria-label` as an **optional prop** — `tools` with a JSDoc hint ("recommended for
icon-only buttons"), `wiley` as `"aria-label"?: string`. That is precisely the
weaker alternative this pattern exists to replace, so scoring them as corroboration
would have been backwards. Only zamp's design system has the real thing.

Still a `Pattern`, so it is opt-in and its absence elsewhere is not a defect. The
section below is where it earns promotion back to meta if a second repo adopts it.

# Where else to apply it

Any component with a *conditionally required* prop is a candidate: a link needing
either `href` or `onClick`; an image needing `alt` unless explicitly
`aria-hidden`; a control needing either a visible label or an accessible name.
The union is more work than an optional prop and a runtime warning, and it is the
only version that cannot be ignored.
