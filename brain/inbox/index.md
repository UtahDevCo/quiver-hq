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

Two more from the same k1 thread, after auditing 168 stored extractions against
their source PDFs. Both are about what a check is worth, and both were paid for by
shipping the wrong thing first and measuring it:

* `a-witness-the-model-generates-cannot-check-the-model` - had the extractor echo the row it read from, then transcribe rows verbatim before filling fields. Both witnesses reproduced the misread: the check fired on 0 of 25 known-wrong readings. Compare against a field the failing step did not produce, and score the detector on known-bad cases before shipping it.
* `a-b-a-prompt-fix-before-shipping-it` - the instruction that named the failure exactly measured 23 of 48 clean runs against 25 of 48 without it. Run-to-run variance at temperature 0 exceeded the effect. Negative result kept in the test file so the reasoning is not re-run.

**2026-08-03 — one from validating the regenerated K-1 corpus.** Proposed `meta`.
The corpus fixed everything I had asked for and still contradicted the returns it
came from, because the invariant I supplied was the wrong law.

* `a-per-record-validator-cannot-catch-a-wrong-rule` - **my error.** I told the generator that capital plus liabilities can never go negative. Section 704(d) limits the deduction, not the allocation, so it enforced it by shrinking the allocation. 175 of 175 documents pass 12 internal checks; the partners' K-1s miss the partnership's Schedule K by 305,247 on one year. Only a check spanning records against an independently computed total could see it.

**2026-08-04 — three from auditing wiley's free-month over-grant in production.** Proposed
`meta`. A monitor named in a commit message as the proof a billing fix held had been
reporting PASS while reading a field that does not exist.

* `a-filter-that-matches-nothing-every-run-is-a-broken-predicate` - `skipReason` is written nowhere; the writer records the reason in `error`. The filter matched 0 of 2472 documents on every date. Assert the predicate matches something collection-wide and abort with a distinct exit code when it does not. **Corrects the "empty candidate set" diagnosis in `audits-must-report-their-own-coverage`, which cites this same file and blames that day's small population; it carries two human `verified` entries.**
* `a-checker-that-never-matched-a-row-has-untested-verdict-logic` - repairing the selector exposed a second defect: the verdict called every post-boundary comp a violation, but a promo month is post-boundary by design, so it reported FAIL on two correct production days. Zero matched rows means zero executions of the pass/fail branch.
* `duplicated-predicates-rot-first-in-the-code-nobody-runs` - six copies of one filter, and the three wrong ones were the verification, the audit, and the production cleanup. Users correct runtime copies; nothing corrects a monitor that reports zero.

**2026-08-05 — 16 routed out of zamp's `patterns.md`.** Chris supplied a ~90-item
distillation of recurring PR-review feedback (now kept as the citable source at
`local/zamp/patterns.md`). A grep sweep confirmed most of it was absent from
`AGENTS.md`, `.coderabbit.yaml`, `.cursor/rules`, the `pr-review` checklist, and
this brain — so it is net-new material, not a re-distillation. The ~45 operational
"flag this in review" items went into the `pr-review.local.md` checklist instead of
here; these 16 are the ones that pass the brand-new-empty-repo test. All evidence
is zamp-only, so none of them is corroborated across repos yet.

*Proposed `meta` (15):*

* `treat-migration-friction-as-a-first-class-design-cost` - **read first.** Append enum values, never mid-insert: appending is a metadata-only `ALTER`, inserting shifts every later ordinal and forces a table rebuild. The out-of-group comment is load-bearing — without it the next tidy-up silently reintroduces the rewrite.
* `read-a-primitives-defaults-before-overriding-them` - defaults arrive from four places (primitive, parent layout, HTML element, JSX). A re-stated default is a pinned copy of a value the primitive owns, so it drifts silently when the primitive changes.
* `flex-column-children-stretch-by-default` - `w-full` is a no-op; `self-start` is the opt-out. Parent `items-start` "works" and lands the regression on the *siblings*, which is why it gets misdiagnosed.
* `curated-docs-beat-call-sites-when-learning-an-api` - copying the nearest call site launders an inverted convention into new code, and each copy strengthens the wrong precedent. Concrete case: `<FieldGroup><FieldSet>` reversed at `nps-survey.client.tsx:114`.
* `poll-external-jobs-with-capped-backoff-sized-to-the-worst-case` - `attempts × interval` is an unstated timeout; when the provider legitimately runs long the job reports failure, so the fix gets attempted at the wrong layer.
* `cap-externally-generated-files-before-ingesting-them` - without a stated cap the ceiling is discovered as an OOM, which reads as an infrastructure fault rather than an oversized input.
* `no-forwardref-in-react-19` - `ref` is an ordinary prop now. Worth stating explicitly because every pre-19 example on the internet will reproduce the wrapper by default.
* `type-children-as-propswithchildren` - keeps a hand-written `children:` type meaningful as a signal that children are deliberately narrowed. Two zamp authors independently, which is weaker than two repos.
* `ts-pattern-match-over-nested-ternaries-for-status-dispatch` - `.exhaustive()` converts "someone added a variant" into a compile error; the ternary chain's trailing fallback renders a plausible empty state instead. Carries a dependency, so the stack choice may want splitting from the practice.
* `named-local-functions-over-iifes-for-derived-values` - an IIFE inverts reading order: the body becomes mandatory reading before the assignment makes sense.
* `one-throwable-per-try-catch-when-side-effects-are-mixed` - an observability argument. A wide catch collapses storage, queue, and constraint failures into one Sentry group, destroying the one answer an incident needs.
* `try-catch-extraction-is-a-commitment-not-a-one-off` - the mixed form is worse than either consistent alternative; shows up when an incremental refactor extracts only the step it was already touching.
* `use-client-is-a-js-boundary-marker-not-an-interactivity-marker` - the wrong mental model pushes the boundary upward, and a scaffolded `onClick={() => {}}` commits a whole subtree to the client for nothing.
* `dont-test-your-frameworks-guarantees` - these tests are actively negative: they fail on harmless renames, which triggers wholesale test deletion. The positive half (realtime payload contracts, deliberate error-swallows) is the more useful half.
* `split-polymorphic-components-when-the-discriminator-is-structural` - a `Pattern`, deliberately opt-in. Records the shape-vs-value test, because applied indiscriminately it produces component sprawl.

*Proposed `project: zamp` (1):*

* `orchestrator-cleanup-belongs-in-onfailure` - a correctness bug, not a style choice: an outer catch fires before Inngest's retries, marking a record `FAILED` that then succeeds on retry. Also pins the `event.data.event.data` envelope trap. May be better merged into the existing `inngest-background-conventions` concept than promoted separately.
