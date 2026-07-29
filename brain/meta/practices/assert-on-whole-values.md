---
type: Practice
title: Assert on whole values, and unwrap at the assertion site
description: Compare the entire error or object rather than picking at one field, and skip intermediate variables in tests.
tags: [testing, assertions, readability]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "expect(err.message).toBe('Something failed')"
    why: "asserts one field, so a different error type with the same message still passes"
    instead: "expect(err).toStrictEqual(new Error('Something failed'))"
  - term: "asserting a success/failure flag before unwrapping"
    why: "the unwrap already throws on the wrong branch; the extra assertion is noise"
    instead: "unwrap directly and let it throw"
  - term: "const res = await fn(); const val = res.unwrap(); expect(val)..."
    why: "an intermediate name for a value used once adds a line and reading cost"
    instead: "expect((await fn()).unwrap()) — unwrap inline where you assert"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Test Assertion Patterns
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

- Assert on the **whole value**: `toStrictEqual(new Error("..."))`, not
  `.message`.
- **Unwrap inline** at the assertion site.
- **No intermediate variables** for values used once.

# Why whole-value assertions matter more than they look

A `.message`-only assertion is the most common way a test keeps passing after
the behavior it guards has changed. Swap the error class, add a `cause`, change
the type — the assertion still holds. The test becomes decoration.

`toStrictEqual` on the constructed error also documents the expected type, which
is information the reader would otherwise have to go find.

# Scope

The unwrap phrasing comes from a `Result`-based codebase, but the principle is
framework-agnostic: assert on the largest value you can state exactly, and state
it in one place.

# Related

[Mock at the narrowest scope that works](mock-at-narrowest-scope.md).
