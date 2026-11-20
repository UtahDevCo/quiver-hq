---
type: Observation
title: Elfa clip socket must be an enclosing dovetail, not the raw rail negative
description: The socket has to narrow to a mouth that captures the rail's head so it can only slide along the length. Building it as the literal negative of the tapered rail leaves the mouth as wide as the rail and the clip falls straight out.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [elfa, clip, dovetail, socket, 3d-printing, reverse-engineering]
generated: { by: claude/opus-4-8, at: 2026-09-16T20:46:27Z }
status: draft
sources:
  - id: code
    resource: projects/3d-printing/allen-organizer/src/allen_organizer/gridfinity_tray.py
    title: _socket() enclosing dovetail + MOUNT_CLEAR/MOUNT_BASE_EXPAND
    last_modified: 2026-09-16
  - id: module
    resource: brain/projects/3d-printing/modules/elfa-utility-board-clip-dovetail-interface.md
    title: existing Elfa clip interface module this refines
    last_modified: 2026-09-14
not:
  - term: "Build the socket as the literal negative of the clip rail's measured cross-section"
    why: "the vendor rail is a tapered bar wide at its base; its negative has a mouth as wide as the rail, so the clip is not captured and pulls straight out"
    instead: "clone the vendor rack leg's socket (enclosing dovetail: mouth -3.32, base -6.79, depth 6) so a narrow mouth captures the wide head"
---

# Observation

The Elfa `ElfaModuleClip` rail is a tapered bar. To hang a part on it, the socket
must be an **enclosing dovetail**: a narrow mouth (~3.3 mm) at the board face
opening to a wide base (~6.8 mm) deep in the part. The narrow mouth captures the
rail's head so the part can only slide along the rail's length; it can't pull off
perpendicular. Clone the vendor rack leg's socket profile directly (base -6.79,
mouth -3.32, depth 6). Do **not** re-derive the socket from the rail's own
cross-section.

Tuned clearances, validated on printed coupons against a printed clip (QIDI Plus
4, PLA):
- `MOUNT_CLEAR = -0.35` — socket 0.35 mm tighter per side than the vendor dims.
  (+0.15 gripped but was ~1 mm loose; -0.35 fit but the head bottomed tight.)
- `MOUNT_BASE_EXPAND = 0.3` — opens the base only so the rail head seats without
  binding, while the mouth keeps its grip.
- Cut the socket through the Gridfinity foot **and** clear a wider foot band
  (~18 mm) behind it: the clip's fat stopper is wider than the thin rail and
  hits the intact foot beside the socket as it seats.

# Why it matters

Getting the socket shape wrong wastes many print-test cycles. Building it as the
raw rail negative produced a slot that printed cleanly, looked plausible, and
completely failed — the clip dropped out because there was no undercut to capture
it. The distinction (enclosing dovetail vs open taper) is invisible until you
hold the print against the clip.

# Evidence

The raw-rail-negative socket printed and the clip "fell straight out" (owner's
words, with a side-by-side photo of the correct earlier dovetail vs the broken
open taper). Reverting `_socket()` to the vendor dovetail restored the grip;
then MOUNT_CLEAR -0.35 + BASE_EXPAND 0.3 dialed it to a confirmed perfect fit
across four printed coupons.
