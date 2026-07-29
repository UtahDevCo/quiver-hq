---
type: Log
title: Brain bundle history
---

# Bundle history

## 2026-07-28

- **Initialization**: Bundle bootstrapped as OKF v0.2 by `claude/opus-5` at Chris's direction. Created the `meta` / `projects` two-layer split, the [conventions](conventions.md) concept defining override resolution and the three local extensions (`Practice Override`, `relations:`, `not:`), and the five management skills under `skills/`.
- **Decision**: per-project layers live here and are symlinked into each submodule as `.brain`, extending the existing `local/<project>/` pattern. `.brain` added to `~/.gitignore_global` so it can never be committed to a work repo.
- **Decision**: `projects/k1-fork` deliberately excluded from the brain. It is a third-party fork (`schulzgregory/tax-pe-fork`) and its conventions are not ours to adopt.
- **Scope**: harvest targets are `zamp`, `wiley`, `tools`, `trikin` — the submodules carrying curated agent context. The remaining submodules have no `AGENTS.md`/`CLAUDE.md` and are deferred.
