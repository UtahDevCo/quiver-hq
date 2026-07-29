# Practices

Default-on. Follow unless a project override says otherwise.

# Enforcement

* [make-misuse-unrepresentable](make-misuse-unrepresentable.md) - Delete the alternatives from the toolchain instead of documenting a preference.

# Design system

* [constrain-the-palette-at-config](constrain-the-palette-at-config.md) - Delete redundant token scales so misuse doesn't compile.
* [semantic-tokens-only](semantic-tokens-only.md) - Reference semantic and intent tokens; never raw palette steps or hardcoded values.
* [typography-and-layout-as-utilities](typography-and-layout-as-utilities.md) - Font utilities on semantic HTML; no Text/Heading/Flex/Box primitives; gap over margins.
* [ds-vendor-wrap-export-layering](ds-vendor-wrap-export-layering.md) - Generated primitives are third-party; wrappers hold your opinions; the barrel is curated.
* [ds-wrapper-passthrough](ds-wrapper-passthrough.md) - Type wrappers off the primitive with ComponentProps; never a bare re-export.

# API design

* [deprecate-without-breaking-consumers](deprecate-without-breaking-consumers.md) - Keep the old export, mark @deprecated with a prop-by-prop mapping including its gaps.
