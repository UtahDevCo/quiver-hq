---
type: Observation
title: A forbidden input must be rejected in the parser, not only omitted from the type
description: Omitting a field from a type stops code from passing it; it does nothing when the value arrives as stored JSON edited outside the codebase. Reject the key by name where the JSON is parsed, with the reason in the error.
kind: practice
proposed_layer: meta
observed_in: trikin
tags: [validation, types, config, compliance, parsing]
generated: { by: claude/opus-5, at: 2026-08-07T18:57:02Z }
status: draft
not:
  - term: "the field isn't in the input type, so it can't be used"
    why: "true for call sites the compiler sees; a definition loaded from a database column or a config file is unknown at the boundary and a permissive parser passes the extra key straight through"
    instead: "enumerate the forbidden keys where the stored value is parsed, throw naming the key found, and put the reason in the error message"
sources:
  - id: guard
    resource: projects/trikin/web/src/lib/underwriting/policy.ts
    title: "TIME_KEYED_FIELDS and parsePricingTier (trikin commit c657ba0)"
    last_modified: 2026-08-07
  - id: rationale
    resource: projects/trikin/web/docs/trikin-capital/model.md
    title: "model.md — Pricing is flat per risk tier, never per day"
    last_modified: 2026-08-07
---

# Observation

When a rule forbids an input rather than merely not needing it, leaving the field
out of the type covers only the paths the compiler checks. Anything reaching the
same computation as parsed JSON, a database column, or a config file arrives as
`unknown` and gets structurally narrowed, and structural narrowing ignores extra
keys. Enumerate the forbidden names at the parse boundary and reject on sight:

```ts
const timeKeyed = Object.keys(fields).filter((key) => TIME_KEYED_FIELDS.includes(key));

if (timeKeyed.length > 0) {
  throw new PolicyDefinitionError(
    `pricing tier ${index} is keyed on ${timeKeyed.join(", ")}; a discount that varies ` +
      `with time is interest, and duration is an eligibility gate rather than a price input`
  );
}
```

Two properties make it worth the awkwardness of a name list. The error names the
key that was found, so whoever wrote it knows what to remove. The message carries
the reason and a pointer to the document holding the argument, so removing the
guard is visibly a decision rather than a cleanup.

# Why it matters

The type-only version fails exactly when the rule is being broken by someone
outside the codebase, which is the case the rule exists for. In trikin, pricing
matrices are stored JSON because the governing document permits automated approval
only over Member-approved rules, and a rule living in source cannot be
Member-approved. So the people most able to add a forbidden key are the ones who
never see the TypeScript.

The name list is deliberately incomplete and cannot be otherwise. It is a
speed bump aimed at the obvious spellings, not a proof. Its value is that adding
`daysOutstanding` to a matrix fails loudly at parse time with the reason attached,
instead of silently repricing every deal.

This is `make-misuse-unrepresentable` applied where the type system stops: the
representation is JSON, so the parser is the only place the constraint can live.

# Evidence

trikin buys commission receivables, and whether the transaction is a true sale or
a disguised loan turns partly on whether the discount varies with duration. A
discount that grows with elapsed time is interest. `docs/trikin-capital/model.md`
records the argument, with a yield table showing the same flat 10% reading as 135%
annualised at 30 days and 45% at 90.

The guard is in two layers. `PricingFacts` carries `brokerId` and
`assignedPaymentRightCents` and no date field, so no call site can pass a duration.
`TIME_KEYED_FIELDS` lists thirteen spellings (`days`, `expectedDaysToPayment`,
`elapsedDays`, `dailyRateBps`, `apr`, and so on) and `parsePricingTier` throws on
any of them, so no stored matrix can either. The same rule set defines
`maxExpectedDaysToPayment`, where duration is legitimate, because there it gates
eligibility rather than setting a price. Tests cover four of the spellings.
