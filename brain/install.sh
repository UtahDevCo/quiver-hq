#!/usr/bin/env bash
#
# quiver-hq/brain/install.sh — one-time per-machine wiring for the brain.
# Idempotent: safe to re-run. Mirrors quiver-hq/solo/install.sh.
#
# The bundle itself travels with the repo. These four pieces do NOT, because
# they live outside it:
#   1. ~/.gitignore_global    `.brain` — so a symlink can never be committed
#                             into a work repo
#   2. ~/.claude/CLAUDE.md    two @imports — without these the brain is
#                             invisible to every session
#   3. ~/.claude/skills/      one symlink per brain skill
#   4. projects/<n>/.brain    symlink into each project's brain layer
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .../quiver-hq/brain
QUIVER="$(dirname "$HERE")"                            # .../quiver-hq

# 1. gitignore_global ---------------------------------------------------------
# Must come first: creating .brain symlinks before this is ignored would leave
# them staged in a work repo.
IGNORE="$(git config --global core.excludesFile || true)"
if [ -z "$IGNORE" ]; then
  IGNORE="$HOME/.gitignore_global"
  git config --global core.excludesFile "$IGNORE"
  echo "✓ set git core.excludesFile -> $IGNORE"
fi
IGNORE="${IGNORE/#\~/$HOME}"
touch "$IGNORE"
if grep -qxF '.brain' "$IGNORE"; then
  echo "✓ $IGNORE already ignores .brain"
else
  printf '\n# Brain symlinks into submodules -> quiver-hq/brain/projects/<name>\n.brain\n' >> "$IGNORE"
  echo "✓ added .brain to $IGNORE"
fi

# 2. Global CLAUDE.md imports -------------------------------------------------
# Two top-level imports rather than nesting the index inside CLAUDE.brain.md:
# if nested imports ever fail to resolve, the meta index vanishes from every
# session silently. Cheap insurance on the load-bearing piece.
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
mkdir -p "$HOME/.claude"
touch "$CLAUDE_MD"
# CLAUDE.style.md is a repo-root peer rather than part of the brain. It is wired
# here because this is the only installer that touches ~/.claude/CLAUDE.md, and a
# third installer for one import line is not worth the surface area.
for IMPORT in \
  '@~/dev/quiver-hq/CLAUDE.style.md' \
  '@~/dev/quiver-hq/brain/CLAUDE.brain.md' \
  '@~/dev/quiver-hq/brain/meta/index.md'
do
  if grep -qF "$IMPORT" "$CLAUDE_MD"; then
    echo "✓ ~/.claude/CLAUDE.md already imports ${IMPORT##*/}"
  else
    printf '\n%s\n' "$IMPORT" >> "$CLAUDE_MD"
    echo "✓ added ${IMPORT##*/} import to ~/.claude/CLAUDE.md"
  fi
done

# 3. Skills ------------------------------------------------------------------
# Symlinked, not copied, so editing a skill in the repo takes effect at once and
# every machine tracks the same version.
SKILLS="$HOME/.claude/skills"
mkdir -p "$SKILLS"
for SRC in "$HERE"/skills/*/; do
  NAME="$(basename "$SRC")"
  if [ -e "$SKILLS/$NAME" ] && [ ! -L "$SKILLS/$NAME" ]; then
    echo "✗ $SKILLS/$NAME exists and is not a symlink — left alone" >&2
  else
    ln -sfn "${SRC%/}" "$SKILLS/$NAME"
    echo "✓ linked /$NAME -> ${SRC%/}"
  fi
done

# 4. Per-project .brain symlinks ---------------------------------------------
# Driven by brain/projects/ (in git) rather than by projects/ (submodules), so a
# checkout without every submodule doesn't produce dangling links.
for LAYER in "$HERE"/projects/*/; do
  NAME="$(basename "$LAYER")"
  TARGET="$QUIVER/projects/$NAME"
  if [ ! -d "$TARGET" ]; then
    echo "· no checkout at projects/$NAME — skipping (run: git submodule update --init)"
    continue
  fi
  if [ -e "$TARGET/.brain" ] && [ ! -L "$TARGET/.brain" ]; then
    echo "✗ projects/$NAME/.brain exists and is not a symlink — left alone" >&2
    continue
  fi
  ln -sfn "../../brain/projects/$NAME" "$TARGET/.brain"
  echo "✓ linked projects/$NAME/.brain -> brain/projects/$NAME"
done

# 5. Verify ------------------------------------------------------------------
echo
FAIL=0
for LAYER in "$HERE"/projects/*/; do
  NAME="$(basename "$LAYER")"
  TARGET="$QUIVER/projects/$NAME"
  [ -d "$TARGET/.git" ] || [ -f "$TARGET/.git" ] || continue
  # A .brain that shows up in status means step 1 didn't take.
  if git -C "$TARGET" status --porcelain 2>/dev/null | grep -q '\.brain'; then
    echo "✗ projects/$NAME: .brain is NOT ignored — check core.excludesFile" >&2
    FAIL=1
  fi
done
[ "$FAIL" -eq 0 ] && echo "✓ all .brain symlinks are git-ignored"

cat <<'EOF'

Done. Verify in a NEW Claude session (imports load at startup):
  /brain-recall error handling      → should resolve without reading files first

Daily:   /brain-push "<learning>"   ·  /brain-recall <topic>
Weekly:  /brain-promote             ·  /brain-audit
EOF
