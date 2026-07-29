#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$root"

echo "Building Go binaries from ./cmd into ./bin"
mkdir -p bin

# If there are no subdirs, the loop is skipped
for d in cmd/*; do
  if [ -d "$d" ]; then
    name=$(basename "$d")
    echo "Building $name..."
    go build -o "bin/$name" "./cmd/$name"
  fi
done

echo "Done. Binaries are in $root/bin"

# Register the `gh stacks` alias (bin/gh-stacks travels with the repo on PATH; the
# alias itself lives in per-machine gh config, so set it here for reproducibility).
if command -v gh >/dev/null 2>&1; then
  echo "Registering 'gh stacks' alias..."
  gh alias set stacks --clobber '!exec gh-stacks'
fi
