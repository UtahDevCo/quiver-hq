---
type: Observation
title: Give an LLM output schema exactly one home per field
description: A response schema offering two valid places for the same value makes the model's choice a coin flip that readers must all replicate.
kind: practice
proposed_layer: meta
tags: [llm, schema, prompt-design, extraction]
generated: { by: claude/opus-5, at: 2026-08-10T16:03:58Z }
status: draft
sources:
  - id: prompt
    resource: projects/k1/web/packages/ingestion/src/index.ts
    title: K1_EXTRACTION_PROMPT, declaring both box_NN.codes and a flat box_NN_codes sibling
    last_modified: 2026-08-10
  - id: consequence
    resource: projects/k1
    title: "k1 e88ffbb — 53 codes on 9 of 175 documents extracted and then dropped"
    last_modified: 2026-08-10
not:
  - term: "leave both keys in the schema and merge them in every reader"
    why: "the merge is correct only in the readers that remember to do it, and nothing makes a new reader remember"
    instead: "delete one key from the schema, so there is no second place for a value to hide"
---

# Observation

A JSON schema you hand a model is an instruction set, and a field with two valid locations
is an instruction to pick one at random. The model will use both across a corpus, sometimes
within one document, and every consumer then has to merge them or silently lose data.

k1's extraction prompt declared each coded Schedule K-1 box twice: `box_14_self_employment_earnings_loss.codes: {}`
and a sibling `box_14_codes: {}`. The model filled whichever it preferred per document. The
normalizer read one. 53 values across 9 of 175 documents landed in the other and were
dropped, and the model produced conflicting copies in both maps on 5 occasions.

This is [[make-misuse-unrepresentable]] applied to the model's output contract rather than
to the toolchain. Deleting the redundant key is the fix; documenting which one wins is not.

# Why it matters

Reading only one of two homes is not a bug a reviewer can see, because the reader looks
correct against the schema. Neither is it a bug a test suite catches, unless a fixture
happens to use the other home. It surfaces as accuracy you cannot explain and a metric that
disagrees with what users see.

Deleting a key from a prompt after the fact carries a real cost that adding it never did:
model behaviour changes on every field, so every accuracy measurement taken under the old
schema has to be re-run. In k1 that meant a choice between merging both maps in the reader
now, which recovered the data and preserved 350 calls' worth of measurement, and fixing the
schema, which is correct but invalidates all of it. The cheap fix and the right fix were
different, which is the argument for spending the attention when the schema is written.

# Evidence

The prompt's own declaration, both keys, adjacent:

```
"box_14_self_employment_earnings_loss": { "row": "14", "label": "...", "amount": null, "codes": {}, "citation": { "page": null } },
"box_14_codes": {},
```

Distribution over 175 documents at thinking budget 0: 173 codes filed only in the sibling,
53 filed only in the nested map, 983 in both, of which 4 carried different amounts in the two
copies. The 2048 arm was worse at 86 nested-only across 12 documents, and there the model
also began using the codes map as a free-form dictionary, keying entries by a prose
description instead of a code letter.
