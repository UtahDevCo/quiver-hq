---
type: Practice Override
title: Typography and layout primitives are banned outright
overrides: /meta/practices/typography-and-layout-as-utilities.md
mode: extend
why: "zamp enforces the prohibition in .coderabbit.yaml and is migrating off the Rt* Radix Themes layout primitives. Other repos use a Typography component deliberately and are not out of compliance."
generated: { by: claude/opus-5, at: 2026-07-29T20:23:37Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "<Flex>, <Box>, <Grid>, <Container>, <Section> layout primitives"
    why: "reimplements CSS in props, renders a bare div, and loses semantic meaning"
    instead: "a semantic element (<section>, <header>, <ul>, <nav>) with layout utility classes"
  - term: "<Text>, <Heading>, <Code>, <Em>, <Strong> typography primitives"
    why: "a component wrapper around a font size, with worse semantics than the HTML tag"
    instead: "the correct HTML element plus a font utility"
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — typography, layout, and spacing rules
    author: human:christopher
    last_modified: 2026-07-25
  - id: tools-counterexample
    resource: projects/tools/packages/components/src/typography.tsx
    title: "tools — a deliberate Typography component with headline/title/subtitle variants"
    last_modified: 2026-07-29
---

# The extension

The meta practice recommends utilities on semantic HTML. **In zamp the component
alternatives are additionally forbidden**, enforced in review by
`.coderabbit.yaml`, and the `Rt*` Radix Themes layout primitives are being
actively removed — see
[deprecated-ui-surfaces](../decisions/deprecated-ui-surfaces.md).

# Why this is an override rather than a meta rule

Harvesting `tools` and `wiley` found the prohibition is **not** how Chris works
everywhere. `tools/packages/components/src/typography.tsx` is a deliberate
`Typography` component with `headline` / `title` / `subtitle` / `strong` variants —
a direct counterexample, and a considered one.

Chris's ruling: the no-`Text`/`Heading` rule is a zamp standard and unnecessary in
the other codebases. So a repo using a typography component is **not** deviating
from a practice; it simply doesn't have this extension.

What stayed universal: purpose-named font utilities, semantic elements over
anonymous divs, and `gap` over margins — the last confirmed independently in both
`tools` and `wiley`.
