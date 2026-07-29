---
type: Observation
title: Validation happens three times, deliberately
description: Client, server action, and domain mutation each validate — because background jobs bypass the first two.
kind: practice
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [validation, zod, architecture]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Error Handling / triple validation
    last_modified: 2026-07-25
---

# Observation

1. **Client** — via `useFormServerAction` or `useForm` (both wrap
   react-hook-form).
2. **Server action** — via `next-safe-action`, using `inputSchema` and
   `bindArgsSchemas` (see any `*.action.ts`).
3. **Domain mutation** — sensitive and critical checks at runtime, *without* Zod.

# Why it matters

The third layer is the interesting one, and the reason it exists is stated
explicitly: domain mutations also run from **background processes**, which never
touch layers 1 or 2. So the redundancy isn't belt-and-braces — layer 3 is the
*only* validation on the background path.

It's also deliberately not Zod, to keep the check consistent between the
request path and the job path.

# Why project-layer

Reads like a general principle ("validate at every trust boundary"), but the
three specific layers and the no-Zod-in-domain choice are shaped by this
architecture. Revisit for meta promotion if a second repo shows the same split.
