---
type: Observation
title: Check what the evaluator reads before regenerating data a bad config produced
description: A wrong model id in stored runs looked like it invalidated 16 of 28 measurement cases; the eval case carries only the question, bundle, member answers, and human label, so the stored verdict is never read.
kind: failure-mode
proposed_layer: meta
observed_in: k1
tags: [evaluation, measurement, cost, data-model, reasoning-errors]
status: draft
not:
  - term: "regenerate every stored run because the config that produced it was wrong"
    why: "the evaluator re-runs the component under test, so the stale field was not an input to any metric — regenerating would have spent ~28 multi-provider panel runs to change nothing"
    instead: "read the case type the evaluator consumes and confirm the stale field appears in it before treating the data as spoiled"
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
sources:
  - { id: eval-case, resource: "projects/k1/web/packages/db/src/panel-judge-eval.ts:69-84", title: "JudgeEvalCase — id, question, bundle, members, expected, labelledBy. No verdict, no judge model." }
  - { id: export, resource: "projects/k1/web/packages/db/src/panel-label-export.ts:199", title: "toCase(run, label) — builds a case from a stored run and its human label" }
---

# Observation

I found that 16 of 28 stored evaluation runs had been scored by a model the
product does not ship, and concluded the runs were spoiled and had to be
regenerated. That conclusion was wrong, and I had already told the user a version
of it.

The type the evaluator consumes:

```ts
export interface JudgeEvalCase {
  id: string
  question: string
  bundle: ProjectReasoningBundle
  members: BlindedMemberAnswer[]   // the answers, not the members
  expected: JudgeEvalExpectation   // the human label
  labelledBy: "synthetic" | string
}
```

No verdict. No judge id. The stored verdict is a *previous* run of the component
under test, and the harness re-runs that component over every case. The stale
model id was never an input to a single metric.

# Why it matters

The cost of the error was asymmetric and would have landed on the user: about 28
panel runs across three paid providers, each carrying a full evidence bundle,
plus the human relabelling of the seven cases whose ids would have changed. All to
correct a field nothing reads.

The general shape is that a stored artifact accumulates fields from the pipeline
that produced it, and only some of them are inputs to the measurement. A wrong
value in one of the others is untidy, not disqualifying. The check is mechanical:
open the type the evaluator takes and look for the field.

What made the mistake easy is that the config *was* genuinely wrong, and it did
invalidate a different number computed over the same runs (the judge's
invalid-output rate). One wrong config, two conclusions, only one of them true.

Related: [[a-local-model-override-measures-a-model-you-do-not-ship]] — the
misconfiguration that prompted this.

# Review notes

Recorded against my own reasoning error rather than against a code defect. The
code is correct; the framing was not.
