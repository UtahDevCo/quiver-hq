---
type: Failure Mode
title: A page of a listing is not the population
description: pageSize=40 hid a live deploy, pageSize=200 returned 100 of 272 rollouts, and pageSize=300 returned 8 of 12 Firestore documents because one had grown to 880 KiB. Only nextPageToken tells you the page was partial.
tags: [api, pagination, firestore, coverage, verification, deploy]
generated: { by: claude/opus-5, at: 2026-07-29T23:45:00Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
not:
  - term: "sorting a pageSize-capped response by createTime and reading the top as the newest"
    why: "the API paginates in an order unrelated to createTime, so truncation drops records that client-side sorting cannot recover"
    instead: "follow nextPageToken until it is absent, or use a server-side orderBy, and re-run paged to exhaustion before reporting that something is absent"
  - term: "raising pageSize to avoid paginating"
    why: "the server caps the page — pageSize=200 returned 100 of 272 rollouts plus a nextPageToken, so the record needed was still missing"
    instead: "loop on nextPageToken until it is absent; a larger pageSize only moves the cliff"
  - term: "pageSize=300 on a 12-document collection returns all 12"
    why: "the Firestore REST list bounds the response by serialized size, so one ~900 KiB document pushes later documents onto the next page"
    instead: "loop on nextPageToken regardless of how generous pageSize looks, because the cap is on bytes and your data grows"
  - term: "deriving a denominator or a total from a single page"
    why: "the number is quietly a floor, and it shrinks as your documents grow rather than staying wrong by a fixed amount"
    instead: "page to exhaustion before publishing a count, and say which figures came from an exhausted read"
sources:
  - id: rollouts
    resource: "firebaseapphosting.googleapis.com v1beta .../backends/wiley-web/rollouts"
    title: "pageSize=40 omitted rollout-2026-07-29-001; pageSize=100 returned it as SUCCEEDED"
    author: claude/opus-5
    last_modified: 2026-07-29
  - id: builds
    resource: "firebaseapphosting.googleapis.com v1beta .../backends/wiley-web/builds"
    title: the independent endpoint that contradicted the false negative
    author: claude/opus-5
    last_modified: 2026-07-29
  - id: probe
    resource: "GET https://firestore.googleapis.com/v1/projects/k1-2026/databases/(default)/documents/projectIngestStates?pageSize=300"
    title: Returned 8 of 12 documents with nextPageToken set
    author: claude/opus-5
    last_modified: 2026-08-05
  - id: related-concept
    resource: brain/meta/failure-modes/audits-must-report-their-own-coverage.md
    title: Audits must report their own coverage
    last_modified: 2026-08-05
---

# The trap

A single-request listing is a sample. Two independent mechanisms make it a subset
of the population while looking exactly like the whole thing.

**No guaranteed sort.** I queried Firebase App Hosting for rollouts with
`pageSize=40`, sorted the response by `createTime` myself, and concluded no deploy
had been triggered by a merge 10 minutes earlier. Re-querying with `pageSize=100`
returned `rollout-2026-07-29-001 | SUCCEEDED`, created 20 seconds after the merge.
The deploy had been live the whole time. The API paginates in an order unrelated to
`createTime`, and sorting after truncation cannot recover what truncation dropped.

**A byte cap independent of pageSize.** The Firestore REST
`documents/{collection}` list bounds each response by serialized size. Asking for
300 documents from a collection holding 12 returned 8, with `nextPageToken` set.
The same collection had returned 9 an hour earlier, before one document grew from
roughly 530 KiB to 880 KiB, which was enough to push a later document onto page
two.

# Why a bigger pageSize is not the fix

That is the fix I reached for, and I hit the same endpoint again the next day.
`pageSize=200` returned **100** rollouts and a `nextPageToken`: the server caps the
page and says so in a field the caller has to notice. 272 rollouts across 3 pages,
and the one I needed was on page 3. A larger number moves the cliff and feels like
diligence.

Under the byte cap it is worse, because the cliff moves on its own. A page that
holds today shrinks as documents grow, so a query that was exhaustive when written
becomes partial without anyone touching it.

# What the wrong reading costs

The truncated rollout query was about to become "auto-deploy isn't configured, may
I deploy manually", and I had already built a polling monitor around the same
`pageSize=40` query, so it would have kept reporting the false negative until it
timed out on a confidently wrong conclusion.

The Firestore listing produced the opposite error: a document I had seen an hour
earlier was absent, so I concluded it had been deleted mid-run. It was on page two,
its extraction rows intact, which I established only by querying a second store.
The document was still being written to 25 seconds before the listing that omitted
it, which is what made the deletion theory testable and then false.

Two figures I had already reported and used in an argument were wrong for this
reason. Corrected against an exhausted read, the totals moved by 3 projects and
420 files.

# What to do instead

- Follow `nextPageToken` until it is absent. That is the only thing that terminates.
- Sort server-side with the API's `orderBy` where one exists. Where none exists,
  page to exhaustion.
- Absence found through a capped query is not evidence of absence. Re-run without
  the cap before reporting that something is missing.
- Corroborate a negative from an independent angle. The *builds* endpoint showed
  `build-2026-07-29-001 | READY | branch: main`, which contradicted the "no deploy"
  conclusion and is what prompted the re-query.
- Verify a deploy by provenance rather than timing. "Rollout happened 20s after a
  commit" guesses at the trigger; reading the build's `source.codebase.hash` and
  matching it to the merge commit proves what is running.

A count from one page is a coverage claim, which puts this under
[audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md):
an unexhausted listing is a skip the audit never recorded. Where the disagreement is
between what a read can see and what a write enforces, see
[a-listing-endpoint-is-not-the-uniqueness-domain](a-listing-endpoint-is-not-the-uniqueness-domain.md).
