---
type: Observation
title: Extracting one step into a Result-returning helper commits the whole function to that shape
description: A function mixing extracted Result helpers with an inline try/catch forces the reader to switch between two error-handling styles mid-function; pick one shape per function.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [error-handling, result-type, refactoring, consistency, code-review]
status: draft
not:
  - term: "two extracted Result-returning helpers followed by a raw try/catch for the third step"
    why: "the reader re-orients between two error-handling conventions inside one function, and the inline step's failure is reported in a different shape from its siblings"
    instead: "extract the remaining steps too, so every step is uniformly `const r = await step(); if (r.isErr()) return r;`"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Try/catch extraction is a commitment, not a one-off'" }
---

# Observation

If an orchestrator function has several side-effecting steps and you extract one of
them into a `Result`-returning helper, extract the rest as well. One shape per
function.

```typescript
// ❌ Mixed: two extracted helpers plus one inline try/catch
const rawResult = await loadTransformOutput({ ... });
if (rawResult.isErr()) return rawResult;
const validated = validateTransactions(rawResult.value);
if (validated.isErr()) return validated;
try {
  await s3Client.send(new PutObjectCommand({ ... }));
} catch (error) {
  return Err(new Error("Upload failed", { cause: error }));
}

// ✅ Symmetric: every step is a Result-returning helper
const rawResult = await loadTransformOutput({ ... });
if (rawResult.isErr()) return rawResult;
const validated = validateTransactions(rawResult.value);
if (validated.isErr()) return validated;
const uploadResult = await uploadZampCsv({ ... });
if (uploadResult.isErr()) return uploadResult;
```

# Why it matters

The mixed form is worse than either consistent alternative, which is what makes it
worth stating. Uniform inline try/catches are readable. Uniform extracted helpers
are readable. A function with both makes the reader re-derive, at each step, which
convention is in play — and the visual asymmetry suggests the inline step is special
in some way when it usually isn't.

It also matters for how the failure surfaces: the extracted steps produce errors
built and labelled in one place, while the inline step builds its own, so
error-message conventions drift within a single function.

Practically, this shows up during review of an incremental refactor — someone
extracts the step they were already touching and leaves the neighbors. The rule
makes the expectation explicit: extraction is a commitment for the whole function,
so either finish it or leave it alone.

# Evidence

Recorded in `patterns.md` under Code Style with the S3-upload case above.

Proposed `meta`. Companion to the same-day observation on one throwable per
try/catch: that one says *how narrow* each catch should be, this one says the
chosen shape must be applied uniformly.
