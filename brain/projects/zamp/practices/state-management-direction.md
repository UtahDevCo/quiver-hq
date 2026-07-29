---
type: Practice
title: Read through server components; write through server actions
description: Client-side tRPC and react-query are deprecated. Resolve data in async server components and pass it down as props.
tags: [rsc, data-fetching, nextjs, migration]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
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

# The practice

**Reading** — preferred: call domain queries directly inside `async` server
components, pass resolved data to client components as props. Server actions when a
mutation or revalidation is involved. tRPC only when no direct domain query exists
(legacy).

**Writing** — react-hook-form through `useFormServerAction` / `useForm`; submissions
via server actions using `useFormServerAction`, `useAction`, or `useActionState`.

# Why it matters

This is a migration **direction**, not a settled state, so the codebase contains
plenty of the deprecated pattern. New code follows the arrow; existing code is not a
violation — see "the brain describes; it does not retrofit" in
[conventions](../../../conventions.md).
