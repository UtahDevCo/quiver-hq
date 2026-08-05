---
type: Observation
title: Don't test your framework's own guarantees — test the contracts your code introduces
description: Assertions on step ordering, retry behavior, or that Promise.all parallelized are tests of the framework; the valuable tests cover cross-boundary payload shapes and deliberately non-obvious choices.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [testing, background-jobs, inngest, test-design, contracts]
status: draft
not:
  - term: "asserting step names, step execution order, or exact step.run call counts"
    why: "these are guarantees of the workflow engine, so the test restates the framework's contract and breaks on harmless refactors while catching no defect of yours"
    instead: "assert the payload shapes your code publishes across a boundary, and the behaviors a reader couldn't infer from the code"
  - term: "asserting that Promise.all actually ran two steps in parallel"
    why: "parallelism is the runtime's job; the assertion is either tautological or testing the engine"
    instead: "test the observable result the concurrent work produces"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Don't test Inngest framework behavior'" }
---

# Observation

A durable-workflow engine already guarantees step ordering, retries, and error
propagation. Tests should not re-assert them. Specifically, skip tests that check:

- step names or execution order
- that `Promise.all` really ran two steps concurrently
- that an error in one step halted subsequent steps
- exact counts of step invocations or realtime publishes

Instead test what *your* code does that reading it wouldn't reveal:

- **cross-boundary payload contracts** — e.g. the shape of a realtime publish that
  a frontend consumes
- **deliberate design decisions that look like bugs** — e.g. a best-effort publish
  that intentionally swallows its error
- **code paths that don't run on the happy path** — e.g. failure handlers

# Why it matters

Framework-behavior tests are worse than merely redundant: they are actively
negative. They fail when someone renames a step or reorders independent work —
changes that break nothing — so the suite generates false alarms, and the usual
response is to weaken or delete tests wholesale, taking real coverage with them.
They also consume the test-writing budget that should have gone to the payload
contract nobody is checking.

The positive half is the more useful half. A realtime publish shape is a genuine
contract between two codebases with no compiler enforcing it, and an intentional
error-swallow is precisely the thing a future reader will "fix" unless a test
states that it's deliberate. Those are the tests that earn their maintenance.

# Evidence

Recorded in `patterns.md` under Testing, framed against Inngest, with the four
skip-cases and three test-instead cases above.

Proposed `meta`: the reasoning applies to any framework with its own guarantees —
job runners, ORMs, routers, validation libraries. The Inngest specifics are
illustrative. Sits alongside the existing meta practices
`assert-on-whole-values` and `mock-at-narrowest-scope`.
