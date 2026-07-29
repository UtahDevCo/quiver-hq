---
type: Pattern
title: FormDrawer — a generic react-hook-form container in a drawer
description: Wraps Drawer with create/edit modes, loading skeleton, dismissible API error, dirty-check on close, Cmd/Ctrl+Enter submit, and an rAF-timed reset that waits out the close animation.
tags: [ui, forms, drawer, react-hook-form]
generated: { by: claude/opus-5, at: 2026-07-29T22:55:47Z }
verified:
  - { by: human:christopher, at: 2026-07-29T22:55:47Z }
status: stable
stale_after: 2027-07-29
relations:
  - { kind: depends-on, target: /projects/wiley/patterns/drawer.md }
not:
  - term: "setTimeout(() => form.reset(), 300) to reset after the drawer closes"
    why: "hardcodes a guess at the animation duration; too short and the user watches fields blank out, too long and a reopen shows stale values"
    instead: "requestAnimationFrame, which resets on the next paint after the close commits"
sources:
  - id: form-drawer
    resource: projects/wiley/web/components/forms/form-drawer.tsx
    title: "wiley — FormDrawer (~250 lines)"
    author: human:christopher
    last_modified: 2026-07-29
  - id: form-input
    resource: projects/wiley/web/components/forms/form-input.tsx
    title: "wiley — FormInput, generic over TFieldValues/TName, with char counter and formatValue"
---

# The API

```ts
type FormDrawerProps<TFieldValues> = {
  mode: "create" | "edit";
  isLoading?: boolean;       // → skeleton
  isSubmitting?: boolean;
  submitDisabled?: boolean;
  error?: string | null;     // → dismissible FormApiError
  submitText?: string;
  closeOnSuccess?: boolean;
  resetOnClose?: boolean;
  skipDirtyCheck?: boolean;
  drawerMode?: DrawerMode;  onModeChange?: (m: DrawerMode) => void;
};
```

# What it handles so each form doesn't

- **Loading vs empty**: `isLoading` swaps in `FormSkeleton` rather than rendering an
  empty form that looks broken.
- **API error surface**: `error` renders a dismissible `FormApiError` inside the
  drawer, separate from field-level validation.
- **Dirty check on close**: confirms before discarding edits, with `skipDirtyCheck`
  for the cases where that prompt is noise.
- **Cmd/Ctrl+Enter submits**, which is what anyone who fills forms all day expects.
- **Reset timed to the animation**: `requestAnimationFrame` after close, not a
  guessed `setTimeout`. See the `not:` entry — this is the detail most implementations
  get wrong in one direction or the other.

# Portability

**High.** Generic over `TFieldValues`, no business logic, and its only real
assumption is react-hook-form. Lifting it needs `Drawer`, `Form`, `FormSkeleton`, and
`FormApiError` — a contained set.

`FormInput` is worth taking with it: generic over `<TFieldValues, TName>`, with a
character counter and an optional `formatValue` transform applied on every keystroke
(used for live phone-number formatting). Requires `formatValue` to be fast and
deterministic, since it runs per keypress.

# The division of state, which is the reusable idea

The parent owns **whether the drawer is open** (ideally via
[useDrawerState](url-driven-drawer-state.md)). The FormDrawer owns **form state**.
Neither reaches into the other.

That split is why the same container works for a create flow, an edit flow loaded
from a query, and a filter panel — the thing that varies is the schema and the
submit handler, and both are props.
