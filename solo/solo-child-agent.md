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

## Rules
1. One lane only — never edit outside your ownership.
2. Scratchpad is truth — read before acting, append (never overwrite) results.
3. Cross-lane deps go through NEEDS notes; the mother integrates deliberately.
4. Always leave a DONE block so the mother can integrate without re-reading your diff.
