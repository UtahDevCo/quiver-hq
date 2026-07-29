---
type: Observation
title: Never send Error objects across a serialization boundary
description: Error instances do not serialize. Pass error.message across server/client boundaries.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [react, rsc, serialization]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
not:
  - term: "<ClientComponent error={error} />"
    why: "Error instances are not serializable; the prop arrives empty or throws"
    instead: "<ClientComponent error={error.message} />"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Server/Client Boundaries
    last_modified: 2026-07-25
  - id: rsc-reviewer
    resource: projects/zamp/.claude/agents/rsc-boundary-reviewer.md
    title: rsc-boundary-reviewer — rule 4
---

# Observation

Pass `error.message` (a string), never the `Error` instance, from a server
component to a client component.

# Why it matters

The type system does not catch it — `error` is a valid prop type on both sides.
zamp considers it important enough to enforce with a dedicated reviewer subagent,
which is a strong signal it recurs.

Generalizes beyond RSC to any serialization boundary: postMessage, structured
clone, job payloads, cache entries.
