---
type: Observation
title: minZero clamps each bucket before the sum, so a refund in one bucket cannot offset another
description: Clamping happens per bucket after the groupBy and before the plus, so a negative taxableAmount is discarded rather than netted against a positive nontaxableAmount.
kind: failure-mode
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [summaries, aggregation, refunds, testing, correctness]
status: draft
not:
  - term: "reading minZero(a).plus(minZero(b)) as a floor on the combined total"
    why: "each term is clamped independently, so -100 in one bucket and +500 in the other yields 500 rather than 400"
    instead: "clamp the netted value if netting is intended: minZero(a.plus(b))"
generated: { by: claude/opus-5, at: 2026-07-30T16:37:53Z }
sources:
  - { id: minzero, resource: "projects/zamp/domains/summaries/src/summary/shared.ts:5-7", title: "minZero returns ZERO for null, undefined, or negative" }
  - { id: idiom, resource: "projects/zamp/domains/summaries/src/states/tennessee/summary.ts", title: "generateScheduleG applies minZero per bucket, then plus, then round" }
  - { id: precedent, resource: "projects/zamp/domains/summaries/src/states/puerto-rico/summary.test.ts:1339-1367", title: "minZero Edge Cases describe block, including returns exceeding exempt sales" }
---

# Observation

`minZero` is a per-value clamp:

```ts
export function minZero(value: Decimal | null | undefined) {
  return !value || value.isNegative() ? ZERO : value;
}
```

The standard aggregation idiom applies it to each bucket, then adds:

```ts
minZero(t._sum.taxableAmount).plus(minZero(t._sum.nontaxableAmount)).round()
```

Two consequences that are easy to misread.

Clamping is per bucket, so the buckets cannot offset each other. A period with
`taxableAmount = -100` and `nontaxableAmount = 500` yields `500`, where clamping the
netted value would yield `400`.

Clamping happens after the `groupBy`, so it applies to the aggregate rather than to
individual rows. Refund rows inside a group net against sales rows first, and only the
group total is floored at zero. A refund larger than the period's sales collapses to
`0` rather than going negative, and if the schedule filters zero rows out of its
breakdown, the location disappears from the report entirely.

# Why it matters

Refunds are ordinary, and a return that exceeds the sales booked in the same period is
ordinary at month boundaries. The behaviour is defensible: a filing rarely wants a
negative exemption. What makes it worth writing down is that nothing at the call site
signals which of the two clampings you are getting, and the difference between them is
real money on a return.

Puerto Rico treats this as a first-class case rather than an edge, with a dedicated
`minZero Edge Cases` block covering returns exceeding sales and returns exceeding
exempt sales. Any new state schedule that aggregates with `minZero` deserves the same
test, because the arithmetic is invisible until a refund shows up in production.

# Evidence

Puerto Rico's guards at `puerto-rico/summary.test.ts:1339-1367` include
`applies minZero to Section 2 when returns exceed sales` (a `1000.00` sale against a
`-3000.00` return, asserting `0`) and
`applies minZero to Section 5 when returns exceed exempt sales`.

TN Schedule G had no equivalent until commit `91508f930`, which added
`clamps Column C to zero when returned exempt sales exceed sales`: two Section G rows
in one composite at `10000.00` and `-25000.00`, asserting the breakdown is empty and
both the Schedule G total and Schedule A Line 10 are `0`. The breakdown empties rather
than showing a zero row because `generateScheduleG` filters on
`!row.exemptSalesAmount.isZero()`.
