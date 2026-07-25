# Soloterm orchestration for quiver-hq

One system to orchestrate Claude (and Codex/Gemini/etc.) across **every**
quiver-hq sub-project, with full visibility in the Soloterm control plane.

## Layout
```
quiver-hq/
  bin/solo-orch          # the command (already on PATH via quiver-hq/bin)
  solo/
    solo-child-agent.md  # protocol each spawned worker follows
    solo-child-lib.sh    # helper the worker sources (revision-safe append)
    install.sh           # one-time per-machine setup
    README.md
```
`solo-orch` finds `solo/` via `../solo`, so the whole thing is self-contained
and portable — clone quiver-hq on any machine, run `solo/install.sh`, done.

## Per-machine setup (once)
```bash
quiver-hq/solo/install.sh          # links `solo`, registers MCP, runs doctor
```
Then, in the Solo app, enable **Settings → Integrations → Local CLI/HTTP access**
and **Solo MCP**. Verify with `solo doctor` (want: `Ready: yes`).

## Per-project setup (once each)
Register any directory as a Solo project so `solo-orch` can find it:
```bash
solo projects create <name> "/absolute/path"
```
Submodules under `projects/*` are each their own Solo project.

## Everyday use — how you (or Claude) orchestrate
From *any* project directory (the project is auto-detected from `$PWD`):

```bash
solo-orch project                       # confirm which Solo project you're in
solo-orch agents                        # which tools you can spawn
solo-orch note "Goal: add X. Lanes: code owns src/**, test owns **/*.test.ts"
solo-orch spawn code "implement X in src/**"
solo-orch spawn test "cover X"          # spawn as many lanes as you want
AGENT_TOOL=codex solo-orch spawn docs "write the guide"   # mix tools per lane
solo-orch status                        # this project's agents + todos
solo-orch gather                        # tail each agent's output
solo-orch term scratch                  # open an ad-hoc terminal
solo-orch ps                            # EVERY process across ALL projects
```

## Visibility (the control plane)
- **Soloterm app sidebar**: every project, every spawned agent/terminal/command,
  live status, unread dots, CPU/mem. Scratchpads and todos have their own panels.
- **CLI**: `solo status` (global snapshot) · `solo-orch ps` (all processes) ·
  `solo-orch status` (one project) · `solo-orch gather` (agent output).

## Model
- **Mother** = whatever session runs `solo-orch` (a Claude Code session, or you).
- **Children** = agents spawned per *lane*, each owning a disjoint file set.
- **Shared memory** = the per-project `orchestration` scratchpad (revision-guarded).
- **Work tracking** = one todo per lane (`open → in_progress → completed`).
- Children follow `solo-child-agent.md`: orient → claim → work → append findings →
  DONE → complete. Cross-lane needs go through NEEDS notes, never direct edits.
