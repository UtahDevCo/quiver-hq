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

# Push a learning up to the brain's inbox (~/dev/quiver-hq/brain/inbox/).
# Cheap and fire-and-forget: Chris reviews via /brain-promote. Never writes to
# brain/meta/ and never sets `verified` — see brain/conventions.md.
#
#   brain_push <kind> <title> [evidence] [layer]
#     kind      practice|pattern|failure-mode|stack|workflow|module|invariant|decision
#     title     one line; becomes the concept title
#     evidence  path:line, commit, or URL (optional but strongly preferred)
#     layer     meta|project  (default: project — promotion can lift, not un-apply)
brain_push() {
  local kind="$1" title="$2" evidence="${3:-}" layer="${4:-project}"
  local brain="$HOME/dev/quiver-hq/brain" inbox slug stamp file project

  [ -n "$kind" ] && [ -n "$title" ] || { echo "brain_push: need <kind> <title>" >&2; return 2; }
  inbox="$brain/inbox"
  [ -d "$inbox" ] || { echo "brain_push: no brain inbox at $inbox" >&2; return 1; }

  # -E because BSD sed has no \+ in basic regex.
  slug="$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]' \
          | sed -E -e 's/[^a-z0-9]+/-/g' -e 's/^-+//' -e 's/-+$//' | cut -c1-60)"
  stamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  file="$inbox/$(date -u +%Y-%m-%d)-${slug:-observation}.md"
  # Collide-proof without clobbering a sibling lane's push.
  [ -e "$file" ] && file="${file%.md}-$$.md"

  # Infer the project from $PWD when inside a quiver-hq submodule.
  project="$(printf '%s' "$PWD" | sed -n 's|.*/quiver-hq/projects/\([^/]*\).*|\1|p')"

  {
    printf -- '---\n'
    printf 'type: Observation\n'
    printf 'title: %s\n' "$title"
    printf 'kind: %s\n' "$kind"
    printf 'proposed_layer: %s\n' "$layer"
    # observed_in is provenance (always); proposed_project is a placement
    # request, so it must not contradict proposed_layer: meta.
    [ -n "$project" ] && printf 'observed_in: %s\n' "$project"
    [ -n "$project" ] && [ "$layer" = "project" ] && printf 'proposed_project: %s\n' "$project"
    printf 'generated: { by: %s, at: %s }\n' "${BRAIN_ACTOR:-claude/unknown}" "$stamp"
    printf 'status: draft\n'
    if [ -n "$evidence" ]; then
      printf 'sources:\n  - id: evidence\n    resource: %s\n' "$evidence"
    fi
    printf -- '---\n\n# Observation\n\n%s\n' "$title"
    [ -n "${SOLO_LANE:-}" ] && printf '\nSurfaced by lane `%s` during a Solo orchestration run.\n' "$SOLO_LANE"
    [ -n "$evidence" ] && printf '\n# Evidence\n\n%s\n' "$evidence"
    printf '\n# Review notes\n\nPushed from a child agent with minimal context. Verify against the\nevidence before promoting.\n'
  } > "$file"

  echo "brain_push: $file"
}
