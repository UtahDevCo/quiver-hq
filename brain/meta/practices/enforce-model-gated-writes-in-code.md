---
type: Practice
title: When a model's output gates a write, enforce the gate in code, not by trusting the model to self-flag
description: A model told to flag its own low-confidence output does so inconsistently; a deterministic code check on the same signals is the actual gate.
kind: practice
tags: [llm, validation, human-in-the-loop, gating, writes]
generated: { by: claude/opus-4.8, at: 2026-08-25T14:22:12Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/k1/web/packages/db/src/waterfall-extraction-store.ts
    title: evaluateWaterfallExtraction deterministic hurdle backstop
    last_modified: 2026-08-25
  - id: commit
    resource: https://github.com/UtahDevCo/k1/commit/d6d1b0d
    title: "fix(waterfall-extraction): force review on hurdle/ratchet/class clauses"
not:
  - term: "Rely on the model's `unresolved` / `needs_review` field to withhold a write"
    why: "the model applied the rule on 6 of 10 structurally-similar inputs and skipped it on the other 4, returning a clean status with a silently-chosen value"
    instead: "keep the model's self-flag as one signal, and add a deterministic code check over the same evidence that forces review independently"
---

# Practice

When a model's structured output decides whether a value is safe to persist
(a human-in-the-loop gate, an auto-approve threshold, a "confident enough to
store" flag), do not let the model's self-assessment be the gate. Treat it as
one input and enforce the real gate in code, over the same evidence the model
saw.

Concretely in k1 waterfall extraction: the extractor returns `unresolved[]`
and is told to populate it whenever the distribution split is conditional
(a hurdle, a ratchet, a unit class) and therefore not representable as the
fixed split the store accepts. Running Gregory's 10-entity synthetic LPA
corpus (2026-08-24), it flagged 6 of 10 correctly and left 4 clean
(`status: "proposed"`) with a silently-chosen tier — Delta (targeted
capital), Epsilon (3-band IRR), Theta (non-monotonic MOIC), Keystone
(preferred-class priority). Two of those picked the post-hurdle tier, not the
current one.

The fix was two-lever: tighten the prompt (necessary, insufficient) AND add a
deterministic backstop that scans the clause text and the model's own notes
for hurdle markers (`multiple`/`MOIC`/`IRR`/`ratchet`/`hurdle`/`N.NNx`
notation/`preferred|common units`/`priority return`/`from and after`/`so long
as`) and forces `needs_review` regardless of what the model returned. A plain
fixed split contains none of the markers, so it still auto-proposes.

# Why it matters

The failure mode is silent and one-directional: the model returns a clean
status, the value looks decisive, and it flows to a write. Here the write was
a money split (a distribution waterfall that drives cash and tax allocation),
so a wrongly-stored tier is a wrong client number. The asymmetry is the whole
argument for the code check: a false positive costs one extra human review; a
false negative stores a wrong value under a green light. A gate you can only
trust 6 times out of 10 is not a gate.

# Evidence

Live dry-run on gregory-test after the fix: the 4 leakers all flip to
`needs_review`. Three flip via the tightened prompt (now reporting the
baseline tier: Epsilon 40/60, Theta 55/45); Keystone flips via the code
backstop alone, because the model still returned a clean 5-way Common split
and the deterministic scan caught the "Preferred Units" class priority it
missed. A genuinely simple `60/30/10` clause still returns `proposed`, so the
backstop does not over-block. Before: 4/10 leaked. After: 0/10.

The backstop lives in `evaluateWaterfallExtraction`
(`packages/db/src/waterfall-extraction-store.ts`), a pure function that takes
the extraction plus the raw clause text, so it is unit-tested without a model.

# Related

[[make-misuse-unrepresentable]] — the same instinct, one layer up: the deeper
fix is a schema that can hold a tiered waterfall so the value is never
silently flattened. [[check-how-the-callee-reports-refusal]] — a refusal
carried in a droppable field (a status string) is exactly what gets dropped.
