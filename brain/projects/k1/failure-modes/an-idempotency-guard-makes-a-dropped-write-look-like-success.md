---
type: Failure Mode
title: An idempotency guard makes a dropped write look like a success
description: Asking the identical question in a fresh conversation returned HTTP 200 with nothing rendered and nothing stored, six attempts each on two questions, while 38 other runs on the same page succeeded.
tags: [idempotency, api-design, error-handling, silent-failure]
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: instance-of, target: /meta/failure-modes/verify-a-write-actually-happened.md }
not:
  - term: "derive the message id from the message content, then reject a collision with 409"
    why: "a user who asks the same question twice, or a test harness that replays a fixed set, gets a response-shaped no-op with no error surface — the guard cannot tell a retry of one request from a second genuine request"
    instead: "seed the id with a per-submission nonce so repeats are distinct, and make the collision path render something rather than resolving silently"
sources:
  - { id: guard, resource: "projects/k1/web/apps/web/app/api/projects/[tenantSlug]/[projectId]/ai-conversations/[conversationId]/messages — the 409 \"Message ID already exists\" branch", title: "the suspected collision point" }
  - { id: repro, resource: "projects/k1 — panel case generation, 2026-07-30/31", title: "two questions failed 6 attempts each while 38 other runs on the same page succeeded" }
---

# The trap

Two specific questions could not be submitted. Six attempts each, across two
environments, while 38 other questions on the same page in the same session
succeeded.

With `window.fetch` instrumented:

```
status 200, ok: true
no error text, no status line, nothing rendered
0 runs persisted
```

Rewording one of them, same meaning and same underlying data, started immediately. The
blocker is the exact text, which points at a content-derived identifier rather than at
anything about the question's difficulty. A real user hits this by asking the same
question twice.

# Why it matters

The response is shaped like success at every layer a caller can inspect: status 200,
no error body, no console output. Only a database read shows the absence, and only if
you know to look for a row that was never created. That read-back is
[verify-a-write-actually-happened](../../../meta/failure-modes/verify-a-write-actually-happened.md),
applied at the call site.

An idempotency guard is supposed to make a retry harmless, and it does that by making
the second call a no-op. That is correct when the first call succeeded and wrong when
the second call was a distinct request that happens to be identical. The guard cannot
tell those apart without a nonce the client varies per submission.

# What is confirmed and what is suspected

Confirmed: the symptom, reproducibly. Two questions, six attempts each, two
environments, 200 with nothing rendered and nothing persisted, and a reworded variant
working on the first try.

Suspected: the mechanism. The route has a `409 "Message ID already exists"` branch and
the client appears to derive message ids deterministically, which is the strongest
candidate for the path taken. It was not proven to be the path taken. Nothing here is
a read of the code that shows the collision firing, and server logs were not checked.
Reproduce against server logs before treating the content-derived id as the cause.
