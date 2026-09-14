---
type: Failure Mode
title: Reconstruct the ledger before a backcharge; never derive "owed" from one collection's SKIPPED count
description: Counting every skipped cycle as owed billed comped customers and dead cards; correct owed was a quarter of the naive figure.
kind: failure-mode
tags: [money, billing, backcharge, dunning, firestore, wiley]
generated: { by: claude/opus-4-8, at: 2026-09-10T20:18:22Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: ledger-probe
    resource: projects/wiley/web/scripts/_probe-58-ledger.ts
    title: read-only per-account backcharge ledger that reads the reason field and cross-checks invoices
    last_modified: 2026-09-10
  - id: skip-reasons
    resource: projects/wiley/web/functions/src/daily-billing.ts
    title: processNewCharges writes the skip reason to billing_periods.error (VIP_SKIPPED / CREDIT_APPLIED / PROMO_FREE_MONTH)
    last_modified: 2026-09-10
not:
  - term: "owed = count(billing_periods where status == SKIPPED) * monthlyAmount"
    why: "SKIPPED conflates deliberately-free cycles (credits/promo/intro) and already-attempted card declines with genuinely-unbilled cycles; counting all of them billed comped customers and dead cards"
    instead: "owed = cycles that were NEVER attempted, after netting out every free entitlement and excluding failed-charge periods, cross-checked against the authoritative payment record"
---

# Failure Mode

Before charging customers for "missed" cycles, reconstruct a per-account ledger
from every payment record. Do not derive "owed" from a single derived view such
as a count of skipped billing periods.

The safe method:

1. Cross-check the **authoritative payment record** across every path. In wiley
   that is the `invoices` collection (status is always `PAID`); a `COMPLETED`
   billing period links to it via `invoiceId`. An account with any paid invoice
   has paid, regardless of what the period view suggests.
2. **Net out every free entitlement** using the actual reason, not the status.
   In wiley the reason is `billing_periods.error`, not a `skipReason` field, and
   the free reasons are `VIP_SKIPPED`, `CREDIT_APPLIED`, `PROMO_FREE_MONTH`
   (intro-free first month, promo/Kickstarter free months, VIP, service credits).
3. Count as owed **only cycles that were never attempted** (never scheduled, no
   charge tried). Separate "never charged" (a backcharge candidate) from "charged
   and the card declined" (a dunning problem). A SKIPPED period carrying
   `RECOVERY_CHARGE_FAILED: Expired Card` is the latter: re-charging a dead card
   collects nothing and risks a double-charge.
4. Before charging a card that previously declined, verify it is currently valid.

The stakes are asymmetric: overcharging a real customer is far worse than
under-collecting, so define "owed" conservatively.

# Why it matters

A first pass at wiley counted every `SKIPPED` period as an owed cycle and
reported roughly **$1,159 owed across ~42 accounts**. Reading the reason field,
cross-checking `invoices`, and excluding failed-card attempts brought the real
figure to **$269 owed, ~$35 cleanly collectible today**. The naive list's top
target (jbentleyr, "$69.84") was entirely `CREDIT_APPLIED` and owed nothing;
two others (heather.walner, alison.pippo) were Expired/Closed-card declines.
Acting on the naive number would have billed customers who were deliberately
comped and re-charged dead cards.

# Evidence

- `projects/wiley/web/scripts/_probe-58-ledger.ts` — read-only ledger. For each
  real-line subscription: cross-checks `invoices` (status `PAID`), classifies
  each period by `error` (free reason vs `RECOVERY_CHARGE_FAILED`), and counts
  owed as never-attempted cycles only. Output: 1128 real-line subs, 197 never
  paid anything, but only 18 genuinely owe (24 cycles, $269.16), of which one
  ACTIVE account with no bad-card signal ($34.92) is cleanly collectible.
- Two earlier probes (`_probe-58-census.ts`, `_probe-58-backcharge.ts`) read the
  wrong field (`skipReason`) and counted all SKIPPED as owed; that is the
  overstatement this concept exists to prevent.
