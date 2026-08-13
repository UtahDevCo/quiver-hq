---
type: Failure Mode
title: Caching the read behind a limit or authorization check defeats the check
description: A one-hour cache on an exposure query leaves the cap in place and comparing against an hour-old number, so every request inside the window passes a limit that should admit one.
tags: [caching, nextjs, correctness, limits, security]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "unstable_cache(fetchOutstandingExposure, key, { revalidate: 3600 })"
    why: "the limit still gets compared, against an hour-old number, so N concurrent requests all pass a cap that only one of them should have"
    instead: "read it live, mark the route `export const dynamic = \"force-dynamic\"`, and grep-test that the cache helper never appears on these paths"
  - term: "relying on reviewers to remember which reads may not be cached"
    why: "the cache helper arrives as the house idiom for benign dashboard reads, and the person who copies it onto a money path is reaching for consistency"
    instead: "fail the build when the cache helper appears under the underwriting or money-path modules"
sources:
  - id: broker-actions
    resource: "projects/trikin/web/src/app/[role]/dashboard/(broker)/broker-actions.ts:100-105"
    title: unstable_cache with 1-hour revalidate wrapping a data read, the established house pattern
    author: claude/opus-5
    last_modified: 2026-07-30
  - id: property-actions
    resource: "projects/trikin/web/src/app/[role]/dashboard/(property)/property-actions.ts:82"
    title: the same pattern, second occurrence
    author: claude/opus-5
    last_modified: 2026-07-30
---

# The trap

Caching a display query is fine. Caching the query a limit, quota, entitlement, or
concentration check reads is a correctness hole with no symptom.

The check is still there, still executing, still comparing against the threshold. It
compares against a number from up to an hour ago, so every request inside the window
sees the same pre-decision state, and a cap that should admit one purchase admits as
many as arrive before revalidation. Nothing errors and nothing logs. Code review
sees a limit check because there is one.

# Why it spreads

The caching arrives as a house pattern for a benign reason and then gets copied onto
a path where it is not benign. In the repo this came from,
`unstable_cache(..., { revalidate: 3600 })` was the established idiom for dashboard
reads, which is reasonable for a leads table. The successor product computes
regulated exposure limits over the same query layer, and the idiom is sitting right
there.

So the countermeasure is a grep test that fails the build when the cache helper
appears under the underwriting or money-path modules, plus `force-dynamic` on those
routes. Enforce it where the temptation is.

# Evidence

`(broker)/broker-actions.ts:100`:

```ts
const cachedGetLeads = unstable_cache(
  async () => getLeadsByBroker(...),
  [cacheKey],
  { revalidate: 3600 }
);
```

Harmless here. The identical shape over `getOutstandingExposure()` would make every
concentration cap in the underwriting policy advisory.

Same family as
[verify-a-write-actually-happened](verify-a-write-actually-happened.md): a control
that reports success without observing current state is not a control.
