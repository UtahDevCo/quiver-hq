---
type: Observation
title: Co-locate validation schemas with what they validate
description: A schema lives next to its mutation or query as *.schema.ts, not in a centralized schemas.ts.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [validation, zod, file-organization]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
not:
  - term: "a centralized schemas.ts collecting a domain's validators"
    why: "the schema drifts from the code it validates and becomes a merge-conflict magnet"
    instead: "*.schema.ts next to the mutation or query it belongs to"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Schema Organization
    last_modified: 2026-07-25
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — zod schema variables should be camelCase
---

# Observation

Co-locate: `*.schema.ts` beside the mutation/query it validates. Schema
variables are camelCase. zamp is actively migrating off centralized
`schemas.ts` files.

# Why it matters

Recorded as a *completed migration direction*, which makes it stronger evidence
than a greenfield preference — they had the centralized version and moved away
from it.
