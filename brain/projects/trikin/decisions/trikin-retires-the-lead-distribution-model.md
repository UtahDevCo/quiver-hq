---
type: Decision
title: trikin retires the lead-distribution business and is repurposed for commission receivables
description: The leads domain was deleted rather than migrated and its data dropped without a snapshot, on Chris's instruction. Records what those tables and integrations were so old commits stay readable.
tags: [decision, pivot, architecture, history]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
not:
  - term: "reading docs/archive/*-DEPRECATED.md as requirements"
    why: "it is detailed and confident and describes a business that no longer exists; both files carry a header saying so"
    instead: "docs/trikin-capital/model.md, which carries the replacement model and its ranked source documents"
  - term: "reusing the 15%/50% split or the trikinCommission / propertyCommission vocabulary"
    why: "those were revenue sharing on a lead sale; the new business buys a receivable at a discount, so the numbers and the names produce nonsense"
    instead: "the purchase-price and discount vocabulary of the receivables model"
  - term: "the words lead, partner, market, and the pre-pivot sense of deal stage"
    why: "retired vocabulary that no longer maps onto any table"
    instead: "transaction, broker, payor, and a deal stage that is derived rather than stored"
sources:
  - id: charter
    resource: projects/trikin/docs/trikin-capital/model.md
    title: "the replacement business model, with its ranked source documents"
  - id: archived
    resource: projects/trikin/docs/archive/knowledge-base-leads-DEPRECATED.md
    title: "the retired model's own knowledge base, kept with a deprecation header"
---

# The decision

As of 2026-07-30, `projects/trikin` no longer implements lead distribution. The app
shell is kept (Next.js 15 on Cloudflare Workers, D1 plus Drizzle, NextAuth 5 magic
links, shadcn/ui, Resend, the audit log) and the domain is replaced with commission
receivables purchasing.

Deleted rather than migrated: the `leads`, `atlas_*`, `market_settings`,
`lead_sync_runs`, and `lead_sync_events` tables; the HighLevel, Zoho, Snowflake, and
HubSpot integrations; the seven broker-specific sync integrations (Rivo, Oakland
Creek, Dwelling Collection, Apt Locator, Apt Locater, Promove, Apartment Source); the
Atlas and Rentberry property-manager pulls; and the admin leads, markets, and
data-sync surfaces. Legacy data was dropped without a snapshot, on Chris's explicit
instruction, because the business failed and the data has no residual value.

# What the old model was

Property managers ("providers") sent overflow rental inquiries from condo listings to
Trikin, which routed them to apartment-locating firms ("closers") under capacity and
market filters. On a close, revenue split roughly 15% to Trikin and 50% to the
providing property manager. The `leads` table carried both the lead payload and the
commission accounting, which is why it had 60-odd columns.

This is recorded so that pre-pivot commits remain legible.

# Why it matters

Three traps for a future session are listed in `not:` above: the archived knowledge
base reads like requirements, the old commission split shares vocabulary with the new
one and shares nothing else, and the pre-pivot nouns still appear throughout git
history.

# Evidence

`git log` before the pivot branch is entirely lead-distribution work: "Improve lead
sync reporting", "prevent retry pipeline from overwriting successful broker
assignments", "Standardizing markets". That history is worth keeping readable, which
is the reason this file exists rather than the code being deleted quietly.

# No stale_after

A decision is a historical fact, per the freshness table in
[conventions](../../../conventions.md).
