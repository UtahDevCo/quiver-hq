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
- **Promoted** the general-practice batch — 9 to `meta/practices/`, 1 demoted. These are single-source (zamp only), so they carry more inference risk than the design-system batch; each records in its body which parts are library-specific and which are the transferable principle.
- **Demoted** `directive-driven-filenames` to `projects/zamp/practices/`. The transferable rule ("when runtime context changes a file's semantics, put it in the filename") is thin on its own; the value is the concrete `*.client.tsx` / `*.action.ts` extensions, which are Next.js App Router conventions. Flagged as a promotion candidate — wiley is also Next.js, so corroboration is plausible.
- **Resolved the tension** flagged during harvest: [follow-local-conventions](meta/practices/follow-local-conventions.md) governs *internal implementation idiom* only, and explicitly does not override the design-system practices. The boundary written into the concept: if a user or downstream consumer can see it, it's uniform; if only the module's maintainer sees it, it's local.
- **Renamed on promotion** for clarity over the observation slugs: `test-assertion-style` → `assert-on-whole-values`, `test-mocking-discipline` → `mock-at-narrowest-scope`, `error-propagation-to-edges` → `error-propagation-and-capture`. The new names state the rule rather than the topic.
- **Inbox now holds 11 zamp project concepts.** The meta layer is complete for this repo.
- **Added [install.sh](install.sh)** — four pieces of wiring live outside the repo and so did not travel with the first push: the `.brain` entry in `~/.gitignore_global`, the two `~/.claude/CLAUDE.md` imports, the five skill symlinks, and the per-project `.brain` symlinks. Without the CLAUDE.md imports the brain is invisible to every session, which is a silent failure — hence the installer. Modelled on `solo/install.sh`.
- **Moved the global CLAUDE.md prose** into [CLAUDE.brain.md](CLAUDE.brain.md) so it is versioned and edits reach every machine without re-running the installer, matching `solo/CLAUDE.solo-orch.md`. The meta index is imported as a *second top-level* line rather than nested inside that file: if nested imports ever fail to resolve, the index disappears from every session with no error.

## 2026-07-28

- **Initialization**: Bundle bootstrapped as OKF v0.2 by `claude/opus-5` at Chris's direction. Created the `meta` / `projects` two-layer split, the [conventions](conventions.md) concept defining override resolution and the three local extensions (`Practice Override`, `relations:`, `not:`), and the five management skills under `skills/`.
- **Decision**: per-project layers live here and are symlinked into each submodule as `.brain`, extending the existing `local/<project>/` pattern. `.brain` added to `~/.gitignore_global` so it can never be committed to a work repo.
- **Decision**: `projects/k1-fork` deliberately excluded from the brain. It is a third-party fork (`schulzgregory/tax-pe-fork`) and its conventions are not ours to adopt.
- **Scope**: harvest targets are `zamp`, `wiley`, `tools`, `trikin` — the submodules carrying curated agent context. The remaining submodules have no `AGENTS.md`/`CLAUDE.md` and are deferred.
