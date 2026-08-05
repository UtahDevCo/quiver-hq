# Meta brain — always-on index

Higher-order practices that apply to **every** project. This index is loaded into
every session; the concepts it links are not. **Read a concept in full before relying
on it**, and prefer it over your own defaults.

- **Practices are default-on.** Follow them unless a project override says otherwise.
  Deviating is a defect.
- **Patterns are opt-in.** Reach for them when the problem arises. Their absence is
  not a defect, and you should never retrofit one into working code unprompted.

A project may narrow, extend, replace, or suspend anything here via a
`Practice Override` in `brain/projects/<name>/overrides/`. Resolve overrides first —
`/brain-recall` does it for you, or read `<project>/.brain/index.md`.

Governance and the local extensions: [conventions](../conventions.md).

# Practices

## Enforcement and judgment

* [make-misuse-unrepresentable](practices/make-misuse-unrepresentable.md) - When you have a house choice among interchangeable options, delete the alternatives from the toolchain instead of documenting a preference.
* [follow-local-conventions](practices/follow-local-conventions.md) - Consistency with the surrounding module beats applying a preferred pattern everywhere. Read the neighbours before choosing.
* [prefer-curated-examples-over-call-sites](practices/prefer-curated-examples-over-call-sites.md) - Learn a shared component's API from its stories, not the nearest call site. Copying a call site can launder an inverted convention.

## Style

* [minimal-comments](practices/minimal-comments.md) - Prefer self-documenting code. A comment that restates the code is noise; only a genuinely non-obvious why earns a line.
* [kebab-case-files-named-exports](practices/kebab-case-files-named-exports.md) - Files are kebab-case, component identifiers are PascalCase, and nothing uses a default export. The no-default-export half is the load-bearing part.
* [small-single-purpose-files](practices/small-single-purpose-files.md) - Around 200 lines for logic and 300 for components, one primary export, and dead code removed in the change that orphaned it.
* [named-functions-over-iifes](practices/named-functions-over-iifes.md) - An IIFE inverts reading order; a named function costs the same and says what it computes.

## Error handling

* [error-propagation-and-capture](practices/error-propagation-and-capture.md) - Never rewrap an error you are merely passing along, and never report it twice. One failure, one report, at one place.
* [no-error-objects-across-boundaries](practices/no-error-objects-across-boundaries.md) - Error instances do not serialize. Pass the message string across any process, runtime, or storage boundary.
* [check-how-the-callee-reports-refusal](practices/check-how-the-callee-reports-refusal.md) - An action that returns `error.message` reports failure through a value the caller can drop; deleting the client guard then silences every failure mode, not just the one being fixed.
* [one-throwable-per-try-catch](practices/one-throwable-per-try-catch.md) - A catch per kind of side effect. A wide catch collapses distinct failures into one useless error group.
* [uniform-error-handling-shape-per-function](practices/uniform-error-handling-shape-per-function.md) - Extraction is a commitment: don't mix extracted Result helpers with an inline try/catch in one function.

## Testing

* [assert-on-whole-values](practices/assert-on-whole-values.md) - Compare the entire error or object rather than picking at one field, and skip intermediate variables in tests.
* [mock-at-narrowest-scope](practices/mock-at-narrowest-scope.md) - Spy on one export before replacing a module. A mock you don't assert against verifies almost nothing.
* [wait-for-the-work-to-start-then-to-finish](practices/wait-for-the-work-to-start-then-to-finish.md) - A fixed sleep after submit let slow requests read as already finished, so the next action aborted them in flight; two edges fixed 38 of 40 runs and named the other two.
* [dont-test-framework-guarantees](practices/dont-test-framework-guarantees.md) - Don't assert step order or that Promise.all parallelized. Test payload contracts and deliberate non-obvious choices.

## Security

* [authorize-before-doing-work](practices/authorize-before-doing-work.md) - The authorization check is the first statement in a privileged entry point — before validation-dependent reads, before queries, before side effects. Then log who did what.

## Money

* [money-in-integer-minor-units](practices/money-in-integer-minor-units.md) - Six monetary columns in a production schema were declared `real`, a type that cannot hold $1,782.59 exactly and drifts under addition.
* [derive-the-other-side-of-a-split-by-subtraction](practices/derive-the-other-side-of-a-split-by-subtraction.md) - Round one side of a percentage split and subtract for the rest, so `part + remainder === total` holds by construction across all 10,001 rates.

## Data you did not write

* [probe-a-field-before-depending-on-it](practices/probe-a-field-before-depending-on-it.md) - Count fill rate, uniqueness and the arithmetic a field's name claims, over every row you can reach. One declared field was populated in 0 of 679 rows; another named `total` held the agent's share in 100 of 100.
* [diff-operation-order-not-just-payloads](practices/diff-operation-order-not-just-payloads.md) - Both rails, the trigger names, the field lists and a worked example correct to the cent all matched; the counterparty spec still inverted confirm-then-fund into fund-then-notify.

## Measurement

* [report-a-rate-per-condition-never-pooled](practices/report-a-rate-per-condition-never-pooled.md) - Three input degradations averaged to 77.4%; separately they were 92.1%, 92.1% and 48.0%, and only the split identifies which one to look at.

## Model output

