---
type: Failure Mode
title: A collectionGroup() query needs a COLLECTION_GROUP-scoped index, not the automatic one
description: Firestore auto-indexes single fields at COLLECTION scope only; a collectionGroup query with a filter fails at runtime until you add a COLLECTION_GROUP fieldOverride.
kind: failure-mode
tags: [firestore, indexes, collection-group, cloud-functions, deploy]
generated: { by: claude/opus-4.8, at: 2026-09-01T16:53:13Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/popreminders.com/firestore.indexes.json
    title: fieldOverride added for reminders.state (COLLECTION_GROUP)
    last_modified: 2026-09-01
  - id: commit
    resource: https://github.com/deltaepsilon/popreminders.com/commit/a1c65f8
    title: "Add collection-group index for reminders.state"
---

# Failure Mode

A Firestore `collectionGroup('X').where(...)` (or `.orderBy(...)`) query requires an
explicit **COLLECTION_GROUP-scoped** single-field index. Firestore's automatic
single-field indexes are **COLLECTION-scoped only**, so a collection-group query on the
same field is *not* auto-indexed. Declare it as a `fieldOverrides` entry in
`firestore.indexes.json` and deploy it:

```json
{
  "fieldOverrides": [
    {
      "collectionGroup": "reminders",
      "fieldPath": "state",
      "indexes": [
        { "order": "ASCENDING", "queryScope": "COLLECTION" },
        { "order": "DESCENDING", "queryScope": "COLLECTION" },
        { "order": "ASCENDING", "queryScope": "COLLECTION_GROUP" }
      ]
    }
  ]
}
```

Keep the two COLLECTION-scoped entries too: overriding a field replaces its automatic
indexing, so omitting them silently drops the defaults.

After deploy, the index takes a few minutes to build. During that window the query keeps
failing, but the error text changes to "That index is not ready yet." A tiny dataset
still takes 1-5 minutes.

# Why it matters

The query typechecks, builds, and deploys with zero warnings. It fails **only at
runtime, only on prod**, with `9 FAILED_PRECONDITION: The query requires a
COLLECTION_GROUP_ASC index for collection X and field Y`. No local check catches it: an
emulator-less deploy, `tsc`, and the functions build all pass. If the function swallows
or only logs its errors (a scheduled function does), the symptom is silent: the job runs
every minute, throws every minute, and does zero work, while every other signal says
"deployed successfully."

# Evidence

popreminders.com Phase 3: the scheduled `everyMinuteTick` ran
`collectionGroup('reminders').where('state','in',['calm','due','nudging','snoozed'])` to
drive reminder state. Deploy succeeded; both functions showed ACTIVE. But every tick
logged `Error: 9 FAILED_PRECONDITION: The query requires a COLLECTION_GROUP_ASC index for
collection reminders and field state` and advanced zero reminders. Adding the
`fieldOverrides` entry and waiting for the build fixed it: the next tick logged
`everyMinuteTick: scanned 1, advanced 1, pushed 1` and the test reminder moved
`due → nudging` with `nudgesSent: 1`.

# Not

not:
  - term: "relying on the automatic single-field index for a collectionGroup query"
    why: "automatic single-field indexes are COLLECTION-scoped; collectionGroup queries need COLLECTION_GROUP scope, which is never auto-created"
    instead: "add a fieldOverrides entry with queryScope COLLECTION_GROUP and deploy firestore:indexes"
  - term: "trusting a green `firebase deploy` as proof the scheduled query works"
    why: "the query fails only at runtime on prod; deploy, tsc, and the functions build all pass"
    instead: "read the function's execution logs once after deploy and confirm it did work, not just that it started"
