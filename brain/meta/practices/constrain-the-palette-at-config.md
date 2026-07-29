---
type: Practice
title: Delete the design tokens you don't want used
description: Remove redundant token scales from the toolchain config so misuse doesn't compile, rather than banning them in review.
tags: [design-system, tokens, tailwind, enforcement]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: instance-of, target: /meta/practices/make-misuse-unrepresentable.md }
  - { kind: depends-on, target: /meta/practices/semantic-tokens-only.md }
sources:
  - id: tailwind-globals
    resource: projects/zamp/utils/tailwind/globals.css
    title: "utils/tailwind/globals.css — removes slate, gray, zinc, stone; keeps neutral"
    author: human:christopher
    last_modified: 2026-07-25
  - id: components-json
    resource: projects/zamp/utils/design-system/components.json
    title: 'components.json — baseColor: "neutral"'
---

# The practice

Tailwind ships five near-identical gray scales — `slate`, `gray`, `zinc`,
`stone`, `neutral`. Pick one and **delete the other four from the config.**

Keep the surviving choice consistent with the component generator's
configuration (zamp: `baseColor: "neutral"`), so generated code and hand-written
code agree.

# Why

`bg-slate-500` and `bg-gray-500` are visually indistinguishable and semantically
identical. Their only effect is to make two files that should match not match.

Deleting them means the wrong choice produces no CSS, which is a faster and more
reliable teacher than a review comment. It also shrinks the decision space for
anyone — human or agent — writing a class name.

# Generalizes

This is the canonical instance of
[make misuse unrepresentable](make-misuse-unrepresentable.md). The same reasoning
applies to any token family with redundant entries: font sizes, shadows, spacing
steps, breakpoints.

# Related

[Semantic tokens only](semantic-tokens-only.md) is the rule this enforces
structurally. Deleting scales handles the greys; the semantic-token rule covers
the hues that must remain available to the theme layer.
