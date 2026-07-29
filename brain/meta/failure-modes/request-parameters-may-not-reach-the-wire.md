---
type: Failure Mode
title: A request parameter you set is a claim about intent, not about the wire
description: Vendor SDKs silently discard unsupported settings and report it only in `result.warnings`. `temperature: 0` in your source can be false at the wire, with HTTP 200 and no failing test.
tags: [third-party-apis, llm, telemetry, verification, determinism]
generated: { by: claude/opus-5, at: 2026-07-29T22:54:15Z }
verified:
  - { by: human:christopher, at: 2026-07-29T23:10:47Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: conflicts-with, target: /meta/failure-modes/probe-before-trusting-an-api-claim.md }
not:
  - term: "assuming an unsupported parameter causes a 4xx you would notice"
    why: "the provider strips the setting and continues with a 200; nothing fails loudly"
    instead: "read `result.warnings` and surface the dropped feature names on your own result type"
  - term: "a build-time test asserting the request body contains the parameter"
    why: "it pins behaviour for the hard-coded model ids in the test only — the model is chosen at runtime, and that one may differ"
    instead: "report the drop per call, so the model production actually selected is the one you have evidence about"
  - term: "encoding the intent in the type, e.g. `temperature: 0` as a literal field"
    why: "a literal type reads as a guarantee while remaining a request the vendor may ignore"
    instead: "name it `requestedTemperature`, and carry what was actually honoured alongside it"
sources:
  - id: k1-transport
    resource: projects/k1/web/packages/ai/src/sdk-transport.ts
    title: "k1 — temperature: 0 sent unconditionally for all three vendors"
    last_modified: 2026-07-29
  - id: k1-test
    resource: projects/k1/web/packages/ai/src/__tests__/openai-transport.test.ts
    title: 'k1 — test at :211 pinning "temperature 0 is DROPPED for a reasoning model"'
    last_modified: 2026-07-29
  - id: vendor-openai
    resource: "@ai-sdk/openai@3.0.74"
    title: 'provider source — if (isReasoningModel) { baseArgs.temperature = void 0; warnings.push({type:"unsupported", feature:"temperature"}) }'
    last_modified: 2026-07-29
---

# The trap

Setting a request parameter records what you **asked for**. It is not evidence the
vendor honoured it. Provider SDKs routinely drop settings a model does not accept,
return HTTP 200, and mention it **only** in `result.warnings`.

```js
// @ai-sdk/openai@3.0.74
if (isReasoningModel) {
  if (baseArgs.temperature != null) {
    baseArgs.temperature = void 0;
    warnings.push({ type: "unsupported", feature: "temperature", details: "..." });
  }
}
```

- `@ai-sdk/openai` drops `temperature` for **every** reasoning model — the whole
  `gpt-5.x` family and the o-series.
- `@ai-sdk/anthropic` drops sampling parameters for models whose capabilities carry
  `rejectsSamplingParameters`, and drops `temperature` whenever thinking is enabled.

So `temperature: 0` in your source can be false at the wire while every test that
inspects the request body still passes — because those tests pin hard-coded model ids
and the model is chosen at runtime.

# Why it matters

The consequence is not a crash. It is a **silently invalid comparison.**

In k1 an adversarial panel runs N vendors over one frozen evidence bundle and routes on
where they disagree. Two members answer at temperature 0; the OpenAI member — the
configured default — answers at 1. That is a difference in the *measurement*, sitting
inside an instrument whose only output is a comparison, available to be read as a
difference between the models.

A panel is the worst possible host for this bug, because disagreement is the signal. Added
nondeterminism doesn't look like a defect. It looks like a finding. Compare
[self-reported-confidence-is-not-a-signal](self-reported-confidence-is-not-a-signal.md),
which is the same class of problem one layer up.

# What to do instead

Stop discarding the SDK's own telemetry. Map the `type: "unsupported"` warnings — each
carries the dropped `feature` name — onto your result type, so the drop is visible for
whatever model was actually selected.

```ts
// SharedV3Warning, @ai-sdk/provider — only the first means "we threw your setting away"
| { type: 'unsupported';   feature: string; details?: string }
| { type: 'compatibility'; feature: string; details?: string }   // degraded, not dropped
| { type: 'other';         message: string }                     // no feature name
```

# The general shape

This is the **inverse** of
[probe-before-trusting-an-api-claim](probe-before-trusting-an-api-claim.md): there, a
claimed limitation was not evidence the limitation existed. Here, an **absent error** is
not evidence the request was honoured. Both are the same discipline — the vendor's
behaviour is a measurement, not an assumption.

It generalises past LLM work to any request-shaping parameter a middle layer may quietly
normalise away: retry counts, timeouts, consistency levels, isolation levels, compression
settings.

Note also where the knowledge already lived in k1 — pinned in a test and reasoned through
in a PRD — and still did not help, because it wasn't in the **runtime output of a run**.
A fact recorded only in a document does not defend the system.
