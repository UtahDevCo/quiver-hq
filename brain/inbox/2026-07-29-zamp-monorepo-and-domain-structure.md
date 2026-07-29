---
type: Observation
title: Monorepo layout — apps, domains, utils
description: pnpm workspace on Turborepo. Business logic in versioned domain packages following CQRS; apps consume them.
kind: module
proposed_layer: project
proposed_project: zamp
observed_in: zamp
tags: [monorepo, architecture, ddd, cqrs]
generated: { by: claude/opus-5, at: 2026-07-29T14:06:39Z }
status: draft
sources:
  - id: agents-md
    resource: projects/zamp/AGENTS.md
    title: zamp AGENTS.md — Architecture Overview
    last_modified: 2026-07-25
---

# Observation

**`apps/`** — `company` (3000), `admin` (3001), `partner` (3002),
`shopify` (3003), `api` (3005), `api-docs` (3006), `background` (Inngest runner).

**`domains/`** — business logic as workspace packages:

```
domain/src/
  mutations/      writes
  queries/        reads
  background.ts   Inngest jobs
  *.schema.ts     co-located Zod (preferred)
  schemas.ts      centralized (legacy, being removed)
  constants.ts
```

Patterns: CQRS · `Result<T, Error>` via `ts-results-es` · Inngest events for
cross-domain communication.

**`utils/`** — db, ui libs, feature flags, formatting, validators, logging, events.

**Migration in flight:** `domains/internal-api` (legacy tRPC) is being replaced
by React Server Actions co-located in the consuming app.

# Why it matters

The domain package boundary is what makes the `Result` pattern and the sharding
rules enforceable in one place. Reading a domain's `mutations/` and `queries/`
directories is the fastest way to understand a slice of the product.
