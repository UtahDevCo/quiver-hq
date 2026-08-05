---
type: Observation
title: Treat migration friction as a first-class design cost, and append enum values rather than inserting them
description: Schema shape should be chosen partly on migration cost; appending an enum value is a metadata-only ALTER while inserting one mid-list shifts stored ordinals and forces a full table rebuild.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [database, migrations, schema-design, enums, prisma, mysql, vitess]
status: draft
not:
  - term: "inserting a new enum value next to its semantic siblings, mid-list"
    why: "shifts the stored ordinal of every later value, turning a metadata-only ALTER into a full table rewrite"
    instead: "append the value at the END of the enum, even when that breaks semantic grouping, with a one-line comment so it isn't 'tidied' back into the group"
  - term: "choosing the cleanest logical schema and treating the migration as a downstream implementation detail"
    why: "on a sharded/online DB a column reorder, type change, or NOT NULL-without-default is a locking rewrite; the cost is a design input, not a detail"
    instead: "prefer additive forms (nullable column, new table, appended enum value); use expand-migrate-contract for unavoidable rewrites"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Treat migration friction as a first-class cost; prefer metadata-only schema changes'" }
  - { id: schema, resource: projects/zamp/utils/db/prisma/schema/, title: "Prisma schema; app data runs on Vitess (vttestserver locally, PlanetScale in stage/prod)" }
---

# Observation

When choosing a schema shape, weigh the cost of the migration that gets you there
alongside the logical cleanliness of the result. Prefer changes that are
metadata-only or online-safe over ones that force a table rewrite.

The sharpest instance is enum ordering. Adding a value at the **end** of an enum is
a metadata-only `ALTER` — no existing value's stored ordinal changes. Inserting one
mid-list shifts the ordinals of every value after it and forces a full table
rebuild. So append, even when appending breaks the enum's semantic grouping, and
leave a one-line comment explaining why it sits out of place:

```prisma
enum ImportSessionFailureReason {
  // ...existing values, in their existing order...
  AMOUNT_SANITY // Kept last (out of its group) so the migration is a metadata-only append, not a row-rewriting reorder.
}
```

Keep the generated migration's `MODIFY ... ENUM(...)` list in that same order.

More generally: prefer additive forms (a new nullable column, a new table, an
appended enum value) over rewriting or locking ones (column reorder, type change,
`NOT NULL` without a default). For unavoidable rewrites, use
expand-migrate-contract. And sometimes the lowest-friction migration is none —
check whether an existing column, an existing shape, or a non-persisted guard
already achieves the goal before adding a column or an enum value at all.

# Why it matters

The comment is load-bearing, which is what makes this worth recording rather than
leaving as tribal knowledge. An out-of-group enum value looks like sloppiness, so
the next engineer — or an agent asked to tidy the schema — will move it back into
its semantic group and silently reintroduce a full table rewrite on a large,
sharded table. The reason has to live next to the value.

The general principle matters because migration cost is invisible at design time
and extremely visible at deploy time.

# Evidence

zamp's app data runs on Vitess (`vttestserver` locally, PlanetScale in stage and
prod), where table rewrites on sharded tables are the expensive case. The enum
guidance is recorded in `patterns.md` with the `AMOUNT_SANITY` comment as the
worked example.

This is proposed as `meta` rather than project-layer because nothing about it is
zamp-specific: MySQL enum ordinals behave this way generally, and
"weigh migration cost as a design input" applies to any repo with a live database.
Corroboration from a second repo would strengthen it — as written the evidence is
from zamp only.
