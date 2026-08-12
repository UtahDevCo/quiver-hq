---
type: Observation
title: A diff-only diagnostic cannot tell "both correct" from "both wrong"
description: Comparing two candidates to each other without scoring either against truth makes a shared failure look like success.
kind: failure-mode
proposed_layer: meta
tags: [evaluation, debugging, diagnostics]
generated: { by: claude/opus-5, at: 2026-08-08T20:15:03Z }
status: draft
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

# Observation

A diagnostic that reports only where two candidates differ has no way to express
that both are wrong in the same way. Its quietest output, an empty diff, is
ambiguous between the best case and a shared failure, and it is naturally read as
the best case.

Any comparison tool should print each side's absolute score against ground truth,
not just the delta between the sides.

# Why it matters

The ambiguity resolves in the flattering direction. An empty diff is read as
"nothing wrong here", so a shared failure is not merely missed, it is actively
reported as a pass. This is how an investigation concludes early with the wrong
answer while feeling well-evidenced.

# Evidence

Investigating documents where a Gemini extraction config scored 40% against
another's 100%, I wrote a script that re-extracted under both settings and printed
only boxes whose verdicts differed. It printed "no verdict differences" for two
documents, and I reported to the user that the regression did not reproduce.

It did reproduce. A second script that printed the actual score per arm showed the
document at 40% on four consecutive repeats. The first run had both arms low, so
the diff was empty and I read silence as agreement-on-correct.

The fix is one line of output. `console.table(differences)` became:

    console.log(`off ${offPct}%  pinned ${pinPct}%  (${n} boxes)`)
    console.table(differences)

Related: [[audits-must-report-their-own-coverage]], which is the same shape of
error one level up, where "couldn't check" is reported as "checked, fine".
