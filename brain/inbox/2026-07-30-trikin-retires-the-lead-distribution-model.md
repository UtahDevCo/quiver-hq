---
type: Observation
title: trikin's lead-distribution business is retired; the repo is being repurposed for commission receivables
description: The leads domain was deleted rather than migrated and its data dropped without a snapshot, on Chris's instruction. Records what those tables and integrations were so old commits stay readable.
kind: decision
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [decision, pivot, architecture, history]
status: draft
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: charter, resource: projects/trikin/docs/trikin-capital/model.md, title: "the replacement business model, with its ranked source documents" }
  - { id: archived, resource: projects/trikin/docs/archive/knowledge-base-leads-DEPRECATED.md, title: "the retired model's own knowledge base, kept with a deprecation header" }
---

# Observation

As of 2026-07-30, `projects/trikin` no longer implements lead distribution. The app
shell is kept — Next.js 15 on Cloudflare Workers, D1 + Drizzle, NextAuth 5 magic
links, shadcn/ui, Resend, the audit log — and the domain is replaced with commission
receivables purchasing.

Deleted rather than migrated: the `leads`, `atlas_*`, `market_settings`,
`lead_sync_runs`, and `lead_sync_events` tables; the HighLevel, Zoho, Snowflake, and
HubSpot integrations; the seven broker-specific sync integrations (Rivo, Oakland
Creek, Dwelling Collection, Apt Locator, Apt Locater, Promove, Apartment Source);
the Atlas and Rentberry property-manager pulls; and the admin leads, markets, and
data-sync surfaces. Legacy data was dropped without a snapshot, on Chris's explicit
instruction — the business failed and the data has no residual value.

What the old model *was*, so that pre-pivot commits remain legible: property managers
("providers") sent overflow rental inquiries from condo listings to Trikin, which
routed them to apartment-locating firms ("closers") under capacity and market
filters. On a close, revenue split roughly 15% to Trikin and 50% to the providing
property manager. The `leads` table carried both the lead payload and the commission
accounting, which is why it had 60-odd columns.

# Why it matters

Three concrete traps for a future session:

- **`docs/archive/*-DEPRECATED.md` is not requirements.** It is detailed, confident,
  and describes a business that no longer exists. Both files carry a header saying so.
- **The old commission split has nothing to do with the new one.** 15%/50% was
  revenue sharing on a lead sale. The new business buys a receivable at a discount.
  Reusing the numbers or the `trikinCommission` / `propertyCommission` vocabulary
  produces nonsense.
- **The word "lead" and the pre-pivot sense of "deal stage", "partner", and "market"
  are retired vocabulary.** The replacements are transaction, broker, payor, and a
  derived deal stage that is computed rather than stored.

Recorded as a decision rather than a practice because it is a historical fact and
carries no `stale_after` — per `brain/conventions.md`, decisions do not expire.

# Evidence

`git log` before the pivot branch is entirely lead-distribution work — "Improve lead
sync reporting", "prevent retry pipeline from overwriting successful broker
assignments", "Standardizing markets". That history is worth keeping readable, which
is the reason this file exists rather than just deleting the code quietly.
