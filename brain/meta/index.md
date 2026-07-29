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

# Practices — enforcement and judgment

* [make-misuse-unrepresentable](practices/make-misuse-unrepresentable.md) - When the team has settled on one of several interchangeable options, delete the alternatives from the toolchain rather than documenting a preference.
* [follow-local-conventions](practices/follow-local-conventions.md) - Match the surrounding module for internal idiom — read two or three siblings before choosing a pattern. Global uniformity applies only to visible surface (tokens, component APIs, published exports).

# Practices — style

* [minimal-comments](practices/minimal-comments.md) - Comment a genuinely non-obvious *why*, one terse line. Never restate the code. **Don't touch pre-existing comments authored by others.**
* [kebab-case-files-named-exports](practices/kebab-case-files-named-exports.md) - `kebab-case.tsx` files, `PascalCase` identifiers, `UPPER_SNAKE` constants. **No default exports** — that half is load-bearing. Next.js `page`/`layout`/`route` are the framework exception.
* [small-single-purpose-files](practices/small-single-purpose-files.md) - ~200 lines logic / ~300 components (tests, stories, config exempt). One primary export. Delete orphaned code in the change that orphaned it.

# Practices — error handling

* [error-propagation-and-capture](practices/error-propagation-and-capture.md) - Return a propagating error untouched; attach context only when you originate it; capture once, where you stop it. Never capture-then-rethrow.
* [no-error-objects-across-boundaries](practices/no-error-objects-across-boundaries.md) - Error instances don't serialize. Pass `error.message` across server/client, workers, job payloads, and caches.

# Practices — testing

* [assert-on-whole-values](practices/assert-on-whole-values.md) - `toStrictEqual(new Error(...))`, not `.message`. Unwrap inline at the assertion site. No single-use intermediates.
* [mock-at-narrowest-scope](practices/mock-at-narrowest-scope.md) - Escalate by blast radius: `spyOn` → deep-mock → module mock. Always assert `toHaveBeenCalledWith` *and* `toHaveBeenCalledTimes`.

# Practices — security

* [authorize-before-doing-work](practices/authorize-before-doing-work.md) - The authorization check is the first statement in a privileged entry point — before any read, write, or external call. Then log actor, action, target, note.

# Practices — validation

* [colocate-schemas-with-what-they-validate](practices/colocate-schemas-with-what-they-validate.md) - `*.schema.ts` beside the function it guards, never a centralized schema file.

# Practices — design system

* [constrain-the-palette-at-config](practices/constrain-the-palette-at-config.md) - Delete redundant token scales (Tailwind's five greys → one) so misuse doesn't compile.
* [semantic-tokens-only](practices/semantic-tokens-only.md) - Reference semantic and intent tokens. Never raw palette steps or hardcoded values, CSS variables included. Inline `style` escape hatch requires a comment.
* [typography-and-layout-as-utilities](practices/typography-and-layout-as-utilities.md) - Font utilities named by purpose on semantic HTML; `gap` over margins. Banning `Text`/`Heading`/`Flex`/`Box` outright is a zamp-only extension — a typography component elsewhere is fine.
* [ds-vendor-wrap-export-layering](practices/ds-vendor-wrap-export-layering.md) - Generated primitives are third-party and unedited; a thin wrapper layer holds your opinions; the barrel is curated.
* [ds-wrapper-passthrough](practices/ds-wrapper-passthrough.md) - Type wrappers off the primitive with `ComponentProps`, spread the rest, never a bare re-export. No manual ref forwarding in React 19.

# Practices — API design

* [deprecate-without-breaking-consumers](practices/deprecate-without-breaking-consumers.md) - Keep the old export working. `@deprecated` carries a prop-by-prop mapping that names its own gaps, and points at runnable examples.

# Practices — review

* [conventional-comments](practices/conventional-comments.md) - `<label> [decorations]: <subject>`. `issue` blocks, `suggestion` doesn't, `praise` at least once per review. **Applies to your own review output.**

# Patterns — design system

* [token-architecture-three-layers](patterns/token-architecture-three-layers.md) - Scale → intent quartets (`accent`/`background`/`border`/`foreground`) → component semantics. `oklch()`; radius derived from one base by `calc()`.

# Stacks

*Default technology choices and the reasoning behind them. Empty.*

# Failure modes

*Things that look right and are not. Each was paid for in production.*

* [verify-a-write-actually-happened](failure-modes/verify-a-write-actually-happened.md) - A `catch` mapping an error class to success reports writes that never landed. Read the state back; assert on the field you wrote, not a derived one.
* [audits-must-report-their-own-coverage](failure-modes/audits-must-report-their-own-coverage.md) - `.catch(() => null); continue` turns "couldn't check" into "checked, fine". Print attempted / inspected / skipped-by-reason and call the count a floor.
* [probe-before-trusting-an-api-claim](failure-modes/probe-before-trusting-an-api-claim.md) - "The API doesn't support X" in a comment is a hypothesis. Probe before extending the workaround; commit the probe, including ones that falsified your own guess.
* [self-reported-confidence-is-not-a-signal](failure-modes/self-reported-confidence-is-not-a-signal.md) - LLM confidence tracks prose register, not correctness. Never display it or route on it; surface citations, gaps, and model disagreement instead.
* [a-listing-endpoint-is-not-the-uniqueness-domain](failure-modes/a-listing-endpoint-is-not-the-uniqueness-domain.md) - `if (!found) create()` assumes the listing covers everything the create checks. When it doesn't, the write is rejected forever and never learns the id it needed.
* [a-dead-control-may-be-a-duplicate](failure-modes/a-dead-control-may-be-a-duplicate.md) - A setting whose value never reaches the backend may be a redundant second writer, not missing plumbing. Removal is a no-op; connecting it changes behaviour for everyone whose two values disagree.
* [request-parameters-may-not-reach-the-wire](failure-modes/request-parameters-may-not-reach-the-wire.md) - Vendor SDKs discard unsupported settings, return 200, and report it only in `result.warnings`. An absent error is not evidence the request was honoured.
* [automatic-behavior-is-unmeasured-until-recorded](failure-modes/automatic-behavior-is-unmeasured-until-recorded.md) - Prompt caching and similar automatic optimizations leave nothing to grep. Record the vendor's counter or the saving is only assumed.

# Workflows

* [corroboration-requires-independent-sources](workflows/corroboration-requires-independent-sources.md) - Two sources corroborate only if independent. Diff convention docs before counting them twice; weight independent code above documentation; report *unfalsifiable here* separately from *contradicted here*.

# Using the brain

* `/brain-recall <topic>` - resolve practices for the current project and answer.
* `/brain-push "<learning>"` - record something worth keeping into the inbox.
* `/brain-harvest <project>` - extract knowledge from a repo into the inbox.
* `/brain-promote` - review the inbox and place concepts (human gate).
* `/brain-audit` - run attesters, surface stale and unverified concepts.
