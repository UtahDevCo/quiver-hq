---
type: Log
title: Brain bundle history
---

# Bundle history

## 2026-07-29

- **Harvested** `projects/zamp` into `inbox/` — 31 observations from `AGENTS.md`, `.coderabbit.yaml`, `.cursor/rules/sharded-tables.mdc`, `CLAUDE.local.md`, the two reviewer subagents, `git-conventions.local.md`, the `add-ds-component` skill, and the design-system package. Declined: the 117 concrete components and zamp/indigo theme values (project-specific values, not standards), operational commands and port tables, and the 17 daily-scan/triage subagents (orchestration wiring, not knowledge).
- **Promoted** the design-system batch — 10 concepts, all first-of-their-kind. Chris explicitly declared zamp's design-system standards to be his own, so these entered `meta/` on his assertion rather than on cross-repo corroboration; recorded as `author: human:christopher` in `sources` per [conventions](conventions.md).
- **Added** `Practice` vs `Pattern` (default-on vs opt-in) and "the brain describes, it does not retrofit" to [conventions](conventions.md). Without the first distinction an agent treats an available pattern as a required rule and rewrites code that was already fine.
- **Synthesized** [make-misuse-unrepresentable](meta/practices/make-misuse-unrepresentable.md) — the general principle behind deleting unused palette scales and behind the type-enforced accessibility union. This was *inferred* from two instances, not found stated in any repo; promoted only on Chris's explicit approval. It is the first concept in the brain not traceable to a written source, and it is flagged as such in its own body.
- **Demoted** the Storybook practice to `projects/zamp/practices/story-per-component.md`. Storybook is zamp-only (confirmed by Chris), so a default-on meta practice would fire in repos that cannot satisfy it. The transferable half — a component isn't done until there's a runnable example — is deliberately *not* recorded as meta yet, because no second repo has shown what shape it should take.
- **Deferred**: 21 observations remain in `inbox/` — 10 general-practice meta candidates and 11 zamp project concepts.

## 2026-07-28

- **Initialization**: Bundle bootstrapped as OKF v0.2 by `claude/opus-5` at Chris's direction. Created the `meta` / `projects` two-layer split, the [conventions](conventions.md) concept defining override resolution and the three local extensions (`Practice Override`, `relations:`, `not:`), and the five management skills under `skills/`.
- **Decision**: per-project layers live here and are symlinked into each submodule as `.brain`, extending the existing `local/<project>/` pattern. `.brain` added to `~/.gitignore_global` so it can never be committed to a work repo.
- **Decision**: `projects/k1-fork` deliberately excluded from the brain. It is a third-party fork (`schulzgregory/tax-pe-fork`) and its conventions are not ours to adopt.
- **Scope**: harvest targets are `zamp`, `wiley`, `tools`, `trikin` — the submodules carrying curated agent context. The remaining submodules have no `AGENTS.md`/`CLAUDE.md` and are deferred.
