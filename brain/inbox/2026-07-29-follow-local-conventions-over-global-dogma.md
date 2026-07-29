---
type: Observation
title: Follow module-level conventions rather than imposing one global pattern
description: Consistency with surrounding code beats applying a preferred pattern uniformly across a codebase.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [consistency, review, judgment]
generated: { by: claude/opus-5, at: 2026-07-29T14:03:13Z }
status: draft
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: ".coderabbit.yaml — \"Do not enforce a single global return pattern (such as Result); follow module-level conventions.\""
    last_modified: 2026-07-25
---

# Observation

Do not enforce a single global return pattern. Follow the conventions of the
module you are editing.

# Why it matters

This is unusual and worth keeping precisely because it constrains the *reviewer*
rather than the author. A large codebase is always mid-migration in several
directions at once; a reviewer who demands global uniformity generates churn that
makes things worse.

The practical version for an agent: **read the neighbors before choosing a
pattern.** The surrounding file is better evidence of the right choice than a
repo-wide rule.

# Tension worth noting at promotion

This sits in real tension with the design-system rules, which *are* enforced
globally. The distinction seems to be: cross-cutting *visual and API surface*
gets uniformity; *internal implementation idiom* gets local autonomy. Worth
stating explicitly if promoted.
