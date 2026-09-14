---
type: Failure Mode
title: A client component importing from a server-tainted module breaks the bundler, not tsc
description: Pulling a pure helper into a "use client" file from a module that also imports firebase-admin drags the server SDK into the browser bundle; tsc passes, the page fails to load.
kind: failure-mode
tags: [nextjs, react-server-components, bundler, client-server-boundary, verification, typescript]
generated: { by: claude/opus-4-8, at: 2026-09-09T13:51:56Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/wiley/web/lib/phone-normalize.ts
    title: normalizePhoneNumber extracted to a client-safe module
    last_modified: 2026-09-09
  - id: broken-import
    resource: projects/wiley/web/lib/approved-callers.ts
    title: approved-callers.ts imports firebase-admin at module top
    last_modified: 2026-09-09
not:
  - term: "import { normalizePhoneNumber } from '@/lib/approved-callers' inside a 'use client' component"
    why: "approved-callers.ts imports firebase-admin, so the whole server SDK (google-auth-library -> child_process) is pulled into the browser bundle and Turbopack fails with Can't resolve 'child_process'"
    instead: "import from a pure client-safe module (lib/phone-normalize.ts); re-export it from the server module so server callers are unchanged"
---

# Failure Mode

Importing even a pure, dependency-free helper into a `"use client"` component
from a module that *also* imports server-only code (firebase-admin, a Node
built-in, anything touching `child_process`/`fs`) pulls that entire server graph
into the browser bundle. The bundler then fails resolving a Node built-in
(Turbopack: `Module not found: Can't resolve 'child_process'`).

`tsc --noEmit` passes clean, because TypeScript type-checking does not model the
client/server bundle boundary — it resolves types across the whole graph without
caring what ships to the browser. The break is invisible to tsc and only appears
when the page actually loads (or during `next build`).

Fix: extract the pure function into its own module with zero server imports, and
re-export it from the server-tainted module so existing server callers keep their
import path. In wiley, `normalizePhoneNumber` lived in
`web/lib/approved-callers.ts` (imports firebase-admin). Moving it to
`web/lib/phone-normalize.ts` and re-exporting (`import { normalizePhoneNumber }
from "@/lib/phone-normalize"; export { normalizePhoneNumber };` — a re-export
alone does not create the local binding the module needs at lines 48/135) fixed a
client-drawer build break.

# Why it matters

A green `tsc` is treated as sufficient proof a change is safe, so a change that
crosses the client/server boundary can be committed, pushed, and even pass code
review while being 100% broken at runtime. The class of break costs nothing in
type-checking and blocks the whole route at load. Verification for any
boundary-crossing change must load the page or run the production build, not stop
at `tsc`.

# Evidence

- `web/app/contacts/contact-drawer.tsx` (a `"use client"` component) first
  imported `normalizePhoneNumber` from `@/lib/approved-callers`. `tsc --noEmit`
  reported 0 errors project-wide. Loading `/contacts` produced a Turbopack build
  error: `Module not found: Can't resolve 'child_process'`, with the import trace
  running `google-auth-library/build/src/auth/googleauth.js` ->
  `lib/firebase-admin.ts` -> `lib/approved-callers.ts` ->
  `app/contacts/contact-drawer.tsx [Client Component Browser]`.
- Fix commit `ea58678` (wiley main): new `web/lib/phone-normalize.ts`,
  re-exported from `approved-callers.ts`, drawer imports from the pure module.
  tsc still 0 errors; `/contacts` loads.
