---
type: Observation
title: Prefer a named local function over an IIFE for a derived value
description: An IIFE's parentheses say nothing about what the block computes; a named function costs the same and documents intent at the call site.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [code-style, javascript, typescript, naming, readability]
status: draft
not:
  - term: "const latestSession = (() => { ...branches... })();"
    why: "the reader has to execute the whole block mentally before learning what it produces, because nothing names the computation"
    instead: "declare a named function (resolveLatestSession) and call it — same length, self-describing"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Prefer named local functions over IIFEs for derived values'" }
---

# Observation

When a derived value needs several statements to compute, use a named function
rather than an immediately-invoked arrow.

```ts
// ❌ Anonymous IIFE — what does this block compute?
const latestSession = (() => {
  if (result === null) return null;
  if (result.isErr()) {
    captureException(result.error);
    return null;
  }
  return result.value;
})();

// ✅ The name says it
function resolveLatestSession() {
  if (result === null) return null;
  if (result.isErr()) {
    captureException(result.error);
    return null;
  }
  return result.value;
}
const latestSession = resolveLatestSession();
```

Put the function inside the component when it closes over local variables; hoist it
to module scope when it doesn't.

# Why it matters

An IIFE inverts the normal reading order. Ordinarily a name tells you what
something is and you descend into the body only if you care; with an IIFE there is
no name, so understanding the block is mandatory before you can understand the line
it's assigned to. That cost is paid by every future reader, in exchange for saving
the original author one identifier.

The hoisting rule matters as a secondary point: an IIFE that doesn't capture
anything is a module-level helper that got trapped inside a component body, where
it's re-created every render and can't be tested.

# Evidence

Recorded in `patterns.md` under Code Style with the `resolveLatestSession` case,
which is representative — a `Result` unwrap with a Sentry capture in the error
branch, a shape that recurs wherever `Result` types meet React.

Proposed `meta`: pure code-style judgment about JavaScript, no repo-specific nouns.
Sits alongside the existing meta practice on small single-purpose files.
