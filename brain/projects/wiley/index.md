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

* [a-sentinel-ordinal-may-mean-last-not-special](failure-modes/a-sentinel-ordinal-may-mean-last-not-special.md) - 99 looked like a pin on the catch-all rule until an unrelated rule inherited it by becoming last.
* [an-uncommitted-ui-change-reads-as-a-missing-capability](failure-modes/an-uncommitted-ui-change-reads-as-a-missing-capability.md) - A staged-but-unsaved portal reorder produced the same null diff as "the portal cannot reorder".
* [netsapiens-soft-delete-reserves-timeframe-name](failure-modes/netsapiens-soft-delete-reserves-timeframe-name.md) - A deleted answering rule / timeframe persists flagged "Deleted" and keeps its name reserved, so createTimeframe collides forever and only a vendor backend purge clears it.
* [client-import-from-server-tainted-module-breaks-bundler-not-tsc](failure-modes/client-import-from-server-tainted-module-breaks-bundler-not-tsc.md) - Pulling a pure helper into a "use client" file from a module that also imports firebase-admin drags the server SDK into the browser bundle; tsc passes, the page fails to load.
* [reconstruct-the-ledger-before-a-backcharge](failure-modes/reconstruct-the-ledger-before-a-backcharge.md) - Counting every skipped cycle as owed billed comped customers and dead cards; correct owed was a quarter of the naive figure.

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
