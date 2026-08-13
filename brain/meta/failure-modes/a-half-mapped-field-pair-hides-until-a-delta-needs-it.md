---
type: Failure Mode
title: A half-mapped beginning/ending field pair hides until something needs the delta
description: A normalizer mapped the ending column and never the beginning. 172 of 174 documents carried it in the raw extraction and 0 of 174 in the normalized store, and the first consumer that subtracted them read the gap as a deemed contribution.
tags: [normalization, data-modelling, absent-vs-zero, coverage]
generated: { by: claude/opus-5, at: 2026-08-06T15:07:14Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "treating the absent beginning column as 0 so the computation can proceed"
    why: "absent and a real zero are the same number to the consumer and give opposite answers; on a K-1 an absent beginning liability share reads as a section 752(a) deemed contribution equal to the entire ending share, inflating basis"
    instead: "make the missing column a blocking gap and return no input at all, so the caller cannot get a plausible wrong answer"
  - term: "measuring extraction coverage against the normalized store"
    why: "0 of 691 rows populated reads as an extraction failure and sends the work to re-extracting the corpus; the extractor had been reading the field correctly the whole time"
    instead: "measure the raw payload and the normalized record separately, and compare the two counts"
  - term: "counting populated fields one at a time when auditing coverage"
    why: "a pair with one half mapped scores as 50% populated and looks like ordinary sparsity rather than a mapping bug"
    instead: "check paired fields as pairs, and flag any pair where one half is systematically absent"
  - term: "a test asserting the guard returns null"
    why: "an adapter that never works also returns null, so `blocked` and `broken` are the same assertion"
    instead: "pair it with a control asserting the same record with the column present does produce an input"
sources:
  - id: fix
    resource: projects/k1/web/packages/db/src/k1-canonical.ts
    title: normalizeGoogleK1Output mapped part_k .ending but never .beginning
    author: claude/opus-5
    last_modified: 2026-08-06
  - id: commit
    resource: "k1@317cd6c"
    title: "feat(db): adapt canonical K-1 records into the @k1/tax basis engine"
    author: claude/opus-5
    last_modified: 2026-08-06
---

# The trap

When a source field comes as a `beginning`/`ending` pair, a normalizer that maps only
one half produces a record that looks complete to every consumer that displays
values, and is wrong only for consumers that subtract the two. Display consumers ship
first, so the defect can sit in the write path across an entire corpus before
anything needs the delta.

# Why it matters

The consumer that needs the delta is usually a computation, and a computation given a
zero for a missing operand does not fail. It returns a confident wrong number.

In k1, `normalizeGoogleK1Output` read `part_k.<liability>.ending` and never
`.beginning`. All 174 documents in the V4 corpus stored the beginning column as
absent while the raw extraction carried it on 172 of them. Nothing noticed, because
the matrix UI only ever displayed the ending column. The first consumer that needed
both was the section 752 liability delta in the basis walk, where a missing beginning
column reads as a rise from zero: a deemed cash contribution equal to the partner's
whole ending liability share. That inflates outside basis and releases suspended
losses that should still be suspended, and the resulting walk is internally
consistent, so no reconciliation check fires.

A prior measurement had been taken against the normalized store and recorded the
beginning column as populated on 0 of 691 rows. Read as an extraction failure, it
made the downstream feature look blocked on re-extracting the corpus.

# Evidence

The Google branch of the normalizer, before the fix:

```ts
liabilitiesNonrecourseEnd:
  cleanNumber(readPath(data, "part_k.nonrecourse.ending")) ??
  cleanNumber(readPath(data, "part_k.nonrecourse.amount")),
// no liabilitiesNonrecourseBegin at all
```

The Extend branch of the same file, 350 lines earlier, mapped both halves. The two
normalizers had drifted and the type permitted it, because every field on
`K1RecipientInfo` is optional.

Coverage measured the two ways, on the same 174 rows:

```
raw extraction        172/174  part_k.nonrecourse.beginning
normalized record       0/174  recipient.liabilitiesNonrecourseBegin
```

The adapter written on top refuses rather than defaults:

```ts
if (missing.length > 0) {
  gaps.push({ field: `recipient.liabilities.${column}`, severity: "blocking", ... })
  return null
}
```

A mutation replacing that guard with `if (false)` is killed by a test asserting the
input is `null`, paired with a control asserting the same K-1 with the column present
does produce an input. That control is the difference between a passing test and
[a-capability-probe-needs-a-positive-control](a-capability-probe-needs-a-positive-control.md).
