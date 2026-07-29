# Child Agent Protocol (Soloterm lanes)

You were spawned by a **mother** (a Claude/Codex/etc. session driving `solo-orch`)
as a worker on ONE **lane** of a larger task. Your launch prompt gave you:

```
SOLO_PROJECT_ID    the Solo project id
SOLO_SCRATCHPAD_ID the shared "orchestration" scratchpad id
SOLO_LANE          your lane name (e.g. code | test | docs | infra)
SOLO_TODO_ID       the todo you own
SOLO_CHILD_LIB     path to the helper lib (quiver-hq/solo/solo-child-lib.sh)
```

The `solo` CLI is on PATH and authenticated. Follow these steps in order.

## 1. Export your context, then load the helper
```bash
export SOLO_PROJECT_ID SOLO_SCRATCHPAD_ID SOLO_LANE SOLO_TODO_ID   # set to the values above
source "$SOLO_CHILD_LIB"
```

## 2. Orient — read the shared plan (source of truth)
```bash
solo scratchpads read "$SOLO_SCRATCHPAD_ID" --project-id "$SOLO_PROJECT_ID" --mode content
```

## 3. Claim your todo
```bash
solo todos update "$SOLO_TODO_ID" --project-id "$SOLO_PROJECT_ID" --status in_progress
```
Statuses: `open` → `in_progress` → `completed`.

## 4. Do the work — stay inside your lane
Modify only files your lane owns. Disjoint ownership is what makes parallel
lanes safe. Need something another lane owns? Post a NEEDS note, don't reach in:
```bash
solo_needs "blocked on: <thing> owned by <other lane>"
```

## 5. Report findings (revision-guarded, safe under concurrency)
```bash
solo_append "### [$SOLO_LANE] progress
- did X in path/to/file
- decision: chose Y because Z"
```

## 6. Finish
```bash
solo_append "### [$SOLO_LANE] DONE
- deliverables: <files / PR>
- how to verify: <command or steps>"
solo todos complete "$SOLO_TODO_ID" --project-id "$SOLO_PROJECT_ID"
```

## 7. Push learnings up to the brain
Before you exit, ask: **did I learn something that outlives this lane?** A
convention, a reusable pattern, a gotcha that cost you time, a dependency that
behaved unexpectedly. If so, record it — you are the only session that will ever
have this context:

```bash
brain_push <kind> "<title>" "<evidence path:line>" [meta|project]
#   kind: practice|pattern|failure-mode|stack|workflow|module|invariant|decision
brain_push failure-mode "Vitess rejects nested reads without companyId" \
           "domains/billing/queries/get-invoice.ts:88"
```

This appends to `~/dev/quiver-hq/brain/inbox/` for Chris to review via
`/brain-promote`. It is fire-and-forget — you do not wait, and you do not
decide where it belongs.

Rules: default to `project` (promotion can lift it later; a wrong `meta`
practice silently applies everywhere). Always pass evidence. One call per
learning. **Never write to `brain/meta/` and never set `verified`.**

Nothing generalizable? Skip this step — an inbox of noise is worse than an empty
one.

## Rules
1. One lane only — never edit outside your ownership.
2. Scratchpad is truth — read before acting, append (never overwrite) results.
3. Cross-lane deps go through NEEDS notes; the mother integrates deliberately.
4. Always leave a DONE block so the mother can integrate without re-reading your diff.
5. Push durable learnings to the brain inbox; never write to `brain/meta/` directly.
