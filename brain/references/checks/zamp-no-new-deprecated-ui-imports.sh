#!/usr/bin/env bash
#
# Computation for /projects/zamp/invariants/no-new-deprecated-ui-imports.md
#
# Emits an OKF receipt on stdout. Pipe into references/expect_empty.py.
#
#   usage: zamp-no-new-deprecated-ui-imports.sh [base-ref] [head-ref]
#          defaults: origin/master HEAD
#
# Both ends are parameters so the check can be validated against historical
# ranges without checking anything out — the repo may be someone else's working
# tree, and an attester that requires mutating it is untestable in practice.
#
# Scoped to the diff on purpose. zamp has 88 files importing @util/ui and 145
# using Rt* components; a whole-repo check would fail permanently and carry no
# information. The decision it enforces says only newly added or modified lines
# are violations, so the diff IS the invariant.
#
set -uo pipefail

REPO="${ZAMP_REPO:-$HOME/dev/quiver-hq/projects/zamp}"
BASE="${1:-origin/master}"
HEAD_REF="${2:-HEAD}"
CMD="zamp-no-new-deprecated-ui-imports.sh $BASE $HEAD_REF"

emit() {  # exit_code, then matches as JSON array text
  printf '{"command":"%s","exit_code":%s,"matches":%s}\n' "$CMD" "$1" "$2"
}

cd "$REPO" 2>/dev/null || { emit 3 '[]'; exit 0; }
for r in "$BASE" "$HEAD_REF"; do
  git rev-parse --verify --quiet "$r" >/dev/null || { emit 4 '[]'; exit 0; }
done

# Added lines only (^+), in changed ts/tsx files, excluding the design-system
# packages themselves (they legitimately contain the deprecated wrappers) and
# stories (which demonstrate deprecated components on purpose).
FILES="$(git diff --name-only --diff-filter=d "$BASE".."$HEAD_REF" -- '*.ts' '*.tsx' \
  | grep -Ev '^utils/design-system(-next)?/' \
  | grep -Ev '\.stories\.tsx?$' || true)"

[ -z "$FILES" ] && { emit 0 '[]'; exit 0; }

MATCHES=""
while IFS= read -r f; do
  [ -n "$f" ] || continue
  # Deliberately not testing -f: the refs may be historical, so the path need not
  # exist in the working tree. git diff reads from the object store.
  # -U0 keeps hunk headers so we can recover line numbers for added lines.
  hits="$(git diff -U0 "$BASE".."$HEAD_REF" -- "$f" | awk -v file="$f" '
    /^@@/ { if (match($0, /\+[0-9]+/)) { ln = substr($0, RSTART+1, RLENGTH-1) + 0 }; next }
    /^\+\+\+/ { next }
    /^\+/ {
      line = substr($0, 2)
      # Bare "@util/ui" AND subpaths ("@util/ui/components/..."), but never
      # "@util/ui-templates" — that is a separate, current package.
      if (line ~ /["'"'"']@util\/ui(\/[^"'"'"']*)?["'"'"']/)  print file ":" ln "  @util/ui import"
      else if (line ~ /(<|[ ,{])Rt[A-Z][A-Za-z0-9_]*/)  print file ":" ln "  Rt* component"
      ln++
    }')"
  [ -n "$hits" ] && MATCHES="${MATCHES}${hits}"$'\n'
done <<< "$FILES"

if [ -z "${MATCHES//[$'\n']/}" ]; then
  emit 0 '[]'
else
  JSON="$(printf '%s' "$MATCHES" | grep -v '^$' | python3 -c 'import sys,json; print(json.dumps([l.rstrip("\n") for l in sys.stdin]))')"
  emit 0 "$JSON"
fi
