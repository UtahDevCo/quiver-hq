---
type: Failure Mode
title: An audit that silently skips what it cannot read reports a falsely reassuring zero
description: Print attempted, inspected, and skipped-by-reason. "Zero findings" and "zero findings among what I could read" are different claims, and only the first one stops the investigation.
tags: [auditing, observability, error-handling, scripts]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-29T20:23:37Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "`const x = await fetch(id).catch(() => null); if (x === null) continue;`"
    why: "converts \"couldn't check\" into \"checked, fine\" at every call site, and the summary count then reads as complete"
    instead: "tally the skip with its reason, and print effective coverage alongside the finding count"
  - term: "reporting `Found 0 divergences` from a scan that had unreadable items"
    why: "a clean report is exactly what makes someone close the investigation"
    instead: "`0 findings among 966/1058 readable (91%) — this is a floor, not a total`"
  - term: "auditing only your own datastore when two systems can diverge"
    why: "damage in the system you don't control is invisible by construction, especially if failed writes roll your side back"
    instead: "audit the side you don't own; that is where the divergence lives"
sources:
  - id: wiley-quiet-hours-sweep
    resource: projects/wiley
    title: wiley — NetSapiens quiet-hours fleet sweep over 1058 accounts, 2026-07-29
    author: claude/opus-5
    last_modified: 2026-07-29
---

# The trap

A fleet sweep over 1058 accounts printed **"0 accounts with divergence."** The
scan loop was:

```ts
const tfs = await ns.getTimeframes(domain).catch(() => null);
if (tfs === null) continue;   // unreadable looks identical to clean
```

92 domains were returning `401 Invalid Scope` and being skipped silently. Adding
coverage accounting turned the same run into **24 divergent accounts, 8 customers
unable to receive any calls.**

The defect is structural, not a typo. `.catch(() => null)` plus `continue` is the
natural way to write a resilient scanner, and it launders "couldn't check" into
"checked, fine" at every call site.

# What to do instead

- Print **attempted, successfully inspected, skipped by reason**, and an explicit
  effective-coverage figure.
- State the epistemic status in the output itself: *"N findings among M readable —
  this is a floor, not a total."*
- List a few skipped items so the gap is investigable rather than abstract.
- Then actually close the gap. Here, checking the 92 showed all returned 404 from
  `getDomain` — not provisioned upstream at all — which legitimately reduced the
  floor to the total. That conclusion required a second script, not an assumption.

# The two-system corollary

When two systems can diverge, audit the one you don't control. A Firestore-only
audit could not see the broken accounts *by construction*, because the failed
saves rolled Firestore back — leaving your own datastore in the state you'd
expect while the upstream one was wrong.

Closely related: [verify-a-write-actually-happened](verify-a-write-actually-happened.md),
which is how the divergence got created in the first place.
