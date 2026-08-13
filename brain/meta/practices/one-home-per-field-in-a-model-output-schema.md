---
type: Practice
title: Give a model output schema exactly one home per field
description: Two valid keys for the same value made the model pick per document; 53 codes across 9 of 175 documents landed in the key the normalizer did not read.
tags: [llm, schema, prompt-design, extraction]
generated: { by: claude/opus-5, at: 2026-08-10T16:03:58Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: instance-of, target: /meta/practices/make-misuse-unrepresentable.md }
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
  - term: "document which key wins"
    why: "the model reads the schema, not the doc, and will keep filling both"
    instead: "remove the redundant key before the first accuracy run, while re-measuring is still cheap"
---

# The practice

A JSON schema handed to a model is an instruction set, and a field with two valid
locations instructs the model to pick one at random. It will use both across a corpus
and sometimes within one document, leaving every consumer to merge them or lose data.

One field, one home. This is
[make-misuse-unrepresentable](make-misuse-unrepresentable.md) applied to the model's
output contract rather than to the toolchain.

# Why it matters

Reading one of two homes is not a bug a reviewer sees, because the reader looks correct
against the schema, and a test suite catches it only if a fixture happens to use the
other home. It surfaces as accuracy you cannot explain and a metric that disagrees with
what users see.

Deleting a key after the fact costs what adding it never did. Model behaviour changes on
every field, so every accuracy measurement taken under the old schema has to be re-run.
In k1 that meant choosing between merging both maps in the reader now, which recovered
the data and preserved 350 calls' worth of measurement, and fixing the schema, which is
correct and invalidates all of it. That the cheap fix and the right fix diverged is the
argument for spending the attention when the schema is written.

# Evidence

k1's extraction prompt declared each coded Schedule K-1 box twice, the two keys adjacent:

```
"box_14_self_employment_earnings_loss": { "row": "14", "label": "...", "amount": null, "codes": {}, "citation": { "page": null } },
"box_14_codes": {},
```

The model filled whichever it preferred per document; the normalizer read one. 53 values
across 9 of 175 documents landed in the other and were dropped, and the model produced
conflicting copies in both maps on 5 occasions.

Distribution over 175 documents at thinking budget 0: 173 codes filed only in the
sibling, 53 filed only in the nested map, 983 in both, of which 4 carried different
amounts in the two copies. The 2048 arm was worse at 86 nested-only across 12 documents,
and there the model also began using the codes map as a free-form dictionary, keying
entries by a prose description instead of a code letter.
