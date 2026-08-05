---
type: Observation
title: Fixing a checker's selector exposes verdict logic that has never run
description: A filter matching zero rows means the branch deciding pass from fail was never executed either. Repairing the selector is half the fix; the verdict needs its own control before you trust the next green run.
kind: failure-mode
proposed_layer: meta
tags: [auditing, verification, scripts, testing]
generated: { by: claude/opus-5, at: 2026-08-04T20:45:03Z }
status: draft
not:
  - term: "shipping the field-name correction and trusting the next PASS"
    why: "the verdict branch has zero executions behind it; the first real data may be judged by logic that was never right"
    instead: "after repairing the selector, run it against a period when the defect was known live and require a FAIL with a non-zero exit"
  - term: "treating every post-boundary comp as a violation"
    why: "a promo month is post-boundary by design, so a correct production day with promo comps reports FAIL and the alert gets dismissed"
    instead: "check entitlement before calling it a violation, and report intro-window, entitled, and violating counts separately"
sources:
  - id: wiley-verdict-defect
    resource: projects/wiley/web/scripts/verify-daily-billing-postfix.ts
    title: "wiley f4e5ba6 — second defect surfaced only once the selector was fixed"
    author: claude/opus-5
    last_modified: 2026-08-04
---

# Observation

A checker whose filter matched zero rows for its whole life also never executed the
code that decides pass from fail. Repairing the field name made it see 755 rows and
immediately exposed a second, independent defect in the verdict.

The PASS condition was *every comped month is inside the intro-free window*. But the
counter legitimately comps promo months, which fall **after** the intro boundary by
design. With the selector fixed and nothing else changed, the script reported FAIL on
2026-08-01 and 2026-08-04, both of which were correct production days: one promo-backed
comp each.

Two bugs in opposite directions. The selector made it impossible to fail; the verdict
made it certain to fail wrongly once it could see data. Neither was observable while
the other was present.

# Why it matters

The natural repair is a one-token change, and the natural next step is to run it and
accept the green result. Here that would have produced false alarms on the first two
real days, and a false alarm on a billing monitor gets the monitor muted.

Generalisation: an assertion's verdict branch has as many executions behind it as the
selector has matched rows. Zero matched rows means zero executions, so the verdict is
untested code that merely looks reviewed. Repairing a selector converts untested code
into live code in one step, with no intervening signal.

# Evidence

Corrected verdict, which separates the three outcomes rather than collapsing two of
them into a violation:

```ts
if (isIntroFreeBillingPeriod(sub, scheduled)) { intro++; continue; }

const promoMonths = promoCode ? (promoMonthsByCode.get(promoCode) ?? 0) : 0;
const postBoundary = (skipsByUser.get(uid) ?? [])
  .filter((d) => !isIntroFreeBillingPeriod(sub, d)).sort();
if (postBoundary.indexOf(scheduled) < promoMonths) { entitled++; continue; }

violations++;
```

Output after the fix, showing the discrimination the original verdict could not make:

```
--date=2026-08-04  audited=1  intro-window=0  promo-entitled=1  violations=0  -> PASS
--date=2026-07-30  audited=9  intro-window=1  promo-entitled=1  violations=7  -> FAIL
```

The 2026-07-30 run is the control: the defect was live that morning, the seven failures
are each a period comped exactly on its boundary with `promo=(none)`, and the same run
correctly passes the two legitimate comps that day. A checker that only ever returns
one verdict has not been shown to work, whichever verdict it is.
