---
type: Observation
title: An idempotency guard makes a dropped write look like a success
description: Asking the identical question in a fresh conversation returned HTTP 200 with nothing rendered and nothing stored, reproducibly, while rewording the same question worked on the first try.
kind: failure-mode
proposed_layer: project
proposed_project: k1
observed_in: k1
tags: [idempotency, api-design, error-handling, silent-failure]
status: draft
not:
  - term: "derive the message id from the message content, then reject a collision with 409"
    why: "a user who asks the same question twice, or a test harness that replays a fixed set, gets a response-shaped no-op with no error surface — the guard cannot tell a retry of one request from a second genuine request"
    instead: "seed the id with a per-submission nonce so repeats are distinct, and make the collision path render something rather than resolving silently"
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
sources:
  - { id: guard, resource: "projects/k1/web/apps/web/app/api/projects/[tenantSlug]/[projectId]/ai-conversations/[conversationId]/messages — the 409 \"Message ID already exists\" branch", title: "the suspected collision point" }
  - { id: repro, resource: "projects/k1 — panel case generation, 2026-07-30/31", title: "two questions failed 6 attempts each while 38 other runs on the same page succeeded" }
---

# Observation

Two specific questions could not be submitted. Six attempts each, across two
environments, while 38 other questions on the same page in the same session
succeeded.

What was observed with `window.fetch` instrumented:

```
status 200, ok: true
no error text, no status line, nothing rendered
0 runs persisted
```

Rewording one of them, same meaning and same underlying data, started
immediately. So the blocker is the exact text, which points at a content-derived
identifier rather than at anything about the question's difficulty. The route has a
`409 "Message ID already exists"` branch, and the client appears to derive message
ids deterministically.

A real user hits this by asking the same question twice.

# Why it matters

The response is shaped like success at every layer a caller can inspect. Status
200, no error body, no console output. Only a database read shows the absence, and
only if you know to look for a row that was never created.

An idempotency guard is supposed to make a retry harmless. It does that by making
the second call a no-op, which is correct when the first call succeeded and wrong
when the second call was a distinct request that happens to be identical. The guard
cannot distinguish those without a nonce the client varies per submission.

The mechanism here is a hypothesis. The symptom is confirmed and reproducible; the
409 branch is the strongest candidate but was not proven to be the path taken.

Related: [[verify-a-write-actually-happened]] — the read-back that would have
caught this at the call site.

# Review notes

Suspected cause, not confirmed. Worth reproducing against server logs before
promoting, and worth filing regardless because the symptom is user-reachable.
