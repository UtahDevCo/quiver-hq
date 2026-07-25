## Soloterm orchestration (`solo-orch`)

This machine runs **Soloterm** (Solo.app). Across ALL projects you can orchestrate
child agents, scratchpads, terminals, and todos through the `solo-orch` command
(source of truth: `~/dev/quiver-hq/solo/`, on PATH via `~/.local/bin/solo-orch`).

**When to use it:** whenever the user asks you to spin up / delegate to other agents,
run work in parallel lanes, or coordinate a larger task with visibility in Soloterm.
You act as the "mother": you spawn workers and they appear in the Solo sidebar.

**First, confirm it's live** (skip if you already know it is):
```bash
command -v solo-orch >/dev/null && solo doctor | grep -q 'Ready: yes' && solo-orch project
```
- If `solo-orch` is missing → run `~/dev/quiver-hq/solo/install.sh`.
- If doctor isn't ready → tell the user to enable **Solo → Settings → Integrations →
  Local CLI/HTTP access + Solo MCP**.
- If `solo-orch project` says no project matches → `solo projects create <name> "$PWD"`.

**Commands** (project auto-detected from `$PWD`):
```bash
solo-orch project                  # which Solo project you're in
solo-orch agents                   # tools you can spawn (claude, codex, gemini, …)
solo-orch note "Goal … lane map …" # write shared context to the orchestration scratchpad
solo-orch spawn <lane> "<objective>"   # create a lane todo + spawn ONE agent
AGENT_TOOL=codex solo-orch spawn <lane> "<obj>"   # pick a non-Claude tool
solo-orch status                   # this project's agents + todos
solo-orch gather                   # tail each agent's output
solo-orch term [name]              # open a terminal
solo-orch ps                       # ALL processes across ALL projects (control plane)
solo-orch sweep [--quiet]          # triage board for ALL projects, with flags
```

**Lead loop:** to manage the portfolio (not one task), run `/lead` — one pass of
`SWEEP → TRIAGE → ACT → RECORD → next wake` over every project. `/loop /lead` makes
it standing. Protocol: `~/dev/quiver-hq/solo/solo-lead-agent.md`.

**Model:** children spawn one-per-lane, each owning a **disjoint** file set (prevents
races). Shared memory = the per-project `orchestration` scratchpad (revision-guarded).
Work tracking = one todo per lane (`open → in_progress → completed`). Spawned agents
follow `~/dev/quiver-hq/solo/solo-child-agent.md`.

**Rules:**
- Spawning agents is a real, resource-consuming action — confirm with the user before
  a multi-lane dispatch; a single lane is fine to demo.
- `solo-orch ps`/`status` may show agents and modified files you did NOT create
  (other sessions, the user). Never attribute them to your workers and never revert
  another session's work.
- Full docs: `~/dev/quiver-hq/solo/README.md`.
