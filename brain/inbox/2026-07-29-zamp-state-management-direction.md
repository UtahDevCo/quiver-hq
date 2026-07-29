---
type: Observation
title: Read through server components; write through server actions
description: Client-side tRPC and react-query are deprecated. Prefer resolving data in async server components.
kind: practice
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [rsc, data-fetching, nextjs, migration]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
not:
  - term: "client-side tRPC or react-query calls for reads or writes"
    why: "deprecated pattern being actively removed"
    instead: "call the domain query in an async server component and pass resolved data down as props"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — State Management
    last_modified: 2026-07-25
---

# Observation

**Reading** — preferred: call domain queries directly inside `async` server
components, pass resolved data to client components as props. Server actions when
a mutation or revalidation is involved. tRPC only when no direct domain query
exists (legacy).

**Writing** — react-hook-form through `useFormServerAction` / `useForm`;
submissions via server actions using `useFormServerAction`, `useAction`, or
`useActionState`.

# Why it matters

This is a migration direction, not a settled state, so the codebase contains
plenty of the deprecated pattern. New code follows the arrow; existing code is
not a violation.
