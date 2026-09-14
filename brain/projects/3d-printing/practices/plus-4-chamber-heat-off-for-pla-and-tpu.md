---
type: Practice
title: On the Plus 4, run PLA and TPU with the chamber heater OFF and the enclosure open
description: An enclosed heated chamber cooks PLA into heat-creep clogs and starves part cooling; open the door and pull the glass top for PLA and TPU. Chamber heat is for ABS/ASA/PC/nylon/CF.
kind: practice
tags: [3d-printing, qidi, chamber, pla, tpu, heat-creep, failure-mode]
generated: { by: claude/opus-4-8, at: 2026-09-13T20:39:11Z }
verified:
  - { by: human:christopher, at: 2026-09-14T19:48:30Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: qidi-review
    resource: https://qidi3d.com/blogs/news/qidi-plus-4-3d-printer-review
    title: QIDI Plus 4 review (chamber usage per material)
    last_modified: 2026-09-13
  - id: 3dwithus
    resource: https://3dwithus.com/qidi-plus4-review-3d-printer-tests-tips-and-settings
    title: 3DwithUs Plus 4 tests/tips (PLA lid-off, PETG closed OK)
    last_modified: 2026-09-13
not:
  - term: "Print PLA in the closed, chamber-heated enclosure like everything else"
    why: "PLA in a warm sealed chamber softens in the heat break (heat creep) and clogs, and loses the part cooling PLA depends on"
    instead: "Chamber heater OFF, door open, glass top removed for PLA (and generally TPU)"
---

# Practice

The Plus 4's chamber heater helps some materials and actively harms others. The
rule by material:

- **Chamber ON (50–65°C):** ABS, ASA (~50–60°C), PC and PA/nylon-CF (~55–65°C),
  PPS-CF (~65°C). These want the warm enclosure to avoid warping and layer
  cracking.
- **Chamber OFF + door open + glass top removed:** **PLA** and generally
  **TPU**. PLA in a hot sealed chamber heat-creeps (softens above the heat
  break, then clogs) and loses cooling; the printer itself warns against running
  fully enclosed with low-temp filament.
- **PETG:** closed chamber is fine, no active heat needed.

Practical rule: door/top open + heater off for PLA and TPU; closed (heat
optional) for PETG; heater on for the engineering/CF materials.

# Why it matters

Heat creep is the headline trap on this machine. A PLA print that clogs
mid-way, or a part that comes out under-cooled and drooping, usually traces to
running PLA in the heated/sealed enclosure instead of opening it up. See
[[qidi-plus-4-hardware-profile]] for the chamber spec.
