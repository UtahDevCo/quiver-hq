---
type: Observation
title: Map integration fields by fill rate and arithmetic, not by name
description: A counterparty's field names lie about what they hold. Before mapping one onto your schema, measure how often it is populated at the trigger stage and test the arithmetic it claims.
kind: practice
proposed_layer: meta
tags: [integration, crm, data-quality, schema, underwriting]
generated: { by: claude/opus-5, at: 2026-08-06T14:59:39Z }
status: draft
sources:
  - id: probe
    resource: HubSpot portal 8092761, deal stages 11779171 and 11779172, read-only probe 2026-08-06
    title: "134 deals sampled across two invoicing stages, per-property fill rates and relation tests"
    last_modified: 2026-08-06
  - id: schema
    resource: projects/trikin/web/src/lib/intake/deal-packet.schema.ts
    title: Standard Deal File required fields
    last_modified: 2026-08-05
not:
  - term: "map the counterparty's field to ours because the names line up"
    why: "a field named total_commissions held the agent's share rather than the deal total, in 100 of 100 rows, and a commission_rate column reproduced no figure in the data"
    instead: "for each candidate, measure fill rate at the exact trigger stage and test every arithmetic relation the name implies; map only what survives both"
---

# Observation

When building an intake contract against someone else's system, resolve each field with
two measurements before writing the mapping:

1. **Fill rate at the trigger stage**, not across the whole object. A field populated
   90% of the time overall can be 0% at the moment your integration fires.
2. **The arithmetic the name claims.** If a field is called a total, test that it equals
   the sum. If it is called a rate, test that applying it reproduces the derived figure.

Map only what survives both. Report the fields that survive neither as missing data the
counterparty has to supply, rather than as a mapping you will guess at.

# Why it matters

Reading a property list and matching names produces a mapping that typecheck-passes,
deploys, and is wrong on live data. The wrongness is silent because every field is
populated with a plausible number.

Three specific ways it failed on a real portal:

- `total_commissions` equalled the agent's referral share, not the deal total, in
  **100/100** rows. Pricing off it would have underwritten against the wrong base.
- `commission_rate` reproduced nothing: `amount * commission_rate / 100 == referral`
  held in **0/100**. A sibling text column read "150%" on a row where the numeric column
  read 100.
- The figure the whole product prices off was **not derivable at all**. The best
  candidate relation held in 45/100 and no other beat 3/100. Only a weak bound survived
  (`take_home <= referral`, 100/100), which means the number has to be accepted as
  asserted and cannot be cross-checked.

The fill-rate half moved a design decision. Two adjacent pipeline stages looked
interchangeable as a trigger, and the invoice number and invoice date were populated
**0/29** at the earlier one and **105/105** and **104/105** at the later one. A schema
requiring an invoice date can only fire at the later stage. Nothing in the field list
says that; only the fill rate does.

# Evidence

Relation tests over 100 deals at one stage:

```
100/100  total_commissions == reps_referral
100/100  reps_referral == amount * (1 - gross_margin)
 45/100  take_home == amount * gross_margin
  3/100  take_home == referral * gross_margin
100/100  take_home <= referral
  0/100  amount * commission_rate / 100 == referral
```

Fill rates for four fields the schema marked required, at the trigger stage, n=105:

```
legal_name                       0/105
building_address                 0/105
first_payment_date               0/105
latest_docusign_download_link    0/105
```

All four had names implying they were populated, and a name-based mapping would have
declared the integration ready. The correct output of the exercise was four questions for
the counterparty.

A second-order find from the same probe: a boolean named `deal_is_verified` was set on
1/105 rows. It had been a candidate for satisfying a verification requirement. A fill
rate that low means the field is aspirational, and building a control on it would have
produced a control that never fires.
