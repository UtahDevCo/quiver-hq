# failure-modes

Things that look right and are not. Each of these was paid for in production.

## Writes, migrations and stored data

* [verify-a-write-actually-happened](verify-a-write-actually-happened.md) - "Not found" and "not addressable this way" both arrive as 404. Read the state back and assert on the field you wrote — a silent no-op is strictly worse than a crash.
* [fixing-the-write-path-does-not-fix-the-written-rows](fixing-the-write-path-does-not-fix-the-written-rows.md) - Correcting a write path stops new bad rows and nothing else. If the field is still read on a path that decides behaviour, the defect keeps firing from stored data after the fix ships and the losses are recovered.
* [a-recompute-backfill-fabricates-where-the-value-was-null](a-recompute-backfill-fabricates-where-the-value-was-null.md) - Of 27 rows a dry run offered, 17 were the real repair and 10 stored null and recomputed to an empty tax form claiming the current year, because the deriving function answers even with nothing to read.
* [a-half-mapped-field-pair-hides-until-a-delta-needs-it](a-half-mapped-field-pair-hides-until-a-delta-needs-it.md) - A normalizer mapped the ending column and never the beginning. 172 of 174 documents carried it in the raw extraction and 0 of 174 in the normalized store, and the first consumer that subtracted them read the gap as a deemed contribution.
* [a-listing-endpoint-is-not-the-uniqueness-domain](a-listing-endpoint-is-not-the-uniqueness-domain.md) - The set a create checks for conflicts is often wider than what the matching list returns. "GET says it isn't there" does not mean you can create it — and `if (!found) create()` then retries a doomed write forever.

## Checks that pass without checking

* [audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md) - Print attempted, inspected, and skipped-by-reason. "Zero findings", "zero findings among what I could read", and "zero candidates to look at" are three different claims, and only the first one stops the investigation.
* [duplicated-predicates-rot-in-the-code-nobody-runs](duplicated-predicates-rot-in-the-code-nobody-runs.md) - Six copies of one filter. The three in audit and verification scripts read a field written nowhere; the three on paths with users were right, because users correct runtime code and nothing corrects a monitor.
* [a-well-formed-rule-may-never-be-reached](a-well-formed-rule-may-never-be-reached.md) - An audit passed 281 of 289 accounts on four per-rule checks. Three of the passes were wrong, because a catch-all rule at a lower ordinal took every call before the correct rule ran.
* [a-page-of-a-listing-is-not-the-population](a-page-of-a-listing-is-not-the-population.md) - pageSize=40 hid a live deploy, pageSize=200 returned 100 of 272 rollouts, and pageSize=300 returned 8 of 12 Firestore documents because one had grown to 880 KiB. Only nextPageToken tells you the page was partial.
* [an-eventually-consistent-field-answers-confidently-wrong](an-eventually-consistent-field-answers-confidently-wrong.md) - A probe read is-active seconds after staging and reported the opposite of the truth. Read again at t+160s the answer flipped, and nothing in either response said the field had not settled.
* [caching-the-read-behind-a-check-defeats-the-check](caching-the-read-behind-a-check-defeats-the-check.md) - A one-hour cache on an exposure query leaves the cap in place and comparing against an hour-old number, so every request inside the window passes a limit that should admit one.

## Probing someone else's system

* [probe-before-trusting-an-api-claim](probe-before-trusting-an-api-claim.md) - "The API doesn't support X" gets load-bearing fast. Probe it before extending the workaround — and commit the probe, including the ones that falsified your own guess.
* [a-capability-probe-needs-a-positive-control](a-capability-probe-needs-a-positive-control.md) - Without seeding a value and proving it landed, "the thing is gone" and "the thing was never there" are the same reading, and the probe certifies a limitation it never demonstrated.
* [probe-inputs-must-make-outcomes-distinguishable](probe-inputs-must-make-outcomes-distinguishable.md) - A probe whose input is already in the target state collapses two behaviours into one observation, and "no effect" gets read as the stronger of the two.
* [request-parameters-may-not-reach-the-wire](request-parameters-may-not-reach-the-wire.md) - Vendor SDKs silently discard unsupported settings and report it only in `result.warnings`. `temperature: 0` in your source can be false at the wire, with HTTP 200 and no failing test.
* [automatic-behavior-is-unmeasured-until-recorded](automatic-behavior-is-unmeasured-until-recorded.md) - Prompt caching is on by default on most vendors, so there is no flag to grep and no diff to review. The vendor's own counter is the only evidence the discount is real — discard it and an assumed saving is indistinguishable from none.
* [a-dead-control-may-be-a-duplicate](a-dead-control-may-be-a-duplicate.md) - A setting whose value never reaches the backend might be a redundant second writer, not missing plumbing. Grep the backend field before wiring it up — connecting it ships a behaviour change to everyone whose two values disagree.

