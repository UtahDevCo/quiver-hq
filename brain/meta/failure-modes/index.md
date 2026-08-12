# failure-modes

Things that look right and are not. Each of these was paid for in production.

* [verify-a-write-actually-happened](verify-a-write-actually-happened.md) - A catch that maps an error to success reports writes that never landed. Read the state back and assert on the field you wrote.
* [audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md) - An audit that silently skips what it cannot read reports a falsely reassuring zero, and so does one with no candidates. Print attempted, inspected, and skipped-by-reason.
* [probe-before-trusting-an-api-claim](probe-before-trusting-an-api-claim.md) - A comment asserting a third-party API limitation is a hypothesis, not a fact. Probe it before extending the workaround.
* [self-reported-confidence-is-not-a-signal](self-reported-confidence-is-not-a-signal.md) - LLM-reported confidence tracks prose register, not correctness. Don't display it, don't route on it.
* [a-listing-endpoint-is-not-the-uniqueness-domain](a-listing-endpoint-is-not-the-uniqueness-domain.md) - The set a create checks for conflicts is often wider than what list returns, and `if (!found) create()` then retries a doomed write forever.
* [a-dead-control-may-be-a-duplicate](a-dead-control-may-be-a-duplicate.md) - A setting whose value never reaches the backend may be a redundant second writer. Grep the field before wiring it up.
* [request-parameters-may-not-reach-the-wire](request-parameters-may-not-reach-the-wire.md) - Vendor SDKs drop unsupported settings, return 200, and say so only in `result.warnings`.
* [automatic-behavior-is-unmeasured-until-recorded](automatic-behavior-is-unmeasured-until-recorded.md) - An optimization that happens without your code asking cannot be verified by reading your code. Record the vendor's counter.
* [fixing-the-write-path-does-not-fix-the-written-rows](fixing-the-write-path-does-not-fix-the-written-rows.md) - Correcting a write path stops new bad rows and nothing else. The field is still read, so the defect keeps firing from stored data after the fix ships.
* [a-capability-probe-needs-a-positive-control](a-capability-probe-needs-a-positive-control.md) - Seed a distinctive value and prove it landed, or "it is gone" and "it was never there" are the same reading and the probe certifies a limitation it never demonstrated.
* [probe-inputs-must-make-outcomes-distinguishable](probe-inputs-must-make-outcomes-distinguishable.md) - An input already in the state you requested makes no-op, append and replace produce identical bytes. Ask which other behaviours would have produced this reading.
* [measure-the-noise-floor-before-ranking-two-prompts](measure-the-noise-floor-before-ranking-two-prompts.md) - A single-sample benchmark cannot return "no difference". Two identical runs at temperature 0 read 2.7, 4.7 and 11.3 points apart, so the floor is not a constant either.
* [a-measurement-must-use-the-input-container-production-uses](a-measurement-must-use-the-input-container-production-uses.md) - The declared MIME type and container are part of the input. Bare PNGs read 48% where the same rasters inside a PDF read 92.9%, and production accepts only PDFs.
* [a-generator-cannot-produce-the-failure-it-has-no-state-for](a-generator-cannot-produce-the-failure-it-has-no-state-for.md) - A field the generator always populates is unmeasured when blank, not passing. 99.8% synthetic against 83.3% on real documents, and every error was the state the generator cannot emit.
