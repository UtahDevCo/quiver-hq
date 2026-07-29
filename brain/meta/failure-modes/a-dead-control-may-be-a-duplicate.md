---
type: Failure Mode
title: A dead control may be a duplicate, not a gap
description: A setting whose value never reaches the backend might be a redundant second writer, not missing plumbing. Grep the backend field before wiring it up — connecting it ships a behaviour change to everyone whose two values disagree.
tags: [product, settings, duplicate-state, migration, timezones]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T23:10:47Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "wiring up a setting whose value is never sent, because the plumbing is obviously missing"
    why: "two writers for one backend field is a defect regardless of which wins; connecting the one you happen to be looking at ships a behaviour change to every account whose two values disagree"
    instead: "grep the backend field name first — if something else already writes it, you have a duplicate-ownership question, not a bug"
  - term: "defaulting a setting from the client environment (Intl.DateTimeFormat().resolvedOptions().timeZone, locale, system clock)"
    why: "records where the configuring human was, not the thing being configured — silently wrong when someone sets up on behalf of another, or while travelling"
    instead: "derive it from a property of the subject; here the phone's service address, not the admin's browser"
  - term: "comparing two config values as strings to size the affected population"
    why: "America/Chicago vs US/Central are the same zone; a naive diff reported 397/397 mismatches when the real answer was 85"
    instead: "resolve both to a canonical form — for zones, a UTC offset at a fixed instant — before counting"
sources:
  - id: wiley-quiet-hours-timezone
    resource: projects/wiley
    title: "wiley — quiet-hours timezone picker, found redundant 2026-07-29"
    author: claude/opus-5
    last_modified: 2026-07-29
---

# The trap

A quiet-hours drawer had a timezone picker whose value never reached the vendor API.
The obvious reading — *a gap, send the value* — was wrong.

Onboarding already set the vendor domain's `time-zone` from the **service address**,
and address edits kept it current. Timeframes had always evaluated in a real zone. The
picker duplicated a control that already worked, one card higher on the same settings
page.

Wiring it through would have **shifted 53 live customers' quiet windows by 1–2 hours.**
Deleting it changed no behaviour and stopped the UI misreporting the zone to 85
accounts.

# Why the instinct is wrong

A dead input looks like an unfinished feature, and "finish it" is the default move.
But two writers for one backend field is a defect whichever one wins, so the first
question is *which should own it* — not *how to connect the one in front of you*.

The asymmetry decides it: **removal is a no-op for everyone; connecting it is a
behaviour change for exactly the accounts whose two values disagree** — and that
population is invisible until you measure it.

# What to do instead

- Grep the backend field name before plumbing anything through.
- Pick the owner by which source describes the **subject**, not the **operator**. The
  phone's location beats the admin's browser.
- Measure the disagreeing population before choosing, and compare **semantically**.
  See the `not:` entry — a lazy string diff will hand you a scary number and send you
  at the wrong fix.
- Treat a **narrower option list** as a tell: the picker offered 4 US zones, the
  address control 11, so some customers could not express their own zone at all. A
  control that cannot represent the full domain is usually the redundant one.

Related: [audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md)
for sizing the affected population honestly, and
[probe-before-trusting-an-api-claim](probe-before-trusting-an-api-claim.md) — the
same instinct to verify the premise before building on it.
