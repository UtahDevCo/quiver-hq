---
type: Failure Mode
title: A local model override measures a model you do not ship
description: .env.local pinned an older model id than production, so a judge-reliability run scored gemini-2.5-flash at 3 invalid outputs in 18 runs while the shipped gemini-3.6-flash had 0 in 13.
tags: [llm, evaluation, configuration, environments, measurement]
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/automatic-behavior-is-unmeasured-until-recorded.md }
sources:
  - { id: env-local, resource: "projects/k1/web/.env.local", title: 'K1_AI_QUERY_GEMINI_MODEL="gemini-2.5-flash"' }
  - { id: apphosting, resource: "projects/k1/web/apphosting.yaml:105-108", title: "K1_AI_QUERY_GEMINI_MODEL: gemini-3.6-flash, the value production runs" }
  - { id: default, resource: "projects/k1/web/packages/ai/src/project-query-models.ts:14", title: "DEFAULT_GEMINI_MODEL = gemini-3.6-flash, a third value in play" }
  - { id: eval-case, resource: "projects/k1/web/packages/db/src/panel-judge-eval.ts:69-84", title: "JudgeEvalCase — id, question, bundle, members, expected, labelledBy. No verdict, no judge model." }
  - { id: export, resource: "projects/k1/web/packages/db/src/panel-label-export.ts:199", title: "toCase(run, label) — builds a case from a stored run and its human label" }
not:
  - term: 'K1_AI_QUERY_GEMINI_MODEL="gemini-2.5-flash" in .env.local, while apphosting.yaml ships gemini-3.6-flash'
    why: "the harness runs locally by default, so the model under measurement was the one no user is served, and the two differed by 3 invalid outputs in 18 runs against 0 in 13"
    instead: "pin the local id to the deployed id, or have the harness print the resolved model and refuse to write a report when it does not match the shipped config"
  - term: "regenerate every stored run because the config that produced it was wrong"
    why: "the evaluator re-runs the component under test, so the stale field was not an input to any metric, and regenerating would have spent about 28 multi-provider panel runs to change nothing"
    instead: "read the case type the evaluator consumes and confirm the stale field appears in it before treating the data as spoiled"
---

# The trap

An LLM evaluation harness resolves its model from the environment. Run it on a
developer machine and `.env.local` wins, so the number you publish describes
whichever id happens to be pinned there.

Measured across one day of runs on the same project and the same questions:

```
gemini-3.6-flash   0 invalid judge outputs / 13 runs     <- what production serves
gemini-2.5-flash   3 invalid judge outputs / 18 runs     <- what .env.local pinned
```

All three failures had every panel member answering normally. The judge alone could
not produce parseable output, and only on the harder question shapes: a rare-metric
lookup, an aggregation, and a paid-versus-received difference. A 17% invalid rate
against a gate threshold of 10% decides whether the judge ships or the mechanical
fallback does.

# Why it matters

The failure is quiet in both directions. Nothing errors, and the report is
well-formed and specific, which is what makes it persuasive. This gate exists to
decide whether an LLM judge is reliable enough to replace a mechanical one, so
measuring the wrong model produces a decision about a model that will never run.

Three ids were reachable in this one repo: the `.env.local` pin, the
`apphosting.yaml` value, and a `DEFAULT_GEMINI_MODEL` constant. Any of them could
win depending on how the process starts.

The countermeasure is for the harness to name the model it resolved in the report,
and to refuse to write a gate verdict when that id differs from the shipped config.
A human labelling data cannot see which model produced it.

# The follow-up: check what the evaluator reads before regenerating data

Finding the bad config, the next conclusion was that 16 of 28 stored evaluation
runs had been scored by a model the product does not ship and had to be
regenerated. That was wrong, and the user had already been told a version of it.

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

No verdict, no judge id. The stored verdict is a previous run of the component
under test, and the harness re-runs that component over every case. The stale model
id was never an input to a single metric.

The cost of acting on it would have landed on the user: about 28 panel runs across
three paid providers, each carrying a full evidence bundle, plus human relabelling
of the seven cases whose ids would have changed, all to correct a field nothing
reads.

A stored artifact accumulates fields from the pipeline that produced it, and only
some of them are inputs to the measurement. A wrong value in one of the others is
untidy. The check is mechanical: open the type the evaluator takes and look for the
field.

What made the mistake easy is that the config was genuinely wrong, and it did
invalidate a different number computed over the same runs, the judge's
invalid-output rate. One wrong config, two conclusions, one of them true.

# Evidence

Three sources of the same variable, two values:

```yaml
# web/apphosting.yaml — production
- variable: K1_AI_QUERY_GEMINI_MODEL
  value: gemini-3.6-flash
```

```sh
# web/.env.local — every local run
K1_AI_QUERY_GEMINI_MODEL="gemini-2.5-flash"
```

The second half is recorded against a reasoning error rather than a code defect.
The code is correct; the framing was not.

Related: [automatic behavior is unmeasured until recorded](automatic-behavior-is-unmeasured-until-recorded.md),
the same class, where the thing you assume is in effect leaves no trace confirming
it.
