---
type: Failure Mode
title: A collectionGroup query is denied when the read rule authorizes via get()
description: Firestore can't prove a collectionGroup list is safe if the read rule uses get()/exists(); it 403s even OR'd with a query-safe clause. Use resource.data-only rules, or subscribe per-parent and merge.
kind: failure-mode
tags: [firestore, security-rules, collection-group, queries]
generated: { by: claude/opus-4.8, at: 2026-09-03T03:46:08Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: agenda-hook
    resource: projects/popreminders.com/src/features/reminders/use-agenda.ts
    title: useAgenda subscribes per-group and merges instead of collectionGroup(reminders)
    last_modified: 2026-09-03
  - id: rules
    resource: projects/popreminders.com/firestore.rules
    title: groups read uses resource.data.memberUids (not get); reminders read adds assigneeUid clause
    last_modified: 2026-09-03
---

# Failure Mode

A Firestore `collectionGroup()` list query returns `PERMISSION_DENIED` when the matched
read rule authorizes through `get()`/`exists()` — e.g. `isMember(groupId)` doing
`get(/databases/$(db)/documents/groups/$(groupId)).data.memberUids`. Firestore must prove
a list/query only returns allowed documents from the **query constraints + `resource.data`
alone**; a `get()`-based clause is not statically provable, so the whole query is rejected.
This holds even when the `get()` clause is OR'd with a query-safe one:
`allow read: if isMember(groupId) || resource.data.assigneeUid == request.auth.uid` still
denies `collectionGroup('reminders').where('assigneeUid','==',me)`.

Two fixes:
1. Make the read rule query-safe with `resource.data` only (drop the `get()`), when the rule
   doesn't need parent data. This is how the top-level groups-list query was fixed:
   `request.auth.uid in resource.data.memberUids` instead of `isMember` via `get()`.
2. When the rule genuinely needs parent data, avoid `collectionGroup`: iterate the known
   parent ids and subscribe **per parent** (single-collection queries), merging client-side.
   Each single-parent query is `isMember`-gated and query-safe because the `get()` target is
   constant from the path. This is how the calendar agenda was fixed (`useAgenda`).

# Why it matters

The denial surfaces only at query time and only for the cross-parent collectionGroup list. A
single-doc `get()` under the same rule succeeds, and a per-collection query (single parent)
succeeds — so it looks like the rule is fine everywhere except the one place you need it. Cost
in popreminders.com: it bit twice (groups list in P2, reminders agenda in P6), each a
half-hour detour, because the shape looks correct and the rule "obviously" allows the read.

Amplifier: an `onSnapshot` error callback that swallows the error
(`() => setItems([])`) hides the 403 entirely — the UI just renders empty with a clean
console. Diagnose by replaying the exact query via the Firestore REST `:runQuery` endpoint
with the user's bearer token (pull it from IndexedDB `firebaseLocalStorageDb`); the raw 403
`PERMISSION_DENIED` comes back immediately.

# Evidence

```
// Denied: collectionGroup list against a get()-based read rule
POST .../documents:runQuery  { structuredQuery: { from: [{collectionId:'reminders', allDescendants:true}],
  where: { fieldFilter: { field:{fieldPath:'assigneeUid'}, op:'EQUAL', value:{stringValue: uid} } } } }
=> 403 { "error": { "code":403, "message":"Missing or insufficient permissions.", "status":"PERMISSION_DENIED" } }

// reminders read rule at the time — the assigneeUid clause is query-safe, but the get()-based
// isMember OR-branch makes the whole collectionGroup list unprovable:
match /reminders/{doc} {
  allow read: if isMember(groupId) || (signedIn() && resource.data.assigneeUid == request.auth.uid);
}
```

Fix that shipped — subscribe per group, merge:
```ts
const unsubs = groupIds.map((groupId) =>
  onSnapshot(query(collection(db,'groups',groupId,'reminders'), where('assigneeUid','==',uid)), ...));
```

not:
  - term: "collectionGroup(db,'reminders').where('assigneeUid','==',uid) with an isMember() OR-clause rule"
    why: "the get()-based branch makes the collectionGroup list unprovable; 403 at query time"
    instead: "iterate known parent ids and subscribe per-parent (single-collection, isMember-safe), then merge"
  - term: "onSnapshot(q, onData, () => setItems([]))"
    why: "the error callback swallows PERMISSION_DENIED so the UI shows empty with no console error"
    instead: "log the error, or omit the swallow so the denial is visible; confirm with REST :runQuery"
