# zamp

Project knowledge for `projects/zamp`. Reachable from inside the repo as
`.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Practices

Project-local practices — not general enough (yet) for the meta layer.

* [real-db-test-for-prisma-changes](practices/real-db-test-for-prisma-changes.md) - New or changed Prisma calls ship with a real-DB test. Shard-key and join defects are invisible to types and to mocked prisma.
* [triple-validation](practices/triple-validation.md) - Client, server action, and domain mutation each validate — because background jobs bypass the first two.
* [state-management-direction](practices/state-management-direction.md) - Read through async server components; write through server actions. Client-side tRPC and react-query are deprecated.
* [inngest-background-conventions](practices/inngest-background-conventions.md) - Naming, step selection, and error semantics for background functions. Test the underlying mutation unless the function holds real orchestration.
* [story-per-component](practices/story-per-component.md) - Every design-system component ships a colocated Storybook story. Storybook is zamp-only, so this is scoped here.
* [directive-driven-filenames](practices/directive-driven-filenames.md) - `'use client'` → `*.client.tsx`, `'use server'` → `*.action.ts`. Promotion candidate once wiley corroborates.

# Modules

* [monorepo-and-domain-structure](modules/monorepo-and-domain-structure.md) - pnpm workspace on Turborepo. Business logic in versioned domain packages following CQRS; apps consume them.
* [design-system-next](modules/design-system-next.md) - A Next.js overlay, not the next generation. Use it when you need router integration.

# Invariants

* [sharded-tables-companyid](invariants/sharded-tables-companyid.md) - Every Prisma operation on a sharded table carries companyId at the top level of `where`/`data`. A nested relation does not count.
* [relation-load-strategy](invariants/relation-load-strategy.md) - Nested reads touching sharded tables need `relationLoadStrategy: "query"` — in four specific cases, not blanket.
* [no-new-deprecated-ui-imports](invariants/no-new-deprecated-ui-imports.md) - **Attested.** No added line imports `@util/ui` or an `Rt*` component. Diff-scoped; validated against real history.

*The two Prisma invariants have no executable check yet. `sharded-tables-companyid` is the highest-value remaining candidate — it needs the sharded-table list joined against call sites.*

# Decisions

* [deprecated-ui-surfaces](decisions/deprecated-ui-surfaces.md) - `@util/ui` and the `Rt*` generation are retired but still importable. Existing usages in untouched files are not violations.

# Workflows

* [add-ds-component](workflows/add-ds-component.md) - Install and wrap the primitive, fix generator import bugs, write stories from the fetched docs, polish. The barrel export is left to the human.
* [git-branch-and-pr-naming](workflows/git-branch-and-pr-naming.md) - Linear ticket prefix, lowercase in branches and uppercase in PR titles. Both CI-gated; commits are not.

# Gems

*Project-local patterns worth promoting to meta. Empty.*
