# wiley

Project knowledge for `projects/wiley`. Reachable from inside the repo as
`.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Patterns

Opt-in and portable. Reach for these when the problem arises; their absence
elsewhere is not a defect.

* [drawer](patterns/drawer.md) - Overlay/push panel, controlled or uncontrolled, with focus save/restore, a tab trap, reference-counted scroll lock, and a stacking viewport.
* [url-driven-drawer-state](patterns/url-driven-drawer-state.md) - `useDrawerState` keeps visibility and mode in search params, and takes `pathname`/`searchParams`/`replace` as arguments — so it has zero framework imports and is unit-testable.
* [form-drawer](patterns/form-drawer.md) - Generic react-hook-form container: create/edit modes, skeleton, dismissible API error, dirty check, Cmd/Ctrl+Enter, and an rAF-timed reset instead of a guessed `setTimeout`.

# Modules

*What the major pieces are and how they fit. Empty.*

# Invariants

*Rules with an executable check attached. Empty.*

# Decisions

*Why things are the way they are. Empty.*

# Gems

*Project-local patterns worth promoting to meta. Empty.*

# Examined and deliberately not recorded

Honest coverage notes from the 2026-07-29 harvest, so a later reader doesn't assume
these were missed:

* `components/sidebar.tsx` — **not portable.** Hardwired nav items, PostHog calls, and
  a `useUser()` dependency. Reuse would mean extracting `navItems` as a prop and
  replacing the hooks, at which point little is left. Good component, local to wiley.
* `components/header.tsx` — portable but trivial: one `toggleSidebar` prop and a
  responsive icon/text swap. Nothing worth writing down.
* `components/data-table/data-table.tsx` — the presentational layer over TanStack
  Table. Portable only if you adopt TanStack *and* manage query, pagination, sorting,
  and filter state in the parent. Reconsider if a second repo adopts the same split.
* **wiley has no test files**, so it cannot corroborate the meta testing practices —
  absence of evidence, not disagreement.
