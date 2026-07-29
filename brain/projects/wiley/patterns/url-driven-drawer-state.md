---
type: Pattern
title: Drawer open/close state lives in the URL, via an injected-dependency hook
description: useDrawerState keeps drawer visibility and mode in search params so back/forward and reload work — and takes pathname, searchParams, and replace as arguments, so it has zero framework imports.
tags: [ui, drawer, url-state, hooks, testability]
generated: { by: claude/opus-5, at: 2026-07-29T22:55:47Z }
verified:
  - { by: human:christopher, at: 2026-07-29T22:55:47Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "calling usePathname() / useSearchParams() / useRouter() inside the hook"
    why: "binds a piece of pure URL logic to one framework and one router, and makes it untestable without mounting a Next.js app"
    instead: "take pathname, searchParams, and handleReplace as parameters; the caller wires the router"
  - term: "writing the default mode into the URL"
    why: "every drawer opened at its default leaves ?drawerMode=overlay behind, so shared links carry noise and no-op history entries accumulate"
    instead: "delete the param when the value equals the default"
sources:
  - id: hook
    resource: projects/wiley/web/hooks/use-drawer-state.ts
    title: "wiley — useDrawerState (102 lines)"
    author: human:christopher
    last_modified: 2026-07-29
---

# The pattern

```ts
const { isOpen, mode, setOpen, setMode, toggleOpen, toggleMode } = useDrawerState({
  id: "contact",              // namespaces params: drawer-contact, drawerMode-contact
  defaultMode: "overlay",
  pathname,                   // injected
  searchParams,               // injected (URLSearchParams)
  handleReplace,              // injected (url: string) => void
});
```

Drawer visibility becomes `?drawer-contact=open`. Browser back closes the drawer,
reload reopens it, and the URL is shareable.

# Why the injected dependencies are the interesting part

The hook imports **nothing** but `useCallback` and `useMemo`. No `next/navigation`,
no router. The caller passes `pathname`, `searchParams`, and a `handleReplace`
function.

Consequences:

- Unit-testable by passing a `URLSearchParams` and a spy — no app mount, no router
  mock. Compare this to the usual version, which needs the whole framework standing
  up to assert that a param got set.
- Portable to any router, or to none.
- The caller decides `replace` vs `push`, which is the right place for that decision:
  a drawer toggle should not usually create a history entry, but sometimes it should.

This is dependency injection in a React hook, and it is the single most copyable idea
in wiley's UI layer.

# Three details that are easy to get wrong

**Closing cleans up the mode param too.** `setOpen(false)` deletes both
`drawer-<id>` and `drawerMode-<id>`, so a closed drawer leaves nothing behind.

**The default is never written.** `setMode(defaultMode)` *deletes* the param rather
than setting it, keeping URLs minimal.

**Redundant updates are dropped.** `updateParams` compares the serialized string
against a snapshot and returns early if unchanged — no wasted `replace()`, no
duplicate history entries, no render loop.

# Namespacing

`id` produces `drawer-<id>` / `drawerMode-<id>`, so several independent drawers can
be open on one page with separate state. Without `id` it falls back to bare
`drawer` / `drawerMode`.

Note the asymmetry with the [Drawer component](drawer.md), which accepts an `id` prop
and explicitly ignores it. The `id` that matters is this one.
