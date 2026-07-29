---
type: Practice
title: New or changed Prisma calls need a real-DB test
description: Shard-key and join-strategy defects are invisible to type-checking and to mocked prisma. Only a real database catches them.
tags: [testing, database, vitess]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /projects/zamp/invariants/sharded-tables-companyid.md }
  - { kind: depends-on, target: /projects/zamp/invariants/relation-load-strategy.md }
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — real-DB test requirement
    last_modified: 2026-07-25
---

# The practice

A new or changed Prisma call — especially a nested read touching a sharded table —
ships with a real-DB test: `beforeEach(resetDB)`, data from
`@util/db/test/db-factories/*`, invoking the function and asserting on the returned
relations.

Factories live in `@util/db/test/factories/{schema}` (pure in-memory) and
`@util/db/test/db-factories/{schema}` (DB-touching), mirroring the Prisma schema
file names. Missing factory → add it there, not domain-locally. Test-file-local
helpers are acceptable for composite scenarios needing domain logic that would cycle
if placed in `@util/db`.

# Why it matters

This is the test that catches the two invariants above, and the reason those
invariants are survivable at all.

# Promotion candidate

The transferable rule is **spend test effort on the failure modes your type system
and your mocks structurally cannot see** — which is general, and sharper than "write
integration tests." Held at project layer because the only evidence is zamp, and
stated that abstractly it risks becoming a platitude that licenses any slow test.
Promote when a second repo shows what shape the general version takes.
