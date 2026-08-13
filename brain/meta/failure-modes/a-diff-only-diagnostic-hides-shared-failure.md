---
type: Failure Mode
title: A diff-only diagnostic cannot tell "both correct" from "both wrong"
description: A script that printed only where two extraction arms disagreed said "no verdict differences" on a document that scored 40% on four consecutive repeats.
tags: [evaluation, debugging, diagnostics]
generated: { by: claude/opus-5, at: 2026-08-08T20:15:03Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
sources:
  - id: evidence
    resource: projects/k1 scratchpad regress.ts vs repro.ts
    title: k1 thinking-budget regression investigation, 2026-08-07
    last_modified: 2026-08-07
not:
  - term: "print only the fields where A and B disagree"
    why: "an empty table then means either 'both right' or 'both wrong', and it reads as 'both right'"
    instead: "print each candidate's score against ground truth alongside the differences"
---

# The trap

A diagnostic that reports only where two candidates differ has no way to express
that both are wrong in the same way. Its quietest output, an empty diff, is
ambiguous between the best case and a shared failure, and it gets read as the best
case.

Any comparison tool should print each side's absolute score against ground truth
next to the delta between the sides.

# Why it matters

The ambiguity resolves in the flattering direction. An empty diff is read as
"nothing wrong here", so a shared failure is reported as a pass. That is how an
investigation concludes early with the wrong answer while feeling well-evidenced.

# Evidence

Investigating documents where a Gemini extraction config scored 40% against
another's 100%, a script re-extracted under both settings and printed only boxes
whose verdicts differed. It printed "no verdict differences" for two documents, and
the user was told the regression did not reproduce.

It did reproduce. A second script that printed the actual score per arm showed the
document at 40% on four consecutive repeats. The first run had both arms low, so
the diff was empty and the silence was read as agreement on a correct answer.

The fix is one line of output. `console.table(differences)` became:

    console.log(`off ${offPct}%  pinned ${pinPct}%  (${n} boxes)`)
    console.table(differences)

Related: [audits must report their own coverage](audits-must-report-their-own-coverage.md),
the same shape of error one level up, where "couldn't check" is reported as
"checked, fine".
