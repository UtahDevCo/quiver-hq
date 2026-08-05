---
type: Observation
title: Check an externally-generated file against an explicit maximum before ingesting it
description: A provider-generated export has no size contract, so ingest should compare size or object count to a stated cap and fail with a user-readable reason rather than discovering the limit as an OOM.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [external-apis, ingest, resource-limits, background-jobs, error-messages]
status: draft
not:
  - term: "streaming a provider export straight into the parser and trusting it to be a reasonable size"
    why: "there is no size contract on a provider-generated file; the ceiling gets discovered as an OOM or a timeout, which reads as an infrastructure fault rather than an oversized input"
    instead: "compare size or object count to an explicit named maximum before processing, and fail the job with a user-readable reason"
  - term: "skipping the check when the provider's metadata doesn't report a size"
    why: "absence of a reported size is the case most likely to be unbounded, not the case that's safe"
    instead: "enforce the cap while streaming the download, aborting once it's exceeded"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Cap externally-generated files before ingesting them'" }
  - { id: shopify-orders, resource: "projects/zamp/domains/.../shopify/orders.ts", title: "fails syncs above MAX_ZAMP_OBJECT_COUNT with a 'File too large' reason" }
---

# Observation

When a sync pulls a provider-generated file — a bulk-operation result, a report
export — check its size or object count against an explicit, named maximum before
processing it, and fail the job with a reason a user can read.

When the provider's metadata doesn't report a size up front, enforce the cap while
streaming the download rather than skipping the check.

# Why it matters

An unbounded input becomes an infrastructure symptom. Without a cap, the ceiling
is discovered as an out-of-memory kill or a timeout — which points the
investigation at memory limits, container sizing, and retry behavior, none of
which are the cause. With a cap, the same event produces "File too large," which
points at the actual input and is something a user or support engineer can act on.

The named-constant part matters too: `MAX_ZAMP_OBJECT_COUNT` is reviewable and
tunable, where an implicit limit imposed by available memory is neither.

The streaming case is the one most often skipped, and it is the one that most needs
the check — a provider that won't tell you how big the file is has given you no
reason to assume it's small.

# Evidence

`patterns.md` cites zamp's `shopify/orders.ts`, which fails syncs above
`MAX_ZAMP_OBJECT_COUNT` with a "File too large" sync-history reason, as the
established precedent to follow for other providers.

Proposed `meta`: "bound your inputs at the trust boundary and fail with an
actionable message" is general. The vendor and constant name are illustrative.
Related to the polling observation filed the same day — both are about not
assuming things about an external provider's behavior.
