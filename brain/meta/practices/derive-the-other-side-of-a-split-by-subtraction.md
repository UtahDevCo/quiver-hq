---
type: Practice
title: Derive the other side of a split by subtraction
description: Round one side of a percentage split and subtract for the rest, so `part + remainder === total` holds by construction across all 10,001 rates.
tags: [money, rounding, invariants, testing]
generated: { by: claude/opus-5, at: 2026-07-30T16:30:46Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/practices/money-in-integer-minor-units.md }
sources:
  - id: money
    resource: projects/trikin/web/src/lib/money.ts
    title: splitByBps and roundHalfAwayFromZero
    last_modified: 2026-07-30
  - id: test
    resource: projects/trikin/web/src/lib/money.test.ts
    title: "test: never loses a cent, across every rate at a value that rounds badly"
    last_modified: 2026-07-30
not:
  - term: "{ part: round(total * bps), remainder: round(total * (1 - bps)) }"
    why: "both sides round the same direction at some rates, so part + remainder drifts off total by a cent"
    instead: "const part = round(total * bps); return { part, remainder: total - part }"
  - term: "Math.round(cents * bps / 10000)"
    why: "Math.round breaks ties toward +Infinity, so -0.5 rounds to -0 while 0.5 rounds to 1, which is asymmetric on the negative amounts write-offs produce"
    instead: "value < 0 ? -Math.round(-value) : Math.round(value)"
  - term: "keep the symmetric formulation and add a test that the parts sum to the whole"
    why: "the test only covers the (amount, rate) pairs you enumerated"
    instead: "pick the formulation where the identity holds for every input"
---

# The practice

Splitting an integer money amount by a percentage: compute one side with rounding,
derive the other by subtraction.

```ts
const part = roundHalfAwayFromZero((amountCents * bps) / BPS_DENOMINATOR);
return { part, remainder: amountCents - part };
```

`part + remainder === amountCents` is then true for every amount and every rate,
with no test needed to establish it.

Round half away from zero, not `Math.round`. `Math.round(-0.5)` is `-0` while
`Math.round(0.5)` is `1`. Money arithmetic runs over negative amounts during
write-offs and downward corrections, and that asymmetry loses a cent in one
direction only, which stays invisible in aggregate until the signs mix.

# Why the symmetric version is the tempting one

Rounding both sides independently is the natural way to write this, reads correctly,
and passes any small hand-written test. It fails on the specific pairs where both
halves round the same direction.

In trikin's commission purchase the split is between what the agent is owed and what
the broker retains, and downstream between the purchase price and the Purchaser's
discount. Both pairs print on a Purchase Confirmation, an electronic instrument
retained seven years under Texas UETA whose enforceability depends on being "capable
of accurate reproduction". A document whose stated components do not add up to its
stated total is a bad thing to have signed and hashed.

# Evidence

The comment lives at the call site because the symmetric version is the one someone
will reach for:

```ts
/**
 * Rounding both sides independently is the bug this exists to prevent: at a
 * 3333 bps split of 1000 cents, independent rounding yields 333 + 667 = 1000 by
 * luck, and 333 + 666 = 999 as soon as the rate changes.
 */
export function splitByBps(amountCents: Cents, bps: Bps): Split {
  const part = applyBps(amountCents, bps);

  return { part, remainder: amountCents - part };
}
```

The test sweeps all 10,001 rates against an amount chosen to round badly and asserts
on the whole list of failures, so a regression names the rates it broke at:

```ts
it("never loses a cent, across every rate at a value that rounds badly", () => {
  const lossy: number[] = [];

  for (let bps = 0; bps <= 10_000; bps += 1) {
    const { part, remainder } = splitByBps(999, bps);

    if (part + remainder !== 999) {
      lossy.push(bps);
    }
  }

  expect(lossy).toStrictEqual([]);
});
```

The stdlib's behaviour is pinned alongside the custom function, so the reason for the
custom function survives someone deciding it is redundant:

```ts
expect([roundHalfAwayFromZero(0.5), roundHalfAwayFromZero(-0.5)]).toStrictEqual([1, -1]);
expect([Math.round(0.5), Math.round(-0.5)]).toStrictEqual([1, -0]);
```
