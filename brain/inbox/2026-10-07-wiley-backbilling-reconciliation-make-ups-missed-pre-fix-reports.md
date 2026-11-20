---
type: Observation
title: Wiley make-up charges before 2026-08-07 never reached delivered reports; cross-month isolates true back-billing
description: Until the 2026-08-07 collection-date fix, the partner workbook selected rows by statement date, so every make-up charge (collected on a later day than its cycle) was filed under an already-delivered report date and reached no delivered file. To reconcile, census make-ups as collection-month != statement-month; same-month 1-2 day offsets are timing jitter, not back-billing.
kind: failure-mode
proposed_layer: project
proposed_project: wiley
tags: [billing, reports, reconciliation, altaworx, make-up-charge, false-pass]
generated: { by: claude/opus-4.8, at: 2026-10-07T20:25:36Z }
status: draft
sources:
  - id: mechanism
    resource: projects/wiley/web/lib/billing/report-generator.ts
    title: fetchPeriodsCollectedBetween selects by invoice createdAt (lines 138-171); isMakeUp = collectedDate != scheduledDate (474-497)
    last_modified: 2026-10-07
  - id: fix-commit
    resource: projects/wiley/web (git)
    title: f073b2a "fix(billing): report charges on the day they were collected" (2026-08-07); c33f0fb kept Statement Date on accrual (2026-08-18)
    last_modified: 2026-08-07
  - id: census
    resource: projects/wiley/web/scripts/_probe-backbilling-census.ts
    title: Read-only census joining invoices to billing_periods by invoiceId, bucketing make-ups by collection vs statement month
    last_modified: 2026-10-07
---

# Observation

A make-up charge (a cycle collected on a different day than it was billed:
`RECURRING_RETRY` recovery and `BACKDATED_ADMIN_CHARGE`) always carries a
`scheduledDate` in a prior day. Until 2026-08-07 the partner billing workbook
selected rows by `scheduledDate`, and the daily report for that date was cut and
delivered before the late charge landed. So the charge reached no delivered
report: the money moved, the workbook Altaworx reconciles from never showed it.
Commit f073b2a switched selection to the invoice `createdAt` (collection date),
so a make-up now lands in the current report on its collection day, labelled
"Make-Up Charge" because `collectedDate != scheduledDate`; `scheduledDate` stays
the accrual-basis Statement Date (c33f0fb).

To size back-billing, join `invoices` to `billing_periods` by `invoiceId` and
keep PAID invoices where `collectedDate != statementDate`. Then split on
**collection month vs statement month**: cross-month is true back-billing
(a prior cycle caught up); same-month 1-2 day offsets are nightly-job / UTC
date-boundary jitter and reached their report normally. Conflating the two
inflates the number ~2.5x.

# Why it matters

Prod census 2026-10-07: 1,034 raw make-ups ($13,240.67), but only 415 are
cross-month true back-billing ($5,340.79); the other 619 ($7,899.88) are
same-month jitter (411 of them exactly 1 day). Of the 415, 320 ($4,131.94) were
collected inside the 6/21-7/20 window Altaworx had run, and all 320 predate the
2026-08-07 fix, so they were almost certainly absent from the delivered reports
Altaworx reconciled against. The reconciliation gap is therefore closer to the
full $5,340.79 than to the $1,208.85 collected outside the window. The artifact
that carries all of it is a Partner Reports custom range by collection date
(2026-04-01..today), because post-fix selection places each make-up on its real
collection day. Custom-range reports upload to the `custom/` GCS prefix, which
`getHistoricalReportsAction` does not scan, so they are invisible in the portal
UI and only reachable by direct link or console.

# Evidence

report-generator.ts:143-147 documents the original miss: "a recovery charge
collected on 2026-07-02 for a period scheduled 2026-05-01 was filed under
2026-05-01. The daily file for that date was cut months earlier and is never
regenerated, so the money reached no report at all." The census script reproduces
the split; running it against prod produced the figures above.

not:
  - term: 'count every invoice where collectedDate != scheduledDate as back-billing'
    why: "same-month 1-2 day offsets are nightly-job/UTC jitter that reached their report normally; this inflated 415 true back-billing charges to 1,034"
    instead: 'require collectedMonth != statementMonth to isolate a caught-up prior cycle'
  - term: 'assume a charge inside Altaworx reconciled collection window was reconciled'
    why: "all 320 in-window make-ups predate the 2026-08-07 selection fix, so they were filed under stale statement dates and absent from the delivered files"
    instead: 'regenerate the collection-date range post-fix and reconcile the delta, treating pre-2026-08-07 make-ups as suspect'
