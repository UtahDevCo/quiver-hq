---
type: Practice
title: Store money as integer minor units, with the unit in the column name
description: Six monetary columns in a production schema were declared `real`, a type that cannot hold $1,782.59 exactly and drifts under addition.
tags: [schema-design, money, correctness, sqlite, drizzle]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
sources:
  - id: schema
    resource: projects/trikin/web/src/db/schema.ts:192-221
    title: "advertisedRent, applicationFee, securityDeposit, totalCommission, trikinCommission, propertyCommission all declared real()"
    last_modified: 2026-07-30
not:
  - term: "real(\"totalCommission\")"
    why: "$1,782.59 has no exact binary float representation; sums of many such values drift, and the drift lands on a legal document"
    instead: "integer(\"totalCommissionCents\")"
  - term: "integer(\"totalCommission\")"
    why: "an unsuffixed integer money column is the next bug, because nothing at the call site distinguishes 1995 dollars from 1995 cents"
    instead: "put the unit in the name: `…Cents` for money, `…Bps` for rates"
  - term: "a float percentage such as 0.15"
    why: "the shape invites clamping to 1.0, which silently truncates a legitimate 150% rate"
    instead: "integer basis points, named `…Bps`"
---

# The practice

Money is an integer in minor units, and the column name carries the unit:
`totalCommissionCents`. Rates are integer basis points, named `…Bps`. All
arithmetic and all formatting go through one module so rounding happens in one
testable place.

Binary floating point cannot represent most two-decimal values, so a `real` column
stores a number that is already not the amount, and repeated addition compounds the
difference.

# Why it bites late

Nothing fails and no test goes red. A float renders to two decimals convincingly, so
the dashboard looks right. It shows up as reconciliation off by a few cents, then as
a total that does not tie to the sum of its parts, by which point the number is in
reports, invoices, and, in a receivables business, signed instruments stating a
purchase price.

Fixing the column type afterwards does not recover the precision already lost in the
stored rows.

# The check

Assert at the schema level rather than relying on vigilance: no `real(` column whose
name matches a monetary pattern, and every `…Cents` column declared `integer(`.

# Evidence

trikin's `web/src/db/schema.ts` declared six monetary columns as `real`:

```ts
advertisedRent: real("advertisedRent"),
totalCommission: real("totalCommission"),
trikinCommission: real("trikinCommission"),
propertyCommission: real("propertyCommission"),
```

A verification email in the same business quotes a commission of `$1,782.59`, one of
the many values that column cannot hold exactly.
