---
type: Failure Mode
title: A model's self-reported confidence is not a signal — don't display it, don't route on it
description: LLM-reported confidence tracks prose register, not correctness. Measured — identical correct conclusions reported 80/15/45%; two runs of one model both said 80% and one was wrong.
tags: [llm, calibration, ui, evaluation, adversarial-panel]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "a `Confidence 82%` badge beside a model-authored answer"
    why: "a percentage next to a claim is read as calibrated whether or not it is; it manufactures the trust the review step exists to withhold"
    instead: "show what the answer rests on — citations, the work paper, what was missing — and let the reader calibrate"
  - term: "triggering an escalation, second opinion, or review when self-reported confidence < threshold"
    why: "fires on hedging register rather than on risk; misses the confident-and-wrong case, which is the only case worth escalating"
    instead: "gate on facts about the evidence — a weak supporting extraction, a missing input, a high-stakes question class"
  - term: "dropping the number from the stored record because it is uninterpretable"
    why: "destroys the data needed to measure calibration later, and the export is an audit artifact rather than a recommendation"
    instead: "keep it in the record labelled uncalibrated; withhold it from any surface that reads as advice"
  - term: "prompting the model to calibrate — \"set confidence to reflect how completely the evidence settles the question\""
    why: "was in the prompt for all three measurements below and changed nothing"
    instead: "treat the field as unfixable at the prompt layer and design around it"
sources:
  - id: k1-panel-runs
    resource: projects/k1
    title: k1 — measured on the live 3-vendor adversarial panel, 2026-07-29
    author: claude/opus-5
    last_modified: 2026-07-29
---

# The trap

The `confidence` field a model returns in a structured answer carries no
information about whether that answer is correct. Don't render it as a percentage
next to the answer, and don't use it as a routing or escalation signal. Keep it in
the stored record, labelled uncalibrated.

# The measurement

Three vendors (Gemini 2.5 Flash, Claude Sonnet 4.6, GPT-5.5) answered the same
question over one byte-identical evidence bundle and reached the **same correct
conclusion.** Self-reported confidence: **80%, 15%, 45%.**

Separately, on a question with a known trap — K-1 amounts have a direction, and
reversing payer and recipient produces a plausible wrong total — two runs of the
**same model at the same prompt version** both reported **80%**, and one was wrong.
The number did not move when correctness did.

A third point in the same corpus: a model reported **85%** on a governing document
whose operative definitions still contained un-chosen bracketed alternatives —
i.e. on a question the source text does not settle at all.

# Why it matters

The failure is asymmetric and in the dangerous direction. Low confidence on a right
answer costs a little unnecessary review. **High confidence on a wrong answer is
the case every review process exists to catch, and self-reported confidence is
silent on exactly that case.**

Worse, displaying it *substitutes* for the reader's own calibration. A reviewer who
sees 80% reads the answer less carefully than one who sees the citations and the
gaps.

# What to surface instead

Things that actually vary with correctness:

- what the answer cites, and whether those citations support it
- what the model said it was missing — requested documents, caveats
- **disagreement between independent models.** This is the one that moved. On the
  same corpus, a member that reversed a K-1 direction was caught and named by an
  adversarial panel while its own confidence sat at 80%.

# Provenance note

Recorded by a different session than the one that promoted it, and the specific
percentages have not been independently reproduced. Promoted anyway because the
asymmetry argument stands on its own: a signal that is silent on the
confident-and-wrong case cannot be used to catch it, whatever the exact numbers
were. If a later measurement contradicts this, deprecate rather than overwrite —
the reversal would be worth more than the rule.
