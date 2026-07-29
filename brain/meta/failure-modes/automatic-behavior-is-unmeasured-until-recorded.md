---
type: Failure Mode
title: An automatic optimization is unmeasured until you record its counter
description: Prompt caching is on by default on most vendors, so there is no flag to grep and no diff to review. The vendor's own counter is the only evidence the discount is real — discard it and an assumed saving is indistinguishable from none.
tags: [llm, cost, telemetry, caching, observability]
generated: { by: claude/opus-5, at: 2026-07-29T22:54:15Z }
verified:
  - { by: human:christopher, at: 2026-07-29T23:10:47Z }
status: stable
stale_after: 2027-01-29
relations:
  - { kind: instance-of, target: /meta/failure-modes/request-parameters-may-not-reach-the-wire.md }
not:
  - term: "adding explicit cache_control breakpoints to \"turn caching on\""
    why: "on OpenAI and Gemini 2.5 it is already on; on Anthropic a write costs ~1.25x and pays back only if the same prefix is re-sent to the SAME model inside the TTL"
    instead: "establish whether the prefix actually repeats per model, then measure — caches are model-scoped, not request-scoped"
  - term: "caching the system prompt because it is the obviously stable part"
    why: "below the model's minimum cacheable prefix nothing caches and no error is raised — the floor is 1024-2048 tokens and system prompts are routinely under 1500"
    instead: "measure the prefix in tokens before placing a breakpoint, and verify with the cache-read counter rather than by inspection"
  - term: "fanning one large shared bundle out to N models and expecting the cache to amortise it"
    why: "each model has its own cache, so N distinct models means N cold prefixes — reuse is zero however stable the bundle is"
    instead: "expect amortisation only across repeat calls to one model, e.g. successive turns of one conversation"
sources:
  - id: k1-transport
    resource: projects/k1/web/packages/ai/src/sdk-transport.ts
    title: "k1 — recorded inputTokens/outputTokens but discarded usage.cachedInputTokens"
    last_modified: 2026-07-29
  - id: vendor-openai
    resource: https://developers.openai.com/api/docs/guides/prompt-caching
    title: 'OpenAI — "works automatically for eligible requests, with no code changes required" (>=1024 tokens)'
    last_modified: 2026-07-29
  - id: vendor-gemini
    resource: https://ai.google.dev/gemini-api/docs/caching
    title: 'Gemini — "Implicit caching is enabled by default for all Gemini 2.5 and newer models" (>=2048 tokens)'
    last_modified: 2026-07-29
---

# The trap

Two of the three major vendors cache prompts with **no opt-in**:

| Vendor | Caching | Minimum prefix |
|---|---|---|
| OpenAI | automatic, no code change possible | 1024 tokens |
| Gemini 2.5+ | implicit, enabled by default | 2048 tokens |
| Anthropic | explicit `cache_control` only | 2048 tokens on several models |

Because there is no parameter, there is nothing in the diff, nothing to grep, and no
flag to find. *"Are we getting the caching discount?"* cannot be answered by reading the
code — only by recording the counter the vendor already returns. In the Vercel AI SDK
that is one vendor-neutral field, `usage.cachedInputTokens`, normalising Anthropic's
`cache_read_input_tokens`, OpenAI's `cached_tokens`, and Gemini's
`cachedContentTokenCount`.

Discard it and you have an **assumed** discount. Assumed discounts get quoted in cost
models, and they are indistinguishable from no discount at all.

# Why it matters

It makes cost work unfalsifiable in both directions, and the wrong direction is the
expensive one.

Asked to reduce LLM spend in k1, the obvious recommendation was "add prompt caching to
the multi-vendor panel." Three facts, none visible without checking, killed it: two
vendors already cache; the panel's system prompts are all **under** the minimum cacheable
prefix, so a breakpoint there would have silently done nothing; and caches are
**model-scoped**, so fanning one bundle across N distinct models has zero reuse by
construction — a cache write at 1.25x that is never read is a pure loss.

**The recommendation would have added cost while appearing to reduce it, and nothing in
the codebase would have contradicted it.**

# The economics worth carrying

A cache **write** costs ~1.25x (5-minute TTL) or ~2x (1-hour); reads ~0.1x. So a
5-minute prefix breaks even on the second read, a 1-hour prefix on the third. Which is
why *"does this exact prefix repeat, on this exact model, inside the TTL"* is the question
to answer before writing any caching code — and why the answer needs a counter rather
than an argument.

# The general shape

Same root cause as
[request-parameters-may-not-reach-the-wire](request-parameters-may-not-reach-the-wire.md):
the SDK reports something and the transport throws it away at the boundary. Cost and
correctness both degrade silently when vendor telemetry is dropped.

Generalises to any automatic optimization you are billed for or depend on — CDN and HTTP
caching, query plan caches, connection pooling, compression negotiation. If it happens
without your code asking, then your code cannot be read to find out whether it happened.

# Freshness

`stale_after` is **six months**, not the usual year for a failure mode. The token
minimums, the multipliers, and the "which vendors are automatic" table are live vendor
pricing and will drift. The structural lesson outlives them; re-check the numbers before
quoting them.
