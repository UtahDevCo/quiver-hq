---
type: Observation
title: The testing practices hold under bun:test — only the import surface differs
description: assert-on-whole-values and mock-at-narrowest-scope both apply, but the runner is `bun test` with imports from "bun:test", not vitest.
kind: practice
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [testing, bun, override, practice-override]
status: draft
not:
  - term: "import { describe, it, expect, vi } from 'vitest'"
    why: "vitest is not a dependency; the runner is bun test and the mock namespace is `mock`/`spyOn`, not `vi`"
    instead: "import { describe, it, expect, mock, spyOn } from 'bun:test'"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: agents, resource: projects/trikin/AGENTS.md, title: "Testing section — write unit tests using bun test, tests adjacent to source" }
  - { id: pkg, resource: projects/trikin/package.json, title: "bun@1.2.20; no vitest dependency" }
  - { id: tests, resource: projects/trikin/web/src/utils/lead-assignment-summary.test.ts, title: "one of 22 existing test files" }
---

# Observation

`assert-on-whole-values` and `mock-at-narrowest-scope` are both satisfiable here —
`bun:test` provides `toStrictEqual`, `spyOn`, `toHaveBeenCalledWith`, and
`toHaveBeenCalledTimes`, so the substance of both practices carries over unchanged.
What differs is only the import surface and the escalation ladder's middle rung:
`spyOn` → `mock.module` (not vitest's `vi.mock` with its hoisting semantics).

Recorded as `mode: narrow` on both practices rather than left implicit, so an agent
does not reach for vitest, add it as a dependency, and end up with two runners.

# Why it matters

Low stakes individually, but it is the kind of thing that produces a
plausible-looking test file that cannot run, and then a dependency added to make it
run. Both meta practices are written in vitest vocabulary; naming the local
equivalent is cheaper than letting each session rediscover it.

# Evidence

22 `*.test.ts` files, `bun test` in `package.json` scripts, no vitest anywhere in
the dependency tree.
