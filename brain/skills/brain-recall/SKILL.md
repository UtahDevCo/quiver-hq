---
name: brain-recall
description: Look up what the brain knows about a topic, resolving meta practices against the current project's overrides. Use when about to write code and you want the established practice, when the user asks "what do we do for X", "what's our convention for X", "how do we usually handle X", or before making a technology choice that may already have a documented default.
type: Skill
---

# brain-recall

Answer from the brain, with project overrides correctly applied. The reason
this is a skill and not just "read the files" is the resolution order — getting
that wrong means confidently applying a practice a project has explicitly
suspended.

## Steps

1. **Determine the project scope.** From `$PWD`:
   - Inside `~/dev/quiver-hq/projects/<name>/` → project is `<name>`; its layer
     is `.brain/` (or `~/dev/quiver-hq/brain/projects/<name>/`).
   - Elsewhere → meta only. Say so, because the answer may be incomplete for a
     project that has overrides.

2. **Read the meta index** at `~/dev/quiver-hq/brain/meta/index.md` and select
   candidate concepts by topic. Read the full concept files — the index lines
   are deliberately lossy and are not a substitute.

3. **Read the project's overrides** in
   `brain/projects/<name>/overrides/`, plus anything relevant in that project's
   `invariants/`, `gems/`, and `decisions/`.

4. **Resolve**, per `brain/conventions.md`:

   | `mode` | Effect |
   |---|---|
   | `replace` | The override wins outright. Do not report the meta rule as applicable. |
   | `narrow` | Meta rule holds, with the documented carve-out. Report both. |
   | `extend` | Meta rule holds, plus the project's additions. Report both. |
   | `suspend` | Meta rule does **not** apply here. Report it separately as a known gap, with its `stale_after`. |

   A `Practice Override` whose `overrides:` path does not resolve is an error —
   report it, do not guess which practice was meant.

5. **Answer, then flag.** Lead with the resolved practice. Then surface, only if
   present:
   - **Stale** — `today >= stale_after`. Say the practice may be out of date and
     give the date.
   - **Unverified** — no `verified` entry, i.e. no human has reviewed it. Say so
     before the user acts on it.
   - **Deprecated** — never present a `status: deprecated` concept as current.
     Follow its `relations: superseded-by` and answer from the successor,
     mentioning the supersession.
   - **Expired suspension** — a `suspend` past its `stale_after`. The project is
     out of compliance and the exception was supposed to be revisited.

6. **Cite paths.** Every claim gets a `brain/...` path so Chris can jump to it
   and correct it. An uncited recall is indistinguishable from you making it up.

## When the brain is silent

Say so plainly — "the brain has nothing on X" — then answer from your own
judgment, clearly marked as *not* an established practice. Do not dress up a
default as a documented convention.

Then offer to `/brain-push` your answer, so the next lookup is not silent.
That is how the brain fills in: at the moment the gap is discovered.
