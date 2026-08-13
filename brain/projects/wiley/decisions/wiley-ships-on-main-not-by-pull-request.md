---
type: Decision
title: Wiley ships by committing straight to main
description: Chris's stated workflow, 2026-07-30. The App Hosting backend wiley-web is GitHub-linked, so a push to main is itself the deploy; four branch-and-PR cycles in one session cost time before this was said.
tags: [workflow, git, deploy, apphosting]
generated: { by: claude/opus-5, at: 2026-07-30T16:17:33Z }
status: stable
not:
  - term: "open a PR and wait for review before landing a fix in wiley"
    why: "Chris's stated workflow is to commit on main; a PR adds a review gate he did not ask for and delays the deploy, since a push to main is what triggers the rollout"
    instead: "commit to main and push; open a PR only when you specifically want a review or a durable write-up of a large change"
sources:
  - { id: chris-directive, resource: "human:christopher, 2026-07-30 session", title: "\"Don't worry about PRs, just do it all on main and push/deploy as quickly as you can.\"", author: human:christopher }
  - { id: backend, resource: "firebase apphosting backend wiley-web, projects/wiley-phone/locations/us-central1", title: "GitHub-linked to UtahDevCo-wiley, rootDirectory /web — a push to main produces a build and rollout automatically" }
  - { id: rollout, resource: "rollout-2026-07-29-001 / build-2026-07-29-001", title: "build source.codebase.hash 316e5ce matched the merge commit, confirming main is the deploy trigger" }
---

# The decision

Wiley is a solo repo. `main` is the working branch, and pushing to it deploys.

Chris, 2026-07-30: *"Don't worry about PRs, just do it all on main and push/deploy
as quickly as you can."*

# Why

The App Hosting backend `wiley-web` is linked to the GitHub repo, so a push to `main`
creates a build and a rollout with no further action. A PR delays a deploy and adds a
review step to a repo with one developer. Four branch-and-PR cycles happened in a
single session before this was stated, which cost real time.

# How to apply

- Commit to `main` and push. Reach for a PR when you specifically want review, or when
  a change is large enough that the PR body is worth having as a record.
- Verify the deploy by provenance: read the build's `source.codebase.hash` and match it
  to your commit. Correlating "a rollout happened shortly after I pushed" is a guess
  about the trigger.
- Local checks matter more here, since committing straight to `main` removes the PR
  safety net. Run the typecheck and the relevant verification script before pushing.
- This repo's working tree is frequently dirty with another session's in-progress work,
  and `main` is what is checked out there, so `git commit` can sweep up changes that are
  already staged. Print `git diff --cached --stat` and read it before every commit, or
  use a separate `git worktree` when the tree is dirty.

# No stale_after

A decision is a historical fact, per the freshness table in
[conventions](../../../conventions.md). What can go stale is the deploy trigger: if
`wiley-web` stops being GitHub-linked, that is a new decision rather than an edit to
this one.
