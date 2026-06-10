# Quiver HQ NixOS Configuration

This repository contains the reproducible NixOS and Home Manager configuration
for Quiver HQ machines. Multica is the agent orchestration layer; local coding
agents run through the Multica daemon rather than a repository-specific
controller.

## Multica

The flake packages the Multica CLI and Home Manager installs it for `chris`.
On Linux, Home Manager also defines `multica-daemon.service` as a user service.
The service:

- connects to Multica Cloud
- runs agent tasks on this machine
- detects supported agent CLIs from the user's profile
- stores task worktrees under `~/multica_workspaces`
- starts automatically after Multica authentication has saved a token in
  `~/.multica/config.json`

The release is pinned in `flake.nix`. Upgrade it by updating the version,
platform hashes, and then rebuilding the target host.

### First-Time Setup

Apply the host configuration:

```bash
sudo nixos-rebuild switch --flake .#$(hostname)
```

Authenticate with Multica Cloud:

```bash
multica login
multica auth status
```

`multica login` opens a browser. For a headless machine, create a personal
access token at <https://app.multica.ai/settings> and run:

```bash
multica login --token=
```

Start the declarative user service after authentication:

```bash
systemctl --user start multica-daemon
multica daemon status
```

The service is enabled for future user sessions and machine restarts. It is
skipped safely until `~/.multica/config.json` contains an authentication token.

Do not run `multica daemon start` separately while the systemd service is
active. Both commands operate on the same daemon profile and health port.

### Operations

```bash
multica daemon status
multica workspace list
multica workspace switch <workspace-id-or-slug>
multica issue list
multica issue create
systemctl --user status multica-daemon
systemctl --user restart multica-daemon
journalctl --user -u multica-daemon -f
```

Shell aliases:

- `mlogs`: follow the user service journal
- `mrestart`: restart the user service

The upstream CLI reference is available at
<https://github.com/multica-ai/multica/blob/main/CLI_AND_DAEMON.md>.

### Agent Runtimes

Multica detects supported CLIs from the user service `PATH`. This configuration
already provides Claude Code, Gemini CLI, GitHub Copilot CLI, OpenCode, and
Antigravity. Additional supported CLIs can be installed through Home Manager
and become available after restarting `multica-daemon`.

After login, confirm detected runtimes with:

```bash
multica daemon status
```

Then create agents and assign their runtimes in the Multica web application.

## Secret Management

`quiver-secrets` stores project environment values in 1Password.

```bash
quiver-secrets ingest ./projects/example
quiver-secrets hydrate ./projects/example
```

This remains independent of Multica. Projects that use `.env.tmpl` should be
hydrated before assigning agent work that requires those secrets.

## Project Submodules

Projects are maintained as Git submodules under `projects/`.

```bash
git submodule update --init --recursive
./manage-submodules.sh
```

Register each repository with the appropriate Multica project or resource.
Multica creates isolated task worktrees under `~/multica_workspaces`; it does
not execute tasks directly inside the checked-out submodule.

## Development Shell

```bash
nix develop
```

The shell provides Go, Node.js, Bun, SQLite, Git LFS, Multica, and the
repository's other packaged tools.

## Validation

Evaluate or build the package directly:

```bash
nix build .#multica
./result/bin/multica version
```

Validate a host configuration without activating it:

```bash
nix build .#nixosConfigurations.$(hostname).config.system.build.toplevel
```
