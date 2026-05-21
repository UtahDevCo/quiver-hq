---
name: skills-manager
description: Search, list, install, update, and manage reusable AI agent skills from the open-source registry https://skills.sh/. Use when asked to add a new skill, find skills on the marketplace, list installed skills, or keep skills up to date.
---

# Skills Manager Skill

This skill equips the AI agent with capabilities to manage, search, list, install, update, and remove agent-compatible skills using the official command-line interface for **[skills.sh](https://skills.sh/)**.

With this skill, you can rapidly search the marketplace, install reusable packages of instructions, and extend your agent capabilities dynamically in the active workspace.

## Core Capabilities
1. **List Installed Skills:** Displays a formatted view of all project-level and user-level skills.
2. **Find/Search Skills:** Interactively or programmatically searches the `skills.sh` registry for skills matching a keyword.
3. **Add Skills:** Clones repositories and installs target skills to all agent configurations (including symlinking to `OpenClaw` and `Antigravity` agent dirs).
4. **Update Skills:** Upgrades installed skills to their latest releases from their source repositories.
5. **Remove Skills:** Uninstalls and clean-removes skills from the local project agents.

---

## When to Use This Skill
Use this skill whenever the user says:
- *"Add the X skill from skills.sh"*
- *"Search skills.sh for X"*
- *"List all installed skills"*
- *"Update my installed agent skills"*
- *"Remove the X skill"*

---

## Execution Guide

The skill executes via a helper script `manage.js` bundled in its `scripts` directory.

### Step 1: Execute the Skills Manager Script
Execute the script using `bun` from the root of the active workspace.

#### 1. List Installed Skills
```bash
bun ./skills/skills-manager/scripts/manage.js --list
```

#### 2. Search for Skills on the Registry
Search for matching skills (e.g. searching for "shadcn"):
```bash
bun ./skills/skills-manager/scripts/manage.js --find shadcn
```

#### 3. Install a Skill from a GitHub Repository or Package Name
This automatically resolves dependencies, clones the repository, verifies security assessments, and installs the skill for all agents:
```bash
bun ./skills/skills-manager/scripts/manage.js --add shadcn/ui
```

#### 4. Update all Installed Skills to the Latest Version
```bash
bun ./skills/skills-manager/scripts/manage.js --update
```

#### 5. Remove a Skill
```bash
bun ./skills/skills-manager/scripts/manage.js --remove shadcn
```

---

## Troubleshooting
- **Internet Access / Firewall Blocks:** The `skills` tool needs HTTPS access to `github.com` and `skills.sh`. Ensure you are connected to the network.
- **Agent Recognition:** By default, `--add` uses `--all` parameter which automatically targets all recognized agents (including Antigravity, OpenClaw, Codex, etc.).
