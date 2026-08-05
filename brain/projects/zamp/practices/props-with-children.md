---
type: Practice
title: Type a children prop as PropsWithChildren
description: PropsWithChildren is the dominant shape in this repo for the ordinary children case; reserve an explicit children field for children deliberately typed narrower than ReactNode.
tags: [react, typescript, components, conventions]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "export function Foo({ children }: { children: ReactNode })"
    why: "hand-rolls the shape React already exports, and spends the signal that a hand-written children type otherwise carries"
    instead: "PropsWithChildren, or PropsWithChildren<{ label: string }> when there are other props"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Use PropsWithChildren for components that take children'"
    author: human:christopher
    last_modified: 2026-08-05
  - id: precedent-bressain
    resource: projects/zamp/apps/company/src/app/(onboarding)/[id]/onboarding/page-components.tsx
    title: "Bressain's usage"
    last_modified: 2026-08-05
  - id: precedent-walsh
    resource: projects/zamp/apps/admin/src/app/components/filing-management/filing-details-sheet.client.tsx
    title: "James Walsh's usage; also activity/activity-feed.tsx"
    last_modified: 2026-08-05
---

# The practice

When a component takes `children`, type its props as `PropsWithChildren` — or
`PropsWithChildren<{ ...otherProps }>` — from `react`.

```tsx
import type { PropsWithChildren } from "react";

export function Foo({ children }: PropsWithChildren) { ... }
export function Bar({ children, label }: PropsWithChildren<{ label: string }>) { ... }
```

Reserve an explicit `children` field for when you are deliberately typing children
*narrower* than `ReactNode` — e.g. `children: ReactElement<SomeProps>` to require a
particular element type.

# Why the consistency buys something

Mostly convention, but there is a real signal underneath. If the ordinary case always
uses `PropsWithChildren`, a hand-written `children:` field becomes informative: it tells
the reader this component constrains what it accepts, so look at the type. If both forms
appear interchangeably for the ordinary case, that signal is gone and a deliberately
narrowed children type is indistinguishable from someone's stylistic preference.

# Why this sits in the project layer

The idiom is React-general, but the evidence is this repo only — two contributors
converging independently within one codebase, which
[corroboration-requires-independent-sources](../../../meta/workflows/corroboration-requires-independent-sources.md)
treats as weaker than two repos agreeing. It is also a convention rather than a
correctness rule: nothing breaks either way.

Promote to `meta/` if a second repo shows the same preference.
