---
type: Observation
title: File extension declares the runtime boundary
description: A 'use client' file is named *.client.tsx; a 'use server' file is named *.action.ts. The boundary is visible in the file tree.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [naming, rsc, nextjs]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — path instructions
    last_modified: 2026-07-25
  - id: rsc-reviewer
    resource: projects/zamp/.claude/agents/rsc-boundary-reviewer.md
    title: rsc-boundary-reviewer — rules 1 and 2
---

# Observation

- `'use client'` → `*.client.tsx`. Exception: `index.tsx` inside a directory
  whose name ends in `.client` (e.g. `widget.client/index.tsx`).
- `'use server'` → `*.action.ts`.

# Why it matters

Which side of the boundary a file lives on is the single most consequential fact
about it, and by default it is invisible — buried in a one-line directive at the
top. Encoding it in the filename makes it visible in the tree, in imports, in
review diffs, and in glob-based tooling.

# Layer note

The specific extensions are Next.js-flavored. The transferable rule is: **when a
file's runtime context changes its semantics, put that in the filename.**
