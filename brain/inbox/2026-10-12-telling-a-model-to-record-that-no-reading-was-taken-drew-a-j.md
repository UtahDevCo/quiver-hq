---
type: Observation
title: Telling a model to 'record that no reading was taken' drew a JSON null in a required string field, failing a strict parser for the whole entity; say the literal text to write
kind: failure-mode
proposed_layer: project
generated: { by: claude/opus-5.5, at: 2026-10-12T23:47:03Z }
status: draft
sources:
  - id: evidence
    resource: web/packages/ai/src/waterfall-terms-extraction.ts (prompt v3 -> v4, commit 634b5a2)
---

# Observation

Telling a model to 'record that no reading was taken' drew a JSON null in a required string field, failing a strict parser for the whole entity; say the literal text to write

Surfaced by lane `terms-extractor` during a Solo orchestration run.

# Evidence

web/packages/ai/src/waterfall-terms-extraction.ts (prompt v3 -> v4, commit 634b5a2)

# Review notes

Pushed from a child agent with minimal context. Verify against the
evidence before promoting.
