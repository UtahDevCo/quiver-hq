---
type: Observation
title: The verified amount comes from the payor's acknowledgment, not the claimant's calculation
description: The brokerage's computed commission and the property manager's acknowledged commission are different numbers that routinely disagree. Store both with provenance; underwrite the payor's.
kind: invariant
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [fintech, verification, provenance, underwriting, schema-design]
status: draft
not:
  - term: "commissionCents — one column, populated from whichever source arrived"
    why: "the two sources disagree by real money and the row cannot say which one it holds, so pricing silently uses whatever was written last"
    instead: "claimedCommissionCents + acknowledgedCommissionCents + commissionAmountSource; pricing reads the acknowledged figure and refuses a broker_claim-only row"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: thread, resource: "Drive — Invoicing proof to pull from, screenshots 14nnYyA8EP5zTVlbgaP2_jlVPQd3K_g35 / 10yAYnMJ1H10YxmJ6euPqJSDp22CGUZ_8", title: "brokerage claims $1,996.50; the property's leasing professional replies \"the commission amount it'll be $1,782.59\"" }
  - { id: doa, resource: "Delegation of Authority and Initial Underwriting Policy §4, §7", title: "the amount, payor, and payment conditions must be reasonably verifiable; verification should use contact information obtained independently of the applicant" }
---

# Observation

The only real verification thread available for this product shows the pattern in
one exchange. The brokerage emails the property a commission confirmation — client,
property, unit, move-in date, rent $1,331, rate `%150`, total **$1,996.50**. The
property's leasing professional replies: "The only thing that needs to be update is
the commission amount it'll be **$1,782.59**."

An 11% disagreement, in the first example, from the party who actually pays.

So the claimed figure and the acknowledged figure are **two columns**, plus a
`commissionAmountSource` discriminator (`broker_claim` |
`payor_acknowledgment` | `independent_verification`). Underwriting reads the
acknowledged one, and a transaction carrying only a claim is not underwritable.

The provenance of the *contact* is a separate column from the provenance of the
*amount*, and is also load-bearing here: the policy wants verification using
contact details obtained independently of the applicant, while the contract forbids
the purchaser from contacting the property manager at all. In the pilot the
acknowledgment therefore arrives broker-forwarded — applicant-supplied — which must
route to human review rather than auto-approve until counsel resolves it.

# Why it matters

Collapsing the two into one column loses the disagreement, and the disagreement is
the signal. With one column the row cannot tell you whether it holds a verified
number or a hopeful one, so pricing and the resulting signed instrument use whatever
was written most recently — and a purchase price computed off the claim is a price
the payor will not fund.

Recording both also gives the thing this business actually needs to sell later:
per-brokerage evidence of how accurate their claims are.

# Evidence

Note in passing from the same thread that the rate is `%150` — malformed, and a
percentage of *one month's rent*, so legitimately above 100%. $1,331 × 150% =
$1,996.50 confirms the reading. Any code assuming a rate at or below 100%, or an
annualised base, computes a wrong number with no error.
