---
type: Practice Override
title: Whole-value assertions come from bun:test, not vitest
overrides: /meta/practices/assert-on-whole-values.md
mode: narrow
why: "The substance of the practice carries over unchanged; only the import surface differs. Named so an agent does not reach for vitest, add it as a dependency, and end up with two runners."
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "import { describe, it, expect } from 'vitest'"
    why: "vitest is not a dependency; the runner is bun test"
    instead: "import { describe, it, expect } from 'bun:test'"
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

[Assert on whole values](../../../meta/practices/assert-on-whole-values.md) holds
here in full. `bun:test` provides `toStrictEqual`, so whole-value assertions,
inline unwrapping, and the no-intermediate-variables rule all apply as written.

What differs is the import: `bun:test`, and the command is `bun test`.

# Why it is worth recording

Low stakes on its own. It is the kind of thing that produces a plausible-looking
test file that cannot run, and then a dependency added to make it run. The meta
practice is written in vitest vocabulary, and naming the local equivalent is cheaper
than letting each session rediscover it.

# Evidence

22 `*.test.ts` files, `bun test` in `package.json` scripts, no vitest anywhere in
the dependency tree.

The mocking half of the testing rules has its own override:
[mocking under bun:test](bun-test-is-the-runner-mocking.md).
