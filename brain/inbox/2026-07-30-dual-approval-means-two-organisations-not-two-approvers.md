---
type: Observation
title: Dual approval means two distinct organisations, so authority cannot live in a role array
description: '"Both Members must approve" is unprovable by counting approvals. Authority needs an effective-dated identity carrying its organisation, its cap, and the resolution that granted it.'
kind: invariant
proposed_layer: project
proposed_project: trikin
observed_in: trikin
tags: [authorization, governance, approvals, schema-design, audit]
status: draft
not:
  - term: "approvals.filter(a => a.decision === 'approved').length >= 2"
    why: "two approvals from the same Member satisfy the count and not the requirement; and a role array has no history, so a revoked approver's past approval silently becomes invalid or stays valid depending on today's state"
    instead: "authority_identities with memberOrg, effectiveFrom/effectiveTo/revokedAt, maxSinglePurchaseCents, canReleasePayments, appointedByApprovalId — and require distinct memberOrg"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: doa, resource: "Delegation of Authority and Initial Underwriting Policy §2, §3, §8", title: "Authorized Representatives table with designee and backup per Member; per-officer purchase authority; separate authorized payment release" }
  - { id: founders, resource: "Founders' Principles and Agreed Business Terms §3-4", title: "SBI 50% / Trikin Holdings 50%; material decisions unanimous" }
  - { id: approles, resource: "projects/trikin/web/src/db/schema.ts:34-56", title: "users.appRoles — a mutable JSON array with no history, the wrong home for this" }
---

# Observation

The governing policy says a purchase above $10,000 requires "prior written approval
from both Members" of a 50/50 joint venture. Four things follow that a role array
structurally cannot express:

- **Organisational distinctness.** One approval from SBI *and* one from LevyCo.
  Counting approvals cannot prove they came from opposite sides of the ownership.
- **Effective dating.** An approval made in March must be judged against the
  authority in effect in March. `appRoles` is destructively mutated, so revoking an
  approver today rewrites the validity of every past approval — in whichever
  direction happens to be convenient.
- **Per-officer limits.** The policy contemplates a Credit/Operations Officer with a
  dollar cap and a *separate* payment-release officer. Those are attributes of an
  appointment, not roles.
- **Provenance of the appointment.** Authority is granted by Member resolution, so
  each identity should chain back to the approval that granted it. Toggling a role
  in an admin drawer leaves no such record.

Hence a separate `authority_identities` table, and a clean split: `AppRole.Admin`
grants the `/admin/*` **surface**; an authority identity grants the power to
**decide**. An operations user can be an admin with zero authority identities —
sees every queue, can approve nothing.

The resolution function stays pure and enforces: distinct `memberOrg` for the dual
tier; the requester never among the approvers; each authority effective at its own
`decidedAt`; the officer cap respected; and, for a funding release, an approver set
**disjoint** from the purchase approvers, which is what "separate authorized payment
release" means.

# Why it matters

The naive version passes every test you would think to write, because the tests
would use two different users — and two different users is not the requirement. It
fails only when the two approvals happen to come from the same side, which is the
normal case when one Member is more responsive than the other. So the control
degrades exactly under the conditions it exists for.

The effective-dating half matters for a different reason: without it, the answer to
"was this $40,000 purchase properly approved?" changes over time as personnel
change. An audit trail whose verdict depends on when you ask it is not an audit
trail.

The generalisable shape: **when a rule is about *whose* approval, a role array is
the wrong primitive** — it models capability, and the rule is about identity,
organisation, and time.

# Evidence

DoA §2 tabulates an "Initial Designee" and a "Backup / Replacement" per Member
(Andy Swartz for SBI, Joshua Levy for LevyCo), which is an effective-dated
appointment with a named successor — precisely the thing a `string[]` on a user row
cannot hold.
