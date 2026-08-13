---
type: Failure Mode
title: An eventually-consistent field answers confidently wrong, never "unknown"
description: A probe read is-active seconds after staging and reported the opposite of the truth. Read again at t+160s the answer flipped, and nothing in either response said the field had not settled.
tags: [probing, eventual-consistency, measurement, verification]
generated: { by: claude/opus-5, at: 2026-08-12T19:40:27Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "reading the derived field right after staging and recording the result"
    why: "an unsettled read is indistinguishable from a settled one, so the probe reports a false finding with full confidence"
    instead: "wait past the observed propagation delay, and make the ambiguous reading print as inconclusive rather than as an answer"
  - term: "recording a verdict that contradicts the hypothesis as a falsification"
    why: "a stale read is plausible and lands as evidence against whatever you expected, so the measurement failure gets filed as a finding"
    instead: "re-read before believing any result that would overturn the hypothesis, and say in the output that this branch is also what a stale read looks like"
  - term: "a settle wait long enough to pass today"
    why: "the delay is a property of the backend and moves without telling you, so a fixed wait decays into the same false verdict"
    instead: "teach the probe the shape a stale read produces, such as neither of two matching rules reporting active, and print that shape as a third state"
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/probe-answerrule-shadowing.ts
    title: probe that printed the wrong verdict until a settle wait was added
    author: claude/opus-5
    last_modified: 2026-08-12
  - id: prior-art
    resource: projects/wiley/web/app/actions/settings.ts
    title: comment documenting that the same field lags a write in both directions
    author: claude/opus-5
    last_modified: 2026-08-12
---

# The trap

A status field the backend derives from other state (`is-active`, `is-current`,
effective-policy, computed-status) does more than go stale after a write. It reports
a definite, wrong value, and it looks exactly like a settled read.

A probe written to answer a yes/no question by reading such a field prints a clean
verdict either way. Nothing in the response says "not settled yet".

# Why it matters

A probe testing which of two matching rules a phone system would apply read the
`is-active` flag seconds after staging and reported that the catch-all rule won. That
verdict was the opposite of the truth. Read again 160 seconds later, the staged rule
held `is-active` and the catch-all did not.

The wrong answer was plausible, it contradicted the working hypothesis, and it would
have been recorded as a falsification of the hypothesis rather than as a measurement
failure.

# Evidence

Same account, same two rules, two reads:

    t+0s     staged rule  is-active=false      *  is-active=true    <- wrong
    t+160s   staged rule  is-active=true       *  is-active=false   <- correct

The codebase already carried a comment saying this field "propagates behind" the
underlying record and is "unreliable in both directions" when read straight after a
write. That comment lived on the write path, and the probe was new code that did not
inherit the warning.

The fixed probe waits, and its "the opposite of the hypothesis" branch now says so:

    This is ALSO what an unsettled read looks like, and it is what this probe
    printed before the wait was added. Re-run once more before believing it.

A distinct third state helps. When neither of two simultaneously-matching rules
reports active, nothing has settled, and that is knowably different from either real
answer. Making the outcomes distinguishable in the first place is
[probe-inputs-must-make-outcomes-distinguishable](probe-inputs-must-make-outcomes-distinguishable.md);
this concept is what a settled read costs you in wall-clock time.
