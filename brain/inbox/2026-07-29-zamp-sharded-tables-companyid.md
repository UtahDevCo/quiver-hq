---
type: Observation
title: Every Prisma operation on a sharded table carries companyId
description: Reads, writes, and upserts against sharded tables must include companyId at the top level of where/data — a nested relation does not count.
kind: invariant
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [database, vitess, sharding, prisma]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
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

# Observation

Canonical list of sharded tables: `utils/db/test/vitess-config/sharded-tables.ts`,
annotated `@shardKey` in `utils/db/prisma/schema/*.prisma`.

Placement: `where` for reads/updates/deletes, `data` for
`create`/`createMany`, **both** `where` and `create` for `upsert`.

# Why it matters

Invisible to type-checking and to mocked-prisma tests. It fails only against a
real Vitess topology, which means it reaches staging unless something else
catches it — hence a Cursor rule, a CodeRabbit instruction, *and* a dedicated
reviewer subagent all guarding the same thing.

# Attestation candidate

The strongest `Invariant` candidate in the repo, but not trivially greppable —
it needs the sharded-table list joined against Prisma call sites. Worth building;
start from what `shard-safety-reviewer` already does.
