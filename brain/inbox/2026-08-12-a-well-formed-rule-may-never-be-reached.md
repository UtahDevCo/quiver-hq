---
type: Observation
title: A well-formed rule may never be reached
description: Per-rule health checks answer "is this rule valid", then get read as "does this rule take effect". In an ordered first-match-wins evaluator those are different questions.
kind: failure-mode
proposed_layer: meta
tags: [auditing, rules-engines, ordering, netsapiens]
generated: { by: claude/opus-5, at: 2026-08-12T19:40:27Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/audit-quiet-hours-rule-order.ts
    title: audit that measures reachability rather than per-rule validity
    last_modified: 2026-08-12
  - id: probe
    resource: projects/wiley/web/scripts/probe-answerrule-shadowing.ts
    title: probe establishing lowest-ordinal-wins by staging two simultaneously-matching rules
    last_modified: 2026-08-12
not:
  - term: "score each rule on its own fields and call the healthy ones enforced"
    why: "a rule can be enabled, correctly configured, and pointed at the right window while an earlier rule that also matches takes every call"
    instead: "check the rule's position against every earlier rule that also matches, and report reachability as its own verdict"
---

# Observation

When a system evaluates an ordered list of rules and the first match wins,
auditing each rule against its own fields measures whether the rule is
well-formed. It does not measure whether the rule ever runs. Those get conflated
because a per-rule check produces a satisfying per-rule verdict.

Reachability is a separate question with a separate input: the rule's position
relative to every earlier rule whose match condition overlaps. A rule sitting
behind an unconditional earlier rule is dead no matter how correct it is.

This applies anywhere ordered matching decides behaviour: firewall and ACL
chains, route tables, IAM policy evaluation, CSS specificity, middleware stacks,
answering rules in a phone system.

# Why it matters

An audit of 289 accounts reported 281 as having quiet hours enforced. It checked
four things per account: the timeframe exists, the answering rule exists, the
rule is enabled, Do Not Disturb is set. Three accounts passed all four and were
still wrong, because their catch-all rule sat at a lower ordinal than the
QuietHours rule and took every call first.

The failure is quiet in the worst way. Every field the audit knew to look at was
correct, so there was nothing to flag, and the audit's confidence went up rather
than down as the checks passed.

# Evidence

Two accounts, same platform, opposite outcomes:

    healthy    QuietHours prio 0   enabled=yes dnd=yes
               *          prio 99  enabled=yes
    broken     *          prio 0   enabled=yes dnd=yes
               QuietHours prio 99  enabled=yes dnd=yes

Both rows of the broken account pass a per-rule check.

Evaluation order was established rather than assumed, by staging two rules that
both matched at the same moment and reading back which one the platform marked
`is-active`: the rule at ordinal 7 took it from the catch-all at 99.

The corrected audit reports reachability as its own verdict (`reached`,
`shadowed`, `no-rule`, `unreadable`) and prints how many accounts reach their
rule as a control, so a run that classifies nothing is distinguishable from a
run that finds nothing wrong.
