---
type: Invariant
title: An approval threshold applies to the aggregate, and policy defines the aggregate
description: The $10,000 dual-approval line is measured across seven relationship dimensions plus the candidate, because the policy exists to stop one purchase being split into two.
tags: [underwriting, limits, anti-structuring, compliance, schema-design]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-02-13
relations:
  - { kind: depends-on, target: /projects/trikin/invariants/dual-approval-means-two-organisations-not-two-approvers.md }
  - { kind: depends-on, target: /projects/trikin/failure-modes/atomic-batch-is-not-a-serializable-transaction.md }
not:
  - term: "if (amountCents > THRESHOLD) requireDualApproval()"
    why: "two related $6,000 purchases each pass, and the policy explicitly forbids sequencing purchases to avoid a threshold, so the naive check implements the loophole rather than the rule"
    instead: "tier = max(candidate, aggregate across lease/transaction/agent/broker/property-manager/owner/payor/related-series), computed by one module that createOffer cannot bypass"
sources:
  - id: doa
    resource: "Delegation of Authority and Initial Underwriting Policy §1, §3.1, §3.3"
    title: "\"No person may split, sequence, or restructure related purchases to avoid an approval threshold\"; aggregation across same lease, transaction, agent, brokerage, property manager, owner, payor, or closely related series"
  - id: charter
    resource: projects/trikin/docs/trikin-capital/invariants.md
    title: "the enforcement chain — NOT NULL evaluationId FK, single writer, unique downstream FKs"
---

# The rule

The policy sets a $10,000 line: at or below it one officer may approve, above it
both Members must. The threshold is evaluated on the **maximum across every
aggregation dimension**, including the candidate purchase itself: same lease, same
transaction, same agent, same brokerage, same property manager, same owner, same
payor, and a rolling *related series* keyed on agent plus payor.

Comparing the requested amount to the number is the hole the policy was written to
close. DoA §1 says no one may split, sequence, or restructure related purchases to
avoid a threshold.

Three enforcement mechanisms, because "call the aggregation function" is not
enforcement:

- `purchase_offers.evaluationId` is a **NOT NULL foreign key** to the evaluation
  record, so an offer cannot exist without an evaluation having been written.
- `createOffer()` is the **only** exported function that inserts an offer. There is
  no lower-level primitive to reach past it.
- Downstream FKs (confirmation → offer, funding → confirmation, receivable →
  confirmation) are unique and NOT NULL, so money exists only at the end of a
  complete evaluated chain, and only once.

Structuring is also *detected* rather than merely prohibited: three or more
related-series purchases inside the window, or a sequential pair on one lease whose
sum crosses the line, routes to dual approval with a hold regardless of any single
amount.

# Why it matters

Getting this wrong does not look like a bug. Each individual purchase is
policy-compliant, each was approved by someone entitled to approve it, and the audit
trail is complete. The aggregate position required two named approvals and received
one, which is an unauthorised transaction discoverable only by recomputing exposure
after the fact.

The generalisable half: when a limit exists to prevent evasion, the unit the limit
applies to is defined by the policy, and your table's primary key is a different
unit. Reading the threshold without reading the aggregation clause produces a check
that enforces the number and not the rule.

# Evidence

DoA §3.1 lists the dimensions and adds "or closely related series when separate
treatment would reasonably create circumvention or concentration risk", an
explicitly open-ended catch-all. That is why the related-series window is
configuration under Member approval rather than a constant.

# The race this depends on

Computing an aggregate and then inserting is a read-then-decide, and D1 does not
make that safe. See
[atomic batch is not a serializable transaction](../failure-modes/atomic-batch-is-not-a-serializable-transaction.md).
