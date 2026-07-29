---
type: Observation
title: New or changed Prisma calls need a real-DB test
description: Shard-key and join-strategy defects are invisible to type-checking and to mocked prisma. Only a real database catches them.
kind: practice
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [testing, database, vitess]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — real-DB test requirement
    last_modified: 2026-07-25
---

# Observation

A new or changed Prisma call — especially a nested read touching a sharded
table — ships with a real-DB test: `beforeEach(resetDB)`, data from
`@util/db/test/db-factories/*`, invoking the function and asserting on the
returned relations.

Factories live in `@util/db/test/factories/{schema}` (pure in-memory) and
`@util/db/test/db-factories/{schema}` (DB-touching), mirroring the Prisma schema
file names. Missing factory → add it there, not domain-locally. Test-file-local
helpers are acceptable for composite scenarios needing domain logic that would
cycle if placed in `@util/db`.

# Why it matters

This is the test that catches the two invariants above, and it's the reason those
invariants are survivable at all. It's a good general lesson about where to spend
test effort — on the failure modes your type system and mocks structurally cannot
see — but the specifics are zamp's.
