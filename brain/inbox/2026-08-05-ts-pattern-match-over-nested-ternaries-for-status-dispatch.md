---
type: Observation
title: Dispatch on a status union with ts-pattern match(), not nested ternaries
description: Once a status union has three or more cases, match() with .exhaustive() makes the branch set readable and makes a newly added variant a compile error instead of a silent fallthrough.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [typescript, ts-pattern, control-flow, exhaustiveness, react]
status: draft
not:
  - term: "a ? x : b ? y : c ? z : fallback for a status union"
    why: "unreadable past two levels, and adding a new variant to the union silently lands in the fallback instead of failing to compile"
    instead: "match(value).with(...).exhaustive() for fixed enums, or .otherwise(...) for a deliberate fallback"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'Prefer ts-pattern match() over nested ternaries for status dispatch'" }
  - { id: callsites, resource: "projects/zamp/apps — transmission-table.client.tsx, your-subscription/page.tsx, economic-nexus/page.tsx, import-session page.tsx", title: "four established match() dispatch sites" }
---

# Observation

When a component, page, or value branches on a status/state union with three or more
cases, use `match()` from `ts-pattern` rather than nested ternaries or an if-chain.

Useful pieces of the API:

- `P.union(...)` groups several variants under one handler.
- `.when(predicate, handler)` accepts type guards.
- `.exhaustive()` for a fixed enum where every case is handled.
- `.otherwise(fallback)` for an explicit, deliberate fallback.

# Why it matters

Readability is the visible reason; exhaustiveness is the durable one.

`.exhaustive()` turns "someone added a variant to the union" into a compile error at
every dispatch site. The nested-ternary version has a trailing `: fallback`, so the
new variant renders the fallback — which is frequently a plausible-looking empty
state or a neutral badge. Nobody notices, and the gap surfaces later as "why does
this status show nothing?"

That's the whole argument for the dependency: it converts a silent behavioral gap
into a build failure. `.otherwise()` should be a decision, not a leftover.

# Evidence

`patterns.md` records this as established across four zamp dispatch sites
(`transmission-table.client.tsx`, `your-subscription/page.tsx`,
`economic-nexus/page.tsx`, the import-session `page.tsx`), and notes `.when()`
being used with real type guards such as `isLiveImportSessionStatus`.

Proposed `meta` as a practice. Note it carries a dependency (`ts-pattern`), so a
reviewer may prefer to split the "use ts-pattern" stack choice from the
"dispatch exhaustively" practice — the latter is achievable with a switch plus a
`never` check in a repo that doesn't want the library.
