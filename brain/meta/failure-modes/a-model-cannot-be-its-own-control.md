---
type: Failure Mode
title: A model cannot be its own control
description: A transcript the model wrote about its own read agreed with the wrong figure 25 times out of 25, and four repeats of one config dropped the same boxes on 9 of 17 documents.
tags: [llm, validation, evaluation, extraction, voting, monitoring]
generated: { by: claude/opus-5, at: 2026-07-31T21:00:00Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
sources:
  - id: measurement
    resource: projects/k1/web/packages/ingestion/src/__tests__/k1-extraction-prompt.test.ts
    title: recorded negative result — transcript agreed with the wrong figure on 25 of 25 wrong readings
    last_modified: 2026-07-31
  - id: fix
    resource: projects/k1 commit adc44e7
    title: "fix(extraction): catch the misread-row class in validation, not in the prompt"
    last_modified: 2026-07-31
  - id: gate
    resource: projects/k1/web/packages/ingestion/src/cross-budget-gate.ts
    title: k1 cross-budget gate, header comment carries the measured rates
    last_modified: 2026-08-08
  - id: gate-commit
    resource: k1@8584370
    title: "feat(ingestion): default thinking off, add cross-budget disagreement gate"
    last_modified: 2026-08-08
not:
  - term: "having the model echo which row / page / field it read a value from, then validating the value against that echo"
    why: "the echo is produced by the same read that produced the error, so the two agree exactly when you need them to disagree"
    instead: "check the value against a field the model filled independently, or against a second source, then measure the detector's catch rate on known-bad cases before shipping it"
  - term: "emit a verbatim transcript first, fill the fields from it, then compare the two"
    why: "the transcript carries the same misread; on 25 wrong readings it matched the wrong figure 25 times"
    instead: "compare each figure against a different field on the same document that has a mechanical relationship to it"
  - term: "run the same extraction 3 times and gate on majority agreement"
    why: "an error caused by the configuration reproduces identically every pass, so all three votes agree, are all wrong, and the gate reports high confidence"
    instead: "vary the parameter suspected of causing the failure and compare across settings"
---

# The trap

Any check built from a second output of the same model under the same conditions
agrees with the first output on exactly the cases it was built to catch. The
model has one vantage point, and asking it again does not add one.

Two shapes, both of which pass code review.

The first is a self-witness: ask the model to record how it read something, then
validate the value against that record. Echoing the source location onto each
field ("set `row` to the row number you read this from") produced a location
copied straight out of the schema template the model was handed, so the check
fired on nothing, ever. Emitting a verbatim transcript first and filling fields
from it produced a transcript carrying the same misread.

The second is self-consistency: sample N times, keep the majority. That filters
error which is random per call. When the error comes from the configuration, every
repeat reproduces it, the votes are unanimous, and the agreement gate stamps the
wrong answer as high confidence.

Before building either, check whether the errors you want to catch reproduce.
Re-run the documents that failed, several times, under the same settings. Errors
that come back identically need a different axis of diversity.

# Why it matters

Both designs ship and then report zero problems forever, which reads as evidence
the data is clean. That costs more than doing nothing, because it retires the
question. An agreement gate is sold as the control that catches bad extractions,
so a deterministic error passes through wearing a confidence score and reviewers
stop looking.

Before shipping any detector, run it over cases known to be bad and print the
catch rate. A detector that fires on 0 of the known bad cases is not one.

# Evidence

k1's K-1 extraction shifted figures one row up: the distributions line landed in
box 18 and box 19 emptied, box 14's self-employment loss landed in box 13.
Confirmed against the source PDFs on 28 of 168 documents.

The transcript design, scored on the wrong readings it was written to catch:

```
transcript check on wrong Part III readings:   fired on 0/25
transcript check on correct Part III readings: fired on 0/23
```

What replaced it compares each figure against a *different* field on the same
form. Box 19 distributions has a second witness in Part L withdrawals, and
Schedule K-1 prints deductions as positive amounts, so:

```
Part L reports withdrawals and box 19 is empty   -> 10 of 28
box 18 carries the Part L withdrawals figure     -> 15 of 28
box 19 disagrees with Part L withdrawals         ->  3 of 28
box 12 or box 13 is negative                     ->  6 of 28
together: 21 of 28 bad documents, 0 of 140 correct documents
```

The misread partnership name needed a vantage point further out again. Nothing on
one form contradicts its own name, so it was caught one level up, where a single
EIN carrying two spellings across a project is visible.

The voting half, measured on Gemini 2.5 Flash extracting Schedule K-1 PDFs at
temperature 0. Thinking budget 0 beat a pinned 2048 across 175 documents (94.2%
against 90.8% box accuracy). On 9 of the 17 documents where budget 0 lost, it lost
the *same* boxes on all 4 repeats: codes 13W, 20A and 20Z came back with a null
amount, while budget 2048 read them exactly.

Over 175 documents, 2125 boxes, both budgets scored against ground truth:

```
both arms same verdict   1949 boxes   98.5% correct   (off 95.5%, 2048 92.1%)
both present, different    89 boxes   off right 78, 2048 right 11, neither 0
```

Agreement across two different budgets beats either budget alone. Agreement across
three repeats of one budget would have certified the dropped codes as correct.

Two arms at different settings also came in cheaper than three samples at one
setting, $0.0207 against $0.0238 per document.

Related: [audits must report their own coverage](audits-must-report-their-own-coverage.md),
where a check that could not run is reported as a check that passed.
