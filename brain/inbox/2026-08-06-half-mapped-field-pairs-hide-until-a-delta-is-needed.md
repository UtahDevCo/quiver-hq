---
type: Observation
title: A half-mapped beginning/ending field pair stays invisible until something needs the delta
description: Normalizers that map only the ending column of a paired field look complete to every display consumer and silently invert the sign of the first computation that subtracts them.
kind: failure-mode
proposed_layer: meta
tags: [normalization, data-modelling, absent-vs-zero]
generated: { by: claude/opus-5, at: 2026-08-06T15:07:14Z }
status: draft
sources:
  - id: fix
    resource: projects/k1/web/packages/db/src/k1-canonical.ts
    title: normalizeGoogleK1Output mapped part_k .ending but never .beginning
    last_modified: 2026-08-06
  - id: commit
    resource: "k1@317cd6c"
    title: "feat(db): adapt canonical K-1 records into the @k1/tax basis engine"
    last_modified: 2026-08-06
not:
  - term: "treat the absent beginning column as 0 so the computation can proceed"
    why: "absent and a real zero are the same number to the consumer and give opposite answers; on a K-1 an absent beginning liability share reads as a section 752(a) deemed contribution equal to the entire ending share, inflating basis"
    instead: "make the missing column a blocking gap and return no input at all, so the caller cannot get a plausible wrong answer"
---

# Observation

When a source field comes as a `beginning`/`ending` pair, a normalizer that maps only
one half produces a record that looks complete to every consumer that displays values,
and is wrong only for consumers that subtract the two. Since display consumers ship
first, the defect can sit in the write path across an entire corpus before anything
needs the delta.

Two habits catch it. Check paired fields as pairs when auditing coverage, rather than
counting populated fields one at a time. And where a field can be legitimately absent,
make absence a distinct value the consumer must handle, not a default that silently
becomes zero.

# Why it matters

The consumer that needs the delta is usually a computation, and a computation given a
zero for a missing operand does not fail. It returns a confident wrong number.

In k1, `normalizeGoogleK1Output` read `part_k.<liability>.ending` and never
`.beginning`. All 174 documents in the V4 corpus stored the beginning column as absent
while the raw extraction carried it on 172 of them. Nothing noticed, because the matrix
UI only ever displayed the ending column. The first consumer that needed both was the
section 752 liability delta in the basis walk, where a missing beginning column reads as
a rise from zero: a deemed cash contribution equal to the partner's whole ending
liability share. That inflates outside basis and releases suspended losses that should
still be suspended, and the resulting walk is internally consistent, so no
reconciliation check fires.

A prior measurement had also been taken against the normalized store and recorded the
beginning column as populated on 0 of 691 rows. Read as an extraction failure, it made
the downstream feature look blocked on re-extracting the corpus. The extractor had been
reading the field correctly the whole time.

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

The adapter written on top now refuses rather than defaults:

```ts
if (missing.length > 0) {
  gaps.push({ field: `recipient.liabilities.${column}`, severity: "blocking", ... })
  return null
}
```

A mutation replacing that guard with `if (false)` is killed by a test asserting the
input is `null`, paired with a control asserting the same K-1 with the column present
does produce an input. Without the control, "blocked" would be indistinguishable from
"the adapter never works".
