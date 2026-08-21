---
type: Observation
title: An uncommitted UI change reads exactly like a missing capability
description: A staged-but-unsaved portal reorder produced the same null diff as "the portal cannot reorder".
kind: failure-mode
proposed_layer: meta
tags: [measurement, ui, probes, netsapiens]
generated: { by: claude/opus-5, at: 2026-08-14T13:45:00Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/snapshot-answering-rules.ts
    title: header note on the green vs yellow save banner
    last_modified: 2026-08-14
---

# Observation

To find out whether a vendor portal could reorder records that our API key could
not, the method was: snapshot the backend, make the change in the portal,
snapshot again, diff. The first reorder auto-committed and showed a green banner
reading "Answering rules have been reprioritized". The second showed a yellow
banner with Cancel and Save buttons, and the change sat in the browser only.

A snapshot taken at that moment reported no field changed on any rule. That
output is identical, byte for byte, to what a portal with no reorder capability
would have produced.

When measuring an external system through a human action in someone else's UI,
the commit boundary is part of the experiment. Record what the UI claimed
(banner, toast, button state) alongside the backend reading, and treat a null
result as unresolved until the UI has confirmed a write.

# Why it matters

The intended conclusion from a null diff was "the portal cannot reorder, so the
route is closed and these accounts need the vendor". Acting on it would have
escalated three repairable customer accounts to a third party. The same UI
affordance behaved differently twice in one session, so "it saved last time" is
not a safe assumption either.

# Evidence

Diff taken with the reorder staged and unsaved:

    === christopheresplinUXTSZZ / 1001   star-first → pending ===
      no field changed on any rule.
    VERDICT
      NOTHING CHANGED. Either the portal action did not reach NetSapiens, or the
      snapshots bracket the wrong moment.

After clicking Save, the same comparison returned REORDERED across 11 rules with
timeframe ids intact.

The verdict text was written before this happened, which is the only reason the
null reading was treated as ambiguous rather than as an answer.

not:
  - term: "a null diff after a UI action means the UI cannot perform that action"
    why: "staged, unsaved and unsupported all read as an unchanged backend"
    instead: "confirm the UI reported a committed write before interpreting the diff"
