---
type: Observation
title: A sentinel ordinal may mean "last", not "this particular rule"
description: 99 looked like a pin on the catch-all rule until an unrelated rule inherited it by becoming last.
kind: failure-mode
proposed_layer: meta
tags: [ordering, api, inference, netsapiens]
generated: { by: claude/opus-5, at: 2026-08-14T13:40:00Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/probe-answerrule-priority.ts
    title: probe header, RESOLVED 2026-08-14 section
    last_modified: 2026-08-14
  - id: tool
    resource: projects/wiley/web/scripts/snapshot-answering-rules.ts
    title: snapshot/diff harness that measured the portal reorder
    last_modified: 2026-08-14
---

# Observation

Every account in a 290-account fleet held exactly two ordered rules, one at
priority 0 and one at 99. Healthy accounts read `0:QuietHours 99:*`; three broken
ones read `0:* 99:QuietHours`. Seeing `*` at 99 on every healthy account and on
the test domain, I concluded 99 was a slot reserved for the catch-all, and
therefore that the ordinary create path could not have produced the broken shape,
and therefore that the cause was upstream of the API.

All of that was wrong. Reordering the test domain moved an unrelated rule from 9
to 99 purely by making it last. 99 is the final slot. With exactly two rules,
"one gets 0 and one gets 99" is arithmetic, and the three accounts were ordered
wrong rather than in a state the API cannot reach.

The general shape: when a value appears on the same entity in every sample, test
whether it attaches to the ENTITY or to its POSITION before building on it. A
fleet of uniform two-element lists cannot distinguish the two, however many
accounts you read. Only perturbing the order can.

# Why it matters

The false reading sent the investigation toward "the cause is upstream, so find
what provisions these accounts" and away from "they are simply in the wrong
order, reorder them". It also produced a fleet-wide Firestore correlation sweep
looking for a differentiator that did not exist.

Reading more accounts would never have corrected it. 287 accounts agreed with the
wrong model because every one of them had the same two-element shape. The
correction cost one drag on a test domain.

# Evidence

Before, after dragging the catch-all to the top, one operation:

    ~ *                       ordinal-priority  99 → 0
    ~ QhOrphanProbe           ordinal-priority   0 → 1
    ~ QuietHoursDisableProbe  ordinal-priority   9 → 99   ← inherited the sentinel

`QuietHoursDisableProbe` had never been touched and had sat at 9. It took 99 by
becoming last, which is what falsified "99 belongs to the catch-all".

not:
  - term: "read more production accounts to find what distinguishes the broken ones"
    why: "a uniform population cannot separate a property of the entity from a property of its position"
    instead: "perturb the ordering on a domain you can write to, and read what moves"
