---
type: Practice
title: Propagate errors untouched; capture once, at the edge
description: Never rewrap an error you are merely passing along, and never report it twice. One failure, one report, at one place.
tags: [error-handling, observability, debugging]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "wrapping an error you are only propagating, e.g. Err(new Error('doThing failed', { cause: result.error }))"
    why: "hides the inner stack and cause chain behind a frame that adds no information"
    instead: "return it as-is — if (result.isErr()) return result;"
  - term: "captureException(e) followed by throw e"
    why: "the edge handler captures it too, producing duplicate reports for one failure and breaking issue grouping"
    instead: "let it bubble; capture only where you stop it"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Error Handling
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

Three rules that are really one idea — **one failure, one report, at one place.**

1. **Propagating** — return the existing error unchanged. It already carries its
   stack and cause chain.
2. **Originating** — when *you* create the error, do attach context:
   `new Error("Message", { cause: originalError })`.
3. **Reporting** — let errors reach the system edge, which captures uncaught
   failures automatically. Capture manually **only when you are intentionally
   stopping** the error: it's recoverable, or it must not surface to the user, and
   you still want to know it happened.

The signal that a manual capture is correct: you are *swallowing* the error
rather than passing it on.

# Why both anti-patterns are seductive

Rewrapping looks like good hygiene — you're "adding context!" — while erasing the
stack that identifies the real failure site. Capture-then-rethrow looks defensive
while doubling alert volume and splitting one incident across two issues.

Both read as *more* careful than the correct version, which is why they survive
review.

# The legitimate capture-and-throw case

When throwing would genuinely lose detail — e.g. a failure whose error is an
*array* of underlying causes that would collapse into one composite message —
capture each underlying error with structured context, then throw a summary. The
duplication is deliberate: preserving per-error context beats deduping the
summary.

This exception is narrow. If you can name the single underlying error, you don't
qualify.

# Library note

Recorded from a codebase using `Result`/`ts-results-es` and Sentry, but the
rules are library-agnostic — they apply equally to bare `throw`, to Go-style
error returns, and to any error reporter.

# Related

[Never send Error objects across a serialization boundary](no-error-objects-across-boundaries.md)
covers what happens when an error has to *cross* a process or runtime edge.
