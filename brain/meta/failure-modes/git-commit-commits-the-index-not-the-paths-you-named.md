---
type: Failure Mode
title: git commit commits the index, not the paths you named in git add
description: A one-file commit landed two files, because another session had already staged a deletion. The squash merge carried it to main and left package.json pointing at a script that no longer existed.
tags: [git, workflow, verification, parallel-sessions]
generated: { by: claude/opus-5, at: 2026-07-29T23:40:00Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "`git add <one-file>` followed by a bare `git commit`"
    why: "commit takes the entire index, including anything another session or a partially-completed `git add -p` had already staged"
    instead: "print `git diff --cached --stat` and read it, or use `git commit -- <paths>` to commit only those paths"
  - term: "reading `git status` output as noise when it shows files you did not touch"
    why: "on a machine running parallel agent sessions a dirty shared tree is the normal case, and the staged column is what decides your commit"
    instead: "treat unexpected modifications as information about who else is working here, and branch into a `git worktree` with its own index"
  - term: "completing the half-change you accidentally committed"
    why: "the deletion was one half of someone else's coherent change whose other half was still uncommitted; landing the rest is guessing at their intent"
    instead: "restore what you removed and leave their work where they left it"
sources:
  - id: incident
    resource: "projects/wiley commit d901c36, squash-merged to main as 316e5ce"
    title: a one-file commit that silently contained two files
    author: claude/opus-5
    last_modified: 2026-07-29
  - id: breakage
    resource: "projects/wiley web/package.json on main"
    title: left declaring the remediate:free-months script against a file the commit had deleted
    author: claude/opus-5
    last_modified: 2026-07-29
---

# The trap

`git commit` commits the whole index. Naming a path in `git add` scopes the
*staging*, and nothing about it scopes the commit.

```
git add web/scripts/verify-quiet-hours-repaired-accounts.ts
git commit -m "test(quiet-hours): re-check the 9 repaired accounts"
```

That commit contained two files. Another session had staged a deletion of
`web/scripts/remediate-free-months.ts`, so the deletion rode along, and the squash
merge carried it to `main`. `package.json` was left declaring
`"remediate:free-months": "bun ./scripts/remediate-free-months.ts"` against a file
that no longer existed.

# Why it survives review

Neither command mentions the pre-existing staged change in its output.
`git status --short` does show it, in a column (` M` versus `M `) that is easy to
skim past. The damage stays invisible until someone runs the missing script or
reads the merge diff, which on a squash merge is a diff nobody re-reads.

# What to do instead

- Print exactly what is about to land before every commit: `git diff --cached --stat`.
  If it lists a file you did not intend, stop. One line, and it makes the failure
  impossible.
- Prefer `git commit -- <paths>` or `git commit -o <paths>`, which commit only the
  named paths regardless of index state.
- Assume a shared working tree carries somebody else's work in progress.
- When you need to commit against a branch without disturbing a dirty tree, use a
  separate `git worktree`. It has its own index, so another session's staged changes
  cannot leak in and your `git checkout` cannot clobber their files.
- Repair by restoring what you removed. Finishing their change is guessing.

The class this belongs to is a write that reached production without being read
back, which is [verify-a-write-actually-happened](verify-a-write-actually-happened.md)
arriving through the version control system.
