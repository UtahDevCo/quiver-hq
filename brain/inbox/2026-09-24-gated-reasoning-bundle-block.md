---
type: Observation
title: Adding a gated reasoning-bundle block in k1's AI Analyst
description: To surface a new deterministic data source to the reasoning model, add a parallel optional block across four edit sites following the extractionQuality/otherDocuments/reconciliation/individualReturns examples.
kind: pattern
proposed_layer: project
proposed_project: k1
tags: [reasoning, ai-analyst, prompt, k1]
generated: { by: claude/opus-4.8, at: 2026-09-24T19:57:31Z }
status: draft
sources:
  - id: reconciliation-block
    resource: projects/k1/web/packages/db/src/project-query-reasoning.ts
    title: reconciliationView builder + questionNeedsReconciliation + gated attach (commit 7bb2084)
    last_modified: 2026-09-23
  - id: individual-returns-block
    resource: projects/k1/web/packages/ai/src/project-query-reasoning.ts
    title: IndividualReturnsView + INDIVIDUAL RETURNS prompt section + version 18 (commit fa2de52)
    last_modified: 2026-09-24
  - id: gate-classifier
    resource: projects/k1/web/packages/db/src/reasoning-gate-classifier.ts
    title: ReasoningGateKey union + GATE_SPECS + noul fan-out
    last_modified: 2026-09-24
---

# Observation

The k1 AI Analyst feeds the model a "reasoning bundle" of optional blocks, each
gated by whether the question needs it. To add a new deterministic data source
(a computed view, an extracted document type), add a parallel optional block by
copying an existing one — `extractionQuality`, `otherDocuments`, `reconciliation`,
or `individualReturns` are worked examples. Four edit sites:

1. **@k1/ai `packages/ai/src/project-query-reasoning.ts`**: a serializable
   `FooView` type; a `foo?: FooView` member on `ProjectReasoningBundle`; a prose
   section in `REASONING_SYSTEM_PROMPT` explaining what the block is and how to
   cite it; bump `REASONING_SYSTEM_PROMPT_VERSION` with a changelog line. (@k1/ai
   must not depend on @k1/db, so the View is a plain serializable shape.)
2. **@k1/db `packages/db/src/project-query-reasoning.ts`**: a pure `fooView(...)`
   builder returning `FooView | null` (null omits the block); a `FOO_TERMS` array
   with a `questionNeedsFoo(question)` keyword gate; the
   `if (gates.foo.needsBlock) { bundle = { ...bundle, foo } }` attach in
   `answerTenantProjectReasoning`.
3. **@k1/db `reasoning-gate-classifier.ts`**: extend the `ReasoningGateKey`
   union, the `REASONING_GATE_KEYS` array, the `GATE_SPECS` record, and the
   `noul()` fan-out; import the keyword gate.
4. **Tests**: builder (surface / omit-when-empty / sort) and the keyword gate in
   `project-query-reasoning.test.ts`; update the fan-out mock in
   `reasoning-gate-classifier.test.ts`.

# Why it matters

Miss the gate-classifier fan-out mock and the classifier test throws
(`answers[key].noul` on undefined) because `REASONING_GATE_KEYS` iterates a key
the mock did not return. Miss the version bump and a prompt change ships
untracked (the hash still records what ran, but intent is lost). Skip the null
return and an empty block burns tokens and tells the model a source exists when
it has no rows. The gate is two-tier — a keyword fallback plus a calibrated
TypeSafe `noul`, biased to recall — so a paraphrase with none of the terms still
attaches when TypeSafe is configured; the keyword list is the floor, not the
whole gate.

# Evidence

Built twice in one session: `reconciliation` (commit 7bb2084, prompt v16→17) and
`individualReturns` (commit fa2de52, v17→18). Both verified live: asking the
Analyst a reconciliation question returned the exact open ledger-vs-Item-L
residuals from the block; asking for a 1040's 6198/8582 losses returned the typed
per-activity figures.

Two cross-cutting gotchas surfaced:
- A builder that calls a function in another @k1/db module which imports back
  from `project-query-reasoning` (e.g. `computeProjectReconciliationView` in
  `reconciliation-view.ts`) creates a static import cycle. Use a dynamic
  `await import("./reconciliation-view")` at the attach site; an `import type`
  for the view's type is erased and safe.
- @k1/db must not import @k1/ingestion, so an extracted shape is stored as a
  local `Stored*` interface (mirrors `StoredOtherDocumentExtraction`). A new
  `k1_extractions` column is added by an idempotent ALTER in
  `ensureK1ExtractionsTable`; reads self-heal because `listGraphRowsForTenant`
  catches the failed SELECT, ensures the table, and retries — so no manual
  migration is needed and the new column is safe to deploy before any backfill.

# not

not:
  - term: "add the gate key to the union but skip the fan-out mock in reasoning-gate-classifier.test.ts"
    why: "REASONING_GATE_KEYS iterates the new key and answers[key] is undefined, so the classifier test throws at answers[key].noul"
    instead: "add the key's noul answer to the mock outcome in the fan-out test"
  - term: "static import computeProjectReconciliationView from reconciliation-view.ts into project-query-reasoning.ts"
    why: "reconciliation-view.ts imports latest1065FormsFromRows back from project-query-reasoning, a static cycle"
    instead: "dynamic import at the attach site; import type only for the type"
