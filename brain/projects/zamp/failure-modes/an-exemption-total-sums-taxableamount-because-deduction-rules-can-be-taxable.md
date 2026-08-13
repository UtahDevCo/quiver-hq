---
type: Failure Mode
title: An exemption total sums taxableAmount because a deduction-coded rule can be TAXABLE
description: minZero(taxableAmount).plus(minZero(nontaxableAmount)) is load-bearing, and TN Schedule A deduction 1 (food) is TAXABLE at 4%. Copying the idiom to a schedule whose rule is EXEMPT invites a taxed base being reported as exempt.
tags: [tax-engine, summaries, aggregation, correctness, filing]
generated: { by: claude/opus-5, at: 2026-07-30T16:37:53Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "treating the taxableAmount term as harmless boilerplate when copying the idiom to a new schedule"
    why: "it exists to catch reduced-rate deductions like TN food at 4%; on a schedule whose rule is EXEMPT it is dormant, and it silently activates if the rule is ever authored TAXABLE"
    instead: "decide per schedule: sum nontaxableAmount only when the rule is EXEMPT/NONTAXABLE by construction, or constrain the rule type and say so"
sources:
  - { id: idiom, resource: "projects/zamp/domains/summaries/src/states/tennessee/summary.ts", title: "generateScheduleA getDeductionAmount and generateScheduleG both use minZero(taxable).plus(minZero(nontaxable))" }
  - { id: food-rule, resource: "projects/zamp/domains/tax/data/data/TN/TN-Rule.csv", title: "TN Schedule A deduction 1 (food) is type TAXABLE at rate 0.040000" }
  - { id: bucketing, resource: "projects/zamp/domains/tax/src/calculate/taxes.ts:265-281", title: "TAXABLE routes the base into taxableAmount and computes taxDue" }
  - { id: no-g-rules, resource: "projects/zamp/domains/tax/data/data", title: "zero rules with sectionCode G across all 53 *-Rule.csv files as of 2026-07-30" }
  - { id: pr, resource: "https://github.com/zamptax/zamp/pull/9344#discussion_r3684493135", title: "PR 9344, question raised to the FRI author rather than resolved by guessing" }
---

# The trap

The repo-wide idiom for an exemption or deduction total is:

```ts
minZero(d._sum.taxableAmount).plus(minZero(d._sum.nontaxableAmount)).round()
```

The `taxableAmount` term looks like belt-and-braces. It is required. A rule carrying a
`deductionCode` is free to be `type: TAXABLE`, and in Tennessee one is: Schedule A
deduction 1 (food) is `('TAXABLE', 'A', '1', '0.040000')`. Food is reported on the
exemptions schedule while still being taxed, at a reduced 4%, so the engine puts its
base in `taxableAmount`. Drop that term and the food line reads zero.

The hazard appears when the idiom is copied to a schedule whose rule is
`NONTAXABLE`/`EXEMPT`. There the `taxableAmount` term contributes nothing, which reads
as confirmation that it is inert. It is dormant, and it activates the moment someone
authors that schedule's rule as `TAXABLE`, at which point a taxed base is reported as
exempt sales and inflates the exemption total.

TN Schedule G is exactly this shape. As of 2026-07-30 no rule with `sectionCode: "G"`
exists in any of the 53 `*-Rule.csv` files, so Schedule G rows only ever arrive with
`nontaxableAmount` set, and the formula is correct by accident of the data.

# Why it matters

Both readings of the idiom look right, and the data decides which one you got. On
Schedule A the `taxableAmount` term is the only thing making the food line non-zero.
On Schedule G it is a latent path waiting on a CSV row nobody has written yet.

The failure is quiet in the worst way: it inflates an exemptions total, which feeds
gross sales, which is a number on a filed return. No exception, no failing test, and
the person who triggers it is whoever authors the rule months later, with no reason to
suspect a summary formula.

Make the rule type an explicit precondition of the aggregation rather than an
assumption. Either constrain the rule to `NONTAXABLE`/`EXEMPT` and sum
`nontaxableAmount` alone, or keep the two-bucket sum and write down that a `TAXABLE`
rule on this schedule would be a defect.

# Evidence

Parsed `domains/tax/data/data/TN/TN-Rule.csv` (2912 rules) grouping by
`(type, sectionCode, deductionCode, taxRate)` over rules with a non-empty
`deductionCode`:

```
  954  ('NONTAXABLE', 'B', '4', '0.000000')
    2  ('NONTAXABLE', 'A', '2', '0.000000')
    2  ('TAXABLE',    'A', '1', '0.040000')   <- food, reported as a deduction, still taxed
    2  ('TAXABLE',    'C', '11', '0.025000')
    2  ('TAXABLE',    'C', '1',  '0.027500')
```

`sectionCode` values present in TN: `B`, `A`, `I`, `''`, `C`, `D`. No `G`. A sweep of
all `domains/tax/data/data/*/*-Rule.csv` for `sectionCode == "G"` returned 0 rows.

Rather than silently pick a side, the open question went onto the PR thread for the FRI
author to answer.

# Related

The third bucket in that idiom is settled by
[exemptamount-is-always-zero](../invariants/exemptamount-is-always-zero-exempt-sales-live-in-nontaxableamount.md):
`exemptAmount` is not a candidate term, because nothing writes it. The clamping is
covered by [minzero-clamps-each-bucket](minzero-clamps-each-bucket-before-the-sum-so-refunds-do-not-net.md).
