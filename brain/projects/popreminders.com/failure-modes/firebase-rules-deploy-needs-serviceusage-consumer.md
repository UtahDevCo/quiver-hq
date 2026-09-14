---
type: Failure Mode
title: Deploying Firestore rules with a service account needs serviceUsageConsumer, not just the two obvious roles
description: firebase deploy --only firestore:rules,firestore:indexes runs an API-enabled preflight against serviceusage.googleapis.com, so the SA needs roles/serviceusage.serviceUsageConsumer on top of firebaserules.admin + datastore.indexAdmin, or it 403s before deploying anything.
kind: failure-mode
tags: [ci, firebase, firestore, iam, service-account, gcp]
generated: { by: claude/opus-4.8, at: 2026-09-03T13:06:03Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: workflow
    resource: projects/popreminders.com/.github/workflows/deploy-firestore.yml
    title: CI deploys firestore:rules,firestore:indexes with the FIREBASE_SERVICE_ACCOUNT key
    last_modified: 2026-09-03
  - id: failing-run
    resource: https://github.com/deltaepsilon/popreminders.com/actions/runs/33756571666
    title: Deploy step 403 "Permission denied to get service [firestore.googleapis.com]" before granting serviceUsageConsumer
    last_modified: 2026-09-03
---

# Failure Mode

`firebase deploy --only firestore:rules,firestore:indexes` with a service-account key
(`GOOGLE_APPLICATION_CREDENTIALS`) runs an "is the Firestore API enabled" preflight
against `serviceusage.googleapis.com` before it deploys. If the SA lacks
`serviceusage.services.get`, that preflight 403s and the deploy exits 1 having touched
nothing:

```
Error: Request to https://serviceusage.googleapis.com/v1/projects/<proj>/services/
firestore.googleapis.com had HTTP Error: 403, Permission denied to get service
[firestore.googleapis.com]
```

The minimal role set for a rules+indexes deploy is three roles, not two:
- `roles/firebaserules.admin` — deploy the rules
- `roles/datastore.indexAdmin` — deploy the indexes
- `roles/serviceusage.serviceUsageConsumer` — pass the API-enabled preflight (the one
  that's easy to miss)

# Why it matters

The two "obvious" roles (firebaserules.admin + datastore.indexAdmin) are what every
doc mentions, so you grant those and the deploy still fails — with an error about
`serviceusage`, not about rules or indexes, so it looks like a project-config or
API-not-enabled problem rather than a missing role on the deployer. The `firebase-
adminsdk` default SA does NOT carry serviceUsageConsumer, so using that key out of the
box hits this. Cost here: one CI round plus a detour reading the serviceusage 403 as an
"enable the API" problem.

# Evidence

Run 33756571666: SA had firebaserules.admin + datastore.indexAdmin, deploy step failed
with the serviceusage 403. After `gcloud projects add-iam-policy-binding ... --role
roles/serviceusage.serviceUsageConsumer`, run 33756962428 deployed rules+indexes green
in 33s with no other change.

not:
  - term: "grant the SA firebaserules.admin + datastore.indexAdmin and expect rules deploy to work"
    why: "the deploy's serviceusage preflight 403s without serviceUsageConsumer; the error names serviceusage, not rules"
    instead: "also grant roles/serviceusage.serviceUsageConsumer (three roles total) on the deploying SA"
