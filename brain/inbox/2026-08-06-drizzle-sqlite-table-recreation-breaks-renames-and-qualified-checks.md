---
type: Observation
title: Read every drizzle-kit SQLite table recreation before it reaches production
description: A generated `__new_table` recreation can read the post-rename column name from the pre-rename table and emit a table-qualified CHECK that cannot survive RENAME TO.
kind: failure-mode
proposed_layer: meta
tags: [drizzle, sqlite, migrations, d1, data-loss]
generated: { by: claude/opus-5, at: 2026-08-06T21:35:02Z }
status: draft
sources:
  - id: evidence
    resource: projects/trikin/web/migrations/0005_rename_license_columns.sql
    title: The generated migration and the two hand-applied fixes
    last_modified: 2026-08-06
  - id: commit
    resource: projects/trikin
    title: 18d5b81 refactor(trikin) drop the Texas assumption from licences and deal states
    last_modified: 2026-08-06
---

# Observation

SQLite cannot drop a column default, so drizzle-kit generates a full table recreation:
`CREATE TABLE __new_x`, `INSERT INTO __new_x SELECT ... FROM x`, `DROP TABLE x`,
`ALTER TABLE __new_x RENAME TO x`. Answering its interactive "renamed from another column?"
prompt correctly updates the snapshot but does not fix the generated SQL. Three things to
check by hand every time, before the file is committed:

1. **The `SELECT` column list.** When the recreation also renames a column, the generated
   `INSERT ... SELECT` reads the *new* name from the *old* table. That column does not
   exist yet, so the statement errors and the migration aborts partway.
2. **`PRAGMA foreign_keys` placement.** With two tables recreated in one migration, the
   `=ON` can land between them rather than after both. Every `DROP TABLE` in the file has
   to sit inside one OFF/ON pair.
3. **Table-qualified CHECK constraints.** Drizzle writes `CHECK("__new_agents"."col" ...)`.
   `ALTER TABLE ... RENAME TO` does not rewrite the qualifier, and SQLite then rejects the
   rename outright: `error in table agents after rename: no such column:
   __new_agents.defaultAgentFeeBps`. Write the reference unqualified.

Then prove the migration on a throwaway database rather than on the current schema: apply
every migration *before* the new one, write rows using the *old* column names, apply the
new one, and read the rows back. Applying the whole chain to an empty database exercises
none of this, because there is nothing to copy and nothing to lose.

# Why it matters

Defect 1 is the safe failure: the statement errors and the deploy stops. Defect 3 is worse
in D1, where a migration is applied statement by statement without an enclosing
transaction, so `DROP TABLE agents` succeeds and the `RENAME TO` that was meant to replace
it fails. The table is gone and its replacement is still called `__new_agents`.

The generated SQL is the artifact that runs against production. The snapshot being correct
says nothing about the SQL, and here the snapshot was right while the SQL was wrong twice.

# Evidence

Reproducing defect 3, applying each statement in order against `bun:sqlite`:

```
FAIL 0005_rename_license_columns.sql stmt 8 :: error in table agents after rename:
  no such column: __new_agents.defaultAgentFeeBps
ALTER TABLE `__new_agents` RENAME TO `agents`;
```

Generated, and broken:

```sql
CONSTRAINT "agents_default_fee_bps_range"
  CHECK("__new_agents"."defaultAgentFeeBps" IS NULL OR ...)
INSERT INTO `__new_brokers`(..., "licenseNumber", "licenseState", ...)
  SELECT ..., "licenseNumber", "licenseState", ... FROM `brokers`;
```

Fixed:

```sql
CONSTRAINT "agents_default_fee_bps_range"
  CHECK("defaultAgentFeeBps" IS NULL OR ...)
INSERT INTO `__new_brokers`(..., "licenseNumber", "licenseState", ...)
  SELECT ..., "trecLicenseNumber", "trecLicenseState", ... FROM `brokers`;
```

The probe that would have caught both: apply 0000-0004, insert two broker rows and an
agent row under the old column names, apply 0005, then assert the rows survived with their
values in the new columns and that the CHECK, the unique index, the FK and its
`ON DELETE restrict` all still reject what they should. All eight assertions passed only
after the fixes.

not:
  - term: "the migration applied cleanly against a fresh database, so it is safe"
    why: "an empty table copies zero rows, so neither the wrong SELECT column nor a lost row can show up"
    instead: "seed rows under the pre-migration column names, then apply the migration and read them back"
  - term: "drizzle-kit recorded the rename, so the rename is handled"
    why: "the snapshot and the emitted SQL are produced separately; the snapshot was correct while the SQL was not"
    instead: "read the generated SQL line by line whenever the diff contains a __new_ table"
