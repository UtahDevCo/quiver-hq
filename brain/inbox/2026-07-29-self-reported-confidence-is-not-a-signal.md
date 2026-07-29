---
type: Observation
title: A model's self-reported confidence is not a signal — do not display it, do not route on it
description: LLM-reported confidence tracks prose register, not correctness. Measured: identical correct conclusions reported 80/15/45%; two runs of one model both said 80% and one was wrong.
kind: failure-mode
proposed_layer: meta
observed_in: k1
tags: [llm, calibration, ui, evaluation, adversarial-panel]
status: draft
not:
  - term: "`Confidence 82%` badge beside a model-authored answer"
    why: "a percentage next to a claim is read as calibrated whether or not it is; it manufactures the trust the review step exists to withhold"
    instead: "show what the answer rests on — citations, the work paper, what was missing — and let the reader calibrate"
  - term: "triggering an escalation, a second opinion, or a review when self-reported confidence < threshold"
    why: "fires on hedging register rather than on risk; misses the confident-and-wrong case, which is the only case worth escalating"
    instead: "gate on facts about the evidence: a weak supporting extraction, a missing input, a high-stakes question class"
  - term: "dropping the number from the stored record because it is uninterpretable"
    why: "destroys the data needed to measure calibration, and the export is an audit artifact rather than a recommendation"
    instead: "keep it in the record, labelled uncalibrated; withhold it from the surface that reads as advice"
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
sources:
  - id: k1-panel-runs
    resource: projects/k1/web/apps/web/app/[tenantSlug]/projects/[projectId]/project-ai-query.tsx
    title: k1 — measured on the live 3-vendor adversarial panel, 2026-07-29
    author: agent:claude
---

# Observation

The `confidence` field a model returns in a structured answer carries no
information about whether that answer is correct. Do not render it as a
percentage next to the answer, and do not use it as a routing or escalation
signal. Keep it in the stored record, labelled as uncalibrated.

# The measurement

Three vendors (Gemini 2.5 Flash, Claude Sonnet 4.6, GPT-5.5) answered the same
question over one byte-identical evidence bundle, and reached the **same correct
conclusion**. Self-reported confidence: **80%, 15%, 45%.**

Separately, on a question with a known trap (K-1 amounts have a direction, and
reversing payer and recipient produces a plausible wrong total), two runs of the
**same model at the same prompt version** both reported **80%** — and one of them
was wrong. The number did not move when correctness did.

A third data point in the same corpus: a model reported **85%** on a governing
document whose operative definitions contained un-chosen bracketed alternatives,
i.e. on a question the source text does not settle at all.

# Why it matters

The failure is asymmetric and in the dangerous direction. Low confidence on a
right answer costs a little unnecessary review. High confidence on a wrong answer
is the case every review process exists to catch, and self-reported confidence is
silent on exactly that case. Worse, displaying it *substitutes* for the reader's
own calibration: a reviewer who sees 80% reads the answer less carefully than one
who sees the citations and the gaps.

The corollary for prompts: an instruction like "set confidence to reflect how
completely the evidence settles the question, not how fluent your answer is"
does not fix this. It was in the prompt for all three measurements above.

# What to do instead

Surface the things that actually vary with correctness:

- what the answer cites, and whether those citations support it
- what the model said it was missing (`requestedDocuments`, caveats)
- **disagreement between independent models** — this is the one that moved. On
  the same corpus, a member that reversed a K-1 direction was caught by an
  adversarial panel and named, while its own confidence stayed at 80%.

# Promotion note

Strong candidate for a meta failure mode: it applies to any LLM output with a
self-assessed confidence field, not just this project. Related concepts worth
linking once they exist: an adversarial-panel pattern, and something on
distinguishing an evaluation surface (where uncalibrated diagnostics belong) from
an advice surface (where they do not).
