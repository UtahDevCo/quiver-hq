---
type: Workflow
title: Rank the documents before building from them
description: A 265-line knowledge base, the newest and clearest file in the folder, described a transaction the executed contract forbids. Write the authority ranking into the repo as step one.
tags: [requirements, research, provenance, corroboration]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/workflows/corroboration-requires-independent-sources.md }
sources:
  - id: kb
    resource: "Google Doc — Knowledge Base: Trikin Capital (1g7eHnsk…), modified 2026-07-29"
    title: "\"Trikin Capital advances agents a portion of their earned apartment-locating commission\" — 265 lines of clear prose, most recently edited source"
    last_modified: 2026-07-29
  - id: bma
    resource: "Broker Master Commission Purchase Program Agreement §3.6-3.7, §13.3"
    title: "Purchaser pays the Broker, who pays the Agent; Purchaser may not compensate an Agent for brokerage services"
    last_modified: 2026-07-30
  - id: charter
    resource: projects/trikin/docs/trikin-capital/model.md
    title: "the resulting ranked source list, five documents deep, with the marketing doc explicitly marked non-governing"
    last_modified: 2026-07-30
not:
  - term: "treating the clearest or most recently edited document as the spec"
    why: "prose quality and recency track how much someone wanted to explain the idea, not which document the organisation is bound by"
    instead: "write the authority ranking into the repo's own charter before designing, and cite the governing clause at each decision"
  - term: "noting elsewhere that a document is superseded"
    why: "the next reader opens the folder, not your note"
    instead: "put a deprecation header at the top of the non-governing file itself"
---

# The workflow

Handed a folder of source documents for a new product, rank them by authority and
write that ranking into the repo before designing anything. Cite the governing clause
at each decision that turns on it, and mark the non-governing documents as
non-governing inside the documents themselves.

Two heuristics that held up:

- **Prefer the document someone signed.** An agreement with signature blocks, defined
  terms, and a governing-law clause outranks any summary of it.
- **The conflict is where the constraint lives.** Diffing the two documents located
  the invariants faster than reading either one alone.

# What it cost when skipped

Two documents described the same transaction incompatibly. A 265-line knowledge base,
well written and the most recently modified file in the folder, said the company
*advances agents* their commission. The executed contract said the company *buys the
receivable from the brokerage and pays the brokerage*, and separately that it may not
pay an agent at all.

The knowledge base was the more inviting spec by every surface signal: newer, longer,
plainer, organised around the reader. Built as written, it produces an
unlicensed-compensation violation.

Nothing in a folder listing tells you which document binds. Filesystem metadata ranks
by recency and prose ranks by effort, and the correlation with authority often runs
backwards, since the binding document is drafted by lawyers optimising for
enforceability while the summary is written by whoever most wanted the idea understood.
The correction is cheap and one-time; skipping it compounds through every schema and UI
decision downstream and is hard to unwind once the data model encodes the wrong
transaction.

# Relation to corroboration

[corroboration-requires-independent-sources](corroboration-requires-independent-sources.md)
covers sources that agree, where the question is whether the agreement is real. This is
the adjacent case: two sources conflict, and the resolution is authority rather than
counting.

# Evidence

The knowledge base, in bold, as its own summary of the business: "**Trikin Capital
advances agents a portion of their earned apartment-locating commission after the
move-in is verified.**"

BMA §13.3: "Purchaser is not acting as a real estate broker and shall not pay
compensation directly to any Agent for the performance of Brokerage Services."

Both statements are about the same money, and one of them is the deal.
