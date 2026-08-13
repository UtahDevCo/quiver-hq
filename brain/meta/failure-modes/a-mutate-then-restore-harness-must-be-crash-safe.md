---
type: Failure Mode
title: A mutate-then-restore harness leaves the mutation behind when it dies mid-iteration
description: Piping a mutation-testing loop through `head -3` sends SIGPIPE between the mutate and the restore, committing a deliberate bug to the working tree while the harness prints KILLED for everything it finished.
tags: [mutation-testing, shell, test-harness, verification]
generated: { by: claude/opus-5, at: 2026-08-06T17:20:00Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "trusting the harness's own KILLED/SURVIVED output as evidence the tree is clean"
    why: "the harness reports on the mutants it finished; the one it died inside prints nothing and is the one still in your source"
    instead: "re-grep the mutated lines after the run, and run the full suite from a cold cache before committing"
  - term: "restoring the source on the normal path at the end of the loop body"
    why: "any signal between the edit and the restore skips it, and `| head` is enough to produce one"
    instead: "`trap 'cp $BAK $SRC' EXIT INT TERM` so the restore runs however the shell exits"
  - term: "relying on typecheck and lint to catch a leaked mutant"
    why: "a mutation harness deliberately writes plausible, compiling, subtly-wrong code; the leaked mutant here passed both"
    instead: "assert the specific mutated expressions are back, by grep count, as a step of the harness"
sources:
  - id: incident
    resource: projects/k1/web/apps/web/lib/server/ingest-state-patch.ts
    title: an arrayUnion-dedupe mutant survived into the tree and failed the next full run
    author: claude/opus-5
    last_modified: 2026-08-06
---

# The trap

A mutation harness is a loop that edits source, runs tests, then puts the source
back. The restore is the only thing standing between the run and a deliberately
broken tree, and it does not happen if the process dies between the two steps.

`zsh mutate.sh | head -3` is enough. `head` exits after three lines, the next write
gets SIGPIPE, and the shell dies wherever it happened to be. If that is after
`perl -pi` applied the mutation and before the `cp` that restores it, the mutant is
now the code.

# Why it matters

The harness prints `KILLED` for everything it managed to finish, which reads as a
clean run, and the mutant it died inside prints nothing at all. Absence of a line is
not something a reader notices.

What makes it dangerous is that a mutation harness deliberately writes plausible,
compiling, subtly-wrong code. In the k1 case the leaked mutant deleted an
`if (!ids.includes(id))` guard, turning arrayUnion-style dedupe into a plain append.
Typecheck passed and lint passed. It was caught only because a full test run happened
afterwards for an unrelated reason, and that run was the last verification before a
commit.

The near-miss is that the harness output which proved the code was well tested came
from the same invocation that corrupted the code.

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

The residue check that belonged in the harness from the start, cheap enough that
there is no reason to skip it:

```
grep -c 'includes(id)' ingest-state-patch.ts   # 1
grep -c '??=' ingest-state-coalescer.ts        # 1
```

Verifying the tree independently rather than believing the run's own summary is
[verify-a-write-actually-happened](verify-a-write-actually-happened.md) applied to
your source files, and a summary that omits the iteration it died inside is
[audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md).
