# Quiver HQ NixOS Configuration

This repository contains the complete NixOS and home-manager configuration for the hosts and development environments used at Quiver HQ. It is designed to be fully reproducible and managed via this git repository.

## Quiver HQ Agentic Tools

The project includes a Go-based agentic controller and a secret management utility.

### 1. Secret Management (`quiver-secrets`)

Manage environment variables via 1Password.

*   **Ingest**: Scan a project for `.env` files, push secrets to 1Password, and create a `.env.tmpl` file.
    ```bash
    ./quiver-secrets ingest ./my-project
    ```
*   **Hydrate**: Reconstruct a `.env` file from 1Password using the `.env.tmpl`.
    ```bash
    ./quiver-secrets hydrate ./my-project
    ```

### 2. Mission Controller (`controller`)

The central daemon that orchestrates agents and logs missions to SQLite.

*   **Systemd Service**: The controller is managed as a NixOS systemd service.
    ```bash
    qlogs      # View live daemon logs
    qrestart   # Restart the daemon
    ```
*   **Manual Run**: (For debugging)
    ```bash
    nix develop -c env GEMINI_API_KEY=$(op read op://Personal/quiver-hq/GEMINI_API_KEY) \
        DISCORD_BOT_TOKEN=$(op read op://Personal/quiver-hq/DISCORD_BOT_TOKEN) \
        ./controller
    ```

### 3. Remote Access & Stability

*   **Tailscale**: The system is configured with Tailscale for secure remote access.
*   **Persistence**: The daemon automatically starts on boot (or WSL startup) and restarts on failure via systemd.

### 4. Discord Slash Commands

Talk to the daemon remotely via Discord using `/` commands:

*   `/ping`: Check if the daemon is online.
*   `/mission list`: List all active missions.
*   `/mission start <project> <id> <command> [args...]`: Start a new mission. 
    *   **Autocomplete**: The `project` field will suggest submodules found in `.gitmodules`.
    *   **Threads**: Creates a dedicated thread for output.
*   `/mission stop <id>`: Kill a running mission.

### 4. Human-in-the-Loop (Approval Gates)

Agents can request approval for risky actions by outputting a specific signal:
`QUIVER_SIGNAL:REQUEST_APPROVAL <prompt>`

The daemon will present **Approve** and **Deny** buttons in the Discord thread. The agent will wait for your decision, which is piped back to its `stdin` as `APPROVED` or `DENIED`.

### 5. Database Management

Missions and logs are stored in `quiver.db`.
```bash
nix develop -c sqlite3 quiver.db "SELECT * FROM mission_logs;"
```

---

## 🚀 Setup & Integration Guide

Follow these steps to fully activate the Quiver HQ ecosystem.

### 1. 1Password Integration (The Secret Vault)
The controller expects a 1Password item named `quiver-hq` to store its credentials.

1.  **Sign In**: Run `opsignin` (or `eval $(op signin)`) in your terminal.
2.  **Create Item**: Create a new **API Credential** or **Secure Note** in 1Password named `quiver-hq`.
3.  **Add Fields**:
    *   `GEMINI_API_KEY`: Your Google AI Studio API key.
    *   `DISCORD_BOT_TOKEN`: Your Discord bot token (see below).
    *   `DISCORD_CHANNEL_ID`: (Optional) The ID of the channel where the daemon should post startup notifications.

### 2. Discord Integration (The UI)
You need to create a Discord application to act as the Quiver HQ interface.

1.  **Developer Portal**: Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  **Create App**: Click "New Application" and name it "Quiver HQ".
3.  **Bot Setup**:
    *   Go to the **Bot** tab.
    *   Reset/Copy the **Token** and save it to your `quiver-hq` 1Password item.
    *   **Crucial**: Scroll down to "Privileged Gateway Intents" and enable **Message Content Intent**. This is required to pipe your replies to the agent's stdin.
4.  **OAuth2 (Invite)**:
    *   Go to **OAuth2** -> **URL Generator**.
    *   Select scopes: `bot`, `applications.commands`.
    *   Select bot permissions: `Read Messages/View Channels`, `Send Messages`, `Create Public Threads`, `Send Messages in Threads`.
    *   Open the generated URL to invite the bot to your server.

