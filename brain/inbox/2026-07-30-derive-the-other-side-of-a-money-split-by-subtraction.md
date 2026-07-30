---
type: Observation
title: Derive the other side of a money split by subtraction, never by rounding both sides
description: Rounding each side of a percentage split independently makes the parts stop summing to the whole at some rates; subtract instead so the identity holds by construction.
kind: practice
proposed_layer: meta
tags: [money, rounding, invariants, testing]
observed_in: trikin
status: draft
not:
  - term: "{ part: round(total * bps), remainder: round(total * (1 - bps)) }"
    why: "both sides round the same direction at some rates, so part + remainder drifts off total by a cent"
    instead: "const part = round(total * bps); return { part, remainder: total - part }"
  - term: "Math.round(cents * bps / 10000)"
    why: "Math.round breaks ties toward +Infinity, so -0.5 rounds to -0 while 0.5 rounds to 1 — asymmetric on the negative amounts that write-offs produce"
    instead: "value < 0 ? -Math.round(-value) : Math.round(value)"
generated: { by: claude/opus-5, at: 2026-07-30T16:30:46Z }
sources:
  - id: money
    resource: projects/trikin/web/src/lib/money.ts
    title: splitByBps and roundHalfAwayFromZero
    last_modified: 2026-07-30
  - id: test
    resource: projects/trikin/web/src/lib/money.test.ts
    title: "test: never loses a cent, across every rate at a value that rounds badly"
    last_modified: 2026-07-30
---

# Observation

When splitting an integer money amount by a percentage, compute **one** side with
rounding and derive the other by subtraction:

```ts
const part = roundHalfAwayFromZero((amountCents * bps) / BPS_DENOMINATOR);
return { part, remainder: amountCents - part };
```

`part + remainder === amountCents` is then true by construction, for every amount
and every rate, with no test required to establish it.

Two related points on the rounding function itself. Use round-half-away-from-zero
rather than `Math.round`: the latter breaks ties toward positive infinity, so
`Math.round(-0.5)` is `-0` while `Math.round(0.5)` is `1`. Money arithmetic runs
over negative amounts during write-offs and downward corrections, and the
asymmetry loses a cent in one direction only — which is the hardest kind of
discrepancy to find, because it does not show up in aggregate until the signs mix.

# Why it matters

Rounding both sides independently is the natural way to write this, reads
correctly, and passes any small hand-written test. It fails on specific
(amount, rate) pairs where both halves round the same direction, and then the
parts no longer sum to the whole.

In a commission purchase the split is between what the agent is owed and what the
broker retains, and downstream between the purchase price and Purchaser's
discount. Both pairs appear on a Purchase Confirmation — an electronic instrument
retained seven years under Texas UETA, whose enforceability depends on being
"capable of accurate reproduction". A document whose stated components do not add
up to its stated total is a bad thing to have signed, and worse to have hashed and
frozen.

The wider point is that this is an invariant available for free from the shape of
the code. Choosing the formulation where the property holds by construction is
strictly better than choosing the symmetric-looking formulation and then testing
for the property — the test can only tell you about the cases you enumerated.

# Evidence

`splitByBps` in `money.ts`, with the reasoning kept at the call site because the
symmetric version is the tempting one:

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

The test sweeps all 10,001 rates against an amount chosen to round badly, and
asserts on the whole list of failures rather than a count, so a regression names
the rates it broke at:

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

The asymmetry of `Math.round` is pinned directly, including the stdlib's actual
behaviour, so the reason for the custom function survives someone deciding it is
redundant:

```ts
expect([roundHalfAwayFromZero(0.5), roundHalfAwayFromZero(-0.5)]).toStrictEqual([1, -1]);
expect([Math.round(0.5), Math.round(-0.5)]).toStrictEqual([1, -0]);
```
