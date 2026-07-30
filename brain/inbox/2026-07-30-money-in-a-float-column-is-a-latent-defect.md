---
type: Observation
title: Money in a float column is a latent defect, not a style choice
description: SQLite `real` (and any binary float) cannot represent most cent values exactly and drifts under addition. Store integer minor units.
kind: practice
proposed_layer: meta
observed_in: trikin
tags: [schema-design, money, correctness, sqlite, drizzle]
status: draft
not:
  - term: "real(\"totalCommission\")"
    why: "$1,782.59 has no exact binary float representation; sums of many such values drift, and the drift lands on a legal document"
    instead: "integer(\"totalCommissionCents\") — and name the column so the unit is impossible to mistake"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: schema, resource: "projects/trikin/web/src/db/schema.ts:192-221", title: "advertisedRent, applicationFee, securityDeposit, totalCommission, trikinCommission, propertyCommission all declared real()" }
---

# Observation

Six monetary columns in a production schema were `real`. Not a rounding-style
preference — binary floating point cannot represent most two-decimal values, so the
stored number is already not the amount, and repeated addition compounds the
difference.

Two rules, and the second is the one that actually prevents recurrence:

1. Money is an **integer** in minor units.
2. The column **name carries the unit** — `totalCommissionCents`, not
   `totalCommission`. An unsuffixed integer money column is the next bug, because
   nothing at the call site distinguishes 1995 dollars from 1995 cents.

Corollary for rates: store integer basis points rather than a float percentage,
named `…Bps`. This matters wherever a rate can exceed 100% — a `0.15`-shaped field
invites clamping that silently truncates a legitimate 150%.

Route all arithmetic and all formatting through one module, so rounding happens in
exactly one place and can be tested.

# Why it matters

There is no error and no failing test. The values look right in the dashboard,
because a float renders to two decimals convincingly. The discrepancy shows up as
reconciliation that is off by a few cents, then as a total that does not tie to a
sum of parts, and by then it is in reports, invoices, and — in a receivables
business — signed instruments stating a purchase price.

Cheap to prevent at schema-writing time, expensive to fix afterwards, because
correcting the column type does not recover the precision already lost in the stored
rows.

Worth a grep-level check rather than vigilance: assert no `real(` column in the
schema whose name matches a monetary pattern, and that every `…Cents` column is
declared `integer(`.

# Evidence

`web/src/db/schema.ts`:

```ts
advertisedRent: real("advertisedRent"),
totalCommission: real("totalCommission"),
trikinCommission: real("trikinCommission"),
propertyCommission: real("propertyCommission"),
```

The real verification email in the same business quotes a commission of
`$1,782.59` — one of the many values this column cannot hold exactly.
