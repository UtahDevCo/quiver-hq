---
type: Observation
title: A/B a prompt fix against ground truth before shipping it, and keep the negative result
description: A well-reasoned prompt instruction measured slightly worse than no instruction; run-to-run variance at temperature 0 was larger than any effect.
kind: practice
proposed_layer: meta
tags: [llm, prompt-engineering, measurement, extraction]
generated: { by: claude/opus-5, at: 2026-07-31T21:00:00Z }
status: draft
sources:
  - id: measurement
    resource: projects/k1/web/packages/ingestion/src/__tests__/k1-extraction-prompt.test.ts
    title: recorded A/B — 25 of 48 clean runs before the instruction, 23 of 48 after
    last_modified: 2026-07-31
  - id: fix
    resource: projects/k1 commit adc44e7
    title: "fix(extraction): catch the misread-row class in validation, not in the prompt"
    last_modified: 2026-07-31
not:
  - term: "shipping a prompt rule because it names the exact failure and reads as obviously correct"
    why: "an instruction that describes the error can leave the error rate unchanged, and one run of one document cannot tell you either way"
    instead: "score both prompts over N documents with repeats against ground truth; if the arms are within run-to-run variance, the change did nothing"
---

# Observation

Prompt changes need an A/B against ground truth, with repeats, before they ship. The
instruction that names the failure precisely and reads as obviously correct is exactly
the one that gets shipped unmeasured.

Repeats are not optional. At temperature 0 the same document and the same prompt gave
different answers across runs, and single-run comparisons flipped sign depending on
which run you looked at. Two runs per arm over 24 documents was the minimum that made
the comparison legible, and what it showed was no effect.

When the measurement comes back negative, revert the change and write the numbers into
the test file next to the code. The reasoning that produced the instruction is
persuasive and will be reproduced by the next person, or by the same person in a month.

# Why it matters

An unmeasured prompt rule costs tokens on every call forever, and it converts an open
problem into a closed one. The team believes the class is handled. Nobody re-opens it,
because the fix is right there in the prompt describing the bug.

The measurement is also what redirects the work. Once the numbers said the prompt could
not fix the misread, the same effort went into validation, where detectors scored 21 of
28 bad documents with 0 false alarms on 140 good ones. That is a shipped improvement
instead of a shipped belief.

# Evidence

k1's Gemini K-1 extraction files a printed figure one row above where it belongs. The
prompt fix stated the rule, named the two adjacent pairs that get confused most, and
required a verbatim row-by-row transcript before any field was filled.

24 documents at a fixed stride over the corpus, 2 runs per arm, temperature 0, scored
against the same PDFs parsed with pypdf:

```
old  extractions=48  wrongFields=48  cleanRuns=25/48 (52%)
new  extractions=48  wrongFields=50  cleanRuns=23/48 (48%)
```

Variance inside one arm was larger than the gap between arms: documents clean on both
old runs came back wrong on a new run and vice versa, and one document was wrong under
the old prompt on run 1 and clean on run 2.

Two things worth noting about why prompting could not help here. The page is not
ambiguous — pypdf reports row 19's label and its amount at the same y coordinate, so
there is nothing to disambiguate. And an earlier, narrower fix to the same prompt
*did* work and was confirmed by the same harness: telling the extractor where the
capital-account basis is printed took `part_l.accounting_method` from 0 of 168 stored
rows to 48 of 48 extractions. Prompt fixes work for a field the model was not looking
for. They did nothing for a field it was looking at and misreading.
