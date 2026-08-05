---
type: Observation
title: Don't use forwardRef in React 19 — ref is a first-class prop
description: React 19 passes ref as an ordinary prop to function components, so forwardRef adds a wrapper and a second type parameter for nothing in new code.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [react, react-19, components, typescript, design-system]
status: draft
not:
  - term: "const Foo = forwardRef<HTMLDivElement, FooProps>((props, ref) => ...)"
    why: "React 19 delivers ref as a normal prop; the wrapper adds indirection, an extra generic, and a displayName concern with no benefit"
    instead: "accept ref in the props type and use it directly: function Foo({ ref, ...rest }: FooProps) { ... }"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — 'No forwardRef in React 19'" }
---

# Observation

In React 19, `ref` is passed to function components as an ordinary prop. New
components should accept it in their props type rather than wrapping in
`forwardRef`.

# Why it matters

`forwardRef` in a React 19 codebase is a small, self-propagating tax. It costs an
extra generic parameter, an extra layer of indirection when reading the component,
and a `displayName` to set. More to the point, it reads as *required* to the next
author — someone writing a sibling component sees `forwardRef` on the neighbor and
matches it, so the obsolete form spreads through a component library long after
the version bump that retired it.

This is worth recording as an explicit practice rather than assumed, because
almost every React example and pre-19 library on the internet still uses
`forwardRef`, so an agent or a developer working from familiar patterns will
reproduce it by default.

# Evidence

Recorded in `patterns.md` under React Patterns. Applies to new components; the
brain does not authorize retrofitting existing `forwardRef` components (see
"The brain describes; it does not retrofit" in `conventions.md`).

Proposed `meta`: this is a fact about the React version, not about this repo. It
becomes correct-by-default in any repo on React 19 and should be reconsidered only
if a project pins an older React.
