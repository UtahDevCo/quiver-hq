---
type: Observation
title: Wiley ships by committing to main, not by opening a pull request
description: Chris asked for the quiet-hours copy fix to be committed straight to main and deployed; PRs are optional here, and a push to main is itself the deploy.
kind: decision
proposed_layer: project
proposed_project: wiley
observed_in: wiley
tags: [workflow, git, deploy, apphosting]
status: draft
not:
  - term: "open a PR and wait for review before landing a fix in wiley"
    why: "Chris's stated workflow is to commit on main; a PR adds a review gate he did not ask for and delays the deploy, since a push to main is what triggers the rollout"
    instead: "commit to main and push; open a PR only when you specifically want a review or a durable write-up of a large change"
generated: { by: claude/opus-5, at: 2026-07-30T16:17:33Z }
sources:
  - { id: chris-directive, resource: "human:christopher, 2026-07-30 session", title: "\"Don't worry about PRs, just do it all on main and push/deploy as quickly as you can.\"" }
  - { id: backend, resource: "firebase apphosting backend wiley-web, projects/wiley-phone/locations/us-central1", title: "GitHub-linked to UtahDevCo-wiley, rootDirectory /web — a push to main produces a build and rollout automatically" }
  - { id: rollout, resource: "rollout-2026-07-29-001 / build-2026-07-29-001", title: "build source.codebase.hash 316e5ce matched the merge commit, confirming main is the deploy trigger" }
---

**Wiley is a solo repo. `main` is the working branch and pushing to it deploys.**
Do not default to the branch-and-PR flow here.

Chris, 2026-07-30: *"Don't worry about PRs, just do it all on main and push/deploy
as quickly as you can."*

**Why:** Wiley's App Hosting backend `wiley-web` is linked to the GitHub repo, so a
push to `main` creates a build and a rollout with no further action. A PR
therefore does not gate a deploy — it only delays one, and adds a review step to a
repo with a single developer. Branching still happened four times in one session
before this was stated, which cost real time.

**How to apply:**

- Commit to `main` and push. Reach for a PR only when you specifically want review,
  or when a change is large enough that the PR body is worth having as a record.
- Verify the deploy by **provenance, not timing**: read the build's
  `source.codebase.hash` and match it to your commit. Correlating "a rollout
  happened shortly after I pushed" is a guess about the trigger.
- Committing straight to `main` removes the PR safety net, so the local checks
  matter more, not less. Run the typecheck and the relevant verification script
  *before* pushing — there is no reviewer between you and production.
- **This repo's working tree is frequently dirty with another session's
  in-progress work.** Since `main` is checked out there, `git commit` can sweep up
  changes that are already staged. Print `git diff --cached --stat` and read it
  before every commit, or use a separate `git worktree` when the tree is dirty.
  See [git-commit-commits-the-index-not-your-paths](2026-07-29-git-commit-commits-the-index-not-your-paths.md).
