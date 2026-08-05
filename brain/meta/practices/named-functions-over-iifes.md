---
type: Practice
title: Prefer a named local function over an IIFE for a derived value
description: An IIFE inverts reading order — the body becomes mandatory reading before the assignment makes sense. A name costs the same and documents the computation.
tags: [code-style, javascript, typescript, naming, readability]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "const value = (() => { ...branches... })();"
    why: "nothing names the computation, so the reader must mentally execute the whole block before understanding the line it is assigned to"
    instead: "declare a named function and call it — the same length, and self-describing"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Prefer named local functions over IIFEs for derived values'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

When a derived value needs several statements, use a named function rather than an
immediately-invoked arrow.

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

Keep the function inside the component when it closes over local variables; hoist it
to module scope when it doesn't.

# Why the reading order matters

An IIFE inverts the normal contract. Ordinarily a name tells you what something is,
and you descend into the body only if you care. With an IIFE there is no name, so
understanding the block is mandatory before the assignment means anything. That cost
is paid by every future reader, to save the original author one identifier.

The hoisting rule is the secondary point and worth keeping: an IIFE that captures
nothing is a module-level helper trapped inside a function body, where it is
re-created on every call and can't be tested directly.

# Relation

The per-expression sibling of
[small-single-purpose-files](small-single-purpose-files.md): naming a unit of work is
what makes it reviewable, movable, and testable.
