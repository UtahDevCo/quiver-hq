#!/usr/bin/env bash
# quiver-hq/solo/solo-child-lib.sh — helpers a spawned child agent sources.
# Requires exported env: SOLO_PROJECT_ID, SOLO_SCRATCHPAD_ID. Requires: solo, jq.

solo_revision() {
  solo scratchpads list --project-id "$SOLO_PROJECT_ID" --json \
    | jq -r --argjson id "$SOLO_SCRATCHPAD_ID" '.data.scratchpads[]|select(.id==$id)|.revision'
}

# Append text to the shared scratchpad, revision-guarded, retrying on conflict.
solo_append() {
  local text="$1" rev attempt
  for attempt in 1 2 3 4 5; do
    rev="$(solo_revision)"
    if solo scratchpads append "$SOLO_SCRATCHPAD_ID" --project-id "$SOLO_PROJECT_ID" \
         --content "$text" --expected-revision "$rev" --newline --json \
         | jq -e '.ok == true' >/dev/null; then
      return 0
    fi
    sleep 0.4   # lost the race to a sibling; re-read revision and retry
  done
  echo "solo_append: failed after retries (revision churn?)" >&2
  return 1
}

solo_needs() { solo_append "### [${SOLO_LANE:-?}] NEEDS
$1"; }
