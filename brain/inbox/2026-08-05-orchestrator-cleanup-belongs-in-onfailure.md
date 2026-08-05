---
type: Observation
title: Put orchestrator terminal-state cleanup in Inngest's onFailure, not an outer try/catch
description: onFailure receives the full step context and fires only after retries exhaust, so terminal-state writes land exactly once and the main handler stays a straight-line happy path.
kind: practice
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [inngest, background-jobs, error-handling, retries, orchestration]
status: draft
not:
  - term: "wrapping an Inngest handler body in a try/catch to mark a record FAILED"
    why: "the catch fires on the first transient error, before Inngest's retries have run, so it writes terminal state for a failure that would have succeeded on retry"
    instead: "declare onFailure at the function config level — it fires only on NonRetriableError or after retries exhaust"
  - term: "reading the original event payload as event.data inside onFailure"
    why: "failure events wrap the original, so event.data is the failure envelope, not your payload"
    instead: "event.data.event.data"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Orchestrator cleanup goes in onFailure, not an outer try/catch'" }
  - { id: existing-practice, resource: brain/projects/zamp/practices/inngest-background-conventions.md, title: "existing zamp Inngest conventions concept this extends" }
---

# Observation

When an Inngest function must mark a terminal-state record (`status: FAILED`) or
publish a failure event on any error, put that in `onFailure` at the function-config
level rather than in a try/catch wrapping the handler body. The main handler then
reads as a straight-line happy path.

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

`onFailure` receives the full step context — `step.run`, `step.sendEvent`,
`step.realtime.publish` — so the cleanup is itself durable.

# Why it matters

The retry interaction is the real point, and it's the part that makes the try/catch
version a correctness bug rather than a style choice.

An outer catch runs on the *first* error, which includes transient ones. So a
network blip marks the record `FAILED` — and then Inngest retries the function,
which may well succeed, leaving a completed run behind a record that says it failed.
`onFailure` fires only on `NonRetriableError` or after retries are exhausted, so
terminal state is written only for genuinely terminal failures.

The payload-shape gotcha is a separate trap: failure events wrap the original, so
the data lives at `event.data.event.data`. Reading `event.data` yields the envelope,
which is easy to miss because it doesn't fail loudly — it just yields undefined
fields.

# Evidence

Recorded in `patterns.md` under Background Jobs.

Proposed `project` layer rather than `meta` because both the API and the retry
semantics are Inngest-specific. It extends the existing
`projects/zamp/practices/inngest-background-conventions.md`, and a reviewer may
prefer to merge it there instead of promoting it as a separate concept. The
underlying principle — cleanup belongs in the handler the engine calls after retries
are exhausted, not in application-level error handling — would generalize if a
second engine corroborated it.
