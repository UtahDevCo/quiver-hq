---
type: Observation
title: "`git add <file>` then `git commit` still commits everything already staged"
description: git commit commits the whole index, so a deletion another session had already staged rode along into my commit and reached main.
kind: failure-mode
proposed_layer: meta
observed_in: wiley
tags: [git, workflow, verification]
status: draft
not:
  - { term: "git add <one-file> then a bare git commit", why: "commit takes the entire index, including anything another session or a partial `git add -p` had already staged", instead: "print `git diff --cached --stat` and read it first, or use `git commit -- <paths>` to commit only those paths" }
generated: { by: claude/opus-5, at: 2026-07-29T23:40:00Z }
sources:
  - { id: incident, resource: "projects/wiley commit d901c36, squash-merged to main as 316e5ce", title: "a one-file commit that silently contained two files" }
  - { id: breakage, resource: "projects/wiley web/package.json on main", title: "left declaring the remediate:free-months script against a file the commit had deleted" }
---

# `git add <file>` then `git commit` still commits everything already staged

`git commit` commits **the whole index**, not the paths you just added. If
anything was already staged — by another agent session, a partially-completed
`git add -p`, or an editor integration — it rides along silently.

On Wiley I ran:

```
git add web/scripts/verify-quiet-hours-repaired-accounts.ts
git commit -m "test(quiet-hours): re-check the 9 repaired accounts"
```

The commit contained **two** files. Another session had already staged a deletion
of `web/scripts/remediate-free-months.ts`, so my commit deleted it too, and the
squash merge carried it to `main`. `main` was left declaring
`"remediate:free-months": "bun ./scripts/remediate-free-months.ts"` in
`package.json` against a file that no longer existed.

**Why:** naming a path in `git add` feels like it scopes the commit to that path.
It doesn't — it scopes the *staging*. Nothing in the output of either command
mentions the pre-existing staged change, and `git status --short` shows it in a
column (` M` vs `M `) that is easy to skim past. The damage is invisible until
someone runs the missing script or reads the merge diff.

**How to apply:**

- Before every commit, print exactly what is about to land:
  `git diff --cached --stat`. Read it. If it lists a file you did not intend,
  stop. This is a one-line habit that makes the failure impossible.
- Prefer `git commit -- <paths>` or `git commit -o <paths>`, which commit **only**
  the named paths regardless of index state.
- Assume a shared working tree is dirty with someone else's work. On a machine
  running parallel agent sessions this is the normal case, not the exception —
  `git status` showing modifications you didn't make is information, not noise.
- When you need to commit against a branch without disturbing a dirty tree, use a
  separate `git worktree`. It has its own index, so another session's staged
  changes cannot leak in and your `git checkout` cannot clobber their files.
- Repair by restoring, not by finishing someone else's change. The deletion was
  half of a coherent change whose other half (the `package.json` edit) was still
  uncommitted; landing the rest would have been guessing at their intent.

Related: [audits-must-report-their-own-coverage](../meta/failure-modes/audits-must-report-their-own-coverage.md),
[verify-a-write-actually-happened](../meta/failure-modes/verify-a-write-actually-happened.md)
