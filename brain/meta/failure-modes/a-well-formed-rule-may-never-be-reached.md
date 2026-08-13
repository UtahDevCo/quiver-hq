---
type: Failure Mode
title: A well-formed rule may never be reached
description: An audit passed 281 of 289 accounts on four per-rule checks. Three of the passes were wrong, because a catch-all rule at a lower ordinal took every call before the correct rule ran.
tags: [auditing, rules-engines, ordering, reachability]
generated: { by: claude/opus-5, at: 2026-08-12T19:40:27Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/audits-must-report-their-own-coverage.md }
not:
  - term: "scoring each rule on its own fields and calling the healthy ones enforced"
    why: "a rule can be enabled, correctly configured, and pointed at the right window while an earlier rule that also matches takes every call"
    instead: "check the rule's position against every earlier rule that also matches, and report reachability as its own verdict"
  - term: "assuming which end of the ordinal range wins"
    why: "lowest-first and highest-first are both common, and an audit built on the wrong assumption inverts every verdict it produces"
    instead: "stage two rules that match at the same moment and read back which one the platform marks active"
  - term: "a reachability audit that emits only pass and fail"
    why: "a rule nobody could classify and a rule that reached correctly land in the same bucket, so a run that classified nothing looks like a run that found nothing wrong"
    instead: "emit reached, shadowed, no-rule and unreadable, and print the reached count as a control"
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/audit-quiet-hours-rule-order.ts
    title: audit that measures reachability rather than per-rule validity
    author: claude/opus-5
    last_modified: 2026-08-12
  - id: probe
    resource: projects/wiley/web/scripts/probe-answerrule-shadowing.ts
    title: probe establishing lowest-ordinal-wins by staging two simultaneously-matching rules
    author: claude/opus-5
    last_modified: 2026-08-12
---

# The trap

When a system evaluates an ordered list of rules and the first match wins, auditing
each rule against its own fields measures whether the rule is well-formed. Whether
the rule ever runs is a different question, and the two get conflated because a
per-rule check produces a satisfying per-rule verdict.

Reachability has a separate input: the rule's position relative to every earlier rule
whose match condition overlaps. A rule sitting behind an unconditional earlier rule is
dead no matter how correct it is.

This applies anywhere ordered matching decides behaviour, including firewall and ACL
chains, route tables, IAM policy evaluation, CSS specificity, middleware stacks, and
answering rules in a phone system.

# Why it matters

An audit of 289 accounts reported 281 as having quiet hours enforced. It checked four
things per account: the timeframe exists, the answering rule exists, the rule is
enabled, Do Not Disturb is set. Three accounts passed all four and were still wrong,
because their catch-all rule sat at a lower ordinal than the QuietHours rule and took
every call first.

Every field the audit knew to look at was correct, so there was nothing to flag, and
the audit's confidence rose as the checks passed.

# Evidence

Two accounts, same platform, opposite outcomes:

    healthy    QuietHours prio 0   enabled=yes dnd=yes
               *          prio 99  enabled=yes
    broken     *          prio 0   enabled=yes dnd=yes
               QuietHours prio 99  enabled=yes dnd=yes

Both rows of the broken account pass a per-rule check.

Evaluation order was established rather than assumed, by staging two rules that both
matched at the same moment and reading back which one the platform marked
`is-active`. The rule at ordinal 7 took it from the catch-all at 99. That read is
itself subject to
[an-eventually-consistent-field-answers-confidently-wrong](an-eventually-consistent-field-answers-confidently-wrong.md),
which is why the probe waits before believing the flag.

The corrected audit reports reachability as its own verdict (`reached`, `shadowed`,
`no-rule`, `unreadable`) and prints how many accounts reach their rule as a control,
so a run that classifies nothing is distinguishable from a run that finds nothing
wrong. That separation is
[audits-must-report-their-own-coverage](audits-must-report-their-own-coverage.md).
