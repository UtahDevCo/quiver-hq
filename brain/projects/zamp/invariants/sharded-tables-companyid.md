---
type: Invariant
title: Every Prisma operation on a sharded table carries companyId
description: Reads, writes, and upserts against sharded tables must include companyId at the top level of where/data — a nested relation does not count.
tags: [database, vitess, sharding, prisma]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-01-29
tags: [database, vitess, sharding, prisma, attested]
runtime: python3
parameters:
  base_ref: origin/master
  head_ref: HEAD
computation: /references/checks/zamp-sharded-companyid.py
executor:
  resource: /references/checks/zamp-sharded-companyid.py
  receipt: '{ "command": "<cmd>", "exit_code": 0, "matches": [], "coverage": {} }'
attester:
  resource: /references/expect_empty.py
not:
  - term: "companyId on a nested relation inside where"
    why: "Vitess needs the shard key at the top level to route the query; a nested filter does not route it"
    instead: "companyId directly in where (reads/updates/deletes), data (create/createMany), both (upsert)"
sources:
  - id: cursor-rule
    resource: projects/zamp/.cursor/rules/sharded-tables.mdc
    title: Cursor rule — sharded tables
    last_modified: 2026-07-25
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — domains path instructions
  - id: shard-reviewer
    resource: projects/zamp/.claude/agents/shard-safety-reviewer.md
    title: shard-safety-reviewer subagent
---

# The rule

Canonical list of sharded tables: `utils/db/test/vitess-config/sharded-tables.ts`,
annotated `@shardKey` in `utils/db/prisma/schema/*.prisma`.

Placement: `where` for reads/updates/deletes, `data` for `create`/`createMany`,
**both** `where` and `create` for `upsert`.

# Why it matters

Invisible to type-checking and to mocked-prisma tests. It fails only against a real
Vitess topology, which means it reaches staging unless something else catches it —
hence a Cursor rule, a CodeRabbit instruction, *and* a dedicated reviewer subagent
all guarding the same thing.

The test that does catch it:
[real-db-test-for-prisma-changes](../practices/real-db-test-for-prisma-changes.md).

# Computation

Attested by [zamp-sharded-companyid.py](../../../references/checks/zamp-sharded-companyid.py):

```bash
brain/references/checks/zamp-sharded-companyid.py [base] [head] \
  | brain/references/expect_empty.py
```

It derives the sharded-model list from `@shardKey` in the Prisma schema **and**
cross-checks it against `SHARDED_TABLES`. **Disagreement between the two is an
ERROR, not a pass** — if the sources have drifted, no verdict is trustworthy. That
turns the concept's own "canonical list" claim into something enforced rather than
asserted.

For each `prisma.`/`tx.`/`db.` call on a sharded model in a changed
`domains/**/*.ts` file, it brace-matches the argument object (skipping strings,
template literals, and comments) and requires `companyId` at **depth 1** of `where`,
`data`, or both `where` and `create` per the operation. A `companyId` nested inside a
relation filter therefore fails, which is the whole point.

# What it deliberately does not decide

Measured on `HEAD~60..HEAD`: **346 call sites checked, 55 skipped, 0 violations.**

The skips are the honest part:

- **`company: { connect: { id } }` on a write (50 of the 55).** This was the check's
  first finding, reported as 4 violations — and it was **wrong**. Prisma's relation
  syntax populates the `companyId` column in the generated INSERT, so the shard key
  does reach the wire; it just isn't spelled as a scalar. The recorded rule excludes
  nested relations *inside `where`*, which is a join Vitess cannot route by, and says
  nothing about `connect` in `data`. Reclassified as undecidable rather than resolved
  by guessing — settling it needs a real-DB test, per
  [probe-before-trusting-an-api-claim](../../../meta/failure-modes/probe-before-trusting-an-api-claim.md).
- **Spreads** (`where: { ...filter }`). `shard-safety-reviewer` permits companyId
  "via spread of an object that *provably* contains it", and proving that needs type
  information this check does not have.
- **Raw SQL** (`$queryRaw` / `$executeRaw`) — out of scope entirely.

Coverage counts ride along in the receipt and the attester prints them, so a `PASS`
cannot be misread as full coverage. That is
[audits-must-report-their-own-coverage](../../../meta/failure-modes/audits-must-report-their-own-coverage.md)
applied to the brain's own tooling.

# Validation

A positive control lives outside zamp — a throwaway repo with a synthetic sharded
model — because zamp is a shared working tree and an attester that needs it mutated
to test is an attester nobody tests. It confirms one catch per violation class
(missing in `where`, nested-relation-only, missing in `data`, missing in an
`upsert.create`), that a `tx.` prefix is recognized, that a correct call is not
flagged, and that source drift returns ERROR rather than PASS.

**Zero matches over 60 commits of real history is only meaningful because of that
control.** On its own it is indistinguishable from a broken check.
