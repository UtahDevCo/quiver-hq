---
type: Practice
title: Every design-system component ships a colocated story
description: A new component .tsx without a matching .stories.tsx is incomplete. Vendored primitives are exempt.
tags: [design-system, storybook, documentation]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:58Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /meta/practices/ds-vendor-wrap-export-layering.md }
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — design-system story requirement
    author: human:christopher
    last_modified: 2026-07-25
  - id: add-ds-component
    resource: projects/zamp/.claude/skills/add-ds-component/SKILL.md
    title: add-ds-component skill — Step 3, Stories
---

# The practice

Every new `.tsx` in `components/` has an associated story file. Exemption:
anything under the vendored `shadcn/` directory.

- `title` namespaced by category — `"Base/Button"`, `"Forms/InputField"`.
- Default story uses `args` + `argTypes` so props are interactively tweakable.
- One story per notable variant or state: disabled, error, sizes, colors.
- Prefer `args` over `render`; use `render` only when the story needs
  composition.
- **Minimal styling.** No extra wrapper divs or utility classes unless the story
  cannot render without them — the component's own styles should speak.
- Viewport stories when behavior changes at a breakpoint.
- Clean up generated `argTypes`: string-or-undefined props render as radio
  buttons, so force `control: "text"`.
- Share repeated `argTypes` via an exported constant rather than copying
  (zamp: `FIELD_STATUS_STORY_ARG_TYPES` in `field-status.tsx`).
- Story JSDoc becomes the rendered doc — add it only when the story name isn't
  self-explanatory.

# Why

The story is the design system's test suite and its documentation at once. It's
also what a deprecation migration guide points at, per
[deprecate without breaking consumers](../../../meta/practices/deprecate-without-breaking-consumers.md) —
which only works if stories are universal.

# Why this is project-layer, not meta

Storybook is a zamp-only tool. Chris confirmed this on 2026-07-29, so the
practice is scoped here rather than applied to every repo. Promote it to
`meta/` if a second project adopts Storybook.

The transferable half — *a component isn't done until there's a runnable example
of it* — is worth lifting even without Storybook. It has not been written as a
meta practice because no second repo has corroborated the shape it should take.
