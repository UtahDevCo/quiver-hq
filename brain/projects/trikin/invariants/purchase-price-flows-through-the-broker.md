---
type: Invariant
title: The Purchase Price goes to the Broker's settlement account, never to an agent
description: The purchaser buys the Agent's Fee from the Broker and pays the Broker, who then pays its agent. Paying an agent directly is an unlicensed-brokerage-compensation violation, so the schema gives it nowhere to happen.
tags: [fintech, receivables, compliance, licensing, schema-design]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-02-13
relations:
  - { kind: instance-of, target: /meta/practices/make-misuse-unrepresentable.md }
not:
  - term: "fundings.agentId / payoutToAgent() / \"we advance the agent\""
    why: "the Purchaser is not a licensed real estate broker and may not compensate an agent for brokerage services (BMA Art. XIII); the marketing knowledge base describes it this way and is wrong"
    instead: "fundings.destinationBankAccountId, constrained to a bank_accounts row with ownerType='broker' and purpose='broker_settlement'"
sources:
  - id: bma
    resource: "Broker Master Commission Purchase Program Agreement §3.6-3.7, §13.3 (Drive 11KQNwyDixIUhu4rxIiEjK2bxsK5IT-xw)"
    title: "Purchaser transmits the Purchase Price to Broker's designated settlement account; Broker pays the Agent through its ordinary payment process and shall not characterize it as a loan; Purchaser shall not pay compensation directly to any Agent for Brokerage Services"
  - id: charter
    resource: projects/trikin/docs/trikin-capital/invariants.md
    title: "the invariant as written into the repo, with its enforcement"
---

# The rule

The money path: the Property Manager pays the Broker a Commission; the Purchaser
buys the Agent's Fee **from the Broker** and wires the Purchase Price to the
Broker's settlement account; the **Broker** pays the agent through its ordinary
payout process; later the Broker remits the assigned proceeds back to the Purchaser.

The Purchaser and the agent never exchange money in either direction.

Enforced by making it unrepresentable rather than by review. The `fundings` table
has **no agent column at all**, its destination is a `bank_accounts` row constrained
to `ownerType = 'broker'` and `purpose = 'broker_settlement'`, and a CHECK
constraint prevents an agent-owned bank account from existing in the first place.
That is
[make misuse unrepresentable](../../../meta/practices/make-misuse-unrepresentable.md)
applied to a licensing rule.

It also constrains copy. No user-visible string may say the purchaser advances,
lends, funds, or pays the agent.

# Why it matters

This is a licensing violation. The Purchaser is not a licensed real estate broker,
and compensating an agent for brokerage services is exactly what it may not do.

It matters specifically because the plausible wrong version is written down in the
company's own marketing knowledge base: "Trikin Capital advances agents a portion of
their earned commission." An agent handed both documents and no ranking will build
the illegal one, because it is the simpler design and it is stated in prose rather
than buried in Article XIII.

# Evidence

BMA §3.6: "Purchaser shall transmit the Purchase Price stated in the applicable
Purchase Confirmation to Broker's designated settlement account."

BMA §3.7: "Broker shall pay the Purchase Price to the participating Agent through
Broker's ordinary payment process. Broker shall not characterize such payment as a
loan from Broker or from Purchaser."

BMA §13.3: "Purchaser is not acting as a real estate broker and shall not pay
compensation directly to any Agent for the performance of Brokerage Services."
