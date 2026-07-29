# failure-modes

Things that look right and are not. Each of these was paid for in production.

* [verify-a-write-actually-happened](verify-a-write-actually-happened.md) - A catch that maps an error to success reports writes that never landed. Read the state back and assert on the field you wrote.
* [audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md) - An audit that silently skips what it cannot read reports a falsely reassuring zero. Print attempted, inspected, and skipped-by-reason.
* [probe-before-trusting-an-api-claim](probe-before-trusting-an-api-claim.md) - A comment asserting a third-party API limitation is a hypothesis, not a fact. Probe it before extending the workaround.
* [self-reported-confidence-is-not-a-signal](self-reported-confidence-is-not-a-signal.md) - LLM-reported confidence tracks prose register, not correctness. Don't display it, don't route on it.
