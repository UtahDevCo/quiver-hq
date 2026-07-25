#!/usr/bin/env bash
#
# quiver-hq/solo/install.sh — one-time per-machine setup for the Soloterm
# orchestration system. Idempotent: safe to re-run.
#
# What it does (nothing project-specific, nothing destructive):
#   1. Puts the `solo` CLI on PATH  (~/.local/bin/solo -> Solo.app solo-cli)
#   2. Registers Solo's MCP server with Claude Code (user scope)
#   3. Symlinks `solo-orch` onto PATH  (~/.local/bin/solo-orch -> this dir)
#   4. Runs `solo doctor` and reminds you about the two GUI toggles
#
set -euo pipefail

APP="/Applications/Solo.app/Contents/MacOS"
LOCAL_BIN="$HOME/.local/bin"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$LOCAL_BIN"

# 0. solo-orch on PATH --------------------------------------------------------
ln -sf "$HERE/solo-orch" "$LOCAL_BIN/solo-orch"
echo "✓ linked solo-orch -> $HERE/solo-orch"

# 1. solo CLI shim ------------------------------------------------------------
if command -v solo >/dev/null 2>&1; then
  echo "✓ solo CLI already on PATH ($(command -v solo))"
elif [ -x "$APP/solo-cli" ]; then
  ln -sf "$APP/solo-cli" "$LOCAL_BIN/solo"
  echo "✓ linked solo -> $APP/solo-cli"
else
  echo "✗ could not find Solo.app solo-cli. Install Soloterm, or adjust APP= in this script." >&2
fi

# 2. Claude Code MCP server ---------------------------------------------------
if command -v claude >/dev/null 2>&1; then
  if claude mcp list 2>/dev/null | grep -q '^solo:'; then
    echo "✓ Solo MCP already registered with Claude Code"
  elif [ -x "$APP/mcp" ]; then
    claude mcp add solo -s user "$APP/mcp" && echo "✓ registered Solo MCP (user scope)"
  else
    echo "✗ could not find Solo.app mcp helper; skipping MCP registration" >&2
  fi
else
  echo "· claude CLI not found; skipping MCP registration"
fi

# 3. Global CLAUDE.md import (every Claude session learns solo-orch) ----------
CLAUDE_MD="$HOME/.claude/CLAUDE.md"
IMPORT='@~/dev/quiver-hq/solo/CLAUDE.solo-orch.md'
mkdir -p "$HOME/.claude"
if [ -f "$CLAUDE_MD" ] && grep -qF "$IMPORT" "$CLAUDE_MD"; then
  echo "✓ ~/.claude/CLAUDE.md already imports solo-orch instructions"
else
  printf '\n%s\n' "$IMPORT" >> "$CLAUDE_MD"
  echo "✓ added solo-orch import to ~/.claude/CLAUDE.md"
fi

# 4. Health check -------------------------------------------------------------
echo
echo "── solo doctor ──"
solo doctor 2>&1 | sed -n '1,8p' || true
cat <<'EOF'

If doctor shows "Discovery: failed", enable BOTH toggles in the Solo app:
  Solo → Settings → Integrations
    • Local CLI / HTTP access
    • Solo MCP
Then re-run:  solo doctor

Usage:  solo-orch project   (from any registered project directory)
EOF
