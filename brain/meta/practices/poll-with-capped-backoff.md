---
type: Practice
title: Size an external-job poll to the provider's worst case, with capped exponential backoff
description: attempts × interval is an unstated timeout nobody reviewed; when the provider legitimately runs long the job reports failure and the fix gets attempted at the wrong layer.
tags: [background-jobs, polling, external-apis, backoff, durable-workflows]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "for (let i = 0; i < 30; i++) { await sleep(10_000); ... }"
    why: "the attempt count and interval jointly encode a five-minute maximum that nobody stated or reviewed; a slower provider run reports as a failed job"
    instead: "back off exponentially with a cap, and size the total window to the provider's realistic worst case"
  - term: "polling a provider that offers a completion webhook"
    why: "spends latency and attempts reproducing a signal the provider will push for free"
    instead: "subscribe to the webhook; poll only where no callback exists"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Poll external async jobs with capped exponential backoff'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

When polling an external provider for job completion — report generation, bulk
export — don't use a fixed interval with a fixed attempt count. Two changes:

1. **Size the total window to the provider's realistic worst case.** Some providers'
   report generation is measured in hours, not minutes.
2. **Back off exponentially with a cap,** so early polls stay responsive for the
   common fast case while the tail doesn't overshoot into pointless requests.

In a durable workflow engine, long sleeps are free — the run is suspended rather than
holding a process — so a multi-hour window costs nothing but patience.

If the provider offers a completion webhook, prefer it over polling entirely.

# Why the failure is misattributed

`attempts × interval` is an implicit timeout that nobody wrote down and no reviewer
evaluated. When the provider legitimately exceeds that product, the job doesn't
report "still waiting" — it reports failure, and the failure looks like the report
being broken or missing.

So the fix gets attempted at the wrong layer: retry counts, error handling, alert
thresholds, anywhere except the number that actually caused it. Making the window
explicit and generous converts that whole class of incident into a slow success.

The corollary: fixed intervals are wrong in both directions. Ten seconds is wasteful
for a job that usually takes two hours and too slow for one that usually takes four.
Backoff handles both ends with one expression.

# Scope

Recorded against a durable workflow engine, where suspended sleeps make a long
window cheap. Without durable sleeps the same shape holds but a long window costs a
held worker, so the trade is real — prefer the webhook harder in that case.
