---
type: Practice
title: Co-locate a schema with what it validates
description: A validator lives next to the function it guards, not in a centralized schema file.
tags: [validation, file-organization, zod]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:11Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "a centralized schemas.ts collecting a module's validators"
    why: "the schema drifts from the code it validates and becomes a merge-conflict magnet"
    instead: "*.schema.ts beside the function it guards"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Schema Organization (recorded as a completed migration direction)
    author: human:christopher
    last_modified: 2026-07-25
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — schema variables are camelCase
---

# The practice

Put the schema in a `*.schema.ts` next to the function it validates. Schema
variables are camelCase.

# Why this evidence is stronger than a preference

zamp *had* centralized schema files and is actively moving away from them. A
completed migration away from a structure is much better evidence than a
greenfield opinion — somebody paid for the lesson.

The failure mode of centralization is drift: the schema and the function it guards
change in different commits, by different people, and the mismatch is only
discovered at runtime.
