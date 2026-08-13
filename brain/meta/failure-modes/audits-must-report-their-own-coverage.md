---
type: Failure Mode
title: An audit that silently skips what it cannot read reports a falsely reassuring zero
description: Print attempted, inspected, and skipped-by-reason. "Zero findings", "zero findings among what I could read", and "zero candidates to look at" are three different claims, and only the first one stops the investigation.
tags: [auditing, observability, error-handling, scripts]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
  - { by: human:christopher, at: 2026-07-31T20:18:38Z }
status: stable
stale_after: 2027-07-31
not:
  - term: "`const x = await fetch(id).catch(() => null); if (x === null) continue;`"
    why: "converts \"couldn't check\" into \"checked, fine\" at every call site, and the summary count then reads as complete"
    instead: "tally the skip with its reason, and print effective coverage alongside the finding count"
  - term: "reporting `Found 0 divergences` from a scan that had unreadable items"
    why: "a clean report is exactly what makes someone close the investigation"
    instead: "`0 findings among 966/1058 readable (91%) — this is a floor, not a total`"
  - term: "a verification loop that prints PASS having iterated an empty candidate set"
    why: "no item failed because no item was examined; the verdict is true and carries no information"
    instead: "print `audited=N` beside the verdict, and when N is 0 say the run was vacuous and name what would give it real samples"
  - term: "explaining a zero-candidate run by the population being small that day"
    why: "a wrong field name produces the same zero on every day, and the per-day story is more available than the bug, so it ends the investigation; `p.skipReason` matched 0 of 2472 documents because the writer records the reason in `error`"
    instead: "run the predicate against the whole collection with no date bound and exit non-zero when it matches nothing there either"
  - term: "trusting an audit's own coverage count when it reads through a shared client helper"
    why: "a helper that catches 401 and returns an empty list reports full coverage from a call site with no error handling in it; 289 readable / 0 unreadable against a true 288 / 1"
    instead: "check that the reader can report a failure at all, or read the endpoint directly in the audit"
  - term: "auditing only your own datastore when two systems can diverge"
    why: "damage in the system you don't control is invisible by construction, especially if failed writes roll your side back"
    instead: "audit the side you don't own; that is where the divergence lives"
sources:
  - id: wiley-postfix-vacuous-pass
    resource: projects/wiley/web/scripts/verify-daily-billing-postfix.ts
    title: wiley — post-deploy check printed PASS with 0 candidates to audit, 2026-07-31
    author: claude/opus-5
    last_modified: 2026-07-31
  - id: wiley-quiet-hours-sweep
    resource: projects/wiley
    title: wiley — NetSapiens quiet-hours fleet sweep over 1058 accounts, 2026-07-29
    author: claude/opus-5
    last_modified: 2026-07-29
  - id: wiley-skipreason-fix
    resource: projects/wiley/web/scripts/verify-daily-billing-postfix.ts
    title: "wiley f4e5ba6 — the predicate read a field nothing writes, and had matched 0 of 2472 documents"
    author: claude/opus-5
    last_modified: 2026-08-04
  - id: wiley-skip-writer
    resource: projects/wiley/web/functions/src/daily-billing.ts
    title: wiley skipPeriodForPromo — writes the reason into `error`, not `skipReason`
    last_modified: 2026-07-30
  - id: wiley-tolerant-helper
    resource: projects/wiley
    title: wiley — audit-quiet-hours-rule-order read 401 as an empty list, 289/0 against a true 288/1
    author: claude/opus-5
    last_modified: 2026-08-12
---

# The trap

A fleet sweep over 1058 accounts printed **"0 accounts with divergence."** The
scan loop was:

```ts
const tfs = await ns.getTimeframes(domain).catch(() => null);
if (tfs === null) continue;   // unreadable looks identical to clean
```

92 domains were returning `401 Invalid Scope` and being skipped silently. Adding
coverage accounting turned the same run into **24 divergent accounts, 8 customers
unable to receive any calls.**

The defect is structural, not a typo. `.catch(() => null)` plus `continue` is the
natural way to write a resilient scanner, and it launders "couldn't check" into
"checked, fine" at every call site.

# What to do instead

