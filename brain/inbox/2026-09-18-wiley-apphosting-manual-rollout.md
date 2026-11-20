---
type: Observation
title: Wiley App Hosting does not auto-deploy on push; use a manual git rollout
description: A push to main does not deploy wiley-web; run apphosting:rollouts:create and verify via Cloud Run, not the stale App Hosting list APIs.
kind: decision
proposed_layer: project
proposed_project: wiley
tags: [deploy, apphosting, firebase, wiley, gotcha]
generated: { by: claude/opus-4.8, at: 2026-09-18T17:04:11Z }
status: draft
sources:
  - id: undeployed-backlog
    resource: "git log projects/wiley, 2026-09-10..2026-09-17"
    title: "7 commits (cards #60/#62/#63 incl. a billing change) sat undeployed until a manual rollout"
    last_modified: 2026-09-18
  - id: rollout-cmd
    resource: "firebase-tools apphosting:rollouts:create wiley-web --git-commit <sha> --force --project wiley-phone"
    title: "Command that actually deploys"
    last_modified: 2026-09-18
  - id: stale-list-api
    resource: "GET firebaseapphosting.googleapis.com/v1/.../backends/wiley-web/{rollouts,builds}"
    title: "List endpoints returned only builds up to 2026-09-09 while newer builds were live"
    last_modified: 2026-09-18
  - id: existing-note
    resource: projects/wiley/.brain/decisions/wiley-ships-on-main-not-by-pull-request.md
    title: "Prior note claims push-to-main is the deploy trigger — now false"
    last_modified: 2026-07-30
---

# Observation

Pushing to `main` does **not** deploy the Wiley web app. The App Hosting backend
`wiley-web` (project `wiley-phone`) does not roll out on push in practice. To
deploy, create a rollout from a specific commit:

```
npx firebase-tools apphosting:rollouts:create wiley-web --git-commit <sha> --force --project wiley-phone
```

Verify the serving build by ground truth, not by the rollout CLI's success line:

1. `GET run.googleapis.com/v2/projects/wiley-phone/locations/us-central1/services/wiley-web`
   → `latestReadyRevision` (its name embeds the build id, e.g. `wiley-web-build-2026-09-18-011`).
2. `GET firebaseapphosting.googleapis.com/v1/projects/wiley-phone/locations/us-central1/backends/wiley-web/builds/<build-id>`
   → match `source.codebase.hash` to your commit.

The App Hosting REST **list** endpoints for rollouts and builds are stale/cached:
during this session they showed nothing newer than 2026-09-09 while builds from
today were provably serving. Use the direct-GET + Cloud Run path above instead.

This contradicts the existing decision note
`wiley-ships-on-main-not-by-pull-request` (2026-07-30), which says a push is
itself the deploy. Reconcile the two on promotion — the deploy trigger changed.

# Why it matters

The stale assumption cost real coverage: 7 commits from 2026-09-10 to 2026-09-17,
including a billing behavior change (card #60, charge on signup day), sat
undeployed for up to a week. Anyone trusting "push = deploy" ships nothing and
believes they shipped. Trusting the App Hosting list API to confirm a deploy also
fails silently, because it lags days behind reality.

# Evidence

- `git log` showed commits `1d06abc..cca97c7` (Sep 10-15) with the newest App
  Hosting build dated Sep 9 until a manual rollout was fired.
- After `apphosting:rollouts:create`, Cloud Run `latestReadyRevision` advanced to
  `wiley-web-build-2026-09-18-0NN` and the build's `source.codebase.hash` matched
  the pushed commit, while the rollouts/builds LIST API still showed Sep 9 as newest.

# not

- term: "push to main, assume App Hosting auto-deploys"
  why: "wiley-web does not roll out on push; the change never reaches production"
  instead: "fire apphosting:rollouts:create --git-commit <sha> and verify via Cloud Run latestReadyRevision + build hash"
- term: "confirm a deploy with apphosting:rollouts:list / builds:list"
  why: "those list endpoints are cached and lagged days behind live builds"
  instead: "direct-GET the specific build and match source.codebase.hash"
