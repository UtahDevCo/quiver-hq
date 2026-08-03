---
type: Observation
title: A per-record validator cannot catch a rule the generator applied consistently
description: Every document-internal check passed on a corpus whose allocation rule was legally wrong; only a cross-document sum contradicted it.
kind: failure-mode
proposed_layer: meta
tags: [validation, test-data, invariants, measurement]
generated: { by: claude/opus-5, at: 2026-08-03T15:10:00Z }
status: draft
sources:
  - id: measurement
    resource: projects/k1/data/K1_Corpus_v2/manifest.json
    title: "Alpha 2021 partner K-1s sum to -144,753 against a Schedule K of -450,000; 175/175 documents pass every internal check"
    last_modified: 2026-08-03
  - id: spec
    resource: projects/k1/data/multi_tier_suspended_loss_engine.txt
    title: "Part 8 point E, the author's own flag that the tier claim is load-bearing and unconfirmed"
    last_modified: 2026-08-03
not:
  - term: "declaring a generated corpus correct because every per-document invariant passes"
    why: "a generator that applies one wrong rule to every record produces records that are all internally consistent and all wrong, so per-record checks are structurally unable to see it"
    instead: "add at least one check that spans records and has an external anchor: the parts must sum to a total that was computed independently of the parts"
---

# Observation

A validator that only ever looks at one record cannot detect a rule error, because the
generator applied the same rule to every record and each one is therefore self-consistent.
The error is only visible where records have to agree with something outside themselves.

For allocation data the anchor is a summation: the parts must add up to a total that was
computed without reference to the parts. For a Schedule K-1 that is the partnership return
the K-1s came from. Every partner's box 1 must sum to the partnership's own Schedule K
line 1, and nothing on any single K-1 can tell you whether it does.

Two corollaries worth carrying:

- When you hand someone an invariant to enforce, they may enforce it by changing the data
  rather than by fixing the model. Get the invariant right, because an enforced wrong rule
  is harder to spot than an unenforced one.
- When a spec author flags their own load-bearing claim as unconfirmed, check whether the
  implementation matches the claim before checking whether the claim is true. Here the
  claim was right and the implementation contradicted it.

# Why it matters

The corpus in question passes 12 internal checks on 175 of 175 documents, including a
capital-account roll-forward and an income tie-out that the previous version failed on
every document. Read either the self-report or the per-document checks and you conclude it
is correct. The one cross-document check disagrees by 305,247 dollars on a single
partnership-year.

Worse, the mechanism that was supposed to be exercised never runs. The intermediate entity
passed through exactly 100% of what it received in all four years, so the cascade the
specification describes is untested while appearing to be covered.

# Evidence

I specified an invariant for a synthetic Schedule K-1 corpus: a partner's ending capital
account plus their share of liabilities must never be negative. That is wrong. Section
704(d) limits the partner's *deduction*, not the partnership's *allocation*, and the
tax-basis capital account is reduced by the loss as allocated whether or not it is
deductible. Capital plus liabilities going negative is the signal that a carryforward
exists, and I had called it impossible.

The generator enforced it the only way it could, by shrinking the allocation. Result:

```
Alpha 2021 box 1     partner K-1s -144,753   Schedule K -450,000
Alpha 2023 box 1     partner K-1s  352,761   Schedule K  620,000
Alpha 2024 box 1     partner K-1s  871,992   Schedule K  910,000
Alpha 2022 box 13W   partner K-1s        0   Schedule K   18,000
```

Every one of those documents reconciles internally, because the capital account was
derived from the truncated income figure. Item L ties to Part III on 175 of 175. The
detector I had shipped for capital-account reconciliation stays silent on all of them, and
correctly so: the document is consistent. It is the corpus that contradicts the return.

The check that found it took the manifest's independently stated partnership-level total
and compared it against the sum of the documents. That is 20 lines of code and it is the
only one of my 13 checks that could have found this class at all.
