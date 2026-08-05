---
type: Observation
title: Give each kind of side effect its own try/catch returning a Result, rather than one catch spanning several
description: A single catch around a DB write plus an S3 upload plus an event send produces one indistinguishable error, so the report can't say which side effect actually failed.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [error-handling, result-type, observability, sentry, mutations]
status: draft
not:
  - term: "one try/catch wrapping a DB write, an S3 upload, and an inngest.send()"
    why: "collapses three distinct failure modes into one error message, so monitoring can't distinguish a storage outage from a queue outage from a constraint violation"
    instead: "extract a Result-returning helper per concern, each with its own narrowly-scoped try/catch, and orchestrate with .isErr() → return"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'One throwable per try/catch in mutations with mixed side effects'" }
  - { id: predates, resource: "projects/zamp/domains/.../bulk-toggle-filing-hold.ts", title: "older mixed-concern try/catch that predates the convention — explicitly not to be copied" }
---

# Observation

When a mutation performs multiple *kinds* of side effect — a DB write plus an event
send, a DB write plus an object-store upload — split each into its own helper that
wraps its own throwable in its own `try`/`catch` and returns `Result<T, Error>`. The
main mutation then orchestrates with `.isErr() → return`.

```typescript
async function transitionState(...): Promise<Result<void, Error>> {
  try {
    /* DB ops */
  } catch (error) {
    return Err(new Error("Failed to transition", { cause: error }));
  }
}

async function sendEvents(...): Promise<Result<void, Error>> {
  try {
    await inngest.send([...]);
    return Ok(undefined);
  } catch (error) {
    return Err(new Error("Failed to send events", { cause: error }));
  }
}
```

# Why it matters

This is an observability argument, not an aesthetic one. A single wide catch yields
a single error message, so every distinct cause — a constraint violation, an S3
outage, a queue being unreachable — arrives in Sentry as the same event, grouped
together, with the same title. The one question you need answered during an
incident ("which side effect broke?") is exactly the one the wide catch destroys.

Narrow catches also stop a later failure from masking an earlier one, and they keep
each error message honest: a catch that spans three operations can only be labelled
vaguely, and vague labels are what make a Sentry group useless.

# Evidence

Recorded in `patterns.md`, which also flags
`bulk-toggle-filing-hold.ts` as an older mixed-concern implementation that predates
the convention and should not be used as a model.

Proposed `meta`. It composes with two existing meta practices —
`error-propagation-and-capture` and the guidance against re-wrapping an existing
`Err` — and with the companion observation filed the same day that extraction
should be applied symmetrically across a function rather than to one step.
