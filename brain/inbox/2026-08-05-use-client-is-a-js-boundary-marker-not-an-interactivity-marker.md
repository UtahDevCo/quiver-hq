---
type: Observation
title: "\"use client\" marks a JavaScript boundary, not interactivity"
description: A Server Component can render fully interactive HTML; the directive is only needed for state, hooks, function-valued event handlers, or browser APIs.
kind: practice
proposed_layer: meta
observed_in: zamp
tags: [react, rsc, nextjs, server-components, bundle-size]
status: draft
not:
  - term: "adding \"use client\" so that a button or a form is 'interactive'"
    why: "HTML is already interactive — buttons focus and click, forms submit, anchors navigate — without any client JS; the directive only ships JavaScript"
    instead: "render the element from the server, and add the boundary only when you need state, hooks, a function handler, or a browser API"
  - term: "onClick={() => {}} as a placeholder on a component that has no behavior yet"
    why: "a no-op handler is what forces the client boundary, so the component ships JS to do nothing"
    instead: "drop the handler and render inert HTML from the server until a real behavior exists"
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
sources:
  - { id: patterns, resource: local/zamp/patterns.md, title: "Coding Patterns — '\"use client\" is a JS-boundary marker, not an interactivity marker'" }
---

# Observation

`"use client"` marks where JavaScript starts shipping to the browser — it does not
mark "this part of the page is interactive."

A Server Component can render `<button type="button">`. The DOM element is
focusable, clickable, and keyboard-accessible; what's missing is only a JS handler
firing. Add the client boundary when you actually need React state, hooks, an event
handler bound to a function, or a browser-only API.

A no-op `onClick={() => {}}` is a smell: it is the thing forcing the boundary, and
it buys nothing. Drop the wrapper and render the inert HTML from the server until a
real handler exists.

# Why it matters

The mental model determines where the boundary lands, and the wrong model pushes it
upward. If "interactive" means "client," then any subtree containing a button gets
marked — and because the directive is contagious downward, marking a layout or a
page converts everything beneath it. The bundle grows for markup that needed no
JavaScript at all.

The no-op handler case is worth calling out separately because it usually arrives
during scaffolding: a component is stubbed with an empty handler "for later," which
silently commits the whole subtree to the client. Later never removes it.

Framed correctly, the question at each component stops being "is this interactive?"
and becomes "does this need JavaScript?" — which has a much smaller answer set.

# Evidence

Recorded in `patterns.md` under React Patterns, alongside the repo's related
filename convention (a `'use client'` file takes a `.client.tsx` suffix, and a file
that doesn't need the directive should drop it rather than keep a mismatched name).

Proposed `meta`: this is about the React Server Components model generally. The
`.client.tsx` naming half is project-specific and already covered in
`projects/zamp/practices/directive-driven-filenames.md`.
