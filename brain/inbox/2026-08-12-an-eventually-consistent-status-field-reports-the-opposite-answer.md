---
type: Observation
title: An eventually-consistent status field reports the opposite answer, not "unknown"
description: A derived status read too soon does not come back empty or null. It comes back confidently wrong, and a probe that reads immediately prints a clean, false verdict.
kind: failure-mode
proposed_layer: meta
tags: [probing, eventual-consistency, measurement]
generated: { by: claude/opus-5, at: 2026-08-12T19:40:27Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/probe-answerrule-shadowing.ts
    title: probe that printed the wrong verdict until a settle wait was added
    last_modified: 2026-08-12
  - id: prior-art
    resource: projects/wiley/web/app/actions/settings.ts
    title: comment documenting that the same field lags a write in both directions
    last_modified: 2026-08-12
not:
  - term: "read the derived field right after staging and record the result"
    why: "an unsettled read is indistinguishable from a settled one, so the probe reports a false finding with full confidence"
    instead: "wait past the observed propagation delay, and make the ambiguous reading print as inconclusive rather than as an answer"
---

# Observation

A status field the backend derives from other state (is-active, is-current,
effective-policy, computed-status) is not simply stale after a write. It reports
a definite, wrong value, and it looks exactly like a settled read.

A probe written to answer a yes/no question by reading such a field will print a
clean verdict either way. Nothing in the response says "not settled yet".

Two defences, and the second matters more. Wait past the observed propagation
delay before reading. Then make the probe recognise the shape that a stale read
produces and print it as inconclusive, because a wait long enough today is not
long enough forever.

# Why it matters

A probe testing which of two matching rules a phone system would apply read the
`is-active` flag seconds after staging and reported that the catch-all rule won.
That verdict was the opposite of the truth. Read again 160 seconds later, the
staged rule held `is-active` and the catch-all did not.

The wrong answer was not obviously wrong. It was plausible, it contradicted the
working hypothesis, and it would have been recorded as a falsification of the
hypothesis rather than as a measurement failure.

# Evidence

Same account, same two rules, two reads:

    t+0s     staged rule  is-active=false      *  is-active=true    <- wrong
    t+160s   staged rule  is-active=true       *  is-active=false   <- correct

The codebase already carried a comment saying this field "propagates behind" the
underlying record and is "unreliable in both directions" when read straight
after a write. The comment was on the write path; the probe was new code and did
not inherit the warning.

The fixed probe waits, and its "the opposite of the hypothesis" branch now says
so explicitly:

    This is ALSO what an unsettled read looks like, and it is what this probe
    printed before the wait was added. Re-run once more before believing it.

A distinct third state helps: when neither of two simultaneously-matching rules
reports active, nothing has settled, and that is knowably different from either
real answer.
