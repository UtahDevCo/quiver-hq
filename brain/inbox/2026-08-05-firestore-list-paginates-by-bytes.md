---
type: Observation
title: A Firestore collection listing paginates by response bytes, not document count
description: pageSize far above the document count still truncates when one document is large, and nextPageToken is the only signal that the listing was partial.
kind: failure-mode
proposed_layer: meta
tags: [firestore, audits, coverage, pagination]
generated: { by: claude/opus-5, at: 2026-08-05T20:16:13Z }
status: draft
sources:
  - id: probe
    resource: "GET https://firestore.googleapis.com/v1/projects/k1-2026/databases/(default)/documents/projectIngestStates?pageSize=300"
    title: Returned 8 of 12 documents with nextPageToken set
    last_modified: 2026-08-05
  - id: related-concept
    resource: brain/meta/failure-modes/audits-must-report-their-own-coverage.md
    title: Audits must report their own coverage
    last_modified: 2026-08-05
not:
  - term: "pageSize=300 on a 12-document collection returns all 12"
    why: "the REST list caps the response by serialized size, so one ~900 KiB document can push later documents onto the next page"
    instead: "loop on nextPageToken until it is absent, regardless of how generous pageSize looks"
---

# Observation

The Firestore REST `documents/{collection}` list endpoint bounds each response by
serialized byte size as well as by `pageSize`. Asking for 300 documents from a
collection holding 12 returned 8, with `nextPageToken` set. The truncation is invisible
unless you check that token: the response is a well-formed list of real documents.

It is also unstable over time. The same collection returned 9 documents an hour earlier.
One document had grown from roughly 530 KiB to 880 KiB in between, which was enough to
push a later document onto page two.

# Why it matters

A single-page read of a collection is a coverage claim, and it can be wrong in the
direction that looks like data loss. I listed the collection, found a document I had seen
an hour earlier now absent, and concluded it had been deleted mid-run. It had not. It was
on page two. The extraction rows it owned were intact the whole time, and I only
established that by querying a second store.

The generic form: any listing API that bounds a response by bytes will silently return a
subset, and a subset that shrinks as your data grows. Deriving a denominator from one page
gives you a number that is quietly a floor. Two figures I had already reported and used in
an argument (project count and file totals) were wrong for exactly this reason.

# Evidence

```
?pageSize=50   -> 9 documents   (nextPageToken present, unchecked)
?pageSize=300  -> 8 documents   nextPageToken: True
paged to exhaustion -> 12 documents
```

The corrected totals differed from the single-page ones by 3 projects and 420 files. The
document that "disappeared" was still being written to 25 seconds before the listing that
omitted it, which is what made the deletion theory testable and then false.
