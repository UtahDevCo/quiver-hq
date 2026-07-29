---
type: Practice
title: Mock at the narrowest scope that works, and assert how it was called
description: Spy on one export before replacing a module. A mock you don't assert against verifies almost nothing.
tags: [testing, mocking, vitest]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "reaching for module-level mocking first"
    why: "replaces the whole module for every importer, silently changing behavior far outside the test"
    instead: "spy on the specific export; escalate only when that genuinely can't work"
  - term: "importing the real module inside a unit test (vi.importActual and friends)"
    why: "slow, and it drags real module graphs into a test that was supposed to be isolated"
    instead: "spy on the export, or deep-mock the client object"
  - term: "asserting only that a mock was called"
    why: "passes even when it was called with the wrong arguments the wrong number of times"
    instead: "toHaveBeenCalledWith(...) and toHaveBeenCalledTimes(n)"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Test Style Guidelines
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

**Escalation order** — take the first that works:

1. `vi.spyOn` — one export, one test.
2. `mockDeep<T>()` (`vitest-mock-extended`) — when you need a complex shape,
   e.g. an SDK client.
3. `vi.mock` — only after both above are ruled out.

Avoid `vi.importActual`.

**Always assert the interaction:** `.toHaveBeenCalledWith()` **and**
`.toHaveBeenCalledTimes()`.

**Keep setup direct:** `beforeEach(resetDB)`, not an async wrapper around a
single call.

**Minimal imports:** don't import the mocking helper if you aren't mocking.

# Why the order is what it is

It's a **blast-radius ordering**, not a style preference. `spyOn` touches one
export for the duration of one test. `vi.mock` replaces a module for everything
that imports it, for the whole file — which is how a mock starts lying: the test
passes, and it passes for a reason unrelated to the code under test.

Reaching for the heaviest tool first is the single most common cause of tests that
pass while the feature is broken.

# Scope note

The API names are Vitest-specific; the escalation principle and the
assert-the-interaction rule apply to Jest, Sinon, and any spy library.
