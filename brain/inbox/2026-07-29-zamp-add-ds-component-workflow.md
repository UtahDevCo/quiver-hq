---
type: Observation
title: Adding a design-system component is a defined four-step workflow
description: Install and wrap the primitive, fix known generator import bugs, write stories from the fetched docs, then polish and deprecate.
kind: workflow
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [design-system, workflow, storybook]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
sources:
  - id: skill
    resource: projects/zamp/.claude/skills/add-ds-component/SKILL.md
    title: add-ds-component skill
    author: human:christopher
    last_modified: 2026-07-25
---

# Observation

1. **Gather** — shadcn or custom? deprecating something? the Base-UI-flavored
   docs URL? special wrapper/story instructions? Asked in a single message.
2. **Install and wrap** — `pnpm dlx shadcn@latest add <name> --cwd
   utils/design-system --overwrite`; add the `// source: <url>` line; fix the
   generator's known bad imports; write the wrapper. If a wrapper already exists
   at that path, rename the old one to `rt-*` first.
3. **Stories** — fetch the docs page *and* the primitive's API reference, then
   write stories covering the surface the wrapper actually exposes.
4. **Polish** — passthrough shape, JSDoc, `@deprecated` migration guides. **Do
   not** add the export to the barrel; remind the user to do it before pushing.

Known generator import bugs it corrects:

| Generated | Correct |
|---|---|
| `"src/lib/utils"`, `"@/lib/utils"` | `"../../lib/utils"` |
| `"src/components/shadcn/<n>"`, `"@/components/shadcn/<n>"` | `"@base-ui/react/<n>"` |
| `"src/hooks/<n>"`, `"@/hooks/<n>"` | `"../../hooks/<n>"` |

# Why it matters

Two deliberate human checkpoints: the barrel export is left to the user, and
renames are the user's call. The workflow stops short of the irreversible,
review-worthy steps.

The URL requirement is load-bearing — it insists on the `/base/` variant because
the primitive library determines the generated output. A wrong URL yields a
component built on the wrong primitives.
