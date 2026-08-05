# Practices

Default-on. Follow unless a project override says otherwise.

# Enforcement and judgment

* [make-misuse-unrepresentable](make-misuse-unrepresentable.md) - When you have a house choice among interchangeable options, delete the alternatives from the toolchain instead of documenting a preference.
* [follow-local-conventions](follow-local-conventions.md) - Consistency with the surrounding module beats applying a preferred pattern everywhere. Read the neighbours before choosing.
* [prefer-curated-examples-over-call-sites](prefer-curated-examples-over-call-sites.md) - Learn a shared component's API from its stories, not the nearest call site. Copying a call site can launder an inverted convention.

# Style

* [minimal-comments](minimal-comments.md) - Prefer self-documenting code. A comment that restates the code is noise; only a genuinely non-obvious why earns a line.
* [kebab-case-files-named-exports](kebab-case-files-named-exports.md) - Files are kebab-case, component identifiers are PascalCase, and nothing uses a default export. The no-default-export half is the load-bearing part.
* [small-single-purpose-files](small-single-purpose-files.md) - Around 200 lines for logic and 300 for components, one primary export, and dead code removed in the change that orphaned it.
* [named-functions-over-iifes](named-functions-over-iifes.md) - An IIFE inverts reading order; a named function costs the same and says what it computes.

# Error handling

* [error-propagation-and-capture](error-propagation-and-capture.md) - Never rewrap an error you are merely passing along, and never report it twice. One failure, one report, at one place.
* [no-error-objects-across-boundaries](no-error-objects-across-boundaries.md) - Error instances do not serialize. Pass the message string across any process, runtime, or storage boundary.
* [check-how-the-callee-reports-refusal](check-how-the-callee-reports-refusal.md) - An action that returns `error.message` reports failure through a value the caller can drop; deleting the client guard then silences every failure mode, not just the one being fixed.
* [one-throwable-per-try-catch](one-throwable-per-try-catch.md) - A catch per kind of side effect. A wide catch collapses distinct failures into one useless error group.
* [uniform-error-handling-shape-per-function](uniform-error-handling-shape-per-function.md) - Extraction is a commitment: don't mix extracted Result helpers with an inline try/catch in one function.

# Testing

* [assert-on-whole-values](assert-on-whole-values.md) - Compare the entire error or object rather than picking at one field, and skip intermediate variables in tests.
* [mock-at-narrowest-scope](mock-at-narrowest-scope.md) - Spy on one export before replacing a module. A mock you don't assert against verifies almost nothing.
* [wait-for-the-work-to-start-then-to-finish](wait-for-the-work-to-start-then-to-finish.md) - A fixed sleep after submit let slow requests read as already finished, so the next action aborted them in flight; two edges fixed 38 of 40 runs and named the other two.
* [dont-test-framework-guarantees](dont-test-framework-guarantees.md) - Don't assert step order or that Promise.all parallelized. Test payload contracts and deliberate non-obvious choices.

# Security

* [authorize-before-doing-work](authorize-before-doing-work.md) - The authorization check is the first statement in a privileged entry point — before validation-dependent reads, before queries, before side effects. Then log who did what.

# Money

* [money-in-integer-minor-units](money-in-integer-minor-units.md) - Six monetary columns in a production schema were declared `real`, a type that cannot hold $1,782.59 exactly and drifts under addition.
* [derive-the-other-side-of-a-split-by-subtraction](derive-the-other-side-of-a-split-by-subtraction.md) - Round one side of a percentage split and subtract for the rest, so `part + remainder === total` holds by construction across all 10,001 rates.

# Data you did not write

* [probe-a-field-before-depending-on-it](probe-a-field-before-depending-on-it.md) - Count fill rate, uniqueness and the arithmetic a field's name claims, over every row you can reach. One declared field was populated in 0 of 679 rows; another named `total` held the agent's share in 100 of 100.
* [diff-operation-order-not-just-payloads](diff-operation-order-not-just-payloads.md) - Both rails, the trigger names, the field lists and a worked example correct to the cent all matched; the counterparty spec still inverted confirm-then-fund into fund-then-notify.

# Measurement

* [report-a-rate-per-condition-never-pooled](report-a-rate-per-condition-never-pooled.md) - Three input degradations averaged to 77.4%; separately they were 92.1%, 92.1% and 48.0%, and only the split identifies which one to look at.

# Model output

* [one-home-per-field-in-a-model-output-schema](one-home-per-field-in-a-model-output-schema.md) - Two valid keys for the same value made the model pick per document; 53 codes across 9 of 175 documents landed in the key the normalizer did not read.

# Validation

* [colocate-schemas-with-what-they-validate](colocate-schemas-with-what-they-validate.md) - A validator lives next to what it guards, not in a centralized schema file. The adjacency is the rule; the filename convention is per-project.

# React

* [use-client-is-a-javascript-boundary](use-client-is-a-javascript-boundary.md) - The directive marks where JS ships, not where interactivity lives. A Server Component can render an interactive button.

# Database

* [prefer-metadata-only-schema-changes](prefer-metadata-only-schema-changes.md) - Migration cost is a design input. Append enum values; inserting mid-list rewrites every row.

# Background jobs

* [poll-with-capped-backoff](poll-with-capped-backoff.md) - Size the window to the provider's worst case. attempts × interval is an unstated timeout that misattributes the failure.
* [cap-external-file-size-before-ingest](cap-external-file-size-before-ingest.md) - State the maximum and fail legibly; otherwise the ceiling arrives as an OOM that looks like infrastructure.

# Design system

* [constrain-the-palette-at-config](constrain-the-palette-at-config.md) - Remove redundant token scales from the toolchain config so misuse doesn't compile, rather than banning them in review.
* [semantic-tokens-only](semantic-tokens-only.md) - Use semantic and intent tokens. Hardcoded values and raw palette steps both break theming and dark mode.
* [typography-and-layout-as-utilities](typography-and-layout-as-utilities.md) - Use font utilities and real HTML elements. Component primitives for text and layout add a layer that buys nothing and costs semantics.
* [flex-column-children-stretch-by-default](flex-column-children-stretch-by-default.md) - w-full is a no-op on a flex-column child; opt out with self-start, never parent items-start.
* [read-primitive-defaults-before-overriding](read-primitive-defaults-before-overriding.md) - A re-stated default is a pinned copy of a value you don't own, and it drifts silently.
* [ds-vendor-wrap-export-layering](ds-vendor-wrap-export-layering.md) - When using a component generator — treat generated primitives as third-party, put your opinions in a thin wrapper layer, and curate the public surface.
* [ds-wrapper-passthrough](ds-wrapper-passthrough.md) - Derive props from the primitive, add your own, merge classes, spread the rest. Never a bare re-export.

# API design

* [deprecate-without-breaking-consumers](deprecate-without-breaking-consumers.md) - Keep the original export, mark it @deprecated with a prop-by-prop mapping, and point at the replacement's live examples.

# Review

* [conventional-comments](conventional-comments.md) - Every review comment carries an explicit label and blocking-ness, so the reader never has to guess whether feedback is a blocker.