### 3. Tailscale Integration (The Network)
Tailscale provides secure remote access to your NixOS/WSL machine.

1.  **Apply Config**: Run `sudo nixos-rebuild switch --flake .#quiver-wsl`.
2.  **Authenticate**: Run `sudo tailscale up`.
3.  **Login**: Click the link provided in the terminal to add this machine to your Tailnet.
4.  **Remote Control**: You can now access your Quiver HQ dashboard or terminal from any device on your Tailnet (phone, laptop, etc.).

### 4. Running the Controller
Once the secrets are set in 1Password and the NixOS config is applied:

1.  **Build**: `nix develop -c go build -o controller ./cmd/controller/main.go`
2.  **Start Service**: `sudo systemctl start quiver-controller`
3.  **Watch Logs**: `qlogs`

---

## Workflows

There are two primary workflows for using this repository: managing an existing system and installing a new system from scratch.

### 1. Day-to-Day System Management (Existing System)

This is the most common workflow. Use it to apply updates or configuration changes to a system that is already running this configuration.

1.  **Edit Configuration**: Make any desired changes to the `.nix` files in this repository.
2.  **Apply Changes**: From within this repository's root directory (`/home/chris/dev/quiver-hq`), run the following command to apply the configuration to your running system:

    ```bash
    sudo nixos-rebuild switch --flake .#quiver-wsl
    ```

    *   `sudo nixos-rebuild switch`: The standard command to build and activate a new system generation.
    *   `--flake .`: Tells the command to use the `flake.nix` in the current directory.
    *   `#quiver-wsl`: Specifies which `nixosConfigurations` output from your `flake.nix` to build and apply.

3.  **Commit**: Once you are happy with the changes, commit them to git to track your configuration's history.

    ```bash
    git add .
    git commit -m "feat: add new package and update shell alias"
    ```

### 2. "From Scratch" Installation (New System)

Use this workflow to install a completely new NixOS system (e.g., a new WSL instance, a new VM, or a new physical machine) using this repository as the source of truth.

1.  **Boot Installer**: Boot the target machine using a standard NixOS installer image.
2.  **Prepare Disks**: Partition and format the disks as required for your new system.
3.  **Mount Filesystems**: Mount the newly created filesystems under `/mnt`. For example, mount your root partition on `/mnt` and your boot partition on `/mnt/boot`.
4.  **Clone Repository**: Clone this repository onto the installation medium.

    ```bash
    git clone https://github.com/your-username/quiver-hq.git /mnt/etc/nixos
    ```
    *(Note: It's common practice to clone the configuration into `/mnt/etc/nixos`)*

5.  **Run Installation**: Instead of generating a new configuration, run `nixos-install` and point it directly to the host definition within your cloned flake:

    ```bash
    sudo nixos-install --flake /mnt/etc/nixos#quiver-wsl
    ```

After the installation is complete and you reboot, the new system will be running the exact configuration defined in this repository.

## Configuration Recommendations

Your configuration is well-structured. Here are a few recommendations to make it even more robust and portable.

### Use Portable Paths

Your `home.nix` contains aliases with hardcoded absolute paths (e.g., `/home/chris/dev/quiver-hq`). This can break if you clone the repo to a different location or use it for another user.

**Recommendation**: Modify the `reload` alias in `nixos/home.nix` to be independent of its absolute path. A more robust version would change directory to the known location first:

*   **From**: `alias reload="sudo nixos-rebuild switch --flake /home/chris/dev/quiver-hq#quiver-wsl"`
*   **To**: `alias reload='(cd /home/chris/dev/quiver-hq && sudo nixos-rebuild switch --flake .#quiver-wsl)'`

This ensures the command always runs from the correct directory context.

### Centralize Shell Configuration

You have correctly placed your Zsh configuration inside `home.nix` using `programs.zsh.initContent`. The file at `nixos/files/.zshrc` appears to be unused, as its content is managed by home-manager. This is good! Centralizing configuration in `home.nix` is the idiomatic approach.

### Hardware Configuration

The file `nixos/hosts/wsl/hardware-configuration.nix` is specific to your current machine. When installing on a new machine, NixOS will generate a new version of this file that is specific to that new hardware. Your current setup correctly isolates this file from the common configuration.
