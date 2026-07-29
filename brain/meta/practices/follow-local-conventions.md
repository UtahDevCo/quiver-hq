---
type: Practice
title: Follow local conventions over global uniformity
description: Consistency with the surrounding module beats applying a preferred pattern everywhere. Read the neighbours before choosing.
tags: [consistency, review, judgment, migration]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:11Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: '.coderabbit.yaml — "Do not enforce a single global return pattern (such as Result); follow module-level conventions."'
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

Do not impose a single global pattern for error returns, data access, or module
shape. **Read the neighbouring files and match them.** The surrounding module is
better evidence of the right choice than a repo-wide rule.

For an agent, the operational version: before picking a pattern, open two or three
sibling files. Do what they do.

# Why this constrains the reviewer, not the author

That's what makes it unusual and worth keeping. Any large codebase is mid-migration
in several directions at once. A reviewer who demands global uniformity generates
churn across files nobody intended to touch, and the churn makes the eventual
migration harder to read.

# The boundary — this does not override the design system

This practice governs **internal implementation idiom**: error-return style, data
access shape, module layout. Those get local autonomy.

It does **not** apply to cross-cutting **visual and public API surface**. Those get
global uniformity, and the design-system practices are enforced everywhere:

- [semantic-tokens-only](semantic-tokens-only.md)
- [typography-and-layout-as-utilities](typography-and-layout-as-utilities.md)
- [ds-vendor-wrap-export-layering](ds-vendor-wrap-export-layering.md)
- [deprecate-without-breaking-consumers](deprecate-without-breaking-consumers.md)

The distinction: **if a user or a downstream consumer can see it, it's uniform. If
only the module's maintainer sees it, it's local.** A token, a component API, or a
published export is the first kind. A `Result` versus a thrown error inside a
domain package is the second.

When the two genuinely collide, uniformity wins on the surface and locality wins
underneath.