## Measuring a model

* [measure-the-noise-floor-before-ranking-two-prompts](measure-the-noise-floor-before-ranking-two-prompts.md) - Comparing two prompts, models, or configs on one sample each produces a difference every time, and without a repeat run at fixed settings there is nothing to say whether that difference is larger than the measurement itself.
* [a-model-cannot-be-its-own-control](a-model-cannot-be-its-own-control.md) - A transcript the model wrote about its own read agreed with the wrong figure 25 times out of 25, and four repeats of one config dropped the same boxes on 9 of 17 documents.
* [score-through-the-shipping-accessor](score-through-the-shipping-accessor.md) - An eval harness read the model output more permissively than production, crediting 53 codes across 9 of 175 documents that the pipeline dropped, and reporting 95.5% where the shipping accessor gave 93.4%.
* [a-diff-only-diagnostic-hides-shared-failure](a-diff-only-diagnostic-hides-shared-failure.md) - A script that printed only where two extraction arms disagreed said "no verdict differences" on a document that scored 40% on four consecutive repeats.
* [a-local-override-measures-a-model-you-do-not-ship](a-local-override-measures-a-model-you-do-not-ship.md) - .env.local pinned an older model id than production, so a judge-reliability run scored gemini-2.5-flash at 3 invalid outputs in 18 runs while the shipped gemini-3.6-flash had 0 in 13.
* [a-debugging-read-can-consume-a-blind-measurement](a-debugging-read-can-consume-a-blind-measurement.md) - A polling probe that scraped the result card would have revealed the verdict for every queued case before the human labeller opened one, and the labels would still have been recorded as blind.
* [self-reported-confidence-is-not-a-signal](self-reported-confidence-is-not-a-signal.md) - LLM-reported confidence tracks prose register, not correctness. Measured — identical correct conclusions reported 80/15/45%; two runs of one model both said 80% and one was wrong.
* [a-generator-cannot-produce-the-failure-it-has-no-state-for](a-generator-cannot-produce-the-failure-it-has-no-state-for.md) - If the generator always populates a field, extraction can never be scored on what it does when the field is blank, and the rate reads perfect on the one case that matters.
* [a-per-record-check-cannot-see-a-consistently-wrong-rule](a-per-record-check-cannot-see-a-consistently-wrong-rule.md) - 175 of 175 synthetic K-1s passed 12 internal checks while the corpus disagreed with its own partnership return by 305,247 dollars on one partnership-year.
* [a-measurement-must-use-the-input-container-production-uses](a-measurement-must-use-the-input-container-production-uses.md) - Sending bare PNGs to a model that production only ever feeds PDFs produced a 45-point accuracy collapse that does not exist in the product, and it pointed at building a pipeline stage to fix it.
* [two-readers-of-one-record-disagree-about-what-exists](two-readers-of-one-record-disagree-about-what-exists.md) - The matrix UI displayed Box L while the model reported it absent, because the bundle builder read normalizedK1.boxes and Box L lives on normalizedK1.recipient; a grep returned two readers and that count was the diagnosis.

## Documents, config and tooling

* [a-clean-text-layer-can-render-as-an-illegible-page](a-clean-text-layer-can-render-as-an-illegible-page.md) - Two PDF text operators drawn 26.5pt into each other extract as separate intact strings and render as one smear. Box 18 scored 0 of 132 while structurally identical boxes scored 83 to 95 percent.
* [a-missing-runtime-secret-ships-an-inert-feature](a-missing-runtime-secret-ships-an-inert-feature.md) - A feature that falls back by design, plus a config file the platform never reads, produces a green deploy and a passing smoke test with nothing switched on.
* [git-commit-commits-the-index-not-the-paths-you-named](git-commit-commits-the-index-not-the-paths-you-named.md) - A one-file commit landed two files, because another session had already staged a deletion. The squash merge carried it to main and left package.json pointing at a script that no longer existed.
* [a-mutate-then-restore-harness-must-be-crash-safe](a-mutate-then-restore-harness-must-be-crash-safe.md) - Piping a mutation-testing loop through `head -3` sends SIGPIPE between the mutate and the restore, committing a deliberate bug to the working tree while the harness prints KILLED for everything it finished.
