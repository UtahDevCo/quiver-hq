# zamp

Project knowledge for `projects/zamp`. Reachable from inside the repo as
`.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

* [no-text-heading-layout-primitives](overrides/no-text-heading-layout-primitives.md) - `extend` on [typography-and-layout-as-utilities](../../meta/practices/typography-and-layout-as-utilities.md) — Typography and layout primitives are banned outright

# Patterns

* [accessibility-enforced-by-types](patterns/accessibility-enforced-by-types.md) - A discriminated union requiring a label, placeholder, or aria-label turns an accessibility rule into a compile error.
* [theme-by-data-attribute](patterns/theme-by-data-attribute.md) - A theme is a directory satisfying a token contract, scoped to [data-theme="name"], with dark mode as a nested selector.

# Workflows

* [add-ds-component](workflows/add-ds-component.md) - Install and wrap the primitive, fix known generator import bugs, write stories from the fetched docs, then polish and deprecate. The barrel export is left to the human.
* [git-branch-and-pr-naming](workflows/git-branch-and-pr-naming.md) - Linear ticket prefix, lowercase in branches and uppercase in PR titles. Both are CI-gated; commits are not.

# Failure modes

* [an-exemption-total-sums-taxableamount-because-deduction-rules-can-be-taxable](failure-modes/an-exemption-total-sums-taxableamount-because-deduction-rules-can-be-taxable.md) - minZero(taxableAmount).plus(minZero(nontaxableAmount)) is load-bearing, and TN Schedule A deduction 1 (food) is TAXABLE at 4%. Copying the idiom to a schedule whose rule is EXEMPT invites a taxed base being reported as exempt.
* [minzero-clamps-each-bucket-before-the-sum-so-refunds-do-not-net](failure-modes/minzero-clamps-each-bucket-before-the-sum-so-refunds-do-not-net.md) - Clamping happens per bucket after the groupBy and before the plus, so taxableAmount -100 with nontaxableAmount 500 yields 500 rather than 400.

# Practices

* [directive-driven-filenames](practices/directive-driven-filenames.md) - A 'use client' file is named *.client.tsx; a 'use server' file is named *.action.ts. Which side of the boundary a file lives on is visible in the tree.
* [inngest-background-conventions](practices/inngest-background-conventions.md) - Naming, step selection, and error semantics for background functions. Test the underlying mutation unless the function holds real orchestration logic.
* [real-db-test-for-prisma-changes](practices/real-db-test-for-prisma-changes.md) - Shard-key and join-strategy defects are invisible to type-checking and to mocked prisma. Only a real database catches them.
* [state-management-direction](practices/state-management-direction.md) - Client-side tRPC and react-query are deprecated. Resolve data in async server components and pass it down as props.
* [story-per-component](practices/story-per-component.md) - A new component .tsx without a matching .stories.tsx is incomplete. Vendored primitives are exempt.
* [triple-validation](practices/triple-validation.md) - Client, server action, and domain mutation each validate — because background jobs bypass the first two.

# Modules

* [design-system-next](modules/design-system-next.md) - The name suggests a successor package. The code is a framework-integration layer that depends on the base package. Use it when you need router integration.
* [monorepo-and-domain-structure](modules/monorepo-and-domain-structure.md) - pnpm workspace on Turborepo. Business logic in versioned domain packages following CQRS; apps consume them.

# Invariants

* [exemptamount-is-always-zero-exempt-sales-live-in-nontaxableamount](invariants/exemptamount-is-always-zero-exempt-sales-live-in-nontaxableamount.md) - The tax engine hardcodes exemptAmount to 0 at its only write site and routes RuleType.EXEMPT into nontaxableAmount, so summing exemptAmount is a provable no-op.
* [no-new-deprecated-ui-imports](invariants/no-new-deprecated-ui-imports.md) - Changed lines must not introduce imports from the frozen @util/ui package or Rt* Radix Themes components. Scoped to the diff, because existing usages are not violations.
* [relation-load-strategy](invariants/relation-load-strategy.md) - With relationJoins enabled, nested reads default to a join strategy that compiles to correlated subqueries and fails on Vitess with VT12001.
* [ruletype-adjusted-is-dead-enum-surface](invariants/ruletype-adjusted-is-dead-enum-surface.md) - ADJUSTED appears in 0 of 53 rule CSVs and the engine handles it in the same branch as TAXABLE, so it reads as a distinct tax treatment that does not exist.
* [sharded-tables-companyid](invariants/sharded-tables-companyid.md) - Reads, writes, and upserts against sharded tables must include companyId at the top level of where/data — a nested relation does not count.

# Decisions

* [deprecated-ui-surfaces](decisions/deprecated-ui-surfaces.md) - Three retired surfaces are still importable. New code uses design-system or design-system-next; existing usages in untouched files are not violations.

# Gems

*Project-local patterns worth promoting to meta. Empty.*
