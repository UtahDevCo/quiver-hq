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
