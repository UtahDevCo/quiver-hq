---
type: Observation
title: RuleType.ADJUSTED is dead enum surface behaving as an alias for TAXABLE
description: ADJUSTED appears in 0 of 53 rule CSVs and the engine handles it in the same branch as TAXABLE, so it reads as a distinct tax treatment that does not exist.
kind: invariant
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [tax-engine, prisma, dead-code, make-misuse-unrepresentable]
status: draft
not:
  - term: "reasoning about ADJUSTED as a separate tax treatment when auditing bucket logic"
    why: "it has no rows and no documented semantics; treating it as real invents a case that cannot occur"
    instead: "read it as TAXABLE, and either delete it or document what would justify it"
generated: { by: claude/opus-5, at: 2026-07-30T16:37:53Z }
sources:
  - { id: enum, resource: "projects/zamp/utils/db/prisma/schema/shared.prisma:773-779", title: "RuleType enum: TAXABLE, NONTAXABLE, ADJUSTED, EXCLUDED, EXEMPT" }
  - { id: only-use, resource: "projects/zamp/domains/tax/src/calculate/taxes.ts:268-271", title: "the sole reference, in the same branch as TAXABLE" }
  - { id: sweep, resource: "projects/zamp/domains/tax/data/data", title: "grep for ADJUSTED across all 53 *-Rule.csv files returned 0 files as of 2026-07-30" }
---

# Observation

`RuleType` declares five members. `ADJUSTED` has one reference in the codebase, and it
shares a branch with `TAXABLE`:

```ts
} else if (rule.type === RuleType.TAXABLE || rule.type === RuleType.ADJUSTED) {
  taxableAmount = taxableBase;
  taxDue = taxableBase.times(rule.taxRate);
}
```

No rule data uses it. A grep across all 53 `domains/tax/data/data/*/*-Rule.csv` files
matched 0 files. Nothing documents what an adjusted rule would mean or when to author
one.

# Why it matters

The cost lands on anyone auditing how amounts reach their buckets. A five-member enum
where one member is an undocumented alias for another reads as four tax treatments plus
a subtlety worth working out. The subtlety is absent, so the time spent looking for it
is wasted, and any conclusion drawn about ADJUSTED-specific behaviour describes a case
that cannot arise.

This is the situation `make-misuse-unrepresentable` addresses: an option nobody selects
should leave the toolchain rather than sit in the enum accumulating speculation. Either
delete `ADJUSTED` and let the type system reject it, or record the case it was reserved
for so the next reader stops guessing.

# Evidence

Sweep on 2026-07-30 against the checked-in rule data:

```
files containing ADJUSTED: 0 of 53   (domains/tax/data/data/*/*-Rule.csv)
```

Type distribution for Tennessee (2912 rules), showing the three members that occur:

```
TAXABLE 1942, NONTAXABLE 968, EXCLUDED 2
```

Noted as an aside on
https://github.com/zamptax/zamp/pull/9344#discussion_r3684493135 while tracing which
amount bucket an exemption lands in.
