---
type: Failure Mode
title: A catch that maps an error to success reports writes that never landed
description: "\"Not found\" and \"not addressable this way\" both arrive as 404. Read the state back and assert on the field you wrote — a silent no-op is strictly worse than a crash."
tags: [error-handling, third-party-apis, idempotency, observability]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /meta/practices/error-propagation-and-capture.md }
not:
  - term: "`if (disabling && isNotFoundError(e)) return {}`  // already gone, nothing to do"
    why: "conflates \"the write was unnecessary\" with \"the write was impossible\" — both are 404"
    instead: "read the state back and assert it; throw naming the record and the manual remedy if it can't be reached"
  - term: "trusting that a write landed because the call returned without throwing"
    why: "an API can accept a malformed request, or the path can be wrong for this tenant, and still 2xx or 404-as-noop"
    instead: "read back and compare against the intended state"
  - term: "asserting on a derived or propagated field to confirm a write"
    why: "computed fields lag in either direction and produce spurious failures for writes that did work"
    instead: "assert on the exact field you wrote"
sources:
  - id: wiley-upsert-answering-rule
    resource: projects/wiley
    title: wiley — upsertAnsweringRule swallowed every disable for months, found 2026-07-29
    author: claude/opus-5
    last_modified: 2026-07-29
---

# The trap

```ts
if (enabled === "no" && this.isNotFoundError(error)) {
    return {};   // "already gone, nothing to do"
}
```

The intent was reasonable: disabling something that doesn't exist is a no-op. But
on this instance the rule was **never addressable by that path**, so the 404 fired
every time and the branch swallowed every disable.

The app told customers quiet hours was off while their phone kept rejecting every
call, with no error anywhere, **for months.** A crash would have been diagnosed in
a day. This is the specific sense in which a silent failure is worse than a loud
one — not that it's harder to debug, but that nobody ever starts.

The root confusion: *not found* and *my request was malformed, or this resource
isn't addressable this way* arrive as the same status code. Mapping 404 to
idempotent success conflates "the write was unnecessary" with "the write was
impossible."

# What to do instead

- After a write whose success matters, **read the state back and assert it.** A
  call returning without throwing is not evidence.
- Assert against the field you actually wrote, not a derived one. Here the
  answering rule's `time_range_data` lagged the timeframe, so asserting on it
  produced spurious failures for disables that had genuinely worked.
- When you can't reach the intended state, throw with an actionable message naming
  the record and the manual remedy. Never return success.
- Be suspicious of **any** `catch` that maps an error class to success. Ask what
  *else* produces that status code.

This is the concrete case behind
[error-propagation-and-capture](../practices/error-propagation-and-capture.md)'s
rule about capturing only where you stop an error: this code stopped the error and
then discarded it, which is the one thing a capture point must not do.

How the damage stayed invisible afterward:
[audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md).
