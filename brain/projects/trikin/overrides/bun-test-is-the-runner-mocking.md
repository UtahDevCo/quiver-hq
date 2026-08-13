---
type: Practice Override
title: The mocking escalation ladder uses bun:test's spyOn and mock.module
overrides: /meta/practices/mock-at-narrowest-scope.md
mode: narrow
why: "The blast-radius ordering and the assert-the-interaction rule both hold; the middle rung is mock.module rather than vitest's vi.mock, which has different hoisting semantics."
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "import { vi } from 'vitest' / vi.mock(...)"
    why: "vitest is not a dependency; the mock namespace is `mock` and `spyOn` from bun:test"
    instead: "import { mock, spyOn } from 'bun:test'; escalate spyOn → mock.module"
sources:
  - id: agents
    resource: projects/trikin/AGENTS.md
    title: "Testing section — write unit tests using bun test, tests adjacent to source"
  - id: pkg
    resource: projects/trikin/package.json
    title: "bun@1.2.20; no vitest dependency"
  - id: tests
    resource: projects/trikin/web/src/utils/lead-assignment-summary.test.ts
    title: "one of 22 existing test files"
---

# The carve-out

[Mock at the narrowest scope](../../../meta/practices/mock-at-narrowest-scope.md)
holds here. `bun:test` provides `spyOn`, `toHaveBeenCalledWith`, and
`toHaveBeenCalledTimes`, so the escalation order and the requirement to assert both
the arguments and the call count carry over unchanged.

The ladder in local vocabulary: `spyOn` first, then `mock.module` when that cannot
work. `vi.mock` and its hoisting semantics do not exist here.

# Why it is worth recording

The meta practice already notes that trikin has no mock setup in the test files
examined, so this override describes the runner rather than an observed mocking
convention. It exists to stop a session writing `vi.spyOn`, finding it undefined,
and installing vitest.

# Evidence

22 `*.test.ts` files, `bun test` in `package.json` scripts, no vitest anywhere in the
dependency tree.

The assertion half has its own override:
[whole-value assertions under bun:test](bun-test-is-the-runner-assertions.md).
