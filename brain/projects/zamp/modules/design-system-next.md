---
type: Module
title: design-system-next is a Next.js overlay, not the next generation
description: The name suggests a successor package. The code is a framework-integration layer that depends on the base package. Use it when you need router integration.
tags: [design-system, monorepo, naming]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: ds-next-pkg
    resource: projects/zamp/utils/design-system-next/
    title: "@util/design-system-next — link.tsx, pagination/, mobile-nav.tsx, linkable-table.tsx"
    last_modified: 2026-07-25
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — describes it as "where it has a replacement primitive"
---

# What it is

`@util/design-system-next` holds components needing Next.js router integration —
`link.tsx`, `pagination/`, `linkable-table.tsx`, `mobile-nav.tsx` — and takes
`@util/design-system` as a workspace dependency. No duplicated implementations.

**Selection rule:** `design-system-next` when you need router integration, otherwise
`design-system`.

# Discrepancy worth resolving

`AGENTS.md` describes it as the place to look "where it has a replacement primitive,"
which reads as *successor package*. The code says *framework overlay*. Both readings
produce the same import advice most of the time, which is probably why the ambiguity
survived.

The `-next` suffix is doing double duty — Next.js *and* "newer" — and that's the root
of it. Worth a note in `AGENTS.md`; not worth renaming a package over.

# Promotion candidate

The transferable lesson — **a framework-integration layer should depend on a
framework-agnostic core, not fork it** — may deserve a meta `Pattern` if a second
repo shows the same split.
