---
name: brain-push
description: Record a learning into the brain's inbox for later review. Use when you or the user discover something worth keeping — a coding practice, a reusable pattern, a gotcha, a technology choice, or a project-specific rule. Also use when the user says "remember this", "add this to the brain", "push this up", or "that's a good practice". Cheap and fast; bias toward recording.
type: Skill
---

# brain-push

Append one observation to `~/dev/quiver-hq/brain/inbox/`. That is the whole job.

You are **not** deciding where the knowledge belongs, whether it's already
known, or whether it's true. `/brain-promote` does that later, with Chris in the
loop. Your job is to capture it before it evaporate, with enough evidence that a
future reviewer can verify it.

## Do not

- **Do not write to `brain/meta/` or `brain/projects/`.** Inbox only.
- **Do not add a `verified:` entry.** Only Chris verifies. See
  `brain/conventions.md`.
- Do not deduplicate against existing concepts. Cheap duplicates are fine;
  promotion merges them. Hesitating is what loses the learning.

## Steps

1. **Classify** — pick `kind` and a proposed layer.

   `kind` is one of: `practice`, `pattern`, `failure-mode`, `stack`,
   `workflow`, `module`, `invariant`, `decision`.

   `proposed_layer` is `meta` or `project`. The test, from
   `brain/conventions.md`: *would you want this applied to a brand-new empty
   repo?* If yes → `meta`. If it names a specific package, table, port, or
   internal path → `project`. **When unsure, propose `project`.** Promotion can
   lift a project concept to meta; demoting a wrong meta practice is worse,
   because it has been silently applied everywhere in the meantime.

2. **Gather evidence.** At least one `sources` entry pointing at a real file
   and line, a commit, or a URL. An observation with no evidence is nearly
   unpromotable — if you truly have none, say so in the body.

3. **Write the file** to
   `~/dev/quiver-hq/brain/inbox/<UTC-date>-<slug>.md`:

   ```bash
   date -u +%Y-%m-%d    # use this for the filename prefix
   date -u +%Y-%m-%dT%H:%M:%SZ    # use this for generated.at
   ```

   ```yaml
   ---
   type: Observation
   title: Don't rewrap an existing Err
   description: Returning an existing Err as-is preserves the stack and cause chain.
   kind: practice
   proposed_layer: meta
   tags: [error-handling, typescript]
   generated: { by: claude/opus-5, at: 2026-07-28T18:22:04Z }
   status: draft
   sources:
     - id: evidence
       resource: projects/zamp/AGENTS.md
       title: zamp AGENTS.md error-handling section
       last_modified: 2026-07-25
   ---

   # Observation

   <What the learning is. Be specific enough to act on.>

   # Why it matters

   <The consequence of getting it wrong. This is the part reviewers use to
   decide whether it's real.>

   # Evidence

   <Code, a diff, a failure you hit. Concrete beats abstract.>
   ```

   Set `proposed_project: <name>` when `proposed_layer: project`.

4. **Add `not:` if you can.** If the learning has a tempting wrong version,
   record it — negative knowledge is the most valuable thing here:

   ```yaml
   not:
     - term: "Err(new Error('failed', { cause: result.error }))"
       why: "rewrapping hides the inner stack and cause chain"
       instead: "if (result.isErr()) return result"
   ```

5. **Confirm in one line.** `Pushed: <title> → inbox (kind, proposed layer)`.
   Do not summarize the whole file back.

## Multiple learnings

One file per learning. Do not batch several practices into one observation —
promotion places files individually, and a merged observation forces a split
later. If you have five, write five files.
