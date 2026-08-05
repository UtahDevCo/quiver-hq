---
type: Practice
title: One error-handling shape per function — extraction is a commitment, not a one-off
description: A function mixing extracted Result helpers with an inline try/catch forces the reader between two conventions mid-function; the mixed form is worse than either consistent alternative.
tags: [error-handling, result-type, refactoring, consistency]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
relations:
  - { kind: depends-on, target: /meta/practices/one-throwable-per-try-catch.md }
not:
  - term: "two extracted Result-returning helpers followed by a raw try/catch for the third step"
    why: "the reader re-orients between two error-handling conventions inside one function, and the inline step reports its failure in a different shape from its siblings"
    instead: "extract the remaining steps too, so every step reads as `const r = await step(); if (r.isErr()) return r;`"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Try/catch extraction is a commitment, not a one-off'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

If a function has several side-effecting steps and you extract one into a
`Result`-returning helper, extract the rest as well. One shape per function.

```typescript
// ❌ Mixed: two extracted helpers plus one inline try/catch
const raw = await loadTransformOutput({ ... });
if (raw.isErr()) return raw;
const validated = validateTransactions(raw.value);
if (validated.isErr()) return validated;
try {
  await storage.send(new PutObjectCommand({ ... }));
} catch (error) {
  return Err(new Error("Upload failed", { cause: error }));
}

// ✅ Symmetric: every step is a Result-returning helper
const raw = await loadTransformOutput({ ... });
if (raw.isErr()) return raw;
const validated = validateTransactions(raw.value);
if (validated.isErr()) return validated;
const uploaded = await uploadCsv({ ... });
if (uploaded.isErr()) return uploaded;
```

# Why the mixed form is worse than either alternative

That asymmetry is the point. Uniform inline try/catches are readable. Uniform
extracted helpers are readable. A function containing both makes the reader re-derive
at each step which convention is in play — and the visual difference implies the
inline step is special when it usually isn't.

It also drifts the error messages: extracted steps build and label their errors in one
place, while the inline step builds its own, so message conventions diverge inside a
single function.

Practically this surfaces during incremental refactors — someone extracts the step
they were already touching and leaves the neighbours. Naming it makes the expectation
explicit: finish the extraction or leave it alone.

# Boundary

This says nothing about *which* shape to choose; it says pick one per function.
[one-throwable-per-try-catch](one-throwable-per-try-catch.md) is what decides how
narrow each catch should be once you've committed to a shape. Local module idiom
decides which shape to prefer, per
[follow-local-conventions](follow-local-conventions.md).
