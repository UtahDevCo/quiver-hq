---
type: Practice
title: Inngest background job conventions
description: Naming, step selection, and error semantics for background functions. Test the underlying mutation unless the function holds real orchestration logic.
tags: [background-jobs, inngest]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-08-05
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Background Jobs
    last_modified: 2026-07-25
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — onFailure cleanup, handler logger, background/ colocation"
    author: human:christopher
    last_modified: 2026-08-05
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
- Destructure `logger` from the handler args rather than a module-level
  `getLogger` — the injected logger attaches `runId` / `functionId` / `eventId`
  and flows through Inngest's telemetry.
- Co-locate Inngest-only helpers (realtime channels, publishers) under
  `background/` beside the function, not at the domain root — a root file signals
  "domain-wide API".
- Usually **no dedicated test** — test the underlying mutation instead. Exception:
  test the background function directly when it holds real orchestration logic
  beyond calling a mutation.

# Terminal-state cleanup goes in `onFailure`, not an outer try/catch

When a function must mark a record `FAILED` or publish a failure event on any error,
declare that in `onFailure` at the function-config level. The handler body then stays
a straight-line happy path.

```typescript
inngest.createFunction(
  {
    id: "my-fn",
    triggers: [...],
    onFailure: async ({ event, step, error }) => {
      const { companyId, recordId } = event.data.event.data;
      await step.run("mark-failed", async () => {
        (await updateRecord({ companyId, recordId, data: { status: FAILED } })).unwrap();
      });
    },
  },
  async ({ event, step, logger }) => {
    // happy path only
  },
);
```

This is a correctness difference, not a style choice. An outer catch fires on the
*first* error, including transient ones — so a network blip writes `FAILED`, and then
Inngest retries and may succeed, leaving a completed run behind a record that says it
failed. `onFailure` fires only on `NonRetriableError` or after retries are exhausted,
so terminal state is written only for genuinely terminal failures. It receives the
full step context (`step.run`, `step.sendEvent`, `step.realtime.publish`), so the
cleanup is itself durable.

Gotcha: failure events **wrap** the original, so the payload is at
`event.data.event.data`. Reading `event.data` yields the envelope and fails quietly
with undefined fields.

# Why it matters

The testing guidance is the part worth keeping: it names the condition under which
the default flips, rather than saying "use judgment."

Background functions are also the reason
[triple-validation](triple-validation.md) has a third layer — this is the path that
bypasses the first two.
