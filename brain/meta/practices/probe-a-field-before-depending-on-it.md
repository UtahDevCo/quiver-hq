---
type: Practice
title: Probe a field on real rows before depending on it
description: Count fill rate, uniqueness and the arithmetic a field's name claims, over every row you can reach. One declared field was populated in 0 of 679 rows; another named `total` held the agent's share in 100 of 100.
tags: [data-quality, probes, integration, prompt-engineering, schema, identity]
generated: { by: claude/opus-5, at: 2026-07-31T14:26:40Z }
status: stable
stale_after: 2027-08-13
sources:
  - id: k1-coverage
    resource: projects/k1/web/packages/ai/src/project-query-reasoning.ts
    title: k1 prompt v5 note — coverage measured over 679 stored rows before writing the Box K bullets
    last_modified: 2026-07-31
  - id: k1-fix
    resource: projects/k1 commit 98d32a3
    title: "fix(reasoning): put Box L and Box K in the evidence bundle"
    last_modified: 2026-07-31
  - id: trikin-roster
    resource: projects/trikin/web/bin/dev/load-oakland-creek.ts
    title: buildRoster, and the reason it leaves some agents unnamed
    last_modified: 2026-08-06
  - id: trikin-roster-commit
    resource: projects/trikin
    title: b0d1af6 feat(trikin) load Oakland Creek's live deals into a local fixture
    last_modified: 2026-08-06
  - id: hubspot-probe
    resource: HubSpot portal 8092761, deal stages 11779171 and 11779172, read-only probe 2026-08-06
    title: "134 deals sampled across two invoicing stages, per-property fill rates and relation tests"
    last_modified: 2026-08-06
  - id: deal-packet-schema
    resource: projects/trikin/web/src/lib/intake/deal-packet.schema.ts
    title: Standard Deal File required fields
    last_modified: 2026-08-05
not:
  - term: "reading the type definition to decide what a field holds"
    why: "a schema says what is permitted; an optional field declared in the type can be populated in zero rows"
    instead: "count present and absent per field over every stored row, then write the code against the counts"
  - term: "measuring fill rate across the whole object"
    why: "a field populated 90% of the time overall can be 0% at the stage where your integration fires"
    instead: "measure at the exact trigger stage, and let the stage with the data decide when you fire"
  - term: "the name field is populated on most records, so it can resolve the id beside it"
    why: "fill rate answers whether a value is present, not whether the mapping is one-to-one"
    instead: "count ids-with-many-names and names-with-many-ids across every record, then decide"
  - term: "taking the most common name for an ambiguous id"
    why: "it converts a detectable gap into an undetectable wrong value on a payment instruction"
    instead: "leave it empty, mark it unconfirmed, and report the count"
  - term: "mapping a counterparty field onto yours because the names line up"
    why: "a field named total_commissions held the agent's share rather than the deal total in 100 of 100 rows, and a commission_rate column reproduced no figure in the data"
    instead: "test every arithmetic relation the name implies, and map only what survives"
---

# The practice

Before code, a prompt, or a mapping depends on a field, write a throwaway probe and
run it over every row you can reach. Measure three things and put the counts in the
commit message or beside the code that uses them:

- **Fill rate**, at the exact stage or moment your code runs.
- **Uniqueness**, in both directions, whenever the field is standing in for an
  identifier.
- **The arithmetic the name claims.** If it is called a total, test that it equals
  the sum. If it is called a rate, test that applying it reproduces the derived
  figure.

Map or rely on only what survives. Report what does not as missing data the
counterparty has to supply, and where a value is ambiguous, leave it empty rather
than taking the majority.

Numbers are what make the decision reviewable later. "Field X is usually absent" rots;
"0 of 679" does not.

# Why it matters

A field that is absent, ambiguous, or misnamed produces a confident wrong answer
rather than a refusal, and every value looks valid downstream. An LLM reads a missing
value as zero, which for a running balance books the entire ending figure as a
first-period increase. A name that is 91% correct is the worst possible accuracy for
identity data: high enough to pass a spot check, low enough that one row in eleven
carries someone else's name.

Coverage also changes what the code should say. A field present a quarter of the time
needs the absent case handled as the common path.

# Evidence

## A declared field populated nowhere (k1)

Writing the Box K section of a reasoning prompt, the Section 752 basis adjustment is
the year-over-year movement in partner liabilities, so the natural instruction is
"take the beginning-to-ending movement". The type declares both columns:

```ts
liabilitiesNonrecourseBegin?: number
liabilitiesNonrecourseEnd?: number
```

A probe over every stored row in six tenants:

```
rowsSeen: 679, boxL: 505, method: 168, c704: 0,
nrBegin: 0, nrEnd: 337, qnrfEnd: 337, recBegin: 0, recEnd: 337
```

Zero rows carry a beginning figure. The instruction was rewritten to derive the
movement from the prior year's ending figure, with an explicit "do not treat a
missing beginning as zero". `capitalAccountMethod` at 168/679 turned "state the
basis" from an aside into the common path, and `c704: 0` marked a field worth no
prompt words at all. The probe also showed three of thirteen projects with the field
populated on zero rows, so the fix could not help them, and one pair of liability
categories identical on 337/337 rows, which is a mapping bug or a fixture artifact
and needed flagging either way.

## A name column that is not one-to-one with its id (trikin, HubSpot deal loader)

HubSpot refused `crm.objects.owners.read`, and every deal carried both
`hubspot_owner_id` and `invoiced_deal_owner`, a plain-text person's name. It reads
like the lookup table the missing scope would have returned.

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

One id carries six names, one of which is a shared admin account. The two fields
describe different roles, deal owner and invoicing rep, and they agree often enough
that a small sample looks clean. The loader leaves the ambiguous ones empty:

```ts
const certain = names?.size === 1;
legalName: certain ? [...names][0] : `UNCONFIRMED — hubspot_owner_id ${identifier}`,
```

32 of 33 agents got a name, and the one that did not is reported in the run summary.
The 17 ambiguous ids also became concrete evidence for the access request.

## A field named `total` that is not the total (trikin, HubSpot intake probe)

Relation tests over 100 deals at one stage:

```
100/100  total_commissions == reps_referral
100/100  reps_referral == amount * (1 - gross_margin)
 45/100  take_home == amount * gross_margin
  3/100  take_home == referral * gross_margin
100/100  take_home <= referral
  0/100  amount * commission_rate / 100 == referral
```

`total_commissions` equals the agent's referral share, so pricing off it would have
underwritten against the wrong base. `commission_rate` reproduces nothing, and a
sibling text column read "150%" on a row where the numeric column read 100. The
figure the product prices off was not derivable at all: the best candidate held in
45/100 and no other beat 3/100, leaving only the bound `take_home <= referral` at
100/100, so that number has to be accepted as asserted.

Fill rates for four fields the schema marked required, at the trigger stage, n=105:

```
legal_name                       0/105
building_address                 0/105
first_payment_date               0/105
latest_docusign_download_link    0/105
```

A name-based mapping would have declared the integration ready. The correct output
was four questions for the counterparty.

The fill-rate half also moved a design decision. Two adjacent pipeline stages looked
interchangeable as a trigger, and the invoice number and invoice date were populated
0/29 at the earlier one against 105/105 and 104/105 at the later one. A schema
requiring an invoice date can only fire at the later stage, and only the fill rate
says so. A boolean named `deal_is_verified`, a candidate for satisfying a
verification requirement, was set on 1/105 rows: a control built on it would never
have fired.
