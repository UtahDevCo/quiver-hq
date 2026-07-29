## The brain (second brain, OKF bundle)

`~/dev/quiver-hq/brain/` is Chris's second brain: coding practices, patterns,
and per-project knowledge as an Open Knowledge Format v0.2 bundle. The meta
index is always in context; the concepts it links are not — **read a concept in
full before relying on it.**

- Working inside `~/dev/quiver-hq/projects/<name>/`? That project's layer is at
  `.brain/index.md`. Project overrides beat meta practices — resolve them
  first, or run `/brain-recall <topic>` which does it for you.
- Learned something worth keeping? `/brain-push "<learning>"`. Cheap, and the
  inbox is reviewed later — bias toward recording. **Don't hand-write files into
  `brain/inbox/`** — the brain is OKF (`type:`/`kind:`/`proposed_layer:`/`sources:`),
  not the auto-memory format (`name:`/`description:`/`metadata.type:`), and the
  memory shape silently loses the layer proposal, provenance, and `not:` entries.
  Auto-memory is for facts about Chris and this session; the brain is for durable
  engineering knowledge. Different stores, different shapes.
- **Never write to `brain/meta/` directly, and never add a `human:` `verified`
  entry.** Agents propose into `brain/inbox/`; only Chris promotes, via
  `/brain-promote`. That gate is what makes the trust tiers mean anything.
- Governance and the local extensions: `brain/conventions.md`.
