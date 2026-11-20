---
type: Observation
title: Nix devshell binaries shadow Homebrew and block global npm installs
description: On Chris's Mac the Nix devshell puts an older gh first on PATH and Node in the read-only Nix store, so new CLI features and npm -g installs fail until you route around it.
kind: stack
proposed_layer: meta
tags: [nix, homebrew, gh-cli, vercel-cli, local-env]
generated: { by: claude/opus-5.5, at: 2026-11-03T17:59:48Z }
status: draft
sources:
  - id: session
    resource: none (shell output, 2026-11-03 session testing zamp PR 10626)
    title: which -a gh / npm i -g vercel EACCES
    last_modified: 2026-11-03
not:
  - term: "npm i -g vercel"
    why: "npm prefix is /nix/store/...-nodejs-slim-24.15.0, which is read-only: EACCES mkdir .../lib"
    instead: "brew install vercel (cask, links /opt/homebrew/bin/vercel)"
  - term: "gh pr comment ... --attach (bare gh)"
    why: "bare gh resolves to the Nix devshell gh 2.94.0, which has no --attach"
    instead: "/opt/homebrew/bin/gh pr comment ... --attach (brew upgrade gh first)"
  - term: "export PRISMA_SCHEMA_ENGINE_BINARY from ~/.zshrc"
    why: "points at a garbage-collected /nix/store prisma-engines path; prisma db push fails with 'provided path ... can't be resolved'"
    instead: "unset PRISMA_SCHEMA_ENGINE_BINARY before prisma commands, or remove the export"
---

# Observation

`which -a gh` lists `/nix/store/...-devshell-dir/bin/gh` (2.94.0) ahead of `/opt/homebrew/bin/gh` (2.103.3 after `brew upgrade gh`). Node comes from `/nix/store/...-nodejs-slim-24.15.0`, so `npm config get prefix` is a read-only store path and `npm i -g` fails with EACCES. `~/.zshrc` exports `PRISMA_SCHEMA_ENGINE_BINARY` to a Nix store path that no longer exists.

For a CLI that needs to be newer than the devshell or installed globally, use Homebrew and call it by absolute path when the Nix copy shadows it. Unset the stale Prisma variable before Prisma schema commands.

# Why it matters

The failures look like tool bugs ("flag not found", EACCES, "schema engine can't be resolved") rather than PATH order, and each one cost a detour in the PR 10626 e2e run.

# Evidence

- `gh version 2.94.0 (nixpkgs)` from bare `gh`; `/opt/homebrew/bin/gh --version` reports 2.103.3 and its `pr comment --help` lists `--attach`.
- `npm i -g vercel@latest`: `EACCES: permission denied, mkdir '/nix/store/4366l8b6kz1f2sxq6243rfs53grc73zz-nodejs-slim-24.15.0/lib'`. `brew install vercel` succeeded (65.9.0).
- `vitess-init.sh`: `Env var PRISMA_SCHEMA_ENGINE_BINARY is provided but provided path /nix/store/w23kx0fpr9sq8196lfravfq0pms9asj8-prisma-engines_7-7.7.0/bin/schema-engine can't be resolved.`