- Print **attempted, successfully inspected, skipped by reason**, and an explicit
  effective-coverage figure.
- State the epistemic status in the output itself: *"N findings among M readable —
  this is a floor, not a total."*
- List a few skipped items so the gap is investigable rather than abstract.
- Then actually close the gap. Here, checking the 92 showed all returned 404 from
  `getDomain` — not provisioned upstream at all — which legitimately reduced the
  floor to the total. That conclusion required a second script, not an assumption.

# The empty candidate set

The same falsely reassuring zero arrives by a second route, with no error handling
involved at all. A check that filters a population down to the interesting cases,
then loops, reports success when the filter matches nothing:

```ts
const freeSkips = periods.filter((p) => p.skipReason === "PROMO_FREE_MONTH");
let violations = 0;
for (const p of freeSkips) { /* ... */ }
console.log(violations === 0 ? "PASS" : "FAIL");   // PASS when freeSkips is []
```

A script written to confirm a deployed billing fix ran the morning after and
printed `PASS`.

> The first version of this section, carrying both `verified` entries above,
> explained that zero by the day's billing pass having produced 8 periods and none
> of the governed type: *"Nothing was unreadable and nothing was swallowed. The
> loop simply had no work."* That diagnosis was wrong, and the correction below has
> not been human-verified.

The loop had no work on **every** date. `skipReason` is written nowhere in the
repository. `skipPeriodForPromo` records the reason in a field called `error`, so
the filter matched 0 of 2472 documents on every day it had ever run. Reading the
real field finds 755 comped months, 373 of them past the boundary the fix governs.
The script had been named in a commit message as the verification that a production
billing fix held, and it reported PASS for four days across a remediation that wrote
to 140 production subscriptions.

What went wrong in the reasoning is worth as much as the field name. A small
population that day is a plausible, self-contained explanation for a zero, and it is
more available than "the predicate has never matched anything," so it ended the
investigation one step early.

The guard is a control assertion over the whole collection, with no date bound and
its own exit code:

```ts
if (totalComped === 0) {
  console.error("ABORT — the predicate matched nothing in the entire collection.");
  process.exit(2);   // not 0, and not the code a real violation uses
}
```

A per-run `audited=0` is necessary and not sufficient, because it invites a per-run
explanation. The collection-wide count is what separates *nothing happened today*
from *this script has never seen a row*.

Two habits follow. Count `unevaluated` separately from pass and fail, because a
candidate that could not be judged is neither. And when a post-deploy check comes
back vacuous, name the date or condition that will give it real samples, so the run
schedules its own replacement instead of closing the question. In the same session
a second property was unfalsifiable for a different reason: the corrected signup
grant could not be checked at all, because nobody had signed up since the deploy.

# A predicate that never matched has untested verdict logic behind it

Repairing the selector is half the fix. The code that decides pass from fail sat
behind a filter that matched nothing, so it had never executed on real input, and it
was also wrong: it flagged legitimate intro-window and promo-entitled comps. Both
defects had to be found before the checker discriminated, which a control run is
what proves:

```
--date=2026-07-30 (pre-deploy)  -> 7 violations, exit 1
    and the same run passes 1 intro-window and 1 promo-entitled comp that day
--date=2026-08-01                -> PASS, exit 0
```

Treat a selector fix as exposing new code rather than as completing the repair.

# A tolerant helper is a third route to the same zero

A shared client helper that catches an auth error and returns an empty list produces
the identical clean report, at a call site with no visible error handling. A fleet
audit built on one read 289 accounts as readable and 0 as unreadable. Reading the
endpoints directly found 288 readable and 1 unreadable. The swallow was in the
helper, one layer below the audit, where the audit's own coverage accounting could
not see it.

When an audit reports full coverage, check that the reader it calls can report a
failure at all.

# The two-system corollary

When two systems can diverge, audit the one you don't control. A Firestore-only
audit could not see the broken accounts *by construction*, because the failed
saves rolled Firestore back — leaving your own datastore in the state you'd
expect while the upstream one was wrong.

Closely related: [verify-a-write-actually-happened](verify-a-write-actually-happened.md),
which is how the divergence got created in the first place.
