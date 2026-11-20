---
type: Observation
title: Cache a configured firebase-admin Firestore on globalThis in Next.js
description: Firestore settings() may run once per process, but Next bundles a lib module once per route, so a module-level guard calls it twice and the second route throws.
kind: failure-mode
proposed_layer: meta
tags: [nextjs, firebase-admin, firestore, bundling]
generated: { by: claude/opus-5.5, at: 2026-11-12T14:37:29Z }
status: draft
sources:
  - id: fix
    resource: projects/calligraphy/apps/calligraphy.org/lib/firebase/admin.ts
    title: adminFirestore() caches the configured instance on globalThis
    last_modified: 2026-11-12
  - id: commit
    resource: projects/calligraphy
    title: "1866eb3 Phase 0: drop Payload and Fly, move the site onto Firebase"
    last_modified: 2026-11-12
not:
  - term: "let firestore; if (!firestore) { firestore = getFirestore(app); firestore.settings({...}) }"
    why: "each route bundle gets its own copy of the module variable, but firebase-admin keeps one Firestore per app, so the second bundle's settings() call throws"
    instead: "store the configured instance on globalThis (or use a getter that never calls settings() twice for the same app)"
---

# Observation

firebase-admin allows `Firestore.settings()` (for example `ignoreUndefinedProperties: true`) once, before any other call on that instance. `getFirestore(app)` returns the same instance process-wide. Next.js bundles a shared lib module separately per route, so a module-level "already configured" variable does not dedupe across routes: the first route configures Firestore, the second route's copy of the module calls `settings()` again and throws "Firestore has already been initialized. You can only call settings() once, and only before calling any other methods on a Firestore object."

Cache the configured instance on `globalThis`.

# Why it matters

The failure depends on which routes have run in the process. In calligraphy, `/` and `/directory` rendered fine, then `POST /api/leads` returned 500 in the same `next start` server. A test that hits one route at a time never sees it.

# Evidence

Observed 2026-11-12 running the standalone build against the emulators: `[Leads] failed to write lead Firestore has already been initialized...`. Moving the cache to `globalThis.__calligraphyFirestore` fixed it; the lead then stored and returned its id.
