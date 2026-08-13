# wiley

Project knowledge for `projects/wiley`. Reachable from inside the repo as
`.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Patterns

* [drawer](patterns/drawer.md) - A custom drawer supporting both overlay and push modes, controlled or uncontrolled, with focus save/restore, a tab trap, reference-counted scroll lock, and stack-aware Escape.
* [form-drawer](patterns/form-drawer.md) - Wraps Drawer with create/edit modes, loading skeleton, dismissible API error, dirty-check on close, Cmd/Ctrl+Enter submit, and an rAF-timed reset that waits out the close animation.
* [url-driven-drawer-state](patterns/url-driven-drawer-state.md) - useDrawerState keeps drawer visibility and mode in search params so back/forward and reload work — and takes pathname, searchParams, and replace as arguments, so it has zero framework imports.

# Workflows

*How to run a piece of work here. Empty.*

# Failure modes

*Things that look right here and are not. Empty.*

# Practices

*Project-local rules. Empty.*

# Modules

*What the major pieces are and how they fit. Empty.*

# Invariants

*Rules with an executable check attached. Empty.*

# Decisions

* [wiley-ships-on-main-not-by-pull-request](decisions/wiley-ships-on-main-not-by-pull-request.md) - Chris's stated workflow, 2026-07-30. The App Hosting backend wiley-web is GitHub-linked, so a push to main is itself the deploy; four branch-and-PR cycles in one session cost time before this was said.

# Gems

*Project-local patterns worth promoting to meta. Empty.*
