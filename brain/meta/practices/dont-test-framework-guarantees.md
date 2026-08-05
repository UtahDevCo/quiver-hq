---
type: Practice
title: Don't test your framework's guarantees — test the contracts your code introduces
description: Assertions on step ordering, retries, or that Promise.all parallelized restate the framework's contract; they fail on harmless refactors, which is what triggers wholesale test deletion.
tags: [testing, test-design, background-jobs, contracts]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "asserting step names, step execution order, or exact step-invocation counts"
    why: "these are guarantees of the framework, so the test restates its contract while breaking on harmless renames and reorderings"
    instead: "assert the payload shapes your code publishes across a boundary, and behaviors a reader could not infer from the code"
  - term: "asserting that Promise.all actually ran two steps in parallel"
    why: "parallelism is the runtime's job; the assertion is either tautological or a test of the engine"
    instead: "assert the observable result the concurrent work produces"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Don't test Inngest framework behavior'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

A framework already guarantees its own semantics — step ordering, retries, error
propagation, query building, route matching. Tests should not re-assert them. Skip
tests that check:

- step or handler names, and execution order
- that a concurrent primitive really ran things concurrently
- that an error in one step halted subsequent steps
- exact counts of framework-level calls

Test instead what *your* code does that reading it wouldn't reveal:

- **cross-boundary payload contracts** — the shape of a message another codebase
  consumes, with no compiler enforcing it
- **deliberate decisions that look like bugs** — a best-effort publish that
  intentionally swallows its error
- **paths that don't run on the happy path** — failure and cleanup handlers

# Why these tests are worse than redundant

They are actively negative. A framework-behavior test fails when someone renames a step
or reorders independent work — changes that break nothing. The suite then produces false
alarms, and the usual response is to weaken or delete tests wholesale, taking real
coverage with them. They also consume the test-writing budget that should have gone to
the payload contract nobody is checking.

The positive half is the more valuable half, and it's the half that gets skipped. A
published message shape is a genuine contract across a boundary with no type checking.
An intentional error-swallow is exactly what a future reader will "fix" unless a test
states that it is deliberate.

# Relation

Sits with [assert-on-whole-values](assert-on-whole-values.md) and
[mock-at-narrowest-scope](mock-at-narrowest-scope.md): together they say test your own
behavior, at the narrowest scope that exercises it, asserting on whole values.
