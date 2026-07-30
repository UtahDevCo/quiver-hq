---
type: Observation
title: trikin independently corroborates four meta practices that had only zamp as a source
description: A repo with a different stack, different author history, and no shared tooling states the same file-naming, comment, export, and schema-colocation rules — which upgrades them from single-source inference.
kind: practice
proposed_layer: meta
observed_in: trikin
tags: [corroboration, conventions, governance]
status: draft
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: agents, resource: projects/trikin/AGENTS.md, title: "React Component Development Guide — kebab-case files, PascalCase components, named exports, UPPER_SNAKE constants, comments only for non-obvious logic" }
  - { id: server-actions, resource: projects/trikin/AGENTS.md, title: "\"Server action files can ONLY export async functions. Do NOT export constants, types, or Zod schemas from server action files; move those to separate type/schema files.\"" }
---

# Observation

`brain/log.md` for 2026-07-29 records nine general practices promoted to `meta/`
from **zamp only**, with the note that single-source practices "carry more inference
risk". trikin is an independent second source for four of them:

- **`kebab-case-files-named-exports`** — stated in full, including the
  `UPPER_SNAKE_CASE` constants half and the no-default-exports half that the meta
  concept flags as load-bearing.
- **`minimal-comments`** — "add comments only to explain complex logic, non-obvious
  decisions, or important workarounds."
- **`colocate-schemas-with-what-they-validate`** — reached by a *different route*,
  which is the interesting part. trikin's reason is a Next.js constraint: a
  `"use server"` file may only export async functions, so schemas must live in a
  sibling. Same destination, independent derivation.
- **`small-single-purpose-files`** — corroborated as an *aspiration* only; see below.

Worth checking against `corroboration-requires-independent-sources` before counting:
the two repos share an author, so this is "how Chris works everywhere" rather than
two teams converging by accident. That is the weaker form of corroboration but it is
also exactly what the meta layer is *for* — and `brain/conventions.md` says Chris's
assertion outranks corroboration anyway.

# Why it matters

Three of the four move from "inferred from one repo" to "stated independently in
two", which is the threshold `conventions.md` sets for a practice being genuinely
general. That is worth recording explicitly, because the alternative is that the
next harvest re-derives the same doubt.

The fourth is a genuine negative finding and more useful than the three positives:
**`small-single-purpose-files` is violated at scale in trikin.** `sync-leads.ts` is
1,821 lines, `pull-from-atlas.ts` is 913, `queries/leads.ts` is 861, and
`admin-leads-table.tsx` is 757 against a ~300-line component budget. So the practice
is not corroborated as *behaviour* — only as intent, and only because trikin's own
`AGENTS.md` does not actually state it.

Per "the brain describes; it does not retrofit", that is not a defect to go fix.
Most of those files are being deleted in the pivot anyway. It is worth knowing that
the practice has one repo demonstrating it and one repo aspiring to it.

# Evidence

Two conventions in trikin's `AGENTS.md` that zamp does *not* have, and which are
therefore project-layer rather than corroboration: a prescribed intra-file ordering
(imports → types → constants → render → exported functions → orchestrators → leaf
helpers, with each function followed by the helpers it calls), and a ban on IIFEs
inside a React render in favour of a component declared below the consumer.
