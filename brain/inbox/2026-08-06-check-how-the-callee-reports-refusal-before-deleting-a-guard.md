---
type: Observation
title: Check how the callee reports refusal before deleting a caller-side guard
description: Moving validation server-side only preserves feedback if the server throws; an action that returns its error message needs the caller to inspect the return value.
kind: failure-mode
proposed_layer: meta
observed_in: therapyanimalhub.com
tags: [error-handling, server-actions, review, next-js]
generated: { by: claude/opus-5, at: 2026-08-06T15:03:36Z }
status: draft
not:
  - term: "the server action validates it, so the client check is redundant"
    why: "true only when the action throws; an action that returns error.message reports failure through a value the caller can drop"
    instead: "read the action's failure path first, then delete the guard and wire whichever mechanism it uses"
sources:
  - id: evidence
    resource: https://github.com/deltaepsilon/therapyanimalhub.com/pull/27
    title: "therapyanimalhub.com PR #27 — Provider ID is missing after a Pass"
    last_modified: 2026-08-06
  - id: fix
    resource: projects/therapyanimalhub.com/src/app/(partner)/provider/letters/[intakeFormId]/compose-letter.tsx
    title: Mark-as-sent call site, fixed in commit 96f722f
    last_modified: 2026-08-06
---

# Observation

Deleting a redundant client-side guard is safe only if the server rejects by
**throwing**. Two mechanisms look alike at the call site and are not:

- The action throws. The caller needs `try`/`catch` to show anything.
- The action catches and **returns** `error.message`. The caller must inspect the
  return value; a discarded return is indistinguishable from success.

Before removing a caller-side check on the grounds that "the server validates it",
read the action's failure path and wire up whichever mechanism it actually uses.

# Why it matters

Removing the guard is usually the right call: the server check is authoritative and
the client copy drifts. But if the action reports failure by return value and the
caller ignores it, the change silences **every** failure mode of that action, not
just the one being fixed. The symptom is worse than the bug it replaced: an action
that used to show a misleading error now shows nothing at all, and the user sees a
successful-looking page reload over unchanged state.

# Evidence

therapyanimalhub.com PR #27 fixed a provider being blocked by a stale
`workflow.providerId` by validating ownership server-side, then deleted the client
guard that had produced the misleading toast:

```diff
-            if (!intakeForm.providerId) {
-              toast({ title: 'Error', description: 'Provider ID is missing' });
-
-              return;
-            }
```

`sendThirdPartyLetterNotification` ends in `catch { return error instanceof Error ?
error.message : JSON.stringify(error) }`, so its type is `string | undefined`. The
call site dropped it:

```ts
await sendThirdPartyLetterNotification({ intakeFormId: intakeForm.id });
location.reload();
```

A SendGrid failure, a failed ownership assert, or a missing user all became a page
reload with the letter still unsent. The fix inspects the return:

```ts
const error = await sendThirdPartyLetterNotification({ intakeFormId: intakeForm.id });

if (error) {
  console.error(error);
  toast({ title: 'Error', description: error });
  setSubmitting(false);

  return;
}

location.reload();
```

A sibling button in the same file already wrapped its throwing action in
`try`/`catch` with a toast, so both mechanisms were live in one component.

Returning a message string rather than an `Error` across the boundary is itself
correct (see `no-error-objects-across-boundaries`). Dropping it is the defect.
