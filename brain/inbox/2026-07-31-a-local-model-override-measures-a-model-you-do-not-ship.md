---
type: Observation
title: A local model override measures a model you do not ship
description: .env.local pinned an older model id than production, so a measurement run scored the wrong judge and produced a reliability number that transferred to nothing.
kind: failure-mode
proposed_layer: meta
observed_in: k1
tags: [llm, evaluation, configuration, environments, measurement]
status: draft
not:
  - term: 'K1_AI_QUERY_GEMINI_MODEL="gemini-2.5-flash" in .env.local, while apphosting.yaml ships gemini-3.6-flash'
    why: "the harness runs locally by default, so the model under measurement was the one no user is served — and the two differed by 3 invalid outputs in 18 runs versus 0 in 13"
    instead: "pin the local id to the deployed id, or have the harness print the resolved model and refuse to write a report when it does not match the shipped config"
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
sources:
  - { id: env-local, resource: "projects/k1/web/.env.local", title: 'K1_AI_QUERY_GEMINI_MODEL="gemini-2.5-flash"' }
  - { id: apphosting, resource: "projects/k1/web/apphosting.yaml:105-108", title: "K1_AI_QUERY_GEMINI_MODEL: gemini-3.6-flash, the value production runs" }
  - { id: default, resource: "projects/k1/web/packages/ai/src/project-query-models.ts:14", title: "DEFAULT_GEMINI_MODEL = gemini-3.6-flash, a third value in play" }
---

# Observation

An LLM evaluation harness resolves its model from the environment. Run it on a
developer machine and `.env.local` wins, so the number you publish describes
whichever id happens to be pinned there.

Measured across one day of runs on the same project and the same questions:

```
gemini-3.6-flash   0 invalid judge outputs / 13 runs     <- what production serves
gemini-2.5-flash   3 invalid judge outputs / 18 runs     <- what .env.local pinned
```

Every one of those three failures had all three panel members answering
normally. The judge alone could not produce parseable output, and only on the
harder question shapes: a rare-metric lookup, an aggregation, and a
paid-versus-received difference. A 17% invalid rate against a gate threshold of
10% is the difference between shipping the judge and falling back.

# Why it matters

The failure is quiet in both directions. Nothing errors, and the report is
well-formed and specific, which is what makes it persuasive. The gate here exists
to decide whether an LLM judge is reliable enough to replace a mechanical one, so
measuring the wrong model produces a decision about a model that will never run.

Three different ids were reachable in this one repo: the `.env.local` pin, the
`apphosting.yaml` value, and a `DEFAULT_GEMINI_MODEL` constant. Any of the three
could win depending on how the process starts.

The countermeasure is for the harness to name the model it resolved in the
report, and to refuse to write a gate verdict when that id differs from the
shipped config. A human labelling data cannot see which model produced it.

Related: [[automatic-behavior-is-unmeasured-until-recorded]] — the same class,
where the thing you assume is in effect leaves no trace confirming it.

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
