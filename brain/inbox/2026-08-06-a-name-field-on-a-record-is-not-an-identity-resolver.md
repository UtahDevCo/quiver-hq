---
type: Observation
title: Test a CRM name field for one-to-one before using it to resolve an id
description: A name column that sits next to an owner id looks like a free way to resolve that id, until you count how many ids carry two names and how many names carry two ids.
kind: practice
proposed_layer: meta
tags: [integration, crm, data-quality, identity]
generated: { by: claude/opus-5, at: 2026-08-06T21:35:02Z }
status: draft
sources:
  - id: evidence
    resource: projects/trikin/web/bin/dev/load-oakland-creek.ts
    title: buildRoster, and the reason it leaves some agents unnamed
    last_modified: 2026-08-06
  - id: commit
    resource: projects/trikin
    title: b0d1af6 feat(trikin) load Oakland Creek's live deals into a local fixture
    last_modified: 2026-08-06
---

# Observation

When a permission you want is denied, a name field already present on the records is the
obvious substitute. HubSpot refused `crm.objects.owners.read`, and every deal carried both
`hubspot_owner_id` and `invoiced_deal_owner`, a plain-text person's name. It reads exactly
like the lookup table the missing scope would have returned.

Before using it that way, measure the mapping in both directions across every record you
can reach, not a sample:

- how many ids map to more than one name
- how many names map to more than one id

Over 5,580 deals: 17 of 180 owner ids carried more than one name, and 16 names appeared
under more than one id. One id carried six names, one of them `Oakland Creek Admin`, which
is a shared account rather than a person. The fields describe two different roles, the deal
owner and the invoicing rep, and they agree often enough that a small sample looks clean.

Where the mapping is not one-to-one, leave the value empty rather than taking the majority.
An unnamed row is a visible gap; a plausible wrong name is not, and in this case the name
is what prints on the payee line of an assignment notice.

# Why it matters

91% correct is the worst possible accuracy for identity data. It is high enough to pass a
spot check and low enough that roughly one agent in eleven has someone else's name attached
to their payment instruction. Nothing downstream can detect it, because a name is free text
and every value looks valid.

The same measurement also produced something useful to ask for: the 17 ambiguous ids are
concrete evidence for the access request, rather than a general plea for the scope.

# Evidence

```
deals pulled: 5580
invoiced_deal_owner fill rate: 4162/5580
distinct owner ids with a name: 180
owner ids mapping to MORE THAN ONE name: 17
   49399733 ['Angie Navo', 'Jeannie Adams', 'Jesse Clifford', 'Joshua Levy',
             'Nick Marchiano', 'Oakland Creek Admin']
   218400433 ['Drew Banazek', 'Gina Pettenon', 'Kavin Hanner']
names mapping to more than one owner id: 16
   Nick Marchiano ['178827082', '49399733', '566291294']
   Zane Nguyen ['126218352', '375127159']
```

What the loader does with it:

```ts
const certain = names?.size === 1;
legalName: certain ? [...names][0] : `UNCONFIRMED — hubspot_owner_id ${identifier}`,
```

32 of 33 agents got a name. The one that did not is reported in the run summary rather
than filled in.

not:
  - term: "the name field is populated on most records, so it can resolve the id"
    why: "fill rate answers whether a value is present, not whether the mapping is one-to-one"
    instead: "count ids-with-many-names and names-with-many-ids across every record, then decide"
  - term: "take the most common name for an ambiguous id"
    why: "it converts a detectable gap into an undetectable wrong value on a payment instruction"
    instead: "leave it empty, mark it unconfirmed, and report the count"
