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

# Attestation candidate

The size limit is mechanically checkable over changed files with the exemptions
encoded, and is the best first `Invariant` in the brain.
