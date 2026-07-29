# Meta brain — always-on index

Higher-order practices that apply to **every** project. This index is loaded into
every session; the linked concepts are not. Read a concept in full before relying
on it, and prefer it over your own defaults.

- **Practices are default-on.** Follow them unless a project override says
  otherwise. Deviating is a defect.
- **Patterns are opt-in.** Reach for them when the problem arises. Their absence
  is not a defect, and you should never retrofit one into working code unprompted.

A project may narrow, extend, replace, or suspend anything here via a
`Practice Override` in `brain/projects/<name>/overrides/`. Resolve overrides
first — `/brain-recall` does it for you, or read `<project>/.brain/index.md`.

Governance and the local extensions: [conventions](../conventions.md).

# Practices — enforcement

* [make-misuse-unrepresentable](practices/make-misuse-unrepresentable.md) - When the team has settled on one of several interchangeable options, delete the alternatives from the toolchain rather than documenting a preference.

# Practices — design system

* [constrain-the-palette-at-config](practices/constrain-the-palette-at-config.md) - Delete redundant token scales (Tailwind's five greys → one) so misuse doesn't compile.
* [semantic-tokens-only](practices/semantic-tokens-only.md) - Reference semantic and intent tokens. Never raw palette steps or hardcoded values, CSS variables included. Inline `style` escape hatch requires a comment.
* [typography-and-layout-as-utilities](practices/typography-and-layout-as-utilities.md) - Font utilities named by purpose on semantic HTML. No `Text`/`Heading`/`Flex`/`Box` primitives. `gap` over margins.
* [ds-vendor-wrap-export-layering](practices/ds-vendor-wrap-export-layering.md) - Generated primitives are third-party and unedited; a thin wrapper layer holds your opinions; the barrel is curated.
* [ds-wrapper-passthrough](practices/ds-wrapper-passthrough.md) - Type wrappers off the primitive with `ComponentProps`, spread the rest, never a bare re-export. No manual ref forwarding in React 19.

# Practices — API design

* [deprecate-without-breaking-consumers](practices/deprecate-without-breaking-consumers.md) - Keep the old export working. `@deprecated` carries a prop-by-prop mapping that names its own gaps, and points at runnable examples.

# Patterns — design system

* [token-architecture-three-layers](patterns/token-architecture-three-layers.md) - Scale → intent quartets (`accent`/`background`/`border`/`foreground`) → component semantics. `oklch()`; radius derived from one base by `calc()`.
* [theme-by-data-attribute](patterns/theme-by-data-attribute.md) - Folder per theme, `[data-theme="name"]` scoping, dark mode nested. Write the completeness contract down; a second theme is the cheapest audit of your token layer.

# Patterns — API design

* [accessibility-enforced-by-types](patterns/accessibility-enforced-by-types.md) - A discriminated union over `label` | `placeholder` | `aria-label` makes an unlabeled input a compile error.

# Stacks

*Default technology choices and the reasoning behind them. Empty.*

# Failure modes

*Things that look right and are not. Empty.*

# Workflows

*Repeatable processes: review loops, triage, release. Empty.*

# Using the brain

* `/brain-recall <topic>` - resolve practices for the current project and answer.
* `/brain-push "<learning>"` - record something worth keeping into the inbox.
* `/brain-harvest <project>` - extract knowledge from a repo into the inbox.
* `/brain-promote` - review the inbox and place concepts (human gate).
* `/brain-audit` - run attesters, surface stale and unverified concepts.
