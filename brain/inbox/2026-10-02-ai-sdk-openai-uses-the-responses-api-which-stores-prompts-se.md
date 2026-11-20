---
type: Observation
title: @ai-sdk/openai uses the Responses API, which stores prompts server-side unless providerOptions.openai.store=false; k1 panel never sets it
kind: failure-mode
proposed_layer: project
observed_in: k1
proposed_project: k1
generated: { by: claude/opus-5.5, at: 2026-10-02T13:16:38Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/packages/ai/src/openai-transport.ts:100, packages/ai/src/sdk-transport.ts:296
---

# Observation

@ai-sdk/openai uses the Responses API, which stores prompts server-side unless providerOptions.openai.store=false; k1 panel never sets it

Surfaced by lane `topos-privacy-scope` during a Solo orchestration run.

# Evidence

projects/k1/web/packages/ai/src/openai-transport.ts:100, packages/ai/src/sdk-transport.ts:296

# Review notes

Pushed from a child agent with minimal context. Verify against the
evidence before promoting.
