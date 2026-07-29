---
type: Pattern
title: Drawer — overlay/push panel with focus management and a stacking viewport
description: A custom drawer supporting both overlay and push modes, controlled or uncontrolled, with focus save/restore, a tab trap, reference-counted scroll lock, and stack-aware Escape.
tags: [ui, drawer, accessibility, framer-motion, portal]
generated: { by: claude/opus-5, at: 2026-07-29T22:55:47Z }
verified:
  - { by: human:christopher, at: 2026-07-29T22:55:47Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /projects/wiley/patterns/url-driven-drawer-state.md }
sources:
  - id: drawer
    resource: projects/wiley/web/components/shared/drawer.tsx
    title: "wiley — Drawer, DrawerViewport, closeHighestDrawer (378 lines)"
    author: human:christopher
    last_modified: 2026-07-29
  - id: freeze-scroll
    resource: projects/wiley/web/hooks/use-freeze-scroll.ts
    title: "useFreezeScroll — reference-counted scroll lock keyed by useId"
---

# The API

```ts
type DrawerProps = {
  title: string;                                 // required — used as aria-label
  children: React.ReactNode;
  actions?: React.ReactNode;                     // rendered in a <footer>
  trigger?: React.ReactNode;                     // optional; wrapped in a click target
  open?: boolean;         onOpenChange?: (open: boolean) => void;
  defaultOpen?: boolean;  onOpen?: () => void;  onClose?: () => void;
  mode?: DrawerMode;      onModeChange?: (mode: DrawerMode) => void;
  defaultMode?: DrawerMode;                      // "overlay" | "push"
  position?: "left" | "right";                   // default "right"
  scrim?: boolean;  showModeToggle?: boolean;  trapFocus?: boolean;
  className?: string;  drawerClassName?: string;  triggerClassName?: string;
};
```

Deps: `framer-motion`, `clsx`, `lucide-react`, and four local hooks
(`useDebouncedValue`, `useFreezeScroll`, `useKeydown`, plus `Portal`). No Radix, no
vaul.

# The four things worth copying

**Controlled or uncontrolled, done correctly.** `isOpen = open ?? isInternalOpen`
and `currentMode = mode ?? internalMode`. Internal state updates only when the prop
is `undefined`, and the callbacks fire either way — so a controlled parent never
fights the component, and an uncontrolled one still gets events.

**Exit animation without an unmount flash.**

```ts
const debouncedOpen = useDebouncedValue(isOpen, { millis: 175 });
const isRendered = isOpen || debouncedOpen;
```

The node stays mounted 175ms past close so framer-motion can animate out. This is
the problem everyone hits when they conditionally render an animated panel, and the
usual fix is an `AnimatePresence` wrapper or a hand-rolled `setTimeout`.

**Push mode is measured, then handed to CSS.** On open in push mode it reads
`getBoundingClientRect().width`, sets `--drawer-push-offset` on `document.body`, and
adds a `drawer-push-left`/`-right` class. Page content shifts via CSS; JS never
lays anything out.

**Reference-counted scroll lock.** `useFreezeScroll` keeps a `Map` keyed by `useId()`
and freezes while *any* instance wants it — so closing one of two nested drawers
doesn't restore scrolling underneath the other. The naive boolean version of this is
a common bug.

# Accessibility

- Focus save/restore: captures `document.activeElement` on open, focuses the first
  focusable inside on open, restores on close.
- Tab trap wrapping both directions, re-querying focusable elements on every
  keypress so dynamically added content is included.
- `aria-modal={currentMode === "overlay"}` — correctly *conditional*, because a push
  drawer is not modal. Easy to get wrong.
- Semantic shell: `<section>` → `<motion.aside role="dialog">` → `<header>`/`<footer>`,
  `<h2>` title, `aria-hidden` on the scrim, labelled icon buttons.

# Known rough edges

Recorded because they are what you would hit on reuse, not to be uncharitable.

- **`closeHighestDrawer()` works by simulating a DOM click.** It queries the viewport
  for `.drawer-close-button` and clicks the last one. Control flow routed through the
  DOM, coupled to a CSS class name and to document order matching stack order.
- **Escape fires once per open drawer.** Every open instance has an active `useKeydown`
  handler and each calls `closeHighestDrawer()`, so with N drawers open one Escape
  press produces N clicks on the topmost close button. Harmless today, latent.
- **Two competing stack accountants in one component family.** `useFreezeScroll` uses
  a `Map` keyed by `useId`; the drawer itself uses module-level mutable integers
  (`activeDrawerCount`, `overlayModeCount`). The `Map` version is the right one.
- **`id` is accepted and explicitly ignored** — `id: _id, // Not currently used
  internally`. Confusing, because
  [useDrawerState](url-driven-drawer-state.md) *does* use `id` to namespace its
  params.
- **The trigger wrapper is a `<div onClick>`** with no `role`, `tabIndex`, or key
  handler. Fine if you pass a `<button>`, inaccessible if you pass a `<span>` — in a
  component that is otherwise careful about a11y.

# Unresolved: two drawer implementations

wiley has **both**:

| Path | Basis | Consumers |
|---|---|---|
| `components/shared/drawer.tsx` | custom, framer-motion | 4 |
| `components/ui/drawer.tsx` | shadcn wrapper over `vaul` | 1 (`app/admin/billing/user/[id]/page.tsx`) |

Two interchangeable options coexisting is exactly what
[make-misuse-unrepresentable](../../../meta/practices/make-misuse-unrepresentable.md)
says to resolve by deletion. The custom one has the features and the users; the vaul
one has a single consumer. Not acted on — the brain describes and does not retrofit
— but this is the cheap cleanup when someone next touches that billing page.
