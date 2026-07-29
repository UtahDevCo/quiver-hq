---
type: Observation
title: A request parameter you set is a claim about intent, not about the wire
description: Vendor SDKs silently DISCARD unsupported settings and report it only in `result.warnings`. `temperature: 0` in your source — even as a literal type — can be false at the wire with no error and no failing test.
kind: failure-mode
proposed_layer: meta
tags: [third-party-apis, llm, telemetry, verification, determinism]
generated: { by: claude/opus-5, at: 2026-07-29T22:54:15Z }
status: draft
not:
  - term: "assuming an unsupported parameter causes a 4xx you would notice"
    why: "both @ai-sdk/openai and @ai-sdk/anthropic strip the setting and continue with a 200; nothing fails loudly"
    instead: "read `result.warnings` and surface the dropped feature names on your own result type"
  - term: "a build-time test asserting the request body omits the parameter"
    why: "it pins the behaviour for the hard-coded model ids in the test only — the model is chosen at runtime by env override, and that one may differ"
    instead: "report the drop per call, so the model production actually selected is the one you have evidence about"
  - term: "encoding the intent in the type, e.g. `temperature: 0` as a literal field"
    why: "a literal type reads as a guarantee while remaining a request the vendor may ignore"
    instead: "name it `requestedTemperature`, and carry what was actually honoured alongside it"
sources:
  - id: evidence
    resource: projects/k1/web/packages/ai/src/sdk-transport.ts
    title: "sdk-transport.ts — `temperature: 0` sent unconditionally for all three vendors"
    last_modified: 2026-07-29
  - id: evidence
    resource: projects/k1/web/packages/ai/src/__tests__/openai-transport.test.ts
    title: 'openai-transport.test.ts:211 — "temperature 0 is sent to a non-reasoning model but DROPPED for a reasoning model"'
    last_modified: 2026-07-29
  - id: vendor
    resource: "@ai-sdk/openai@3.0.74 dist/index.js"
    title: 'provider source — `if (isReasoningModel) { baseArgs.temperature = void 0; warnings.push({type:"unsupported", feature:"temperature"}) }`'
    last_modified: 2026-07-29
---

# Observation

Setting a request parameter records what you *asked for*. It is not evidence the
vendor honoured it. Provider SDKs routinely drop settings a model does not accept,
return HTTP 200, and mention it **only** in `result.warnings`:

- `@ai-sdk/openai` drops `temperature` for **every** reasoning model — the whole
  `gpt-5.x` family and the o-series.
- `@ai-sdk/anthropic` drops sampling parameters for models whose capabilities carry
  `rejectsSamplingParameters`, and drops `temperature` whenever thinking is enabled.

Neither returns an error. So `temperature: 0` in your source can be false at the
wire while every test that inspects the request body still passes — because those
tests pin hard-coded model ids, and the model is usually chosen at runtime.

The fix is to stop discarding the SDK's own telemetry: map the `type: "unsupported"`
warnings (each carries the dropped `feature` name) onto your result type, so the
drop is visible for whatever model was actually selected.

# Why it matters

The consequence is not a crash — it is a **silently invalid comparison**.

In k1 an adversarial model panel runs N vendors over one frozen evidence bundle and
routes on where they disagree. Its Google and Anthropic members answer at
temperature 0; its OpenAI member (`gpt-5.5`, the configured default) answers at 1.
That is a difference in the **measurement** sitting inside an instrument whose only
output is a comparison — available to be read as a difference between the models.
A panel is exactly the kind of system where this is worst, because disagreement is
the signal, so added nondeterminism doesn't look like a bug. It looks like a finding.

Generalises past LLM work: any request-shaping parameter a middle layer may quietly
normalise away — retry counts, timeouts, consistency levels, isolation levels —
has the same shape. Related: [[probe-before-trusting-an-api-claim]] (a comment
asserting a limitation is a hypothesis); this is its inverse — an *absent* error is
also not evidence.

# Evidence

`@ai-sdk/openai@3.0.74`, the Responses model's `getArgs`:

```js
if (isReasoningModel) {
  if (baseArgs.temperature != null) {
    baseArgs.temperature = void 0;
    warnings.push({
      type: "unsupported",
      feature: "temperature",
      details: "temperature is not supported for reasoning models",
    });
  }
}
```

`@ai-sdk/anthropic@3.0.86`:

```js
const { rejectsSamplingParameters } = getModelCapabilities(this.modelId);
if (rejectsSamplingParameters) {
  if (temperature != null) {
    warnings.push({ type: "unsupported", feature: "temperature",
      details: `temperature is not supported by ${this.modelId} and will be ignored` });
    temperature = void 0;
  }
}
```

The warning union worth mapping (`SharedV3Warning`, `@ai-sdk/provider`) — only the
first member means "we threw your setting away":

```ts
| { type: 'unsupported';   feature: string; details?: string }
| { type: 'compatibility'; feature: string; details?: string }   // degraded, not dropped
| { type: 'other';         message: string }                     // no feature name
```

The k1 codebase had already measured this and pinned it in a test, with the
consequence reasoned through in PRD 19 §4.2/§4.7 ("PRD 17 should treat OpenAI as
the noisier member") — the gap was that the knowledge lived in a test and a
document rather than in the runtime output of a run.
