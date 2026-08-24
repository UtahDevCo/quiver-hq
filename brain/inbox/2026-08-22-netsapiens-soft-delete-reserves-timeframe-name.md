---
type: Observation
title: NetSapiens soft-deletes reserve a timeframe name that no endpoint can free
description: A deleted answering rule / timeframe persists flagged "Deleted" and keeps its name reserved, so createTimeframe collides forever and only a vendor backend purge clears it.
kind: failure-mode
proposed_layer: project
proposed_project: wiley
tags: [netsapiens, altaworx, quiet-hours, third-party-api, soft-delete]
generated: { by: claude/opus-4.8, at: 2026-08-22T11:34:17Z }
status: draft
sources:
  - id: code
    resource: projects/wiley/web/app/actions/settings.ts
    title: syncQuietHoursToNetSapiens reserved-name catch (createTimeframe 400 -> throw "needs NetSapiens support")
    last_modified: 2026-08-22
  - id: audit
    resource: projects/wiley/web/scripts/audit-quiet-hours-netsapiens.ts
    title: ORPHAN_RULE fleet sweep (flag = qhRule present && qhTf absent)
    last_modified: 2026-08-22
  - id: commit
    resource: projects/wiley (git 49ba88e)
    title: "fix(quiet-hours): stop the 409 lockout and the 24/7 DND (cards #27, #30) — removed the delete-then-recreate that orphaned these"
    last_modified: 2026-07-29
not:
  - term: "Delete the orphaned QuietHours answering rule in the NetSapiens Manager Portal (the red ✕)"
    why: "The portal ✕ soft-deletes: the rule stays in the list flagged 'Deleted' and keeps reserving the timeframe name, so createTimeframe still 400s. Confirmed on the test domain 2026-08-22."
    instead: "Escalate to NetSapiens/Altaworx to hard-delete/purge the record on the backend; nothing in the API or portal can free the name."
  - term: "Have the customer (or an admin via impersonation) re-save quiet hours to recreate the timeframe"
    why: "Re-save calls createTimeframe, which 400s 'already exists for the given user' for these accounts; the save throws before rebinding the rule, so it is a safe no-op but never fixes a reserved-name account."
    instead: "Run repair-orphan-quiet-hours-resave.ts --apply to classify FIXED vs RESERVED; RESERVED accounts need the vendor purge."
---

# Observation

In the Wiley NetSapiens partition (Altaworx, nsb1.unifiedsolutions.cloud), answering rules and timeframes are **soft-deleted**. A deleted answering rule remains visible in the Manager Portal (Users → 1001 → Answering Rules) carrying a "Deleted" badge, and it keeps its associated timeframe name reserved.

That soft-delete residue is the root cause of the card #32/#39 ORPHAN_RULE class:

- `createTimeframe("QuietHours")` (a domain-scope POST) returns `400 "A timeframe with this name already exists for the given user"` — it collides with a soft-deleted user-scope record.
- `GET .../timeframes` returns empty at **both** domain and user scope (extensions 1001 and 2001).
- `DELETE .../answerrules/QuietHours` returns 404 while `GET` still lists the rule.
- Clicking the portal delete (✕) does not release the name — it just soft-deletes again.

Neither the v1/v2 API nor the Manager Portal can hard-delete/purge these records. Only a NetSapiens/Altaworx backend action frees the name.

# Why it matters

Quiet hours can never be (re)configured for an affected customer until the vendor purges the record. Any repair built on "delete the rule and let the customer re-save" silently fails: the delete looks like it worked (badge flips to "Deleted"), but the name stays reserved and the next save 400s. Card #24 swallowed exactly this and left quiet hours inert while reporting success. As of 2026-08-22, 11 real customer accounts are stuck in this state (6 show the app "enabled" while nothing enforces).

# Evidence

Diagnosis surfaces, all checked 2026-08-22:
- Domain Time Frames view: only leftover `Qh…Probe` artifacts, no `QuietHours`.
- User-scope Time Frames via URL filter `.../portal/timeframes/index/filter:extension/value:2001` (and `1001`): nothing.
- Users → 1001 → Answering Rules: multiple rules listed with "Deleted" badges still present — the tell.

Live confirmation: `repair-orphan-quiet-hours-resave.ts --apply` on all 6 "on" accounts + the test domain returned 7/7 `RESERVED` (createTimeframe 400), 0 `FIXED`, with no state change (the sync throws before touching a rule).

Detection scripts (all read-only except the last):
- `web/scripts/audit-quiet-hours-netsapiens.ts` — fleet sweep, `ORPHAN_RULE` when a QuietHours rule exists but no QuietHours timeframe.
- `web/scripts/audit-orphan-rule-repairability.ts --emails <list>` — per-account, reports `shape: orphan`.
- `web/scripts/repair-orphan-quiet-hours-resave.ts --apply` — attempts the create; `FIXED` = name was free, `RESERVED` = needs vendor.

The delete-then-recreate sync path that created these orphans was removed in commit `49ba88e`, so no new accounts enter this state — these are historical residue.
