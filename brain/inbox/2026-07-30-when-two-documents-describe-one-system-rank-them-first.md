---
type: Observation
title: When two documents describe the same system, establish which one governs before building
description: A marketing summary and an executed contract described the same product differently; the summary was clearer, more recent, and wrong. Rank the sources as step one, in writing.
kind: workflow
proposed_layer: meta
observed_in: trikin
tags: [requirements, research, provenance, corroboration]
status: draft
not:
  - term: "treating the clearest or most recently edited document as the spec"
    why: "prose quality and recency track how much someone wanted to explain the idea, not which document the organisation is bound by"
    instead: "write the authority ranking into the repo's own charter before designing, and cite the governing clause at each decision"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: kb, resource: "Google Doc — Knowledge Base: Trikin Capital (1g7eHnsk…), modified 2026-07-29", title: "\"Trikin Capital advances agents a portion of their earned apartment-locating commission\" — 265 lines of clear prose, most recently edited source" }
  - { id: bma, resource: "Broker Master Commission Purchase Program Agreement §3.6-3.7, §13.3", title: "Purchaser pays the Broker, who pays the Agent; Purchaser may not compensate an Agent for brokerage services" }
  - { id: charter, resource: projects/trikin/docs/trikin-capital/model.md, title: "the resulting ranked source list, five documents deep, with the marketing doc explicitly marked non-governing" }
---

# Observation

Handed a folder of source documents for a new product, I found two that described
the same transaction incompatibly. A 265-line knowledge base, well written and the
most recently modified file in the folder, said the company *advances agents* their
commission. The executed contract said the company *buys the receivable from the
brokerage and pays the brokerage*, and separately that it may not pay an agent at
all.

The knowledge base was the more inviting spec by every surface signal: newer,
longer, plainer, organised around the reader. It was also the one that, if built,
would have produced an unlicensed-compensation violation.

The workflow: before designing anything, write an explicit authority ranking into
the repo, and cite the governing clause at each decision that turns on it. Mark the
non-governing documents as non-governing *in the documents themselves* — a
deprecation header at the top of the file, not a note elsewhere.

# Why it matters

The failure is not "we read the wrong document". It is that nothing in a folder
listing tells you which document binds. Filesystem metadata ranks by recency,
prose ranks by effort, and neither correlates with authority — often inversely,
since the binding document is drafted by lawyers optimising for enforceability and
the summary is written by whoever most wanted the idea understood.

The correction is cheap and one-time; the cost of skipping it compounds through
every schema and UI decision downstream, and it is very hard to unwind once the
data model has encoded the wrong transaction.

Two heuristics that held up here:

- **Prefer the document someone signed.** An agreement with signature blocks,
  defined terms, and a governing-law clause outranks any summary of it.
- **The conflict is the interesting part.** Where the two disagreed was exactly
  where the legal constraint lived, so diffing them located the invariants faster
  than reading either one alone.

Related: [[corroboration-requires-independent-sources]] — that workflow says two
sources corroborate only if independent. This is the adjacent case: two sources
*conflict*, and the resolution is authority rather than counting.

# Evidence

The knowledge base, in bold, as its own summary of the business: "**Trikin Capital
advances agents a portion of their earned apartment-locating commission after the
move-in is verified.**"

BMA §13.3: "Purchaser is not acting as a real estate broker and shall not pay
compensation directly to any Agent for the performance of Brokerage Services."

Both statements are about the same money. Only one of them is the deal.
