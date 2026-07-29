---
type: Practice
title: Never send Error objects across a serialization boundary
description: Error instances do not serialize. Pass the message string across any process, runtime, or storage boundary.
tags: [error-handling, serialization, react, rsc]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "<ClientComponent error={error} /> where error is an Error"
    why: "Error instances are not serializable; the prop arrives empty or throws at the boundary"
    instead: "<ClientComponent error={error.message} />"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Server/Client Boundaries
    author: human:christopher
    last_modified: 2026-07-25
  - id: rsc-reviewer
    resource: projects/zamp/.claude/agents/rsc-boundary-reviewer.md
    title: rsc-boundary-reviewer — rule 4 (dedicated subagent enforces this)
---

# The practice

Pass `error.message` (a string), never the `Error` instance, across a
serialization boundary.

Boundaries this covers:

- server → client components (React Server Components)
- `postMessage` / `structuredClone` / web workers
- background job and queue payloads
- cache entries and any persisted state

# Why it keeps happening

The type system does not catch it. `error` is a valid prop or field name on both
sides, and the types line up. It fails at runtime, at the boundary, often as an
empty object rather than a thrown error — so it degrades into a blank error
message in production rather than a crash in development.

zamp considers it important enough to enforce with a dedicated reviewer subagent,
which is a strong signal that types-plus-review isn't sufficient on its own.

# If you need more than the message

Serialize deliberately: pick the fields you want (`message`, `name`, a
correlation id) and build a plain object. Do not reach for a generic
error-serializer that walks the whole instance — you will leak stack traces to
clients.

# Related

[Propagate errors untouched; capture once, at the edge](error-propagation-and-capture.md).
