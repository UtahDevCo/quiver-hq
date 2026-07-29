---
type: Observation
title: Small files, one primary export
description: Under ~200 lines for .ts and ~300 for .tsx, one primary export per file, and no orphaned code left behind.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [file-organization, review]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — global path instructions
    last_modified: 2026-07-25
---

# Observation

- **Size:** <200 lines for `.ts`, <300 for `.tsx`. Exempt: tests, stories,
  configuration, documentation.
- **One primary export per file.**
- **Remove orphaned code in the same PR that orphaned it.**
- Avoid mutable state where practical.
- Keep `try`/`catch` focused — avoid several unrelated awaits in one block.

# Why it matters

The size limits are a proxy for single responsibility that is cheap to check and
hard to argue with. The exemption list matters as much as the limit: tests and
stories are legitimately long and flagging them trains people to ignore the rule.

# Attestation candidate

The size limit is mechanically checkable and is a good first `Invariant` — a
script over changed files, with the exemptions encoded.
