---
type: Failure Mode
title: In clause extraction, LLM name-matching against a candidate list is robust; the weak point is whether the target schema can represent the clause
description: On a 10-clause corpus, party-name mapping was flawless including first-name to full-name; every failure was the fixed-split schema being unable to hold a tiered waterfall.
kind: failure-mode
tags: [llm, extraction, schema, waterfall]
generated: { by: claude/opus-4.8, at: 2026-08-25T14:22:12Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/k1/web/packages/ai/src/waterfall-extraction.ts
    title: structured waterfall extractor (candidate-party mapping + fixed-split output)
    last_modified: 2026-08-25
---

# Failure Mode

When extracting a structured value from a legal clause with an LLM, the party
name-resolution step was not the failure point; the representability of the
target schema was. On Gregory's 10-entity synthetic LPA corpus, the extractor
mapped 100% of clause parties to K-1 owner ids (0 unmatched across all 10),
including clauses that name partners by first name only ("Alice", "Carol",
"Frank") resolving to the full K-1 names ("Alice Chen", "Carol Washington",
"Frank Okafor"), because the prompt is given the entity's candidate party
list as context. Org-to-org names matched everywhere too.

Every substantive extraction problem was instead the fixed-split output
schema being unable to hold what the clause actually said: hurdle-conditional
residuals, ratchets, IRR bands, targeted-capital mechanics, and unit-class
priority all collapse to a single split or a flag.

# Why it matters

It says where to spend hardening effort. The intuition going in was that
first-name-only clauses would break the name match; that intuition was wrong
and would have wasted effort on the mapping layer. The real gap is schema
expressiveness — the fixed split cannot represent a tiered waterfall — so the
durable roadmap item is a richer waterfall representation, not better name
matching.

# Evidence

Batch dry-run through `POST /api/projects/.../waterfalls/extract` on
gregory-test, 2026-08-24: `unmatched` was `[]` for all 10 entities. Pinnacle
(partners Alice/Bob/Carol/David, clause uses bare first names) and Keystone
(five first-name partners) both mapped every party. The candidate list is
assembled in `projectWaterfallCandidates` and passed to the extractor via
`buildWaterfallExtractionUserPrompt`
(`packages/ai/src/waterfall-extraction.ts`).

# Related

[[one-home-per-field-in-a-model-output-schema]] — sibling lesson about the
schema being where model-extraction quality is won or lost.
