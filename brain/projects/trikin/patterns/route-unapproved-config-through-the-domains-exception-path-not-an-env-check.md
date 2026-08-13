---
type: Pattern
title: Route unapproved config through the domain's own exception path, not an environment check
description: When config is provisional, gating on NODE_ENV or a deploy flag lets it become authoritative by being deployed. Mark the config unapproved and let the domain's existing escalation carry it.
tags: [config, approvals, workflow, compliance, deployment]
generated: { by: claude/opus-5, at: 2026-08-07T18:57:02Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "if (env.ENVIRONMENT !== 'production') allow the placeholder values"
    why: "the check passes the moment the row is promoted or copied to prod, so provisional config becomes authoritative through a deploy rather than a decision, and nothing downstream records that it was provisional"
    instead: "carry the approval state on the config row, and have the reader report what is unapproved so the caller escalates through the path the domain already defines"
sources:
  - id: reader
    resource: projects/trikin/web/src/db/queries/policy.ts
    title: "getEffectivePolicy returning an unapproved[] alongside the policy (trikin commit c657ba0)"
    last_modified: 2026-08-07
  - id: consumer
    resource: projects/trikin/web/src/lib/underwriting/create-offer.ts
    title: "Unapproved policy becomes a material exception, closing the auto path"
    last_modified: 2026-08-07
---

# The pattern

Config that is drafted but not yet signed off needs to stay non-authoritative until
someone approves it. The reflex is an environment check, which ties "provisional" to
"not deployed" and gets those two apart as soon as the row is promoted.

Put the approval state on the config itself and have the reader return what is
missing rather than throwing or silently substituting:

```ts
type EffectivePolicy = { ruleSet; pricingMatrix; unapproved: string[] };
```

A non-empty `unapproved` is then handled by whatever escalation the domain already
has. In trikin that is a material exception: it closes the automated path, forces
both approvers, and writes a memo naming what was unapproved in the same batch as
the record it qualifies. No environment detection anywhere, and the same code path
runs locally and in production with the behaviour following the data.

The precondition is that the domain already has an escalation mechanism. If it does
not, this is a reason to build one: the mechanism is useful on its own, and it makes
provisional config a case it handles rather than a special case.

# Why it matters

The environment check has three failures the data-carried version does not. It
passes on the day the row reaches production, which is a deploy rather than a
decision. It leaves nothing on the resulting records, so nothing written against
provisional config is distinguishable afterwards. And it makes local and production
behaviour differ, so the escalation path is the one path never exercised before it
matters.

# Evidence

trikin's Delegation of Authority leaves two numbers blank pending Member approval: a
maximum advance rate and a minimum gross yield. `bin/dev/seed-policy-v1.sql` seeds
the rule set and pricing matrix as `status: 'draft'` with `isPlaceholder = 1`, and
says in a comment not to apply it to production.

`getEffectivePolicy` reports a draft rule set and a placeholder matrix in
`unapproved`. `createPurchaseOffer` turns a non-empty list into a material exception
under DoA §3:

```ts
const materialException = policy.unapproved.length > 0
  ? { rationale: `priced off unapproved policy: ${policy.unapproved.join("; ")}`,
      mitigants: "routed to dual-member approval ..." }
  : null;

const routing = routeDecision({
  aggregateConsideredCents,
  hasMaterialException: materialException !== null,
  automatedApprovalEnabled: policy.ruleSet.automatedApprovalEnabled,
});
```

`routeDecision` sends any material exception to both Members whatever the amount, so
with draft policy in place no auto-approval path is reachable and every offer
carries a memo saying why. Approving the policy is what changes the behaviour, and
it changes it in production and locally at the same moment.
