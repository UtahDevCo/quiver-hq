---
type: Observation
title: k1-2026 Firebase auth emails send from the default firebaseapp.com sender because the toposmodel.com custom email domain was configured but never verified (customDomainState NOT_STARTED), which is the likely reason sign-in links land in spam
kind: failure-mode
proposed_layer: project
generated: { by: claude/opus-5.5, at: 2026-10-12T23:44:44Z }
status: draft
sources:
  - id: evidence
    resource: identitytoolkit admin v2 projects/k1-2026/config notification.sendEmail.dnsInfo, read 2026-10-12; docs/auth-password-2fa-passkeys.md section 5
---

# Observation

k1-2026 Firebase auth emails send from the default firebaseapp.com sender because the toposmodel.com custom email domain was configured but never verified (customDomainState NOT_STARTED), which is the likely reason sign-in links land in spam

Surfaced by lane `login-2fa` during a Solo orchestration run.

# Evidence

identitytoolkit admin v2 projects/k1-2026/config notification.sendEmail.dnsInfo, read 2026-10-12; docs/auth-password-2fa-passkeys.md section 5

# Review notes

Pushed from a child agent with minimal context. Verify against the
evidence before promoting.
