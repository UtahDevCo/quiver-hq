---
type: Failure Mode
title: A listing endpoint is not the uniqueness domain
description: The set a create checks for conflicts is often wider than what the matching list returns. "GET says it isn't there" does not mean you can create it — and `if (!found) create()` then retries a doomed write forever.
tags: [third-party-apis, rest, idempotency, uniqueness, verification]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T23:10:47Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /meta/failure-modes/verify-a-write-actually-happened.md }
not:
  - term: "if (!found) await create()  // the lookup said the name was free"
    why: "correct only if the listing covers everything the create checks — an invisible premise that is almost never documented, and when it fails the code retries the same doomed create forever"
    instead: "treat an already-exists error as a real branch: catch it, resolve the id, and update instead"
  - term: "concluding a record is unreachable because the list endpoint cannot see it"
    why: "uniqueness is often enforced across a wider scope (user/tenant/parent/global) or a different API version than the one you listed"
    instead: "enumerate the other scopes and API versions before concluding; neither view is necessarily complete, in either direction"
  - term: "asserting on the value a sync function returned"
    why: "the defect here was a call that never happened, which no assertion on a return value can catch"
    instead: "assert the calls made — a stub client plus an expected call sequence"
sources:
  - id: wiley-timeframes
    resource: projects/wiley
    title: "wiley — quiet-hours timeframe create locked out by a user-scope collision, 2026-07-29"
    author: claude/opus-5
    last_modified: 2026-07-29
---

# The trap

```ts
const existing = await nsClient.findDomainTimeframeByName(domain, "QuietHours");
if (existing) { await update(existing.id); } else { await create(); }  // 400s forever
```

`GET /domains/{d}/timeframes` returned `[]`, so the code created — and got
`400 "A timeframe with this name already exists for the given user."`

A timeframe of that name existed at **user** scope, which the domain-scope listing
does not include, even though the domain-scope create collides with it. The read and
the write disagreed about what "exists" means: `GET` answered *nothing at this scope*,
`POST` enforced uniqueness across a wider set.

Worse, v1 and v2 of the API each listed rows the other could not see. **Neither view
was complete, in both directions.**

# Why it locks up permanently

`if (!found) create()` reads as obviously correct, and it is — *provided the listing
covers everything the create checks*. That premise is invisible.

When it fails, the failure is absorbing: the code never learns the id it would need in
order to update, so it retries the identical doomed create on every run, forever.

# The mirror image is worse

The same blind lookup on the **disable** path returned early — "nothing to disable,
calls already ring" — while a user-scope timeframe kept rejecting every call. A lookup
that under-reports turns into a silently swallowed write on the teardown path, which is
[verify-a-write-actually-happened](verify-a-write-actually-happened.md) arriving from a
different direction.

# What to do instead

- Handle *already exists* explicitly, even when your own lookup just said the name was
  free. It is a branch, not an impossibility.
- When a create rejects for a conflict your read cannot explain, enumerate the other
  scopes and API versions before concluding the record is unreachable.
- **Run the control experiment before theorising.** Creating a never-used name
  succeeded, which proved creates worked and the *name* was the problem. Without that,
  "creates are broken" and "this name is taken" look identical.
