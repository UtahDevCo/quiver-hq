---
type: Observation
title: An assertion with no samples is not a pass
description: A check that iterates an empty set prints PASS while proving nothing. Report the sample count next to the verdict, and say when it is zero.
kind: failure-mode
proposed_layer: meta
observed_in: wiley
tags: [testing, verification, monitoring, incident-response]
generated: { by: claude/opus-5, at: 2026-07-31T18:57:54Z }
status: draft
sources:
  - id: vacuous-run
    resource: projects/wiley/web/scripts/verify-daily-billing-postfix.ts
    title: "post-deploy check, 0 PROMO_FREE_MONTH skips available to audit on 2026-07-31"
    last_modified: 2026-07-31
not:
  - term: "PASS — no violations found"
    why: "indistinguishable from 'nothing was examined'. The reader assumes coverage the run never had."
    instead: "audited=N unevaluated=M violations=0, and when N is 0 say the assertion was vacuous and name the date it will actually be exercised"
---

# Observation

A verification loop over an empty candidate set reports success. The verdict is
technically true and carries no information, because the property was never
tested against anything.

Any check that filters a population down to the interesting cases must print the
size of that filtered set beside the verdict, and must say so plainly when the
size is zero. Add the corollary for post-deploy checks: name the date or
condition under which the check will first have real samples, so a vacuous run
schedules its own replacement instead of closing the question.

This is the zero-sample sibling of
[audits-must-report-their-own-coverage](../meta/failure-modes/audits-must-report-their-own-coverage.md).
That one covers candidates skipped by a swallowed error. This one covers a
candidate set that was legitimately empty.

# Why it matters

After deploying a billing fix to wiley, the check that was supposed to confirm
the fix held ran the morning after and printed PASS. It had examined nothing:
that day's billing pass produced 8 periods, 2 of which were manual retries from
the previous run, and **0** of the skip type the fix governs.

Reported as a pass, it would have closed out the verification. The deployed
ordering was not exercised until the following day, when 11 subscriptions crossed
the boundary that the fix controls. A whole day of believing the fix was
confirmed, on the strength of an empty loop.

Separately, in the same session, the grant half of the fix could not be verified
at all, because no customer had signed up since the deploy. Two distinct
unfalsifiable-here results, both of which read as green.

# Evidence

The run, reported honestly:

```
billing_periods scheduled 2026-07-31: 8
     7  COMPLETED
     1  SKIPPED

PROMO_FREE_MONTH skips to audit: 0

audited=0  unevaluated=0  violations=0
PASS — no PROMO_FREE_MONTH skip on 2026-07-31 comped a payable period.
```

The `audited=0` line is what makes the PASS legible. Without it the last line
stands alone and is actively misleading.

The shape that produces this:

```ts
const freeSkips = periods.filter((p) => p.skipReason === "PROMO_FREE_MONTH");
let violations = 0;
for (const p of freeSkips) { /* ... */ }
console.log(violations === 0 ? "PASS" : "FAIL");   // PASS when freeSkips is []
```

Counting `unevaluated` separately matters too: a candidate that could not be
judged (missing anchor, missing parent document) is neither a pass nor a
violation, and folding it into either one overstates what was checked.
