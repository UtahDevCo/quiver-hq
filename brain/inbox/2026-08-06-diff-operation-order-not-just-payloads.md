---
type: Observation
title: Diff an external spec's operation order separately from its payloads
description: A counterparty spec can match your field names exactly and still invert a control on the money path, because ordering lives in prose that a field-by-field diff never reads.
kind: practice
proposed_layer: meta
tags: [integration, contracts, money-path, review]
generated: { by: claude/opus-5, at: 2026-08-06T14:28:59Z }
status: draft
sources:
  - id: built-gate
    resource: projects/trikin/web/src/lib/assignment/issue-notice.ts
    title: issueAssignmentNotice raises PayeeUpdateUnconfirmed in the same act that writes the notice
    last_modified: 2026-08-05
  - id: canonical-doc
    resource: projects/trikin/docs/trikin-capital/integration-rails.md
    title: "Integration rails, section: The payee update is gated, not announced"
    last_modified: 2026-08-05
  - id: counterparty-spec
    resource: email from josh@trikin.co, 2026-08-05 14:01, forwarded to the Oakland Creek HubSpot team
    title: Brokerage-facing two-rail spec
    last_modified: 2026-08-05
not:
  - term: "reconcile an external spec by mapping its field list onto your schema"
    why: "payload agreement is the cheap half; the control usually lives in a verb order or a precondition stated once in prose"
    instead: "diff three things separately: fields, order of operations, and the preconditions each side enforces before each step"
---

# Observation

When reconciling an externally authored integration spec against a system you have
already built, diff the **order of operations** and the **preconditions on each step**
as separate passes from the payload diff. A control your code enforces is a precondition
the other side's prose must state explicitly. If the spec merely fails to contradict it,
that is not agreement, and the party implementing from that spec will build the
unguarded version.

# Why it matters

Trikin's Rail 2 is confirm-then-fund. `issueAssignmentNotice` raises a blocking
`payee_update_unconfirmed` hold in the same act that writes the assignment notice row,
and the notice table is NOT NULL on `holdId` so a notice cannot exist without money
being stopped. Funding waits for the brokerage to confirm that its payout record names
the purchaser.

The brokerage-facing spec our own principal sent the counterparty describes
fund-then-notify: "Agent signs assignment + Trikin funds agent. Then Trikin sends the
brokerage an Assignment Notice / Payee Update."

That inversion removes the only loss remedy in the design. Under direct-to-agent
funding, if the brokerage pays the agent anyway the purchaser cannot recover from the
agent, because a covenant forbids the agent ever owing the purchaser money, and the cash
is already spent. What is left is a contractual repurchase claim against the brokerage,
which is a claim rather than a payment.

The reason it was easy to miss is that everything else matched. Both rails, the trigger
names, the field lists, and a worked example correct to the cent: $2,000 gross, 70%
split, $1,400 asset, $1,260 advanced, $140 fee. A field-by-field reconciliation passes
clean and reports agreement.

# Evidence

Built (`issue-notice.ts:121`), inside the same transaction as the notice insert:

```ts
    reason: HoldReason.PayeeUpdateUnconfirmed,
```

Canonical doc, `integration-rails.md`:

> So the notice is a request that must come back confirmed. A funding release is blocked
> until the brokerage acknowledges that its payout record now names Trikin.

Counterparty spec, same rail:

> Trigger inside Trikin: Agent signs assignment + Trikin funds agent
> Then Trikin sends the brokerage an Assignment Notice / Payee Update.

Caught by reading the trigger sentence, not by comparing the two field tables. The field
tables agreed.
