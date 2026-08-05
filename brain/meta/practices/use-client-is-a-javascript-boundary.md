---
type: Practice
title: "\"use client\" marks a JavaScript boundary, not interactivity"
description: A Server Component can render fully interactive HTML. Treating the directive as an interactivity marker pushes the boundary upward and ships JavaScript for markup that needed none.
tags: [react, rsc, nextjs, server-components, bundle-size]
generated: { by: claude/opus-5, at: 2026-08-05T19:33:19Z }
verified:
  - { by: human:christopher, at: 2026-08-05T21:09:32Z }
status: stable
stale_after: 2027-08-05
not:
  - term: "adding \"use client\" so a button or form is 'interactive'"
    why: "HTML is already interactive — buttons focus and click, forms submit, anchors navigate — with no client JavaScript; the directive only ships a bundle"
    instead: "render it from the server; add the boundary when you need state, hooks, a function handler, or a browser API"
  - term: "onClick={() => {}} as a placeholder on a component with no behavior yet"
    why: "the no-op handler is the thing forcing the client boundary, so the subtree ships JavaScript to do nothing"
    instead: "drop the handler and render inert HTML from the server until a real behavior exists"
sources:
  - id: patterns
    resource: local/zamp/patterns.md
    title: "zamp patterns.md — '\"use client\" is a JS-boundary marker, not an interactivity marker'"
    author: human:christopher
    last_modified: 2026-08-05
---

# The practice

`"use client"` marks where JavaScript starts shipping to the browser. It does not mark
"this part of the page is interactive."

A Server Component can render `<button type="button">`. The element is focusable,
clickable, and keyboard-accessible; what's missing is only a JS handler firing. Add the
boundary when you actually need React state, hooks, an event handler bound to a
function, or a browser-only API.

A no-op `onClick={() => {}}` is a smell: it is what forces the boundary, and it buys
nothing.

# Why the mental model decides where the boundary lands

If "interactive" means "client," then any subtree containing a button gets marked — and
because the directive is contagious downward, marking a layout or a page converts
everything beneath it. The bundle grows to serve markup that needed no JavaScript.

Framed correctly, the question at each component stops being "is this interactive?" and
becomes "does this need JavaScript?" — which has a far smaller answer set.

The placeholder-handler case deserves separate attention because it arrives during
scaffolding: a component is stubbed with an empty handler "for later," silently
committing the subtree to the client. Later rarely removes it.

# Scope

Specific to React Server Components. Any related filename convention — e.g. requiring
a `.client.tsx` suffix on files carrying the directive — is a project-level choice and
belongs in that project's layer.
