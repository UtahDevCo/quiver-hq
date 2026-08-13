---
type: Failure Mode
title: Drizzle wraps constraint errors on .execute() but not on db.batch()
description: A UNIQUE-violation catch that matches error.message works after db.batch() and silently fails after .execute(), because only the latter wraps the driver error in DrizzleQueryError. Walk the cause chain.
tags: [drizzle, sqlite, d1, error-handling, concurrency]
generated: { by: claude/opus-5, at: 2026-08-07T18:57:02Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: instance-of, target: /meta/failure-modes/probe-before-trusting-an-api-claim.md }
not:
  - term: "error instanceof Error && /UNIQUE constraint failed/i.test(error.message)"
    why: "after .execute() the top-level error is a DrizzleQueryError whose message carries the SQL and the bound parameters, never the constraint, so the branch is dead"
    instead: "walk error.cause to the driver error before matching, and match on the walked chain regardless of which call shape raised it"
  - term: "the sibling call site catches UNIQUE the same way, so it has the same bug"
    why: "the sibling went through db.batch(), which surfaces the driver error unwrapped, and its race test passes"
    instead: "run the sibling's own test before editing it; the call shape decides, not the catch block"
sources:
  - id: fix
    resource: projects/trikin/web/src/db/queries/aggregation-locks.ts
    title: "isUniqueViolation, walking the cause chain (trikin commit c657ba0)"
    last_modified: 2026-08-07
  - id: counterexample
    resource: projects/trikin/web/src/db/queries/approvals.ts
    title: "recordDecision — matches error.message directly and is correct, because it catches around db.batch()"
    last_modified: 2026-08-07
---

# The trap

`drizzle-orm` does not present a uniform error shape across its two execution paths.
On `.execute()` the driver error is wrapped in a `DrizzleQueryError`, whose own
`message` is the SQL text and the bound parameters. On `db.batch()` the driver error
propagates unwrapped. So this catch:

```ts
if (error instanceof Error && /UNIQUE constraint failed/i.test(error.message)) { ... }
```

is correct after `db.batch()` and is a dead branch after `.execute()`. Match by
walking `cause` instead, which is right for both:

```ts
function isUniqueViolation(error: unknown): boolean {
  for (let current = error; current instanceof Error; current = current.cause) {
    if (/UNIQUE constraint failed|PRIMARY KEY/i.test(current.message)) return true;
  }

  return false;
}
```

Checked against drizzle-orm ^0.44.5 on Cloudflare D1. Any SQLite driver reached
through drizzle is worth re-probing rather than assuming, per
[probe before trusting an API claim](../../../meta/failure-modes/probe-before-trusting-an-api-claim.md).

# Why it matters

Constraint violations caught this way are almost always a concurrency backstop: the
code read, decided, and is relying on the index to reject the loser of a race that
read-then-write isolation would have prevented. When the branch is dead, the loser
gets a 500 and an unhandled exception instead of the domain error the design
intended. The failure appears only when two requests actually collide, which is the
path least likely to be exercised by hand.

The second half is about the fix rather than the bug. Having found it, I assumed a
sibling call site with a visibly identical catch had it too. Probing first showed the
opposite: that one wraps `db.batch()`, its race test passes, and "fixing" it would
have edited working code on the strength of a pattern match. The distinguishing fact
is the call shape, and it is not visible in the catch block.

# Evidence

trikin `aggregation_locks` implements mutual exclusion by conditional update:
`UPDATE ... WHERE heldUntil <= now RETURNING`, and when nothing matched, an `INSERT`
whose primary key rejects a live holder. A test asserting that a second acquire
returns a retryable 409 got a 500 instead. The insert goes through `.execute()`, so
the thrown value was a `DrizzleQueryError` and the message match never fired.
`isUniqueViolation` walking `cause` fixed it.

`db/queries/approvals.ts` `recordDecision` guards dual-member approval the same way,
protecting a `(subjectType, subjectId, memberOrg)` unique index against two tabs both
passing a same-Member check:

```ts
try {
  await db.batch(writes);
} catch (error) {
  if (error instanceof Error && /UNIQUE constraint failed/i.test(error.message)) {
    throw new ApprovalRecordError(...);
  }

  throw error;
}
```

Its existing race test passes unchanged, because `db.batch()` surfaces the error
unwrapped. Left alone.
