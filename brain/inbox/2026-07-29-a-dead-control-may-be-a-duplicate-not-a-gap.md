---
name: a-dead-control-may-be-a-duplicate-not-a-gap
description: A setting whose value never reaches the backend might be a redundant second source of truth, not missing plumbing — check whether the backend already has that value before wiring it up.
metadata:
  type: project
---

Wiley's quiet-hours drawer had a timezone picker whose value never reached
NetSapiens. The obvious reading — "a gap; send the value" — was wrong. Onboarding
already set the NetSapiens domain `time-zone` from the **service address**, and
address edits kept it current. Timeframes had always evaluated in a real zone. The
picker was a **duplicate** of a control that already worked, one card higher up the
same settings page.

Wiring it through would have **shifted 53 live customers' quiet windows by 1–2
hours**. Deleting it changed no behaviour at all and stopped the UI misreporting
the zone to 85 accounts.

**Why:** a dead input looks like an unfinished feature, and "finish it" is the
default instinct. But two writers for one backend field is a defect regardless of
which one wins, so the first question is *which* should own it — not *how* to
connect the one you happen to be looking at. Connecting it ships a behaviour
change to everyone whose two values disagree, and that population is invisible
until you measure it.

**How to apply:**

- Before plumbing a setting through, grep the backend field name. If something
  else already writes it, you have a duplicate-ownership question, not a bug.
- Pick the owner by which source describes the *subject*, not the *operator*. Here
  the phone's location (service address) beats the person's browser.
- Measure the disagreeing population before choosing. Removal is a no-op for
  everyone; connecting it is a behaviour change for exactly those accounts.
- **Compare semantically, not by string.** `America/Chicago` vs `US/Central` made
  a naive diff report 397/397 mismatches; resolving both to a UTC offset at a
  fixed instant gave the real answer, 85. A scary number from a lazy comparison
  will send you at the wrong fix.
- Watch for defaults derived from the client environment
  (`Intl.DateTimeFormat().resolvedOptions().timeZone`, locale, clock). They record
  where the *configuring human* was, which is not the same as the thing being
  configured — and they silently produce garbage when someone sets up on behalf of
  another, or while travelling.
- A narrower option list than the authoritative control is a tell: the picker
  offered 4 US zones, the address control 11, so some customers could not express
  their own zone at all.

Related: [[probe-the-api-before-trusting-a-code-comment]],
[[audits-must-report-their-own-coverage]]
