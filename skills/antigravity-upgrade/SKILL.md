---
name: antigravity-upgrade
description: Upgrade the Google Antigravity Suite (CLI, Manager, and IDE) within this Nix-managed developer environment. Use when asked to check for updates, upgrade antigravity packages, modify flake.nix, or rebuild the system using nixos-rebuild.
---

# Antigravity Upgrade Skill

This skill provides the mechanisms and scripts required to upgrade the declarative Google Antigravity Suite (CLI, Agent Manager, and IDE) inside your Nix-managed development environment (`quiver-wsl` / `quiver-hq`).

Because the system configuration is fully declarative and managed via a Nix flake, typical in-place auto-updaters or CLI update commands fail due to `/nix/store` being read-only. This skill automates the calculation of the new cryptographic SRI hashes (`sha256-...`), modifies `flake.nix` with the correct versions/URLs/hashes, and rebuilds the system configuration.

## Core Capabilities
1. **Cryptographic Integrity Auto-Verification:** Uses Nix's high-speed prefetch functionality (`nix store prefetch-file`) to fetch updates in-memory, calculate their SRI hashes, and ensure reproducible builds.
2. **Safe Parser-Based Patching:** Reads and precisely modifies only the `antigravityPackages` attribute set within `flake.nix` using targeted, safe substring matching.
3. **WSL Rebuild Pipeline:** Optionally triggers the system-level switch command `sudo nixos-rebuild switch --flake .#quiver-wsl` to apply the changes system-wide instantly.

---

## When to Use This Skill
Use this skill whenever the user (or another agent) asks:
- *"Upgrade the Antigravity IDE to the latest version"*
- *"Upgrade the CLI or Manager to a new version"*
- *"Check for new Antigravity updates and apply them"*
- *"Rebuild the environment with a newer version of the Antigravity suite"*

---

## Execution Guide

The skill executes via a helper script `upgrade.js` bundled in its `scripts` directory.

### Step 1: Execute the Upgrade Script
Execute the script using `bun` from the root of the active workspace. Pass the version parameters for the components you want to upgrade.

#### 1. Preview changes (Dry Run)
Check the SRI hash calculation and `flake.nix` modifications without writing any changes:
```bash
bun ./skills/antigravity-upgrade/scripts/upgrade.js --cli 1.0.0-5288553236791296 --dry-run
```

#### 2. Upgrade the IDE to a new version
This automatically prefetches the target URL, calculates the SRI hash, updates `flake.nix`, and builds the package:
```bash
bun ./skills/antigravity-upgrade/scripts/upgrade.js --ide 2.0.2-XXXXXXXX
```

#### 3. Upgrade all components and trigger a NixOS switch
```bash
bun ./skills/antigravity-upgrade/scripts/upgrade.js --cli 1.0.1-XXXXXX --manager 2.0.2-XXXXXX --ide 2.0.2-XXXXXX --rebuild
```

### Script Arguments:
*   `--cli <version>`: Specify a new version identifier for the `antigravity-cli` (e.g. `1.0.1-5288553236791296`).
*   `--manager <version>`: Specify a new version identifier for the `antigravity-manager` (e.g. `2.0.2-6566078776737792`).
*   `--ide <version>`: Specify a new version identifier for the `antigravity-ide` (e.g. `2.0.2-4861014005645312`).
*   `--rebuild`: Automatically execute `sudo nixos-rebuild switch --flake .#quiver-wsl` after writing updates.
*   `--dry-run`: Calculate hashes and show the planned diff without modifying any files.

---

## Troubleshooting
- **Missing Nix Store Prefetch Permissions:** Ensure you are running in an environment where the `nix` command is in your PATH (normally provided by the Nix development shell or NixOS).
- **Mismatched URL Structures:** If Google changes their archive repository structure, open `./skills/antigravity-upgrade/scripts/upgrade.js` and update the base template URLs at the top of the file.
- **Sudo Password Prompt:** If running `--rebuild` asks for a password, your user (`chris`) is configured in NixOS with passwordless sudo for convenience, but you can also run the system switch manually in the terminal.
