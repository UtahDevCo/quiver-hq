# Inbox

Unreviewed observations. Everything enters the brain here as `type: Observation`
with `status: draft`, then `/brain-promote` places it into `meta/` or
`projects/<name>/` with a human `verified` entry.

Agents write here freely. Agents never write to `meta/` directly.

# Required shape

Prefer `brain_push` (from `solo/solo-child-lib.sh`) or `/brain-push`, which emit
this for you. If you write the file by hand, use **this** shape:

```yaml
---
type: Observation
title: <one line stating the rule, not the topic>
description: <one sentence a reviewer can triage from>
kind: practice|pattern|failure-mode|stack|workflow|module|invariant|decision
proposed_layer: meta|project
proposed_project: <name>        # only when proposed_layer is project
observed_in: <name>             # always — this is provenance
tags: [...]
status: draft
not:                            # wherever an anti-pattern is known
  - { term: "...", why: "...", instead: "..." }
generated: { by: claude/opus-5, at: <ISO 8601 UTC> }
sources:
  - { id: <slug>, resource: <path or url>, title: <what it is> }
---
```

**This is not the auto-memory format.** `name:` / `description:` /
`metadata.type:` belongs to Claude's per-session memory store — a different thing in
a different directory. Files in that shape have landed here three times. They get
normalized at promotion, but the shape silently drops `kind`, `proposed_layer`,
`sources`, and `not:` — the four fields triage actually uses. In particular
`metadata.type: project` means a *memory category*, not a brain layer, so it reads as
a layer proposal that was never made.

Never set `verified:`. That is the promotion gate and it is Chris's alone.

# Currently queued

**2026-07-29 — two failure modes.** Both have now been normalized to the shape
above, `[[wikilinks]]` converted to relative links that resolve, so they need no
special handling at promotion:

* `git-commit-commits-the-index-not-your-paths` - `git commit` takes the whole index, so another session's already-staged deletion rode into a "one file" commit and reached main.
* `paginated-list-apis-may-not-be-sorted` - a `pageSize=40` query hid the newest rollout, making a live deploy look like it had never triggered.

**2026-07-30 — wiley, 1 decision:**

* `wiley-ships-on-main-not-by-pull-request` - Chris's stated workflow: commit to `main` and push; a push to `main` is itself the deploy, so a PR only delays it.

**2026-07-30 — the trikin harvest, 17 observations.** Written during the Trikin
Capital pivot. `projects/trikin/index.md` is still the empty stub, so this batch
populates a layer from nothing.

*Proposed `meta` (7) — read these first; three are new failure modes:*

* `a-boolean-authorization-guard-is-not-a-guard` - a guard returning `bool` is a no-op when the caller forgets it, and cannot carry tenancy. Throw, and return the scope.
* `caching-a-limit-check-silently-defeats-it` - a cached exposure figure leaves the check running against stale data. The control appears to work and does not.
* `impersonation-without-an-audit-row-destroys-attribution` - swapping `session.user.id` with no audit row makes the trail assert something false.
* `money-in-a-float-column-is-a-latent-defect` - `real` cannot hold `$1,782.59`. Integer minor units, and the unit goes in the column name.
* `when-two-documents-describe-one-system-rank-them-first` - a workflow. The clearest, newest source described an illegal version of the product.
* `render-a-signed-artifact-once-and-content-address-it` - a pattern. Freeze the bytes, pin the template, re-verify on a schedule.
* `trikin-corroborates-four-meta-practices-independently` - upgrades three practices off single-source, and records one honest negative: `small-single-purpose-files` is violated at scale here.

*Proposed `project: trikin` (10):*

