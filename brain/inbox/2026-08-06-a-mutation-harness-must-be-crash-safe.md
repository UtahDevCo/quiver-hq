---
type: Observation
title: A mutate-then-restore harness leaves the mutation behind when it dies mid-iteration
description: Piping a mutation-testing loop through head sends SIGPIPE between the mutate and the restore, committing a deliberate bug to the working tree while the harness reports success.
kind: failure-mode
proposed_layer: meta
tags: [mutation-testing, shell, test-harness]
generated: { by: claude/opus-5, at: 2026-08-06T17:20:00Z }
status: draft
sources:
  - id: incident
    resource: projects/k1/web/apps/web/lib/server/ingest-state-patch.ts
    title: an arrayUnion-dedupe mutant survived into the tree and failed the next full run
    last_modified: 2026-08-06
not:
  - term: "trust the harness's own KILLED/SURVIVED output as evidence the tree is clean"
    why: "the harness reports on the mutants it finished; the one it died inside prints nothing and is the one still in your source"
    instead: "re-grep the mutated lines after the run, and run the full suite from a cold cache before committing"
---

# Observation

A mutation harness is a loop that edits source, runs tests, then puts the source back.
The restore is the only thing standing between the run and a deliberately broken tree,
and it does not happen if the process dies between the two steps.

`zsh mutate.sh | head -3` is enough to cause it. `head` exits after three lines, the
next write gets SIGPIPE, and the shell dies wherever it happened to be. If that is
after `perl -pi` applied the mutation and before the `cp` that restores it, the mutant
is now the code.

Two habits make it safe. Trap in the harness so the restore runs on exit
(`trap 'cp $BAK $SRC' EXIT INT TERM`), and after the run, independently verify the tree
rather than believing the harness's summary.

# Why it matters

The failure is quiet in the worst way. The harness prints `KILLED` for everything it
managed to finish, which reads as a clean run, and the mutant it died inside prints
nothing at all. Absence of a line is not something a reader notices.

What makes it dangerous is that a mutation harness deliberately writes plausible,
compiling, subtly-wrong code. This is not a syntax error that fails loudly. In the k1
case the leaked mutant deleted an `if (!ids.includes(id))` guard, turning
arrayUnion-style dedupe into a plain append. Typecheck passed. Lint passed. It was
caught only because a full test run happened afterwards for an unrelated reason, and
that run was the last verification before a commit.

The near-miss is that the harness output which "proved" the code was well tested was
produced by the same invocation that corrupted the code.

# Evidence

The two invocations, and the difference between them:

```
zsh /tmp/mut2.sh 2>&1 | head -3      # SIGPIPE after mutant 3; mutant 4 left applied
zsh /tmp/mut2.sh                     # all 7 restored
```

The harness reported success both times for what it printed:

```
KILLED   coalescer always opens its own transaction  (9 pass 1 fail )
KILLED   chained flush is overwritten instead of shared  (9 pass 1 fail )
KILLED   log cap keeps the oldest instead of the newest  (9 pass 1 fail )
```

The leaked mutant, still in the file afterwards:

```ts
for (const id of patch.ingestEventIds ?? []) {
  ingestEventIds.push(id)                                    // mutant
  // if (!ingestEventIds.includes(id)) ingestEventIds.push(id)   // original
}
```

The residue check that should have been part of the harness from the start, and is
cheap enough that there is no reason to skip it:

```
grep -c 'includes(id)' ingest-state-patch.ts   # 1
grep -c '??=' ingest-state-coalescer.ts        # 1
```
