---
type: Observation
title: Local auth-override spoof is dead on any deployed Cloudflare Worker (NODE_ENV=production gate)
kind: failure-mode
proposed_layer: project
observed_in: trikin
proposed_project: trikin
generated: { by: claude/demo-infra, at: 2026-09-22T14:14:00Z }
status: draft
sources:
  - id: evidence
    resource: web/src/lib/auth.tsx:278
---

# Observation

Local auth-override spoof is dead on any deployed Cloudflare Worker (NODE_ENV=production gate)

Surfaced by lane `demo-infra` during a Solo orchestration run.

# Evidence

web/src/lib/auth.tsx:278

# Review notes

Pushed from a child agent with minimal context. Verify against the
evidence before promoting.
