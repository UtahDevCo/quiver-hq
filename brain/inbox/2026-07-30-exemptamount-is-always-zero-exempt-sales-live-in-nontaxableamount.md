---
type: Observation
title: TransactionTax.exemptAmount is always zero; exempt sales live in nontaxableAmount
description: The tax engine hardcodes exemptAmount to 0 at its only write site and routes RuleType.EXEMPT into nontaxableAmount. Summing exemptAmount is a provable no-op.
kind: invariant
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [tax-engine, prisma, aggregation, summaries, correctness]
status: draft
not:
  - term: "_sum: { taxableAmount: true, nontaxableAmount: true, exemptAmount: true }"
    why: "exemptAmount is structurally 0, so the extra term adds nothing and implies a bucket the engine never fills"
    instead: "_sum: { taxableAmount: true, nontaxableAmount: true } — RuleType.EXEMPT already landed in nontaxableAmount"
  - term: "adding excludedAmount to an exemption column to be thorough"
    why: "excludedAmount is RuleType.EXCLUDED, amounts outside the taxing base; California sums it alone for excluded marketplace sales"
    instead: "leave it out, or query it separately with its own where clause"
generated: { by: claude/opus-5, at: 2026-07-30T16:37:53Z }
sources:
  - { id: hardcode, resource: "projects/zamp/domains/tax/src/calculate/taxes.ts:129", title: "exemptAmount: new Decimal(0) at the only TransactionTax write site" }
  - { id: bucketing, resource: "projects/zamp/domains/tax/src/calculate/taxes.ts:265-281", title: "rule.type to bucket mapping; NONTAXABLE and EXEMPT share the nontaxableAmount branch" }
  - { id: locals, resource: "projects/zamp/domains/tax/src/calculate/taxes.ts:260-262", title: "taxableAmount, nontaxableAmount, excludedAmount are locals; exemptAmount is not" }
  - { id: schema, resource: "projects/zamp/utils/db/prisma/schema/transaction.prisma:214-217", title: "the four Decimal(19,4) amount buckets" }
  - { id: zero-sums, resource: "projects/zamp/domains/summaries/src/states/michigan/summary.ts:64", title: "Michigan sums exemptAmount; canada-british-columbia/summary.ts:120 and the other Canadian provinces do the same" }
  - { id: excluded, resource: "projects/zamp/domains/summaries/src/states/california/summary.ts:503", title: "excludedAmount summed alone, filtered on exceptionCode MARKETPLACE" }
  - { id: pr, resource: "https://github.com/zamptax/zamp/pull/9344#discussion_r3684493135", title: "PR 9344 review thread where this was traced" }
---

# Observation

`TransactionTax` has four amount columns: `taxableAmount`, `nontaxableAmount`,
`exemptAmount`, `excludedAmount`. Only three of them are ever written.

The engine assigns buckets from `rule.type`:

```ts
} else if (rule.type === RuleType.TAXABLE || rule.type === RuleType.ADJUSTED) {
  taxableAmount = taxableBase;
  taxDue = taxableBase.times(rule.taxRate);
} else if (rule.type === RuleType.NONTAXABLE || rule.type === RuleType.EXEMPT) {
  nontaxableAmount = taxableBase;
} else if (rule.type === RuleType.EXCLUDED) {
  excludedAmount = taxableBase;
}
```

`RuleType.EXEMPT` shares a branch with `NONTAXABLE`, so an exempt sale lands in
`nontaxableAmount`. `exemptAmount` gets no branch at all, and at the single site that
builds the row it is written as a literal:

```ts
exemptAmount: new Decimal(0),
```

It is not even a local variable alongside the other three. The only other production
code that touches it is the magic rescale (`calculate/index.ts:627`), which computes
`0 * magic`.

So when you need an exemption total, `taxableAmount` plus `nontaxableAmount` is the
complete set. `excludedAmount` answers a different question: `RuleType.EXCLUDED`
covers amounts outside the taxing base, and California sums it on its own, filtered to
`exceptionCode: "MARKETPLACE"`, for excluded marketplace sales. There is no
`deductionAmount` column; a deduction is identified by `deductionCode` in the `where`.

# Why it matters

The schema advertises four buckets and gives no hint that one is inert, so "should
this also include exempt?" is the first question any reviewer asks. Answering it from
the schema alone produces one of two wrong moves: adding `exemptAmount` (harmless
today, but it encodes a belief that will mislead the next reader) or adding
`excludedAmount` (pulls unrelated money into an exemption column).

Michigan and four Canadian provinces already sum `exemptAmount`. Those aggregates are
adding a structural zero. Nothing fails, which is why the pattern spreads: each new
state copies a neighbour that appeared to handle the case.

The load-bearing consequence is for anyone who later starts populating
`exemptAmount`, whether in a fixture, an importer, or a new engine branch. Every
summary that omits it would silently under-report, and every summary that includes it
would start double-counting against `nontaxableAmount`. Decide which bucket owns
exempt money before writing to the unused one.

# Evidence

A regression test on TN Schedule G pins the behaviour. It stamps a Section G row with
all three of `nontaxableAmount: 10000`, `exemptAmount: 7000`, `excludedAmount: 3000`,
and asserts Column C is `10000`
(`domains/summaries/src/states/tennessee/summary.test.ts`, test
`leaves exemptAmount and excludedAmount out of Column C`, commit `91508f930`).

Confirmed the test can fail: adding `exemptAmount: true` to the `groupBy` `_sum` and
`.plus(minZero(t._sum.exemptAmount))` to the arithmetic produced
`expected "10000" got "17000"`, and that test alone failed out of six.
