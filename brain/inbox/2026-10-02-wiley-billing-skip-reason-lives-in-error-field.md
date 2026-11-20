---
type: Observation
title: Wiley billing_periods skip reason lives in `error`, not `skipReason`
description: The reason a billing period was skipped (PROMO_FREE_MONTH, VIP_SKIPPED, CREDIT_APPLIED) is written to `error`; there is no `skipReason` field, and audits that read it silently pass over every row.
kind: failure-mode
proposed_layer: project
proposed_project: wiley
tags: [billing, firestore, audit, false-pass, data-quality]
generated: { by: claude/opus-4.8, at: 2026-10-02T16:03:00Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/lib/billing/free-month-residue.ts
    title: free-month-residue.ts comment documenting the skipReason/error miss (lines 23-32)
    last_modified: 2026-10-02
  - id: mechanism
    resource: projects/wiley/web/functions/src/daily-billing.ts
    title: skipPeriodForPromo writes the reason into `error` (reason field ~line 176, 591, 602, 859)
    last_modified: 2026-10-02
---

# Observation

On Wiley's `billing_periods` documents, the reason a cycle was skipped
(`PROMO_FREE_MONTH`, `VIP_SKIPPED`, `CREDIT_APPLIED`) is written into the
`error` field by `skipPeriodForPromo`. There is no `skipReason` field, and
nothing in the codebase writes one. Any audit, census, or probe that classifies
skips must read `error`.

# Why it matters

A prior residue audit, its cleanup, and `verify-daily-billing-postfix.ts` all
read `skipReason`. The field does not exist, so they matched 0 of 2472 periods,
computed `consumed: 0` for every subscription, and `verify-daily-billing-postfix.ts`
reported PASS without evaluating a single skip. A real promo over-grant
($290 of comped months) sat undetected behind a green check. My own first
diagnostic probe (`_probe-john-why-skipped.ts`) read `skipReason`, showed blank
reasons, and led me to briefly misclassify a promo-comped account as a silent
"engine never charges" billing bug — corrected only after reading `error`.

The general trap: a monitor that reads a field name that does not exist returns
empty and reads as a clean PASS. Before trusting a zero/clean audit result,
confirm the field exists and that the query matches a nonzero control set.
Ties to [[checks-that-pass-without-checking]] and
[[probe-a-field-before-depending-on-it]].

# Evidence

`free-month-residue.ts` documents it directly: "Three scripts read `skipReason`
until 2026-08-04 and so matched zero of 2472 documents: the residue audit and
the cleanup computed `consumed: 0` for every subscription, and
verify-daily-billing-postfix.ts reported PASS without evaluating a single skip."

Ground truth from prod (2026-10-02), reading `error`: johnbsullivan's five
unbilled periods all carry `error === "PROMO_FREE_MONTH"`. Reading `skipReason`
on the same documents returns `undefined`, which renders as blank and looks like
an anomalous unexplained skip.

not:
  - term: 'period.skipReason === "PROMO_FREE_MONTH"'
    why: "skipReason does not exist on billing_periods; the predicate is always false and the audit passes over every row"
    instead: 'period.error === "PROMO_FREE_MONTH" (with status === "SKIPPED")'
