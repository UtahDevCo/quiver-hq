---
type: Practice
title: Wait for the work to start, then wait for it to finish
description: A fixed sleep after submit let slow requests read as already finished, so the next action aborted them in flight; two edges fixed 38 of 40 runs and named the other two.
tags: [ui-automation, testing, async, race-conditions, chrome-devtools]
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
status: stable
stale_after: 2027-08-13
sources:
  - id: driver
    resource: "projects/k1 — Chrome DevTools MCP driver over the panel query page"
    title: "38 of 40 generated runs succeeded only after the wait-for-busy guard was added"
    last_modified: 2026-07-31
not:
  - term: "click Send, sleep 10s, then poll for the idle state and move on"
    why: "a request that has not started yet is indistinguishable from one that finished, so the driver advances and the next navigation aborts the in-flight fetch before the server persists anything"
    instead: "wait for the busy state to appear, then wait for it to clear, so a stall becomes an explicit timeout naming the item"
---

# The practice

When a driver triggers async work and then waits on it, wait on two edges: the busy
state appearing, then the busy state clearing. Polling only for "done" reads the
moment between submit and request-registration as done.

# What one edge costs

The sequence that lost runs:

```
click Send
sleep 10s
poll until the busy indicator is absent   <- absent because it never appeared
click "New conversation"                  <- aborts the fetch
```

Nothing failed. The click succeeded, the poll succeeded, the navigation succeeded, and
the server never wrote a row. Where the HTTP response was observed at all it was 200.

Adding the wait-for-busy guard fixed 38 of 40 generations and converted the remaining
two into an explicit "never started" that named the input. Those two were a real
product bug, invisible for as long as the driver was discarding its own work.

# Why the diagnostics are the larger half

A driver that loses results silently produces a partial dataset that looks complete,
and the missing entries read as "we did not get to those" rather than "those are
broken". Two edges make every loss loud and attributable, per
[audits-must-report-their-own-coverage](../failure-modes/audits-must-report-their-own-coverage.md).
