---
type: Observation
title: Re-parent aptamigo.com affiliates under Dan with the maintenance script
description: TAH affiliate onboarding leaves @aptamigo.com affiliates mis-parented; a recurring script re-parents them under Dan with a 10% override.
kind: workflow
proposed_layer: project
proposed_project: therapyanimalhub.com
tags: [affiliates, partner-applications, maintenance, production-write, turso]
generated: { by: claude/opus-4.8, at: 2026-08-17T19:43:00Z }
status: draft
not:
  - term: "before.find(r => r.email === DAN_EMAIL).id"
    why: "the query selects the column as `userId`, so `.id` is undefined — parent resolves to null and orphans everyone"
    instead: "dan.userId"
  - term: "set only parentAffiliateId when re-parenting"
    why: "without the parentPayoutPercentage override, resolveCommissionChain pays the parent their own headline rate"
    instead: "write parentPayoutType=percentage and parentPayoutPercentage=10 on the child row too"
sources:
  - id: script
    resource: projects/therapyanimalhub.com/bin/data/set-aptamigo-subaffiliates.ts
    title: set-aptamigo-subaffiliates.ts (commit 959d30d)
    last_modified: 2026-08-17
  - id: rate-model
    resource: projects/therapyanimalhub.com/src/lib/affiliate-referral-rates.ts
    title: affiliate referral rate resolution
    last_modified: 2026-08-17
  - id: prior-art
    resource: projects/therapyanimalhub.com/bin/data/set-affiliate-cascade.ts
    title: set-affiliate-cascade.ts (Josh-above-Dan cascade)
    last_modified: 2026-08-17
---

# Observation

TAH affiliate onboarding does not parent new `@aptamigo.com` signups under Dan, so they
land mis-parented (usually with no parent at all). This has to be fixed periodically, not
once. Run `bin/data/set-aptamigo-subaffiliates.ts` to re-parent every `@aptamigo.com`
affiliate under Dan (`dan@aptamigo.com`, userId `766bb879-cc6f-4aad-a7fd-34fa0d0c26e2`).

The script:
- Dry-run by default; `--execute` applies.
- Sets `parentAffiliateId = Dan` plus an explicit `parentPayoutType = percentage` /
  `parentPayoutPercentage = 10` override on each child row. The override is mandatory:
  `resolveCommissionChain` otherwise pays the parent their own headline rate, not the
  intended 10% cut.
- Touches only the `parent*` columns. Each affiliate's own payout rate is left alone.
- Excludes Dan himself, so his own row (parented under Josh at a 15% override) is untouched.
- Reads every row back and asserts the write landed, then prints a per-affiliate revert block.

It runs against **live production Turso** (TAH dev connects to prod), so it is a money/prod
write: run the dry run, confirm, then `--execute`, and keep the printed revert block.

# Why it matters

The `parent*` columns decide who gets paid on every future sale. Getting the parent id or
the override wrong misprices commissions silently until someone audits payouts. During the
first run, a `dan.id` vs `dan.userId` bug (the query selects `userId`) resolved the parent
to `undefined`, which would have orphaned every affiliate and set a 10% override pointing
nowhere. The dry run caught it before any write. The read-back assertion is the second
guard: a no-op UPDATE would otherwise look successful.

# Evidence

First execute run (2026-08-17) re-parented 3 of 4 aptamigo affiliates (lgribbons, lstagi,
justin.jorgensen) to Dan at 10%; braelyn.bianchi was already under Dan at 10%; Dan excluded.
All four verified via read-back. Revert block emitted per affiliate.
