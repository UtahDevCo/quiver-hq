---
type: Observation
title: Wait for the work to start before waiting for it to finish
description: A fixed sleep after submit let slow requests read as already finished, so the next action aborted them in flight and the runs disappeared with no error anywhere.
kind: practice
proposed_layer: meta
observed_in: k1
tags: [ui-automation, testing, async, race-conditions, chrome-devtools]
status: draft
not:
  - term: "click Send, sleep 10s, then poll for the idle state and move on"
    why: "a request that has not started yet is indistinguishable from one that finished, so the driver advances and the next navigation aborts the in-flight fetch before the server persists anything"
    instead: "wait for the busy state to appear, then wait for it to clear — two edges, not one — which turns a silent loss into an explicit timeout naming the item"
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
sources:
  - { id: driver, resource: "projects/k1 — Chrome DevTools MCP driver over the panel query page", title: "38 of 40 generated runs succeeded only after the wait-for-busy guard was added" }
---

# Observation

Driving a UI to generate data has one edge case that eats results: the moment
after submit, before the request registers. A poll for "is it done" reads that
moment as done.

The sequence that lost runs:

```
click Send
sleep 10s
poll until the busy indicator is absent   <- absent because it never appeared
click "New conversation"                  <- aborts the fetch
```

Nothing failed. The click succeeded, the poll succeeded, the navigation succeeded,
and the server never wrote a row. The HTTP response was 200 where it was observed
at all.

Waiting for the busy state to appear first, then for it to clear, fixed 38 of 40
generations and converted the remaining two into an explicit "never started" that
named the input. Those two turned out to be a real product bug, which had been
invisible for as long as the driver was silently discarding its own work.

# Why it matters

The diagnostic value is the larger half. A driver that loses results silently
produces a partial dataset that looks complete, and the missing entries read as
"we did not get to those" rather than "those are broken". Two edges instead of one
makes every loss loud and attributable.

Related: [[audits-must-report-their-own-coverage]] — a harness that cannot say what
it failed to do reports a floor as a total.
