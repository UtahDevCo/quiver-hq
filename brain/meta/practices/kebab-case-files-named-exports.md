---
type: Practice
title: kebab-case filenames, PascalCase components, named exports only
description: Files are kebab-case, component identifiers are PascalCase, and nothing uses a default export. The no-default-export half is the load-bearing part.
tags: [file-organization, naming, imports, react]
generated: { by: claude/opus-5, at: 2026-07-29T22:55:47Z }
verified:
  - { by: human:christopher, at: 2026-07-29T22:55:47Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "export default function Button() {}"
    why: "the import name is unconstrained, so the same component gets imported under different names; it is invisible to grep and to rename refactors, and re-exporting it through a barrel needs an alias"
    instead: "export function Button() {}"
  - term: "PascalCase or camelCase filenames (Button.tsx, userAvatar.tsx)"
    why: "case-insensitive filesystems on macOS and Windows treat Button.tsx and button.tsx as the same file, so a case-only rename produces a phantom diff that CI on Linux sees differently"
    instead: "button.tsx, user-avatar.tsx"
  - term: "UPPER_SNAKE or kebab-case for component identifiers"
    why: "JSX resolves a lowercase tag as an HTML element, so <user-avatar /> silently renders an unknown element instead of your component"
    instead: "PascalCase identifiers inside kebab-case files"
sources:
  - id: tools-agents
    resource: projects/tools/AGENTS.md
    title: "tools AGENTS.md — file naming and export rules"
    author: human:christopher
    last_modified: 2026-07-29
  - id: wiley-code
    resource: projects/wiley/web/components/forms/form-input.tsx
    title: "wiley — form-input.tsx, contact-drawer.tsx, admin-leads-table.tsx; named exports throughout"
    last_modified: 2026-07-29
  - id: trikin-code
    resource: projects/trikin/web/src/components/click-button.tsx
    title: "trikin — click-button.tsx, admin-leads-table.tsx; named exports throughout"
    last_modified: 2026-07-29
  - id: zamp-code
    resource: projects/zamp/utils/design-system/src/components/input-field.tsx
    title: "zamp — kebab-case design-system files, named exports through a curated barrel"
    last_modified: 2026-07-25
---

# The practice

- **Files**: `kebab-case.tsx` / `kebab-case.ts`.
- **Component and type identifiers**: `PascalCase`.
- **Module-level constants**: `UPPER_SNAKE_CASE`.
- **Exports**: named. No `export default`, anywhere.

# Why no default exports is the part that matters

The naming halves are coordination — pick one and stop thinking about it. The
default-export ban buys something concrete:

- **The import name becomes part of the contract.** With a default export, two files
  can import the same component as `Button` and `Btn`, and both compile. Grep stops
  working, and so does "rename symbol."
- **Barrels stay mechanical.** `export * from './button'` composes; a default export
  needs `export { default as Button }` written by hand for every file.
- **Tree-shaking and lazy boundaries stay predictable.** A default export of an
  anonymous arrow function gives bundlers and stack traces nothing to name.

The exception you will actually hit: Next.js App Router **requires** default exports
for `page.tsx`, `layout.tsx`, `route.ts`, and friends. That is a framework contract,
not a violation — the rule is about your own modules.

# Corroboration

All four repos, in code, independently of documentation. `tools` and `trikin` also
state it in `AGENTS.md`, but those two files descend from a shared template so they
count as one written source — the reason this is recorded as a practice is that
wiley and zamp follow it too, having never been told to in a document that was
harvested here. See
[corroboration-requires-independent-sources](../workflows/corroboration-requires-independent-sources.md).
