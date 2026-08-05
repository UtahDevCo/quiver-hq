---
type: Observation
title: A filter that matches nothing is a broken predicate until you prove the population is empty
description: A monitor keyed on a field name nothing writes returns zero on every run and reads as clean. Assert collection-wide that the predicate matches something, and exit non-zero when it doesn't.
kind: failure-mode
proposed_layer: meta
tags: [auditing, observability, scripts, billing, verification]
generated: { by: claude/opus-5, at: 2026-08-04T20:45:03Z }
status: draft
not:
  - term: "explaining a zero-candidate run by the population being small that day"
    why: "a wrong field name produces the same zero on every day, and the per-day explanation is more plausible than the bug, so it ends the investigation"
    instead: "run the same predicate against the whole collection with no date bound; if it matches nothing there either, the predicate is wrong"
  - term: "`periods.filter((p) => p.skipReason === 'PROMO_FREE_MONTH')`"
    why: "`skipReason` is written nowhere; the writer records the reason in `error`. Matched 0 of 2472 documents"
    instead: "import the predicate from the module that owns the write, and assert it matches > 0 collection-wide before trusting a verdict"
sources:
  - id: wiley-skipreason-fix
    resource: projects/wiley/web/scripts/verify-daily-billing-postfix.ts
    title: "wiley f4e5ba6 — fix(billing): read the field the skip writer actually sets"
    author: claude/opus-5
    last_modified: 2026-08-04
  - id: wiley-skip-writer
    resource: projects/wiley/web/functions/src/daily-billing.ts
    title: wiley skipPeriodForPromo — writes the reason into `error`, not `skipReason`
    last_modified: 2026-07-30
  - id: corrects-existing-concept
    resource: brain/meta/failure-modes/audits-must-report-their-own-coverage.md
    title: existing meta concept whose "empty candidate set" diagnosis this corrects
    last_modified: 2026-07-31
---

# Observation

A checker filtered `billing_periods` on `p.skipReason === "PROMO_FREE_MONTH"`. No
code in the repository writes `skipReason`. The writer, `skipPeriodForPromo`, records
the reason in a field called `error`:

```ts
await periodRef.update({ status: "SKIPPED", error: params.reason, ... });
```

So the filter matched 0 of 2472 documents, on every date, and the script printed
`PASS`. Reading `error` instead finds 755 comped months, 373 of them past the
boundary the fix governs.

The guard is a control assertion against the whole collection, with no date bound
and a distinct exit code:

```ts
const totalComped = [...skipsByUser.values()].reduce((t, d) => t + d.length, 0);
if (totalComped === 0) {
  console.error("ABORT — the predicate matched nothing in the entire collection.");
  process.exit(2);   // not 0, and not the same code as a real violation
}
```

A per-run count of `audited=0` is necessary but not sufficient, because it invites a
per-run explanation. The collection-wide count is what distinguishes *nothing
happened today* from *this script has never seen a row*.

# Why it matters

This script was named in a commit message as the verification that a production
billing fix held. It could not fail. It reported PASS for four days across a real
remediation that wrote to 140 production subscriptions.

Two sibling scripts shared the same wrong field, including the one that writes
production data. Both computed `consumed: 0` for every subscription, which biases
residue downward, so the remediation under-cleared. Recomputing with the real field
left the residue set unchanged at 11 accounts, so nothing was mis-written this time.
That was luck about the direction of the bias, not a property of the design.

# Evidence

The existing meta concept
[audits-must-report-their-own-coverage](../meta/failure-modes/audits-must-report-their-own-coverage.md)
already cites this exact file under "The empty candidate set", and attributes the
empty set to that day's billing pass having produced no skips of the governed type:

> That day's billing pass had produced 8 periods, 2 of them manual retries from the
> previous run, and **0** of the skip type the fix governs. Nothing was unreadable
> and nothing was swallowed. The loop simply had no work.

That diagnosis is wrong, and it carries two `human:christopher` `verified` entries.
The loop had no work on every possible date, because the field does not exist. The
plausible per-day story is what stopped the investigation from reaching the field
name. Promotion should correct that section rather than add a second concept beside
it.

Control that the corrected checker discriminates, run against production:

```
--date=2026-07-30 (pre-deploy)  -> 7 violations, exit 1
    each a period comped exactly ON its boundary, promo=(none), entitledMonths=0
    same run passes 1 intro-window and 1 promo-entitled comp that day
--date=2026-08-01                -> PASS, exit 0
--date=2026-08-04                -> PASS, exit 0
```
