---
type: Practice
title: Layer a design system as vendored primitives, wrappers, and a barrel
description: When using a component generator — treat generated primitives as third-party, put your opinions in a thin wrapper layer, and curate the public surface.
tags: [design-system, architecture, dependencies]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /meta/practices/ds-wrapper-passthrough.md }
not:
  - term: "editing a generated primitive to change its behavior"
    why: "the next regeneration silently reverts it"
    instead: "change the wrapper; in generated files fix only broken imports"
  - term: "importing a generated primitive directly from application code"
    why: "bypasses the wrapper, so the customization layer stops being authoritative"
    instead: "import from the design-system package's public surface"
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — design-system path instructions
    author: human:christopher
    last_modified: 2026-07-25
  - id: ds
    resource: projects/zamp/utils/design-system/
    title: zamp design-system package layout
---

# The practice

Applies when a CLI or registry generates component code into your repo
(shadcn-style). Three layers, one rule each:

| Layer | Rule |
|---|---|
| **Vendored** (`components/shadcn/`) | Third-party. Fix generated import bugs only. Excluded from lint. |
| **Wrapper** (`components/*.tsx`) | What the app imports. Owns customization, variants, docs. |
| **Barrel** (`components/index.ts`) | The public surface. Explicit and curated. |

Generated files carry a provenance comment on line 1:

```ts
// source: https://ui.shadcn.com/docs/components/base/alert
```

# Why

This is what makes "adopt a component library" survivable. Without a wrapper
layer you either fork the library and lose upgrades, or scatter per-usage
overrides and lose consistency. The wrapper is the seam where your opinions live,
and it costs almost nothing while it's a pure passthrough.

Excluding vendored code from lint is the deliberate other half: linting code you
cannot edit at the source produces churn with no fix.

# Related

[Wrapper components are explicit passthroughs](ds-wrapper-passthrough.md)
specifies what goes in the middle layer.
