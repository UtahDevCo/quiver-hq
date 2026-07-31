---
type: Observation
title: Fixing the write path does not fix the rows it already wrote
description: A defect that persists state keeps causing harm after the code fix ships, because the bad field is still read on the hot path.
kind: failure-mode
proposed_layer: meta
observed_in: wiley
tags: [remediation, data-migration, billing, incident-response]
generated: { by: claude/opus-5, at: 2026-07-31T18:57:54Z }
status: draft
sources:
  - id: ordering
    resource: projects/wiley/web/functions/src/daily-billing.ts
    title: "boundary check ends line 585, counter check begins line 588"
    last_modified: 2026-07-31
  - id: grant-site
    resource: projects/wiley/web/app/actions/billing.ts
    title: "signup grant, freeMonthsRemaining: 0 at line 1026 after the fix"
    last_modified: 2026-07-30
  - id: cleanup
    resource: projects/wiley/web/scripts/billing-clear-free-month-residue.ts
    title: "commit 34ff7ec, the separate cleanup the code fix did not cover"
    last_modified: 2026-07-31
not:
  - term: "fix deployed + past losses recovered = incident closed"
    why: "both are backward-looking. Neither one examines the rows the broken code wrote that are still being read."
    instead: "enumerate the rows the old write path produced, evaluate each against the corrected rule, and treat that as a third task with its own verification"
---

# Observation

When a defect writes a field that later drives behaviour, correcting the write
path stops new bad rows and nothing else. Every row already written keeps
producing the original harm, because the read path has not changed.

Closing out a stateful defect is three tasks, not one:

1. Fix the code that writes the field.
2. Remediate the losses already incurred.
3. **Sweep the rows the broken code left behind and correct them against the new rule.**

Task 3 is the one that gets dropped, because tasks 1 and 2 both feel like
completion and both produce satisfying numbers. Ask directly: *what did the
broken code leave behind, and is it still read?*

# Why it matters

wiley's billing had an intro-free-month defect that comped a second month for
almost every customer. On 2026-07-30 the fix shipped (signup stopped writing
`freeMonthsRemaining: 1`, and the boundary test was reordered ahead of the
counter test) and $2,614 of missed charges was recovered from 208 customers.
Deployment was verified, the money landed, the incident read as closed.

140 active subscriptions were still carrying `freeMonthsRemaining: 1` written by
the old grant path. The counter is consulted immediately after the boundary test,
so the residue reproduced the defect exactly: once a period passes the anchor+1
boundary `isIntroFreeBillingPeriod` returns false, control falls through to the
next check, and the counter comps the charge and decrements.

$1,619.54 still at risk. 9 subscriptions were leaking on their next billing
period and 11 crossed their boundary at 06:00 UTC the following morning. Found
by auditing the stored counters, roughly twelve hours before the first of them
would have been comped.

The recovery and the cleanup are also not the same work aimed at the same money:
the recovery charged for months already lost, and the residue was about to lose
more.

# Evidence

The two checks, adjacent, in `functions/src/daily-billing.ts`:

```ts
      // ...boundary path ends
      console.log(`[BILLING] Intro free month applied for user ${sub.userId}`);
      processed++;
      continue;
    }

    if (sub.freeMonthsRemaining && sub.freeMonthsRemaining > 0) {   // line 588
      await skipPeriodForPromo({
        userId: sub.userId,
        periodId: docId,
        reason: "PROMO_FREE_MONTH",
        decrementFreeMonth: true,
      });
```

Reordering these two made the intro window stop *spending* a promo month, which
was a real bug. It did not stop a stale counter from comping a payable period,
because past the boundary the first test is simply false.

Audit of stored counters, 2026-07-31:

```
subscriptions carrying freeMonthsRemaining > 0: 173  (2 more had no anchor)
  counter matches entitlement (legitimate promo): 22
  counter EXCEEDS entitlement (residue):         151
LIVE EXPOSURE (active + provisioned): 140 subs, 140 months, $1619.54 pre-tax
  boundary already passed (leaking on next period): 9
  boundary still ahead: 131
```

Entitlement was derived, not assumed: `promoFreeMonths` from the redeemed code,
minus comps already delivered *on or after* the boundary. Pre-boundary skips are
the standard free month and must not draw down a promo allowance. Getting that
subtraction backwards produced two earlier miscounts in the same investigation,
which is why the rule was extracted to a module both the audit and the cleanup
import rather than reimplement.
