---
type: Practice
title: Inngest background job conventions
description: Naming, step selection, and error semantics for background functions. Test the underlying mutation unless the function holds real orchestration logic.
tags: [background-jobs, inngest]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Background Jobs
    last_modified: 2026-07-25
---

# The practice

- Defined in each domain's `background.ts`; named `{action}{Entity}Function`.
- `step.run` for synchronous work in the same function; `step.invoke` for calling
  other functions or external services.
- `Promise.all` around concurrent `step.invoke` calls — each step has its own
  throttle limits, so parallel invokes genuinely buy throughput.
- Step names are kebab-case: `step.invoke('get-audience-members-california', …)`.
- Non-retriable errors for permanent failures.
- `.unwrap()` on Results in background functions; `.expect()` in server actions.
- Usually **no dedicated test** — test the underlying mutation instead. Exception:
  test the background function directly when it holds real orchestration logic
  beyond calling a mutation.

# Why it matters

The testing guidance is the part worth keeping: it names the condition under which
the default flips, rather than saying "use judgment."

Background functions are also the reason
[triple-validation](triple-validation.md) has a third layer — this is the path that
bypasses the first two.
