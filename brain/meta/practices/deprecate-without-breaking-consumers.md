---
type: Practice
title: Retire an API with a migration guide, never a rename
description: Keep the original export, mark it @deprecated with a prop-by-prop mapping, and point at the replacement's live examples.
tags: [api-design, deprecation, migration]
generated: { by: claude/opus-5, at: 2026-07-29T14:05:03Z }
verified:
  - { by: human:christopher, at: 2026-07-29T15:38:27Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "renaming or deleting the old export when shipping a replacement"
    why: "breaks every consumer at once and forces a big-bang migration nobody schedules"
    instead: "keep the export, mark it @deprecated, let consumers migrate at their own pace"
  - term: "@deprecated with no migration guide"
    why: "tells the reader to stop without telling them where to go, so they don't move"
    instead: "a prop-by-prop old=new mapping plus a pointer to working examples"
sources:
  - id: radix-components
    resource: projects/zamp/utils/design-system/src/components/radix-components.ts
    title: "zamp Rt* deprecations with migration guides"
    author: human:christopher
    last_modified: 2026-07-25
---

# The practice

```tsx
/**
 * @deprecated use the newer Button component, going forward.
 *
 * ## Migration guide
 *
 * - `loading`: Same as before.
 * - `variant`: `solid`=`default`, `soft`=`secondary`, `surface`=no equivalent, use `outline`.
 * - `size`: `1`=`xs`, `2`=`sm`, `3`=`lg`, `4`=no equivalent.
 * - `radius`: Use Tailwind: `small`=`rounded-sm`, ... `full`=`rounded-full`.
 * - `color`: `gray`=`neutral`, `red`=destructive variant. If your color is missing, let's add it.
 * - `asChild`: Use `render`.
 *
 * See `Button` usage examples in `button.stories.tsx` for further details.
 */
```

Supporting conventions:

- Give the retired file and export an identifying prefix (zamp uses `rt-` /
  `Rt*` for the generation being phased out) so it's obvious at the import site.
- A retired member of a bulk re-export gets pulled into its own `const` so it
  can carry the JSDoc.
- Point at **live examples**, not prose. A story or test the reader can run beats
  a paragraph.

# Why the guide is the whole thing

Note the mapping names the *gaps*: "`surface`=no equivalent",
"`4`=no equivalent", "If your color is missing, let's add it." Admitting
non-parity is what makes the guide trustworthy — a guide that implies a clean
1:1 mapping gets abandoned at the first prop that doesn't map, and the consumer
quietly stays on the old API.

# Generalizes beyond components

The same shape works for any published surface: functions, endpoints, config
keys, CLI flags, event names. Keep the old name working, document the mapping
including its gaps, point at a runnable example.
