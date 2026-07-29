---
type: Invariant
title: No newly added @util/ui or Rt* imports
description: Changed lines must not introduce imports from the frozen @util/ui package or Rt* Radix Themes components. Scoped to the diff, because existing usages are not violations.
tags: [design-system, deprecation, migration, attested]
generated: { by: claude/opus-5, at: 2026-07-29T20:23:37Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-01-29
relations:
  - { kind: instance-of, target: /projects/zamp/decisions/deprecated-ui-surfaces.md }
runtime: bash
parameters:
  base_ref: origin/master
  head_ref: HEAD
computation: /references/checks/zamp-no-new-deprecated-ui-imports.sh
executor:
  resource: /references/checks/zamp-no-new-deprecated-ui-imports.sh
  receipt: '{ "command": "<cmd>", "exit_code": 0, "matches": [] }'
attester:
  resource: /references/expect_empty.py
not:
  - term: "running this check across the whole repo"
    why: "88 files import @util/ui and 145 use Rt* components; a whole-repo check fails permanently and carries no information"
    instead: "diff-scope it — the decision says only newly added or modified lines are violations, so the diff IS the invariant"
sources:
  - id: decision
    resource: brain/projects/zamp/decisions/deprecated-ui-surfaces.md
    title: The decision this check enforces
    author: human:christopher
---

# The invariant

No added line in a changed `.ts`/`.tsx` file imports from `@util/ui` (bare or
subpath) or references an `Rt*` component. Enforces
[deprecated-ui-surfaces](../decisions/deprecated-ui-surfaces.md).

Excluded: `utils/design-system/`, `utils/design-system-next/` (they legitimately
contain the deprecated wrappers), and `*.stories.tsx` (which demonstrate deprecated
components on purpose).

# Running it

```bash
brain/references/checks/zamp-no-new-deprecated-ui-imports.sh [base-ref] [head-ref] \
  | brain/references/expect_empty.py
```

Both ends are parameters so the check can be validated against historical ranges
without checking anything out. That matters: zamp is a shared working tree, and an
attester that requires mutating it to test is an attester nobody tests.

# Verdicts

| Exit | Meaning |
|---|---|
| 0 | PASS — no new deprecated imports on the diff |
| 1 | VIOLATED — reports each `file:line` |
| 2 | ERROR — the check could not run |

The 1-vs-2 split is deliberate. "The check ran and found a violation" and "the check
never produced a verdict" are different findings, and collapsing them into a single
failure is how real breakage gets lost in noise.

# Validation

Proven against real history rather than asserted:

- `f530e5049^..f530e5049` — added `import { parseAsISODateRange } from "@util/ui"` →
  **VIOLATED**, reporting `search-params.ts:19`.
- `b2d8a8caf^..b2d8a8caf` — a migration commit that *removed* two `@util/ui`
  imports → **PASS**, correctly.
- Nonexistent base ref → **ERROR**, not a false pass.

Two bugs found and fixed during that validation, both of which would have made the
check silently useless:

1. The first regex required a closing quote, so it matched only the bare
   `"@util/ui"` and missed every subpath import (`@util/ui/components/Filters/parsers`)
   — which is how most real usages are written.
2. `@util/ui-templates` is a **separate, current** package. The regex must not flag
   it. There is now a negative control for exactly this.

The first test run was itself a false negative caused by a bad test premise:
`git log -S` counts occurrence changes in *either* direction, so the commit picked
as "adds an import" had actually removed two. Worth remembering — the check was
right and the test was wrong.
