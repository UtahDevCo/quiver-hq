---
type: Failure Mode
title: A recompute-from-source backfill fabricates data wherever the stored value was null
description: Of 27 rows a dry run offered, 17 were the real repair and 10 stored null and recomputed to an empty tax form claiming the current year, because the deriving function answers even with nothing to read.
tags: [backfill, migration, data-quality, defaults]
generated: { by: claude/opus-5, at: 2026-08-10T18:21:23Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/fixing-the-write-path-does-not-fix-the-written-rows.md }
not:
  - term: "recomputed !== stored, so write it"
    why: "the deriving function answers even when it has nothing to read, and its answer is defaults"
    instead: "require the recomputed record to be substantively populated, and refuse rows where it is not"
  - term: "folding refused rows into the unchanged count"
    why: "a refusal is a row that cannot be repaired, and unchanged means a row that turned out fine; merging them hides the population the backfill could not help"
    instead: "count degenerate and would_lose_codes separately, and name the rows in each"
  - term: "a `catch` that maps a normalization throw to null, read by a caller as nothing to fix"
    why: "it turns a crash into a silent pass, and makes a genuine absence indistinguishable from a failed derivation"
    instead: "return undefined for no input and null for a throw, and keep both apart from a real result at every caller"
  - term: "counting formType and taxYear toward whether a recomputed record is populated"
    why: "those are exactly the two fields the fallback fills from nothing, so they are what makes a blank record look populated"
    instead: "count boxes carrying a value, treating a `0` as populated because zero is a real reading that carries into a basis calculation"
sources:
  - id: backfill
    resource: projects/k1/web/packages/db/src/renormalize-extractions.ts
    title: "k1 821d31d — renormalizeTenantK1Extractions, degenerate and would_lose_codes refusals"
    author: claude/opus-5
    last_modified: 2026-08-10
  - id: dry-run
    resource: projects/k1
    title: "gregory-test dry run: 27 rows changed, 10 of them null -> empty form claiming the current tax year"
    author: claude/opus-5
    last_modified: 2026-08-10
---

# The trap

A backfill that recomputes a derived column from each row's own stored inputs reads
as the safe kind of migration. No external calls, no new data, current code re-run
over old input. The hazard is rows whose input is missing: the deriving function
still returns a value, built from its defaults, and `recomputed !== stored` is true,
so a diff-driven backfill writes it.

In k1 a normalizer fix had left already-written canonical forms missing their code
letters, so the repair recomputed `normalized_k1_json` from the
`initial_output_json` on each row. The dry run offered 27 rows. 17 were the real
repair, recovering 100 code letters. The other 10 stored `null` and recomputed to a
Schedule K-1 claiming the current tax year with every identity field `""` and no box
data, because those rows carry no provider tag and the fallback normalizer fills
defaults from nothing.

Writing them would have moved every consumer from "no data for this document" to a
specific, confident, wrong tax return.

# Why the damage runs the direction it does

The pre-backfill state was an honest absence, which a UI renders as empty and a
reviewer reads as "not extracted". The post-backfill state is a populated record.
Nothing downstream can tell it was manufactured, and the tax year it invents is
today's, so it is plausible.

It is also invisible in the aggregate the backfill reports. "27 rows changed, 100
code letters recovered" is true and describes only the 17. The 10 contribute zero to
the headline number while doing all of the harm.

The tell was cheap and trusting the summary would have missed it. 12 of the 27 rows
showed `0 -> 0` on the letters-recovered column, meaning they changed for some reason
other than the one the backfill was written for. Any row a migration rewrites for a
reason you cannot name is a row to inspect before it is a row to write.

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

The guard is a floor on what counts as a result: the recomputed record must be
substantively populated in the dimension the backfill exists to repair, and a row
that fails is refused and named. Two counters, `degenerate` and `would_lose_codes`,
kept apart from `unchanged`.

# Where this sits

Sweeping the rows a broken write path left behind is the third task in
[fixing-the-write-path-does-not-fix-the-written-rows](fixing-the-write-path-does-not-fix-the-written-rows.md),
and this is how that sweep goes wrong: the recompute reaches rows the original defect
never touched. Counting rows touched instead of rows improved is
[audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md)
pointed at a write path. Reading state back afterward is
[verify-a-write-actually-happened](verify-a-write-actually-happened.md); the
populated-record floor is the check that belongs before.