* [one-home-per-field-in-a-model-output-schema](practices/one-home-per-field-in-a-model-output-schema.md) - Two valid keys for the same value made the model pick per document; 53 codes across 9 of 175 documents landed in the key the normalizer did not read.

## Validation

* [colocate-schemas-with-what-they-validate](practices/colocate-schemas-with-what-they-validate.md) - A validator lives next to what it guards, not in a centralized schema file. The adjacency is the rule; the filename convention is per-project.

## React

* [use-client-is-a-javascript-boundary](practices/use-client-is-a-javascript-boundary.md) - The directive marks where JS ships, not where interactivity lives. A Server Component can render an interactive button.

## Database

* [prefer-metadata-only-schema-changes](practices/prefer-metadata-only-schema-changes.md) - Migration cost is a design input. Append enum values; inserting mid-list rewrites every row.

## Background jobs

* [poll-with-capped-backoff](practices/poll-with-capped-backoff.md) - Size the window to the provider's worst case. attempts × interval is an unstated timeout that misattributes the failure.
* [cap-external-file-size-before-ingest](practices/cap-external-file-size-before-ingest.md) - State the maximum and fail legibly; otherwise the ceiling arrives as an OOM that looks like infrastructure.

## Design system

* [constrain-the-palette-at-config](practices/constrain-the-palette-at-config.md) - Remove redundant token scales from the toolchain config so misuse doesn't compile, rather than banning them in review.
* [semantic-tokens-only](practices/semantic-tokens-only.md) - Use semantic and intent tokens. Hardcoded values and raw palette steps both break theming and dark mode.
* [typography-and-layout-as-utilities](practices/typography-and-layout-as-utilities.md) - Use font utilities and real HTML elements. Component primitives for text and layout add a layer that buys nothing and costs semantics.
* [flex-column-children-stretch-by-default](practices/flex-column-children-stretch-by-default.md) - w-full is a no-op on a flex-column child; opt out with self-start, never parent items-start.
* [read-primitive-defaults-before-overriding](practices/read-primitive-defaults-before-overriding.md) - A re-stated default is a pinned copy of a value you don't own, and it drifts silently.
* [ds-vendor-wrap-export-layering](practices/ds-vendor-wrap-export-layering.md) - When using a component generator — treat generated primitives as third-party, put your opinions in a thin wrapper layer, and curate the public surface.
* [ds-wrapper-passthrough](practices/ds-wrapper-passthrough.md) - Derive props from the primitive, add your own, merge classes, spread the rest. Never a bare re-export.

## API design

* [deprecate-without-breaking-consumers](practices/deprecate-without-breaking-consumers.md) - Keep the original export, mark it @deprecated with a prop-by-prop mapping, and point at the replacement's live examples.

## Review

* [conventional-comments](practices/conventional-comments.md) - Every review comment carries an explicit label and blocking-ness, so the reader never has to guess whether feedback is a blocker.
# Failure modes

Things that look right and are not, each paid for in production. There are 32, so
they live one level down rather than in this file. Open the group when you are
about to do that kind of work, and read the concept before writing the code.

* [Writes, migrations and stored data](failure-modes/index.md) - 5 concepts. Read before a backfill, a normalizer change, or any "the fix is deployed" claim.
* [Checks that pass without checking](failure-modes/index.md) - 6 concepts. Read before trusting an audit, a monitor, a paginated sweep, or a cached guard.
* [Probing someone else's system](failure-modes/index.md) - 6 concepts. Read before recording what a third-party API can or cannot do.
* [Measuring a model](failure-modes/index.md) - 11 concepts. Read before comparing two prompts, two models, or two configurations. This is the largest group and the most expensive to ignore.
* [Documents, config and tooling](failure-modes/index.md) - 4 concepts. Rendering, runtime secrets, git staging, mutation harnesses.

Full list with one-line descriptions: [failure-modes/index.md](failure-modes/index.md).

# Workflows

* [corroboration-requires-independent-sources](workflows/corroboration-requires-independent-sources.md) - Before counting two repos as agreement, diff their convention docs. Generated or copied files make one document look like two, and the check costs one grep.
* [pair-both-arms-in-one-window-or-drift-picks-the-winner](workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md) - Comparing a fresh capture against a stored baseline lets provider drift masquerade as a treatment effect, and a control group cannot detect it because the control sits in the same degraded window. Capturing both arms as adjacent calls reversed the sign of a real decision, twice.
* [rank-the-documents-before-building-from-them](workflows/rank-the-documents-before-building-from-them.md) - A 265-line knowledge base, the newest and clearest file in the folder, described a transaction the executed contract forbids. Write the authority ranking into the repo as step one.
# Patterns

* [token-architecture-three-layers](patterns/token-architecture-three-layers.md) - Scale, then intent quartets, then component semantics. The repeating role set is the load-bearing part.

Opt-in, so reach for one when the problem appears. Full list, including the two that
live in zamp's layer: [patterns/index.md](patterns/index.md).

# Stacks

*Default technology choices and the reasoning behind them. Empty.*

# Using the brain

* `/brain-recall <topic>` - resolve practices for the current project and answer.
* `/brain-push "<learning>"` - record something worth keeping into the inbox.
* `/brain-harvest <project>` - extract knowledge from a repo into the inbox.
* `/brain-promote` - review the inbox and place concepts (human gate).
* `/brain-audit` - run attesters, surface stale and unverified concepts.
