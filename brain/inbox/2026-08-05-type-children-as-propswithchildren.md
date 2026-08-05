---
type: Observation
title: Type a children prop as PropsWithChildren, not as { children: ReactNode }
description: PropsWithChildren is the idiomatic shape for the ordinary children case; reserve an explicit children field for when you're deliberately typing children narrower than ReactNode.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [react, typescript, components, conventions]
status: draft
not:
  - term: "export function Foo({ children }: { children: ReactNode })"
    why: "hand-rolls the shape React already exports, and loses the signal that a hand-written children type carries — namely that the type is deliberately narrower"
    instead: "PropsWithChildren, or PropsWithChildren<{ label: string }> when there are other props"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Use PropsWithChildren for components that take children'" }
  - { id: precedent-a, resource: "projects/zamp/apps/company/src/app/(onboarding)/[id]/onboarding/page-components.tsx", title: "Bressain's usage" }
  - { id: precedent-b, resource: "projects/zamp/apps/admin/src/app/components/filing-management/filing-details-sheet.client.tsx", title: "James Walsh's usage" }
---

# Observation

When a component takes `children`, type its props as `PropsWithChildren` — or
`PropsWithChildren<{ ...otherProps }>` — imported from `react`, rather than
declaring `{ children: ReactNode }` by hand.

```tsx
import type { PropsWithChildren } from "react";

export function Foo({ children }: PropsWithChildren) { ... }
export function Bar({ children, label }: PropsWithChildren<{ label: string }>) { ... }
```

Reserve an explicit `children` field for when you are intentionally typing children
*narrower* than `ReactNode` — e.g. `children: ReactElement<SomeProps>` to require a
particular element type.

# Why it matters

Mostly consistency, but there's a real signal underneath it. If the ordinary case
uses `PropsWithChildren`, then a hand-written `children:` field becomes
informative — it tells the reader "this component constrains what children it
accepts, look at the type." If both forms are used interchangeably for the ordinary
case, that signal is gone, and a deliberately narrowed children type is
indistinguishable from someone's stylistic preference.

# Evidence

`patterns.md` records this as the dominant pattern in zamp and cites both
design-system-adjacent contributors independently using it: Bressain in
`page-components.tsx`, James Walsh in `filing-details-sheet.client.tsx` and
`activity-feed.tsx`. Two authors converging independently within one repo is
weaker than two repos agreeing, so this is proposed `meta` on the strength of the
idiom being React-general rather than on corroboration.

If it's judged project-layer instead, that's a reasonable read — the evidence is
zamp-only.
