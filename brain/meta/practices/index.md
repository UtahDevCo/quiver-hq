# Practices

Default-on. Follow unless a project override says otherwise.

# Enforcement

* [make-misuse-unrepresentable](make-misuse-unrepresentable.md) - Delete the alternatives from the toolchain instead of documenting a preference.
* [follow-local-conventions](follow-local-conventions.md) - Match the surrounding module for internal idiom; uniformity applies only to visible surface.

# Style

* [minimal-comments](minimal-comments.md) - Comment the non-obvious why, never the what. Don't touch others' comments.
* [small-single-purpose-files](small-single-purpose-files.md) - ~200 lines logic, ~300 components, one primary export, delete orphaned code immediately.

# Error handling

* [error-propagation-and-capture](error-propagation-and-capture.md) - Propagate untouched, capture once at the edge.
* [no-error-objects-across-boundaries](no-error-objects-across-boundaries.md) - Error instances don't serialize; pass the message.

# Testing

* [assert-on-whole-values](assert-on-whole-values.md) - toStrictEqual the whole error; unwrap inline; no single-use intermediates.
* [mock-at-narrowest-scope](mock-at-narrowest-scope.md) - spyOn before module mocks; always assert how it was called.

# Measurement

* [report-a-rate-per-condition-never-pooled](report-a-rate-per-condition-never-pooled.md) - Three degradations pooled to 77.4%, which no condition exhibited. Split by condition, hold the sample fixed, and report detection beside accuracy.

# Validation

* [colocate-schemas-with-what-they-validate](colocate-schemas-with-what-they-validate.md) - Schema sits beside the function it guards.

# Design system

* [constrain-the-palette-at-config](constrain-the-palette-at-config.md) - Delete redundant token scales so misuse doesn't compile.
* [semantic-tokens-only](semantic-tokens-only.md) - Semantic and intent tokens only; no raw palette steps or hardcoded values.
* [typography-and-layout-as-utilities](typography-and-layout-as-utilities.md) - Purpose-named font utilities on semantic HTML; gap over margins.
* [ds-vendor-wrap-export-layering](ds-vendor-wrap-export-layering.md) - Generated primitives are third-party; wrappers hold your opinions.
* [ds-wrapper-passthrough](ds-wrapper-passthrough.md) - Type wrappers off the primitive; never a bare re-export.

# API design

* [deprecate-without-breaking-consumers](deprecate-without-breaking-consumers.md) - Keep the old export; the migration guide names its own gaps.

# Review

* [conventional-comments](conventional-comments.md) - Labelled feedback with explicit blocking-ness. Applies to agent output too.
