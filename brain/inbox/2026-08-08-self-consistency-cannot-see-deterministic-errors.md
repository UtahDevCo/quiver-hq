---
type: Observation
title: Self-consistency voting cannot see a deterministic error
description: Repeating one config N times only catches random error; diversify the parameter that causes the failure instead.
kind: failure-mode
proposed_layer: meta
tags: [llm, evaluation, voting, extraction]
generated: { by: claude/opus-5, at: 2026-08-08T20:15:03Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/packages/ingestion/src/cross-budget-gate.ts
    title: k1 cross-budget gate, header comment carries the measured rates
    last_modified: 2026-08-08
  - id: commit
    resource: k1@8584370
    title: "feat(ingestion): default thinking off, add cross-budget disagreement gate"
not:
  - term: "run the same extraction 3 times and gate on majority agreement"
    why: "an error caused by the configuration reproduces identically every pass, so all three votes agree and are all wrong, and the gate reports high confidence"
    instead: "vary the parameter suspected of causing the failure and compare across settings"
---

# Observation

Self-consistency (sample N times, keep the majority) is only a correctness filter
for error that is random per call. When the error is caused by the configuration
rather than by sampling, every repeat reproduces it, the votes are unanimous, and
an agreement gate marks the wrong answer as high confidence.

Before building a voting path, check whether the errors you want to catch
reproduce. Re-run the specific documents that failed, several times, under the
same settings. Errors that come back identically every time need a different axis
of diversity, not more samples on the same axis.

# Why it matters

The failure is silent and it inverts the signal. An agreement gate is normally
sold as the thing that catches bad extractions, so a deterministic error passes
through the one control that was supposed to stop it, wearing a confidence score.
It is worse than no gate, because reviewers stop looking.

# Evidence

Gemini 2.5 Flash extracting Schedule K-1 PDFs at temperature 0. Thinking budget 0
beat a pinned 2048 across 175 documents (94.2% vs 90.8% box accuracy). On 9 of the
17 documents where budget 0 lost, it lost the *same* boxes on all 4 repeats: codes
13W, 20A and 20Z returned with a null amount, while budget 2048 read them exactly.

Measured over 175 documents, 2125 boxes, both budgets scored against ground truth:

    both arms same verdict   1949 boxes   98.5% correct   (off 95.5%, 2048 92.1%)
    both present, different    89 boxes   off right 78, 2048 right 11, neither 0

Agreement across two different budgets beats either budget alone. Agreement across
three repeats of one budget would have certified the dropped codes as correct.

Cost note, since it is usually the objection: two arms at different settings was
cheaper than three samples at one setting ($0.0207 vs $0.0238 per document).
