---
type: Observation
title: Deprecated UI surfaces — @util/ui and the Rt* generation
description: Three retired surfaces still importable in zamp. New code uses design-system or design-system-next.
kind: decision
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [design-system, deprecation, migration]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
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

# Observation

| Surface | Status |
|---|---|
| `@util/ui` | Legacy. Frozen — no new components. |
| `Rt*` / `rt-*.tsx` | Radix Themes generation, phased out. |
| Radix Themes layout + typography primitives | Not in new code. |
| `@util/design-system` | Current. |
| `@util/design-system-next` | Current, framework-integrated. |
| `@util/ui-templates` | Composed page-level templates. |

Existing usages in untouched files are **not** violations — only newly added or
modified lines are.

# Attestation candidate

Directly greppable, and a good first `Invariant`: flag `from "@util/ui"` and
`Rt[A-Z]` imports in changed files, excluding the design-system packages and
stories.
