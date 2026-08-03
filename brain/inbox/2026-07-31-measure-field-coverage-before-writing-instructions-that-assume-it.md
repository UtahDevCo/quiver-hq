---
type: Observation
title: Measure field coverage on real rows before writing instructions that assume a field is populated
description: A declared optional field can be populated in 0% of stored rows; a schema tells you what is allowed, not what is there.
kind: practice
proposed_layer: meta
tags: [llm, prompt-engineering, data-quality, probes]
generated: { by: claude/opus-5, at: 2026-07-31T14:26:40Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/packages/ai/src/project-query-reasoning.ts
    title: k1 prompt v5 note — coverage measured over 679 stored rows before writing the Box K bullets
    last_modified: 2026-07-31
  - id: fix
    resource: projects/k1 commit 98d32a3
    title: "fix(reasoning): put Box L and Box K in the evidence bundle"
    last_modified: 2026-07-31
not:
  - term: "reading the type definition to decide what the model can rely on"
    why: "an optional field declared in the schema may be populated nowhere in the data"
    instead: "count present/absent per field over every stored row, then write the instruction against the counts"
---

# Observation

Before writing an instruction that tells a model to compute something from field
X, count how many stored rows actually have field X. A schema says what is
permitted. Only the data says what is there, and for optional fields the answer is
often zero.

Write the throwaway probe, run it over every row you can reach, and put the counts
in the commit message or a comment beside the instruction. The numbers are what
make the instruction reviewable later; "field X is usually absent" rots, "0 of 679"
does not.

# Why it matters

An instruction premised on an absent field produces a confidently wrong answer
rather than a refusal, and the specific wrong answer is usually the worst one
available: the model reads the missing value as zero. For a running-balance
computation, zero is not a small error. Reading a missing beginning balance as zero
books the entire ending balance as a first-period increase.

Coverage also changes what the instruction should say. A field present 25% of the
time needs the absent case handled as the common path, not as an edge case
mentioned last.

# Evidence

k1, writing the Box K (partner's share of liabilities) section of a reasoning
prompt. The Section 752 basis adjustment is the year-over-year movement in those
liabilities, so the natural instruction is "take the beginning-to-ending
movement". The type declares both columns:

```ts
liabilitiesNonrecourseBegin?: number
liabilitiesNonrecourseEnd?: number
```

A probe over every stored row in six tenants:

```
rowsSeen: 679, boxL: 505, method: 168, c704: 0,
nrBegin: 0, nrEnd: 337, qnrfEnd: 337, recBegin: 0, recEnd: 337
```

Zero rows carry a beginning figure. The instruction was rewritten to derive the
movement from the prior year's ending figure and to say so, with an explicit "do
not treat a missing beginning as zero". `capitalAccountMethod` at 168/679 turned
"state the basis" from an aside into the common path, and `c704: 0` meant a field
worth no prompt words at all.

The probe also surfaced two things no schema would have: three of thirteen
projects had the field populated on zero rows, so the fix could not help them at
all, and one pair of liability categories was identical on 337/337 rows, which is
either a mapping bug or a fixture artifact and needed flagging either way.
