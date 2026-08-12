---
type: Observation
title: A recompute-from-source backfill fabricates data wherever the stored value was null
description: Re-deriving a column from a row's own inputs looks lossless, but on rows whose input is absent the deriving function returns its defaults, and the backfill writes a confident empty record over an honest null.
kind: failure-mode
proposed_layer: meta
tags: [backfill, migration, data-quality, defaults]
generated: { by: claude/opus-5, at: 2026-08-10T18:21:23Z }
status: draft
sources:
  - id: backfill
    resource: projects/k1/web/packages/db/src/renormalize-extractions.ts
    title: "k1 821d31d — renormalizeTenantK1Extractions, degenerate and would_lose_codes refusals"
    last_modified: 2026-08-10
  - id: dry-run
    resource: projects/k1
    title: "gregory-test dry run: 27 rows changed, 10 of them null -> empty form claiming the current tax year"
    last_modified: 2026-08-10
not:
  - term: "recomputed !== stored, so write it"
    why: "the deriving function answers even when it has nothing to read, and its answer is defaults"
    instead: "require the recomputed record to be substantively populated, and refuse rows where it is not"
---

# Observation

A backfill that recomputes a derived column from each row's own stored inputs reads as the safe
kind of migration. No external calls, no new data, just re-running current code over old input.
The hazard is rows whose input is missing. The deriving function still returns a value, built
from its defaults, and `recomputed !== stored` is true, so a diff-driven backfill writes it.

In k1 a normalizer fix had left already-written canonical forms missing their code letters, so
the repair recomputed `normalized_k1_json` from the `initial_output_json` on each row. The dry
run offered 27 rows. 17 were the real repair, recovering 100 code letters. The other 10 stored
`null` and recomputed to a Schedule K-1 claiming the current tax year with every identity field
`""` and no box data, because those rows carry no provider tag and the fallback normalizer fills
defaults from nothing.

Writing them would have moved every consumer from "no data for this document" to a specific,
confident, wrong tax return.

The guard is not a diff. It is a floor on what counts as a result: the recomputed record must be
substantively populated in the dimension the backfill exists to repair, and a row that fails
that is refused and named. Two counters, `degenerate` and `would_lose_codes`, kept separate from
`unchanged`, because a refusal is a row that cannot be repaired and not a row that turned out
fine.

# Why it matters

The direction of the damage is what makes this expensive. The pre-backfill state was an honest
absence, which a UI renders as empty and a reviewer reads as "not extracted". The
post-backfill state is a populated record. Nothing downstream can tell it was manufactured, and
the tax year it invents is today's, so it is plausible.

It is also invisible in the aggregate the backfill reports. "27 rows changed, 100 code letters
recovered" is true and describes only the 17. The 10 contribute zero to the headline number
while doing all of the harm. This is [[audits-must-report-their-own-coverage]] pointed at a
write path: the count of rows touched is not the count of rows improved.

The tell was cheap and would have been missed by trusting the summary. 12 of the 27 rows showed
`0 -> 0` on the letters-recovered column, meaning they changed for some reason other than the one
the backfill was written for. Any row a migration rewrites for a reason you cannot name is a row
to inspect before it is a row to write. Related: [[verify-a-write-actually-happened]] covers
reading state back afterward; this is the check that belongs before.

# Evidence

The recomputed form for the 10 refused rows, field by field, against a stored `null`:

```
  : null -> undefined
  formType: undefined -> "1065"
  taxYear:  undefined -> 2026        # today's year, from a default
  entity.ein: undefined -> ""
  entity.name: undefined -> ""
  recipient.tin: undefined -> ""
  ... 16 further identity fields, all "" 
```

The deriving helper's own shape made this reachable: it returns `undefined` when there is no
input to read and `null` when normalization throws, and both had to be kept apart from a real
result. A `catch` that maps a throw to `null` and a caller that treats `null` as "nothing to fix"
turns a crash into a silent pass.

The floor that fixed it counts boxes carrying a value, and deliberately excludes `formType` and
`taxYear`, which are exactly the two fields the fallback fills from nothing and so are what make
a blank record look populated. A box read as `0` counts as populated, because zero is a real
reading that carries into a basis calculation.
