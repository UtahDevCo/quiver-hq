---
type: Observation
title: Assert on whole error values, unwrapped inline
description: Compare the error object with toStrictEqual rather than picking at .message, and unwrap at the assertion site.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [testing, assertions]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
not:
  - term: "expect(result.unwrapErr().message).toBe('Error message here')"
    why: "asserts on one field, so a change in error type or cause passes silently"
    instead: "expect(result.unwrapErr()).toStrictEqual(new Error('Error message here'))"
  - term: "expect(result.isErr()).toBe(true) before unwrapErr()"
    why: "unwrapErr() already throws if the result is Ok; the extra assertion is noise"
    instead: "call unwrapErr() directly"
  - term: "const res = await fn(); const val = res.unwrap(); expect(val)..."
    why: "an intermediate variable adds a line and a name for no benefit"
    instead: "expect((await fn()).unwrap()) — unwrap at the assertion site"
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Test Assertion Patterns
    last_modified: 2026-07-25
---

# Observation

Assert on the whole error value, and unwrap inline rather than binding
intermediates.

# Why it matters

`.message`-only assertions are the most common way a test keeps passing after
the behavior it guards has changed — a different error class with the same
message satisfies it.
