---
name: antigravity-upgrade
description: Upgrade the Google Antigravity Suite (CLI, Manager, and IDE) within this Nix-managed developer environment. Use when asked to check for updates, upgrade antigravity packages, modify flake.nix, or rebuild the system using nixos-rebuild.
---

# Antigravity Upgrade Skill

This skill provides the mechanisms and scripts required to upgrade the declarative Google Antigravity Suite (CLI, Agent Manager, and IDE) inside your Nix-managed development environment (`quiver-wsl` / `quiver-hq`).

Because the system configuration is fully declarative and managed via a Nix flake, typical in-place auto-updaters or CLI update commands fail due to `/nix/store` being read-only. This skill automates the discovery of the latest versions from Google Cloud Storage (GCS), calculates the new cryptographic SRI hashes (`sha256-...`), modifies `flake.nix` with the correct versions/URLs/hashes, and rebuilds the system configuration.

## Core Capabilities
1. **Automatic Version Discovery:** Queries the public `antigravity-public` GCS bucket to find the latest CLI and Manager versions. Probes the IDE CDN for the latest IDE release.
2. **Cryptographic Integrity Auto-Verification:** Uses Nix's high-speed prefetch functionality (`nix store prefetch-file`) to fetch updates in-memory, calculate their SRI hashes, and ensure reproducible builds.
3. **Safe Parser-Based Patching:** Reads and precisely modifies only the `antigravityPackages` attribute set within `flake.nix` using targeted, safe substring matching.
4. **Dynamic Hostname Rebuild:** Uses `hostname` to auto-detect the correct NixOS configuration target (e.g. `quiver-pn54`, `quiver-wsl`), then triggers `sudo nixos-rebuild switch --flake .#<hostname>`.

---

## Shell Alias

A shell alias `upgrade-agy` is defined in `~/dev/quiver-hq/nixos/home.nix`. Simply run:

```bash
upgrade-agy
```

This runs the full auto-discovery + rebuild pipeline:
```bash
cd ~/dev/quiver-hq && bun /home/chris/.gemini/config/skills/antigravity-upgrade/scripts/upgrade.js --auto --rebuild
```

---

## When to Use This Skill
Use this skill whenever the user (or another agent) asks:
- *"Upgrade the Antigravity apps to the latest version"*
- *"Check for new Antigravity updates and apply them"*
- *"Rebuild the environment with a newer version of the Antigravity suite"*
- *"Run upgrade-agy"* — or when the user types the alias directly

---

## Execution Guide

The skill executes via a helper script `upgrade.js` bundled in its `scripts` directory.

### Option 1: Fully Automatic (Recommended)
Discovers the latest versions from GCS, updates `flake.nix`, and rebuilds — no manual version lookup needed:

```bash
cd ~/dev/quiver-hq
bun /home/chris/.gemini/config/skills/antigravity-upgrade/scripts/upgrade.js --auto --rebuild
```

#### Dry-run first (preview changes without applying):
```bash
bun /home/chris/.gemini/config/skills/antigravity-upgrade/scripts/upgrade.js --auto --dry-run
```

### Option 2: Manual Version Pinning
Specify exact version identifiers for the components you want to upgrade:

```bash
bun /home/chris/.gemini/config/skills/antigravity-upgrade/scripts/upgrade.js \
  --cli 1.0.1-6660132856266752 \
  --manager 2.0.6-5413878570549248 \
  --ide 2.0.1-4861014005645312 \
  --rebuild
```

### Script Arguments:
*   `--auto`: Auto-discover and upgrade all components to their latest GCS versions.
*   `--cli <version>`: Specify a new version identifier for the `antigravity-cli` (e.g. `1.0.1-6660132856266752`).
*   `--manager <version>`: Specify a new version identifier for the `antigravity-manager` (e.g. `2.0.6-5413878570549248`).
*   `--ide <version>`: Specify a new version identifier for the `antigravity-ide` (e.g. `2.0.1-4861014005645312`).
*   `--rebuild`: Automatically execute `sudo nixos-rebuild switch --flake .#$(hostname)` after writing updates.
*   `--dry-run`: Calculate hashes and show the planned diff without modifying any files.

---

## How Auto-Discovery Works
1. **CLI** — Lists `antigravity-cli/` prefixes in `gs://antigravity-public` and picks the highest semver+buildId.
2. **Manager** — Lists `antigravity-hub/` prefixes in `gs://antigravity-public` and picks the highest semver+buildId (excluding dogfood channels).
3. **IDE** — Probes the CDN (`edgedl.me.gvt1.com`) for newer versions by combining known semver minors with build IDs found in the manager/CLI buckets. Falls back gracefully if no newer version is found.

---

## Troubleshooting
- **Missing Nix Store Prefetch Permissions:** Ensure you are running in an environment where the `nix` command is in your PATH (normally provided by the Nix development shell or NixOS).
- **Mismatched URL Structures:** If Google changes their archive repository structure, open `./scripts/upgrade.js` and update the `getCliUrl`, `getManagerUrl`, or `getIdeUrl` template functions at the top of the file.
- **Sudo Password Prompt:** If running `--rebuild` asks for a password, your user (`chris`) is configured in NixOS with passwordless sudo for convenience, but you can also run the system switch manually in the terminal.
- **IDE Version Not Found:** The IDE CDN is not publicly listable. If probing fails to find a newer IDE version, check `antigravity.google/download` manually and pass the version explicitly with `--ide <version>`.
