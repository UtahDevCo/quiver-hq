---
type: Failure Mode
title: Fixing the code that wrote a bad field does not fix the rows already holding it
description: Correcting a write path stops new bad rows and nothing else. If the field is still read on a path that decides behaviour, the defect keeps firing from stored data after the fix ships and the losses are recovered.
tags: [remediation, data-migration, incident-response, billing, observability]
generated: { by: claude/opus-5, at: 2026-07-31T18:57:54Z }
verified:
  - { by: human:christopher, at: 2026-07-31T20:18:38Z }
status: stable
stale_after: 2027-07-31
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
not:
  - term: "fix deployed + past losses recovered = incident closed"
    why: "both claims look backward. Neither one examines the rows the broken code wrote that are still being read on a live path."
    instead: "enumerate the rows the old write path produced, evaluate each against the corrected rule, and treat that sweep as a third task with its own verification"
  - term: "reordering the checks so the correct rule wins"
    why: "a correct rule that returns false falls through to whatever runs next, which is often the buggy check you were routing around"
    instead: "trace what executes when the corrected condition is false, for a row carrying the bad value"
  - term: "recovering the money already lost, and calling that the remediation"
    why: "recovery is about periods already past; residue is about periods not yet reached. Different rows, different direction in time, both real."
    instead: "size them separately — recovered so far, and still exposed going forward"
sources:
  - id: wiley-ordering
    resource: projects/wiley/web/functions/src/daily-billing.ts
    title: wiley — boundary check ends line 585, stale-counter check begins line 588
    author: claude/opus-5
    last_modified: 2026-07-31
  - id: wiley-grant-site
    resource: projects/wiley/web/app/actions/billing.ts
    title: wiley — signup grant, freeMonthsRemaining set to 0 at line 1026 after the fix
    author: claude/opus-5
    last_modified: 2026-07-30
  - id: wiley-cleanup
    resource: projects/wiley/web/scripts/billing-clear-free-month-residue.ts
    title: wiley — commit 34ff7ec, the separate sweep the code fix did not cover
    author: claude/opus-5
    last_modified: 2026-07-31
---

# The trap

A billing defect comped a second free month for almost every customer. The fix
shipped: the signup path stopped writing `freeMonthsRemaining: 1`, and the correct
boundary rule was reordered ahead of the counter that had been shadowing it. Then
208 customers were charged for the months already missed, $2,614 recovered, every
invoice checked for a transaction id. Deployment verified two ways.

140 active subscriptions were still carrying `freeMonthsRemaining: 1`, written by
the old grant path before it was corrected. The two checks sit adjacent:

```ts
      // boundary path: period is inside the intro window, skip it
      continue;
    }

    if (sub.freeMonthsRemaining && sub.freeMonthsRemaining > 0) {   // line 588
      await skipPeriodForPromo({ ..., decrementFreeMonth: true });
```

Past the boundary the first test is simply **false**, so control falls straight to
the second one, and the stale counter comps the first payable charge exactly as
the original bug did. $1,619.54 still exposed, 9 subscriptions leaking on their
next billing period, 11 crossing their boundary the following morning.

Reordering the checks fixed a real bug: the intro window had been *spending* promo
months. It could not fix this one, because the shadowed path was never the problem
for a row that had already been written.

# Why it survives a careful fix

Both of the things that felt like completion were backward-looking. The code fix
governs rows written from now on. The recovery collects money already lost. Neither
one asks what the broken code left sitting in the database, and both produce
satisfying numbers that read as closure.

Closing out a defect that persists state is three tasks:

1. Fix the code that writes the field.
2. Recover the losses already incurred.
3. Sweep the rows the broken code wrote and correct them against the new rule.

Task 3 is the one that goes missing. The question that surfaces it: **what did the
broken code leave behind, and is it still read?**

# What to do instead

- Before declaring a stateful defect closed, query the population the old write
  path produced and evaluate each row against the corrected rule. This is a
  separate deliverable from the code fix, with its own verification.
- Derive the correct value rather than assuming it. Here entitlement was
  `promoFreeMonths` minus comps already delivered *on or after* the boundary,
  because a comp before the boundary is the standard free month and must not draw
  down a promo allowance. Getting that subtraction backwards produced two
  miscounts earlier in the same investigation.
- Extract the rule into one module the audit and the cleanup both import. Three
  divergent copies of the boundary rule are what created this defect; a fourth
  copy living in the remediation script would have carried it forward.
- Write the corrected value, not zero. A customer mid-way through a genuine
  multi-month promo keeps what they are owed, so the sweep sets the entitled
  remainder. In this run all 140 happened to be `1 → 0`, which is knowable only
  after computing it.
- Guard the sweep like a money move: expected count and total asserted against
  live data, a named approver recorded per row, and a transaction that re-reads
  the field and aborts that row if it moved. The daily job decrements the same
  counter, so a blind write would have overwritten a concurrent decrement.
- Read the state back afterward and assert on the field you wrote, per
  [verify-a-write-actually-happened](verify-a-write-actually-happened.md). 140 of
  140 counters and 140 of 140 audit-log entries were confirmed by a second script
  that read from the results file rather than trusting the writer's own tally.
- Report what you deliberately left alone. Eleven inactive subscriptions could not
  leak a charge and were deferred behind a flag; two had no billing anchor, so
  entitlement was unknowable and the script named them and refused to guess.

# How the residue gets found

By auditing stored values against the corrected rule, which makes this concept
depend on [audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md):
the sweep must distinguish rows it corrected, rows it deliberately skipped, and
rows it could not evaluate. Folding the third group into either of the first two
is what turns an incomplete cleanup into a reported-complete one.
