---
name: brain-harvest
description: Crawl a repository and extract its accumulated knowledge into the brain's inbox — coding practices, reusable component patterns, architectural decisions, and gotchas. Use when the user says "harvest <project>", "extract learnings from <repo>", "mine this repo for patterns", or points at a new codebase and asks what's worth keeping. Reads agent context files (AGENTS.md, CLAUDE.md, .coderabbit.yaml, .cursor/rules, skills, subagents) first, then code.
type: Skill
---

# brain-harvest

Extract what a repo already knows about itself into `brain/inbox/`, classified
meta vs project, for Chris to promote.

**Usage:** `/brain-harvest <project>` where `<project>` is a directory under
`~/dev/quiver-hq/projects/`.

The highest-value material is not the code — it is the **agent context files**,
because those are already distilled knowledge someone wrote down deliberately.
Read those first and exhaustively. Code-reading is a second pass for named gems.

## Hard rules

- **Write only to `brain/inbox/`.** Never to `meta/` or `projects/`. Promotion
  is a separate, human-gated step. This two-phase split is the only thing
  keeping the meta layer from filling with a subagent's guesses about what's
  "general."
- **Never add a `verified:` entry.**
- **Never harvest `projects/k1-fork`.** Third-party code; its conventions are
  not ours. If asked, decline and say why.
- One observation per file. See `/brain-push` for the frontmatter shape.

## Phase 1 — inventory the context surface

Find, and read completely, whichever of these exist:

| Source | Why it matters |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | The main distillation. Usually the richest single file. |
| `CLAUDE.local.md` | **Read this carefully.** Git-ignored, so it holds Chris's *personal* practices — disproportionately likely to be genuinely meta. |
| `.coderabbit.yaml` | Review rules. Often encodes conventions absent from AGENTS.md. |
| `.cursor/rules/*.mdc` | Pattern-triggered rules. Frequently the sharpest invariants. |
| `.claude/skills/*/SKILL.md` | Encoded workflows. |
| `.claude/agents/*.md` | Reviewer subagents — these are invariants in prose form and the best source of `Invariant` candidates. |
| `README`, `CONTRIBUTING`, `docs/` | Setup and architecture. Usually project-specific. |

Note that `*.local.md` files and `.claude/agents/` entries may be symlinks into
`~/dev/quiver-hq/local/<project>/`. Follow them; that is the canonical store.

## Phase 2 — classify

For every distinct rule, convention, or pattern, apply the test from
`brain/conventions.md`: **would you want this applied to a brand-new empty
repo?**

| Signal | → Layer |
|---|---|
| Names a package, table, port, env var, internal path, or vendor | `project` |
| A language/framework-level rule with no local nouns | `meta` |
| Appears in a *reviewer subagent* | usually `project` invariant, sometimes meta practice |
| Found in `CLAUDE.local.md` | lean `meta` — it's Chris's own, not the team's |
| A build/test command | `project`, low value; skip unless non-obvious |

**Check corroboration before proposing `meta`.** Read
`brain/meta/index.md` and the other `brain/projects/*/` layers. A rule
appearing independently in two or more repos is genuinely general — say so in
the body, and cite both, because that is the strongest promotion argument
available. A rule seen once is `project` until proven otherwise; add
`relations: [{kind: instance-of, target: /meta/...}]` if a meta concept it
might instantiate already exists.

**When unsure, propose `project`.** Promotion can lift; silently applying a
wrong meta practice everywhere is the more expensive error.

## Phase 3 — code gems (only when asked, or when the user names one)

If the user names a specific artifact ("the drawer in wiley", "zamp's design
system"), read it and capture what makes it *non-trivial*: the API surface,
state model, accessibility handling, animation approach, and its dependencies —
portability is the thing that decides whether it can be reused. A `Pattern`
observation that just says "there's a good drawer" is worthless.

For large repos, fan out with parallel `Explore` subagents over disjoint
directories rather than reading serially. Ask before spawning more than three.

## Phase 4 — write and report

Write each observation to `brain/inbox/<UTC-date>-<slug>.md` using the
`/brain-push` frontmatter. Set `proposed_project` on project-layer items. Add
`not:` entries wherever the repo documents an anti-pattern — those files are
full of them and they are the most valuable thing you will extract.

Then report **one table**, nothing else:

| # | Title | kind | layer | corroboration | evidence |
|---|---|---|---|---|---|

End with: total count, and an explicit list of anything you **declined** to
harvest with the reason. Silent omission reads as complete coverage when it
isn't.

Do not summarize the observations in prose. Chris reviews them at
`/brain-promote` time; a second summary here is wasted context.

## Scale

A repo like `zamp` (271-line `AGENTS.md`, a `.coderabbit.yaml`, `.cursor/rules`,
19 subagents, a 117-component design system) yields roughly 20–30 observations.
If you produce fewer than 10 from a repo that rich, you skimmed — go back to the
files you did not open.
