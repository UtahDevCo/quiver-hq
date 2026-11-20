---
type: Observation
title: Wiley push to main does not deploy; the ships-on-main decision note is stale
description: Deploy wiley-web with a git rollout from a commit, then verify via Cloud Run's latestReadyRevision, whose name is the build id with a "wiley-web-" prefix.
kind: decision
proposed_layer: project
proposed_project: wiley
tags: [deploy, apphosting, firebase, wiley, stale-doc]
generated: { by: claude/opus-5.5, at: 2026-10-06T21:09:03Z }
status: draft
sources:
  - id: stale-note
    resource: projects/wiley/.brain/decisions/wiley-ships-on-main-not-by-pull-request.md
    title: "Says the GitHub-linked backend makes a push to main the deploy; false since at least 2026-09"
    last_modified: 2026-07-30
  - id: prior-inbox
    resource: brain/inbox/2026-09-18-wiley-apphosting-manual-rollout.md
    title: "First observation of the manual-rollout requirement; this note extends it"
    last_modified: 2026-09-18
  - id: commit
    resource: "projects/wiley commit 53b1344cfb57b61112a4119469f91b6eb4d46c90"
    title: "feat(auth): 6-digit emailed login code, shipped 2026-10-06 via manual rollout"
    last_modified: 2026-10-06
  - id: build
    resource: "firebaseapphosting.googleapis.com/v1/projects/wiley-phone/locations/us-central1/backends/wiley-web/builds/build-2026-10-06-002"
    title: "state READY, source.codebase.hash 53b1344cfb57b61112a4119469f91b6eb4d46c90"
    last_modified: 2026-10-06
not:
  - term: "git push origin main means wiley-web is deployed"
    why: "wiley-web does not roll out on push; production keeps the previous build"
    instead: "apphosting:rollouts:create wiley-web --git-commit <sha>, then verify the build hash"
  - term: "strip a trailing segment from latestReadyRevision to get the build id"
    why: "the revision name is exactly wiley-web-<build-id>; stripping more yields a nonexistent build"
    instead: "remove only the 'wiley-web-' prefix"
---

# Observation

Pushing to `main` does not deploy wiley-web. The decision note
`wiley-ships-on-main-not-by-pull-request` still says it does, and should be
corrected on promotion (keep its "ship on main, no PRs" half, replace the
"push is the deploy" half).

Deploy after pushing:

```
npx firebase-tools apphosting:rollouts:create wiley-web --git-commit <sha> --force --project wiley-phone
```

On 2026-10-06 the build was READY within a few minutes. Verify by ground truth:

1. `GET run.googleapis.com/v2/projects/wiley-phone/locations/us-central1/services/wiley-web`
   and read `latestReadyRevision`.
2. The revision name is the build id with `wiley-web-` in front:
   `wiley-web-build-2026-10-06-002` means build `build-2026-10-06-002`. Strip only
   the prefix; there is no trailing suffix.
3. `GET .../backends/wiley-web/builds/<build-id>` and match
   `source.codebase.hash` to the pushed commit.
4. Fetch `https://app.wileyphone.com/`, pull a `/_next/static/chunks/*.js` URL,
   and confirm it returns 200 and contains a UI string from the change.

# Why it matters

An agent that trusts the decision note pushes and reports "deployed" while
production keeps the old build. The 2026-09-18 note records 7 commits, one of
them a billing change, sitting undeployed for up to a week that way.

# Evidence

- 2026-10-06: pushed `53b1344`, ran the rollout command, Cloud Run
  `latestReadyRevision` = `wiley-web-build-2026-10-06-002`, build
  `build-2026-10-06-002` READY with hash `53b1344cfb57…`. Live chunk
  `/_next/static/chunks/8b33b8e36cadac4f.js` returned 200 and contained
  "Email me a code".
- A first verification attempt stripped a trailing `-<suffix>` from the revision
  name, produced build id `build-2026-10-06`, and got an empty response.
