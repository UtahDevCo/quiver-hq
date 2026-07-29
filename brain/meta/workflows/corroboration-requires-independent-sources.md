---
type: Workflow
title: Two sources only corroborate if they are independent — check for a shared ancestor first
description: Before counting two repos as agreement, diff their convention docs. Generated or copied files make one document look like two, and the check costs one grep.
tags: [brain, harvest, methodology, evidence]
generated: { by: claude/opus-5, at: 2026-07-29T22:55:47Z }
verified:
  - { by: human:christopher, at: 2026-07-29T22:55:47Z }
status: stable
stale_after: 2027-07-29
not:
  - term: "\"it appears in two repos' AGENTS.md, so it's general\""
    why: "convention docs get copied between repos and generated from templates; the second copy is not a second observation"
    instead: "diff them first, and prefer evidence from code the docs never mention"
  - term: "counting a rule stated in a doc as equal evidence to a rule visible in code"
    why: "a doc records an intention, which may never have been followed; code records what actually happens"
    instead: "weight independent code evidence above documentation, and say which kind you have"
sources:
  - id: tools-trikin-diff
    resource: projects/trikin/AGENTS.md
    title: "trikin/AGENTS.md — 59 of 118 non-blank lines byte-identical to tools/AGENTS.md, header reads \"Auto-generated from all feature plans\""
    last_modified: 2026-07-29
---

# The rule

Before recording a practice as corroborated by two repos, verify the two sources are
actually independent. Generated, scaffolded, or copy-pasted convention files make a
single document look like consensus.

# The check

```bash
# how many non-trivial lines are byte-identical?
grep -Fxf a/AGENTS.md b/AGENTS.md | awk 'length>25' | wc -l
grep -c . a/AGENTS.md   # denominator
```

Also read the top of the file. A header like `Auto-generated from all feature plans`
settles it immediately.

If overlap is high, the two files are **one** source. Look for evidence in code that
the docs do not mention, which cannot have been copied.

# What this cost when skipped

Harvesting `tools`, `trikin`, and wiley to test 19 zamp-only practices, three
subagents independently reported broad agreement between `tools` and `trikin` — the
same rules, in the same order, often in the same words. That reads as strong
corroboration.

`trikin/AGENTS.md` shares **59 of its 118 non-blank lines byte-identically** with
`tools/AGENTS.md`, and the shared block opens `Auto-generated from all feature plans`.
Roughly a dozen rules were one template counted twice. Re-scoring on code evidence
alone changed the verdict on several, and demoted three concepts out of the meta
layer entirely.

# The ranking to use

1. **Independent code in 2+ repos** — strongest. Nobody had to be reminded.
2. **A completed migration away from something** — very strong. Somebody paid.
3. **Chris's explicit assertion** — outranks corroboration by
   [convention](../../conventions.md); record it as `author: human:christopher` so a
   reviewer can tell a declared standard from an inferred one.
4. **Independent documentation in 2+ repos** — moderate. Verify independence first.
5. **One repo's documentation** — a project-layer observation, not a practice.

# The inverse error

Absence is not disagreement. wiley has no test files, so it cannot corroborate a
testing practice — but it does not contradict one either. Report *unfalsifiable
here* separately from *contradicted here*, per
[audits-must-report-their-own-coverage](../failure-modes/audits-must-report-their-own-coverage.md).
