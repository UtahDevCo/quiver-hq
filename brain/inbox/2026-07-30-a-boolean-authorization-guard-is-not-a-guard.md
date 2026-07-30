---
type: Observation
title: An authorization helper that returns a boolean is not a guard
description: A caller who forgets to check the return value gets silent full access, and the call site reads exactly like a guard. Make the helper throw and return the caller's scope.
kind: failure-mode
proposed_layer: meta
observed_in: trikin
tags: [security, authorization, api-design, make-misuse-unrepresentable]
status: draft
not:
  - term: "if (!(await authCheck(AppRole.Admin))) return; // easy to omit"
    why: "omitting the check is invisible at the call site — `await authCheck(role)` on its own line looks like an assertion and is a no-op"
    instead: "const { userId, brokerId } = await requireBrokerScope(); // throws, and you need the return value to proceed"
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
sources:
  - { id: authcheck, resource: "projects/trikin/web/src/utils/auth-check.ts:4-15", title: "authCheck(role) returns boolean; userCheck/getSessionUserId in the same file throw" }
---

# Observation

`authCheck(role)` returns `true`/`false`. Two failure modes follow, and the second
is the dangerous one:

1. A caller forgets to branch on the result. `await authCheck(AppRole.Admin);` on
   its own line is syntactically fine, reads like an assertion, and does nothing.
2. Because it only answers "does this user hold this role", it cannot answer "which
   tenant's data may this user see" — so every call site has to remember to scope
   its own query, separately, by hand.

The fix is one shape: the guard **throws** on failure and **returns the scope** on
success.

```ts
const { userId, brokerId, brokerRole } = await requireBrokerScope();
const deals = await listDeals({ brokerId });   // scope is an argument, not a convention
```

Now forgetting the check is impossible, because you cannot get `brokerId` without
passing it. Tenancy stops being a thing each call site remembers and becomes a
thing the type system hands you.

Tell: the same file already had `userCheck()` and `getSessionUserId()` that throw.
A codebase with both conventions side by side has already discovered the right one
and not finished applying it.

# Why it matters

Same-file inconsistency is the signal — it means the boolean form is a leftover, not
a decision, and new code copies whichever it happens to see first.

The tenancy half is what turns it from untidy into a breach. In the application this
came from, the pre-existing product had one shared partner view, so role-only
checking was adequate and nobody noticed the gap. The successor product has multiple
counterparties with a contractual confidentiality obligation to each other, and the
identical helper is now the thing standing between them.

This is [[make-misuse-unrepresentable]] applied to authorization, and it is why
[[authorize-before-doing-work]] should say the guard returns a scope rather than
merely that it comes first.

# Evidence

`web/src/utils/auth-check.ts`:

```ts
export async function authCheck(role: AppRole) {
  const session = await auth();
  const userId = session?.user?.id;
  if (!userId) return false;
  const { roles } = await getUserRoles(userId);
  return roles.includes(role);        // ← boolean; nothing forces the caller to look
}

export async function userCheck(userId: string) {
  if (userId === (await getSessionUserId())) return true;
  throw new Error("User not authorized");   // ← the right shape, same file
}
```
