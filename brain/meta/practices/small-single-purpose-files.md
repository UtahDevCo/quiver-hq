---
type: Practice
title: Small files, one primary export, nothing orphaned
description: Around 200 lines for logic and 300 for components, one primary export, and dead code removed in the change that orphaned it.
tags: [file-organization, review, maintainability]
generated: { by: claude/opus-5, at: 2026-07-29T14:01:48Z }
verified:
  - { by: human:christopher, at: 2026-07-29T18:53:32Z }
status: stable
stale_after: 2027-07-29
sources:
  - id: coderabbit
    resource: projects/zamp/.coderabbit.yaml
    title: .coderabbit.yaml — global path instructions
    author: human:christopher
    last_modified: 2026-07-25
  - id: trikin-counterexample
    resource: projects/trikin
    title: "trikin — a repo where the rule is not followed: sync-leads.ts 1821 lines, pull-from-atlas.ts 913, queries/leads.ts 861, admin-leads-table.tsx 757"
    last_modified: 2026-07-30
---

# The practice

- **Size:** under ~200 lines for logic files, ~300 for component files.
  **Exempt:** tests, stories, configuration, documentation.
- **One primary export per file.**
- **Remove orphaned code in the same change that orphaned it.**
- Avoid mutable state where practical.
- Keep `try`/`catch` focused — avoid several unrelated awaits in one block.

# Why a line count

It's a crude proxy for single responsibility, and its virtue is that it's cheap to
check and hard to argue with. "This file does too much" is a debate; "this file is
430 lines" is not.

**The exemption list matters as much as the limit.** Tests, stories, and config
are legitimately long. Flagging them trains people to ignore the rule, and a rule
that's routinely ignored is worse than no rule.

# Why orphaned code is grouped here

The change that stops calling something is the only moment anyone knows it's dead.
A follow-up cleanup never gets scheduled, and six months later nobody can prove
the code is unreachable. Delete it while you still have the evidence.

# One repo demonstrates it, one aspires to it

Worth knowing before quoting this as a house standard. zamp encodes the limit in
`.coderabbit.yaml` and follows it. trikin's `AGENTS.md` does not state it, and the
repo runs to `sync-leads.ts` at 1,821 lines, `pull-from-atlas.ts` at 913,
`queries/leads.ts` at 861, and `admin-leads-table.tsx` at 757 against a ~300-line
component budget.

That is a negative corroboration result and it stands. Under "the brain describes,
it does not retrofit" those files are not a defect list, and most of them are being
deleted in trikin's pivot anyway.

# Attestation candidate

The size limit is mechanically checkable over changed files with the exemptions
encoded, and is the best first `Invariant` in the brain.
