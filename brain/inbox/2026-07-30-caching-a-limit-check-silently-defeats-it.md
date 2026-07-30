---
type: Observation
title: Caching the read behind a limit or authorization check silently defeats it
description: A cached exposure or entitlement figure leaves the check in place and running, but deciding on stale data. The control appears to work and does not.
kind: failure-mode
proposed_layer: meta
observed_in: trikin
tags: [caching, nextjs, correctness, limits, security]
status: draft
not:
  - term: "unstable_cache(fetchOutstandingExposure, key, { revalidate: 3600 })"
    why: "the limit still gets compared, against an hour-old number — so N concurrent requests all pass a cap that only one of them should have"
    instead: "read it live, mark the route `export const dynamic = \"force-dynamic\"`, and grep-test that the cache helper never appears on these paths"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: broker-actions, resource: "projects/trikin/web/src/app/[role]/dashboard/(broker)/broker-actions.ts:100-105", title: "unstable_cache with 1-hour revalidate wrapping a data read — the established house pattern" }
  - { id: property-actions, resource: "projects/trikin/web/src/app/[role]/dashboard/(property)/property-actions.ts:82", title: "the same pattern, second occurrence" }
---

# Observation

Caching a *display* query is fine. Caching the query that a limit, quota,
entitlement, or concentration check reads is a correctness hole with no symptom.

The check is still there. It still executes. It still compares against the
threshold. It just compares against a number from up to an hour ago — so every
request inside the window sees the same pre-decision state, and a cap that should
admit one purchase admits as many as arrive before revalidation.

Nothing errors, nothing logs, and code review sees a limit check because there is
one.

# Why it matters

The danger is that caching arrives as a *house pattern* for a benign reason and then
gets copied onto a path where it is not benign. In the repo this came from,
`unstable_cache(..., { revalidate: 3600 })` was the established idiom for dashboard
reads — entirely reasonable for a leads table. The successor product computes
regulated exposure limits over the same query layer, and the idiom is sitting right
there to be copied.

So the countermeasure is not "remember not to do this". It is a grep test that fails
the build when the cache helper appears under the underwriting or money-path
modules, plus `force-dynamic` on those routes. Enforce it where the temptation is,
because the person who reaches for it will be reaching for consistency with the rest
of the codebase.

Related: [[verify-a-write-actually-happened]] — same family. A control that reports
success without observing current state is not a control.

# Evidence

`(broker)/broker-actions.ts:100`:

```ts
const cachedGetLeads = unstable_cache(
  async () => getLeadsByBroker(...),
  [cacheKey],
  { revalidate: 3600 }
);
```

Harmless here. Identical shape over `getOutstandingExposure()` would make every
concentration cap in the underwriting policy advisory.
