---
type: Observation
title: Admin impersonation that swaps the session user and writes no audit row destroys attribution
description: Every action taken while impersonating is recorded as the impersonated user with nothing distinguishing it. Make impersonation read-only and prove it at the database, not in the handler.
kind: failure-mode
proposed_layer: meta
observed_in: trikin
tags: [security, audit, impersonation, nextauth, e-signature]
status: draft
not:
  - term: "session.user.id = impersonatedUser.id  // and nothing else changes"
    why: "downstream writes are indistinguishable from the real user's own actions, so the audit trail actively asserts something false"
    instead: "assertNotImpersonating() in every write path, a wasImpersonated column with a CHECK constraint, and an audit row on start and stop"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: auth, resource: "projects/trikin/web/src/lib/auth.tsx:78-101", title: "session callback replaces user.id/email/name/image with the impersonated user's; no audit write" }
  - { id: admin-actions, resource: projects/trikin/web/src/app/admin/admin-actions.ts, title: "startImpersonation / stopImpersonation write no admin_action_logs row" }
---

# Observation

The impersonation implementation set `session.user.id` to the target user and
carried on. It stashed the real admin in `session.adminUser`, so the information
existed — but nothing downstream consulted it, and neither entering nor leaving
impersonation wrote an audit row.

Consequence: an action taken while impersonating is recorded as the impersonated
user's own action, with no marker. The audit trail is not merely incomplete, it
asserts something untrue, and there is no query that recovers the truth afterwards.

Three defences, deliberately layered:

1. `assertNotImpersonating()` as the first statement of every write path.
   Impersonation becomes read-only, which is what it is almost always intended to be.
2. A `wasImpersonated` column on evidence rows with a **CHECK constraint** pinning
   it false. If a code path forgets defence 1, the database refuses the row.
3. Audit rows on start and stop, plus an `impersonatedUserId` column on every
   audited write.

# Why it matters

Support impersonation is built to reproduce a bug, and reproducing a bug is reading.
The write capability is incidental, unused, and unguarded — so it survives review
because nobody is doing the thing that would expose it.

It becomes disqualifying the moment the system captures anything meant to be
attributable to a person. Under an electronic-signature regime, attribution is the
whole basis of enforceability: a signature is binding because it was the act of that
person. A signature record that cannot rule out having been produced by an admin
wearing that person's session is not evidence of anything. That is why defence 2 is
a database constraint rather than a code convention — it is the only layer that
still holds when someone adds a new write path a year later and does not know the
rule exists.

Related: [[authorize-before-doing-work]], which says to log actor, action, target,
and note. This is the case where the *actor* is the field that lies.

# Evidence

`web/src/lib/auth.tsx`, session callback:

```ts
if (impersonatedUser) {
  session.impersonationId = impersonationId;
  session.adminUser = session.user;
  session.user.id = impersonatedUser.id;      // ← everything downstream now sees the target
  session.user.email = impersonatedUser.email;
  ...
}
```

`session.adminUser` is populated and then never read by any write path.
