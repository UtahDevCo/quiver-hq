---
type: Observation
title: An atomic write batch is not a serializable transaction — read-then-decide still races
description: Cloudflare D1's db.batch() is atomic, but the read that informed the decision happened before it. Concurrent requests can both observe a pre-decision world and both write.
kind: failure-mode
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [d1, cloudflare, concurrency, limits, sqlite]
status: draft
not:
  - term: "const used = await sumExposure(key); if (used + amount <= cap) await db.batch([...insert])"
    why: "atomicity of the batch says nothing about the staleness of `used`; two requests can both read the same pre-insert total and both pass the cap"
    instead: "take a lock row by conditional UPDATE and assert meta.changes === 1, release it inside the same batch, and back it with a sweep that re-checks committed state"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: charter, resource: projects/trikin/docs/trikin-capital/invariants.md, title: "\"D1 cannot make this race-free on its own\" — the mitigation ladder as written into the repo" }
  - { id: do, resource: projects/trikin/workers/notifications/src/durable-object.ts, title: "a Durable Object already deployed in this repo — the serialization primitive that actually fixes it" }
---

# Observation

`db.batch()` on Cloudflare D1 is atomic: every statement lands or none does. It is
easy to read that as transactional and conclude a read-modify-write is safe. It is
not — the *read* that produced the decision ran in an earlier round trip, and D1
gives no read-then-write isolation across statements.

So for any check of the form "sum what exists, compare to a cap, insert if it
fits", two concurrent requests can both read the same pre-insert total, both
conclude they fit, and both insert. Each individual write was atomic. The invariant
still broke.

Mitigation ladder, weakest to strongest:

1. **Lock row by conditional update** — `UPDATE locks SET heldUntil=?, holder=?
   WHERE key=? AND heldUntil < ?`, then assert `meta.changes === 1`. This works
   because the conditional UPDATE is a single statement, which is the only unit D1
   actually serialises. Release inside the same batch as the insert.
2. **Post-commit sweep** — recompute over committed rows on a schedule and flag or
   block anything that breached. Catches whatever slipped, and is the only layer
   that tells you the other layers are working.
3. **Durable Object keyed by the contended entity** — actual serialization, and the
   real fix.

# Why it matters

The consequence is proportional to what the cap protects. Here it is a regulated
approval threshold: two requests of $6,000 against related receivables can both pass
a $10,000 single-approver limit and produce a $12,000 aggregate position that
required two named approvals and got one. That is an unauthorised transaction, not a
data-quality issue.

It is also nearly untestable by inspection and invisible in normal operation — it
needs concurrency plus contention on the same key, which is exactly what a demo and
a pilot lack and what scale supplies.

Recorded as project-layer because the specific `meta.changes` idiom and D1's
guarantees are Cloudflare-specific. The general shape — *atomicity is not
isolation; check-then-act needs the check and the act to be the same operation* —
generalises to any edge SQL, DynamoDB without a condition expression, or Firestore
outside a transaction, and would promote once a second repo shows it.

# Evidence

The repo already runs a Durable Object (`workers/notifications/src/durable-object.ts`),
so the strongest mitigation is a deployment pattern already proven here rather than
new infrastructure — which is what makes deferring to the lock-plus-sweep
combination a deliberate staging decision rather than a lack of options.
