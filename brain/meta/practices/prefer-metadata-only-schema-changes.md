---
type: Practice
title: Weigh migration friction as a design input; prefer metadata-only schema changes
description: Migration cost is a design input, not a downstream detail. Append enum values rather than inserting them — appending is metadata-only, inserting rewrites every row.
tags: [database, migrations, schema-design, enums, mysql]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "inserting a new enum value next to its semantic siblings, mid-list"
    why: "shifts the stored ordinal of every later value, turning a metadata-only ALTER into a full table rewrite"
    instead: "append the value at the END of the enum, even when that breaks semantic grouping, with a one-line comment so it isn't 'tidied' back into the group"
  - term: "choosing the cleanest logical schema and treating the migration as an implementation detail"
    why: "a column reorder, type change, or NOT NULL without a default is a locking rewrite; on a large or sharded table that cost dominates the design"
    instead: "prefer additive forms — nullable column, new table, appended enum value — and use expand-migrate-contract when a rewrite is unavoidable"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Treat migration friction as a first-class cost'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

When choosing a schema shape, weigh the cost of the migration that gets you there
alongside the cleanliness of the result. Prefer changes that are metadata-only or
online-safe over ones that force a table rewrite.

The sharpest instance is enum ordering. Appending a value is a metadata-only
`ALTER` — no existing value's stored ordinal changes. Inserting one mid-list shifts
the ordinals of everything after it and rewrites the table. So append, even when
appending breaks the enum's semantic grouping:

```prisma
enum ImportSessionFailureReason {
  // ...existing values, in their existing order...
  AMOUNT_SANITY // Kept last (out of its group) so the migration is a metadata-only append, not a row-rewriting reorder.
}
```

Keep the generated migration's `MODIFY ... ENUM(...)` list in that same order.

More generally: prefer additive forms over rewriting or locking ones. And check
whether an existing column, an existing shape, or a non-persisted guard already
achieves the goal — sometimes the lowest-friction migration is none.

# Why the comment is load-bearing

An out-of-group enum value looks like carelessness. The next engineer — or an agent
asked to tidy the schema — will move it back beside its siblings and silently
reintroduce a full table rewrite on a large table. Nothing in the diff will say
what it cost.

This is the rare case where a comment is mandatory rather than noise: the ordering
encodes a migration property that is invisible from the code, so the reason has to
live next to the value. It is a deliberate carve-out from
[minimal-comments](minimal-comments.md).

# Scope

Recorded from a MySQL-family database (Vitess/PlanetScale). Enum ordinal behavior
is engine-specific — Postgres enums add values without rewriting, so the enum half
narrows there. The general principle, that migration cost is a design input rather
than a downstream detail, is engine-independent.
