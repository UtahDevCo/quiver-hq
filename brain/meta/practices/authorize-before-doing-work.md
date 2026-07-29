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
sources:
  - id: wiley-contacts
    resource: projects/wiley/web/app/actions/contacts.ts
    title: "wiley — assertSelfOrAdmin() before any Firestore read, then an ownership re-check on edit"
    last_modified: 2026-07-29
  - id: trikin-admin
    resource: projects/trikin/web/src/app/admin/admin-actions.ts
    title: "trikin — checkAdminAuthorization() first in every admin action, plus logAdminAction() to admin_action_logs"
    last_modified: 2026-07-29
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

# The one ordering subtlety

Validation sometimes has to precede authorization, because you need a parsed input
to know *what* you are authorizing against — wiley parses with Zod, then calls
`assertSelfOrAdmin(validated.userId)`. That is correct. The rule is that no
**read, write, or external call** precedes the check, not that literally nothing does.
