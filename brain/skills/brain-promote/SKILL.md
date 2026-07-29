---
name: brain-promote
description: Review the brain's inbox and place observations into the meta or project layer with human sign-off. Use when the user says "promote the inbox", "review the brain inbox", "process the brain", or after a harvest. This is the human gate — it is the only path by which anything enters brain/meta/.
type: Skill
---

# brain-promote

Turn reviewed observations into concepts. This is the **only** path into
`brain/meta/` and the only place a `human:` `verified` entry is ever added.

Chris is in the loop for every promotion. You prepare, propose, and execute
after approval — you do not decide.

## Hard rules

- **Never add `verified: human:christopher` without explicit approval** for that
  specific concept in this conversation. Approval of the batch plan is approval
  to write; it is not license to verify things Chris did not look at.
- **Never overwrite a concept that contradicts an incoming observation.**
  Deprecate in place. See below — this is the highest-value behavior in the
  whole brain.
- Delete an inbox file only after its concept is written.

## Steps

### 1. Read the inbox

List `brain/inbox/*.md`. If empty, say so and stop.

Read every observation in full. Also read `brain/meta/index.md`, the relevant
`brain/projects/*/index.md`, and `brain/conventions.md`.

### 2. Triage each observation

Classify into exactly one:

| Verdict | Meaning | Action |
|---|---|---|
| **New** | Nothing covers it. | Place as a new concept. |
| **Duplicate** | An existing concept already says this. | Merge: strengthen the existing concept's `sources`, refresh `stale_after`. Do not create a second file. |
| **Refinement** | Existing concept is right but incomplete. | Edit the existing concept. Add the new evidence to `sources`. |
| **Contradiction** | Existing concept says something *different*. | Deprecate-in-place (§3). Never a silent overwrite. |
| **Promotion** | A `projects/<p>/` concept is corroborated by another repo. | Move to `meta/`, leave a `Practice Override` behind if the origin project's version was narrower. |
| **Reject** | Wrong, hallucinated, or too trivial to keep. | Delete the inbox file, note it in `log.md`. |

Re-check every `proposed_layer: meta`. Harvest is instructed to lean
`project` — but agents still over-generalize. Demote anything whose evidence is
a single repo unless the rule is obviously language-level.

### 3. Contradictions: deprecate, never overwrite

When a practice has genuinely changed:

1. Set the old concept's `status: deprecated`. **Keep the file and its body.**
2. Add `relations: [{kind: superseded-by, target: /path/to/new.md}]`.
3. Add a `# Why this changed` section to the old file: what the old rule was,
   what broke, when it flipped. The reasoning behind a reversal is more valuable
   than either rule alone, and it is exactly what an overwrite destroys.
4. Write the new concept with `relations: [{kind: supersedes, target: <old>}]`
   and a `not:` entry naming the old rule as the tempting wrong answer.

The model is `metrics/gross-margin.md` + `metrics/gross-margin-legacy.md` in the
OKF `acme_retail` bundle. Read it if the shape isn't obvious.

### 4. Propose the batch, then wait

Present one table and **stop for approval**:

| # | Observation | Verdict | → Destination | Notes |
|---|---|---|---|---|

Call out separately, because these are the decisions Chris most needs to see:
- Anything going to `meta/` (it will apply to every project from then on)
- Every contradiction and what gets deprecated
- Anything you demoted from the proposed layer, and why

Do not write anything until Chris responds.

### 5. Execute

For each approved item:

1. Write the concept to its destination. `type` follows `kind`: `practice` →
   `Practice`, `pattern` → `Pattern`, `failure-mode` → `Failure Mode`, `stack` →
   `Stack`, `workflow` → `Workflow`, `module` → `Module`, `invariant` →
   `Invariant`, `decision` → `Decision`. Create subdirectories as needed.
2. Set `generated` to the *original* observation's `generated` — preserve who
   actually wrote it. Then add:
   ```yaml
   verified:
     - { by: human:christopher, at: <now, ISO 8601 UTC> }
   status: stable
   stale_after: <per the conventions table>
   ```
3. Carry `sources` forward. Add the inbox file's own evidence; never drop
   provenance in the move.
4. Preserve and complete `not:` entries. Add `relations:` where a typed edge
   exists.
5. Update the containing `index.md` — one line, `[Title](file.md) - description`
   from the concept's own `description`.
6. **If it landed in `meta/`, update `brain/meta/index.md`.** That file is
   always-on context; a concept missing from it is effectively invisible.
7. Delete the inbox file.

### 6. Log

Append one dated entry to `brain/log.md`, newest-first, recording **why** — not
just what moved. Follow the existing entries' voice. Deprecations and meta
additions always get a line; routine placements can be summarized in one.

### 7. Report

Counts by verdict, the list of new `meta/` concepts, and every deprecation.
Then stop. Do not re-summarize the concepts themselves.

## Keeping the meta index thin

`brain/meta/index.md` is loaded into every session in every project, so its
size is a permanent tax. One line per concept, description only, no prose.

If `meta/` passes ~40 concepts, say so and propose splitting the index by
category with the top-level index linking to sub-indexes — progressive
disclosure is exactly what OKF §8 index files are for.
