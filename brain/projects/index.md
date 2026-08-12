# Projects

Per-project knowledge and overrides of the [meta layer](../meta/index.md). Each
directory is symlinked into its submodule as `.brain` (git-ignored), so a
session working inside a project can read it at a stable relative path.

* [zamp](zamp/index.md) - Zamp tax platform. pnpm/Turborepo monorepo, DDD domains, Vitess sharding, in-house design system.
* [wiley](wiley/index.md) - Next.js app. Source of the drawer, sidebar, form, and data-table patterns.
* [tools](tools/index.md) - Internal tooling. Frontend-design and chrome-devtools practices.
* [trikin](trikin/index.md) - trikin.co.
* [k1](k1/index.md) - Deterministic Schedule K-1 / Form 1065 extraction and tax engine. LLM extraction measurement lives here.

# Deliberately excluded

* `k1-fork` - third-party fork (`schulzgregory/tax-pe-fork`). Not our code; its conventions are not ours to adopt.
