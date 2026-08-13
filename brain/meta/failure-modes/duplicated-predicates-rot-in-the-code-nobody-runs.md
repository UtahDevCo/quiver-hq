---
type: Failure Mode
title: When a predicate is duplicated, the stale copies collect in the code nothing exercises
description: Six copies of one filter. The three in audit and verification scripts read a field written nowhere; the three on paths with users were right, because users correct runtime code and nothing corrects a monitor.
tags: [duplication, auditing, scripts, refactoring]
generated: { by: claude/opus-5, at: 2026-08-04T20:45:03Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
not:
  - term: "auditing the runtime copies of a rule and assuming the monitoring copies match"
    why: "the runtime copies are corrected by user-visible breakage; the monitoring copies have no such pressure and silently diverge"
    instead: "when consolidating, check the monitoring and audit copies first, because that is where the wrong ones are"
  - term: "leaving a correct local copy in place because it currently agrees"
    why: "it agrees today and nothing enforces that it keeps agreeing; this codebase had already paid for the same duplication once"
    instead: "import the predicate from the module that owns the write, and delete the local copy"
sources:
  - id: wiley-six-copies
    resource: projects/wiley/web/lib/billing/free-month-residue.ts
    title: "wiley f4e5ba6 — predicate consolidated after 3 of 6 copies were found wrong"
    author: claude/opus-5
    last_modified: 2026-08-04
  - id: wiley-prior-divergence
    resource: projects/wiley/web/lib/billing/intro-free.ts
    title: "wiley cf16e56 — the same codebase's boundary rule had already diverged across three copies"
    last_modified: 2026-07-30
---

# The trap

One predicate, *was this billing period comped as a free month*, existed in six
places. Three were correct and three were wrong, and the split was not random:

| Correct, reading `error` | Wrong, reading `skipReason` |
|---|---|
| `billing-charge-queue.ts` | `verify-daily-billing-postfix.ts` |
| `billing-remediation-export.ts` | `audit-residual-free-months.ts` |
| `reconcile-billing-card-anchor.ts` | `billing-clear-free-month-residue.ts` |

The three wrong ones are the post-deploy verification, the residue audit, and the
cleanup that writes production. All three produce a number a human reads and then
stops looking. The three correct ones feed charge queues and remediation exports,
where a wrong number surfaces as a missing or wrong charge someone notices.

# Why it goes the direction it goes

The intuition when consolidating duplicated logic is to treat the runtime path as
suspect and the tooling as incidental. It is the reverse. Runtime copies sit under
constant correction from users. A monitoring copy that reads a nonexistent field
reports zero, which looks like good news, and nothing pushes back.

This codebase had already paid for the same class of defect. `cf16e56` consolidated
the adjacent intro-free boundary rule after it diverged across three hand-maintained
copies, one of which compared `<=` where the others compared `<` and actively created
over-grants. That consolidation moved the boundary rule into a shared module and left
the skip predicate duplicated, so the next divergence landed in the copies that had
just been left alone.

# Evidence

The correct shape, present in three scripts independently:

```ts
const skippedFor = (reason: string) =>
  periods.filter((p) => p.status === "SKIPPED" && p.error === reason);
```

The wrong shape, present in the other three:

```ts
if (p.skipReason !== "PROMO_FREE_MONTH") return;   // field written nowhere
```

Consolidated into the module that already owned the entitlement arithmetic these
scripts share, so the audit and the cleanup cannot disagree by construction:

```ts
export function isPromoFreeMonthSkip(period: SkippedPeriod): boolean {
  return period.status === "SKIPPED" && period.error === PROMO_FREE_MONTH;
}
```

Requiring `status === "SKIPPED"` as well as the reason is deliberate. A period
restored after being comped keeps `error` and moves off `SKIPPED`, and it was not
paid for by the counter. All 755 matching documents are currently `SKIPPED` with no
restore, so the two conditions are equivalent today and will not stay that way.

The three correct copies were left in place in `f4e5ba6` and still hold their own
local definitions. A predicate that reads a field written nowhere reports zero
findings from a scan that examined nothing, which is
[audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md)
reached through drift rather than through error handling.
