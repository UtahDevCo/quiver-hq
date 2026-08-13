---
type: Practice
title: Check authorization before doing any work
description: The authorization check is the first statement in a privileged entry point — before validation-dependent reads, before queries, before side effects. Then log who did what.
tags: [security, authorization, server-actions, audit]
generated: { by: claude/opus-5, at: 2026-07-29T22:55:47Z }
verified:
  - { by: human:christopher, at: 2026-07-29T22:55:47Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "fetching the record, then checking whether the caller may see it"
    why: "the read already happened; you pay for it, you may log it, and any error message leaks that the record exists"
    instead: "authorize first, then read"
  - term: "relying on the UI not to show the action"
    why: "server actions and route handlers are public endpoints regardless of which button renders"
    instead: "an explicit check inside every privileged entry point"
  - term: "a privileged mutation with no audit record"
    why: "you cannot answer \"who changed this\" after the fact, and that is the question that always gets asked"
    instead: "log actor, action, target id, and a note in the same transaction as the write"
  - term: "`if (!(await authCheck(role))) return;`"
    why: "a boolean guard is a no-op when the caller forgets to branch, and it cannot say which tenant's rows the caller may read, so scoping becomes a per-call-site convention"
    instead: "`const { brokerId } = await requireBrokerScope();` — it throws, and the query needs a value only the check produces"
  - term: "impersonation that swaps the session user id and logs nothing"
    why: "every later write records the impersonated user, so the audit trail asserts something false rather than being incomplete"
    instead: "write a row at the start and the end of the impersonation session carrying both identities"
sources:
  - id: wiley-contacts
    resource: projects/wiley/web/app/actions/contacts.ts
    title: "wiley — assertSelfOrAdmin() before any Firestore read, then an ownership re-check on edit"
    last_modified: 2026-07-29
  - id: trikin-admin
    resource: projects/trikin/web/src/app/admin/admin-actions.ts
    title: "trikin — checkAdminAuthorization() first in every admin action, plus logAdminAction() to admin_action_logs"
    last_modified: 2026-07-29
  - id: trikin-authcheck
    resource: projects/trikin/web/src/utils/auth-check.ts
    title: "trikin — authCheck() returns a boolean beside userCheck() and getSessionUserId() that throw, in one file"
    last_modified: 2026-07-30
  - id: trikin-impersonation
    resource: projects/trikin/web/src/auth.tsx
    title: "trikin — the session callback replaces user.id and stashes the admin where nothing reads it"
    last_modified: 2026-07-30
---

# The practice

In any privileged entry point — server action, route handler, worker endpoint,
CLI subcommand — the authorization check comes **first**. Before the query, before
the side effect, before anything you would rather not have done for an unauthorized
caller.

Then record it: actor, action, target id, and a short note.

# Why ordering matters, not just presence

"Authorized somewhere in the function" and "authorized first" are different
guarantees:

- A read that precedes the check has already happened. You paid for it, it may be
  in your query logs, and its error path can leak existence.
- Ownership checks are a *second* layer, not a substitute. wiley does both: it
  authorizes the caller, and then on edit re-reads the target document and verifies
  the `userId` matches — which is what actually stops an IDOR, since being a valid
  user says nothing about owning *this* record.

# Independently corroborated

Two repos, two unrelated stacks, no shared documentation lineage:

| Repo | Guard | Audit |
|---|---|---|
| wiley | `assertSelfOrAdmin(validated.userId)` before any Firestore read | — |
| trikin | `checkAdminAuthorization()` first in every admin action | `logAdminAction()` → `admin_action_logs` |

Neither repo's `AGENTS.md` states the rule; both codebases simply do it everywhere.
A convention followed without being written down is usually a stronger signal than
one that is documented — nobody had to be reminded.

trikin is the only one of the two with the audit half. It is included here because
the missing-audit-trail regret is universal and cheap to prevent, not because two
repos agreed on it.

# The guard throws, and it returns the scope

Ordering is the first half. The shape of the helper is the second, and a helper that
returns a boolean is not a guard:

```ts
await authCheck(AppRole.Admin);   // syntactically fine, reads like an assertion, does nothing
```

Forgetting to branch is invisible at the call site. Worse, a boolean answers only
"does this user hold this role", so every call site has to scope its own query by
hand and remember which tenant it is allowed to read.

```ts
const { userId, brokerId } = await requireBrokerScope();   // throws
const deals = await listDeals({ brokerId });               // scope is an argument
```

Now the check cannot be skipped, because the query needs a value only the check
produces. This is
[make-misuse-unrepresentable](make-misuse-unrepresentable.md) applied to
authorization.

The tell that a codebase has already worked this out and not finished: trikin's
`auth-check.ts` holds `authCheck()` returning a boolean beside `userCheck()` and
`getSessionUserId()` that throw. Same file, both conventions, and new code copies
whichever it meets first. Role-only checking was adequate while the product had one
shared partner view. The successor has several counterparties under a contractual
confidentiality obligation to each other, and the same helper is what stands between
them.

# Impersonation is a write that needs its own row

An admin impersonation feature that swaps `session.user.id` and writes no audit row
destroys attribution for everything that follows. Every downstream write records the
impersonated user, so the trail asserts something false rather than being merely
incomplete. In trikin's `auth.tsx` the session callback replaces `user.id` and
stashes the real admin under a separate key that nothing reads.

Log the start and the end of an impersonation session as their own events, carrying
both identities.

# The one ordering subtlety

Validation sometimes has to precede authorization, because you need a parsed input
to know *what* you are authorizing against — wiley parses with Zod, then calls
`assertSelfOrAdmin(validated.userId)`. That is correct. The rule is that no
**read, write, or external call** precedes the check, not that literally nothing does.
