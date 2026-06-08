---
name: multica
description: Managing agents, skills, projects, and task execution using the Multica CLI and daemon. Use when asked to setup, start, stop, check status of Multica runtimes, assign tasks to agents, or synchronize/register skills with Multica.
---

# Multica Integration Skill

This skill equips the AI agent with the compiled knowledge of the **Multica CLI** and **daemon architecture**, enabling seamless management of agents, runtimes, workspaces, and reusable skills in a vendor-neutral, teammate-focused manner.

With this skill, you can manage the local agent daemon, synchronize local repository skills to Multica's workspace database, provision agents for local runtimes, and coordinate task boards.

---

## Core Capabilities & Commands

The `multica` CLI is fully installed and available in the Nix shell environment. Use it to run the following tasks:

### 1. Setup & Authentication
*   **Initial Setup**: Run `multica setup` to configure the CLI, authenticate with your Multica account (opens browser verification), and start the daemon.
*   **Self-Hosted Setup**: Run `multica setup self-host` to connect to a self-hosted instance (prompting for server URL and token).
*   **Manual Authentication**: Run `multica login` to log in to the default Cloud server.

### 2. Daemon Management
The local agent runtime daemon coordinates tasks from the Multica platform to your local machine.
*   **Start Daemon**: Run `multica daemon start` to launch the background runner. It automatically scans your system path for installed agent CLIs (Claude, Codex, Gemini, Copilot, Hermes).
*   **Status Check**: Run `multica daemon status` to see if the daemon is online and inspect which agents it discovered.
*   **Stop Daemon**: Run `multica daemon stop`.
*   **Logs Monitoring**: Run `multica daemon logs -f` to watch agent runs in real-time.

### 3. Workspace Operations
*   **List Workspaces**: Run `multica workspace list` to display workspaces you belong to.
*   **Switch Workspace**: Run `multica workspace switch <id|slug>` to set the active default workspace.

### 4. Runtimes & Agents
*   **List Runtimes**: Run `multica runtime list` (or `multica runtime list --output json`) to view connected machines/runtimes and their statuses.
*   **List Agents**: Run `multica agent list` to see active AI teammates in the workspace.
*   **Create Agent**: Run `multica agent create --name "<Agent Name>" --runtime-id "<runtime-uuid>"` to provision a new agent teammate.
*   **Assign Skills to Agent**: Run `multica agent skills set <agent-uuid> --skill-ids "<comma-separated-skill-ids>"` to attach specific skills to an agent.

### 5. Skills Management
*   **List Skills**: Run `multica skill list --output json` to list all registered skills in the active workspace.
*   **Create Skill**: Run `multica skill create --name "<name>" --description "<description>" --content-file "<path/to/body>"` to register a new skill.
*   **Update Skill**: Run `multica skill update <skill-uuid> --content-file "<path/to/body>"`.
*   **Upsert Skill File**: Run `multica skill files upsert <skill-uuid> --path "<relative-path>" --content-file "<path/to/local/file>"` to upload companion files (scripts, rules, assets).

---

## Local Workspace Synchronization

To avoid manually configuring skills and agents on the Multica web board, a synchronization script has been created at `/.agents/skills/multica/scripts/sync.js`. 

This script scans both `./skills/` and `./.agents/skills/` directories for subdirectories containing a `SKILL.md` file, parses their frontmatter, registers/updates them in your active Multica workspace, uploads companion files, and optionally provisions missing agents and sets skill links.

### How to Run the Sync Script

From the workspace root directory:

1.  **Dry-Run Mode (Safe Preview)**:
    Inspect what will be created, updated, or deleted without modifying anything in Multica:
    ```bash
    bun ./.agents/skills/multica/scripts/sync.js --dry-run
    ```

2.  **Standard Synchronization**:
    Create/update all local skills and upload their companion files:
    ```bash
    bun ./.agents/skills/multica/scripts/sync.js
    ```

3.  **Full Environment Provisioning**:
    Synchronize skills, automatically provision agents for all online runtimes (Claude, Antigravity, Gemini, Copilot, Codex), and assign all skills to all active agents:
    ```bash
    bun ./.agents/skills/multica/scripts/sync.js --create-agents --assign-all
    ```

---

## Migration Steps for New Skills

When creating or adding new skills that you want migrated to Multica:
1.  Create a folder under `.agents/skills/<skill-name>` or `skills/<skill-name>`.
2.  Add a `SKILL.md` containing a YAML frontmatter block (defining `name` and `description`) followed by the Markdown instructions.
3.  Add any companion scripts (e.g. `scripts/*.js`), rule checklists (e.g. `rules/*.md`), or assets in the same directory.
4.  Run the synchronizer to push the changes:
    ```bash
    bun ./.agents/skills/multica/scripts/sync.js --assign-all
    ```

---

## Troubleshooting

*   **Authentication Errors**: If CLI commands fail with auth errors, run `multica login` to refresh your token.
*   **Missing Agents/Runtimes**: If `multica runtime list` does not show your local runtime, ensure the daemon is running locally by executing `multica daemon start`.
*   **Escaping Issues**: Long Markdown descriptions or rules should always be updated using `--content-file` instead of raw `--content` flags to prevent shell formatting/escaping errors. The `sync.js` script handles this automatically by writing to `scratch/temp_sync_content.md`.
