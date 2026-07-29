---
type: Practice
title: Co-locate a schema with what it validates
description: A validator lives next to what it guards, not in a centralized schema file. The adjacency is the rule; the filename convention is per-project.
tags: [validation, file-organization, zod]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:11Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "a centralized schemas.ts collecting a module's validators"
    why: "the schema drifts from the code it validates and becomes a merge-conflict magnet"
    instead: "a schema file adjacent to its consumer — *.schema.ts, types.ts, or a local schemas/ directory"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Schema Organization (recorded as a completed migration direction)
    author: human:christopher
    last_modified: 2026-07-25
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — schema variables are camelCase
  - id: wiley-schemas
    resource: projects/wiley/web/components/forms/schemas/contacts.ts
    title: "wiley — schemas/ directory beside the drawer and action that share it"
    last_modified: 2026-07-29
  - id: trikin-types
    resource: projects/trikin/web/src/app/admin/notifications/types.ts
    title: "trikin — types.ts beside the actions.ts that consumes it"
    last_modified: 2026-07-29
---

# The practice

Put the schema **adjacent to its consumer**. Never in a centralized file that
collects a module's validators.

# The filename convention is local, the adjacency is not

Corroborated in three repos, each spelling it differently:

| Repo | Shape |
|---|---|
| zamp | `*.schema.ts` beside the function; camelCase schema variables |
| wiley | `components/forms/schemas/<name>.ts`, shared by the drawer and the action |
| trikin | `types.ts` beside the `actions.ts` that consumes it |

wiley's is a *directory* of schemas, which looks like the centralization this
practice warns against and is not — it sits inside the feature that owns it, beside
its consumers, rather than at the app root. The test is distance to the consumer,
not whether the word "schemas" appears in the path.

Match the surrounding module, per
[follow-local-conventions](follow-local-conventions.md).

# Why this evidence is stronger than a preference

zamp *had* centralized schema files and is actively moving away from them. A
completed migration away from a structure is much better evidence than a
greenfield opinion — somebody paid for the lesson.

The failure mode of centralization is drift: the schema and the function it guards
change in different commits, by different people, and the mismatch is only
discovered at runtime.
