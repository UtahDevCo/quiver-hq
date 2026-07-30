---
type: Observation
title: A function that must not use a value should not receive it
description: When two same-typed values are incompatible bases for one calculation, narrow the parameter object so only the correct one is in scope.
kind: practice
proposed_layer: meta
tags: [api-design, types, money, make-misuse-unrepresentable]
observed_in: trikin
status: draft
not:
  - term: "priceAssignedPaymentRight({ transaction })  // whole row in scope"
    why: "commissionCents and agentFeeCents are both integer cents on the same object; picking the wrong one is a valid program that silently overpays"
    instead: "priceAssignedPaymentRight({ assignedPaymentRightCents, discountBps }) — the wrong base is not passed in"
  - term: "// NOTE: discount applies to the fee, not the commission"
    why: "a comment is advisory; the next contributor reads the type, not the comment"
    instead: "omit the parameter, and put the other calculation in a module this one does not import"
generated: { by: claude/opus-5, at: 2026-07-30T16:30:46Z }
sources:
  - id: pricing
    resource: projects/trikin/web/src/lib/pricing.ts
    title: priceAssignedPaymentRight — input type excludes the commission
    last_modified: 2026-07-30
  - id: agent-fee
    resource: projects/trikin/web/src/lib/agent-fee.ts
    title: computeAgentFee — the only module that sees a commission amount
    last_modified: 2026-07-30
  - id: test
    resource: projects/trikin/web/src/lib/pricing.test.ts
    title: "test: would overpay by the broker's whole split if priced off the commission"
    last_modified: 2026-07-30
---

# Observation

When a calculation has exactly one correct input among several same-typed
candidates, do not pass the container that holds all of them. Narrow the
parameter object to the single correct value, and move the sibling calculation
into a module the first one does not import.

Type systems do not help here. `Cents` and `Cents` are the same type. Naming does
not help either, because both names are plausible at the call site. The only
mechanism that actually removes the failure is absence: the wrong value is not in
scope, so the wrong program does not typecheck.

This is a per-function version of
[[make-misuse-unrepresentable]] and worth distinguishing from it. That practice
deletes the alternative from the toolchain globally. Here both values must keep
existing — a commission and a fee are both real, both needed, both stored on the
same row. What gets deleted is not the value but its *reachability from one
function*.

# Why it matters

In Trikin Capital the purchase price is a discount taken against the Agent's Fee
(what the broker owes its agent). Taking the same discount against the Commission
(what the property manager owes the broker) produces an offer larger than the
asset being bought, by the entire broker split.

On the one real transaction we have that is $1,604.33 instead of $1,123.03 — a
$481.30 overpayment, 42.9% above the correct price, on a receivable that can only
ever pay back $1,247.81. Purchaser pays out more than it can collect, every time,
and the arithmetic never throws. It appears on a signed legal instrument.

The generalisation is that this failure mode is invisible to every ordinary
defence. No type error, no exception, no failing assertion, no obviously wrong
number in review — $1,604.33 looks exactly as reasonable as $1,123.03. Only the
absence of the parameter catches it.

# Evidence

`pricing.ts` cannot see a commission, because its input type has nowhere to put
one:

```ts
export type PricingInput = {
  /** Face value: the Agent's Fee, or the assigned portion of it. */
  assignedPaymentRightCents: Cents;
  /** Purchaser's gross spread, from an approved pricing matrix. */
  discountBps: Bps;
};
```

The commission-consuming calculation lives in `agent-fee.ts`, which `pricing.ts`
does not import. The dependency runs one way: a caller computes the fee, then
prices the fee.

The cost of the substitution is pinned in a test, so the number stays true if the
pricing changes:

```ts
it("would overpay by the broker's whole split if priced off the commission", () => {
  const wrong = priceAssignedPaymentRight({
    assignedPaymentRightCents: KINDLY_THREAD.acknowledgedCommissionCents,
    discountBps: KINDLY_THREAD.discountBps,
  });

  expect(wrong.purchasePriceCents - 112_303).toBe(48_130);
});
```

Note what that test is doing: it asserts the *magnitude of a bug that is now
unreachable*. It documents why the parameter is absent, so a future contributor
who finds the split awkward and "simplifies" it by passing the whole transaction
row has to delete a test that states the consequence in dollars.
