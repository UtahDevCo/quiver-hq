---
name: a-listing-endpoint-is-not-the-uniqueness-domain
description: The set an API's create checks for conflicts is often wider than what its list endpoint returns — so "GET says it isn't there" does not mean you can create it.
metadata:
  type: project
---

Wiley's quiet-hours sync did:

```ts
const existing = await nsClient.findDomainTimeframeByName(domain, "QuietHours");
if (existing) { await update(existing.id); } else { await create(); }  // 400s forever
```

`GET /domains/{d}/timeframes` returned `[]`, so the code created — and got
`400 "A timeframe with this name already exists for the given user."` A timeframe
of that name existed at **user** scope, which the domain-scope listing does not
include, even though the domain-scope create collides with it.

The read and the write disagreed about what "exists" means. `GET` answered
"nothing at this scope"; `POST` enforced uniqueness across a wider set.

**Why:** `if (!found) create()` reads as obviously correct, and it is — provided
the listing covers everything the create checks. That premise is invisible and
almost never documented. When it fails you get a permanent lockout, because the
code retries the same doomed create forever and never learns the id it would need
to update instead.

**How to apply:**

- Treat an "already exists" error on create as a real branch, not an impossible
  one. Handle it explicitly even when your lookup just said the name was free.
- When a create rejects for a conflict your read cannot explain, enumerate the
  other scopes (user/tenant/parent/global) and the other API versions before
  concluding the record is unreachable. Here v1 and v2 each listed rows the other
  could not see — **neither view was complete**, in both directions.
- The mirror-image bug is worse and easy to miss: the same blind lookup in the
  *disable* path returned early with "nothing to disable, calls already ring"
  while a user-scope timeframe kept rejecting calls. A lookup that under-reports
  turns into a silently swallowed write on the teardown path. See
  [[verify-a-write-actually-happened]].
- Verify by asserting **the calls made**, not the value returned. The defect was
  a call that never happened, so no assertion on a return value would have caught
  it. A stub client plus an expected call sequence does.
- Run the control experiment before theorising: creating a
  never-used name succeeded, which proved creates worked and the *name* was the
  problem. Without that, "creates are broken" and "this name is taken" look
  identical.

Related: [[probe-the-api-before-trusting-a-code-comment]],
[[audits-must-report-their-own-coverage]]
