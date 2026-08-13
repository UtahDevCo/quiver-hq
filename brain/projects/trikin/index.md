# trikin

Project knowledge for `projects/trikin`. Reachable from inside the repo as
`.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

* [bun-test-is-the-runner-assertions](overrides/bun-test-is-the-runner-assertions.md) - `narrow` on [assert-on-whole-values](../../meta/practices/assert-on-whole-values.md) — Whole-value assertions come from bun:test, not vitest
* [bun-test-is-the-runner-mocking](overrides/bun-test-is-the-runner-mocking.md) - `narrow` on [mock-at-narrowest-scope](../../meta/practices/mock-at-narrowest-scope.md) — The mocking escalation ladder uses bun:test's spyOn and mock.module
* [shadcn-has-no-wrapper-layer-to-govern](overrides/shadcn-has-no-wrapper-layer-to-govern.md) - `suspend` on [ds-wrapper-passthrough](../../meta/practices/ds-wrapper-passthrough.md) — There is no wrapper layer here for ds-wrapper-passthrough to govern
* [shadcn-primitives-are-the-wrapper-layer](overrides/shadcn-primitives-are-the-wrapper-layer.md) - `replace` on [ds-vendor-wrap-export-layering](../../meta/practices/ds-vendor-wrap-export-layering.md) — In a shadcn repo the generated primitives are the wrapper layer
* [shadcn-repo-ships-tailwinds-full-palette](overrides/shadcn-repo-ships-tailwinds-full-palette.md) - `suspend` on [constrain-the-palette-at-config](../../meta/practices/constrain-the-palette-at-config.md) — A stock shadcn/ui repo cannot satisfy constrain-the-palette-at-config

# Patterns

* [render-a-signed-artifact-once-and-content-address-it](patterns/render-a-signed-artifact-once-and-content-address-it.md) - "Capable of accurate reproduction" fails the moment a referenced record changes. Freeze the bytes, store the hash, pin the template version, and re-verify on a schedule.
* [route-unapproved-config-through-the-domains-exception-path-not-an-env-check](patterns/route-unapproved-config-through-the-domains-exception-path-not-an-env-check.md) - When config is provisional, gating on NODE_ENV or a deploy flag lets it become authoritative by being deployed. Mark the config unapproved and let the domain's existing escalation carry it.
* [the-three-export-stacking-drawer-recurs-in-two-repos](patterns/the-three-export-stacking-drawer-recurs-in-two-repos.md) - Both repos export Drawer / DrawerViewport / closeHighestDrawer over a reference-counted scroll lock, and the APIs diverged, so the shape corroborates while wiley's accessibility work stays wiley-only.

# Workflows

*How to run a piece of work here. Empty.*

# Failure modes

* [a-writeback-field-list-is-a-disclosure-decision](failure-modes/a-writeback-field-list-is-a-disclosure-decision.md) - Fields you push into a counterparty's system are visible to everyone with a seat in it. Ask who reads the record, not just what the integration needs.
* [atomic-batch-is-not-a-serializable-transaction](failure-modes/atomic-batch-is-not-a-serializable-transaction.md) - Cloudflare D1's db.batch() is atomic, but the read that informed the decision happened in an earlier round trip. Two concurrent requests can both observe a pre-decision world and both write.
* [drizzle-sqlite-table-recreation-breaks-renames-and-qualified-checks](failure-modes/drizzle-sqlite-table-recreation-breaks-renames-and-qualified-checks.md) - A generated `__new_table` recreation can read the post-rename column name from the pre-rename table and emit a table-qualified CHECK that cannot survive RENAME TO.
* [drizzle-wraps-constraint-errors-on-execute-but-not-on-batch](failure-modes/drizzle-wraps-constraint-errors-on-execute-but-not-on-batch.md) - A UNIQUE-violation catch that matches error.message works after db.batch() and silently fails after .execute(), because only the latter wraps the driver error in DrizzleQueryError. Walk the cause chain.

# Practices

*Project-local rules. Empty.*

# Modules

*What the major pieces are and how they fit. Empty.*

# Invariants

* [an-approval-threshold-applies-to-the-aggregate](invariants/an-approval-threshold-applies-to-the-aggregate.md) - The $10,000 dual-approval line is measured across seven relationship dimensions plus the candidate, because the policy exists to stop one purchase being split into two.
* [dual-approval-means-two-organisations-not-two-approvers](invariants/dual-approval-means-two-organisations-not-two-approvers.md) - "Both Members must approve" is unprovable by counting approvals. Authority needs an effective-dated identity carrying its organisation, its cap, and the resolution that granted it.
* [purchase-price-flows-through-the-broker](invariants/purchase-price-flows-through-the-broker.md) - The purchaser buys the Agent's Fee from the Broker and pays the Broker, who then pays its agent. Paying an agent directly is an unlicensed-brokerage-compensation violation, so the schema gives it nowhere to happen.
* [the-payor-not-the-claimant-sets-the-verified-amount](invariants/the-payor-not-the-claimant-sets-the-verified-amount.md) - The brokerage's computed commission and the property manager's acknowledged commission are different numbers that routinely disagree. Store both with provenance; underwrite the payor's.

# Decisions

* [trikin-retires-the-lead-distribution-model](decisions/trikin-retires-the-lead-distribution-model.md) - The leads domain was deleted rather than migrated and its data dropped without a snapshot, on Chris's instruction. Records what those tables and integrations were so old commits stay readable.

# Gems

*Project-local patterns worth promoting to meta. Empty.*
