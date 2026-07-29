---
type: Practice
title: Typography and layout are utilities on semantic HTML
description: Use font utilities and real HTML elements. Component primitives for text and layout add a layer that buys nothing and costs semantics.
tags: [design-system, html, accessibility, css]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "<Flex>, <Box>, <Grid>, <Container>, <Section> layout primitives"
    why: "reimplements CSS in props, renders a bare div, and loses semantic meaning"
    instead: "a semantic element (<section>, <header>, <ul>, <nav>) with layout utility classes"
  - term: "<Text>, <Heading>, <Code>, <Em>, <Strong> typography primitives"
    why: "a component wrapper around a font size, with worse semantics than the HTML tag"
    instead: "the correct HTML element plus a font utility"
  - term: "margins for spacing between siblings"
    why: "margins collapse, don't compose, and attach spacing to the wrong element"
    instead: "gap or space utilities on the parent, or the design-system container's own spacing"
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — typography, layout, and spacing rules
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

**Typography** — font utilities named by *purpose*, with size as a suffix only
where the purpose has variants. zamp's set is a good template:
`font-page-title`, `font-headline-{1,2,3}`, `font-text-{lg,sm,xs}`,
`font-label`, `font-badge`, `font-caption`, `font-numeric`, `font-link`.

**Layout** — semantic HTML plus utilities for flex, sizing, responsiveness.

**Spacing and borders** — prefer what design-system containers already provide;
then `gap`/`space`; margins last.

**Custom components** are fine, but only when the design system doesn't already
cover the need in some capacity.

# Why purpose-named, not size-named

`font-label` survives a decision to make labels smaller. `font-xs` does not.
Naming by purpose keeps the design decision in the token layer where it can be
changed once, instead of distributed across every call site.

# Why utilities beat layout primitives

`<Flex>` renders a `<div>`. Choosing utilities forces you to pick a real
element every time, which is where the accessibility payoff comes from — you end
up with `<nav>`, `<section>`, and `<ul>` instead of a tree of anonymous divs.

Note this cuts against the general instinct to prefer components over classes.
The exception holds because layout and typography have *native semantic
elements*; wrapping them in components discards information that assistive
technology depends on.
