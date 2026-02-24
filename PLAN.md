# 🎯 QUIVER HQ: MASTER EXECUTION PLAN (v1.1)

## ✅ PHASE 0: FOUNDATION (COMPLETED)
- [x] Initialize Go workspace & SQLite schema.
- [x] Implement `internal/db` for mission logging.
- [x] Implement `quiver-secrets` for 1Password orchestration.
- [x] Implement `internal/manager` (The Executor Core).
- [x] Implement `internal/discord` (Basic Bot + Thread-per-Mission).
- [x] Implement Two-way communication (Discord -> Agent Stdin).

---

## ✅ PHASE 1: SUBMODULE & SECRET ORCHESTRATION (COMPLETED)
- [x] Task 1.1: Submodule Discovery Logic
    - [x] Create `internal/projects/scanner.go`.
    - [x] Function: `ListSubmodules()` (Parses `.gitmodules`).
    - [x] Function: `GetProjectPath(name string)` (Maps name to absolute path).
- [x] Task 1.2: Integrated Secret Hydration
    - [x] Add `PrepareWorkspace(projectPath string)` to the controller.
    - [x] Execution: Automatically run `quiver-secrets hydrate` before starting a mission in a submodule.

---

## ✅ PHASE 2: DISCORD UI & HUMAN-IN-THE-LOOP (HITL) (COMPLETED)
- [x] Task 2.1: Approval Gates (Buttons/Modals)
    - [x] Implement `RequestApproval` logic in the Manager.
    - [x] Use Discord ActionRows for "Approve/Deny" on risky signals.
- [x] Task 2.2: Slash Command Autocomplete
    - [x] Migrate `!mission` commands to Slash Commands (`/mission`).
    - [x] Connect the Submodule Scanner to Discord’s Autocomplete API for project names.

---

## ✅ PHASE 3: REMOTE ACCESS & STABILITY (COMPLETED)
- [x] Task 3.1: Tailscale Integration
    - [x] Update `configuration.nix` with `services.tailscale.enable = true;`.
- [x] Task 3.2: Daemonization (Systemd)
    - [x] Define a NixOS systemd service for the `quiver-controller`.

---

## [ ] PHASE 4: LONG-TERM MEMORY & RAG
*Priority: Low | Goal: Agentic continuity and history awareness.*

- [ ] **Task 4.1: Mission Summary Generation**
    - [ ] Post-mission hook: Send logs to Gemini for a "Briefing Summary."
- [ ] **Task 4.2: Local Context Injection**
    - [ ] Save summaries to `projects/<submodule>/docs/history.md`.
    - [ ] Update system prompt to read history before starting new missions.

---

## [ ] PHASE 5: MONITORING & METRICS
*Priority: Low | Goal: Operational health for the "Always-On" server.*

- [ ] **Task 5.1: Health Heartbeat**
    - [ ] Go Ticker: Send system stats to Discord every 6 hours.
- [ ] **Task 5.2: Automated Backups**
    - [ ] Script: `VACUUM` SQLite and backup `quiver.db`.
