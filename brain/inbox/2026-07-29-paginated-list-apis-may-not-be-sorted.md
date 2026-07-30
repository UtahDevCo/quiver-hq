---
type: Observation
title: A paginated list endpoint may not be sorted, so a page limit can hide the newest record
description: Sorting a truncated page client-side made a live deploy look like it had never triggered; the newest rollout was simply not in the first 40 results.
kind: failure-mode
proposed_layer: meta
observed_in: wiley
tags: [api, pagination, verification, deploy]
status: draft
not:
  - { term: "sort a pageSize-capped response by createTime and read the top as newest", why: "the API paginates in an order unrelated to createTime, so truncation drops records that sorting cannot recover", instead: "page until exhausted or use a server-side orderBy; re-run uncapped before reporting that something is absent" }
generated: { by: claude/opus-5, at: 2026-07-29T23:45:00Z }
sources:
  - { id: rollouts, resource: "firebaseapphosting.googleapis.com v1beta .../backends/wiley-web/rollouts", title: "pageSize=40 omitted rollout-2026-07-29-001; pageSize=100 returned it as SUCCEEDED" }
  - { id: builds, resource: "firebaseapphosting.googleapis.com v1beta .../backends/wiley-web/builds", title: "the independent endpoint that contradicted the false negative" }
---

# A paginated list endpoint may not be sorted, so a page limit can hide the newest record

I queried Firebase App Hosting for rollouts with `pageSize=40`, sorted the
response by `createTime` myself, and concluded **no deploy had been triggered** by
a merge 10 minutes earlier. I was about to tell the user auto-deploy wasn't
configured and ask permission to deploy manually.

Re-querying with `pageSize=100` returned `rollout-2026-07-29-001 | SUCCEEDED`,
created 20 seconds after the merge. The deploy had been live the whole time.

The API paginates in an order unrelated to `createTime`, so the newest record was
not in the first 40. Sorting *after* truncation cannot recover what truncation
dropped.

**Why:** client-side sorting creates the illusion of a complete ordered view. The
response looks authoritative — it's sorted, it's from the API, the newest entry is
at the top — and the truncation is invisible because a short page and a genuinely
short list are indistinguishable in the output. I then built a polling monitor
around the same `pageSize=40` query, so it would have kept reporting the false
negative until it timed out and printed a confidently wrong conclusion.

**How to apply:**

- **Sort server-side or fetch everything.** Use the API's `orderBy` if it has one.
  If it doesn't, page until exhausted; do not sort a truncated page and treat the
  top as the newest.
- **Absence found via a capped query is not evidence of absence.** Before reporting
  "there is no X", re-run without the cap. Cheap, and it's the difference between
  a fact and a guess.
- **Corroborate a negative from an independent angle.** The *builds* endpoint
  showed `build-2026-07-29-001 | READY | branch: main` — that contradicted my
  "no deploy" conclusion and is what made me re-query. One endpoint's silence
  should not outweigh another's positive.
- **Verify a deploy by provenance, not by timing.** Correlating "rollout happened
  20s after a commit" is a guess about the trigger. Reading the build's
  `source.codebase.hash` and matching it to the merge commit is proof of what is
  actually running.

Related: [audits-must-report-their-own-coverage](../meta/failure-modes/audits-must-report-their-own-coverage.md),
[a-listing-endpoint-is-not-the-uniqueness-domain](../meta/failure-modes/a-listing-endpoint-is-not-the-uniqueness-domain.md)
