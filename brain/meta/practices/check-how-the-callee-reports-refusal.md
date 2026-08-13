---
type: Practice
title: Check how the callee reports refusal before deleting a caller-side guard
description: An action that returns `error.message` reports failure through a value the caller can drop; deleting the client guard then silences every failure mode, not just the one being fixed.
tags: [error-handling, server-actions, review, next-js]
generated: { by: claude/opus-5, at: 2026-08-06T15:03:36Z }
status: stable
stale_after: 2027-08-13
sources:
  - id: evidence
    resource: https://github.com/deltaepsilon/therapyanimalhub.com/pull/27
    title: "therapyanimalhub.com PR #27 — Provider ID is missing after a Pass"
    last_modified: 2026-08-06
  - id: fix
    resource: projects/therapyanimalhub.com/src/app/(partner)/provider/letters/[intakeFormId]/compose-letter.tsx
    title: Mark-as-sent call site, fixed in commit 96f722f
    last_modified: 2026-08-06
not:
  - term: "the server action validates it, so the client check is redundant"
    why: "true only when the action throws; an action that returns error.message reports failure through a value the caller can drop"
    instead: "read the action's failure path first, then delete the guard and wire whichever mechanism it uses"
  - term: "await theAction(args); location.reload();"
    why: "a discarded return value is indistinguishable from success, so every failure becomes a page reload over unchanged state"
    instead: "const error = await theAction(args); if (error) { toast(error); return; }"
---

# The practice

Deleting a redundant caller-side guard is safe only once you have read how the callee
reports refusal. Two mechanisms look identical at the call site:

- The callee throws, and the caller needs `try`/`catch` to show anything.
- The callee catches and returns `error.message`, and the caller must inspect the
  return value.

Read the failure path, delete the guard, wire whichever mechanism is live. Both can
be live in one file.

# Why it matters

Removing the guard is usually right, since the server check is authoritative and the
client copy drifts. When the action reports by return value and the caller ignores it,
the change silences every failure mode of that action. The symptom is worse than the
bug it replaced: an action that used to show a misleading error now shows nothing, and
the user sees a successful-looking page reload over unchanged state.

# Evidence

therapyanimalhub.com PR #27 fixed a provider blocked by a stale `workflow.providerId`
by validating ownership server-side, then deleted the client guard that had produced
the misleading toast:

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

A SendGrid failure, a failed ownership assert, and a missing user all became a page
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

A sibling button in the same file already wrapped its throwing action in `try`/`catch`
with a toast, so one component carried both mechanisms.

Returning a message string rather than an `Error` across the boundary is itself
correct, per
[no-error-objects-across-boundaries](no-error-objects-across-boundaries.md). Dropping
it is the defect.
