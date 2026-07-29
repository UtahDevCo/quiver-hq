---
type: Observation
title: Let errors bubble to the system edges; capture once
description: Never rewrap an existing Err, and never captureException-then-rethrow — both destroy context or duplicate signal.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [error-handling, observability, sentry]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
not:
  - term: "Err(new Error('doThing failed', { cause: result.error }))"
    why: "rewrapping an Err you are merely propagating hides the inner stack and cause chain"
    instead: "if (result.isErr()) return result;"
  - term: "Sentry.captureException(e) followed by throw e"
    why: "the edge handler captures it too, producing duplicate events for one failure"
    instead: "let it bubble; capture only where you stop it"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Error Handling
    last_modified: 2026-07-25
---

# Observation

Two rules, same underlying idea — **one error, one report, at one place.**

1. **Propagating:** return the existing `Err` as-is. It already carries its
   stack and `cause` chain.
2. **Creating:** when you originate an error, *do* attach context —
   `Err(new Error("Message", { cause: originalError }))`.
3. **Reporting:** let errors reach the system edge, which captures uncaught
   errors automatically. Capture manually **only when you are intentionally
   stopping** the error — it's recoverable, or it must not surface to the user —
   and you still want to know.

The signal for a manual capture is that you are *swallowing* rather than
propagating.

# Why it matters

Both anti-patterns produce plausible-looking code. Rewrapping looks like good
hygiene ("adding context!") while erasing the stack that identifies the real
failure site. Capture-then-rethrow looks defensive while doubling your alert
volume and breaking issue grouping.

# Documented edge case, worth carrying forward

Capture *and* throw is legitimate when throwing would lose detail — e.g. a
result whose error is an array of underlying failures that would collapse into
one composite `Error`. Capture each underlying error with structured context,
then throw a summary. The duplication is deliberate: per-error context beats
deduping the summary.

# Layer note

The `Result`/`ts-results-es` vocabulary is zamp's choice, but the underlying
rules are library-agnostic. Promote the rules; leave `ts-results-es` in the
project layer.
