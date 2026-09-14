# Projects

Per-project knowledge and overrides of the [meta layer](../meta/index.md). Each
directory is symlinked into its project folder as `.brain` (git-ignored), so a
session working inside a project can read it at a stable relative path. Most
projects are submodules; some (like `3d-printing`) are standalone folders
managed by quiver-hq directly.

* [zamp](zamp/index.md) - Zamp tax platform. pnpm/Turborepo monorepo, DDD domains, Vitess sharding, in-house design system.
* [wiley](wiley/index.md) - Next.js app. Source of the drawer, sidebar, form, and data-table patterns.
* [tools](tools/index.md) - Internal tooling. Frontend-design and chrome-devtools practices.
* [trikin](trikin/index.md) - trikin.co.
* [k1](k1/index.md) - Deterministic Schedule K-1 / Form 1065 extraction and tax engine. LLM extraction measurement lives here.
* [quiver-photos-v2](quiver-photos-v2/index.md) - Google Photos backup tool. Go TUI (v3) plus Cloudflare Pages functions; releases auto-publish on a v3.* tag.
* [3d-printing](3d-printing/index.md) - Home 3D printing setup. QIDI Plus 4 (heated-chamber CoreXY), SUNLU dryer, Magigoo; PLA+/PETG/PETG-CF/TPU. Standalone folder, not a submodule.
* [popreminders.com](popreminders.com/index.md) - Reminder app. Expo SDK 57 dev-build + Firebase (pop-reminders); Firestore rules/indexes, FCM, and notifee channels.
* [therapyanimalhub.com](therapyanimalhub.com/index.md) - TAH. Affiliate/commission platform on Turso; production writes via maintenance scripts.

# Deliberately excluded

* `k1-fork` - third-party fork (`schulzgregory/tax-pe-fork`). Not our code; its conventions are not ours to adopt.
