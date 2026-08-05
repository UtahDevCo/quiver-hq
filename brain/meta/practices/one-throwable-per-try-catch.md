---
type: Practice
title: Give each kind of side effect its own try/catch returning a Result
description: One catch spanning a DB write, an upload, and an event send collapses three distinct failure modes into one indistinguishable error, destroying the attribution an incident needs.
tags: [error-handling, result-type, observability, mutations]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
relations:
  - { kind: depends-on, target: /meta/practices/error-propagation-and-capture.md }
not:
  - term: "one try/catch wrapping a DB write, an object-store upload, and an event send"
    why: "collapses three failure modes into one message, so monitoring cannot distinguish a storage outage from a queue outage from a constraint violation"
    instead: "extract a Result-returning helper per concern, each with its own narrow try/catch, and orchestrate with .isErr() → return"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'One throwable per try/catch in mutations with mixed side effects'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

When a function performs multiple *kinds* of side effect — a DB write plus an event
send, a DB write plus an object-store upload — split each into a helper that wraps its
own throwable in its own `try`/`catch` and returns a `Result`. The caller orchestrates
with `.isErr() → return`.

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
    await queue.send([...]);
    return Ok(undefined);
  } catch (error) {
    return Err(new Error("Failed to send events", { cause: error }));
  }
}
```

# Why this is an observability argument

A single wide catch produces a single error message, so every distinct cause — a
constraint violation, a storage outage, an unreachable queue — arrives in the error
tracker as the same event, grouped under the same title. The one question an incident
actually needs answered, *which side effect broke*, is precisely what the wide catch
destroys.

Narrow catches also stop a later failure from masking an earlier one, and they keep
each message honest: a catch spanning three operations can only be labelled vaguely,
and vague labels are what make an error group useless.

# Relation

Composes with [error-propagation-and-capture](error-propagation-and-capture.md),
which governs what to do with an error once you hold it — propagate untouched, attach
context only when originating, capture once where you stop it. This practice governs
how *narrowly* to catch in the first place.
[uniform-error-handling-shape-per-function](uniform-error-handling-shape-per-function.md)
then requires applying the chosen shape consistently across the function.
