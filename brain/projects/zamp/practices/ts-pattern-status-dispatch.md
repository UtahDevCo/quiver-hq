---
type: Practice
title: Dispatch on a status union with ts-pattern match(), not nested ternaries
description: Once a status union has three or more cases, match().exhaustive() makes a newly added variant a compile error instead of a silent fallthrough into a plausible-looking empty state.
tags: [typescript, ts-pattern, control-flow, exhaustiveness, react]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "a ? x : b ? y : c ? z : fallback for a status union"
    why: "unreadable past two levels, and a new variant added to the union lands silently in the fallback rather than failing to compile"
    instead: "match(value).with(...).exhaustive() for fixed enums, or .otherwise(...) for a deliberate fallback"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — 'Prefer ts-pattern match() over nested ternaries for status dispatch'"
    author: human:christopher
    last_modified: 2026-08-05
  - id: callsites
    resource: projects/zamp/apps
    title: "established at transmission-table.client.tsx, your-subscription/page.tsx, economic-nexus/page.tsx, import-session page.tsx"
    last_modified: 2026-08-05
---

# The practice

When a component, page, or value branches on a status/state union with three or more
cases, use `match()` from `ts-pattern` rather than nested ternaries or an if-chain.

- `P.union(...)` groups several variants under one handler.
- `.when(predicate, handler)` accepts type guards.
- `.exhaustive()` for a fixed enum where every case is handled.
- `.otherwise(fallback)` for an explicit, deliberate fallback.

# Why exhaustiveness is the actual argument

Readability is the visible reason; exhaustiveness is the durable one.

`.exhaustive()` turns "someone added a variant to the union" into a compile error at
every dispatch site. The nested-ternary version ends in `: fallback`, so the new variant
renders the fallback — frequently a plausible-looking empty state or a neutral badge.
Nobody notices, and it surfaces later as "why does this status show nothing?"

That is the whole case for the dependency: it converts a silent behavioral gap into a
build failure. `.otherwise()` should be a decision, not a leftover.

# Why this sits in the project layer

The underlying practice — dispatch exhaustively over a closed union — is general, and a
repo without `ts-pattern` can get most of it from a `switch` plus a `never`-typed
default. What is repo-specific is the library choice, and this concept bundles the two.

If `ts-pattern` becomes a default across repos, the right shape is a `Stack` concept for
the library plus a `meta` practice for exhaustive dispatch. `meta/stacks/` is currently
empty, which is why this stays here for now.
