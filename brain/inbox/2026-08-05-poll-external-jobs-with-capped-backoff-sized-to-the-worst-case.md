---
type: Observation
title: Size an external-job poll to the provider's worst case with capped exponential backoff, not fixed interval times fixed count
description: A fixed-interval, fixed-attempt poll loop silently encodes a guess about provider latency in its attempt ceiling; exponential backoff with a cap decouples the total window from the polling granularity.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [background-jobs, polling, external-apis, backoff, durable-workflows]
status: draft
not:
  - term: "for (let i = 0; i < 30; i++) { await sleep(10_000); ... }"
    why: "the attempt count and interval jointly encode a maximum wait (5 minutes here) that nobody stated or reviewed; when the provider takes longer the job fails as if the report were broken"
    instead: "back off exponentially with a cap, and size the total window to the provider's realistic worst case"
  - term: "polling a provider that offers a completion webhook"
    why: "spends attempts and latency reproducing a signal the provider will push for free"
    instead: "subscribe to the webhook; fall back to polling only where no callback exists"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Poll external async jobs with capped exponential backoff, sized to the provider's worst case'" }
  - { id: shopify-bulk, resource: "projects/zamp/domains/.../shopify", title: "Shopify bulk operations expose a completion webhook, so polling is unnecessary there" }
---

# Observation

When polling an external provider for job completion — report generation, bulk
export — don't reach for a fixed-interval loop with a fixed attempt count. Two
changes:

1. **Size the total window to the provider's realistic worst case.** Some
   providers' report generation is measured in hours, not minutes.
2. **Back off exponentially with a cap**, so early polls stay responsive for the
   common fast case while the tail doesn't overshoot into pointless requests.

In a durable workflow engine, long sleeps are free — the run is suspended, not
holding a process — so a multi-hour window costs nothing but patience.

And if the provider offers a completion webhook, prefer it over polling entirely.

# Why it matters

The failure mode is a misattributed error. `attempts × interval` is an implicit
timeout that nobody wrote down and no reviewer evaluated. When the provider
legitimately takes longer than that product, the job doesn't report "still
waiting" — it reports failure, and the failure looks like the provider's report
being broken or missing. The fix then gets attempted at the wrong layer: retry
logic, error handling, alerting thresholds, anywhere except the number that
actually caused it.

Making the window explicit and generous converts that class of incident into a
slow success.

The corollary is that fixed intervals are also wrong in the other direction: a
10-second interval is wasteful for a job that usually takes two hours, and too
slow for one that usually takes four seconds. Backoff handles both ends.

# Evidence

`patterns.md` records this against zamp's Amazon report-generation sync (generation
can take hours) and notes that Shopify bulk operations offer a completion webhook
and should use it instead of polling. `step.sleep` is durable in Inngest, which is
what makes the long window cheap there.

Proposed `meta`: the reasoning is about external async jobs and backoff generally.
The specific durable-sleep mechanism is engine-dependent, but the shape of the
mistake is not — the vendor names are illustrative rather than load-bearing.
