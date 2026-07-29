# Inbox

Unreviewed observations. Everything enters the brain here as `type: Observation`
with `status: draft`, then `/brain-promote` places it into `meta/` or
`projects/<name>/` with a human `verified` entry.

Agents write here freely. Agents never write to `meta/` directly.

# Required shape

Prefer `brain_push` (from `solo/solo-child-lib.sh`) or `/brain-push`, which emit
this for you. If you write the file by hand, use **this** shape:

```yaml
---
type: Observation
title: <one line stating the rule, not the topic>
description: <one sentence a reviewer can triage from>
kind: practice|pattern|failure-mode|stack|workflow|module|invariant|decision
proposed_layer: meta|project
proposed_project: <name>        # only when proposed_layer is project
observed_in: <name>             # always — this is provenance
tags: [...]
status: draft
not:                            # wherever an anti-pattern is known
  - { term: "...", why: "...", instead: "..." }
generated: { by: claude/opus-5, at: <ISO 8601 UTC> }
sources:
  - { id: <slug>, resource: <path or url>, title: <what it is> }
---
```

**This is not the auto-memory format.** `name:` / `description:` /
`metadata.type:` belongs to Claude's per-session memory store — a different thing in
a different directory. Files in that shape have landed here three times. They get
normalized at promotion, but the shape silently drops `kind`, `proposed_layer`,
`sources`, and `not:` — the four fields triage actually uses. In particular
`metadata.type: project` means a *memory category*, not a brain layer, so it reads as
a layer proposal that was never made.

Never set `verified:`. That is the promotion gate and it is Chris's alone.

# Currently queued

Four wiley/API observations awaiting review, two of them in the memory shape.
