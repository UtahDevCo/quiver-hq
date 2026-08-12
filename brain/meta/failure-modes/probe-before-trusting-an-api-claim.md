---
type: Failure Mode
title: A comment asserting a third-party API limitation is a hypothesis, not a fact
description: "\"The API doesn't support X\" gets load-bearing fast. Probe it before extending the workaround — and commit the probe, including the ones that falsified your own guess."
tags: [third-party-apis, comments, verification, debugging]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /meta/practices/minimal-comments.md }
  - { kind: generalizes, target: /meta/failure-modes/a-capability-probe-needs-a-positive-control.md }
  - { kind: generalizes, target: /meta/failure-modes/probe-inputs-must-make-outcomes-distinguishable.md }
not:
  - term: "extending a workaround whose justification is a code comment about an external system"
    why: "later readers treat the comment as settled and build more logic on top; the confidence is doing work no test ever justified"
    instead: "probe the claim against a non-production tenant first — usually under a minute"
  - term: "deleting a probe script once it has answered the question"
    why: "throws away the difference between \"someone once believed this\" and \"this was measured on <date>\""
    instead: "commit the probe as the evidence for the comment it justifies"
  - term: "discarding a probe that disproved your own hypothesis"
    why: "the next person re-derives the same plausible wrong idea"
    instead: "record the falsified hypothesis too — negative results are the expensive ones to reproduce"
sources:
  - id: wiley-netsapiens-timeframes
    resource: projects/wiley
    title: wiley — syncQuietHoursToNetSapiens delete-then-recreate workaround, disproved 2026-07-29
    author: claude/opus-5
    last_modified: 2026-07-29
  - id: wiley-allowlist-removal
    resource: projects/wiley/web/scripts/_probe-allowlist-removal-matrix.ts
    title: "wiley 60d9eb8 — a probe that confirmed the claim, and needed two design fixes before it could have failed"
    author: claude/opus-5
    last_modified: 2026-08-08
---

# The trap

A comment asserted: *"NetSapiens has no update-timeframe endpoint, so changing the
window means delete-then-recreate."*

It was **false**. `PUT /ns-api/v2/domains/{d}/timeframes/{id}` works fine, and a
single probe against a scratch domain disproved it in under a minute.

Everything destructive in that code path existed only to work around a limitation
that did not exist — and the workaround itself permanently wedged 11 customer
accounts. Deleting the timeframe orphaned the answering rule, which then reserved
the timeframe name so nothing could recreate it.

Two prior fixes had already elaborated the delete-recreate dance rather than
questioning its premise. That is the shape of the failure: an unverified claim
about an external system becomes load-bearing, and each subsequent fix treats it
as the one fixed point in the problem.

# What to do instead

When a comment or a design explains itself with "the API doesn't support X",
**verify X before extending the workaround.** Write a throwaway probe against a
non-production tenant.

- Claim false → delete the workaround. Don't patch it.
- Claim true → leave the probe in the repo as the evidence. A committed probe is
  the difference between *someone once believed this* and *this was measured on
  a date*.

# Keep the negative results

The first hypothesis here — that the delete was blocked by the referencing rule —
was plausible, matched the error text, and was wrong; the fix built on it did not
stop the bug. Recording a falsified hypothesis is what stops the next person
spending the same hour on it.

This is the one case where a comment earns its keep under
[minimal-comments](../practices/minimal-comments.md): it documents a
non-obvious *why* about an external system. It just has to be true, and cite how
that was established.

# Then check the probe could have failed

Running the probe is the first half. A probe against the same vendor on 2026-08-08
confirmed a limitation and still had two defects that would each have produced the
same confirmation from an API with no limitation at all:

- No positive control, so an absent value and a value that was never written read
  identically. See [a capability probe needs a positive control](a-capability-probe-needs-a-positive-control.md).
- Inputs already in the requested state, so append, replace and no-op left the
  store byte-identical. See [probe inputs must make outcomes distinguishable](probe-inputs-must-make-outcomes-distinguishable.md).

A committed probe raises how much the next reader trusts the claim, which is the
point of committing it and also the reason a badly designed one is worse than none.
