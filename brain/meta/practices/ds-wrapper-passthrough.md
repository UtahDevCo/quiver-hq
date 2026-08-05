---
type: Practice
title: Wrapper components are explicit passthroughs typed off the primitive
description: Derive props from the primitive, add your own, merge classes, spread the rest. Never a bare re-export.
tags: [design-system, react, typescript, api-design]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-08-05
relations:
  - { kind: instance-of, target: /meta/practices/ds-vendor-wrap-export-layering.md }
not:
  - term: "export { Button } from './shadcn/button'"
    why: "a bare re-export leaves nowhere to add a prop later without a breaking import change"
    instead: "an explicit function component that spreads props through"
  - term: "hand-writing the wrapper's prop type"
    why: "drifts from the primitive on every upgrade"
    instead: "ComponentProps<typeof Primitive> & { yourProps }"
sources:
  - id: wrappers
    resource: projects/zamp/utils/design-system/src/components/
    title: "zamp wrappers — input.tsx, button.tsx, alert.tsx"
    author: human:christopher
    last_modified: 2026-07-25
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'No forwardRef in React 19'; broadened the ref bullet from wrappers to any component"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

```tsx
export type InputProps = Omit<ShadcnInputProps, "aria-invalid"> & { error?: boolean };

export function Input({ error, ...props }: InputProps) {
  return <ShadcnInput {...props} aria-invalid={error || undefined} />;
}
```

- Prop types **derive** from the primitive: `ComponentProps<typeof Primitive>`,
  narrowed with `Omit` where the wrapper takes ownership of a prop.
- Added props are a union on top, not a rewrite.
- Class composition through a `cn()` merge helper; variants via
  `class-variance-authority`.
- Always spread the remainder: `{...props}`.
- **No `forwardRef`, and no manual ref forwarding** — in React 19 `ref` is an
  ordinary prop, so a function component accepts it directly and primitives already
  forward. This applies when authoring *any* component, not just a wrapper: accept
  `ref` in the props type instead of wrapping. Worth stating explicitly because
  nearly every pre-19 example still uses `forwardRef`, so it gets reproduced by
  default and then spreads — an author writing a sibling component matches the
  neighbour.
- JSDoc on the primary export, linking both the component docs and the
  underlying primitive's API reference.
- Every named export of the generated file is either wrapped or re-exported.
  Missing a sub-component is the common failure — check the full export list.

# Why an explicit passthrough beats a re-export

The wrapper's value is that it exists *before* you need it. Adding a passthrough
later is a breaking import change across the codebase; adding a prop to an
existing passthrough is free. The cost of the empty wrapper is three lines.
