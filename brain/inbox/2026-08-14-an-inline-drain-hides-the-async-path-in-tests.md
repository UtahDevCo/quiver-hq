---
type: Observation
title: A synchronous inline drain masks the async fallback in any small-batch test
description: When the request that enqueues work also drains a slot's worth inline, a batch small enough to finish inline never exercises the async/scheduled drainer, so a test on a small batch verifies the wrong path.
kind: failure-mode
proposed_layer: meta
proposed_project: k1
tags: [testing, ingestion, queues, verification, background-jobs]
generated: { by: claude/opus-4-8, at: 2026-08-14T19:11:07Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/apps/web/app/api/projects/[tenantSlug]/[projectId]/uploads/route.ts
    title: Upload route drains its own queued batch inline before returning
    last_modified: 2026-08-14
  - id: context
    resource: projects/k1/docs/architecture/scheduled-drain.md
    title: Three drain callers, two of them user-triggered and synchronous
    last_modified: 2026-08-14
---

# Observation

If the request that enqueues work also drains a slot's worth of it inline (here: the upload
route claims and extracts up to `GOOGLE_INGESTION_MAX_ACTIVE` = 6 documents before returning),
then a background/scheduled drainer only ever has work to do when a batch is larger than one
request can finish. A test that uploads a small batch and then checks the scheduled drainer
will see it find nothing — not because the drainer is broken, but because the inline path
already finished the work. The test proves the wrong path.

Two aggravators made this worse in practice: (1) a second user-triggered caller (a browser
poll on the ingest-state route) kept draining for ~30s after the tab was "closed", because
closing a tab does not abort an in-flight server request; (2) the scheduled sweep ran on a
5-minute timer, so anything the inline + poll paths finished inside 5 minutes was invisible to
it. The signal that exposed it: the sweep's `projectsSeen`/`nothingQueued` counters never moved
after the upload — its view of the world was unchanged, which is different from "it drained and
found the queue empty".

To actually exercise the async path, the batch must exceed what the enqueuing request (plus any
stragglers) can drain before the async drainer runs — or drive the async endpoint directly.

# Why it matters

A green "the scheduled job works" result can be entirely produced by the synchronous path,
leaving the async fallback — the whole reason the job exists — unverified in production. Here
the scheduled drain had *never* dispatched a document across its entire history, yet ingestion
looked healthy, because every real upload was small enough to finish inline.

# Evidence

10-doc upload: all 10 reached terminal state, but the cron's `projectsSeen` stayed at 15 and
`nothingQueued` at 13 across the sweeps after the upload — unchanged, i.e. it never had work.
Confirmed the upload route awaits `drainQueuedIngestionRuns` inline (uploads/route.ts) and the
Google drain extracts synchronously via `Promise.all` before returning (google-workflows.ts).
Only a 29-doc batch with the tab genuinely closed left residual queued work for the async
(Cloud Tasks) path to pick up and prove.

# not

- term: "upload a handful of docs, close the tab, assert the scheduled drainer ran"
  why: "the inline drain + straggler polls finish a small batch before the scheduler fires"
  instead: "upload more than one request's slot count, or POST the async drain endpoint directly with residual work queued"