* `purchase-price-flows-through-the-broker` - **the flagship invariant.** Trikin never pays an agent; the schema gives it nowhere to happen.
* `an-approval-threshold-applies-to-the-aggregate` - the $10k line is measured across seven relationship dimensions, because it exists to stop splitting.
* `the-payor-not-the-claimant-sets-the-verified-amount` - two commission columns with provenance; they disagreed by 11% in the first real example.
* `dual-approval-means-two-organisations-not-two-approvers` - authority needs effective dating and an org, so it cannot live in `users.appRoles`.
* `trikin-retires-the-lead-distribution-model` - a decision. What the deleted tables and integrations were, so old commits stay legible.
* `shadcn-repo-ships-tailwinds-full-palette` - `suspend` override on `constrain-the-palette-at-config`. Also records two design-system practices *checked and passing*.
* `shadcn-primitives-are-the-wrapper-layer` - `replace` on `ds-vendor-wrap-export-layering`, `suspend` on `ds-wrapper-passthrough`. One fact, two override files.
* `bun-test-is-the-runner-not-vitest` - `narrow` on both testing practices. Substance holds; the import surface differs.
* `the-three-export-stacking-drawer-recurs-in-two-repos` - diffed against wiley before counting: common ancestry, independently evolved. The *shape* promotes; wiley's accessibility work does not.
* `atomic-batch-is-not-a-serializable-transaction` - filed `project` because the `meta.changes` idiom is D1-specific, but the general form — atomicity is not isolation, so check-then-act needs both in one operation — is the promotion candidate here.

**2026-07-30 — two more from building the money layer.** Both proposed `meta`,
both backed by passing tests rather than by reasoning:

* `scope-the-parameter-so-the-wrong-base-is-unreachable` - a per-function sibling to `make-misuse-unrepresentable`: when two same-typed values are incompatible bases for one calculation, don't pass the container that holds both. Priced off the commission instead of the fee, Trikin overpays 42.9% and nothing throws.
* `derive-the-other-side-of-a-money-split-by-subtraction` - `remainder = total - part`, so the parts sum to the whole by construction. Also pins `Math.round`'s tie-breaking asymmetry, which loses a cent on negative amounts only.

**2026-07-31 — six from releasing the k1 adversarial panel and building its
measurement set.** Five proposed `meta`, one `project: k1`. Two are recorded
against my own errors rather than against a code defect:

* `a-local-model-override-measures-a-model-you-do-not-ship` - `.env.local` pinned an older judge than production, so the reliability number described a model no user is served: 3 invalid outputs in 18 runs against 0 in 13.
* `check-what-the-evaluator-reads-before-regenerating-data` - **my error.** I called 16 of 28 measurement cases spoiled by that wrong model id. The eval case carries only question, bundle, member answers, and label, so the judge is re-run and the stored verdict is never read. Regenerating would have spent ~28 paid multi-provider runs to change nothing.
* `reading-an-artifact-can-consume-the-blind-measurement` - **also mine.** A polling probe captured the verdict chip, which would have destroyed blindness for every constructed case before the labeller opened one, with `capturedBlind` still recording `true`.
* `a-missing-runtime-secret-ships-a-healthy-build-with-the-feature-inert` - a monorepo with two `apphosting.yaml` files, a backend `rootDirectory` pointing at one of them, and a feature that falls back by design. Green deploy, passing smoke test, nothing switched on.
* `wait-for-the-work-to-start-before-waiting-for-it-to-finish` - a fixed sleep after submit let slow requests read as finished, so the next navigation aborted them in flight. Two edges instead of one fixed 38 of 40 generations and turned the remaining two into a named failure that was a real bug.
* `an-idempotency-guard-makes-a-dropped-write-look-like-success` (`project: k1`) - identical text into a fresh conversation returns HTTP 200 with nothing rendered and nothing stored. Cause is a hypothesis (content-derived message id hitting a 409 guard); the symptom is reproducible and user-reachable.

**2026-07-31 — three from a K-1 field the model could not see.** All proposed
`meta`. One diagnosis, one test, one probe, from the same bug: the chat reported
Box L absent while the matrix UI displayed it.

* `a-models-account-of-its-own-context-is-a-claim-about-the-payload` - user insists the data is there, model insists it cannot see it, both correct. Two accessors on one normalized record and only the UI's was extended. Diagnosis is `grep` the field name and count the readers.
* `test-that-the-prompt-names-the-fields-the-payload-ships` - nothing type-checks a prompt against its data. k1's prompt asked for a basis walk with a capital-contributions column against a bundle that never carried one, through two prompt revisions.
* `measure-field-coverage-before-writing-instructions-that-assume-it` - a declared optional column populated in 0 of 679 rows. The instruction premised on it would have had the model read the gap as zero and book a whole ending balance as a first-year increase.
