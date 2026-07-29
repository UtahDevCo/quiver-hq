---
type: Observation
title: Nested reads touching sharded tables need relationLoadStrategy query
description: With relationJoins enabled, nested reads default to a join strategy that compiles to correlated subqueries and fails on Vitess.
kind: invariant
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [database, vitess, sharding, prisma]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — relationLoadStrategy rule
    last_modified: 2026-07-25
  - id: shard-reviewer
    resource: projects/zamp/.claude/agents/shard-safety-reviewer.md
    title: shard-safety-reviewer subagent
---

# Observation

The `relationJoins` preview feature is on, so an `include` — or a `select`
nesting a relation — defaults to the `join` strategy, which fails on Vitess
(`VT12001`) when the traversal touches a sharded table and isn't shard-local.

`relationLoadStrategy: "query"` is **required** when:

- the join is cross-keyspace (sharded ↔ unsharded), *even with* a companyId filter;
- the relation is to-one into or within a sharded table (can't carry a companyId filter);
- it's a to-many sharded relation without a nested `where: { companyId }`, or
  whose model has no companyId column.

**Keep the join** for a same-keyspace sharded→sharded to-many relation that
carries a nested `where: { companyId }`.

# Why it matters

The default is wrong for this topology, and the failure mode is a runtime error
class (`VT12001`) rather than anything a reviewer would notice by reading. Note
the last rule — this is not "always set query," and blanket-applying it would
give up a real optimization.
