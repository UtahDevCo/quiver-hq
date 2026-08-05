---
type: Practice
title: Check an externally-generated file against an explicit maximum before ingesting it
description: Without a stated cap the ceiling is discovered as an OOM or timeout, which reads as an infrastructure fault rather than an oversized input.
tags: [external-apis, ingest, resource-limits, background-jobs, error-messages]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "streaming a provider export straight into the parser and trusting it to be a reasonable size"
    why: "there is no size contract on a provider-generated file; the ceiling surfaces as an OOM or timeout, which points the investigation at memory limits instead of at the input"
    instead: "compare size or object count to an explicit named maximum first, and fail the job with a user-readable reason"
  - term: "skipping the check when the provider's metadata doesn't report a size"
    why: "an unreported size is the case most likely to be unbounded, not the case that's safe"
    instead: "enforce the cap while streaming the download, aborting once it is exceeded"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Cap externally-generated files before ingesting them'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

When a job pulls a provider-generated file — a bulk-operation result, a report export
— check its size or object count against an explicit, named maximum before processing
it, and fail with a reason a user can read.

When the provider doesn't report a size up front, enforce the cap while streaming the
download rather than skipping it.

# Why an unbounded input becomes an infrastructure symptom

Without a cap, the ceiling is discovered as an out-of-memory kill or a timeout. That
points the investigation at container sizing, memory limits, and retry behavior —
none of which are the cause. With a cap, the same event produces "File too large,"
which names the actual problem and is something support can act on without an
engineer.

The named constant matters too: an explicit maximum is reviewable and tunable, where
a limit imposed implicitly by available memory is neither, and changes silently when
the runtime is resized.

The streaming case is the one most often skipped and the one that most needs the
check — a provider that won't tell you how big the file is has given you no reason to
assume it's small.

# Relation

The same posture as [poll-with-capped-backoff](poll-with-capped-backoff.md): don't
infer a bound on an external provider's behavior from the cases you have seen. State
the bound, enforce it, and fail legibly when it's crossed.
