---
type: Decision
title: Deprecated UI surfaces — @util/ui and the Rt* generation
description: Three retired surfaces are still importable. New code uses design-system or design-system-next; existing usages in untouched files are not violations.
tags: [design-system, deprecation, migration]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
not:
  - term: "importing from @util/ui"
    why: "legacy package, frozen — no new components are accepted there"
    instead: "@util/design-system, @util/design-system-next, or @util/ui-templates for page-level composition"
  - term: "any component whose name starts with Rt"
    why: "Radix Themes wrapper generation, being phased out"
    instead: "the same-named component from @util/design-system"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Utilities
    last_modified: 2026-07-25
  - id: rsc-reviewer
    resource: projects/zamp/.claude/agents/rsc-boundary-reviewer.md
    title: rsc-boundary-reviewer — rule 5
---

# The decision

| Surface | Status |
|---|---|
| `@util/ui` | Legacy. Frozen — no new components. |
| `Rt*` / `rt-*.tsx` | Radix Themes generation, phased out. |
| Radix Themes layout + typography primitives | Not in new code. |
| `@util/design-system` | Current. |
| `@util/design-system-next` | Current, framework-integrated — see [design-system-next](../modules/design-system-next.md). |
| `@util/ui-templates` | Composed page-level templates. |

Existing usages in untouched files are **not** violations — only newly added or
modified lines are.

The layout/typography row is the local enforcement of
[typography-and-layout-as-utilities](../../../meta/practices/typography-and-layout-as-utilities.md).

# Attestation candidate

Directly greppable, and the best first `Invariant` in the repo: flag `from "@util/ui"`
and `Rt[A-Z]` imports in changed files, excluding the design-system packages and
stories. Cheap to write and it fails loudly.

# No stale_after

A decision is a historical fact, per the freshness table in
[conventions](../../../conventions.md). What can go stale is the surface list — if a
fourth package appears, that's a new decision, not an edit to this one.
