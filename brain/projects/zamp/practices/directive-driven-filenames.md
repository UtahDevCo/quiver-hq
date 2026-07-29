---
type: Practice
title: File extension declares the runtime boundary
description: A 'use client' file is named *.client.tsx; a 'use server' file is named *.action.ts. Which side of the boundary a file lives on is visible in the tree.
tags: [naming, rsc, nextjs]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — path instructions
    author: human:christopher
    last_modified: 2026-07-25
  - id: rsc-reviewer
    resource: projects/zamp/.claude/agents/rsc-boundary-reviewer.md
    title: rsc-boundary-reviewer — rules 1 and 2
---

# The practice

- `'use client'` → `*.client.tsx`. Exception: `index.tsx` inside a directory
  whose name ends in `.client` (e.g. `widget.client/index.tsx`).
- `'use server'` → `*.action.ts`.

Server actions additionally validate input via `next-safe-action` —
`inputSchema`, or `bindArgsSchemas` for bound args. An action that doesn't
validate is a bug.

# Why

Which side of the boundary a file sits on is the most consequential fact about it,
and by default it's invisible — one line at the top. Encoding it in the filename
makes it visible in the file tree, in every import statement, in review diffs, and
to glob-based tooling.

# Why this is project-layer

The transferable rule — *when a file's runtime context changes its semantics, put
that in the filename* — is sound but thin on its own. The value here is the
concrete extensions, and those are Next.js App Router conventions.

**Promotion candidate.** `wiley` is also Next.js (16.x). If it uses the same
convention, this becomes a genuine meta practice on corroboration. Re-evaluate
when wiley is harvested.
