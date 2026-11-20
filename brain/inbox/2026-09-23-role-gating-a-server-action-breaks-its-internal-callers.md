---
type: Observation
title: Role-gating a server action breaks its internal callers
description: Adding a role check to an exported Next.js server action breaks every caller that reused it without that role, including patient actions, webhooks and crons.
kind: failure-mode
proposed_layer: project
proposed_project: therapyanimalhub.com
tags: [nextjs, server-actions, auth, security-hardening]
generated: { by: claude/opus-5.5, at: 2026-09-23T21:40:11Z }
status: draft
sources:
  - id: gate-commit
    resource: projects/therapyanimalhub.com commit 835fce4
    title: "security(slice 2): role-gate provider actions and add redirect layouts"
  - id: fix-reset-workflow
    resource: projects/therapyanimalhub.com commit 3dbcd5f
    title: "fix(patient): stop post-payment dashboard crashing for returning customers"
  - id: fix-webhook
    resource: projects/therapyanimalhub.com commit 9b1883b
    title: "fix(stripe-webhook): stop full refunds 500ing on the admin-gated provider lookup"
  - id: render-logs
    resource: Render logs, service srv-cs6frmbqf0us73ec9v70, 2026-09-12 to 2026-09-23
    title: "Error: Unauthorized, digest 2701482952, on /user/dashboard?payment_intent=..."
not:
  - term: "await requireProviderRole() added at the top of a shared exported action"
    why: "every non-provider caller (patient action, route handler, webhook, cron) now throws, and nothing flags it at build or test time"
    instead: "move the shared logic into a non-'use server' lib module, gate only the public action, and have internal callers use the lib function"
---

# Observation

Adding a role check to an exported server action gates every caller of that function, not just the client. In TAH, security slice 2 added `requireProviderRole()` to the provider action `updateWorkflowState`. The patient action `resetWorkflow` also called it, from the dashboard page Stripe redirects to after payment. The Stripe webhook had the same problem: it called the admin-gated partner action `getUser` to look up provider emails for refund notifications.

Before gating an exported action, grep its callers. Patient actions, route handlers, webhooks and crons have no provider or admin session. Put the shared logic in a lib module without `'use server'` (exporting it from a `'use server'` file makes it a public action) and gate only the public entry point.

# Why it matters

The failures went unnoticed for about a month:

- **Post-payment dashboard.** Every returning customer who paid (anyone with an existing workflow) got the error page. Their workflow was never reset to unscheduled, and each failure texted the on-call phone "TAH error: 2701482952", a digest with no message.
- **Stripe webhook.** Every full refund returned 500 after the charge upsert. The refund emails to support, providers and the customer never went out, and Stripe kept redelivering.

Tests mocked the gated modules, so nothing failed in CI. Server actions called server-side don't go through an HTTP boundary, so the gate reads as an internal throw.

# Evidence

Stack from the Render log, 2026-09-23 20:18:29Z: `Error: Unauthorized` in `requireRole`, called from `updateWorkflowState`, called from `resetWorkflow`, called from `/user/dashboard/page`, with digest `2701482952`. It was reproduced locally against a scratch DB: 500 before the fix, 200 after, and the workflow reset from `denied` to `unscheduled`. The webhook stack showed `Error: Not authorized` in `/api/webhook/stripe/route.js`, 19 times since Sep 9. A regression test (`route.test.ts`, full refund) fails on the old code.
