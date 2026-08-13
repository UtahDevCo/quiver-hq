---
type: Failure Mode
title: A writeback field list is a disclosure decision
description: Fields you push into a counterparty's system are visible to everyone with a seat in it. Ask who reads the record, not just what the integration needs.
tags: [integration, privacy, confidentiality, crm]
generated: { by: claude/opus-5, at: 2026-08-06T14:28:59Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "include every figure the sending side already knows, so the record is complete"
    why: "the receiving system has its own readers, and a field pushed to a counterparty is published to everyone with a seat in their CRM"
    instead: "include the minimum the counterparty needs to take the action, then justify each remaining field against who can read it"
sources:
  - id: counterparty-spec
    resource: email from josh@trikin.co, 2026-08-05 14:01, forwarded to the Oakland Creek HubSpot team
    title: "Rail 2 required writeback fields, including Amount Paid to Agent and Agent Remaining Balance"
    last_modified: 2026-08-05
  - id: built-notice
    resource: projects/trikin/docs/trikin-capital/integration-rails.md
    title: "Rail 2: the Assignment Update File, field table"
    last_modified: 2026-08-05
---

# The trap

When designing what your system writes back into a counterparty's system, decide
each field on **who can read the receiving record**, not on what the integration is
capable of sending. A field pushed into a CRM is readable by every seat in that CRM,
indefinitely, and typically without an audit trail on your side.

The test to apply per field: what action does the counterparty take with it? If
none, it is disclosure rather than integration.

# Why it matters

An integration spec for Trikin's assignment writeback listed, among the required
fields a brokerage's CRM should carry:

| Field | Example |
|---|---|
| Amount Paid to Agent | $1,260 |
| Agent Remaining Balance | $0 |

The brokerage needs two things to redirect a payment: the assigned amount ($1,400)
and the payee. `Amount Paid to Agent` is the discounted advance, so it discloses to
an agent's employer that the agent took early payment and on what terms. Nobody at
the brokerage acts on it.

The asymmetry is what makes this a failure mode rather than a preference. Sending
the field is one line of code and is irreversible in practice, because the value now
lives in someone else's database under their retention policy. Omitting it costs
nothing, since no workflow on the receiving side consumes it.

# What the repo does

The built notice carries the assigned amount and the payee and nothing about the
advance (`integration-rails.md`, Rail 2 field table): `trikinDealId`,
`brokerDealIdentifier`, `assignedAmountCents`, `payeeName`, `payeeReference`,
`assignmentEffectiveAt`, `assignmentDocumentUrl`, `agentAcknowledgedAt`.

Every figure there is copied from the accepted purchase confirmation rather than a
live row, so the amount a brokerage is told to redirect is the amount the agent
signed away. The advance amount is not one of the things the agent signed away to
the brokerage.

# The evidence here is thin

There is no measurement behind this. What exists is one spec email listing two
fields and one field table in the repo that omits them. Nobody has observed a
brokerage reading `Amount Paid to Agent`, and no agent has complained, because the
rail has not run in production.

So the claim being made is about design intent: the shipped field list is narrower
than the requested one, and the reason recorded for the difference is who can read
the receiving record. Treat the reasoning as a checklist item for the next
integration rather than as a confirmed harm. What would firm it up: a second rail
where a requested field was cut for the same reason, or an actual reader of a
counterparty CRM confirming the field was visible to agents' colleagues.
