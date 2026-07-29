---
type: Observation
title: Prompt caching is automatic on most vendors — which is why nobody can prove it is working
description: OpenAI and Gemini 2.5 cache prompts with no opt-in, so there is no code to review and no flag to find. `usage.cachedInputTokens` is the only evidence the discount is real; discard it and an assumed saving becomes indistinguishable from none.
kind: failure-mode
proposed_layer: meta
tags: [llm, cost, telemetry, caching, observability]
generated: { by: claude/opus-5, at: 2026-07-29T22:54:15Z }
status: draft
not:
  - term: "adding explicit `cache_control` breakpoints to 'turn caching on'"
    why: "on OpenAI and Gemini 2.5 it is already on; on Anthropic a write costs 1.25x and pays back only if the same prefix is re-sent to the SAME model inside the TTL"
    instead: "establish whether the prefix actually repeats per model first, then measure — caches are model-scoped, not request-scoped"
  - term: "caching the system prompt because it is the obviously stable part"
    why: "below the model's minimum cacheable prefix nothing caches and no error is raised — Anthropic's floor is 2048 tokens on several models, and system prompts are routinely under 1500"
    instead: "measure the prefix in tokens before placing a breakpoint; verify with the cache-read counter, not by inspection"
  - term: "fanning one large shared bundle out to N models and expecting the cache to amortise it"
    why: "each model has its own cache, so N distinct models means N cold prefixes — the reuse is zero however stable the bundle is"
    instead: "expect amortisation only across repeat calls to one model, e.g. successive turns of one conversation"
sources:
  - id: evidence
    resource: projects/k1/web/packages/ai/src/sdk-transport.ts
    title: "sdk-transport.ts — recorded inputTokens/outputTokens but discarded usage.cachedInputTokens"
    last_modified: 2026-07-29
  - id: vendor
    resource: https://developers.openai.com/api/docs/guides/prompt-caching
    title: 'OpenAI — "Prompt Caching works automatically for eligible requests, with no code changes required" (>=1024 tokens)'
    last_modified: 2026-07-29
  - id: vendor
    resource: https://ai.google.dev/gemini-api/docs/caching
    title: 'Gemini — "Implicit caching is enabled by default for all Gemini 2.5 and newer models" (>=2048 tokens)'
    last_modified: 2026-07-29
---

# Observation

Two of the three major vendors cache prompts with **no opt-in**:

| Vendor | Caching | Minimum prefix |
|---|---|---|
| OpenAI | automatic, no code change possible | 1024 tokens |
| Gemini 2.5+ | implicit, enabled by default | 2048 tokens |
| Anthropic | explicit `cache_control` only | 2048 tokens on several models |

Because there is no parameter, there is nothing in the diff, nothing to grep, and
no flag to find — so "are we getting the caching discount?" cannot be answered by
reading the code. It can only be answered by recording the counter the vendor
already returns. In the Vercel AI SDK that is one vendor-neutral field,
`usage.cachedInputTokens`, which normalises Anthropic's `cache_read_input_tokens`,
OpenAI's `cached_tokens` and Gemini's `cachedContentTokenCount`.

Discard it and you have an *assumed* discount. Assumed discounts get quoted in cost
models, and they are indistinguishable from no discount at all.

# Why it matters

It makes cost work unfalsifiable in both directions, and the wrong direction is the
expensive one.

Asked to reduce LLM spend in k1, the obvious-looking recommendation was "add prompt
caching to the multi-vendor panel." Three facts, none visible without checking,
killed it: two vendors already cache; the panel's system prompts are all **under**
the minimum cacheable prefix so a breakpoint there would have silently done nothing;
and caches are **model-scoped**, so fanning one bundle across N distinct models has
zero reuse by construction — a cache write at 1.25x that is never read is a pure
loss. The recommendation would have added cost while appearing to reduce it, and
nothing in the codebase would have contradicted it.

Same root cause as [[a-request-parameter-you-set-may-never-reach-the-wire]]: the
SDK reports something and the transport throws it away. Cost and correctness both
degrade silently when vendor telemetry is dropped at the boundary.

# Evidence

`generateText` in `ai@6.0.199` — probed rather than assumed, with a mocked model
reporting a 40-token cache read:

```
usage = {
  "inputTokens": 100,
  "inputTokenDetails": { "noCacheTokens": 60, "cacheReadTokens": 40, "cacheWriteTokens": 0 },
  "outputTokens": 7,
  "totalTokens": 107,
  "cachedInputTokens": 40
}
```

The provider mappings, from source (both fold cached tokens into the input total, so
`cachedInputTokens` is a subset of `inputTokens`):

```js
// @ai-sdk/anthropic@3.0.86
cacheRead: cacheReadTokens          // <- usage.cache_read_input_tokens
// @ai-sdk/google@3.0.83
cacheRead: cachedContentTokens      // <- usage.cachedContentTokenCount
```

Economics worth carrying: a cache **write** costs ~1.25x (5-minute TTL) or ~2x
(1-hour), reads ~0.1x. So a 5-minute-TTL prefix breaks even on the second read and a
1-hour prefix on the third — which is why "does this exact prefix repeat, on this
exact model, inside the TTL" is the question to answer before writing any caching
code, and why the answer needs a counter rather than an argument.
