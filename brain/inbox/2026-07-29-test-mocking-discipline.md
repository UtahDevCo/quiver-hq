---
type: Observation
title: Mocking preference order, and always verify the calls
description: Reach for spyOn first, mockDeep for complex shapes, vi.mock last; avoid importActual. Assert both arguments and call count.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [testing, mocking, vitest]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
not:
  - term: "vi.importActual"
    why: "slow, and it pulls real module graphs into a unit test"
    instead: "spyOn the specific export, or mockDeep the client"
  - term: "asserting a mock was called without asserting how"
    why: "a passing mock assertion with no argument check verifies almost nothing"
    instead: "toHaveBeenCalledWith(...) and toHaveBeenCalledTimes(n)"
  - term: "importing vi when you are not mocking anything"
    why: "signals mocking that isn't happening"
    instead: "omit the import"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Test Style Guidelines
    last_modified: 2026-07-25
---

# Observation

**Preference order:** `vi.spyOn` → `mockDeep<T>()` (from
`vitest-mock-extended`, for complex shapes like an SDK client) → `vi.mock`
only after both are ruled out. Avoid `vi.importActual`.

**Always verify:** `.toHaveBeenCalledWith()` **and**
`.toHaveBeenCalledTimes()`.

**Keep setup direct:** `beforeEach(resetDB)`, not an async wrapper around it.

**Minimal imports:** only import what the test uses.

# Why it matters

The order is a blast-radius ordering: `spyOn` touches one export, `vi.mock`
replaces a whole module and silently changes behavior for everything importing
it. Reaching for the heaviest tool first is how mocks start lying.

# Layer note

`vitest-mock-extended` and `resetDB` are concrete dependencies; the ordering
principle and the verify-the-call rule are general.
